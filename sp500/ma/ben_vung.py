import json, numpy as np, pandas as pd
import dong_co as E, he
UV = [('bat_day','none',dict(k_atr=0.75,stop_atr=None,tp_ve_open=True)),
      ('bat_day','none',dict(k_atr=0.75,stop_atr=2.0,tp_ve_open=True)),
      ('bat_day','none',dict(k_atr=1.0,stop_atr=2.0,tp_ve_open=True)),
      ('bat_day','sma200+adx20',dict(k_atr=0.75,stop_atr=1.0,tp_ve_open=True)),
      ('swing_rsi2','sma200',dict(nguong=10,ra_rsi=70)),
      ('mua_gio_vao','none',dict(gio_bar=1,can_xanh=True,stop_atr=None,cho_ban=False))]
def chay(ho,g,p,spread,xuyen=0.0):
    E.SPREAD=spread; he.SP=spread+2*xuyen   # xuyen: truot/khop khong tron gia, moi chieu
    return getattr(he,ho)(E.che_do(g),**p)
out=[]
yrs=pd.DatetimeIndex(E.days).year
for ho,g,p in UV:
    for sp,xu in [(0.8,0),(1.5,0),(1.5,0.5),(3.0,0.5)]:
        r,m,n=chay(ho,g,p,sp,xu)
        for L in (5,10,15):
            k=E.ket_qua(r,m,L)
            nam={int(y):round(float(np.prod(1+L*r[yrs==y])-1)*100,1) for y in sorted(set(yrs))}
            out.append(dict(ho=ho,che_do=g,tham_so=p,spread=sp,truot=xu,L=L,n=n,cagr=round(k['cagr']*100,1),dd=round(k['dd']*100,1),theo_nam=nam))
            print(ho,g,p,sp,xu,L,n,out[-1]['cagr'],out[-1]['dd'],min(nam.values()))
json.dump(out,open('ben_vung.json','w'),ensure_ascii=False,indent=0)
