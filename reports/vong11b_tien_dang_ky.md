# Vong 11b - DANG KY TRUOC bo sung (ghi 2026-10-12 ~13:20 UTC+7, TRUOC khi tai/nhin du lieu M30 vang, OHLC SPX, hay quet)

## (a1) Vang M30 - quy tac cua nguoi dung
Du lieu: HistData XAUUSD M1 2024-01 -> 2026-09 (co san), gop M30, gio server NY+7 (gio MT5 XM, sua vong 8).
Moi ngay (thu 2-6): huong buoi sang d = sign(gia luc HH:00 - gia mo 08:00 server) voi HH = gio nen giua trua;
nen M30 luc 12:00 nguoc d VA nen M30 luc 12:30 cung d -> vao lenh huong d o dong cua nen 12:30 (13:00), dong o 17:00.
Hai bien the (ca hai DEM vao Holm): (i) gio SERVER: 08:00 / 12:00 / 12:30 / ra 17:00 server;
(ii) gio GMT: cung cac moc theo GMT (server = GMT+2 mua dong / +3 mua he My).
Phi: spread khu hoi 2 bps tra mot lan + truot 0,5 bps/chieu; trong ngay -> khong swap.
## (a2) S&P 500 IBS hoi quy
IBS = (C - L)/(H - L) ngay; IBS < 0,2 -> mua US500 o dong cua, giu 1 ngay. ^GSPC OHLC Yahoo tu 1990 (OHLC truoc do kem tin cay).
Phi CFD US500 nhu vong 10 (1 bps, tai chinh hoa ngay giu). Cong bo: 2010 (lay muc pho bien).
=> (a1)(a2) = 3 phep thu, cong vao ho Holm 22 cua vong 11 -> 25.

## (b) Quet he thong (KHAM PHA / GIU LAI theo thoi gian)
Tai san ngay (Yahoo): EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD, vang GC=F, Brent BZ=F, ^GSPC, ^NDX, ^GDAXI, ^N225.
Tai san gio: HistData M1 -> H1 (gio server NY+7) 7 cap FX + XAUUSD, 2024-01 -> 2026-09.
O quet (moi o 1 phep thu, huong chon o nua KHAM PHA):
- thu trong tuan (5), ngay trong thang theo lich (1..31), thang trong nam (12) cho moi tai san ngay;
- gio trong ngay (24) cho moi tai san gio (loi suat close-to-close cua bar gio do);
- cap cheo: moi cap co thu tu (A, B), A != B trong tai san ngay: giu B ngay t theo dau r_A(t-1) x huong.
Chia: nua DAU chuoi (theo thoi gian) = kham pha; nua SAU chua dong toi = xac nhan.
Kham pha: t hai phia cua TB loi suat ngay o (gia, chua phi); chon huong = dau TB. Xac nhan: p mot phia theo huong da chon
tren nua sau. Holm VA BH-FDR (q 10 %) tren m = TOAN BO so o da quet (ke ca o khong qua kham pha, p = 1).
O song quet: Holm < 0,05 (FDR chi bao cao). Sau do moi o song chay voi phi XM + swap (nhu vong 11), x1 va x1,5,
tren nua xac nhan: phai lai sau phi o ca hai, maxDD < 80 %. Moi ket qua: MO PHONG.

## Sua (a1) theo xac nhan cua nguoi dung (ghi ~13:17, van TRUOC khi nhin du lieu vang M30)
- Dinh nghia CHINH: gio Viet Nam GMT+7 (khong DST): mo buoi sang 08:00 VN, nen M30 12:00 VN (05:00 UTC) nguoc huong,
  nen 12:30 VN (05:30 UTC) cung huong -> vao o 13:00 VN, dong 17:00 VN. Doi gio: server NY+7 -> -7 h = gio New York
  (co DST) -> UTC -> +7 h.
- Hai bien the server va GMT o tren van chay va DEM: (a1) = 3 phep thu; ho Holm vong 11 = 22 + 3 + 1 (IBS) = 26.
