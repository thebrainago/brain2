BOX DONE - PC PENDING - 2026-11-28 22:00 (UTC+7 / Asia/Saigon)

MT5 (p6, 100% real ticks, 2026.06.01–11.27) — số @ 1 lot và quy 100 USD (XM min lot 0,10). Exness cent: KHÔNG CÓ.

- US30 L_z240 NY: MT5 +9.085 / DD 2.455 (8 giỏ, 7W1L, PF 17,02). Python +7.053 / 2.286 — khớp (lãi +29%, DD +7%). Lỗ giỏ lớn nhất −567, ngày tệ nhất 30/10/2026 −567. Tại min lot 0,10: lãi +909 / DD 245 / lỗ giỏ −57. DD 245 > vốn 100 USD → quá đắt, không thêm vào sổ.
- GER40 z15 Á: MT5 +983 / DD 1.110 (21 giỏ, 19W2L, PF 2,07). Python +1.687 / 545 — không khớp (lãi 58%, DD ×2,0). Lỗ giỏ lớn nhất −684, ngày tệ nhất cùng 30/10/2026 −684. Tại min lot 0,10: +98 / DD 111 / lỗ giỏ −68. Quá đắt + MT5 yếu hơn → không thêm vào sổ.
- NZDJPY IBS London: MT5 KHÔNG CÓ. Tester 21988/7672 bắt đầu 21:16:30; runq_fx 1528 chết vì tasklist timeout; fx_watch 22160 không hỏi được PID. Python đã trượt spread ×2. Không thêm.

PID: đã tắt đúng 11396 (runq), 19628 (p6 terminal), 19588 (p6 metatester). Không đụng 13548 / claude / Sierra.

Chỉ số khác (t173u, bước đầu, chưa tải M1 mới vì p6 bận tester): tại min lot, 1 ATR H1 ≈ JP225 0,22 USD (rẻ nhất, nhưng 0 pass thật / 4 pass giả), UK100 3,10 (0 pass), GER40 7,09, US100 10,61, US30 10,71. Ứng viên rẻ chưa có M1: CHN50 (min 0,01), GerMid50 (min 0,01), AUS200, Taiwan, CA60, HK50. Exness cent tất cả: KHÔNG CÓ.

Còn lại:
1) Thu báo cáo NZDJPY (htm) từ E:\mt5_tester\p6 hoặc E:\GrokWork\mt5_runs\reports sang C:\Users\DUNG\v3work\out\mt5\reports, parse, điền §7.
2) Khi p6 rảnh: chạy pc_tools/dl_m1_idx.py, rồi screen/basket/placebo/battery, xếp theo DD USD tại min lot.
3) Chép README + reports vào E:\GrokWork\bt_fx; đẩy git grok/scenarios-v3; dòng đầu ALL DONE chỉ khi xong (1) và đã chép ổ E.

Git: 81f6370 trên grok/scenarios-v3 (không đụng main). E:\GrokWork\bt_fx chưa gồm bản README/MT5 này.
