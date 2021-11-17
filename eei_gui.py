import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import os

st.set_page_config(
 page_title='EEI',
 layout="wide",
 initial_sidebar_state="expanded",
)

st.sidebar.title("EEI Hesaplayıcı")
st.sidebar.markdown('''
Pompa verilerini seçerek ölçülen değerler ve EEI hesaplarına ulaşabilirsiniz.
'''
)

###############################################################################
# sidebar
###############################################################################

st.markdown(f'''
    <style>
    section[data-testid="stSidebar"] .css-ng1t4o {{width: 40rem;}}
    </style>
''',unsafe_allow_html=True)

st.sidebar.title("Kontrol Paneli")
# dosya = st.sidebar.file_uploader('Azami ayarda manuel veri.')
# kismi = st.sidebar.file_uploader("Değişken devirde kontrollü veri.")

# if dosya is None:
#     dosya = "Wilo_Stratos_azami_deney_2021Nov16_16.56.21.xlsx"
# if kismi is None:
#     kismi = "Wilo_Strator_dP5.3_deney_2021Nov16_17.18.43.xlsx"
    
sbtler = os.listdir("max_devir")

dosya = st.sidebar.selectbox(
    "Max devirde sabit eğri",
    sbtler)

dpler = os.listdir("dP_data")    

kismi = st.sidebar.selectbox(
    "Oransal Basınç Modu (dP)",
    dpler)
    
tol = st.sidebar.number_input("Eğri Uydurma Aralığı [+-Q]",value=2.0)
#☻veriekle = st.sidebar.number_input("Değişken devir için veri ekle",value=0)

###############################################################################
# veri okuma & ön düzeltmeler
###############################################################################

df = pd.read_excel("max_devir/"+dosya,index_col=0)
dfh = df.copy()
df = df.groupby("D",as_index=False).mean()
df = df[df.Q>0.2]
df = df[df.H>0.2]
df = df[df.Phyd>=0]

dfk = pd.read_excel("dP_data/"+kismi,index_col=0)
dfkh = dfk.copy()
dfk = dfk.groupby("D",as_index=False).mean()
dfk = dfk[dfk.Q>0.2]
dfk = dfk[dfk.H>0.2]
dfk = dfk[dfk.Phyd>0]

# dfk = dfk[dfk.H.between(dfk.H.max()/3,dfk.H.max())]
# dfk = dfk[:dfk.Pcons.argmax()+1]


Q_tah = st.sidebar.number_input("Nominal debi.",value=df.Q[df.Phyd.idxmax()])  


Hint = interp1d(df.Q, df.H)     
intH = interp1d(dfk.Q, dfk.H)
Pconsint = interp1d(df.Q, df.Pcons)  
intPcons = interp1d(dfk.Q, dfk.Pcons)

kes=df[df.Q.between(Q_tah-tol,Q_tah+tol)]                                       
Hfit = np.poly1d(np.polyfit(kes.Q,kes.H,3))
df["Phfit"] = df.Q*Hfit(df.Q)*2.72
Phydr = df.Phfit.max()
Q_100 = df.Q[df.Phfit.idxmax()]
H_100 = Hfit(df.Q[df.Phfit.idxmax()])

dfk = dfk[dfk.Q<=Q_100*1.3]                                                   #veriekle yapılabilir
dfk = dfk[dfk.Q>=Q_100/6]

#Pbeyans = df.Phyd.idxmax()

###############################################################################
# ham veri grafikleri
###############################################################################

konteyner_1 = st.container()
kols_1 = konteyner_1.columns([1,1])

fig, ax=plt.subplots(2,1,sharex=True)
fig.set_size_inches(8,8)
plt.tight_layout()

ax[0].scatter(df.Q,df.H,color="violet",s=15)
ax[0].plot(df.Q,Hint(df.Q),color="black")
ax[0].set_title("Pompa Ölçümleri")
ax[0].set_ylabel("Basma Yüksekliği")
ax[0].grid()

#ax[0].scatter(df.Q[Pbeyans],df.H[Pbeyans])


ax[0].scatter(dfk.Q,dfk.H,color="orange",s=15)
ax[0].plot(dfk.Q,intH(dfk.Q),color="red")  
 
ax[0].scatter(Q_tah-tol,Hfit(Q_tah-tol),color="r",marker="|",s=700)
ax[0].scatter(Q_tah+tol,Hfit(Q_tah+tol),color="r",marker="|",s=700)

