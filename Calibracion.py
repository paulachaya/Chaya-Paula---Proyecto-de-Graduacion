# El siguiente código trabaja con la clase
# 'Calibracion' para crear una interfaz gráfica
# para la función.

import threading
import tkinter as tk
from screeninfo import get_monitors
import numpy as np
import csv
import pandas as pd
import Funciones as F
from sklearn.linear_model import LinearRegression
from Eyetracker import eyetracker
from Eyetracker import Lectura



class Calibracion(tk.Tk):
    def __init__(self):
        super().__init__()

        # Obtengo los monitores conectados
        monitores = get_monitors()
        if len(monitores)>1:
            pant_2 = monitores[1] #Segunda pantalla

            #............VENTANA 1.............
            # Defino titulo y dimensiones de la ventana 1
            self.title('Calibracion')
            self.geometry('300x200')

            # Botón para iniciar la calibracion
            self.boton_calibracion = tk.Button(self,
                                               text='Iniciar Calibración',
                                               command = lambda: self.ventana_calibracion())
            self.boton_calibracion.pack(pady=20)
        
            # Botón para guardar los datos de calibracion
            self.boton_guardar = tk.Button(self,
                                           text='Guardar Calibración',
                                           command = lambda: self.Guardar_calibracion())
            self.boton_guardar.pack(pady=20)

            # ............VENTANA 2................
            self.ventana2 = tk.Toplevel(self)  
            self.ventana2.title('Calibracion')
            self.ventana2.geometry(f"{pant_2.width}x{pant_2.height}+{pant_2.x}+{pant_2.y}")
            self.ventana2.canvas = tk.Canvas(self.ventana2,
                                                width=pant_2.width, 
                                                height=pant_2.height, 
                                                bg='white')
            self.ventana2.canvas.pack() 
            # Arranco la función de eyetracker para
            # mostrar la cámara.
            threading.Thread(target=eyetracker).start()


#   Funcion para iniciar calibracion en el segundo monitor     
    def ventana_calibracion(self):
        # Genero texto dentro del canvas 
        self.texto_canvas('Iniciando Calibración...')
        # Mantengo el texto 3 segundos
        self.after(3000, lambda: self.borrar())

        # Una vez presentado el texto, 
        # arranco la funcion de calibracion.
        # Determino los valores de las variables.
        self.puntos_cal = [[-120,-60],[-40,-60],[40,-60],[120,-60],
                           [-120,-20],[-40,-20],[40,-20],[120,-20],
                           [-120,20],[-40,20],[40,20],[120,20],
                           [-120,60],[-40,60],[40,60],[120,60]] #puntos para calibrar
        i = 0
        self.datos = [] # lista para guardar datos
        etapa = 'calibracion'
        self.after(5000,lambda:print('\nIniciando calibración... '))
        self.after(6000, lambda: 
                   self.calibracion(self.puntos_cal,i,self.datos,etapa))

#   Funcion de texto    
    def texto_canvas(self,texto):
        center_x = self.ventana2.canvas.winfo_screenwidth() /2
        center_y = self.ventana2.canvas.winfo_screenheight()/2
        self.ventana2.canvas.create_text(center_x, center_y, text=texto,
                                         font=("Arial", 48), fill="black",
                                         anchor=tk.CENTER)

#   Funcion para graficar puntos en pantalla.
    def graficar(self,punto):
        x,y =punto
        self.ventana2.canvas.create_oval(F.mm_a_px_X(x)-5,
                                            F.mm_a_px_Y(y)-5,
                                            F.mm_a_px_X(x)+5,
                                            F.mm_a_px_Y(y)+5,
                                            fill='black')
        # La función se vuelve a llamar para cada punto de la lista
        print(f'Punto en pantalla:({x},{y}) [mm]')

#   Funcion para borrar cualquier cosa que 
#   esté en pantalla
    def borrar(self):
        self.ventana2.canvas.delete('all')
                    
