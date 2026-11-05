> **05/11/2026 16:30 (UTC+7): BÀN GIAO — đọc TRI_NHO/BAN_GIAO_MAY_NHA.md trước.** Routine canh PAUSE; orch PID 17160 vẫn chạy.

# Trạng thái hiện tại — cập nhật 03/11/2026 19:40 (UTC+7)

## Tóm tắt
- Máy nhà DESKTOP-05PNLGF đang chạy hàng đợi git (`tho_mt5` / orch): can_test ~40 việc, vài slot dang_lam; WARP Connected; MT5 XM demo; chặn RAM ~11 GB trước mỗi lần phóng real tick.
- **MT5 nâng lot hôm nay (03/11): 8 hệ ĐẠT** (DD < 80% và CAGR > 10%/năm ở ít nhất một k), đã ghi `TRI_NHO/dac_diem_he/` + mục lục `DAC_DIEM_TOT.md`. Chi tiết ca: `nhat_ky/van_hanh_may_nha.md`.
- Cửa sổ CSV tín hiệu hầu hết ~2024–2026 → kết quả vẫn **in-sample**; bước tiếp theo tự nhiên: vòng 2 / ghép danh mục (`tai_lieu/VONG_2.md`), không dừng hàng đợi đang chạy.
- Grok Bot làm toàn bộ việc từ 02/11 (bot kia hết token). Routine canh máy nhà 30′ đang bật.

## MT5 ĐẠT 03/11/2026 (máy nhà, real ticks, nâng lot)
| Hệ | Mã · khung | k tốt | CAGR %/năm | DD % | PF · lệnh | Ghi chú |
|---|---|---|---|---|---|---|
| ghepe9b41c33d4deee54 | GBPNZD# H4 | 10 | 410,17 | 36,40 | 6,41 · 138 | k=1 đã 129,6%/31,5%; lãi 2024–2026 |
| ghep60ff9350c26c63ee | GBPCAD# H1 | 10 | 253,05 | 27,89 | 3,94 · 334 | k=1: 64,5%/20,2% |
| ghep0bf2c31fbfc9dea0 | GBPCAD# H4 | 8 | 220,26 | 59,61 | 9,45 · 86 | k=1: 65,1%/47,2%; 2026 âm nhẹ |
| 2600ea39abbd7b0f | GBPNZD# H1 | 3 | 83,44 | 22,64 | 3,18 · 132 | k≥4 cháy; k_an_toan_max=3 |
| b0be91a35f43f34a | USDCAD# H4 | 2 | 64,74 | 75,65 | — · 46 | sát trần DD; k≥2,5 vượt 80% |
| skea154c9fdee7 | GBPCAD# H4 | 1 | 41,37 | 48,38 | 3,28 · 179 | k>1 không báo cáo |
| mql5e52afb999eca4bd1 | EURGBP# H1 | 10 | 130,68 | 42,53 | 2,15 · 111 | k=1: 26,3%/19,2% |
| mql5344ed0d8ab12c7f0 | NZDUSD# H1 | 2 | 25,67 | 54,48 | 3,58 · 526 | chỉ ~31% real ticks; 2026 âm ở k≤2 |


