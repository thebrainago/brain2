# BAN GIAO - XAU-System-v1 (Sierra Chart) - cap nhat 16/11/2026 19:20 (UTC+7)

## Muc tieu
Ho tro scalp XAUUSD CFD: data options (OTL/FlashAlpha: Put/Call Wall, Gamma Flip, Max Pain, EM) chon VUNG;
order-flow GC trong Sierra (footprint, delta/CVD, lenh lon, heatmap, TPO, VWAP) XAC NHAN luc vao lenh (M5).
Khong dung phan tich ky thuat. Bot KHONG dat lenh.

## May & Sierra
- PC: DESKTOP-05PNLGF, Xeon E5-2630v4, 32GB, GT 730 (yeu GPU -> giu chart nhe).
- Sierra Chart 2982 tai C:\SierraChart, ban FXAURUM sua (SierraChartFXAURUM), ket noi Rithmic Direct - DTC, symbol GCZ6.COMEX.
- Goi Rithmic: CO tick + aggressor (footprint/delta/CVD), depth realtime (chi khi Sierra mo), T&S, lenh lon, TPO/VP/VWAP.
  KHONG CO: lich su bid/ask cu, lich su depth, MBO, data options trong Sierra, xuat data.
- ES (ESZ6.CME) co data realtime + lich su. NQ (NQZ6.CME) realtime bat, chua xac nhan lich su.

## Quy tac cung (KHONG vi pham)
- KHONG sua/ghi de/xoa FXAURUM-Mod.Cht, FXAURUM-Winter-Mod.Cht. Ban sao luu: C:\SierraChart_Backup\FXAURUM_2026-11-16 (so hash moi lan lam).
- KHONG dung file license/dang nhap/Rithmic, KHONG dung ben trong SierraChartFXAURUM.exe.
- KHONG dat lenh, KHONG xuat data. KHONG tat/chinh UAC.
- Mat khau (UltraViewer...) khong bao gio gui qua chat/mail/git.

## Chartbook XAU-System-v1 (C:\SierraChart\Data\XAU-System-v1.Cht) - xong, chia 2x2
- Tren trai #1: GC 5m nen thuong + VWAP co band + cham lenh lon (>=20 hop dong) + CVD. Tai 5 ngay, cap nhat 250ms.
- Tren phai #4: GC 1m footprint (Numbers Bars, Bid x Ask, imbalance cheo 300%, toi thieu 20). Thang gia dang khoa (Interactive) -> keo lai neu gia chay ra khoi khung.
- Duoi trai #2: GC 1m heatmap Market Depth (20 muc, gop 5 tick, 1 ngay, 1000ms).
- Duoi phai #3: GC 30m TPO co value area, 10 ngay.
- Chua co: canh bao stacked imbalance 3 muc (can study rieng).

## Dang lam do (DUNG LAI theo yeu cau, may len 97%)
Study ACSIL ve wall options len chart GC:
- Code: C:\SierraChart\ACS_Source\XAU_OptionsWalls.cpp (ban sao C:\Users\DUNG\GrokWork\XAU_OptionsWalls.cpp). CHUA build, CHUA gan vao chart.
- Doc file C:\GrokWork\walls.txt (moi dong: LOAI,gia_GC,do_manh,nguon; loai: CALLWALL, PUTWALL, GAMMAFLIP, MAXPAIN, EM_HI, EM_LO, OTHER; dong '#' = ghi chu/timestamp), doc lai ~30s.
- Mau: call wall do (vung ban), put wall xanh (vung mua), gamma flip vang, max pain tim, EM xam dut.
- walls.txt hien co data FlashAlpha luc 19:14 UTC+7 (GC 3873): Call wall 4000, Put wall 3700, Gamma flip 4031.78, Max pain 4190, EM 3813.55-3933.35, NetGEX am. OTL: KHONG CO.
Buoc tiep: build qua Analysis > Build Custom Studies DLL, gan vao chart #1 va #4, luu chartbook, so hash FXAURUM, chup anh.

