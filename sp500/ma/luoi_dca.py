# Luoi 4: DCA / luoi hai chieu / go lenh (27/11/2026). Tieu chi moi cua Anh: lai rong > 0 va DD < 80%.
import os, json, itertools, numpy as np, multiprocessing as mp
from cau_hinh import TAM
import dong_co as E, dca
LEV=[0.5,1,2,3,5,8]
REG=['none','sma200','slope200','sma50&slope200','adx20']
mid=np.searchsorted(E.days.values,np.datetime64('2022-01-01'))
n1=(E.days[mid-1]-E.days[0]).days/365.25; n2=(E.days[-1]-E.days[mid]).days/365.25; nam=(E.days[-1]-E.days[0]).days/365.25
def viec():
    for g in REG:
        for cb,b,nh,nm,tp,sl,lap,b0 in itertools.product([False,True],[0.25,0.5,0.75,1.0],[1.0,1.5,2.0],[3,5,8],[0.1,0.25,0.5],[0.0,1.0],[False,True],[0,6]):
            if cb and g=='none': continue
            yield ('dca',g,dict(cho_ban=cb,buoc=b,nhan=nh,nmax=nm,tp=tp,sl=sl,lap=lap,bar0=b0))
    for g in ['none','sma200','slope200','sma50&slope200']:
        for che,b,nm,tb in itertools.product([0,1,2],[0.1,0.2,0.3,0.5,0.75],[2,3,5,10],[0.5,1.0,2.0]):
            if g=='none' and che==2: continue
            yield ('luoi_hai_chieu',g,dict(che=che,buoc=b,nmax=nm,tp_b=tb))
    for g in REG:
        for v,tp,nh,nm,b0 in itertools.product([0.25,0.5,1.0],[0.1,0.25,0.5,1.0],[1.5,2.0,3.0],[2,3,4,5,7],[0,6]):
            yield ('go_lenh',g,dict(vung=v,tp=tp,nhan=nh,nmax=nm,bar0=b0))
def chay(v):
    ho,g,p=v; r,m,n=getattr(dca,ho)(E.che_do(g),**p)
    bang=[]
    for L in LEV:
        k=E.ket_qua(r,m,L); a=E.ket_qua(r[:mid],m[:mid],L,nam=n1); b=E.ket_qua(r[mid:],m[mid:],L,nam=n2)
        bang.append(dict(L=L,cagr=float(k['cagr']),dd=float(k['dd']),cagr_17_21=float(a['cagr']),cagr_22_26=float(b['cagr']),dd_17_21=float(a['dd']),dd_22_26=float(b['dd'])))
    return dict(ho=ho,che_do=g,tham_so=p,so_lenh=int(n),lenh_nam=n/nam,theo_L=bang), r.astype(np.float32), m.astype(np.float32)
if __name__=='__main__':
    V=list(viec()); print('so bien the',len(V),flush=True)
    Rs=[];Ms=[]
    with mp.Pool(6) as P, open(os.path.join(TAM,'luoi_dca.jsonl'),'w') as f:
        for i,(o,r,m) in enumerate(P.imap(chay,V,chunksize=16)):
            f.write(json.dumps(o)+'\n'); Rs.append(r); Ms.append(m)
            if i%1000==0: print(i,flush=True)
    np.savez_compressed(os.path.join(TAM,'r_dca.npz'),R=np.stack(Rs),M=np.stack(Ms))
    print('xong')