#   Funcion de CALIBRACION: Esta funcion tiene
#   dos instancias:
#   1°) Calibracion: muestra dos puntos en pantalla 
#       para obtener las rectas de calibracion.
#   2°) Validacion: con las rectas obtenidas,
#       muestra un punto en cada cuadrante y analiza
#       la distancia entre el punto y la posicion
#       en pantalla del ojo del participante.
    
    def calibracion(self,puntos,i,datos,etapa):
        self.datos_cal = []
        # Por cada punto, voy a llamar a dos funciones en paralelo:
        #   1) funcion GRAFICAR: grafica el punto en pantalla.
        #   2) funcion LECTURA: obtiene los datos del eyetracker. 
               
        if i < len(puntos):
            # Emito sonido para avisar que comienza la lectura.
            F.beep1()         
            # Grafico el punto.
            self.graficar(puntos[i])

            if etapa == 'validacion':
                # Uso los valores obtenidos de la funcion 'Obtencion_rectas'
                valores_rectas = [self.ord_x, self.pend_x, 
                                  self.ord_y, self.pend_y]
            else:
                valores_rectas = [0,0,0,0]

            # Hilo para realizar la lectura en paralelo con el gráfico
            lectura_thread = threading.Thread(target=Lectura,
                                              args=(2,etapa,valores_rectas,datos))
            lectura_thread.start()

            # Borro el punto y llamo a la siguiente iteración después de 6 segundos
            self.after(3000, lambda: self.borrar())  
            self.after(4000, lambda: 
                       self.calibracion(puntos, i + 1,datos,etapa))

        else:
            if etapa == 'calibracion':
                #print(f'Datos leídos de calibración:\n {datos} \n')

                # Una vez finalizado el primer bucle,
                # utilizo la funcion 'Obtencion_rectas'
                # para calcular las pendientes y ordenadas
                # de las rectas de calibracion
                self.Obtencion_rectas(datos)

                # Una vez obtenidas las rectas de calibracion,
                # utilizo la funcion de verificacion
                self.after(1000, lambda:
                           print('\nIniciando validación...'))
                self.after(1500, lambda: 
                           self.texto_canvas('Iniciando validación...'))
                self.after(2500, lambda: self.borrar())

                # Para la validación se realiza el mismo 
                # mecanismo de mostrar puntos y obtener
                # datos del eyetracker en paralelo,
                # por lo tanto se vuelve a llamar a la funcion
                # pero con nuevos valores en las variables.
                self.puntos_validacion = [[50,50],[50,-50],
                                          [-50,-50],[-50,50]]
                i = 0
                self.datos = []
                etapa = 'validacion'
                self.after(3000, lambda:
                           self.calibracion(self.puntos_validacion,
                                            0,
                                            self.datos,
                                            etapa))
            else:
                # Una vez finalizada la validación, 
                # se llama a la funcion de 'Cálculo_de_distancias'
                self.Calculo_de_errores(datos)
            
