# Dịch ngược vòng 2: swap + margin cho lưới, và 5 EA vàng Telegram + CLMCA (03/11/2026)

> Mọi số dưới đây là **MÔ PHỎNG Python**, chưa phải Strategy Tester MT5. Tiêu chí ĐẠT duy nhất: **DD < 80% VÀ CAGR > 10%/năm**.

## Dữ liệu
- Tải thêm HistData M1 2008–2023 (miễn phí, thư viện `histdata`) cho XAUUSD (từ 2009-03), EURCHF, AUDNZD, NZDCAD, EURGBP → gộp H1 (và M15/H4 cho vàng), giờ EST cố định +7 h ≈ NY+7. Nối với chuỗi 2024–2026 sẵn có (hd28 / hd_ck7). NZDCAD không có đoạn 2024–2026 trên box → chỉ 2008–2023. Dữ liệu nằm ngoài repo: `/workspace/du_lieu_fx/hd_dai/`.
- Dukascopy H1: ~18 s/tháng → bỏ.

## Phần 1 — Lưới UV1/UV2 có swap + margin
- Swap: `config/phi_xm_micro.json` (XM đo 06/10/2026) cho EURCHF, AUDNZD, EURGBP; AUDCAD, NZDCAD không có trong bảng XM → `config/chi_phi_do.json` (FXCE đo 22/08/2026, **không phải XM**). Áp giá trị hiện tại cho cả 2008–2026: **swap lịch sử CHƯA ĐO ĐƯỢC**. Ba kịch bản: `swap_do` (giá trị đo), `swap_bao_thu` (cả hai chiều = −max(|mua|,|bán|)), `swap_0_lac_quan` (swap 0, chỉ để tham khảo).
- Margin 1:500 theo chân lớn hơn, stop-out 20% → đóng tất cả; giá base/USD và giá trị pip là hằng số xấp xỉ. Vốn 1.000 USD, lô lãi kép.

