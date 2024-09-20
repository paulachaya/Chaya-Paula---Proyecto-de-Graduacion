import multiprocessing.queues
import serial
import threading
import tkinter as tk
import time
from screeninfo import get_monitors
import numpy as np
import csv
import matplotlib.pyplot as plt
import pandas as pd
import queue
import winsound
from multiprocessing import Process
import multiprocessing
import Funciones as F


class Calibracion(tk.Tk):
    def __init__(self):
        super().__init__()

        # Obtengo los monitores conectados
        monitores = get_monitors()
        if len(monitores)>1:
            pant_2 = monitores[1] #Segunda pantalla

            # Defino titulo y dimensiones de la ventana 1
            self.title('Calibracion')
            self.geometry('300x200')

            # Genero un botón para abrir una ventana en el segundo monitor para iniciar la calibracion
            self.boton_calibracion = tk.Button(self,
                                               text='Iniciar Calibración',
                                               command = lambda: self.ventana_calibracion())
            self.boton_calibracion.pack(pady=20)
        
            # Genero un boton para guardar los datos de calibracion
            self.boton_guardar = tk.Button(self,
                                           text='Guardar Calibración',
                                           command = lambda: self.Guardar_calibracion())
            self.boton_guardar.pack(pady=20)

            # Creo una segunda ventana
            self.ventana2 = tk.Toplevel(self)  
            self.ventana2.title('Calibracion')
            self.ventana2.geometry(f"{pant_2.width}x{pant_2.height}+{pant_2.x}+{pant_2.y}")
            self.ventana2.canvas = tk.Canvas(self.ventana2,
                                                width=pant_2.width, 
                                                height=pant_2.height, 
                                                bg='black')
            self.ventana2.canvas.pack()
            
    #    self.ser = serial.Serial('COM6', 9600).
    #    self.protocol("WM_DELETE_WINDOW", self.on_closing)

#   Esta funcion se encarga de cerrar la conexion serial y destruir la ventana de Calibracion.
    def on_closing(self): 
        try:
            self.ser.close()
        except Exception as e:
            print("Error closing serial connection:", e)
        self.destroy()    
      
#   Funcion para abrir la ventana de calibracion en el segundo monitor     
    def ventana_calibracion(self):
        # Genero texto dentro del canvas 
        self.texto_canvas('Calibración')
        # Mantengo el texto 3 segundos
        self.after(3000, lambda: self.borrar())

        # Una vez presentado el texto, 
        # arranco la funcion de calibracion.
        # Determino los valores de las variables.
        self.puntos_cal = [[0,0],[75,75]]
        i = 0
        self.datos = []
        etapa = 'inicio'
        self.after(5000,lambda:print('Iniciando calibración... \n'))
        self.after(6000, lambda: 
                   self.calibracion(self.puntos_cal,i,self.datos,etapa))

#   Funcion de texto    
    def texto_canvas(self,texto):
        center_x = self.ventana2.canvas.winfo_screenwidth() /2
        center_y = self.ventana2.canvas.winfo_screenheight()/2
        self.ventana2.canvas.create_text(center_x, center_y, text=texto,
                                         font=("Arial", 48), fill="white",
                                         anchor=tk.CENTER)

#   Funcion para graficar puntos en pantalla.
    def graficar(self,punto):
        x,y =punto
        self.ventana2.canvas.create_oval(F.mm_a_px_X(x)-5,
                                            F.mm_a_px_Y(y)-5,
                                            F.mm_a_px_X(x)+5,
                                            F.mm_a_px_Y(y)+5,
                                            fill='white')
        # La función se vuelve a llamar para cada punto de la lista
        print('Se graficó punto:',x,y)    

#   Funcion para borrar cualquier cosa que 
#   esté en pantalla
    def borrar(self):
        print('\n')
        self.ventana2.canvas.delete('all')
                    
