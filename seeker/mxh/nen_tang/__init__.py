# -*- coding: utf-8 -*-
"""Bộ chuyển đổi theo nền tảng. Bộ chọn (selector) dễ thay đổi khi nền tảng đổi giao diện: lỗi chọn -> ghi log, không đoán bừa."""
from __future__ import annotations
import re, urllib.parse
from ..an_toan import AnToan


class NenTang:
    ten = "?"
    cho_phep_theo_doi = True
    cho_phep_xin_vao = False

    def __init__(self, page, at: AnToan):
        self.page, self.at = page, at

    def mo(self, url: str) -> str:
        if not self.at.cho_phep(self.ten, "trang_doc"):
            raise RuntimeError("Đã chạm trần trang_doc hôm nay")
        self.page.goto(url, wait_until="domcontentloaded", timeout=45000)
        self.at.nghi("giua_thao_tac")
        from ..trinh_duyet import van_ban_trang
        txt = van_ban_trang(self.page)
        self.at.kiem_trang(txt, self.page.url)
        self.at._ghi(self.ten, "trang_doc", url, "da_lam")
        return txt

    def cuon(self, lan: int = 3):
        for _ in range(lan):
            self.page.mouse.wheel(0, 1600); self.at.nghi("cuon_trang")

    def lien_ket(self, mau: str) -> list[str]:
        hs = self.page.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
        return sorted({h.split("?")[0] for h in hs if re.search(mau, h)})

    # --- giao diện chung ---
    def tim(self, q: str) -> list[dict]: raise NotImplementedError
    def doc(self, url: str) -> list[dict]: raise NotImplementedError
    def lien_quan(self, url: str) -> list[str]: return []

    def _bam(self, ten_nut_regex: str):
        nut = self.page.get_by_role("button", name=re.compile(ten_nut_regex, re.I)).first
        nut.click(timeout=8000)

    def theo_doi(self, url: str, nut=r"^(follow|theo dõi)$") -> str:
        if not self.cho_phep_theo_doi:
            return "khong_ho_tro"
        self.mo(url)
        return self.at.thuc_hien(self.ten, "theo_doi", url, lambda: self._bam(nut))

    def xin_vao(self, url: str, nut=r"^(join group|tham gia nhóm|join)$") -> str:
        if not self.cho_phep_xin_vao:
            return "khong_ho_tro"
        self.mo(url)
        return self.at.thuc_hien(self.ten, "xin_vao_nhom", url, lambda: self._bam(nut))


def q(x: str) -> str:
    return urllib.parse.quote(x)
