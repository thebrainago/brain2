# -*- coding: utf-8 -*-
"""Động cơ Seeker v2: hàng đợi ưu tiên có ngân sách + giới hạn độ sâu, khử trùng, chạy tiếp được.

    python -m seeker.dong_co --ngan-sach 60 --sau 2 [--nguon reddit_algotrading,mql5_forum_ru] [--chi-telegram]

Trạng thái: data/seeker_state/ (gitignored). Ý tưởng: data/seeker_state/y_tuong.jsonl.
Tóm tắt commit được: reports/seeker_v2/DIGEST.md + THONG_KE.json."""
from __future__ import annotations
import argparse, heapq, json, re, time, urllib.parse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import yaml
from . import GOC, TRANG_THAI, BAO_CAO, van_ban as VB, y_tuong as YT, telegram as TG
from .do_thi import DoThi
from .thu_thap import ThuThap

TRUY_CAP_TU_DONG = {"html", "rss", "api"}


def doc_yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


class DongCo:
    def __init__(self, thu_muc: Path = TRANG_THAI, thu_thap: ThuThap | None = None, gian_cach_s: float = 3.0):
        self.tm = Path(thu_muc); self.tm.mkdir(parents=True, exist_ok=True)
        self.nguon = {n["id"]: n for n in doc_yaml(GOC / "nguon" / "web.yaml")["nguon"]}
        self.tg_cfg = doc_yaml(GOC / "nguon" / "telegram.yaml")
        st = self._doc("trang_thai.json", {})
        self.do_thi = DoThi(doc_yaml(GOC / "tu_khoa_hat_giong.yaml"), st.get("do_thi"))
        self.da_tham: set[str] = set(st.get("da_tham", []))
        self.hang: list = [tuple(x) for x in st.get("hang", [])]; heapq.heapify(self.hang)
        self.nguon_moi: dict = st.get("nguon_moi", {})          # miền mới phát hiện -> số lần nhắc
        self.tg_bien: dict = self._doc("telegram_frontier.json", {})
        self.nhat_ky: list = []
        self.tt = thu_thap or ThuThap(self.tm / "cache", gian_cach_s=gian_cach_s, nhat_ky=self.nhat_ky)
        self.tt.nhat_ky = self.nhat_ky
        self.dem = Counter(st.get("dem", {}))
        self.y_moi: list[dict] = []

    # ---------------- lưu / đọc ----------------
    def _doc(self, ten, mac_dinh):
        p = self.tm / ten
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else mac_dinh

    def luu(self):
        st = {"do_thi": self.do_thi.trang_thai(), "da_tham": sorted(self.da_tham)[-50000:],
              "hang": self.hang[:5000], "nguon_moi": self.nguon_moi, "dem": dict(self.dem)}
        (self.tm / "trang_thai.json").write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")
        (self.tm / "telegram_frontier.json").write_text(json.dumps(self.tg_bien, ensure_ascii=False, indent=1), encoding="utf-8")
        with open(self.tm / "y_tuong.jsonl", "a", encoding="utf-8") as f:
            for y in self.y_moi: f.write(json.dumps(y, ensure_ascii=False) + "\n")
        with open(self.tm / "nhat_ky.jsonl", "a", encoding="utf-8") as f:
            for x in self.nhat_ky: f.write(json.dumps(x, ensure_ascii=False) + "\n")
        self.y_moi, self.nhat_ky[:] = [], []

    # ---------------- hàng đợi ----------------
    def day(self, uu_tien: float, url: str, nguon: str, nn: str, sau: int, loai: str = "trang"):
        if url in self.da_tham:
            return
        heapq.heappush(self.hang, (-round(uu_tien, 4), url, nguon, nn, sau, loai))

    def gieo(self, chon: list[str] | None = None, so_truy_van: int = 3, chi_telegram=False):
        if not chi_telegram:
            for nid, n in self.nguon.items():
                if n["truy_cap"] not in TRUY_CAP_TU_DONG or (chon and nid not in chon) or "{kenh}" in n["url"]:
                    continue
                p = n.get("uu_tien", 0.5)
                if "{q}" not in n["url"]:
                    self.day(p, n.get("rss") or n["url"], nid, n["ngon_ngu"], 0)
                mau = n.get("tim_kiem") or (n["url"] if "{q}" in n["url"] else None)
                if mau:
                    for q in self.do_thi.truy_van(n["ngon_ngu"], so_truy_van):
                        self.day(p * 0.9, mau.replace("{q}", urllib.parse.quote(q)), nid, n["ngon_ngu"], 0, "tim")
        kenh = [k["ten"] for k in (self.tg_cfg.get("kenh") or []) if k.get("ten") and k.get("cach", "cong_khai") == "cong_khai"]
        tu_kp = sorted(self.tg_bien.items(), key=lambda x: -x[1].get("diem", 0))
        for k in kenh: self.day(0.95, TG.url_trang(k), "telegram:" + k, "*", 0, "tg")
        for k, v in tu_kp[: (self.tg_cfg.get("gioi_han") or {}).get("kenh_moi_luot", 40)]:
            if not v.get("da_doc") and v.get("diem", 0) >= 2:
                self.day(0.5 + min(0.4, v["diem"] / 50), TG.url_trang(k), "telegram:" + k, "*", 1, "tg")

    # ---------------- xử lý ----------------
    def _xu_ly_van_ban(self, txt, nguon, nn, url, ngay, tieu_de=""):
        for k in re.findall(r"t\.me/(?:s/)?([A-Za-z][A-Za-z0-9_]{4,31})", txt):
            k = TG.chuan_ten(k)
            if k: self.tg_bien.setdefault(k, {"diem": 0, "tu": []})["diem"] += 2
        self.do_thi.hoc(txt, nn)
        y = YT.rut(txt, self.do_thi.khai_niem_trong(txt), nguon, nn, url, ngay, tieu_de)
        if y:
            self.y_moi.append(y); self.dem["y_tuong"] += 1
        return y

    def _xu_ly_tg(self, html, url, nguon, sau, gioi_han_sau):
        kenh = nguon.split(":", 1)[1]
        r = TG.doc_trang(html, kenh, tuple((self.tg_cfg.get("gioi_han") or {}).get("duoi_tep", [])) or (".ex4",))
        self.tg_bien.setdefault(kenh, {"diem": 0})["da_doc"] = True
        self.dem["tg_tin"] += len(r["tin"])
        for t in r["tin"]:
            if t["van_ban"]:
                self._xu_ly_van_ban(t["van_ban"], nguon, "*", t["url"], t["ngay"])
        if r["tep"]:
            with open(self.tm / "telegram_tep.jsonl", "a", encoding="utf-8") as f:
                for x in r["tep"]: f.write(json.dumps({"kenh": kenh, **x}, ensure_ascii=False) + "\n")
            self.dem["tg_tep"] += len(r["tep"])
        for k, d in r["kenh_moi"].items():
            v = self.tg_bien.setdefault(k, {"diem": 0, "tu": []})
            v["diem"] += d; v.setdefault("tu", []); v["tu"] = sorted(set(v["tu"]) | {kenh})[:20]
        trang = int(url.split("before=")[1]) if "before=" in url else None
        so_trang = (self.tg_cfg.get("gioi_han") or {}).get("trang_moi_kenh", 3)
        da = self.dem.get("tg_trang:" + kenh, 0) + 1; self.dem["tg_trang:" + kenh] = da
        if r["id_nho_nhat"] and da < so_trang and r["id_nho_nhat"] != trang:
            self.day(0.6, TG.url_trang(kenh, r["id_nho_nhat"]), nguon, "*", sau, "tg")

    def chay(self, ngan_sach: int = 50, sau_toi_da: int = 2, lien_ket_moi_trang: int = 8, luu_moi: int = 10):
        t0 = time.time(); n = 0
        while self.hang and n < ngan_sach:
            uu, url, nguon, nn, sau, loai = heapq.heappop(self.hang)
            if url in self.da_tham:
                continue
            self.da_tham.add(url); n += 1
            txt = self.tt.tai(url)
            self.dem["yeu_cau"] += 1
            if txt is None:
                self.dem["that_bai:" + nguon.split(":")[0]] += 1; continue
            self.dem["ok:" + nguon.split(":")[0]] += 1
            if loai == "tg":
                self._xu_ly_tg(txt, url, nguon, sau, sau_toi_da); continue
            tr = VB.tach_json(txt) if txt.lstrip()[:1] in "[{" else VB.tach_trang(txt, url)
            if tr["muc"]:
                for m in tr["muc"]:
                    self._xu_ly_van_ban(m["tieu_de"] + "\n" + m["van_ban"], nguon, nn, m["url"] or url, m["ngay"], m["tieu_de"])
            else:
                self._xu_ly_van_ban(tr["van_ban"][:20000], nguon, nn, url, None, tr["tieu_de"])
            # mở rộng theo liên kết
            mien_goc = urllib.parse.urlsplit(url).netloc
            them = 0
            for lk, chu in tr["lien_ket"]:
                m = urllib.parse.urlsplit(lk).netloc
                if "t.me/" in lk:
                    k = TG.chuan_ten(lk.split("t.me/")[-1])
                    if k: self.tg_bien.setdefault(k, {"diem": 0, "tu": []})["diem"] += 2
                    continue
                if m and m != mien_goc and not m.endswith(("reddit.com", "redditmedia.com", "redd.it", "github.com", "githubusercontent.com")):
                    self.nguon_moi[m] = self.nguon_moi.get(m, 0) + 1
                    continue
                if sau + 1 > sau_toi_da or them >= lien_ket_moi_trang:
                    continue
                kn = self.do_thi.khai_niem_trong(chu + " " + lk.replace("-", " "))
                if kn or loai == "tim" or (tr["muc"] and lk in [x["url"] for x in tr["muc"]][:lien_ket_moi_trang]):
                    self.day(-uu * 0.7 + 0.1 * len(kn), lk, nguon, nn, sau + 1); them += 1
            if n % luu_moi == 0:
                self.do_thi.thang_cap(); self.luu()
        moi = self.do_thi.thang_cap()
        self.dem["giay"] += round(time.time() - t0, 1)
        for k, v in self.tt.dem.items(): self.dem["tai_" + k] += v
        self.luu()
        return {"so_yeu_cau": n, "tu_khoa_moi": moi}

    # ---------------- báo cáo commit được ----------------
    def bao_cao(self, thu_muc: Path = BAO_CAO, toi_da=40):
        thu_muc.mkdir(parents=True, exist_ok=True)
        ys, thay = [], set()
        p = self.tm / "y_tuong.jsonl"
        if p.exists():
            for d in p.read_text(encoding="utf-8").splitlines():
                y = json.loads(d)
                if y["id"] not in thay: thay.add(y["id"]); ys.append(y)
        theo_nguon = Counter(y["nguon"].split(":")[0] for y in ys)
        theo_pp = Counter(k for y in ys for k in y["phuong_phap"])
        tk_moi = {q: v for q, v in self.do_thi.da_biet.items() if v["nguon_goc"] == "tu_kham_pha"}
        tk = {"cap_nhat": datetime.now(timezone.utc).isoformat(timespec="seconds"), "so_y_tuong": len(ys),
              "theo_nguon": dict(theo_nguon), "theo_phuong_phap": dict(theo_pp), "dem": dict(self.dem),
              "tu_khoa_tu_kham_pha": len(tk_moi), "kenh_tg_bien": len(self.tg_bien),
              "mien_moi_top": dict(Counter(self.nguon_moi).most_common(25))}
        (thu_muc / "THONG_KE.json").write_text(json.dumps(tk, ensure_ascii=False, indent=1), encoding="utf-8")
        L = ["# Seeker v2 — bản tóm tắt (digest)", "", f"Cập nhật: {tk['cap_nhat']} (UTC). Số liệu dưới đây là ĐO THẬT từ data/seeker_state/.", "",
             f"- Ý tưởng (đã khử trùng): **{len(ys)}**", f"- Yêu cầu HTTP tích lũy: {self.dem.get('yeu_cau', 0)}; bị chặn: {self.dem.get('tai_bi_chan', 0)}; robots cấm: {self.dem.get('tai_robots_cam', 0)}",
             f"- Từ khóa tự khám phá đã thăng cấp: {len(tk_moi)}", f"- Kênh Telegram trong biên khám phá: {len(self.tg_bien)}", "",
             "## Theo nguồn", *[f"- {k}: {v}" for k, v in theo_nguon.most_common()], "",
             "## Theo phương pháp", *[f"- {k}: {v}" for k, v in theo_pp.most_common()], "",
             "## Từ khóa tự khám phá", *[f"- `{q}` → {v['khai_niem']} (điểm {v['diem']:.2f})" for q, v in list(tk_moi.items())[:30]], "",
             "## Ứng viên từ khóa hàng đầu (chưa thăng cấp)",
             *[f"- `{c}` (điểm {v['diem']:.2f}, {v['lan']} tài liệu, gắn {v['khai_niem']})" for c, v in sorted(self.do_thi.ung_vien.items(), key=lambda x: -x[1]['diem'])[:20]], "",
             "## Miền mới được nhắc tới (ứng viên nguồn)", *[f"- {m}: {c}" for m, c in Counter(self.nguon_moi).most_common(15)], "",
             "## Kênh Telegram tự khám phá (top)", *[f"- @{k}: điểm {v.get('diem')} (từ {', '.join(v.get('tu', [])[:3])})" for k, v in sorted(self.tg_bien.items(), key=lambda x: -x[1].get('diem', 0))[:15]], "",
             f"## {min(toi_da, len(ys))} ý tưởng tin cậy nhất", ""]
        for y in sorted(ys, key=lambda y: -y["do_tin_cay"])[:toi_da]:
            L.append(f"- [{y['nguon']}/{y['ngon_ngu']}] {', '.join(y['phuong_phap'])} — tin cậy {y['do_tin_cay']} — {y['url']}")
            if y["tham_so"]: L.append(f"  - tham số: {json.dumps(y['tham_so'], ensure_ascii=False)}")
        (thu_muc / "DIGEST.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        return tk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ngan-sach", type=int, default=50); ap.add_argument("--sau", type=int, default=2)
    ap.add_argument("--nguon", default=""); ap.add_argument("--chi-telegram", action="store_true")
    ap.add_argument("--gian-cach", type=float, default=3.0)
    a = ap.parse_args()
    dc = DongCo(gian_cach_s=a.gian_cach)
    dc.gieo([x for x in a.nguon.split(",") if x] or None, chi_telegram=a.chi_telegram)
    r = dc.chay(a.ngan_sach, a.sau)
    print(json.dumps({**r, **dc.bao_cao()}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
