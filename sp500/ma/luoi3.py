# Luoi 3: VWAP keo, gap, IBS (27/11/2026)
import os
from cau_hinh import TAM
import itertools, json, multiprocessing as mp
import luoi
def viec():
    for g in luoi.REG:
        for tb,la,sa,cb in itertools.product([6,12,24],[0.0,0.25,0.5],[None,0.5,1.0],[False,True]):
            yield ('vwap_keo',g,dict(tu_bar=tb,lech_atr=la,stop_atr=sa,cho_ban=cb))
        for ng,k,sa in itertools.product([0.1,0.3,0.5,0.8],['lap','theo'],[None,0.5,1.0]):
            yield ('khoang_trong',g,dict(nguong_atr=ng,kieu=k,stop_atr=sa))
        for ng,gn in itertools.product([0.1,0.2,0.3,0.5],[1,2,3,5]):
            yield ('ibs',g,dict(nguong=ng,giu_ngay=gn))
if __name__=='__main__':
    V=list(viec()); print('so bien the',len(V),flush=True)
    with mp.Pool(6) as P, open(os.path.join(TAM,'luoi3.jsonl'),'w') as f:
        for o in P.imap_unordered(luoi.chay,V,chunksize=8): f.write(json.dumps(o)+'\n')
    print('xong')
