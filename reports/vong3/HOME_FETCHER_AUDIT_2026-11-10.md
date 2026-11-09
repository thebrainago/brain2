# Kiểm định công cụ fetch máy nhà và lịch sử Myfxbook — 10/11/2026

Phạm vi: chỉ làm offline. Không gửi request mới tới website nào, không thao tác máy nhà. Mọi số dưới đây đều là số đo lại từ file đã lưu.

## 1. Rà soát `seeker_unblock/` (cấp trên cùng; không đụng `box/`)
- **Đã xoá:**
  - `dpi_proxy.py`: tách gói ClientHello để né chặn SNI.
  - `ech_test.py`.
  - `pw_capture.py`: ghi XHR bằng Playwright.
  - `save.py`: gửi header XHR.
  - `myfxbook_fix_cols.py`: gọi XHR để lấy tiêu đề cột.
- **Đã viết lại:**
  - `net.py` dùng `requests` thường với User-Agent trung thực. Bỏ curl_cffi giả Chrome, bỏ DoH và proxy.
    Gặp 403/429/503 hoặc trang chặn Cloudflare thì ném `SiteBan` và dừng ngay ở lần đầu.
  - `probe.py`, `dl.py`: theo `net.py` mới.
- **Đã vô hiệu hoá:**
  - `myfxbook.py fetch` thoát mã 2, vì endpoint XHR nội bộ không có tài liệu. Chỉ còn `parse-html` offline.
  - `mql5_browser.py` thoát mã 2. Không còn điều khiển Playwright hay lưu phiên đăng nhập từ shell.
- **Giữ nguyên:**
  - `mql5.py`, `myfxbook_discover.py`: trang công khai, nhịp 4–5 s, dừng khi bị chặn.
  - Công cụ offline: `myfxbook_fix_auto.py`, `myfxbook_fix_offline.py`, `tom_tat_myfxbook.py`.
- **Thêm mới:** `kiem_dinh_lich_su.py`, `test_offline.py`.
- **Kiểm tra bí mật và thông tin cá nhân:**
  - Quét các mẫu `password`, `token=`, `cookie`, `session`, `@`, `api.txt`, tên user Windows và link statement: không còn trong code hay README.
  - Đã bỏ tên repo khỏi User-Agent.
  - Dữ liệu thô (có tên trader công khai và token quảng cáo của trang) chỉ nằm ở `/workspace/nguon_khac/home/`, ngoài git.
- **Test:**
  - `python3 -m py_compile` trên 12/12 file .py: đạt.
  - `python3 test_offline.py`: 4/4 đạt, gồm: dừng ngay ở lần chặn đầu tiên; parse HTML thô 6426348 ra 20 dòng với cột đúng; `fetch` và `mql5_browser` thoát mã 2; sửa cột offline đúng.
- **Trạng thái chặn:** Myfxbook chặn IP nhà (Cloudflare 1015/429) từ khoảng 00:00 ngày 10/11 (giờ VN), do bản cũ chạy 6 tiến trình song song. Đã dừng toàn bộ.
  Trên máy nhà: đã tắt `dpi_proxy`, WARP vẫn ở trạng thái cũ (Disconnected).

## 2. Kiểm định lịch sử ba hệ (`kiem_dinh_lich_su.py`, kết quả ở `/workspace/nguon_khac/home/kiem_dinh_3he.json`)

| Hệ | Số dòng / tổng Myfxbook báo | Trùng record | Tiêu đề cột từ HTML thô | Đối chiếu từng trường | Cột lot | Trạng thái |
|---|---|---|---|---|---|---|
| 6426348 (555) | 3.747 / 3.747 | 0 | Có, khớp cột CSV | 20/20 dòng trang 1 khớp 8 trường | **Không có** | **VERIFIED** (nghĩa cột; trang 2..N chỉ kiểm số dòng và trùng lặp) |
| 9900626 (H traders oil) | 2.744 / 2.744 | 0 | **Không có HTML thô** | — | Cột suy ra là "lots", chưa xác minh | **UNVERIFIED** |
| 11992558 (FX3) | 1.236 / 1.236 | 0 | **Không có HTML thô** | — | Cột suy ra là "lots", chưa xác minh | **UNVERIFIED** |

