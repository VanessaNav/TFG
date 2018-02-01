from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np



def createGrid():
    w = gl.GLViewWidget()
    w.show()#showMaximized()
    w.setWindowTitle('pyqtgraph: GLMeshItem')
    w.setCameraPosition(distance=1000)

    g = gl.GLGridItem()
    g.scale(50, 50, 25)
    w.addItem(g)

    return w

def show3D(dic):
    w = createGrid()

    for i in dic.keys():
        z = np.ones( (len(dic[i]), 1) ) * (i+4)
        p = np.hstack((dic[i], z))
        face = np.arange(len(dic[i]))
        m = gl.GLMeshItem(vertexes=p, faces=np.array([face]))  # , faceColors=colors, smooth=False)
        w.addItem(m)


    '''
    npPoints = np.subtract(npPoints, [-350, -70])

    zeros = np.zeros((len(npPoints), 1))
    npPoints = np.hstack((npPoints, zeros))  # añadir eje z 0
    ones = np.ones((len(p2), 1)) 
    #p2 = np.hstack((p2, ones))  # añadir eje z 1

    face = np.arange(len(npPoints))
    #fac2 = np.arange(len(p2))

    m = gl.GLMeshItem(vertexes=npPoints, faces=np.array([face]))  # , faceColors=colors, smooth=False)
    w.addItem(m)

    #me = gl.GLMeshItem(vertexes=p2, faces=np.array([fac2]))  # , faceColors=colors, smooth=False)
    #w.addItem(me)
    '''


