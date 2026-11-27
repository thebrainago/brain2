# Walk-forward: moi nam Y chon bien the tot nhat tren 3 nam truoc (L co dinh), ap vao nam Y
import os
from cau_hinh import TAM, NGUON_M5
import json, numpy as np, pandas as pd, multiprocessing as mp
import dong_co as E, he, luoi
def r_of(v):
    ho,g,p=v; r,m,n=getattr(he,ho)(E.che_do(g),**p); return r.astype(np.float32), m.astype(np.float32)
if __name__=='__main__':
    V=list(luoi.viec())
    with mp.Pool(6) as P: out=P.map(r_of,V,chunksize=16)
    Rr=np.stack([o[0] for o in out]); M=np.stack([o[1] for o in out])
    np.savez_compressed(os.path.join(TAM,'r_all.npz'),R=Rr,M=M)
    yrs=pd.DatetimeIndex(E.days).year.values
    ket={}
    for L in (5,10,15):
        r_wf=np.zeros(Rr.shape[1]); m_wf=np.zeros(Rr.shape[1]); chon=[]
        for Y in range(2020,2027):
            tr=(yrs>=Y-3)&(yrs<Y); te=yrs==Y
            # diem train: log-tang-truong voi L (phat chay tai khoan)
            g=np.log(np.clip(1+L*Rr[:,tr],1e-6,None)).sum(1)
            low=np.min(1+L*M[:,tr],axis=1); g[low<=0]=-1e9
            b=int(np.argmax(g)); chon.append((Y,V[b][0],V[b][1],V[b][2]))
            r_wf[te]=Rr[b,te]; m_wf[te]=M[b,te]
        st=np.searchsorted(E.days.values,np.datetime64('2020-01-01'))
        k=E.ket_qua(r_wf[st:],m_wf[st:],L,nam=(E.days[-1]-E.days[st]).days/365.25)
        nam={int(Y):round(float(np.prod(1+L*r_wf[yrs==Y])-1)*100,1) for Y in range(2020,2027)}
        ket[L]={'cagr':round(k['cagr']*100,1),'dd':round(k['dd']*100,1),'theo_nam':nam,'chon':[list(map(str,c)) for c in chon]}
        print(L,ket[L]['cagr'],ket[L]['dd'],nam); [print('  ',c) for c in chon]
    json.dump(ket,open(os.path.join(TAM,'wf.json'),'w'),ensure_ascii=False,indent=1)