Với hai hệ UNVERIFIED, thứ tự cột chỉ được suy ra từ dữ liệu: cột thời lượng đúng định dạng và dấu pips trùng dấu lãi.
Cách này không đủ để xác lập nghĩa cột, nên **không đưa ra số phí hay kết luận PASS/FAIL nào** cho hai hệ này.

### Đo được cho 6426348 (chỉ các trường đã xác minh, chỉ lệnh đã đóng)
- 3.546 lệnh Buy/Sell, từ 2020-04-21 đến 2026-11-04, tương đương 6,54 năm và 542 lệnh/năm. Ngoài ra có 149 lần nạp và 52 lần rút.
- Tỉ lệ lệnh có lãi 97,24%. Pips trung bình 119,67, trung vị 64,5.
- Lãi USD: tổng 229.754,23, trung bình 64,79 mỗi lệnh. Lệnh lỗ nặng nhất −280,00, lệnh lãi lớn nhất 14.562,6.
- Thời gian giữ lệnh trung bình 348,1 giờ, trung vị 27,9 giờ.
- Tổng nạp 121.463,33 USD, tổng rút 292.650,00 USD.
- Mã chính: WTI.FS 1.718 lệnh, USOIL 1.385, AUDCHF 221, CHINA5 87, TESLA+ 56, META+ 33.

### Không đo được, và lý do
- **Cổng phí XM cho 6426348: CHƯA ĐO ĐƯỢC.** 0% số lệnh thuộc mã có trong `config/phi_xm_micro.json`; dầu, chỉ số, cổ phiếu, BTC và AUDCHF đều chưa có phí XM.
  Ngoài ra thiếu lot, nên không quy được spread và swap ra USD.
  Quy theo pips (độc lập với lot) cũng cần phí XM của chính mã đó, mà mã này chưa có.
- **CAGR và DD:** không tính. Bảng History chỉ có lệnh đã đóng, không có equity hay DD thả nổi. Nạp/rút thường xuyên và không có lot.
  Tỉ lệ thắng 97% cùng thời gian giữ lệnh dài là dấu hiệu có thể có DD thả nổi lớn mà dữ liệu này không thấy được.
  Số Myfxbook tự công bố trên trang danh sách (gain +18.376,14%, DD 44,52%) là **số của nguồn, không phải số đo của mình**.
- **9900626 và 11992558:** không đưa số nào vì UNVERIFIED. 11992558 có 72,5% số lệnh thuộc mã có phí XM.
  Hệ này có thể đo phí nếu có CSV export chính thức, hoặc HTML thô có tiêu đề cột.
- **HappyGold 12106293:** chưa có dữ liệu, vì bị chặn.

### Cách có dữ liệu hợp lệ
- Myfxbook: CSV export chính thức (Anh tự thao tác, link gửi qua email) hoặc Myfxbook API chính thức. Không gọi XHR nội bộ.
- MQL5: Anh tự bấm Export history trên trình duyệt đã đăng nhập.
- Bổ sung phí XM cho USOIL/WTI vào `phi_xm_micro.json` (đo từ terminal XM) thì mới chạy được cổng phí cho các hệ dầu.

## 3. Dữ liệu thô (ngoài git)
`/workspace/nguon_khac/home/`:
- `myfxbook/`: 14 CSV, 47 meta, `systems_list.csv` (569 hệ), `tom_tat.csv`.
- `mql5/`: `stats.csv` và 60 JSON.
- `raw/`: HTML thô.
- `kiem_dinh_3he.json`.

Bản sao 3 hệ ưu tiên: `/workspace/myfxbook/{6426348,9900626,11992558}.csv` cùng meta.
