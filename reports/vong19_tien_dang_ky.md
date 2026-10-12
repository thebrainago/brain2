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

## BO SUNG (2026-10-12 ~15:40 UTC+7, sau ket qua phan 1, TRUOC khi chay phan nay) - phong cach khac + bo du lieu thu hai
Vao moi (13): XU_HUONG_DAI: DONCHIAN55 (pha 55 bar), MA50_200 (cat); BIEN_DONG: SQUEEZE (BB20 nam trong Keltner20x1,5 roi dong ra ngoai -> theo huong);
SMC: SWEEP (dinh > dinh 20 bar roi dong duoi dinh cu -> ban; nguoc lai mua), FVG (low[t] > high[t-2] -> mua; nguoc lai ban);
SR: PIVOT (cham S1 ngay truoc roi dong tren -> mua; cham R1 roi dong duoi -> ban); ICHIMOKU (dong cat len/xuong may 26/52);
FIB (xu huong theo MA200, gia hoi 50-61,8 % song 48 bar roi dong theo xu huong); OPENING_RANGE (pha dinh/day bar 10:00 server = mo London);
GAP_FILL (thu 2: mo cach dong thu 6 > 0,3xATR -> danh lap gap); MTF (RSI14 30/70 chi khi cung huong MA200 = keo ve);
NEWS_FADE (bar 15:00 server ngay NFP/CPI: danh nguoc huong bar o dong); ML_LOGIT (hoi quy logistic tren 5 loi nhuan tre + RSI,
hoc tren nua phat hien, vao khi xac suat > 0,55 / < 0,45).
Khong do: VWAP (khong co khoi luong that), scalping rieng (vong 18 da do TP nho) -> CHUA DO DUOC / da do.
Carry, cap/stat-arb: dung ket qua vong 11 (CARRY_AUDJPY, AUD_NZD_HOI_QUY), gan nhan CARRY / STAT_ARB.
Thoat (3): TR2, GIO6, TP (1xATR/SL 1,5xATR). Bo 1: FX H1 bid/ask 2024-26 x 7 cap -> 13 x 3 x 7 = 273 o.
Bo 2 (moi tai/chua dung trong vong nay): EURUSD 2018-2023 (HistData M5->H1, spread co dinh 1,4 pip), NZDUSD 2018-2023 (Dukascopy bid/ask that),
AUDCAD 2008-2023 (HistData, spread 2,5 pip), vang/US500/UK100 H1 Yahoo 730 ngay (spread co dinh 2/1/1,5 bps, khong bid/ask) ->
(13 + 8 vao cu) x 3 x 6 = 378 o. Do ben: tuong quan hang (Spearman) trung vi nua kiem theo (vao, thoat) giua bo 1 va bo 2.
Holm cong don tu 5.677 (+ 273 + 378). Song nhu phan 1.
