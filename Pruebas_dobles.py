import threading
import tkinter as tk
from screeninfo import get_monitors
import numpy as np
import csv
import pandas as pd
import Funciones as F
import time
import keyboard
from collections import Counter
from Eyetracker import eyetracker
from Eyetracker import Lectura

#Cargo datos de calibracion
calibracion = pd.read_csv('calibracion.csv',delimiter=';')
print('Datos de Calibración:')
print(calibracion.columns)
ord_x, pend_x = float(calibracion['Ordenada X'][0]), float(calibracion['Pendiente X'][0])
ord_y, pend_y = float(calibracion['Ordenada Y'][0]), float(calibracion['Pendiente Y'][0])
print(ord_x,pend_x,ord_y,pend_y)

class Pruebas(tk.Tk):
    def __init__(self):
        super().__init__()

        # Obtengo los monitores conectados
        monitores = get_monitors()
        if len(monitores)>1:
            self.pant_2 = monitores[1] #Segunda pantalla
            self.pant_1 = monitores[0]
            # Defino titulo y dimensiones de la ventana 1
            self.title('Pruebas')
            self.geometry('300x200')

            # Genero un botón para abrir una ventana en el segundo monitor para iniciar la calibracion
            self.boton_prueba1 = tk.Button(self,
                                               text='Iniciar Prueba Teclado',
                                               command = lambda: self.Pruebas('Teclado'))
            self.boton_prueba1.pack(pady=20)
        
            # Genero un boton para guardar los datos de calibracion
            self.boton_prueba2 = tk.Button(self,
                                           text='Iniciar Prueba Eyetracker',
                                           command = lambda: self.Pruebas('Eyetracker'))
            self.boton_prueba2.pack(pady=20)

            # Botón para guardar los datos
            self.boton_Guardar = tk.Button(self,
                                           text='Guardar Resultados',
                                           command = lambda: self.Guardar())
            self.boton_Guardar.pack(pady=20)

            # Creo una segunda ventana
            self.ventana2 = tk.Toplevel(self)  
            self.ventana2.title('Prueba')
            self.ventana2.geometry(f"{self.pant_2.width}x{self.pant_2.height}+{self.pant_2.x}+{self.pant_2.y}")
            self.ventana2.canvas = tk.Canvas(self.ventana2,
                                                width=self.pant_2.width, 
                                                height=self.pant_2.height, 
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
        if self.tipo == 'Eyetracker':
            self.vent1.canvas.create_text(center_x, center_y, 
                                          text=texto,
                                          font=("Arial", 48),
                                          fill="white",
                                          anchor=tk.CENTER)

#   Funcion para graficar puntos en pantalla.
    def graficar(self,punto,ventana):
        x,y =punto
        if ventana=='Prueba':
            self.ventana2.canvas.create_oval(F.mm_a_px_X(x)-5,
                                             F.mm_a_px_Y(y)-5,
                                             F.mm_a_px_X(x)+5,
                                             F.mm_a_px_Y(y)+5,
                                             fill=self.color)
                                                
        if ventana=='Operario':
            self.color='red'

        if self.tipo=='Eyetracker':
            self.vent1.canvas.create_oval(F.mm_a_px_X(x)-5,
                                          F.mm_a_px_Y(y)-5,
                                          F.mm_a_px_X(x)+5,
                                          F.mm_a_px_Y(y)+5,
                                          fill=self.color)

#   Funcion para graficar cruz de fijación.
    def graficar_cruz(self,largo,ancho):
         # Grafico la cruz de fijación en la ventana de prueba
        self.line1 = self.ventana2.canvas.create_line(F.mm_a_px_X(self.ox) - largo,
                                                      F.mm_a_px_Y(self.oy),
                                                      F.mm_a_px_X(self.ox) + largo,
                                                      F.mm_a_px_Y(self.oy),
                                                      fill='white',
                                                      width=ancho)
        self.line2 = self.ventana2.canvas.create_line(F.mm_a_px_X(self.ox),
                                                      F.mm_a_px_Y(self.oy) - largo,
                                                      F.mm_a_px_X(self.ox),
                                                      F.mm_a_px_Y(self.oy) + largo,
                                                      fill='white',
                                                      width=ancho)
        self.reducir_tamano(F.mm_a_px_X(self.ox),F.mm_a_px_Y(self.oy),largo)
        
        if self.tipo == 'Eyetracker':
            #Grafico la cruz tambien en la ventana del operador
            self.vent1.canvas.create_line(F.mm_a_px_X(self.ox) - largo,
                                          F.mm_a_px_Y(self.oy),
                                          F.mm_a_px_X(self.ox) + largo,
                                          F.mm_a_px_Y(self.oy),
                                          fill='white',
                                          width=ancho)
            self.vent1.canvas.create_line(F.mm_a_px_X(self.ox),
                                          F.mm_a_px_Y(self.oy) - largo,
                                          F.mm_a_px_X(self.ox),
                                          F.mm_a_px_Y(self.oy) + largo,
                                          fill='white',
                                          width=ancho)
                                                     
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
        if self.tipo=='Eyetracker':
            self.vent1.canvas.delete('all')

#   Función para elegir un vector de 
#   forma aleatoria
    def Aleatorio(self,i,vectores):
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
            #print(f'El primer vector dentro del rango es {vector}')
            self.dist_xmin, self.dist_xmax = self.dist_xmin - x, self.dist_xmax - x
            self.dist_ymin, self.dist_ymax = self.dist_ymin - y, self.dist_ymax - y
        else:
            # Si no se encontró un vector, se define uno
            # hacia el origen
            x,y = -self.ox,-self.oy
            self.dist_xmin, self.dist_xmax = -180,180
            self.dist_ymin, self.dist_ymax = -90,90
            self.cantidad_total_vectores = self.cantidad_total_vectores + 1
            #i = i-1

            # Como se trata de un vector que no pertence a la lista,
            # se cambia de color para avisar en la funcion de prueba
            # que no se debe guardar las respuestas asociadas a este 
            # vector.
            self.color = 'red'
            print('No se encontró ningun vector dentro del rango')

        #self.dist_xmin, self.dist_xmax = self.dist_xmin - x, self.dist_xmax - x
        #self.dist_ymin, self.dist_ymax = self.dist_ymin - y, self.dist_ymax - y
        return x,y

#   Funcion de Pruebas:
#   En esta funcion de arma el patrón de vectores inicial,
#   y se determina la cantidad de vueltas por prueba
    def Pruebas(self,tipo):
        self.tipo = tipo
        # Si está en modo 'Eyetracker', abre una ventana
        # para el operario (para ver la posición del ojo
        # durante la prueba)
        if self.tipo == 'Eyetracker':
            # Arranco la función de eyetracker para
            # mostrar la cámara.
            threading.Thread(target=eyetracker).start()
            # Creo una ventana para operario
            self.vent1 = tk.Tk()  
            self.vent1.title('Ventana de Operador')
            self.vent1.geometry(f"{self.pant_1.width}x{self.pant_1.height}+{self.pant_1.x}+{self.pant_1.y}")
            self.vent1.canvas = tk.Canvas(self.vent1,
                                          width=self.pant_1.width, 
                                          height=self.pant_1.height, 
                                          bg='black')
            self.vent1.canvas.pack() 
       
        self.texto_canvas('Inicio de prueba')
        print(f'Tipo de prueba: {tipo}')
        print(f'Ronda 1')

        self.after(2000, lambda: self.borrar())
       
        # Genero el patrón de vectores incial
        radios = np.arange(7, 21, 2)
        #radios = np.arange(12,18,1.5)
        lim1, lim2 = -np.pi / 5, np.pi / 5
        num_puntos = 1
        #num_puntos = 0
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
            
        # Defino las variables para las gráficas
        self.largo,self.ancho,self.color = 30, 3, 'white'
            
        # Defino variables de la  funcion 'Iniciar'
        k = 1
        i = 0
        self.ox,self.oy = 0,0 
        self.vect_no_percibidos = []
        self.respuesta = []
        self.after(4000, lambda: self.Iniciar_prueba(k,
                                                     Vectores,
                                                     i,
                                                     self.vect_no_percibidos))
        
              
#   Función 'Iniciar Prueba': Muestra los puntos
#   y cruces en pantalla y guarda los resultados
#   (es decir, si el sujeto percibió o no los puntos)
    def Iniciar_prueba(self,k,distancias,i,vect_no_percibidos):
        # Por cada Vector (x,y) , voy a llamar a dos funciones en paralelo:
        #   1) funcion GRAFICAR: grafica el punto en pantalla.
        #   2) funcion de respuesta:
        #       a) para tipo 'Eyetracker': obtiene los datos del EYETRACKER. 
        #       b) para tipo 'Teclado': Obtiene a informacion de la barra
        #          espaciadora.
        if k<=2:
            if i < self.cantidad_total_vectores:
                ox, oy = self.ox, self.oy
                # Grafica la cruz en el origen de coordenadas

                ######################################
                print(f'Cruz en:{self.ox},{self.oy}.')
                ######################################
                
                self.graficar_cruz(self.largo,
                                self.ancho)
                
                # Con la funcion Aleatorio
                # elijo la distancia o vector (x,y)
                vector_x, vector_y = self.Aleatorio(i,distancias)
                dist_x,dist_y = vector_x + self.ox, vector_y + self.oy

                ############################################################
                print(f'Se grafica el vector a distancia {dist_x},{dist_y}')
                ############################################################


                # La cruz tarda 1 segundo en achicarse
                # Luego de 1s, emito sonido para avisar
                # que aparecerá el punto
                
                
                self.after(800, lambda: self.borrar())
                self.after(1000,lambda: F.beep1())

                # Luego del sonido, grafico el punto en pantalla
                self.after(1300, lambda: self.graficar((dist_x,dist_y),'Prueba'))

                if self.tipo=='Teclado':
                    self.resultado = 0
                    teclado = threading.Thread(target=self.teclado,
                                            args=(i,))
                    teclado.start()

                    # El punto se borra a los 200 ms
                    self.after(1500, lambda: self.borrar())

                    # Luego de 2 segundos, se determina
                    # si se presionó la barra en la prueba
                    self.after(2500, lambda: 
                            self.analisis_respuesta_teclado(vector_x,
                                                            vector_y))
                if self.tipo == 'Eyetracker':
                    self.datos = []
                    self.resultado = 0
                    valores_rectas = [ord_x,
                                      pend_x, 
                                      ord_y, 
                                      pend_y]
                    # Hilo para realizar la lectura en paralelo con el gráfico
                    lectura_thread = threading.Thread(target=Lectura,
                                                      args=(2,
                                                            self.tipo,
                                                            valores_rectas,
                                                            self.datos))
                    lectura_thread.start()
                    # El punto se borra a los 200 ms
                    self.after(1500, lambda: self.borrar())

                    # Luego de 2 segundos, se determina
                    # si se presionó la barra en la prueba
                    
                    self.after(2700, lambda: self.validez_y_respuesta(i,
                                                                      dist_x,
                                                                      dist_y,
                                                                      ox,
                                                                      oy,))  
                        
                # Terminada la lectura, el nuevo origen será 
                # la coordenada del vector (x,y)
                # Se llama a la funcion nuevamente
                self.after(3000, lambda: self.Iniciar_prueba(k,
                                                             distancias,
                                                             i+1,
                                                             vect_no_percibidos))  

                self.ox, self.oy = dist_x, dist_y
            else:
                k += 1
                print(f'Ronda 2')
                print(f'Tipo:{self.tipo}')
                self.after(2000, lambda: self.borrar())
                Vectores = F.patron_nuevo(resultado_paciente=self.respuesta)
                # Se mezcla la lista para que los vectores
                # se presenten de forma aleatoria
                np.random.shuffle(Vectores)

                # Determino la cantidad total de Vectores
                self.cantidad_total_vectores = len(Vectores)
                print(f'Cantidad de vectores no detectados: {self.cantidad_total_vectores}')
                # Determino los límites de la pantalla,
                # es decir, las distancias maximas y minimas 
                # que puedo presentar en pantalla
                self.dist_xmin, self.dist_xmax = -180,180
                self.dist_ymin, self.dist_ymax = -90,90
                    
                # Defino las variables para las gráficas
                self.largo,self.ancho,self.color = 30, 3, 'white'
                #self.tipo = self.tipo    
                # Defino variables de la  funcion 'Iniciar'
                i = 0
                self.ox,self.oy = 0,0 
                self.after(4000, lambda: self.Iniciar_prueba(k,
                                                             Vectores,
                                                             i,
                                                             self.vect_no_percibidos))
        
        else:
            print('Fin')
            self.texto_canvas('Fin')
            self.Sujeto = input('Ingrese Nombre de participante')
            self.Ojo = input("Ojo evaluado en esta prueba 'Derecho/Izquierdo': ")
            F.Grafica_resultado(self.Sujeto, self.Ojo,self.vect_no_percibidos)
    
    def teclado(self,i):
        tiempo = time.time()
        print('arranco')
        while (time.time() - tiempo) <= 2:
            try:
                if keyboard.is_pressed('space'):
                    self.resultado = 1
                    print('Tecla presionada.\n')
                    time.sleep(0.5)
                    break
            except:
                break
        print(f'{i+1}/{self.cantidad_total_vectores}:{self.resultado}\n')

    def analisis_respuesta_teclado(self,vector_x,vector_y):
        if self.color == 'white':
                self.respuesta.append([vector_x,vector_y,self.resultado])              
                if self.resultado == 0: # no detectó el estímulo
                    #self.vect_no_detectado.append([dist_x-self.ox, dist_y-self.oy])
                    print(f'Vector {vector_x,vector_y} no percibido.\n')
                    self.vect_no_percibidos.append([vector_x,vector_y])

    # Funcion de validez prueba objetiva
    def validez_y_respuesta(self,i,dist_x,dist_y,ox,oy):
        x = [coord[0] for coord in self.datos[0]]
        y = [coord[1] for coord in self.datos[0]]
        
###################################################################
####### Tiene una Fs = 60 Hz, po lo tanto debería recibir 120 datos
####### de los cuales los primeros 60 son de la cruz de fijacion
####### y los ultimos 60 del estímulo.

        #print(f'Cantidad de datos en X:{len(x)}')
        #print(f'Cantidad de datos en Y:{len(y)}')

        #print(f'Valores X de fijación: {x[0:55]}')
        #print(f'Valores Y de fijación: {y[0:55]}')

        #print(f'Valores X estímulo: {x[-55:]}')
        #print(f'Valores Y estímulo: {y[-55:]}')
###################################################################


        if self.color == 'white':
            if (abs(np.mean(x[30:50])-ox)<40) and (abs(np.mean(y[30:50])-oy)<40):
                # Analizo la respuesta
                if (((abs(np.mean(x[-15:]) - (dist_x))) < 40)
                    and ((abs(np.mean(y[-15:]) - (dist_y))) < 40)):
                    self.resultado = 1
                    print(f'Vector {dist_x-ox,dist_y-oy} percibido.')
                else:
                    self.resultado = 0
                    self.vect_no_percibidos.append([dist_x-ox,dist_y-oy])
                    print(f'Vector {dist_x-ox,dist_y-oy} NO percibido.')
                    
            else:
                print('No Válido')
                self.vect_no_percibidos.append([dist_x-ox,dist_y-oy])
                self.resultado=0
            self.respuesta.append([dist_x-ox,dist_y-oy,self.resultado])
            print(f'{i+1}/{self.cantidad_total_vectores}:{self.resultado}\n') 
        else:
            print('Punto de acomodación.')

        # Grafico donde vio el sujeto en la pantalla
        self.graficar((np.mean(x[-15:]),np.mean(y[-15:])),"Operario")
        
        
    def Guardar(self):
        #Lista de Vectores original
        # Genero el patrón de vectores incial
        radios = np.arange(7, 21, 2)
        #radios = np.arange(12,18,1.5)
        lim1, lim2 = -np.pi / 5, np.pi / 5
        num_puntos = 1
        #num_puntos = 0
        Vectores = F.Patron_vectores(radios,lim1,lim2,num_puntos)
        # Armo un unico vector con las coordenadas xy:
        for i in range(len(self.vect_no_percibidos)):
            Vectores.append(self.vect_no_percibidos[i])

        # cuento la frecuencia de cada par de coordenadas
        vector = [tuple(coord) for coord in Vectores]
        frecuencias = Counter(vector)
        
        # Convertir los datos en una tabla de pandas
        data = [(x, y, freq-1) for (x, y), freq in frecuencias.items()]
        df = pd.DataFrame(data, columns=['coordenada x [mm]',
                                         'coordenada y [mm]',
                                         'frecuencia de fallos'])
        # Guardar la tabla en un archivo CSV
        df.to_csv(f'Prueba_Sujeto{self.Sujeto}_Ojo{self.Ojo}_{self.tipo}.csv',index=False,sep=';')      
         
        self.after(1000, lambda: self.destroy())

def main(): 
    app = Pruebas()
    app.mainloop()
if __name__ == '__main__':
    main()