# -*- coding: utf-8 -*-
from . import NenTang, q


class X(NenTang):
    ten = "x"

    def tim(self, tu):
        self.mo(f"https://x.com/search?q={q(tu)}&f=live"); self.cuon(3)
        return [{"url": u, "loai": "bai"} for u in self.lien_ket(r"x\.com/[^/]+/status/\d+$")]

    def doc(self, url):
        self.mo(url); self.cuon(2)
        t = self.page.eval_on_selector_all("article", "els => els.slice(0,20).map(e => e.innerText)")
        return [{"url": url, "van_ban": x} for x in t]

    def lien_quan(self, url):
        return self.lien_ket(r"x\.com/[A-Za-z0-9_]{2,15}$")