ax[0].legend(["Sabit Eğri İnterpolasyon","Değişken Basınç İnterpolasyon","Sabit Eğri Ölçüm","Değişken Basınç Ölçüm","Eğri Uydurma Aralığı"])                                      

ax[1].scatter(df.Q,df.Pcons,color="violet",s=15)
ax[1].plot(df.Q,Pconsint(df.Q),color="black")
ax[1].set_ylabel("Güç Tüketimi")
ax[1].set_xlabel("Debi")
ax[1].grid()

ax[1].scatter(dfk.Q,dfk.Pcons,color="orange",s=15)
ax[1].plot(dfk.Q,intPcons(dfk.Q),color="red")      

kols_1[0].pyplot(fig)

kols_1[1].markdown("""* Pompa Ölçümleri test düzeneğinde yapıldı.
* Ölçümler 3. derece eğriye uyduruldu.
""")

kols_1[1].write("** Q_max      :%.2f m³/h **" %(df.Q.max()))
kols_1[1].write("** H_max      :%.2f m **" %(df.H.max()))
kols_1[1].write("** Pcons_max  :%.2f W **" %(df.Pcons.max()))
kols_1[1].write("** Phyd_max  :%.2f W **" %(df.Phyd.max()))


with konteyner_1.expander("TS EN 16297-1:2013-04 atıf"):
    st.image("fig/TSE_1.png")
    
with konteyner_1.expander("Polyfit Yardımcısı & Verim (%eta)"):
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
    
    st.pyplot(fig)


    
