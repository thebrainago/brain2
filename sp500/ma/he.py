import numpy as np
import dong_co as E
O, H, L, C = E.O, E.H, E.L_, E.C
ND, NB = O.shape
SP = E.SPREAD

def _vao_ra(d, k_vao, gia_vao, huong, stop, tp, k_ra=NB-1):
    """Mo phong 1 lenh trong ngay d tu bar k_vao (gia_vao) den stop/tp/het phien. Tra r, mae."""
    hi = H[d, k_vao:k_ra+1]; lo = L[d, k_vao:k_ra+1]
    if huong > 0:
        mae_dd = lo.min()
        hit_s = np.where(lo <= stop)[0] if stop is not None else np.array([], int)
        hit_t = np.where(hi >= tp)[0] if tp is not None else np.array([], int)
    else:
        mae_dd = hi.max()
        hit_s = np.where(hi >= stop)[0] if stop is not None else np.array([], int)
        hit_t = np.where(lo <= tp)[0] if tp is not None else np.array([], int)
    s = hit_s[0] if len(hit_s) else 10**9; t = hit_t[0] if len(hit_t) else 10**9
    if s <= t and s < 10**9:            # cung bar -> tinh stop truoc (than trong)
        ra = stop; worst = stop
    elif t < 10**9:
        ra = tp; seg = slice(k_vao, k_vao+t+1)
        worst = (L[d, seg].min() if huong > 0 else H[d, seg].max())
    else:
        ra = C[d, k_ra]; worst = mae_dd
    phi = SP/gia_vao
    r = huong*(ra - gia_vao)/gia_vao - phi
    mae = min(0.0, huong*(worst - gia_vao)/gia_vao) - phi
    return r, mae

def orb(regime, m=30, tp_r=None, cho_ban=True, he_so_ban=1.0, stop_kieu='or'):
    k = m//5; r = np.zeros(ND); mae = np.zeros(ND); n = 0
    for d in range(ND):
        g = regime[d]
        if g == 0 or np.isnan(E.ATR[d]): continue
        oh = H[d, :k].max(); ol = L[d, :k].min(); rng = oh - ol
        if rng <= 0: continue
        for j in range(k, NB-1):
            if g > 0 and H[d, j] > oh:
                e = max(oh, O[d, j]); st = ol if stop_kieu == 'or' else e - 0.5*E.ATR[d]
                tp = e + tp_r*(e-st) if tp_r else None
                # bar vao: chi xet tu bar sau (than trong)
                if j+1 >= NB: break
                rr, mm = _vao_ra(d, j+1, e, +1, st, tp); r[d], mae[d] = rr, mm; n += 1; break
            if g < 0 and cho_ban and L[d, j] < ol:
                e = min(ol, O[d, j]); st = oh if stop_kieu == 'or' else e + 0.5*E.ATR[d]
                tp = e - tp_r*(st-e) if tp_r else None
                if j+1 >= NB: break
                rr, mm = _vao_ra(d, j+1, e, -1, st, tp); r[d], mae[d] = rr*he_so_ban, mm*he_so_ban; n += 1; break
    return r, mae, n

def mua_gio_vao(regime, gio_bar=6, can_xanh=True, stop_atr=1.0, cho_ban=True, he_so_ban=1.0):
    """Vao luc bar gio_bar (6=10:00) theo huong che do neu gia da di cung huong tu open; ra cuoi phien."""
    r = np.zeros(ND); mae = np.zeros(ND); n = 0
    for d in range(ND):
        g = regime[d]
        if g == 0 or np.isnan(E.ATR[d]): continue
        if g < 0 and not cho_ban: continue
        e = O[d, gio_bar]
        if can_xanh and (e - O[d, 0])*g <= 0: continue
        st = e - g*stop_atr*E.ATR[d] if stop_atr else None
        rr, mm = _vao_ra(d, gio_bar, e, g, st, None)
        w = 1.0 if g > 0 else he_so_ban
        r[d], mae[d] = rr*w, mm*w; n += 1
    return r, mae, n

def bat_day(regime, k_atr=0.5, stop_atr=1.0, tp_ve_open=True):
    """Nguoc xu huong trong ngay: che do tang -> mua limit tai open - k*ATR; ra o open hoac cuoi phien."""
    r = np.zeros(ND); mae = np.zeros(ND); n = 0
    for d in range(ND):
        g = regime[d]
        if g == 0 or np.isnan(E.ATR[d]): continue
        e = O[d, 0] - g*k_atr*E.ATR[d]
        hit = np.where(L[d, 1:] <= e)[0] if g > 0 else np.where(H[d, 1:] >= e)[0]
        if not len(hit): continue
        j = hit[0] + 1
        st = e - g*stop_atr*E.ATR[d] if stop_atr else None
        tp = O[d, 0] if tp_ve_open else None
        if j+1 >= NB: continue
        rr, mm = _vao_ra(d, j, e, g, st, tp); r[d], mae[d] = rr, mm; n += 1
    return r, mae, n

