import cv2
import numpy as np
import time

# Variable global para almacenar la posición de la pupila
pupil_data = None

# Función del eyetracker
def eyetracker():
    global pupil_data

    # Define las coordenadas del ROI
    ROI_FRAME = [179, 146, 442, 303]
    x1, y1 = ROI_FRAME[0], ROI_FRAME[1]
    x2, y2 = ROI_FRAME[2], ROI_FRAME[3]

    # Inicia la captura de video desde la cámara
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara.")
        return

    while True:
        ret, frame = cap.read()
        if ret:
            # Extrae la región seleccionada como ROI
            roi = frame[y1:y2, x1:x2]

            if roi.size > 0:
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                smoothed_roi = cv2.bilateralFilter(gray_roi, 9, 75, 75)
                edges = cv2.Canny(smoothed_roi, 50, 150)

                # Usa la detección de círculos de Hough
                circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                                            param1=100, param2=30, minRadius=10, maxRadius=60)

                if circles is not None:
                    circles = np.round(circles[0, :]).astype("int")
                    # Guarda la posición de la pupila
                    pupil_data = (circles[0][0], circles[0][1])

                    # Dibuja el círculo en la imagen
                    cv2.circle(roi, (circles[0][0], circles[0][1]), circles[0][2], (0, 255, 0), 2)
                    cv2.circle(roi, (circles[0][0], circles[0][1]), 2, (0, 0, 255), 3)

            # Muestra la imagen del ROI
            cv2.imshow('Detección de Pupila en ROI', roi)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Error: No se pudo capturar el frame.")
            break

    cap.release()
    cv2.destroyAllWindows()

# Función de calibración que usa los datos de la pupila
def calibracion():
    global pupil_data
    while True:
        if pupil_data is not None:
            print(f"Datos de la pupila recibidos: {pupil_data}")
        time.sleep(2)  # Simula que esta función necesita los datos cada 2 segundos

# Ejecutar ambas funciones en paralelo sin sockets ni multiprocessing
if __name__ == "__main__":
    eyetracker()
    calibracion()
