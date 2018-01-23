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

        self.btn_clear = QPushButton("Clear")
        self.btn_undo = QPushButton("Undo")
        self.check_particles = QCheckBox("Draw Particles")
        self.check_showC = QCheckBox("Previous Image Curves")
        self.check_showP = QCheckBox("Previous Image Particles")

        self.check_showC.setChecked(False)
        self.check_showP.setChecked(False)
        self.check_particles.setChecked(False)

        self.btn_next = QPushButton()
        self.btn_prev = QPushButton()

        self.btn_prev.setIcon(QIcon('resources/back.png'))
        self.btn_next.setIcon(QIcon('resources/next.png'))

        box = QHBoxLayout()
        grid = QGridLayout()

        box.addWidget(self.btn_prev)
        box.addWidget(self.btn_next)
        box.addStretch()
        box.addWidget(self.check_particles)
        box.addWidget(self.check_showC)
        box.addWidget(self.check_showP)
        box.addWidget(self.btn_undo)
        box.addWidget(self.btn_clear)

        grid.addLayout(box,0,0)

        self.isOpen()

        self.menuBar = QMenuBar(self)
        fileMenu = self.menuBar.addMenu("File")
        openAction = QAction('Open image sequence...', self)
        fileMenu.addAction(openAction)
        openAction.triggered.connect(self.load)
        genAction = QAction('Generate 3D structure',self)
        fileMenu.addAction(genAction)
        genAction.triggered.connect(self.gen3D)
        exitAction = QAction('Exit', self)
        fileMenu.addAction(exitAction)
        exitAction.triggered.connect(self.close)
        self.layout.addWidget(self.menuBar,0,0)

        self.layout.addWidget(self.paint,1,0)
        self.layout.addLayout(grid,2,0)

        self.btn_clear.clicked.connect(self.isClear)
        self.btn_next.clicked.connect(self.isNext)
        self.btn_prev.clicked.connect(self.isPrev)
        self.check_showC.clicked.connect(self.isShowC)
        self.check_showP.clicked.connect(self.isShowP)
        self.btn_undo.clicked.connect(self.isUndo)
        self.check_particles.clicked.connect(self.isParticles)

        self.btn_next.setFixedWidth(50)
        self.btn_prev.setFixedWidth(50)
        self.btn_clear.setFixedWidth(50)
        self.btn_undo.setFixedWidth(50)

    def UpdateScreenWithImage(self, filename):
        img = cv2.imread(filename) #cargar imagen

        actual_height, actual_width , c = img.shape #tomar su altura y anchura (c son los colores rgb)
        screenSize = QDesktopWidget().screenGeometry(-1) # tamaño de la pantalla

        screenHeight = screenSize.height() -150 #quitarle la barra de tareas, y los margenes de la aplicacion (arriba y abajo)
        screenWidth = screenSize.width() -20 #quitarle los margenes de la aplicacion (dcha e izda)

        ratio = actual_width / actual_height #para saber si la imagen es mas ancha que alta, o viceversa

        if (screenWidth / ratio > screenHeight): #si la imagen no cabe de ancha...
            scale = screenHeight / actual_height #ajustarla con la altura de la imagen
            #self.resize(screenWidth / ratio, screenHeight)
            #self.setGeometry(10,30,screenWidth / ratio, screenHeight)
        else: #si la imagen no cabe de alta...
            scale = screenWidth / actual_width #ajustarla con la anchura de la imagen
            #self.resize(screenWidth, screenHeight * ratio)
            #self.setGeometry(10, 30, screenWidth, screenHeight * ratio)

        return scale

    def writeJSON(self,outputName,dic): #para exportar a json los datos dibujados
        with open(outputName, 'w') as f:
            json.dump(dic, f)

    def isOpen(self):#cuando se elige la opcion open image sequence
        self.dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        self.imgSequence = fnmatch.filter(listdir(self.dir), '*.jpg')  # secuencia de imagenes
        self.imgN = 0 #comenzar por la primera

        scale=self.UpdateScreenWithImage(self.dir + "/" + self.imgSequence[self.imgN])

        self.paint = Paint(self.dir + "/" + self.imgSequence[self.imgN], scale)

        #self.resize(self.paint.pixMap.width(), self.paint.pixMap.height())

        self.setWindowTitle(self.windowTitle() +"_"+ self.imgSequence[self.imgN])  # titulo de la ventana

        self.paint.loadCurves(self.dir + "/" + self.imgSequence[self.imgN] + ".json")
        self.paint.loadParticles(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json")

        if self.check_showC.isChecked():
            self.paint.showPrevCurves(self.dir + "/" + self.imgSequence[self.imgN - 1] + ".json")

        #if self.check_particles.isChecked():

        if self.check_showP.isChecked():
            self.paint.showPrevParticles(self.dir + "/" + self.imgSequence[self.imgN - 1] + "_particles.json")


    def load(self):
        self.dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        self.imgSequence = fnmatch.filter(listdir(self.dir), '*.jpg')  # secuencia de imagenes
        self.imgN = 0

        self.setWindowTitle(self.imgSequence[self.imgN])  # titulo de la ventana

        scale = self.UpdateScreenWithImage(self.dir + "/" + self.imgSequence[self.imgN])

        self.paint.initIMG(self.dir + "/" + self.imgSequence[self.imgN], scale)  # pintar la siguiente imagen en la escena

        #self.resize(self.paint.pixMap.width(), self.paint.pixMap.height())

        self.paint.loadCurves(self.dir + "/" + self.imgSequence[self.imgN] + ".json")
        self.paint.loadParticles(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json")

        if self.check_showC.isChecked():
            self.paint.showPrevCurves(self.dir + "/" + self.imgSequence[self.imgN - 1] + ".json")

        #if self.check_particles.isChecked():

        if self.check_showP.isChecked():
            self.paint.showPrevParticles(self.dir + "/" + self.imgSequence[self.imgN - 1] + "_particles.json")

    def gen3D(self):
        #os.system("script2.py 1")
        print('llamar al script de blender???')

    def isNext(self): #cuando se pulsa 'siguiente imagen'
        if self.paint.isNext == False:
            self.paint.isNext = True
        else:
            self.paint.isNext = False

        if self.imgN < len(self.imgSequence) - 1:
            # escribimos un archivo json con el diccionario de curvas de una imagen (su titulo es el nombre de la imagen)
            self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)

            # escribimos un archivo json con el diccionario de particulas de una imagen (su titulo es el nombre de la imagen_particles)
            self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

            self.imgN += 1 #pasar a la siguiente imagen de la secuencia

            self.setWindowTitle(self.imgSequence[self.imgN])  # titulo de la ventana

            scale = self.UpdateScreenWithImage(self.dir + "/" + self.imgSequence[self.imgN])

            self.paint.initIMG(self.dir + "/" + self.imgSequence[self.imgN], scale) #pintar la siguiente imagen en la escena

            #self.resize(self.paint.pixMap.width(), self.paint.pixMap.height())

            self.paint.loadCurves(self.dir + "/" + self.imgSequence[self.imgN] + ".json") #cargar sus curvas
            self.paint.loadParticles(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json")

            #if self.check_particles.isChecked(): #si esta a true, cargar tambien sus particulas

            if self.check_showC.isChecked():
                self.paint.showPrevCurves(self.dir + "/" + self.imgSequence[self.imgN - 1] + ".json")

            if self.check_showP.isChecked():
                self.paint.showPrevParticles(self.dir + "/" + self.imgSequence[self.imgN - 1] + "_particles.json")
        else:
            print("There are no more images for this sequence")

    def isPrev(self): #cuando se pulsa el boton 'imagen anterior'
        if self.paint.isPrev == False:
            self.paint.isPrev = True
        else:
            self.paint.isPrev = False

        if self.imgN > 0:
            # escribimos un archivo json con el diccionario de curvas de una imagen (su titulo es el nombre de la imagen)
            self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)

            # escribimos un archivo json con el diccionario de particulas de una imagen (su titulo es el nombre de la imagen_particles)
            self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

            self.imgN -= 1 #para pasar a la imagen anterior de la secuencia

            self.setWindowTitle(self.imgSequence[self.imgN])  # titulo de la ventana

            scale = self.UpdateScreenWithImage(self.dir + "/" + self.imgSequence[self.imgN])

            self.paint.initIMG(self.dir + "/" + self.imgSequence[self.imgN], scale) #pintar la imagen anterior en la escena

            #self.resize(self.paint.pixMap.width(), self.paint.pixMap.height())

            self.paint.loadCurves(self.dir + "/" + self.imgSequence[self.imgN] + ".json")
            self.paint.loadParticles(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json")

            #if self.check_particles.isChecked(): #si esta a true, cargar tambien sus particulas

            if self.check_showC.isChecked():
                self.paint.showPrevCurves(self.dir + "/" + self.imgSequence[self.imgN - 1] + ".json")

            if self.check_showP.isChecked():
                self.paint.showPrevParticles(self.dir + "/" + self.imgSequence[self.imgN - 1] + "_particles.json")
        else:
            print("There are no more images for this sequence")

    def isClear(self): #cuando se pulsa el boton CLEAR
        if self.paint.isClear == False:
            self.paint.isClear = True
        else:
            self.paint.isClear = False

        scale = self.UpdateScreenWithImage(self.dir + "/" + self.imgSequence[self.imgN])

        self.paint.initIMG(self.dir + "/" + self.imgSequence[self.imgN],scale)  # pintar la imagen en la escena, SIN curvas ni puntos

        #self.resize(self.paint.pixMap.width(), self.paint.pixMap.height())

        # dejar vacios los json cuando se pulse clear?
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)


    def isShowC(self):
        if self.paint.isShowC == False:
            self.paint.isShowC = True
        else:
            self.paint.isShowC = False

        # escribimos un archivo json con el diccionario de curvas de una imagen (su titulo es el nombre de la imagen)
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)

        # escribimos un archivo json con el diccionario de curvas de una imagen (su titulo es el nombre de la imagen)
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

        scale = self.UpdateScreenWithImage(self.dir + "/" + self.imgSequence[self.imgN])

        self.paint.initIMG(self.dir + "/" + self.imgSequence[self.imgN],scale)  # pintar la imagen en la escena, SIN curvas ni particulas

        #self.resize(self.paint.pixMap.width(), self.paint.pixMap.height())

        if self.check_showC.isChecked():
            self.paint.showPrevCurves(self.dir + "/" + self.imgSequence[self.imgN - 1] + ".json")

        self.paint.loadCurves(self.dir + "/" + self.imgSequence[self.imgN] + ".json")
        self.paint.loadParticles(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json")

        #if self.check_particles.isChecked():

        if self.check_showP.isChecked():
            self.paint.showPrevParticles(self.dir + "/" + self.imgSequence[self.imgN - 1] + "_particles.json")


    def isShowP(self):
        if self.paint.isShowP == False:
            self.paint.isShowP = True
        else:
            self.paint.isShowP = False

        # escribimos un archivo json con el diccionario de curvas de una imagen (su titulo es el nombre de la imagen)
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)

        # escribimos un archivo json con el diccionario de curvas de una imagen (su titulo es el nombre de la imagen)
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

        scale = self.UpdateScreenWithImage(self.dir + "/" + self.imgSequence[self.imgN])

        self.paint.initIMG(self.dir + "/" + self.imgSequence[self.imgN],scale)  # pintar la imagen en la escena, SIN curvas ni particulas

        #self.resize(self.paint.pixMap.width(), self.paint.pixMap.height())

        if self.check_showP.isChecked():
            self.paint.showPrevParticles(self.dir + "/" + self.imgSequence[self.imgN - 1] + "_particles.json")

        self.paint.loadCurves(self.dir + "/" + self.imgSequence[self.imgN] + ".json")
        self.paint.loadParticles(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json")

        #if self.check_particles.isChecked():

        if self.check_showC.isChecked():
            self.paint.showPrevCurves(self.dir + "/" + self.imgSequence[self.imgN - 1] + ".json")

    def isParticles(self):
        if self.paint.isParticles == False:
            self.paint.isParticles = True
        else:
            self.paint.isParticles = False

        # escribimos un archivo json con el diccionario de curvas de una imagen (su titulo es el nombre de la imagen)
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)

        # escribimos un archivo json con el diccionario de curvas de una imagen (su titulo es el nombre de la imagen)
        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

        scale = self.UpdateScreenWithImage(self.dir + "/" + self.imgSequence[self.imgN])

        self.paint.initIMG(self.dir + "/" + self.imgSequence[self.imgN],scale)  # pintar la imagen en la escena, SIN curvas ni particulas

        #self.resize(self.paint.pixMap.width(), self.paint.pixMap.height())

        self.paint.loadCurves(self.dir + "/" + self.imgSequence[self.imgN] + ".json")

        #if self.check_particles.isChecked():
        self.paint.loadParticles(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json")

        if self.check_showC.isChecked():
            self.paint.showPrevCurves(self.dir + "/" + self.imgSequence[self.imgN - 1] + ".json")

        if self.check_showP.isChecked():
            self.paint.showPrevParticles(self.dir + "/" + self.imgSequence[self.imgN - 1] + "_particles.json")

    def isUndo(self):
        if self.paint.isUndo == False:
            self.paint.isUndo =True
        else:
            self.paint.isUndo = False

        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)

        self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)

        scale = self.UpdateScreenWithImage(self.dir + "/" + self.imgSequence[self.imgN])

        self.paint.initIMG(self.dir + "/" + self.imgSequence[self.imgN],scale)  # pintar la imagen en la escena, SIN curvas

        #self.resize(self.paint.pixMap.width(), self.paint.pixMap.height())

        self.paint.loadCurves(self.dir + "/" + self.imgSequence[self.imgN] + ".json")

        self.paint.loadParticles(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json")

        curveN = "curve" + str(self.paint.curveCounter)
        particleN = "particle" + str(self.paint.particleCounter)

        if any(self.paint.imgCurves):
            self.paint.imgCurves.pop(curveN)
            self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + ".json", self.paint.imgCurves)
            scale = self.UpdateScreenWithImage(self.dir + "/" + self.imgSequence[self.imgN])
            self.paint.initIMG(self.dir + "/" + self.imgSequence[self.imgN],scale)  # pintar la imagen en la escena, SIN curvas
            #self.resize(self.paint.pixMap.width(), self.paint.pixMap.height())
            self.paint.loadCurves(self.dir + "/" + self.imgSequence[self.imgN] + ".json")

        if any(self.paint.imgParticles):
            self.paint.imgParticles.pop(particleN)
            self.writeJSON(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json", self.paint.imgParticles)
            scale = self.UpdateScreenWithImage(self.dir + "/" + self.imgSequence[self.imgN])
            self.paint.initIMG(self.dir + "/" + self.imgSequence[self.imgN],scale)
            #self.resize(self.paint.pixMap.width(), self.paint.pixMap.height())
            self.paint.loadParticles(self.dir + "/" + self.imgSequence[self.imgN] + "_particles.json")



app = QApplication(sys.argv)

mainWindow = MainWindow()
mainWindow.show()

app.exec_()