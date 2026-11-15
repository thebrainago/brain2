# Tiền đăng ký giả thuyết (Evo) — 15/11/2026 12:57 Asia/Saigon

> Đóng băng TRƯỚC khi chạy backtest. Không chỉnh tham số sau khi nhìn kết quả.
> 8 giả thuyết, tham số lấy từ tài liệu đã công bố. N_FDR = 8 (một kiểm định chính / giả thuyết).
> Thị trường xác nhận và kiểm bề rộng (h) được báo cáo riêng, không dùng để “chọn hệ đẹp”.

## Mục tiêu và cửa

- Dữ liệu: chỉ số tiền mặt (và CFD XM khi có) từ 1985 nếu có. **IS: ngày < 2016-01-01. OOS: ≥ 2016-01-01, nhìn một lần.**
- Khớp lệnh: nến tiếp theo (next open), trừ khi luật công bố đòi hỏi khớp gần đóng cửa (e, f-FOMC). Không tối ưu thời điểm vào.
- Phí: spread + swap/financing đo trên tài khoản XM DEMO (p4), Friday triple. Ký hiệu mới phải đo trước khi kết luận OOS.
- Đòn bẩy báo cáo ở 1× (lot = equity / (giá × contract) khi vào, giữ cố định trong lệnh). Không tối ưu lot.
- Cửa OOS (hệ có lệnh rời): ≥ 30 lệnh, lợi nhuận trung bình/lệnh > 0, **PF theo lệnh ≥ 1.20**, Sharpe lịch dương ≥ 0.30, p random-shift (1000, dịch chuỗi vị thế, phí tính lại) ≤ 0.05.
- Cửa OOS (hệ gần như luôn giữ hoặc ít lần vào/ra: e, g): Sharpe lịch ≥ 0.30, p ≤ 0.05, CAGR > 0, PF/lệnh vẫn báo cáo nếu tách được lệnh.
- FDR: Benjamini–Hochberg trên **đúng 8 p-value OOS** của các kiểm định chính dưới đây, α = 0.05. Một giả thuyết “sống sót” khi cửa OOS đạt **và** q_BH ≤ 0.05.
- IS được báo cáo đủ, nhưng **không** dùng để chỉnh luật hay loại giả thuyết trước OOS (các hiệu ứng này đã công bố; IS âm vẫn phải nhìn OOS một lần).

## Tám giả thuyết (tham số đóng băng)

### (a) IBS rổ US100+US500+US30 equal-risk, so với US100 đơn
- Nguồn: IBS = (C−L)/(H−L); ngưỡng 0.20 phổ biến (Connors / thực nghiệm chỉ số). Luật vào/ra đóng băng theo ứng viên đang chạy: **IBS < 0.20 tại đóng cửa, vào mở nến sau; ra khi IBS > 0.80 hoặc sau 4 nến D1.**
- Equal-risk: trọng số nhân = 1/σ_20 (σ nhân quả 20 phiên close-to-close), chuẩn hóa trong các thành viên đang có lệnh; nếu σ chưa đủ thì chia đều. Rổ không đòn bẩy thêm (tổng trọng số = 1).
- **Kiểm định chính:** PnL ngày của rổ 3 chỉ số, OOS. So sánh mô tả với US100 đơn (cùng luật, không tính thêm 1 p cho FDR).
- Câu hỏi của người dùng về US500: US500 đơn đã yếu hơn US100; kiểm định này hỏi rổ equal-risk (có US500) có ổn định hơn US100 đơn hay không — không tối ưu thành phần rổ.

### (b) Turn-of-month (TOM)
- Nguồn: Ariel (1987); Lakonishok & Smidt (1988); McConnell & Xu (2008). Cửa chuẩn: ngày giao dịch cuối tháng (−1) đến hết 3 ngày đầu tháng sau (+1,+2,+3).
- Luật đóng băng: **vào tại mở cửa ngày −1, ra tại mở cửa ngày +4** (giữ hết +3). Long only, 1×.
- **Kiểm định chính:** rổ equal-risk US100+US500+US30, cùng cách tính trọng số như (a). US100/US500 đơn: xác nhận.

### (c) RSI(2) < 10, giá trên SMA200 (Connors)
- Nguồn: Connors & Alvarez, *Short Term Trading Strategies That Work* (2009): mua RSI(2) quá bán, chỉ long khi đóng cửa trên SMA200, bán khi RSI(2) phục hồi.
- Luật đóng băng: **RSI(2) < 10 và đóng cửa > SMA200 (SMA nhân quả, ẩn 199 phiên đầu); vào mở nến sau; ra khi RSI(2) > 70, khớp mở nến sau.** RSI Wilder/standard 2 kỳ. Không SL, không tối ưu ngưỡng 5 vs 10.
- **Kiểm định chính:** US100. Xác nhận: US500.

