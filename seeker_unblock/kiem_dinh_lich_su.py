"""kiem_dinh_lich_su.py - kiem dinh OFFLINE CSV lich su Myfxbook doi chieu HTML tho da luu + meta.
Mot he chi duoc gan VERIFIED khi: co HTML tho cua chinh tai khoan do chua <th> (thu tu cot that), thu tu cot
trung voi cot ma CSV dang dung, va cac dong trong HTML tho trung khop tung truong voi CSV theo record id.
Khong co HTML tho -> UNVERIFIED (cot chi suy tu du lieu), khong dua so phi/PASS.
Chay: python3 kiem_dinh_lich_su.py RAW_DIR CSV_DIR oid1 oid2 ... > ket_qua.json"""
import sys, os, glob, json, csv, statistics as st, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myfxbook as M
FIELDS = ["open_time_ms", "close_time_ms", "symbol", "action", "open_price", "close_price", "pips", "profit"]
FEE = "/workspace/brain2/config/phi_xm_micro.json"

def check(raw_dir, csv_dir, oid):
    out = {"oid": oid}
    meta = json.load(open(os.path.join(csv_dir, f"{oid}_meta.json")))
    rows = list(csv.DictReader(open(os.path.join(csv_dir, f"{oid}.csv"), encoding="utf-8")))
    rec = [r["record"] for r in rows]
    out["meta"] = {k: meta.get(k) for k in ("total_reported", "rows", "trades", "pages", "cols", "sua_cot")}
    out["so_dong_csv"] = len(rows); out["record_trung_lap"] = len(rec) - len(set(rec))
    out["du_dong_so_voi_tong_bao_cao"] = len(rows) == meta.get("total_reported")
    tr = [r for r in rows if r["action"] in ("Buy", "Sell")]
    out["so_lenh_buy_sell"] = len(tr); out["dong_khac"] = collections.Counter(r["action"] for r in rows if r not in tr).most_common()
    out["co_cot_lot"] = any(r.get("lots") for r in tr)
    raws = [f for f in glob.glob(os.path.join(raw_dir, "*")) if oid in os.path.basename(f) and "HistoryFirstPage" in f]
    if not raws:
        out["trang_thai"] = "UNVERIFIED"; out["ly_do"] = "khong co HTML tho chua tieu de cot cua tai khoan nay; thu tu cot chi suy tu du lieu"
    else:
        h = M.load_history_html(raws[0]); cols = M.head_cols(h); prs = M.parse_rows(h, cols)
        out["cot_tu_html_tho"] = cols
        used = meta.get("cols")
        same = [c for c in (used or M.OLD)] == [c for c in cols][:len(used or M.OLD)]
        out["cot_csv_trung_html"] = same
        by = {r["record"]: r for r in rows}; khop = lech = 0; vd = []
        for p in prs:
            c = by.get(p["record"])
            if not c: lech += 1; vd.append((p["record"], "thieu trong csv")); continue
            bad = [f for f in FIELDS if (p[f] or "").replace(",", "") != (c[f] or "").replace(",", "")]
            if bad: lech += 1; vd.append((p["record"], bad))
            else: khop += 1
        out["doi_chieu_html_tho"] = {"so_dong_html": len(prs), "khop": khop, "lech": lech, "vi_du_lech": vd[:5]}
        out["trang_thai"] = "VERIFIED" if (same and lech == 0 and out["du_dong_so_voi_tong_bao_cao"] and out["record_trung_lap"] == 0) else "UNVERIFIED"
        out["pham_vi_xac_minh"] = ("thu tu cot: tu <th> HTML tho trang 1 (cung tai khoan, cac trang sau cung bang); "
                                   f"gia tri: {khop}/{len(prs)} dong trang 1 khop tung truong; cac trang 2..N chi kiem dem dong/trung lap")
    # kha nang do phi XM
    fee = json.load(open(FEE)); syms = collections.Counter(r["symbol"] for r in tr)
    co = {s: n for s, n in syms.items() if s.upper().replace(".", "").replace("+", "") in fee}
    out["ma_co_phi_xm"] = co; out["ty_le_lenh_co_phi_xm"] = round(sum(co.values()) / max(len(tr), 1), 4)
    out["ma_chinh"] = syms.most_common(6)
    return out

if __name__ == "__main__":
    raw, d = sys.argv[1], sys.argv[2]
    print(json.dumps([check(raw, d, o) for o in sys.argv[3:]], ensure_ascii=False, indent=1))
