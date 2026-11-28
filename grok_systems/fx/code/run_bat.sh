#!/bin/bash
cd /workspace/bt_3m/fx/code
printf '%s\n' "GER40Cash# z5_30_2.5 asia 0.5 0.5 5" "GER40Cash# z15_30_3.0 asia 1.0 1.0 5" "US100Cash# L_rsi2_1440 all 1.0 2.0 3" "OILCash# L_rsi2_1440 all 2.0 1.0 3" "US30Cash# L_z240_20_2.5 ny 1.0 4.0 5" "US30Cash# rsi2t_15_10 asia 1.0 1.0 5" | xargs -P 3 -L1 bash -c '/workspace/venv3/bin/python fx_battery.py "$@" >> ../results/bat_cfd.log 2>&1' _
echo BAT_DONE >> ../results/bat_cfd.log
