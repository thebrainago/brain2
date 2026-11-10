# Bàn giao Grok Bot – brain2 (10/11/2026)

## 1. Mục tiêu và tiêu chí
- Tìm hệ giao dịch chạy được trên XM (Free Demo), tiêu chí cuối: **DD < 80%** và **CAGR kép > 10%/năm**.
- Chỉ báo số đo thật. Không khóa holdout 2 năm; **mỗi cặp tối ưu riêng**, không mang tham số y nguyên sang cặp khác.

## 2. Quy trình rút gọn (vòng 3, từ 09/11)
Seeker → **Cổng 0** (phí XM, vài giây) → **Cổng S** (luật đọc được / EA chạy được trong tester) → **V1** → **V3** (V2 gộp vào V3).
- Cổng 0 loại khi: kỳ vọng ròng sau phí XM ≤ 0, hoặc edge/phí < 1,5, hoặc ước CAGR/DD trượt. Công cụ: `ban_giao/quy_trinh_v3/loc_phi_nhanh.py`.
- V1: walk-forward 12/3, tham số chỉ chọn trên train, phí XM, so với vào lệnh ngẫu nhiên.
- V3: WF 12/3, k chọn trên train. **Lượt A** 2009→2026-10; **Lượt B** 2024–2026 cần ≥ 99% tick thật. MT5 Model=4, nạp 10000, đòn bẩy 1:500, symbol hậu tố `#`. Tester để swap = 0 trên `#` → ước swap sau bằng `phi_xm_micro.json`.
- Chi tiết: `ban_giao/quy_trinh_v3/QUY_TRINH_VONG3_2026-11-09.md`, `V3_CSV_RUN.md`; code `nhan/v3_wf.py`, `may_nha/tho_mt5.py`, `mt5tools/an_toan_tester.py`.

## 3. Chạy MT5 trên máy nhà (DESKTOP-05PNLGF, PowerShell, dùng `;`)
- Repo máy nhà `E:\brain2_grok` (nhánh `fix/r1-cpu-seeker-moi-quantlab-gates`, nhiều file chưa commit) – **không đụng**: không checkout/stash/rebase/reset/đổi nhánh.
- Chạy job đơn trên slot portable `E:\brain2_grok\mt5_slots\g12`:
  `Start-Process E:\brain2_grok\mt5_slots\g12\terminal64.exe -ArgumentList '/portable','/config:<ini>'`
