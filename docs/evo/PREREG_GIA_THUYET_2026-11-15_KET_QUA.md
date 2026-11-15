# Kết quả 8 giả thuyết đã tiền đăng ký — 15/11/2026 (Asia/Saigon)

Tiền đăng ký đóng băng lúc 12:57, commit `a1315ae`, **trước** khi chạy backtest. Tham số không chỉnh. IS: ngày < 2016-01-01. OOS: ≥ 2016-01-01, nhìn một lần. N_FDR = 8, Benjamini–Hochberg α = 0.05. Đòn bẩy 1×. Phí XM DEMO đo trên `E:\mt5_tester\p4` (p4 đã tắt sau khi đo; không dùng `E:\evo_forward`).

**Không giả thuyết nào sống sót** (cửa OOS và q_BH ≤ 0.05). Không viết EA mới, không chạy Strategy Tester, không gắn thêm vào forward demo.

## Cửa sổ dữ liệu

| Mã | Nguồn | Bắt đầu | Kết thúc |
|---|---|---|---|
| US100 | ^NDX tiền mặt | 1985-10-01 | 2026-11-13 |
| US500 | ^GSPC tiền mặt | 1970-01-02 | 2026-11-13 |
| US30 | ^DJI tiền mặt | 1992-01-02 | 2026-11-13 |
| GER40 | ^GDAXI tiền mặt | 1999-01-04 | 2026-11-13 |
| JP225 | ^N225 tiền mặt | 1999-01-04 | 2026-11-13 |
| UK100 | ^FTSE tiền mặt | 1999-01-04 | 2026-11-13 |
| XAU | Yahoo GC=F | 2000-08-30 | 2026-11-13 |
| AUDCAD | tiền mặt (mô tả) | 2003-12-01 | 2026-11-14 |

Vàng 1985 không có trên hộp; (h) bắt đầu khi từng mã có dữ liệu. EURUSD đã đo phí trên p4 nhưng không có lịch sử D1 dài nên không đưa vào bảng bề rộng. Lịch FOMC: 335 ngày họp **định kỳ** (1985–2026) từ trang Fed; loại conference call, họp khẩn, bị huỷ, notation vote (2020 còn 7 họp vì 17–18/3 bị huỷ).

Phí mới (median M15, fin dài hạn): GER40Cash# spread 1.95 / 5.01%/năm, Friday triple; JP225Cash# 6.0 / 3.27%; UK100Cash# 1.60 / 7.09%; GOLD.i# 0.20 / 7.09%, Wednesday triple. US100/500/30 giữ bảng 15/11 (~6.48%/năm, spread 1.95 / 0.55 / 3.9).

## Kiểm định chính (N_FDR = 8)

p = random-shift 1000 (dịch vị thế, phí tính lại), trừ (e): long mọi đêm nên dịch vị thế suy biến — p dịch chuỗi lợi nhuận qua đêm, giữ lịch phí.

