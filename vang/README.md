# Module vàng (`vang/`)

Backtest mọi họ tín hiệu sẵn có trong brain2 (và tổ hợp lọc + vào + quản trị) cho **XM GOLD CFD**, tài khoản micro (quy về mã `GOLD.i#`, lot chia 100 theo `may_nha/VAN_HANH_MAY_NHA.md`).

Trả lời / báo cáo tiếng Việt có dấu. Chỉ ghi số đã đo.

## Tiêu chí ĐẠT

CAGR kép > 10%/năm **và** DD tối đa < 80% sau phí XM, tối thiểu 20 lệnh.

## Cấu trúc

- `ma/du_lieu.py` — nạp nến XM GOLD.i (D1/H1, gộp H4) và parquet M5/M15.
- `ma/phi_xm.py`, `cau_hinh/phi_xm_vang.json` — phí đo từ `reports/phi_xm_micro_that.csv` (13/10/2026).
- `ma/tin_hieu.py` — họ tín hiệu: xu hướng, hồi quy, phá vỡ, phiên/ORB, mùa vụ, lọc.
- `ma/mo_phong.py` — mô phỏng lệnh (Numba) và lưới/DCA.
- `ma/chay_quet.py` — quét tổ hợp theo khung.
- `ma/keo_fxaurum.py` — kéo nến/order flow GCZ6 (chạy trên máy nhà, **không** gọi `syncTicks`/`syncHistory`).
- `ma/kiem_may_nha.py` — kiểm RAM, cổng 9001, khe p3/p4.
- `ma/orderflow.py` — backtest lọc order flow trên cửa sổ Fxaurum (~3 tháng).
- `bao_cao/` — kết quả tiếng Việt.
- `ket_qua/` — CSV số đo.
- `TRANG_THAI.md` — trạng thái và cách chạy tiếp.

## Cách chạy (trên box, thư mục gốc repo)

```bash
PYTHONUTF8=1 python3 -m vang.ma.chay_quet          # D1 H4 H1 M15 M5
PYTHONUTF8=1 python3 -m vang.ma.chay_quet H1       # một khung
```

Kéo data Fxaurum trên máy nhà (cổng `ws://127.0.0.1:9001/` đang mở, ghi ra `E:\brain2_tmp\vang\fxaurum`):

```bat
set PYTHONUTF8=1
python E:\brain2_tmp\vang\keo_fxaurum.py --out E:\brain2_tmp\vang\fxaurum
```

## Phí dùng khi mô phỏng

- Spread H1 trung vị 16 điểm (0,16 USD/ounce) khi nến không có cột spread; từ 2018-10-10 dùng spread nến.
- Mỗi chiều: nửa spread + trượt 0,5×spread (giả định thận trọng, chưa đo demo).
- Hoa hồng 0. Swap mặc định 0 (Ultra Low DISABLED); có file chạy lại top với swap đủ.

## Việc không làm trong module này

Không đụng thư mục `sp500/`. Không chạy `tho_mt5.py --song-song`. Không đọc `E:\api.txt`. Khe tester máy nhà: chỉ p3 và p4. Không tắt `claude.exe` hay terminal XM chính.
