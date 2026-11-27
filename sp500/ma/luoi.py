# Luoi tham so SP500: che do loc xu huong x ho he x tham so x don bay
import os
from cau_hinh import TAM, NGUON_M5
import itertools, json, numpy as np, multiprocessing as mp
import dong_co as E, he
REG = ['none','sma50','sma100','sma200','slope100','slope200','adx20','adx25','sma200+adx20','sma50&slope200']
LEV = [1,2,3,5,8,10,15,20]
nam = (E.days[-1]-E.days[0]).days/365.25
mid = np.searchsorted(E.days.values, np.datetime64('2022-01-01'))

def viec():
    for g in REG:
        for m,tp,cb,hs,st in itertools.product([5,15,30,60],[None,1,2,3],[False,True],[0.25,0.5,1.0],['or','atr']):
            if not cb and hs != 1.0: continue
            yield ('orb', g, dict(m=m,tp_r=tp,cho_ban=cb,he_so_ban=hs,stop_kieu=st))
        for gb,cx,sa,cb,hs in itertools.product([1,6,12,24,66],[True,False],[None,0.5,1.0,2.0],[False,True],[0.25,0.5,1.0]):
            if not cb and hs != 1.0: continue
            yield ('mua_gio_vao', g, dict(gio_bar=gb,can_xanh=cx,stop_atr=sa,cho_ban=cb,he_so_ban=hs))
        for k,sa,tv in itertools.product([0.25,0.5,0.75,1.0],[None,0.5,1.0,2.0],[True,False]):
            yield ('bat_day', g, dict(k_atr=k,stop_atr=sa,tp_ve_open=tv))
        for ng,ra in itertools.product([5,10,20,30],[50,70,90]):
            yield ('swing_rsi2', g, dict(nguong=ng,ra_rsi=ra))
        yield ('mua_giu', g, {})

def chay(v):
    ho, g, p = v
    reg = E.che_do(g)
    r, m, n = getattr(he, ho)(reg, **p)
    out = {'ho': ho, 'che_do': g, 'tham_so': p, 'so_lenh': int(n), 'lenh_nam': n/nam,
           'r_tb_lenh_bps': float(r[r != 0].mean()*1e4) if (r != 0).any() else 0.0}
    bang = []
    for L in LEV:
        k = E.ket_qua(r, m, L)
        a = E.ket_qua(r[:mid], m[:mid], L, nam=(E.days[mid-1]-E.days[0]).days/365.25)
        b = E.ket_qua(r[mid:], m[mid:], L, nam=(E.days[-1]-E.days[mid]).days/365.25)
        bang.append({'L': L, 'cagr': float(k['cagr']), 'dd': float(k['dd']),
                     'cagr_17_21': float(a['cagr']), 'cagr_22_26': float(b['cagr']), 'dd_17_21': float(a['dd']), 'dd_22_26': float(b['dd'])})
    out['theo_L'] = bang
    return out

if __name__ == '__main__':
    V = list(viec()); print('so bien the:', len(V), flush=True)
    with mp.Pool(6) as P, open(os.path.join(TAM,'luoi.jsonl'), 'w') as f:
        for i, o in enumerate(P.imap_unordered(chay, V, chunksize=8)):
            f.write(json.dumps(o) + '\n')
            if i % 200 == 0: print(i, flush=True)
    print('xong')