| H | Luật (đóng băng) | IS n / PF / Sharpe / CAGR / DD / p | OOS n / PF / Sharpe / CAGR / DD / p | q_BH | Cửa | Sống sót |
|---|---|---|---|---|---|---|
| a | IBS equal-risk US100+US500+US30 | 1497 / 0.71 / −0.62 / −8.6% / 99.5% / 0.285 | 385 / 1.35 / 0.52 / 5.7% / 19.7% / 0.160 | 0.522 | Không | Không |
| b | TOM equal-risk cùng rổ | 552 / 1.01 / 0.02 / −0.1% / 47.5% / 0.007 | 130 / 1.34 / 0.31 / 2.0% / 11.9% / 0.371 | 0.522 | Không (p) | Không |
| c | RSI(2)<10, trên SMA200, US100 | 237 / 1.45 / 0.27 / 2.5% / 53.7% / 0.011 | 87 / 1.35 / 0.25 / 1.8% / 14.1% / 0.424 | 0.522 | Không | Không |
| d | Đáy 5 phiên, giữ 5 phiên, US100 | 698 / 0.94 / −0.08 / −3.6% / 84.2% / 0.132 | 234 / 1.28 / 0.42 / 5.6% / 33.0% / 0.413 | 0.522 | Không (p) | Không |
| e | Long close→open, US100 | 7628 / 0.25 / −7.72 / −61.6% / 100% / 0.014 | 2732 / 0.99 / −0.06 / −1.8% / 38.3% / 0.432 | 0.522 | Không | Không |
| f | Trước lễ NYSE ∪ FOMC, US100 | 484 / 0.93 / −0.31 / −2.2% / 70.2% / 0.004 | 184 / 1.13 / 0.17 / 0.8% / 13.5% / 0.388 | 0.522 | Không | Không |
| g | SMA 10 tháng, 1×, US100 | 26 / 3.94 / 0.34 / 4.8% / 48.6% / 0.230 | 9 / 9.02 / 0.53 / 8.0% / 28.7% / 0.457 | 0.522 | Không (p) | Không |
| h | IBS equal-weight GER40+JP225+UK100+XAU | 565 / 1.07 / 0.13 / 0.8% / 32.6% / 0.121 | 362 / 0.96 / −0.10 / −0.9% / 29.9% / 0.906 | 0.906 | Không | Không |

Cửa sự kiện cần ≥30 lệnh, TB>0, PF≥1.20, Sharpe≥0.30, p≤0.05. Cửa (e)(g): Sharpe≥0.30, p≤0.05, CAGR>0.

## Câu hỏi US500 / IBS

US500 IBS **đơn** (xác nhận, không phải kiểm định chính): OOS 353 lệnh, PF 1.44, Sharpe 0.64, 6.0%/năm, DD 10.9%, **p = 0.051** — trượt cửa p. Yếu hơn US100 đơn cùng luật (8.7%/năm, Sharpe 0.66, p = 0.073, cũng trượt p). Rổ equal-risk (a) không ổn định hơn US100 đơn: OOS chỉ 5.7%/năm, p = 0.160, IS vẫn rất âm (CAGR −8.6%, DD 99.5%). Không tối ưu lại thành phần rổ sau OOS.

(Ứng viên demo đang chạy vẫn là luật D1 IBS US100 đã kiểm trước đó; bài này không mở lại hay hạ ứng viên đó.)

## Xác nhận (không nằm trong FDR — không được "chọn hệ đẹp" sau khi nhìn)

Hai ô **đạt cửa OOS thô** nhưng **không** phải kiểm định chính, không có q_BH, **không được đưa vào EA / demo**:

- US30 IBS đơn: OOS PF 1.59, Sharpe 0.83, 7.5%/năm, DD 14.0%, p = 0.006. Muốn xét thì phải tiền đăng ký lại từ đầu, nhìn OOS một lần trên cửa sổ mới.
- XAU TOM: OOS PF 1.90, Sharpe 0.73, 6.1%/năm, DD 13.3%, p = 0.015. Cùng quy tắc: chỉ mô tả bề rộng.

Các xác nhận khác đều trượt cửa. IBS không lặp lại trên GER40/JP225/UK100/AUDCAD. TOM vàng OOS đẹp nhưng IS gần hoà (PF 1.05, p = 0.44). Overnight US100/US500 sau phí XM lỗ. SMA10 US100 OOS +8.0%/năm nhưng p = 0.46 — đúng với bài học cũ: phần lớn là drift dài hạn, không phải edge vào lệnh.

## Việc đã / chưa làm

- Không viết EA, không compile, không chạy tester p4, không đụng `E:\evo_forward` / p5 / slot live.
- Mã chạy: `tools/kiem_dinh/evo/prereg_2026-11-15/ibs_prereg_hypotheses.py` (seed 20261115, 1000 random-shift). Bảng đầy đủ: `docs/evo/prereg_2026-11-15/`.
