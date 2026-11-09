# Seeker gỡ nghẽn + Lọc phí nhanh (Cổng 0) — 09/11/2026

Giờ Việt Nam (Asia/Bangkok, UTC+7). Người soạn: Grok Bot (executor).  
**Không commit/push.** File nằm ngoài repo: `/workspace/quy_trinh_v3/`.  
Mọi số dưới đây là **ĐO** từ file trong `/workspace/brain2` hoặc từ lần test-fetch HTTP hôm nay; chỗ thiếu ghi **CHƯA ĐO ĐƯỢC** / **ƯỚC**.

---

## 0. Tóm tắt một trang

1. **Số nguồn Seeker:** `config/nguon_seeker.json` ghi **`tong: 311`**. Anh nhắc “~321” — khớp gần với `311 + 9` nguồn theo dõi (`config/nguon_theo_doi.json` = 9) → **320**. Cộng `nguon_tu_tim` (28) và `nguon_ung_vien` (26) là kho khác, không phải cùng một chỉ số.
2. **Ưu tiên Anh (t303):** tìm hệ **đã có kết quả công khai** (statement / signal / backtest người khác) → thừa hưởng lọc sẵn. Gỡ nghẽn bằng Gmail đã nối, trình duyệt, VPN/egress máy nhà khi cần.
3. **Cổng 0 lọc phí:** script `/workspace/quy_trinh_v3/loc_phi_nhanh.py` + kết quả JSON cùng thư mục. Trên **9 ứng viên V3**: **7 PASS**, **0 REJECT** (sau khi quy đổi quote→USD đúng), **1 CHƯA ĐO** (EMA_Cross_Demo), **1 PASS mỏng** (brainxlmrz chỉ có CAGR/DD salvage, DD 78,81% sát trần 80%).
4. **Drift all-BUY:** `ghepe9b4`, `ghep60ff`, `ghep_0bf2` CSV vào **100% MUA**. Buy&hold giá cặp cùng kỳ: GBPNZD **CAGR 5,85%**, GBPCAD **4,20%** (trước đòn bẩy) — thấp hơn nhiều CAGR in-sample của hệ, nhưng hướng lãi trùng xu hướng tăng 2024–2026 → **bắt buộc** so ngẫu nhiên / B&H ở V3.
5. **Rút ngắn quy trình:** đề xuất **Cổng 0 (giây) → V1 → V3** (gộp V2 vào V3 nếu MT5 đã có swap + margin + trần giữ). Lô V3 hiện tại Cổng 0 **không** loại ai có CSV → tiết kiệm MT5 của lô này ≈ **0**; giá trị nằm ở **ứng viên Seeker mới** trước khi xếp hàng máy nhà.

---

## 1. Inventory nguồn Seeker (số đo)

| Kho | File | Số đo |
|---|---|---|
| Nguồn cấu hình chính | `config/nguon_seeker.json` | **311** (`tong` = `len(nguon)`) |
| Theo dõi CDP máy nhà | `config/nguon_theo_doi.json` | **9** |
| Tự tìm (Quantocracy…) | `config/nguon_tu_tim.json` | **28** (trạng thái tất cả `THU`) |
| Ứng viên TG/GH | `config/nguon_ung_vien.json` | **26** |
| Quét box (API/RSS) | `reports/SEEKER_BOX_DO.json` | **41** kênh: **36 ok / 5 fail** |
| Chỉ mục đa nguồn | `reports/SEEKER_DA_NGUON.json` | **2580** ứng viên; có mã 1919; `bang_chung_lai.co` **832**; lịch sử từng lệnh **26** |
| URL bị chặn (chọn tay) | `reports/URL_BI_CHAN.md` | **79** URL |
| URL bị chặn (máy gom) | `reports/URL_BI_CHAN_THEM.md` | **7** nguồn `nguon_can_trinh_duyet` |

### 1.1 Phân loại `nguon_seeker.json` (311)

