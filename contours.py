import numpy as np
import matplotlib.pyplot as plt

from skimage import measure,io

# get the image
r1 = io.imread("IMAGES/C1-64-Sk2-serie2-BC0000.jpg", as_grey=True)

# Find contours at a constant value of 0.8
contours = measure.find_contours(r1, 0.8)

# Display the image and plot all contours found
fig, ax = plt.subplots()
ax.imshow(r1, interpolation='nearest', cmap=plt.cm.gray)

for n, contour in enumerate(contours):
    ax.plot(contour[:, 1], contour[:, 0], linewidth=2)

ax.axis('image')
ax.set_xticks([])
ax.set_yticks([])
plt.show()