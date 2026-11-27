import os
from cau_hinh import TAM, NGUON_M5
import itertools, json, numpy as np, multiprocessing as mp
import dong_co as E, he, luoi
def viec():
    for g in luoi.REG:
        for ct in [None,(0,),(4,),(0,1,2,3)]: yield ('qua_dem',g,dict(chi_thu=ct))
        for a,b in itertools.product([1,2,3,4],[1,2,3,4,5]): yield ('dau_thang',g,dict(ngay_cuoi=a,ngay_dau=b))
        for nv,nr,cb,hs in itertools.product([10,20,55,100],[5,10,20,50],[False,True],[0.25,0.5,1.0]):
            if nr>=nv or (not cb and hs!=0.5): continue
            yield ('donchian',g,dict(n_vao=nv,n_ra=nr,cho_ban=cb,he_so_ban=hs))
if __name__=='__main__':
    V=list(viec()); print('so bien the',len(V),flush=True)
    with mp.Pool(6) as P, open(os.path.join(TAM,'luoi2.jsonl'),'w') as f:
        for o in P.imap_unordered(luoi.chay,V,chunksize=8): f.write(json.dumps(o)+'\n')
    print('xong')
