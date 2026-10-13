# -*- coding: utf-8 -*-
"""chay_lien_tuc.py - CHAY MT5 LIEN TUC tren may nha den han (vong 27). BACKTEST, khong phai tien that.

Moi vong 15 s: do muc (dieu_phoi_song_song) -> so slot; slot trong -> lay viec (sinh_viec, khong bao gio can) -> ghi .set + ini
-> terminal portable /config (ShutdownTerminal=1, uu tien Idle) -> xong thi doc bao cao, ghi so cai (Holm).
Slot: D:\\mt5_tester\\p1,p2, E:\\mt5_tester\\p3,p4 (KHONG o C:). Dung nhanh: slot hong 2 lan lien (<90 s, khong bao cao) -> bo slot.
Chay:  python mt5tools/chay_lien_tuc.py --den 22:10 [--muc MAX]
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dieu_phoi_song_song as DP  # noqa: E402
import sinh_viec as SV  # noqa: E402

SLOT = [r"D:\mt5_tester\p1", r"D:\mt5_tester\p2", r"E:\mt5_tester\p3", r"E:\mt5_tester\p4"]
REP = Path(r"D:\mt5_lien_tuc\rep")
LOG = Path(r"D:\mt5_lien_tuc\chay.log")
GOC_SET = Path(__file__).resolve().parent.parent / "ea_demo"


def log(s: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + s + "\n")


def doc_htm(p: Path) -> dict:
    t = p.read_bytes().decode("utf-16", errors="ignore")
    cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", t, re.S)]

    def g(k):
        try:
            return cells[cells.index(k) + 1]
        except ValueError:
            return None

    def num(x):
        try:
            return float(x.replace(" ", "").replace("\xa0", "").split("(")[0])
        except Exception:
            return None
    r = {"net": num(g("Total Net Profit:")), "pf": num(g("Profit Factor:")), "lenh": num(g("Total Trades:")),
         "dd": g("Equity Drawdown Maximal:"), "chat_luong": g("History Quality:")}
    i = t.find(">Deals<"); loi = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", t[i:], re.S):
        c = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(c) >= 13 and c[4] == "out":
            try:
                loi.append(float(c[10].replace(" ", "")) + float(c[9].replace(" ", "")) + float(c[8].replace(" ", "")))
            except Exception:
                pass
    r["p"] = round(SV.p_gia_tri(loi), 6)
    return r


def phong(slot: str, v: dict, ten: str) -> subprocess.Popen:
    ea = "BRAIN_V24_%s_Trail_D1" % v["ea"]
    goc = (GOC_SET / (ea + ".set")).read_text(encoding="utf-8")
    Path(slot, "MQL5", "Profiles", "Tester").mkdir(parents=True, exist_ok=True)
    Path(slot, "MQL5", "Profiles", "Tester", ten + ".set").write_text(SV.file_set(v, goc), encoding="ascii")
    fr, to = SV.IS if v["pha"] == "IS" else SV.OOS
    ini = Path(slot, ten + ".ini")
    ini.write_text("[Tester]\nExpert=BRAIN\\%s.ex5\nExpertParameters=%s.set\nSymbol=%s\nPeriod=%s\nModel=4\nExecutionMode=0\n"
                   "Optimization=0\nFromDate=%s\nToDate=%s\nForwardMode=0\nDeposit=10000\nCurrency=USD\nLeverage=30\n"
                   "Report=%s\nReplaceReport=1\nShutdownTerminal=1\nVisual=0\n" % (ea, ten, v["ma"], v["tf"], fr, to, ten), encoding="ascii")
    return subprocess.Popen([slot + r"\terminal64.exe", "/portable", "/config:" + str(ini)], creationflags=0x00000040)  # IDLE_PRIORITY_CLASS


def ha_uu_tien():
    try:
        import psutil
        for p in psutil.process_iter(["name", "exe"]):
            if (p.info["name"] or "").lower() in ("terminal64.exe", "metatester64.exe") and "mt5_tester" in (p.info["exe"] or ""):
                if p.nice() != psutil.IDLE_PRIORITY_CLASS:
                    p.nice(psutil.IDLE_PRIORITY_CLASS)
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--den", default="22:10"); ap.add_argument("--muc"); a = ap.parse_args()
    hh, mm = map(int, a.den.split(":")); han = dt.datetime.now().replace(hour=hh, minute=mm, second=0)
    REP.mkdir(parents=True, exist_ok=True)
    chay, hong, bo = {}, {}, set()
    log("BAT DAU, han %s" % han)
    while True:
        now = dt.datetime.now()
        d = DP.do_may(1.0)
        muc = DP.chon_muc(d["game"], d["toan_man_hinh"], d["cpu_nguoi_dung"], a.muc if not (d["game"] or d["toan_man_hinh"]) else None)
        n = DP.so_slot_mt5(muc)
        for s, (pr, v, ten, t0) in list(chay.items()):
            if pr.poll() is None:
                continue
            del chay[s]
            f = Path(s, ten + ".htm")
            if f.exists():
                r = doc_htm(f); shutil.move(str(f), str(REP / f.name)); hong[s] = 0
                rec = {k: v[k] for k in ("ea", "ma", "tf", "ts", "pha")}; rec.update(r, file=f.name, giay=int(time.time() - t0), luc=now.isoformat(timespec="seconds"))
                SV.ghi(rec)
                log("XONG %s %s net=%s lenh=%s pf=%s %ss" % (ten, v["pha"], r["net"], r["lenh"], r["pf"], rec["giay"]))
            else:
                ngan = time.time() - t0 < 90
                hong[s] = hong.get(s, 0) + 1
                rec = {k: v[k] for k in ("ea", "ma", "tf", "ts", "pha")}; rec.update(loi="khong_bao_cao", giay=int(time.time() - t0), luc=now.isoformat(timespec="seconds"))
                SV.ghi(rec)
                log("HONG %s (lan %d)" % (ten, hong[s]))
                if ngan and hong[s] >= 2:
                    bo.add(s); log("BO SLOT %s (fail-fast)" % s)
        if now >= han:
            if not chay:
                break
            time.sleep(15); continue
        trong = [s for s in SLOT[:n] if s not in chay and s not in bo and Path(s, "terminal64.exe").exists()]
        if trong:
            dang = {SV.khoa(v) for _, v, _, _ in chay.values()}
            for s, v in zip(trong, SV.lay_viec(len(trong), dang_chay=dang)):
                ten = "lt_%s_%s_%s_%s_%s" % (v["ea"], re.sub(r"[^A-Za-z0-9]", "", v["ma"]), v["tf"], v["pha"], format(abs(hash(SV.khoa(v))) % 10**8, "08d"))
                chay[s] = (phong(s, v, ten), v, ten, time.time())
                log("PHONG %s %s muc=%s %s" % (ten, s, muc, json.dumps(v["ts"])))
                time.sleep(3)
        ha_uu_tien()
        time.sleep(15)
    log("HET HAN - DUNG. %s" % json.dumps(SV.tong_ket(), ensure_ascii=False)[:400])


if __name__ == "__main__":
    main()
