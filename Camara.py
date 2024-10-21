# Este archivo se utiliza para determinar
# los puntos del ROI para usar con el eyetracker
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

# Variables globales para almacenar la selección de ROI y los datos
start_point = None
end_point = None
drawing = False
roi_selected = False
ROI_FRAME = None
detected_pupil_position = None

# Listas para almacenar las coordenadas x, y y el tiempo
x_data = []
y_data = []
time_data = []

# Frecuencia de muestreo (en Hz)
sampling_frequency = 50  # 10 Hz = 10 muestras por segundo
sampling_interval = 1 / sampling_frequency  # Intervalo de muestreo en segundos

# Función para manejar los eventos del mouse
def select_roi(event, x, y, flags, param):
    global start_point, end_point, drawing, roi_selected, ROI_FRAME

    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (x, y)
        drawing = True
        roi_selected = False

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = [x, y]

    elif event == cv2.EVENT_LBUTTONUP:
        end_point = [x, y]
        drawing = False
        roi_selected = True
        ROI_FRAME = [start_point[0], start_point[1], end_point[0], end_point[1]]
        print(f"ROI_FRAME=[{ROI_FRAME[0]},{ROI_FRAME[1]},{ROI_FRAME[2]},{ROI_FRAME[3]}]")

# Función para detectar la pupila en el ROI
def detect_pupil_in_roi(frame, roi_coords):
    global detected_pupil_position
    x1, y1, x2, y2 = roi_coords
    roi = frame[y1:y2, x1:x2]

    if roi.size > 0:
        # Convertir el ROI a escala de grises
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        smoothed_roi = cv2.bilateralFilter(gray_roi, 9, 75, 75)
        edges = cv2.Canny(smoothed_roi, 50, 150)

        # Detección de círculos (pupila)
        circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                                   param1=100, param2=30, minRadius=10, maxRadius=60)

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            detected_pupil_position = (circles[0][0], circles[0][1])
            print(detected_pupil_position)
            for (x, y, r) in circles:
                # Dibujar el contorno del círculo (pupila) detectado
                cv2.circle(roi, (x, y), r, (0, 255, 0), 2)
                # Dibujar el centro del círculo
                cv2.circle(roi, (x, y), 2, (0, 0, 255), 3)

        # Mostrar el ROI con el círculo detectado
        cv2.imshow('Detección de Pupila en ROI', roi)

# Función para actualizar la gráfica
def update_graph(i):
    if detected_pupil_position is not None:
        # Actualizar los datos en las listas
        current_time = time.time() - start_time
        x_data.append(detected_pupil_position[0])
        y_data.append(detected_pupil_position[1])
        time_data.append(current_time)

        # Limitar el número de puntos en la gráfica (últimos 50)
        if len(x_data) > 50:
            x_data.pop(0)
            y_data.pop(0)
            time_data.pop(0)

        # Actualizar la gráfica
        ax1.clear()
        ax2.clear()
        ax1.plot(time_data, x_data, label="Coordenada X", color="blue")
        ax2.plot(time_data, y_data, label="Coordenada Y", color="red")

        ax1.set_title("Posición X en función del tiempo")
        ax2.set_title("Posición Y en función del tiempo")
        ax1.set_xlabel("Tiempo (s)")
        ax1.set_ylabel("X")
        ax2.set_xlabel("Tiempo (s)")
        ax2.set_ylabel("Y")

# Configuración inicial de la gráfica (solo aparecerá después de definir el ROI)
fig, (ax1, ax2) = plt.subplots(2, 1)
plt.subplots_adjust(hspace=0.5)

# Inicia la captura de video desde la cámara
cap = cv2.VideoCapture(0)

# Verifica si la cámara se abrió correctamente
if not cap.isOpened():
    print("Error: No se pudo acceder a la cámara.")
else:
    cv2.namedWindow('Cámara')
    cv2.setMouseCallback('Cámara', select_roi)

    # Loop principal para capturar frames y mostrar la detección de pupila
    while True:
        ret, frame = cap.read()

        if ret:
            # Dibuja un rectángulo durante la selección
            if start_point and end_point and drawing:
                cv2.rectangle(frame, start_point, end_point, (0, 255, 0), 2)

            # Detectar pupila en el ROI seleccionado
            if roi_selected and ROI_FRAME:
                detect_pupil_in_roi(frame, ROI_FRAME)

                # Una vez seleccionado el ROI, iniciar la animación de la gráfica
                if len(time_data) == 0:
                    start_time = time.time()  # Iniciar el conteo de tiempo
                    ani = FuncAnimation(fig, update_graph, interval=100, cache_frame_data=False)  # Inicia la animación

                plt.pause(0.001)  # Actualizar la gráfica en tiempo real

            cv2.imshow('Cámara', frame)

            # Si se presiona la tecla 'q', rompe el bucle y cierra la ventana
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Error: No se pudo capturar el frame.")
            break

# Libera la cámara y cierra las ventanas abiertas
cap.release()
cv2.destroyAllWindows()

