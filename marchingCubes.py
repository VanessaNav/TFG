import fnmatch
import json
from os import listdir
import cv2
from PyQt5.QtGui import QColor
from skimage import io
from skimage.transform import resize
from skimage import measure
import numpy as np
import pyqtgraph.opengl as gl

def createGrid():
    w = gl.GLViewWidget()
    w.setBackgroundColor(QColor(255,255,255))
    w.show()#showMaximized()
    w.setWindowTitle('pyqtgraph: GLMeshItem')
    w.setCameraPosition(distance=200)

    g = gl.GLGridItem(color=(0.,0.,0.,1.))
    g.scale(20, 20, 10)
    w.addItem(g)

    return w

def particlesIn3D(particles, w):
    md = gl.MeshData.sphere(rows=7, cols=7)

    for part in particles:
        m = gl.GLMeshItem(meshdata=md, smooth=True, color=(0, 0, 0, 1), shader='edgeHilight', glOptions='opaque')
        m.translate(part[2], part[0], part[1])

        w.addItem(m)

def euclDistanceFromCenter(mask): #mask: 0 negro/false y 1 blanco/true
    pointsX, pointsY = np.where(mask) #nos quedamos con las coordenadas x e y de los puntos donde la mascara esta a true
    meanPoint = (np.mean(pointsX), np.mean(pointsY)) #punto medio
    #en el punto medio, la img tendrá la mayor intensidad

    distances = np.full(mask.shape, -np.inf, dtype=float) #matriz de distancias inicializada a -inf :
    # representara las distancias de cada punto a true al punto medio

    # distancia euclidea de todos los puntos a true de la mascara y el punto medio
    eucl = np.sqrt(((pointsX - meanPoint[0]) ** 2) +
                   ((pointsY - meanPoint[1]) ** 2))

    distances[mask] = eucl #rellenamos la matriz con las distancias calculadas, solo en aquellos puntos que estan contenidos en la curva dibujada

    return distances

def show3D(dir, particles):
    print('Generating 3D...')

    imgMaskSequence = fnmatch.filter(listdir(dir), '*_maskCurves.png') #mascaras de las imgs:
    #para que se creen las mascaras, en la interfaz hay que pintar las curvas con el checkbox marcado

    nothingToShow = True #si no hay datos de las imgs, no podemos mostrar nada en 3d
    if not len(imgMaskSequence) == 0:
        nothingToShow = False

        numImgs = len(imgMaskSequence)
        counter = 0 #contador de imagen

        for image in imgMaskSequence:

            img = io.imread(dir + '/' + image) #leemos la img correspondiente a la mascara que estamos analizando

            if not np.sum(img)==0: #si la mascara de la img no contiene ninguna curva (esta a 0/negro entera)...

                if counter == 0: #si es la primera img, nos quedamos con su shape como referencia para las demas
                    reference_shape = img.shape
                    #esta sera la shape de la matriz 3d de puntos
                    gridReduced = (numImgs, int(reference_shape[0]/10), int(reference_shape[1]/10))  #reducimos para que podamos ver bien la estructura
                    #antes de reducirlo, solo se veian edges en negro, no se veian las faces de la estructura
                    arr = np.zeros(gridReduced) #3d matrix:
                    #primera dimension: numero de imagenes (cada img es una capa): esta sera la coordenada z
                    #segunda y tercera dimensiones: coordenadas x e y de los ptos
                else:
                    img = resize(img, reference_shape) #aplicamos a las demas imgs la shape de la primera

                reduced_shape = (int(reference_shape[0] / 10), int(reference_shape[1] / 10)) #reducimos la mascara de la imagen para tener menos puntos en el 3d
                # antes de reducirlo, solo se veian edges en negro, no se veian las faces de la estructura
                img = resize(img, reduced_shape)

                img[img == 255] = 1 #para poder convertir la mascara a mascara booleana, primero debemos convertir los blancos (255) a 1
                img = img.astype(bool)

                # Para suavizar los escalones entre las curvas, vamos a ir 'desvaneciendo' la img conforme mas se acerque al contorno de la curva
                dis = euclDistanceFromCenter(img) #calculamos la matriz de distancias a partir de la mascara creada

                max = np.max(dis)
                dis = dis / max - 1 #normalizar distancias para que todas esten entre -1 y 0:
                #0 significa que esta dentro de la curva pero lejos del punto medio
                #-1 significa que esta justo en el pto medio
                dis[dis < -1] = 0.5 #las distancias que se quedan en -inf las dejamos en 0.5 (porque son los puntos que no forman parte de la curva)

                dis2 = (dis + 1) * 150 #para comprobar como sale la degradacion, la imprimimos en una img
                #sumamos 1 para volver a dejar DIS dentro del rango del 0 al 1
                #el 150 es para la degradacion de grises del 0 al 150
                cv2.imwrite(dir + "/" + "dis{0}.png".format(counter), dis2)

                arr[counter] = dis #imagen 1 a la capa 1 con intensidad = dis, imagen 2 a la capa 2... etc

                counter += 1

    else:
        print("Nothing to show in 3D")

    if not nothingToShow: #si hay datos de las imgs, podemos llamar a MC

        verts, faces, normals, values = measure.marching_cubes_lewiner(arr) #MC algorithm for curves

        w = createGrid()

        mesh = gl.GLMeshItem(vertexes=verts, faces=faces, shader='viewNormalColor') #curves
        w.addItem(mesh)

        particlesIn3D(particles, w) #particles
