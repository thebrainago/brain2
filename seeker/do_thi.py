# -*- coding: utf-8 -*-
"""Đồ thị khái niệm: hạt giống đa ngôn ngữ -> sau mỗi lượt đọc rút cụm từ ứng viên bằng TF-IDF
+ đồng xuất hiện với khái niệm đã biết, chấm độ mới, đưa cụm tốt vào biên (frontier) tìm kiếm.
Không dùng LLM trả phí."""
from __future__ import annotations
import hashlib, math
from collections import Counter, defaultdict
from . import van_ban as VB


class DoThi:
    def __init__(self, hat_giong: dict, trang_thai: dict | None = None):
        tt = trang_thai or {}
        self.hat_giong = hat_giong
        self.da_biet: dict[str, dict] = tt.get("da_biet") or {}
        if not self.da_biet:
            for kn, theo_nn in hat_giong.items():
                for nn, ds in theo_nn.items():
                    for q in ds:
                        self.da_biet[q.lower()] = {"khai_niem": kn, "ngon_ngu": nn, "nguon_goc": "hat_giong", "diem": 1.0}
        self.df: Counter = Counter(tt.get("df") or {})
        self.so_tai_lieu: int = tt.get("so_tai_lieu", 0)
        self.dong_xh: dict[str, Counter] = defaultdict(Counter, {k: Counter(v) for k, v in (tt.get("dong_xh") or {}).items()})
        self.ung_vien: dict[str, dict] = tt.get("ung_vien") or {}
        self.da_hoc: set[str] = set(tt.get("da_hoc") or [])

    def trang_thai(self) -> dict:
        # Giới hạn kích thước: giữ 20k cụm có df cao nhất
        df = dict(self.df.most_common(20000))
        return {"da_biet": self.da_biet, "df": df, "so_tai_lieu": self.so_tai_lieu,
                "dong_xh": {k: dict(v.most_common(50)) for k, v in self.dong_xh.items()},
                "da_hoc": sorted(self.da_hoc)[-50000:],
                "ung_vien": dict(sorted(self.ung_vien.items(), key=lambda x: -x[1]["diem"])[:2000])}

    def khai_niem_trong(self, van_ban: str) -> list[str]:
        t = van_ban.lower()
        return sorted({v["khai_niem"] for q, v in self.da_biet.items() if q in t})

    def hoc(self, van_ban: str, ngon_ngu: str) -> list[dict]:
        """Cập nhật thống kê bằng một tài liệu; trả các cụm ứng viên mới của tài liệu này (đã chấm)."""
        h = hashlib.sha1(van_ban.strip().lower().encode()).hexdigest()[:16]
        if h in self.da_hoc:          # cùng nội dung đã học -> không đếm lại
            return []
        self.da_hoc.add(h)
        tok = VB.token(van_ban)
        if len(tok) < 5:
            return []
        cum = Counter(VB.cum_tu(tok, 2)) + Counter(VB.cum_tu(tok, 3)) + Counter(tok)
        self.so_tai_lieu += 1
        for c in cum:
            self.df[c] += 1
        kn = self.khai_niem_trong(van_ban)
        ra = []
        tong = sum(cum.values()) or 1
        for c, n in cum.most_common(400):
            if c in self.da_biet or len(c) < 4:
                continue
            for k in kn:
                self.dong_xh[k][c] += 1
            idf = math.log((1 + self.so_tai_lieu) / (1 + self.df[c])) + 1
            tfidf = (n / tong) * idf
            gan = sum(self.dong_xh[k][c] for k in kn)        # đồng xuất hiện với khái niệm đã biết
            moi = 1.0 / (1 + self.df[c] / max(1, self.so_tai_lieu) * 10)   # hiếm trên toàn kho -> mới
            diem = tfidf * 100 * (1 + math.log1p(gan)) * moi * (1 if kn else 0.3)
            uv = self.ung_vien.setdefault(c, {"diem": 0.0, "lan": 0, "ngon_ngu": ngon_ngu, "khai_niem": []})
            uv["diem"] = round(max(uv["diem"], diem) + 0.05 * uv["lan"], 4); uv["lan"] += 1
            uv["khai_niem"] = sorted(set(uv["khai_niem"]) | set(kn))
            ra.append({"cum": c, **uv})
        return ra

    def thang_cap(self, toi_da: int = 10, nguong: float = 1.0, lan_toi_thieu: int = 3) -> list[str]:
        """Đưa ứng viên tốt nhất (xuất hiện ≥ lan_toi_thieu tài liệu, gắn với ≥1 khái niệm) thành từ khóa đã biết."""
        chon = [(c, v) for c, v in self.ung_vien.items()
                if v["lan"] >= lan_toi_thieu and v["khai_niem"] and v["diem"] >= nguong and c.count(" ") == 1]
        chon.sort(key=lambda x: -x[1]["diem"])
        moi = []
        for c, v in chon[:toi_da]:
            self.da_biet[c] = {"khai_niem": v["khai_niem"][0], "ngon_ngu": v["ngon_ngu"], "nguon_goc": "tu_kham_pha", "diem": v["diem"]}
            self.ung_vien.pop(c, None); moi.append(c)
        return moi

    def truy_van(self, ngon_ngu: str, toi_da: int = 5) -> list[str]:
        ds = [(q, v) for q, v in self.da_biet.items() if v["ngon_ngu"] in (ngon_ngu, "*")]
        ds.sort(key=lambda x: (x[1]["nguon_goc"] != "tu_kham_pha", -x[1]["diem"]))
        return [q for q, _ in ds[:toi_da]]
