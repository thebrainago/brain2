# Vong 10 - he MUA VU / CHU KY tan suat thap - DANG KY TRUOC
Ghi 2026-10-12 ~13:10 (UTC+7), TRUOC khi tai hay nhin bat ky du lieu ngay nao. Khong sua sau khi xem.

## Du lieu (mien phi)
- S&P 500 (chi so gia ^SPX, KHONG co co tuc - than trong cho chieu mua) ngay, cang dai cang tot (muc tieu 1950 -> nay).
- Vang XAUUSD ngay (muc tieu 1975 -> nay). Lai suat T-bill 3 thang (FRED DTB3) cho phi qua dem.
- Nguon uu tien Stooq CSV; neu khong duoc: FRED / Yahoo / nguon cong khai khac - ghi ro trong bao cao.

## Quy tac (8, CO DINH, chi mua hoac dung ngoai; vao/ra o gia dong cua ngay)
1. CHU_KY_BAU_CU_NAM3: giu SPX ca nam khi nam % 4 == 3 (nam truoc bau cu My). Cong bo: Hirsch 1967.
2. HALLOWEEN: giu SPX tu phien dau thang 11 den phien cuoi thang 4. Bouman & Jacobsen 2002.
3. DAU_CUOI_THANG: giu SPX phien cuoi thang + 3 phien dau thang sau (mua o dong cua phien ke cuoi). Ariel 1987.
4. SANTA: giu SPX 5 phien cuoi thang 12 + 2 phien dau thang 1. Hirsch 1972.
5. VANG_TRUOC_TET: giu XAUUSD 20 phien ket thuc o phien cuoi TRUOC mung 1 Tet (lich am, goi lunardate). Cong bo khong chinh thuc - lay 2010.
6. SPX_10THANG: cuoi thang dong cua > SMA 10 thang -> giu SPX ca thang sau. Faber 2007.
7. VANG_10THANG: nhu 6 cho XAUUSD. Faber 2007.
8. SPX_3TUAN_GIAM: sau 3 tuan (dong cua thu 6) giam lien tiep -> giu SPX 1 tuan sau. Quy tac D1/W1 hiem; cong bo: dan gian (lay 2000).

## Chi phi kieu XM (CFD)
- Spread khu hoi tra MOT lan (mo hinh vong 9): US500 1,0 bps, XAUUSD 2,0 bps moi lenh khu hoi; truot 0,5 bps moi chieu.
- Qua dem chieu mua: -(T-bill 3T + 2,5 %)/365 moi ngay lich giu lenh (CFD tai chinh hoa). Truoc khi co DTB3: dung 4 %.
- Moi ket qua bao o spread x1 va x1,5.

## Kiem
- Ngoai mau theo thoi gian: 30 % cuoi chuoi cua tung tai san. Phan ra sau cong bo: so Sharpe truoc / sau nam cong bo.
- p mot phia tu t = Sharpe_nam * sqrt(so_nam) tren TOAN chuoi (loi rong moi ngay, ke ca ngay dung ngoai = 0).
- Holm tren 8 quy tac (x1,5 la stress, khong tinh them phep thu).
- SONG khi TAT CA: lai sau phi toan chuoi > 0, maxDD < 80 %; ngoai mau lai sau phi (x1 VA x1,5); Sharpe SAU cong bo > 0;
  p Holm < 0,05.
- Bao cao them (khong dung de chon): so voi mua-giu, chenh loi suat TB ngay trong/ngoai quy tac (Welch t).
