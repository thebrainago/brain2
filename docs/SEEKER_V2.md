# Seeker v2 — nghiên cứu rộng + sâu, MXH, dịch ngược

Cập nhật 03/11/2026. Mọi con số trong tài liệu này là đo thật; chỗ chưa đo ghi **CHƯA ĐO ĐƯỢC**.

## 0. Trước v2 đã có gì (kiểm kê)

- Kịch bản rời ở thư mục gốc: `seeker_v26.py` (tải mã mql5/GitHub từ danh sách máy nhà), `seeker_deep.py` (tìm qua Bing/Google/DDG đa ngôn ngữ + rút luật bằng regex), `seeker_cong_dong.py`, `seeker_theo_doi.py`, `seeker_kham_pha_sau.py`, `seeker_quet_nguon.py`, `nguon_kham_pha.py` (đoán username Telegram từ từ khóa, đọc t.me/s), `nguon_dien_dan.py`, `nguon_reddit.py`, `nguon_telegram.py`, `keywords_nguon.py` (ngân hàng từ khóa 13 ngôn ngữ, CỐ ĐỊNH), `tu_follow_join.py` (follow X qua CDP, trần 8/ngày).
- Trong `nhan/`: `nguon_seeker.py`, `kham_pha_nguon.py`, `kham_pha_sau.py`, `doc_seeker_da_nguon.py`, `tu_khoa_da_ngon_ngu.py`, `hop_dong.py` (hợp đồng `DocumentArtifact`/`TradeHistoryArtifact`/`CandidateArtifact`), `bien_dich_ung_vien.py`, `_luan_nguoc.py` (phân kiểu trader từ hồ sơ signal đã lưu), `suy_nguoc.py` (dấu hiệu trước cú chạy giá — khác với dịch ngược lệnh).
- Thiếu: từ khóa không tự mở rộng; không có hàng đợi ưu tiên/ngân sách/chạy tiếp; không tôn trọng robots.txt có hệ thống; không có bộ thao tác MXH có trần + chạy thử; không có module suy ngược phương pháp từ lịch sử lệnh.

v2 KHÔNG xóa các file cũ; các kịch bản cũ vẫn chạy như trước.

## A. Động cơ nghiên cứu (`seeker/`)

| Tệp | Vai trò |
|---|---|
| `seeker/nguon/web.yaml` | Sổ nguồn: diễn đàn, site, repo, kênh theo ngôn ngữ (en, zh, ru, ja, vi, es, pt, id, ar) + cách truy cập (`html`/`rss`/`api`/`trinh_duyet`/`can_dang_nhap`) |
| `seeker/nguon/telegram.yaml` | Danh sách kênh Telegram Anh duyệt + giới hạn (trang/kênh, đuôi tệp) |
| `seeker/tu_khoa_hat_giong.yaml` | Khái niệm hạt giống (grid, DCA, martingale, hedge, mean reversion, session breakout, scalping, trend) dịch 9 ngôn ngữ |
| `seeker/do_thi.py` | Đồ thị khái niệm: TF-IDF + đồng xuất hiện với khái niệm đã biết → điểm mới → thăng cấp thành từ khóa tìm kiếm |
| `seeker/thu_thap.py` | Tải lịch sự: robots.txt, giãn cách theo miền, cache 6 giờ, gặp 403/429/captcha → ghi log, bỏ qua |
| `seeker/telegram.py` | Đọc `t.me/s/<kênh>` (không đăng nhập): tin, tên tệp đính kèm, khám phá kênh từ chuyển tiếp / @nhắc / link t.me |
| `seeker/y_tuong.py` | Bản ghi ý tưởng chuẩn: nguồn, ngôn ngữ, url, ngày, phương pháp, tham số, bằng chứng, độ tin cậy |
| `seeker/dong_co.py` | Hàng đợi ưu tiên, ngân sách, giới hạn độ sâu, khử trùng, lưu/chạy tiếp, digest |

Chạy:
```
python -m seeker.dong_co --ngan-sach 60 --sau 1 --nguon mql5_forum_ru,github_search
python -m seeker.dong_co --chi-telegram --ngan-sach 40
```
Trạng thái (gitignored): `data/seeker_state/` — `trang_thai.json`, `y_tuong.jsonl`, `nhat_ky.jsonl`, `telegram_frontier.json`, `telegram_tep.jsonl`, `cache/`. Commit: `reports/seeker_v2/DIGEST.md`, `THONG_KE.json`.

