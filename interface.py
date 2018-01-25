import json
import fnmatch
import cv2
import sys
from os import listdir
from PyQt5.QtWidgets import QApplication, QDialog, QGridLayout, QPushButton, \
    QAction, QMenuBar, QFileDialog, QCheckBox, QHBoxLayout, QDesktopWidget
from PyQt5.QtGui import QIcon

from drawingCurves import Paint


class MainWindow(QDialog): #ventana principal
    def __init__(self):
        QDialog.__init__(self)

        self.setWindowTitle("drawingCurves")
        self.showMaximized() # ventana maximizada por defecto

        self.layout = QGridLayout() #dentro del layout se añadiran los botones y la imagen
        self.setLayout(self.layout)

        self.initLayout()

        self.paint = Paint()
        self.isOpen()

        self.initMenubar()

        #añadir todos los elementos a la ventana
        self.layout.addWidget(self.menuBar,0,0)
        self.layout.addWidget(self.paint,1,0)
        self.layout.addLayout(self.grid,2,0)

    def initLayout(self):
        #configuracion de botones y checkbox's
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

        self.btn_clear.clicked.connect(self.isClear)
        self.btn_next.clicked.connect(self.isNext)
        self.btn_prev.clicked.connect(self.isPrev)
        self.check_showC.clicked.connect(self.isShow)
        self.check_showP.clicked.connect(self.isShow)
        self.btn_undo.clicked.connect(self.isUndo)

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
        #opciones del menu y sus acciones asociadas
        fileMenu = self.menuBar.addMenu("File")

        openAction = QAction('Open image sequence...', self)
        fileMenu.addAction(openAction)
        openAction.triggered.connect(self.isOpen)

        genAction = QAction('Generate 3D structure', self)
        fileMenu.addAction(genAction)
        genAction.triggered.connect(self.gen3D)

        exitAction = QAction('Exit', self)
        fileMenu.addAction(exitAction)
        exitAction.triggered.connect(self.close)

    def UpdateScreenWithImage(self, filename):
        img = cv2.imread(filename) #cargar imagen

        actual_height, actual_width , c = img.shape #tomar su altura y anchura (c son los colores rgb)
        screenSize = QDesktopWidget().screenGeometry(-1) # tamaño de la pantalla

        screenHeight = screenSize.height() -150 #quitarle la barra de tareas, y los margenes de la aplicacion (arriba y abajo)
        screenWidth = screenSize.width() -20 #quitarle los margenes de la aplicacion (dcha e izda)

        ratio = actual_width / actual_height #para saber si la imagen es mas ancha que alta, o viceversa

        if (screenWidth / ratio > screenHeight): #si la imagen no cabe de ancha...
            scale = screenHeight / actual_height #ajustarla con la altura de la imagen
            #self.resize(screenWidth / ratio, screenHeight +85)
            #self.setGeometry(10,30,screenWidth / ratio, screenHeight)
        else: #si la imagen no cabe de alta...
            scale = screenWidth / actual_width #ajustarla con la anchura de la imagen
            #self.resize(screenWidth, screenHeight * ratio)
            #self.setGeometry(10, 30, screenWidth, screenHeight * ratio)

        return scale

    def writeJSON(self,outputName,dic): #para exportar a json los datos dibujados
        with open(outputName, 'w') as f:
            json.dump(dic, f)

    def load(self):
        self.setWindowTitle("drawingCurves_" + self.imgSequence[self.imgN])  # titulo de la ventana

        scale = self.UpdateScreenWithImage(self.dir + "/" + self.imgSequence[self.imgN])

        self.paint.initIMG(self.dir + "/" + self.imgSequence[self.imgN], scale)  # pintar la siguiente imagen en la escena

        self.paint.loadCurves(self.dir + "/" + self.imgSequence[self.imgN] + ".json")
        self.paint.loadParticles(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json")

        if self.check_showC.isChecked():
            self.paint.showPrevCurves(self.dir + "/" + self.imgSequence[self.imgN - 1] + ".json")

        if self.check_showP.isChecked():
            self.paint.showPrevParticles(self.dir + "/" + self.imgSequence[self.imgN - 1] + "_particles.json")

    def isOpen(self):#cuando se elige la opcion open image sequence
        self.dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.imgSequence = fnmatch.filter(listdir(self.dir), '*.jpg')  # secuencia de imagenes
        if self.imgSequence:
            self.imgN = 0 #comenzar por la primera
            self.load()
            self.paint.globalList = []
        else:
            print("no images in this folder")

    def gen3D(self):
        #os.system("script2.py 1")
        print('llamar al script de blender???')

    def isNext(self): #cuando se pulsa 'siguiente imagen'
        if self.imgN < len(self.imgSequence) - 1:
            # escribimos un archivo json con el diccionario de curvas de una imagen (su titulo es el nombre de la imagen)
            self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
            # escribimos un archivo json con el diccionario de particulas de una imagen (su titulo es el nombre de la imagen_particles)
            self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

            self.imgN += 1 #pasar a la siguiente imagen de la secuencia

            self.load()
            self.paint.globalList = []
        else:
            print("There are no more images for this sequence")

    def isPrev(self): #cuando se pulsa el boton 'imagen anterior'
        if self.imgN > 0:
            # escribimos un archivo json con el diccionario de curvas de una imagen (su titulo es el nombre de la imagen)
            self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
            # escribimos un archivo json con el diccionario de particulas de una imagen (su titulo es el nombre de la imagen_particles)
            self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

            self.imgN -= 1 #para pasar a la imagen anterior de la secuencia

            self.load()
            self.paint.globalList = []
        else:
            print("There are no more images for this sequence")

    def isClear(self): #cuando se pulsa el boton CLEAR
        scale = self.UpdateScreenWithImage(self.dir + "/" + self.imgSequence[self.imgN])

        self.paint.initIMG(self.dir + "/" + self.imgSequence[self.imgN], scale)  # pintar la imagen en la escena, SIN curvas ni puntos
        self.paint.globalList = []

        # dejar vacios los json cuando se pulse clear?
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

    def isShow(self):
        # escribimos un archivo json con el diccionario de curvas de una imagen (su titulo es el nombre de la imagen)
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
        # escribimos un archivo json con el diccionario de curvas de una imagen (su titulo es el nombre de la imagen)
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

        self.load()

    def isParticles(self):
        if self.paint.isParticles == False:
            self.paint.isParticles = True
        else:
            self.paint.isParticles = False

        # escribimos un archivo json con el diccionario de curvas de una imagen (su titulo es el nombre de la imagen)
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
        # escribimos un archivo json con el diccionario de curvas de una imagen (su titulo es el nombre de la imagen)
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

        self.load()

    def isUndo(self):
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

        globalList=self.paint.globalList
        self.load()

        if globalList:
            item = globalList.pop()

            if item.startswith("curve"):

                if self.paint.curveCounter-1 >0:
                    curveN = "curve" + str(self.paint.curveCounter - 1)

                    if any(self.paint.imgCurves):
                        i=self.paint.imgCurves.pop(curveN)
                        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
                        self.paint.curveCounter -= 1
                        self.load()

            if item.startswith("particle"):

                if self.paint.particleCounter-1 >0:
                    particleN = "particle" + str(self.paint.particleCounter - 1)

                    if any(self.paint.imgParticles):
                        self.paint.imgParticles.pop(particleN)
                        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)
                        self.paint.particleCounter -= 1
                        self.load()
        else:
            print("Nothing to undo")

app = QApplication(sys.argv)

mainWindow = MainWindow()
mainWindow.show()

app.exec_()