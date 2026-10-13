# DIEU PHOI MAY NHA + BOX SONG SONG (vong 27, 13/10/2026)

Muc dich: may nha (DESKTOP-05PNLGF, 10 nhan/20 luong, RAM 32 GB 1 kenh) va box cloud chay CUNG LUC, khong de len nhau, khong lam phien
chu du an khi choi game. Ma: `mt5tools/dieu_phoi_song_song.py` (chon muc) + `mt5tools/chay_mt5_slot.ps1` (hang doi MT5 theo slot).
Nen tang dieu toc: the-brain `qwen/dieu_toc.py` (cua khoi dong chung, tran CPU 90%, RAM/commit toi thieu) va `qwen/dieu_toc_lan.py` (AIMD giu CPU muc tieu).

## 4 muc
| Muc | Khi nao (tu do) | CPU ca may | MT5 song song | Tab cao | Python | Uu tien |
|---|---|---|---|---|---|---|
| MAX | khong game, CPU nguoi dung < 15% | 90% | 4 | 3 | 8 | BelowNormal |
| CAO | CPU nguoi dung 15-40% | 75% | 3 | 2 | 6 | BelowNormal |
| VUA | CPU nguoi dung >= 40% | 50% | 2 | 1 | 3 | Idle |
| THAP | game dang chay (Valorant/LoL/CS2...) hoac cua so truoc toan man hinh | 15% | 0 | 0 | 1 | Idle |
`python mt5tools/dieu_phoi_song_song.py [MAX|CAO|VUA|THAP]` in JSON {muc, do, cau_hinh, phan_viec}; tham so = ep muc. RiotClient mo san KHONG tinh la choi game.
Do lai moi 60 s; ha muc ngay khi phat hien game (dung phong MT5 moi; viec MT5 dang chay giu Idle cho xong, khong giet giua chung).

## Chia viec
- **May nha**: MT5 tester (chi tk DEMO), cao nguon bi chan tren box / can dang nhap (trinh duyet that, chi DOC), xuat tick/gia XM.
- **Box**: phan tich Python (mo phong, doc bao cao `.htm`, so khop EA <-> Python), cao nguon cong khai, commit/push.
- Ket qua may nha -> repo: `reports/mt5_v27/`, `reports/seeker_may_nha/`. Box doc va so sanh.

## Luat o dia (bat buoc)
- Terminal MT5 portable: `D:\mt5_tester\p1,p2`, `E:\mt5_tester\p3,p4`. Tester/Agent/bases lich su KHONG BAO GIO o C:.
  `%APPDATA%\MetaQuotes\Tester\<id>` la junction sang `D:\MT5cache\Tester_AppData\<id>`.
- Chua co RAM disk (khong cai ImDisk/AIM - can chu du an dong y cai phan mem ngoai Python). Khi co: dat `R:\mt5_tester` cho slot nong.
- Cuoi ca: xoa `p*\Tester\Agent-*`, `p*\bases\*\history`, `p*\bases\*\ticks`; ghi dung luong da xoa.

## Hang doi MT5 (`chay_mt5_slot.ps1 -Slot <thu muc> -Jobs "MA#|set|tu|den|nhan;..."`)
- Mot tien trinh PowerShell cho MOT slot; moi job = mot terminal `/portable /config:ini` voi `ShutdownTerminal=1`.
- **Dung nhanh (fail-fast)**: job ket thuc < 90 s ma khong co bao cao -> xoa het hang doi, ghi `FAIL-FAST`. (13/10 18:39: slot moi thieu
  `config\accounts.dat` -> "tester not started because the account is not specified" -> terminal mo/dong 6 lan lien tiep, chu du an thay nhap nhay.)
- Han: khong phong job moi sau 22:10, giet slot luc 22:35.
- Slot moi: chep `config\accounts.dat` + `common.ini` cua terminal goc VA `MQL5\Profiles\Tester\*.set` (robocopy /XD Tester bo qua ca Profiles\Tester!).

## Quet lai nguon dinh ky
Moi ca may nha (1 lan/ngay): chay lai quet DOC-ONLY (`reports/seeker_may_nha/`), so voi lan truoc theo URL, ghi muc moi vao HANG_CHO_MAY_NHA.
Theo doi (follow) nguon tren tk thebrainago: chu du an da cho phep 13/10, nhung may nha CHUA co ho so Chrome 9224 da dang nhap (xem HANG_CHO #22).
