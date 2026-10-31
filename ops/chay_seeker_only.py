# -*- coding: utf-8 -*-
"""SEEKER-only loop: feed nao.db + optional nguon quet; parallel with QUANTLAB-only."""
from __future__ import annotations
import json, os, sys, time, traceback
from pathlib import Path
from datetime import datetime

RUN = Path(r"E:\brain2_grok_seeker_run")
LAB = Path(r"E:\brain2_grok")
LOG = RUN / "seeker_only.log"
STOP = RUN / "DUNG_LAI"
BAI_HOC = LAB / "data" / "bai_hoc.json"

os.environ["BRAIN_SO"] = str(RUN / "nao.db")
os.environ.setdefault("BRAIN_DATA", str(LAB / "data"))
os.environ.setdefault("BRAIN_CACHE", str(RUN / "data_khung"))
os.environ["BRAIN_LLM_PROVIDER"] = "hang_cho"
os.environ["BRAIN_DIEU_TOC"] = "tat"
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUTF8", "1")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
os.environ["TEMP"] = str(RUN / "tmp")
os.environ["TMP"] = str(RUN / "tmp")
os.environ["TMPDIR"] = str(RUN / "tmp")
os.environ.setdefault("BRAIN_MAX_WORKERS", "6")
os.environ.setdefault("BRAIN_CPU_LIMIT", "55")

sys.path.insert(0, str(LAB))
os.chdir(str(LAB))

SIGNAL_PREF = (
    "mql5_signals", "mql5_code", "mql5_bai_viet", "mql5_ma_expert",
    "myfxbook", "fxblue", "signalstart", "ls_mql5", "ls_signal",
    "tradingview", "github", "collective2", "zulutrade", "etoro",
    "rss_mql5", "rss_robotwealth", "rss_quant", "arxiv", "paperswithcode",
)

def ghi(m):
    d = time.strftime("%Y-%m-%d %H:%M:%S ") + m
    try:
        LOG.open("a", encoding="utf-8").write(d + "\n")
    except Exception:
        pass
    print(d, flush=True)

def qua_gio():
    if STOP.exists():
        try:
            started = float((RUN / "sk_started_epoch.txt").read_text().strip())
        except Exception:
            return True
        return (time.time() - started) > 120
    now = datetime.now()
    if (now.hour, now.minute) >= (8, 0):
        try:
            started = float((RUN / "sk_started_epoch.txt").read_text().strip())
        except Exception:
            return False
        return (time.time() - started) > 1800
    return False

def doc_bai_hoc_wins():
    if not BAI_HOC.exists():
        return []
    try:
        raw = json.loads(BAI_HOC.read_text(encoding="utf-8"))
    except Exception:
        return []
    wins = []
    if isinstance(raw, dict):
        for k in ("thang", "winning", "win", "families_win", "gia_dinh_thang", "uu_tien"):
            v = raw.get(k)
            if isinstance(v, list):
                wins.extend([str(x) for x in v])
            elif isinstance(v, dict):
                wins.extend([str(a) for a, b in v.items() if b])
    return sorted(set(wins))

def nap_tu_khoa_bai_hoc(SO, wins):
    """Bias keyword pool toward winning symbols/families (mutate search)."""
    base = [
        "grid ea {w}", "dca recovery {w}", "hedge basket {w}",
        "expert advisor {w} mql5", "{w} H1 strategy source",
        "{w} H4 mean reversion", "signal {w} copy trading",
    ]
    them = []
    skip = {"h1", "h4", "d1", "m30", "m15", "ghep", "mql5", "skst", "skea", "khac"}
    for w in wins[:12]:
        w = str(w).strip()
        if not w or len(w) > 32 or w.lower() in skip:
            continue
        for pat in base:
            them.append(pat.format(w=w))
    them += [
        "mql5 signals profitable 2024", "myfxbook eurusd grid",
        "gbpcad expert advisor source", "cadjpy h4 strategy",
        "nzdusd dca ea open source", "pine script gbpcad strategy",
    ]
    n = 0
    for tu in them:
        try:
            SO.chay(
                "INSERT OR IGNORE INTO tu_khoa(tu, so_lan_dung, so_ket_qua) VALUES(?,?,?)",
                tu, 0, 0,
            )
            SO.chay("UPDATE tu_khoa SET so_ket_qua=so_ket_qua+1 WHERE tu=? AND so_lan_dung=0", tu)
            n += 1
        except Exception:
            pass
    return n

def nudge_nguon_due(SO, wins, limit=24):
    """When moi=0, force a batch of sources due — prefer signal platforms + never-harvested."""
    rows = SO.nhieu(
        "SELECT ma, lan_cuoi, chu_ky_giay, thu_hoach, loi_lien_tuc, trang_thai FROM nguon WHERE trang_thai='BAT'"
    ) or []
    now = time.time()
    scored = []
    win_l = [w.lower() for w in wins]
    for r in rows:
        ma = r["ma"]
        ml = ma.lower()
        pref = 0
        if any(s in ml for s in SIGNAL_PREF):
            pref += 5
        if any(w in ml for w in win_l if len(w) >= 3):
            pref += 3
        if (r.get("thu_hoach") or 0) == 0:
            pref += 2
        if (r.get("loi_lien_tuc") or 0) >= 3:
            pref -= 4
        scored.append((pref, ma))
    scored.sort(reverse=True)
    picked = [ma for pref, ma in scored if pref > 0][:limit]
    if not picked:
        picked = [ma for _, ma in scored[:limit]]
    for ma in picked:
        SO.chay("UPDATE nguon SET lan_cuoi=?, loi_lien_tuc=0 WHERE ma=?", now - 10**9, ma)
    return picked

