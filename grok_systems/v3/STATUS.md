ALL DONE (round 8: vốn 100 USD = 10k cent; README mục 13, SUMMARY mục 23, PDF v2)
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
- 14:22 newsig5 done (XAU 1545/US500 1695 cfg); batnew5 (top10 pairs) + scalp2 n5 running
- 14:27 batnew5: pass XAU gp1 pw_break+emapull, gp2 sw_fade+dz_fade, gp3 dz_fade+imb30z; US500 up1 sw1.8+sw1.5, up2 dz_mom+rnd50, up3 sw1.5+vclimax_fade3. scalp pairs xs8 pd+pw break, xs9 g3_60mom+big3mom, xs10 swfade+big3mom (fixed SL/TP, A-picked). MT5 q_p4v7/q_p6v7 launched (PC PIDs 3412, 20964). opt7 (extended universe) running.
- 15:05 MT5 v7 done (100% real ticks): gp1 .06 +9,237/8.5% (rerun; first run 0 trades glitch), gp2 .06 +7,479/11.4%, gp3 .05 +5,677/10.6%, up1 2.0 +4,245/7.4%, up2 2.0 +2,921/6.4%, up3 1.0 +1,604/8.9%, xs8 .3 +10,437/6.1%, xs9 .3 +11,815/11.0%, xs10 .3 +10,140/6.9%. All match Python. Running joint7.
- 15:07 joint7 done; docs updated; ALL DONE
- 15:14 start opt8: recompute scenarios at 100k joint; Gold-only and US500-only at 100k and 50k; W on; reuse U6.pkl + MT5 deals (linear).
- 15:31 opt8/joint8 done. Joint 100k: Safe +96,123/3.7%, Bal +161,631/6.8%, Agg +304,204/11.0% (×1.7 +517,672/18.7%). Gold-only 100k Agg trimmed to +208,221/19.3%. US500-only 100k Agg +167,946/18.8%. Docs updated.
- 15:49 PDF tóm tắt 6 trang: /workspace/bt_3m/v3/pdf/TomTat_KichBan_Vang_SP500_2026-11-28.pdf (cũng trên E: và git).
- 16:12 t157u: capital = 10k cent = 100 USD. Specs searched (Exness Standard Cent help center 27/11/2026; XM Micro help center). Running direct9/opt9 (lots 100k x1/1000 -> cent lots = L/10, step 0.01).
- 16:25 round 8 done: direct9.py, opt9.py, tier9.py, mk_cent_md.py; results/r6/{direct9,opt9,cent_final,cent_sens}.json, ROUND8_NOTES.md; pdf/TomTat_KichBan_v2_100USD_cent_2026-11-28.pdf
