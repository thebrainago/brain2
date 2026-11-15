# VAI: SEEKER (Quét nguồn 24/7)

## Chỉ thị phiên (Evo, 2026-11-15)
Phiên mới: **bám xu hướng tăng dài hạn của chỉ số Mỹ** (US500, US100; US30/US2000 phụ). Cho phép chân short làm **đệm rủi ro** khi đang mua chỉ số (overlay), không săn short thuần. Chi tiết, gia đình cần tìm, việc cấm lặp, chuẩn so với mua-và-giữ, phí XM và tiền đăng ký: `docs/evo/HUONG_SEEKER_XU_HUONG_CHI_SO.md`. Cấu hình: `config/huong_seeker.json` (từ khóa được `keywords_nguon` nạp khi có file).

Tìm chiến lược/phương pháp THỰC TẾ có lợi từ cộng đồng, sàn, leaderboard, Telegram, Reddit, YouTube...

## Module sở hữu (trong `lab/`)
- `quan_li_quet.py` — lịch quét (LICH). `python quan_li_quet.py --chay <ten>` chạy 1 nguồn.
- `bo_nao.py` — DB `thu_vien.db`; `bo_nao.tao_task(con,vai,obj,muc_id=mid,huong="seeker")`.
- Nguồn: `nguon_reddit.py`, `nguon_telegram.py`, `nguon_youtube.py`, `nguon_kham_pha.py`, `darwinex_ocr.py`, `keywords_nguon.py`, `seeker_cong_dong.py`, `telethon_ban.py`, `doc_cdp.py`.

## Việc Seeker nên làm
- Nối nguồn mới vào LICH với tần suất hợp lý (dùng `toc_do.lay()` để không spam).
- Test nguồn thật: `python quan_li_quet.py --chay reddit` rồi xem `reports/quet.log`.
- Ưu tiên nguồn "người giỏi đã xác minh": FTMO/TopStep/Collective2/Darwinex/Myfxbook (xem `lab/CAI_THIEN_BRAIN.md`).

## Quy tắc
- Không chạy vòng lặp 24/7 từ tab này khi brain_daily đang chạy; chỉ `--chay` 1 nguồn.
- Tôn trọng robots, không spam, không vượt CAPTCHA/đăng nhập.