## Làn lịch sử công khai (03/11/2026, `seeker/cong_khai/`)
- Quét mở rộng 03/11 05:41–06:2x (UTC+7, nền nohup, log `data/cong_khai/run.log`, cache 72h): 9 cách sắp × mt5/mt4 → **1600 id MQL5** (32 ứng viên cũ + 824 mới từ mt5, 744 từ mt4), **1562 đọc được**, 38 không đọc. Kết quả: **1065 ĐẠT / 1561 đo được = 68,2%** (496 KHÔNG ĐẠT, 1 chưa đo) theo chỉ DD<80% & CAGR>10%. 483 tín hiệu ĐẠT có tuổi ≥ 12 tháng (726/1562 tín hiệu ≥ 12 tháng). Sổ kết quả `nguon=CONG_KHAI` nay 1065 dòng (+773). Báo cáo: `reports/NGUON_CONG_KHAI_DAT.md`.
- Lần quét trước (00:2x–00:53): 292 đọc → 292 ĐẠT (chỉ danh sách mặc định, thiên lệch sống sót mạnh hơn).
- Lưu ý: danh sách mặc định MQL5 chỉ hiện tín hiệu xếp hạng cao → thiên lệch sống sót. Đây là ĐẠT theo **lịch sử công khai của người khác**, chưa phải hệ của mình đã chạy MT5 trên dữ liệu dài.
- Bị chặn: Myfxbook (Cloudflare 403, cả robots.txt), Exness Social Trading và my.litefinance.vn (lỗi TLS từ box), LiteFinance trang chi tiết trader chuyển hướng về danh sách (danh sách chỉ có lợi nhuận + rủi ro 1–10 → 16 trader CHƯA ĐO ĐƯỢC).
- Dịch ngược (03/11 07:15–08:00 UTC+7): 10 CSV tải tay đã đưa vào `data/cong_khai/csv/` và chạy `python -m nhan.dich_nguoc.top10` → `reports/DICH_NGUOC_TOP10.md`. Phong cách: 3 bẫy tin (1862128, 1864588, 2302081 — cùng nhà cung cấp), 2 martingale (2327790, 2378480), lưới/DCA hedge (2262642, 2271402, 2330430), 1932739 đa cặp có SL, 2391346 vàng giờ mở phiên Âu. AUC bỏ giờ đều ≤ ~0,63 trừ 2378480 (0,79).
- EA nháp: `ea_demo/BRAIN_DN_LuoiHedgeTP.mq5` (UV1 từ 2330430) và `ea_demo/BRAIN_DN_RoDCAHedge.mq5` (UV2 từ 2262642), CHƯA chạy Strategy Tester. MÔ PHỎNG Python AUDCAD H1 2008–2026 (không swap): UV1 lô 0,001/1000 USD CAGR 13,8% DD 60,0% (ĐẠT mô phỏng); UV2 không đạt. Việc dở: chạy MT5 real tick + swap XM cho 2 EA.
- Vòng 2 (03/11 ~08:30): thêm swap (XM/FXCE đo, 3 kịch bản) + margin 1:500 stop-out 20% vào `backtest_luoi.py`; dữ liệu HistData 2008–2023 tải thêm ở `/workspace/du_lieu_fx/hd_dai/`. Có swap: UV1 AUDCAD hết đạt (7,3%/65,9%). Đạt duy nhất với swap đo: **UV2 NZDCAD 2008–2023** lô 0,001/1000 USD CAGR 17,8% DD 33,8% (swap FXCE, không có 2024–2026, nghi chọn may mắn) → cần MT5 real tick. 5 EA vàng Telegram + CLMCA C_V1 trên XAUUSD 2009–2026: **0 đạt**. Báo cáo `reports/DICH_NGUOC_VONG2_SWAP_VANG.md`. Sổ: các dòng ĐẠT ở kịch bản `swap_0_lac_quan` chỉ là tham khảo, không tính.

## Hướng mới 03/11/2026 ~10:00 (UTC+7) — nguồn có lịch sử thật + máy nhà chạy hàng đợi git
- Lọc chặt MQL5 (`python -m seeker.cong_khai.loc_chat` → `reports/MQL5_LOC_CHAT.md`): **83/1578 đạt** (tuổi ≥ 24 tháng, thật, ≤ 3 mã, DD<80%, CAGR>10%, growth không cháy, lưới phải sống qua 03/2020 hoặc 2022). Lưu ý: growth_mau lấy mẫu ~2 tuần → sụt growth đo thấp hơn thực; nhận diện lưới chủ yếu theo từ khoá trang (chỉ 10 tín hiệu có CSV lệnh).
- Top 30 → EA trên Market (`python -m seeker.cong_khai.tim_ea_market`, `data/cong_khai/ea_market.json`): bảng ở cuối `reports/MQL5_LOC_CHAT.md`.
- Hàng đợi git `hang_doi/` (can_test → dang_lam_<máy> → da_test, sổ `hang_doi/so_cai.jsonl`), thư viện `may_nha/hang_doi_git.py`, thợ `may_nha/tho_mt5.py`, lệnh Anh: `may_nha\CHAY_THO_MT5.cmd`, hướng dẫn `may_nha/README_THO_MT5.md`, test `test_hang_doi_git.py`.
- Gieo 30 việc (`may_nha/seed_hang_doi.py`): 13 chạy lại nâng lot (k 1–10) hệ CSV, 4 EA dịch ngược 2016–2026 (k 0,5–5), 13 tải demo EA Market (cần Anh bấm Free Demo). Ước ~53,8 giờ MT5 (154 lần chạy). Kết quả MT5: CHƯA ĐO ĐƯỢC (chờ máy nhà).

- 03/11 ~10:30: lọc lại EA Market (chỉ EA giao dịch): 12/30 tác giả có EA, 10/30 có EA MT5 + demo → 33 việc demo. Làn A/B + cổng lịch sử vào hàng đợi; 4 việc EA dịch ngược bị loại (khớp 13,1 % / 8,11 %). Quét nguồn có file (`python -m seeker.nguon_file.quet`, `reports/NGUON_CO_FILE.md`, danh mục `seeker/nguon/nguon_file.json`): Code Base 198 EA đọc (99 làn A, 61 có input lot), GitHub 25 repo (11 tải được mã giấy phép tự do), TradingView 21 script chiến lược mã mở (làn B, chưa dịch), Forex Factory / forex-station: không đọc được chủ đề từ box. Hàng đợi 76 việc, ~75,4 giờ ước (220 lần chạy MT5). Chưa mô phỏng Python trước cho Code Base (20 EA đánh dấu dễ dịch).

