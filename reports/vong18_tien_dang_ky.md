# Vong 18 - he "bat cu chay manh" - DANG KY TRUOC (2026-10-12 ~15:00 UTC+7, truoc khi tai/chay). MO PHONG.
## Seeker
Truy van GitHub co chu dich (4 loai): hedging EA; straddle / pending stop hai dau / OCO; breakout phien / range chau A / tin (news straddle);
breakout thuong; kiet suc - dao chieu (exhaustion reversal). Chi nguon cong khai mien phi (GitHub). MQL5 codebase/forum: chi khi tai duoc khong dang nhap.
Moi goi qua ong doc san co (bo doc KHONG sua de vua). Dem: so repo xem / goi tai / co .set / dich duoc diem vao.
## Co che chuan hoa (kiem tren du lieu co bid/ask that: FX H1 7 cap 2024-01..2026-09; vang/chi so: CHUA DO DUOC neu khong co bid/ask)
Moi he: 1 bien the "goc" + 2 bien the chot nhanh: TP = 0,5xATR14 / SL = 1xATR14, va thoat theo thoi gian 3 bar. => 3 bien the.
 B1 straddle phien A: dat buy stop o dinh 00-08 gio server, sell stop o day; khop cai nao truoc (OCO, huy cai kia), het ngay thi dong.
    goc: SL o bien doi dien, TP = 1x do rong range.
 B2 straddle "tin": 08:30 NY (15:30 server) thu 6 dau thang (NFP) va ngay CPI (ALFRED): dat stop +-0,5xATR14 tu gia luc 15:00 server; goc TP 1xATR SL 1xATR.
 B3 breakout thuong: dong vuot dinh/day 24 bar -> vao mo bar sau; goc trailing 2xATR.
 B4 kiet suc: 3 nen cung chieu, tong bien do > 3xATR14, nen thu 3 dong o 25 % cuc tri -> vao nguoc; goc TP 1xATR SL 1,5xATR.
 B5 hedging (dai dien loai "hedge recovery"): mo ca buy va sell; chan nao lo 1xATR thi dong va mo lai chan do voi lot x2 (toi da 5 cap) cho toi khi tong lai >= 0,5xATR x lot dau
    -> la martingale; do maxDD, ty le chay (von 10.000, lot dau 0,01, stop-out 50 %).
Tong o: 5 he x 3 bien the x 7 cap = 105 (+ he dich tu EA tai ve neu co, dem them).
Gia: vao/ra theo bid + spread that cua bar (+20 % XM); stop khop o muc stop (dung gia high/low bid; mua khop o ask = bid + spread);
neu SL va TP cung bar -> gia dinh XAU NHAT (SL truoc). Truot gia them: 0 / 0,5 / 1 pip moi lenh (do nhay); song phai dat o 0,5 pip.
Phat hien nua dau / kiem nua sau; t mot phia loi rong/lenh > 0 o nua kiem; Holm cong don tu 5.061.
Song: Holm < 0,05, lai ca hai nua, spread x1,5 + truot 0,5 pip nua kiem lai, maxDD < 80 %.
