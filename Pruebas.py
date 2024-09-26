import serial
import threading
import tkinter as tk
from screeninfo import get_monitors
import numpy as np
import csv
import pandas as pd
import Funciones as F
import time

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
        self.ventana2.canvas.create_text(center_x, center_y, 
                                         text=texto,
                                         font=("Arial", 48),
                                         fill="white",
                                         anchor=tk.CENTER)

#   Funcion para graficar puntos en pantalla.
    def graficar(self,punto):
        x,y =punto
        self.ventana2.canvas.create_oval(F.mm_a_px_X(x)-5,
                                            F.mm_a_px_Y(y)-5,
                                            F.mm_a_px_X(x)+5,
                                            F.mm_a_px_Y(y)+5,
                                            fill=self.color)
        # La función se vuelve a llamar para cada punto de la lista
        print('Se presentó punto a distancia:',x,y)    

#   Funcion para graficar cruz de fijación.
    def graficar_cruz(self,largo,ancho,color):
         # Grafico la cruz de fijación en la ventana de prueba
        self.line1 = self.ventana2.canvas.create_line(F.mm_a_px_X(self.ox) - largo,
                                                      F.mm_a_px_Y(self.oy),
                                                      F.mm_a_px_X(self.ox) + largo,
                                                      F.mm_a_px_Y(self.oy),
                                                      fill=color,
                                                      width=ancho)
        self.line2 = self.ventana2.canvas.create_line(F.mm_a_px_X(self.ox),
                                                      F.mm_a_px_Y(self.oy) - largo,
                                                      F.mm_a_px_X(self.ox),
                                                      F.mm_a_px_Y(self.oy) + largo,
                                                      fill=color,
                                                      width=ancho)
        self.reducir_tamano(F.mm_a_px_X(self.ox),F.mm_a_px_Y(self.oy),largo)

    # Funcion para disminuir el tamaño
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
#   esté en pantalla.
    def borrar(self):
        self.ventana2.canvas.delete('all')

#   Función para elegir un vector de 
#   forma aleatoria
    def Aleatorio(self,vectores):
        vector, indice = None, -1
        for j, (X,Y) in enumerate(vectores):
            # Busco cual es el primer vector de coordenadas (x,y)
            # dentro de la lista de 'vectores' que se encuentra 
            # dentro de los límites de pantalla.
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
        else:
            # Si no se encontró un vector, se define uno
            # hacia el origen

            x,y = -self.ox,-self.oy
            # Como se trata de un vector que no pertence a la lista,
            # se cambia de color para avisar en la funcion de prueba
            # que no se debe guardar las respuestas asociadas a este 
            # vector.
            color = 'red'
            print('No se encontró ningun vector dentro del rango')
        
        self.dist_xmin, self.dist_xmax = self.dist_xmin - x, self.dist_xmax - x
        self.dist_ymin, self.dist_ymax = self.dist_ymin - y, self.dist_ymax - y
        x,y = x+self.ox, y+self.oy
        return x,y

#   Funcion de Pruebas:
#   En esta funcion de arma el patrón de vectores inicial,
#   y se determina la cantidad de vueltas por prueba
    def Pruebas(self,tipo):
        self.texto_canvas('Inicio de prueba.')
        self.after(2000, lambda: self.borrar())
       
        # Genero el patrón de vectores incial
        radios = np.arange(7, 22, 3)
        lim1, lim2 = -np.pi / 4, np.pi / 4
        num_puntos = 3
        Vectores = F.Patron_vectores(radios,lim1,lim2,num_puntos)

        # Se mezcla la lista para que los vectores
        # se presenten de forma aleatoria
        np.random.shuffle(Vectores)

        # Determino la cantidad total de Vectores
        self.cantidad_total_vectores = len(Vectores)

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
        self.vect_no_percibidos = []
        self.after(4000, lambda: self.Iniciar_prueba(cantidad_total_vectores,
                                                     Vectores,
                                                     i,
                                                     self.datos,
                                                     self.vect_no_percibidos,
                                                     tipo))
        
              
#   Función 'Iniciar Prueba': Muestra los puntos
#   y cruces en pantalla y guarda los resultados
#   (es decir, si el sujeto percibió o no los puntos)
    def Iniciar_prueba(self,cant_total,distancias,i,datos,vect_no_percibidos,tipo):
        # Por cada Vector (x,y) , voy a llamar a dos funciones en paralelo:
        #   1) funcion GRAFICAR: grafica el punto en pantalla.
        #   2) funcion de respuesta:
        #       a) para tipo 'Eyetracker': obtiene los datos del arduino. 
        #       b) para tipo 'Teclado': Obtiene a informacion de la barra
        #          espaciadora.
        if i < self.cantidad_total_vectores:
            
            # Grafica la cruz en el origen de coordenadas
            print('Grafico cruz de fijación.')
            self.graficar_cruz(self.largo,
                               self.ancho,
                               self.color)

            # Con la funcion Aleatorio
            # elijo la distancia o vector (x,y)
            dist_x, dist_y = self.Aleatorio(distancias)

            # La cruz tarda 1 segundo en achicarse
            # Luego de 1s, emito sonido para avisar
            # que aparecerá el punto
            self.after(1000, lambda: F.beep1())

            # Luego del sonido, grafico el punto en pantalla
            self.after(1200, lambda: print(f'Punto: {dist_x,dist_y}'))
            self.after(1300, lambda: self.graficar((dist_x,dist_y)))

            if tipo=='Teclado':
                self.resultado = 0
                teclado = threading.Thread(target=self.teclado,
                                           args=(i,))
                teclado.start()

            # El punto se borra a los 200 ms
            self.after(1500, lambda: self.borrar())

            # Luego de 2 segundos, se determina
            # si se presionó la barra en la prueba
            self.after(2000, lambda: 
                       self.analisis_respuesta_teclado(self.resultado,
                                                        self.color,
                                                        dist_x,
                                                        dist_y))
            
            # Terminada la lectura, el nuevo origen será 
            # la coordenada del vector (x,y)
            # Se llama a la funcion nuevamente
            self.after(2500, lambda: self.Iniciar_prueba(distancias,
                                                         ox,oy, i+1,
                                                         vect_no_percibidos,
                                                         tipo))
            self.ox, self.oy = dist_x, dist_y
        else:
            print('Fin')
            self.texto_canvas('Fin')

    def teclado(self,i):
        tiempo = time.time()
        print('arranco')
        while (time.time() - tiempo) <= 3:
            try:
                if keyboard.is_pressed('space'):
                    self.resultado = 1
                    print('tecla presionada')
                    time.sleep(0.5)
                    break
            except:
                break
        print(f'{i}/{self.cantidad_total_vectores}:{self.resultado}\n')


    def analisis_respuesta_teclado(self,resultado,color,dist_x,dist_y):
        if color == 'white':              
                print(resultado)
                if resultado == 0: # no detectó el estímulo
                    #self.vect_no_detectado.append([dist_x-self.ox, dist_y-self.oy])
                    print(f'Vector ({dist_x, dist_y}) no percibido.)')

def main(): 
    app = Pruebas()
    app.mainloop()
if __name__ == '__main__':
    main()