"""probe.py URL... - chan doan: ma HTTP, do dai, tieu de, co phai trang chan khong (requests thuong, 1 request/URL)."""
import sys
from net import Net, SiteBan
n = Net(min_gap=3, tries=1)
for u in sys.argv[1:]:
    try:
        r = n.get(u); t = r.text
        title = t[t.find("<title>") + 7:t.find("</title>")][:100] if "<title>" in t else ""
        print(r.status_code, len(t), repr(title), u)
    except SiteBan as e: print("BI_CHAN", u, e); break
    except Exception as e: print("LOI", u, str(e)[:150])
