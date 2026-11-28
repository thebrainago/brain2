#!/bin/bash
cd /workspace/bt_3m/fx/code
for s in "$@"; do echo "$s"; done | xargs -P 3 -I{} bash -c 'PLACEBO=-2 /workspace/venv3/bin/python fx_basket.py "{}" >> ../results/batch_mir.log 2>&1'
echo MIR_DONE >> ../results/batch_mir.log
