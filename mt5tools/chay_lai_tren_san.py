# -*- coding: utf-8 -*-
"""chay_lai_tren_san.py - CHAY LAI cac cau hinh MT5 DA CO LAI tren TAI KHOAN CUA CHU DU AN (Exness cent / XM micro), roi GHEP.
17/10/2026. BACKTEST MT5 tester, khong phai tien that. Khong quet tham so moi: chi chay lai dung cau hinh da lai
trong so cai XM Ultra Low (reports/mt5_lien_tuc/so_cai.jsonl, 13/10) - xem phi/spread/swap that cua san anh an bao nhieu.

Can truoc (may nha):
  1. Mot terminal MT5 PORTABLE rieng cho moi san, DANG DANG NHAP tai khoan cua anh (vd D:\\mt5_tester\\exness_cent).
     Tester lay thong so ma (spread, swap, hop dong) tu chinh server dang ket noi -> sai san = sai phi.
  2. `python mt5tools/do_phi_san.py <slot>\\terminal64.exe` -> reports/phi_san/<server>/ma_san.json (bang ten ma cua san).
Chay:
  python mt5tools/chay_lai_tren_san.py danh-sach --ma-san reports/phi_san/<server>/ma_san.json          (in viec, khong chay)
  python mt5tools/chay_lai_tren_san.py chay --slot D:\\mt5_tester\\exness_cent --ma-san ... --von 10000 --tien USC
  python mt5tools/chay_lai_tren_san.py tong-ket --ma-san ... [--dd-muc-tieu 20]
Ra: reports/mt5_san_chu/<server>/so_cai.jsonl (moi lan chay: so lieu + tung deal dong lenh) va tong_ket.json.
Tong ket la DUONG VON DONG LENH (khong tinh lo tha noi) -> sut giam that con lon hon; ghi ro trong file.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import do_phi_san as DPS  # noqa: E402
import sinh_viec as SV  # noqa: E402

GOC = SV.GOC
TOAN = ("2016.01.01", "2026.10.01")


def chon_cau_hinh(so_cai: list[dict], top: int = 2) -> list[dict]:
    """Moi (EA, ten goc, khung): `top` cau hinh tot nhat theo PF cua nua KEM hon (IS hay OOS), bo cau hinh cho ket qua trung het."""
    nhom: dict[tuple, list[dict]] = {}
    for u in SV.tong_ket(so_cai)["ung_vien_ca_hai"]:
        g = DPS.ten_goc(u["ma"])
        if g:
            nhom.setdefault((u["ea"], g, u["tf"]), []).append(u)
    out = []
    for (ea, g, tf), us in sorted(nhom.items()):
        da, chon = set(), []
        for u in sorted(us, key=lambda z: -min(z["IS"]["pf"] or 0, z["OOS"]["pf"] or 0)):
            dau = (u["IS"]["net"], u["OOS"]["net"])
            if dau in da:
                continue                      # bien the chi khac InpTrATR ma ket qua y het
            da.add(dau); chon.append({"ea": ea, "goc": g, "tf": tf, "ts": u["ts"], "nguon": {"ma_xm": u["ma"], "IS": u["IS"], "OOS": u["OOS"]}})
            if len(chon) >= top:
                break
        out += chon
    return out


def viec_tren_san(cau_hinh: list[dict], ma_san: dict) -> tuple[list[dict], list[str]]:
    """Gan ten ma that cua san. Tra (viec, ten goc san KHONG co)."""
    viec, thieu = [], []
    for c in cau_hinh:
        m = ma_san.get("ma", {}).get(c["goc"])
        if not m:
            thieu.append(c["goc"]); continue
        lot = max(0.01, float(m.get("lot_min") or 0.01))
        viec.append({**c, "ma": m["symbol"], "lot": lot, "pha": "TOAN", "tien_moi_gia_1lot": m.get("tien_moi_gia_1lot")})
    return viec, sorted(set(thieu))


def khoa(v: dict) -> str:
    return json.dumps({k: v[k] for k in ("ea", "ma", "tf", "ts", "pha", "lot")}, sort_keys=True)


def doc_deals(t: str) -> list[list]:
    """Bang Deals cua bao cao tester (.htm da giai ma) -> [[thoi_gian 'YYYY.MM.DD HH:MM:SS', rong = loi+swap+hoa_hong], ...] cac deal 'out'."""
    i = t.find(">Deals<"); out = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", t[i:] if i >= 0 else "", re.S):
        c = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(c) >= 13 and c[4] in ("out", "in/out"):
            try:
                out.append([c[0], round(sum(float(c[k].replace(" ", "").replace("\xa0", "")) for k in (8, 9, 10)), 2)])
            except ValueError:
                pass
    return out


def tong_ket_duong_von(deals: list[list], von: float, nam: float) -> dict:
    """Duong von DONG LENH tu deals [[thoi_gian, rong]] -> lai %/nam (don gian, tren von), sut giam max %, thang te nhat, lenh/thang."""
    if not deals:
        return {"lenh": 0, "net": 0.0, "lai_pct_nam": 0.0, "sut_giam_pct": 0.0, "thang_te_nhat": None, "lenh_thang": 0.0}
    ds = sorted(deals); eq = dinh = von; dd = 0.0; thang: dict[str, float] = {}
    for tg, x in ds:
        eq += x; dinh = max(dinh, eq); dd = max(dd, (dinh - eq) / dinh if dinh > 0 else 1.0)
        thang[tg[:7]] = thang.get(tg[:7], 0.0) + x
    net = eq - von
    return {"lenh": len(ds), "net": round(net, 2), "lai_pct_nam": round(100 * net / von / nam, 3), "sut_giam_pct": round(100 * dd, 3),
            "thang_te_nhat": round(min(thang.values()), 2), "thang_am": sum(v < 0 for v in thang.values()), "so_thang": len(thang),
            "lenh_thang": round(len(ds) / max(1, len(thang)), 2)}


def ghep(so_cai: list[dict], von: float, dd_muc_tieu: float = 20.0) -> dict:
    """Moi (EA, ten goc) lay MOT cau hinh co net cao nhat tren san nay, cong deals lai = mot tai khoan chay tat ca cung luc.
    Chon theo net tren chinh san nay la CHON TREN CUNG DU LIEU (nhan, khong chan) - demo moi la phan xu cuoi."""
    nam = (int(TOAN[1][:4]) - int(TOAN[0][:4])) + (int(TOAN[1][5:7]) - 1) / 12.0
    moi: dict[str, dict] = {}
    for r in so_cai:
        if r.get("deals") is not None:
            moi[khoa(r)] = r                  # chay lai cung cau hinh -> lay lan sau cung
    tung, tot = [], {}
    for r in moi.values():
        x = {**{k: r[k] for k in ("ea", "goc", "ma", "tf", "ts", "lot")}, **tong_ket_duong_von(r["deals"], von, nam), "pf": r.get("pf"),
             "dd_von_tha_noi_mt5": r.get("dd")}
        tmg = r.get("tien_moi_gia_1lot")
        # spread/truot THEM moi lenh (don vi gia) ma manh van hoa: lai rong moi lenh / tien moi 1 gia o lot dang chay
        x["chiu_them_gia_moi_lenh"] = round(x["net"] / x["lenh"] / (tmg * r["lot"]), 5) if tmg and x["lenh"] else None
        tung.append(x)
        k = (x["ea"], x["goc"])
        if x["net"] > 0 and (k not in tot or x["net"] > tot[k][0]["net"]):
            tot[k] = (x, r["deals"])
    bo = tong_ket_duong_von([d for _, ds in tot.values() for d in ds], von, nam)
    chon = [x for x, _ in tot.values()]
    dong_gop = []                             # bo tung manh ra: bo ghep mat bao nhieu lai, sut giam doi the nao
    for k in tot:
        b = tong_ket_duong_von([d for kk, (_, ds) in tot.items() if kk != k for d in ds], von, nam)
        dong_gop.append({"manh": "%s %s" % k, "lai_mat_khi_bo": round(bo["net"] - b["net"], 2),
                         "sut_giam_pct_khi_bo": b["sut_giam_pct"], "sut_giam_pct_ca_bo": bo["sut_giam_pct"]})
    k = dd_muc_tieu / bo["sut_giam_pct"] if bo["sut_giam_pct"] else None
    return {"ghi_chu": "duong von DONG LENH (khong tinh lo tha noi) - sut giam that lon hon; tang lot tuyen tinh la uoc luong THO",
            "von": von, "so_nam": round(nam, 2), "tung_manh": sorted(tung, key=lambda z: -z["net"]), "manh_trong_bo": len(chon),
            "bo_ghep": bo, "dong_gop": sorted(dong_gop, key=lambda z: -z["lai_mat_khi_bo"]), "manh": sorted("%s %s %s" % (c["ea"], c["ma"], c["tf"]) for c in chon), "dd_muc_tieu_pct": dd_muc_tieu, "he_so_lot": round(k, 2) if k else None,
            "lai_pct_nam_o_dd_muc_tieu": round(bo["lai_pct_nam"] * k, 2) if k else None}


def chuan_bi_ea(slot: Path) -> None:
    """Chep EA vao slot va bien dich neu chua co .ex5 (can metaeditor64.exe trong slot)."""
    dich = slot / "MQL5" / "Experts" / "BRAIN"; dich.mkdir(parents=True, exist_ok=True)
    for f in list((GOC / "ea_demo").glob("BRAIN_V24_*.mq*")):
        shutil.copy2(f, dich / f.name)
    me = slot / "metaeditor64.exe"
    for ea in ("MRZ", "RSI"):
        mq = dich / ("BRAIN_V24_%s_Trail_D1.mq5" % ea)
        if not mq.with_suffix(".ex5").exists():
            if not me.exists():
                raise SystemExit("Thieu %s va khong co metaeditor64.exe trong slot -> bien dich tay bang MetaEditor" % mq.with_suffix(".ex5"))
            subprocess.run([str(me), "/portable", "/compile:" + str(mq), "/log"], timeout=300)
            if not mq.with_suffix(".ex5").exists():
                raise SystemExit("Bien dich hong: xem %s" % mq.with_suffix(".log"))


def chay_mot(slot: Path, v: dict, von: float, tien: str, don_bay: int, cho_toi_da: int) -> dict:
    import chay_lien_tuc as CL   # doc_htm dung chung voi so cai XM
    ea = "BRAIN_V24_%s_Trail_D1" % v["ea"]
    ten = "sc_%s_%s_%s_%08d" % (v["ea"], re.sub(r"[^A-Za-z0-9]", "", v["ma"]), v["tf"], abs(hash(khoa(v))) % 10**8)
    goc = (GOC / "ea_demo" / (ea + ".set")).read_text(encoding="utf-8")
    st = [x for x in SV.file_set(v, goc).splitlines() if not x.startswith("InpLots=")] + ["InpLots=%s" % v["lot"]]
    (slot / "MQL5" / "Profiles" / "Tester").mkdir(parents=True, exist_ok=True)
    (slot / "MQL5" / "Profiles" / "Tester" / (ten + ".set")).write_text("\n".join(st) + "\n", encoding="ascii")
    ini = slot / (ten + ".ini")
    ini.write_text("[Tester]\nExpert=BRAIN\\%s.ex5\nExpertParameters=%s.set\nSymbol=%s\nPeriod=%s\nModel=4\nExecutionMode=0\n"
                   "Optimization=0\nFromDate=%s\nToDate=%s\nForwardMode=0\nDeposit=%d\nCurrency=%s\nLeverage=%d\n"
                   "Report=%s\nReplaceReport=1\nShutdownTerminal=1\nVisual=0\n" % (ea, ten, v["ma"], v["tf"], TOAN[0], TOAN[1], von, tien, don_bay, ten),
                   encoding="ascii")
    t0 = time.time()
    try:
        subprocess.run([str(slot / "terminal64.exe"), "/portable", "/config:" + str(ini)], timeout=cho_toi_da)
    except subprocess.TimeoutExpired:
        return {"loi": "qua_gio", "giay": int(time.time() - t0)}
    f = slot / (ten + ".htm")
    if not f.exists():
        return {"loi": "khong_bao_cao", "giay": int(time.time() - t0)}     # CHUA_DO_DUOC, khong phai AM
    r = CL.doc_htm(f); r["deals"] = doc_deals(f.read_bytes().decode("utf-16", errors="ignore"))
    r["file"] = f.name; r["giay"] = int(time.time() - t0)
    return r


def _doc_jsonl(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("lenh", choices=["danh-sach", "chay", "tong-ket"]); ap.add_argument("--ma-san", required=True)
    ap.add_argument("--slot"); ap.add_argument("--von", type=float, default=10000); ap.add_argument("--tien", default="USD")
    ap.add_argument("--don-bay", type=int, help="mac dinh: don bay that trong tai_khoan.json canh ma_san.json"); ap.add_argument("--top", type=int, default=2)
    ap.add_argument("--cho-toi-da", type=int, default=2400); ap.add_argument("--dd-muc-tieu", type=float, default=20.0)
    a = ap.parse_args()
    ms = json.loads(Path(a.ma_san).read_text(encoding="utf-8"))
    if a.don_bay is None:
        tk = Path(a.ma_san).with_name("tai_khoan.json")
        a.don_bay = int(json.loads(tk.read_text(encoding="utf-8")).get("don_bay") or 500) if tk.exists() else 500
    ra = GOC / "reports" / "mt5_san_chu" / re.sub(r"[^A-Za-z0-9._-]", "_", ms.get("server", "san"))
    so = ra / "so_cai.jsonl"
    viec, thieu = viec_tren_san(chon_cau_hinh(SV.doc_so_cai(), a.top), ms)
    if a.lenh == "danh-sach":
        for v in viec:
            print(json.dumps({k: v[k] for k in ("ea", "goc", "ma", "tf", "lot", "ts")}, ensure_ascii=False))
        print("%d viec; san khong co ma: %s" % (len(viec), ", ".join(thieu) or "-"))
        return
    if a.lenh == "tong-ket":
        ra.mkdir(parents=True, exist_ok=True)
        kq = ghep(_doc_jsonl(so), a.von, a.dd_muc_tieu)
        (ra / "tong_ket.json").write_text(json.dumps(kq, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps({k: kq[k] for k in ("manh_trong_bo", "bo_ghep", "he_so_lot", "lai_pct_nam_o_dd_muc_tieu")}, ensure_ascii=False, indent=1))
        return
    ra.mkdir(parents=True, exist_ok=True)
    slot = Path(a.slot); chuan_bi_ea(slot)
    da = {khoa(r) for r in _doc_jsonl(so) if not r.get("loi")}
    for n, v in enumerate(viec, 1):
        if khoa(v) in da:
            continue
        print("[%d/%d] %s %s %s lot %s" % (n, len(viec), v["ea"], v["ma"], v["tf"], v["lot"]), flush=True)
        r = chay_mot(slot, v, int(a.von), a.tien, a.don_bay, a.cho_toi_da)
        rec = {**{k: v.get(k) for k in ("ea", "goc", "ma", "tf", "ts", "pha", "lot", "nguon", "tien_moi_gia_1lot")}, **r, "server": ms.get("server"),
               "von": a.von, "tien": a.tien, "luc": time.strftime("%Y-%m-%dT%H:%M:%S")}
        with open(so, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print("   ->", r.get("loi") or "net %s lenh %s pf %s dd %s" % (r.get("net"), r.get("lenh"), r.get("pf"), r.get("dd")), flush=True)
    print("XONG. Tiep: python mt5tools/chay_lai_tren_san.py tong-ket --ma-san %s --von %s" % (a.ma_san, a.von))


if __name__ == "__main__":
    main()
