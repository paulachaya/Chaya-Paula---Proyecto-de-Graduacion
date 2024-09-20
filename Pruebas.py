import serial
import threading
import tkinter as tk
from screeninfo import get_monitors
import numpy as np
import csv
import pandas as pd
import Funciones as F

class Pruebas(tk.Tk):
    def __init__(self):
        super().__init__()

        # Obtengo los monitores conectados
        monitores = get_monitors()
        if len(monitores)>1:
            pant_2 = monitores[1] #Segunda pantalla

            # Defino titulo y dimensiones de la ventana 1
            self.title('Pruebas')
            self.geometry('300x200')

            # Genero un botón para abrir una ventana en el segundo monitor para iniciar la calibracion
            self.boton_calibracion = tk.Button(self,
                                               text='Iniciar Prueba Teclado',
                                               command = lambda: self.Pruebas('Teclado'))
            self.boton_calibracion.pack(pady=20)
        
            # Genero un boton para guardar los datos de calibracion
            self.boton_guardar = tk.Button(self,
                                           text='Iniciar Prueba Eyetracker',
                                           command = lambda: self.Pruebas('Eyetracker'))
            self.boton_guardar.pack(pady=20)

            # Creo una segunda ventana
            self.ventana2 = tk.Toplevel(self)  
            self.ventana2.title('Prueba')
            self.ventana2.geometry(f"{pant_2.width}x{pant_2.height}+{pant_2.x}+{pant_2.y}")
            self.ventana2.canvas = tk.Canvas(self.ventana2,
                                                width=pant_2.width, 
                                                height=pant_2.height, 
                                                bg='black')
            self.ventana2.canvas.pack() 

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
        print('Se presentó punto a distancia:',x,y)    


    def graficar_cruz(self,punto,largo,ancho,color):
        ox,oy = punto
         # Grafico la cruz de fijación en la ventana de prueba
        self.line1 = self.ventana2.canvas.create_line(F.mm_a_px_X(ox) - largo,
                                                      F.mm_a_px_Y(oy),
                                                      F.mm_a_px_X(ox) + largo,
                                                      F.mm_a_px_Y(oy),
                                                      fill=color,
                                                      width=ancho)
        self.line2 = self.ventana2.canvas.create_line(F.mm_a_px_X(ox),
                                                      F.mm_a_px_Y(oy) - largo,
                                                      F.mm_a_px_X(ox),
                                                      F.mm_a_px_Y(oy) + largo,
                                                      fill=color,
                                                      width=ancho)
        self.reducir_tamano(F.mm_a_px_X(ox),F.mm_a_px_Y(oy),largo)

    # Funcion reducir_tamaño:
    # Utilizo para disminuir el tamaño
    # de la cruz de fijación
    def reducir_tamano(self,ox,oy,largo):
        interval = 50
        largo -= 4 
            # Actualizar las posiciones de las líneas de la cruz
        self.ventana2.canvas.coords(self.line1, ox - largo, oy, ox + largo, oy)
        self.ventana2.canvas.coords(self.line2, ox, oy - largo, ox, oy + largo)
            # Si el tamaño es mayor que 0, continuar reduciendo el tamaño
        if largo > 0:
            self.ventana2.canvas.after(interval, lambda: self.reducir_tamano(ox,oy,largo)) 