| Dữ liệu | UV | Swap | Lô/1000 USD | CAGR | DD max | Stop-out/cháy | Tổng swap USD | ĐẠT |
|---|---|---|---|---|---|---|---|---|
| AUDCAD_H1_2008_2026 | UV1 | swap_do | 0.002 | -100,0% | 100,0% | 2008-10-08 | -31 | không |
| AUDCAD_H1_2008_2026 | UV1 | swap_do | 0.001 | 7,3% | 65,9% | không | -3,423 | không |
| AUDCAD_H1_2008_2026 | UV1 | swap_do | 0.0005 | 2,8% | 33,2% | không | -1,039 | không |
| AUDCAD_H1_2008_2026 | UV1 | swap_do | 0.00025 | 1,1% | 15,7% | không | -421 | không |
| AUDCAD_H1_2008_2026 | UV2 | swap_do | 0.002 | -100,0% | 100,0% | 2008-09-16 | 7 | không |
| AUDCAD_H1_2008_2026 | UV2 | swap_do | 0.001 | -100,0% | 100,0% | 2008-10-06 | 8 | không |
| AUDCAD_H1_2008_2026 | UV2 | swap_do | 0.0005 | 4,6% | 82,5% | không | -1,026 | không |
| AUDCAD_H1_2008_2026 | UV2 | swap_do | 0.00025 | 2,5% | 42,8% | không | -311 | không |
| AUDCAD_H1_2008_2026 | UV1 | swap_bao_thu | 0.002 | -100,0% | 100,0% | 2008-10-08 | -106 | không |
| AUDCAD_H1_2008_2026 | UV1 | swap_bao_thu | 0.001 | -100,0% | 100,0% | 2020-03-19 | -3,853 | không |
| AUDCAD_H1_2008_2026 | UV1 | swap_bao_thu | 0.0005 | -5,6% | 74,5% | không | -2,035 | không |
| AUDCAD_H1_2008_2026 | UV1 | swap_bao_thu | 0.00025 | -1,8% | 38,6% | không | -924 | không |
| AUDCAD_H1_2008_2026 | UV2 | swap_bao_thu | 0.002 | -100,0% | 100,0% | 2008-09-11 | -124 | không |
| AUDCAD_H1_2008_2026 | UV2 | swap_bao_thu | 0.001 | -100,0% | 100,0% | 2008-10-06 | -68 | không |
| AUDCAD_H1_2008_2026 | UV2 | swap_bao_thu | 0.0005 | 1,6% | 82,2% | không | -1,543 | không |
| AUDCAD_H1_2008_2026 | UV2 | swap_bao_thu | 0.00025 | 1,1% | 44,4% | không | -599 | không |
| AUDCAD_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.002 | -100,0% | 100,0% | 2008-10-08 | 0 | không |
| AUDCAD_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.001 | 13,8% | 60,0% | không | 0 | ĐẠT |
| AUDCAD_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.0005 | 6,4% | 27,0% | không | 0 | không |
| AUDCAD_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.00025 | 3,1% | 15,4% | không | 0 | không |
| AUDCAD_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.002 | -100,0% | 100,0% | 2008-09-16 | 0 | không |
| AUDCAD_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.001 | -100,0% | 100,0% | 2008-10-06 | 0 | không |
| AUDCAD_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.0005 | 7,4% | 83,0% | không | 0 | không |
| AUDCAD_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.00025 | 3,7% | 43,0% | không | 0 | không |
| AUDNZD_H1_2008_2026 | UV1 | swap_do | 0.002 | -100,0% | 100,0% | 2013-12-12 | -5,324 | không |
| AUDNZD_H1_2008_2026 | UV1 | swap_do | 0.001 | -3,9% | 91,3% | không | -3,774 | không |
| AUDNZD_H1_2008_2026 | UV1 | swap_do | 0.0005 | -0,3% | 38,5% | không | -1,141 | không |
| AUDNZD_H1_2008_2026 | UV1 | swap_do | 0.00025 | -0,0% | 18,1% | không | -462 | không |
| AUDNZD_H1_2008_2026 | UV2 | swap_do | 0.002 | -100,0% | 100,0% | 2008-10-10 | -169 | không |
| AUDNZD_H1_2008_2026 | UV2 | swap_do | 0.001 | -100,0% | 100,0% | 2015-04-03 | -941 | không |
| AUDNZD_H1_2008_2026 | UV2 | swap_do | 0.0005 | 2,1% | 50,6% | không | -1,031 | không |
| AUDNZD_H1_2008_2026 | UV2 | swap_do | 0.00025 | 1,0% | 22,2% | không | -401 | không |
| AUDNZD_H1_2008_2026 | UV1 | swap_bao_thu | 0.002 | -100,0% | 100,0% | 2013-07-31 | -7,708 | không |
| AUDNZD_H1_2008_2026 | UV1 | swap_bao_thu | 0.001 | -100,0% | 100,0% | 2014-12-16 | -2,356 | không |
| AUDNZD_H1_2008_2026 | UV1 | swap_bao_thu | 0.0005 | -100,0% | 100,0% | 2020-03-12 | -1,611 | không |
| AUDNZD_H1_2008_2026 | UV1 | swap_bao_thu | 0.00025 | -4,9% | 69,3% | không | -1,103 | không |
| AUDNZD_H1_2008_2026 | UV2 | swap_bao_thu | 0.002 | -100,0% | 100,0% | 2008-10-10 | -237 | không |
| AUDNZD_H1_2008_2026 | UV2 | swap_bao_thu | 0.001 | -100,0% | 100,0% | 2014-12-11 | -2,214 | không |
| AUDNZD_H1_2008_2026 | UV2 | swap_bao_thu | 0.0005 | -1,4% | 76,2% | không | -1,526 | không |
| AUDNZD_H1_2008_2026 | UV2 | swap_bao_thu | 0.00025 | -0,6% | 35,5% | không | -701 | không |
| AUDNZD_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.002 | -100,0% | 100,0% | 2014-01-14 | 0 | không |
| AUDNZD_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.001 | 8,2% | 64,9% | không | 0 | không |
| AUDNZD_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.0005 | 4,1% | 29,7% | không | 0 | không |
| AUDNZD_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.00025 | 2,1% | 13,2% | không | 0 | không |
| AUDNZD_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.002 | -100,0% | 100,0% | 2008-10-10 | 0 | không |
| AUDNZD_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.001 | 10,5% | 93,4% | không | 0 | không |
| AUDNZD_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.0005 | 5,3% | 45,4% | không | 0 | không |
| AUDNZD_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.00025 | 2,6% | 25,1% | không | 0 | không |
| EURCHF_H1_2008_2026 | UV1 | swap_do | 0.002 | -100,0% | 100,0% | 2010-06-08 | -600 | không |
| EURCHF_H1_2008_2026 | UV1 | swap_do | 0.001 | -100,0% | 100,0% | 2010-07-01 | -181 | không |
| EURCHF_H1_2008_2026 | UV1 | swap_do | 0.0005 | -100,0% | 100,0% | 2011-08-02 | -86 | không |
| EURCHF_H1_2008_2026 | UV1 | swap_do | 0.00025 | -100,0% | 100,0% | 2026-03-02 | -393 | không |
| EURCHF_H1_2008_2026 | UV2 | swap_do | 0.002 | -100,0% | 100,0% | 2010-06-29 | -616 | không |
| EURCHF_H1_2008_2026 | UV2 | swap_do | 0.001 | -100,0% | 100,0% | 2011-08-02 | -346 | không |
| EURCHF_H1_2008_2026 | UV2 | swap_do | 0.0005 | -100,0% | 100,0% | 2011-08-09 | -131 | không |
| EURCHF_H1_2008_2026 | UV2 | swap_do | 0.00025 | 1,7% | 53,0% | không | -691 | không |
| EURCHF_H1_2008_2026 | UV1 | swap_bao_thu | 0.002 | -100,0% | 100,0% | 2008-10-27 | -256 | không |
| EURCHF_H1_2008_2026 | UV1 | swap_bao_thu | 0.001 | -100,0% | 100,0% | 2010-06-25 | -739 | không |
| EURCHF_H1_2008_2026 | UV1 | swap_bao_thu | 0.0005 | -100,0% | 100,0% | 2011-05-27 | -510 | không |
| EURCHF_H1_2008_2026 | UV1 | swap_bao_thu | 0.00025 | -100,0% | 100,0% | 2014-07-24 | -704 | không |
| EURCHF_H1_2008_2026 | UV2 | swap_bao_thu | 0.002 | -100,0% | 100,0% | 2010-06-07 | -1,805 | không |
| EURCHF_H1_2008_2026 | UV2 | swap_bao_thu | 0.001 | -100,0% | 100,0% | 2010-06-29 | -659 | không |
| EURCHF_H1_2008_2026 | UV2 | swap_bao_thu | 0.0005 | -100,0% | 100,0% | 2011-08-09 | -458 | không |
| EURCHF_H1_2008_2026 | UV2 | swap_bao_thu | 0.00025 | -2,5% | 56,0% | không | -1,240 | không |
| EURCHF_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.002 | -100,0% | 100,0% | 2010-06-22 | 0 | không |
| EURCHF_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.001 | -100,0% | 100,0% | 2010-08-31 | 0 | không |
| EURCHF_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.0005 | -100,0% | 100,0% | 2011-08-01 | 0 | không |
| EURCHF_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.00025 | -3,4% | 68,1% | không | 0 | không |
| EURCHF_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.002 | -100,0% | 100,0% | 2010-06-29 | 0 | không |
| EURCHF_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.001 | -100,0% | 100,0% | 2011-08-02 | 0 | không |
| EURCHF_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.0005 | -100,0% | 100,0% | 2011-08-09 | 0 | không |
| EURCHF_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.00025 | 4,7% | 57,5% | không | 0 | không |
| EURGBP_H1_2008_2026 | UV1 | swap_do | 0.002 | -100,0% | 100,0% | 2008-12-18 | -17 | không |
| EURGBP_H1_2008_2026 | UV1 | swap_do | 0.001 | 10,0% | 93,5% | không | -4,495 | không |
| EURGBP_H1_2008_2026 | UV1 | swap_do | 0.0005 | 4,2% | 45,3% | không | -1,121 | không |
| EURGBP_H1_2008_2026 | UV1 | swap_do | 0.00025 | 1,9% | 20,8% | không | -424 | không |
| EURGBP_H1_2008_2026 | UV2 | swap_do | 0.002 | -100,0% | 100,0% | 2008-12-18 | -22 | không |
| EURGBP_H1_2008_2026 | UV2 | swap_do | 0.001 | -100,0% | 100,0% | 2008-12-26 | -9 | không |
| EURGBP_H1_2008_2026 | UV2 | swap_do | 0.0005 | 7,5% | 63,7% | không | -1,230 | không |
| EURGBP_H1_2008_2026 | UV2 | swap_do | 0.00025 | 3,7% | 33,4% | không | -402 | không |
| EURGBP_H1_2008_2026 | UV1 | swap_bao_thu | 0.002 | -100,0% | 100,0% | 2008-12-18 | -104 | không |
| EURGBP_H1_2008_2026 | UV1 | swap_bao_thu | 0.001 | -100,0% | 100,0% | 2015-03-10 | -1,616 | không |
| EURGBP_H1_2008_2026 | UV1 | swap_bao_thu | 0.0005 | -1,8% | 55,5% | không | -1,959 | không |
| EURGBP_H1_2008_2026 | UV1 | swap_bao_thu | 0.00025 | -0,8% | 26,8% | không | -888 | không |
| EURGBP_H1_2008_2026 | UV2 | swap_bao_thu | 0.002 | -100,0% | 100,0% | 2008-12-18 | -192 | không |
| EURGBP_H1_2008_2026 | UV2 | swap_bao_thu | 0.001 | -100,0% | 100,0% | 2008-12-26 | -99 | không |
| EURGBP_H1_2008_2026 | UV2 | swap_bao_thu | 0.0005 | 5,7% | 58,6% | không | -1,636 | không |
| EURGBP_H1_2008_2026 | UV2 | swap_bao_thu | 0.00025 | 2,9% | 34,4% | không | -566 | không |
| EURGBP_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.002 | -100,0% | 100,0% | 2008-12-18 | 0 | không |
| EURGBP_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.001 | 16,4% | 73,0% | không | 0 | ĐẠT |
| EURGBP_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.0005 | 7,6% | 36,9% | không | 0 | không |
| EURGBP_H1_2008_2026 | UV1 | swap_0_lac_quan | 0.00025 | 3,6% | 20,8% | không | 0 | không |
| EURGBP_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.002 | -100,0% | 100,0% | 2008-12-18 | 0 | không |
| EURGBP_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.001 | -100,0% | 100,0% | 2008-12-29 | 0 | không |
| EURGBP_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.0005 | 10,4% | 63,5% | không | 0 | ĐẠT |
| EURGBP_H1_2008_2026 | UV2 | swap_0_lac_quan | 0.00025 | 5,1% | 33,3% | không | 0 | không |
| NZDCAD_H1_2008_2023 | UV1 | swap_do | 0.002 | -100,0% | 100,0% | 2014-03-19 | -1,455 | không |
| NZDCAD_H1_2008_2023 | UV1 | swap_do | 0.001 | 8,3% | 58,1% | không | -1,603 | không |
| NZDCAD_H1_2008_2023 | UV1 | swap_do | 0.0005 | 3,5% | 30,9% | không | -471 | không |
| NZDCAD_H1_2008_2023 | UV1 | swap_do | 0.00025 | 1,6% | 15,4% | không | -186 | không |
| NZDCAD_H1_2008_2023 | UV2 | swap_do | 0.002 | 40,0% | 68,7% | không | -30,248 | ĐẠT |
| NZDCAD_H1_2008_2023 | UV2 | swap_do | 0.001 | 17,8% | 33,8% | không | -1,705 | ĐẠT |
| NZDCAD_H1_2008_2023 | UV2 | swap_do | 0.0005 | 8,5% | 16,9% | không | -334 | không |
| NZDCAD_H1_2008_2023 | UV2 | swap_do | 0.00025 | 4,2% | 9,4% | không | -109 | không |
| NZDCAD_H1_2008_2023 | UV1 | swap_bao_thu | 0.002 | -100,0% | 100,0% | 2014-03-19 | -1,482 | không |
| NZDCAD_H1_2008_2023 | UV1 | swap_bao_thu | 0.001 | 8,2% | 58,4% | không | -1,652 | không |
| NZDCAD_H1_2008_2023 | UV1 | swap_bao_thu | 0.0005 | 3,4% | 31,0% | không | -485 | không |
| NZDCAD_H1_2008_2023 | UV1 | swap_bao_thu | 0.00025 | 1,6% | 15,5% | không | -189 | không |
| NZDCAD_H1_2008_2023 | UV2 | swap_bao_thu | 0.002 | 39,7% | 68,8% | không | -31,146 | ĐẠT |
| NZDCAD_H1_2008_2023 | UV2 | swap_bao_thu | 0.001 | 17,4% | 33,7% | không | -1,891 | ĐẠT |
| NZDCAD_H1_2008_2023 | UV2 | swap_bao_thu | 0.0005 | 8,4% | 17,0% | không | -350 | không |
| NZDCAD_H1_2008_2023 | UV2 | swap_bao_thu | 0.00025 | 4,2% | 9,5% | không | -114 | không |
| NZDCAD_H1_2008_2023 | UV1 | swap_0_lac_quan | 0.002 | 27,5% | 84,4% | không | 0 | không |
| NZDCAD_H1_2008_2023 | UV1 | swap_0_lac_quan | 0.001 | 12,0% | 50,9% | không | 0 | ĐẠT |
| NZDCAD_H1_2008_2023 | UV1 | swap_0_lac_quan | 0.0005 | 5,4% | 27,6% | không | 0 | không |
| NZDCAD_H1_2008_2023 | UV1 | swap_0_lac_quan | 0.00025 | 2,6% | 13,7% | không | 0 | không |
| NZDCAD_H1_2008_2023 | UV2 | swap_0_lac_quan | 0.002 | 45,0% | 66,9% | không | 0 | ĐẠT |
| NZDCAD_H1_2008_2023 | UV2 | swap_0_lac_quan | 0.001 | 19,9% | 33,1% | không | 0 | ĐẠT |
| NZDCAD_H1_2008_2023 | UV2 | swap_0_lac_quan | 0.0005 | 9,5% | 16,2% | không | 0 | không |
| NZDCAD_H1_2008_2023 | UV2 | swap_0_lac_quan | 0.00025 | 4,7% | 9,0% | không | 0 | không |