| `cach` | Số |
|---|---|
| http | 97 |
| rss | 56 |
| *(thiếu field — mục `nen_tang_nguon_md`)* | 48 |
| api | 38 |
| trinh_duyet | 30 |
| telegram_web | 22 |
| dang_nhap | 10 |
| x_mcp_* | 9 |
| tay | 1 |

| `can_dang_nhap` | Số |
|---|---|
| false | 242 |
| true | 21 |
| null (thiếu field) | 48 |

**Track-record / lịch sử tài khoản / copy / chợ EA** trong kho 311: **14** mã (collective2, darwinex, myfxbook, zulutrade, etoro, fxblue, fxstat, signalstart, mql5_market_free, ctrader_copy, duplitrade, forexfactory_trade_explorer, myfxbook_autotrade, fxblue_market).

### 1.2 `SEEKER_BOX_DO.json` — lần đo fail (5/41)

| Kênh | ok | n | giay |
|---|---|---|---|
| arxiv | False | 0 | 110,1 |
| quantconnect | False | 0 | 0,5 |
| rss_fh_financial_hacker | False | 0 | 1,5 |
| rss_reddit_quant | False | 0 | 0,1 |
| rss_gestaltu | False | 0 | 0,3 |

### 1.3 Test-fetch read-only hôm nay (09/11/2026, UA Chrome, timeout 12s)

| Nguồn | Kết quả đo | Nhóm nghẽn |
|---|---|---|
| myfxbook.com/systems | HTTP **403** | Cloudflare / bot |
| myfxbook.com/api | HTTP **403** | Cloudflare (API cũng chặn IP box) |
| forums.babypips.com | HTTP **403** | Cloudflare |
| www.forexfactory.com/forum/71… | HTTP **403** | Cloudflare / region |
| www.reddit.com/r/algotrading/.json | HTTP **403** Blocked | Bot / region |
| papers.ssrn.com | HTTP **403** | Bot |
| wccta.com | HTTP **403** | Bot (trước đây 08/2026 từng 200 — **đổi trạng thái**) |
| www.fxstat.com | SSL hostname mismatch | TLS |
| www.darwinex.com | redirect loop | Login / anti-bot |
| www.fxblue.com/ | HTTP **200** | OK trang chủ; `/users` **404** (URL cũ chết) |
| www.mql5.com/en/signals | HTTP **200** | HTML list OK; **export history cần đăng nhập** (đã ghi URL_BI_CHAN) |
| www.mql5.com/en/code/mt5/experts | HTTP **200** | OK |
| www.collective2.com | HTTP **200** + cờ login | Cần session |
| www.zulutrade.com/leaders | HTTP **200** | Trang về được; captcha có thể ở bước sau |
| www.duplitrade.com | HTTP **200** + captcha | Captcha |
| ftmo.com/en/leaderboard | HTTP **200** | HTML; dữ liệu leaderboard thường sau JS |
| quantpedia.com/strategies | HTTP **200** | OK fetch; nội dung strategy có thể paywall |
| tradingview.com/scripts | HTTP **200** | List OK; **mã Pine cần JS/login** |
| forex-station.com | HTTP **200** | OK |
| gogojungle.co.jp | HTTP **200** | OK trang; sản phẩm trả phí — **không mua** |
| ctrader.com/copy | HTTP **200** | OK |

### 1.4 Nhóm nghẽn → cách gỡ (theo Anh t303)