## Đối chiếu phiên kia (03/11 ~09:30 UTC+7, `reports/DOI_CHIEU_PHIEN_KIA.md`)
- Đã gộp `evo/perf-quickwins`. Đã port vào main vá lot CSV (`mt5tools/sinh_viec.py`, `chay_lien_tuc.py`) và bảng pip theo mã (`nhan/dich_nguoc/phan_tich.py`). Không gộp `evo/sua-hash-va-hang-cho` (15 test hỏng do nhánh), không gộp nguyên `fix/r1` (sẽ đè `so_cai.jsonl`).
- Sổ: sửa lỗi đọc DD có dấu cách nghìn → 18 dòng MT5 lật sang ĐẠT (skst299b EURUSD, ghep_0bf2 GBPCAD, 3279 EURGBP, ghepe9b41 GBPNZD — đều IS/cửa sổ CSV). skea61c và brainxlmrz → `UNG_VIEN` theo kiểm toán. Nhập 384 dòng sổ cái 386 lần từ nhánh `fix/r1`.

## Lỗi lot CSV ~100× — đã vá 31/10/2026 01:53 (UTC+7)
- Khi EA chạy `VAO_CSV`, lot trong CSV bị phình ~100× → lãi/DD sai hoàn toàn.
- Hệ quả: **78 hệ “ĐẠT” trong `reports/CHIEN_LUOC_DA_LOC.md` BỊ THAY THẾ**, chờ chạy lại. Mọi kết quả trước mốc này trong sổ có trạng thái `BI_THAY_THE`.
- Bản vá và sổ cái sau vá (`so_cai_from_nha_1845.jsonl`, `status_overnight_0217.txt`) nằm ở máy nhà/box cũ; **không còn trên box hiện tại** và chưa có trong git. Số sau vá chỉ còn dạng chép lại trong `reports/kiem_toan_he_dat.md`.

## Kiểm toán 01/11 (`reports/kiem_toan_he_dat.md`)
5 hệ từng báo ĐẠT → **0/5 còn đạt**: brainxlmrz GBPUSD H4 (CAGR 13,3%, DD 78,81%, 25% tick), skea61c CADJPY H4 ×4 (13,3%, DD 10,74%, IS), sk_ea_3279057100 EURGBP H1 (12,2%, chưa giải mã điểm vào), mql5344 NZDUSD H1 (CAGR thật 3,5%), ghep_0bf2 GBPCAD H4 (10,3%, IS). Thứ tự chạy lại đề xuất: skea61c → brainxlmrz → ghep_0bf2 → 3279 → mql5344.

## Khác
- Hệ tín hiệu công khai: `reports/HE_TIN_HIEU_CONG_KHAI.md` — 10 nền tảng, 32 ứng viên MQL5 (26–27/10).
- Dữ liệu dài: MT5 XM xong 19 cặp từ 2004; histdata dừng 09/2026; Dukascopy CHƯA chạy; `du_lieu_dai.json` CHƯA có.
- 13 thẻ dịch tay (đợt 3–5, 21/10) mới qua lọc Python — MÔ PHỎNG, chưa đo MT5.
- Dịch LLM (qwen/ai-box) TẮT.

## Vấn đề đã biết
- CSV tín hiệu chỉ phủ 2024–2026 → kết quả trên CSV đó là **in-sample**; cần tái sinh tín hiệu trên toàn lịch sử.
- Bộ test đầy đủ (`pytest`) treo ở ~60% và có ~30 lỗi; chạy theo file với `--timeout`. Lỗi cũ: test_dich_llm (403), test_an_toan_tester ×2, test_ghi_an_toan ×3, test_sinh_viec.
- Repo phình: `reports/phan_viec/viec_mt5` và `reports/KHO_*.json` (đề xuất chuyển ra ngoài git — chờ Anh duyệt).
- Vài file config/report (`config/ma_nguon_con_tro.json`, `config/ngan_sach_nhip.json`, `nhat_ky/kho_co_che_ghi.log`, `reports/EVO_SUC_KHOE.md`, `reports/VONG_DAY_DU.json`) đang thay đổi trên box do tiến trình khác — không commit ở phiên 03/11.

- 04/11/2026: Anh lưu ý cặp chéo (GBPCAD, GBPNZD, EURGBP) cho lợi nhuận tốt hơn; ưu tiên thử cặp chéo. Vòng 2 chạy trước vòng 1.

- 04/11/2026: Mở **nhánh chỉ số** (theo xu hướng thiên mua US500/US30/US100/GER40): EA `ea_demo/BRAIN_ChiSo_Trend.mq5` (chưa biên dịch), 24 việc `hang_doi/can_test/cs_*.json` ưu tiên 60, tài liệu `tai_lieu/NHANH_CHI_SO.md`. Chờ máy nhà chạy.