**Đọc kết quả**:
- Khi thêm swap đo được, **UV1 AUDCAD lô 0,001 không còn đạt** (CAGR 7,3%, DD 65,9%; trước đó không-swap 13,8%/60,0%).
- Đạt với swap ĐO: chỉ **UV2 trên NZDCAD 2008–2023** — lô 0,001/1000 USD: CAGR 17,8%, DD 33,8%; lô 0,002: CAGR 40,0%, DD 68,7%; vẫn đạt ở kịch bản swap bảo thủ (17,4%/33,7% và 39,7%/68,8%). Swap NZDCAD lấy từ FXCE (−1,83/−2,01 điểm), không phải XM; chuỗi thiếu 2024–2026; chọn ra từ 5 cặp × 2 ứng viên × 4 mức lô × 3 kịch bản = 120 lần chạy → rủi ro chọn may mắn cao. Cần kiểm MT5 real tick với swap XM NZDCAD trước khi tin.
- EURCHF: cả hai ứng viên cháy (2010–2011 và SNB 2015) trừ lô nhỏ nhất (không đạt).
- Các dòng ĐẠT chỉ ở kịch bản swap 0 (UV1 AUDCAD 0,001; UV1 EURGBP 0,001; UV2 EURGBP 0,0005; NZDCAD) **không tính là đạt**.

