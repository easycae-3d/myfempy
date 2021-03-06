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
from myfempy.tools.tools import loading_bar_v1
from myfempy.felib.felemset import get_elemset

#------------------------------------------------------------------------------
def assembler(modelinfo, key):
    
    dofe = modelinfo['nodecon'][0]*modelinfo['nodedof'][0]
    nelem = len(modelinfo["inci"])
    ith = np.zeros((nelem*(dofe*dofe)),dtype=int)
    jth = np.zeros((nelem*(dofe*dofe)),dtype=int)
    val = np.zeros((nelem*(dofe*dofe)),dtype=float)
    
    loading_bar_v1(0,'ASSEMBLER')
    for ee in range(nelem):
        loading_bar_v1(100*((ee+1)/nelem),'ASSEMBLER')
        
        element = get_elemset(int(modelinfo['inci'][ee][1]))
        setelement = element(modelinfo)
        
        if key == 'stiffness':
            ke, loc = setelement.stiff_linear(ee)
        
        elif key == 'mass':
            ke, loc = setelement.mass(ee)
        
        elif key == 'damper':
            pass         
        
        loc_T = loc.reshape(1,dofe).T
        Ycopy_loc = np.tile(loc_T,(1,dofe))
        Ycopy_loc_T = np.transpose(Ycopy_loc)
        ith[(dofe*dofe)*ee:(dofe*dofe)*(ee+1)] = Ycopy_loc.flatten('F')
        jth[(dofe*dofe)*ee:(dofe*dofe)*(ee+1)] = Ycopy_loc_T.flatten('F')
        val[(dofe*dofe)*ee:(dofe*dofe)*(ee+1)] = ke.flatten('F')
        
    matrix = sp.csc_matrix((val, (ith, jth)), shape=(modelinfo["nodedof"][0]*len(modelinfo["coord"]), modelinfo["nodedof"][0]*len(modelinfo["coord"])))
    # KG = sp.coo_matrix((val, (ith, jth)), shape=[fulldofs, fulldofs])
    # KG = sp.csc_matrix(KG)
    return  matrix


#------------------------------------------------------------------------------
#%% vetor forca
def loads(modelinfo, KG):
    
    forcelist = np.zeros((modelinfo["nodedof"][0]*len(modelinfo["coord"]),len(np.unique(modelinfo['forces'][:,3]))))
    # loading_bar_v1(0,'ASBLFG')
    for fstep in range(len(np.unique(modelinfo['forces'][:,3]))):
        # loading_bar_v1(100*((fstep+1)/len(np.unique(modelinfo['forces'][:,3]))),'ASBLFG')
        forceaply = modelinfo['forces'][np.where(modelinfo['forces'][:,3]==fstep+1),:][0]
        nload = forceaply.shape[0]  
        if modelinfo['nodedof'][0] == 2:
            if (modelinfo['elemid'][0] == 110) or (modelinfo['elemid'][0] == 120) or (modelinfo['elemid'][0] == 210) or (modelinfo['elemid'][0] == 220):
                for ii in range(nload):
                    if int(forceaply[ii,1])==1:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]))
                        forcelist[gdlload,fstep] += forceaply[ii,2]
                    
                    elif int(forceaply[ii,1])==2:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-1))
                        forcelist[gdlload,fstep] += forceaply[ii,2]
                    
                    elif int(forceaply[ii,1])==16:
                        loc = np.array([int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0])),\
                                        int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-1))])
                        kespr = forceaply[ii,2]*np.array([[1,-1],[-1,1]])
                        KG[np.ix_(loc,loc)] += kespr
                    
                    
            elif modelinfo['elemid'][0] == 130:
                for ii in range(nload):
                    if int(forceaply[ii,1])==2:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]))
                        forcelist[gdlload,fstep] += forceaply[ii,2]
                    elif int(forceaply[ii,1])==6:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-1))
                        forcelist[gdlload,fstep] += forceaply[ii,2]          
                        
                    elif int(forceaply[ii,1])==16:
                        loc = np.array([int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0])),\
                                        int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-1))])
                        kespr = forceaply[ii,2]*np.array([[1,-1],[-1,1]])
                        KG[np.ix_(loc,loc)] += kespr
              
                    
        elif modelinfo['nodedof'][0] == 3:
            if modelinfo['elemid'][0] == 140:
                for ii in range(nload):
                    if int(forceaply[ii,1])==1:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]))
                        forcelist[gdlload,fstep] += forceaply[ii,2]
                    elif int(forceaply[ii,1])==2:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-1))
                        forcelist[gdlload,fstep] += forceaply[ii,2]
                    elif int(forceaply[ii,1])==6:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-2))
                        forcelist[gdlload,fstep] += forceaply[ii,2]
                        
                    elif int(forceaply[ii,1])==16:
                        loc = np.array([int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0])),\
                                        int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-1))])
                        kespr = forceaply[ii,2]*np.array([[1,-1],[-1,1]])
                        KG[np.ix_(loc,loc)] += kespr
                
                    
                    
            elif (modelinfo['elemid'][0] == 310) or (modelinfo['elemid'][0] == 320):
                for ii in range(nload):
                    if int(forceaply[ii,1])==1:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]))
                        forcelist[gdlload,fstep] += forceaply[ii,2]
                    elif int(forceaply[ii,1])==2:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-1))
                        forcelist[gdlload,fstep] += forceaply[ii,2]
                    elif int(forceaply[ii,1])==3:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-2))
                        forcelist[gdlload,fstep] += forceaply[ii,2]
                        
                    elif int(forceaply[ii,1])==16:
                        loc = np.array([int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0])),\
                                        int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-1))])
                        kespr = forceaply[ii,2]*np.array([[1,-1],[-1,1]])
                        KG[np.ix_(loc,loc)] += kespr
                    
    
        elif modelinfo['nodedof'][0] == 6:
            if modelinfo['elemid'][0] == 141:
                for ii in range(nload):
                    if int(forceaply[ii,1])==1:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]))
                        forcelist[gdlload,fstep] += forceaply[ii,2]
                    elif int(forceaply[ii,1])==2:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-1))
                        forcelist[gdlload,fstep] += forceaply[ii,2]
                    elif int(forceaply[ii,1])==3:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-2))
                        forcelist[gdlload,fstep] += forceaply[ii,2]
                    elif int(forceaply[ii,1])==4:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-3))
                        forcelist[gdlload,fstep] += forceaply[ii,2]
                    elif int(forceaply[ii,1])==5:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-4))
                        forcelist[gdlload,fstep] += forceaply[ii,2]
                    elif int(forceaply[ii,1])==6:
                        gdlload = int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-5))
                        forcelist[gdlload,fstep] += forceaply[ii,2]
                        
                    elif int(forceaply[ii,1])==16:
                        loc = np.array([int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0])),\
                                        int(modelinfo['nodedof'][0]*forceaply[ii,0]-(modelinfo['nodedof'][0]-1))])
                        kespr = forceaply[ii,2]*np.array([[1,-1],[-1,1]])
                        KG[np.ix_(loc,loc)] += kespr
                    
    forcelist = sp.csc_matrix(forcelist)           
    return forcelist, KG