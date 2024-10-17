import cv2
import numpy as np

# Variables globales para almacenar la selección de ROI
roi_selected = False
roi = None
start_point = None
end_point = None
drawing = False

# Función para manejar los eventos del mouse
def select_roi(event, x, y, flags, param):
    global roi_selected, roi, start_point, end_point, drawing
    
    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (x, y)
        drawing = True
    
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = (x, y)
    
    elif event == cv2.EVENT_LBUTTONUP:
        end_point = (x, y)
        drawing = False
        roi_selected = True

# Inicia la captura de video desde la cámara infrarroja
cap = cv2.VideoCapture(0)

# Verifica si la cámara se abrió correctamente
if not cap.isOpened():
    print("Error: No se pudo acceder a la cámara.")
else:
    cv2.namedWindow('Cámara')
    cv2.setMouseCallback('Cámara', select_roi)

    while True:
        # Captura frame por frame
        ret, frame = cap.read()

        if ret:
            # Si el ROI ha sido seleccionado, ajusta la región de interés
            if roi_selected and start_point and end_point:
                # Extrae la región seleccionada como ROI
                x1, y1 = start_point
                x2, y2 = end_point
                roi = frame[y1:y2, x1:x2]

                if roi.size > 0:
                    # Convierte el ROI a escala de grises
                    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

                    # Aplica un filtro bilateral para suavizar la imagen y mantener los bordes nítidos
                    smoothed_roi = cv2.bilateralFilter(gray_roi, 9, 75, 75)

                    # Aplica la detección de bordes para resaltar áreas de alto contraste
                    edges = cv2.Canny(smoothed_roi, 50, 150)

                    # Usa la detección de círculos de Hough para encontrar la pupila y el reflejo
                    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                                               param1=100, param2=30, minRadius=10, maxRadius=60)

                    detected_pupil_position = None  # Inicializa la variable

                    # Si se detectan círculos
                    if circles is not None:
                        circles = np.round(circles[0, :]).astype("int")

                        # Dibuja los círculos detectados y guarda la posición de la pupila
                        for (x, y, r) in circles:
                            detected_pupil_position = (x, y)  # Guarda la posición del centro del círculo
                            # Dibuja el contorno del círculo
                            cv2.circle(roi, (x, y), r, (0, 255, 0), 2)
                            # Dibuja el centro del círculo
                            cv2.circle(roi, (x, y), 2, (0, 0, 255), 3)

                    # Imprime la posición de la pupila detectada
                    if detected_pupil_position is not None:
                        print(f"Posición de la pupila: {detected_pupil_position}")

                    # Muestra la imagen del ROI sin deformación y con bordes detectados
                    cv2.imshow('Detección de Pupila en ROI', roi)

            # Muestra el frame original y permite seleccionar ROI
            if start_point and end_point and not roi_selected:
                cv2.rectangle(frame, start_point, end_point, (0, 255, 0), 2)

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