## Phần 2 — 5 EA vàng Telegram (vutruea) + CLMCA, XAUUSD 2009-03 → 2026-10 (17,6 năm)
- Dịch sang Python từ mã nguồn `.mq5` (`nhan/dich_nguoc/backtest_vang.py`), giữ tham số mặc định (rủi ro % theo AutoLot mặc định: EA1/2/4 1,5%, EA3 2%, EA5 1%; CLMCA C_V1 rủi ro 1% số dư thay vì $50 cố định của bộ .set để lãi kép). Vốn 10.000 USD, lô chuẩn 100 oz, bước 0,01.
- Phí: spread 0,55 USD (p50 GOLDmicro XM đo), hoa hồng 0, swap XM đo −83,83 / +20,64 điểm/lot/ngày (x3 thứ Tư) + kịch bản bảo thủ + kịch bản swap 0. Swap XM hiện tại áp cho 2009–2021 (lãi suất ~0) gần như chắc chắn quá nặng → kịch bản swap 0 để tham chiếu.
- Giới hạn mô hình: tín hiệu ở nến đóng, vào ở giá mở nến kế; nến chạm cả SL lẫn TP → SL trước; trailing/breakeven/thang SL cập nhật bằng giá đóng nến (EA thật cập nhật mỗi tick); CLMCA chưa mô phỏng trần 2 lệnh lỗ/ngày và độ trễ vào lệnh 60 giây; EA3 không có OCO (giống mã gốc).

