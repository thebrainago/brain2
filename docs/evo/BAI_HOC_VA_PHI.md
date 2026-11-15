# Bài học kiểm định & phí đo thật (Evo, 2026-11-15)

> ĐỌC FILE NÀY TRƯỚC khi chấm/kiểm ứng viên trong brain2. Chi tiết: `docs/evo/kiem_toan_tieu_chi.md`, `docs/evo/ung_vien_vuong_tieu_chi.md`.

## 1. Phí đo thật (XM Ultra Low demo, `E:\mt5_tester\p5`, không commission)

| Symbol | Spread nến trung vị / p90 (pip) | Tick trung vị | Model brain2 cũ | Swap L/S %/năm | Ghi chú |
|---|---|---|---|---|---|
| AUDCAD | 2.4 / 2.7 | 2.9 | 3.84 | −0.8 / 3.8 | model cao ~30% |
| AUDNZD | 2.7 / 2.8 | 3.3 | 4.19 | −0.1 / 4.5 | model cao ~27% |
| EURCAD | 1.8 / 2.4 | 2.6 | 2.89 | 1.5 / 1.5 | sát |
| EURGBP | 1.8 / 2.0 | 2.0 | 1.63 | 2.5 / −0.5 | model THẤP 18% |
| AUDCHF | 1.5 / 1.8 | 2.0 | 2.40 | −3.5 / 6.5 | model cao ~20% |
| EURUSD# | 1.0 / 1.1 | 1.1 | 1.09 | 2.5 / −0.5 | sát |
| CADJPY# | 2.7 / 3.1 | 3.2 | — | — | |
| US100Cash# | 1.95 điểm | 1.95 | — | phí qua đêm | |

- Swap âm = được cộng. Symbol có `#` trên tài khoản này: `swap_mode=0` (không swap).
- Spread phẳng cả ngày, TRỪ giờ 0 (rollover): vọt 4–8 pip. KHÔNG vào lệnh lúc 00:00 server.
- Chạy lại nhóm "phí ăn hết lãi" (217) với phí thật: chỉ cứu 21 (40 nếu bỏ swap) ⇒ phí là thật, không phải model thổi phồng.

## 2. Lỗi pipeline đã sửa (nhánh `evo/sua-tieu-chi`, commit 631852e)
1. **PF tính theo nến thay vì theo lệnh** (`nhan/do_luong.py` `chi_so`) ⇒ kéo PF về ~1 (vd 2.1 thành 0.87). Nay có `pf_lenh`; chuỗi phơi nhiễm cùng chiều/rổ DCA = 1 lệnh.
2. **p-value lấy max của ~6 seed** (`nhan/cong.py` `placebo`) ⇒ lệch lên (0.002 thành 0.02). Nay gộp đếm mọi seed thành 1 p.
3. Đã kiểm ĐÚNG: không trừ phí 2 lần, swap theo đêm (thứ Tư x3), Sharpe năm hoá theo số nến thật, dịch tín hiệu đúng 1 nến.
4. Chưa sửa: `dich_mq5` cho D1 vào lệnh 00:00 (rollover).

## 3. Bài học
- 1.214/1.236 giả thuyết là quét mẫu × tham số tự động, KHÔNG phải hệ đã có lãi từ Myfxbook/statement. Quét nhiều = nhiều pass ăn may (1.236 phép thử ⇒ ~62 đạt p≤0.05 do may).
- Tài khoản cent/lot nhỏ KHÔNG làm hệ pass: PF/Sharpe/p không đổi theo lot.
- Nới lỏng ngưỡng ⇒ thêm nhiễu (237 "PASS" cũ thì 220 thua placebo). Chỉ nới hợp lệ: gộp lệnh nhiều cặp với quy tắc đóng băng; PF≥1.1 chỉ tham khảo.
- Edge FX thật đơn cặp ~Sharpe 0.2–0.4: phải gộp rổ nhiều cặp + dữ liệu dài/forward.
- Khung: tỷ lệ phí/lãi gộp H1 1.26×, H4 0.66×, D1 0.24×; % hệ còn dương sau phí H1 33%, H4 47%, D1 51% ⇒ FX nên H4/D1.
- Python lạc quan hơn MT5 Strategy Tester rõ rệt ⇒ luôn kiểm MT5 trước khi gọi ứng viên mạnh.
- Holdout 60/40 cũ đã bị nhìn nhiều lần ⇒ pass thật cần forward demo sau 2026-10-02.
- Gate "ăn khe rollover" PHẢI giữ (bỏ thì 88 pass giả).
- Giả thuyết nên đăng ký trước, ít biến thể, có lý do kinh tế.

