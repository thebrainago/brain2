# Kiểm toán tiêu chí & pipeline QUANTLAB (Evo, 15/11/2026)

Nguồn: `nao.db` (1.236 giả thuyết, holdout 60/40, dữ liệu đến 02/10/2026). Script: `tools/kiem_dinh/evo/danh_gia_lai.py`, `tong_hop_danh_gia.py`, `chuyen_cap_gop.py`. Chỉ đọc DB, không ghi sổ, không bật dieu_phoi.

## 0. Tiền đề cần sửa
1.214/1.236 giả thuyết là **quét mẫu × tham số tự động** (`kham_pha`, `kham_pha_theo_mau`), 22 từ GitHub, **0 từ Myfxbook/statement**. Tức không phải "hàng nghìn hệ đã có lãi thống kê", mà là biến thể chọn trên train.

## 1. Lỗi tìm thấy
| # | Chỗ | Lỗi | Ảnh hưởng | Sửa |
|---|---|---|---|---|
| 1 | `nhan/do_luong.py` `chi_so` (pf) + audit cũ | PF tính **theo bar**, không theo lệnh. Lệnh giữ nhiều bar → nhiễu trong lệnh kéo PF về ~1 (vd PF lệnh 2,1 = PF bar 0,87) | Phần lớn của "1.078 ca PF<1,2" là do đo sai | Thêm `pf_lenh`, `so_lenh_gio`, `tb_lenh_pct` (gộp đoạn phơi nhiễm cùng dấu = 1 lệnh/rổ DCA; phí chiều ra tính vào lệnh) |
| 2 | `nhan/cong.py` `placebo` | Kết luận = **max p của ~6 hạt** (mỗi hạt 99–199 lượt). Max của các ước lượng nhiễu bị lệch lên (p thật 0,02 → báo 0,02–0,155) | Đánh trượt oan ở cổng p | Gộp đếm mọi hạt thành **một p** (vuot+1)/(N+1); giữ `p_max_hat` để tham khảo |
| 3 | Mô hình phí | Không double-count (spread nửa mỗi chiều + trượt 0,25×spread/chiều); swap theo đêm, ×3 thứ Tư: đúng | — | Không sửa (xem §3) |
| 4 | Không thấy lỗi | Sharpe năm hoá theo số bar thật/năm (đúng cho H1/H4); engine dịch 1 bar một lần (template không tự dịch); MDE và FDR **đã không chặn** ở chế độ `loi_nhuan` | — | — |
| 5 | Giới hạn thật | Holdout 40% của chuỗi 2018→: cặp AUD* chỉ 3,4 năm OOS, luật D1 tần suất thấp khó đủ 30 lệnh | 431 ca <30 lệnh | Nới: gộp lệnh nhiều cặp (§2) |
| 6 | `nhan/dich_mq5.py` (EA sinh tự động) | Khung D1 vào lệnh lúc 00:00 (giờ đảo ngày, spread ×3–4, đôi khi "market closed") | MT5 D1 kém hơn Python | Chưa sửa – việc tiếp |

## 2. Cổng: giữ / nới
| Cổng | Quyết định | Lý do |
|---|---|---|
| p ≤ 0,05 (dịch vòng, một phía) | **Giữ**, sửa cách gộp | Chặn nhiễu |
| PF ≥ 1,2 | **Giữ, đo theo lệnh**; báo kèm số ở PF ≥ 1,1 | Đã có p chặn nhiễu |
| Sharpe ≥ 0,3, TB lệnh > 0 | Giữ | Rẻ, hợp lý |
| ≥ 30 lệnh OOS | **Nới**: cho phép gộp lệnh trên các cặp khác với luật đóng băng | Không làm lọt nhiễu vì p gộp vẫn phải ≤ 0,05 |
| Cổng 11 "ăn khe đảo ngày" | **Giữ (bắt buộc)** | 169 ca lãi đến từ báo giá bịa lúc đảo ngày; bỏ cổng này số pass nhảy lên 88 nhưng là giả |
| MDE, FDR | Không chặn (đã vậy) | FDR chỉ tham khảo |
| Walk-forward cuộn | Chưa làm (tốn CPU) | — |

