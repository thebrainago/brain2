# Hệ xử lý lệnh dùng cho SP500 — KHUNG CHÍNH: HYB + AG (thiết kế phiên tối 26/11/2026)

> Nguồn: Anh gửi lại qua XAUUSD Scalp Bot (parent chuyển, 27/11/2026 20:08 giờ Việt Nam). Kết quả đầy đủ nằm ở máy nhà, `E:\backtests\sp500_sys\` (sweep_big, hybrid, antigrind). Phần dưới chép lại đúng thông số được gửi. Chỉ áp dụng cho vàng và SP500.

## Triết lý
- Gỡ lệnh bằng hedge + nhồi (pyramiding), không dùng SL cứng.
- Rổ có thể giữ nhiều ngày (95 giờ vẫn chấp nhận).
- DD tới khoảng 80 % là chấp nhận được, tính cả tiền nạp thêm: vốn khoảng 10.000 USD, có thể nạp thêm tới 30.000 USD.

## Hệ US500 HYB + AG 1,5x
**Vào lệnh**
- Mỗi lần vào: 3 lệnh × 0,1 lot.
- Chỉ vào khi tổng điểm chỉ báo ≥ 1:
  - +1 cho mỗi điều kiện: BB M15 dưới −2σ; nến M5 có râu từ chối; trong 2 giờ đầu phiên Mỹ; ATR thấp.
  - −1 nếu giá dưới VWAP −2σ.

**DCA (theo khoảng cách + vùng)**
- Hệ số lot 1,3; tối đa 10 tầng.
- Khoảng cách mỗi tầng là 3 ATR M15, sau đó dời về vùng mạnh nhất trong phạm vi ±1,5 ATR. Khoảng cách luôn giữ trong 1,5–4,8 ATR.
- Điểm vùng: zigzag 0,5; fibo 1; volume profile ES 1,5; quyền chọn 1,5.

**Chốt**
- Mỗi tầng chốt một nửa khi lời +1 ATR M15.
- Cả rổ thoát khi về hoà vốn.

**Hedge-nhồi**
- Mỗi đợt mở 5 lệnh ngược chiều, tổng = 1x rổ; tối đa 2x.
- TP 0,8 ATR M5.
- Không DCA khi đang có hedge ngược chiều mở.
- Giá phá lại một mức đã phá rồi thì không tính là lần phá mới.

**AG (anti-grind)**
- Mở hedge 1,5x khi độ dốc EMA200 D1 < 0 và rổ đã ≥ 5 tầng hoặc đã mở > 5 ngày.
- Đóng hedge khi giá lấy lại EMA200, hoặc khi rổ + hedge về hoà vốn.

## Kết quả đã có (phiên 26/11, chưa đo lại ở đây)
**US500, tháng 6 → tháng 11**
- Lãi +1.502, maxDD 576.
- Sống sót 11/11 kịch bản stress (7 sập mạnh, 2 giảm chậm, 2 gap). Kịch bản tệ nhất −2.719.
- Không có AG thì mọi phiên bản đều cháy khi giá giảm chậm.

**Sweep 230.400 cấu hình**
- Vùng tốt: lot 0,5, hệ số 1,15, khoảng cách 3 ATR, AG 2x. Lãi +1.840 đến +1.995, vẫn có lãi khi spread gấp 2.
- Lot ≥ 1,0 thua ở stress sâu.
- DCA < 1,5 ATR hoặc hệ số ≥ 1,5 làm tăng khả năng cháy.
- Hedge TP 0,3 ATR bị spread ăn hết.
- Các bộ lọc VIX/EM/phanh DD không giúp gì.
- DSR ≤ 0,15 và tương quan IS–OOS thấp, nên chưa có cấu hình nào thắng baseline.

## Quy trình kiểm chuẩn cho mọi hệ mới
1. Tách IS/OOS.
2. Spread gấp 2.
3. Chạy đủ 11 kịch bản stress.
4. Độ ổn định với tham số lân cận.
5. Xác suất cháy và lỗ thả nổi xấu nhất so với ngưỡng 80 % (tính cả tiền nạp thêm).
6. Deflated Sharpe.
7. Chạy bóng: chỉ ghi log, không đặt lệnh.

**Luật:** bot không bao giờ đặt lệnh thật và không đổi luật đang chạy thật.

## Việc của SP500 bây giờ
- Giai đoạn A: dùng tín hiệu từ dữ liệu Fxaurum (delta/footprint, cụm big trade, hấp thụ dựng từ tick, VWAP/POC, mức quyền chọn) làm ứng viên cải thiện **điểm vào** và **điểm vùng** của HYB+AG.
- Giai đoạn B: cắm các tín hiệu đó vào HYB+AG, so với baseline theo đủ 7 bước trên.

---

## Phụ lục: các bộ máy xử lý lệnh khác có trong repo (tóm tắt ngày 27/11/2026)

## Đã tìm phiên “tối 26/11” ở đâu, tìm thấy gì
- **Repo** (`git log --all`, 26/11 12:00 → 27/11 12:00): không có commit nào. Commit gần nhất trước đó là của các worker ngày 27/11.
- **Máy nhà:** không có tệp `.md/.mq5/.mqh/.py/.json/.txt/.set/.ini/.ps1` nào sửa trong khoảng 26/11 17:00 → 27/11 07:00, xét trong `E:\brain2_grok` (sâu 6 cấp), Desktop và Documents. Thư mục `C:\Users\DUNG\.claude` không có `projects`, chỉ có backups/cache/downloads/sessions (ngày 02/10) và settings.json.
- Các slot g3 và g12: tệp mới nhất đều của ngày 27/11 (boba_v3 lúc 19:07–19:29, SP500_WF_* lúc 19:10–19:25). `BRAIN_XuLiLenh` ở g3 có từ 04/11.
- **Box:** được dựng lại sáng 27/11 lúc 07:40, nên mtime cũ đã mất.
- Bot này không đọc được bản ghi của phiên chat khác.
- **Kết luận (cập nhật 20:40 27/11):** lần tìm đầu (ở trên) không quét `E:\backtests`, nên bỏ sót. Thiết kế phiên tối 26/11 do Anh đưa lại qua XAUUSD Scalp Bot. Toàn bộ kết quả nằm ở `E:\backtests\sp500_sys\` trên máy nhà (sweep_big, hybrid, antigrind; tệp ghi 26/11 19:49–23:41). Dữ liệu M1 dùng để dựng kịch bản s00 là `E:\backtests\rapid_hedge\US500Cash_M1.csv` (01/06 → 26/11/2026, 176.531 nến, giờ máy chủ XM; prep cộng 5h ra UTC+7). Đã chạy lại `sim_ag.run` cấu hình gốc HYB+AG 1,5x trên box: lãi +1.501,90 USD, maxDD 575,97, sống 11/11 stress, tệ nhất −2.719,17 — khớp đúng số của phiên 26/11. Ba bộ máy trong repo ở phụ lục dưới đây chỉ để tham khảo.

## 1. `ea_demo/BRAIN_XuLiLenh.mq5` (v1.10, 17/10 → 03/11/2026) — bộ máy rổ lệnh
Mỗi chiều (mua/bán) có một rổ. Mỗi tick, rổ được xử lý theo thứ tự sau:
1. **Cắt lỗ tuỳ chọn** `InpCatLoPct`: tính trên rổ + hedge + lãi/lỗ đã chốt của hedge. Mặc định 0, tức không SL.
2. **Giữ tối đa** `InpGiuToiDaNen`: đủ N nến thì đóng cả rổ.
3. **Đang khoá (hedge):**
   - **Gỡ:** khi tổng ≥ `InpGoTien` thì đóng hết.
   - **Mở khoá:** khi giá hồi `InpMoKhoaATR/Pct` từ cực trị thì đóng lệnh khoá. Ghi lại mốc, chỉ khoá lại khi giá vượt mốc đó.
   - Trong lúc khoá thì không nhồi và không TP.
4. **TP rổ:** tính từ giá vốn bình quân ± `InpTPATR/Gia/Pct`.
   - 4b. Gỡ sau khi đã mở khoá: rổ + phần đã chốt của lệnh khoá ≥ `InpGoTien`.
5. **Trailing rổ:** bật khi giá vượt giá vốn + kích hoạt; giá trả lại một khoảng thì đóng.
6. **Khoá (hedge):** rổ lỗ thả nổi ≥ `InpHedgeKhiLoPct` % số dư thì mở lệnh ngược chiều = tổng lot × `InpHedgeTiLe`. Tối đa `InpHedgeMaxLan` lần, và chỉ khi margin level ≥ `InpMarginMin`.
7. **Nhồi:**
   - `NHOI_NGHICH` (DCA): giá đi ngược một bước. Bước tính bằng ATR, giá hoặc %, có giãn bước `g^k`.
   - `NHOI_THUAN` (nhồi thuận / pyramiding): giá đi đúng chiều một bước.
   - Kiểu lot: đều, tuyến tính, hoặc nhân hệ số r. Tối đa `InpMaxTang` tầng.

**Vào lệnh:** MRZ, RSI, Donchian, không tín hiệu (luôn có rổ), hoặc **`VAO_CSV`**. Với `VAO_CSV`, EA đọc lệnh vào từ CSV `thoi_gian,ma,chieu,gia,nguon[,lot]` theo giờ server, đặt trong `Common\Files`. Lệnh vượt `SYMBOL_VOLUME_MAX` được tách. EA xuất `_lenh_mt5.csv` và `_gia.csv` để đối chiếu với Python.

**Bảo vệ:** giờ cấm (`InpGioCamTu/Den`), trần spread, margin tối thiểu. Có thêm các bộ lọc ADX, ATR percentile, NFP và file tin (mặc định tắt).

## 2. Bản Python tương ứng: `nhan/tai_khoan.py`, hàm `chay_tk`
Cùng logic như EA, chạy ở cấp tài khoản: lot thật, ký quỹ, stop-out, phí theo sàn. Thông số nằm trong `QuanLi`:
- TP: `tp_pct/tp_gia`.
- DCA: `dca_buoc_pct`, `dca_toi_da`, `dca_he_so_lot`, `dca_lot_tuyen_tinh`.
- Trailing: `trail_kich_pct`, `trail_khoang_pct`.
- Hedge: `hedge_khi_lo_pct`, `hedge_ti_le`, `mo_khoa_pct`, `hedge_max_lan`.
- Gỡ: `go_tien`; gỡ chéo giữa các rổ: `go_cheo`, `go_nguong_diem`.
- Khác: `cat_lo_pct`, `giu_toi_da_nen`, `margin_min_pct`, `gio_cam`.

Đầu vào là danh sách `LenhVao(nguon, chi_so, gia, chieu, lot)`, tức một “dòng lệnh vào” từ bất kỳ nguồn tín hiệu nào. `nhan/ong_dan.xuat_csv_vao` ghi dòng lệnh này ra CSV cho EA `VAO_CSV`.

## 3. Hai EA dịch ngược làm mẫu (bản nháp, chưa đo)
- **`BRAIN_DN_RoDCAHedge`:** hai rổ BUY/SELL chạy độc lập cùng lúc (hedge), lot đều. Thêm lệnh khi giá đi ngược `BuocPip`; đóng rổ khi giá đạt giá TB ± `TPPip`. Không SL.
- **`BRAIN_DN_LuoiHedgeTP`:** lưới hai chiều, mỗi mức có 1 BUY và 1 SELL với TP riêng. Đóng hết khi tổng thả nổi ≥ 0 và số lệnh ≥ `DongRoKhi`.

## Cách ghép với tín hiệu dữ liệu (giai đoạn B)
Tín hiệu orderflow ESZ6 (giai đoạn A) được đổi thành `LenhVao` trên trục nến M5 của US500Cash# XM.
1. Chạy `tai_khoan.chay_tk` với lưới `QuanLi`, gồm: chỉ TP, DCA nghịch, nhồi thuận, DCA + hedge/gỡ, có hoặc không đóng cuối phiên.
2. Xuất CSV, rồi chạy `BRAIN_XuLiLenh` ở chế độ `VAO_CSV` trên p6 (tick thật, vì XM có tick US500 từ 21/07/2025).

Tiêu chí: lãi ròng > 0 và DD < 80 %.
