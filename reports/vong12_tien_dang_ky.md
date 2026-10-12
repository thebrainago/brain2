# Vong 12 - he cu tu the-brain (CHI THAM KHAO) - DANG KY TRUOC
Ghi 2026-10-12 ~13:30 UTC+7, sau khi DOC dac ta trong the-brain, TRUOC khi tai du lieu AUDCAD / chay bat ky o nao.

## Doc duoc tu the-brain (nhanh claude/autonomous-trading-system-rzzt7h, khop main va 3c982747)
- V6: "he chi so My (US500 CFD), 8,6 %/nam, chay tren XM cent" (HANDOFF.md). Loi vao = IBS < 0,2 tren D1
  (+ lop "bias > 0" vi mo/VIX/mua vu, + danh muc chi so My, + bar theo phien My). BAO_CAO_2026_09_03: IBS<0,2 don
  bay 4x 20,71 %/nam, maxDD -49,4 % (Python). Ban thu IBS tren CFD 15/08 bi cong FAIL. Ma EA/.set goc da MAT (VPS het).
- AUDCAD: danh muc 8 cum hoi quy H4 (16 he chon top-40 tren train 2016-2021, 16/40 song holdout 2021-2026),
  "27 %/nam o lot 36, DD 30 %" tren MT5 tester (holdout) + demo. Sau do (18/09) chinh the-brain ket luan: 668 co che
  AUDCAD, khong he nao vua du tan suat vua Sharpe > 0; ung vien rsi_dao_chieu Python Sharpe 1,16 -> tester 0,68,
  +2,76 %/nam. Dinh nghia 16 he khong day du trong repo (ten co che sinh tu ma EA) -> chi dung lai duoc nhung he CO dinh
  nghia trong `nhan/mau.py`.

## Quy tac dua vao (3, CO DINH)
1. V6_IBS_DANH_MUC: IBS < 0,2 -> mua o dong cua, giu 1 ngay, rieng tung chi so ^GSPC va ^NDX, moi chi so 1/2 von
   (bac 3 cua `_hieu_chuan_v6`). Lop bias KHONG dung lai (dinh nghia phu thuoc nhieu nguon, khong tai tao trung thuc) - ghi CHUA LAM.
   Du lieu tu 1990 (^NDX tu 1990 neu co). Phi CFD US500/US100 nhu vong 10-11.
2. AUDCAD_RSI_DAO_CHIEU: AUDCAD H4, RSI14 < 30 -> mua, RSI14 > 55 -> dong (m_rsi_dao_chieu, chi mua).
3. AUDCAD_OU_N50_Z25_MUA: AUDCAD H4, z = (close - SMA50)/SD50 < -2,5 -> mua, |z| < 0,3 -> dong (chi mua).
Du lieu AUDCAD: HistData M1 -> H4 gio server NY+7, cang dai cang tot (muc tieu 2010 -> 2026-09).
Phi: spread khu hoi AUDCAD 2,8 bps tra mot lan, truot 0,5 bps/chieu; swap = (r_AU - r_CA) - 1 %/nam (BIS), x1 va x1,5.

## Kiem (nhu vong 11)
30 % cuoi = ngoai mau; Sharpe sau cong bo (V6: 2010; AUDCAD: 2026-09-15 -> khong co doan sau -> dung NM thay);
Holm tren 26 + 3 = 29. Song: lai sau phi toan chuoi > 0, maxDD < 80 %, NM lai x1 VA x1,5, p Holm < 0,05.
