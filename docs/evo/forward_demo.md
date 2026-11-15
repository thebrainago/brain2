# Forward demo – 3 ứng viên (Evo, bắt đầu 15/11/2026 11:29 Asia/Saigon)

> ỨNG VIÊN – CHƯA PASS. Forward vừa bắt đầu ≠ pass. Chỉ tài khoản DEMO.

## Máy & terminal
- Máy nhà (DESKTOP-05PNLGF), bản MT5 portable riêng: `E:\evo_forward` (copy từ `E:\mt5_tester\p5`, `Bases` RIÊNG – không junction sang `shared_bases`).
- Profile `EvoForward` (4 chart). Khởi động: `terminal64.exe /portable /profile:EvoForward`.
- Bền vững: shortcut `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\EvoForward_MT5.lnk` (chạy lại khi user DUNG đăng nhập).
- File đánh dấu `E:\evo_forward\EVO_RUNNER_IN_USE.txt`.
- Tài khoản: XM **DEMO** `345930355` @ `XMGlobal-MT5 10` (tài khoản demo duy nhất brain2 có; mật khẩu KHÔNG lưu ở đây). Đã kiểm `ACCOUNT_TRADE_MODE=DEMO`, `terminal_trade_allowed=1` (file status bên dưới).
- Lưu ý: tài khoản này dùng chung với các slot tester và có sẵn 2 lệnh + 1 lệnh chờ KHÔNG phải của Evo (số dư ~1.009 USD, equity ~830 USD lúc gắn). EA chỉ quản lý lệnh theo magic + symbol; lot nhỏ để không ăn margin.

## EA đã gắn
| Chart | EA | Luật (đóng băng) | Magic | Lot |
|---|---|---|---|---|
| AUDCAD# | `EvoForward_H4` InpMaCoChe=0 | `AUDCAD.H4.mua_ibs_thap_kl_mong_khi_rsi_duoi_phan_vi_thap_atr_vua…giu4` | 26111501 | 0.01 |
| EURUSD# | `EvoForward_H4` InpMaCoChe=1 | `EURUSD.H4.mat_can_bang_lenh_dong_cua…giu2` (20–22h) | 26111502 | 0.01 |
| US100Cash# | `IBS_US100` (InpAckDemoOnly=true) | IBS<0.20 vào mở nến D1 sau; ra IBS>0.80 hoặc 4 nến | 26111503 | 0.10 |
| EURUSD# H1 | `EvoXuatCSV` | không đặt lệnh, chỉ xuất CSV mỗi 60 phút | – | – |

- `EvoForward_H4` sinh bằng `tools/kiem_dinh/evo/forward/sinh_forward.py` qua `nhan/dich_mq5` (bản đã sửa): `InpGioTranh=0` → KHÔNG vào/ra trong giờ server 0 (rollover, spread 4–8 pip); `InpChiDemo=true` → từ chối tài khoản không phải DEMO; khởi động lại giữa chừng thì đếm lại số nến đã giữ.
- `IBS_US100`: bản đã test MT5 + sửa: chỉ DEMO (`!= DEMO` → từ chối), khôi phục nến vào sau khi khởi động lại. CFD chỉ số đóng cửa lúc 00:00 nên lệnh tự chờ phiên mở.

## Dữ liệu forward (rẻ để kiểm)
`E:\evo_forward\MQL5\Files\`:
- `evo_forward_deals.csv` – toàn bộ deal của 3 magic (login, demo flag, giờ server, giá, lãi, swap, phí).
- `evo_forward_open.csv` – vị thế đang mở.
- `evo_forward_status.txt` – login, trade_mode, quyền giao dịch, số dư.

Kiểm nhanh: `Get-Content E:\evo_forward\MQL5\Files\evo_forward_deals.csv`.

## Tiêu chí kết luận forward
Chỉ đánh giá sau ≥ 30 lệnh/ứng viên (AUDCAD IBS ~11 lệnh/năm ⇒ cần gộp rổ cặp hoặc chờ lâu; EURUSD MOC ~14/năm; US100 IBS ~33/năm). So với MT5 tester cùng giai đoạn; tự kiểm: entry theo luật, %/năm trung thực, lot, tập trung.