| Nhóm | Ví dụ đo được | Cách gỡ | Cần Anh? |
|---|---|---|---|
| A. Cloudflare / 403 / captcha | Myfxbook, BabyPips, ForexFactory, Reddit, SSRN | Playwright trên box **hoặc** Chrome CDP máy nhà (đã có profile `nguon_theo_doi`); giải captcha tay nếu hiện | Có — captcha / lần đầu login |
| B. Cần đăng nhập + mã mail | MQL5 export history (40 URL trong URL_BI_CHAN), Myfxbook export, Collective2, Darwinex API | Session trình duyệt + **user-Gmail** nhận OTP/link | Có — OTP điện thoại MQL5 nếu bật; Gmail bot tự đọc nếu về mailbox |
| C. Render JS / SPA | FX Blue leaderboard, TradingView source, FTMO board | Playwright; với FX Blue Anh **đã có tài khoản** (mail thebrainalgo) | Có thể tự sau khi login lưu profile |
| D. Region / TLS từ box | Exness Social, LiteFinance (báo cáo 03/11), một số SSL | Egress **máy nhà** (IP nhà) | Có — bật máy nhà |
| E. Paywall / trả phí | GogoJungle sản phẩm, Quantpedia full | **Không mua**; chỉ lấy số forward công khai đã index | Không (bỏ) |
| F. URL chết / đổi | fxblue `/users` 404, darwinex `/d-live` 404 | Cập nhật URL rồi fetch lại | Không |
| G. Robots / chính sách | arxiv robots (SEEKER_QUET_NGUON 20/10) | Tôn trọng robots; dùng API/RSS cho phép | Không |

**Đã đăng ký (từ Gmail, `DANH_GIA_SEEKER_HOP.md`):** MQL5 (Vanh1799), Myfxbook (vanhvanhvanh), FX Blue (thebrainalgo), Forex Factory, cTrader, TradingView, BabyPips, Quantpedia newsletter — **không** thấy mail Darwinex / ZuluTrade / Exness.

---

## 2. Top 30 nguồn/URL ưu tiên gỡ (có kết quả kiểm chứng)

Xếp theo: (1) có statement/signal/live history thật → (2) đã có tài khoản Anh → (3) số ứng viên đang nghẽn → (4) dễ gỡ.

