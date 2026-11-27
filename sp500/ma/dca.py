# Ho DCA / luoi (grid) / go lenh (recovery) / hedge - trong phien My, dong het cuoi phien (khong swap). numba.
# Duong gia trong nen M5: O -> (L,H neu nen tang; H,L neu nen giam) -> C (giong cach MT5 dung khi khong co tick).
import numpy as np
from numba import njit
import dong_co as E
O, H, L, C = E.O, E.H, E.L_, E.C
ND, NB = O.shape

@njit(cache=True)
def _duong(o,h,l,c):
    if c>=o: return (o,l,h,c)
    return (o,h,l,c)

@njit(cache=True)
def k_dca(O,H,L,C,atr,reg,cho_ban,buoc,nhan,nmax,tp,sl,lap,bar0,sp):
    nd,nb=O.shape; r=np.zeros(nd); mae=np.zeros(nd); nl=0
    gia=np.zeros(64); kl=np.zeros(64)
    for d in range(nd):
        g=reg[d]; a=atr[d]
        if g==0 or a!=a: continue
        if g<0 and not cho_ban: continue
        p0=O[d,bar0]; da_thuc=0.0; xau=0.0; n=0; dang=False; ket_thuc=False
        for j in range(bar0,nb):
            pts=_duong(O[d,j],H[d,j],L[d,j],C[d,j])
            for q in range(4):
                x=pts[q]
                if ket_thuc: break
                if not dang:
                    if j==bar0 and q==0 or lap:
                        n=1; gia[0]=x; kl[0]=1.0; dang=True; da_thuc-=sp; nl+=1
                    else: continue
                # them lenh khi gia di nguoc buoc*ATR tu lenh cuoi
                while n<nmax and g*(x-gia[n-1])<=-buoc*a:
                    gia[n]=gia[n-1]-g*buoc*a; kl[n]=kl[n-1]*nhan; da_thuc-=sp*kl[n]; n+=1; nl+=1
                tong=0.0; sl_=0.0
                for i in range(n): tong+=kl[i]*g*(x-gia[i]); sl_+=kl[i]
                tb=0.0
                for i in range(n): tb+=kl[i]*gia[i]
                tb/=sl_
                if da_thuc+tong<xau: xau=da_thuc+tong
                if g*(x-tb)>=tp*a:                       # chot ro
                    da_thuc+=sl_*tp*a; dang=False; n=0
                    if not lap: ket_thuc=True
                elif sl>0 and n>=nmax and g*(x-gia[n-1])<=-sl*a:   # cat lo sau khi day ro
                    da_thuc+=tong; dang=False; n=0; ket_thuc=True
        if dang:
            x=C[d,nb-1]; tong=0.0
            for i in range(n): tong+=kl[i]*g*(x-gia[i])
            da_thuc+=tong
        r[d]=da_thuc/p0; mae[d]=min(xau,0.0)/p0
    return r,mae,nl

@njit(cache=True)
def k_luoi(O,H,L,C,atr,reg,che,buoc,nmax,tp_b,sp):
    """Luoi 2 chieu quanh gia mo phien: moi muc buoc*ATR; gia xuong cat muc -> mua (TP +tp_b buoc), len cat muc -> ban.
    che: 0 hai chieu, 1 chi mua, 2 theo che do (tang chi mua, giam chi ban)."""
    nd,nb=O.shape; r=np.zeros(nd); mae=np.zeros(nd); nl=0
    mua_v=np.zeros(256); ban_v=np.zeros(256)
    for d in range(nd):
        a=atr[d]
        if a!=a or reg[d]==0 and che==2: continue
        cm = che!=2 or reg[d]>0
        cb = che==0 or (che==2 and reg[d]<0)
        s=buoc*a; p0=O[d,0]; nm=0; nbn=0; da=0.0; xau=0.0; prev=p0
        for j in range(nb):
            pts=_duong(O[d,j],H[d,j],L[d,j],C[d,j])
            for q in range(4):
                x=pts[q]
                # TP cac lenh mo
                k=0
                for i in range(nm):
                    if x>=mua_v[i]+tp_b*s: da+=tp_b*s
                    else: mua_v[k]=mua_v[i]; k+=1
                nm=k; k=0
                for i in range(nbn):
                    if x<=ban_v[i]-tp_b*s: da+=tp_b*s
                    else: ban_v[k]=ban_v[i]; k+=1
                nbn=k
                # cat muc luoi
                lo=min(prev,x); hi=max(prev,x)
                m0=np.ceil((lo-p0)/s); m1=np.floor((hi-p0)/s)
                mm=m0
                while mm<=m1:
                    lv=p0+mm*s
                    if mm!=0:
                        if x<prev and mm<0 and cm and nm<nmax: mua_v[nm]=lv; nm+=1; da-=sp; nl+=1
                        if x>prev and mm>0 and cb and nbn<nmax: ban_v[nbn]=lv; nbn+=1; da-=sp; nl+=1
                    mm+=1
                prev=x
                t=0.0
                for i in range(nm): t+=x-mua_v[i]
                for i in range(nbn): t+=ban_v[i]-x
                if da+t<xau: xau=da+t
        x=C[d,nb-1]
        for i in range(nm): da+=x-mua_v[i]
        for i in range(nbn): da+=ban_v[i]-x
        r[d]=da/p0; mae[d]=min(xau,0.0)/p0
    return r,mae,nl

