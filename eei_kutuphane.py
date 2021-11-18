import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import os

def azami (dosya, groupby = "D", minQ = 0.1, minH = 0.1, minPhyd = 0.1):
    df = pd.read_excel("max_devir/"+dosya,index_col=0)
    dfh = df.copy()
    df = df.groupby(groupby,as_index=False).mean()
    df = df[df.Q>minQ]
    df = df[df.H>minH]
    df = df[df.Phyd>=minPhyd]
    QHint = interp1d(df.Q,df.H)
    QPconsint =interp1d(df.Q,df.Pcons)
    return df, QHint, QPconsint
    
def dP (dosya, groupby = "D", minQ = 0.1, minH = 0.1, minPhyd = 0.1):
    df = pd.read_excel("dP_data/"+dosya,index_col=0)
    dfh = df.copy()
    df = df.groupby(groupby,as_index=False).mean()
    df = df[df.Q>minQ]
    df = df[df.H>minH]
    df = df[df.Phyd>=minPhyd]
    QHint = interp1d(df.Q,df.H)
    QPconsint =interp1d(df.Q,df.Pcons)
    return df, QHint, QPconsint

def PompaOlcumleri (df,dfk,azami_QHint,dP_QHint,azami_QPconsint,dP_QPconsint,Q_tah,tol):

    fig, ax=plt.subplots(2,1,sharex=True)
    fig.set_size_inches(8,8)
    plt.tight_layout()
    
    ax[0].scatter(df.Q,df.H,color="violet",s=15)
    ax[0].plot(df.Q,azami_QHint(df.Q),color="black")
    ax[0].set_title("Pompa Ölçümleri")
    ax[0].set_ylabel("Basma Yüksekliği")
    ax[0].set_ylim(bottom=0)
    ax[0].set_xlim(left=0)
    ax[0].grid()
    
    #ax[0].scatter(df.Q[Pbeyans],df.H[Pbeyans])
    
    ax[0].scatter(dfk.Q,dfk.H,color="orange",s=15)
    ax[0].plot(dfk.Q,dP_QHint(dfk.Q),color="red")  
     
    ax[0].scatter(Q_tah-tol,azami_QHint(Q_tah-tol),color="r",marker="|",s=700)
    ax[0].scatter(Q_tah+tol,azami_QHint(Q_tah+tol),color="r",marker="|",s=700)
    
    ax[0].legend(["Sabit Eğri İnterpolasyon","Değişken Basınç İnterpolasyon","Sabit Eğri Ölçüm","Değişken Basınç Ölçüm","Eğri Uydurma Aralığı"])                                      
    
    ax[1].scatter(df.Q,df.Pcons,color="violet",s=15)
    ax[1].plot(df.Q,azami_QPconsint(df.Q),color="black")
    ax[1].set_ylabel("Güç Tüketimi")
    ax[1].set_xlabel("Debi")
    ax[1].set_ylim(bottom=0)
    ax[1].set_xlim(left=0)
    ax[1].grid()
    
    ax[1].scatter(dfk.Q,dfk.Pcons,color="orange",s=15)
    ax[1].plot(dfk.Q,dP_QPconsint(dfk.Q),color="red")
    return fig

def PolyVerim (df,Q_100,H_100):
    fig, ax=plt.subplots(1,2)
    fig.set_size_inches(10,4)
    plt.tight_layout()
    
    ax[0].set_label("Q")
    ax[0].set_label("Phyd")
    ax[0].grid()
    ax[0].set_xlabel("Q")
    ax[0].set_ylabel("Phyd")
    
    ax[0].scatter(df.Q,df.Phyd,color="orange",s=5)
    ax[0].plot(df.Q,df.Phfit)
    
    ax[0].legend("Ölçüm","Phyd(Hfit)")
    
    ax[1].set_xlabel("Q")
    ax[1].set_ylabel("H")
    ax[1].plot(df.Q,df.H)
    ax[1].scatter(Q_100,H_100,color="orange")
    ax[1].annotate(" Q_100: %.2f,"%Q_100,(Q_100,H_100))
    ax[1].annotate("                      H_100: %.2f"%H_100,(Q_100,H_100))
    ax[1].grid()
    axe = ax[1].twinx()

    df["eta"] = df.Phfit/df.Pcons*100
    axe.plot(df.Q,df.eta,"violet")
    axe.set_ylim(top=100)
    axe.set_ylabel("%eta")
    axe.scatter(df.Q[df.eta.idxmax()],df.eta.max(),color="red")
    axe.annotate("%% %.2f"%df.eta.max(),(df.Q[df.eta.idxmax()],df.eta.max()))
    return fig

