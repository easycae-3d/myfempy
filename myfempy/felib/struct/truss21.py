# -*- coding: utf-8 -*-
"""
========================================================================
~~~ MODULO DE SIMULACAO ESTRUTURAL PELO METODO DOS ELEMENTOS FINITOS ~~~
       	                    __                                
       	 _ __ ___   _   _  / _|  ___  _ __ ___   _ __   _   _ 
       	| '_ ` _ \ | | | || |_  / _ \| '_ ` _ \ | '_ \ | | | |
       	| | | | | || |_| ||  _||  __/| | | | | || |_) || |_| |
       	|_| |_| |_| \__, ||_|   \___||_| |_| |_|| .__/  \__, |
       	            |___/                       |_|     |___/ 

~~~      Mechanical studY with Finite Element Method in PYthon       ~~~
~~~                PROGRAMA DE ANÁLISE COMPUTACIONAL                 ~~~
~~~              copyright @ 2022, all rights reserved               ~~~
========================================================================
"""

# import sys
import numpy as np
# import scipy.sparse as sp
# from scipy.linalg import block_diag
from myfempy.felib.materset import get_elasticity

#%%------------------------------------------------------------------------------

class Truss21:
    '''Truss 2D 2-node linear Finite Element'''

    def __init__(self, modelinfo):
                              
        self.dofe = modelinfo['nodecon'][0]*modelinfo['nodedof'][0]
        self.fulldof = modelinfo["nodedof"][0]*len(modelinfo["coord"])
        self.nodedof = modelinfo['nodedof'][0]
        self.nelem = len(modelinfo["inci"])
        self.nnode =len(modelinfo["coord"])
        self.inci = modelinfo['inci']
        self.coord = modelinfo['coord']
        self.tabmat = modelinfo['tabmat']
        self.tabgeo = modelinfo['tabgeo']

    
    def elemset():
        
        dofelem = {'key':'truss21',
                   'id': 120,
                   'def':'struct 1D',
                   'dofs': ['ux', 'uy'],
                   'nnodes': ['i', 'j'],
                   'tensor': ['sxx']}
        
        return dofelem

    
    def lockey(self, list_node):
        
        noi = list_node[0]
        noj = list_node[1]
        
        loc = np.array([self.nodedof*noi-2, self.nodedof*noi-1,
                        self.nodedof*noj-2, self.nodedof*noj-1])
    
        return loc
    
    def stiff_linear(self, ee):
        
        noi = int(self.inci[ee,4])
        noj = int(self.inci[ee,5])
        
        noix = self.coord[noi-1,1]
        noiy = self.coord[noi-1,2]
        nojx = self.coord[noj-1,1]
        nojy = self.coord[noj-1,2]
        
        D = get_elasticity(self.tabmat,self.inci,ee)
        E = D[0]
        
        A = self.tabgeo[int(self.inci[ee,3]-1),0]
        
        L = np.sqrt((nojx-noix)**2 + (nojy-noiy)**2)
        s = (nojy-noiy)/L
        c = (nojx-noix)/L
        
        T = np.zeros((self.dofe,self.dofe))
        T[0,0] = c
        T[0,1] = s
        T[1,0] = -s
        T[1,1] = c
        T[2,2] = c
        T[2,3] = s
        T[3,2] = -s
        T[3,3] = c
                
        ket2 = np.zeros((self.dofe,self.dofe))
        ket2[0,0] = 1.0
        ket2[0,2] = -1.0
        ket2[2,0] = -1.0
        ket2[2,2] = 1.0
        ket2 = ((E*A)/L)*ket2
    
        ket2T = np.dot(np.dot(np.transpose(T),ket2),T)
            
        list_node = [noi,noj]
        loc = Truss21.lockey(self, list_node)
    
        return ket2T, loc
    
    # # tensao no elemento de barra
    def matrix_B(self, ee, csc):
            
        noi = int(self.inci[ee,4])
        noj = int(self.inci[ee,5])
        
        noix = self.coord[noi-1,1]
        noiy = self.coord[noi-1,2]
        nojx = self.coord[noj-1,1]
        nojy = self.coord[noj-1,2]
        
        D = get_elasticity(self.tabmat,self.inci, ee)
        E = D[0]
        
        L = np.sqrt((nojx-noix)**2 + (nojy-noiy)**2)
        s = (nojy-noiy)/L
        c = (nojx-noix)/L
        
        T = np.array([[c,s,0,0],\
                      [0,0,c,s]])
                
        B = (E/L)*np.array([-1, 1])
                
        return  B, T