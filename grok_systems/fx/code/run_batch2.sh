#!/bin/bash
cd /workspace/bt_3m/fx/code
for s in "$@"; do echo "$s"; done | xargs -P 3 -I{} bash -c '/workspace/venv3/bin/python fx_screen.py "{}" >> ../results/batch.log 2>&1; /workspace/venv3/bin/python fx_basket.py "{}" >> ../results/batch.log 2>&1'
echo BATCH2_DONE >> ../results/batch.log
