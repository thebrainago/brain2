# SP500: setup "quét về ONH rồi mua", KHÔNG SL, chờ giá quay lại / DCA — lần thử đầu trên H1 (16/10/2026)

**MÔ PHỎNG xấp xỉ trên nến H1 của XM `US500Cash`, 2016 → 10/2026. Không phải tiền thật, không phải MT5, chưa thấy được cú quét ở mức phút.** Claude làm để có mốc cho Grok làm lại ở M1.
Chạy lại: `python mau_thu/onh_h1.py` (~50 giây, có giới hạn 30 ngày) và `python mau_thu/onh_dca.py` (~10 giây, chờ không giới hạn + DCA).

## Giả định (tất cả sửa được trong script)

- **ONH** = đỉnh phiên đêm, từ 18:00 giờ New York hôm trước đến 09:00 NY. Dự án SP500 phase 1 đã tách khỏi git (18/09) nên không có định nghĩa ONH nào trong repo — đây là định nghĩa thông dụng (Globex mở 18:00 NY), **chủ dự án cần xác nhận giờ**.
- **Giờ**: dữ liệu H1 theo giờ server XM = EET/EEST (đo lại bằng khối lượng: 3–4 tuần mỗi năm lúc Mỹ/châu Âu đổi giờ lệch nhau, mở cửa phiên Mỹ rơi vào 15:30 server thay vì 16:30). Script đổi sang giờ New York thật. *Chú thích "giờ server NY+7" trong `nhan/moc_nam_cham.py` sai ở những tuần đó.*
- **Setup (bản hiểu)**: sau 09:00 NY có một nến H1 **đóng trên ONH** ("mở phiên tăng"); sau đó một nến chạm ONH (`low ≤ ONH`) → BUY limit tại ONH, trong phiên Mỹ (đến 16:00 NY).
- **Thoát**: chạm TP (% giá vào). **Không SL.** Bản `onh_dca.py` chờ đến cùng; bản `onh_h1.py` đóng theo giá thị trường sau 30 ngày.
- **Chi phí**: spread 1 bps (≈ 0,77 điểm — GIẢ ĐỊNH; đo Ultra Low ~0,6 điểm, bản Standard ước cao hơn); swap mua XM `US500Cash` đo 13/09/2026 = −1,21 USD/lot/đêm = 5,77 %/năm ≈ 1,58 bps mỗi đêm (≈ 1,2 điểm), thứ Sáu ×3. Swap cố định 5,77 % cho cả 10 năm → các năm lãi suất thấp (2016–2021) bị tính **hơi nặng**.
- 1 bps ≈ 0,77 điểm ở giá 7.650. **Nếu 1 điểm = 1 USD ở lot của chủ dự án** (chưa xác nhận) thì TP 0,07 % ≈ 5,4 điểm ≈ 5,4 USD.

## Kết quả chính (852 setup; ~80 lệnh/năm)

**Chờ đến cùng, 1 lệnh, TP 0,07 % (~5,4 điểm):**

| | ONH-retest | Mua đại lúc 09:00 NY mỗi ngày (2.681 ngày) |
|---|---|---|
| Lệnh cuối cùng chạm TP | 100 % (852/852) | 100 % (1 lệnh còn mở đến hết dữ liệu) |
| Chạm TP ngay trong phiên (bản 30 ngày) | 74 % | 81 % |
| Chạm TP trong 5 ngày | 94 % | 93 % |
| Giữ lâu nhất | **704 ngày** (vào 13/01/2022) | 483 ngày |
| Lỗ treo (tính trên 1 đơn vị) trung vị / p99 / **tệ nhất** | ~0,2 % / 7,9 % / **30,9 %** (vào 26/02/2020) | – / 9,3 % / 34,9 % |
| Lãi/lệnh trước swap | **+6,0 bps** | +6,0 bps |
| Lãi/lệnh sau spread + swap | **+1,1 bps** | +1,8 bps |

- Gần như mọi lệnh đều "về bờ" vì chỉ số Mỹ luôn hồi lại (đúng như chủ dự án nói). **Cái quyết định lãi hay lỗ là vài lệnh kẹt rất lâu**, và swap 1,2 điểm mỗi đêm ăn dần lãi: một lệnh giữ qua 5 đêm mất ~6 điểm — bằng cả TP.
- Theo năm (sau swap, bps/lệnh): 2016 +1,9 · 2017 +3,1 · 2018 +1,0 · 2019 +4,7 · 2020 +3,1 · 2021 +3,9 · **2022 −20,9** (lệnh kẹt 704 ngày, lỗ treo 26 %) · 2023 +3,9 · 2024 +3,1 · 2025 +3,6 · 2026 +3,6.
- **ONH-retest KHÔNG hơn mua đại lúc 09:00 NY** ở độ phân giải H1. Đây không kết luận về setup thật của chủ dự án (vào bằng quan sát nến phút) — chỉ nói: phần "ONH + quét" chưa thấy lợi thế khi nhìn nến giờ; lãi hiện có chủ yếu từ "chỉ số Mỹ hồi lại + TP nhỏ".

**TP 0,25 % (~19 điểm), 1 lệnh, chờ đến cùng:** +13,4 bps/lệnh sau swap (+24,0 nếu không tính swap), lỗ treo tệ nhất vẫn 30,9 %; mua đại 09:00 NY: +13,9 bps.

**DCA (thêm 1 đơn vị mỗi −0,5 % hoặc −1 %, tối đa 3 lần thêm; TP tính trên giá trung bình):**
- Thời gian chờ ngắn hơn rõ (p99: 9,6 ngày thay vì 42,7) nhưng **vốn bị phình tới 4 đơn vị**: lỗ treo tệ nhất 99–120 % giá trị của MỘT đơn vị.
- ONH-retest + DCA 0,5 %: −4,0 bps/lệnh sau swap (vẫn do đợt 2022); mua đại + DCA 0,5 %: +3,0 bps.

## Điều chưa biết / chưa làm (việc cho Grok, xem `CHI_THI_CHU_DU_AN.md`)

1. Làm lại ở **M1** (HistData SPXUSD trên máy Grok): xác định đúng cú quét, giờ vào thật, thứ tự TP/lỗ trong nến.
2. Swap theo từng năm (lãi suất thật + markup XM) thay vì 5,77 % cố định; thử Standard thật khi có số.
3. Thang tiền thật của chủ dự án: 1 điểm = ? USD, lot, margin. Báo "cần bao nhiêu vốn để ngồi qua −30 % mà không bị stop-out".
4. Biến thể DCA khác (bước theo ATR, đảo chiều, hedge, nhồi theo xu hướng) và các mốc khác (ONL, PDH/PDL, giá mở phiên Âu/Á).
5. Tách theo chế độ (tăng/giảm), ngày trong tuần, VIX thấp/cao.
6. Dữ liệu H1 chỉ từ 2016 (trước đó chỉ có nến ngày).
