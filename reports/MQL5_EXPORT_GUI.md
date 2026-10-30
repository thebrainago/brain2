# MQL5 / Myfxbook — export lịch sử (Playwright tự động)

Session browser user đã login MQL5 được **cấp phép dùng** (t15u/t25u). Không trích cookie/token; không API riêng.

## Tự động (máy nhà)

```
E:\brain2_grok\venv\Scripts\python.exe -u tools\tai_lich_su_trinh_duyet.py --toi-da 100 --nghi 5
```

Nightly `Brain2_QuetTinHieuDem` (02:00 Asia/Bangkok) → `E:\brain2_grok_tin_hieu\chay_quet_dem.ps1` → `--mql5-pw` → parse → dual-track `dich_boc` (thuong + dca_go_lenh) → `hang_cho_tin_hieu.jsonl`.

| Mục | Đường dẫn |
|-----|-----------|
| Profile bền | `E:\brain2_grok_tin_hieu\pw_profile` (copy Chrome Profile đã vào mql5/myfxbook) |
| CSV MQL5 | `E:\brain2_grok_tin_hieu\data\mql5_csv\<signal_id>.csv` |
| CSV Myfxbook | `E:\brain2_grok_tin_hieu\data\myfxbook_csv\` |
| Temp | `E:\brain2_grok_tin_hieu\tmp\` (xoá sau chạy) |

Lịch sự ≥5s; tối đa ~100 signal/đêm; age≥12 tháng; CPU BelowNormal; không đụng mt5_slots.

## Nút UI MQL5

Trang signal → tab **Trading History** (`#tab_history`) → **Export to CSV: History**.

## Trạng thái E2E (2026-10-30, Asia/Bangkok)

### MQL5 — **BLOCKED (0 history CSV)**

1. Profile `pw_profile` có Cookies nhưng **không phải session community đã login** (Export ẩn / need-auth).
2. Home IP: HTTP **403** trên `https://www.mql5.com/en` và `/en/auth_login` → không thể login mới từ máy nhà. Trang signal công khai đôi khi vẫn 200.
3. **MT5 Terminal**: chỉ có `bases/signals/signals.dat` (catalog) — **không** có trade-history CSV để đọc thay thế.
4. **Thiếu để mở khoá**: session MQL5 đã login trong Chrome thường (login từ mạng khác/VPN), rồi `--force-profile` / `--resync-cookies` khi Chrome tắt; hoặc egress khác không 403 auth.

### Myfxbook — **BLOCKED by reCAPTCHA (0 CSV)**

Browser + `--host-resolver-rules` vượt DNS/TLS/Cloudflare; mở được trang system và `#csvStatement` trong menu Filter→Export. Click mở `#captchaModal` / grecaptcha trước `getCSVFile()` — **không bypass captcha**. Tự động hoá đầy đủ không lấy được CSV.

### FXBlue

Vẫn chạy trong nightly (không cần Playwright login).

## Fallback / vận hành

```
# Sync profile khi Chrome đã tắt (Cookies không khoá)
python -u tools\tai_lich_su_trinh_duyet.py --chi-dong-bo-profile --force-profile
python -u tools\tai_lich_su_trinh_duyet.py --resync-cookies
python -u tools\tai_lich_su_trinh_duyet.py --kiem-tra-mt5
```
