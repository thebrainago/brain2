# Backtest MT5 v24 (RSI/MRZ trailing D1) — BACKTEST MT5, KHÔNG PHẢI TIỀN THẬT
Máy nhà, XM Global MT5 build 6231, server XMGlobal-MT5 10, tài khoản demo nhóm "Standard/Cash Ultra Low" (hậu tố `#`), 13/10/2026.
Model=1 (OHLC M1), deposit 10.000 USD, lot 0,01 (chỉ số: vol_min 0,1), 4 terminal song song (mặc định + C:\MT5slots\s1..s3 /portable).
EA đã sửa (commit e87e1905): thử lại lệnh vào/đóng khi bị [Market closed] lúc 00:00.
- `tong_hop.json`: số liệu từng báo cáo (net, số lệnh, PF, DD, bps TB/lệnh, deal đầu).
- `python_theo_ma.json`: ea_logic_v24 trên dữ liệu Yahoo cùng giai đoạn (phí cũ `cu` và phí XM thật `xm`).
Hạn chế: chỉ số/dầu/vàng trước ~2016 XM không có M1 (quality 4–12%), tick sinh ra lúc 00:00 rơi vào giờ đóng cửa → 0 lệnh;
US500/UK100/GER40 2016–2026 0 lệnh (agent: "cannot generate history data" — bộ nhớ đệm tick 11–21 GB); GOLD 2016–2026 cả 2 EA treo agent, không có báo cáo.
