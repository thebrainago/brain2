# Loc lai theo tieu chi moi (lai > 0, DD < 80%) + walk-forward cho ho DCA/luoi/go lenh. Don vi trong jsonl la ty le (0.8 = 80%).
import os, json, collections, numpy as np, pandas as pd
from cau_hinh import TAM
import dong_co as E, luoi_dca
DD=0.8
def dat(b, hai=False):
    ok=b['cagr']>0 and b['dd']<DD
    return ok and (not hai or (b['cagr_17_21']>0 and b['cagr_22_26']>0 and b['dd_17_21']<DD and b['dd_22_26']<DD))
def loc(tep):
    rows=[json.loads(l) for t in tep for l in open(os.path.join(TAM,t))]
    c1=collections.Counter(); c2=collections.Counter(); tot={}
    for o in rows:
        h=o['ho']; a=[b for b in o['theo_L'] if dat(b)]; z=[b for b in o['theo_L'] if dat(b,True)]
        if a: c1[h]+=1
        if z:
            c2[h]+=1; b=max(z,key=lambda b:b['cagr'])
            if h not in tot or b['cagr']>tot[h]['L']['cagr']: tot[h]=dict(che_do=o['che_do'],tham_so=o['tham_so'],lenh_nam=round(o['lenh_nam']),L={k:round(v*100,1) if k!='L' else v for k,v in b.items()})
    return dict(tong=len(rows),dat=sum(c1.values()),dat_2_nua=sum(c2.values()),theo_ho=dict(c1),theo_ho_2_nua=dict(c2),tot_nhat_2_nua=tot)
if __name__=='__main__':
    kq={'cu_4950':loc(['luoi.jsonl','luoi2.jsonl','luoi3.jsonl']),'dca_10236':loc(['luoi_dca.jsonl'])}
    d=np.load(os.path.join(TAM,'r_dca.npz')); R=d['R']; M=d['M']; V=list(luoi_dca.viec())
    yrs=pd.DatetimeIndex(E.days).year.values; st=np.searchsorted(E.days.values,np.datetime64('2020-01-01'))
    wf={}
    for nhom in ['dca','luoi_hai_chieu','go_lenh','tat_ca']:
        idx=np.array([i for i,v in enumerate(V) if nhom=='tat_ca' or v[0]==nhom])
        for L in (1,2,3,5):
            r=np.zeros(R.shape[1]); m=np.zeros(R.shape[1]); chon=[]
            for Y in range(2020,2027):
                tr=(yrs>=Y-3)&(yrs<Y); te=yrs==Y
                g=np.log(np.clip(1+L*R[idx][:,tr],1e-6,None)).sum(1); g[np.min(1+L*M[idx][:,tr],axis=1)<=0]=-1e9
                b=idx[int(np.argmax(g))]; chon.append([Y,V[b][0],V[b][1],V[b][2]]); r[te]=R[b,te]; m[te]=M[b,te]
            k=E.ket_qua(r[st:],m[st:],L,nam=(E.days[-1]-E.days[st]).days/365.25)
            nam={int(Y):round(float(np.prod(1+L*r[yrs==Y])-1)*100,1) for Y in range(2020,2027)}
            wf[f'{nhom}_L{L}']=dict(cagr=round(k['cagr']*100,1),dd=round(k['dd']*100,1),dat=bool(k['cagr']>0 and k['dd']<DD),theo_nam=nam,chon=chon)
            print(nhom,L,wf[f'{nhom}_L{L}']['cagr'],wf[f'{nhom}_L{L}']['dd'],nam,flush=True)
    kq['wf_2020_2026']=wf
    json.dump(kq,open(os.path.join(os.path.dirname(__file__),'..','ket_qua','loc_lai_tieu_chi_moi.json'),'w'),ensure_ascii=False,indent=1,default=str)
    for k in ('cu_4950','dca_10236'): print(k,{x:kq[k][x] for x in ('tong','dat','dat_2_nua','theo_ho_2_nua')})
    for h,t in kq['dca_10236']['tot_nhat_2_nua'].items(): print(h,t)
