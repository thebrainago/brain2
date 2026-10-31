# -*- coding: utf-8 -*-
"""QUANTLAB-only loop: high CPU scan, export PASS to de_xuat_mt5.jsonl."""
from __future__ import annotations
import json, os, sys, time, traceback
from pathlib import Path
from datetime import datetime

RUN = Path(r"E:\brain2_grok_seeker_run")
LAB = Path(r"E:\brain2_grok")
LOG = RUN / "quantlab_only.log"
DEXUAT = RUN / "de_xuat_mt5.jsonl"
STOP = RUN / "DUNG_LAI"
BAI_HOC = LAB / "data" / "bai_hoc.json"

os.environ["BRAIN_SO"] = str(RUN / "nao.db")
os.environ.setdefault("BRAIN_DATA", str(LAB / "data"))
os.environ.setdefault("BRAIN_CACHE", str(RUN / "data_khung"))
os.environ["BRAIN_LLM_PROVIDER"] = "hang_cho"
# library caps at cpu_count//2 (=10 on 20-thread); 10 ~= half cores, leave room for MT5+SEEKER
os.environ["BRAIN_QUET_TIEN_TRINH"] = os.environ.get("BRAIN_QUET_TIEN_TRINH", "8")
os.environ["BRAIN_DIEU_TOC"] = "tat"
os.environ["TEMP"] = str(RUN / "tmp")
os.environ["TMP"] = str(RUN / "tmp")
os.environ["TMPDIR"] = str(RUN / "tmp")

sys.path.insert(0, str(LAB))
os.chdir(str(LAB))

def ghi(m):
    d = time.strftime("%Y-%m-%d %H:%M:%S ") + m
    try:
        LOG.open("a", encoding="utf-8").write(d + "\n")
    except Exception:
        pass
    print(d, flush=True)

def doc_bai_hoc():
    if not BAI_HOC.exists():
        return {"families_win": [], "raw": None}
    try:
        raw = json.loads(BAI_HOC.read_text(encoding="utf-8"))
    except Exception:
        return {"families_win": [], "raw": None}
    wins = []
    if isinstance(raw, dict):
        for k in ("thang", "winning", "win", "families_win", "gia_dinh_thang", "uu_tien"):
            v = raw.get(k)
            if isinstance(v, list):
                wins.extend([str(x) for x in v])
            elif isinstance(v, dict):
                wins.extend([str(a) for a, b in v.items() if b])
        for k, v in raw.items():
            if isinstance(v, dict) and (v.get("thang") or v.get("win")):
                wins.append(str(k))
    return {"families_win": sorted(set(wins)), "raw_keys": list(raw)[:20] if isinstance(raw, dict) else type(raw).__name__}

def xuat_pass(SO):
    da = set()
    if DEXUAT.exists():
        for line in DEXUAT.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
                da.add(o.get("gt_ma") or o.get("ten") or o.get("the_id"))
            except Exception:
                pass
    rows = SO.nhieu(
        "SELECT k.gt_ma, k.verdict, k.chi_so, k.luc, g.tai_san, g.khung, g.co_che, "
        "g.template, g.tham_so, g.ho FROM ket_qua k "
        "LEFT JOIN gia_thuyet g ON g.ma=k.gt_ma "
        "WHERE k.superseded_by IS NULL AND k.verdict IN ('PASS','UNG_VIEN','CO_CO_CHE') "
        "ORDER BY k.id"
    ) or []
    bh = doc_bai_hoc()
    wins = set(x.lower() for x in bh["families_win"])
    them = 0
    with DEXUAT.open("a", encoding="utf-8") as f:
        for r in rows:
            ma = r.get("gt_ma")
            if not ma or ma in da:
                continue
            try:
                cs = json.loads(r["chi_so"] or "{}") if isinstance(r.get("chi_so"), str) else (r.get("chi_so") or {})
            except Exception:
                cs = {}
            he = (cs.get("he") if isinstance(cs, dict) else None) or cs or {}
            if not isinstance(he, dict):
                he = {}
            ho = (r.get("ho") or r.get("co_che") or r.get("template") or "")
            uu = 800 if str(ho).lower() in wins or any(w in str(ho).lower() for w in wins) else 500
            job = {
                "nguon": "seeker_quantlab_run",
                "pha": "QL_" + str(r.get("verdict") or "PASS"),
                "ten": ma, "gt_ma": ma, "the_id": ma,
                "ma": r.get("tai_san") or "", "tf": r.get("khung") or "",
                "san": "XM", "tien": "USD", "von": 10000, "diem": 10000.0,
                "don_bay": 500, "demo_account": "345930355", "live_cam": "342418441",
                "ea": "QL_PYTHON", "co_che": r.get("co_che"), "template": r.get("template"),
                "tham_so": r.get("tham_so"), "ho": r.get("ho"),
                "python": {
                    "lai_pct_nam": he.get("cagr") or he.get("tong_lai_pct"),
                    "sut_giam_pct": he.get("sut_giam_pct") or he.get("max_dd_pct"),
                    "sharpe": he.get("sharpe"), "so_lenh": he.get("so_lenh"),
                },
                "verdict": r.get("verdict"), "luc_ql": r.get("luc"),
                "uu_tien": uu, "hoan_may_nha": False,
                "bai_hoc_uu_tien": bool(uu >= 800),
                "ghi_chu": "isolated QL PASS; tester pickup later; not appended to live hang_cho",
            }
            f.write(json.dumps(job, ensure_ascii=False, default=str) + "\n")
            da.add(ma)
            them += 1
    return them

