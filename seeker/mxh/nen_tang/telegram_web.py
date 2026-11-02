# -*- coding: utf-8 -*-
"""Telegram Web (web.telegram.org/k) trong hồ sơ riêng — Anh đăng nhập tay (QR/OTP), tool không bao giờ chạm OTP.
Đọc kênh/nhóm (kể cả riêng tư Anh đã vào), tải tệp ex4/ex5/mq4/mq5/set/pdf vào data/, khám phá kênh qua chuyển tiếp/@nhắc,
tham gia kênh công khai (giới hạn ngày, mặc định chạy thử)."""
from __future__ import annotations
import re
from pathlib import Path
from . import NenTang
from ... import telegram as TG

DUOI = (".ex4", ".ex5", ".mq4", ".mq5", ".mqh", ".set", ".pdf", ".zip", ".rar")


class TelegramWeb(NenTang):
    ten = "telegram"; cho_phep_xin_vao = True

    def tim(self, tu):
        # Ưu tiên t.me/s công khai (động cơ chính); trong web chỉ dùng ô tìm kiếm toàn cục
        self.mo("https://web.telegram.org/k/")
        o = self.page.locator("input.input-search-input").first
        o.fill(tu); self.at.nghi("giua_thao_tac")
        ten = self.page.eval_on_selector_all(".search-group .chatlist-chat", "els => els.map(e => e.getAttribute('data-peer-id') + '|' + e.innerText)")
        o.fill("")
        return [{"url": x, "loai": "kenh"} for x in ten]

    def la_kenh_hay_nhom(self) -> bool:
        """Chỉ đọc KÊNH/NHÓM. Chat 1-1 (tiêu đề 'last seen/online/truy cập') -> từ chối."""
        try:
            phu = self.page.locator(".chat-info .info, .top .bottom .info").first.inner_text(timeout=5000).lower()
        except Exception:
            return False
        return bool(re.search(r"subscriber|member|thành viên|người đăng ký|подписчик|участник", phu))

    def doc(self, url_hoac_ten: str):
        ten = url_hoac_ten.split("t.me/")[-1].lstrip("@")
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{4,31}", ten):
            self.mo(f"https://web.telegram.org/k/#@{ten}")
        else:   # chỉ có tên hiển thị -> tìm trong ô tìm kiếm, mở kết quả khớp đúng tên
            self.mo("https://web.telegram.org/k/")
            o = self.page.locator("input.input-search-input").first; o.fill(ten); self.at.nghi("giua_thao_tac")
            self.page.locator(".search-group .chatlist-chat", has_text=ten).first.click(timeout=10000)
            self.at.nghi("giua_thao_tac")
        if not self.la_kenh_hay_nhom():
            self.at._ghi(self.ten, "bo_qua_chat_ca_nhan", ten, "bo_qua")
            return []
        self.at.nghi("giua_thao_tac")
        for _ in range(3):
            self.page.mouse.move(700, 400); self.page.mouse.wheel(0, -2500); self.at.nghi("cuon_trang")
        tin = self.page.eval_on_selector_all(".bubble[data-mid]", "els => els.slice(-80).map(e => ({mid: e.getAttribute('data-mid'), t: e.innerText, doc: (e.querySelector('.document-name')||{}).innerText || ''}))")
        return [{"url": f"https://t.me/{ten}/{x['mid']}", "van_ban": x["t"], "tep": x["doc"]} for x in tin]

    def tai_tep(self, ten_kenh: str, tin: list[dict], thu_muc: Path) -> list[dict]:
        ra = []
        for x in tin:
            if not x.get("tep") or not x["tep"].lower().endswith(DUOI):
                continue
            dich = Path(thu_muc) / ten_kenh / re.sub(r"[^\w.\-]+", "_", x["tep"])
            if dich.exists():
                ra.append({"tep": str(dich), "bai": x["url"], "kq": "da_co"}); continue
            def _tai():
                bong = self.page.locator(f".bubble[data-mid='{x['url'].rsplit('/', 1)[1]}'] .document").first
                with self.page.expect_download(timeout=60000) as d:
                    bong.click()
                dich.parent.mkdir(parents=True, exist_ok=True); d.value.save_as(str(dich))
            # tải tệp không gây hậu quả với người khác -> chạy cả khi chay_thu
            kq = "vuot_tran" if not self.at.cho_phep(self.ten, "tai_tep") else None
            if kq is None:
                try:
                    _tai(); self.at._ghi(self.ten, "tai_tep", x["tep"], "da_lam"); kq = "da_tai"
                except Exception as e:
                    kq = f"loi:{type(e).__name__}"
            ra.append({"tep": str(dich), "bai": x["url"], "kq": kq})
        return ra

    def lien_quan(self, _url=None) -> list[str]:
        html = self.page.content()
        return sorted(set(TG.doc_trang(html, "")["kenh_moi"]) | {m.lower() for m in re.findall(r"@([A-Za-z][A-Za-z0-9_]{4,31})", self.page.inner_text("body"))})

    def xin_vao(self, url):
        return super().xin_vao(url, r"^(join|tham gia|subscribe)")
