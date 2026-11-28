BOX DONE - PC PENDING - 2026-11-28 19:36 (UTC+7 / Asia/Saigon)

Box + git: research, README_FX, battery/port, EA, first push 16c216c, and a follow-up commit on grok/scenarios-v3 (never main).
MT5 vs Python: KHÔNG CÓ readable MT5 net/DD/trades for NZDJPY, US30, or GER40. Reports live only under E:\GrokWork\mt5_runs (runq_p6.log, results_p6.jsonl, reports\fx_*.htm) and E:\mt5_tester\p6. Read and CopyToBox refuse E: paths; no copies exist under C:\Users\DUNG (the allowed root). Queue q_p6_fx2.json was started 18:58 after InpTF=16385 and real ticks were downloaded (GER40 53.8 MB, US30 71.3 MB, NZDJPY 61.0 MB). Python OOS @ 1 lot still: NZDJPY +3000/DD 2088; US30 +7053/DD 2286; GER40 +1687/DD 545.

Remaining PC steps (need a working Shell or E: read access; do not kill 13548):
1) Read E:\GrokWork\mt5_runs\runq_p6.log and results_p6.jsonl plus reports\fx_ger40_z15_asia.htm, fx_us30_z240_ny.htm, fx_nzdjpy_ibs240_ldn.htm (copy them to C:\Users\DUNG\v3work\out\ if needed).
2) If the 18:58 runq (last known PIDs 11396 / 8884 / 8532) already finished, compare those reports to the Python numbers above. If no report, rerun E:\GrokWork\mt5_runs\runq.py E:\GrokWork\mt5_runs\q_p6_fx2.json on slot p6 only.
3) Finish sync into E:\GrokWork\bt_fx\ (CopyFromBox may be refused on E:). Staging: C:\Users\DUNG\v3work\out\sync_fx.tgz and, if written, C:\Users\DUNG\v3work\out\bt_fx\.
4) Fill README_FX section 7 with MT5 numbers, set this file's first line to ALL DONE, push a further commit to grok/scenarios-v3 only.
