# Thống kê khoảng cách tới MA50 (EVO tự tính)

Tính lúc: 2026-11-13 15:39 UTC+07:00
Múi giờ: Asia/Saigon (UTC+7)

## Định nghĩa

- \( d = (Close - MA50)/MA50 \times 100 \), MA50 = trung bình đơn 50 phiên đóng cửa.
- **Episode**: phiên đầu tiên `d` vượt ngưỡng; bỏ qua tín hiệu mới trong 20 phiên tiếp theo.
- **Lợi nhuận kỳ hạn**: đóng cửa sau 5 / 20 / 60 phiên.
- **Drawdown**: `min(low)` trong 60 phiên tới so với đóng cửa ngày tín hiệu. Ngưỡng hit: 10% với chỉ số, 3% với forex.
- **Về dưới MA50**: có ít nhất một phiên trong 60 phiên tới mà close < MA50 của đúng phiên đó.
- **Đỉnh 60 phiên**: close là cao nhất 60 phiên và là đỉnh cục bộ (phiên sau thấp hơn). "Gãy" = min low 60 phiên tới giảm ≥10% (chỉ số) hoặc ≥3% (forex).

## Nguồn dữ liệu

- Stooq (`^dji`) bị Cloudflare chặn. Dùng Yahoo Finance API v8/chart, tải từng đoạn ~700 ngày, nến ngày.
- ^DJI: 1992-01-02 đến 2026-11-12 (Yahoo không cung cấp đoạn trước 1992 trong API này).
- ^GSPC: 1970-01-02 đến 2026-11-12 (lượt tải không lấy được 1950–1969).
- Forex: không thấy OHLC ngày/H4 sẵn trong `/workspace/brain2-run`. Dùng Yahoo `AUDCAD=X`, `AUDNZD=X`, `EURCAD=X`, `CADJPY=X`. **Chưa phải kho Dukascopy/MT5** — chỉ để có số sơ bộ.
- File kèm: `ma50_results.json`, `ma50_distribution.csv`, `ma50_episode_summary.csv`, `ma50_episodes.csv`, `ma50_peaks_then_drop_examples.csv`.

## Dow Jones (8.730 phiên có MA50, 1992-03-12 đến 2026-11-12)

Phân vị của d: **p95=5,71%; p99=7,87%; p99,5=8,97%; p99,9=10,83%**. Min = −30,81%; trung bình +0,81%.

**Max d = 14,99% ngày 2020-06-08.** Số phiên d ≥ 8 / 10 / 12 / 15 / 20 / 24% = **79 / 18 / 3 / 0 / 0 / 0**.

**Ngưỡng 24% (và cả 20%, 15%) không xuất hiện lần nào.** Không có "phần sau khi chạm 24%" để thống kê.

| Ngưỡng | Số episode | Lãi TB 5p | 20p | 60p | % DD≥10% / 60p | % có lúc close < MA50 / 60p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 8% | 11 | +0,56% | −0,40% | +2,45% | 9% (1/11) | 82% (9/11) |
| 10% | 4 | +0,49% | +1,57% | +5,55% | 0% (0/4) | 75% (3/4) |
| 12% | 1 (2020-06-05) | −5,55% | −3,04% | +4,87% | 0% (0/1) | 0% (0/1) |
| 15 / 20 / 24% | 0 | — | — | — | — | — |

Ngày episode 12% (2020-06-05, d=13,54%) nằm trong nhịp phục hồi COVID; 60 phiên sau vẫn lãi, không về dưới MA50. Mẫu n=1, không suy ra luật.

Đỉnh 60 phiên rồi giảm ≥10% trong 60 phiên: **57 / 567 (10,1%)**. Trung bình d tại những đỉnh đó: **4,81%** (trung vị 4,58%; cao nhất 9,66% ngày 2001-05-21). **Không phải 24%.**

## S&P 500 (14.290 phiên, 1970-03-13 đến 2026-11-12)

Max d = **15,40% ngày 1982-10-13**. p95=6,22%; p99=8,72%; p99,5=9,97%; p99,9=12,92%.

Số phiên ≥8/10/12/15/20/24% = **216 / 71 / 26 / 1 / 0 / 0**. Vẫn **không có 20% hay 24%**.

Episode 10% n=9, lãi TB 60 phiên +8,56%, 0/9 DD≥10%. Episode 15% n=1 (1982-10-13): +1,84 / +3,26 / +6,20% sau 5/20/60 phiên.

Đỉnh rồi gãy ≥10%: **101 / 891 (11,3%)**, trung bình d **4,99%** (cao nhất 9,11%).

## Bốn cặp chéo forex (Yahoo daily)

Không cặp nào tới 15–24%. Ngưỡng thực tế nằm quanh p99 ≈ 4–7%.

| Cặp | Span (có MA50) | N | Max d (ngày) | p99 | p99,5 | p99,9 |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| AUDCAD | 2004-02-06 → 2026-11-13 | 5927 | 7,43% (2009-04-01) | 4,34 | 4,72 | 6,01 |
| AUDNZD | 2004-02-06 → 2026-11-13 | 5926 | 6,19% (2007-09-04) | 4,38 | 4,86 | 5,77 |
| EURCAD | 2004-02-06 → 2026-11-13 | 5910 | 8,30% (2015-08-24) | 5,19 | 6,11 | 7,15 |
| CADJPY | 2004-10-28 → 2026-11-13 | 5736 | 9,15% (2016-12-12) | 6,72 | 7,30 | 8,32 |

Episode (khử trùng 20 phiên), hit = DD ≥3% trong 60 phiên:

| Cặp | Ngưỡng | N | Lãi TB 5/20/60p | % DD≥3% | % về dưới MA50 |
| --- | ---: | ---: | --- | ---: | ---: |
| AUDCAD | 4,34 / 4,72 | 12 / 9 | −0,63/−0,97/+0,81 ; −0,58/−1,48/+0,03 | 50 / 56 | 83 / 100 |
| AUDNZD | 4,38 / 4,86 | 10 / 7 | +0,30/+0,01/+0,74 ; +0,07/−0,41/+0,69 | 50 / 57 | 90 / 86 |
| EURCAD | 5,19 / 6,11 | 10 / 6 | +0,17/−1,41/−1,12 ; −1,90/−2,48/−3,63 | 70 / 83 | 100 / 100 |
| CADJPY | 6,72 / 7,30 | 11 / 9 | −0,76/−0,03/−1,01 ; −0,90/−2,24/−2,65 | 73 / 67 | 91 / 100 |

Đỉnh 60 phiên rồi giảm ≥3% / 60 phiên: AUDCAD 117/213 (d TB 2,85%); AUDNZD 67/218 (3,05%); EURCAD 76/172 (3,91%); CADJPY 153/246 (4,16%).

## Kết luận ngắn

1. Câu "bình quân từ đỉnh cách MA50 24% là gãy" **không đúng** trên Dow 1992–2026 và S&P 1970–2026 với định nghĩa trên: 24% không xuất hiện; các đỉnh rồi giảm ≥10% chỉ cách MA50 khoảng **5%** (trung bình).
2. Trên cặp chéo, stretch thực tế là **khoảng 4–7%** (p99). Sau khi chạm vùng đó, giá thường có drawdown ≥3% và thường về dưới MA50 trong 60 phiên — đây mới là ứng viên vùng tín hiệu/DCA, vẫn phải test lại trên dữ liệu broker và khung H4.