#   Funcion Obtencion_rectas: a partir de 
#   los datos obtenidos por el Arduino, 
#   se calculan las ordenadas y pendientes
#   de las rectas de calibracion            
    def Obtencion_rectas(self,datos):
        print('\nObteniendo rectas de calibración...')
        # Los datos vienen en el siguiente formato
        # [[x1, y1], [x2, y2],...]
        x_eyetracker = np.array([coord[0] for coord in datos])
        y_eyetracker = np.array([coord[1] for coord in datos])

        # Separo los valores de X e Y de los puntos
        # de calibración
        x = np.array([coord[0] for coord in self.puntos_cal])
        y = np.array([coord[1] for coord in self.puntos_cal])
        
        # Crear modelo de regresion lineal para cada eje
        calibracion_x = LinearRegression()
        calibracion_y = LinearRegression()

        # Ajustar el modelo a los datos
        #calibracion_x.fit(x.reshape(-1, 1), x_eyetracker)  # reshape para ajustar la dimensión
        #calibracion_y.fit(y.reshape(-1, 1), y_eyetracker)
        calibracion_x.fit(x_eyetracker.reshape(-1, 1), x)  # reshape para ajustar la dimensión
        calibracion_y.fit(y_eyetracker.reshape(-1, 1), y)

        # Coeficientes obtenidos (pendiente y término independiente)
        print('\nCalibracion en X')
        print(f"Pendiente (m): {calibracion_x.coef_[0]}")
        print(f"Intersección (b): {calibracion_x.intercept_}")

        print('\nCalibracion en Y')
        print(f"Pendiente (m): {calibracion_y.coef_[0]}")
        print(f"Intersección (b): {calibracion_y.intercept_}")

        self.pend_x = calibracion_x.coef_[0]
        self.ord_x = calibracion_x.intercept_
        self.pend_y = calibracion_y.coef_[0]
        self.ord_y = calibracion_y.intercept_

    # Funcion Calculo_de_distancias:
    # Esta funcion evalúa la distancia entre
    # un determinado punto mostrado en pantalla y 
    # la posicion de la mirada del sujeto
    def Calculo_de_errores(self, datos):
        # Los puntos y los datos tienen el siguiente formato
        # puntos/datos = [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]

        # Verifico que ambos arreglos tienen el mismo tamaño
        if len(self.puntos_validacion)!= len(datos):
            print('Faltan datos')
        
        else:
            error_x,error_y = [],[]
            # Tengo que evaluar la distancia punto a punto
            for i in range(len(self.puntos_validacion)):
                pto_x, pto_y = self.puntos_validacion[i]
                lectura_x, lectura_y = datos[i]

                # Calculo los errores en X e Y
                error_x.append(np.abs(pto_x - lectura_x))
                error_y.append(np.abs(pto_y - lectura_y))

            # Obtengo el error promedio en cada eje
            Error_promedio_x = np.mean(error_x)
            Error_promedio_y = np.mean(error_y)
            
            self.error_x = Error_promedio_x
            self.error_y = Error_promedio_y

            # Desviaciones
            Desv_x = np.std(error_x,ddof=1)
            Desv_y = np.std(error_y,ddof=1)

            print(f'\nError Promedio (mm):\nEje X: {Error_promedio_x}[mm]\nEje Y: {Error_promedio_y}[mm]')
            print(f'Desviación en x (mm):{Desv_x}[mm]\nDesviación en y: {Desv_y}[mm]')
            
            #Errores en grados
            Error_x_grados = F.mm_a_grados(Error_promedio_x)
            Error_y_grados = F.mm_a_grados(Error_promedio_y)

            # Desviaciones en grados
            Desv_x_grados = F.mm_a_grados(Desv_x)
            Desv_y_grados = F.mm_a_grados(Desv_y)

            print(f'\nError Promedio (grados):\nEje X: {Error_x_grados}°\nEje Y: {Error_y_grados}°')
            print(f'Desviación en x (grados):{Desv_x_grados}°\nDesviación en y (grados): {Desv_y_grados}°')

    
#   Funcion guardar_calibracion:
#   Una vez obtenida la Distancia Promedio, si se presiona
#   el boton de 'Guardar calibracion', los datos de las rectas
#   se guardan en un archivo .csv
    def Guardar_calibracion(self):
        # valores_rectas tiene el siguiente formato
        with open('calibracion.csv', mode='w', newline='') as file:
            writer = csv.writer(file,delimiter=';')
            writer.writerow(['Ordenada X',
                             'Pendiente X',
                             'Ordenada Y', 
                             'Pendiente Y',
                             'Error X',
                             'Error Y'])
            writer.writerow([self.ord_x,
                             self.pend_x,
                             self.ord_y,
                             self.pend_y,
                             self.error_x,
                             self.error_y])
        print("Calibración guardada en calibracion.csv")
        self.after(1000, lambda: self.destroy())

   

def main():
    app = Calibracion()
    app.mainloop()
    
if __name__ == '__main__':
    main()