| # | Nguồn | Giá trị kết quả | Nghẽn đo được | Cách gỡ | Cần Anh |
|---|---|---|---|---|---|
| 1 | **MQL5 Signals — export history** (40 id trong URL_BI_CHAN) | Lịch sử từng lệnh công khai sau login | Cần đăng nhập MQL5 | Browser + login Vanh1799; Gmail OTP nếu có | OTP ĐT nếu hỏi |
| 2 | **Myfxbook Systems/Strategies** | Gain/DD/Age + Export history CSV | Cloudflare 403 từ box | CDP máy nhà / Playwright + login vanhvanhvanh | Captcha lần đầu |
| 3 | **Myfxbook API** (`/api`) | Track record máy đọc được | 403 từ box | Thử lại từ máy nhà; lấy token miễn phí trong account | Lấy API token (1 lần) |
| 4 | **FX Blue** leaderboard + export | Thống kê TK công khai | Trang chủ 200; URL cũ 404; cần JS | Cập nhật URL leaderboard + login thebrainalgo | Login nếu hết session |
| 5 | **Collective2** | Chiến lược + audit nhiều năm | 200 nhưng cần login | Đăng ký/login + Playwright | Tạo TK nếu chưa có |
| 6 | **Darwinex DARWINs** | Track record broker-audit | Redirect loop từ box | Máy nhà + login; API key nếu cấp | Đăng ký nếu muốn |
| 7 | **ZuluTrade leaders** | ROI/DD/tuổi | 200; captcha có thể | Playwright; captcha tay | Captcha |
| 8 | **Forex Factory Trade Explorer / Trading Systems** | Thread + statement đính kèm | 403 từ box | CDP máy nhà (đã trong theo_doi) | Captcha/login FF |
| 9 | **BabyPips free systems / EA forum** | EA + forward | Cloudflare 403 | CDP máy nhà | Captcha |
| 10 | **TradingView strategies** (30 script URL_BI_CHAN) | Pine + Strategy Tester trades | Mã qua JS | Browser login TV; lưu `.pine` vào `nhap_tay/` | Login nếu cần |
| 11 | **eToro rankings / Popular Investor** | Copy-investor stats | API path 404 hôm nay | Cập nhật endpoint / scrap UI | — |
| 12 | **cTrader Copy** | Thống kê copy | 200 | Parser + login cTrader (đã có mail) | Login |
| 13 | **SignalStart** | Bảng signal | 200 | Parser HTTP | — |
| 14 | **Forex Station** | EA/thread | 200 | Parser | — |
| 15 | **FTMO / TopStep / prop leaderboards** | Funded P&amp;L | FTMO 200 HTML; trước Cloudflare | Playwright | Captcha có thể |
| 16 | **MQL5 CodeBase** (đã nạp 483) | EA + số tác giả | 200 — **đang chạy tốt** | Giữ; ưu tiên entry có `bang_chung_lai` số | — |
| 17 | **MQL5 Market Free** | EA free demo | HTTP | Chỉ Free Demo | — |
| 18 | **GogoJungle** (43 đã index) | Forward seller | 200; trả phí | Chỉ số công khai — **không mua** | — |
| 19 | **Reddit r/algotrading** | Ý tưởng + thỉnh thoảng kết quả | 403 | Máy nhà hoặc API token | — |
| 20 | **Quantpedia strategies** | Mô tả học thuật | 200; full có thể trả phí | Free blurbs only | — |
| 21 | **SSRN / papers** | Paper quant | 403 | Máy nhà / open PDF | — |
| 22 | **WCCTA / Trading Cup** | Championship | WCCTA 403 hôm nay (đổi) | Playwright máy nhà | — |
| 23 | **DupliTrade** | Copy stats | Captcha | Playwright + captcha | Captcha |
| 24 | **FX Stat** | Account stats | SSL mismatch | Sửa host/URL | — |
| 25 | **Telegram kênh EA** (22 `telegram_web` + ung_vien) | File EA/set chia sẻ | Cần TG client | Theo `QUY_TRINH_NHOM_TELEGRAM.md`; **không gửi tin** (rule) | — |
| 26 | **GitHub** (1159 trong DA_NGUON) | README backtest | Đang ok (BOX_DO n=101) | Ưu tiên repo có báo cáo số | — |
| 27 | **arXiv q-fin** | Paper | BOX_DO fail 110s | Dùng export API/RSS thay scrape | — |
| 28 | **QuantConnect forum** | Backtest cộng đồng | BOX_DO fail | Login QC + browser | Login |
| 29 | **BarclayHedge / CTA index** | Index CTA | Trước 200 | Parser (ít EA FX) | — |
| 30 | **X search backtest** (theo_doi) | Tin cộng đồng | Cần X MCP / login | `x` connector nếu còn auth | Auth X nếu hết |

**Quy tắc lọc Seeker sau khi gỡ:** chỉ đưa vào V1 khi có (a) `tin_hieu` tái tạo được **hoặc** (b) EA chạy tester được — đúng Cổng S trong `QUY_TRINH_VONG3`. Statement thuần → làn B `khop_vao_pct ≥ 70`.

---

## 3. Cổng 0 — `loc_phi_nhanh.py`

### 3.1 Cách hoạt động

- Phí: `config/phi_xm_micro.json` (ĐO). **NZDUSD không có** trong file này → fallback `config/chi_phi_do.json` khóa `NZDUSDMICRO` (ĐO 09/2026), gắn nhãn.
- Hoa hồng XM micro: **0** (`_hoa_hong_lot`, ĐO 37.773 deal).
- Quy đổi quote→USD: `gia_luc_do` ĐO 13/09/2026 (USDJPY 153,488; USDCAD 1,38699; GBPUSD 1,35239; NZDUSD 0,58109).
- Từ CSV lệnh MT5: `net_E = E[profit] + E[swap]`; `spread_cost` ước p90; `edge/cost = (E[profit]+spread_cost) / (spread_cost + max(-E[swap],0))`.
- **REJECT** nếu `net_E ≤ 0` hoặc `edge/cost < 1,5` hoặc không đạt CAGR > 10% & DD < 80% (khi có số đo).

