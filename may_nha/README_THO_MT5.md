# Thợ MT5 máy nhà — hàng đợi git (03/11/2026)

> **Đọc trước:** [`VAN_HANH_MAY_NHA.md`](VAN_HANH_MAY_NHA.md) (giới hạn máy, cách chạy) · nhật ký [`../nhat_ky/van_hanh_may_nha.md`](../nhat_ky/van_hanh_may_nha.md).

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

## Chạy song song nhiều slot (phân luồng)

```
may_nha\CHAY_THO_MT5.cmd --song-song              (mỗi slot portable đăng nhập XM một thợ)
may_nha\CHAY_THO_MT5.cmd --song-song 2            (tối đa 2 thợ)
may_nha\CHAY_THO_MT5.cmd --song-song --den-gio 22:00   (ngừng nhận việc mới lúc 22:00, làm nốt việc đang chạy rồi dừng hẳn)
may_nha\CHAY_THO_MT5.cmd --song-song --gio-chay 10     (chỉ nhận việc mới trong 10 giờ)
```

- Số thợ mặc định = số slot XM tìm thấy (`BRAIN_SLOTS`, ví dụ `set BRAIN_SLOTS=D:\mt5_tester\p1;E:\mt5_tester\p3`),
  **trần 4** và **trần nửa số luồng CPU** để máy vẫn dùng được. Thợ chạy ưu tiên BELOW_NORMAL, terminal tester ưu tiên IDLE.
- Mỗi thợ là một tiến trình riêng, tên máy `<tên PC>_<tên slot>` → thư mục `hang_doi/dang_lam_<tên PC>_<slot>/`.
  Mỗi thợ tự nhận việc qua khoá git (commit + push); trong cùng clone dùng thêm khoá tệp `.git/tho_git.lock` để không đụng nhau.
- Làn A (`co_ma_nguon`) luôn được nhận trước làn B.
- Hết khung giờ: thợ không nhận việc mới, làm xong việc đang chạy rồi thoát mã 3 → `CHAY_THO_MT5.cmd` dừng hẳn (không tự chạy lại).
  Lỗi khác → tự khởi động lại sau 60 giây. Lưu ý: `--gio-chay` tính lại từ lúc khởi động lại sau lỗi; muốn mốc cứng dùng `--den-gio`.

## Dừng / xem tiến độ

- Dừng: Ctrl+C trong cửa sổ đang chạy (hoặc đóng cửa sổ). Việc đang làm dở nằm ở `dang_lam_<máy>`; lần sau chạy lại thợ đó
  (cùng tên máy/slot) làm tiếp việc đó trước.
- Tiến độ: `python may_nha\tho_mt5.py --tinh-trang` (trong `D:\brain2_tho`): số việc chờ + giờ ước, việc đang làm từng thợ,
  5 việc xong gần nhất. Nhật ký chi tiết: `D:\brain2_tho\hang_doi\log_<tên PC>.txt`. Trên GitHub: xem `hang_doi/so_cai.jsonl`.

## Thư mục

| Thư mục / tệp | Nghĩa |
|---|---|
| `hang_doi/can_test/` | việc chờ (spec JSON) |
| `hang_doi/dang_lam_<máy>/` | việc máy/slot đó đã nhận (khoá) |
| `hang_doi/da_test/` | việc xong + `ket_qua` (CAGR, DD, PF, lãi theo năm, k tốt nhất) |
| `hang_doi/loai/` | việc bị cổng loại (làn B khớp < 70 % / lịch sử không đạt) |
| `hang_doi/bao_cao/` | báo cáo `.htm` MT5 của từng lần chạy |
| `hang_doi/so_cai.jsonl` | sổ cái: thêm / nhận / xong / hỏng |
| `TRI_NHO/dac_diem_he/<hệ>.md` | đặc điểm tốt của hệ (kể cả trượt), thợ tự ghi sau mỗi việc |
| `TRI_NHO/DAC_DIEM_TOT.md` | mục lục mảnh tốt để ghép |

## Thợ làm gì

1. `git fetch` + `merge --ff-only` (không rebase, không autostash, không force push).
2. Nhận việc ưu tiên cao nhất: chuyển tệp sang `hang_doi/dang_lam_<tên máy>/`, commit, push. Push bị từ chối = máy khác
   nhận trước -> bỏ commit local của thợ, kéo lại, chọn việc khác.
3. Chạy: `mt5_backtest` (mỗi hệ số lot một lần chạy MT5 riêng; CSV lệnh vào được nhân lot — bản vá lot CSV),
   `mql5_demo_download` (xem dưới), `myfxbook_fetch` (tải trang công khai).
4. Ghi `hang_doi/da_test/<id>.json` (CAGR %/năm từ lãi ròng, DD equity MT5, k tốt nhất đạt DD<80 % và CAGR>10 %), báo cáo
   `.htm` vào `hang_doi/bao_cao/`, thêm dòng `hang_doi/so_cai.jsonl`, push. Lặp.
5. Ghi đặc điểm hệ (`nhan/dac_diem_he.py`): kiểu vào/quản lý, mã/khung có lãi, năm có lãi, PF, tỉ lệ thắng, DD, lý do trượt
   → `TRI_NHO/dac_diem_he/` + `TRI_NHO/DAC_DIEM_TOT.md`, commit cùng kết quả.
6. Hết việc: tự sinh việc dò hệ số lot mịn quanh mức an toàn lớn nhất; vẫn hết thì chờ 5 phút rồi kéo lại.

An toàn: thợ chỉ giết cây tiến trình DO CHÍNH NÓ phóng (theo PID) khi quá giờ (mặc định 4 giờ/lần chạy).
Không bao giờ taskkill theo tên — `claude.exe`, `terminal64.exe` XM của Anh vẫn chạy bình thường.

## Việc cần Anh (demo EA Market)

Demo `.ex5` trên MQL5 Market chỉ tải được từ terminal đã đăng nhập tài khoản MQL5: trong slot XM mở tab **Market**,
tìm tên EA (danh sách trong `hang_doi/da_test/demo_*.json` trạng thái `CHO_ANH`, hoặc `reports/MQL5_LOC_CHAT.md`),
bấm **Free Demo**. Thợ tự thấy tệp trong `MQL5\Experts\Market\` và tự sinh việc backtest 2016–2026 cho EA đó.
