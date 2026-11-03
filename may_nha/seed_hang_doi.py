# -*- coding: utf-8 -*-
"""Box: gieo việc vào hang_doi/can_test (03/11/2026). python may_nha/seed_hang_doi.py -> in số việc + giờ ước."""
from __future__ import annotations
import glob, json, re, sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC / "may_nha"))
import hang_doi_git as HD  # noqa: E402

HE_CSV = [("skeadd17", "H1"), ("skea154", "H4"), ("2600ea", "H1"), ("mql5e52a", "H1"), ("skea61c", "H4"), ("skea3279", "H1"),
          ("b0be91", "H4"), ("ghep60ff", "H1"), ("ghep0bf2", "H4"), ("ghepe9b41", "H4"), ("skst299b", "H1"), ("skst299b", "H4"),
          ("mql5344", "H1")]
K_CSV = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]
K_DN = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]
DN = [("BRAIN_DN_RoDCAHedge", m) for m in ("NZDCADmicro", "AUDCADmicro", "EURGBPmicro")] + [("BRAIN_DN_LuoiHedgeTP", "AUDCADmicro")]


def viec_ong_dan() -> dict:
    out = {}
    for f in glob.glob(str(GOC / "reports/**/*.jsonl"), recursive=True):
        try:
            for l in open(f, encoding="utf-8"):
                if '"nguon": "ong_dan"' not in l or '"san": "XM"' not in l:
                    continue
                v = json.loads(l)
                if v.get("csv_vao") and not v.get("toi_uu") and not v.get("tang") and v.get("ten", "").endswith("_XM_CSV"):
                    out.setdefault(v["ten"], v)
        except (OSError, ValueError):
            pass
    return out


def giay_da_do() -> dict:
    g: dict = {}
    p = GOC / "reports/mt5_lien_tuc/so_cai.jsonl"
    for l in p.open(encoding="utf-8") if p.exists() else []:
        try:
            r = json.loads(l)
        except ValueError:
            continue
        if r.get("ten") and r.get("giay"):
            g[r["ten"]] = max(g.get(r["ten"], 0), r["giay"])
    return g


def specs() -> list[dict]:
    od, gd, out = viec_ong_dan(), giay_da_do(), []
    for tien_to, tf in HE_CSV:
        ten = next((t for t in sorted(od) if t.startswith("od_" + tien_to)), None)
        if not ten:
            print("KHÔNG thấy việc ống dẫn cho", tien_to); continue
        v = od[ten]
        out.append({"id": "lot_%s_%s" % (ten[3:-7], tf), "loai": "mt5_backtest", "uu_tien": 80, "che_do": "ong_dan_csv",
                    "ea_file": v.get("ea_file", "BRAIN_XuLiLenh"), "ma": v["ma"], "tf": tf, "tu": v.get("tu"), "den": v.get("den") or "2026.10.01",
                    "model": 4, "von": int(v.get("von") or 1000), "tien": "USD", "don_bay": int(v.get("don_bay") or 500),
                    "ts": v["ts"], "tham_so_lot": "InpLot0", "csv_vao": v["csv_vao"].replace("\\", "/"), "he_so_lot": K_CSV,
                    "uoc_phut": max(5, round(gd.get(ten, 600) / 60 * 1.2)), "nguon": v.get("the_id"),
                    "ghi_chu": "chạy lại nâng lot trên toàn dải CSV (dài nhất có), tick thật, XM"})
    for ea, ma in DN:
        ts = dict(x.split("=", 1) for x in (GOC / "ea_demo" / (ea + ".set")).read_text(encoding="utf-8").split() if "=" in x)
        out.append({"id": "lot_%s_%s_H1" % (ea[9:], ma[:6]), "loai": "mt5_backtest", "uu_tien": 70, "che_do": "ea_goc", "ea_file": ea,
                    "ma": ma, "tf": "H1", "tu": "2016.01.01", "den": "2026.10.01", "model": 4, "von": 10000, "tien": "USD",
                    "don_bay": 500, "ts": ts, "tham_so_lot": "LotMoi1000", "he_so_lot": K_DN, "uoc_phut": 60,
                    "ghi_chu": "EA dịch ngược từ tín hiệu MQL5, dải dài nhất 2016–2026, tick thật"})
    em = GOC / "data/cong_khai/ea_market.json"
    loc = {x["id"]: x for x in json.loads((GOC / "data/cong_khai/loc_chat.json").read_text(encoding="utf-8"))}
    da = set()
    for i, s in enumerate(json.loads(em.read_text(encoding="utf-8")) if em.exists() else []):
        for p in s["san_pham"]:
            try:
                gia = float(p["gia_usd"])
            except ValueError:
                gia = 0
            if p["nen_tang"] != "MT5" or not p["free_demo"] or not p["la_ea"] or gia <= 0 or p["url"] in da:
                continue
            da.add(p["url"]); pid = p["url"].rstrip("/").split("/")[-1]
            ma = (loc.get(s["id"], {}).get("ma") or ["EURUSD"])[0]
            out.append({"id": "demo_%s" % re.sub(r"[^A-Za-z0-9]", "", pid), "loai": "mql5_demo_download", "uu_tien": 60 - i,
                        "url_product": p["url"], "ten_product": p["ten"].split("|")[0].strip(), "gia_usd": p["gia_usd"],
                        "tin_hieu_id": s["id"], "ma": ma + "micro" if len(ma) == 6 else ma, "tf": "H1", "uoc_phut": 2})
    return out


if __name__ == "__main__":
    s = specs()
    n = HD.ghi_cuc_bo(GOC, s)
    tong = sum(HD.uoc_gio(v) for v in s)
    print("viec", len(s), "moi", n, "gio_uoc %.1f" % tong, "mt5_runs", sum(len(v.get("he_so_lot") or []) for v in s))
