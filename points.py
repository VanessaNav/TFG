import fnmatch
import json
import numpy
import numpy as np
from os import listdir

def getAllCurves(dir):
    jsonFiles = fnmatch.filter(listdir(dir), '*.json')  # secuencia de json

    allPoints = dict()
    imgCount = -1

    for file in jsonFiles:
        imgPoints = []

        if 'particles' not in file:
            file = dir + '/' + file

            with open(file, 'r') as f:
                s = f.read()
                dic = json.loads(s)

                if not dic is None:
                    imgCount += 1
                    for keyN, points in dic.items():
                        for p in range(len(points)):
                            points[p] = numpy.subtract(points[p], [-350, -70])

                        imgPoints.append(points)
                        allPoints.update({imgCount: imgPoints})

    arr = getAllCurvesFromDic(allPoints)
    return arr

def getAllCurvesFromDic(allPoints):
    allP = []

    if not allPoints is None:
        for i in allPoints.keys():
            for imgCurves in allPoints[i]:
                z = np.ones((len(imgCurves), 1)) * i  # coordenadas del eje z a añadir
                p = np.hstack((imgCurves, z))  # añadimos el eje z como una nueva columna

            allP += p.tolist()  # como no me sale con np, lo paso a lista y voy concatenando los puntos con +=

        allP = np.array(allP)  # pasarlo a array otra vez

    return allP

def getDicFromCurves(dir):
    jsonFiles = fnmatch.filter(listdir(dir), '*.json')  # secuencia de json

    allPoints = dict()
    imgCount = -1

    for file in jsonFiles:

        if 'particles' not in file:
            file = dir + '/' + file

            with open(file, 'r') as f:
                s = f.read()
                dic = json.loads(s)

                if not dic is None:
                    imgCount += 1
                    for keyN, points in dic.items():
                        points = numpy.subtract(numpy.array(points), [-350, -70])
                        #for p in range(len(points)):
                            #points[p] = numpy.subtract(points[p], [-350, -70])

                        #imgPoints.append(points)
                        allPoints.update({(imgCount,keyN): points})
    return allPoints


def getAllPoints(dir):
    jsonFiles = fnmatch.filter(listdir(dir), '*.json')  # secuencia de json

    allPoints = dict()
    imgCount = -1

    for file in jsonFiles:
        imgPoints = []

        if 'particles' in file:
            file = dir + '/' + file

            with open(file, 'r') as f:
                s = f.read()
                dic = json.loads(s)

                if not dic is None:
                    imgCount += 1
                    for keyN, points in dic.items():
                        points = numpy.array(points)
                        points = numpy.subtract(points, [-350, -70])

                        imgPoints.append(points)
                        allPoints.update({imgCount: imgPoints})

    arr = getAllPointsFromDic(allPoints)
    return arr

def getAllPointsFromDic(allPoints):
    allP = []

    if not allPoints is None:
        for i in allPoints.keys():
            z = np.ones((len(allPoints[i]), 1)) * i  # coordenadas del eje z a añadir
            p = np.hstack((allPoints[i], z))  # añadimos el eje z como una nueva columna

            allP += p.tolist()  # como no me sale con np, lo paso a lista y voy concatenando los puntos con +=

        allP = np.array(allP)  # pasarlo a array otra vez

        red_allP = np.array([10,10,1])
        allP = allP / red_allP

    return allP

