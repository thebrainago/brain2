"""dl.py URL OUTFILE - tai 1 trang cong khai ve file (requests thuong, dung neu bi chan)."""
import sys
from net import Net
r = Net(tries=1).get(sys.argv[1])
open(sys.argv[2], "wb").write(r.content); print(r.status_code, len(r.content))