if st.button("Data Analizi Yap"):    
    with konteyner_1.expander("Data Analizi"):
        st.subheader("Sabit Eğri Verisi")
        st.write("Zamana Bağlı Ölçüm Grafikleri")
        fig, ax=plt.subplots(2,5)
        fig.set_size_inches(12,5)
        plt.tight_layout()
        
        ax[0,0].set_title("Sıcaklık [°C]")
        ax[0,0].scatter(dfh.index.values,dfh["T"],s=0.1)
        ax[0,1].set_title("Debi [m³/s]")
        ax[0,1].scatter(dfh.index.values,dfh.Q,s=1)
        ax[0,2].set_title("Enerji Tüketimi [W]")
        ax[0,2].scatter(dfh.index.values,dfh.Pcons,s=1)
        ax[0,3].set_title("Basma Yüksekliği [m]")
        ax[0,3].scatter(dfh.index.values,dfh.H,s=1)
        ax[0,4].set_title("Vana Açıklığı [°]")
        ax[0,4].scatter(dfh.index.values,dfh.D,s=1)
        
        ax[1,0].set_title("Statik Basınç [Bar]")
        ax[1,0].scatter(dfh.index.values,dfh.P,s=0.1)
        ax[1,1].set_title("Giriş Basıncı [Bar]")
        ax[1,1].scatter(dfh.index.values,dfh.P1,s=1)
        ax[1,2].set_title("Çıkış Basıncı [Bar]")
        ax[1,2].scatter(dfh.index.values,dfh.P2,s=1)
        ax[1,3].set_title("Fark Basıncı [Bar]")
        ax[1,3].scatter(dfh.index.values,dfh.dP,s=1)
        ax[1,4].set_title("Hidrolik Güç [W]")
        ax[1,4].scatter(dfh.index.values,dfh.Phyd,s=1)
        
        st.pyplot(fig)
        
        st.write("Farklı Grup Analizleri")
        fig, ax=plt.subplots(5,5)
        fig.set_size_inches(12,10)
        plt.tight_layout()
        
        
        ax[0,0].set_ylabel("D vs H")
        ax[1,0].set_ylabel("D vs Q")
        ax[2,0].set_ylabel("Q vs H")
        ax[3,0].set_ylabel("Q vs Phyd")
        ax[4,0].set_ylabel("Q vs Pcons")
        
        ax[0,0].set_title("df")
        ax[0,0].scatter(dfh.D,dfh.H,s=1)
        ax[1,0].scatter(dfh.D,dfh.Q,s=1)
        ax[2,0].scatter(dfh.Q,dfh.H,s=1)
        ax[3,0].scatter(dfh.Q,dfh.Phyd,s=1)
        ax[4,0].scatter(dfh.Q,dfh.Pcons,s=1)
        
        dfQ = dfh.groupby("Q",as_index=False).mean()
        
        ax[0,1].set_title("dfQ")
        ax[0,1].scatter(dfQ.D,dfQ.H,s=1)
        ax[1,1].scatter(dfQ.D,dfQ.Q,s=1)
        ax[2,1].scatter(dfQ.Q,dfQ.H,s=1)
        ax[3,1].scatter(dfQ.Q,dfQ.Phyd,s=1)
        ax[4,1].scatter(dfQ.Q,dfQ.Pcons,s=1)
        
        dfH = dfh.groupby("H",as_index=False).mean()
        
        ax[0,2].set_title("dfH")
        ax[0,2].scatter(dfH.D,dfH.H,s=1)
        ax[1,2].scatter(dfH.D,dfH.Q,s=1)
        ax[2,2].scatter(dfH.Q,dfH.H,s=1)
        ax[3,2].scatter(dfH.Q,dfH.Phyd,s=1)
        ax[4,2].scatter(dfH.Q,dfH.Pcons,s=1)
        
        dfD = dfh.groupby("D",as_index=False).mean()
        
        ax[0,3].set_title("dfD")
        ax[0,3].scatter(dfD.D,dfD.H,s=1)
        ax[1,3].scatter(dfD.D,dfD.Q,s=1)
        ax[2,3].scatter(dfD.Q,dfD.H,s=1)
        ax[3,3].scatter(dfD.Q,dfD.Phyd,s=1)
        ax[4,3].scatter(dfD.Q,dfD.Pcons,s=1)
        
        dfPcons = dfh.groupby("Pcons",as_index=False).mean()
        
        ax[0,4].set_title("dfPcons")
        ax[0,4].scatter(dfPcons.D,dfPcons.H,s=1)
        ax[1,4].scatter(dfPcons.D,dfPcons.Q,s=1)
        ax[2,4].scatter(dfPcons.Q,dfPcons.H,s=1)
        ax[3,4].scatter(dfPcons.Q,dfPcons.Phyd,s=1)
        ax[4,4].scatter(dfPcons.Q,dfPcons.Pcons,s=1)
        
        st.pyplot(fig)
        
        st.dataframe(df)
        st.subheader("Değişken Basınç Verisi")
        st.write("Zamana Bağlı Ölçüm Grafikleri")
        fig, ax=plt.subplots(2,5)
        fig.set_size_inches(12,5)
        plt.tight_layout()
        
        ax[0,0].set_title("Sıcaklık [°C]")
        ax[0,0].scatter(dfkh.index.values,dfkh["T"],s=0.1)
        ax[0,1].set_title("Debi [m³/s]")
        ax[0,1].scatter(dfkh.index.values,dfkh.Q,s=1)
        ax[0,2].set_title("Enerji Tüketimi [W]")
        ax[0,2].scatter(dfkh.index.values,dfkh.Pcons,s=1)
        ax[0,3].set_title("Basma Yüksekliği [m]")
        ax[0,3].scatter(dfkh.index.values,dfkh.H,s=1)
        ax[0,4].set_title("Vana Açıklığı [°]")
        ax[0,4].scatter(dfkh.index.values,dfkh.D,s=1)
        
        ax[1,0].set_title("Statik Basınç [Bar]")
        ax[1,0].scatter(dfkh.index.values,dfkh.P,s=0.1)
        ax[1,1].set_title("Giriş Basıncı [Bar]")
        ax[1,1].scatter(dfkh.index.values,dfkh.P1,s=1)
        ax[1,2].set_title("Çıkış Basıncı [Bar]")
        ax[1,2].scatter(dfkh.index.values,dfkh.P2,s=1)
        ax[1,3].set_title("Fark Basıncı [Bar]")
        ax[1,3].scatter(dfkh.index.values,dfkh.dP,s=1)
        ax[1,4].set_title("Hidrolik Güç [W]")
        ax[1,4].scatter(dfkh.index.values,dfkh.Phyd,s=1)
        
        st.pyplot(fig)
        
        st.write("Farklı Grup Analizleri")
        fig, ax=plt.subplots(5,5)
        fig.set_size_inches(12,10)
        plt.tight_layout()
        
        ax[0,0].set_ylabel("D vs H")
        ax[1,0].set_ylabel("D vs Q")
        ax[2,0].set_ylabel("Q vs H")
        ax[3,0].set_ylabel("Q vs Phyd")
        ax[4,0].set_ylabel("Q vs Pcons")
        
        ax[0,0].set_title("df")
        ax[0,0].scatter(dfkh.D,dfkh.H,s=1)
        ax[1,0].scatter(dfkh.D,dfkh.Q,s=1)
        ax[2,0].scatter(dfkh.Q,dfkh.H,s=1)
        ax[3,0].scatter(dfkh.Q,dfkh.Phyd,s=1)
        ax[4,0].scatter(dfkh.Q,dfkh.Pcons,s=1)
        
        dfQ = dfkh.groupby("Q",as_index=False).mean()
        
        ax[0,1].set_title("dfQ")
        ax[0,1].scatter(dfQ.D,dfQ.H,s=1)
        ax[1,1].scatter(dfQ.D,dfQ.Q,s=1)
        ax[2,1].scatter(dfQ.Q,dfQ.H,s=1)
        ax[3,1].scatter(dfQ.Q,dfQ.Phyd,s=1)
        ax[4,1].scatter(dfQ.Q,dfQ.Pcons,s=1)
        
        dfH = dfkh.groupby("H",as_index=False).mean()
        
        ax[0,2].set_title("dfH")
        ax[0,2].scatter(dfH.D,dfH.H,s=1)
        ax[1,2].scatter(dfH.D,dfH.Q,s=1)
        ax[2,2].scatter(dfH.Q,dfH.H,s=1)
        ax[3,2].scatter(dfH.Q,dfH.Phyd,s=1)
        ax[4,2].scatter(dfH.Q,dfH.Pcons,s=1)
        
        dfD = dfkh.groupby("D",as_index=False).mean()
        
        ax[0,3].set_title("dfD")
        ax[0,3].scatter(dfD.D,dfD.H,s=1)
        ax[1,3].scatter(dfD.D,dfD.Q,s=1)
        ax[2,3].scatter(dfD.Q,dfD.H,s=1)
        ax[3,3].scatter(dfD.Q,dfD.Phyd,s=1)
        ax[4,3].scatter(dfD.Q,dfD.Pcons,s=1)
        
        dfPcons = dfkh.groupby("Pcons",as_index=False).mean()
        
        ax[0,4].set_title("dfPcons")
        ax[0,4].scatter(dfPcons.D,dfPcons.H,s=1)
        ax[1,4].scatter(dfPcons.D,dfPcons.Q,s=1)
        ax[2,4].scatter(dfPcons.Q,dfPcons.H,s=1)
        ax[3,4].scatter(dfPcons.Q,dfPcons.Phyd,s=1)
        ax[4,4].scatter(dfPcons.Q,dfPcons.Pcons,s=1)
        
        st.pyplot(fig)
        st.dataframe(dfk)

