import json
import cv2
import numpy as np
import time
from matplotlib import path
import fnmatch
from os import listdir

# Package to crop images, generate masks and get particles points

def cropImageBorders(filename): #to crop the image black borders
    # read  image
    img = cv2.imread(filename)

    # threshold image
    ret, threshed_img = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 15, 255, cv2.THRESH_BINARY)
    # find contours and get the external one
    image, contours, hier = cv2.findContours(threshed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # with each contour, get its area and find the bigger one
    aux_area = 0
    for c in contours:
        # get the bounding rect
        contour_area = cv2.contourArea(c)
        if contour_area > aux_area:
            aux_area = contour_area
            x, y, w, h = cv2.boundingRect(c)

    # apply the crop to the bigger area
    crop = img[y:y + h, x:x + w]
    cv2.imwrite(filename, crop)

def getMask(verts, imgShape): #to generate a mask from an image
    # first, we have to substract the img position to the points to get the img pixels
    points = np.subtract(verts, [-350, -70])

    #to reduce the contains_points execution time, for each curve, we get its limits
    curveMax = np.max(points, axis= 0)
    curveMin = np.min(points, axis= 0)

    # Pixel coordinates of the img
    pixx = np.arange(curveMin[0],curveMax[0]) #array from minX to maxX curve limits
    pixy = np.arange(curveMin[1],curveMax[1]) #array from minY to maxY curve limits
    xv, yv = np.meshgrid(pixx, pixy) #Return coordinate matrices from coordinate vectors.
    #flatten sirve para convertir los arrays a vectores
    #vstack es para formar una matriz con los puntos correspondientes a los pixeles de la img
    pix = np.vstack((xv.flatten(), yv.flatten())).T #T es la matriz traspuesta

    #and then get the drawn curve points (p)
    p = path.Path(points)

    #get pixels within the drawn curve --> this is the mask
    startT = time.time()
    ind = p.contains_points(pix)#, radius=1)
    print("containsPoints: --- %s seconds ---" % (time.time() - startT))

    #we have to reshape the mask to the curve's limits
    distX = curveMax[0] - curveMin[0]
    distY = curveMax[1] - curveMin[1]
    ind = ind.reshape((int(distY), int(distX)))

    #the final mask has to contain all the img pixels as zeros, except the ones that conform the curve and its interior
    mask = np.zeros(imgShape, dtype=bool)
    mask[int(curveMin[1]):int(curveMax[1]), int(curveMin[0]):int(curveMax[0])] = ind

    return mask

def getAllPoints(dir): # to get all particles points
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

                if not len(dic)==0:
                    imgCount += 1
                    for keyN, points in dic.items():
                        points = np.array(points)
                        points = np.subtract(points, [-350, -70])

                        imgPoints.append(points)
                        allPoints.update({imgCount: imgPoints})

    arr = getAllPointsFromDic(allPoints)
    return arr

def getAllPointsFromDic(allPoints): # aux function for getAllPoints
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