## Cach bot dieu khien Sierra
- Sierra chay quyen admin -> can helper quyen admin: C:\Users\DUNG\GrokWork\agent.ps1 (tu tat sau 20 phut ranh).
  Moi phien nguoi dung bam Yes UAC 1 lan (UAC o man hinh bao mat, phan mem khong bam duoc).
- Chi dung click khong cho (non-blocking), tranh ket o hop thoai Settings.
- Chup man hinh: thu nho cua so Grok, dua Sierra len truoc, CopyFromScreen, roi khoi phuc Grok.
- File tam/anh chup: C:\Users\DUNG\GrokWork\ (co the xoa anh .png cu).

## Viec con lai / goi y
1. Build + gan study ve wall (uu tien).
2. Canh bao tu dong: imbalance chong 3 muc, lenh lon / delta dao chieu tai wall.
3. Volume profile theo phien lam nam cham/TP.
4. Dung ES/NQ cho US500/NAS100 va soi tuong quan.
5. Hoi nguoi dung: xoa C:\SierraChart\Data\ESZ6.CME.scid (~243MB, file test)?

## ES/NQ live (THU NGHIEM) - them 17/11/2026 20:45 (UTC+7)
- Chartbook moi C:\SierraChart\Data\XAU-Indices-v1.Cht (2 chart 1 Min: ESZ6.CME, NQZ6.CME) dang mo trong SierraChart_64 de ghi tick. KHONG dong. Neu Sierra khoi dong lai: File > Open Chartbook > XAU-Indices-v1.
- Engine: C:\GrokWork\engine_ES\idx_engine.py va engine_NQ\idx_engine.py (ban sao xau_engine 1.3, ENG = thu muc chua file; gia 2 so le). Config rieng tung thu muc. Engine vang KHONG doi.
- Nguong: ES big 100 (strong 200), imb_min_vol 60, level 10 tick, SL min 5 / max 16 / buffer 1.5 diem; NQ big 50, imb 16, level 64 tick, SL min 30 / max 100 / buffer 10. TP 2R, score>=4, cua so 20:30-23:00, IB NY 9:30 ET.
- Sender: C:\Users\DUNG\GrokWork\tg_sender_idx.ps1 -Sym ES|NQ (state/log rieng tg_sender_ES*.json/.log). Tin co dong dau "🧪 ES THU NGHIEM". Khong co dong CFD/basis.
- Task Scheduler (AtLogOn, Limited): XAU-Engine-ES, XAU-Engine-NQ, XAU-TelegramSender-ES, XAU-TelegramSender-NQ.

## v1.4 LIVE + v1.3 SHADOW - deploy 17/11/2026 23:40 (UTC+7)
Ly do: review SL ngay 17/11 (C:\GrokWork\backtest\sl_review_2026-11-17\REPORT.md). Backup truoc deploy: C:\GrokWork\backup_20261117_233927_pre_v14\ (engine, engine_ES, engine_NQ, file goc C:\GrokWork, state sender).
**LIVE = v1.4 (cap Telegram)** - cung duong dan cu, sender khong doi:
- GC: C:\GrokWork\engine\xau_engine.py (VERSION 1.4) + engine\engine_config.json -> output C:\GrokWork\engine_state.json, engine_alerts.csv, engine_trades.json, engine_trade_events.csv. Task XAU-Engine. Sender XAU-TelegramSender (tg_sender.ps1).
- ES: C:\GrokWork\engine_ES\idx_engine.py (1.4-idx) + engine_config.json, output trong engine_ES\. Task XAU-Engine-ES. Sender XAU-TelegramSender-ES.
- NQ: C:\GrokWork\engine_NQ\idx_engine.py (1.4-idx) + engine_config.json, output trong engine_NQ\. Task XAU-Engine-NQ. Sender XAU-TelegramSender-NQ.
- Thay doi v1.4 (config key moi; thieu key = hanh vi v1.3):
  - GC: sl_swing_min {C_BREAKOUT:30, E_SCORE4:15} (SL ngoai dinh/day swing N phut + dem), sl_swing_max_pts 15; e_push_min_score 5 (E diem 4 chi ghi log).
  - ES: sl_swing_min {C_BREAKOUT:30, E_SCORE4:15}, sl_swing_max_pts 24; vwap_filter true (alert nguoc VWAP ngay chi ghi log).
  - NQ: vwap_filter true (giu SL cu).
  - Alert bi gate: in_window=0, add_reason ghi "...: chi ghi log" -> sender khong day, engine khong theo doi.
