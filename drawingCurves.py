import json
import os.path
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsLineItem
from PyQt5.QtCore import QPointF, QRectF, Qt, QLineF
from PyQt5.QtGui import QPen, QBrush, QPixmap, QImage

#COPIA ADAPTADA DE: http://jquery-manual.blogspot.com.es/2015/07/16-python-pyqt-interfaz-grafica.html



from erosioning import cropImageBorders

class Paint(QGraphicsView): #clase para crear el plano donde podremos dibujar
    def __init__(self):
        QGraphicsView.__init__(self)

        r=QRectF(self.viewport().rect())
        self.setSceneRect(r)
        self.scene = QGraphicsScene() # escena que debemos añadir al plano de dibujo

        self.isParticles = False #para dibujar particulas

        self.penColors = [Qt.red, Qt.magenta, Qt.blue, Qt.green] #lista de colores para el pen

        self.globalList = []  # lista para llevar ordenados los ids de curvas y particulas de las imagenes (para el UNDO)

        self.N = 10 #numero de puntos a partir del cual lo dibujado se corresponde a una curva y no a una particula

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
        scenePix = self.scene.addPixmap(self.pixMap)  # añadimos la imagen (escalada) a la escena
        scenePix.setPos(-350, -70)  # para que la imagen este en la esquina superior izquierda
        #scenePix.setPos(-160, -70)  # para que la imagen este en la esquina superior izquierda

    def draw(self, e, thickness, brushPattern, width=1): #funcion para pintar
        self.pen = QPen(self.penColors[self.colorN])
        self.pen.setWidth(width)
        brush = QBrush(brushPattern) #para que lo que se dibuje no tenga transparencia
        # incluir el pen a la escena: el pen dibuja circulos (puntos gordos)
        self.scene.addItem(self.scene.addEllipse(e.x(), e.y(), thickness, thickness, self.pen, brush))

        self.scene.update() #para actualizar los puntos dibujados con el raton

    def mousePressEvent(self, event): #cuando se pulsa el raton
        e = QPointF(self.mapToScene(event.pos())) #crear un punto en la posición marcada por el raton

        self.colorN = 0
        self.pointList.append((e.x(), e.y()))  # añadir el punto a la lista de puntos para las curvas

        self.draw(e, 1, Qt.SolidPattern) #para dibujar el punto de la curva/particula

    def mouseMoveEvent(self, event): #cuando se mueve el raton
        e = QPointF(self.mapToScene(event.pos()))#crear un punto en la posición marcada por el raton

        self.colorN = 0
        self.pointList.append((e.x(), e.y()))  # añadir el punto a la lista de puntos para las curvas

        self.draw(e, 1, Qt.SolidPattern) #para dibujar el punto de la curva/particula

    def mouseReleaseEvent(self, event, scale=None):
        if len(self.pointList) > self.N:
            self.isParticles = False

            if not scale == None: #aplicar escala a la imagen
                self.pointList = [ (x * scale, y * scale) for (x, y) in self.pointList ]

            # terminar la curva con una linea recta
            start = self.pointList[0]
            end = self.pointList[len(self.pointList) - 1]
            self.endCurveWithLine(start, end)

            curveN = "curve" + str(self.curveCounter)
            self.curveCounter += 1  # el contador de curva es la clave del diccionario

            # diccionario para asociar una lista de puntos a cada una de las curvas de la imagen
            self.imgCurves.update({curveN:self.pointList})

            #añadir el id de la curva a la lista global
            self.globalList.append(curveN)

            # una vez guardados los puntos de una curva, reiniciamos la lista de puntos
            self.pointList = []
        else:
            self.isParticles = True

            particle = self.pointList.pop()

            if not scale == None:  # aplicar escala a la imagen
                #self.particleList = [(x * scale, y * scale) for (x, y) in self.particleList]
                particle[0] = particle[0] * scale
                particle[1] = particle[1] * scale

            particleN = "particle" + str(self.particleCounter)
            self.particleCounter += 1  # el contador de particula es la clave del diccionario

            # diccionario para asociar una lista de puntos a cada una de las particulas de la imagen
            self.imgParticles.update({particleN: particle})

            # añadir el id de la particula a la lista global
            self.globalList.append(particleN)

            # una vez guardados los puntos de una particula, reiniciamos la lista de particulas
            self.pointList = []

            self.colorN = 2
            e = QPointF(particle[0], particle[1])
            self.draw(e, 8, Qt.NoBrush, 2)

    def endCurveWithLine(self, start, end):
        startPoint = QPointF(start[0], start[1])
        endPoint = QPointF(end[0], end[1])
        self.line = QGraphicsLineItem(QLineF(startPoint, endPoint))
        self.pen.setWidth(2)
        self.line.setPen(self.pen)
        self.scene.addItem(self.line)

    def loadCurves(self, inputName, scale=None):
        self.colorN = 0
        if os.path.isfile(inputName):
            with open(inputName, 'r') as f:
                s=f.read()
                self.imgCurves = json.loads(s)
                if any(self.imgCurves):
                    self.drawPastCurves(self.imgCurves, 1, Qt.SolidPattern, scale)
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
                    self.drawPastParticles(self.imgParticles, 8, Qt.NoBrush, scale)
                else:
                    print("there are no particles for this image")
        else:
            print("there's no json file for this image")

    def drawPastCurves(self, dic, thickness, brushPattern, scale):
        for curve, points in dic.items():
            self.curveCounter += 1
            if not scale == None:  # aplicar escala a la imagen
                points = [(x / scale, y / scale) for (x, y) in points]

            for p in points:
                e = QPointF(p[0], p[1])  # crear un punto en la posición marcada por el json
                self.draw(e, thickness, brushPattern)

            # terminar la curva con una linea recta
            start = points[0]
            end = points[len(points) - 1]
            self.endCurveWithLine(start, end)


    def drawPastParticles(self, dic, thickness, brushPattern, scale):
        for keyN, particle in dic.items():
            self.particleCounter += 1
            if not scale == None:
                particle[0] = particle[0] / scale
                particle[1] = particle[1] / scale
            e = QPointF(particle[0], particle[1])
            self.draw(e, thickness, brushPattern, 2)

    def showPrevCurves(self, inputName, scale=None):
        self.colorN = 1
        if os.path.isfile(inputName):
            with open(inputName, 'r') as f:
                s = f.read()
                dic = json.loads(s)
                if any(dic):
                    self.drawPastCurves(dic, 1, Qt.SolidPattern, scale)
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
                    self.drawPastParticles(dic, 8, Qt.NoBrush, scale)
                else:
                    print("there are no particles for this image")
        else:
            print("there's no json file for this image")