###############################################################################
# Hfit
###############################################################################

konteyner_2 = st.container()
kols_2 = konteyner_2.columns([1,1])                                                                     #ÖÖÖÖÖÖÖF

fig, ax=plt.subplots(2,1,sharex=True)
fig.set_size_inches(8,8)
plt.tight_layout()

ax[0].plot(df.Q,Hfit(df.Q))

ax[0].scatter(Q_100,H_100,color="r")
ax[0].scatter(Q_tah-tol,Hfit(Q_tah-tol),color="r",marker="|",s=500)
ax[0].scatter(Q_tah+tol,Hfit(Q_tah+tol),color="r",marker="|",s=500)

ax[0].legend(["Hdfit",["Q_%100","H_%100"]])
ax[0].set_title("Düzeltilmiş QH Eğrisi")
ax[0].set_ylabel("Basma Yüksekliği")
ax[0].grid()

ax[1].plot(df.Q,df.Phfit)
ax[1].scatter(df.Q[df.Phfit.idxmax()],df.Phfit.max(),color="red")
ax[1].set_ylabel("Hidrolik Güç")
ax[1].legend(["Phyd",["Q_%100","H_%100"]])
ax[1].set_xlabel("Debi")
ax[1].grid()

ax[0].plot(np.full(10,Q_100),np.linspace(0,H_100,10),linestyle="-.",color="orange")
ax[0].plot(np.linspace(0,Q_100,10),np.full(10,H_100),linestyle="-.",color="orange")
ax[1].plot(np.full(10,Q_100),np.linspace(0,Phydr,10),linestyle="-.",color="orange")

