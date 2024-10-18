import cv2
import numpy as np
import time
import Funciones as F



# Variables globales para almacenar la posición de la pupila
detected_pupil_position = None
ROI_FRAME = [126, 123, 501, 362]

# Frecuencia de muestreo en Hz (muestras por segundo)
sampling_frequency = 30  # Puedes ajustar esta frecuencia a tu necesidad (en Hz)
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
        start_time = time.time()  # Marca el inicio del bucle

        ret, frame = cap.read()
        if ret:
            # Extrae la región seleccionada como ROI
            roi = frame[y1:y2, x1:x2]

            if roi.size > 0:
                # Convierte el ROI a escala de grises y realiza procesamiento
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                smoothed_roi = cv2.bilateralFilter(gray_roi, 9, 75, 75)
                edges = cv2.Canny(smoothed_roi, 50, 150)

                # Usa la detección de círculos de Hough para encontrar la pupila
                circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                                           param1=100, param2=30, minRadius=10, maxRadius=60)

                if circles is not None:
                    circles = np.round(circles[0, :]).astype("int")
                    # Guarda la posición del centro del primer círculo detectado
                    detected_pupil_position = (2*circles[0][0], 2*circles[0][1])
                    #print(detected_pupil_position)
                    # Dibuja el círculo detectado en el ROI
                    for (x, y, r) in circles:
                        cv2.circle(roi, (x, y), r, (0, 255, 0), 2)  # Dibuja el contorno del círculo
                        cv2.circle(roi, (x, y), 2, (0, 0, 255), 3)  # Dibuja el centro del círculo

                # Muestra la imagen del ROI con el círculo detectado
                cv2.imshow('Detección de Pupila en ROI', roi)

            # Muestra el frame original
            cv2.imshow('Cámara', frame)

            # Espera a que se presione 'q' para salir
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Error: No se pudo capturar el frame.")
            break

        # Controla la frecuencia de muestreo
        elapsed_time = time.time() - start_time
        if elapsed_time < sampling_interval:
            time.sleep(sampling_interval - elapsed_time)

    cap.release()
    cv2.destroyAllWindows()


def Lectura(tiempo,etapa,rectas,queue):
    tiempo_inicio = time.time()
    datos = []
    time.sleep(0.01)
    while (time.time()-tiempo_inicio)<=tiempo:
        try:
            x,y = detected_pupil_position[0],detected_pupil_position[1]
            #print(detected_pupil_position)

            if etapa=='validacion':
                if len(datos)>20: # sólo trabajo con los ultimos 50 datos
                    datos.pop(0)
                ord_x, pend_x, ord_y, pend_y = rectas
                #datos.append([F.valor_eyetracker_a_mm_X(ord_x, pend_x, x),
                #              F.valor_eyetracker_a_mm_Y(ord_y, pend_y, y)])
                datos.append([F.valor_eyetracker_a_mm_X(ord_x, pend_x, x),
                              F.valor_eyetracker_a_mm_Y(ord_y, pend_y, y)])
                 
            if etapa=='calibracion': 
                if len(datos)>20: # sólo trabajo con los ultimos 50 datos
                    datos.pop(0)       
                datos.append([x,y])

            if etapa=='prueba':
                datos.append([x,y])

        except ValueError:
            print('Error')

    if etapa=='calibracion' or etapa=='validacion':
        datos = [np.mean([coord[0] for coord in datos]), np.mean([coord[1] for coord in datos])]
    print(f'Eyetracker:{datos}\n')
    queue.append(datos)

#eyetracker()