#   Funcion para borrar cualquier cosa que 
#   esté en pantalla
    def borrar(self):
        print('\n')
        self.ventana2.canvas.delete('all')

    def Aleatorio(self,vectores):
        vector, indice = None, -1
        for j, (X,Y) in enumerate(vectores):
            if ((self.dist_xmin < X < self.dist_xmax) 
                and (self.dist_ymin < Y < self.dist_ymax)):
                x,y = X ,Y
                vector, indice = (x,y), j
                break
        if vector is not None:
            # Si se encontró un vector, se elimina de la lista
            vectores.pop(indice)
            self.color = 'white'
            print(f'El primer vector dentro del rango es {vector}')
            print('cantidad de vectores:',len(vectores))
        else:
            x,y = -self.ox,-self.oy
            color = 'red'
            print('No se encontró ningun vector dentro del rango')
        return x,y

    def Pruebas(self,tipo):
        # Genero el patrón de vectores incial
        radios,lim1,lim2,num_puntos = np.arange(7, 22, 3), -np.pi / 4, np.pi / 4, 3
        Vectores = F.Patron_estimulos(radios,lim1,lim2,num_puntos)
        
        # La prueba (teclado o eyetracker) trabaja con 2 rondas
        #   La primera ronda trabaja con el primer patrón de vectores
        #   La segunda ronda trabaja con el patron filtrado
        #   a partir de los resultados obtenidos en la 1° ronda.
        self.distancias_no_percibidas = []
        for k in range(2):
            self.texto_canvas(f'Ronda {k+1}')

            # Se mezcla la lista para que los
            # vectores para que se presenten 
            # de forma aleatoria
            np.random.shuffle(Vectores)

            # Determino la cantidad total de Vectores
            cantidad_total_estimulos = len(Vectores)

            # Determino los límites de la pantalla,
            # es decir, las distancias maximas y minimas 
            # que puedo presentar en pantalla
            self.dist_xmin, self.dist_ymin = np.min(Vectores, axis=0)
            self.dist_xmax, self.dist_ymax = np.max(Vectores, axis=0) 
            print('Limites X:', self.dist_xmin, self.dist_xmax)
            print('Limites Y:', self.dist_ymin, self.dist_ymax)
            
            # Defino las variables para las gráficas
            self.largo,self.ancho,self.color = 30, 3, 'white'
            
            # Defino variables de la  funcion 'Iniciar'
            i = 0
            self.ox,self.oy = 0,0 
            self.datos = []
            self.Iniciar_prueba(cantidad_total_estimulos,Vectores,i,self.datos,tipo)

            
    

    def Iniciar_prueba(self,cant_total,distancias,i,datos,tipo):
        # Por cada Vector (x,y) , voy a llamar a dos funciones en paralelo:
        #   1) funcion GRAFICAR: grafica el punto en pantalla.
        #   2) funcion LECTURA: obtiene los datos del arduino. 
               
        if i < cant_total:

            # Grafica la cruz en el origen de coordenadas
            self.graficar_cruz((self.ox,self.oy),self.largo,self.ancho,self.color)

            # Con la funcion Aleatorio
            # elijo la distancia o vector (x,y)
            dist_x, dist_y = self.Aleatorio(distancias)

            # Emito sonido para avisar que comienza la lectura.
            # Grafico el punto.
            F.beep1()
            self.graficar((dist_x, dist_y))
            if tipo == 'Eyetracker':
                print('Se lee del arduino')
                # Uso los valores obtenidos de la calibracion
                #valores_rectas = [self.ord_x, self.pend_x, 
                #                  self.ord_y, self.pend_y]
                # Hilo para realizar la lectura en paralelo con el gráfico
                #lectura_thread = threading.Thread(target=F.lectura_arduino,
                #                                args=(etapa,valores_rectas,datos,))
                #lectura_thread.start()

                # Borro el punto y llamo a la siguiente iteración después de 2 segundos
                #self.after(2500, lambda: self.borrar())  
                #self.after(3000, lambda: 
                #        self.calibracion(puntos, i + 1,datos,etapa))
            # Si estoy en tipo = 'Teclado'
            else: 
                resultado = 0
                # Llamo a la funcion de barra espaciadora
                teclado_thread = threading.Thread(target=F.space_press,
                                                  args=(resultado))
                teclado_thread.start()
                print(resultado)
                if (self.color=='white' and resultado==0):
                    self.distancia_no_percibida.append((dist_x,dist_y))
                self.after(1500, lambda:self.borrar())
                self.after(2000, lambda:self.Iniciar_prueba(distancias,i+1,datos,tipo))
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