# -*- coding: utf-8 -*-
"""Chay DON (Optimization=0) cho cac co che qua loc so bo cua chay_lo, doc bang deal trong .htm,
tinh Sharpe nam hoa THEO LENH (mean/std*sqrt(lenh/nam)), PF lenh, TB lenh, %/nam, tap trung top10%.
python chay_don.py --ds don.json   (don.json = [{"ea":..., "i":..}, ...])
"""
import argparse, html, json, math, re, subprocess, time
from pathlib import Path
from chay_lo import TU, DEN

def ini(copy, ea, sym, i):
    p = copy / f"don_{ea}_{i}.ini"
    p.write_text(f"""[Tester]
Expert=EVO\\{ea}.ex5
Symbol={sym}
Period=M15
Model=2
ExecutionMode=0
Optimization=0
FromDate={TU}
ToDate={DEN}
ForwardMode=0
Deposit=10000
Currency=USD
Leverage=1:100
Report=don_{ea}_{i}
ReplaceReport=1
ShutdownTerminal=1
Visual=0

[TesterInputs]
InpMaCoChe={i}
InpDich=0
InpLot=0.1
InpMagic=26090601
InpGioTranh=0
InpChiDemo=true
""", encoding="utf-16")
    return p

def deals(f):
    t = f.read_bytes()
    t = t.decode("utf-16") if t[:2] in (b"\xff\xfe", b"\xfe\xff") else t.decode("utf-8", "ignore")
    k = t.find(">Deals<")
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", t[k:], re.S)
    out, h = [], None
    for r in rows:
        c = [html.unescape(re.sub("<[^>]+>", "", x)).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        if h is None:
            if "Direction" in c: h = {k: j for j, k in enumerate(c)}
            continue
        if len(c) >= len(h) and c[h["Direction"]] in ("out", "in/out"):
            try:
                f = lambda k: float(c[h[k]].replace(" ", "")) if k in h and c[h[k]] else 0.0
                out.append({"t": c[h["Time"]], "pnl": f("Profit") + f("Swap") + f("Commission") + f("Fee")})
            except ValueError:
                pass
    return out

def chi_so(ds, von=10000.0):
    if not ds: return {"lenh": 0}
    x = [d["pnl"] for d in ds]; n = len(x)
    y0 = time.strptime(ds[0]["t"][:10], "%Y.%m.%d"); y1 = time.strptime(ds[-1]["t"][:10], "%Y.%m.%d")
    nam = max((time.mktime(y1) - time.mktime(y0)) / 31557600, 0.5)
    m = sum(x) / n; sd = (sum((v - m) ** 2 for v in x) / max(n - 1, 1)) ** .5
    th = sum(v for v in x if v > 0); tl = -sum(v for v in x if v < 0)
    top = sorted(x, reverse=True)[:max(1, n // 10)]
    nam_lai = {}
    for d in ds: nam_lai[d["t"][:4]] = nam_lai.get(d["t"][:4], 0) + d["pnl"]
    return {"lenh": n, "nam": round(nam, 1), "pf_lenh": round(th / tl, 3) if tl else None,
            "tb_lenh_usd": round(m, 2), "sharpe_nam": round(m / sd * math.sqrt(n / nam), 3) if sd else None,
            "pct_nam_von10k": round(sum(x) / von / nam * 100, 2),
            "top10_pct_lai": round(sum(top) / th * 100, 1) if th else None,
            "nam_duong": f"{sum(1 for v in nam_lai.values() if v > 0)}/{len(nam_lai)}"}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ds"); ap.add_argument("--copy", default=r"E:\mt5_tester\p3")
    ap.add_argument("--goc", default=r"E:\evo_runner"); a = ap.parse_args()
    copy, goc = Path(a.copy), Path(a.goc)
    man = {n["ea"]: n for n in json.loads((goc / "out" / "manifest.json").read_text(encoding="utf-8"))["nhom"]}
    kq = []
    for it in json.loads(Path(a.ds).read_text(encoding="utf-8")):
        ea, i = it["ea"], int(it["i"]); sym = man[ea]["symbol"]
        rep = copy / f"don_{ea}_{i}.htm"; rep.unlink(missing_ok=True)
        p = subprocess.Popen([str(copy / "terminal64.exe"), "/portable", f"/config:{ini(copy, ea, sym, i)}"])
        try: p.wait(timeout=1200)
        except subprocess.TimeoutExpired: p.kill()
        r = dict(it, symbol=sym, ten=man[ea]["co_che"][i]["ten"], kd=man[ea]["co_che"][i].get("kd"))
        r.update(chi_so(deals(rep)) if rep.exists() else {"loi": "khong co htm"})
        kq.append(r); print(json.dumps(r, ensure_ascii=False), flush=True)
        (goc / "ket_qua_don.json").write_text(json.dumps(kq, ensure_ascii=False, indent=1), encoding="utf-8")

if __name__ == "__main__":
    main()
