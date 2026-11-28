# STATUS 2026-11-28 14:13 (Asia/Saigon) -- ROUND 6 RUNNING (6a done: scenarios+MT5 joint; 6b newsig5 pairs running)
Round 5 finished: SUMMARY_V3.md section 19 written; synced to E:\GrokWork\bt_v3. No jobs running (box and PC MT5 queues all finished).
Key results: weekend hedge-lock W (EA BRAIN_XuLiLenh_r5) keeps 91-96% net, removes weekend-gap DD; MT5 joint DD: NEW4 +24.1k/8.4%, PortD-G30 +74.9k/15.1%, PortD-G40 +85.4k/17.7%, PortE(G30+g3,g5,u12,u13) +101.3k/13.2%; g4 dropped. New systems g3,g5,u12,u13 MT5-verified.
Files: results/r5/*, r4/joint5.json, code/{engine2,r5lib,p5,opt5,pd5,pf5,pf5b,stress5,g5,pol5,newsig2,newsig3,batnew2,batnew3,mk_v5*}.py, r5ea/BRAIN_XuLiLenh_r5.mq5.
Next (optional round 6): forward-demo plan at half lots; more new-signal families; MT5 gap-day replay.

## ROUND 6 log
- 13:36 newsig4 screen (93 new specs: nPOC, VA80, gap fill/go, NR day, weekend gap, TOD anchors, range expansion, vol climax, whale@extreme, z-window extensions, VWAP trend pullback, NY IB, CVD lead) launched PIDs 42596 (XAU) 42597 (US500) -> results/newsig4_<a>.parquet
- next: scalp2.py (SL/TP pass over newsig1-4 families) -> results/r6/scalp2_<a>.parquet; then cov.py, battery r6, MT5 finalists, combo search.
- 13:45 README_SCENARIOS.md + git branch grok/scenarios-v3 commit 5c842ee (mk_git.sh). COVERAGE.md via code/cov.py.
- 13:55 newsig4 done (XAU 1338/US500 1347 cfgs). batnew4: pass XAU g7=imb30z_fade2.0 (all battery +); US500 u15 fz5z_fade2.0 (plc100), u16 vclimax_fade_3 (95), u17 vclimax_mom_2 (90), u18 fz30z_fade2.0 (90), u19 g2_60z_mom2.0 (90). scalp2 + sc6 (A-picked fixed-price SL/TP, B OOS): XAU xs3 g1_30z_fade2.0 SL13 TP8 H90 (B tB 3.1), xs4 imb15z_fade3.0 SL8 TP10, xs5 basis_rev SL8 TP6, xs6 g3_60z_mom3.0 SL10 TP13, xs7 day_ext_fail SL8 TP18 H30. US500 scalps: none pass.
- 13:58 MT5 queues q_p4v6 (6 jobs) / q_p6v6 (5 jobs) launched on PC (wrappers PIDs 2776 p4, 12700 p6). Results -> results_p4/p6.jsonl names v6_*.
- next: opt6.py combination search (greedy corr-aware + lot opt, A->B / B->A OOS), scenarios.
- 14:10 newsig5 (inverse pullback/IBS + 91 confluence pairs/asset) launched; opt6 (scenarios) running; MT5 v6 queues running
- 14:13 round 6a DONE: MT5 v6 11 jobs, opt6 scenarios, joint6 (MT5), SUMMARY s.20, README updated. PortE DD corrected 14.9%.
