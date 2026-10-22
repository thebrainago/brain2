# Bàn giao cho Claude — 21/10/2026 (22:15 giờ VN)

Máy nhà DESKTOP-05PNLGF (Admin), repo `C:\Users\DUNG\brain2`. PID dưới đây lấy theo trạng thái lúc bàn giao — kiểm lại bằng `tasklist` trước khi đụng.

## 1. Đang chạy (chỉ dừng bằng đúng PID)
**Tải dữ liệu dài:** powershell 8856 → python 16596; slot p6 terminal 15464 (`E:\mt5_tester\p6`).
- MT5 XM: xong 19 cặp, đều từ 2004 (H1 ~85.9k nến).
- Đang histdata, sau đó Dukascopy (gặp 429 thì lùi, không vượt chặn).
- Log: `data\du_lieu_dai\*.log`.
- Khi xong: `python -m nhan.du_lieu_dai --dung`, chạy test, commit `reports/du_lieu_dai/` và `config/phi_xm_micro.json`.

**Bộ chạy job:** cmd 14140 → python 5972 (mt5tools `chay_lien_tuc.py`), env `BRAIN_RAM_DONG=1 BRAIN_TICK_CHUNG=1 BRAIN_CONG_MOI=1 BRAIN_GEN=1 BRAIN_VONG2=1`, slot p1, p7, p3, p4.
- Sổ cái `reports\mt5_lien_tuc\so_cai.jsonl` (950 dòng lúc 22:10).
- Log `D:\brain2_log\vong2_21_10.log` rỗng do buffer (không phải lỗi).

## 2. Việc tiếp
1. Khi có `data\du_lieu_dai\du_lieu_dai.json`:
   `set BRAIN_ONG_DAN_DU_LIEU=data\du_lieu_dai\du_lieu_dai.json && python -m nhan.vong2 --top 40`
2. Chạy hàng chờ MT5 box `reports/phan_viec/hang_cho_mt5_box.jsonl`: 56 job lưới/28 thẻ + 4 job đợt 4 + 10 job đợt 5.
3. Khi rảnh: bước chuyển tick một lần `dung_chung_tick.ps1` (`tai_lieu/TANG_TOC_MT5.md` mục 2).
4. Đo tiếp RAM/agent và lệch OHLC-tick (`lech_ohlc_tick.jsonl`; 3 cặp đầu: lãi lệch 5–11%, DD lệch <2.2 điểm).
5. Slot MetaQuotes-Demo `C:\MT5_lich_su_metaquotes` đã chuẩn bị, chờ Anh tự mở tài khoản demo (để sau).

## 3. Dịch EA
- ai-box/qwen TẮT (`dich_llm=false`); Grok Bot dừng dịch vì tốn.
- Grok dịch tay đợt 3, 4, 5: 13 thẻ qua lọc Python (MÔ PHỎNG, CHƯA xác nhận MT5):

| Đợt | Thẻ | EA | Mã/khung | Lãi %/năm | DD % |
|---|---|---|---|---|---|
| 3 | sk_ea_2f4540d68a | GridScalperEA | AUDUSD H1 | 86.9 | 45.1 |
| 3 | sk_ea_3d5da5b65e | Sniper Gold Hybrid Recovery | XAUUSD H4 | 33.6 | 63.7 |
| 3 | sk_ea_9345f47763 | MakeGrid193 | EURUSD H1 | 24.8 | 50.5 |
| 3 | sk_ea_b18d784179 | Zerith XAU SwingGrid Recovery | GBPUSD H1 | 19.0 | 20.0 |
| 3 | sk_ea_31b7c0180f | Zerith MACD Martingale Grid | GBPUSD H4 | 18.1 | 55.7 |
| 3 | sk_ea_8760277bca | MintyGrid 7.2 | GBPJPY H4 | 15.4 | 43.5 |
| 4 | sk_ea_b7faac890a | Zerith Oneshot | GBPUSD H1 | 75.0 | 62.2 |
| 4 | sk_ea_a0d40c82ed | Hon-Matrix (gần đúng) | EURUSD H1 | 19.0 | 16.5 |
| 5 | sk_ea_37d18e3ece | ZONE_RECOVERY_AREA_II | EURCAD H1 | 62.6 | 55.9 |
| 5 | sk_ea_c67d5d31e9 | Ichimoku EA v1.3 | GBPCAD H4 | 33.0 | 27.1 |
| 5 | sk_ea_42415c4f24 | Trickerless_RHMP (gần đúng) | EURGBP H1 | 24.5 | 50.4 |
| 5 | sk_ea_94672bd399 | GBPJPY_EA_scalper_n6 | GBPJPY H4 | 24.1 | 43.4 |
| 5 | sk_ea_5056669865 | Zone_Recovery_Formula | GBPCHF H1 | 23.0 | 36.8 |

- Họ Zone Recovery chỉ có nhánh mua (lỗi `else` trong mã gốc).
- Commit sửa ValueError `luoi`: `800732b9` (lưu ý: prompt trong `cau_llm.py` đã đổi).
- Chi tiết: `reports/phan_viec/DICH_TAY_DOT3/4/5_2026-10-21.md`.

## 4. Quy tắc
- Không in/commit key; không đọc `E:\api.txt`.
- `taskkill` chỉ đúng PID; không kill `claude.exe` hay `C:\Program Files\XM Global MT5\terminal64.exe`.
- Không đụng Riot Games ổ D. KHÔNG tắt máy.
- Không autostash/rebase/force push.
- Chỉ báo số đo được; còn lại ghi CHƯA ĐO ĐƯỢC; mô phỏng ghi MÔ PHỎNG.
- Commit khi test pass. Lỗi cũ đã biết: test_dich_llm (403), test_an_toan_tester ×2, test_ghi_an_toan ×3, test_sinh_viec.
- Code của người khác: chỉ trong `data/`.

## 5. Chờ Anh quyết
- Phân bổ danh mục vòng 2 (nghiêng chia đều các hệ bền).
- Đo commission.
- Ưu tiên máy nhà.
- backtesting.online (cần đăng nhập Google).
- Crazy Dog (chỉ mua nếu có dùng thử).
- Slot Exness (115 job kẹt).
- Chọn lại LLM khi Anh báo.

## Cập nhật 21/10 23:00 – dừng toàn bộ máy nhà

- Anh cần máy chơi LoL nên Grok Bot đã dừng hết (taskkill đúng PID 9808, 8856, 15464, 16456). Bộ chạy job 5972/14140 đã tự kết thúc trước đó; sổ cái 955 lần thử đã đẩy (ed8c8be1).
- Dữ liệu dài: MT5 XM xong 19 cặp từ 2004; histdata dừng ở 09/2026; Dukascopy CHƯA chạy; bước gộp `nhan.du_lieu_dai --dung` bị ngắt giữa chừng, `du_lieu_dai.json` CHƯA có. Lần sau chạy lại `mt5tools\TAI_LICH_SU_MT5.bat` (phần đã tải sẽ bỏ qua), rồi gộp và chạy vòng 2 dữ liệu dài.
- Grok Bot hết hạn mức tới Chủ nhật: Claude tiếp quản toàn bộ. Tác vụ hẹn giờ TheBrain* vẫn Disabled.
- Danh mục chiến lược đã lọc: `reports/CHIEN_LUOC_DA_LOC.md`.