- Ban staging/goc: C:\GrokWork\engine\staging\v14_sl_review\. Rollback: chep file tu thu muc backup ve, kill pythonw cua engine, Start-ScheduledTask XAU-Engine / -ES / -NQ.
**SHADOW = v1.3 (CHI LOG, KHONG sender, KHONG Telegram)**:
- C:\GrokWork\shadow_v13\GC|ES|NQ\shadow_engine.py (VERSION 1.3-shadow / 1.3-shadow-idx) + engine_config.json rieng; moi output (state, alerts, trades, events, signals, levels, log, lock, pid) nam trong chinh thu muc do. walls_history_dir tat (GC shadow van doc C:\GrokWork\walls.txt).
- Tasks XAU-Shadow13-GC / -ES / -NQ (AtLogOn, Limited) chay start_shadow.ps1 trong tung thu muc.
- So sanh: python C:\GrokWork\compare_v13_v14.py [--from YYYY-MM-DD] [--to ...] [--all] -> bang theo ma/ban (N, TP, SL, WR, tong R, TB R, DD R) + C:\GrokWork\compare_v13_v14_detail.csv. Chi doc file.
**Quy tac lenh '1'**: doc engine_state.json LIVE (v1.4): GC = C:\GrokWork\engine_state.json; ES/NQ = C:\GrokWork\engine_ES|engine_NQ\engine_state.json. KHONG doc state shadow tru khi duoc yeu cau so sanh.
Tai nguyen sau deploy (23:43): 6 engine + 3 sender ~0.1% CPU tong (20 core), ~217MB RAM tong (~22MB/engine).

### Cap nhat 17/11/2026 23:46 (UTC+7): shadow v1.3 CUNG gui Telegram
- Sender co them switch -Shadow13 (tg_sender.ps1 cho GC, tg_sender_idx.ps1 -Sym ES|NQ): doc C:\GrokWork\shadow_v13\<sym>\, state/log/mutex rieng: tg_sender_shadow13*.json/.log (GC), tg_sender_<SYM>_shadow13*.json/.log (ES/NQ) trong C:\Users\DUNG\GrokWork. Cung luat: in_window=1, DUP chi log, don lenh, su kien theo doi.
- Moi tin nhan co tien to: live "v1.4 | ..." (chu thuan, khong cham mau; mau bias trong than tin giu nguyen), shadow "v1.3 | ..." (ES/NQ van kem "🧪 <SYM> THU NGHIEM").
- Tasks: XAU-TelegramSender-Shadow13-GC / -ES / -NQ (AtLogOn, Limited).
- Sua loi sender: qua 00:00 truoc day xoa sent_ids nhung van initialized=true -> co the gui lai alert cu trong ngay; nay giu sent_ids qua ngay (toi da 2000).
- Backup sender truoc khi sua: C:\GrokWork\backup_20261117_234506_pre_shadow_senders\