@njit(cache=True)
def k_go(O,H,L,C,atr,reg,vung,tp,nhan,nmax,bar0,sp):
    """Go lenh (zone recovery): vao theo che do; gia di nguoc 'vung'*ATR -> mo lenh nguoc chieu klg*nhan;
    dao chieu moi lan cham bien vung; dong tat ca khi tong lai >= tp*ATR*1 don vi; het nmax lenh -> giu toi cuoi phien."""
    nd,nb=O.shape; r=np.zeros(nd); mae=np.zeros(nd); nl=0
    gia=np.zeros(32); kl=np.zeros(32); hg=np.zeros(32)
    for d in range(nd):
        g=reg[d]; a=atr[d]
        if g==0 or a!=a: continue
        p0=O[d,bar0]; gia[0]=p0; kl[0]=1.0; hg[0]=g; n=1; da=-sp; xau=-sp; xong=False; nl+=1
        tren=p0 if g>0 else p0+vung*a; duoi=p0-vung*a if g>0 else p0
        for j in range(bar0,nb):
            pts=_duong(O[d,j],H[d,j],L[d,j],C[d,j])
            for q in range(4):
                if xong: break
                x=pts[q]
                t=0.0
                for i in range(n): t+=kl[i]*hg[i]*(x-gia[i])
                if da+t<xau: xau=da+t
                if da+t>=tp*a: da+=t; xong=True; break
                huong_cuoi=hg[n-1]
                if n<nmax:
                    if huong_cuoi>0 and x<=duoi: gia[n]=duoi; kl[n]=kl[n-1]*nhan; hg[n]=-1; da-=sp*kl[n]; n+=1; nl+=1
                    elif huong_cuoi<0 and x>=tren: gia[n]=tren; kl[n]=kl[n-1]*nhan; hg[n]=1; da-=sp*kl[n]; n+=1; nl+=1
        if not xong:
            x=C[d,nb-1]
            for i in range(n): da+=kl[i]*hg[i]*(x-gia[i])
        r[d]=da/p0; mae[d]=min(xau,0.0)/p0
    return r,mae,nl

def dca(regime, cho_ban=False, buoc=0.5, nhan=1.0, nmax=5, tp=0.25, sl=0.0, lap=False, bar0=0):
    return k_dca(O,H,L,C,E.ATR,regime.astype(np.float64),cho_ban,buoc,nhan,nmax,tp,sl,lap,bar0,E.SPREAD)
def luoi_hai_chieu(regime, che=0, buoc=0.2, nmax=10, tp_b=1.0):
    return k_luoi(O,H,L,C,E.ATR,regime.astype(np.float64),che,buoc,nmax,tp_b,E.SPREAD)
def go_lenh(regime, vung=0.5, tp=0.25, nhan=2.0, nmax=5, bar0=0):
    return k_go(O,H,L,C,E.ATR,regime.astype(np.float64),vung,tp,nhan,nmax,bar0,E.SPREAD)
