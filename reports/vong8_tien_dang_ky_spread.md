# Vong 8 - do manh loc spread (S) bang spread THAT - DANG KY TRUOC
Ghi 2026-10-12 ~10:15 (UTC+7), truoc khi chay bat ky o nao tren du lieu tick.

## Du lieu
- HistData TICK (bid/ask tung tick) 2024-01 -> 2026-09, 7 cap: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, NZDUSD, USDCAD.
  Gop H1 (`gop_histdata_tick.py`, gio server NY+7): gia BID, spread_open = ask - bid o tick dau bar.
- Spread tai khoan XM gia lap theo CONG: xm_t = spread_that_t + (spread_XM_trung_binh - trung_binh(spread_that)),
  spread_XM_trung_binh = spread cua mo hinh phi XM hien co (`mo_hinh_chi_phi(df, ma)`). Tuc XM = gia ECN + markup
  co dinh; gian luc qua dem / tin la gian THAT cua nguon. Ap cho CA phi (moi lenh vao/ra tra spread cua bar do)
  lan loc S. Do nhay: mo hinh NHAN (xm_t = spread_that_t * XM_tb / tb_that) - chi bao cao, khong dung de chon.

## O
- Moi EA dich duoc co khung H1 (khung co dinh H1 hoac khong co dinh) x 7 cap x 26 to hop thu vien vong 7
  (`nhan/thu_vien_co_che.py`, tham so khong doi). 70 % dau trong mau, 30 % cuoi ngoai mau. Dem MOI o.
- Holm tren toan bo o cua luot nay (ho rieng; luot vong 7 da dung het alpha cua no).

## Do manh S (cau hoi chinh)
- Cap so sanh: moi to hop X khong chua S va |X| <= 2 -> (X, X+S): 11 cap / (EA, cap tien).
- Bao cao: so lenh bi loc, trung vi va trung binh chenh lech loi NM (X+S - X), ty le cap duoc cai thien,
  kiem dau (sign test) hai phia tren cac cap co chenh lech khac 0.
- Ket luan "S co ich" chi khi: trung vi chenh lech NM > 0 VA sign test p < 0,05. Nguoc lai: "khong chung minh duoc".

## Nhan / song (giong vong 7)
- Nhan cong: NM lai sau phi > 0, maxDD < 80 %, >= 20 lenh NM. Song: nhan cong + TM lai + p Holm < 0,05.
