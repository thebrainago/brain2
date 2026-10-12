# SEEKER — nguồn theo phong cách giao dịch (port từ the-brain, 12/10/2026)

## Nguồn ở đâu
- Sổ đăng ký: `config/nguon_seeker.json` (222 nguồn), sinh lại bằng `python _kiem_ke_nguon_the_brain.py --repo /workspace/the-brain`
  (đọc git của the-brain, nhánh `claude/autonomous-trading-system-rzzt7h`, bàn giao `3c982747`; the-brain chỉ đọc).
- Gốc trong the-brain: `tru/seeker.NGUON` (14) + `NGUON_TRINH_DUYET` (23) + `nhan/nguon_bai_viet` FEEDS (27) + TRANG (7)
  = 71 nguồn đăng ký (`tai_lieu/KIEM_KE_NGUON.md`); + `nguon_dien_dan.py` (6), `_do_dien_dan_quoc_gia.py` (18), `config/dien_dan.json` (23),
  `config/nguon_ung_vien.json` (26: 22 Telegram), `config/nguon_tu_tim.json` (28 blog tự sinh), `config/nguon_cho_ea.json` (26),
  `web_registry.json` (10 cổng API cá nhân), bảng nền tảng `NGUON.md` (45 tên, chưa có URL). Trùng mã được gộp.
- Bổ sung: TradingView public strategies (`tradingview_strategies`), hàng chờ dịch 15 script: `config/hang_cho_tradingview.json`.

## Bốn chiều nhãn (luật từ khoá chốt trước, `nhan/nguon_seeker.gan_nhan`)
- `phong_cach`: xu_huong · hoi_quy · pha_vo · luoi_dca · luot_song · vi_mo_carry · hoc_may · danh_muc_factor · tin_hieu_copy · tong_hop
- `tai_san`: fx · crypto · co_phieu · futures_hang_hoa · chi_so · da_tai_san
- `khung`: ngan_M1_M15 · trung_H1_H4 · dai_D1_W1 · nhieu_khung
- `quan_tri`: luoi_martingale · trailing_ATR · rui_ro_co_dinh · danh_muc · copy_theo_doi · khong_ro
- Nguồn mã (GitHub) có truy vấn riêng theo phong cách: `TRUY_VAN_THEO_PHONG_CACH` → `seeker_tai_ma_theo_phong_cach.py`.

## Quy tắc cũ đã port (chỉ phần ĐỌC)
- Tự sinh nguồn: trang đọc được khai `<link rel=alternate type=rss/atom>` → ứng viên feed mới; link ra ngoài → ứng viên.
- Mở rộng qua mạng xã hội: chỉ GHI ứng viên (t.me, reddit, youtube, github) thấy trong trang công khai. Không follow, không join,
  không đăng nhập, không đăng bài. (Bản the-brain `tu_follow_join.py`/`tu_dang_ky.py` KHÔNG được gọi.)
- Chu kỳ quét: `chu_ky_gio` mỗi nguồn (mặc định 168 giờ), trạng thái `data/nguon_seeker/TRANG_THAI.json`.
- Phân trang: `nhan/doc_nhieu_trang.py` (con trỏ từng danh sách) cho diễn đàn có `mau_trang`, hàm lấy tôn trọng robots.txt.
- Luật cứng: robots.txt, ≥ 4 giây/yêu cầu/tên miền, 403/429/503/Cloudflare/captcha → dừng tên miền, ghi `BỊ CHẶN — cần chạy máy nhà`.

## Chạy
    python seeker_quet_nguon.py --ep --trang-sau 600     # quét mọi nguồn + phân trang 600 giây
    python seeker_tai_ma_theo_phong_cach.py               # GitHub EA theo phong cách (token chỉ ở env GITHUB_TOKEN)
    BRAIN_DIEU_TOC=tat python -m tru.cau_kho --khong-tai  # bộ đọc trên kho
Kết quả: `reports/SEEKER_QUET_NGUON.{md,json}`, `reports/SEEKER_TAI_MA_PHONG_CACH.json`. Mã EA của người khác nằm ở `data/` (gitignore).

## Máy nhà (tùy chọn, TẮT mặc định) — `nhan/may_nha_tuy_chon.py`
WARP (`warp-cli`), mô phỏng người (`simulator_nguoi.py`), DNS-over-HTTPS (`nhan/dns_vuot.py`) chỉ chạy khi `BRAIN_MAY_NHA=1` **và** Windows.
Trên máy nhà, chủ dự án tự quyết định và tự chịu trách nhiệm điều khoản từng trang:
1. `git pull`; `pip install -r requirements.txt` (+ `playwright install chromium` nếu dùng trình duyệt).
2. `python seeker_quet_nguon.py --ep` từ mạng nhà (IP dân dụng) — nhiều trang chặn IP trung tâm dữ liệu nhưng mở cho IP nhà.
3. Nguồn còn `BỊ CHẶN`: mở bằng Chrome thật của mình (CDP 9224, hồ sơ `.browser_thebrain`), `set BRAIN_CDP_CHO_PHEP=1`, `python -m tru.seeker`.
4. Nguồn `CẦN ĐĂNG NHẬP` (MQL5 lịch sử lệnh, Myfxbook, Darwinex, ZuluTrade, Collective2, X/TikTok/Facebook): tự đăng nhập một lần trong trình duyệt đó;
   khoá API chỉ để ở biến môi trường / `config/api_keys.json` (gitignore), không bao giờ commit.
5. Chỉ khi muốn: `set BRAIN_MAY_NHA=1` rồi dùng WARP cho Myfxbook (lưu ý the-brain đo: WARP có thể huỷ phiên MQL5, mql5.com chặn dải IP WARP).
