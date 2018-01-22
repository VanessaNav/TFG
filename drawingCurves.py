import json
from os import listdir
import os.path
import fnmatch
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QGraphicsView, QGraphicsScene, QGridLayout, QPushButton, QGroupBox, \
    QAction, QMainWindow, QMenuBar, QFileDialog, QCheckBox, QHBoxLayout, QLabel
from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QPen, QBrush, QPixmap, QImage, QIcon

#COPIA ADAPTADA DE: http://jquery-manual.blogspot.com.es/2015/07/16-python-pyqt-interfaz-grafica.html

from erosioning import cropImageBorders


class Paint(QGraphicsView): #clase para crear el plano donde podremos dibujar
    def __init__(self,filename,scale):
        QGraphicsView.__init__(self)

        r=QRectF(self.viewport().rect())
        self.setSceneRect(r)

        self.scene = QGraphicsScene() # escena que debemos añadir al plano de dibujo

        self.isClear = False #para los botones de la ventana
        self.isNext = False
        self.isPrev = False
        self.isShow = False
        self.isParticles = False
        self.isUndo = False

        self.initIMG(filename,scale) #para pintar la imagen

        self.penColors = [Qt.red, Qt.magenta, Qt.blue, Qt.green] #lista de colores para el pen

        self.setScene(self.scene) # para incluir la escena en el plano

    def initIMG(self,filename,scale):
        self.scene.clear()  # con clear() se queda el plano en blanco

        self.imgCurves = dict() #diccionario para guardar cada curva de la imagen como clave, y como valores su lista de puntos
        self.imgParticles = dict() #diccionario para guardar cada particula de la imagen como clave, y como valores su lista de puntos

        self.colorN = 0

        self.curveCounter = 0 #contador para indicar la curva
        self.pointList = [] #lista de puntos para las curvas de la imagen

        self.particleCounter = 0 #contador de particulas
        self.particleList = [] #lista de particulas

        cropImageBorders(filename)

        img = QImage(filename)
        imgS = img.scaled(img.width() * scale, img.height() * scale)  # para escalar la imagen

        self.pixMap = QPixmap().fromImage(imgS)
        scenePix = self.scene.addPixmap(self.pixMap)  # añadimos la imagen (escalada) a la escena
        scenePix.setPos(-350, -70)  # para que la imagen este en la esquina superior izquierda

    def draw(self, e): #funcion para pintar
        pen = QPen(self.penColors[self.colorN])
        brush = QBrush(Qt.SolidPattern) #para que lo que se dibuje no tenga transparencia

        # incluir el pen a la escena: el pen dibuja circulos (puntos gordos)
        self.scene.addItem(self.scene.addEllipse(e.x(), e.y(), 0.1, 0.1, pen, brush))

        self.scene.update() #para actualizar los puntos dibujados con el raton

    def mousePressEvent(self, event): #cuando se pulsa el raton
        e = QPointF(self.mapToScene(event.pos())) #crear un punto en la posición marcada por el raton

        if self.isParticles:
            self.colorN = 2
            self.particleList.append((e.x(), e.y()))  # añadir el punto a la lista de particulas
            self.draw(e) #dibujar la particula

        if not self.isParticles:
            self.colorN = 0
            self.pointList.append((e.x(), e.y()))  # añadir el punto a la lista de puntos
            self.draw(e) #para dibujar el punto

    def mouseMoveEvent(self, event): #cuando se mueve el raton
        e = QPointF(self.mapToScene(event.pos()))#crear un punto en la posición marcada por el raton
        #print(event.pos())

        if self.isParticles:
            self.colorN = 2
            self.particleList.append((e.x(), e.y()))  # añadir el punto a la lista de particulas
            self.draw(e)

        if not self.isParticles:
            self.colorN = 0
            self.pointList.append((e.x(), e.y()))  # añadir el punto a la lista de puntos
            self.draw(e) #para dibujar el punto

    def mouseReleaseEvent(self, event, scale=None):
        if not self.isParticles:
            if event.button() == Qt.LeftButton:
                print("Curve saved")

            if not scale == None: #aplicar escala a la imagen
                self.pointList = [ (x * scale, y * scale) for (x, y) in self.pointList ]

            self.curveCounter += 1  # el contador de curva es la clave del diccionario
            curveN = "curve" + str(self.curveCounter)

            # diccionario para asociar una lista de puntos a cada una de las curvas de la imagen
            self.imgCurves.update({curveN:self.pointList})

            # una vez guardados los puntos de una curva, reiniciamos la lista de puntos
            self.pointList = []
        else:
            if event.button() == Qt.LeftButton:
                print("Point saved")

            if not scale == None:  # aplicar escala a la imagen
                self.particleList = [(x * scale, y * scale) for (x, y) in self.particleList]

            self.particleCounter += 1  # el contador de particula es la clave del diccionario
            particleN = "particle" + str(self.particleCounter)

            # diccionario para asociar una lista de puntos a cada una de las particulas de la imagen
            self.imgParticles.update({particleN: self.particleList})

            # una vez guardados los puntos de una particula, reiniciamos la lista de particulas
            self.particleList = []

    def loadPoints(self, inputName, scale=None):
        if not self.isParticles:
            self.colorN = 0
            if os.path.isfile(inputName):
                with open(inputName, 'r') as f:
                    s=f.read()
                    self.imgCurves = json.loads(s)
                    if any(self.imgCurves):
                        for curve, points in self.imgCurves.items():
                            self.curveCounter += 1
                            if not scale == None:  # aplicar escala a la imagen
                                points = [(x / scale, y / scale) for (x, y) in points]

                            for p in points:
                                e = QPointF(p[0],p[1])  # crear un punto en la posición marcada por el json
                                self.draw(e)
                    else:
                        print("there are no curves for this image")
            else:
                print("there's no json file for this image")
        else:
            self.colorN = 2
            if os.path.isfile(inputName):
                with open(inputName, 'r') as f:
                    s = f.read()
                    self.imgParticles = json.loads(s)
                    if any(self.imgParticles):
                        for particle, points in self.imgParticles.items():
                            self.particleCounter += 1
                            if not scale == None:  # aplicar escala a la imagen
                                points = [(x / scale, y / scale) for (x, y) in points]

                            for p in points:
                                e = QPointF(p[0], p[1])  # crear un punto en la posición marcada por el json
                                self.draw(e)
                    else:
                        print("there are no particles for this image")

    def showPrevPoints(self, inputName, scale=None):
        if not self.isParticles:
            self.colorN = 1
            if os.path.isfile(inputName):
                with open(inputName, 'r') as f:
                    s = f.read()
                    dic = json.loads(s)
                    if any(dic):
                        for curve,points in dic.items():
                            self.curveCounter += 1
                            if not scale == None:  # aplicar escala a la imagen
                                points = [(x / scale, y / scale) for (x, y) in points]

                            for p in points:
                                e = QPointF(p[0],p[1])  # crear un punto en la posición marcada por el json
                                self.draw(e)
                    else:
                        print("there are no curves for this image")
            else:
                print("there's no json file for this image")
        else:
            self.colorN = 3
            if os.path.isfile(inputName):
                with open(inputName, 'r') as f:
                    s = f.read()
                    dic = json.loads(s)
                    if any(dic):
                        for particle, points in dic.items():
                            self.particleCounter += 1
                            if not scale == None:  # aplicar escala a la imagen
                                points = [(x / scale, y / scale) for (x, y) in points]

                            for p in points:
                                e = QPointF(p[0], p[1])  # crear un punto en la posición marcada por el json
                                self.draw(e)
                    else:
                        print("there are no particles for this image")
            else:
                print("there's no json file for this image")


