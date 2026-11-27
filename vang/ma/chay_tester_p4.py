# -*- coding: utf-8 -*-
"""Chay Strategy Tester tick that tren dung slot p4, mot test mot luc.
Khong dung p3 (bases dung chung). Khong dung --song-song. Khong dung g3/g12.
Giu RAM trong >= 6 GB. Chi giet PID do script nay phong.
"""
from __future__ import annotations
import json, os, shutil, subprocess, sys, time
from pathlib import Path

SLOT = Path(r"E:\mt5_tester\p4")
OUT  = Path(r"E:\brain2_tmp\vang\mt5")
RAM_MIN_GB = 6.0
CHO_GIAY = 4 * 3600  # toi da 4 gio / test
MA = "GOLD.i#"

def log(s):
    print(s, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "chay_tester.log").open("a", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + s + "\n")

def ram_trong_gb():
    import ctypes
    class M(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = M(); m.dwLength = ctypes.sizeof(M)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 1024**3

def dat_maxbars(slot: Path, n=50000):
    f = slot / "config" / "common.ini"
    if not f.exists():
        return "khong co common.ini"
    raw = f.read_bytes()
    enc = "utf-16" if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else "utf-8"
    try:
        t = raw.decode(enc)
    except Exception:
        t = raw.decode("utf-8", errors="replace"); enc = "utf-8"
    if "MaxBars=" in t:
        import re
        t2 = re.sub(r"MaxBars=\d+", "MaxBars=%d" % n, t)
    else:
        if "[Charts]" in t:
            t2 = t.replace("[Charts]", "[Charts]\nMaxBars=%d" % n, 1)
        else:
            t2 = t + "\n[Charts]\nMaxBars=%d\n" % n
    if t2 != t:
        f.write_bytes(t2.encode(enc))
        return "dat MaxBars=%d (%s)" % (n, enc)
    return "MaxBars da dung"

def bien_dich(mq: Path):
    me = SLOT / "metaeditor64.exe"
    ex5 = mq.with_suffix(".ex5")
    cu = ex5.stat().st_mtime if ex5.exists() else 0.0
    logf = mq.with_suffix(".log")
    subprocess.Popen([str(me), "/portable", "/compile:" + mq.name, "/log:" + logf.name],
                     cwd=str(mq.parent), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    het = time.time() + 180
    while time.time() < het:
        if ex5.exists() and ex5.stat().st_mtime > cu:
            return ""
        time.sleep(1)
    duoi = ""
    if logf.exists():
        duoi = logf.read_bytes().decode("utf-16", errors="ignore")[-600:]
    return "bien dich hong: " + duoi

def doc_htm(p: Path) -> dict:
    import html, re
    t = p.read_bytes().decode("utf-16", errors="ignore")
    cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", t, re.S)]
    def g(k):
        try:
            return cells[cells.index(k) + 1]
        except ValueError:
            # thu ban dich
            for alt in (k, k.replace(":", ""), k.lower()):
                if alt in cells:
                    return cells[cells.index(alt) + 1]
            return None
    def num(x):
        if x is None: return None
        try:
            return float(str(x).replace(" ", "").replace("\xa0", "").replace("%","").split("(")[0].replace(",", ""))
        except Exception:
            return None
    keys = {
        "net": ("Total Net Profit:", "Total net profit:"),
        "pf": ("Profit Factor:", "Profit factor:"),
        "lenh": ("Total Trades:", "Total trades:"),
        "dd": ("Equity Drawdown Maximal:", "Balance Drawdown Maximal:", "Equity drawdown maximal:"),
        "chat_luong": ("History Quality:", "History quality:"),
        "symbol_bc": ("Symbol:",),
        "ky_bc": ("Period:",),
        "thang": ("Profit Trades (% of total):",),
    }
    r = {}
    for k, alts in keys.items():
        v = None
        for a in alts:
            v = g(a)
            if v is not None: break
        r[k] = v
    r["net"] = num(r["net"]); r["pf"] = num(r["pf"]); r["lenh"] = num(r["lenh"])
    # DD often "1234.56 (12.34%)"
    dd = r.get("dd") or ""
    m = None
    import re as _re
    m = _re.search(r"\(([\d\s.,]+)\s*%\)", str(dd))
    r["dd_pct"] = num(m.group(1))/100.0 if m else None
    r["dd_raw"] = dd
    r["chat_luong"] = r.get("chat_luong")
    return r

def cagr(von, net, nam):
    if not nam or von is None or net is None or von + net <= 0:
        return None
    return ( (von + net) / von ) ** (1.0 / nam) - 1.0

def giet_cay(pr):
    # chi cay do minh phong, theo PID
    try:
        subprocess.run(["taskkill", "/PID", str(pr.pid), "/T", "/F"], capture_output=True)
    except Exception as e:
        log("taskkill loi: %s" % e)

def viet_ini_set(ten, ea_ex5, params, tu, den, von=10000):
    (SLOT / "MQL5" / "Profiles" / "Tester").mkdir(parents=True, exist_ok=True)
    setp = SLOT / "MQL5" / "Profiles" / "Tester" / (ten + ".set")
    setp.write_text("\n".join("%s=%s" % (k, v) for k, v in params.items()) + "\n", encoding="ascii")
    ini = (
        "[Tester]\n"
        "Expert=VANG\\%s\n"
        "ExpertParameters=%s.set\n"
        "Symbol=%s\n"
        "Period=H1\n"
        "Model=4\n"
        "ExecutionMode=0\n"
        "Optimization=0\n"
        "OptimizationCriterion=0\n"
        "FromDate=%s\n"
        "ToDate=%s\n"
        "ForwardMode=0\n"
        "Deposit=%d\n"
        "Currency=USD\n"
        "Leverage=1:500\n"
        "Report=%s\n"
        "ReplaceReport=1\n"
        "ShutdownTerminal=1\n"
        "Visual=0\n"
    ) % (ea_ex5, ten, MA, tu, den, von, ten)
    inip = SLOT / (ten + ".ini")
    inip.write_text(ini, encoding="ascii")
    return inip

def chay_mot(ten, ea_ex5, params, tu, den, von=10000):
    ram = ram_trong_gb()
    log("RAM trong %.2f GB truoc test %s" % (ram, ten))
    if ram < RAM_MIN_GB + 5:
        return {"ten": ten, "loi": "RAM trong %.2f GB, can >= %.1f" % (ram, RAM_MIN_GB + 5)}
    # xoa bao cao cu
    for duoi in (".htm", ".html", ".xml", ".png"):
        p = SLOT / (ten + duoi)
        if p.exists():
            p.unlink()
    inip = viet_ini_set(ten, ea_ex5, params, tu, den, von)
    t0 = time.time()
    pr = subprocess.Popen(
        [str(SLOT / "terminal64.exe"), "/portable", "/config:" + str(inip)],
        cwd=str(SLOT),
        creationflags=0x00000040,  # IDLE_PRIORITY_CLASS
    )
    log("phong PID %d %s %s..%s" % (pr.pid, ten, tu, den))
    try:
        pr.wait(timeout=CHO_GIAY)
    except subprocess.TimeoutExpired:
        giet_cay(pr)
        return {"ten": ten, "loi": "qua_gio", "giay": int(time.time()-t0), "pid": pr.pid}
    giay = int(time.time()-t0)
    f = SLOT / (ten + ".htm")
    if not f.exists():
        # mot so ban ghi .html
        f2 = SLOT / (ten + ".html")
        f = f2 if f2.exists() else f
    if not f.exists() or f.stat().st_mtime < t0 - 5:
        return {"ten": ten, "loi": "khong_bao_cao", "giay": giay, "pid": pr.pid}
    r = doc_htm(f)
    # bao cao rong (Period 1970 / 0 bars) = test khong chay
    ky = str(r.get("ky_bc") or "")
    if "1970" in ky or (r.get("lenh") in (0, 0.0, None) and r.get("net") in (0, 0.0, None) and "real ticks" not in str(r.get("chat_luong") or "").lower()):
        raw = f.read_bytes().decode("utf-16", errors="ignore")
        if "1970.01.01" in raw or "Bars:" in raw and ">0<" in raw.replace(" ",""):
            return {"ten": ten, "loi": "bao_cao_rong", "giay": giay, "pid": pr.pid, "chat_luong": r.get("chat_luong"), "ky_bc": ky}
    nam = max(( __import__("datetime").datetime.strptime(den, "%Y.%m.%d") -
                __import__("datetime").datetime.strptime(tu, "%Y.%m.%d") ).days / 365.25, 1e-6)
    r["cagr"] = cagr(von, r.get("net"), nam)
    r["nam"] = nam
    r["ten"] = ten
    r["tu"] = tu
    r["den"] = den
    r["giay"] = giay
    r["von"] = von
    r["ma"] = MA
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, OUT / f.name)
    (OUT / (ten + ".json")).write_text(json.dumps(r, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    log("xong %s giay=%d net=%s cagr=%s dd=%s lenh=%s pf=%s quality=%s" % (
        ten, giay, r.get("net"), r.get("cagr"), r.get("dd_pct"), r.get("lenh"), r.get("pf"), r.get("chat_luong")))
    return r

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if ram_trong_gb() < RAM_MIN_GB + 5:
        log("DUNG: RAM trong thap"); return 2
    log(dat_maxbars(SLOT))
    src = Path(r"C:\Users\DUNG\AppData\Local\Temp\vang_ea")
    dest = SLOT / "MQL5" / "Experts" / "VANG"
    dest.mkdir(parents=True, exist_ok=True)
    for ten in ("VANG_DonchianEMA.mq5", "VANG_LuoiEMA.mq5"):
        mq = dest / ten
        ex5 = mq.with_suffix(".ex5")
        if src.exists() and (src / ten).exists():
            shutil.copy2(src / ten, mq)
        if ex5.exists() and mq.exists() and ex5.stat().st_mtime >= mq.stat().st_mtime:
            log("bo qua bien dich (ex5 da moi) " + ten)
            continue
        loi = bien_dich(mq)
        if loi:
            log(loi); return 3
        log("bien dich ok " + ten)

    hang = []
    # Tick that tren may chi co 2025.08..2026.11 (file .tkc). Chay cua so nay truoc.
    # 202611.tkc moi ~2 MB (thieu), chot ToDate 2026.10.12 trung chuoi Python XM.
    hang.append(("vang_dc_khoi_dong", "VANG_DonchianEMA.ex5", {
        "InpDonchian": 20, "InpEMA": 55, "InpATR": 14, "InpSL_ATR": 2.0, "InpTP_ATR": 4.0,
        "InpRuiRo": 0.02, "InpVonTham": 0, "InpMagic": 2026112701, "InpSlippage": 50,
    }, "2025.10.01", "2026.10.12"))

    hang.append(("vang_dc_tick_202508_202610", "VANG_DonchianEMA.ex5", {
        "InpDonchian": 20, "InpEMA": 55, "InpATR": 14, "InpSL_ATR": 2.0, "InpTP_ATR": 4.0,
        "InpRuiRo": 0.02, "InpVonTham": 0, "InpMagic": 2026112701, "InpSlippage": 50,
    }, "2025.08.01", "2026.10.12"))

    hang.append(("vang_luoi_tick_202508_202610", "VANG_LuoiEMA.ex5", {
        "InpEMA": 55, "InpATR": 14, "InpBuocATR": 1.5, "InpMaxChan": 4,
        "InpTP_ATR": 1.2, "InpSL_ATR": 5.0, "InpLotChan": 0.08,
        "InpMagic": 2026112702, "InpSlippage": 50,
    }, "2025.08.01", "2026.10.12"))

    # Cua so dai: M1 bar 2014-2026 co trong p4, nhung tick that khong co truoc 2025.08.
    # Chi chay khi dat VANG_MT5_DAY_DU=1 (co the tai tick, lau, tốn đĩa).
    if os.environ.get("VANG_MT5_DAY_DU") == "1":
        hang.append(("vang_dc_2018_2026", "VANG_DonchianEMA.ex5", {
            "InpDonchian": 20, "InpEMA": 55, "InpATR": 14, "InpSL_ATR": 2.0, "InpTP_ATR": 4.0,
            "InpRuiRo": 0.02, "InpVonTham": 0, "InpMagic": 2026112701, "InpSlippage": 50,
        }, "2018.01.02", "2026.10.12"))

        hang.append(("vang_dc_2015_2026", "VANG_DonchianEMA.ex5", {
            "InpDonchian": 20, "InpEMA": 55, "InpATR": 14, "InpSL_ATR": 2.0, "InpTP_ATR": 4.0,
            "InpRuiRo": 0.02, "InpVonTham": 0, "InpMagic": 2026112701, "InpSlippage": 50,
        }, "2015.01.02", "2026.10.12"))

        hang.append(("vang_luoi_2018_2026", "VANG_LuoiEMA.ex5", {
            "InpEMA": 55, "InpATR": 14, "InpBuocATR": 1.5, "InpMaxChan": 4,
            "InpTP_ATR": 1.2, "InpSL_ATR": 5.0, "InpLotChan": 0.08,
            "InpMagic": 2026112702, "InpSlippage": 50,
        }, "2018.01.02", "2026.10.12"))

        hang.append(("vang_luoi_2015_2026", "VANG_LuoiEMA.ex5", {
            "InpEMA": 55, "InpATR": 14, "InpBuocATR": 1.5, "InpMaxChan": 4,
            "InpTP_ATR": 1.2, "InpSL_ATR": 5.0, "InpLotChan": 0.09,
            "InpMagic": 2026112702, "InpSlippage": 50,
        }, "2015.01.02", "2026.10.12"))
    else:
        log("bo qua cua so 2015/2018 (chua co tick that truoc 2025.08). Dat VANG_MT5_DAY_DU=1 neu muon chay.")

    kq = []
    for item in hang:
        r = chay_mot(*item)
        if r.get("loi") == "bao_cao_rong":
            log("thu lai 1 lan sau 30s vi bao cao rong: %s" % item[0])
            time.sleep(30)
            r = chay_mot(*item)
        kq.append(r)
        (OUT / "tong_hop.json").write_text(json.dumps(kq, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        if r.get("loi") and r["loi"].startswith("RAM"):
            break
        # nghi ngan, kiem RAM
        time.sleep(20)
        log("RAM sau test %.2f GB" % ram_trong_gb())
    log("HOAN TAT %d test" % len(kq))
    return 0

if __name__ == "__main__":
    sys.exit(main() or 0)
