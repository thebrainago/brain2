# Máy nhà: thẻ python_llm cần xếp lại sau lỗi `_ma_rieng` (kiểm 20/10/2026 21:33, giờ VN)

Nguồn: chụp CHỈ ĐỌC `C:\Users\DUNG\brain2\data\ong_dan\trang_thai.sqlite` (21:12) trên DESKTOP-05PNLGF; HEAD máy nhà lúc đó `b8323c07` (CHƯA có sửa `_ma_rieng`, commit d53de259).

Lỗi: `mau_thu` hiểu mã Python ở `tin_hieu["ma"]` là danh sách symbol → 0 phép thử → `CHUA_DO_DUOC`. Máy nhà có cùng lỗi.

- Thẻ python_llm trên máy nhà: 172
- **Đã dính lỗi (ở `loc` CHUA_DO_DUOC, 0 phép thử) → cần đưa về `quyet_dinh`: 12**
- Đang chờ ở `quyet_dinh` (PYTHON_LLM): 157 → sau `git pull` (có sửa) sẽ chạy đúng, không cần làm gì
- Đã qua MT5 (doc_mt5): 3

Phiên sau, trên máy nhà sau `git pull`:

```python
from nhan import ong_dan as OD; import sqlite3
cn = sqlite3.connect('data/ong_dan/trang_thai.sqlite')
IDS = ["sk_ea_04e16f1791", "sk_ea_128806cd4b", "sk_ea_16500cb0bc", "sk_ea_2cdf157388", "sk_ea_319a2b3752", "sk_ea_33ba5e554f", "sk_ea_37d1b8143e", "sk_ea_37d63eef37", "sk_ea_3d2d636ccf", "sk_ea_3db47be494", "sk_ea_401e6ca5da", "sk_ea_4435af40a6"]
for t, b, tt, kq in OD.cac_the(cn):
    if t['id'] in IDS and tt == 'CHUA_DO_DUOC':
        with cn: cn.execute('DELETE FROM thu WHERE the_id=?', (t['id'],)); OD._luu(cn, t, 'quyet_dinh', 'PYTHON_LLM')
```

| Thẻ | Bước | Trạng thái | Số phép thử |
|---|---|---|---|
| `sk_ea_04e16f1791` | loc | CHUA_DO_DUOC | 0 |
| `sk_ea_128806cd4b` | loc | CHUA_DO_DUOC | 0 |
| `sk_ea_16500cb0bc` | loc | CHUA_DO_DUOC | 0 |
| `sk_ea_2cdf157388` | loc | CHUA_DO_DUOC | 0 |
| `sk_ea_319a2b3752` | loc | CHUA_DO_DUOC | 0 |
| `sk_ea_33ba5e554f` | loc | CHUA_DO_DUOC | 0 |
| `sk_ea_37d1b8143e` | loc | CHUA_DO_DUOC | 0 |
| `sk_ea_37d63eef37` | loc | CHUA_DO_DUOC | 0 |
| `sk_ea_3d2d636ccf` | loc | CHUA_DO_DUOC | 0 |
| `sk_ea_3db47be494` | loc | CHUA_DO_DUOC | 0 |
| `sk_ea_401e6ca5da` | loc | CHUA_DO_DUOC | 0 |
| `sk_ea_4435af40a6` | loc | CHUA_DO_DUOC | 0 |
