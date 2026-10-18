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
import an_toan_tester as AT  # noqa: E402

SLOT = [r"D:\mt5_tester\p1", r"D:\mt5_tester\p2", r"E:\mt5_tester\p3", r"E:\mt5_tester\p4"]
REP = Path(r"D:\mt5_lien_tuc\rep")
LOG = Path(r"D:\mt5_lien_tuc\chay.log")
GOC_SET = Path(__file__).resolve().parent.parent / "ea_demo"
# Don bay dat cho tester. 18/10/2026: truoc day ghi "Leverage=30" -> tester bo qua, moi bao cao la 1:100.
DON_BAY = 30
# Mot viec chay qua so giay nay thi giet va ghi `qua_gio` (do 18/10: lau nhat 506 s / 630 lan). Truoc day khong co
# han: terminal treo -> `poll()` tra None mai, `ket_thuc` (commit so cai) khong bao gio chay.
HAN_VIEC_GIAY = 1800
HAN_TOI_UU_GIAY = 6 * 3600     # viec Optimization cua ong dan chay lau hon nhieu


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
         "dd": g("Equity Drawdown Maximal:"), "chat_luong": g("History Quality:"), "don_bay_bc": g("Leverage:")}
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


KQ_ONG_DAN = Path(__file__).resolve().parent.parent / "reports" / "ong_dan" / "ket_qua_mt5"


def _ban_ghi(v: dict) -> dict:
    """Khoa so cai + (viec ong dan) nguon/the_id/ten/von de `ong_dan.py doc_mt5` noi ket qua ve the."""
    rec = {k: v[k] for k in ("ea", "ma", "tf", "ts", "pha")}
    for k in ("nguon", "the_id", "ten", "san", "von", "toi_uu"):
        if k in v:
            rec[k] = v[k]
    return rec


def tep_bao_cao(slot: str, v: dict, ten: str) -> Path:
    """Toi uu (Optimization>0) -> MT5 ghi <Report>.xml; chay don -> .htm."""
    return Path(slot, ten + (".xml" if v.get("toi_uu") else ".htm"))


def phong(slot: str, v: dict, ten: str) -> subprocess.Popen:
    if v.get("nguon") == "ong_dan":     # 18/10/2026: viec tu ong dan (BRAIN_XuLiLenh, co the la toi uu)
        Path(slot, "MQL5", "Profiles", "Tester").mkdir(parents=True, exist_ok=True)
        Path(slot, "MQL5", "Profiles", "Tester", ten + ".set").write_text(SV.file_set_ong_dan(v), encoding="ascii")
        AT.xoa_bao_cao_cu(Path(slot), ten)
        ini = Path(slot, ten + ".ini")
        ini.write_text(SV.ini_ong_dan(v, ten, AT.dong_don_bay(int(v.get("don_bay") or DON_BAY))), encoding="ascii")
        return subprocess.Popen([slot + r"\terminal64.exe", "/portable", "/config:" + str(ini)], creationflags=0x00000040)
    ea = "BRAIN_V24_%s_Trail_D1" % v["ea"]
    goc = (GOC_SET / (ea + ".set")).read_text(encoding="utf-8")
    Path(slot, "MQL5", "Profiles", "Tester").mkdir(parents=True, exist_ok=True)
    Path(slot, "MQL5", "Profiles", "Tester", ten + ".set").write_text(SV.file_set(v, goc), encoding="ascii")
    fr, to = SV.IS if v["pha"] == "IS" else SV.OOS
    ini = Path(slot, ten + ".ini")
    AT.xoa_bao_cao_cu(Path(slot), ten)
    ini.write_text("[Tester]\nExpert=BRAIN\\%s.ex5\nExpertParameters=%s.set\nSymbol=%s\nPeriod=%s\nModel=4\nExecutionMode=0\n"
                   "Optimization=0\nFromDate=%s\nToDate=%s\nForwardMode=0\nDeposit=10000\nCurrency=USD\n" + AT.dong_don_bay(DON_BAY) +
                   "Report=%s\nReplaceReport=1\nShutdownTerminal=1\nVisual=0\n" % (ea, ten, v["ma"], v["tf"], fr, to, ten), encoding="ascii")
    return subprocess.Popen([slot + r"\terminal64.exe", "/portable", "/config:" + str(ini)], creationflags=0x00000040)  # IDLE_PRIORITY_CLASS


def don_neu_day(slot: str, toi_thieu_gb: float = 6.0) -> None:
    """O dia cua slot con < toi_thieu_gb -> xoa cache tester (Agent-*) + lich su bases cua slot NAY (slot dang ranh)."""
    try:
        if shutil.disk_usage(slot[:3]).free / 1024 ** 3 >= toi_thieu_gb:
            return
        for d in list(Path(slot, "Tester").glob("Agent-*")) + list(Path(slot, "bases").glob("*/history")) + list(Path(slot, "bases").glob("*/ticks")):
            shutil.rmtree(d, ignore_errors=True)
        log("DON %s (o %s con %.1f GB)" % (slot, slot[:2], shutil.disk_usage(slot[:3]).free / 1024 ** 3))
    except Exception as e:
        log("DON loi %s" % e)


