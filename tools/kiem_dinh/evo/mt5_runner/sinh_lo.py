# -*- coding: utf-8 -*-
"""Sinh lo EA cho 289 khang_dinh CHO_KIEM (Evo 15/11/2026).

Moi khang_dinh = 1 template. Chon 1 gia_thuyet dai dien/template (uu tien:
pass tieu chi da sua -> p nho -> sharpe lon, theo danh_gia_lai_ket_qua.json),
dich qua nhan/dich_mq5 (template DSL), gom theo (symbol MT5, khung) thanh MOT EA
chay optimization tren InpMaCoChe. Template viet tay trong nhan/mau.py -> bo, ghi ly do.
Ra: out/<nhom>.mq5 + out/manifest.json. Chi doc nao.db.
"""
import json, os, sqlite3, sys, collections
GOC = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.insert(0, GOC)
from nhan import dich_mq5 as D, ngu_phap as NP
from pathlib import Path
# Kho DSL song (chua commit) nam o repo chinh /workspace/brain2; worktree co ban cu thieu 289 template moi.
NP.KHO_CO_CHE = Path(os.environ.get("KHO_DSL", "/workspace/brain2/config/co_che_dsl.json"))

DB = os.environ.get("NAO_DB", "/workspace/brain2/nao.db")
OUT = os.path.join(os.path.dirname(__file__), "out")
SYM = {  # tai_san brain2 -> ten tren XM demo 345930355 (uu tien # roi micro)
    "XM_US100CASH": "US100Cash#", "US100CASH": "US100Cash#", "US100": "US100Cash#",
    "US500CASH": "US500Cash#", "US500": "US500Cash#", "XM_US500CASH": "US500Cash#",  # "US500Cash" khong co tren tai khoan nay
    "US30CASH": "US30Cash", "US30": "US30Cash", "DE40": "GER40Cash", "GER40": "GER40Cash",
    "GER40CASH": "GER40Cash", "XAUUSD": "GOLD.i#", "GOLD": "GOLD.i#", "UK100": "UK100Cash",
    "JP225": "JP225Cash", "EU50": "EU50Cash", "FRA40": "FRA40Cash",
}
CO_SAN = set("""AUDCAD# AUDCHF# AUDJPY# AUDNZD# AUDUSD# CADJPY# CHFJPY# EURAUD# EURCAD# EURCHF# EURGBP#
EURUSD# GBPCAD# GBPNZD# GBPUSD# NZDCAD# NZDUSD# USDCAD# USDCHF# USDJPY#""".split())
MICRO = set("CADCHF EURJPY EURNZD GBPAUD GBPCHF GBPJPY NZDCHF NZDJPY".split())


def ma_mt5(ts):
    t = ts.upper()
    if t in SYM: return SYM[t]
    if t + "#" in CO_SAN: return t + "#"
    if t in MICRO: return t + "micro"
    return None


def main():
    c = sqlite3.connect("file:%s?mode=ro" % DB, uri=True); c.row_factory = sqlite3.Row
    kd = [dict(r) for r in c.execute("SELECT id, gt_ma, hang FROM khang_dinh WHERE trang_thai='CHO_KIEM'")]
    dg = {r["ma"]: r for r in json.load(open(os.path.join(GOC, "tools/kiem_dinh/evo/danh_gia_lai_ket_qua.json")))}
    kho = {s["ten"]: s for s in NP.doc_kho()}

    def diem(g):
        r = dg.get(g["ma"]) or {}; a = r.get("A") or {}
        ok = (a.get("so_lenh", 0) >= 30 and (a.get("pf_lenh") or 0) >= 1.2 and (a.get("sharpe") or 0) >= .3
              and (a.get("tb_lenh_pct") or 0) > 0 and (a.get("p") or 1) <= .05)
        return (0 if ok else 1, 0 if a else 1, a.get("p") if a.get("p") is not None else 1, -(a.get("sharpe") or -9))

    nhom, bo = collections.defaultdict(list), []
    for k in kd:
        t = k["gt_ma"]
        gts = [dict(r) for r in c.execute("SELECT ma, template, tham_so, tai_san, khung FROM gia_thuyet WHERE template=?", (t,))]
        if t not in kho:
            bo.append({"kd": k["id"], "template": t, "vi_sao": ("khong co trong kho DSL" + ("" if gts else " va chua co gia_thuyet nao")), "so_gt": len(gts)}); continue
        if not gts:
            bo.append({"kd": k["id"], "template": t, "vi_sao": "DSL co nhung chua co gia_thuyet (chua chon tai san/tham so)"}); continue
        gts = [g for g in gts if ma_mt5(g["tai_san"]) and g["khung"] in ("H1", "H4", "D1")]
        if not gts:
            bo.append({"kd": k["id"], "template": t, "vi_sao": "khong co gia_thuyet tren ma/khung chay duoc tren XM"}); continue
        g = sorted(gts, key=diem)[0]
        sp = NP.ap_tham_so(kho[t], json.loads(g["tham_so"] or "{}"))
        sp = dict(sp, ten=g["ma"], _kd=k["id"], _template=t)
        nhom[(ma_mt5(g["tai_san"]), g["khung"])].append(sp)

    os.makedirs(OUT, exist_ok=True)
    man = {"nhom": [], "bo": bo}
    for (sym, kh), specs in sorted(nhom.items()):
        ten = "EvoLo_%s_%s" % (sym.replace("#", "").replace(".", ""), kh)
        try:
            ma, dat = D.sinh_ea(specs, ten, khung=kh)
        except D.KhongDichDuoc as e:
            dat = []
        for s in specs:
            if s.get("_khong_dich"):
                bo.append({"kd": s["_kd"], "template": s["_template"], "vi_sao": "dich_mq5: " + s["_khong_dich"]})
        if not dat or len(dat) <= 2: continue
        open(os.path.join(OUT, ten + ".mq5"), "w", encoding="utf-8").write(ma)
        man["nhom"].append({"ea": ten, "symbol": sym, "khung": kh,
                            "co_che": [{"i": i, "ten": d["ten"], "kd": d.get("_kd"), "template": d.get("_template")}
                                       for i, d in enumerate(dat)]})
    json.dump(man, open(os.path.join(OUT, "manifest.json"), "w"), ensure_ascii=False, indent=1)
    n = sum(len(x["co_che"]) - 2 for x in man["nhom"])
    print("khang_dinh", len(kd), "dich duoc", n, "trong", len(man["nhom"]), "EA; bo", len(bo))
    print(collections.Counter(b["vi_sao"][:60] for b in bo).most_common(8))


if __name__ == "__main__":
    main()
