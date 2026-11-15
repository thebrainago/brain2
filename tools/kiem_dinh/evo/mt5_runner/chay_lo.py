# -*- coding: utf-8 -*-
"""Chay lo EA (sinh boi sinh_lo.py) qua MT5 Strategy Tester tren may nha, song song nhieu ban copy.

python chay_lo.py --goc E:\\evo_runner --copy E:\\mt5_tester\\p3,E:\\mt5_tester\\p4,E:\\mt5_tester\\p5
- Bien dich MOT lan trong ban copy dau, chep .ex5 sang cac ban khac.
- Moi EA = 1 optimization tren InpMaCoChe (Model=2 open prices, chu ky M15, 2016-01-01 -> nay).
- Doc .xml optimization -> ket_qua/<ea>.json. Khong dang nhap bang mat khau: dung tai khoan da luu
  trong ban copy (XM DEMO). Chi tester, khong dat lenh that.
"""
import argparse, json, os, queue, re, shutil, subprocess, threading, time
import xml.etree.ElementTree as ET
from pathlib import Path

TU, DEN = "2016.01.01", "2026.11.13"


def bien_dich(copy: Path, mq5: Path) -> str:
    dich = copy / "MQL5" / "Experts" / "EVO"; dich.mkdir(parents=True, exist_ok=True)
    src = dich / mq5.name; shutil.copy2(mq5, src)
    ex5 = src.with_suffix(".ex5"); log = src.with_suffix(".log")
    cu = ex5.stat().st_mtime if ex5.exists() else 0
    subprocess.run([str(copy / "MetaEditor64.exe"), "/portable", f"/compile:{src}", f"/log:{log}"], timeout=300)
    for _ in range(60):
        if ex5.exists() and ex5.stat().st_mtime > cu: break
        time.sleep(1)
    van = log.read_text(encoding="utf-16", errors="ignore") if log.exists() else ""
    m = re.search(r"(\d+) errors?", van)
    if not ex5.exists() or ex5.stat().st_mtime <= cu or (m and int(m.group(1)) > 0):
        return "LOI bien dich: " + " | ".join([x for x in van.splitlines() if "error" in x][:4])
    return ""


def viet_ini(copy: Path, nh: dict) -> Path:
    n = len(nh["co_che"]); ea = nh["ea"]
    ini = copy / f"lo_{ea}.ini"
    ini.write_text(f"""[Tester]
Expert=EVO\\{ea}.ex5
Symbol={nh['symbol']}
Period=M15
Model=2
ExecutionMode=0
Optimization=1
OptimizationCriterion=0
FromDate={TU}
ToDate={DEN}
ForwardMode=0
Deposit=10000
Currency=USD
Leverage=1:100
Report=lo_{ea}
ReplaceReport=1
ShutdownTerminal=1
Visual=0

[TesterInputs]
InpMaCoChe=0||0||1||{n - 1}||Y
InpDich=0||0||0||0||N
InpLot=0.1||0.1||0||0||N
InpMagic=26090601||26090601||0||0||N
InpGioTranh=0||0||0||0||N
InpChiDemo=true||false||0||true||N
""", encoding="utf-16")
    return ini


def doc_xml(f: Path) -> list:
    ns = {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}
    root = ET.parse(f).getroot()
    rows = root.findall(".//ss:Row", ns)
    ds = [[(c.find("ss:Data", ns).text if c.find("ss:Data", ns) is not None else "") for c in r.findall("ss:Cell", ns)] for r in rows]
    if not ds: return []
    h = ds[0]
    return [dict(zip(h, r)) for r in ds[1:]]


def so(x, d=0.0):
    try: return float(str(x).replace(",", ""))
    except Exception: return d


