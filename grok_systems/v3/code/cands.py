# Candidate programs (signal builders) for basket/scalp validation.
import numpy as np, sig_v3 as S, combo as C, scalp as SC
def build_sig(D,asset,prog,raw_cache):
    """prog: dict(kind='single'|'pair', a, b, W, adx, sess)"""
    if prog['kind']=='new':
        import newsig as NS
        if 'newsp' not in raw_cache: raw_cache['newsp']=NS.specs(D)
        s=raw_cache['newsp'][prog['a']]; s=S.filters(D,s,prog.get('adx','none'),prog.get('sess','all'),asset); return np.where(D.fut_ok.values,s,0).astype(np.int64)
    if prog['kind']=='new2':
        import newsig2 as NS2
        if 'newsp2' not in raw_cache: raw_cache['newsp2']=NS2.specs2(D)
        s=raw_cache['newsp2'][prog['a']]; s=S.filters(D,s,prog.get('adx','none'),prog.get('sess','all'),asset); return np.where(D.fut_ok.values,s,0).astype(np.int64)
    if prog['kind']=='new3':
        import newsig3 as NS3
        if 'newsp3' not in raw_cache: raw_cache['newsp3']=NS3.specs3(D)
        s=raw_cache['newsp3'][prog['a']]; s=S.filters(D,s,prog.get('adx','none'),prog.get('sess','all'),asset); return np.where(D.fut_ok.values,s,0).astype(np.int64)
    if prog['kind']=='new4':
        import newsig4 as NS4
        if 'newsp4' not in raw_cache: raw_cache['newsp4']=NS4.specs4(D)
        s=raw_cache['newsp4'][prog['a']]; s=S.filters(D,s,prog.get('adx','none'),prog.get('sess','all'),asset); return np.where(D.fut_ok.values,s,0).astype(np.int64)
    specs=SC.G['specs']
    def raw(n):
        if n not in raw_cache: raw_cache[n]=np.asarray(specs[n](D),dtype=np.int8)
        return raw_cache[n]
    if prog['kind']=='single': s=raw(prog['a'])
    else: s=C.combine(raw(prog['a']),raw(prog['b']),prog['W'])
    s=S.filters(D,s,prog.get('adx','none'),prog.get('sess','all'),asset)
    ok=D.fut_ok.values
    if any(str(prog.get(k,'')).startswith('xlead') for k in ('a','b')): ok=ok&D.a_ok.values
    return np.where(ok,s,0).astype(np.int64)
