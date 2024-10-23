import cv2
import numpy as np
import time
import Funciones as F


# Variables globales para almacenar la posición de la pupila
detected_pupil_position = None
ROI_FRAME=[176,193,425,315]
# Frecuencia de muestreo en Hz (muestras por segundo)
sampling_frequency = 50  # Puedes ajustar esta frecuencia a tu necesidad (en Hz)
sampling_interval = 1 / sampling_frequency  # Intervalo de tiempo entre muestras

# Función del eyetracker
def eyetracker():
    global detected_pupil_position

    # Define las coordenadas del ROI
    x1, y1 = ROI_FRAME[0], ROI_FRAME[1]  # Esquina superior izquierda
    x2, y2 = ROI_FRAME[2], ROI_FRAME[3]  # Esquina inferior derecha

    # Inicia la captura de video desde la cámara infrarroja
    cap = cv2.VideoCapture(0)

    # Verifica si la cámara se abrió correctamente
    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara.")
        return

    while True:
        start_time = time.perf_counter()  # Marca el inicio del bucle con mayor precisión

        ret, frame = cap.read()
        if ret:
            # Extrae la región seleccionada como ROI
            roi = frame[y1:y2, x1:x2]

            if roi.size > 0:
                # Convierte el ROI a escala de grises (necesario para binarización)
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                
                # Aplica un umbral binario para obtener una imagen en blanco y negro
                _, binary_roi = cv2.threshold(gray_roi, 100, 255, cv2.THRESH_BINARY)

                # Usa la detección de círculos de Hough para encontrar la pupila en la imagen binaria
                circles = cv2.HoughCircles(binary_roi, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                                           param1=50, param2=15, minRadius=10, maxRadius=60)

                if circles is not None:
                    circles = np.round(circles[0, :]).astype("int")
                    # Guarda la posición del centro del primer círculo detectado
                    detected_pupil_position = (2 * circles[0][0], 2 * circles[0][1])

                    # Dibuja el círculo detectado en el ROI binario
                    for (x, y, r) in circles:
                        cv2.circle(roi, (x, y), r, (0, 255, 0), 2)  # Dibuja el contorno del círculo
                        cv2.circle(roi, (x, y), 2, (0, 0, 255), 3)  # Dibuja el centro del círculo

                # Muestra la imagen del ROI binario con el círculo detectado
                cv2.imshow('Detección de Pupila en ROI Binario', binary_roi)

            # Muestra el frame original
            cv2.imshow('Cámara', frame)

            # Espera a que se presione 'q' para salir
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Error: No se pudo capturar el frame.")
            break

        # Controla la frecuencia de muestreo con mayor precisión
        elapsed_time = time.perf_counter() - start_time
        if elapsed_time < sampling_interval:
            time.sleep(sampling_interval - elapsed_time)

    cap.release()
    cv2.destroyAllWindows()


def Lectura(tiempo, etapa, rectas, queue):
    tiempo_inicio = time.perf_counter()  # Usa perf_counter para más precisión
    datos = []
    intervalo_muestreo = 1 / sampling_frequency  # Intervalo de muestreo en segundos
    time.sleep(0.1)

    while (time.perf_counter() - tiempo_inicio) <= tiempo:
        start_time = time.perf_counter()  # Marca el tiempo de inicio del ciclo
        if detected_pupil_position is not None:
            try:
                x, y = detected_pupil_position[0], detected_pupil_position[1]

                if etapa == 'validacion':
                    if len(datos) > 50:  # sólo trabajo con los últimos 50 datos
                        datos.pop(0)
                    ord_x, pend_x, ord_y, pend_y = rectas
                    datos.append([F.valor_eyetracker_a_mm_X(ord_x, pend_x, x),
                                  F.valor_eyetracker_a_mm_Y(ord_y, pend_y, y)])

                elif etapa == 'calibracion':
                    if len(datos) > 50:  # sólo trabajo con los últimos 50 datos
                        datos.pop(0)
                    datos.append([x, y])

                elif etapa == 'Eyetracker': #Prueba de deteccion
                    ord_x, pend_x, ord_y, pend_y = rectas
                    datos.append([F.valor_eyetracker_a_mm_X(ord_x, pend_x, x),
                                  F.valor_eyetracker_a_mm_Y(ord_y, pend_y, y)])

            except ValueError:
                print('Error')

        # Controla la tasa de muestreo
        elapsed_time = time.perf_counter() - start_time
        if elapsed_time < intervalo_muestreo:
            time.sleep(intervalo_muestreo - elapsed_time)

    if etapa == 'calibracion' or etapa == 'validacion':
        datos = [np.mean([coord[0] for coord in datos]), np.mean([coord[1] for coord in datos])]
        print(f'Eyetracker: {datos}\n')

    queue.append(datos)

     

eyetracker()