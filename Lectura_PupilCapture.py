# Lectura de PupilCapture

# Esta función establece una conexión con el software 
# PupilCapture para obtener los datos de la mirada
# (posición x e y normalizadas) en tiempo real.

import zmq
import msgpack
import time
import Funciones as F
import numpy as np

#   1era PARTE:
#       Se crea un socket tipo REQ para enviar solicitudes a PupilCapture.
#       Se solicita el puerto de suscripción (SUB_PORT) para lerr los
#     datos y el puerto de publicacion (PUB_PORT) para escribir datos.


# Crear un contexto de ZeroMQ
ctx = zmq.Context()

# El socket REQ se utiliza para hablar con Pupil Remote y recibir el puerto IPC SUB único de la sesión
pupil_remote = ctx.socket(zmq.REQ)

# Dirección IP del equipo que ejecuta Pupil Capture
ip = 'localhost'  
port = 50020  # El puerto por defecto es 50020, configurado en la GUI de Pupil Capture.

# Conectar al servidor de Pupil Remote.
pupil_remote.connect(f'tcp://{ip}:{port}')

# Solicitar el 'SUB_PORT' para leer los datos.
pupil_remote.send_string('SUB_PORT')
sub_port = pupil_remote.recv_string()

# Solicitar el 'PUB_PORT' para escribir datos.
pupil_remote.send_string('PUB_PORT')
pub_port = pupil_remote.recv_string()


#   2da PARTE:
#       Se crea un socket de tipo SUB para recibir mensajes.
#       El socket se conecta al puerto de suscripción proporcionado 
#     por PupilCapture y se suscribe a los mensajes de 'gaze', que 
#     contienen información sobre la posición de la mirada.


subscriber = ctx.socket(zmq.SUB)
subscriber.connect(f'tcp://{ip}:{sub_port}')
subscriber.subscribe('gaze.')  # Se suscribe a todos los mensajes de mirada ('gaze.')

#   'Lectura_PupilCapture':
#       Esta función depende de 3 variables 
#       -Tiempo: Cada etapa tiene un tiempo (s) diferente para el
#               registro de los datos.
#       -Etapa: Para la calibracion existen dos etapas (Calibración
#               y Validación) mientras que para la prueba de deteccioón
#               requiere de una etapa ('prueba'). Cada una de ellas trabaja 
#               con un tiempo de registro diferente.
#       -Queue: (cola) es una estructura de datos que se utiliza para que
#               un hilo o proceso pueda guardar datos que luego otro
#               hilo o proceso puede recuperar y usar, garantizando 
#               que no haya problemas de sincronización ni bloqueos
#               en el programa.
#       -Rectas: Lista con valores de ordenadas y pendientes
#                En caso de 'calibracion' se define esta lista
#                como tupla de ceros.
def Lectura_PupilCapture(tiempo,etapa,rectas,queue,):
    print('Inicianzo lectura...')
    lectura = [] #Lista para guardar los datos 
    tiempo_inicio = time.time() #Defino t=0
    total=0
    # Bucle de 'T' segundos para recibir y procesar los mensajes en tiempo real
    while (time.time() - tiempo_inicio) <= tiempo:
        # Recibir el tópico y el mensaje serializado
        topic, payload = subscriber.recv_multipart()
        
        # Deserializar el mensaje usando msgpack
        message = msgpack.loads(payload)

        # Lectura solamente de coordenadas X e Y
        # Extraer las coordenadas x, y (posiciones
        # normalizadas)
        norm_pos = message.get(b'norm_pos', None)
        x, y = norm_pos
        if 0 <= x <= 1 and 0 <= y <= 1:
            total += 1

            if etapa=='calibracion': # primera etapa
                lectura.append([x,y]) #Sólo se guardan los valores normalizados
            
            else: # Etapas de validacion y prueba
                ord_x,pend_x,ord_y,pend_y = rectas
                lectura.append([F.valor_eyetracker_a_mm_X(ord_x,pend_x,x),
                                F.valor_eyetracker_a_mm_Y(ord_y,pend_y,y)])
            
            if len(lectura) > 50: # Sólo trabaja con los ultimos 50 datos
                lectura.pop(0)
            #print(f"Coordenadas (x): ({x}, {y})\n")

        else:
            print("Advertencia: Coordenadas fuera de los límites normales (0, 1)\n")
            total += 1 
        time.sleep(0.01)
    print('Cantidad de datos recolectados:',len(lectura))
    print('Cantidad total de datos:',total)
    lectura = [np.mean([coord[0] for coord in lectura]), np.mean([coord[1] for coord in lectura])]
    print(lectura)
    print('Lectura de datos finalizada.')
    queue.append(lectura)