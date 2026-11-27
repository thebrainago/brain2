# BUOC 7 - NHAT KY BONG (chi ghi tin hieu, KHONG dat lenh, KHONG doi luat live). Chay tren MAY NHA (can Fxaurum gateway ws://127.0.0.1:9001/).
# Chi RPC doc aggTrades (khong syncTicks/syncHistory). Moi vong: keo tick 120' gan nhat cua ESZ6 (CME) va GCZ6 (COMEX), gom phut,
# tinh tin hieu bang phong_cach_tay/tin_hieu_data.py, ghi 1 dong cho moi phut DA DONG moi vao CSV.
# Lenh chay (PowerShell):  python bong_tin_hieu.py --ra C:\Users\DUNG\sp500_2711\bong --vong 60 --lan 0
#   --lan 0 = chay mai; dung bang Ctrl+C hoac taskkill /PID <pid> dung PID cua tien trinh nay.
import asyncio, json, os, sys, csv, argparse, collections, time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd, websockets
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import tin_hieu_data as T
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")); from phong_cach_tay import tin_hieu_data as T
URL = "ws://127.0.0.1:9001/"; NY = ZoneInfo("America/New_York"); VN = ZoneInfo("Asia/Saigon")
MA = {"ES": dict(exchange="CME", symbol="ESZ6", lon=20), "GC": dict(exchange="COMEX", symbol="GCZ6", lon=5)}
COT = ["big30", "delta15", "cvd_pk", "vah_val_pha", "muc_fade", "muc_hop_le", "big30_giu", "delta15_giu", "uu_tien", "cong_dca_mua", "cong_dca_ban"]

async def rpc(ws, method, params, rid, timeout=120):
    await ws.send(json.dumps({"method": method, "params": params, "id": rid}))
    end = asyncio.get_event_loop().time() + timeout
    while True:
        m = json.loads(await asyncio.wait_for(ws.recv(), timeout=max(1, end - asyncio.get_event_loop().time())))
        if "stream" in m: continue
        if m.get("id") == rid: return m

async def keo(ws, ma, t0, t1, rid, lim=50000):
    """Phan trang LUI (API tra lim tick CUOI trong [t0,t1]). Tra (phut dict, ho so dict, rid)."""
    cf = MA[ma]; phut = {}; hs = collections.defaultdict(lambda: [0.0, 0.0]); seen = set(); cur = t1
    while cur > t0:
        rid += 1; m = await rpc(ws, "aggTrades", {"exchange": cf["exchange"], "symbol": cf["symbol"], "startTime": t0, "endTime": cur, "limit": lim}, rid)
        rs = m.get("result") or []; moi = 0; first = cur
        for r in rs:
            r = list(r) + [None] * (6 - len(r)); tms, p, q, s, _, tu = r[:6]
            k = tu if tu is not None else (tms, p, q, s)
            if k in seen: continue
            seen.add(k); moi += 1; first = min(first, tms); p = float(p); q = float(q); mua = s == "B"; mi = tms // 60000
            a = phut.get(mi)
            if a is None: a = phut[mi] = [None, p, p, None, 0, 0, 0, 0, 0, 0, 0, 10**15, 0]
            if tms <= a[11]: a[11] = tms; a[0] = p
            if tms >= a[12]: a[12] = tms; a[3] = p
            a[1] = max(a[1], p); a[2] = min(a[2], p); a[4] += q; a[5 if mua else 6] += q; a[7] += 1
            if q >= cf["lon"]: a[8 if mua else 9] += q
            a[10] = max(a[10], q); hs[round(p, 2)][0 if mua else 1] += q
        if len(rs) < lim or moi == 0: break
        cur = first
    return phut, hs, rid

def phien_cua(ma, ms):
    ny = datetime.fromtimestamp(ms / 1000, tz=timezone.utc).astimezone(NY)
    return (ny + timedelta(hours=6)).strftime("%Y%m%d") if ma == "GC" else ny.strftime("%Y%m%d")

def khung_phien_truoc(ma, now_ms):
    ny = datetime.fromtimestamp(now_ms / 1000, tz=timezone.utc).astimezone(NY)
    if ma == "ES":
        d = ny.date() - timedelta(days=1)
        while d.weekday() >= 5: d -= timedelta(days=1)
        a = datetime(d.year, d.month, d.day, 9, 30, tzinfo=NY); b = datetime(d.year, d.month, d.day, 16, 15, tzinfo=NY)
    else:
        cur = datetime.strptime(phien_cua("GC", now_ms), "%Y%m%d").date(); d = cur - timedelta(days=1)
        while d.weekday() >= 5: d -= timedelta(days=1)
        a = datetime(d.year, d.month, d.day, 18, 0, tzinfo=NY) - timedelta(days=1); b = datetime(d.year, d.month, d.day, 17, 0, tzinfo=NY)
    return d.strftime("%Y%m%d"), int(a.timestamp() * 1000), int(b.timestamp() * 1000)

