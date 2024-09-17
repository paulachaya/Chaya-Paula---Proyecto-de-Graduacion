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
import pandas as pd
# __ Funciones de conversión __

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

# __ Funcion para generar los patrones de estimulos __

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
    estimulos = [list(vector) for vector in estimulos]
    return estimulos
        
# __ Función para generar puntos de una circunferencia __

def generar_puntos_circunferencia(radio, lim1, lim2, num_puntos, centro=(0, 0)):
    angulos = np.linspace(lim1, lim2, num_puntos, endpoint=False)  
    x = centro[0] + radio * np.cos(angulos) 
    y = centro[1] + radio * np.sin(angulos) 
    return x, y

# __ Funcion para presionar barra espaciadora __

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

#___________ VENTANA DE PRUEBA _____________

class VentanaPrueba(tk.Toplevel):
    def __init__(self, parent_canvas):
        super().__init__()
        self.parent_canvas = parent_canvas # Para graficar en la pantalla del Operario
        monitores = get_monitors()
        if len(monitores) > 1:
            segundo_monitor = monitores[1]
            print(segundo_monitor.width,segundo_monitor.height)
            
            self.geometry(f"{segundo_monitor.width}x{segundo_monitor.height}+{segundo_monitor.x}+{segundo_monitor.y}")

        self.canvas = tk.Canvas(self, width=segundo_monitor.width,
                                height=segundo_monitor.height,
                                bg='black')
        self.canvas.pack()
    

    # __ Funcion para generar sonido en la prueba __
    def beep1(self):
        winsound.Beep(1000,100)

    # __ Funcion para disminuir el tamaño de la cruz de fijación __
    def reducir_tamano(self,ox,oy,largo):
        interval = 50 # Reducir el tamaño de la cruz
        largo -= 4 
            # Actualizar las posiciones de las líneas de la cruz
        self.canvas.coords(self.line1, ox - largo, oy, ox + largo, oy)
        self.canvas.coords(self.line2, ox, oy - largo, ox, oy + largo)
            # Si el tamaño es mayor que 0, continuar reduciendo el tamaño
        if largo > 0:
            self.canvas.after(interval, lambda: self.reducir_tamano(ox,oy,largo))

    # Funcion para graficar el resultado
    def Grafica_resultado(self, Sujeto,Ojo,estimulo_no_detectado):
        
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


    # __ Función de la prueba __
    def prueba(self):
        # Genero vector con estímulos
        Estimulos_grafica,estimulos = [],[]
        radios,lim1,lim2,num_puntos = np.arange(7, 22, 3), -np.pi / 4, np.pi / 4, 3
        for i in range(len(radios)):
            x, y = generar_puntos_circunferencia(radios[i], lim1, lim2,
                                                 num_puntos, centro=(0, 0))
            num_puntos = num_puntos + 2
            for i in range(1,len(x)):
                estimulos.append([grados_a_mm(x[i]), grados_a_mm(y[i])])
                estimulos.append([grados_a_mm(-x[i]), grados_a_mm(-y[i])])
                Estimulos_grafica.append([grados_a_mm(x[i]), grados_a_mm(y[i])])
                Estimulos_grafica.append([grados_a_mm(-x[i]), grados_a_mm(-y[i])])
        cantidad_inicial_de_estimulos = len(estimulos)
        for k in range(3):
#       ......................... TEXTO ...............................  
            print(f'Ronda {k+1}')
            texto = f'Ronda {k+1}'
            center_x = self.canvas.winfo_screenwidth() /2
            center_y = self.canvas.winfo_screenheight()/2
            self.canvas.create_text(center_x, center_y, text=texto,
                                    font=("Arial", 48), fill="white",
                                    anchor=tk.CENTER)
            time.sleep(2)
            self.canvas.delete('all')