#   Funcion de CALIBRACION: Esta funcion tiene
#   dos instancias:
#   1°) Calibracion: muestra dos puntos en pantalla 
#       para obtener las rectas de calibracion.
#   2°) Verificacion: con las rectas obtenidas,
#       muestra un punto en cada cuadrante y analiza
#       la distancia entre el punto y la posicion
#       en pantalla del ojo del participante.
    
    def calibracion(self,puntos,i,datos,etapa):
        # Por cada punto, voy a llamar a dos funciones en paralelo:
        #   1) funcion GRAFICAR: grafica el punto en pantalla.
        #   2) funcion LECTURA: obtiene los datos del arduino. 
               
        if i < len(puntos):
            # Emito sonido para avisar que comienza la lectura.
            F.beep1()         
            # Grafico el punto.
            self.graficar(puntos[i])
            if etapa == 'verificacion':
                # Uso los valores obtenidos de la funcion 'Obtencion_rectas'
                valores_rectas = [self.ord_x, self.pend_x, 
                                  self.ord_y, self.pend_y]
            else:
                valores_rectas = [0,0,0,0]
            # Hilo para realizar la lectura en paralelo con el gráfico
            lectura_thread = threading.Thread(target=F.lectura_arduino,
                                              args=(etapa,valores_rectas,datos,))
            lectura_thread.start()

            # Borro el punto y llamo a la siguiente iteración después de 4 segundos
            self.after(4500, lambda: self.borrar())  
            self.after(5000, lambda: 
                       self.calibracion(puntos, i + 1,datos,etapa))

        else:
            if etapa == 'inicio':
                print(f'Datos leídos de inicio:\n {datos} \n')

                # Una vez finalizado el primer bucle,
                # utilizo la funcion 'Obtencion_rectas'
                # para calcular las pendientes y ordenadas
                # de las rectas de calibracion
                self.Obtencion_rectas(datos)

                # Una vez obtenidas las rectas de calibracion,
                # utilizo la funcion de verificacion
                self.after(1000, lambda:
                           print('\nIniciando verificación...\n'))

                # Para la verificacion se realiza el mismo 
                # mecanismo de mostrar puntos y obtener
                # datos del Arduino en paralelo,
                # por lo tanto se vuelve a llamar a la funcion
                # pero con nuevos valores en las variables.
                self.puntos_ver = [[60,60],[60,-60],
                                   [-60,-60],[-60,60]]
                i = 0
                self.datos = []
                etapa = 'verificacion'
                self.after(2000, lambda:
                           self.calibracion(self.puntos_ver,0,self.datos,etapa))
            else:
                #print(datos)
                # Una vez finalizada la verificación, 
                # se llama a la funcion de 'Calculo_de_distancias'
                self.Calculo_de_distancias(datos,self.puntos_ver)
            
#   Funcion Obtencion_rectas: a partir de 
#   los datos obtenidos por el Arduino, 
#   se calculan las ordenadas y pendientes
#   de las rectas de calibracion            
    def Obtencion_rectas(self,datos):
        # Los datos vienen en el siguiente formato
        # [[x1, y1], [x2, y2]]
        x1,x2 = [coord[0] for coord in datos]
        y1,y2 = [coord[1] for coord in datos]
        #print(x1,x2,y1,y2)

        # Obtengo las ordenadas y pendientes 
        # de las rectas de calibración

        self.pend_x = 75 / (x2-x1)
        self.pend_y = 75 / (y2-y1)

        self.ord_x = -self.pend_x*x1
        self.ord_y = -self.pend_y*y1

        print(f"\nOrdenada y Pendiente de X: [{self.ord_x}, {self.pend_x}]")
        print(f"Ordenada y Pendiente de Y: [{self.ord_y}, {self.pend_y}]")

    # Funcion Calculo_de_distancias:
    # Esta funcion evalua la distancia entre
    # un determinado punto mostrado en pantalla y 
    # la posicion de la mirada del sujeto
    def Calculo_de_distancias(self, datos,puntos):   
        # Los puntos y los datos tienen el siguiente formato
        # puntos = [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
        # Verifico que ambos arreglos tienen el mismo tamaño
        if len(puntos)!= len(datos):
            print('Faltan datos')
        else:
            Distancia = []
            # Tengo que evaluar la distancia punto a punto
            for i in range(len(puntos)):
                pto_x, pto_y = puntos[i]
                lectura_x, lectura_y = datos[i]

                # Calculo la distancia
                dist_x = pto_x - lectura_x
                dist_y = pto_y - lectura_y
                vector_distancia = np.array([dist_x,dist_y])
                Distancia.append(np.linalg.norm(vector_distancia))

            # Calculo el promedio de distancias
            Distancia_promedio = np.mean(Distancia)
            print(f'El Promedio de Distancias es: {Distancia_promedio}')
    
#   Funcion guardar_calibracion:
#   Una vez obtenida la Distancia Promedio, si se presiona
#   el boton de 'Guardar calibracion', los datos de las rectas
#   se guardan en un archivo .csv
    def Guardar_calibracion(self):
        # valores_rectas tiene el siguiente formato
        val_rectas = [self.ord_x, self.pend_x,
                      self.ord_y, self.pend_y]
        with open('calibracion.csv', mode='w', newline='') as file:
            writer = csv.writer(file,delimiter=';')
            writer.writerow(['Ordenada X',
                             'Pendiente X',
                             'Ordenada Y', 
                             'Pendiente Y'])
            writer.writerow([val_rectas[0],
                             val_rectas[1],
                             val_rectas[2],
                             val_rectas[3]])
        print("Calibración guardada en calibracion.csv")
        self.after(1000, lambda: self.destroy())
    
def main():
    app = Calibracion()
    app.mainloop()
if __name__ == '__main__':
    main()