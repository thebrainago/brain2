# Vong 9 - DANG KY TRUOC (ghi 2026-10-12 ~11:55 UTC+7, truoc khi chay o nao cua vong 9)

Mo hinh phi: spread MOT lan / lenh khu hoi (sua mo hinh phi vong 9, khong doi cong). Moi ket qua bao cao
o HAI muc: spread x1 va spread x1,5 (stress). Du lieu: H1 gop tu tick HistData (spread that tung bar, mo
hinh cong XM = that + markup, gio server NY+7), 7 cap, 2024-01 -> 2026-09, 70 % trong mau / 30 % ngoai mau.

## Phan 1 - do lai ung vien hang dau duoi mo hinh da sua
- Ho phep thu = TOAN BO 8.554 o cua luot vong 8 `spread_mot_lan` (47 EA H1 x 7 cap x 26 to hop) - da chay
  dung mo hinh vong 9; khong chay them bien the nao tren ho nay.
- Ung vien hang dau = o co nhan cong (NM lai sau phi, maxDD < 80 %, >= 20 lenh NM) VA TM lai.
- Song khi: ung vien + p Holm (tren 8.554 o) < 0,05 + o do chay lai voi spread x1,5 van lai NM va TM.

## Phan 2 - manh moi tu file tien ich da tai (A)
Tham so = MODE input cua tac gia trong kho (dem 12/10/2026):
- B hoa von: khi gia dong cua da di >= 1,5 x ATR14 co loi (InpBreakEvenATR = 1.5, 18 file) -> SL ve gia vao
  + 10 point (InpBEBufferPoints = 10, 15 file). Chi siet. Lenh khong co SL -> khong lam gi.
- R khoi luong theo rui ro: 1 % von / lenh (input *Risk* mode = 1.0, 509 file) - trong so = 1 % x gia / khoang SL.
  Lenh khong co SL -> khong lam gi.
- Loc tin (news filter, InpNewsMinutesBefore = 30): KHONG co lich tin lich su mien phi tren box -> CHUA DO DUOC,
  khong dua vao.
- To hop: MANH = A T S P D B R, tran 3 manh; CHI chay to hop co B hoac R (to hop cu da do o phan 1):
  64 - 26 = 38 to hop / (EA, cap). Dem MOI o; Holm tren ho phan 2.
- Nhan / song nhu phan 1 (Holm tren ho phan 2; x1,5 chay lai cho o qua buoc Holm... va cho moi o nhan cong de bao cao).