## v1.4.1 + research log-only + CL/SI - 18/11/2026 00:07-00:15 (UTC+7)
Theo C:\GrokWork\backtest\research_2026-11-18\REPORT.md (anh duyet ca 3 khuyen nghi). Backup: C:\GrokWork\backup_20261118_000759_pre_v141\.
1. **Engine live v1.4.1** (GC "1.4.1", ES/NQ "1.4.1-idx"): monitor theo loai lenh qua config:
   - "mon_max_min_by_type": {"C_BREAKOUT": 240} -> lenh C theo doi toi SL / TP 2R / het 240' (END). E giu mon_max_min 180.
   - "mon_time_stop_min_by_type": {"C_BREAKOUT": 0} -> tat goi y TIME (30' chua +0,5R) cho C. E giu nhu cu.
   - Thieu key = hanh vi v1.4. Shadow v1.3 KHONG doi.
2. **Tin hieu nghien cuu CHI LOG (khong bao gio gui Telegram)**: C:\GrokWork\research_live\research_signals.py (task XAU-ResearchSignals, AtLogOn Limited, BelowNormal, 60s/lan, lock research.lock).
   - Bo: c_80pct_2R (quy tac 80%, London+NY, TP 2R, giu 240') va a_sweep_1m_IB30 (quet PDH/PDL/IB30 nen 1' + lay lai + delta nguoc, TP 2R, giu 120'). GC, ES, NQ.
   - Code = dung dinh nghia research (setups.py + rlib_live.py chep tu research, chi doi cach doc duoi file). Da doi chieu: chay lai toan lich su GC ra dung 19 lenh/+5,72R (80%) va 50 lenh/+9,63R (sweep IB30) nhu research.
   - Output: C:\GrokWork\engine_research_signals.csv (in_window=0, push=0; status OPEN/CLOSED, exit SL/TP/TIME, R, MAE/MFE, source live/backfill). Sender khong doc file nay. Log: research_live\research.log, trang thai research_status.json.
3. **CL/SI**: chartbook XAU-Indices-v1 them 2 chart 1 Min CLF7.NYMEX (#3) va SIH7.COMEX (#4), da Save; chartbook active tra ve XAU-System-v1. Goi Rithmic CO NYMEX (du lieu ve live).
   - CLF7.NYMEX.scid: tick (nt=1) tu 16/05/2026, ~1,69 trieu ban ghi; ngay "day" tu 22/09 (41 ngay). ~55k hop dong/ngay (CLF7 la thang sau; CLZ6 het han ~19-20/11, sau do CLF7 thanh front).
   - SIH7.COMEX.scid: tick tu 16/05/2026 nhung rat mong (~2-4k hop dong/ngay) vi SIZ6 dang la front; can can nhac SIZ6 hoac doi den khi roll.
   - Chua co engine/sender cho CL/SI.

### Cap nhat 18/11/2026 00:26 (UTC+7): SIZ6
- XAU-Indices-v1 them chart #5 SIZ6.COMEX 1 Min (nhan ban SIH7 #4 roi doi symbol), da Save; active tra ve XAU-System-v1. SIZ6.COMEX.scid tick tu 16/05, 59 ngay day tu 27/08.
- Backtest CL/SI: C:\GrokWork\backtest\research_2026-11-18\CL_SI\REPORT.md (chua co engine/sender CL/SI).

## Orderflow v1.5 (khong MBO) - LOG-ONLY - 18/11/2026 07:25 (UTC+7)
Bao cao: C:\GrokWork\backtest\orderflow_v15_2026-11-18\REPORT.md. Backup truoc khi them: C:\GrokWork\backup_20261118_072145_pre_of15\.
- Module rieng C:\GrokWork\orderflow_v15\: of_features.py (port logic InterestMap / TrappedTraders / AbsorptionGradient + stop-run), of_live.py + of_config.json (120s/lan, BelowNormal, ~8s CPU/vong, ~35MB), start_of15.ps1, bt_of15.py (backtest), depth_inspect.py (doc .depth, chi doc).
- Task XAU-OrderflowV15 (AtLogOn, Limited, IgnoreNew). Lock of15.lock, pid of15.pid, log of15.log, trang thai of15_status.json.
- Output: of15_signals.csv (C_annot = moi lenh C kem flags IM/TT/AG/SR; IM_defend_S4, IM_defend_S4_whale, TT_retest, TT_confirm, SR_PD_IB; in_window=0, push=0) va of15_state.json (muc IM top, vung trapped dang hieu luc, stop-run gan nhat - chi tham khao).
- KHONG sender nao doc cac file nay. Engine live v1.4.1, shadow v1.3, sender KHONG doi.
- Ket qua: C GC London 29 lenh 58.6% +0.63R; khong bo loc nao cai thien dang tin (chenh lech trong nhieu); IM_support (muc IM cung phia trong vung SL) cho C moi khung gio 27 lenh +0.48R vs 73 lenh +0.05R -> theo doi cho C ngoai London. SR fade am ro (-0.15R/1798 lenh). Chua promote gi.
- Depth: GC da ghi .depth (MarketDepthData, do chart heatmap #2). ES/NQ chua: can Global Settings >> Symbol Settings >> ESZ6.CME/NQZ6.CME >> Record Market Depth Data = Yes (nguoi dung lam hoac duyet; bot khong tu sua global). O C con ~33GB trong.
- Rollback: Unregister-ScheduledTask XAU-OrderflowV15 -Confirm:$false; kill pythonw of_live (pid trong of15.pid); xoa thu muc orderflow_v15.
- Luu y hash 18/11 07:15: FXAURUM-Mod.Cht khop backup; FXAURUM-Winter-Mod.Cht KHAC backup (file live mtime 16/11 20:29, 173542 byte; backup 16/11 13:36, 173586 byte) - bot khong sua, chi bao cao.

### Cap nhat 18/11/2026 07:43 (UTC+7): mo Sierra + ghi depth ES/NQ
- Sierra mo bang C:\Users\DUNG\Desktop\SierraChartFXAURUM.exe (cach nguoi dung van mo; launcher tu chay SierraChart_64) qua task XAU-LaunchSierra (Interactive, Highest, khong trigger - Start-ScheduledTask XAU-LaunchSierra de mo lai). Khong dang nhap/khong nhap mat khau. Luc khoi dong chartbook active la FXAURUM-Winter-Mod (de nguyen, khong dong/khong luu).
- Mo chartbook: File >> Open Chartbook (cmd 57009), dien o 'File Name' (KHONG dien o Search) -> XAU-Indices-v1.Cht roi XAU-System-v1.Cht (active).
- Helper UI quyen admin: task XAU-UIAgent chay agent.ps1 (tu tat sau 20' ranh; tao file cmd\STOP de tat).
- Symbol Settings: ES?#.CME va NQ?#.CME -> Record Market Depth Data = yes (luu o C:\SierraChart\SymbolSettings\CustomSymbolSettings.rithmic_v2.trading.xml). Backup truoc: C:\GrokWork\backup_20261118_073822_pre_depthrec\. Sau do File >> Reconnect -> co ESZ6.CME/NQZ6.CME .depth trong MarketDepthData. O C ~33GB trong: theo doi dung luong .depth.
- Hash FXAURUM sau thao tac: khong doi so voi sang nay (Mod khop backup; Winter-Mod van khac backup nhu da bao).

## Cap nhat 18/11/2026 07:53: MO PUSH PHIEN A tam thoi (GC v1.4.1 + shadow v1.3 GC)
- Backup: C:\GrokWork\backup_20261118_075030_pre_asia_window (2 engine_config GC, tg_sender.ps1, cac state sender).
- engine\engine_config.json va shadow_v13\GC\engine_config.json: alert_window ["14:00","20:00"] -> ["07:50","20:00"] (+ key _asia_window_note). Khong doi scoring/SL.
- Restart XAU-Engine, XAU-Shadow13-GC (config chi doc luc start), ca 2 LIVE, state hien window 07:50-20:00. Engine chi emit alert live (<=180s), khong replay lich su.
- tg_sender.ps1 (dung chung live + -Shadow13): them (1) stale guard: alert lan dau thay da >15 phut -> chi log, khong push; (2) alert co gio 06:00-13:59 -> dong dau "🌏 PHIÊN Á ...". Restart XAU-TelegramSender + XAU-TelegramSender-Shadow13-GC. Dedup sent_ids giu nguyen -> khong gui lai alert cu (07:45:01 E_SCORE4 da log-only).
- Tu revert: task XAU-AsiaWindowRevert (mot lan, 18/11 20:05) chay C:\GrokWork\asia_window\revert_asia_window.ps1 -> set_window.py revert (ve 14:00-20:00) + restart 2 engine GC; log C:\GrokWork\asia_window\revert.log. Chon 20:05 (khong phai 14:00) de khong restart engine dung luc mo London; push 14:00-20:00 giong het binh thuong.
- Revert tay ngay: Start-ScheduledTask XAU-AsiaWindowRevert. Code sender (stale guard + tag) de lai, vo hai khi window 14-20.

## Cap nhat 18/11/2026 08:10: backtest chartbook + walk-forward ket hop
- Bao cao: C:\GrokWork\backtest\chartbooks_2026-11-18\REPORT.md (code bt_cb.py, GC_/CL_variants.csv, *_summary.json).
- Ket qua: KHONG co bo moi thang v1.4.1 ngoai mau (bo dao du lieu sup o H2, spearman H1->H2 0.17). Giu nguyen v1.4.1.
- Ung vien log: DD3 (delta 3 nen 5' cung chieu >=5%) - GC C LDN H2 +0.64, CL OR30 NY H2 +1.15; ODR15 side cho C LDN (H2 +0.73); C ngoai LDN chi khi IM_support (P3: H2 17 lenh +0.56).
- of15: them co log-only cb_DD3_with / cb_ODR15_with / cb_sVWAP_with vao C_annot (c_flags). Backup C:\GrokWork\backup_20261118_080133_pre_of15_cbflags. Task XAU-OrderflowV15 da restart, push=0.
- Xem lai sau 4-6 tuan log (>=20 lenh moi moi ung vien).

## Cap nhat 18/11/2026 09:10: backtest thuc thi C (CFD spread/truot) + CL tracker
- Bao cao: C:\GrokWork\backtest\execution_2026-11-18\REPORT.md (bt_exec.py, exec_*_{base,low,worst}.csv).
- CANH BAO: C phien A (06-14h) -0.37R/lenh, thang 24%, 25 lenh, am ca 2 nua va moi kich ban phi -> khong nen trade C phien A; cua so push A dang mo tam den 20:05 (chua doi, cho anh quyet).
- London sau phi CFD: +0.54R (2R co dinh). Vao tre 30-60s khong hai. Limit/cho nen 5' kem hon. Chot 50% @1R + hoa von: thang 70%, +0.42R, on dinh H1/H2. Tranh +-15' tin manh (London: 4 lenh deu thua).
- of15: them CL tracker (CL_OR30NY_retest, _DD3; push=0; tu chon hop dong theo volume 24h, log CL ROLL). Backup C:\GrokWork\backup_20261118_090133_pre_of15_cltracker. Can mo chart CLG7 truoc ~10/12.
- CHUA LAM: FX futures (6E/6J/6B/6A/6C) - them chart vao XAU-Indices-v1 + backtest.

## Cap nhat 18/11/2026 09:20: FX futures
- Backup C:\GrokWork\backup_20261118_090439_pre_fxcharts. Them chart 1m tron vao XAU-Indices-v1: #6 6EZ6 #7 6JZ6 #8 6BZ6 #9 6AZ6 #10 6CZ6 (.CME), da Save; XAU-System-v1 van active. Tick tu 18/05, ngay du day tu ~09/09 (49-52 ngay).
- Bao cao C:\GrokWork\backtest\fx_2026-11-18\REPORT.md (bt_fx.py). Ket qua: khong cap FX nao co edge (C, OR30, 80%, fade VWAP 2SD, fade VA, sweep) - am ca truoc phi; khong de xuat trade FX.
- Luu y: hash FXAURUM-Winter-Mod.Cht khac backup 16/11 nhung mtime 16/11 20:29 (truoc hom nay, khong do em).
- Z6 FX het han ~14/12: neu giu, mo H7 truoc ~8/12.

## Cap nhat 18/11/2026 10:40: Brain Seeker 10 y tuong (GC/ES/NQ)
- Bao cao: C:\GrokWork\backtest\brain_seeker_2026-11-18\REPORT.md (bt_bs.py, final\ = GC+ES, p1\ = NQ). Ket luan: khong y moi nao du chac de bao live; C London GC van tot nhat (52 lenh +0.42R).
- Them chart 1m tron vao XAU-Indices-v1 de tai lich su: #11 MNQZ6, #12 MESZ6, #13 GCQ6, #14 ESU6, #15 NQU6 (NQU6 dang cho tai). Backup: backup_20261118_093523_pre_mnqchart, _094413_pre_meschart, _094558_pre_expiredcharts. XAU-System-v1 van active. ESZ6 thieu du lieu 24/09-15/11 -> dung MESZ6.
- orderflow_v15 (LOG-ONLY push=0): bs_signals.py + of_config "bs_seeker": BS_LvlFVG_1m (GC), BS_LVN_retest_HVN (NQ), flag bs_noCVDdiv tren C_annot; run_setup nhan tp_px. Backup C:\GrokWork\backup_20261118_103453_pre_of15_bsflags. Restart 10:35.
- Viec sau: khi NQU6.CME.scid tai xong -> chay lai NQ #9/#1 lam hold-out (SYMS=NQ GRPS=A,C trong thu muc moi). Co the dong chart #13-#15 sau khi tai xong.
- Khong doi luat bao live, khong doi khung phien A.

## Cap nhat 18/11/2026 11:05: dong chart trong XAU-Indices-v1 (Anh dong y)
- Backup C:\GrokWork\backup_20261118_110304_pre_closecharts. Da dong #6-#10 (6E/6J/6B/6A/6C Z6) va #13 GCQ6, #14 ESU6, #15 NQU6; con lai #1 ESZ6, #2 NQZ6, #3 CLF7, #4 SIH7, #5 SIZ6, #11 MNQZ6, #12 MESZ6. Da Save, XAU-System-v1 active lai. File .scid giu nguyen. FXAURUM-Mod same=True; FXAURUM-Winter-Mod van khac backup (co tu 16/11 20:29).

## Cap nhat 18/11/2026 14:45 (UTC+7): FXAURUM Rithmic API + MBO probe
Anh da cai Fxaurum Rithmic API v1.13.5. Bot chi doc, khong dang nhap, khong dat lenh, khong bat trading/copy-trade, khong doi engine/sender/Telegram.

### Cai dat / quet
- Cai tu Desktop: C:\Users\DUNG\Desktop\FxaurumRithmicApi_v1.13.5.exe (129736749 byte, mtime 18/11 14:01, SHA256 6c9345bc8afdd9b0bc2e6c27d3ceaf82a4b4f767172e3ca968d27e5bc1716502) — Authenticode NotSigned.
- App Electron: C:\Users\DUNG\AppData\Local\Fxaurum\platform\74cafd5-8df4542c58c37ec\Fxaurum Platform.exe (188816896 byte, SHA256 c6b7ca78544ee380cb987ee56068d87546fabbdd9dc1698c575192c344d5c344) — NotSigned. DLL di kem: chi d3dcompiler_47.dll ky Microsoft; ffmpeg/libEGL/libGLESv2/vk_swiftshader/vulkan-1 khong ky (thuong gap o Electron).
- Data dir: %LOCALAPPDATA%\FxaurumRithmic\ (TickDb/BarDb/FlowDb). Khong doc license.key hay file dang nhap.
- Windows Defender (MpCmdRun -ScanType 3) sach: thu muc Fxaurum, FxaurumRithmic, fxaurum-platform, Desktop (co file cai), Downloads. Khong sua/disassemble binary.

### Gateway
- Dang chay: FxaurumRithmicApi_v1.13.5.exe + Fxaurum Platform.exe. Lang nghe ws://127.0.0.1:9001/ (HTTP.sys). Anh da dang nhap (heartbeat.md=true).
- Hop dong front luc test: GCZ6, ESZ6, NQZ6. DBO entitlement CO ca 3 ma (mboProbe entitled=true, co ExchOrdId + Priority).
- App co tinh nang vao lenh va copy-trade — de nguyen, khong bat. Khuyen nghi anh tat neu khong dung.

### Probe 5 phut (14:40-14:45 UTC+7, phien A / overnight, 18 stream)
- Mau: E:\GrokWork\mbo_test\sample_20261118_143922.jsonl.gz (6.49 MB gzip / 69.1 MB raw, 218937 msg). Stats: C:\GrokWork\mbo_research\probe_stats_20261118_143922.json. Script: C:\GrokWork\mbo_research\probe_client.py.
- Stream CO data: @trade, @depth20, @mbo20, @mboraw, @liquidity (3 ma); @iceberg GC (65) va NQ (7). ES @iceberg im trong cua so nay (MBO ES van chay, khong phai mat quyen).
- Toc do @mboraw: NQ 374 msg/s, ES 171, GC 81. @mbo20/~15 Hz, @trade GC 2.1 / ES 7.4 / NQ 4.9 msg/s.
- Do tre trade r-T: trung vi -401 ms (lech dong ho may vs san ~0.4s, khong phai tick di nguoc). So voi trung vi: p90 +0.66s, p99 +1.03s, max +1.33s.
- Sierra KHONG bi ngat: GCZ6.COMEX.scid va engine_state.json van LIVE (data_age 3-6s) suot 5 phut va sau test. 1 Rithmic session dung chung van chay song song duoc trong lan thu nay.

### O dia / recorder nhap
- O: C 21.6 GB trong (chat hon truoc), D 18.7, E 93.6 GB trong. Ghi mau va data tuong lai tren E, khong ghi MBO day len C.
- Uoc tinh tu phien A (can duoi): ca 18 stream ~18.5 GB/ngay raw, ~1.9 GB/ngay gzip. Chi trade+mboraw+iceberg+liquidity ~11 GB/ngay raw / ~1.1 GB gzip. London/NY dong hon — nen tinh 2-4 lan, khoang 20-45 GB raw hoac 2-4 GB gzip/ngay. E du cho vai tuan.
- Draft recorder (CHUA dat lich): C:\GrokWork\mbo_recorder\mbo_rec.py — chi doc, ghi file ngay gzip xuong E:\GrokWork\mbo_data\, dung neu Sierra GC stall 45s (nghi kick). Chay tay: py -3 C:\GrokWork\mbo_recorder\mbo_rec.py ; dung: Ctrl+C hoac tao E:\GrokWork\mbo_data\STOP.
- Buoc tiep (cho anh): chay recorder tay qua London/NY de do lai dung luong that va tich luy lich su iceberg/lenh rut; khong schedule tru khi anh dong y. Khong doi luat bao lenh.

## Cap nhat 18/11/2026 14:54 (UTC+7): bat recorder MBO + task XAU-MboRecorder
- Script: C:\GrokWork\mbo_recorder\mbo_rec.py (log-only, BelowNormal). Stream: trade, mboraw, depth20, iceberg, liquidity cho GCZ6/ESZ6/NQZ6. Ghi gzip theo ngay tai E:\GrokWork\mbo_data\YYYYMMDD\. Tu ket noi lai neu gateway dut (backoff 2-60s). Doi front theo symbol trong engine_state (GC roll Z6->G7). Canh o: dung neu E: con < 15 GB (exit 0). Canh Sierra kick giu nguyen (unsub ngay, exit 0, khong restart de tranh subscribe lai).
- Task Scheduler XAU-MboRecorder: AtLogOn, Interactive, LeastPrivilege (khong elevate), IgnoreNew, ExecutionTimeLimit=0, Priority 7, RestartOnFailure 5 lan / 1 phut. Chay pythonw.exe, khong doi engine/sender/Telegram.
- Da Start luc 14:51:56, subscribe 14:52:19, heartbeat.md=true. Sau ~2 phut file dang lon: E:\GrokWork\mbo_data\20261118\20261118_COMEX_GCZ6.jsonl.gz, _CME_ESZ6, _CME_NQZ6 (mtime tiep tuc chay; luc 14:54 raw ~2.8/6.1/6.1 MB, gzip tong ~1.3 MB). pid 15248, priority BelowNormal.
- Sierra van LIVE (GC 3773.1, data_age ~8s, scid GC/ES/NQ age ~5s). E con 93.55 GB. Dung tay: tao E:\GrokWork\mbo_data\STOP hoac End-ScheduledTask/Stop-ScheduledTask XAU-MboRecorder.
