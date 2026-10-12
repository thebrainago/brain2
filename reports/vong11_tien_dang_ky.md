# Vong 11 - DANG KY TRUOC (ghi 2026-10-12 ~13:15 UTC+7, TRUOC khi tai bat ky du lieu FX/hang hoa/lai suat nao)

Tai khoan: chi forex/CFD (XM). Moi he la CFD/FX, phi kieu XM, spread khu hoi tra MOT lan, ket qua o x1 va x1,5.

## Phan 1 - 4 quy tac S&P song o vong 10, tren CFD US500
- 4 quy tac DA chi giu ngay quy tac bat (khong giu lenh ngoai cua so) -> phi qua dem chi tinh ngay giu. Khong co bien the nao them.
- MOT phep thu moi: DANH MUC = trung binh phoi nhiem 4 quy tac (moi quy tac 1/4 von), phi tren thay doi phoi nhiem.
  Tinh vao ho Holm.

## Phan 2 - quy tac FX / hang hoa / vi mo (13, co dinh)
Phi: spread khu hoi EURUSD 1,6 pip, USDJPY 1,9 pip, AUDUSD/NZDUSD 1,8 pip, vang 2 bps, dau 4 bps; truot 0,5 bps/chieu.
Qua dem FX: chieu mua cap XY tra/nhan (r_X - r_Y) - 1 %/nam markup (moi chieu tra markup). Lai suat: nguon mien phi
tim duoc (ghi ro); khong co lai suat lich su cho mot dong tien -> dung chenh 0 + markup va ghi "gia dinh".
Hang hoa CFD: qua dem chieu mua -(r_USD + 2,5 %), chieu ban +(r_USD - 2,5 %).
Vao/ra o dong cua ngay; tin hieu chi dung du lieu toi dong cua ngay truoc.
 1. USD_CUOI_THANG: mua EURUSD 2 phien cuoi thang.
 2. CUOI_QUY_TAI_CAN_BANG: 5 phien cuoi thang 3/6/9/12: neu SPX tang trong quy (toi phien truoc) -> mua EURUSD, nguoc lai ban.
 3. CUOI_NAM_USD: mua EURUSD 10 phien cuoi thang 12.
 4. USD_THANG12_THANG1: mua EURUSD ca thang 12, ban EURUSD ca thang 1.
 5. JPY_CUOI_NAM_TAI_KHOA: ban USDJPY ca thang 3.
 6. VANG_THANG8_THANG2: mua vang thang 8 -> thang 2, dung ngoai thang 3-7.
 7. DAU_THANG2_THANG4: mua dau Brent thang 2-4.
 8. CHENH_2Y_MY_DUC_EURUSD: chenh (US2y - DE2y) thay doi 20 phien > 0 -> ban EURUSD, < 0 -> mua.
 9. TNX_USDJPY: loi suat My 10y (^TNX) thay doi 20 phien > 0 -> mua USDJPY, nguoc lai dung ngoai.
10. TNX_VANG: ^TNX thay doi 20 phien < 0 -> mua vang, nguoc lai dung ngoai.
11. AUD_NZD_HOI_QUY: z = zscore 60 phien cua log(AUDUSD) - log(NZDUSD); z > 2 -> ban AUD/mua NZD (hai chan bang
    danh nghia), z < -2 nguoc lai; dong khi |z| < 0,5.
12. CARRY_AUDJPY: luon mua AUDJPY (nhan chenh lai suat qua swap).
13. VIX_THAP_US500: giu US500 khi VIX (dong cua truoc) < trung vi 252 phien cua chinh no.
Quy tac khong co du lieu mien phi -> "CHUA DO DUOC", khong tinh vao ho (ghi ro).

## Kiem (giong vong 10)
- 30 % cuoi theo thoi gian = ngoai mau; nam cong bo -> Sharpe truoc/sau (1: 2014 Melvin-Prins; 2: 2015; 3: 2000;
  4: 2000; 5: 2000; 6: 2010; 7: 2000; 8: 2000; 9: 2000; 10: 2000; 11: 1999 Gatev pairs; 12: 1990; 13: 2005).
- Holm tren TOAN BO quy tac da thu: 8 cua vong 10 + danh muc phan 1 + moi quy tac phan 2 do duoc.
- Song: lai sau phi + swap toan chuoi > 0, maxDD < 80 %; NM lai o x1 VA x1,5; Sharpe sau cong bo > 0; p Holm < 0,05.
