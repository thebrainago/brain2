# 03 — Kế hoạch thử: "chế độ bóng" (không đổi cổng, chỉ thêm số đo)

Nhãn: **ĐỀ XUẤT, chưa duyệt.** Mọi việc dưới đây chỉ **thêm cột/báo cáo song song**. Không việc nào đổi quyết định QUA/KHÔNG của vòng nào,
không sửa `config/*.json`, không dùng MT5 tester, không ghi `nao.db`. Kết quả ghi vào `de_xuat/ket_qua/T<n>.md` (thư mục tạo khi cần) và `reports/goi_<tên>.md`.

## Tiền đăng ký (đóng băng trước khi ai chạy gì)

- **Dự đoán ghi trước:** với v30 và v31, sau khi thêm `p_gom_cum` và `Holm theo k`, **không ô nào đạt < 0,05**
  (lý do: p GĐ2 thô nhỏ nhất đã là 0,108 và 0,241 — `reports/vong30.json`, `reports/vong31_moc.json`; gom cụm với tương quan dương trong cụm làm p lớn hơn, không nhỏ hơn).
  Nếu dự đoán sai (có ô qua): **không** gọi là phát hiện; ghi "ứng viên cho xác nhận trên dữ liệu MỚI" — GĐ2 đó đã bị nhìn.
- **Dữ liệu GĐ2 của v30–v32 không được tái dùng để xác nhận** bất cứ gì sau khi đã dùng chẩn đoán ở T5.
- Mọi ngưỡng "chuyển từ bóng sang chính" (T6) do **chủ dự án** chốt; số trong file này chỉ là đề xuất.

## Việc, theo thứ tự

| # | Việc | Đầu vào | Đầu ra | Làm ngay được? |
|---|---|---|---|---|
| T0 | Đọc `01`–`02`, chạy `python -m pytest de_xuat/ma_mau -q` (7 test) và `python de_xuat/ma_mau/mo_phong_dac_tinh.py` (~11 s). Ghi đồng ý / không đồng ý / đã đo vào `PHAN_HOI_GROK.md` | repo | `PHAN_HOI_GROK.md` | Có |
| T1 | **Đo ICC thật.** Với lệnh GĐ2 từng ô của v30 và v31 (và GĐ1 của v32): `n`, `sd`, số cụm, `deff` theo cụm = *tuần vào lệnh* và = *ngày vào lệnh* (`hieu_ung_thiet_ke`). Báo trung vị và p90 theo họ | lệnh từng ô (cột `tg`, `ret`, `ts`) — chạy lại script trên box | bảng `T1.md` | Có |
| T2 | **Cột song song cho GĐ2 v30/v31:** `p_cum`, `p_holm_k` (Holm trên k ô đã kiểm), `p_holm_cu` (cũ, họ 20.503), `mde_bps` (power 80 %). Không thay cột cũ, không đổi cột `Qua?` | như T1 | `reports/vong30_bong.md`, `vong31_bong.md` | Có (sau T1) |
| T3 | **Bảng power thật** theo họ từ n, sd, deff của T1: MDE @ 80 % và số lệnh cần để thấy 5 / 10 / 20 bps ở α = 0,05; k = 20; m = 20.503. Thay bảng giả định sd = 100 bps ở `01` mục 2.3 | T1 | `T3.md` | Có |
| T4 | **Thời gian lưới v32 trên 1 chuỗi null** (đảo dấu từng nến). Nếu một lượt lưới ≤ 5 phút → chạy N = 200 làm thử, ghi `p_họ` = `p_max_null` và `max t` null; N = 1.000 khi tốn ≤ ~1 giờ. Null phải khai báo trước (xem `02` mục 4.6) | dữ liệu H1 v32 | `T4.md` | Có |
| T5 | **IC hạng chẩn đoán** GĐ1→GĐ2 cho họ đã đóng (v30, v31): `ic_hang` trên mọi ô đủ lệnh ở cả hai giai đoạn. **Ghi rõ đây là nhìn GĐ2 của ô chưa đăng ký → dữ liệu GĐ2 đó coi như đã dùng** | T1 | `T5.md` | Có, sau khi T2 xong |
| T6 | **Hiệu chuẩn hai chiều** (luật `CLAUDE.md`: null_ty_le_lot + thu_luc_cong) cho cổng mới (p gom cụm + Holm theo k + null cấp họ): (a) ≥ 200 chuỗi null `nha_may_null.tao_null_day_du` qua toàn phễu → tỉ lệ "qua"; (b) cấy cạnh +5 / 10 / 20 / 40 bps (tổng quát hoá `nha_may_null.cay_edge_vao_gia`) lên n ≥ 1.500 lệnh/ô → tỉ lệ bắt. **Canary hỏng thì dừng, không tính p-value nào** | T1–T4 | `T6.md` | Có |
| T7 | **Hồi quy MT5 ↔ Python** trên sổ cái 630 lần (`02` mục 4.8): `a`, `b`, `σ_ε`, và có bao nhiêu trong "242 ứng viên đạt IS+OOS" có cận dưới khoảng dự đoán 80 % > 0 | `reports/mt5_lien_tuc/` | `T7.md` | Có (chỉ đọc sổ cái) |
| T8 | Dựng thử forward demo với SPRT (`02` mục 4.9) cho **1** ứng viên + luật dừng ghi trước | cần chủ dự án (tài khoản demo, thời hạn, `e1`) | — | **Chờ chủ dự án** |