def swing_rsi2(regime_tang, nguong=10, ra_rsi=70, chi_mua=True):
    """RSI2 tren gia dong cua phien RTH; vao luc dong cua, ra khi RSI2>ra_rsi hoac close>SMA5. Phi swap mua moi dem."""
    c = E.c; rs = E.rsi(c, 2); s5 = E.sma(c, 5)
    r = np.zeros(ND); mae = np.zeros(ND); n = 0; giu = False; e = 0
    for d in range(1, ND):
        if giu:
            dem = (E.days[d] - E.days[d-1]).days
            r[d] = (c[d] - c[d-1])/c[d-1] - E.SWAP_MUA_NAM/360*dem
            mae[d] = min(0, (E.l[d] - c[d-1])/c[d-1])
            if rs[d] > ra_rsi or c[d] > s5[d]:
                giu = False; r[d] -= SP/2/c[d]
        else:
            if regime_tang[d] > 0 and rs[d] < nguong:
                giu = True; n += 1; r[d] -= SP/2/c[d]
    return r, mae, n

def mua_giu(regime):
    c = E.c; r = np.zeros(ND); mae = np.zeros(ND); n = 0; giu = False
    for d in range(1, ND):
        if giu:
            dem = (E.days[d] - E.days[d-1]).days
            r[d] = (c[d]-c[d-1])/c[d-1] - E.SWAP_MUA_NAM/360*dem
            mae[d] = min(0, (E.l[d]-c[d-1])/c[d-1])
        muon = regime[d+1] > 0 if d+1 < ND else giu
        if muon != giu:
            r[d] -= SP/2/c[d]; giu = muon; n += giu
    return r, mae, n

def qua_dem(regime, chi_thu=None):
    """Mua dong cua RTH, ban mo cua RTH hom sau (1 dem swap mua). chi_thu: tap thu (0=T2) duoc vao."""
    c=E.c; o=E.o; r=np.zeros(ND); mae=np.zeros(ND); n=0
    for d in range(ND-1):
        if regime[d+1] <= 0: continue          # regime[d+1] dung du lieu den het ngay d
        if chi_thu is not None and E.days[d].dayofweek not in chi_thu: continue
        dem=(E.days[d+1]-E.days[d]).days
        rr=(o[d+1]-c[d])/c[d]-SP/c[d]-E.SWAP_MUA_NAM/360*dem
        r[d+1]+=rr; mae[d+1]+=min(0,rr); n+=1
    return r, mae, n

def dau_thang(regime, ngay_cuoi=1, ngay_dau=3):
    """Mua dong cua N ngay giao dich cuoi thang, ban dong cua ngay giao dich thu ngay_dau thang sau."""
    c=E.c; r=np.zeros(ND); mae=np.zeros(ND); n=0
    m=np.array([d.month for d in E.days]); 
    # chi so trong thang
    tu_cuoi=np.zeros(ND,int); tu_dau=np.zeros(ND,int)
    for i in range(ND):
        j=i; k=0
        while j+1<ND and m[j+1]==m[i]: j+=1; k+=1
        tu_cuoi[i]=k
        j=i; k=1
        while j-1>=0 and m[j-1]==m[i]: j-=1; k+=1
        tu_dau[i]=k
    giu=False
    for d in range(1,ND):
        if giu:
            dem=(E.days[d]-E.days[d-1]).days
            r[d]=(c[d]-c[d-1])/c[d-1]-E.SWAP_MUA_NAM/360*dem; mae[d]=min(0,(E.l[d]-c[d-1])/c[d-1])
            if tu_dau[d]==ngay_dau and tu_cuoi[d]>5: giu=False; r[d]-=SP/2/c[d]
        elif tu_cuoi[d]==ngay_cuoi-1 and d+1<ND and regime[d+1]>0:
            giu=True; n+=1; r[d]-=SP/2/c[d]
    return r, mae, n