def quet_nguon_them(force_ep=False):
    """Scan config/nguon_seeker.json sources; tolerate meta keys without cach."""
    try:
        from nhan import nguon_seeker as NS
        import seeker_quet_nguon as SQN
        ds = NS.nap()
        if isinstance(ds, dict) and "nguon" in ds and isinstance(ds["nguon"], dict):
            ds = ds["nguon"]
        clean = {ma: s for ma, s in (ds or {}).items() if isinstance(s, dict) and "cach" in s}
        if not clean:
            return {"loi": "no_sources_with_cach", "keys": list((ds or {}))[:8]}
        _orig = NS.nap
        NS.nap = lambda: clean
        try:
            rc = SQN.main(["--ep"])
        finally:
            NS.nap = _orig
        return {"rc": rc, "nguon": len(clean)}
    except Exception as e:
        return {"loi": "%s: %s" % (type(e).__name__, e)}

def main():
    for p in (RUN, RUN/"tmp", RUN/"reports", RUN/"logs"):
        p.mkdir(parents=True, exist_ok=True)
    (RUN / "sk_started_epoch.txt").write_text(str(time.time()), encoding="utf-8")
    ghi("=== SEEKER-only start pid=%s workers=%s cpu_limit=%s ===" % (
        os.getpid(), os.environ.get("BRAIN_MAX_WORKERS"), os.environ.get("BRAIN_CPU_LIMIT")))
    import nhan.so as SO
    SO.DB = Path(os.environ["BRAIN_SO"])
    SO.khoi_tao()
    from tru import seeker as SK
    vong = 0
    tong_moi = 0
    rates = []
    last_quet_nguon = 0.0
    moi_zero_streak = 0
    while not qua_gio():
        vong += 1
        wins = doc_bai_hoc_wins()
        try:
            if vong == 1 or moi_zero_streak >= 1:
                nk = nap_tu_khoa_bai_hoc(SO, wins)
                ghi("bai_hoc tu_khoa nap=%s wins=%s" % (nk, wins[:8]))
            if moi_zero_streak >= 1:
                picked = nudge_nguon_due(SO, wins, limit=28)
                ghi("nudge nguon due n=%s sample=%s" % (len(picked), picked[:8]))
            t0 = time.time()
            ghi("SEEKER vong=%d bat dau bai_hoc_wins=%s" % (vong, wins[:8]))
            sk = SK.mot_luot(ngan_sach_giay=480)
            dt = max(0.001, time.time() - t0)
            moi = 0
            if isinstance(sk, dict):
                moi = int(sk.get("tai_lieu_moi") or sk.get("moi") or 0)
                doc = sk.get("DOC") or {}
                art = int(doc.get("artifact_moi") or 0)
                if moi == 0 and art > 0:
                    moi = art
            tong_moi += moi
            ipm = moi / (dt / 60.0)
            rates.append(ipm)
            if moi <= 0:
                moi_zero_streak += 1
            else:
                moi_zero_streak = 0
            st = {
                "vong": vong, "dt": round(dt,1), "moi": moi, "tong_moi": tong_moi,
                "items_per_min": round(ipm,2),
                "items_per_min_avg": round(sum(rates)/len(rates),2),
                "bai_hoc_wins": wins[:20],
                "moi_zero_streak": moi_zero_streak,
                "pid": os.getpid(), "luc": time.strftime("%Y-%m-%d %H:%M:%S"),
                "workers": os.environ.get("BRAIN_MAX_WORKERS"),
            }
            (RUN / "sk_status.json").write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
            (RUN / "last_seeker.json").write_text(
                json.dumps(sk, ensure_ascii=False, indent=1, default=str)[:25000], encoding="utf-8")
            ghi("SEEKER vong=%d xong dt=%.1fs moi=%s ipm=%.2f tong=%s zero_streak=%s" % (
                vong, dt, moi, ipm, tong_moi, moi_zero_streak))
        except Exception as e:
            ghi("SEEKER LOI: %s: %s" % (type(e).__name__, e))
            ghi(traceback.format_exc()[-2500:])

        gap = 900 if moi_zero_streak >= 2 else 2700
        if time.time() - last_quet_nguon > gap:
            try:
                ghi("QUET_NGUON them bat dau force_ep=%s" % (moi_zero_streak >= 1))
                t1 = time.time()
                r = quet_nguon_them(force_ep=True)
                ghi("QUET_NGUON xong dt=%.1fs r=%s" % (time.time()-t1, r))
                last_quet_nguon = time.time()
            except Exception as e:
                ghi("QUET_NGUON LOI: %s" % e)
                last_quet_nguon = time.time()

        time.sleep(5)
    ghi("=== SEEKER-only stop tong_moi=%s ===" % tong_moi)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