### Lượt chạy thật đầu tiên (03/11/2026 00:09 giờ VN)
8 nguồn web + kênh mẫu Telegram `tradingview`, ngân sách 60, độ sâu 1: **35 yêu cầu** (hàng đợi cạn trước ngân sách), 26 tải mới, **4 bị robots.txt cấm** (Reddit — robots của Reddit chặn mọi bot), **3 bị chặn** (note.com API, HTTP 403), 2 lỗi HTTP 404 (URL smart-lab và elitetrader trong sổ nguồn đã sai — cần sửa); **59 tin Telegram**; **18 ý tưởng**; **21 cụm từ khóa tự thăng cấp**; **6 kênh Telegram mới** trong biên. Chi tiết: `reports/seeker_v2/DIGEST.md`.

Hạn chế đo được: cụm tự thăng cấp còn nhiễu (vd. lấy cả tên repo GitHub); rút tham số bằng regex bắt nhầm số (vd. `lot: 0`). Ba kênh Anh đưa (VŨ TRỤ EAFOREX, Software & Indicator, Nhật Hoài Trader Channel) **chưa có @username** → chưa đọc được qua t.me/s; đọc qua Telegram Web (mục B).

## B. Bộ thao tác mạng xã hội (`seeker/mxh/`)

- Trình duyệt **riêng**, hồ sơ cố định ngoài git (`thu_muc_ho_so` trong `seeker/mxh/cau_hinh.yaml`, mặc định `%USERPROFILE%/brain_trinh_duyet_mxh`).
- Bộ chuyển đổi: `facebook` (tìm nhóm, đọc bài, nhóm liên quan, xin vào nhóm), `telegram` (Telegram Web: đọc kênh/nhóm, tải tệp ex4/ex5/mq4/mq5/set/pdf/zip vào `data/mxh_tai_ve/`, khám phá kênh, tham gia kênh), `x` (tìm, đọc, theo dõi), `reddit` (tìm subreddit, đọc, join), `discord` (chỉ đọc server Anh đã vào).
- **An toàn cứng** (`seeker/mxh/an_toan.py`, có test):
  - `chay_thu: true` mặc định — không bấm follow/join, chỉ ghi "sẽ bấm". Bật thật bằng `--that`.
  - Trần/ngày/nền tảng: theo dõi 10, xin vào nhóm 10, trang đọc 300, tải tệp 50.
  - Nhịp kiểu người: 4–11 giây giữa thao tác, 45–120 giây sau follow/join.
  - Cấm tuyệt đối (ném lỗi kể cả khi sửa cấu hình): đăng bài, bình luận, nhắn tin, trả lời, thích, chia sẻ, nhập mật khẩu.
  - Gặp captcha / checkpoint / "unusual activity" / FloodWait → **dừng cả phiên**, ghi log, không vượt.
  - Telegram: **chỉ đọc kênh/nhóm** (kiểm tiêu đề có "subscribers/members"); chat 1-1 với người quen → bỏ qua và ghi log `bo_qua_chat_ca_nhan`. Nhóm Facebook có câu hỏi khi xin vào → không tự trả lời.
- Bộ chọn (selector) Facebook/Telegram Web/X **CHƯA ĐO ĐƯỢC** trên trang thật (box không có Playwright gắn vào trình duyệt đã đăng nhập). Lần chạy đầu trên máy nhà nên dùng chế độ chạy thử và gửi lại log.

### Cách chạy trên máy nhà (Windows)
1. Mở PowerShell trong thư mục repo: `git pull` rồi `pip install -r requirements.txt playwright` và `python -m playwright install chromium` (nếu dùng Chrome đã cài thì không cần dòng này).
2. (Tùy chọn) sao chép `seeker\mxh\cau_hinh.yaml` thành `seeker\mxh\cau_hinh_rieng.yaml` để đổi thư mục hồ sơ / trần.
3. Đăng nhập một lần: `python -m seeker.mxh.chay --dang-nhap` → trình duyệt riêng mở các tab Telegram Web, Facebook, X, Reddit, Discord; **Anh tự đăng nhập** (quét QR / OTP do Anh nhập), xong bấm Enter. Tool không đọc, không lưu mật khẩu.
4. Đọc Telegram theo danh sách: `python -m seeker.mxh.chay --nen-tang telegram --kenh-tu-file`
5. Tìm nhóm Facebook theo đồ thị từ khóa (chạy thử): `python -m seeker.mxh.chay --nen-tang facebook --tim 5 --ngon-ngu vi`
6. Khi xem log thấy ổn: thêm `--that` để follow/join thật (vẫn theo trần ngày).
7. Log: `data\seeker_state\mxh\gioi_han.log.jsonl`; ý tưởng vào chung `data\seeker_state\y_tuong.jsonl`.

## C. Dịch ngược phương pháp (`nhan/dich_nguoc/`)

