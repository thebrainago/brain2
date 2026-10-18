# -*- coding: utf-8 -*-
"""chay_xu_li_lenh.py - chay EA `ea_demo/BRAIN_XuLiLenh.mq5` (DCA / nhoi thuan / trailing / hedge / go) tren MT5 tester.
17/10/2026. BACKTEST MT5, khong phai tien that. MT5 tu tinh diem, spread, swap, hoa hong theo thong so cua SAN DANG KET NOI
(khong doan point bang Python nua). Moi kich ban chay MOT lan, khong quet tham so.

Chay (may nha, terminal portable DANG DANG NHAP tai khoan muon do):
  python mt5tools/chay_xu_li_lenh.py danh-sach [--ma-san reports/phi_san/<server>/ma_san.json]
  python mt5tools/chay_xu_li_lenh.py chay --slot D:\\mt5_tester\\exness_cent [--ma-san ...] [--tien USC] [--chi dca5_hedge]
  python mt5tools/chay_xu_li_lenh.py tong-ket [--ma-san ...]
Ra: reports/xu_li_lenh/<server>/so_cai.jsonl + TONG_KET.md. Cot "dat" = ba yeu to cot loi: lai sau phi, DD VON (gom lo tha noi,
do MT5 do) <= 80 % sau khi chinh lot, lai >= 10 %/nam.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chay_lai_tren_san as CLS  # noqa: E402
import an_toan_tester as AT  # noqa: E402

GOC = CLS.GOC
EA = "BRAIN_XuLiLenh"
TU, DEN = "2016.01.01", "2026.10.01"
# Enum cua EA: InpVao 0 khong tin hieu / 1 MRZ / 2 RSI / 3 Donchian; InpNhoi 0 tat / 1 nghich (DCA) / 2 thuan; InpKieuLot 0 deu / 1 tuyen tinh / 2 nhan
QUAN_LI = {
    "chi_tp_trail": {"InpNhoi": 0, "InpTPATR": 0.5, "InpTrailKichATR": 1.0, "InpTrailKhoangATR": 0.5},
    "dca5_deu":     {"InpNhoi": 1, "InpBuocATR": 1.0, "InpMaxTang": 5, "InpKieuLot": 0, "InpTPATR": 0.5, "InpTrailKichATR": 0},
    "dca5_tang":    {"InpNhoi": 1, "InpBuocATR": 1.0, "InpGianBuoc": 1.3, "InpMaxTang": 5, "InpKieuLot": 1, "InpTPATR": 0.5, "InpTrailKichATR": 0},
    "dca5_hedge":   {"InpNhoi": 1, "InpBuocATR": 1.0, "InpMaxTang": 5, "InpKieuLot": 0, "InpTPATR": 0.5, "InpTrailKichATR": 0,
                     "InpHedgeKhiLoPct": 5.0, "InpHedgeTiLe": 1.0, "InpMoKhoaATR": 1.0, "InpGoTien": 0.0},
    "nhoi_thuan":   {"InpNhoi": 2, "InpBuocATR": 0.5, "InpMaxTang": 3, "InpKieuLot": 0, "InpTPATR": 0, "InpTrailKichATR": 1.0, "InpTrailKhoangATR": 0.7},
}
# (ten goc, khung, tin hieu): MRZ D1 = cac ma da lai tren so cai MT5 13/10; khong tin hieu (PMG) = vang + chi so H1
VAO = [
    ("GBPUSD", "D1", {"InpVao": 1, "InpTF": 16408, "InpN": 50, "InpNguongZ": 2.0}),
    ("AUDUSD", "D1", {"InpVao": 1, "InpTF": 16408, "InpN": 50, "InpNguongZ": 2.0}),
    ("EURGBP", "D1", {"InpVao": 1, "InpTF": 16408, "InpN": 50, "InpNguongZ": 1.5}),
    ("XAUUSD", "H1", {"InpVao": 0, "InpTF": 16385, "InpChieuKhongTin": 0, "InpChoNen": 4}),
    ("US500", "H1",  {"InpVao": 0, "InpTF": 16385, "InpChieuKhongTin": 1, "InpChoNen": 4}),
    ("GER40", "H1",  {"InpVao": 0, "InpTF": 16385, "InpChieuKhongTin": 0, "InpChoNen": 4}),
]
TF_TEN = {16408: "D1", 16388: "H4", 16385: "H1"}


def kich_ban() -> list[dict]:
    out = []
    for goc, tf, vao in VAO:
        for ten, ql in QUAN_LI.items():
            if vao["InpVao"] == 0 and ten == "chi_tp_trail":
                continue                     # khong tin hieu + khong nhoi = vao bua, khong co nghia
            out.append({"ten": "%s_%s_%s" % (goc, tf, ten), "goc": goc, "tf": tf, "quan_li": ten, "ts": {**vao, **ql}})
    return out


def gan_ma(kb: list[dict], ma_san: dict | None) -> tuple[list[dict], list[str]]:
    if not ma_san:
        return [dict(k, ma=k["goc"], lot=0.01) for k in kb], []
    out, thieu = [], []
    for k in kb:
        m = ma_san.get("ma", {}).get(k["goc"])
        if not m:
            thieu.append(k["goc"]); continue
        out.append(dict(k, ma=m["symbol"], lot=max(0.01, float(m.get("lot_min") or 0.01))))
    return out, sorted(set(thieu))


def file_set(k: dict) -> str:
    ts = dict(k["ts"], InpLot0=k["lot"], InpLogChung="false")
    return "\n".join("%s=%s" % kv for kv in sorted(ts.items())) + "\n"


def dd_pct(s: str | None) -> float | None:
    m = re.search(r"\(([\d.]+)%\)", str(s or ""))
    return float(m.group(1)) if m else None


def cot_loi(r: dict, von: float) -> dict:
    """Lai %/nam tu deals (sau phi), DD VON MT5 (gom tha noi), lai o muc lot cho DD 80 %."""
    nam = (int(DEN[:4]) - int(TU[:4])) + (int(DEN[5:7]) - int(TU[5:7])) / 12.0
    lai = (r.get("net") or 0.0) / von / nam * 100.0
    dd = dd_pct(r.get("dd"))
    o80 = lai * 80.0 / dd if dd else None
    return {"lai_pct_nam": round(lai, 3), "dd_von_pct": dd, "lai_pct_nam_o_dd80": round(o80, 1) if o80 is not None else None,
            "he_so_lot": round(80.0 / dd, 1) if dd else None, "dat": bool(lai > 0 and (o80 is None or o80 >= 10.0))}


def chuan_bi(slot: Path) -> None:
    dich = slot / "MQL5" / "Experts" / "BRAIN"; dich.mkdir(parents=True, exist_ok=True)
    mq = dich / (EA + ".mq5")
    shutil.copy2(GOC / "ea_demo" / (EA + ".mq5"), mq)
    if not mq.with_suffix(".ex5").exists() or mq.with_suffix(".ex5").stat().st_mtime < mq.stat().st_mtime:
        me = slot / "metaeditor64.exe"
        if not me.exists():
            raise SystemExit("Thieu metaeditor64.exe trong slot -> mo MetaEditor, bien dich %s" % mq)
        loi = AT.bien_dich(me, mq)          # 18/10/2026: doi .ex5 MOI, khong tin "co .ex5" (ban cu van nam do)
        if loi:
            raise SystemExit("Bien dich hong: %s" % loi)


def chay_mot(slot: Path, k: dict, von: int, tien: str, don_bay: int, cho: int) -> dict:
    import chay_lien_tuc as CL
    ten = "xl_" + re.sub(r"[^A-Za-z0-9_]", "", k["ten"])
    (slot / "MQL5" / "Profiles" / "Tester").mkdir(parents=True, exist_ok=True)
    (slot / "MQL5" / "Profiles" / "Tester" / (ten + ".set")).write_text(file_set(k), encoding="ascii")
    ini = slot / (ten + ".ini")
    ini.write_text("[Tester]\nExpert=BRAIN\\%s.ex5\nExpertParameters=%s.set\nSymbol=%s\nPeriod=%s\nModel=4\nExecutionMode=0\n"
                   "Optimization=0\nFromDate=%s\nToDate=%s\nForwardMode=0\nDeposit=%d\nCurrency=%s\nLeverage=1:%d\n"
                   "Report=%s\nReplaceReport=1\nShutdownTerminal=1\nVisual=0\n" % (EA, ten, k["ma"], k["tf"], TU, DEN, von, tien, don_bay, ten),
                   encoding="ascii")
    AT.xoa_bao_cao_cu(slot, ten)       # 18/10/2026: ten co dinh -> lan hong doc lai bao cao CU
    t0 = time.time()
    try:
        subprocess.run([str(slot / "terminal64.exe"), "/portable", "/config:" + str(ini)], timeout=cho)
    except subprocess.TimeoutExpired:
        return {"loi": "qua_gio", "giay": int(time.time() - t0)}
    f = slot / (ten + ".htm")
    if not AT.bao_cao_moi(f, t0):
        return {"loi": "khong_bao_cao", "giay": int(time.time() - t0)}         # CHUA_DO_DUOC, khong phai AM
    r = CL.doc_htm(f)
    r["deals"] = CLS.doc_deals(f.read_bytes().decode("utf-16", errors="ignore"))
    r["giay"] = int(time.time() - t0)
    ly = AT.phan_xu_ket_qua(r, r["giay"])
    if ly:
        r["loi"] = ly                       # CHUA_DO_DUOC, khong phai AM
    cb = AT.kiem_don_bay(r.get("don_bay_bc"), don_bay)
    if cb:
        r["canh_bao_don_bay"] = cb
    return r


def bang(so: list[dict], von: float) -> str:
    moi = {}
    for r in so:
        if not r.get("loi"):
            moi[r["ten"]] = r
    dong = ["| Kich ban | Ma | Lai %/nam | DD von % (MT5) | Lai o DD 80 % | Lenh | PF | Dat 3 yeu to |", "|---|---|---|---|---|---|---|---|"]
    for r in sorted(moi.values(), key=lambda z: -(cot_loi(z, von)["lai_pct_nam_o_dd80"] or -1e9)):
        c = cot_loi(r, von)
        dong.append("| %s | %s | %.2f | %s | %s | %s | %s | %s |" % (r["ten"], r["ma"], c["lai_pct_nam"], c["dd_von_pct"],
                    c["lai_pct_nam_o_dd80"], r.get("lenh"), r.get("pf"), "DAT" if c["dat"] else "-"))
    hong = [r["ten"] for r in so if r.get("loi")]
    if hong:
        dong.append("\nCHUA_DO_DUOC (khong co bao cao): " + ", ".join(sorted(set(hong))))
    return "\n".join(dong) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("lenh", choices=["danh-sach", "chay", "tong-ket"]); ap.add_argument("--ma-san")
    ap.add_argument("--slot"); ap.add_argument("--von", type=float, default=10000); ap.add_argument("--tien", default="USD")
    ap.add_argument("--don-bay", type=int); ap.add_argument("--cho-toi-da", type=int, default=3600); ap.add_argument("--chi", default="")
    a = ap.parse_args()
    ms = json.loads(Path(a.ma_san).read_text(encoding="utf-8")) if a.ma_san else None
    kb, thieu = gan_ma(kich_ban(), ms)
    if a.chi:
        kb = [k for k in kb if any(x in k["ten"] for x in a.chi.split(","))]
    ra = GOC / "reports" / "xu_li_lenh" / re.sub(r"[^A-Za-z0-9._-]", "_", (ms or {}).get("server", "san_hien_tai"))
    so = ra / "so_cai.jsonl"
    if a.lenh == "danh-sach":
        for k in kb:
            print(k["ten"], k["ma"], json.dumps(k["ts"]))
        print("%d kich ban; san khong co ma: %s" % (len(kb), ", ".join(thieu) or "-"))
        return
    ra.mkdir(parents=True, exist_ok=True)
    cu = [json.loads(x) for x in so.read_text(encoding="utf-8").splitlines() if x.strip()] if so.exists() else []
    if a.lenh == "tong-ket":
        (ra / "TONG_KET.md").write_text("# Xu li lenh tren MT5 (%s)\n\n" % (ms or {}).get("server", "-") + bang(cu, a.von), encoding="utf-8")
        print(bang(cu, a.von)); return
    if a.don_bay is None:
        tk = Path(a.ma_san).with_name("tai_khoan.json") if a.ma_san else None
        a.don_bay = int(json.loads(tk.read_text(encoding="utf-8")).get("don_bay") or 500) if tk and tk.exists() else 500
    slot = Path(a.slot); chuan_bi(slot)
    da = {r["ten"] for r in cu if not r.get("loi")}
    for i, k in enumerate(kb, 1):
        if k["ten"] in da:
            continue
        print("[%d/%d] %s (%s)" % (i, len(kb), k["ten"], k["ma"]), flush=True)
        r = chay_mot(slot, k, int(a.von), a.tien, a.don_bay, a.cho_toi_da)
        rec = {**{x: k[x] for x in ("ten", "goc", "ma", "tf", "quan_li", "ts", "lot")}, **r, "von": a.von, "tien": a.tien,
               "luc": time.strftime("%Y-%m-%dT%H:%M:%S")}
        with open(so, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if not r.get("loi"):
            print("   ->", json.dumps(cot_loi(r, a.von), ensure_ascii=False), flush=True)
        else:
            print("   ->", r["loi"], flush=True)
    print("XONG. Tiep: python mt5tools/chay_xu_li_lenh.py tong-ket" + (" --ma-san " + a.ma_san if a.ma_san else ""))


if __name__ == "__main__":
    main()
