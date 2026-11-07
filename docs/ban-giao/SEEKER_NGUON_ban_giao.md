# Bàn giao nguồn SEEKER — 2026-11-07

Đăng nhập và trạng thái tài khoản nguồn (không có bí mật): [SEEKER_DANG_NHAP_ban_giao.md](./SEEKER_DANG_NHAP_ban_giao.md). Mốc 2026-11-07 15:16 Asia/Bangkok.

## Đợt 2 — sáu nguồn chưa đo (2026-11-07) — dừng, không thu thập

`reports/seeker_nguon/DIEN_DAN_DOT2.json`. Phạm vi theo miền, không đếm trùng: `reports/seeker_nguon/PHAM_VI_DIEN_DAN.json`. Không việc mới. 311 nguồn chưa được giải.

- SignalStart `/search-signals`: HTTP 200, 20 hồ sơ `/analysis/<tên>/<id>`. Danh sách đọc được. Chưa mở hồ sơ.
- GogoJungle `/systemtrade/fx`: HTTP 200. Đếm thô 67 gồm URL search. Parser sửa còn 44 hồ sơ `/systemtrade/fx/<số>`, đọc lại HTML đã lưu. Chưa mở hệ.
- FX-on `fx-on.com` chuyển về trang chủ GogoJungle. Cùng một sàn, không tính nguồn thứ hai. JSON `detailUrl` không bóc.
- DupliTrade: HTTP 200, Next.js, không có URL nhà cung cấp.
- FX Blue sổ `/users`: HTTP 404. robots cấm `/user/`. Sitemap 2.641 URL; phần users chỉ là `/users/example`.
- FXStat `www`: chứng chỉ không khớp (SAN chỉ `fxstat.com`). `https://fxstat.com/` TLS bình thường là trang đăng nhập. Không tắt kiểm chứng chỉ.
- eToro: URL sổ là `/sapi/`. Không gọi.

40 miền diễn đàn/xếp hạng trong sổ: 2 có danh sách lẫn thân bài (TraderViet, diễn đàn MQL5), 2 chỉ có danh sách (SignalStart, GogoJungle), 3 cần trình duyệt, 4 host đã chặn, 20 diễn đàn chung chưa đo và không phải bảng lịch sử tài khoản. Dừng, không mở vòng mới.

## Thân bài và URL xếp hạng có tài liệu (2026-11-07) — vẫn chưa thu thập

`reports/seeker_nguon/DIEN_DAN_THAN.json`. Không việc mới.

- TraderViet một bài `...72248`: HTTP 200, parser XenForo thấy 2 thân bài (1.541 ký tự) và ngày. Bài là giới thiệu sách, không có số lãi.
- MQL5 ` /ru/forum/519621`: HTTP 200, 10 bình luận (3.232 ký tự) sau khi sửa regex `class="content"` bị xuống dòng. Bài thảo luận xu hướng, không phải hệ đã kiểm lãi.
- ZuluTrade `/traders` (trang danh sách công khai, robots cho phép): HTTP 200, không có hồ sơ leader trong HTML.
- Darwinex: `/data/darwin-api` vẫn là login. Help DarwinIA trỏ https://www.darwinexzero.com/darwinia/gold . Trang đó HTTP 200 nhưng không có hàng DARWIN trong HTML. Không bịa URL `/all-darwins`.
- cTrader: help nói danh sách ở tab Strategies trong app. `ctrader.com/copy` không có id chiến lược. Không gọi lại.
- EliteTrader `automated-trading.48`: robots cho phép, trang HTTP 403 Cloudflare. Dừng, không thử lại.

## Chẩn đoán 6 diễn đàn / bảng xếp hạng (2026-11-07) — chưa thu thập

Không tạo việc mới. HTTP 200 không có nghĩa parser ra hồ sơ. Báo cáo `reports/seeker_nguon/DIEN_DAN_NC.json`. Lệnh: `python -m seeker.dien_dan_nghien_cuu` (dùng cache; không đào bài).

| Nguồn | URL đã thử | Truy cập | Parser | Việc tiếp |
|---|---|---|---|---|
| TraderViet | https://traderviet.tv/forums/he-thong-giao-dich-trading-system.11/ | ok HTTP 200 | ra URL bài trên danh sách, chưa mở bài, chưa có số lãi | đợt sau mới đọc từng bài |
| MQL5 forum ru | https://www.mql5.com/ru/forum | ok HTTP 200 sau khi sửa: robots.txt có `Disallow: /captcha/` bị gán nhầm là challenge | ra URL bài, chưa mở bài | không đào trong đợt này |
| BabyPips | https://forums.babypips.com/ | challenge, robots.txt HTTP 403 Just a moment | không chạy | dừng, không đổi UA. Chủ mở trình duyệt nếu cần |
| Darwinex | https://www.darwinex.com/data/darwin-api | auth, chuyển tới /login | không chạy | cần phiên chủ đã có. Không tạo tài khoản hộ |
| ZuluTrade | https://www.zulutrade.com/ | ok HTTP 200 | không ra URL hồ sơ trader trong HTML tĩnh | lịch sử lệnh theo ghi chú sổ nguồn cần đăng nhập. Không có API công khai nào được gọi |
| cTrader Copy | https://ctrader.com/copy | ok HTTP 200 | không ra id chiến lược; link là mục /copy/brokers, /symbols, ngôn ngữ | trang vẽ danh sách bằng JS. Không dùng API ẩn |

