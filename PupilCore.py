# El siguiente código  establece una conexión con el software
# de captura de Pupil Labs (Pupil Capture) utilizando el protocolo
#  ZeroMQ (zmq) para obtener datos de gaze (mirada) en tiempo real.

import zmq
# Necesito un deserializador
import msgpack

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


# Bucle infinito para recibir y procesar los mensajes en tiempo real
while True:
    # Recibir el tópico y el mensaje serializado
    topic, payload = subscriber.recv_multipart()
    
    # Deserializar el mensaje usando msgpack
    message = msgpack.loads(payload)
    
    # Imprimir el tópico y el mensaje recibido (que contiene TODOS los datos de mirada)
    #print(f"{topic}: {message}\n")

    # Lectura solamente de coordenadas X e Y
    # Extraer las coordenadas x, y de norm_pos
    norm_pos = message.get(b'norm_pos', None)
    x, y = norm_pos
    if 0 <= x <= 1 and 0 <= y <= 1:
        print(f"Coordenadas (x): ({x}, {y})\n")
    else:
        print("Advertencia: Coordenadas fuera de los límites normales (0, 1)\n")
    
