# Bàn giao nguồn SEEKER — 2026-11-07

Phiên này sửa bộ đọc và cách ghi lỗi của nguồn **đã có**, không thêm catalog mới, không push `main`, không merge, không chạy MT5, không đụng máy nhà, không restart runner.

Nhánh: `cursor/seeker-source-recovery-ca1f`.

Mâu thuẫn với `TRI_NHO/00_DOC_TRUOC.md` mục 7 (phiên xong thì `git push origin main`): lệnh phiên này cấm push/merge/force-push `main`. Đã ghi vào `TRI_NHO/QUYET_DINH.md`. Worker máy nhà vẫn tự commit `hang_doi` trên `main`; đừng rebase nhánh này lên từng commit hàng đợi.

## Việc đã xong và đã test

Lệnh (không mạng, trừ smoke):

```
python -m pytest test_seeker_nguon_loi.py test_nguon_seeker.py test_cong_khai.py test_seeker_v2.py test_nang_cap_20_10.py::test_loc_trung_truoc_khi_tai -q
python -m seeker.chan_doan
python -m seeker.cong_khai.kho_83
python -m seeker.chan_doan --smoke 2
```

`--smoke` trần cứng 5 URL. Lần chạy 2026-11-07 03:01 (giờ máy, box UTC) chỉ 2 URL. Không quét 311, không quét 1600.

| Việc | Kết quả |
|---|---|
| 311 nguồn | `unknown` 166, `not_implemented` 113, `auth` 18, `stale` 14. `no_data` = 0. Quy tắc dùng được = 0 |
| Bản quét sổ 2026-10-20 | Chỉ 2 nguồn (arxiv robots, quantconnect 3 mục). Gắn `stale`, không gọi là 0 nguồn |
| MQL5 Code Base / GitHub / TradingView / diễn đàn | Parser thuần + fixture. HTTP 200 mà 0 mục = `parse` hoặc `not_implemented`, không phải danh mục rỗng |
| LiteFinance | Danh sách thiếu DD = chưa đánh giá (`so_ho_so` giữ số hồ sơ). Chi tiết bị chuyển hướng = `auth`. Vỏ JS = `parse` |
| CSV MQL5 `/export/history` | Redirect/HTML login = `auth`, không phải 0 lệnh |
| 83 tín hiệu | `reports/seeker_nguon/KHO_83.json`: 23 không USD, 14 lẫn, 46 có USD. Cả 83 `thieu_du_lieu` (chưa có CSV). 0 giao dịch được |
| Lưới từ khoá | Không còn loại hệ. CSV lệnh chồng mới là `chung_minh_lenh`. Cảnh báo 2020/2022 là nhãn |
| Nhịp | `seeker/nhip_tai.py`: ≥ 4 giây/host, cache, lùi 429 cùng UA, dừng host khi challenge, resume |

Smoke thật (không đổi UA, không tắt TLS):

- `https://www.mql5.com/en/signals/1862128` HTTP 200, 148569 ký tự, parser đọc được. Màn hình: Growth 9214.64%, DD 11.7%, CAGR 236.41%/năm, tuổi 44.85 tháng, 746 lệnh, XAUUSD.i, máy chủ thật. **Đây là lịch sử người khác, không phải ĐẠT của hệ mình.**
- `https://social-trading.exness.com/strategy/110170778` `network`: `Errno -2 Name or service not known`. **Không thấy 198.18.0.1 trên box này.** Giả thuyết proxy/DNS 198.18.0.1 của bản 03/11 vẫn chưa được phiên này chứng minh, và lỗi DNS này cũng không chứng minh site chết.

## Không được quét lại

- Đừng chạy `python -m seeker.cong_khai.chay` (1600 id, 2026-11-03, cache 72 giờ nằm trong `data/`, gitignore).
- Đừng chạy `python -m seeker.nguon_file.quet` với mặc định 5 trang Code Base + 25 repo.
- Đừng `seeker_quet_nguon.py --ep` cả 311 từ box này. Myfxbook/ForexFactory/forex-station đã challenge hoặc HTTP 200 mà 0 chủ đề; dừng, không đổi UA.
- Đừng tải CSV history MQL5. Endpoint đòi đăng nhập. Trình duyệt là việc của phiên cha.
- `data/cong_khai/tin_hieu.jsonl` không có trong git. Đừng tái sinh `reports/MQL5_LOC_CHAT.md` khi thiếu file đó — bản 03/11 vẫn là danh sách 83.

## Cách đọc trạng thái

`python -m seeker.chan_doan` chỉ đọc sổ + bản chụp đã commit.

