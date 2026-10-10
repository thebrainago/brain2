# CAU KHO MA - kho SEEKER qua bo doc MQL5 cau truc (`doc_ma`)
*2026-10-10 21:39*  /workspace/seeker_mau/mql5

## Pheu

| buoc | so |
|---|---|
| tong | 160 |
| bo_kich_thuoc | 0 |
| trung_noi_dung | 2 |
| trung_mau_thu | 0 |
| duy_nhat | 158 |
| mql4_bo_qua | 0 |
| ea_dat_lenh | 117 |
| loi_bo_doc | 0 |
| co_diem_vao | 95 |
| ra_co_che | 1 |

## Lan (phan_loai_ma, file duy nhat MQL5)

- chien_luoc: 63
- quan_tri: 59
- tien_ich: 34
- chi_bao: 2

## So chinh (cung dinh nghia `mau_thu/do_moc.py`)

- diem vao tim thay: 240
- diem vao dich duoc: 1  -> **0.4%**
- co che ra: 1 (tu 1 EA)
- phan loai diem vao: {"dich_duoc": 1, "ma_chet": 7, "quan_ly_vi_the": 9, "chua_dich": 223, "quan_ly_dich_duoc": 0}
- loi ra theo EA: {"giu_co_dinh": 1}

## Ly do chua dich (top)

- 63x `khong tim duoc guard cua lenh vao`
- 16x `lenh vao nam trong nhanh else`
- 5x `type == ORDER_TYPE_BUY`
- 5x `lenh vao la ma chet (sau return vo dieu kien)`
- 3x `true`
- 3x `ro lenh chua dich: OnTick khong co dang `if(PositionSelect(_Symbol)) d`
- 3x `isBuy`
- 2x `guard rong sau khi dich`
- 2x `loc thoat som: vol < minVol`
- 2x `MQLInfoInteger(MQL_TESTER)`
- 2x `OrderCalcMargin(ORDER_TYPE_BUY, _Symbol, minVol, ask, margin`
- 2x `!hasSell`
- 2x `signal == ORDER_TYPE_BUY`
- 2x `false`
- 2x `orderType == ORDER_TYPE_BUY`

## EA ra co che

- `74135_EMA_Cross_EA5.mq5` vao 1/2, co che 1, ho xu_huong 
