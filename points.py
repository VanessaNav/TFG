import fnmatch
import json
import numpy
import numpy as np
from os import listdir

class pointsObject():
    def __init__(self, dir):
        self.dir = dir

    def getAllPoints(self):
        jsonFiles = fnmatch.filter(listdir(self.dir), '*.json')  # secuencia de json

        allPoints = dict()
        imgCount = -1

        for file in jsonFiles:
            imgPoints = []

            if 'particles' in file:
                file = self.dir + '/' + file

                with open(file, 'r') as f:
                    s = f.read()
                    dic = json.loads(s)

                    if not len(dic)==0:
                        imgCount += 1
                        for keyN, points in dic.items():
                            points = numpy.array(points)
                            points = numpy.subtract(points, [-350, -70])

                            imgPoints.append(points)
                            allPoints.update({imgCount: imgPoints})

        arr = self.getAllPointsFromDic(allPoints)
        return arr

    def getAllPointsFromDic(self, allPoints):
        allP = []

        if not len(allPoints)==0:
            for i in allPoints.keys():
                z = np.ones((len(allPoints[i]), 1)) * i  # coordenadas del eje z a añadir
                p = np.hstack((allPoints[i], z))  # añadimos el eje z como una nueva columna

                allP += p.tolist()  # como no me sale con np, lo paso a lista y voy concatenando los puntos con +=

            allP = np.array(allP)  # pasarlo a array otra vez

            red_allP = np.array([10,10,1])
            allP = allP / red_allP

        return allP

