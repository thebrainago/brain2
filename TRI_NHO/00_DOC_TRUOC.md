# ĐỌC TRƯỚC — cửa vào duy nhất cho mọi phiên mới

> Mọi phiên chat mới (Grok Bot, Claude, bot khác) đọc file này **đầu tiên**, rồi `TRANG_THAI.md`, rồi 20 dòng cuối `NHAT_KY_PHIEN.md` và `QUYET_DINH.md`. Không cần Anh dạy lại. Tài liệu cũ ở gốc repo (START_HERE.md, BAN_GIAO_*.md, CLAUDE.md…) chỉ là lịch sử; nếu mâu thuẫn với thư mục `TRI_NHO/` thì **`TRI_NHO/` thắng**.

## 1. Mục tiêu dự án
Tìm hệ thống giao dịch chạy được cho **tài khoản XM Micro** của Anh. Phong cách Anh thích: **không SL cứng, TP nhỏ, DCA, hedge, gỡ lệnh (recovery), ghép nhiều hệ** thành một hệ tổ hợp.

## 2. TIÊU CHÍ ĐẠT — DUY NHẤT
**Max DD < 80% VÀ lợi nhuận > 20%/năm tính theo CAGR (lãi kép).**
Không có tiêu chí nào khác (FDR, placebo, Holm, p-value, PF, số lệnh… chỉ là nhãn tham khảo, không bao giờ là cổng). Các tài liệu cũ ghi “≥10%/năm” hay “≤80%” đã bị thay bằng tiêu chí này (xem `QUYET_DINH.md`).

## 3. Luật cố định
- Chỉ báo **số đo được**; không đo được ghi **CHƯA ĐO ĐƯỢC**. Mô phỏng (Python, Monte Carlo, stress) ghi rõ **MÔ PHỎNG**. Không bịa số.
- Không commit khóa/token/mật khẩu; không in secret; không đọc `E:\api.txt`.
- Mã nguồn của người khác chỉ để trong `data/` (đã gitignore).
- `taskkill` chỉ theo **đúng PID**. Không bao giờ kill `claude.exe` hay `C:\Program Files\XM Global MT5\terminal64.exe`.
- Không đụng Riot Games (ổ D). Không tắt máy nhà.
- Không vượt chặn chống bot (captcha, 429 → lùi lại, không lách).
- Dịch bằng LLM trả phí: **TẮT** trừ khi Anh bảo bật.
- Phần cứng không đổi được — tối ưu trong giới hạn hiện có.
- Bắt buộc dữ liệu **dài nhiều năm**; kết quả chỉ trong cửa sổ CSV tín hiệu ngắn = in-sample, không đủ.
- Git: `git pull --no-rebase`; không rebase, không force push, không autostash.

## 4. Bản đồ repo
| Phần | Ở đâu | Ghi chú |
|---|---|---|
| Đường ống chính | `nhan/` | thư viện lõi: dịch EA (`dich_mq5*.py`, `dich_llm.py`), engine tài khoản (`tai_khoan.py`), vòng 2 (`vong2.py`), chi phí (`chi_phi.py`)… |
| Xưởng tổ hợp | `nhan/xuong*.py` (`xuong.py`, `xuong_may.py`, `xuong_toi_uu.py`, `xuong_tach.py`, `xuong_toan_tu.py`, `xuong_danh_muc.py`, `xuong_tin_hieu.py`) | kéo lot theo DD, tối ưu, phân rã cơ chế, toán tử ghép, danh mục |
| Seeker | `tru/seeker.py`, `seeker_*.py`, `nhan/doc_seeker_da_nguon.py`, `nguon_*.py` | tìm nguồn EA/chiến lược đa nguồn |
| QuantLab / MT5 | `tru/quantlab.py`, `mt5tools/` (`chay_lien_tuc.py`, `quan_ly_slot.py`, `sinh_viec.py`), EA `ea_demo/BRAIN_XuLiLenh.mq5` | chạy Strategy Tester real tick trên máy nhà |
| Dữ liệu dài | `nhan/du_lieu_dai.py`, `mt5tools/TAI_LICH_SU_MT5.bat`, `tai_dukascopy_*.py`, `gop_histdata_*.py` | chuỗi MT5 XM → histdata → Dukascopy → gộp `data/du_lieu_dai/du_lieu_dai.json` |
| EVOLUTION | `tru/evolution.py`, `docs/ban-giao/EVOLUTION_ban_giao.md` | giám sát sức khỏe dây chuyền |
| Sổ kết quả | `TRI_NHO/so_ket_qua/ket_qua.csv`, `nhan/so_ket_qua.py` | MỌI kết quả test của mọi phiên |
| Báo cáo | `reports/` | `kiem_toan_he_dat.md`, `HE_TIN_HIEU_CONG_KHAI.md`, `CHIEN_LUOC_DA_LOC.md` (BỊ THAY THẾ) |

## 5. Chạy trên máy nhà (DESKTOP-05PNLGF, Windows)
- Repo: `C:\Users\DUNG\brain2` (cây Grok riêng: `E:\brain2_grok`, venv `E:\brain2_grok\venv`).
- Tải dữ liệu dài: `mt5tools\TAI_LICH_SU_MT5.bat` (phần đã tải tự bỏ qua) → `python -m nhan.du_lieu_dai --dung`.
- Vòng 2 dữ liệu dài: `set BRAIN_ONG_DAN_DU_LIEU=data\du_lieu_dai\du_lieu_dai.json && python -m nhan.vong2 --top 40`.
- Bộ chạy job MT5: `python mt5tools\chay_lien_tuc.py` với env `BRAIN_RAM_DONG=1 BRAIN_TICK_CHUNG=1 BRAIN_CONG_MOI=1 BRAIN_GEN=1 BRAIN_VONG2=1`; tối đa **3 slot** (g1–g3); CPU mục tiêu 70–80%.
- Sau mỗi lần chạy: ghi kết quả vào sổ bằng `from nhan.so_ket_qua import ghi_ket_qua`.
- Box: `/workspace/brain2`, Python `/workspace/venv/bin/python` (hoặc `python3`).

## 6. Ưu tiên hiện tại (02/11/2026)
1. **Seeker**: chạy rộng và sâu, đa ngôn ngữ, đa diễn đàn; tự tìm nguồn mới, tự sinh từ khóa/khái niệm để lần sâu; công cụ tự thao tác mạng xã hội trên trình duyệt riêng Anh cấp (follow, tìm bài, vào group, tìm thêm group); sau đó cơ chế **dịch ngược phương pháp vào lệnh** từ lịch sử trade người khác.
2. **QuantLab**: tăng tốc + tăng số bài test, tối ưu quản lý.
3. **Chạy lại** các hệ cũ sau vá lỗi lot (31/10) trên dữ liệu dài, OOS thật; ghi vào sổ kết quả.

## 7. Quy trình kết thúc phiên (bắt buộc)
- [ ] Cập nhật `TRI_NHO/TRANG_THAI.md` (đang chạy gì, PID nếu có, việc dở).
- [ ] Thêm một mục vào cuối `TRI_NHO/NHAT_KY_PHIEN.md` (ngày giờ UTC+7, bot, việc đã làm, commit).
- [ ] Ghi mọi kết quả test mới vào sổ: `ghi_ket_qua(...)` hoặc `python -m nhan.so_ket_qua --thu-hoach`; rồi `python -m nhan.so_ket_qua --tong-hop`.
- [ ] Quyết định mới của Anh → `TRI_NHO/QUYET_DINH.md`.
- [ ] `git pull --no-rebase` → commit (không secret) → `git push origin main`.