def qua_gio():
    if STOP.exists():
        try:
            started = float((RUN / "ql_started_epoch.txt").read_text().strip())
        except Exception:
            return True
        return (time.time() - started) > 120
    now = datetime.now()
    if (now.hour, now.minute) >= (8, 0):
        try:
            started = float((RUN / "ql_started_epoch.txt").read_text().strip())
        except Exception:
            return False
        return (time.time() - started) > 1800
    return False

def main():
    for p in (RUN, RUN/"tmp", RUN/"reports", RUN/"logs"):
        p.mkdir(parents=True, exist_ok=True)
    (RUN / "ql_started_epoch.txt").write_text(str(time.time()), encoding="utf-8")
    ghi("=== QUANTLAB-only start pid=%s QUET=%s ===" % (os.getpid(), os.environ.get("BRAIN_QUET_TIEN_TRINH")))
    import nhan.so as SO
    SO.DB = Path(os.environ["BRAIN_SO"])
    SO.khoi_tao()
    from tru import quantlab as QL
    rep = RUN / "reports"
    QL.REPORTS = rep
    QL.PLAN_DIR = rep / "quant_plans"
    QL.PHEU_CURSOR = rep / "pheu_cursor.json"
    QL.CANDIDATE_CURSOR = rep / "quantlab_candidate_cursor.json"
    QL.AUTONOMOUS_PROGRESS = rep / "quantlab_autonomous_progress.json"
    QL.TIEN_DO = rep / "quantlab_tien_do.json"
    QL.PLAN_DIR.mkdir(parents=True, exist_ok=True)
    vong = 0
    t_rates = []
    tong_kham = 0
    tong_pass = 0
    tong_xuat = 0
    t_wall0 = time.time()
    while not qua_gio():
        vong += 1
        bh = doc_bai_hoc()
        try:
            t0 = time.time()
            ghi("QL vong=%d bat dau bai_hoc_wins=%s" % (vong, bh.get("families_win")[:8]))
            ql = QL.mot_luot(ngan_sach_giay=900)
            dt = max(0.001, time.time() - t0)
            pas = int((ql or {}).get("pass") or 0) if isinstance(ql, dict) else 0
            kham = int((ql or {}).get("kham_pha") or 0) if isinstance(ql, dict) else 0
            xac = int((ql or {}).get("xac_nhan") or 0) if isinstance(ql, dict) else 0
            them = xuat_pass(SO)
            tong_kham += kham
            tong_pass += pas
            tong_xuat += them
            # jobs/hour: hypotheses scanned (kham_pha) + confirmations + exports this cycle
            jph = (kham + xac + pas + them) / (dt / 3600.0)
            t_rates.append(jph)
            wall_h = max(0.001, (time.time() - t_wall0) / 3600.0)
            st = {
                "vong": vong, "dt": round(dt,1), "pass": pas, "kham_pha": kham, "xac_nhan": xac,
                "xuat_them": them, "tong_kham": tong_kham, "tong_pass": tong_pass, "tong_xuat": tong_xuat,
                "jobs_per_hour_proxy": round(jph,1),
                "jobs_per_hour_avg": round(sum(t_rates)/len(t_rates),1),
                "jobs_per_hour_wall": round((tong_kham + tong_pass + tong_xuat) / wall_h, 1),
                "bai_hoc_wins": bh.get("families_win")[:20],
                "pid": os.getpid(), "luc": time.strftime("%Y-%m-%d %H:%M:%S"),
                "quet_workers": os.environ.get("BRAIN_QUET_TIEN_TRINH"),
            }
            (RUN / "ql_status.json").write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
            (RUN / "last_quantlab.json").write_text(json.dumps(ql, ensure_ascii=False, indent=1, default=str)[:25000], encoding="utf-8")
            ghi("QL vong=%d xong dt=%.1fs pass=%s kham=%s xac=%s xuat=%s jph=%.1f wall_jph=%.1f" % (
                vong, dt, pas, kham, xac, them, jph, st["jobs_per_hour_wall"]))
        except Exception as e:
            ghi("QL LOI: %s: %s" % (type(e).__name__, e))
            ghi(traceback.format_exc()[-2500:])
        time.sleep(3)
    ghi("=== QUANTLAB-only stop tong_kham=%s tong_pass=%s tong_xuat=%s ===" % (tong_kham, tong_pass, tong_xuat))
    return 0

if __name__ == "__main__":
    import multiprocessing as mp
    mp.freeze_support()
    raise SystemExit(main())


