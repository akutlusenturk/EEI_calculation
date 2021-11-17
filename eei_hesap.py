import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import interp1d
from scipy.optimize import fsolve

import ipywidgets as wg
from IPython.display import display
import csv

def dosya_oku(name):
    qhn="QH_"+name+".csv"
    qpn="QP_"+name+".csv"
    dfQH=pd.read_csv(qhn,names=["Q","H"],sep=";",decimal=',')
    dfQP=pd.read_csv(qpn,names=["Q","H"],sep=";",decimal=',')
    QH=dfQH[["Q"]].values[:]
    QP=dfQP[["Q"]].values[:]
    
    if QH.min()>QP.min():
        mini=QH.min()
    else:
        mini=QP.min()
        
    if QH.max()>QP.max():
        maks=QP.max()
    else:
        maks=QH.max()
        
    Q=np.linspace(mini,maks,200)
    
    H = interp1d(dfQH[["Q"]].values[:,0], dfQH[["H"]].values[:,0])
    P1 = interp1d(dfQP[["Q"]].values[:,0], dfQP[["H"]].values[:,0])
    
    fig, ax=plt.subplots(2,1,sharex=True)
    fig.canvas.set_window_title("Pompa ölçümleri")
    ax[0].plot(Q,H(Q))
    ax[0].legend(["Q vs. H"])
    ax[1].plot(Q,P1(Q))
    ax[1].legend(["Q vs. P1"])
    ax[1].ylim(bottom=0,top=P1.max)
    plt.tight_layout()
    fig.set_size_inches(8,8)
    fig.show()

    Q_tah=2.3 #tahmini Phyd_max değeri
    tol=1
    Qk=Q[np.where(np.logical_and(Q> Q_tah-tol, Q<=Q_tah+tol))]
    Hk=H(Qk)
    
    Hfit=np.poly1d(np.polyfit(Qk,Hk,3))
    plt.figure()
    plt.plot(Q,Hfit(Q))
    plt.legend(["Hfit"])
    plt.title("Fitted pump")
    plt.xlabel("Q")
    plt.ylabel("H")
    plt.xlim(right=Q.max()+Q.max()*0.2,left=0)
    
    Phyd=Q*Hfit(Q)*2.72
    Q_100=Q[np.argmax(Phyd)]
    plt.figure()
    plt.plot(Q,Phyd)
    Phydr=Phyd.max()
    plt.scatter(Q_100,Phydr,color="red")
    plt.legend(["Phyd","Phdr"])
    plt.title("Güç Eğrisi")
    plt.xlabel("Q")
    plt.ylabel("P")
    print("Phydr",Phydr)
    plt.xlim(right=Q.max()+Q.max()*0.2,left=0)
    
    