async def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ra", required=True); ap.add_argument("--vong", type=int, default=60)
    ap.add_argument("--lan", type=int, default=0); ap.add_argument("--ma", default="ES,GC"); a = ap.parse_args()
    os.makedirs(a.ra, exist_ok=True); f_log = os.path.join(a.ra, "bong_tin_hieu.csv"); moi_file = not os.path.exists(f_log)
    da_ghi = {}; HS = {}; rid = 1; lan = 0
    with open(f_log, "a", newline="") as fh:
        w = csv.writer(fh)
        if moi_file: w.writerow(["ghi_luc_vn", "ma", "phut_vn", "gia_fut", "phien"] + COT + ["sig", "ghi_chu"]); fh.flush()
        while True:
            lan += 1
            try:
                async with websockets.connect(URL, max_size=2**30, ping_interval=20, open_timeout=15) as ws:
                    now = int(time.time() * 1000)
                    for ma in a.ma.split(","):
                        ten_pt, pa, pb = khung_phien_truoc(ma, now)
                        if HS.get(ma, (None,))[0] != ten_pt:
                            _, hs, rid = await keo(ws, ma, pa, pb, rid)
                            HS[ma] = (ten_pt, pd.DataFrame([(p, v[0], v[1]) for p, v in sorted(hs.items())], columns=["gia", "vol_mua", "vol_ban"]))
                        phut, _, rid = await keo(ws, ma, now - 120 * 60000, now, rid)
                        if not phut: continue
                        F = pd.DataFrame([[mi * 60000] + v[:11] for mi, v in sorted(phut.items())],
                                         columns=["phut_ms", "o", "h", "l", "c", "vol", "vol_mua", "vol_ban", "so_lenh", "lon_mua", "lon_ban", "max_qty"])
                        F = F[F.phut_ms < (now // 60000) * 60000].copy()            # chi phut da dong
                        if F.empty: continue
                        F["phien"] = [phien_cua(ma, x) for x in F.phut_ms]
                        pro = {HS[ma][0]: HS[ma][1]}
                        # ho so phien truoc gan vao phien hien tai: tin_hieu() dung pro[phien truoc] cho phien ke tiep trong danh sach
                        ph = sorted(F.phien.unique()); F = pd.concat([F.iloc[:0], F]); pro_map = {}
                        if ph: pro_map[HS[ma][0]] = HS[ma][1]
                        FF = pd.concat([pd.DataFrame({"phut_ms": [F.phut_ms.min() - 10**9], "o": [np.nan], "h": [np.nan], "l": [np.nan], "c": [np.nan], "vol": [0], "vol_mua": [0],
                                                      "vol_ban": [0], "so_lenh": [0], "lon_mua": [0], "lon_ban": [0], "max_qty": [0], "phien": [HS[ma][0]]}), F], ignore_index=True)
                        R = T.tin_hieu(FF, pro_map, T.NGUONG_MAC_DINH[ma]).iloc[1:]
                        dau = ma not in da_ghi
                        for _, r in R.iterrows():
                            if r.phut_ms <= da_ghi.get(ma, 0): continue
                            if r.phut_ms < now - 3 * 60000 and not dau: continue
                            t_vn = datetime.fromtimestamp(r.phut_ms / 1000, tz=timezone.utc).astimezone(VN).strftime("%Y-%m-%d %H:%M")
                            w.writerow([datetime.now(VN).strftime("%Y-%m-%d %H:%M:%S"), ma, t_vn, r.c, r.phien] + [r[k] for k in COT] + [r[f"sig_{ma}"], "chi log, khong dat lenh"])
                            da_ghi[ma] = r.phut_ms
                        fh.flush()
            except Exception as e:
                print("loi vong", lan, repr(e), flush=True)
            print(datetime.now(VN).strftime("%H:%M:%S"), "vong", lan, "da_ghi", {k: datetime.fromtimestamp(v / 1000, tz=timezone.utc).astimezone(VN).strftime("%H:%M") for k, v in da_ghi.items()}, flush=True)
            if a.lan and lan >= a.lan: break
            await asyncio.sleep(a.vong)

asyncio.run(main())
