import cv2
import numpy as np
import time

# Variables globales para almacenar la selección de ROI y el zoom
start_point = None
end_point = None
drawing = False
roi_selected = False
zoom_factor = 2  # Puedes cambiar este valor para aumentar o reducir el zoom
ROI_FRAME = None
detected_pupil_position = None

# Frecuencia de muestreo en segundos
sampling_rate = 0.  # Cambiar este valor según sea necesario (0.5 = 500 ms)

# Función para manejar los eventos del mouse
def select_roi(event, x, y, flags, param):
    global start_point, end_point, drawing, roi_selected, ROI_FRAME

    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (x, y)
        drawing = True
        roi_selected = False

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        end_point = (x, y)
        drawing = False
        roi_selected = True

        # Define el ROI inicial con las coordenadas seleccionadas
        x1, y1 = start_point
        x2, y2 = end_point
        width = x2 - x1
        height = y2 - y1

        # Calcula el centro del ROI
        center_x = x1 + width // 2
        center_y = y1 + height // 2

        # Aplica el factor de zoom uniformemente
        new_width = int(width * zoom_factor)
        new_height = int(height * zoom_factor)

        # Calcula las nuevas coordenadas del ROI ajustado
        x1 = center_x - new_width // 2
        y1 = center_y - new_height // 2
        x2 = center_x + new_width // 2
        y2 = center_y + new_height // 2

        # Ajusta las coordenadas para que no excedan los límites de la imagen
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(frame.shape[1], x2)
        y2 = min(frame.shape[0], y2)

        # Guarda el nuevo ROI ajustado
        ROI_FRAME = [x1, y1, x2, y2]
        print(f"ROI ajustado con zoom: {ROI_FRAME}")

# Función para detectar la pupila en el ROI
def detect_pupil(roi):
    global detected_pupil_position
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    smoothed_roi = cv2.bilateralFilter(gray_roi, 9, 75, 75)
    edges = cv2.Canny(smoothed_roi, 50, 150)

    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                               param1=100, param2=30, minRadius=10, maxRadius=60)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        detected_pupil_position = (circles[0][0], circles[0][1])
        # Dibuja el círculo detectado en el ROI
        for (x, y, r) in circles:
            cv2.circle(roi, (x, y), r, (0, 255, 0), 2)
            cv2.circle(roi, (x, y), 2, (0, 0, 255), 3)  # Centro del círculo

# Inicia la captura de video desde la cámara
cap = cv2.VideoCapture(0)

# Verifica si la cámara se abrió correctamente
if not cap.isOpened():
    print("Error: No se pudo acceder a la cámara.")
else:
    cv2.namedWindow('Cámara')
    cv2.setMouseCallback('Cámara', select_roi)

    last_sample_time = time.time()

    while True:
        ret, frame = cap.read()

        if ret:
            # Dibuja un rectángulo durante la selección del ROI
            if start_point and end_point and drawing:
                cv2.rectangle(frame, start_point, end_point, (0, 255, 0), 2)
            elif roi_selected and ROI_FRAME:
                x1, y1, x2, y2 = ROI_FRAME

                # Extrae el ROI de la imagen original
                roi = frame[y1:y2, x1:x2]

                if time.time() - last_sample_time >= sampling_rate:
                    # Detecta la pupila dentro del ROI y actualiza el tiempo de muestreo
                    detect_pupil(roi)
                    last_sample_time = time.time()

                # Muestra el ROI con la pupila detectada
                cv2.imshow('Detección de Pupila en ROI', roi)

            # Muestra la imagen de la cámara
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
