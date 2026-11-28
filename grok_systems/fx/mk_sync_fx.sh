#!/bin/bash
cd /workspace/bt_3m/fx; tar czf sync_fx.tgz README_FX.md STATUS.md mk_git_fx.sh mk_sync_fx.sh code/*.py code/*.sh results/*.json results/*.csv results/*.log mt5/*.csv mt5/*.json ea/*.mq5 2>/dev/null; ls -la sync_fx.tgz