- `unknown`: chưa đo. Không phải 0 kết quả.
- `stale`: có bản cũ hơn 3 ngày. `loai_ban_chup` là loại của bản đó. `lan_thanh_cong` chỉ khi bản đó là `ok`.
- `auth`: sổ khai báo đăng nhập, hoặc bản chụp challenge/login. Không lấy cookie.
- `not_implemented`: thủ công, trình duyệt, hoặc Pine chưa nằm trong HTML tĩnh.
- `no_data`: bộ đọc chạy đúng và nguồn thật sự rỗng.
- `quy_tac_dung_duoc`: luật đã giải mã điểm vào và có OOS. Hiện **0**. Mã `.mq5` tải về và 1065/83 màn hình không tính.

Báo cáo: `reports/seeker_nguon/CHAN_DOAN.md`.

## Kho 83

```
python -m seeker.cong_khai.kho_83
python -m seeker.cong_khai.kho_83 --nhap DUONG.csv --id 2394758 --url https://www.mql5.com/en/signals/2394758
```

`--url` phải đúng `https://www.mql5.com/en/signals/<id>` và id phải nằm trong 83. File HTML login bị từ chối. CSV ghi vào `data/cong_khai/csv/` (gitignore) kèm `<id>.nguon.json`. Sổ commit chỉ giữ sha256, số dòng, cấp `replay_csv`. Replay không phải hệ giao dịch. Chưa có điểm vào giải mã và OOS thì `giao_dich_duoc` vẫn false.

Ưu tiên hiển thị: nhóm 0 (không USD) trước, nhóm 2 (USD/vàng/crypto) vẫn giữ. Trùng tên + cùng mã là `trung_nghi_ngo`, không gộp. Khớp tên 70% không phải chứng.

## Mâu thuẫn lưới

Lọc 03/11 loại 244 tín hiệu vì từ khoá lưới/martingale và thiếu năm 2020/2022 (`reports/MQL5_LOC_CHAT.md`). Chỉ thị 07/11: không suy nhãn lưới từ từ khoá, không vứt hệ lưới/DCA có lãi. Code `seeker/cong_khai/loc_chat.py` đã đổi theo chỉ thị mới. Các cổng tuổi ≥ 24 tháng, tài khoản thật, ≤ 3 mã, DD, CAGR, đường growth **giữ**. Bản markdown 83 không bị ghi đè.

## File chính

| File | Vai trò |
|---|---|
| `seeker/phan_loai_loi.py` | auth / challenge / network / parse / not_implemented / no_data / stale / unknown / robots |
| `seeker/nhip_tai.py` | giãn cách, cache, lùi 429, dừng challenge, resume |
| `seeker/chan_doan.py` | chẩn đoán 311 + smoke ≤ 5 |
| `seeker/nguon_file/phan_tich.py` | Code Base, GitHub API, TradingView, diễn đàn |
| `seeker/cong_khai/kho_83.py` | kiểm kê và nhập CSV |
| `seeker/khop_trung.py` | trùng chắc và trùng nghi |
| `seeker/fixtures/` | HTML/JSON/CSV đã cắt, không bí mật |
| `test_seeker_nguon_loi.py` | test các mục trên |

`seeker/thu_thap.py`: `tai_ro()` phân loại; sau challenge không gọi tiếp cùng host. `tai()` vẫn trả None khi stale để không dùng bản cũ như dữ liệu mới.

## Việc phiên sau (không làm trùng)

1. CSV 83: chỉ nhập file chủ đã xuất. Ưu tiên 23 tín hiệu không USD trong `KHO_83.md`, đừng bỏ 46 tín hiệu USD.
2. Pine: chỉ dịch khi HTML tĩnh có `//@version` (`boc_pine`). Trang JS = `not_implemented`. Không bật LLM trả phí.
3. Code Base 99 EA làn A nằm trong bản `seeker/nguon/nguon_file.json`. Mã tải về ở `data/nguon_file/` (gitignore, có thể không có trên box này). Chưa có quy tắc đã giải mã.
4. Myfxbook, Forex Factory, forex-station: dừng khi challenge. Không vượt.
5. Exness: trên box này là DNS `Errno -2`, không phải 198.18.0.1. Đo lại từ máy nhà nếu cần, ghi đúng loại, không tắt TLS.
6. 166 nguồn `unknown` cần một lượt có nhịp khi chủ muốn, từng cụm nhỏ (`seeker_quet_nguon.py --chi a,b`), không `--ep` cả sổ từ datacenter.
7. Đừng gọi màn hình công khai là ĐẠT của hệ. Cần điểm vào đã giải mã rồi OOS/demo.
