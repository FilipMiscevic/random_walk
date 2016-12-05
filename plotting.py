from animals import *
from generate_animal_graphs import *
from numpy.random import seed,choice
import random
from itertools import groupby
import itertools
import pylab,scipy
import csv,re
import os
from mpl_toolkits.mplot3d import Axes3D,proj3d
from matplotlib import cm,markers
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from matplotlib._png import read_png
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from clustering import *

## generic plotting methods

def plot_curve(x,y,z,x_lab='',y_lab='',z_lab='',title='',color='none'):
    '''List,List,List -> None
    Given lists of x,y,z coordinates, plot a 3 dimensional surface.'''
    
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    #X = np.arange(-5, 5, 0.25)
    #Y = np.arange(-5, 5, 0.25)
    z = map(float, z)
    grid_x, grid_y = np.mgrid[min(x):max(x):100j, min(y):max(y):100j]
    grid_z = griddata((x, y), z, (grid_x, grid_y), method='cubic')    

    ax.plot_surface(grid_x, grid_y, grid_z, cmap=plt.cm.Spectral)
    
    ax.set_xlabel(x_lab)
    ax.set_ylabel(y_lab)
    ax.set_zlabel(z_lab)    
    #ax.set_title(title)
    
    #plt.show()
    
    plt.savefig(title)
    
    #Z = np.sin(R)
    ##surf = ax.plot_surface(grid_x, grid_y, grid_z, rstride=1, cstride=1, cmap=cm.coolwarm,
    ##                       linewidth=0, antialiased=False)
    ##ax.set_zlim(-1.01, 1.01)
    
    ##ax.zaxis.set_major_locator(LinearLocator(10))
    ##ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
    
    ##fig.colorbar(surf, shrink=0.5, aspect=5)
    return fig

def plot_scatter(X,Y,Z,x_lab='',y_lab='',z_lab='',title='',label=None,color='none'):
    '''Plot a 3-dimensional scatter plot.'''
    fig = plt.figure()

    if not Z:
        ax = fig.add_subplot(111)
        ax.scatter(X,Y,label=label,c=color)#,c=color)#, s=area, c=colors, alpha=0.5)
    else: 
        ax = fig.add_subplot(111, projection='3d')
        ax.set_zlabel(z_lab) 

        ax.scatter(X,Y,Z,label=label,c=color)
    
    ax.set_xlabel(x_lab)
    ax.set_ylabel(y_lab)
    ax.set_title(title)
    
    
    #plt.show()
    return fig,ax

def plot_scatter2(X,Y,Z,Q,x_lab='',y_lab='',z_lab='',color='none',title=''):
    '''Plot a 3-dimensional scatter plot with two data series in the Z axis.'''
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    n = 100
    for c, m, z_i in [('b', '^', Z), (color, 'o', Q)]:

        ax.scatter(X,Y,z_i, c=c, marker=m)
    
    ax.set_xlabel(x_lab)
    ax.set_ylabel(y_lab)
    ax.set_zlabel(z_lab) 
    ax.set_title(title)    
    
    #plt.show()
    
    return fig