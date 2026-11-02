# -*- coding: utf-8 -*-
"""Discord web: CHỈ đọc các kênh trong server Anh đã tham gia. Không tự vào server (lời mời cần người duyệt), không nhắn."""
from . import NenTang


class Discord(NenTang):
    ten = "discord"; cho_phep_theo_doi = False

    def tim(self, tu):
        return []          # Discord không có tìm kiếm công khai; dùng link mời Anh cung cấp

    def doc(self, url):
        self.mo(url); self.at.nghi("giua_thao_tac")
        t = self.page.eval_on_selector_all("li[id^=chat-messages]", "els => els.slice(-50).map(e => e.innerText)")
        return [{"url": url, "van_ban": x} for x in t]