def chay_mot(copy: Path, nh: dict, ket: Path, tran: int = 2400) -> dict:
    ea = nh["ea"]; ini = viet_ini(copy, nh)
    for h in (".xml", ".htm"):
        (copy / f"lo_{ea}{h}").unlink(missing_ok=True)
    t0 = time.time()
    p = subprocess.Popen([str(copy / "terminal64.exe"), "/portable", f"/config:{ini}"])
    try:
        p.wait(timeout=tran)
    except subprocess.TimeoutExpired:
        p.kill(); return {"ea": ea, "loi": f"qua {tran}s"}
    giay = round(time.time() - t0)
    f = copy / f"lo_{ea}.xml"
    if not f.exists():
        return {"ea": ea, "loi": "khong co xml", "giay": giay}
    out = []
    for d in doc_xml(f):
        i = int(so(d.get("InpMaCoChe"), -1))
        if not 0 <= i < len(nh["co_che"]): continue
        cc = nh["co_che"][i]
        out.append({"i": i, "ten": cc["ten"], "kd": cc.get("kd"), "template": cc.get("template"),
                    "lenh": int(so(d.get("Trades"))), "lai": so(d.get("Profit")), "pf": so(d.get("Profit Factor")),
                    "sharpe_mt5": so(d.get("Sharpe Ratio")), "ky_vong": so(d.get("Expected Payoff")),
                    "dd_pct": so(d.get("Equity DD %")), "hs_phuc_hoi": so(d.get("Recovery Factor"))})
    r = {"ea": ea, "symbol": nh["symbol"], "khung": nh["khung"], "giay": giay, "tu": TU, "den": DEN,
         "model": "M15 open prices", "ket": sorted(out, key=lambda x: x["i"])}
    if not out: r["loi"] = "xml rong (lich su khong dong bo?)"
    elif all(x["lenh"] == 0 for x in out): r["loi"] = "tat ca 0 lenh - nghi moi truong"
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goc", default=r"E:\evo_runner")
    # CHI MOT ban copy: cac ban dung chung Bases (junction) chay song song -> loi khoa file [32],
    # optimization ra xml rong. Song song chi khi moi ban co Bases rieng.
    ap.add_argument("--copy", default=r"E:\mt5_tester\p3")
    ap.add_argument("--chi", default="")
    a = ap.parse_args()
    goc = Path(a.goc); ket = goc / "ket_qua"; ket.mkdir(exist_ok=True)
    man = json.loads((goc / "out" / "manifest.json").read_text(encoding="utf-8"))
    copies = [Path(x) for x in a.copy.split(",")]
    nhom = [n for n in man["nhom"] if not a.chi or n["ea"] in a.chi.split(",")]
    nhom = [n for n in nhom if not (ket / f"{n['ea']}.json").exists()]
    # bien dich trong ban dau, chep ex5
    c0 = copies[0]; ok = []
    for n in nhom:
        loi = bien_dich(c0, goc / "out" / f"{n['ea']}.mq5")
        if loi:
            (ket / f"{n['ea']}.json").write_text(json.dumps({"ea": n["ea"], "loi": loi}, ensure_ascii=False), encoding="utf-8")
            print(n["ea"], loi, flush=True); continue
        for c in copies[1:]:
            d = c / "MQL5" / "Experts" / "EVO"; d.mkdir(parents=True, exist_ok=True)
            shutil.copy2(c0 / "MQL5" / "Experts" / "EVO" / f"{n['ea']}.ex5", d)
        ok.append(n)
    print("bien dich xong", len(ok), "/", len(nhom), flush=True)
    q = queue.Queue()
    for n in sorted(ok, key=lambda n: -len(n["co_che"])): q.put(n)

    def tho(c):
        while True:
            try: n = q.get_nowait()
            except queue.Empty: return
            r = chay_mot(c, n, ket)
            (ket / f"{n['ea']}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
            print(time.strftime("%H:%M:%S"), c.name, n["ea"], r.get("giay"), r.get("loi", "ok"), len(r.get("ket", [])), flush=True)

    ts = [threading.Thread(target=tho, args=(c,)) for c in copies]
    for t in ts: t.start(); time.sleep(20)
    for t in ts: t.join()
    print("XONG", flush=True)


if __name__ == "__main__":
    main()
