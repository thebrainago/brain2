#!/bin/bash
# Assemble grok_systems/fx into box clone /workspace/brain2_scen (branch grok/scenarios-v3 ONLY, never main). Code + results + docs; no raw M1 data.
set -e
F=/workspace/bt_3m/fx; R=/workspace/brain2_scen; D=$R/grok_systems/fx
cd $R; git checkout -q grok/scenarios-v3
rm -rf $D; mkdir -p $D/code $D/results $D/mt5 $D/ea $D/mt5/reports $D/pc_tools
cp $F/README_FX.md $F/STATUS.md $D/
cp $F/code/*.py $F/code/*.sh $D/code/; cp /workspace/bt_3m/code/engine2.py $D/code/ 2>/dev/null || true
for f in $F/results/*.json $F/results/*.csv $F/results/*.md; do [ -f $f ] && [ $(stat -c%s $f) -lt 4000000 ] && cp $f $D/results/; done 2>/dev/null || true
cp $F/results/*.log $D/results/ 2>/dev/null || true
cp $F/mt5/*.csv $F/mt5/*.json $D/mt5/ 2>/dev/null || true
cp $F/ea/*.mq5 $D/ea/ 2>/dev/null || true
cp $F/mk_git_fx.sh $F/mk_sync_fx.sh $D/ 2>/dev/null || true
cp $F/mt5/reports/*.htm $D/mt5/reports/ 2>/dev/null || true
cp $F/pc_tools/*.py $D/pc_tools/ 2>/dev/null || true
mkdir -p $D/pdf
cp $F/pdf/*.pdf $F/pdf/*.py $D/pdf/ 2>/dev/null || true

if grep -rIlE "(api[_-]?key|token|password|secret)\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}" $D; then echo "SECRET-LIKE STRING FOUND, abort"; exit 3; fi
git add grok_systems/fx; git add -f grok_systems/fx/pdf/*.pdf 2>/dev/null || true; git -c user.name="Grok Bot" -c user.email="grokbot@users.noreply.github.com" commit -q -m "${1:-grok_systems/fx: FX / other assets research}" || echo "nothing to commit"
git push -q -u origin grok/scenarios-v3 2>&1 | tail -2; git log --oneline -1
