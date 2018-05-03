import json
import fnmatch
import cv2
import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QDialog, QGridLayout, QPushButton, \
    QAction, QMenuBar, QFileDialog, QCheckBox, QHBoxLayout, QDesktopWidget
from PyQt5.QtGui import QIcon

from drawingCurves import Paint
import utilsPac
import marchingCubes

class MainWindow(QDialog): #ventana principal
    def __init__(self):
        QDialog.__init__(self)

        self.setWindowTitle("3D Cell")
        self.showMaximized() # ventana maximizada por defecto (comentar para probar a reescalar la ventana con la img)

        self.layout = QGridLayout() #dentro del layout se añadirán los botones y la imagen
        self.setLayout(self.layout)

        self.initLayout() #inicializar todos los elementos de la interfaz

        self.paint = Paint() #crear un objeto de la clase Paint para poder dibujar en la interfaz

        self.isOpen() #elegir directorio de la secuencia de imgs

        self.initMenubar() #inicializar las opciones del menú superior de la interfaz

        #añadir todos los elementos a la ventana, indicando su posición Fila, Columna
        self.layout.addWidget(self.menuBar, 0, 0)
        self.layout.addWidget(self.paint, 1, 0)
        self.layout.addLayout(self.grid, 2, 0) #grid contiene diversos elementos: botones, checkbox

    def initLayout(self):
        #configuración de botones y checkbox's
        self.btn_next = QPushButton()
        self.btn_prev = QPushButton()
        self.btn_clear = QPushButton("Clear")
        self.btn_undo = QPushButton("Undo")
        self.check_showC = QCheckBox("Previous Image Curves")
        self.check_showP = QCheckBox("Previous Image Particles")

        self.btn_prev.setIcon(QIcon('resources/back.png'))
        self.btn_next.setIcon(QIcon('resources/next.png'))
        self.check_showC.setChecked(False)
        self.check_showP.setChecked(False)

        #conectar el click de cada botón/checkbox con su acción correspondiente
        self.btn_clear.clicked.connect(self.isClear)
        self.btn_next.clicked.connect(self.isNext)
        self.btn_prev.clicked.connect(self.isPrev)
        self.check_showC.clicked.connect(self.isShow)
        self.check_showP.clicked.connect(self.isShow)
        self.btn_undo.clicked.connect(self.isUndo)

        #ajustar tamaño de algunos botones
        self.btn_next.setFixedWidth(50)
        self.btn_prev.setFixedWidth(50)
        self.btn_clear.setFixedWidth(50)
        self.btn_undo.setFixedWidth(50)

        box = QHBoxLayout() #panel para los controles
        self.grid = QGridLayout() #grid para colocar los controles dentro del panel

        #añadir controles al panel
        box.addWidget(self.btn_prev)
        box.addWidget(self.btn_next)
        box.addStretch()
        box.addWidget(self.check_showC)
        box.addWidget(self.check_showP)
        box.addWidget(self.btn_undo)
        box.addWidget(self.btn_clear)
        #añadir panel al grid
        self.grid.addLayout(box, 0, 0)

    def initMenubar(self):
        self.menuBar = QMenuBar(self)
        #opciones del menú y sus acciones asociadas
        fileMenu = self.menuBar.addMenu("File")

        openAction = QAction('Open image sequence...', self)
        fileMenu.addAction(openAction)
        openAction.triggered.connect(self.isOpen)

        exitAction = QAction('Exit', self)
        fileMenu.addAction(exitAction)
        exitAction.triggered.connect(self.close)

        displayMenu = self.menuBar.addMenu("Display")
        genAction = QAction('Generate 3D structure', self)
        displayMenu.addAction(genAction)
        genAction.triggered.connect(self.gen3D)

    def isOpen(self):#cuando se elige la opción 'open image sequence'
        self.dir = str(QFileDialog.getExistingDirectory(self, "Select Directory")) #directorio seleccionado
        if self.dir: #si se ha elegido algún directorio...

            #crear carpeta donde guardaremos todos los datos que saquemos de la app
            if not os.path.exists(self.dir + "/data/"):
                os.makedirs(self.dir + "/data/")

            self.imgSequence = fnmatch.filter(os.listdir(self.dir), '*.jpg')  #quedarnos con la secuencia de imágenes (.jpg)
            if self.imgSequence: #si esta secuencia no está vacía...
                self.imgN = 0 #comenzamos por la primera
                self.load() #la cargamos en la ventana
                self.paint.globalList = [] #vaciamos su lista global de curvas y partículas (esto es para el UNDO)

            else:
                print("no images in this folder")

        else:
            self.isOpen()

    def UpdateScreenWithImage(self, filename): #para ajustar la img lo máximo posible al tamaño de la pantalla
        img = cv2.imread(filename) #cargar imagen

        actual_height, actual_width , c = img.shape #tomar su altura y anchura (c son los colores rgb)
        screenSize = QDesktopWidget().screenGeometry(-1) # tamaño de la pantalla

        screenHeight = screenSize.height() -150 #quitarle la barra de tareas, y los márgenes de la aplicación (arriba y abajo)
        screenWidth = screenSize.width() -20 #quitarle los márgenes de la aplicación (dcha e izda)

        ratio = actual_width / actual_height #para saber si la imagen es más ancha que alta, o viceversa

        if (screenWidth / ratio > screenHeight): #si la imagen no cabe de ancha...
            scale = screenHeight / actual_height #ajustarla con la altura de la imagen
        else: #si la imagen no cabe de alta...
            scale = screenWidth / actual_width #ajustarla con la anchura de la imagen

        return scale

    def load(self): #para recargar la img con toda su info
        self.setWindowTitle("3D Cell_" + self.imgSequence[self.imgN])  # título de la ventana

        currentImg = self.dir + "/" + self.imgSequence[self.imgN] #imagen actual en la que nos encontramos

        scale = self.UpdateScreenWithImage(currentImg) #calcular su escala con respecto a la pantalla

        if self.check_showC.isChecked(): #si el checkbox 'show prev curves' está activado, mostrar las curvas de la img anterior
            start_time = time.time()
            currentImg = self.paint.showPrevCurves(currentImg, self.dir + "/data/" + self.imgSequence[self.imgN - 1] + ".json")
            print("funcion show: --- %s seconds ---" % (time.time() - start_time))

        self.paint.initIMG(currentImg, scale)  # pintar la imagen en la escena

        self.paint.loadCurves(self.dir + "/data/" + self.imgSequence[self.imgN] + ".json") #cargar todas sus curvas ya dibujadas anteriormente
        self.paint.loadParticles(self.dir + "/data/" + self.imgSequence[self.imgN] + "_particles.json") #cargar todas sus partículas

        if self.check_showP.isChecked(): #si el checkbox 'show prev particles' está activado, mostrar las partículas de la img anterior
            self.paint.showPrevParticles(self.dir + "/data/" + self.imgSequence[self.imgN - 1] + "_particles.json")

    def writeData(self,outputName,dic): #para exportar a json los datos dibujados y generar las máscaras
        with open(outputName, 'w') as f:
            json.dump(dic, f) #pasar el diccionario de curvas/partículas a un archivo .json

            mask = self.paint.generateMask(outputName, dic)


    def gen3D(self): #para generar el 3D
        # escribimos un archivo json con el diccionario de curvas de la imagen (su título es el nombre de la imagen)
        self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
        # escribimos un archivo json con el diccionario de partículas de la imagen (su título es el nombre de la imagen _particles)
        self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

        allParticles = utilsPac.getAllPoints(self.dir + "/data")  # para unir en una sola matriz todos los puntos de todas las partículas de todas las imgs de la secuencia

        #para generar el mesh 3d junto con las partículas marcadas
        threeDeeObj = marchingCubes.threeDeeObject(self.dir + "/data", allParticles)
        threeDeeObj.show3D() #marching cubes + openGL

    def isNext(self): #para pasar a la siguiente img
        if self.imgN < len(self.imgSequence) - 1: #si no es la última img de la secuencia...
            #escribir json's
            self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
            self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

            self.imgN += 1 #pasar a la siguiente imagen de la secuencia

            self.load() #cargar toda su info
            self.paint.globalList = [] #vaciar su lista global de curvas y partículas dibujadas (para el UNDO)

        elif self.imgN == len(self.imgSequence) - 1: #si es la última img de la secuencia...
            #escribir json's
            self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
            self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)
            #no tenemos que cargar ninguna img más, solo vaciar su lista global de curvas y partículas dibujadas (para el UNDO):
            self.paint.globalList = []

        else:
            print("There are no more images for this sequence")

    def isPrev(self): #para pasar a la img anterior
        if self.imgN > 0: #si no es la primera img de la secuencia...
            # escribir json's
            self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
            self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

            self.imgN -= 1 #para pasar a la imagen anterior de la secuencia

            self.load() #cargar toda su info
            self.paint.globalList = [] #vaciar su lista global de curvas y partículas dibujadas (para el UNDO)
        else:
            print("There are no more images for this sequence")

    def isClear(self): #cuando se pulsa el boton CLEAR
        #debemos hacer parte de lo que se hace en la función LOAD, pero no todo
        scale = self.UpdateScreenWithImage(self.dir + "/" + self.imgSequence[self.imgN]) #calculamos escala de la img con la pantalla

        self.paint.initIMG(self.dir + "/" + self.imgSequence[self.imgN], scale)  # pintar la imagen en la escena, SIN curvas ni partículas
        self.paint.globalList = [] #vaciar su lista global de curvas y partículas dibujadas (para el UNDO)

        # dejar vacios los json cuando se pulse CLEAR:
        self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
        self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

    def isShow(self): #cuando se activan los checkbox de mostrar curvas/partículas anteriores
        # escribir json's
        self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
        self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

        self.load() #cargar info de la img

    def isParticles(self): #cuando se activa la opción de mostrar las partículas
        if self.paint.isParticles == False:
            self.paint.isParticles = True
        else:
            self.paint.isParticles = False

        # escribir json's
        self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
        self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

        self.load() #cargar toda la info de la img actual

    def isUndo(self): #para deshacer la curva/partícula más recientemente dibujada
        # escribir json's
        self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
        self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

        globalList = self.paint.globalList #globalList es la lista global de todas las curvas/partículas que se hayan dibujado en la 'sesión' actual

        if globalList: #si se ha dibujado algo nuevo en la sesión actual..
            item = globalList.pop() #sacamos de la lista el último elemento dibujado

            if item.startswith("curve"): #si dicho elemento es una curva...

                if self.paint.curveCounter - 1  > 0: #si ya había alguna curva de otra sesión pasada en el JSON...
                    # actualizar el contador de curvas para que las claves del diccionario sigan un orden lógico
                    curveN = "curve" + str(self.paint.curveCounter - 1)

                    if not len(self.paint.imgCurves)==0: #si el diccionario de curvas de la img actual no está vacío...
                        i = self.paint.imgCurves.pop(curveN) #eliminamos del diccionario de curvas la última curva dibujada
                        #actualizamos el json de curvas de la img
                        self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
                        self.paint.curveCounter -= 1 #actualizamos el contador de curvas
                        self.load() #volvemos a cargar la img con los puntos actualizados

            if item.startswith("particle"): #si dicho elemento es una partícula...

                if self.paint.particleCounter - 1  > 0: #si ya había alguna partícula dibujada de otra sesión pasada en el JSON...
                    # actualizar el contador de partículas para que las claves del diccionario sigan un orden lógico
                    particleN = "particle" + str(self.paint.particleCounter - 1)

                    if not len(self.paint.imgParticles)==0: #si el diccionario de partículas de la img actual no está vacío...
                        self.paint.imgParticles.pop(particleN) #eliminamos del diccionario de partículas la última partícula dibujada
                        # actualizamos el json de partículas de la img
                        self.writeData(self.dir + "/data/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)
                        self.paint.particleCounter -= 1 #actualizamos el contador de partículas
                        self.load() #volvemos a cargar la img con los puntos actualizados
        else:
            print("Nothing to undo")

#para ejecutar la app
app = QApplication(sys.argv)

mainWindow = MainWindow()
mainWindow.show()

app.exec_()