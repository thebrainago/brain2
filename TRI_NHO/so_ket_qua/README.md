# Sổ kết quả chung

- `ket_qua.csv`: mọi kết quả test/backtest của mọi phiên/bot (một dòng một lần đo). Cột: id, he, symbol, timeframe, tu, den, so_nam, nguon, real_tick_pct, net, von, cagr_pct, dd_pct, so_lenh, phi, luc_chay, phien_bot, commit, tep_goc, trang_thai, ghi_chu.
- `trang_thai`: DAT / KHONG_DAT / BI_THAY_THE (trước vá lot 31/10 01:53) / CHUA_DO (thiếu số, không rõ lúc chạy, hoặc chỉ MÔ PHỎNG).
- Gom lại: `python -m nhan.so_ket_qua --thu-hoach`; tổng hợp: `python -m nhan.so_ket_qua --tong-hop`.
- Ghi sau mỗi lần chạy: `from nhan.so_ket_qua import ghi_ket_qua; ghi_ket_qua({...})` (tự khử trùng, tự xét trạng thái).
- Ô trống = CHƯA ĐO ĐƯỢC. Không bao giờ điền số đoán.
