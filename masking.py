import numpy as np
import time
from matplotlib import path

class maskerObj():
    def __init__(self, verts, imgShape):
        self.verts = verts
        self.imgShape = imgShape

    def getMask(self):
        # first, we have to substract the img position to the points to get the img pixels
        points = np.subtract(self.verts, [-350, -70])

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
        mask = np.zeros(self.imgShape, dtype=bool)
        mask[int(curveMin[1]):int(curveMax[1]), int(curveMin[0]):int(curveMax[0])] = ind

        return mask
