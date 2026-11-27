# Bàn giao SP500 + vàng — brain2 (27/11/2026)

> Dành cho phiên bot khác (kể cả bot **SP500 – brain2**). Đọc file này trước khi tiếp tục việc SP500/vàng. Trạng thái chạy thực tế xem các file do worker khác ghi (mục 5); **không tạo hay sửa** thư mục `sp500/` và `vang/`.

Repo: https://github.com/thebrainago/brain2 (nhánh `main`). Máy nhà: **DESKTOP-05PNLGF**, user **DUNG**, machineId `92c57ab1-1431-4e07-ac24-3433da8604d6`. Trả lời tiếng Việt có dấu. Chỉ báo **số đo được**.

---

## 1. Mục tiêu và tiêu chí đạt

Dự án **brain2**: tìm hệ giao dịch chạy được trên tài khoản **XM Free Demo**.

Tiêu chí duy nhất:

- **CAGR kép > 10%/năm** và **DD < 80%**.
- **Không khóa holdout 2 năm.**
- **Tối ưu riêng từng mã** (SP500 riêng, vàng riêng; không mang tham số y nguyên sang mã khác).
- Chỉ báo **số đo thật** (Strategy Tester MT5). Kết quả Python/mô phỏng phải ghi rõ là mô phỏng. Chưa đo thì ghi **CHƯA ĐO ĐƯỢC**. Không bịa số.

Quy trình kiểm định cũ (vòng 3) còn dùng được khi cần: Seeker → Cổng 0 (phí XM) → Cổng S → V1 → V3. Chi tiết: `ban_giao/BAN_GIAO_GROKBOT_2026-11-10.md` và `ban_giao/quy_trinh_v3/`.

---

## 2. Lịch sử ngắn (đến trước 27/11)

### 2.1. Các vòng và hệ đã đo (đến 10–16/11/2026)

Bàn giao đầy đủ vòng 3: `ban_giao/BAN_GIAO_GROKBOT_2026-11-10.md` (commit `89f96b90`). Tóm tắt chat đến 16/11 (chỉ trên máy bot, không có trên git): `/workspace/LICH_SU_CHAT_TOM_TAT_2026-11-16.md`.

- Hệ đạt có điều kiện duy nhất đến 16/11: **ghep60ff adxngang GBPCAD H1**, lot CSV cố định. Lượt A (HistData M1, không tick thật) CAGR 15,32%, DD 50,74%; lượt B (99% tick thật) CAGR 58,96%, DD 75,11%. Bộ quản lý lệnh chọn trên 2024–2026; bản lot theo vốn thì cháy. Báo cáo: `reports/v3/ghep60ff/mt5/`.
- Nhiều hệ đã trượt (brainxlmrz, OnlyUJ 2245675, các hệ CSV ghép khác, Kivenara, MCA100, …). Một số hệ **chưa kiểm định xong** — không coi là trượt: b0be91 USDCAD H4, skea154 GBPCAD H4, mql5e52 EURGBP H1, lô 17/10, UV2 NZDCAD, EMA_Cross_Demo AUDCAD, Myfxbook/MQL5 đợt 2.
- 78 hệ gắn nhãn “ĐẠT” ngày 21/10 đã bị vô hiệu vì lỗi lot ~100× (31/10), không phải đã đo lại.
- Báo cáo scalp XAUUSD (thebrain-data, 19/11): `thebrain-data/BAN_GIAO_QUY_TRINH_BAO_CAO_XAU.md`.

### 2.2. Hướng gamma / GEX / big trade / order flow (từ 11/11)

Hệ 3 lớp đã thống nhất với Anh:

1. Luật vào lệnh brain2.
2. Lớp quyền chọn: GEX, gamma flip, call/put wall, big trade.
3. Xác nhận order flow futures CME (Sierra Chart + Rithmic của Anh; file `.scid` / `.depth`).

Forex/CFD là OTC: tick volume XM **không** dùng làm footprint.

