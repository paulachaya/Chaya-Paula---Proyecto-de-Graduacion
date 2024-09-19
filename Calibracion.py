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
            segundo_monitor = monitores[1]

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
            self.ventana2.geometry(f"{segundo_monitor.width}x{segundo_monitor.height}+{segundo_monitor.x}+{segundo_monitor.y}")
            self.ventana2.canvas = tk.Canvas(self.ventana2,
                                                width=segundo_monitor.width, 
                                                height=segundo_monitor.height, 
                                                bg='black')
            self.ventana2.canvas.pack()
            
    #    self.resultados = []
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
        self.puntos_calibracion = [[0,0],[75,75]]
        i = 0
        self.datos_leidos = []
        etapa = 'inicio'
        self.after(6000, lambda: self.calibracion(self.puntos_calibracion,i,self.datos_leidos,etapa))


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
        print('Borro')
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
                valores_rectas = [self.ord_x, self.pend_x, self.ord_y, self.pend_y]
            else:
                valores_rectas = [0,0,0,0]
            # Hilo para realizar la lectura en paralelo con el gráfico
            lectura_thread = threading.Thread(target=F.lectura_arduino, args=(etapa,valores_rectas,datos,))
            lectura_thread.start()

            # Borro el punto y llamo a la siguiente iteración después de 4 segundos
            self.after(4000, lambda: self.borrar())  
            self.after(4000, lambda: self.calibracion(puntos, i + 1,datos,etapa))

        else:
            if etapa == 'inicio':
                # Una vez finalizado el primer bucle,
                # utilizo la funcion 'Obtencion_rectas'
                # para calcular las pendientes y ordenadas
                # de las rectas de calibracion
                self.Obtencion_rectas(self.datos_leidos)
                # Una vez obtenidas las rectas de calibracion,
                # utilizo la funcion de verificacion
                self.after(1000,lambda:self.borrar())
                self.after(1000, lambda: print('Iniciando verificación...'))
                # Para la verificacion se realiza el mismo 
                # mecanismo de mostrar puntos y obtener
                # datos del Arduino en paralelo,
                # por lo tanto se vuelve a llamar a la funcion
                # pero con nuevos valores en las variables.
                self.puntos_ver = [[60,60],[60,-60],[-60,-60],[-60,60]]
                i = 0
                self.datos = []
                etapa = 'verificacion'
                self.after(2000, lambda: self.calibracion(self.puntos_ver,i,self.datos,etapa))
            else:
                # Una vez finalizada la verificación, 
                # se llama a la funcion de 'Calculo_de_distancias'
                self.Calculo_de_distancias(self.datos)
            
    def Obtencion_rectas(self,datos):
        # Los datos vienen en el siguiente formato
        # [[x1, y1], [x2, y2]]
        x1,x2 = [coord[0] for coord in datos]
        y1,y2 = [coord[1] for coord in datos]
        print(x1,x2,y1,y2)

        # Obtengo las ordenadas y pendientes 
        # de las rectas de calibración

        self.ord_x = -self.pend_x*x1
        self.ord_y = -self.pend_y*y1

        self.pend_x = 75 / (x2-x1)
        self.pend_y = 75 / (y2-y1)

        print(f"Ordenada y Pendiente de X: [{self.ord_x}, {self.pend_x}]")
        print(f"Ordenada y Pendiente de Y: [{self.ord_y}, {self.pend_y}]")
    
    
        
#   Funcion GRAFICA: Esta funcion me muestra los puntos
#   presentados en cada cuadrante y las posiciones del 
#   ojo del participante durante la verificacion
    def grafica_de_verificacion(self,lectura_X,lectura_Y,puntos):
        # Grafico la prueba de verificacion
        plt.figure(figsize=(10, 5))
        for i in range(4):
            valores_x = lectura_X[i]
            valores_y = lectura_Y[i]
            plt.scatter(valores_x, valores_y, marker='o',s=40, color='red')
        plt.scatter([x for (x,y) in puntos],[y for (x,y) in puntos], marker='o',s=40, color='black')
        plt.title('Resultados calibracion')
        plt.xlim(-140, 140)
        plt.ylim(-100, 100)
        plt.show()
    
#   Una vez obtenida la grafica de verificacion, si se presiona
#   el boton de 'Guardar calibracion', los datos de las rectas
#   se guardan en un archivo .csv
    def Guardar_calibracion(self):
        with open('calibracion.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Ordenada X', 'Pendiente X', 'Ordenada Y', 'Pendiente Y'])
            writer.writerow([self.resultados[2], self.resultados[0], self.resultados[3], self.resultados[1]])
        print("Calibración guardada en calibracion.csv")
    
def main():
    app = Calibracion()
    app.mainloop()
if __name__ == '__main__':
    main()