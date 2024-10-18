import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import Circle
import winsound
import time
import random as rd
import keyboard

#   Funciones de conversion para las pruebas de deteccion
def px_a_mm_X(valor_en_px):
    return (0.2941 * valor_en_px) - 200

def px_a_mm_Y(valor_en_px):
    return 110 - (0.2865 * valor_en_px)

def mm_a_px_X(valor_en_mm):
    return int((valor_en_mm + 200) / 0.2941)

def mm_a_px_Y(valor_en_mm):
    return int((valor_en_mm - 110) / (-0.2865))

def grados_a_mm(valor):
    return valor*5.25

def mm_a_grados(valor):
    return(valor/5.25)

def valor_eyetracker_a_mm_X(ord_x, pend_x, valor):
    return ord_x + (valor * pend_x)

def valor_eyetracker_a_mm_Y(ord_y, pend_y, valor):
    return ord_y + (valor * pend_y)

# Funcion de analisis prueba objetiva
def analisis(estimulo_x,estimulo_y,valor_x,valor_y):
    if ((abs(valor_x - estimulo_x) < 30)
        and (abs(valor_y - estimulo_y) < 30)): 
        return 1  
    else:
        return 0

# Funcion de validez prueba objetiva
def validez_de_prueba(valor_x,valor_y):
    if (abs(valor_x)<30) and (abs(valor_y)<30):
        return 1
    else:
        return 0

# Funcion para generar puntos para el patrón de estimulos
def generar_puntos_circunferencia(radio, lim1, lim2, num_puntos, centro=(0, 0)):
    angulos = np.linspace(lim1, lim2, num_puntos, endpoint=False)  
    x = centro[0] + radio * np.cos(angulos) 
    y = centro[1] + radio * np.sin(angulos) 
    return x, y

# Funcion para graficar el resultado a partir de la lista de valores
# xy que corresponden a los estimulos no detectados durante la prueba
def Grafica_resultado(Sujeto,Ojo,estimulo_no_detectado):        
        # Genero el perímetro del escotoma fisiológico
        if Ojo == 'Derecho':
            ex, ey = generar_puntos_circunferencia(3,0,2*np.pi, 100, centro=(15, 0))
        else:
            ex, ey = generar_puntos_circunferencia(3,0,2*np.pi, 100, centro=(-15, 0))
            
        plt.figure(figsize=(15,10))
        plt.hist2d(mm_a_grados(np.array([coord[0] for coord in estimulo_no_detectado])),
                   mm_a_grados(np.array([coord[1] for coord in estimulo_no_detectado])),
                   bins=[30, 10], cmap='Greys')
        plt.plot(ex,ey)
        plt.colorbar(label='Frecuencia')
        plt.xlim(-25,25);plt.ylim(-17,17)
        plt.grid(True,axis='both')
        # Añadir circunferencias de cuadrícula
        for i in range(0, 30):
            circulo = Circle((0, 0), i,linestyle='-',facecolor='none',edgecolor='grey')        
            plt.gca().add_artist(circulo)

        plt.title(f'Resultado final Sujeto {Sujeto} Ojo {Ojo}')
        plt.xlabel('Valor X');plt.ylabel('Valor Y')
        plt.show()

# Funcion para generar sonido
def beep1():
    winsound.Beep(1000,300)
def beep2():
        frequency = 2000  
        duration = 200  
        for _ in range(3):
            winsound.Beep(frequency, duration)
            time.sleep(1)

# Funcion para generar un patron de vectores
def Patron_vectores(radios,lim1,lim2,num_puntos):
    vectores = []
   # radios,lim1,lim2,num_puntos = np.arange(7, 22, 3), -np.pi / 4, np.pi / 4, 3
    for r in radios:
        x, y = generar_puntos_circunferencia(r, lim1, lim2,
                                            num_puntos, centro=(0, 0))
        num_puntos = num_puntos + 2
        for i in range(1,len(x)):
            vectores.append([grados_a_mm(x[i]), grados_a_mm(y[i])])
            vectores.append([grados_a_mm(-x[i]), grados_a_mm(-y[i])])
    return vectores

# Funcion para filtrar el patrón de vectores
def patron_nuevo(resultado_paciente):
    patron_nuevo = []
    for i in range(len(resultado_paciente)):
        x = [coord[0] for coord in resultado_paciente][i]
        y = [coord[1] for coord in resultado_paciente][i]
        
        if resultado_paciente[i][-1:][0]==0:
            for j in range(len(resultado_paciente)):
                diferencia = [abs([coord[0] for coord in resultado_paciente][j]-x),
                              abs([coord[1] for coord in resultado_paciente][j]-y)]
                if (np.linalg.norm(diferencia))<grados_a_mm(3.5):
                    patron_nuevo.append([[coord[0] for coord in resultado_paciente][j],
                                                   [coord[1] for coord in resultado_paciente][j]])
        else:
            if resultado_paciente[i][-1:][0]== 'No válido':
                patron_nuevo.append([x,y])    
    # Convertir la lista a un conjunto de tuplas para eliminar duplicados
    vectores = list(set(tuple(vector) for vector in patron_nuevo))
    # Convertir de nuevo a una lista de listas si es necesario
    vectores = [list(vector) for vector in vectores]
    return vectores

#######################################################################################
# Funcion lectura de arduino
def lectura_arduino(tiempo,etapa,rectas,queue):
    #print('Iniciando lectura de datos...')
    lectura = []
    # Inicia el tiempo de lectura del arduino (4 segundos)
    tiempo_inicio = time.time()
    while (time.time() - tiempo_inicio) <= tiempo: 
        v1,v2 = rd.randint(-450,450),rd.randint(-450,450)
        line = f'{v1},{v2}' 
        if line:
            valores = line.split(',')
            # Verifico que la línea venga con dos valores (x,y) 
            if len(valores)==2:
                try:
                    valores = [int(valor) for valor in valores]
                    if etapa=='validacion':
                        # En la etapa de validacion, se usan las rectas
                        # calculadas anteriormente.
                        #  rectas = [self.ord_x, self.pend_x, self.ord_y, self.pend_y]
                        ord_x, pend_x, ord_y, pend_y = rectas
                        lectura.append([valor_eyetracker_a_mm_X(ord_x, pend_x, valores[0]),
                                        valor_eyetracker_a_mm_Y(ord_y, pend_y, valores[1])]) 
                    else:
                        if len(lectura) > 50:
                            lectura.pop(0)
                        lectura.append([valores[0],valores[1]])
                except ValueError:
                        print("Error al convertir valores:", valores)
    lectura = [np.mean([coord[0] for coord in lectura]), np.mean([coord[1] for coord in lectura])]
    print(f'Eyetracker:{lectura}\n')
    #print('Lectura de datos finalizada.')
    queue.append(lectura)
####################################################################################################

#Funcion de teclado para prueba de deteccion subjetiva
def teclado(i, cant_total,resultado):
    tiempo = time.time()
    print('arranco')
    while (time.time() - tiempo) <= 3:
        try:
            if keyboard.is_pressed('space'):
                resultado = 1
                print('tecla presionada')
                time.sleep(0.5)
                break
        except:
            break
    print(f'{i}/{cant_total}:{resultado}\n')
