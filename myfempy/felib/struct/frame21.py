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

import sys
import numpy as np
import scipy.sparse as sp
from scipy.linalg import block_diag
from myfempy.felib.materset import get_elasticity
from myfempy.felib.crossec import cg_coord
from myfempy.bin.tools import loading_bar_v1

#%%------------------------------------------------------------------------------

class Frame21:
    '''Frame 2D 2-node linear Finite Element'''

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
        
        dofelem = {'key':'frame21',
                   'id': 140,
                   'def':'struct 1D',
                   'dofs': ['ux', 'uy', 'rz'],
                   'nnodes': ['i', 'j'],
                   'tensor': ['sxx']}
        
        return dofelem

    
    def lockey(self, list_node):
        
        noi = list_node[0]
        noj = list_node[1]
        
        loc = np.array([self.nodedof*noi-3, self.nodedof*noi-2, self.nodedof*noi-1,
                        self.nodedof*noj-3, self.nodedof*noj-2, self.nodedof*noj-1])
           
        return loc
    
    
    # montagem matriz de rigidez de portico plana
    def stiff_linear(self,ee):
        
        noi = int(self.inci[ee,4])
        noj = int(self.inci[ee,5])
        
        noix = self.coord[noi-1,1]
        noiy = self.coord[noi-1,2]
        nojx = self.coord[noj-1,1]
        nojy = self.coord[noj-1,2]
        
        D = get_elasticity(self.tabmat,self.inci,ee)
        E = D[0]
        
        A = self.tabgeo[int(self.inci[ee,3]-1),0]
        Izz = self.tabgeo[int(self.inci[ee,3]-1),1]
        
        L = np.sqrt((nojx-noix)**2 + (nojy-noiy)**2)
        s = (nojy-noiy)/L
        c = (nojx-noix)/L
            
        T = np.zeros((self.dofe,self.dofe))
        T[0,0] = c
        T[0,1] = s
        T[1,0] = -s
        T[1,1] = c
        T[2,2] = 1.0
        T[3,3] = c
        T[3,4] = s
        T[4,3] = -s
        T[4,4] = c
        T[5,5] = 1.0
            
            
        kef2 = np.zeros((self.dofe,self.dofe))
        kef2[0,0] = (A*E)/L
        kef2[0,3] = -(A*E)/L
        
        kef2[1,1] = 12*(E*Izz)/L**3
        kef2[1,2] = 6*(E*Izz)/L**2
        kef2[1,4] = -12*(E*Izz)/L**3
        kef2[1,5] = 6*(E*Izz)/L**2
        
        kef2[2,1] = 6*(E*Izz)/L**2
        kef2[2,2] = 4*(E*Izz)/L
        kef2[2,4] = -6*(E*Izz)/L**2
        kef2[2,5] = 2*(E*Izz)/L
        
        kef2[3,0] = -(A*E)/L
        kef2[3,3] = (A*E)/L
        
        kef2[4,1] = -12*(E*Izz)/L**3
        kef2[4,2] = -6*(E*Izz)/L**2
        kef2[4,4] = 12*(E*Izz)/L**3
        kef2[4,5] = -6*(E*Izz)/L**2
        
        kef2[5,1] = 6*(E*Izz)/L**2
        kef2[5,2] = 2*(E*Izz)/L
        kef2[5,4] = -6*(E*Izz)/L**2
        kef2[5,5] = 4*(E*Izz)/L
        kef2 = (E*Izz/L**3)*kef2
            
        kef2T = np.dot(np.dot(np.transpose(T),kef2),T)
            
        list_node = [noi,noj]
        loc = Frame21.lockey(self, list_node) 
              
        return kef2T, loc
    
    
    # montagem matriz de massa de portico plana
    def mass(self,ee):
        
        
        noi = int(self.inci[ee,4])
        noj = int(self.inci[ee,5])
        
        noix = self.coord[noi-1,1]
        noiy = self.coord[noi-1,2]
        nojx = self.coord[noj-1,1]
        nojy = self.coord[noj-1,2]
        
        R = self.tabmat[int(self.inci[ee,2]-1),6]
        A = self.tabgeo[int(self.inci[ee,3]-1),0]
        
        L = np.sqrt((nojx-noix)**2 + (nojy-noiy)**2)               
            
        mef2d2 = np.zeros((self.dofe,self.dofe))
        mef2d2[0,0] = 140
        mef2d2[0,3] = 70
        
        mef2d2[1,1] = 156
        mef2d2[1,2] = 22*L
        mef2d2[1,4] = 54
        mef2d2[1,5] = -13*L
        
        mef2d2[2,1] = 22*L
        mef2d2[2,2] = 4*L**2
        mef2d2[2,4] = 13*L
        mef2d2[2,5] = -3*L**2
        
        mef2d2[3,0] = 70
        mef2d2[3,3] = 140
        
        mef2d2[4,1] = 54
        mef2d2[4,2] = 13*L
        mef2d2[4,4] = 156
        mef2d2[4,5] = -22*L
        
        mef2d2[5,1] = -13*L
        mef2d2[5,2] = -3*L**2
        mef2d2[5,4] = -22*L
        mef2d2[5,5] = 4*L**2
        mef2d2 = (R*A*L/420)*mef2d2
        
        list_node = [noi,noj]
        loc = Frame21.lockey(self, list_node)
        
        return mef2d2, loc
    
        
    def intforces(self, U, lines):
        
        Fint=np.zeros((self.fulldof),dtype=float)
        Nx = np.zeros((len(lines[0][1]),len(lines)),dtype=float)
        Vy = np.zeros((len(lines[0][1]),len(lines)),dtype=float)
        Mz = np.zeros((len(lines[0][1]),len(lines)),dtype=float)
        domL = np.zeros((len(lines[0][1]),len(lines)),dtype=float)
        
        for ee in range(self.nelem):
    
            noi = int(self.inci[ee,4])
            noj = int(self.inci[ee,5])
            noix = self.coord[noi-1,1]
            noiy = self.coord[noi-1,2]
            nojx = self.coord[noj-1,1]
            nojy = self.coord[noj-1,2]
                          
            L = np.sqrt((nojx-noix)**2 + (nojy-noiy)**2)
            s = (nojy-noiy)/L
            c = (nojx-noix)/L
                
            T = np.zeros((self.dofe,self.dofe))
            T[0,0] = c
            T[0,1] = s
            T[1,0] = -s
            T[1,1] = c
            T[2,2] = 1.0
            T[3,3] = c
            T[3,4] = s
            T[4,3] = -s
            T[4,4] = c
            T[5,5] = 1.0
            
            kef2T, loc = Frame21.stiff_linear(self, ee)
            kef2 = np.dot(np.dot(np.transpose(T),kef2T),T)
                
            F = np.dot(kef2,T@U[loc])
            Fint[loc] = [-F[0],F[1],-F[2],F[3],-F[4],F[5]]
        

        for ed in range(len(lines)):
            nnodes = lines[ed][1]
            
            for nn in range(0,len(nnodes)):
                node = int(nnodes[nn])
                Nx[nn,ed] = Fint[self.nodedof*node-3]
                Vy[nn,ed] = Fint[self.nodedof*node-2]
                Mz[nn,ed] = Fint[self.nodedof*node-1]
                domL[nn,ed] = self.coord[node-1,1]
                
            domLIdc = np.argsort(domL[:,ed],axis=0)
            domL[:,ed] = domL[domLIdc,ed]
            Mz[:,ed] = Mz[domLIdc,ed]
            Vy[:,ed] = Vy[domLIdc,ed]
            Nx[:,ed] = Nx[domLIdc,ed]
            
        # BeamNx = np.zeros((self.nelem,3),dtype=float)
        # for ee in range(self.nelem):
            
        #     noi = int(self.inci[ee,4])
        #     noj = int(self.inci[ee,5])
        #     noix = self.coord[noi-1,1]
        #     noiy = self.coord[noi-1,2]
        #     nojx = self.coord[noj-1,1]
        #     nojy = self.coord[noj-1,2]
                    
        #     Lx = np.sqrt(((noix-nojx)**2))
        #     Ly = np.sqrt(((noiy-nojy)**2))
            
        #     if (Lx>0.0)and(Ly==0.0):
        #         BeamNx[noi-1,1] = Nx[noi-1]
        #         BeamNx[noj-1,1] = Nx[noj-1]
            
        #     if (Lx==0.0)and(Ly>0.0):
        #         BeamNx[noi-1,0] = Nx[noi-1]
        #         BeamNx[noj-1,0] = Nx[noj-1]
        
        # meshBeamNx = np.concatenate((self.coord[:,0][:, np.newaxis],np.add(self.coord[:,1:],BeamNx)),axis=1)
        
        # BeamVy = np.zeros((self.nelem,3),dtype=float)
        # for ee in range(self.nnode):
            
        #     noi = int(self.inci[ee,4])
        #     noj = int(self.inci[ee,5])
        #     noix = self.coord[noi-1,1]
        #     noiy = self.coord[noi-1,2]
        #     nojx = self.coord[noj-1,1]
        #     nojy = self.coord[noj-1,2]
                    
        #     Lx = np.sqrt(((noix-nojx)**2))
        #     Ly = np.sqrt(((noiy-nojy)**2))
            
        #     if (Lx>0.0)and(Ly==0.0):
        #         BeamVy[noi-1,1] = Vy[noi-1]
        #         BeamVy[noj-1,1] = Vy[noj-1]
        #     if (Lx==0.0)and(Ly>0.0):
        #         BeamVy[noi-1,0] = Vy[noi-1]
        #         BeamVy[noj-1,0] = Vy[noj-1]
        
        # meshBeamVy = np.concatenate((self.coord[:,0][:, np.newaxis],np.add(self.coord[:,1:],BeamVy)),axis=1)
        
        # BeamMz = np.zeros((self.nelem,3),dtype=float)
        # for ee in range(self.nnode):
            
        #     noi = int(self.inci[ee,4])
        #     noj = int(self.inci[ee,5])
        #     noix = self.coord[noi-1,1]
        #     noiy = self.coord[noi-1,2]
        #     nojx = self.coord[noj-1,1]
        #     nojy = self.coord[noj-1,2]
                    
        #     Lx = np.sqrt(((noix-nojx)**2))
        #     Ly = np.sqrt(((noiy-nojy)**2))
            
        #     if (Lx>0.0)and(Ly==0.0):
        #         BeamMz[noi-1,1] = Mz[noi-1]
        #         BeamMz[noj-1,1] = Mz[noj-1]
        #     if (Lx==0.0)and(Ly>0.0):
        #         BeamMz[noi-1,0] = Mz[noi-1]
        #         BeamMz[noj-1,0] = Mz[noj-1]
        
        # meshBeamMz = np.concatenate((self.coord[:,0][:, np.newaxis],np.add(self.coord[:,1:],BeamMz)),axis=1)
                    
        # domLOrd = np.sort(domL,axis=0)
        
        ifb = {'le':domL, 'val': [Nx, Vy, Mz]}
        title =  ["NX","VY","MZ"]
        
        return ifb, title
    
    
    # # tensao no elemento de portico 2d
    def matrix_B(self, ee, csc):
        
        y = csc[0]
        
        noi = int(self.inci[ee,4])
        noj = int(self.inci[ee,5])
        # list_node = [noi,noj]
        
        noix = self.coord[noi-1,1]
        noiy = self.coord[noi-1,2]
        nojx = self.coord[noj-1,1]
        nojy = self.coord[noj-1,2]
        
        D = get_elasticity(self.tabmat,self.inci,ee)
        E = D[0]
        
        L = np.sqrt((nojx-noix)**2 + (nojy-noiy)**2)
        
        s = (nojy-noiy)/L
        c = (nojx-noix)/L
        T = np.array([[c,s,0,0,0,0],\
                      [-s,c,0,0,0,0],\
                      [0,0,1,0,0,0],\
                      [0,0,0,c,s,0],\
                      [0,0,0,-s,c,0],\
                      [0,0,0,0,0,1]])   
        
        
        coord_local = np.dot(T,np.array([[noix],[noiy],[1],[nojx],[nojy],[1]]))        
        x_mid = (coord_local[3][0]- coord_local[0][0])/2 

        
        B = np.array([-E/L,-(y*E)*((12*x_mid)/(L**3) - 6/(L**2)),\
                    -(y*E)*((6*x_mid)/(L**2) - 4/L) ,\
                    E/L,-(y*E)*(-(12*x_mid)/(L**3) + 6/(L**2)),\
                    -(y*E)*((6*x_mid)/(L**2) - 2/L)])

            
        return B, T