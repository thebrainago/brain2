# Bộ kiểm định các hệ phi kỹ thuật — Gann Sq9, Fibo, chart phi chuẩn, lịch, hồi về trung bình

Mã nguồn chạy lại 7 vòng kiểm định trên vàng (GC=F) và S&P 500 (ES=F, ^GSPC, SPY).

**Báo cáo và bảng kết luận:** [docs/kien-thuc-thong-ke/phi-ky-thuat/README_vi.md](../../../docs/kien-thuc-thong-ke/phi-ky-thuat/README_vi.md)

## Cài đặt và dữ liệu

Chạy mọi lệnh từ thư mục này (`tools/kiem_dinh/gann_sq9`):

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python download_data.py
```

`download_data.py` tạo các file `data_*.pkl` từ Yahoo Finance. **Không commit** file `.pkl`, `.npy`, `.venv` hay bí mật.

## Tái chạy (tóm tắt)

```bash
# Vòng 1: mức Sq9 neo thường
.venv/bin/python sq9_stats.py
.venv/bin/python make_summary.py
.venv/bin/python strategy_sim.py

# Vòng 2: neo lớn + Sq9 thời gian
.venv/bin/python test_a_major_price.py
.venv/bin/python test_b_sq9_time.py
.venv/bin/python make_summary2.py

# Vòng 3: xác suất đi tiếp
.venv/bin/python test_c_continuation.py
.venv/bin/python analyze_c.py
.venv/bin/python make_summary3.py

# Vòng 4: scalp sau cú sập
.venv/bin/python test_d_impulse.py
.venv/bin/python analyze_d.py
.venv/bin/python make_summary4.py

# Vòng 5: bản đồ xác suất theo mốc phiên
.venv/bin/python test_e_session_map.py
.venv/bin/python test_e_daily_history.py
.venv/bin/python analyze_e.py

# Vòng 6: Fibo xoắn ốc + chart phi chuẩn
.venv/bin/python test_f_spiral.py
.venv/bin/python analyze_f.py
.venv/bin/python test_g_charts.py
.venv/bin/python analyze_g.py
.venv/bin/python make_summary6.py

# Vòng 7: trend, hồi về trung bình, lịch, biến động/tin tức
.venv/bin/python test_h_trend.py
.venv/bin/python test_h_meanrev.py
.venv/bin/python test_h_calendar.py
.venv/bin/python test_h_volnews.py
.venv/bin/python make_summary7.py
.venv/bin/python analyze_h_best.py
```

Script Pine (TradingView v6) nằm trong `pine/`. Ngày FOMC/CPI/NFP nằm trong `events/`. CSV kết quả nhỏ (< 1 MB) nằm trong `results/` … `results7/`.
