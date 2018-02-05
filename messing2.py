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