Chạy: `python3 /workspace/quy_trinh_v3/loc_phi_nhanh.py --tu-ung-vien-v3`.

### 3.2 Kết quả trên ứng viên V3 (ĐO)

| Hệ | Cặp | buy% | hold med (ngày) | E[profit] | E[swap] ĐO | net_E | edge/cost | CAGR k=1 | DD k=1 | Cổng 0 |
|---|---|---|---|---|---|---|---|---|---|---|
| skea61c | CADJPY | 49,5 | 0,91 | 5,89 | −0,86 | **5,03** | **3,88** | 13,3% | 10,74% | **PASS** |
| ghep_0bf2 | GBPCAD | **100** | 0,57 | 39,54 | +1,44 | **40,98** | **4,15** | 65,08% | 47,16% | **PASS** + cờ all-BUY |
| ghepe9b4 | GBPNZD | **100** | 8,02 | 64,94 | −4,56 | **60,38** | **7,36** | 129,6% | 31,46% | **PASS** + cờ all-BUY |
| ghep60ff | GBPCAD | **100** | 2,90 | 9,58 | +0,13 | **9,71** | **8,64** | 64,53% | 20,18% | **PASS** + cờ all-BUY |
| 2600ea39 | GBPNZD | 51,9 | 5,92 | 11,93 | −3,50 | **8,43** | **2,69** | 38,28% | 15,8% | **PASS** |
| mql5344 | NZDUSD | 62,9 | 1,39 | 7,35 | −0,32 | **7,03** | **4,99** | 17,49% | 44,82% | **PASS** (phí fallback) |
| 3279 | EURGBP | 50,3 | 11,62 | 22,83 | −8,14 | **14,69** | **2,28** | 71,62% | 52,14% | **PASS phí** nhưng **trượt Cổng S** (chưa giải mã) |
| brainxlmrz | GBPUSD | — | — | — | — | — | — | 13,31% | **78,81%** | **PASS mỏng** (không tách phí) |
| EMA_Cross_Demo | ? | — | — | — | — | — | — | — | — | **CHUA_DO** |

Nguồn số lệnh: `reports/ong_dan/ket_qua_mt5/od_*_lenh_mt5.csv`. CAGR/DD k=1: `hang_doi/da_test/lot_*.json` (trừ brainxlmrz = `TRI_NHO/dac_diem_he/brainxlmrz.json` salvage).

**Lưu ý quan trọng:** các số CAGR/DD trên là **in-sample** cửa sổ CSV (đã bị kiểm toán). Cổng 0 chỉ trả lời “phí XM có ăn hết edge trên mẫu đã chạy không?” — **không** thay V3 OOS.

### 3.3 All-BUY vs buy&hold cùng kỳ (ĐO giá từ CSV vào)

| Hệ | Giá đầu→cuối CSV vào | Ret giá | CAGR giá | Swap ƯỚC 1 micro lot giữ full kỳ (USD) |
|---|---|---|---|---|
| ghepe9b4 / GBPNZD | 2,01505 → 2,35848 (02/01/2024→09/10/2026, 2,77 năm) | +17,04% | **5,85%/năm** | ≈ **−20,8** (swap_mua −3,55 điểm × qd NZD) |
| ghep60ff & ghep_0bf2 / GBPCAD | 1,68549 → 1,88877 | +12,06% | **4,20%/năm** | ≈ **+4,1** (swap_mua +0,57 — GBPCAD long được trả) |

Hệ DCA/lưới in-sample CAGR ≫ B&H giá vì đòn bẩy + nhồi lệnh; GBPCAD long còn được swap dương. **Không** kết luận edge độc lập xu hướng cho đến khi chạy so ngẫu nhiên / B&H cùng quản lý ở V3 (đã ghi trong QUY_TRINH_VONG3).

### 3.4 mql5344 — giữ max 808,9 ngày

