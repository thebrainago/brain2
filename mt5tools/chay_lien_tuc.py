# -*- coding: utf-8 -*-
"""chay_lien_tuc.py - CHAY MT5 LIEN TUC tren may nha den han (vong 27). BACKTEST, khong phai tien that.

Moi vong 15 s: do muc (dieu_phoi_song_song) -> so slot; slot trong -> lay viec (sinh_viec, khong bao gio can) -> ghi .set + ini
-> terminal portable /config (ShutdownTerminal=1, uu tien Idle) -> xong thi doc bao cao, ghi so cai (Holm).
Slot (20/10/2026, chu du an): theo BIEN MOI TRUONG BRAIN_SLOTS, SSD truoc (D:\\mt5_tester\\p1, C:\\mt5_tester\\p7) roi E (p3, p6, p4)
du phong; o SSD giu >= BRAIN_SAN_TRONG_GB (6) trong, thieu thi don theo bac slot ranh roi moi sang E; khong phong viec khi
RAM trong < BRAIN_RAM_MIN_GB (4). Loc HAI TANG viec ong dan: tang 1 OHLC M1 nhanh (toi 5 viec) loai he chay tai khoan /
lo, chi he qua moi chay tang 2 real tick (toi 3 viec). Xem mt5tools/quan_ly_slot.py.
Dung nhanh: slot hong 2 lan lien (<90 s, khong bao cao) -> bo slot.
Chay:  python mt5tools/chay_lien_tuc.py --den 22:10 [--muc MAX]
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
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
import quan_ly_slot as QS  # noqa: E402

# 20/10/2026: slot theo BRAIN_SLOTS (quan_ly_slot.ds_slot). Ban cu: D:p1,p2 E:p3,p4 sua tay tren may nha.
SLOT = QS.ds_slot()
CO_TAT = Path(__file__).resolve().parent.parent / "may_nha_toi_nay" / "TAT_THE_BRAIN.co"
REP = Path(os.environ.get("BRAIN_REP_DIR") or r"D:\mt5_lien_tuc\rep")
LOG = Path(os.environ.get("BRAIN_LOG_LIEN_TUC") or r"D:\mt5_lien_tuc\chay.log")
GOC_SET = Path(__file__).resolve().parent.parent / "ea_demo"
# Don bay dat cho tester. 18/10/2026: truoc day ghi "Leverage=30" -> tester bo qua, moi bao cao la 1:100.
DON_BAY = 30
# Mot viec chay qua so giay nay thi giet va ghi `qua_gio` (do 18/10: lau nhat 506 s / 630 lan). Truoc day khong co
# han: terminal treo -> `poll()` tra None mai, `ket_thuc` (commit so cai) khong bao gio chay.
HAN_VIEC_GIAY = 1800
GIA_HAN_PHUT = 20               # qua --den bao nhieu phut thi giet viec con chay (19/10/2026)
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
         "dd": g("Equity Drawdown Maximal:"), "chat_luong": g("History Quality:"), "don_bay_bc": g("Leverage:"),
         "symbol_bc": g("Symbol:"), "ky_bc": g("Period:")}
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
    if v.get("tang") == 1:      # 20/10/2026: loc tang 1 -> khoa so cai rieng (sinh_viec.khoa)
        rec["tang"] = 1
    return rec


def tep_bao_cao(slot: str, v: dict, ten: str) -> Path:
    """Toi uu (Optimization>0) -> MT5 ghi <Report>.xml; chay don -> .htm."""
    return Path(slot, ten + (".xml" if v.get("toi_uu") else ".htm"))


def phong(slot: str, v: dict, ten: str) -> subprocess.Popen:
    if v.get("nguon") == "ong_dan":     # 18/10/2026: viec tu ong dan (BRAIN_XuLiLenh, co the la toi uu)
        Path(slot, "MQL5", "Profiles", "Tester").mkdir(parents=True, exist_ok=True)
        Path(slot, "MQL5", "Profiles", "Tester", ten + ".set").write_text(SV.file_set_ong_dan(v), encoding="ascii")
        AT.xoa_bao_cao_cu(Path(slot), ten)
        if v.get("csv_vao"):           # 19/10/2026: VAO_CSV -> CSV lenh vao vao Common\Files (tester doc FILE_COMMON)
            SV.dat_csv_vao(v, Path(__file__).resolve().parent.parent)
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


def giet_cay(pr) -> None:
    """20/10/2026 21:10 (may nha): QUA GIO truoc day chi pr.kill() terminal64 -> metatester64 con (agent tester) MO COI chay
    tiep: od_skea0e88e1df54 bi giet 21:10:30 nhung metatester PID 8448 van an 6 GB RAM + CPU toi 21:14 (RAM trong 3,9 GB,
    bo dieu phoi ha muc MT5 ve 0). Nay giet ca cay con cua DUNG tien trinh minh phong (khong taskkill theo ten)."""
    con = []
    try:
        import psutil
        con = psutil.Process(pr.pid).children(recursive=True)
    except Exception:
        pass
    for c in con:
        try:
            c.kill()
        except Exception:
            pass
    try:
        pr.kill()
    except Exception:
        pass


def san_cua_slot(slot: str) -> str:
    """'XM' / 'Exness' / '' theo dong Server= trong config/common.ini cua slot (KHONG doc Login / mat khau).
    19/10/2026: moi slot lay viec dung san minh dang nhap -> XM va Exness chay SONG SONG ca dem, khong chia doi gio."""
    f = Path(slot, "config", "common.ini")
    if not f.exists():
        return ""
    for enc in ("utf-16", "utf-8", "cp1252"):
        try:
            for dong in f.read_text(encoding=enc).splitlines():
                if dong.strip().lower().startswith("server="):
                    sv = dong.split("=", 1)[1].lower()
                    return "XM" if "xm" in sv else "Exness" if "exness" in sv else ""
        except (UnicodeError, OSError):
            continue
    return ""


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
    """Het han: don cache tester cua slot NAO thieu cho, ghi tong ket, commit + push so cai (khong --force).

    19/10/2026: truoc day XOA tick + lich su cua MOI slot sau moi phien -> dem sau tai / sinh lai tu dau hang GB tick
    (va buoc 7 chia doi XM/Exness thi xoa ngay giua dem). Nay chi don khi o dia con < 6 GB (`don_neu_day`)."""
    for s in SLOT:
        if Path(s).exists():
            QS.dam_bao_cho(s, [s], log=log)    # het phien: slot nao duoi san trong thi don theo bac
    # 20/10/2026: KHONG xoa REP nua (bao cao da doc o lai toi dau phien sau roi chuyen sang E: - quan_ly_slot)
    goc = Path(__file__).resolve().parent.parent
    (goc / "reports/mt5_lien_tuc/tong_ket_mt5.json").write_text(json.dumps(SV.tong_ket(), ensure_ascii=False, indent=1), encoding="utf-8")
    try:
        g = lambda *x: subprocess.run(["git", "-C", str(goc)] + list(x), capture_output=True, text=True, timeout=300)
        g("add", "reports/mt5_lien_tuc/so_cai.jsonl", "reports/mt5_lien_tuc/tong_ket_mt5.json")
        if KQ_ONG_DAN.exists():
            g("add", str(KQ_ONG_DAN))
        g("commit", "-m", "May nha chay lien tuc: so cai MT5 (%d lan thu) + tong ket" % len(SV.doc_so_cai()))
        g("pull", "--rebase", "--autostash"); r = g("push")   # buoc khac dang ghi reports/ -> can autostash
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


def ten_viec(v: dict) -> str:
    if v.get("nguon") == "ong_dan" and v.get("ten"):
        return v["ten"] + ("_T1" if v.get("tang") == 1 else "")
    return "lt_%s_%s_%s_%s_%s" % (v["ea"], re.sub(r"[^A-Za-z0-9]", "", v["ma"]), v["tf"], v["pha"],
                                  format(abs(hash(SV.khoa(v))) % 10**8, "08d"))


def xu_ly_xong(s: str, v: dict, ten: str, t0: float, now: dt.datetime, hong: dict, bo: set) -> None:
    """Mot viec da thoat: doc bao cao, chep ket qua, ghi so cai, don file lam viec cua viec do."""
    f = tep_bao_cao(s, v, ten)
    if AT.bao_cao_moi(f, t0) and f.suffix == ".xml":
        KQ_ONG_DAN.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(f), str(KQ_ONG_DAN / f.name)); REP.mkdir(parents=True, exist_ok=True)
        shutil.move(str(f), str(REP / f.name)); hong[s] = 0
        rec = _ban_ghi(v); rec.update(file=f.name, giay=int(time.time() - t0), luc=now.isoformat(timespec="seconds"), slot=s)
        SV.ghi(rec)
        log("XONG TOI UU %s -> %s" % (ten, KQ_ONG_DAN / f.name))
    elif AT.bao_cao_moi(f, t0):
        r = doc_htm(f)
        tang = v.get("tang")
        if v.get("nguon") == "ong_dan":
            # tang 1 -> thu muc con (doc_mt5 chi doc od_* o goc ket_qua_mt5 = ket qua real tick)
            dich = KQ_ONG_DAN / "tang1" if tang == 1 else KQ_ONG_DAN
            dich.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(f), str(dich / f.name))
            if tang != 1:
                try:
                    SV.lay_csv_ra(v, KQ_ONG_DAN)      # lenh MT5 + nen -> doc_mt5 doi chieu voi Python
                except Exception as e:
                    log("CSV ra loi %s %s" % (ten, e))
        REP.mkdir(parents=True, exist_ok=True)
        shutil.move(str(f), str(REP / f.name)); hong[s] = 0
        rec = _ban_ghi(v); rec.update(r, file=f.name, giay=int(time.time() - t0), luc=now.isoformat(timespec="seconds"), slot=s)
        if tang == 1:
            rec["tang"] = 1
            qua, ly_t1 = QS.phan_xu_tang1(r)
            rec["tang1_qua"], rec["tang1_ly_do"] = qua, ly_t1
        ly = AT.phan_xu_ket_qua(r, rec["giay"])
        # 20/10/2026: bao cao chay SAI symbol (vd EURUSD# hop dong chuan thay EURUSDmicro) -> CHUA_DO_DUOC, chay lai
        if r.get("symbol_bc") and v.get("ma") and r["symbol_bc"].strip().lower() != str(v["ma"]).strip().lower():
            ly = "sai_symbol: bao cao %s, viec %s" % (r["symbol_bc"], v["ma"])
        if ly:
            rec["loi"] = ly       # CHUA_DO_DUOC: duoc thu lai (sinh_viec), khong tinh la "da thu, khong lai"
        cb = AT.kiem_don_bay(r.get("don_bay_bc"), int(v.get("don_bay") or DON_BAY))
        if cb:
            rec["canh_bao_don_bay"] = cb
        SV.ghi(rec)
        log("XONG %s %s%s net=%s lenh=%s pf=%s dd=%s %ss%s%s" % (
            ten, v["pha"], " T1" if tang == 1 else "", r["net"], r["lenh"], r["pf"], r.get("dd"), rec["giay"],
            (" CHUA_DO_DUOC " + ly) if ly else "", (" | " + rec["tang1_ly_do"]) if tang == 1 else ""))
    else:
        ngan = time.time() - t0 < 90
        hong[s] = hong.get(s, 0) + 1
        rec = _ban_ghi(v); rec.update(loi="khong_bao_cao", giay=int(time.time() - t0), luc=now.isoformat(timespec="seconds"), slot=s)
        if v.get("tang") == 1:
            rec["tang"] = 1
        SV.ghi(rec)
        log("HONG %s (lan %d)" % (ten, hong[s]))
        if ngan and hong[s] >= 2:
            bo.add(s); log("BO SLOT %s (fail-fast)" % s)
    try:                                    # 20/10/2026: don file lam viec cua viec nay (ket qua da chep xong)
        n = QS.don_sau_viec(s, ten, SV.thu_muc_common() if v.get("csv_vao") else None, v.get("csv_vao"))
        if n:
            log("DON SAU VIEC %s %s: %.1f MB" % (s, ten, n / 1024 ** 2))
    except Exception as e:  # noqa: BLE001
        log("DON SAU VIEC loi %s" % e)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--den", default="22:10"); ap.add_argument("--muc"); a = ap.parse_args()
    hh, mm = map(int, a.den.split(":")); han = dt.datetime.now().replace(hour=hh, minute=mm, second=0, microsecond=0)
    if han <= dt.datetime.now():
        han += dt.timedelta(days=1)   # chay qua dem (vd --den 07:00)
    REP.mkdir(parents=True, exist_ok=True)
    QS.chuyen_bao_cao_cu(REP, truoc=time.time(), log=log)      # bao cao da doc cua phien truoc -> E:
    chay, hong, bo = {}, {}, set()
    tat = False
    hai = QS.hai_tang()
    log("BAT DAU, han %s | slot %s | hai tang %s" % (han, SLOT, hai))
    while True:
        now = dt.datetime.now()
        # 20/10/2026 09:50 (chu du an): BO giam tai theo game / toan man hinh / CPU nguoi dung - may chay The Brain het suc
        # hoac tat han. Mac dinh moi slot trong BRAIN_SLOTS; RAM (>= 4 GB trong) va o dia la gioi han duy nhat
        # (dieu_phoi.py -> muc_mt5.json, QS.du_ram, QS.dam_bao_cho). --muc THAP/VUA/CAO van ep tay duoc.
        n = DP.so_slot_mt5(a.muc, toi_da=len(SLOT)) if a.muc in DP.MUC else len(SLOT)
        for s, (pr, v, ten, t0) in list(chay.items()):
            if pr.poll() is None:
                if time.time() - t0 <= (HAN_TOI_UU_GIAY if v.get("toi_uu") else HAN_VIEC_GIAY):
                    continue
                giet_cay(pr)             # giet DUNG tien trinh cua minh + metatester con, khong taskkill ca may
                del chay[s]
                rec = _ban_ghi(v); rec.update(loi="qua_gio", giay=int(time.time() - t0), luc=now.isoformat(timespec="seconds"))
                if v.get("tang") == 1:
                    rec["tang"] = 1
                SV.ghi(rec)
                log("QUA GIO %s (%ss) - giet, ghi CHUA_DO_DUOC" % (ten, rec["giay"]))
                continue
            del chay[s]
            xu_ly_xong(s, v, ten, t0, now, hong, bo)
        if not tat and CO_TAT.exists():
            # 20/10/2026: TAT_THE_BRAIN.bat -> khong phong viec moi; viec dang chay duoc GIA_HAN_PHUT de xong roi moi giet
            # (chi PID tester cua minh - khong bao gio dong terminal XM chinh hay Claude)
            tat = True
            han = min(han, now)
            log("THAY TAT_THE_BRAIN.co - dung phong viec moi, cho %d viec dang chay (toi da %d phut)" % (len(chay), GIA_HAN_PHUT))
        if now >= han:
            if not chay:
                break
            # 19/10/2026: viec toi uu duoc 6 gio -> khong cho qua han qua GIA_HAN_PHUT; giet DUNG PID cua minh,
            # ghi `qua_gio` (CHUA_DO_DUOC, dem sau chay lai). Truoc day may chay toi trua hom sau.
            if now >= han + dt.timedelta(minutes=GIA_HAN_PHUT):
                for s, (pr, v, ten, t0) in list(chay.items()):
                    giet_cay(pr)
                    rec = _ban_ghi(v); rec.update(loi="qua_gio_het_han", giay=int(time.time() - t0), luc=now.isoformat(timespec="seconds"))
                    SV.ghi(rec)
                    log("HET HAN + %d phut: giet %s, ghi CHUA_DO_DUOC" % (GIA_HAN_PHUT, ten))
                break
            time.sleep(15); continue
        # 20/10/2026: muc may (DP) cho n slot real tick; co viec tang 1 thi duoc them toi BRAIN_TANG1_SLOT viec dong thoi
        tong_max, t2_max = QS.slot_toi_da(hai)
        t2_max = min(t2_max, n)
        tong_max = min(tong_max, len(SLOT)) if n > 0 else 0
        co_san = [s for s in SLOT if s not in chay and s not in bo and Path(s, "terminal64.exe").exists()]
        con_cho = max(0, tong_max - len(chay))
        dang_t2 = sum(1 for _, v, _, _ in chay.values() if v.get("tang") != 1)
        cap = []
        if con_cho and co_san:
            dang = {SV.khoa(v) for _, v, _, _ in chay.values()}
            for s in co_san:
                if len(cap) >= con_cho:
                    break
                # dia: o SSD duoi san trong -> don bac slot ranh cung o; van thieu -> bo qua slot nay (sang E)
                ranh = [x for x in co_san if x not in [c[0] for c in cap]]
                if not QS.dam_bao_cho(s, ranh, log=log):
                    log("BO QUA SLOT %s: o %s duoi san trong %.0f GB sau khi don" % (s, QS.o_cua(s), QS.san_trong(s)))
                    continue
                sn = os.environ.get("BRAIN_SAN_TESTER") or san_cua_slot(s) or None
                chi_t1 = dang_t2 + sum(1 for c in cap if c[1].get("tang") != 1) >= t2_max
                vs = SV.lay_viec(1, dang_chay=dang, san=sn, hai_tang=hai, chi_tang1=chi_t1 and hai)
                if not vs:
                    continue
                v = vs[0]
                if chi_t1 and v.get("tang") != 1:
                    continue
                ok, ly = QS.du_ram(1 if v.get("tang") == 1 else 2)
                if not ok:
                    log("CHO RAM: %s - chua phong %s" % (ly, v.get("ten") or v.get("ea")))
                    break
                dang.add(SV.khoa(v))
                cap.append((s, v))
        for s, v in cap:
            ten = ten_viec(v)
            try:
                chay[s] = (phong(s, v, ten), v, ten, time.time())
            except Exception as e:      # 19/10/2026: CSV thieu / file Common bi khoa -> ghi loi, KHONG dung ca hang
                rec = _ban_ghi(v); rec.update(loi="khong_phong_duoc: %s" % str(e)[:200], giay=0, luc=now.isoformat(timespec="seconds"))
                if v.get("tang") == 1:
                    rec["tang"] = 1
                SV.ghi(rec)
                log("KHONG PHONG DUOC %s: %s" % (ten, e))
                continue
            log("PHONG %s %s muc=%s tang=%s %s" % (ten, s, a.muc or "-", v.get("tang", "-"), json.dumps(v["ts"])))
            time.sleep(3)
        ha_uu_tien()
        time.sleep(15)
    ket_thuc()
    log("HET HAN - DUNG. %s" % json.dumps(SV.tong_ket(), ensure_ascii=False)[:400])


if __name__ == "__main__":
    main()