## 3. Phí thật (XM Ultra Low demo, `E:\mt5_tester\p5`, đo 15/11/2026)
Spread bar = trung vị trường spread nến H1 ~6.000 bar; tick = trung vị bid/ask 3 ngày. Hoa hồng 0. Mô hình = spread + 2×trượt (khứ hồi).
| Cặp | Bar med / p90 | Tick med | Mô hình khứ hồi | Swap thật L/S (%/năm phí) | Mô hình swap | Kết luận |
|---|---|---|---|---|---|---|
| AUDCAD | 2,4 / 2,7 | 2,9 | 3,84 | −0,83 / 3,83 | −0,60 / 3,71 | cao hơn ~30% |
| AUDNZD | 2,7 / 2,8 | 3,3 | 4,19 | −0,05 / 4,46 | 0,08 / 3,10 | cao hơn ~27% |
| EURCAD | 1,8 / 2,4 | 2,6 | 2,89 | 1,49 / 1,45 | 1,43 / 1,57 | ≈ (+11%) |
| EURGBP | 1,8 / 2,0 | 2,0 | 1,63 | 2,52 / −0,48 | 2,62 / −0,45 | **thấp hơn** 18% |
| AUDCHF | 1,5 / 1,8 | 2,0 | 2,40 | −3,52 / 6,54 | −2,87 / 6,00 | cao hơn ~20% |
| EURUSD# | 1,0 / 1,1 | 1,1 | 1,09 | 2,54 / −0,47 | 2,48 / −0,45 | ≈ |
| CADJPY# | 2,7 / 3,1 | 3,2 | (không có chuỗi) | phí 0,52 / 3,7 | — | — |
| US100Cash# | 1,95 / 1,95 điểm | 1,95 | (không có chuỗi) | mode 3 | — | — |
Giờ 0 (đảo ngày) spread 4–8 pip ở mọi cặp; các giờ khác phẳng. Cặp `#` trên tài khoản này có `swap_mode=0` (tắt swap) – nếu tài khoản thật cùng loại thì swap FX ≈ 0.
**Kết luận phí:** mô hình không thổi phồng đáng kể (lệch 10–30% do giả định trượt, EURGBP còn thấp hơn thật). Chạy lại với phí đo thật: R1 (spread tick, trượt 0, swap XM) 54→56 pass; R2 (swap 0) 54→61. Nhóm "phí ăn hết lãi" (217 ca sau cổng 11): R1 cứu 21, R2 cứu 40. **Phí không phải thủ phạm chính, và là phí thật.**

## 4. Kết quả trước / sau (1.067 ca sau cổng 11)
| Bộ tiêu chí | Pass |
|---|---|
| Cũ (PF bar, p max-hạt) | 18 |
| Chỉ sửa p | 26 |
| Chỉ sửa PF | 35 |
| **Sửa cả hai** | **54** |
| + PF ≥ 1,1 | 59 |
| + phí thật R1 / R2 | 56 / 61 |
Phân bố p (OOS từng cặp): p≤0,01: 34 ca (may rủi ~11); p≤0,002: 10 (may rủi ~2). → **Có edge thật trong rổ**, nhưng 54 pass vẫn lẫn khoảng một nửa may rủi; cần bằng chứng độc lập.