| EA | Khung | Swap | Số lệnh | CAGR | DD max | Cháy (số dư < 1%) | Tổng swap USD | ĐẠT |
|---|---|---|---|---|---|---|---|---|
| EA1_MultiEMA_ATR_H1 | H1 | swap_do_XM | 1434 | -100,0% | 99,1% | có | -597 | không |
| EA1_MultiEMA_ATR_H1 | H1 | swap_bao_thu | 1375 | -100,0% | 99,1% | có | -1,086 | không |
| EA1_MultiEMA_ATR_H1 | H1 | swap_0_lac_quan | 1598 | -100,0% | 99,1% | có | 0 | không |
| EA2_RSI_BB_H1 | H1 | swap_do_XM | 1103 | -100,0% | 99,0% | có | -78 | không |
| EA2_RSI_BB_H1 | H1 | swap_bao_thu | 1053 | -100,0% | 99,0% | có | -874 | không |
| EA2_RSI_BB_H1 | H1 | swap_0_lac_quan | 1146 | -100,0% | 99,0% | có | 0 | không |
| EA3_London_Breakout_M15 | M15 | swap_do_XM | 3344 | -100,0% | 99,0% | có | -28 | không |
| EA3_London_Breakout_M15 | M15 | swap_bao_thu | 3344 | -100,0% | 99,1% | có | -29 | không |
| EA3_London_Breakout_M15 | M15 | swap_0_lac_quan | 3352 | -100,0% | 99,1% | có | 0 | không |
| EA4_MACD_200EMA_H1 | H1 | swap_do_XM | 1862 | -10,5% | 89,5% | không | -1,794 | không |
| EA4_MACD_200EMA_H1 | H1 | swap_bao_thu | 1862 | -13,0% | 94,7% | không | -3,194 | không |
| EA4_MACD_200EMA_H1 | H1 | swap_0_lac_quan | 1862 | -8,5% | 83,2% | không | 0 | không |
| EA4_MACD_200EMA_H4 | H4 | swap_do_XM | 358 | 3,9% | 24,2% | không | -2,763 | không |
| EA4_MACD_200EMA_H4 | H4 | swap_bao_thu | 358 | 2,3% | 30,3% | không | -5,236 | không |
| EA4_MACD_200EMA_H4 | H4 | swap_0_lac_quan | 358 | 5,2% | 20,9% | không | 0 | không |
| EA5_Stoch_Pivot_M15 | M15 | swap_do_XM | 10 | -0,0% | 2,0% | không | 0 | không |
| EA5_Stoch_Pivot_M15 | M15 | swap_bao_thu | 10 | -0,0% | 2,0% | không | 0 | không |
| EA5_Stoch_Pivot_M15 | M15 | swap_0_lac_quan | 10 | -0,0% | 2,0% | không | 0 | không |
| CLMCA_C_V1_M15 | M15 | swap_do_XM | 1407 | -100,0% | 99,1% | có | -12,261 | không |
| CLMCA_C_V1_M15 | M15 | swap_bao_thu | 1407 | -100,0% | 99,1% | có | -12,261 | không |
| CLMCA_C_V1_M15 | M15 | swap_0_lac_quan | 1758 | 5,1% | 73,1% | không | 0 | không |

