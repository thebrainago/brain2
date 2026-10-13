# VÒNG LẶP NGHIÊN CỨU LIÊN TỤC (thiết kế, bắt đầu vòng 27 — 13/10/2026)
Chạy trên BOX (không phải máy nhà). Mỗi chu kỳ lấy MỘT việc ở đầu hàng, làm xong → đẩy xuống cuối hàng (xoay vòng 5 việc).
Trạng thái máy: `vong_lap_state.json` (con trỏ hàng) + `vong_lap_log.json` (nhật ký từng chu kỳ).

## Luật cứng (mọi việc)
- Chỉ số ĐO ĐƯỢC; mô phỏng ghi "mô phỏng"; không đo được ghi "CHƯA ĐO ĐƯỢC".
- QUA = lãi sau phí XM thật (`phi_xm_that.py`, spread đo theo giờ khi có) VÀ maxDD < 80 %, dương cả hai nửa
  (phát hiện/kiểm), tiền đăng ký trước (`reports/vongNN_tien_dang_ky.md`), không nhìn trước (test cắt dữ liệu),
  Holm CỘNG DỒN (mọi ô đã thử, kể cả ô dừng ở tầng 1 với p = 1). Sau vòng 27: xem `reports/vong27.json` → `ho_holm`.
- Lọc theo tầng: (1) cạnh thô TRƯỚC phí, cả hai nửa > 0 → (2) đa tài sản SAU phí XM thật → (3) quản trị/ghép.
- Luôn ghép chéo phong cách (hồi quy × xu hướng × động lượng × giờ vào); thử cả khung nhỏ (M5/H1/H4) và lớn (D1/W1).
- Không bí mật / mã EA bên thứ ba trong git (mã chỉ ở `data/cau_kho/`, git bỏ qua; repo giữ tóm tắt luật + URL).
- Commit/push CHỈ khi test xanh; cập nhật `GHI_CHU_NANG_CAP_GROK.md` mỗi chu kỳ.
- Không vượt Cloudflare/chặn bot, không đăng nhập mạng xã hội, không Telegram, không mua gì.

## Hàng 5 việc xoay vòng
1. **Nạp dữ liệu** — thêm tài sản/khung miễn phí tải được (HistData M1 qua thư viện `histdata`, Dukascopy datafeed
   khi không 503, Yahoo D1). Ghi nguồn vào `/workspace/du_lieu_fx/NGUON_DU_LIEU.md`; dữ liệu NGOÀI repo.
2. **Seeker + bộ đọc** — tải mã công khai (mql5 Code Base, GitHub API), sửa lý do hỏng hàng đầu của `nhan/doc_ma.py`
   / `nhan/tien_xu_ly_ea.py`, đo lại tỷ lệ dịch trên toàn bộ EA đã tải (số trước/sau).
3. **Vòng thử** — tiền đăng ký → chạy `vNN.py` → Holm cộng dồn → ghi bảng mô phỏng.
4. **Tốc độ hệ thống + bài học** — đo profile (cProfile), thêm đệm/vector hoá/song song khi rẻ; cập nhật `tai_lieu/KINH_NGHIEM.md`.
5. **Hàng chờ máy nhà** — cập nhật `tai_lieu/HANG_CHO_MAY_NHA.md` (việc chỉ máy nhà làm được: MT5 tester, nguồn bị chặn trên box).

## Một chu kỳ
`git pull` → đọc con trỏ → làm việc → `pytest` các test liên quan → cập nhật GHI_CHU + KINH_NGHIEM → commit/push nếu xanh → tăng con trỏ.
