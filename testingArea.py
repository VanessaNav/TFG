import numpy as np
from matplotlib import path

def getMask(verts, imgShape):
    # Pixel coordinates of the img
    pixx = np.arange(imgShape[0]) #array from 0 to img width
    pixy = np.arange(imgShape[1]) #array from 0 to img height
    xv, yv = np.meshgrid(pixx, pixy) #Return coordinate matrices from coordinate vectors.
    #flatten sirve para convertir los arrays a vectores
    #vstack es para formar una matriz con los puntos correspondientes a los pixeles de la img
    pix = np.vstack((xv.flatten(), yv.flatten())).T #T es la matriz traspuesta

    #first, we have to substract the img position to the points to get the img pixels
    points = np.subtract(verts, [-350, -70])
    #and then get the drawn curve points (p)
    p = path.Path(points)
    #get pixels within the drawn curve
    ind = p.contains_points(pix)#, radius=1)
    ind = ind.reshape((imgShape[1], imgShape[0]))

    return ind
