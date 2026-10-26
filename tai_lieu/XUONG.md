# XƯỞNG TỔ HỢP (22/10/2026)

Chủ dự án: *"xây code để xử lý các hệ đạt: tối ưu tham số, bóc tách cơ chế để dùng cho chiến lược khác, kết hợp thêm tham số và phương pháp, kết hợp chéo các hệ pass với nhau (+ tự bổ sung cách tạo và xây tổ hợp)"*.

Xưởng nằm SAU `ong_dan.loc` và TRƯỚC `sinh_mt5`: lấy thẻ đã đạt (`DAT_LOC`/`DAT_CUOI`), làm ra thẻ mới, đăng ký lại vào ống dẫn ở bước `toi_uu`, để `ong_dan loc` → `sinh_mt5` đưa lên MT5 như mọi thẻ khác. **Mọi số trong Xưởng là MÔ PHỎNG Python** (lot thật, ký quỹ, stop-out, phí sàn; chưa đo được phí thì PHÍ TẠM). MT5 mới là phán quyết cuối.

## Vì sao không trùng `vong2` / `ghep_cheo`
`vong2` (walk-forward, Monte Carlo, stress phí, lưới thô), `ghep_cheo` (vào × quản lí, hai nguồn), `kho_co_che` giữ nguyên. Xưởng bổ sung đúng chỗ còn thiếu:

| Thiếu | Xưởng làm |
|---|---|
| So sánh hệ ở rủi ro khác nhau (lot khác nhau) | **Kéo lot** bằng chia đôi trên engine thật tới sụt giảm mục tiêu, điểm = lãi %/năm ở DD đó (`xuong_may.chuan_lot`) |
| Tối ưu ngẫu nhiên 16 phép | Successive halving (nửa IS → IS → kéo lot) + pattern search + **cao nguyên** (láng giềng ≥ 70 % điểm) + độ bền theo đoạn (`xuong_toi_uu`) |
| Không biết tín hiệu hay quản lí gánh | **Phân rã**: quản lí trên tín hiệu thay thế dịch vòng (không còn quan hệ với giá) và tín hiệu với quản lí trung tính → nhãn `QUAN_LI_GANH` / `TIN_HIEU_GANH` / `CA_HAI_DEU_LAI` / `CAN_CA_HAI` / `KHONG_LAI` (`xuong_tach`) |
| Bóc cơ chế dùng lại | Tách **nguyên tử** (nguồn lệnh, quản lí, gỡ lệnh, bộ lọc) vào `kho_co_che` để `cay_quan_li`/hệ khác lấy |
| Chỉ ghép 2 nguồn | Tín hiệu mới: **bỏ phiếu K/N**, **chuyển chế độ** (biến động, xu hướng, giờ, thứ, vị trí kênh — nhân quả), **giãn lệnh**, **đảo chiều**, **sự kiện đóng băng** (`xuong_tin_hieu`) |
| Không có đột biến/lai | Toán tử `dot_bien` (đổi cấu trúc), `lai_ghep` (lai quản lí), `chuyen_ma` (cấy sang tài sản khác), có thống kê **bandit** chia ngân sách toán tử theo tỉ lệ chốt |
| Ghép chéo chạy cùng lúc | **Danh mục** (`xuong_danh_muc`): tham lam trên đường vốn cộng, bảng lot chung, tương quan ngày |

## Đường chạy
```
python -m nhan.xuong cha                       # nạp hệ đạt, kéo lot, phân rã, tách nguyên tử
python -m nhan.xuong chay --phut 30 --song-song 4 --dd 60 [--toan-tu cay_quan_li,bo_phieu] [--gan-dat] [--khong-ghi]
python -m nhan.xuong toi-uu <id_the>           # tối ưu sâu một thẻ
```
Thứ tự: nạp cha → sinh (mỗi toán tử, hạn mức theo bandit) → sàng A (45 % IS, lot tham chiếu) → sàng B (IS đủ) → kéo lot → tối ưu sâu top N (chỉ trường quản lí EA chạy được) → đăng ký → danh mục. Kết quả: `reports/xuong/XUONG.md`, `ket_qua.json`; cache phép đo `data/xuong/xuong.sqlite` (chạy lại không đo lại).

Rồi: `python ong_dan.py loc` → `python ong_dan.py sinh_mt5` (thẻ Xưởng đi đường VAO_CSV vì tín hiệu không phải kiểu `brain` thuần).

## Luật tìm kiếm
- Chọn trên **IS (70 % đầu)**; OOS chỉ là NHÃN trong báo cáo (đúng chỉ thị 16/10: không dùng làm cổng).
- **Lot khuyến nghị** kéo lại trên TOÀN KỲ tới `--dd` (mặc định 60) vì DD IS thường đẹp hơn OOS (đo tổng hợp: IS 50 → OOS 78,8) → lot đăng ký qua được `loc_python` (DD < 65).
- Không gian tìm kiếm chỉ gồm trường quản lí **EA MT5 thật sự chạy** (`TRUONG_QL_MT5`, không có `go_cheo`), nên mọi kết quả Python xác nhận được bằng MT5.
- Tín hiệu kiểu `lenh_ngoai`, `luoi` chưa hỗ trợ trong Xưởng → `CHUA_DO_DUOC`, không bao giờ `ÂM`.

## Giới hạn phải nhớ
1. Danh mục xấp xỉ **cộng đường vốn**: chưa mô phỏng ký quỹ/stop-out chung và DCA theo vốn. Bảng lot là gợi ý, chạy 2 EA cùng tài khoản trên MT5 để xác nhận. Nên ≤ 5 thẻ.
2. Dữ liệu tổng hợp trên cloud chỉ kiểm logic (14 test `test_xuong.py`). Ví dụ DCA không SL trên ~0,5 năm tổng hợp cho %/năm khổng lồ cả với tín hiệu đảo ngược: **đây là mẫu ngắn, không phải phát hiện** — kết quả có nghĩa chỉ khi chạy trên giá thật nhiều năm (máy nhà / box Grok).
3. Mỗi lần kéo lot ≈ 3–5 phép engine (~2–2,6 s/10 năm H1). Ngân sách thời gian đặt bằng `--phut`; lượng lớn chạy song song `--song-song` (mỗi tiến trình một engine, chỉ tiến trình cha ghi SQLite).
