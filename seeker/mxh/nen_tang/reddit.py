# -*- coding: utf-8 -*-
from . import NenTang, q


class Reddit(NenTang):
    ten = "reddit"; cho_phep_xin_vao = True     # "join" subreddit

    def tim(self, tu):
        self.mo(f"https://www.reddit.com/search/?q={q(tu)}&type=sr"); self.cuon(1)
        return [{"url": u, "loai": "nhom"} for u in self.lien_ket(r"reddit\.com/r/[^/]+/?$")]

    def doc(self, url):
        self.mo(url); self.cuon(3)
        t = self.page.eval_on_selector_all("shreddit-post, article", "els => els.slice(0,30).map(e => ({t: e.innerText, l: e.getAttribute('permalink')}))")
        return [{"url": ("https://www.reddit.com" + b["l"]) if b.get("l") else url, "van_ban": b["t"]} for b in t]

    def lien_quan(self, url):
        return self.lien_ket(r"reddit\.com/r/[^/]+/?$")

    def xin_vao(self, url):
        return super().xin_vao(url, r"^join$")
