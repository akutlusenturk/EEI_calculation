from pyModbusTCP.client import ModbusClient
#import pyModbusTCP.utils
import numpy as np
import time
#from threading import Thread

np.set_printoptions(suppress=True)


##############################################################################

SERVER_HOST = "192.168.1.15"
SERVER_PORT = 502
SERVER_U_ID = 1

c = ModbusClient()

c.host(SERVER_HOST)
c.port(SERVER_PORT)
c.unit_id(SERVER_U_ID)

us=np.arange(1,24)
taban=np.full((23),2)
maske=1/np.power(taban,us)

##############################################################################

def oku(reg=100,n=10):
    if not c.is_open():
        if not c.open():
            print("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))
    if c.is_open():
        regs = c.read_holding_registers(reg,n)
        #print(f"Register {reg} to {reg+n-1} is read.")
    return regs

##############################################################################

def yaz(reg,n):
    if not c.is_open():
        if not c.open():
            print("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))
    if c.is_open():
        c.write_multiple_registers(reg,n)   
        

##############################################################################
        
def zaman():
    tarih = time.strftime("%Y/%m/%d")
    saat = time.strftime("%H:%M:%S")
    return [tarih,saat]

##############################################################################

# def jenerator(adres=400):
    
#     T = 20 + 1.5*np.random.uniform(-1,1)
#     P = 0.99 + 0.1*np.random.uniform(-1,1)
#     Q = 2.5 + 0.2*np.random.uniform(-1,1)
#     P1 = 0.6 + 0.01*np.random.uniform(-1,1)
#     P2 = 3.5 + 0.01*np.random.uniform(-1,1)
#     E = 200 + 0.2*np.random.uniform(-1,1)
#     D = 0.7
    
#     z = np.array([[T,P,Q,P1,P2,E,D]])
#     #zisim = np.array([["T","P","Q","P1","P2,"E","D"]])
#     zint = (z//1).astype(int)
#     zfloat = (np.round_(z,2)%1*100).astype(int)
#     zo = np.concatenate((zint.T,zfloat.T),1)

#     for i in range(len(zo)):
#         for j in range(2):
#             regi = adres + i*10 + j
#             yaz(regi,[zo[i,j]])
                    
#     return (zo)

##############################################################################
    
# def set_debi(q):
#     qi = ikra(400)[2]
#     vana = ikra(400)[5]
#     tod = 0.05
#     tov = 5
#     t=2
#     if abs(qi-q) < qi*tod:
#         print("tamam")
#         pass
#     elif qi > q:
#         set_vana(vana-tov)
#         print(vana)
#         time.sleep(t)
#         set_debi(q)
#     elif qi < q:
#         print(vana)
#         set_vana(vana+tov)
#         time.sleep(t)
#         set_debi(q)


##############################################################################
    
def ieee_con(n):
    sol="{0:016b}".format(int(n[1]))
    sag="{0:016b}".format(int(n[0]))
    ikili=sol+sag
    
    isaret=int(ikili[0]) #0 ise +; 1 ise -
    eksp=ikili[1:9]
    mantissa=ikili[9:]

    exb=int(eksp,2)-127 #127 is the bias for single precision
    manti=np.array(list(mantissa))
    frac=np.sum(manti.astype(int)*maske)
    sonuc=((-1)**isaret)*(1+frac)*(2**exb)

    return sonuc
    
#############################################################################

def set_Q(q,r=1000,t=0.40,tol =0.05):
    for i in range(r):
        Q = np.round(ieee_con(oku(40,2)),3)
        D = oku(42,1)[0]
        time.sleep(t)
        if q > Q+Q*tol:
            yaz(42,[D+1])
        elif q < Q-Q*tol:
            yaz(42,[D-1])
        else:
            break
        print(Q,D)
    return

    
def set_H(h,r=1000,t=0.40,tol =0.05):
    for i in range(r):
        P1 = np.round(ieee_con(oku(32,2)),2)
        P2 = np.round(ieee_con(oku(34,2)),2)
        dP = np.round(P2-P1,2)
        H = np.round(dP*100/9.81,2)
        D = oku(42,1)[0]
        time.sleep(t)
        if h > H+H*tol:
            yaz(42,[D-1])
        elif h < H-H*tol:
            yaz(42,[D+1])
        else:
            break
        print(H,D)
    return


        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    