Nguyên tắc và bảng nguồn (đã đẩy lên git):

- `reports/nguon_live/NGUYEN_TAC_CANH_GAMMA_BIGTRADE.md` (commit `c6bcfcd6`)
- `reports/nguon_live/NGUON_LIVE_GEX_ORDERFLOW_2026-11-11.md` (commit `0f25314a`)

Nguồn chính: OTL (https://live.otldata.com/ — **chỉ xem bằng trình duyệt**, không cào API nội bộ; robots.txt cấm crawler), FlashAlpha, WyckFlow, GEXMetrix, OptionCharts, Gamma Cockpit, tick-stream, SqueezeMetrics DIX, CFTC COT.

Cách đọc và dùng (rút gọn):

- Trên flip: gamma dương, thị trường hay hồi về trung bình. Dưới flip: gamma âm, dễ chạy, breakout mạnh hơn.
- Wall khác nhau theo kỳ đáo hạn; kỳ ngắn biến mất khi đáo hạn. **Không set-and-forget.** Kiểm lại mỗi sáng và sau khoảng 21:30 giờ VN.
- Big trade (LC/SC/LP/SP; LC + SP nghiêng mua) là **bộ lọc hướng và đánh dấu mức**, không phải tín hiệu vào trực tiếp.
- Quy đổi future → CFD: `basis = giá nguồn − giá CFD`, đo cùng lúc, tính lại mỗi lần. Mức theo GLD: nhân ≈ 10,9 rồi trừ basis.
- Dữ liệu khác đáng khai thác: đỉnh/đáy phiên + quét thanh khoản, VWAP, volume profile, phân kỳ delta/hấp thụ, IV/skew, lợi suất thực, DXY, COT, lịch tin.

Số liệu vàng đã ghi (lịch sử, không dùng làm mức hiện tại): file thô trên máy bot `/workspace/canh_chart/muc_gamma.jsonl` (11/11 07:50 và 09:00; 16/11 22:45).

Ngày 16/11 Anh ra lệnh khẩn (t335): tạm dừng mọi routine/vòng lặp để tiết kiệm token. Routine canh gamma đã dừng. Lệnh sau (t341–t343) **mở lại** việc backtest SP500/vàng và dùng hết công suất hai máy — làm theo lệnh mới này, không tự bật lại routine canh chart trừ khi Anh bảo.

### 2.3. Phần cứng máy nhà (đo 27/11/2026)

- Main **Huananzhi X99-P4F** (1 socket LGA 2011-3, 4 khe DDR4).
- CPU **Xeon E5-2630 v4** (10 nhân / 20 luồng, TDP 85W).
- RAM **1 thanh 32GB DDR4 2133 LRDIMM** Samsung `M386A4G40DM0-CPB` — đang chạy **một kênh**. LRDIMM **không trộn** với RDIMM ECC thường.
- Card **GT 730**.
- Ổ: E là HDD chậm; D ít chỗ. Ưu tiên dữ liệu **E > D > C** (xem `may_nha/VAN_HANH_MAY_NHA.md` mục 9).
- RAM là nút thắt: mỗi test real ticks khoảng 2–5,4 GB. Giữ RAM trống ≥ 6 GB. Thực tế nên chạy **tối đa khoảng 4 slot MT5** cùng lúc (tài liệu vận hành cũ ghi trần ~5 test).

Đã bàn mua thêm (chưa mua): 1× E5-2686V4 + 1 thanh 32GB LRDIMM đúng loại (tốt nhất cùng mã Samsung) + tản K400. Main chỉ 1 socket nên **không** lắp kit dual X99.

---

## 3. Việc ngày 27/11/2026

### 3.1. Fxaurum Platform (máy nhà)

Tên đúng: **Fxaurum**. Đây là app chạy **local** trên máy nhà (đã nối Rithmic), không phải nguồn web. Gateway: `ws://127.0.0.1:9001/`. Tài liệu API công khai: https://fxaurum.github.io/rithmic-api-docs/api.html.

Kho tick đã thấy (ngày 27/11):

- **ESZ6** (E-mini S&P 500): khoảng **61,8 triệu tick**, 51 phiên từ 20/08 đến 27/11/2026; dày và liên tục từ 21/09.
- **GCZ6** (vàng COMEX): cùng khoảng ngày, khoảng **6,1 triệu tick**.
- Còn nến 1 phút / 1 giờ (kéo nhanh), nến ngày, dữ liệu order flow (absorption, iceberg, sweep) và khoảng 10 GB dữ liệu options.
- Nến 1 ngày kéo nhiều ngày qua API thì **bị timeout**.

**Cấm** chạy `syncTicks` / `syncHistory` (không đồng bộ lại kho tick/lịch sử qua lệnh này).

Đây là giá **futures**. Khi áp cho CFD XM (US500 / GOLD) phải quy đổi theo **basis** đo cùng lúc, tính lại mỗi lần. Kho chỉ khoảng 3 tháng — hợp để kiểm bộ lọc order flow và entry trong ngày, **không đủ** để backtest nhiều năm. Muốn lấy data tiếp: để app **Fxaurum Rithmic API** mở trên máy nhà.

### 3.2. Chỉ thị của Anh (t341–t343)

- Bật **The Seeker** và **The Brain** để tìm chiến lược / chỉ báo phù hợp SP500.
- Kết hợp các bộ tham số khác nhau để khai thác SP500.
- Quan điểm của Anh: thêm bộ lọc xu hướng, đánh mạnh tay, **hedge mạnh theo chiều mua**, có thể **chốt trong ngày**.
- Backtest **vàng và SP500** với mọi bộ tín hiệu và mọi cách kết hợp chúng. SP500 đào sâu hơn.
- Chỉ cần lãi tốt và DD không quá 80%.
- Dùng hết công suất máy nhà và máy Grok Bot.
- Lưu lịch sử và hướng dẫn trên git **và** máy nhà cho phiên khác đọc được (file này).

### 3.3. Module, slot, bot mới

- Module SP500: thư mục `sp500/` (đào sâu, module riêng trên git).
- Module vàng: thư mục `vang/`.
- Slot MT5: **p1, p6 cho SP500**; **p3, p4 cho vàng**. Biến: `BRAIN_SLOTS=p1;p6;p3;p4`.
- Đã tạo bot mới tên **SP500 – brain2** để tiếp tục phần SP500.

Worker khác ghi tiến độ vào `sp500/TRANG_THAI.md` và `vang/TRANG_THAI.md`. File này chỉ **trỏ tới** hai file đó; không tạo và không sửa hai thư mục đó.

---

## 4. Quy tắc an toàn (giữ nguyên, bắt buộc)

- Không đưa bí mật vào git hay chat. Mật khẩu nằm trong **vault**, không có trong repo.
- **Không đọc** `E:\api.txt`.
- `taskkill` chỉ theo **PID chính xác**. Không bao giờ kill `claude.exe` hoặc terminal XM chính (`C:\Program Files\XM Global MT5`).
- Trên máy nhà: **không** autostash, rebase, force push, `reset --hard`, đổi nhánh.
- **Không sửa** file chưa commit trong `E:\brain2_grok` (nhánh `fix/r1-cpu-seeker-moi-quantlab-gates`).
- Chỉ **Free Demo**. Không gửi Telegram.
- Không bao giờ commit: `config/ma_nguon_con_tro.json`, `config/ngan_sach_nhip.json`, `nhat_ky/kho_co_che_ghi.log`, `reports/EVO_SUC_KHOE.md`, `reports/VONG_DAY_DU.json`.
- **Không chạy** `tho_mt5.py --song-song`.
- Tôn trọng lệnh cấm của trang và robots.txt. Không giả fingerprint, không dùng endpoint không công bố, không chép phiên đăng nhập, không đổi IP để lách ban. **OTL:** chỉ xem bằng trình duyệt như người dùng thường, không cào API nội bộ.
- Không đụng game Riot trên ổ D. Không đổi thiết lập nguồn / sleep của máy nhà.
- Báo cáo bằng tiếng Việt.

---

## 5. Cách phiên khác tiếp tục

1. Đọc file này, rồi `TRI_NHO/00_DOC_TRUOC.md`, rồi quy trình máy nhà `may_nha/VAN_HANH_MAY_NHA.md` — **đặc biệt mục 10**: khi Anh nhắn cần dùng máy (chơi game, việc riêng) thì **dừng ngay** toàn bộ việc brain2 (thợ, tester, routine canh); chỉ chạy lại khi Anh nói rõ.
2. Đọc trạng thái mới nhất (do worker khác ghi, có thể chưa có file ngay lúc bàn giao):
   - `sp500/TRANG_THAI.md`
   - `vang/TRANG_THAI.md`
3. Đường dẫn máy nhà:
   - Repo dùng cho việc này: `C:\Users\DUNG\brain2`
   - `BRAIN_SLOTS=p1;p6;p3;p4` (p1, p6 = SP500; p3, p4 = vàng)
   - Terminal XM chính (không đụng): `C:\Program Files\XM Global MT5`
   - Exness: `E:\exness_cent`
   - Ổ E: HDD chậm. Ổ D: ít chỗ. Dữ liệu và test không gấp: E rồi D, tránh C.
   - Clone thợ cũ: `D:\brain2_tho` (không chạy `tho_mt5.py` trong `C:\Users\DUNG\brain2`). Slot portable lịch sử: `E:\brain2_grok\mt5_slots\g1`…`g12`, `E:\mt5_tester\p5`; p1/p3/p4/p6 từng ở `D:\mt5_tester\` (xem lại trên máy trước khi phóng).
4. Fxaurum: để app mở, gọi API local `ws://127.0.0.1:9001/`. Không chạy `syncTicks`/`syncHistory`. Futures → CFD qua basis.
5. SP500 ưu tiên sâu hơn vàng; kết hợp tín hiệu + lọc xu hướng + lot mạnh + hedge chiều mua + đóng trong ngày, rồi đo trên tester. Tiêu chí: CAGR kép > 10%/năm, DD < 80%.
6. Git trên máy nhà: nếu `C:\Users\DUNG\brain2` có thay đổi chưa commit hoặc không đứng ở `main` thì **không** `git pull` / rebase. Chỉ chép file bàn giao vào `C:\Users\DUNG\brain2\ban_giao\` khi file đó chưa có chỉnh sửa local.
7. Không tự bật lại routine canh gamma / vòng lặp nền trừ khi Anh yêu cầu rõ.

Nhật ký vận hành máy nhà: `nhat_ky/van_hanh_may_nha.md`.

---

## Cập nhật tối 27/11/2026 (đến 23:15 giờ Việt Nam) — cho phiên bot mới đọc

### Yêu cầu hiện hành của Anh
- T1: test các bộ quy tắc vào lệnh theo công cụ data (big trade, delta, CVD, VWAP/VP, GEX) trên data Fxaurum; tìm tổ hợp và cách xử lý khi tín hiệu xung đột.
- T2: tài khoản cent, phong cách tay của Anh: không SL, hedge, nhồi DCA, tỉa lệnh, chốt theo lãi/lỗ tổng; kết hợp entry data + truyền thống + chỉ báo. Mã: XAU và US500.
- Tiêu chí: lãi > 0, DD < 80%; cho phép DCA/hedge/cao tần/gỡ lệnh.
- **Mới (t350, 22:31):** chấp nhận GỒNG, không đóng lỗ tổng; nạp thêm vốn để gồng (giả định trần 30k = 10k + 20k nạp); trong lúc DD sâu thì vào lệnh nhỏ để tỉa rổ lỗ / tăng vốn chịu đựng.
- Sàn cent: Anh CHƯA trả lời dùng sàn nào (đang giả định Exness Standard Cent 1:1000).
- Không bao giờ đặt lệnh thật.

### Kết quả đã đo
**T1 — luật ưu tiên data (big30 > delta15 > mức giá)** — `sp500/UU_TIEN_HYB_SCALP.md` (890aa11c)
- Gắn vào HYB+AG làm điểm vào hoặc chặn DCA: KHÔNG đạt (US500 lãi giảm từ +1.501,90 xuống ~+1.000, DD gần gấp đôi; XAU âm).
- Giữ 1–5 phút: mọi tín hiệu âm sau phí; lợi thế chỉ ở 30–60 phút → dùng data làm bộ lọc chiều/ngữ cảnh.
- Nhật ký bóng log-only `sp500/ma/bong_tin_hieu.py` đang chạy trên máy nhà PID 16676 (ra `C:\Users\DUNG\sp500_2711\bong\nhat_ky`). Dừng: `taskkill /PID 16676 /F`.

**US500 — ĐẠT** — `sp500/LOC_NGU_CANH_DANH_MUC.md`, `sp500/STRESS_CHUNG_VON.md` (d1bb71e5, 2d445567)
- tay_v2 US500 lọc `p1_union_es` (mặc định): +657,83 USD, DD 1,77%.
- tay_v2 ×1,5 lot khi cùng chiều data / ×0,5 khi ngược: +920,39, DD 1,81%, DSR 0,993, 4/4 stress tổng hợp.
- Danh mục lõi chung vốn 10k: HYB+AG US500 + tay_v2 ×1,5/×0,5 + lệnh phụ giữ 60′ = +3.119,31 USD, DD 4,59%, stress chung vốn thật 11/11 (DD tệ nhất 45,22%).

**XAU — CHƯA ĐẠT trên MT5 tick thật**
- Python Jun–Nov (59672872, loss_close 30%, ADX30) đẹp (+15.930, 11/11) nhưng MT5 tick thật 2025.09–2026.11 CHÁY (−9.994). Python cũng cháy cửa sổ đầy → cửa sổ Jun–Nov bị chọn lệch. `BAO_CAO_TAYV2_MT5.md`.
- Bản tốt nhất Python cửa sổ đầy (flat_orphan, maxL8: +57.232, DD 13%) → MT5 vẫn cháy; Python KHÔNG phải proxy cho vàng. `BAO_CAO_VANG_WF.md` (0c6a64b6).
- Nguyên nhân: đóng lỗ tổng 30% bị chạm liên tiếp trong các đợt chạy một chiều (09–10/2025, cuối 01/2026).
- Stress phải gồm cả gap vàng TĂNG +10/+20%.
- Đối chứng đã đạt trên MT5 trước đây: Hedge EMA55 H1 đảo 2 ATR ×1,5 = +13.051,52, DD 45,09%.

### Đang chạy dở (việc tiếp theo)
- Vàng MT5-first trên p4: chế độ loss_close=0 (gồng) + động cơ tỉa lệnh (lệnh nhỏ chốt nhanh, gom lãi đóng tầng lỗ nặng nhất), lọc chiều EMA55 H1 làm biến thể, mô phỏng mốc và số tiền nạp thêm; đạt nếu lãi>0 và DD tệ nhất < 80% của 30k. Script nháp: `vang/ma/chay_tia_p4.py`, `vang/ma/chay_opt_tayv2_p4.py`, `vang/ea/VANG_HedgeTay.mq5` (chưa commit).
- Phân tích lịch sử tay Anh: vàng thắng chủ yếu giữ <5′; lỗ lớn nhất 25/11 lot 1,00 ôm 30′–4h; 50% lệnh thua vào ngược delta15.

### Quy tắc an toàn
Xem phần đầu file này và `may_nha/VAN_HANH_MAY_NHA.md`. Slot p3/p5/p6/g2/g3/g4 dùng chung Bases → chỉ 1 terminal mỗi lúc; vàng dùng p4, SP500 dùng p6. Không kill claude.exe, terminal XM chính; kill theo PID. Không đọc E:\api.txt.