kols_2[0].pyplot(fig)


kols_2[1].markdown("""* Hfit üzerinde hidrolik gücün en yüksek olduğu nokta (P_hydr) hesaplandı.
* P_hydr'a karşılık gelen debi (Q_100) bulundu.'
* Hfit eğrisi üzerinde Q_100 değerinin çıktısı H_100 hesaplandı.
""")

kols_2[1].write("** P_hydr      :%.2f W **" %(Phydr))
kols_2[1].write("** Q_100       :%.2f m³/h **" %(Q_100))
kols_2[1].write("** H_100       :%.2f m **" %(H_100))

with konteyner_2.expander("TS EN 16297-1:2013-04 atıf"):
    st.image("fig/TSE_2.png")

###############################################################################
# Pref
###############################################################################

konteyner_3 = st.container()
kols_3 = konteyner_3.columns([1,1])

Pref=1.7*Phydr+17*(1-np.e**(-0.3*Phydr))

kols_3[0].write("** P_ref = %.2f **" %Pref)
kols_3[1].write(" * Referans Güç (P_ref) hesaplandı.")

with konteyner_3.expander("TS EN 16297-1:2013-04 atıf"):
    st.image("fig/TSE_3.png")
    
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
#     st.image("fig/TSE_4.png")

###############################################################################
# Referans kontrol eğrisi
###############################################################################

konteyner_5 = st.container()
kols_5 = konteyner_5.columns([4,1,1,1,1])

Qrefl=np.linspace(0,Q_100,5)
Hrefl=np.linspace(H_100*0.5,H_100,5)
Qref=Qrefl[1:]
Href=Hrefl[1:]

fig, ax=plt.subplots(1,1)
fig.set_size_inches(8,4)

ax.plot(df.Q,Hfit(df.Q))
ax.scatter(Qref,Href,color="red")
ax.plot(Qrefl,Hrefl,color="violet")
ax.set_title("Referans Kontrol Eğrisi")
ax.legend(["Hdfit","RKD","Ref.Noktaları"])
ax.grid()

#fH = interp1d(dfk.Q,dfk.H)

ax.plot(dfk.Q,intH(dfk.Q))

kols_5[0].pyplot(fig)

kols_5[1].subheader("Q_25ref")
kols_5[1].write("Q_25=%.2f"%Qrefl[1])
kols_5[1].write("H_25=%.2f"%Hrefl[1])

kols_5[2].subheader("Q_50ref")
kols_5[2].write("Q_50=%.2f"%Qrefl[2])
kols_5[2].write("H_50=%.2f"%Hrefl[2])

kols_5[3].subheader("Q_75ref")
kols_5[3].write("Q_75=%.2f"%Qrefl[3])
kols_5[3].write("H_75=%.2f"%Hrefl[3])

kols_5[4].subheader("Q_100ref")
kols_5[4].write("Q_100=%.2f"%Qrefl[4])
kols_5[4].write("H_100=%.2f"%Hrefl[4])


with konteyner_5.expander("TS EN 16297-1:2013-04 atıf"):
    st.image("fig/TSE_5.png")
    

###############################################################################
# Ölçüm düzeltme sidebar
###############################################################################

kontey = st.container()
kolsey = st.sidebar.columns([1,1])
Qm=np.zeros(4)
Hm=np.zeros(4)
Pm=np.zeros(4)

st.sidebar.title("Ölçüm Düzeltme")
st.sidebar.subheader("Q_25 Ölçümleri")
Qm[0] = st.sidebar.number_input("Q_25",value=Qref[0])
Hm[0] = st.sidebar.number_input("H_25",value=np.round(intH(Qref[0]),2))
Pm[0] = st.sidebar.number_input("P_25",value=np.round(intPcons(Qref[0]),2))

st.sidebar.subheader("Q_50 Ölçümleri")
Qm[1] = st.sidebar.number_input("Q_50",value=Qref[1])
Hm[1] = st.sidebar.number_input("H_50",value=np.round(intH(Qref[1]),2))
Pm[1] = st.sidebar.number_input("P_50",value=np.round(intPcons(Qref[1]),2))

