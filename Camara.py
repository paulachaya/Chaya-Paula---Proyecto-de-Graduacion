import cv2
import numpy as np

# Carga los clasificadores Haar para detección de caras y ojos
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Inicia la captura de video desde la primera cámara (índice 0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se pudo acceder a la cámara.")
else:
     # Establece el tamaño de la imagen (por ejemplo, 640x480 píxeles)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1366)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)
    while True:
        ret, frame = cap.read()

        if ret:
            # Convierte a escala de grises para mejorar la detección
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detecta la cara en el frame
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            # Procesa cada cara detectada
            for (x, y, w, h) in faces:
                # Dibuja un rectángulo alrededor de la cara en la imagen en escala de grises
                cv2.rectangle(gray, (x, y), (x + w, y + h), (255, 0, 0), 2)

                 # Define la región de interés (ROI) para los ojos dentro de la cara detectada
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = frame[y:y + h, x:x + w]

                # Detecta los ojos dentro de la ROI
                eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 10)

                for (ex, ey, ew, eh) in eyes:
                    # Dibuja un rectángulo alrededor del ojo en la imagen en escala de grises
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

                    # Recorta la región del ojo
                    eye_roi = roi_gray[ey:ey + eh, ex:ex + ew]

                    # Aplica un desenfoque gaussiano para suavizar la imagen del ojo
                    blurred_eye = cv2.GaussianBlur(eye_roi, (7, 7), 0)

                    # Usa un umbral adaptativo para detectar la pupila
                    _, threshold_eye = cv2.threshold(blurred_eye, 50, 255, cv2.THRESH_BINARY_INV)

                    # Encuentra los contornos
                    contours, _ = cv2.findContours(threshold_eye, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                    # Itera sobre los contornos encontrados
                    for contour in contours:
                        # Filtra contornos pequeños que no sean relevantes
                        if cv2.contourArea(contour) > 30:
                            # Encuentra el centro y el radio del círculo más pequeño que contiene la pupila
                            (x_center, y_center), radius = cv2.minEnclosingCircle(contour)

                            # Dibuja un círculo alrededor de la pupila detectada
                            cv2.circle(roi_color, (int(ex + x_center), int(ey + y_center)), int(radius), (0, 0, 255), 2)

                            # Muestra la región binaria del ojo procesado
                            cv2.imshow('Pupila Detectada', threshold_eye)

            # Muestra el frame completo con la detección de cara y ojos
            cv2.imshow('Detección de cara y ojos con Pupila', frame)

            # Si se presiona 'q', rompe el bucle y cierra la ventana
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Error: No se pudo capturar el frame.")
            break

# Libera la cámara y cierra las ventanas abiertas
cap.release()
cv2.destroyAllWindows()