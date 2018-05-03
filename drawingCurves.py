#copia MUY adaptada de: http://jquery-manual.blogspot.com.es/2015/07/16-python-pyqt-interfaz-grafica.html
import json
import os.path
import cv2
import numpy
import time
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsLineItem
from PyQt5.QtCore import QPointF, QRectF, Qt, QLineF
from PyQt5.QtGui import QPen, QBrush, QPixmap, QImage, QColor

import utilsPac

class Paint(QGraphicsView): #clase para crear el plano donde podremos dibujar
    def __init__(self):
        QGraphicsView.__init__(self)

        r = QRectF(self.viewport().rect()) #área de la ventana en la que se podrá dibujar
        self.setSceneRect(r)
        self.scene = QGraphicsScene() #escena que debemos añadir al plano de dibujo

        self.isParticles = False #para dibujar partículas

        self.penColors = [Qt.red, QColor.fromRgb(255,105,180), Qt.blue, Qt.green] #lista de colores para el pen (el de rgb es rosa, por si hace falta)

        self.globalList = []  #lista para llevar ordenados los ids de curvas y partículas que se van dibujando en las imgs (para el UNDO)

        self.N = 10 #número de puntos a partir del cual lo dibujado se corresponde a una curva y no a una partícula

        self.setScene(self.scene) #para incluir la escena en el plano

        self.previousPoint = None #para quitar la separación entre puntos cuando se dibuja muy rápido

    def initIMG(self, filename, scale):
        self.scene.clear()  #con clear() se queda el plano en blanco

        self.colorN = 0 #comenzamos pintando curvas en rojo

        self.imgCurves = dict() #diccionario para guardar cada curva de la imagen como clave, y como valores su lista de puntos
        self.imgParticles = dict() #diccionario para guardar cada partícula de la imagen como clave, y como valores su lista de puntos

        self.curveCounter = 1 #contador para indicar la curva
        self.particleCounter = 1  # contador de partículas

        self.pointList = [] #lista de puntos para las curvas de la imagen
        self.particleList = [] #lista de partículas

        utilsPac.cropImageBorders(filename) #recortar los bordes negros de la imagen

        img = QImage(filename) #convertir la imagen a QImage
        imgS = img.scaled(img.width() * scale, img.height() * scale)  #ajustar la img a la pantalla

        self.pixMap = QPixmap().fromImage(imgS) #convertir la imagen a QPixmap
        scenePix = self.scene.addPixmap(self.pixMap)  # añadimos la imagen (escalada) a la escena
        scenePix.setPos(-350, -70)  #esto es para que la imagen este en la esquina superior izquierda

    def draw(self, e, thickness, width=1): #función para pintar con el raton
        self.pen = QPen(self.penColors[self.colorN]) #creamos un pen y le asociamos un color de la lista de colores
        self.pen.setWidth(width) #grosor de la línea
        brush = QBrush(Qt.SolidPattern) #para que lo que se dibuje no tenga transparencia
        # incluir el pen a la escena: el pen dibuja círculos (ellipse con altura=thickness y anchura=thickness), el brush los rellena
        self.scene.addItem(self.scene.addEllipse(e.x(), e.y(), thickness, thickness, self.pen, brush))

        self.scene.update() #para actualizar los puntos dibujados con el ratón

    def mousePressEvent(self, event): #cuando se pulsa el ratón
        e = QPointF(self.mapToScene(event.pos())) #crear un punto en la posición marcada por el ratón

        self.previousPoint = (e.x(), e.y()) #lo guardamos para poder comprobar su distancia con el siguiente punto

        self.colorN = 0 #cuando empezamos a dibujar, siempre pintamos en rojo
        self.pointList.append((e.x(), e.y()))  # añadir el punto a la lista de puntos para las curvas

        self.draw(e, 1) #dibujar el punto de la curva/partícula con una thickness = 1 (grosor del lápiz)

    def mouseMoveEvent(self, event): #cuando se mueve el ratón mientras está pulsado
        e = QPointF(self.mapToScene(event.pos()))#crear un punto en la posición marcada por el ratón

        self.completeWithLine(self.previousPoint, (e.x(), e.y())) #completar los puntos con una línea recta si están muy separados
        self.previousPoint = (e.x(), e.y()) #guardamos el punto para poder calcular la distancia con el siguiente

        self.colorN = 0 #seguimos pintando en rojo
        self.pointList.append((e.x(), e.y()))  # añadir el punto a la lista de puntos para las curvas

        self.draw(e, 1) #dibujar el punto de la curva/partícula con una thickness = 1 (grosor del lápiz)

    def mouseReleaseEvent(self, event, scale=None): #cuando se suelta el ratón
        if len(self.pointList) > self.N: #si el numero de puntos del trazo es mayor que N (N determina si es curva o partícula)...
            self.isParticles = False #el trazo dibujado es una curva

            if not scale == None: #aplicar escala
                self.pointList = [ (x * scale, y * scale) for (x, y) in self.pointList ]

            # terminar la curva con una línea recta
            start = self.pointList[0] #el comienzo de dicha línea sera el primer punto dibujado
            end = self.pointList[len(self.pointList) - 1] #el final de dicha línea sera el último punto dibujado
            self.completeWithLine(start, end) #dibujamos la línea

            curveN = "curve" + str(self.curveCounter) #esto será la clave del diccionario (curve1, curve2...)
            self.curveCounter += 1  #aumentamos el contador de curva

            # diccionario para asociar una lista de puntos a cada una de las curvas de la imagen
            self.imgCurves.update({curveN:self.pointList})

            #añadir el id de la curva a la lista global
            self.globalList.append(curveN)

            # una vez guardados los puntos de una curva, reiniciamos la lista de puntos para poder pintar una nueva curva
            self.pointList = []
        else:
            self.isParticles = True #el trazo dibujado es una partícula

            particle = self.pointList.pop() #si se han dibujado varios puntos, nos quedamos con el último de ellos
            p = particle

            if not scale == None:  # aplicar escala
                p[0] = p[0] * scale
                p[1] = p[1] * scale

            particleN = "particle" + str(self.particleCounter) #clave del diccionario (particle1, particle2...)
            self.particleCounter += 1  #aumentamos el contador de partículas

            # diccionario para asociar una lista de puntos a cada una de las partículas de la imagen
            self.imgParticles.update({particleN: particle})

            # añadir el id de la partícula a la lista global
            self.globalList.append(particleN)

            # una vez guardados los puntos de una partícula, reiniciamos la lista de puntos para poder pintar nuevas partículas
            self.pointList = []

            self.colorN = 2 #las partículas las pintamos en azul
            e = QPointF(p[0], p[1]) #creamos un punto en la posición marcada
            #le restamos 3 píxeles para que el punto se dibuje centrado, justo donde se ha marcado con el ratón
            e.setX(e.x() - 3)
            e.setY(e.y() - 3)

            self.draw(e, 8, 2) #pintamos la partícula, con un grosor de lápiz=8, y un radio de brush=2 (para que se vea bien hermosote)

    def completeWithLine(self, start, end): #función para completar el trazo con líneas rectas
        startPoint = QPointF(start[0], start[1]) #creamos un punto con las coordernadas del punto de inicio
        endPoint = QPointF(end[0], end[1]) #creamos un punto con las coordernadas del punto de fin
        self.line = QGraphicsLineItem(QLineF(startPoint, endPoint)) #dibujamos una línea con esos ptos
        # para que la línea se vea bien, la pintamos un poco más gordita
        self.pen.setWidth(2)
        self.line.setPen(self.pen)

        self.scene.addItem(self.line) #añadimos la línea a la escena

    def loadCurves(self, inputName, scale=None): #función para cargar las curvas de la img actual
        self.colorN = 0 #las curvas de la img actual van en rojo
        if os.path.isfile(inputName): #si hay algún json con curvas de otra sesión anterior...
            with open(inputName, 'r') as f: #lo leemos y escribimos su contenido en el diccionario de curvas de la img
                s = f.read()
                self.imgCurves = json.loads(s)
                if not len(self.imgCurves)==0: #si hay alguna curva en el diccionario...
                    self.drawPastCurves(self.imgCurves, 1, scale) #la dibujamos en la img, con un grosor de lápiz=1 (más finita para que no moleste)
                else:
                    print("there are no curves for this image")
        else:
            print("there's no json file for this image")

    def loadParticles(self, inputName, scale=None): #función para cargar las partículas de la img actual
        self.colorN = 2 #las partículas de la img actual van en azul
        if os.path.isfile(inputName): #si hay algún json con partículas de otra sesión anterior...
            with open(inputName, 'r') as f: #lo leemos y escribimos su contenido en el diccionario de partículas de la img
                s = f.read()
                self.imgParticles = json.loads(s)
                if not len(self.imgParticles)==0: #si hay alguna partícula en el diccionario...
                    self.drawPastParticles(self.imgParticles, 8, scale) #la dibujamos en la img, con un grosor de lápiz=8 (para que se vean bien)
                else:
                    print("there are no particles for this image")
        else:
            print("there's no json file for this image")

    def drawPastCurves(self, dic, thickness, scale): #función para pintar las curvas del json
        for curve, points in dic.items(): #recorremos el diccionario de curvas
            self.curveCounter += 1 #aumentamos el contador de curva para que las claves del diccionario sigan un orden lógico

            if not scale == None:  # aplicar escala
                points = [(x / scale, y / scale) for (x, y) in points]

            for i in range(len(points) - 1): #recorremos la lista de puntos pertenecientes a una curva
                e = QPointF(points[i][0], points[i][1])  # crear un punto en la posición marcada por el json
                self.draw(e, thickness) #dibujarlo con el grosor especificado

                # volver a dibujar los puntos de la curva, sin separaciones entre ellos (para la función completeWithLine)
                distance = numpy.sqrt(
                    ((points[i][0] - points[i + 1][0]) ** 2) +
                    ((points[i][1] - points[i + 1][1]) ** 2)
                )
                if distance > 2: #si la distancia euclídea entre ptos consecutivos es muy grande, debemos rellenar el espacio con una línea recta
                    self.completeWithLine(points[i], points[i + 1])

            # terminar con una línea recta si se deja de dibujar y la curva no estaba completa
            start = points[0]
            end = points[len(points) - 1]
            self.completeWithLine(start, end)

    def drawPastParticles(self, dic, thickness, scale): #función para pintar las partículas del json
        for keyN, particle in dic.items(): #recorremos el diccionario de partículas
            self.particleCounter += 1 #aumentamos el contador de partícula para que las claves del diccionario sigan un orden lógico

            if not scale == None:
                particle[0] = particle[0] / scale
                particle[1] = particle[1] / scale

            e = QPointF(particle[0], particle[1]) #creamos el punto en la posición de la partícula
            self.draw(e, thickness, 2) #la dibujamos gordita

    def showPrevCurves(self, currentImg, prevImg): #función para mostrar curvas de la imagen anterior
        if os.path.isfile(prevImg): #si hay img anterior...

            with open(prevImg, 'r') as f: #leemos su json de curvas y guardamos los ptos en un diccionario
                s = f.read()
                dic = json.loads(s)

                if not len(dic)==0: #si hay alguna curva...
                    mask = self.generateMask(prevImg, dic) #generamos la máscara de la img y sus curvas
                    img = cv2.imread(currentImg) #leemos la img actual
                    # escalamos esta img con el tamaño de la máscara de la img antetior para que casen bien
                    small = cv2.resize(img, (mask.shape[1], mask.shape[0]))
                    small[mask==0] //= 2 #mostramos la img actual oscurecida en los ptos de la máscara que estén a 0 (negro)

                    # volvemos a hacer resize (primero con la Y y luego la X) para mostrar la img en la ventana:
                    img = cv2.resize(small, (img.shape[1], img.shape[0]))

                    head, sep, tail = currentImg.rpartition("/") #para meterlo en la carpeta data
                    currentImgData = head + "/data/" + tail

                    cv2.imwrite(currentImgData + '_masked.png' ,img) #guardamos la mascara en un png para comprobar

                    return currentImgData + '_masked.png' #la devolvemos

                else: #si no hay curvas
                    img = cv2.imread(currentImg) #leemos la img actual
                    img //= 2 #oscurecemos toda la img, puesto que no hay ninguna curva en la img anterior (su máscara sería todo 0's)

                    head, sep, tail = currentImg.rpartition("/")  # para meterlo en la carpeta data
                    currentImgData = head + "/data/" + tail
                    
                    cv2.imwrite(currentImgData + '_masked.png', img) #guardamos la máscara en un png para comprobar

                    return currentImgData + '_masked.png' #la devolvemos
        else:
            return currentImg


    def showPrevParticles(self, inputName, scale=None): #función para mostrar partículas de la imagen anterior
        self.colorN = 3 #las pintamos en verde

        if os.path.isfile(inputName): #si existe un fichero de partículas de la img anterior, lo leemos y cargamos los ptos en el diccionario

            with open(inputName, 'r') as f:
                s = f.read()
                dic = json.loads(s)

                if not len(dic)==0: #si no está vacío, dibujamos los puntos gorditos
                    self.drawPastParticles(dic, 8, scale)

                else:
                    print("there are no particles for this image")
        else:
            print("there's no json file for this image")

    def generateMask(self, outputName, dic): #generar la máscara de una img: 0 negro (fuera de la curva), 255 blanco (area dentro de la curva)

        if 'particles' not in outputName: #si es curva..
            finalMaskCurves = numpy.zeros((self.pixMap.height(), self.pixMap.width())) #creamos un array de 0's (toda la máscara negra al ppio)

            for keyN, points in dic.items(): #recorremos las curvas
                #para cada curva, generamos su máscara correspondiente
                mask = utilsPac.getMask(dic[keyN], (self.pixMap.height(), self.pixMap.width())) #obtenemos la máscara (esta función es la más pesada)
                finalMaskCurves[mask] = 255 #los puntos dentro de la curva seran blancos (255)

            cv2.imwrite(outputName + '_maskCurves.png', finalMaskCurves)
            return finalMaskCurves

        else: #si es partícula...
            finalMaskParticles = numpy.zeros((self.pixMap.height(), self.pixMap.width())) #creamos un array de 0's (toda la máscara negra al ppio)

            for keyN, points in dic.items(): #recorremos las partículas
                px = int(points[0]) + 350 #coordenada x de la partícula (hay que sumarle la posición absoluta que le aplicamos a la img al ppio)
                py = int(points[1]) + 70 #coordenada y
                #primero la y y luego la x: 'x' son las columnas e 'y' las filas de la matriz de la imagen
                finalMaskParticles[py, px] = 255 #ponemos a blanco las posiciones de la máscara en las que hay partícula

            #cv2.imwrite(outputName + '_maskParticles.png', self.finalMaskParticles)
            return finalMaskParticles