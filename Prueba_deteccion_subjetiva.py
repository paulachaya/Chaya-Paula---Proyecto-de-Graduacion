import threading
import tkinter as tk
import time
from screeninfo import get_monitors
import numpy as np
import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import Circle
import random as rd
import winsound
from queue import Queue
import keyboard
from collections import Counter


# ...............................................................Funciones de conversión.............................................................................

def px_a_mm_X(valor_en_px):
    return (0.3 * valor_en_px) - 195

def px_a_mm_Y(valor_en_px):
    return 105 + (0.3 * valor_en_px)

def mm_a_px_X(valor_en_mm):
    return int((valor_en_mm + 195) / 0.3)

def mm_a_px_Y(valor_en_mm):
    return int((valor_en_mm - 105) / (-0.3))

def grados_a_mm(valor):
    return valor*5.25

def mm_a_grados(valor):
    return(valor/5.25)

def Varduino_a_mm_X(ordenada_x, pendiente_x, valor_arduino):
    return ordenada_x + (valor_arduino * pendiente_x)

def Varduino_a_mm_Y(ordenada_y, pendiente_y, valor_arduino):
    return ordenada_y + (valor_arduino * pendiente_y)

def patron_nuevo(resultado_paciente):
    patron_nuevo_estimulos = []
    for i in range(len(resultado_paciente)):
        x = [coord[0] for coord in resultado_paciente][i]
        y = [coord[1] for coord in resultado_paciente][i]
        if resultado_paciente[i][-1:][0]==0:
            for j in range(len(resultado_paciente)):
                diferencia = [abs([coord[0] for coord in resultado_paciente][j]-x),
                              abs([coord[1] for coord in resultado_paciente][j]-y)]
                if (np.linalg.norm(diferencia))<grados_a_mm(3.5):
                    patron_nuevo_estimulos.append([[coord[0] for coord in resultado_paciente][j],
                                                   [coord[1] for coord in resultado_paciente][j]])
                    
    # Convertir la lista a un conjunto de tuplas para eliminar duplicados
    estimulos = list(set(tuple(vector) for vector in patron_nuevo_estimulos))
    # Convertir de nuevo a una lista de listas si es necesario
    estimulos = [list(vector) for vector in estimulos]
    return estimulos
        
# ...................................................Función para generar puntos de una circunferencia...........................................................

def generar_puntos_circunferencia(radio, lim1, lim2, num_puntos, centro=(0, 0)):
    angulos = np.linspace(lim1, lim2, num_puntos, endpoint=False)  # Ángulos distribuidos uniformemente
    x = centro[0] + radio * np.cos(angulos)  # Coordenadas X
    y = centro[1] + radio * np.sin(angulos)  # Coordenadas Y
    return x, y

#................................................. Función para generar el área del escotoma fisiológico ........................................................

def generar_puntos_circunferencia_escotoma(radio, num_puntos, centro=(0, 0)):
    angulos = np.linspace(0, 2 * np.pi, num_puntos, endpoint=False)  # Ángulos distribuidos uniformemente
    x = centro[0] + radio * np.cos(angulos)  # Coordenadas X
    y = centro[1] + radio * np.sin(angulos)  # Coordenadas Y
    return x, y

#................................................Funcion para presionar barra espaciadora.........................................................................
def on_space_press(event):
    global space_pressed
    space_pressed = True
def space_press():                  
    global space_pressed
    space_pressed = False
    tiempo_inicio = time.time()
    # Esperar un segundo
    while (time.time() - tiempo_inicio) <= 2:        
        if space_pressed:
            result=1
            time.sleep(0.5)
            break
    else:
        result = 0
    return result
#---------------------------------------------------------------- VENTANA DE PRUEBA -----------------------------------------------------------------------------

