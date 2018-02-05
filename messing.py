import fnmatch
import json
import numpy
import pyqtgraph.opengl as gl
import numpy as np
from os import listdir

faces = np.array([
    [0, 249, 374],
    [0, 249, 498],
    [0, 374, 498],
    [249, 374, 498]
])

colors = np.array([
    [1, 0, 0, 0.3],
    [0, 1, 0, 0.3],
    [0, 0, 1, 0.3],
    [1, 1, 0, 0.3]
])

def createGrid():
    w = gl.GLViewWidget()
    w.show()#showMaximized()
    w.setWindowTitle('pyqtgraph: GLMeshItem')
    w.setCameraPosition(distance=1000)

    g = gl.GLGridItem()
    g.scale(50, 50, 25)
    w.addItem(g)

    return w

def show3D(mat):
    w = createGrid()

    m = gl.GLMeshItem(vertexes=mat, faces=faces, faceColors=colors, smooth=False)
    w.addItem(m)

def getAllPoints(dir):
    jsonFiles = fnmatch.filter(listdir(dir), '*.json')  # secuencia de json

    allPoints = dict()
    imgCount = -1

    for file in jsonFiles:
        if 'particles' not in file:
            file = dir + '/' + file

            with open(file, 'r') as f:
                s = f.read()
                dic = json.loads(s)

                if any(dic):
                    imgCount += 1
                    for keyN, points in dic.items():
                        points = numpy.subtract(points, [-350, -70])
                        allPoints.update({imgCount: points})

    arr = getAllPointsFromDic(allPoints)
    return arr

def getAllPointsFromDic(allPoints):
    allP = []

    if any(allPoints):
        for i in allPoints.keys():
            z = np.ones((len(allPoints[i]), 1)) * (i * 2)  # coordenadas del eje z a añadir
            p = np.hstack((allPoints[i], z))  # añadimos el eje z como una nueva columna

            allP += p.tolist()  # como no me sale con np, lo paso a lista y voy concatenando los puntos con +=

        allP = np.array(allP)  # pasarlo a array otra vez

    return allP

