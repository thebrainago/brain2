# Tăng tốc MT5 trên máy nhà (21/10/2026)

Máy nhà: 10 nhân / 20 luồng, khoảng 32 GB RAM một kênh, mỗi metatester real tick khoảng 6 GB, 5 slot XM portable (p1, p7, p3, p6, p4), mỗi slot chạy một việc đơn (Optimization=0, Model real tick, ShutdownTerminal=1). Mọi tính năng mới **mặc định TẮT** và chỉ bật bằng biến môi trường. Code: `mt5tools/tang_toc.py`, nối vào `chay_lien_tuc.py` và `sinh_viec.py`; test ở `test_tang_toc.py`. Không slot nào được là terminal XM giao dịch (`C:\Program Files\XM Global MT5`): cả code lẫn script đều từ chối.

## 1. Các cờ

| Cờ | Tác dụng | Tham số (mặc định) |
|---|---|---|
| `BRAIN_GEN=1` | Việc **tối ưu di truyền** vòng 2 (`pha=V2_GEN`): Optimization=2, Model=1 (OHLC M1), tiêu chí `OptimizationCriterion=4` (Recovery Factor = lãi / DD tiền). Đọc XML → chọn **tâm cao nguyên** (median Recovery của các điểm lân cận ±1 nấc, không lấy đỉnh lẻ; DD ≤ 85 %, lãi > 0) → top N việc kiểm real tick (`V2_GEN_KIEM`) | `BRAIN_GEN_TOP` (3), `BRAIN_GEN_AGENT_MAX` (16) |
| `BRAIN_CONG_MOI=1` | Cổng tầng 1 (OHLC M1) mới: qua khi **lãi kép ≥ 8 %/năm và DD ≤ 85 %** (thay cho net ≥ 0, DD ≤ 95 %). Mỗi việc real tick xong được ghép với bản tầng 1 cùng khoá → `reports/mt5_lien_tuc/lech_ohlc_tick.jsonl` | `BRAIN_CONG_LAI_MIN` (8), `BRAIN_CONG_DD_MAX` (85) |
| `BRAIN_RAM_DONG=1` | Phóng việc theo RAM **đo được**: cần RAM trống ≥ nhu cầu + dự trữ. Số việc real tick tối đa = ⌊(RAM tổng − 6) / 6⌋. RAM trống < ½ dự trữ → giết việc **mới nhất của mình**, ghi `het_ram` (CHƯA ĐO ĐƯỢC, chạy lại sau) | `BRAIN_RAM_TICK_GB` (6), `BRAIN_RAM_OHLC_GB` (1,5 / agent), `BRAIN_RAM_DU_TRU_GB` (4), `BRAIN_RAM_HE_THONG_GB` (6) |
| `BRAIN_TICK_CHUNG=1` | Kho tick chung + **khoá theo symbol**: symbol chưa “ấm” (chưa có lần real tick nào xong) thì chỉ một slot được chạy real tick symbol đó, slot khác chờ hoặc lấy việc khác. Xong việc → `da_co\<symbol>.txt`; khoá chết > 3 giờ được đổi tên `.lock.cu` (không xoá) | `BRAIN_KHO_TICK` (`E:\mt5_tick_chung`) |

Việc `V2_GEN` chỉ được lấy khi có cả `BRAIN_VONG2=1` và `BRAIN_GEN=1`. Muốn sinh việc: `python mt5tools\tang_toc.py sinh-gen --top 10`. Lệnh này thêm `V2_GEN` cho 10 việc `V2_CAO_NGUYEN` tốt nhất trong `reports/vong2/hang_cho_vong2.jsonl`. Khoảng tối ưu là ±50 % quanh tâm cao nguyên của vòng 2, 9 nấc cho số thực; `InpMaxTang` là số nguyên, bước 1.

Tiện ích: `python mt5tools\tang_toc.py ram` in RAM tổng/trống, số agent và số việc real tick tối đa; `python mt5tools\tang_toc.py hieu-chinh-cong` gợi ý ngưỡng cổng từ các cặp OHLC/tick đã đo (cần ≥ 10 cặp).

## 2. Kho tick chung (làm một lần, khi slot KHÔNG chạy)