### (d) Đáy 5 phiên (mean reversion ngắn)
- Nguồn: đảo chiều ngắn hạn Jegadeesh (1990), Lehmann (1990); luật thực hành “buy the 5-day low”.
- Luật đóng băng: **đóng cửa là thấp nhất của 5 đóng cửa vừa xong (kể cả hôm đó); vào mở nến sau; ra tại mở cửa sau đúng 5 phiên.** Không tối ưu N hay số ngày giữ.
- **Kiểm định chính:** US100. Xác nhận: US500.

### (e) Drift qua đêm (long close→open), không giữ trong phiên
- Nguồn: phần lớn phần bù cổ phiếu Mỹ nằm qua đêm (Cooper/Cliff; Lou–Polk–Skouras; Boyarchenko et al., overnight drift).
- Luật đóng băng: **mua tại đóng cửa phiên tiền mặt (giá close; lạc quan nhẹ so với 15:45), bán tại mở cửa phiên sau.** Tính spread mỗi vòng và financing nếu vị thế đi qua giờ rollover XM (~17:00 ET).
- **Kiểm định chính:** US100. Xác nhận: US500.

### (f) Drift trước ngày nghỉ Mỹ và trước FOMC
- Nguồn: lợi nhuận ngày trước lễ (Ariel 1990; Kim & Park); drift trước họp FOMC (Lucca & Moench 2015, khoảng 24 giờ trước giờ công bố, thường 14:00 ET).
- Luật đóng băng, **hợp nhất** hai cửa (một giả thuyết, không tách để tối ưu):
  - Ngày nghỉ: lịch NYSE (New Year, MLK, Presidents, Good Friday, Memorial, Juneteenth từ 2021, Independence, Labor, Thanksgiving, Christmas). **Vào mở cửa phiên giao dịch cuối trước ngày nghỉ, ra mở cửa phiên giao dịch tiếp theo.**
  - FOMC: ngày họp công bố lãi suất (scheduled). **Vào đóng cửa phiên liền trước ngày FOMC, ra đóng cửa ngày FOMC.**
- **Kiểm định chính:** US100. Xác nhận: US500. Lịch FOMC/NYSE đóng băng theo nguồn công bố, không chọn ngày theo kết quả.

### (g) Time-series momentum, lọc SMA 10 tháng (1×)
- Nguồn: Faber (2007) 10-month SMA; Moskowitz–Ooi–Pedersen (2012) TSMOM. Đóng băng **1×**, không tối ưu đòn bẩy.
- Luật: **cuối tháng, đóng cửa tháng so với SMA 10 đóng cửa tháng (gồm tháng đó); nếu trên SMA thì long 1× tháng sau, nếu dưới thì đứng ngoài.** Khớp mở cửa phiên đầu tháng sau. Phí tính khi đổi trạng thái và financing khi đang long.
- **Kiểm định chính:** US100. Xác nhận: US500.

### (h) Bề rộng: cùng luật IBS và TOM trên GER40, JP225, UK100, XAU
- Mục đích: kiểm xem IBS/TOM có lặp lại ngoài chỉ số Mỹ, không phải để quét thêm thị trường rồi chọn cái đẹp.
- Luật: **đúng luật (a) cho IBS và luật (b) cho TOM**, tham số không đổi.
- **Kiểm định chính (một p):** PnL ngày **equal-weight** của IBS trên bốn mã {GER40, JP225, UK100, XAU}. TOM trên cùng bốn mã và từng mã lẻ, cùng các cặp FX nếu đo được phí (EURUSD, AUDCAD), chỉ để mô tả, **không** thêm vào FDR.

## Phí và dữ liệu

- US100/US500/US30: bảng phí đã đo 15/11/2026 (spread median M15, fin ~6.48%/năm).
- GER40, JP225, UK100, XAU: đo spread + swap trên `E:\mt5_tester\p4` DEMO trước khi kết luận OOS. Không dùng `E:\evo_forward`, không p5, không slot live.
- Dữ liệu IS dài: chỉ số tiền mặt (^NDX, ^GSPC, ^DJI, ^GDAXI, ^N225, ^FTSE, vàng). OOS thêm CFD XM khi có lịch sử.

## Việc sẽ làm sau OOS (cũng đóng băng quy trình)

- Hệ sống sót: viết EA chỉ DEMO, compile trên p4, `Expert=EVO\<tên>.ex5`, tester 2016+.
- **Không** gắn vào forward demo đang chạy; báo cáo rồi chờ quyết định.
- Lưu tiền đăng ký + kết quả trên nhánh `evo/gia-thuyet-chon-loc` (không phải main). Rút bài học vào `docs/evo/BAI_HOC_VA_PHI.md` trên `evo/sua-tieu-chi`.

## Số thử nghiệm

N_FDR = 8. Không thêm luật, ngưỡng, hay thị trường vào tập chọn sau khi nhìn OOS.
