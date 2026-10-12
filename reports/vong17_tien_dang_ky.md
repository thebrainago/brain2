# Vong 17 - DANG KY TRUOC (2026-10-12 ~14:50 UTC+7, truoc khi chay). MO PHONG.
## (2) Don bay mua-giu + loc thoi diem
Tai san: US500 = ^GSPC tu 1950 (gia, khong co tuc) va tu 1990; UK100 = ^FTSE tu 1990 (gia). Tham chieu ^SP500TR tu 1988.
Phi CFD: spread 1 bps (US500) / 1,5 bps (UK100) moi lan doi vi the, truot 0,5 bps, qua dem tren TOAN BO danh nghia L x (T-bill My + 2,5 %)/365 moi ngay lich
(UK100 cung dung T-bill My - xap xi). Tien ky quy khong sinh lai. Stop-out: von <= 0 -> chay (ruin).
O (36): mua-giu L in {1, 1.5, 2, 3} x {can bang lai hang ngay, co dinh (khong can bang)} x 3 chuoi = 24;
loc L in {1, 2} x {MA200 (giu khi dong t-1 > MA200), nham bien dong 15 %/nam (L_t = min(3, L*15%/vol20 ngay)), mua khi giam (L khi gia >= 90 % dinh 252 ngay, 2L khi duoi)}
x US500-1950 va UK100-1990 = 12.
Bao cao: CAGR, maxDD, Sharpe; xac suat chay/DD>80 % qua bootstrap khoi 20 ngay, 2000 duong 10 nam.
"Hon mua-giu 1x": CAGR > CAGR mua-giu CFD 1x cung chuoi VA maxDD < 80 %. Kiem thong ke cho loc thoi diem:
dich vong chuoi phoi nhiem (vong 15), p -> Holm cong don. Mua-giu thuan khong co p (khong phai quy tac thoi diem); chi bao cao.
## (3) Dao chieu ghep + (4) pha vo - FX H1 bid/ask that (HistData tick -> H1, 7 cap, 2024-01..2026-09)
Vao o mo bar t+1 sau tin hieu o dong t; chi phi = spread_open that cua bar vao + 20 % (XM thu them), qua dem 2,5 %/nam.
Manh dao chieu: RSI14 <30 mua / >70 ban; dong ngoai BB(20,2) (duoi mua / tren ban); MACD(12,26,9) cat len khi MACD<0 mua / cat xuong khi >0 ban;
Stoch(14,3) %K<20 mua / >80 ban. To hop 1-3 manh (cung bar) = 14. Quan ly: giu 6 bar; trailing 2xATR14 (toi da 48 bar);
thoat khi het nen H4 hien tai; thoat khi ATR14/ATR100 vuot 1,5 (toi da 48 bar) = 4. => 56 o/cap.
Pha vo: dong vuot dinh/day 20 bar; vuot dinh/day ngay truoc; vuot bien phien A (00-08 gio server); nen bien do > 2xATR14 theo huong nen.
Quan ly: giu 3 bar; trailing 1,5xATR; thoat som neu sau 2 bar chua co lai (toi da 24 bar) = 3. => 12 o/cap.
Tong (3)+(4) = 68 x 7 = 476 o. Nua dau thoi gian = phat hien (chon nghich/thuan khong - chieu co dinh nhu tren, KHONG dao chieu),
nua sau = kiem: t-test mot phia loi rong moi lenh > 0. Song: Holm cong don (4363 + 12 loc + 476 = 4851) < 0,05, lai ca hai nua,
x1,5 spread nua kiem lai, maxDD < 80 %.
## (1) Seeker: chi chay lai ong san co tren kho da tai, ghi so; khong mua du lieu, khong Telegram.
