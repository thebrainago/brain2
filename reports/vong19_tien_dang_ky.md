# Vong 19 - nhom chien luoc, trailing, ghep - DANG KY TRUOC (2026-10-12 ~15:30 UTC+7). MO PHONG.
Nhom: NEN (mo hinh nen), DONG_LUONG, DAO_CHIEU, BREAKOUT, HEDGE_GRID, MR (mean-reversion), PHIEN_GIO, LICH_MUA_VU, VI_MO (lai suat/cheo/tin), DON_BAY.
Gan nhan: ket qua cu theo bang anh xa co dinh trong v19.py (khong doi sau khi xem); EA trong kho theo tu khoa ten/ma (danh sach co dinh).
## Thi nghiem moi (FX H1 bid/ask that 2024-01..2026-09, 7 cap, + 20 % XM, qua dem 2,5 %/nam)
Vao (8, mo bar sau tin hieu): NEN: engulfing; pinbar (bong >= 2/3 bien do). DONG_LUONG: ROC24 doi dau; MACD cat 0.
DAO_CHIEU: RSI14 30/70. BREAKOUT: dinh/day 20 bar. MR: z(close, MA50, sd50) vuot +-2 -> nguoc. PHIEN_GIO: vuot bien phien A (sau 08 gio server).
Thoat (8): TP 1xATR/SL 1,5xATR; thoi gian 6 bar; ATR trailing 1x, 2x, 3x; chandelier (dinh 22 bar - 3xATR); hoa von tai +1xATR roi trail 2xATR;
trail theo khung H4 (day/dinh nen H4 da dong truoc). Moi thoat co SL ban dau 1,5xATR tru TP/thoi gian (co SL). Toi da 72 bar.
SL va TP/stop cung bar -> SL truoc (xau nhat). => 8 x 8 x 7 = 448 o.
## Ghep (dang ky truoc, chon theo NUA PHAT HIEN, khong nhin nua kiem)
Chon 3 nhom co trung vi loi nua phat hien cao nhat trong 448 o; voi moi cap nhom (A tin hieu, B loc): tin hieu A chi lay khi
tin hieu cung huong cua B xuat hien trong 24 bar truoc (hoac B la DONG_LUONG: dau ROC24 cung huong). 3 nhom -> 6 cap co thu tu x thoat tot nhat
nua phat hien cua A (1) + time-exit 6 + ATR 2x = 3 thoat => 18 x 7 = 126 o.
Kiem: t mot phia loi/lenh > 0 nua kiem; Holm cong don 5.145 + 448 + 126 = 5.719. Song: Holm < 0,05, lai ca hai nua, x1,5 spread nua kiem lai, maxDD < 80 %.
Do nhay phi: trung vi nua kiem x1 vs x1,5.
MQL5 codebase: thu ham tai_mql5_goi co san; khong dang nhap; neu bi chan -> CHUA DO DUOC.
