#!/bin/bash
# usage: run_all4.sh SYM...  : scalp screen + basket real + placebo(0) + mirror, 4 symbols in parallel
cd /workspace/bt_3m/fx/code
for s in "$@"; do echo "$s"; done | xargs -P 4 -I{} bash -c 'S="{}"; /workspace/venv3/bin/python fx_screen.py "$S"; /workspace/venv3/bin/python fx_basket.py "$S"; PLACEBO=0 /workspace/venv3/bin/python fx_basket.py "$S"; PLACEBO=-2 /workspace/venv3/bin/python fx_basket.py "$S"' >> ../results/batch_cfd.log 2>&1
echo CFD_DONE >> ../results/batch_cfd.log
