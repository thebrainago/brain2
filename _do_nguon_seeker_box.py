"""Do nguon SEEKER khong can dang nhap tren box Linux (11/10/2026): goi tung ham n_* va RSS, CHI THU, khong ghi nao.db.
Chay: python _do_nguon_seeker_box.py  (~3 phut) -> reports/SEEKER_BOX_DO.json"""
# Do nguon SEEKER tren box (chi THU, khong ghi nao.db): moi nguon requests -> so muc tra ve.
import sys, time, json, signal
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
import tru.seeker as S
from nhan import nguon_bai_viet as NBV
class TO(Exception): pass
def h(*a): raise TO()
signal.signal(signal.SIGALRM, h)
tk = ["grid trading ea mql5", "mean reversion"]
ra = {}
def thu(ten, f):
    t = time.time(); signal.alarm(60)
    try:
        r = f(); n = len(r) if hasattr(r, '__len__') else r
        ra[ten] = {"ok": bool(n), "n": n if isinstance(n, int) else str(n)[:80]}
    except TO: ra[ten] = {"ok": False, "loi": "timeout 60s"}
    except Exception as e: ra[ten] = {"ok": False, "loi": f"{type(e).__name__}: {str(e)[:100]}"}
    finally: signal.alarm(0)
    ra[ten]["giay"] = round(time.time() - t, 1); print(ten, ra[ten], flush=True)
for ma, c in S.NGUON.items():
    thu(ma, lambda c=c: c["ham"](tk))
for ma, f in NBV.FEEDS.items():
    url = f.get("url") if isinstance(f, dict) else f
    thu("rss_" + ma, lambda url=url: NBV.doc_feed(NBV._lay(url, timeout=20) or ""))
json.dump(ra, open('reports/SEEKER_BOX_DO.json', 'w'), ensure_ascii=False, indent=1)