def ket_thuc():
    """Het han: xoa cache tester cua moi slot, ghi tong ket, commit + push so cai (khong --force)."""
    for s in SLOT:
        for d in list(Path(s, "Tester").glob("Agent-*")) + list(Path(s, "bases").glob("*/history")) + list(Path(s, "bases").glob("*/ticks")):
            shutil.rmtree(d, ignore_errors=True)
    shutil.rmtree(REP, ignore_errors=True)
    goc = Path(__file__).resolve().parent.parent
    (goc / "reports/mt5_lien_tuc/tong_ket_mt5.json").write_text(json.dumps(SV.tong_ket(), ensure_ascii=False, indent=1), encoding="utf-8")
    try:
        g = lambda *x: subprocess.run(["git", "-C", str(goc)] + list(x), capture_output=True, text=True, timeout=300)
        g("add", "reports/mt5_lien_tuc/so_cai.jsonl", "reports/mt5_lien_tuc/tong_ket_mt5.json")
        if KQ_ONG_DAN.exists():
            g("add", str(KQ_ONG_DAN))
        g("commit", "-m", "May nha chay lien tuc: so cai MT5 (%d lan thu) + tong ket" % len(SV.doc_so_cai()))
        g("pull", "--rebase"); r = g("push")
        log("GIT push rc=%s %s" % (r.returncode, (r.stderr or "")[-200:]))
    except Exception as e:
        log("GIT loi %s" % e)


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
    hh, mm = map(int, a.den.split(":")); han = dt.datetime.now().replace(hour=hh, minute=mm, second=0, microsecond=0)
    if han <= dt.datetime.now():
        han += dt.timedelta(days=1)   # chay qua dem (vd --den 07:00)
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
                if time.time() - t0 <= (HAN_TOI_UU_GIAY if v.get("toi_uu") else HAN_VIEC_GIAY):
                    continue
                try:
                    pr.kill()            # giet DUNG tien trinh cua minh, khong taskkill ca may
                except Exception:
                    pass
                del chay[s]
                rec = _ban_ghi(v); rec.update(loi="qua_gio", giay=int(time.time() - t0), luc=now.isoformat(timespec="seconds"))
                SV.ghi(rec)
                log("QUA GIO %s (%ss) - giet, ghi CHUA_DO_DUOC" % (ten, rec["giay"]))
                continue
            del chay[s]
            f = tep_bao_cao(s, v, ten)
            if AT.bao_cao_moi(f, t0) and f.suffix == ".xml":
                KQ_ONG_DAN.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(f), str(KQ_ONG_DAN / f.name)); shutil.move(str(f), str(REP / f.name)); hong[s] = 0
                rec = _ban_ghi(v); rec.update(file=f.name, giay=int(time.time() - t0), luc=now.isoformat(timespec="seconds"))
                SV.ghi(rec)
                log("XONG TOI UU %s -> %s" % (ten, KQ_ONG_DAN / f.name))
            elif AT.bao_cao_moi(f, t0):
                r = doc_htm(f)
                if v.get("nguon") == "ong_dan":
                    KQ_ONG_DAN.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(f), str(KQ_ONG_DAN / f.name))
                shutil.move(str(f), str(REP / f.name)); hong[s] = 0
                rec = _ban_ghi(v); rec.update(r, file=f.name, giay=int(time.time() - t0), luc=now.isoformat(timespec="seconds"))
                ly = AT.phan_xu_ket_qua(r, rec["giay"])
                if ly:
                    rec["loi"] = ly       # CHUA_DO_DUOC: duoc thu lai (sinh_viec), khong tinh la "da thu, khong lai"
                cb = AT.kiem_don_bay(r.get("don_bay_bc"), DON_BAY)
                if cb:
                    rec["canh_bao_don_bay"] = cb
                SV.ghi(rec)
                log("XONG %s %s net=%s lenh=%s pf=%s %ss%s" % (ten, v["pha"], r["net"], r["lenh"], r["pf"], rec["giay"], (" CHUA_DO_DUOC " + ly) if ly else ""))
            else:
                ngan = time.time() - t0 < 90
                hong[s] = hong.get(s, 0) + 1
                rec = _ban_ghi(v); rec.update(loi="khong_bao_cao", giay=int(time.time() - t0), luc=now.isoformat(timespec="seconds"))
                SV.ghi(rec)
                log("HONG %s (lan %d)" % (ten, hong[s]))
                if ngan and hong[s] >= 2:
                    bo.add(s); log("BO SLOT %s (fail-fast)" % s)
        if now >= han:
            if not chay:
                break
            time.sleep(15); continue
        trong = [s for s in SLOT[:n] if s not in chay and s not in bo and Path(s, "terminal64.exe").exists()]
        for s in trong:
            don_neu_day(s)
        if trong:
            dang = {SV.khoa(v) for _, v, _, _ in chay.values()}
            for s, v in zip(trong, SV.lay_viec(len(trong), dang_chay=dang)):
                ten = v["ten"] if v.get("nguon") == "ong_dan" and v.get("ten") else "lt_%s_%s_%s_%s_%s" % (v["ea"], re.sub(r"[^A-Za-z0-9]", "", v["ma"]), v["tf"], v["pha"], format(abs(hash(SV.khoa(v))) % 10**8, "08d"))
                chay[s] = (phong(s, v, ten), v, ten, time.time())
                log("PHONG %s %s muc=%s %s" % (ten, s, muc, json.dumps(v["ts"])))
                time.sleep(3)
        ha_uu_tien()
        time.sleep(15)
    ket_thuc()
    log("HET HAN - DUNG. %s" % json.dumps(SV.tong_ket(), ensure_ascii=False)[:400])


if __name__ == "__main__":
    main()