#       ...............................................................
            cantidad_total_estimulos = len(estimulos)
            Xmin, Ymin = np.min(estimulos, axis=0)
            Xmax, Ymax = np.max(estimulos, axis=0) 
            print('Limites X:',Xmin,Xmax)
            print('Limites Y:',Ymin,Ymax)
            # Mezclar el vector de estimulos
            np.random.shuffle(estimulos)
            print('Cantidad de estimulos:',cantidad_total_estimulos)
            estimulo_no_detectado, resultado_paciente = [], []
            largo, ancho = 30, 3
            num_prueba = 0
            ox,oy = 0,0 
            color = 'white'
            for i in range(cantidad_total_estimulos):
                punto, indice = None, -1
                for j, (X,Y) in enumerate(estimulos):
                    if (Xmin < X < Xmax) and (Ymin < Y < Ymax):
                        x,y = X ,Y
                        punto, indice = (x,y), j
                        break
                if punto is not None:
                    # Si se encontró un punto, se elimina de la lista
                    estimulos.pop(indice)
                    color = 'white'
                    print(f'El primer punto dentro del rango es {punto}')
                    print('cantidad de estimulos:',len(estimulos))
                else:
                    x,y = -ox,-oy
                    color = 'red'
                    print('No se encontró ningun punto dentro del rango')
                time.sleep(0.5)
                num_prueba += 1  # Para imprimir el número de prueba que estoy realizando
                Xmin, Xmax = Xmin - x, Xmax - x
                Ymin, Ymax = Ymin - y, Ymax - y
                x,y = x+ox, y+oy
                print('origen en', ox, oy)
                print('Coordenada:',x,y)
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
                self.canvas.after(1500, lambda: self.canvas.delete('all')) 
                self.canvas.after(2000, lambda: self.canvas.delete('all'))  

                # Respuesta del paciente                
                tiempo = time.time()
                while (time.time() - tiempo) <= 2:
                    result = space_press()
                    space_pressed = False 
                    keyboard.on_press_key("space", on_space_press)

                    if color == 'white':              
                        resultado_paciente.append([x-ox,y-oy,result])
                        if result == 0: # no detectó el estímulo
                            estimulo_no_detectado.append([x-ox,y-oy])

                    # Imprimo resultado
                    print(num_prueba, '/',cantidad_total_estimulos, ':', result)
                    # Defino nuevo origen de coordenadas
                    # y los nuevos límites

                    ox, oy = x,y 

                    print('Nuevos límites X:',Xmin,Xmax)
                    print('Nuevos limites Y:',Ymin,Ymax)
                    # Busco el primer par (x,y) que se encuentre
                    # dentro de los nuevos límites
                    
                    
                      
            # Armo el nuevo patrón de estimulos
            estimulos = patron_nuevo(resultado_paciente)

        texto = "Fin de la prueba"
        center_x = self.canvas.winfo_width() // 2
        center_y = self.canvas.winfo_height() // 2
        self.canvas.create_text(center_x, center_y, text=texto,
                                font=("Arial", 48), fill="white",
                                anchor=tk.CENTER)
        
        Sujeto = input('Ingrese numero de participante:')
        Ojo = input('Ojo Derecho/Izquierdo:')
        # Agrego los estimulos no detectados a la lista Estimulos_grafica
        for x,y in estimulo_no_detectado:
            Estimulos_grafica.append([x,y])
        # cuento la frecuencia de cada par xy
        vector = [tuple(coord) for coord in Estimulos_grafica]
        frecuencias = Counter(vector)
        # Convierto los datos en una tabla
        datos = [(x,y,freq-1) for (x,y),freq in frecuencias.items()]
        tabla = pd.DataFrame(datos, columns=['coordenada x [mm]',
                                             'coordenada y [mm]',
                                             'frecuencia de fallos'])
        #Guardo los datos en un archivo .csv
        tabla.to_csv(f'Pruebas\Pruebas subjetivas\Sujeto_{Sujeto}_{Ojo}.csv',index = False, sep=';')

        #Llamo a la función de gráfica
        self.Grafica_resultado(Sujeto,Ojo,estimulo_no_detectado)


            


#_____________________VENTANA USUARIO_____________________

class VentanaUsuario(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ventana Principal")
        self.geometry("300x100")
        self.boton_prueba = tk.Button(self, text="Iniciar prueba",
                                       command=self.iniciar_prueba)
        self.boton_prueba.pack(pady=20)

    def iniciar_prueba(self):
        self.prueba_window = VentanaPrueba(self)
        threading.Thread(target=self.prueba_window.prueba).start()

def main():
    app = VentanaUsuario()
    app.mainloop()

if __name__ == '__main__':
    main()



