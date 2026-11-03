# Thợ MT5 máy nhà — hàng đợi git (03/11/2026)

Máy nhà (Windows, MT5, XM) bật 8–12 giờ/ngày sẽ tự lấy việc từ `hang_doi/can_test/`, chạy MT5 Strategy Tester
(tick thật, tài khoản XM), ghi kết quả vào `hang_doi/da_test/` rồi push. Box (Grok Bot) gieo việc mới.

## Anh chạy (một lệnh, trong thư mục repo brain2 trên máy nhà)

```
may_nha\CHAY_THO_MT5.cmd
```

- Lần đầu lệnh tự clone repo vào `D:\brain2_tho` (bản RIÊNG của thợ, không đụng thư mục Anh đang làm).
  Muốn chỗ khác: `set BRAIN_THO_DIR=E:\brain2_tho` trước khi chạy.
- Slot MT5: tự chọn slot portable đang đăng nhập XM trong `BRAIN_SLOTS` / danh sách mặc định. Chỉ định tay:
  `may_nha\CHAY_THO_MT5.cmd --slot D:\mt5_tester\p1`
- Thử một việc rồi dừng: thêm `--mot-lan`. Dừng hẳn: Ctrl+C.

## Thợ làm gì

1. `git fetch` + `merge --ff-only` (không rebase, không autostash, không force push).
2. Nhận việc ưu tiên cao nhất: chuyển tệp sang `hang_doi/dang_lam_<tên máy>/`, commit, push. Push bị từ chối = máy khác
   nhận trước -> bỏ commit local của thợ, kéo lại, chọn việc khác.
3. Chạy: `mt5_backtest` (mỗi hệ số lot một lần chạy MT5 riêng; CSV lệnh vào được nhân lot — bản vá lot CSV),
   `mql5_demo_download` (xem dưới), `myfxbook_fetch` (tải trang công khai).
4. Ghi `hang_doi/da_test/<id>.json` (CAGR %/năm từ lãi ròng, DD equity MT5, k tốt nhất đạt DD<80 % và CAGR>10 %), báo cáo
   `.htm` vào `hang_doi/bao_cao/`, thêm dòng `hang_doi/so_cai.jsonl`, push. Lặp.
5. Hết việc: tự sinh việc dò hệ số lot mịn quanh mức an toàn lớn nhất; vẫn hết thì chờ 5 phút rồi kéo lại.

An toàn: thợ chỉ giết cây tiến trình DO CHÍNH NÓ phóng (theo PID) khi quá giờ (mặc định 4 giờ/lần chạy).
Không bao giờ taskkill theo tên — `claude.exe`, `terminal64.exe` XM của Anh vẫn chạy bình thường.

## Việc cần Anh (demo EA Market)

Demo `.ex5` trên MQL5 Market chỉ tải được từ terminal đã đăng nhập tài khoản MQL5: trong slot XM mở tab **Market**,
tìm tên EA (danh sách trong `hang_doi/da_test/demo_*.json` trạng thái `CHO_ANH`, hoặc `reports/MQL5_LOC_CHAT.md`),
bấm **Free Demo**. Thợ tự thấy tệp trong `MQL5\Experts\Market\` và tự sinh việc backtest 2016–2026 cho EA đó.
