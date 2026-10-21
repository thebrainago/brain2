# Dịch tay đợt 3 (grokbot-tay) — 21/10/2026 (giờ Sài Gòn, UTC+7)

Grok Bot đọc mã MQL và tự viết `tin_hieu(df)` + `quan_tri` (định dạng `cau_llm.MAU_BOC`), ghi bằng `tho_box/dich_tay.py ghi`
(model `grokbot-tay`). **Không gọi ai-box / LLM trả phí**: 0 lần gọi API, 0 token; `dich_llm` cấu hình vẫn false.
Ưu tiên EA lưới / DCA / martingale / hedge / recovery (xếp theo số từ khoá trong mã). Bản dịch: `data/tho_box/dich_tay/<bam>.json`
(data/ không vào git), mã sinh: `data/tho_box/dich_tay_grok/viet.py`.

## Kết quả đo

| Bước | Số |
|---|---|
| Mã nguồn đã dịch | 19 (= 20 thẻ; MintyGrid có 2 thẻ) |
| Kiểm tĩnh + kiểm chạy (≥3 lệnh AUDCAD H1) | 20/20 DAT |
| Lọc Python 65/15 sau phí (lot thật) | **6 DAT_LOC / 14 TRUOT_LOC** |
| Bỏ, không dịch (không ra tín hiệu): lưới 2 chiều vô điều kiện / tiện ích | T15GridT1, 204060_program, HedgeCoverV1_04, PippoV18 (Murrey) |

Thẻ đạt lọc (tốt nhất của tối ưu Python, CHƯA kiểm MT5):

| Thẻ | EA | Mã/khung | Lãi %/năm | DD % |
|---|---|---|---|---|
| sk_ea_2f4540d68a | GridScalperEA (BB lưới hồi quy) | AUDUSD H1 | 86.9 | 45.1 |
| sk_ea_3d5da5b65e | Sniper Gold Hybrid Recovery | XAUUSD H4 | 33.6 | 63.7 |
| sk_ea_9345f47763 | MakeGrid193 (EMA34+MACD) | EURUSD H1 | 24.8 | 50.5 |
| sk_ea_b18d784179 | Zerith XAU SwingGrid Recovery | GBPUSD H1 | 19.0 | 20.0 |
| sk_ea_31b7c0180f | Zerith MACD Martingale Grid | GBPUSD H4 | 18.1 | 55.7 |
| sk_ea_8760277bca | MintyGrid 7.2 (RSI 30/70) | GBPJPY H4 | 15.4 | 43.5 |

## So sánh tỉ lệ qua lọc (CSDL box `tho_box.sqlite`, thẻ dịch DAT → có kết quả lọc)

| Người dịch | Thẻ dịch DAT | DAT_LOC | Tỉ lệ |
|---|---|---|---|
| qwen3.7-max (ai-box) | 144 | 39 | 27% |
| grokbot-tay đợt 1-2 | 79 | 22 | 28% |
| grokbot-tay đợt 3 (này) | 20 | 6 | 30% |

## Kiểm thử
- pytest đầy đủ trên box: 94 failed / 2884 passed / 49 skipped (20 phút). Các file hỏng chạy lại trên worktree sạch HEAD (data/ symlink) cũng hỏng y hệt (29 failed trong 8 file mẫu) → hỏng sẵn do môi trường box (thiếu tệp, module), không do đợt này (đợt này chỉ đổi báo cáo). test_phan_viec / test_dich_mq5 / test_bien_dich_ung_vien / test_ong_dan: 68 passed.

## Vướng
- `tho_box.sinh_viec_box` (sinh việc MT5) lỗi `ValueError: luoi` trong `ong_dan.tin_hieu` (thẻ có `tin_hieu.kieu = luoi`) →
  chưa sinh việc MT5 mới cho box lần này; 4 thẻ đã sang `sinh_mt5 CHO_EA_GHEP`, 2 thẻ còn ở `loc DAT_LOC`.
