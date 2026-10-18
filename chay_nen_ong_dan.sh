#!/usr/bin/env bash
# Chay ong dan NEN theo dot ngan (19/10/2026). Bi ngat thi chay lai lenh nay: moi phep thu da luu trong
# data/ong_dan/trang_thai.sqlite, dot sau chi lam phan con thieu. Log: data/ong_dan/nen.log (git bo qua).
#   nohup bash chay_nen_ong_dan.sh "12 16 20" 30 > /dev/null 2>&1 &
# Doi 1: danh sach ngan sach / the (tang dan). Doi 2: so the moi dot.
set -u
cd "$(dirname "$0")"
NGAN="${1:-12 16 20}"
MOI_DOT="${2:-30}"
LOG=data/ong_dan/nen.log
mkdir -p data/ong_dan
echo "=== $(date '+%F %T') bat dau: ngan sach [$NGAN], $MOI_DOT the / dot" >> "$LOG"
for ns in $NGAN; do
  while true; do
    truoc=$(python3 -c "import sqlite3;print(sqlite3.connect('data/ong_dan/trang_thai.sqlite').execute('select count(*) from thu').fetchone()[0])")
    python3 ong_dan.py toi_uu --lam-lai --ngan-sach "$ns" --toi-da "$MOI_DOT" >> "$LOG" 2>&1 || break
    sau=$(python3 -c "import sqlite3;print(sqlite3.connect('data/ong_dan/trang_thai.sqlite').execute('select count(*) from thu').fetchone()[0])")
    echo "--- $(date '+%F %T') ngan sach $ns: phep thu $truoc -> $sau" >> "$LOG"
    [ "$sau" -le "$truoc" ] && break
  done
done
for b in loc sinh_mt5 goi do_nguoc bao_cao; do python3 ong_dan.py "$b" >> "$LOG" 2>&1; done
echo "=== $(date '+%F %T') xong" >> "$LOG"