def duzeltilmisQH (df,Hfit,Q_100,H_100,Phydr):
    fig, ax=plt.subplots(2,1,sharex=True)
    fig.set_size_inches(8,8)
    plt.tight_layout()
    
    ax[0].plot(df.Q,Hfit(df.Q))
    
    ax[0].scatter(Q_100,H_100,color="r")
    # ax[0].scatter(Q_tah-tol,Hfit(Q_tah-tol),color="r",marker="|",s=500)
    # ax[0].scatter(Q_tah+tol,Hfit(Q_tah+tol),color="r",marker="|",s=500)
    
    ax[0].legend(["Hfit","Phydr (Q_100,H_100)"])
    ax[0].set_title("Düzeltilmiş QH Eğrisi")
    ax[0].set_ylabel("Basma Yüksekliği (H) [m]")
    ax[0].set_ylim(bottom=0)
    ax[0].set_xlim(left=0)
    ax[0].grid()
    
    ax[1].plot(df.Q,df.Phfit)
    ax[1].scatter(df.Q[df.Phfit.idxmax()],df.Phfit.max(),color="red")
    ax[1].set_ylabel("Hidrolik Güç (Phyd) [W]")
    ax[1].legend(["Phyd","Phydr (Q_100,H_100)"])
    ax[1].set_xlabel("Debi (Q) [m³/h]")
    ax[1].set_ylim(bottom=0)
    ax[1].set_xlim(left=0)
    ax[1].grid()
    
    ax[0].plot(np.full(10,Q_100),np.linspace(0,H_100,10),linestyle="-.",color="orange")
    ax[0].plot(np.linspace(0,Q_100,10),np.full(10,H_100),linestyle="-.",color="orange")
    ax[1].plot(np.full(10,Q_100),np.linspace(0,Phydr,10),linestyle="-.",color="orange")
    return fig

# def RefKontrol (df,dfk,Hfit,dP_QHint,Qrefl,Hrefl):

#     Qref=Qrefl[1:]
#     Href=Hrefl[1:]
    
#     fig, ax=plt.subplots(1,1)
#     fig.set_size_inches(8,4)
    
#     ax.plot(df.Q,Hfit(df.Q))
#     ax.scatter(Qref,Href,color="red")
#     ax.plot(Qrefl,Hrefl,color="violet")
#     ax.set_title("Referans Kontrol Eğrisi")
#     ax.legend(["Hdfit","RKD","Ref.Noktaları"])
#     ax.grid()
    
#     ax.plot(dfk.Q,dP_QHint(dfk.Q))
#     return fig
    
###############################################################################
# Tolerans hesabı (Gereksiz?)
###############################################################################

# konteyner_4 = st.container()
# kols_4 = konteyner_4.columns([1,1])

# yuzde = (H_100)-(H_100*0.2)
# eksi = (H_100)-0.5
# H_100tol = np.array([yuzde,eksi]).max()

# kols_4[0].write("H_100 - H_100*0.20 = %.2f" %yuzde)
# kols_4[0].write("H_100 - 0.5m = %.2f" %eksi)
# kols_4[1].write(" * H_100 toleransı hesaplandı.")
# kols_4[1].write("** H_100 - t = %.2f **"%H_100tol)

# with konteyner_4.expander("TS EN 16297-1:2013-04 atıf"):
#     st.image("TSE_4.png")
###############################################################################
# Data Analizi
###############################################################################

# if st.button("Data Analizi Yap"):    
#     with konteyner_1.expander("Data Analizi"):
#         st.subheader("Sabit Eğri Verisi")
#         st.write("Zamana Bağlı Ölçüm Grafikleri")
#         fig, ax=plt.subplots(2,5)
#         fig.set_size_inches(12,5)
#         plt.tight_layout()
        
#         ax[0,0].set_title("Sıcaklık [°C]")
#         ax[0,0].scatter(dfh.index.values,dfh["T"],s=0.1)
#         ax[0,1].set_title("Debi [m³/s]")
#         ax[0,1].scatter(dfh.index.values,dfh.Q,s=1)
#         ax[0,2].set_title("Enerji Tüketimi [W]")
#         ax[0,2].scatter(dfh.index.values,dfh.Pcons,s=1)
#         ax[0,3].set_title("Basma Yüksekliği [m]")
#         ax[0,3].scatter(dfh.index.values,dfh.H,s=1)
#         ax[0,4].set_title("Vana Açıklığı [°]")
#         ax[0,4].scatter(dfh.index.values,dfh.D,s=1)
        
