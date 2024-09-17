# Prueba Objetiva
import serial
import threading
import tkinter as tk
import time
from screeninfo import get_monitors
import numpy as np
import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import Circle
import pandas as pd
import random as rd
import winsound
from queue import Queue
from collections import Counter
import Funciones as F

# Cargo los datos de calibracion
cal = pd.read_csv('calibracion.csv')
ordenada_x, pendiente_x = float(cal['Ordenada X'][0]), float(cal['Pendiente X'][0])
ordenada_y, pendiente_y = float(cal['Ordenada Y'][0]), float(cal['Pendiente Y'][0])

#  Ventana de prueba
class VentanaPrueba(tk.Toplevel):
    def __init__(self, parent_canvas):
        super().__init__()
        self.parent_canvas = parent_canvas # Para graficar en la pantalla del Operario
        monitores = get_monitors()
        if len(monitores) > 1:
            segundo_monitor = monitores[1]
            self.geometry(f"{segundo_monitor.width}x{segundo_monitor.height}+{segundo_monitor.x}+{segundo_monitor.y}")

        self.canvas = tk.Canvas(self, width=segundo_monitor.width,
                                height=segundo_monitor.height,
                                bg='black')
        self.canvas.pack()
        self.ser = serial.Serial('COM6', 9600)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):  # Esta función se encarga de cerrar la conexión serial.
        try:
            self.ser.close()
        except Exception as e:
            print("Error closing serial connection:", e)
        self.destroy()

# Funcion para disminuir el tamaño de la cruz de fijación
    def reducir_tamano(self,ox,oy,largo):
        interval = 50 
        largo -= 2  
        self.canvas.coords(self.line1, ox - largo, oy, ox + largo, oy)
        self.canvas.coords(self.line2, ox, oy - largo, ox, oy + largo)
        if largo > 0:
            self.canvas.after(interval, lambda:
                              self.reducir_tamano(ox,oy,largo))

# Obtengo el vector de distancias
    radios,lim1,lim2,num_puntos = np.arange(7, 22, 3), -np.pi / 4, np.pi / 4, 3
    estimulos = F.Patron_estimulos(radios,lim1,lim2,num_puntos)

    cantidad_total_estimulos = len(estimulos)
