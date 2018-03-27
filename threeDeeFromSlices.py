import numpy as np
from skimage import io
import fnmatch
from os import listdir
from skimage import measure
import pyqtgraph.opengl as gl
import matplotlib.pyplot as plt
from matplotlib import path
import masking
import points
from skimage.transform import resize

import marchingCubes

class ThreeDeeObject:
    def __init__(self, dir):#, curves):
        #self.curves = curves

        imgSequence = fnmatch.filter(listdir(dir), '*.jpg')
        firstImg = io.imread(dir + '/' + imgSequence[0])
        self.cube = np.zeros((int(firstImg.shape[0]), int(firstImg.shape[1]), len(imgSequence)), dtype=bool)
        self.imgCurves = points.getDicFromCurves(dir)

    def slicing(self):
        for keyN, curve in self.imgCurves.items():
            mask = masking.getMask(curve, (self.cube.shape[1], self.cube.shape[0]))
            plane = self.cube[:,:,keyN[0]]
            plane[mask] = True
            self.cube[:,:,keyN[0]] = plane

        verts, faces, normals, values = measure.marching_cubes_lewiner(self.cube)  # MC algorithm for curves
        w = marchingCubes.createGrid()
        mesh = gl.GLMeshItem(vertexes=verts, faces=faces, shader='viewNormalColor')  # curves
        w.addItem(mesh)

