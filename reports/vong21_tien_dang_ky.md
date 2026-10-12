# Vong 21 - "gia luon gap lai EMA" - DANG KY TRUOC (2026-10-12 ~16:10 UTC+7, truoc khi chay). MO PHONG.
## 1) Do luan diem
Su kien: nen dau tien |close - EMA_n| >= k x ATR14 (n in 20/50/100/200, k in 1,5/2/3/4). Do: ty le cham lai EMA (low<=EMA<=high) trong 48 nen (H1) / 20 nen (D1),
thoi gian trung vi. Baseline: 200 chuoi gia tron ngau nhien loi nhuan (cung bien dong, mat tu tuong quan), tinh y het; z = (thuc - tb tron)/sd tron.
## 2) Luoi (dang ky truoc, KHONG mo rong sau khi xem)
EMA {20,50,100,200} x k {1,5;2;3;4} x che do {MR, PB} x loc ATR {khong, ATR pct500 < 50, > 50} x them {khong, RSI, BB} = 288 o/chuoi.
 do doc s = (EMA_t - EMA_{t-10}) / ATR14; phang: |s| < 0,5; doc: |s| >= 0,5.
 MR: phang va |gia - EMA| >= k ATR -> vao nguoc ve EMA; TP = cham EMA (muc EMA cap nhat moi nen), SL = k ATR tu gia vao, toi da 48 nen.
 PB: doc, trong 24 nen truoc gia da cach EMA >= k ATR theo huong doc, nay dong trong 0,25 ATR quanh EMA -> vao theo huong doc; TP = k ATR, SL = 1,5 ATR, toi da 48 nen.
 RSI: MR can RSI14 < 30 (mua)/ > 70 (ban); PB can RSI cung phia 50 voi huong. BB: MR can dong ngoai BB(20,2); PB can dong trong BB.
 (Da khung: KHONG lam vong nay - gioi han kich thuoc.) SL va TP cung nen -> SL truoc.
## 3) Du lieu
Bo 1: 7 cap FX H1 bid/ask that 2024-26 (+20 % XM). Bo 2: EURUSD 2018-23, NZDUSD 2018-23 (Dukascopy bid/ask), AUDCAD 2008-23, vang/US500/UK100 H1 Yahoo.
D1: EURUSD, GBPUSD, USDJPY, AUDUSD (Yahoo, spread co dinh 1,6/1,6/1,6/2 pip-bps), S&P 500 (1 bps), vang (2 bps), tu 2004 (FX) / 1990 (S&P), qua dem 2,5 %/nam (+ T-bill chieu mua S&P/vang).
Dieu chinh xu huong (moi chuoi): loi moi lenh tru huong x trung binh loi nhuan/nen (nua phat hien) x so nen giu.
Kiem: t mot phia loi rong (da tru xu huong) / lenh > 0 o nua kiem; Holm cong don 6.321 + so o du lenh (>= 15 lenh moi nua).
Song: Holm < 0,05, lai ca hai nua, spread x1,5 nua kiem lai, maxDD < 80 %.
## 4) Do nhay tham so
Voi moi o tot nhat (10 p nho nhat): ty le o lan can (EMA +-1 bac, k +-1 bac, cung che do/loc/them, cung chuoi) co nua kiem > 0.
Ban do trung vi nua kiem theo (EMA, k, che do) gop moi chuoi.