Myfxbook, ForexFactory, forex-station, Exness không gọi lại.

## Myfxbook — dừng host, đường chính thức là API tài khoản của mình

Không gọi lại `www.myfxbook.com`. Bản 2026-11-03: `/systems` HTTP 403 Cloudflare, cả robots.txt. `seeker.cong_khai.chay` bỏ qua host này (`khong_goi: true`).

Tài liệu chính thức (một lần đọc https://www.myfxbook.com/api ):

- API “access your account's data”; câu chữ: **“The API allows access to personal information only.”**
- `login` tạo session (gắn IP, hết hạn khoảng 1 tháng). Mã này không đăng nhập và không lưu mật khẩu.
- `get-my-accounts`: số tổng (gain, drawdown, demo…) của **tài khoản mình**. Không có danh sách lệnh.
- `get-watched-accounts`: tóm tắt tài khoản đang theo dõi (mẫu tài liệu: tên, gain, drawdown, demo, change). **Không có lịch sử lệnh.**
- `get-history`: tối đa **50** giao dịch gần nhất, cần `session` và `id`. Tài liệu không nói id này là hệ công khai của người khác. Không kết luận API mở lịch sử bên thứ ba.
- `get-community-outlook`: tâm lý cộng đồng, không phải bảng xếp hạng.
- Trang tài liệu **không** có phương thức leaderboard `/systems` hay CSV lịch sử trader khác.

Số gain/DD nhập từ JSON là **khai báo**, `dat: false`. Việc ghi vào `hang_doi/nghien_cuu/` (`loai=nghien_cuu_track_record`), không vào `can_test`, nên thợ MT5 không chạy. Chưa giải mã cách vào.

Việc của chủ, trên trình duyệt của chủ (không tạo tài khoản hộ, không vượt captcha):

1. Đăng nhập Myfxbook nếu muốn số của chính tài khoản mình.
2. Gọi API theo trang tài liệu, lưu JSON ra đĩa (không gửi mật khẩu vào git).
3. `python -m seeker.cong_khai.myfxbook_api --nhap tep.json`
4. `python -m seeker.cong_khai.myfxbook_api --trang-thai` in `ket_noi: false`.

## Việc lấy EA gốc vào hàng đợi (cùng ngày, sau chẩn đoán)

`data/cau_kho` **không có** trên máy cloud này. Các số 308/39/493/846 là giả thuyết từ máy khác, chưa kiểm ở đây, không ghi thành số đo.

Cổng cũ: `nhan/cau_kho_ma.xuat` chỉ xuất EA đã dịch thành cơ chế Python. Worker chỉ tải một `.mq5`. Làn mới `python -m seeker.nap_ea_goc` không đòi dịch Python. Heuristic OnTick + lời gọi lệnh **không phải chứng minh**. Include ngoài thư viện chuẩn bị từ chối vì worker không kéo file kèm. `bien_dich` luôn `CHUA_BIEN_DICH` khi không có MetaEditor. Trần 5 việc, hệ số lot chỉ `1.0`, demo, không chạy tester.

Đã xếp 2 việc (kiểm `kiem_spec` rỗng), mã nguồn nằm trong `data/` (gitignore):

| id | URL tải | sha256 | Kết quả |
|---|---|---|---|
| `na_2d4605e4e9a6` | https://raw.githubusercontent.com/EarnForex/News-Trader/main/NewsTrader.mq5 | `2d4605e4e9a6fd6a0583e3f9516ecbebcde83e53747606cea6e6e3aff604c756` | nhận. Apache-2.0, một file, include chuẩn. Chưa biên dịch |
| `na_1233d657c07b` | https://www.mql5.com/en/code/download/77653/EMA_Cross_Demo_EA.mq5 | `1233d657c07b9930ee25318a76cc80083b55482c31d78253215d46c0c72918ef` | nhận. Trang https://www.mql5.com/en/code/77653 . Chưa biên dịch |

Chạy lại cùng URL thì `trung`, không thêm việc. TradingView script `LkgKT3TG` HTTP 200 nhưng Pine không có trong HTML tĩnh → không xếp. LiteFinance `https://my.litefinance.org/en/traders` HTTP 200, 16 id hồ sơ trên danh sách, không có file EA và không có DD → không xếp.

```
python -m pytest test_nap_ea_goc.py -q
python -m seeker.nap_ea_goc --toi-da 3
python -m seeker.nap_ea_goc --toi-da 2 --mau-cong-khai
```

Lệnh thứ hai chỉ đọc kho local. Lệnh thứ ba tối đa vài GET công khai (GitHub contents + một raw, một file Code Base, một trang TradingView, một trang LiteFinance). Không quét 1600 tín hiệu.

Phiên này sửa bộ đọc và cách ghi lỗi của nguồn **đã có**, không thêm catalog mới, không push `main`, không merge, không chạy MT5, không đụng máy nhà, không restart runner.

Nhánh: `cursor/seeker-source-recovery-ca1f`.

Mâu thuẫn với `TRI_NHO/00_DOC_TRUOC.md` mục 7 (phiên xong thì `git push origin main`): lệnh phiên này cấm push/merge/force-push `main`. Đã ghi vào `TRI_NHO/QUYET_DINH.md`. Worker máy nhà vẫn tự commit `hang_doi` trên `main`; đừng rebase nhánh này lên từng commit hàng đợi.

## Việc đã xong và đã test

Lệnh (không mạng, trừ smoke):

```
python -m pytest test_seeker_nguon_loi.py test_nguon_seeker.py test_cong_khai.py test_seeker_v2.py test_nang_cap_20_10.py::test_loc_trung_truoc_khi_tai -q
python -m seeker.chan_doan
python -m seeker.cong_khai.kho_83
python -m seeker.chan_doan --smoke 2
```

`--smoke` trần cứng 5 URL. Lần chạy 2026-11-07 03:01 (giờ máy, box UTC) chỉ 2 URL. Không quét 311, không quét 1600.

| Việc | Kết quả |
|---|---|
| 311 nguồn | `unknown` 166, `not_implemented` 113, `auth` 18, `stale` 14. `no_data` = 0. Quy tắc dùng được = 0 |
| Bản quét sổ 2026-10-20 | Chỉ 2 nguồn (arxiv robots, quantconnect 3 mục). Gắn `stale`, không gọi là 0 nguồn |
| MQL5 Code Base / GitHub / TradingView / diễn đàn | Parser thuần + fixture. HTTP 200 mà 0 mục = `parse` hoặc `not_implemented`, không phải danh mục rỗng |
| LiteFinance | Danh sách thiếu DD = chưa đánh giá (`so_ho_so` giữ số hồ sơ). Chi tiết bị chuyển hướng = `auth`. Vỏ JS = `parse` |
| CSV MQL5 `/export/history` | Redirect/HTML login = `auth`, không phải 0 lệnh |
| 83 tín hiệu | `reports/seeker_nguon/KHO_83.json`: 23 không USD, 14 lẫn, 46 có USD. Cả 83 `thieu_du_lieu` (chưa có CSV). 0 giao dịch được |
| Lưới từ khoá | Không còn loại hệ. CSV lệnh chồng mới là `chung_minh_lenh`. Cảnh báo 2020/2022 là nhãn |
| Nhịp | `seeker/nhip_tai.py`: ≥ 4 giây/host, cache, lùi 429 cùng UA, dừng host khi challenge, resume |

Smoke thật (không đổi UA, không tắt TLS):

- `https://www.mql5.com/en/signals/1862128` HTTP 200, 148569 ký tự, parser đọc được. Màn hình: Growth 9214.64%, DD 11.7%, CAGR 236.41%/năm, tuổi 44.85 tháng, 746 lệnh, XAUUSD.i, máy chủ thật. **Đây là lịch sử người khác, không phải ĐẠT của hệ mình.**
- `https://social-trading.exness.com/strategy/110170778` `network`: `Errno -2 Name or service not known`. **Không thấy 198.18.0.1 trên box này.** Giả thuyết proxy/DNS 198.18.0.1 của bản 03/11 vẫn chưa được phiên này chứng minh, và lỗi DNS này cũng không chứng minh site chết.

## Không được quét lại

- Đừng chạy `python -m seeker.cong_khai.chay` (1600 id, 2026-11-03, cache 72 giờ nằm trong `data/`, gitignore).
- Đừng chạy `python -m seeker.nguon_file.quet` với mặc định 5 trang Code Base + 25 repo.
- Đừng `seeker_quet_nguon.py --ep` cả 311 từ box này. Myfxbook/ForexFactory/forex-station đã challenge hoặc HTTP 200 mà 0 chủ đề; dừng, không đổi UA.
- Đừng tải CSV history MQL5. Endpoint đòi đăng nhập. Trình duyệt là việc của phiên cha.
- `data/cong_khai/tin_hieu.jsonl` không có trong git. Đừng tái sinh `reports/MQL5_LOC_CHAT.md` khi thiếu file đó — bản 03/11 vẫn là danh sách 83.

## Cách đọc trạng thái

`python -m seeker.chan_doan` chỉ đọc sổ + bản chụp đã commit.

- `unknown`: chưa đo. Không phải 0 kết quả.
- `stale`: có bản cũ hơn 3 ngày. `loai_ban_chup` là loại của bản đó. `lan_thanh_cong` chỉ khi bản đó là `ok`.
- `auth`: sổ khai báo đăng nhập, hoặc bản chụp challenge/login. Không lấy cookie.
- `not_implemented`: thủ công, trình duyệt, hoặc Pine chưa nằm trong HTML tĩnh.
- `no_data`: bộ đọc chạy đúng và nguồn thật sự rỗng.
- `quy_tac_dung_duoc`: luật đã giải mã điểm vào và có OOS. Hiện **0**. Mã `.mq5` tải về và 1065/83 màn hình không tính.

Báo cáo: `reports/seeker_nguon/CHAN_DOAN.md`.

## Kho 83

```
python -m seeker.cong_khai.kho_83
python -m seeker.cong_khai.kho_83 --nhap DUONG.csv --id 2394758 --url https://www.mql5.com/en/signals/2394758
```

`--url` phải đúng `https://www.mql5.com/en/signals/<id>` và id phải nằm trong 83. File HTML login bị từ chối. CSV ghi vào `data/cong_khai/csv/` (gitignore) kèm `<id>.nguon.json`. Sổ commit chỉ giữ sha256, số dòng, cấp `replay_csv`. Replay không phải hệ giao dịch. Chưa có điểm vào giải mã và OOS thì `giao_dich_duoc` vẫn false.

Ưu tiên hiển thị: nhóm 0 (không USD) trước, nhóm 2 (USD/vàng/crypto) vẫn giữ. Trùng tên + cùng mã là `trung_nghi_ngo`, không gộp. Khớp tên 70% không phải chứng.

## Mâu thuẫn lưới

Lọc 03/11 loại 244 tín hiệu vì từ khoá lưới/martingale và thiếu năm 2020/2022 (`reports/MQL5_LOC_CHAT.md`). Chỉ thị 07/11: không suy nhãn lưới từ từ khoá, không vứt hệ lưới/DCA có lãi. Code `seeker/cong_khai/loc_chat.py` đã đổi theo chỉ thị mới. Các cổng tuổi ≥ 24 tháng, tài khoản thật, ≤ 3 mã, DD, CAGR, đường growth **giữ**. Bản markdown 83 không bị ghi đè.

## File chính

| File | Vai trò |
|---|---|
| `seeker/phan_loai_loi.py` | auth / challenge / network / parse / not_implemented / no_data / stale / unknown / robots |
| `seeker/nhip_tai.py` | giãn cách, cache, lùi 429, dừng challenge, resume |
| `seeker/chan_doan.py` | chẩn đoán 311 + smoke ≤ 5 |
| `seeker/nguon_file/phan_tich.py` | Code Base, GitHub API, TradingView, diễn đàn |
| `seeker/cong_khai/kho_83.py` | kiểm kê và nhập CSV |
| `seeker/khop_trung.py` | trùng chắc và trùng nghi |
| `seeker/fixtures/` | HTML/JSON/CSV đã cắt, không bí mật |
| `test_seeker_nguon_loi.py` | test các mục trên |

`seeker/thu_thap.py`: `tai_ro()` phân loại; sau challenge không gọi tiếp cùng host. `tai()` vẫn trả None khi stale để không dùng bản cũ như dữ liệu mới.

## Việc phiên sau (không làm trùng)

1. CSV 83: chỉ nhập file chủ đã xuất. Ưu tiên 23 tín hiệu không USD trong `KHO_83.md`, đừng bỏ 46 tín hiệu USD.
2. Pine: chỉ dịch khi HTML tĩnh có `//@version` (`boc_pine`). Trang JS = `not_implemented`. Không bật LLM trả phí.
3. Code Base 99 EA làn A nằm trong bản `seeker/nguon/nguon_file.json`. Mã tải về ở `data/nguon_file/` (gitignore, có thể không có trên box này). Chưa có quy tắc đã giải mã.
4. Myfxbook, Forex Factory, forex-station: dừng khi challenge. Không vượt.
5. Exness: trên box này là DNS `Errno -2`, không phải 198.18.0.1. Đo lại từ máy nhà nếu cần, ghi đúng loại, không tắt TLS.
6. 166 nguồn `unknown` cần một lượt có nhịp khi chủ muốn, từng cụm nhỏ (`seeker_quet_nguon.py --chi a,b`), không `--ep` cả sổ từ datacenter.
7. Đừng gọi màn hình công khai là ĐẠT của hệ. Cần điểm vào đã giải mã rồi OOS/demo.