## 4. Tình trạng ứng viên (cập nhật 2026-11-15 12:05)
- PASS THẬT: 0.
- **Forward demo đang chạy** (bắt đầu 15/11 11:29, `E:\evo_forward`, XM DEMO 345930355; xem `docs/evo/forward_demo.md`): AUDCAD H4 IBS (magic 26111501), EURUSD H4 mất cân bằng cuối phiên (26111502), US100 IBS D1 (26111503). Mới bắt đầu ⇒ chưa phải bằng chứng.
- Sống sót MT5 trước đó: AUDCAD H4 IBS (PF 1.68), EURUSD H4 MOC (PF 1.24, 150 lệnh). ~1%/năm ở 1×.
- Rớt MT5: AUDNZD H1 vol cạn (1.03), EURGBP D1 Keltner (0.85), GBPCAD D1 IBS đáy kép (0.67).
- **Lô 289 khẳng định CHO_KIEM → MT5** (`docs/evo/mt5_lo_khang_dinh.md`): 216 chạy (`DA_KIEM_MT5`), 73 chưa có giả thuyết (giữ CHO_KIEM). 47/216 đạt 4 tiêu chí MT5 2016–2026 (PF lệnh, Sharpe năm, ≥30 lệnh, TB>0) – CHƯA pass: chồng in-sample, 216 phép thử, dồn AUDCAD H4.
- Đạt tiêu chí Python đã sửa: 54 (kho chính) + 35/164 tồn.
- US100 IBS (chỉ số CFD): ứng viên; MT5 2016–2026 PF 1.38, ~7.9%/năm ở 1×.

## 5. Bài học vận hành MT5 (2026-11-15)
- `nhan/dich_mq5` đã sửa: `InpGioTranh=0` (không khớp lệnh giờ server 0 – rollover), `InpChiDemo` (ngoài tester chỉ DEMO), đếm lại nến đã giữ khi khởi động lại.
- Tester dùng chung `Bases` junction KHÔNG chạy song song (lỗi khoá [32] → xml rỗng). `Expert=EVO\<ea>.ex5` trong `[Tester]`. `US500Cash#`, `NZDCAD#` trên tài khoản này.

## 6. Bài học quản lý lệnh / đòn bẩy US100 IBS (2026-11-15)
- Đòn bẩy không thêm edge: PF/Sharpe giữ nguyên, CAGR và DD tăng cùng nhau. XM US100 D1 2016+: 1× 13.8%/năm DD 20.5%; 3× ~39%/năm DD 53%, năm xấu nhất −30%.
- 32 cách thoát (SL/TP ATR, %, trailing, chốt sớm): không cách nào thắng bản gốc trên IS; SL chặt làm hệ hồi quy kém đi. "Thoát IBS>0.5" chỉ đẹp OOS (IS âm), là nhìn trộm.
- Không SL / giữ đến hoà vốn: cháy ở 3× (2022-10, 1987); 1× vẫn kém gốc. Phí qua đêm ~6.5%/năm cộng dồn khi giữ lâu.
- Cắt lỗ thảm hoạ 6–10% / ATR 3–5 và giảm lot theo VIX/vol: không qua IS, không giảm DD 3× OOS. Không đưa vào EA.
- Giữ mua có đòn bẩy: 2–3× vỡ trần DD 80% (2000, 2022). Chỉ hợp lệ: US100 lọc SMA10 tháng, đứng ngoài khi dưới, 1–1.5× (OOS ~12%/năm DD ~41% ở 1.5×). US500 sau swap XM là kém.
- XM: đòn bẩy 1:1000 nên stop-out 20% không đệm; ở 3× giá ngược ~33% là cháy. US100Cash# lot min/step 0.1.