1. `TAT_THE_BRAIN.bat` rồi đợi các slot xong việc.
2. Với từng slot: `powershell -File mt5tools\dung_chung_tick.ps1 -Slot D:\mt5_tester\p1 -Thu` (chạy thử, chỉ đếm), rồi bỏ `-Thu` để chạy thật.
   - Script từ chối nếu slot là terminal XM giao dịch, không có `terminal64.exe`, hoặc đang có `terminal64` / `metatester64` chạy từ thư mục đó.
   - File được **chuyển** (không xoá) vào `E:\mt5_tick_chung\bases`. File trùng thì bản cũ sang `E:\mt5_tick_chung\_trung\<slot>\`. Thư mục cũ đổi tên `bases_cu_<thời gian>`, sau đó tạo junction `Tester\bases → E:\mt5_tick_chung\bases`.
   - Slot p1/p7 đã có junction con (do `chuyen_tick_sang_E.ps1` tạo): file trong đó cũng được chuyển vào kho chung.
3. Đặt `BRAIN_TICK_CHUNG=1` trước khi chạy `chay_lien_tuc`.

Lưu ý: kho chung nằm trên HDD E nên đọc tick có thể chậm hơn SSD. Tốc độ thật **CHƯA ĐO ĐƯỢC**.

## 3. Bật trên máy nhà (khi rảnh, theo thứ tự)

```bat
cd /d C:\Users\DUNG\brain2 && git pull
set BRAIN_RAM_DONG=1
set BRAIN_CONG_MOI=1
python mt5tools\tang_toc.py ram
python mt5tools\chay_lien_tuc.py --den 07:00
```

Sau một đêm chạy ổn: thêm `set BRAIN_TICK_CHUNG=1` (sau khi làm mục 2). Tiếp đó: `set BRAIN_VONG2=1`, `set BRAIN_GEN=1`, `python mt5tools\tang_toc.py sinh-gen --top 5`. Tắt một tính năng bằng cách bỏ cờ (hoặc đặt `=0`) rồi chạy lại.

## 4. Tốc độ kỳ vọng (ƯỚC TÍNH, chưa đo trên máy nhà)

- **OHLC M1 so với real tick:** thường nhanh hơn khoảng 5–20 lần và tốn khoảng 1–2 GB RAM thay vì khoảng 6 GB (ước tính). Nếu khoảng 70 % hệ trượt cổng tầng 1, thời gian real tick giảm khoảng 3 lần (MÔ PHỎNG).
- **Di truyền:** lưới 4–6 tham số × 9 nấc (khoảng 10⁴–10⁵ tổ hợp) thường hội tụ sau khoảng 1–3 nghìn pass. Mỗi pass OHLC trên nhiều agent song song, nên một việc tối ưu cỡ vài chục phút đến vài giờ (ước tính).
- **Kho tick chung:** mỗi symbol chỉ tải và lưu một lần thay vì 5 lần, đỡ khoảng 4/5 dung lượng tick và thời gian tải lần đầu (ước tính).
- **RAM động:** với 32 GB, tối đa 4 việc real tick (32 − 6 = 26, chia 6), hoặc nhiều việc OHLC hơn. Số thực tế phụ thuộc RAM trống lúc chạy.

## 5. Cần đo trên máy nhà

1. RAM thật của một agent OHLC M1 và của metatester real tick theo từng symbol (đặt lại `BRAIN_RAM_OHLC_GB` / `BRAIN_RAM_TICK_GB`).
2. **Giới hạn số agent:** ini `[Tester]` không có khoá số agent. MT5 tạo agent theo số luồng CPU (20). Code đã ước tính `so_agent` và chặn bằng RAM (giết việc khi RAM cạn), nhưng giới hạn thật cần đặt tay trong *Strategy Tester → Agents* của slot tối ưu (tắt bớt agent local). **CHƯA ĐO ĐƯỢC**.
3. Tỉ lệ thời gian OHLC/real tick và độ lệch lãi/DD (file `lech_ohlc_tick.jsonl`), sau đó chạy `hieu-chinh-cong` để chỉnh `BRAIN_CONG_*`.
4. Tốc độ đọc tick từ kho chung trên E so với SSD, và việc khoá có làm slot ngồi chờ lâu không (log `CHO KHOA TICK`).
5. Tiêu chí tối ưu: `OnTester()` của `BRAIN_XuLiLenh` hiện trả *số tầng sâu nhất*, nên không dùng Custom (6). Nếu muốn đúng “số dư / DD equity” thì sửa `OnTester` (cần biên dịch lại trên máy nhà) và đặt `tieu_chi=6`.
