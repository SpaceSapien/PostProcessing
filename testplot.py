'''# the function to be plotted
def func(x,y):
    # gives vertical color bars if x is horizontal axis
    return x

import pylab

# define the grid over which the function should be plotted (xx and yy are matrices)
xx, yy = pylab.meshgrid(
    pylab.logspace(0,2, 101),
    pylab.linspace(-3,3, 111))

# indexing of xx and yy (with the default value for the
# 'indexing' parameter of meshgrid(..) ) is as follows:
#
#   first index  (row index)    is y coordinate index
#   second index (column index) is x coordinate index
#
# as required by pcolor(..)

# fill a matrix with the function values
zz = pylab.zeros(xx.shape)
for i in range(xx.shape[0]):
    for j in range(xx.shape[1]):
        zz[i,j] = func(xx[i,j], yy[i,j])

# plot the calculated function values
pylab.pcolor(xx,yy,zz)

# and a color bar to show the correspondence between function value and color
pylab.colorbar()
pylab.set_xscale('log')
pylab.show()'''

import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

mpl.rcParams['legend.fontsize'] = 10

fig = plt.figure()
ax = fig.gca(projection='3d')
theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)
z = np.linspace(-2, 2, 100)
r = z**2 + 1
x = r * np.sin(theta)
y = r * np.cos(theta)
ax.plot(x, y, z, label='parametric curve')
ax.legend()

plt.show()