Hold max **808,9 ngày** (ĐO từ CSV lệnh). Swap tổng cả mẫu chỉ **−174 USD** trên 542 rổ (nhiều rổ ngắn), nhưng đuôi giữ siêu dài → V3 **bắt buộc** `InpGiuToiDaNen` > 0; không thì Cổng 2/3 phải loại.

---

## 4. Quy trình rút ngắn đề xuất

```
 SEEKER ──► Cổng 0 (loc_phi_nhanh, giây)
              │ REJECT → loai/ + lý do phí
              ▼
            Cổng S (luật/EA)
              ▼
            V1 (điểm vào dài + phí XM) ──► [gộp V2]
              ▼
            V3 máy nhà (WF 12/3, swap+margin+trần giữ+k trong train)
              ▼
            Demo forward
```

**Gộp V2 vào V3 khi nào:** MT5 tester XM **đã** tính spread/swap; EA `BRAIN_XuLiLenh` đã có `InpGiuToiDaNen`, `InpMarginMin`, biến thể atrb/gian/catlo/adx. Việc còn lại của “V2” là **chọn ≤3 biến thể quản lý trên train của từng cửa sổ WF**, không cần vòng MT5 riêng trên cùng CSV ngắn.

**ƯỚC thời gian tiết kiệm** (median ĐO: H4 ≈ 543 s/lần, H1 ≈ 915 s/lần cho ~3 năm real tick):

| Hạng mục | Số đo / ƯỚC | Ghi chú |
|---|---|---|
| Lô V3 hiện tại bị Cổng 0 loại | **0** hệ có CSV | Tiết kiệm MT5 lô này ≈ 0 |
| V1 một hệ × 10 mức k (H4) | ƯỚC 10×543 s ≈ **1,5 giờ** | Mỗi hệ Seeker mới bị Cổng 0 loại trước V1 |
| V1 một hệ × 10 k (H1) | ƯỚC 10×915 s ≈ **2,5 giờ** | |
| V2 đầy đủ ~6 biến thể × 2 k (H4) | ƯỚC 12×543 s ≈ **1,8 giờ**/hệ | Gộp vào V3 → bỏ vòng này trên CSV ngắn |
| Cổng 0 một hệ | **< 1 giây** (ĐO chạy xong cả 9 ứng viên < 0,2 s) | |

Nếu sau khi gỡ Myfxbook/MQL5 mà nạp thêm N ứng viên có statement: kỳ vọng loại sớm những hệ scalp/hold dài trên cặp swap nặng (GBPNZD long, XAU long, …) **trước** khi đụng RAM máy nhà (tối đa ~5 test song song).

---

## 5. Việc cần Anh

1. **Widget/duyệt** còn treo từ lượt trước (sửa code E1–E3… / gates vs labels) — chưa thấy câu trả lời riêng trong t303; t303 chỉ chốt hướng Seeker + lọc phí.
2. **Bật máy nhà** khi sẵn sàng vòng 3 + cho phép egress Seeker (Myfxbook/FF/BabyPips).
3. **OTP / captcha** khi bot login: MQL5 (ĐT), Myfxbook, Collective2, ZuluTrade, FX Blue nếu hết session.
4. **API token Myfxbook** (miễn phí trong account) — một lần, không đưa vào git.
5. **Không cần** mua GogoJungle / Quantpedia trả phí.
6. **NZDUSD:** nên đo bổ sung vào `phi_xm_micro.json` (hiện thiếu) cho đồng bộ với các cặp khác.

---

## 6. File tạo ở `/workspace/quy_trinh_v3/` (chưa commit)

| File | Nội dung |
|---|---|
| `loc_phi_nhanh.py` | Cổng 0 |
| `loc_phi_nhanh_ket_qua.json` | Kết quả chạy 09/11/2026 |
| `SEEKER_GO_NGHEN_VA_LOC_PHI.md` | Báo cáo này |
| `QUY_TRINH_VONG3_2026-11-09.md` | (đã có từ trước) |