## Tiêu chí cho chủ dự án xét chuyển từ "bóng" sang "chính" (đề xuất, chủ dự án chỉnh)

Chỉ xét khi T6 xong và canary qua:

1. Tỉ lệ dương tính giả trên null ≤ **1,5 × α danh nghĩa** (đo, không giả định).
2. Power ở cạnh 10 bps, n = 1.500 ≥ **70 %** với k = 20 (mô phỏng tổng hợp cho 80 %; số thật có thể thấp hơn nếu cạnh phân rã giữa GĐ1/GĐ2).
3. Không ô nào "qua" ở bóng mà cổng cũ chặn **vì lý do tiền** (không thắng mua-giữ, phí khai, thiếu lệnh) — cổng cứng về tiền giữ nguyên.
4. Chủ dự án đã điền (hoặc chủ động bỏ qua) `04_CAU_HOI_CHU_DU_AN.md` mục V, C, π.

## Rủi ro đã biết của chính đề xuất

- Bài đo ở `ma_mau/ket_qua_mo_phong.md` là **tổng hợp**: sd = 100 bps, ICC giả định, GĐ1/GĐ2 độc lập, cạnh không phân rã → power thật thấp hơn.
- Gom cụm với G nhỏ (< ~20) vẫn hơi lạc quan; dùng `p_boot` theo cụm làm kiểm chéo.
- Holm/BH theo k chỉ hợp lệ khi k ứng viên được **chọn chỉ bằng GĐ1** và đăng ký trước (xem `02` mục 3). Vòng nào chọn sau khi liếc GĐ2 thì phải dùng họ rộng hơn.
- Null cấp họ phụ thuộc lựa chọn null; chọn sai (block bootstrap cho tín hiệu hồi quy) sẽ nuốt tín hiệu — đã ghi cảnh báo ở `02` mục 4.6.
- Chưa có bằng chứng nào ở đây rằng tăng power sẽ tìm ra cạnh thật. Đề xuất làm cổng **trung thực hơn về những gì dữ liệu có thể trả lời**, không hứa có cạnh.

## Định dạng báo cáo mỗi việc (theo `CLAUDE.md` "Quy tắc phiên")

Đã làm gì · bằng chứng (lệnh chạy + commit) · số trước/sau · rủi ro còn lại · việc chưa làm. Phân biệt `CHƯA ĐO ĐƯỢC` với kết quả ÂM.
