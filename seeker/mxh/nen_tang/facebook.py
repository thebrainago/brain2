# -*- coding: utf-8 -*-
"""Facebook: tìm nhóm/bài theo từ khóa, đọc bài trong nhóm, theo dõi trang, xin vào nhóm (giới hạn ngày).
Nhóm có câu hỏi khi xin vào: KHÔNG tự trả lời -> ghi log 'can_tra_loi' để Anh tự xử lý."""
from . import NenTang, q


class Facebook(NenTang):
    ten = "facebook"; cho_phep_xin_vao = True

    def tim(self, tu):
        self.mo(f"https://www.facebook.com/search/groups/?q={q(tu)}"); self.cuon(2)
        return [{"url": u, "loai": "nhom"} for u in self.lien_ket(r"facebook\.com/groups/[^/]+/?$")]

    def doc(self, url):
        self.mo(url); self.cuon(4)
        bai = self.page.eval_on_selector_all("div[role=article]", "els => els.slice(0,30).map(e => ({t: e.innerText, l: (e.querySelector('a[href*=\"/posts/\"],a[href*=\"/permalink/\"]')||{}).href}))")
        return [{"url": b.get("l") or url, "van_ban": b["t"]} for b in bai if b.get("t")]

    def lien_quan(self, url):
        if "/groups/" in url:
            self.mo(url.rstrip("/") + "/related_groups")
        return self.lien_ket(r"facebook\.com/groups/[^/]+/?$")

    def xin_vao(self, url):
        r = super().xin_vao(url, r"^(join group|tham gia nhóm)$")
        if r == "da_lam" and self.page.get_by_text(__import__("re").compile("answer questions|trả lời câu hỏi", 2)).count():
            self.at._ghi(self.ten, "can_tra_loi", url, "bo_qua")
            self.page.keyboard.press("Escape")
        return r
