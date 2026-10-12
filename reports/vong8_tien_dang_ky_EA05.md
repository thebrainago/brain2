# Vong 8 - ung vien theo doi EA05_MACD_Momentum NZDUSD H1 + loc phien - DANG KY TRUOC
Ghi 2026-10-12 ~09:30 (UTC+7), TRUOC KHI tai / nhin bat ky du lieu moi nao. Khong sua sau khi xem.

Nguon goc: o tot nhat cua vong 7 (8.008 o, Holm p = 1,0) - CHON RA tu nhieu phep thu, nen chi kiem
tren du lieu CHUA DUNG BAO GIO.

## He (dong bang, khong doi gi)
- EA: `EA05_MACD_Momentum.mq5` trong kho, doc bang bo doc o commit 075b7e6a (moi chan cua EA, chung mot vi the).
- Manh P cua `nhan/thu_vien_co_che.py` (chi vao lenh khi gio server bar vao trong [7, 22)). Khong manh nao khac.
- Khung H1, cap NZDUSD, phi XM `vong_thu_nghiem.mo_hinh_chi_phi(df, ma="NZDUSD")`, _Point 1e-5.

## Du lieu moi
- NZDUSD HistData M1 2018-01 -> 2023-12 (chua tung dung cho NZDUSD; vong 7 dung 2024-01 -> 2026-09),
  gop M5 bang cung cach `gop_histdata_m5.py` (gio server Helsinki), roi H1. Neu tai duoc du lieu
  tick co spread that (Dukascopy...) cho NZDUSD thi chay THEM ban spread that, cung tieu chi.

## Tieu chi "song" (TAT CA phai dat)
1. Toan giai doan moi: lai sau phi > 0 va maxDD < 80 %.
2. So lenh >= 50.
3. p mot phia tu Sharpe (t = SR_nam * sqrt(so nam)) < 0,05 (MOT phep thu dang ky truoc).
4. It nhat 4/6 nam duong lich lai sau phi.
5. Spread XM x1,5: van lai sau phi.
Khong dat -> bo ung vien, khong noi long tieu chi, khong thu bien the khac tren du lieu nay.