- CSV vào `%APPDATA%\MetaQuotes\Terminal\Common\Files`; .set vào `<slot>\MQL5\Profiles\Tester`.
- Không chạy hàng đợi `tho_mt5.py --song-song`.
- Slot g12 có thêm: `MQL5\Experts\v3\` (OnlyUJ_V3, BRAIN_XuLiLenh_V3Von), `MQL5\Scripts\v3\NapGBPCAD_HD.mq5`, symbol tự tạo `GBPCAD_HD` (HistData M1 2008–2026, thấy ở mọi slot qua `shared_bases`).
- `E:\seeker_tools` trên máy nhà là bản code CHƯA rà soát; bản chuẩn là `seeker_unblock/` trên git.

## 4. Quy tắc an toàn (giữ nguyên)
- Không đưa bí mật vào git/chat; không đọc `E:\api.txt`; mật khẩu nằm trong vault của Grok Bot, không có trong repo.
- taskkill chỉ theo PID chính xác; không bao giờ kill `claude.exe` hay terminal XM chính.
- Chỉ Free Demo; không gửi Telegram.
- Không commit: `config/ma_nguon_con_tro.json`, `config/ngan_sach_nhip.json`, `nhat_ky/kho_co_che_ghi.log`, `reports/EVO_SUC_KHOE.md`, `reports/VONG_DAY_DU.json`.
- File .htm/.pdf cần `git add -f`.

## 5. Seeker – nguồn và cơ chế vượt chặn
- Tổng quan 311 nguồn và top-30 nguồn nghẽn: `ban_giao/quy_trinh_v3/SEEKER_GO_NGHEN_VA_LOC_PHI.md`.
- **MQL5**: trang signal công khai đọc được (`seeker_unblock/mql5.py`). CSV `/en/signals/{ID}/export/history` cần đăng nhập trong trình duyệt. Từ 09/11 22:00 mql5.com trả 403 cho trình duyệt box. 60 ID đợt 2: `quy_trinh_v3/mql5_dot2_ids.txt` (chưa có lịch sử).
- **Myfxbook**: xuất CSV ở biểu đồ (icon sliders) → CSV → reCAPTCHA (subagent tự giải được, kể cả chọn ảnh) → Submit → email "CSV File request" từ support@myfxbook.com tới thebrainago@gmail.com, link `statements/{oid}/.../statement.csv` phải mở bằng trình duyệt (curl bị 403). Mở trang nhanh (>~25 trang) → Cloudflare 1015 vài giờ. Chỉ chạy 1 tiến trình, ≥ 3 s/request. Ứng viên đợt 2: `/workspace/myfxbook/dot2_ung_vien.txt` (555 6426348, 11787278, H traders oil 9900626, FX3 11992558).
- **FX Blue, Collective2, Darwinex** (box): `seeker_unblock/box/*` – lấy được lịch sử/chuỗi. ZuluTrade cần OAuth (401); Forex Factory chưa có id explorer công khai; SignalStart có tường đăng nhập.
- Nguyên tắc: tôn trọng chặn do trang đặt ra (`net.py` dừng ngay khi 403/429/1015).

## 6. Trạng thái hệ (10/11)
- **Đạt V3 có điều kiện**: **ghep60ff adxngang GBPCAD H1, lot CSV cố định** – A (HistData M1, không tick thật) CAGR 15,32%, DD 50,74%; B (99% tick thật) CAGR 58,96%, DD 75,11%. Bộ quản lý lệnh chọn trên 2024–2026; bản lot theo vốn cháy. `reports/v3/ghep60ff/mt5/`.
- **Trượt**: brainxlmrz (DD thật 92%), OnlyUJ 2245675 (MT5 B −1,14%, V1 Python +32% sai), các hệ CSV ghép (ghepe9b4, ghep_0bf2, 2600ea39, mql5344, skea61c, ghep60ff gốc), Kivenara, MCA100, Friday Pro, RC105, Tendency EURUSD, Myfxbook đợt 1 (NoPain, R Factor x2, MidasAlgo; Rainy qua Cổng 0 nhưng là lưới), FERRARI2009 IC (e/c 0,885).
- **Chưa kiểm định xong (KHÔNG coi là trượt)**: b0be91 USDCAD H4, skea154 GBPCAD H4, mql5e52 EURGBP H1 (đạt vòng 1/2 in-sample, chưa có V3); lô 17/10 (197 cấu hình MRZ/RSI, bộ 5 mảnh, BOBA US500); UV2 NZDCAD (chưa MT5 tick thật); EMA_Cross_Demo AUDCAD H1 (V1 chưa chạy); Bitcoin Adi (thiếu phí BTCUSD); Happy Gold OxS 12106293 (chưa có CSV); 3 hệ Myfxbook đợt 2 lấy từ History công khai (thiếu lot, 2 hệ chưa xác minh cột).
- Nhớ: 78 hệ "ĐẠT" ngày 21/10 bị vô hiệu do lỗi lot ~100× (31/10), không phải đã đo lại.

## 7. Việc tiếp theo đề xuất
1. Chạy V3 cho b0be91, skea154, mql5e52 (mỗi cặp tối ưu riêng).
2. ghep60ff: tìm tick thật GBPCAD 2009–2018 hoặc chọn lại bộ quản lý lệnh chỉ trên train rồi chạy lại.
3. Kiểm định lại lô 17/10 theo quy trình V3.
4. Myfxbook đợt 2 qua CSV export chính thức (có lot) khi hết ban; MQL5 đợt 2 khi hết 403.
5. EMA_Cross_Demo V1 AUDCAD.

## 8. Vị trí file
- Bản sao sổ làm việc vòng 3 (script + báo cáo + JSON kết quả, không có dữ liệu thô): `ban_giao/quy_trinh_v3/`.
- Báo cáo: `reports/vong3/`, `reports/v3/<hệ>/`.
- Công cụ Seeker: `seeker_unblock/` (README tiếng Việt, `test_offline.py`).
- Dữ liệu thô chỉ ở box (`/workspace/mql5_hist`, `/workspace/myfxbook`, `/workspace/nguon_khac`), không đưa lên git.
