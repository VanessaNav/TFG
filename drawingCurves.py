import json
import os.path
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QPen, QBrush, QPixmap, QImage

#COPIA ADAPTADA DE: http://jquery-manual.blogspot.com.es/2015/07/16-python-pyqt-interfaz-grafica.html

from erosioning import cropImageBorders

class Paint(QGraphicsView): #clase para crear el plano donde podremos dibujar
    def __init__(self):
        QGraphicsView.__init__(self)

        r=QRectF(self.viewport().rect())
        self.setSceneRect(r)
        self.scene = QGraphicsScene() # escena que debemos añadir al plano de dibujo

        self.isParticles = False #para el checkbox 'draw particles' de la ventana

        #self.initIMG(filename,scale) #para pintar la imagen

        self.penColors = [Qt.red, Qt.magenta, Qt.blue, Qt.green] #lista de colores para el pen

        self.globalList = []  # lista para llevar ordenados los ids de curvas y particulas de las imagenes (para el UNDO)

        self.setScene(self.scene) # para incluir la escena en el plano

    def initIMG(self, filename, scale):
        self.scene.clear()  # con clear() se queda el plano en blanco

        self.colorN = 0 #coemnzamos pintando curvas en rojo

        self.imgCurves = dict() #diccionario para guardar cada curva de la imagen como clave, y como valores su lista de puntos
        self.imgParticles = dict() #diccionario para guardar cada particula de la imagen como clave, y como valores su lista de puntos

        self.curveCounter = 1 #contador para indicar la curva
        self.particleCounter = 1  # contador de particulas

        self.pointList = [] #lista de puntos para las curvas de la imagen
        self.particleList = [] #lista de particulas

        cropImageBorders(filename) #para recortar los bordes negros de la imagen

        img = QImage(filename) #convertir la imagen a QImage
        imgS = img.scaled(img.width() * scale, img.height() * scale)  # para escalar la imagen

        self.pixMap = QPixmap().fromImage(imgS) #convertir la imagen a QPixmap

        '''
        sceneW=self.scene.width()
        sceneH=self.scene.height()
        self.scene.setSceneRect(0, 0, sceneW * scale, sceneH * scale)
        '''

        scenePix = self.scene.addPixmap(self.pixMap)  # añadimos la imagen (escalada) a la escena
        scenePix.setPos(-350, -70)  # para que la imagen este en la esquina superior izquierda
        #scenePix.setPos(-160, -70)  # para que la imagen este en la esquina superior izquierda

    def draw(self, e): #funcion para pintar
        pen = QPen(self.penColors[self.colorN])
        brush = QBrush(Qt.SolidPattern) #para que lo que se dibuje no tenga transparencia
        # incluir el pen a la escena: el pen dibuja circulos (puntos gordos)
        self.scene.addItem(self.scene.addEllipse(e.x(), e.y(), 0.1, 0.1, pen, brush))

        self.scene.update() #para actualizar los puntos dibujados con el raton

    def mousePressEvent(self, event): #cuando se pulsa el raton
        e = QPointF(self.mapToScene(event.pos())) #crear un punto en la posición marcada por el raton
        if not self.isParticles:
            self.colorN = 0
            self.pointList.append((e.x(), e.y()))  # añadir el punto a la lista de puntos para las curvas
        else:
            self.colorN = 2
            self.particleList.append((e.x(), e.y()))  # añadir el punto a la lista de particulas

        self.draw(e) #para dibujar el punto de la curva/particula

    def mouseMoveEvent(self, event): #cuando se mueve el raton
        e = QPointF(self.mapToScene(event.pos()))#crear un punto en la posición marcada por el raton
        if not self.isParticles:
            self.colorN = 0
            self.pointList.append((e.x(), e.y()))  # añadir el punto a la lista de puntos para las curvas
        else:
            self.colorN = 2
            self.particleList.append((e.x(), e.y()))  # añadir el punto a la lista de particulas

        self.draw(e) #para dibujar el punto de la curva/particula

    def mouseReleaseEvent(self, event, scale=None):
        if not self.isParticles:
            if not scale == None: #aplicar escala a la imagen
                self.pointList = [ (x * scale, y * scale) for (x, y) in self.pointList ]

            curveN = "curve" + str(self.curveCounter)
            self.curveCounter += 1  # el contador de curva es la clave del diccionario

            # diccionario para asociar una lista de puntos a cada una de las curvas de la imagen
            self.imgCurves.update({curveN:self.pointList})

            #añadir el id de la curva a la lista global
            self.globalList.append(curveN)

            # una vez guardados los puntos de una curva, reiniciamos la lista de puntos
            self.pointList = []
        else:
            if not scale == None:  # aplicar escala a la imagen
                self.particleList = [(x * scale, y * scale) for (x, y) in self.particleList]

            particleN = "particle" + str(self.particleCounter)
            self.particleCounter += 1  # el contador de particula es la clave del diccionario

            # diccionario para asociar una lista de puntos a cada una de las particulas de la imagen
            self.imgParticles.update({particleN: self.particleList})

            # añadir el id de la particula a la lista global
            self.globalList.append(particleN)
            print(self.globalList)

            # una vez guardados los puntos de una particula, reiniciamos la lista de particulas
            self.particleList = []

    def loadCurves(self, inputName, scale=None):
        self.colorN = 0
        if os.path.isfile(inputName):
            with open(inputName, 'r') as f:
                s=f.read()
                self.imgCurves = json.loads(s)
                if any(self.imgCurves):
                    self.drawPastCurves(self.imgCurves, scale)
                else:
                    print("there are no curves for this image")
        else:
            print("there's no json file for this image")

    def loadParticles(self, inputName, scale=None):
        self.colorN = 2
        if os.path.isfile(inputName):
            with open(inputName, 'r') as f:
                s = f.read()
                self.imgParticles = json.loads(s)
                if any(self.imgParticles):
                    self.drawPastParticles(self.imgParticles, scale)
                else:
                    print("there are no particles for this image")
        else:
            print("there's no json file for this image")

    def drawPastCurves(self, dic, scale):
        for curve, points in dic.items():
            self.curveCounter += 1
            if not scale == None:  # aplicar escala a la imagen
                points = [(x / scale, y / scale) for (x, y) in points]

            for p in points:
                e = QPointF(p[0], p[1])  # crear un punto en la posición marcada por el json
                self.draw(e)

    def drawPastParticles(self, dic, scale):
        for particle, points in dic.items():
            self.particleCounter += 1
            if not scale == None:  # aplicar escala a la imagen
                points = [(x / scale, y / scale) for (x, y) in points]

            for p in points:
                e = QPointF(p[0], p[1])  # crear un punto en la posición marcada por el json
                self.draw(e)

    def showPrevCurves(self, inputName, scale=None):
        self.colorN = 1
        if os.path.isfile(inputName):
            with open(inputName, 'r') as f:
                s = f.read()
                dic = json.loads(s)
                if any(dic):
                    self.drawPastCurves(dic, scale)
                else:
                    print("there are no curves for this image")
        else:
            print("there's no json file for this image")

    def showPrevParticles(self, inputName, scale=None):
        self.colorN = 3
        if os.path.isfile(inputName):
            with open(inputName, 'r') as f:
                s = f.read()
                dic = json.loads(s)
                if any(dic):
                    self.drawPastParticles(dic, scale)
                else:
                    print("there are no particles for this image")
        else:
            print("there's no json file for this image")