Đầu vào: MT4 statement HTML, MT5 report HTML, MQL5 signal CSV (`;`), Myfxbook CSV, CSV chung + giá OHLC (CSV `time,open,high,low,close`).
```
python -m nhan.dich_nguoc --lich-su statement.htm --gia gia_EURUSD_H1.csv --ten tk123 --url https://...
```
Đầu ra: symbol, phân bố giờ/thứ, thời gian giữ, kiểu lot (cố định / martingale + hệ số / DCA), bước lưới (pip và bội ATR), hedge, TP/SL; đặc trưng bối cảnh lúc vào (RSI14, ATR, khoảng cách MA50/ATR, z Bollinger 20, phá vỡ phiên Á, giờ, thứ, đà 5 nến) so với thời điểm ngẫu nhiên → AUC kiểm chéo 5 lần của cây quyết định độ sâu 3 + logistic, luật cây dạng văn bản; thẻ ứng viên theo hợp đồng `nhan/hop_dong.py` (`TradeHistoryArtifact` → `CandidateArtifact`, `candidate_kind=method`) ghi vào `data/dich_nguoc/`.

Kiểm thử (`test_dich_nguoc.py`): sinh lệnh từ luật biết trước (giờ 7–10, RSI<30 → BUY, DCA 20 pip, lot ×1.5, TP trung bình +15 pip) → module khôi phục: kiểu martingale, hệ số 1.5 (±0.05), bước 20 pip (±0.5), AUC cây > 0.8, RSI lúc vào < 30. Đối chứng ngẫu nhiên: AUC logistic < 0.62.
Chưa chạy trên lịch sử thật của trader nào: **CHƯA ĐO ĐƯỢC**.

## D. Làn lịch sử công khai (`seeker/cong_khai/`) — 03/11/2026

Song song với Seeker v2: thu tín hiệu có **lịch sử xác minh công khai** rồi chấm theo đúng tiêu chí duy nhất.
```
python3 -m seeker.cong_khai.chay --trang 3 --gian-cach 3
```
| Tệp | Vai trò |
|---|---|
| `mql5.py` | đọc `mql5.com/en/signals/<id>` và danh sách `/en/signals/mt5/list`, `/mt4/list` (robots.txt cho phép; trang `deals/page*` bị cấm nên không đọc) |
| `myfxbook.py` | đọc `myfxbook.com/systems` + `members/...` — đo 03/11: Cloudflare 403 → BỊ CHẶN, không vượt |
| `nen_tang_khac.py` | LiteFinance (danh sách công khai, không có DD/tuổi → CHƯA ĐO ĐƯỢC), Exness Social Trading (lỗi TLS từ box) |
| `cham_diem.py` | `cagr_tu_tang_truong`, `dat()` = DD<80 & CAGR>10 (chỉ hai tiêu chí), `diem_xep_hang()` CHỈ để sắp thứ tự |
| `chay.py` | quét → `data/cong_khai/tin_hieu.jsonl`, `reports/NGUON_CONG_KHAI_DAT.md`, `reports/cong_khai/THONG_KE.json`, ghi sổ `nguon=CONG_KHAI`, đưa CSV có sẵn vào `nhan.dich_nguoc` |

Lượt đầu 03/11 (đo thật): MQL5 292 tín hiệu → 292 ĐẠT (mẫu thiên lệch sống sót vì danh sách mặc định chỉ hiện tín hiệu xếp hạng cao); LiteFinance 16 trader CHƯA ĐO ĐƯỢC; Myfxbook, Exness: bị chặn. CSV lịch sử MQL5 cần đăng nhập → dịch ngược: CHƯA ĐO ĐƯỢC.

## E. Bộ lọc chất lượng nguồn (`seeker/chat_luong_nguon.py`)
Bậc `co_lich_su` (EA/chiến lược + lịch sử kiểm chứng: MQL5 Signals/Code Base, GitHub, Myfxbook) ×1.3 ưu tiên; `chien_luoc` ×1.0; `thao_luan` ×0.5 và bị bỏ khi chạy `--chi-chat-luong`. Ghi đè bằng khóa `chat_luong` trong `web.yaml`. Đây là bộ lọc nguồn, không phải tiêu chí ĐẠT.
Lượt chạy lại 03/11 00:2x (UTC+7): `python3 -m seeker.dong_co --ngan-sach 80 --sau 1 --chi-chat-luong` → 45 yêu cầu, 44 ý tưởng mới (tổng 62), bỏ 11 nguồn thảo luận, elitetrader đọc được sau khi sửa URL; Reddit vẫn bị robots.txt cấm, note.com 403.