def donchian(regime, n_vao=20, n_ra=10, cho_ban=False, he_so_ban=0.5):
    """Pha vo kenh Donchian theo gia dong RTH, giu qua dem (tra swap)."""
    c=E.c; hh=pd_roll(c,n_vao,max); ll=pd_roll(c,n_vao,min); hx=pd_roll(c,n_ra,max); lx=pd_roll(c,n_ra,min)
    r=np.zeros(ND); mae=np.zeros(ND); n=0; vt=0
    for d in range(1,ND):
        if vt!=0:
            dem=(E.days[d]-E.days[d-1]).days; w=1 if vt>0 else he_so_ban
            sw=E.SWAP_MUA_NAM if vt>0 else E.SWAP_BAN_NAM
            r[d]=w*(vt*(c[d]-c[d-1])/c[d-1]-sw/360*dem)
            mae[d]=w*min(0,vt*((E.l[d] if vt>0 else E.h[d])-c[d-1])/c[d-1])
            if (vt>0 and c[d]<=lx[d-1]) or (vt<0 and c[d]>=hx[d-1]): r[d]-=w*SP/2/c[d]; vt=0
        if vt==0 and d+1<ND:
            if c[d]>=hh[d-1] and regime[d+1]>0: vt=1; n+=1; r[d]-=SP/2/c[d]
            elif cho_ban and c[d]<=ll[d-1] and regime[d+1]<0: vt=-1; n+=1; r[d]-=he_so_ban*SP/2/c[d]
    return r, mae, n

def pd_roll(x,n,f):
    import pandas as pd
    s=pd.Series(x).rolling(n); return (s.max() if f is max else s.min()).values

def vwap_keo(regime, tu_bar=6, lech_atr=0.0, stop_atr=1.0, cho_ban=False):
    """Keo ve 'VWAP' gan dung (trung binh gia dien hinh tich luy - HistData khong co volume).
    Che do tang & gia dang tren open: mua khi gia cham duong trung binh tich luy - lech_atr*ATR; ra cuoi phien."""
    r=np.zeros(ND); mae=np.zeros(ND); n=0
    tp=(H+L+C)/3; vw=np.cumsum(tp,axis=1)/np.arange(1,NB+1)
    for d in range(ND):
        g=regime[d]
        if g==0 or np.isnan(E.ATR[d]) or (g<0 and not cho_ban): continue
        for j in range(tu_bar, NB-2):
            muc=vw[d,j-1]-g*lech_atr*E.ATR[d]
            if (C[d,j-1]-O[d,0])*g<=0: continue
            cham = L[d,j]<=muc if g>0 else H[d,j]>=muc
            if cham:
                st=muc-g*stop_atr*E.ATR[d] if stop_atr else None
                rr,mm=_vao_ra(d,j,muc,g,st,None); r[d],mae[d]=rr,mm; n+=1; break
    return r, mae, n

def khoang_trong(regime, nguong_atr=0.3, kieu='lap', stop_atr=1.0):
    """Gap luc mo cua RTH so voi dong cua hom truoc. kieu='lap': danh lap gap (TP = gia dong hom truoc);
    'theo': danh theo huong gap, ra cuoi phien. Chi vao chieu cho phep boi che do (0 = bo)."""
    r=np.zeros(ND); mae=np.zeros(ND); n=0
    for d in range(1,ND):
        if np.isnan(E.ATR[d]) or regime[d]==0: continue
        gap=(O[d,0]-E.PREVC[d])/E.ATR[d]
        if abs(gap)<nguong_atr: continue
        huong=-np.sign(gap) if kieu=='lap' else np.sign(gap)
        if regime[d]*huong<0 and regime[d]!=1: continue
        if regime[d]==-1 and huong>0: continue
        e=O[d,0]; st=e-huong*stop_atr*E.ATR[d] if stop_atr else None
        tp=E.PREVC[d] if kieu=='lap' else None
        rr,mm=_vao_ra(d,0,e,int(huong),st,tp); r[d],mae[d]=rr,mm; n+=1
    return r, mae, n

def ibs(regime, nguong=0.2, giu_ngay=1):
    """Internal Bar Strength = (C-L)/(H-L) phien RTH; mua dong cua khi IBS<nguong (che do tang), ban dong cua sau giu_ngay."""
    c=E.c; x=(E.c-E.l)/np.maximum(E.h-E.l,1e-9); r=np.zeros(ND); mae=np.zeros(ND); n=0; con=0
    for d in range(1,ND):
        if con>0:
            dem=(E.days[d]-E.days[d-1]).days
            r[d]+=(c[d]-c[d-1])/c[d-1]-E.SWAP_MUA_NAM/360*dem; mae[d]+=min(0,(E.l[d]-c[d-1])/c[d-1]); con-=1
            if con==0: r[d]-=SP/2/c[d]
        if con==0 and d+1<ND and x[d]<nguong and regime[d+1]>0:
            con=giu_ngay; n+=1; r[d]-=SP/2/c[d]
    return r, mae, n