#         ax[1,0].set_title("Statik Basınç [Bar]")
#         ax[1,0].scatter(dfh.index.values,dfh.P,s=0.1)
#         ax[1,1].set_title("Giriş Basıncı [Bar]")
#         ax[1,1].scatter(dfh.index.values,dfh.P1,s=1)
#         ax[1,2].set_title("Çıkış Basıncı [Bar]")
#         ax[1,2].scatter(dfh.index.values,dfh.P2,s=1)
#         ax[1,3].set_title("Fark Basıncı [Bar]")
#         ax[1,3].scatter(dfh.index.values,dfh.dP,s=1)
#         ax[1,4].set_title("Hidrolik Güç [W]")
#         ax[1,4].scatter(dfh.index.values,dfh.Phyd,s=1)
        
#         st.pyplot(fig)
        
#         st.write("Farklı Grup Analizleri")
#         fig, ax=plt.subplots(5,5)
#         fig.set_size_inches(12,10)
#         plt.tight_layout()
        
        
#         ax[0,0].set_ylabel("D vs H")
#         ax[1,0].set_ylabel("D vs Q")
#         ax[2,0].set_ylabel("Q vs H")
#         ax[3,0].set_ylabel("Q vs Phyd")
#         ax[4,0].set_ylabel("Q vs Pcons")
        
#         ax[0,0].set_title("df")
#         ax[0,0].scatter(dfh.D,dfh.H,s=1)
#         ax[1,0].scatter(dfh.D,dfh.Q,s=1)
#         ax[2,0].scatter(dfh.Q,dfh.H,s=1)
#         ax[3,0].scatter(dfh.Q,dfh.Phyd,s=1)
#         ax[4,0].scatter(dfh.Q,dfh.Pcons,s=1)
        
#         dfQ = dfh.groupby("Q",as_index=False).mean()
        
#         ax[0,1].set_title("dfQ")
#         ax[0,1].scatter(dfQ.D,dfQ.H,s=1)
#         ax[1,1].scatter(dfQ.D,dfQ.Q,s=1)
#         ax[2,1].scatter(dfQ.Q,dfQ.H,s=1)
#         ax[3,1].scatter(dfQ.Q,dfQ.Phyd,s=1)
#         ax[4,1].scatter(dfQ.Q,dfQ.Pcons,s=1)
        
#         dfH = dfh.groupby("H",as_index=False).mean()
        
#         ax[0,2].set_title("dfH")
#         ax[0,2].scatter(dfH.D,dfH.H,s=1)
#         ax[1,2].scatter(dfH.D,dfH.Q,s=1)
#         ax[2,2].scatter(dfH.Q,dfH.H,s=1)
#         ax[3,2].scatter(dfH.Q,dfH.Phyd,s=1)
#         ax[4,2].scatter(dfH.Q,dfH.Pcons,s=1)
        
#         dfD = dfh.groupby("D",as_index=False).mean()
        
#         ax[0,3].set_title("dfD")
#         ax[0,3].scatter(dfD.D,dfD.H,s=1)
#         ax[1,3].scatter(dfD.D,dfD.Q,s=1)
#         ax[2,3].scatter(dfD.Q,dfD.H,s=1)
#         ax[3,3].scatter(dfD.Q,dfD.Phyd,s=1)
#         ax[4,3].scatter(dfD.Q,dfD.Pcons,s=1)
        
#         dfPcons = dfh.groupby("Pcons",as_index=False).mean()
        
#         ax[0,4].set_title("dfPcons")
#         ax[0,4].scatter(dfPcons.D,dfPcons.H,s=1)
#         ax[1,4].scatter(dfPcons.D,dfPcons.Q,s=1)
#         ax[2,4].scatter(dfPcons.Q,dfPcons.H,s=1)
#         ax[3,4].scatter(dfPcons.Q,dfPcons.Phyd,s=1)
#         ax[4,4].scatter(dfPcons.Q,dfPcons.Pcons,s=1)
        
#         st.pyplot(fig)
        
#         st.dataframe(df)
#         st.subheader("Değişken Basınç Verisi")
#         st.write("Zamana Bağlı Ölçüm Grafikleri")
#         fig, ax=plt.subplots(2,5)
#         fig.set_size_inches(12,5)
#         plt.tight_layout()
        
