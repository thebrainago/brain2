# Vong 7 - Viec (A): thu vien co che nho - TIEU CHI DANG KY TRUOC
Ghi luc 2026-10-12 ~09:20 (UTC+7), TRUOC KHI chay bat ky o nao. Khong sua sau khi xem.

## Manh (tham so co dinh, lay MODE gia tri mac dinh input cua tac gia trong kho data/cau_kho, khong toi uu)
- A  SL/TP ATR: SL = 1.5 x ATR(14), TP = 3.0 x ATR(14) (mode SL-ATR 1.5 [58 file], TP-ATR 3.0 [32], ATR period 14 [397])
- T  keo SL ATR: keo = close -/+ 1.0 x ATR(14), chi siet; chua co SL thi them SL dau 1.5 x ATR(14) (mode trail-ATR khac 0 = 1.0 [39])
- S  loc spread: bo lenh khi spread > 30 point (mode MaxSpread = 30 [99])
- P  loc phien: chi vao lenh khi gio server bar vao trong [7, 22) (mode gio bat dau khac 0 = 7 [63], gio ket thuc = 22 [47])
- D  gioi han ngay: toi da 1 lenh / ngay cho ca he (mode MaxTradesPerDay = 1 [44])
To hop: rong (goc) + 5 don + 10 doi + 10 ba = 26 to hop / don vi. Tran 3 manh.

## Don vi
- Moi EA dich duoc (co_che khac rong) voi bo doc hien tai, tat ca chan cua EA chay CHUNG mot vi the (mo_phong.chay_he).
- Khung: EA khung co dinh -> chi khung do (M15/H1/H4 resample tu HistData M5); EA khong co dinh -> H1.
- Cap: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, NZDUSD, USDCAD (HistData M5 2024-01..2026-09, gio server da dich; XAUUSD bo vi hop dong/point khac).
- Phi XM: vong_thu_nghiem.mo_hinh_chi_phi(df, ma=cap); _Point 1e-5 (JPY 1e-3).

## Do
- Mot lan chay tren TOAN chuoi; 70% dau = trong mau (TM), 30% cuoi = ngoai mau (NM).
- Moi o = (EA, to hop, cap, khung). DEM MOI O DA CHAY (ke ca it lenh, loi, lo) vao so phep thu.
- p mot phia tu Sharpe NM: t = SR_nam * sqrt(so nam NM), p = 1 - Phi(t).
- Hieu chinh Holm-Bonferroni tren TOAN BO so o, alpha ho = 0.05.

## Nhan
- "dat nhan cong (mo phong)": NM lai sau phi > 0, maxDD NM < 80%, so lenh NM >= 20 (cong khong doi).
- "song": dat nhan cong VA TM lai sau phi > 0 VA p sau Holm < 0.05 VA (chi voi o qua buoc truoc):
  spread XM x1.5 van lai NM, VA 3 cua so thoi gian deu nhau (toan chuoi) deu lai.
- Khong o nao "song" -> bao that la khong co gi, khong noi long tieu chi.