**Kiểm độc lập – luật đóng băng trên 11 cặp KHÁC (không tính cặp gốc), gộp lệnh, p gộp:**
| Luật | Cặp dương | Lệnh | PF lệnh | p gộp |
|---|---|---|---|---|
| AUDCAD H4 `mua_ibs_thap_kl_mong_khi_rsi_duoi_phan_vi_thap_atr_vua` | 10/11 | 967 | 1,24 | 0,001 |
| EURUSD H4 `mat_can_bang_lenh_dong_cua` (20–22h) | 10/11 | 1.003 | 1,24 | 0,001 |
| AUDNZD H1 `mua_khoi_luong_can_kiet_sau_cu_giam_manh_khi_gia_tren_ema200` | 8/11 | 534 | 1,31 | 0,002 |
| EURGBP D1 `ns_keltner20_<_q5_giu1` | 8/11 | 521 | 1,23 | 0,025 |
| GBPCAD D1 `mua_hai_bar_ibs_thap_lien_tiep_kl_mong_tren_sma200` | 7/11 | 385 | 1,20 | 0,044 |
(PF≥1,1: thêm 4 luật – xem `chuyen_cap_ket_qua.json`.)

**MT5 Strategy Tester** (XM Ultra Low demo, Model=1, 0,1 lot, vốn 10.000, EA sinh tự động `dich_mq5` → `tools/kiem_dinh/evo/mt5/`):
| Luật | Giai đoạn | Lệnh MT5 / Python | PF MT5 / Python | Lãi | DD |
|---|---|---|---|---|---|
| AUDCAD H4 IBS | 2023-05→2026-11 | 39 / 31 | 1,68 / 5,18 | +1,18% | 0,87% |
| EURUSD H4 MOC | 2016-01→2026-11 | 150 / 148 | 1,24 / 1,65 | +2,05% | 2,31% |
| AUDNZD H1 | 2023-05→2026-11 | 53 / 44 | 1,03 / 1,96 | +0,09% | 0,83% |
| EURGBP D1 Keltner | 2015→2026-11 | 95 / 46 | 0,85 / 3,38 | −2,64% | 4,0% |
| GBPCAD D1 IBS×2 | 2019-12→2026-11 | 36 / 34 | 0,67 / 2,79 | −3,33% | 6,7% |

**Tự kiểm 2 ứng viên còn sống:** vào lệnh theo luật (không replay); OOS thật cho cặp gốc + kiểm trên cặp khác; %/năm trung thực rất nhỏ ở 1× (AUDCAD IBS ~1,3%/năm, phơi nhiễm 1,5%; EURUSD MOC ~0,6–1%/năm) – muốn 10%/năm phải nhân lot, DD nhân theo; lot cố định, không lỗi lot; tập trung: top 10% lệnh = 36% (AUDCAD), dương 4/4 năm. Python lạc quan hơn MT5 rõ (PF 5,2 → 1,7). **Chưa pass**: holdout đã bị nhìn nhiều lần; cần forward demo sau 02/10/2026.

## 5. Tồn 164 `CHO_KIEM_TICK_MT5`
158/164 có trong DB (6 mã cũ đã đổi tên, không chấm lại). 129 template khác nhau. Dưới chuẩn đã sửa: **35 pass 5 tiêu chí**, 72 ít lệnh (<30), 51 dương nhưng p/PF/Sharpe yếu. 3 trong 35 qua cả kiểm gộp cặp khác (AUDCAD H4 IBS, AUDNZD H1, GBPCAD D1).

## 6. Khung thời gian (cùng luật, sau phí, ≥10 lệnh)
| Khung | Lãi gộp TB/lệnh | Phí TB/lệnh | Phí / lãi gộp (trung vị) | Ca dương sau phí |
|---|---|---|---|---|
| H1 | 0,014% | 0,030% | 1,26 | 33% |
| H4 | 0,025% | 0,030% | 0,66 | 47% |
| D1 | 0,040% | 0,025% | 0,24 | 51% |
Không có dữ liệu M15 trong DB; báo cáo cũ `AUDCAD_KHUNG_THAP.md`: M15 thua H4 (placebo danh mục p=0,49). → **H1/H4 không "cao" quá; H1 đã quá nhỏ với spread FX, H4/D1 mới đúng.** Lưu ý D1 trên MT5 phải tránh vào lệnh lúc 00:00.
