# -*- coding: utf-8 -*-
"""Lớp an toàn: mọi thao tác MXH đều phải đi qua đây."""
from __future__ import annotations
import datetime as _dt, json, os, random, re, time
from pathlib import Path

CAM_TUYET_DOI = frozenset({"dang_bai", "binh_luan", "nhan_tin", "nhap_mat_khau", "thich", "chia_se", "tra_loi"})
DAU_HIEU_DUNG = re.compile(r"captcha|checkpoint|verify (?:it'?s|you are) (?:you|human)|unusual activity|"
                           r"security check|xác minh|đáng ngờ|подтвердите|too many requests|rate limit|"
                           r"temporarily (?:blocked|restricted)|tạm thời bị chặn|FloodWait", re.I)


class DungLai(Exception):
    """Gặp captcha / checkpoint / bị hạn chế: dừng toàn bộ phiên, ghi log, KHÔNG thử vượt."""


class VuotTran(Exception):
    pass


class HanhDongCam(Exception):
    pass


def doc_cau_hinh(p: Path | None = None) -> dict:
    import yaml
    goc = Path(__file__).with_name("cau_hinh.yaml")
    ch = yaml.safe_load(goc.read_text(encoding="utf-8"))
    rieng = p or Path(__file__).with_name("cau_hinh_rieng.yaml")
    if rieng.exists():
        ch.update(yaml.safe_load(rieng.read_text(encoding="utf-8")) or {})
    ch["thu_muc_ho_so"] = os.path.expandvars(os.path.expanduser(ch["thu_muc_ho_so"]))
    return ch


class AnToan:
    def __init__(self, cau_hinh: dict, tep_trang_thai: Path, ngu=time.sleep, hom_nay=None):
        self.ch = cau_hinh; self.p = Path(tep_trang_thai); self.ngu = ngu
        self.hom_nay = hom_nay or (lambda: _dt.date.today().isoformat())
        self.st = json.loads(self.p.read_text(encoding="utf-8")) if self.p.exists() else {}
        self.chay_thu = bool(cau_hinh.get("chay_thu", True))
        self.nhat_ky: list[dict] = []

    def _dem(self, nen_tang, hd):
        ngay = self.st.setdefault(self.hom_nay(), {})
        return ngay.setdefault(nen_tang, {}).get(hd, 0)

    def _ghi(self, nen_tang, hd, doi_tuong, ket_qua):
        ngay = self.st.setdefault(self.hom_nay(), {}).setdefault(nen_tang, {})
        ngay[hd] = ngay.get(hd, 0) + (1 if ket_qua in ("da_lam", "chay_thu") else 0)
        self.nhat_ky.append({"luc": _dt.datetime.now().isoformat(timespec="seconds"), "nen_tang": nen_tang,
                             "hanh_dong": hd, "doi_tuong": doi_tuong, "ket_qua": ket_qua})
        self.p.parent.mkdir(parents=True, exist_ok=True)
        self.p.write_text(json.dumps(self.st, ensure_ascii=False, indent=1), encoding="utf-8")
        with open(self.p.with_suffix(".log.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(self.nhat_ky[-1], ensure_ascii=False) + "\n")

    def cho_phep(self, nen_tang: str, hd: str) -> bool:
        """Kiểm tra trước. Ném lỗi nếu hành động bị cấm; trả False nếu đã chạm trần ngày."""
        if hd in CAM_TUYET_DOI or hd not in self.ch.get("hanh_dong_cho_phep", []):
            raise HanhDongCam(hd)
        tran = (self.ch.get("gioi_han_ngay") or {}).get(hd)
        return tran is None or self._dem(nen_tang, hd) < tran

    def thuc_hien(self, nen_tang: str, hd: str, doi_tuong: str, ham) -> str:
        """Chạy `ham()` nếu được phép; ở chế độ chạy thử với hành động có hậu quả (theo dõi/xin vào) thì KHÔNG chạy."""
        if not self.cho_phep(nen_tang, hd):
            self._ghi(nen_tang, hd, doi_tuong, "vuot_tran"); return "vuot_tran"
        co_hau_qua = hd in ("theo_doi", "xin_vao_nhom")
        if co_hau_qua and self.chay_thu:
            self._ghi(nen_tang, hd, doi_tuong, "chay_thu"); return "chay_thu"
        ham()
        self._ghi(nen_tang, hd, doi_tuong, "da_lam")
        self.nghi("sau_follow_join" if co_hau_qua else "giua_thao_tac")
        return "da_lam"

    def nghi(self, loai: str = "giua_thao_tac"):
        a, b = (self.ch.get("nhip") or {}).get(loai, [3, 8])
        self.ngu(random.uniform(a, b))

    def kiem_trang(self, van_ban: str, url: str = ""):
        """Gọi sau mỗi lần tải trang. Thấy dấu hiệu captcha/checkpoint -> DungLai."""
        if "checkpoint" in url or "/challenge" in url or DAU_HIEU_DUNG.search(van_ban[:20000] or ""):
            self.nhat_ky.append({"luc": _dt.datetime.now().isoformat(timespec="seconds"), "url": url, "ket_qua": "dung_lai"})
            raise DungLai(f"Phát hiện captcha/checkpoint/hạn chế tại {url}")
