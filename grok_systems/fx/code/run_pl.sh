#!/bin/bash
cd /workspace/bt_3m/fx/code
for s in "$@"; do echo "$s"; done | xargs -P 3 -I{} bash -c 'PLACEBO=0 /workspace/venv3/bin/python fx_basket.py "{}" >> ../results/batch_pl.log 2>&1'
echo PL_DONE >> ../results/batch_pl.log