**Đọc kết quả**: không EA vàng nào đạt ở bất kỳ kịch bản swap nào.
- EA1 (EMA 21/55/200 + ATR), EA2 (RSI + Bollinger), EA3 (London breakout) mất gần hết vốn trên 17,6 năm, kể cả khi swap = 0 → kỳ vọng âm sau spread.
- EA4 (MACD + EMA200): H1 thua; H4 dương nhưng chỉ 2,3–5,2%/năm (DD 21–30%).
- EA5 (Stochastic + pivot): chỉ 10 lệnh trong 17,6 năm. Điều kiện gần như mâu thuẫn (Stoch cắt lên dưới 25 nhưng giá đóng phải trên EMA21, đồng thời giá trong ±1,5 USD quanh S1/S2) → không đánh giá được.
- CLMCA C_V1 (chỉ mua): với swap XM hiện tại thì cháy (swap −12.261 USD); swap 0: CAGR 5,1%, DD 73,1% → không đạt. Chạy riêng các đoạn ngắn cho thấy (đoạn ngắn, không đủ tiêu chuẩn): 2020–2026 swap 0: 13,7%/66,8%; có swap: −1,0%/77,5%; 2024–2026 có swap: 34,5%/27,6%.
- CLMCA.zip có mã nguồn đầy đủ (`CLMCA.mq5`, MIT, 1.819 dòng, 5 chế độ). Mới dịch chế độ mặc định C_V1; D_V1, C_V1_P1b, C_V1_P2, L07S: CHƯA ĐO ĐƯỢC. Mã nguồn để ở `data/telegram/clmca/` (gitignore).
- Các file `.ex5` trong thư mục Telegram là mã đã biên dịch, không có nguồn → không dịch.