class VentanaPrueba(tk.Toplevel):
    def __init__(self, parent_canvas):
        super().__init__()
        self.parent_canvas = parent_canvas # Para graficar en la pantalla del Operario
        monitores = get_monitors()
        monitor = monitores[0]
        self.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")

        self.canvas = tk.Canvas(self, width=monitor.width,
                                height=monitor.height,
                                bg='black')
        self.canvas.pack()

   # Funcion para generar sonido en la prueba
    def beep1(self):
        winsound.Beep(1000,100)


    # Funcion para disminuir el tamaño de la cruz de fijación
    def reducir_tamano(self,ox,oy,largo):
        interval = 50 # Reducir el tamaño de la cruz
        largo -= 4  # Reducir el tamaño en 2 unidades
            # Actualizar las posiciones de las líneas de la cruz
        self.canvas.coords(self.line1, ox - largo, oy, ox + largo, oy)
        self.canvas.coords(self.line2, ox, oy - largo, ox, oy + largo)
            # Si el tamaño es mayor que 0, continuar reduciendo el tamaño
        if largo > 0:
            self.canvas.after(interval, lambda: self.reducir_tamano(ox,oy,largo))

                
    # Función de la prueba
    def prueba(self):

        # Genero vector con estímulos
        Estimulos = []
        estimulos = []
        radios = np.arange(7, 22, 3)
        lim1, lim2 = -np.pi / 4, np.pi / 4
        num_puntos = 1
        for i in range(len(radios)):
            x, y = generar_puntos_circunferencia(radios[i], lim1, lim2,
                                                 num_puntos, centro=(0, 0))
            num_puntos = num_puntos + 2
            for i in range(1,len(x)):
                Estimulos.append([x[i], y[i]])
                estimulos.append([grados_a_mm(x[i]), grados_a_mm(y[i])])
                Estimulos.append([-x[i], -y[i]])
                estimulos.append([grados_a_mm(-x[i]), grados_a_mm(-y[i])])


        # Mezclar el vector Estimulos y separar las coordenadas x e y
        np.random.shuffle(estimulos)
        print('Cantidad de estimulos:',len(Estimulos))
        estimulo_no_detectado = []
        largo, ancho = 30, 3
                
        for k in range(3): # 3 rondas de prueba
            #..............................................................   
            print(f'Ronda {k+1}')
            texto = f'Ronda {k+1}'
            center_x = self.canvas.winfo_width() // 2
            center_y = self.canvas.winfo_height() // 2
            self.canvas.create_text(center_x, center_y, text=texto,
                                    font=("Arial", 48), fill="white",
                                    anchor=tk.CENTER)
            time.sleep(10)
            self.canvas.delete('all')
            #...............................................................

            num_prueba = 0
            resultado_paciente = []
            ox,oy = 0,0 #Defino origen
            # Encontrar los valores máximos y mínimos para x y y
            Xmin0, Ymin0 = np.min(estimulos, axis=0)
            Xmax0, Ymax0 = np.max(estimulos, axis=0)        
            print('Limites X:',Xmin0,Xmax0)
            print('Limites Y:',Ymin0,Ymax0)

            x, y = estimulos[0][0], estimulos[0][1]#Llamo al primer estímulo

            estimulos.pop(0) #Elimino al primer estímulo
            color = 'white'
            print('Cantidad de estimulos para la ronda:', len(estimulos)+1)
            for i in range(len(Estimulos)):
                time.sleep(0.5)
                num_prueba += 1  # Para imprimir el número de prueba que estoy realizando

                # Grafico la cruz de fijación en la ventana de prueba
                self.line1 = self.canvas.create_line(mm_a_px_X(ox)- largo, mm_a_px_Y(oy),
                                                    mm_a_px_X(ox)+largo, mm_a_px_Y(oy),
                                                    fill=color, width=ancho)
                self.line2 = self.canvas.create_line(mm_a_px_X(ox), mm_a_px_Y(oy)-largo,
                                                    mm_a_px_X(ox), mm_a_px_Y(oy)+largo,
                                                    fill=color, width=ancho)
                self.reducir_tamano(mm_a_px_X(ox),mm_a_px_Y(oy),largo)
                                   
                # Grafico el estímulo en ventana de prueba
                self.canvas.after(1000, lambda: self.beep1())
                self.canvas.after(1200, lambda: self.canvas.create_oval(mm_a_px_X(x)-5,
                                                                        mm_a_px_Y(y)-5,
                                                                        mm_a_px_X(x)+5,
                                                                        mm_a_px_Y(y)+5,
                                                                        fill=color))
                self.canvas.after(1500, lambda: self.canvas.delete('all'))  # Mantengo el estímulo 20 ms
                self.canvas.after(2000, lambda: self.canvas.delete('all'))  

                    # Respuesta del paciente                
                tiempo = time.time()
                while (time.time() - tiempo) <= 2:
                    result = space_press()
                    space_pressed = False # Reset space_pressed after checking
                    keyboard.on_press_key("space", on_space_press)

                    if color == 'white':              
                        resultado_paciente.append([x-ox,y-oy,result])
                        if result == 0: # no detectó el estímulo
                            estimulo_no_detectado.append([x-ox,y-oy])

                    # Imprimo resultado
                    print(num_prueba, '/', 2 * len(Estimulos), ':', result)

                    # Defino nuevo origen de coordenadas
                    ox, oy = x,y

                    # Defino los nuevos límites
                    Xmin = Xmin0 - x
                    Xmax = Xmax0 - x
                    Ymin = Ymin0 - y
                    Ymax = Ymax0 - y

                    print('Nuevos límites X:',Xmin,Xmax)
                    print('Nuevos limites Y:',Ymin,Ymax)
                    # Busco el primer par (x,y) que se encuentre dentro de
                    # los nuevos límites
                    punto = None
                    indice = -1
                    for i, (X,Y) in enumerate(estimulos):
                        if Xmin <= X <= Xmax and Ymin <= Y <= Ymax:
                            x,y = X,Y
                            punto = (x,y)
                            indice = i
                            break
                    if punto is not None:
                        # Si se encontró un punto, se elimina de la lista
                        estimulos.pop(indice)
                        color = 'white'
                        print(f'El primer punto dentro del rango es {punto}')
                        print('cantidad de estimulos:',len(estimulos))
                    else:
                        x,y = 0,0
                        color = 'red'
                        print('No se encontró ningun punto dentro del rango')
                      
            # Armo el nuevo patrón de estimulos
            estimulos = patron_nuevo(resultado_paciente)


        texto = "Fin de la prueba"
        center_x = self.canvas.winfo_width() // 2
        center_y = self.canvas.winfo_height() // 2
        self.canvas.create_text(center_x, center_y, text=texto,
                                font=("Arial", 48), fill="white",
                                anchor=tk.CENTER)

#------------------------------------------------------------VENTANA USUARIO-----------------------------------------------------------------------------

class VentanaUsuario(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ventana Principal")
        self.geometry("300x100")

        self.boton_prueba = tk.Button(self, text="Iniciar prueba", command=self.iniciar_prueba)
        self.boton_prueba.pack(pady=20)

    def iniciar_prueba(self):
        self.prueba_window = VentanaPrueba(self)
        threading.Thread(target=self.prueba_window.prueba).start()

def main():
    app = VentanaUsuario()
    app.mainloop()

if __name__ == '__main__':
    main()