st.sidebar.subheader("Q_75 Ölçümleri")
Qm[2] = st.sidebar.number_input("Q_75",value=Qref[2])
Hm[2] = st.sidebar.number_input("H_75",value=np.round(intH(Qref[2]),2))
Pm[2] = st.sidebar.number_input("P_75",value=np.round(intPcons(Qref[2]),2))

st.sidebar.subheader("Q_100 Ölçümleri")
Qm[3] = st.sidebar.number_input("Q_100",value=Qref[3])
Hm[3] = st.sidebar.number_input("H_100",value=np.round(intH(Qref[3]),2))
Pm[3] = st.sidebar.number_input("P_100",value=np.round(intPcons(Qref[3]),2))


###############################################################################
# Nokta ölçümleri
###############################################################################

konteyner_8 = st.container()
kols_8 = konteyner_8.columns([4,1,1,1,1])

fig, ax=plt.subplots(1,1)
fig.set_size_inches(8,4)

ax.plot(df.Q,Hfit(df.Q))
ax.scatter(Qref[0:4],Href[0:4],color="red")
ax.plot(Qrefl,Hrefl,color="violet")
ax.set_title("Referans Kontrol Eğrisi")
ax.legend(["Hdfit","RKD","Ref.Noktaları"])
ax.grid()

ax.scatter(Qm,Hm,color="black", marker="x",s=50)

kols_8[0].pyplot(fig)

percerQ = np.abs((Qref-Qm)/Qref)
percerH = np.abs((Href-Hm)/Href)

kols_8[1].subheader("Q_25")
kols_8[1].write("Q_25=%.2f"%Qm[0])
kols_8[1].write("H_25=%.2f"%Hm[0])
kols_8[1].write("P_25=%.2f"%Pm[0])
kols_8[1].write("%% dQ_25=%.2f"%percerQ[0])
kols_8[1].write("%% dH_25=%.2f"%percerH[0])

kols_8[2].subheader("Q_50")
kols_8[2].write("Q_50=%.2f"%Qm[1])
kols_8[2].write("H_50=%.2f"%Hm[1])
kols_8[2].write("P_50=%.2f"%Pm[1])
kols_8[2].write("%% dQ_50=%.2f"%percerQ[1])
kols_8[2].write("%% dH_50=%.2f"%percerH[1])

kols_8[3].subheader("Q_75")
kols_8[3].write("Q_75=%.2f"%Qm[2])
kols_8[3].write("H_75=%.2f"%Hm[2])
kols_8[3].write("P_75=%.2f"%Pm[2])
kols_8[3].write("%% dQ_75=%.2f"%percerQ[2])
kols_8[3].write("%% dH_75=%.2f"%percerH[2])

kols_8[4].subheader("Q_100")
kols_8[4].write("Q_100=%.2f"%Qm[3])
kols_8[4].write("H_100=%.2f"%Hm[3])
kols_8[4].write("P_100=%.2f"%Pm[3])
kols_8[4].write("%% dQ_100=%.2f"%percerQ[3])
kols_8[4].write("%% dH_100=%.2f"%percerH[3])

with konteyner_8.expander("TS EN 16297-1:2013-04 atıf"):
    st.image("fig/TSE_8.png")

###############################################################################
# PLavg
###############################################################################

konteyner_9 = st.container()
kols_9 = konteyner_9.columns([1,1,1])

pb = Pm*(Href>= Hm)*Href/Hm
pk = Pm*(Href<Hm)
Pl = pb + pk

L=np.array([0.44,0.35,0.15,0.06])
PLavg=(Pl*L).sum()

kols_9[1].write("PLavg = %.2f" %PLavg)


with konteyner_9.expander("TS EN 16297-1:2013-04 atıf"):
    st.image("fig/TSE_9.png")

with konteyner_9.expander("TS EN 16297-2:2013-04 atıf"):
    st.image("fig/TSE_7.png")
    
###############################################################################
# EEI
###############################################################################

konteyner_10 = st.container()
kols_10 = konteyner_10.columns([1,1,1])

EEI = PLavg/Pref*0.49

kols_10[1].write("EEI = %.3f"%EEI)


with konteyner_10.expander("TS EN 16297-1:2013-04 atıf"):
    st.image("fig/TSE_10.png")

with konteyner_10.expander("TS EN 16297-2:2013-04 atıf"):
    st.image("fig/TSE_11.png")