#         ax[0,0].set_title("Sıcaklık [°C]")
#         ax[0,0].scatter(dfkh.index.values,dfkh["T"],s=0.1)
#         ax[0,1].set_title("Debi [m³/s]")
#         ax[0,1].scatter(dfkh.index.values,dfkh.Q,s=1)
#         ax[0,2].set_title("Enerji Tüketimi [W]")
#         ax[0,2].scatter(dfkh.index.values,dfkh.Pcons,s=1)
#         ax[0,3].set_title("Basma Yüksekliği [m]")
#         ax[0,3].scatter(dfkh.index.values,dfkh.H,s=1)
#         ax[0,4].set_title("Vana Açıklığı [°]")
#         ax[0,4].scatter(dfkh.index.values,dfkh.D,s=1)
        
#         ax[1,0].set_title("Statik Basınç [Bar]")
#         ax[1,0].scatter(dfkh.index.values,dfkh.P,s=0.1)
#         ax[1,1].set_title("Giriş Basıncı [Bar]")
#         ax[1,1].scatter(dfkh.index.values,dfkh.P1,s=1)
#         ax[1,2].set_title("Çıkış Basıncı [Bar]")
#         ax[1,2].scatter(dfkh.index.values,dfkh.P2,s=1)
#         ax[1,3].set_title("Fark Basıncı [Bar]")
#         ax[1,3].scatter(dfkh.index.values,dfkh.dP,s=1)
#         ax[1,4].set_title("Hidrolik Güç [W]")
#         ax[1,4].scatter(dfkh.index.values,dfkh.Phyd,s=1)
        
#         st.pyplot(fig)
        
#         st.write("Farklı Grup Analizleri")
#         fig, ax=plt.subplots(5,5)
#         fig.set_size_inches(12,10)
#         plt.tight_layout()
        
#         ax[0,0].set_ylabel("D vs H")
#         ax[1,0].set_ylabel("D vs Q")
#         ax[2,0].set_ylabel("Q vs H")
#         ax[3,0].set_ylabel("Q vs Phyd")
#         ax[4,0].set_ylabel("Q vs Pcons")
        
#         ax[0,0].set_title("df")
#         ax[0,0].scatter(dfkh.D,dfkh.H,s=1)
#         ax[1,0].scatter(dfkh.D,dfkh.Q,s=1)
#         ax[2,0].scatter(dfkh.Q,dfkh.H,s=1)
#         ax[3,0].scatter(dfkh.Q,dfkh.Phyd,s=1)
#         ax[4,0].scatter(dfkh.Q,dfkh.Pcons,s=1)
        
#         dfQ = dfkh.groupby("Q",as_index=False).mean()
        
#         ax[0,1].set_title("dfQ")
#         ax[0,1].scatter(dfQ.D,dfQ.H,s=1)
#         ax[1,1].scatter(dfQ.D,dfQ.Q,s=1)
#         ax[2,1].scatter(dfQ.Q,dfQ.H,s=1)
#         ax[3,1].scatter(dfQ.Q,dfQ.Phyd,s=1)
#         ax[4,1].scatter(dfQ.Q,dfQ.Pcons,s=1)
        
#         dfH = dfkh.groupby("H",as_index=False).mean()
        
#         ax[0,2].set_title("dfH")
#         ax[0,2].scatter(dfH.D,dfH.H,s=1)
#         ax[1,2].scatter(dfH.D,dfH.Q,s=1)
#         ax[2,2].scatter(dfH.Q,dfH.H,s=1)
#         ax[3,2].scatter(dfH.Q,dfH.Phyd,s=1)
#         ax[4,2].scatter(dfH.Q,dfH.Pcons,s=1)
        
#         dfD = dfkh.groupby("D",as_index=False).mean()
        
#         ax[0,3].set_title("dfD")
#         ax[0,3].scatter(dfD.D,dfD.H,s=1)
#         ax[1,3].scatter(dfD.D,dfD.Q,s=1)
#         ax[2,3].scatter(dfD.Q,dfD.H,s=1)
#         ax[3,3].scatter(dfD.Q,dfD.Phyd,s=1)
#         ax[4,3].scatter(dfD.Q,dfD.Pcons,s=1)
        
#         dfPcons = dfkh.groupby("Pcons",as_index=False).mean()
        
#         ax[0,4].set_title("dfPcons")
#         ax[0,4].scatter(dfPcons.D,dfPcons.H,s=1)
#         ax[1,4].scatter(dfPcons.D,dfPcons.Q,s=1)
#         ax[2,4].scatter(dfPcons.Q,dfPcons.H,s=1)
#         ax[3,4].scatter(dfPcons.Q,dfPcons.Phyd,s=1)
#         ax[4,4].scatter(dfPcons.Q,dfPcons.Pcons,s=1)
        
#         st.pyplot(fig)
#         st.dataframe(dfk)
###############################################################################