"""test_offline.py - kiem tra offline (khong goi mang). Chay: python3 test_offline.py
Du lieu tho nam NGOAI git: /workspace/nguon_khac/home/raw (bo qua test neu khong co)."""
import os, sys, glob, json, csv, tempfile, shutil, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myfxbook as M, net
RAW = "/workspace/nguon_khac/home/raw/mfb"
ok = 0

def t_siteban():
    class R:
        status_code = 429; headers = {"content-type": "text/html"}; text = "error code: 1015"; content = b""
    n = net.Net(min_gap=0, tries=3)
    n.s.get = lambda *a, **k: R()
    try: n.get("https://example.invalid/"); raise AssertionError("phai dung")
    except net.SiteBan: pass
    assert n.stats["bi_chan"] == 1, n.stats  # dung ngay lan dau, khong thu lai

def t_parse_raw():
    fs = glob.glob(os.path.join(RAW, "0_*6426348*.txt"))
    if not fs: print("  bo qua (khong co raw)"); return
    h = M.load_history_html(fs[0]); cols = M.head_cols(h)
    assert cols[:12] == M.OLD, cols
    rows = M.parse_rows(h, cols); assert len(rows) == 20
    tr = [r for r in rows if r["action"] in ("Buy", "Sell")]
    assert tr and all(r["symbol"] for r in tr)

def t_fetch_disabled():
    p = subprocess.run([sys.executable, "myfxbook.py", "fetch", "1"], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    assert p.returncode == 2 and "VO HIEU HOA" in p.stdout
    p = subprocess.run([sys.executable, "mql5_browser.py", "login"], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    assert p.returncode == 2

def t_fix_offline():
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "1.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["record", "open_time_ms", "close_time_ms"] + M.OLD); w.writeheader()
        w.writerow(dict(record="1", open_time_ms="0", close_time_ms="1", open_broker="d1", close_broker="EURUSD", symbol="Buy",
                        action="1.1", sl_pips="1.2", tp_pips="10.0", open_price="5.00", close_price="2h", pips="0.1%"))
    json.dump({"oid": "1", "status": "ok"}, open(os.path.join(d, "1_meta.json"), "w"))
    subprocess.run([sys.executable, "myfxbook_fix_offline.py", os.path.join(d, "1.csv"),
                    "close_broker,symbol,action,open_price,close_price,pips,profit,duration,gain_pct"], check=True, capture_output=True,
                   cwd=os.path.dirname(os.path.abspath(__file__)))
    r = list(csv.DictReader(open(os.path.join(d, "1.csv"))))[0]
    assert r["symbol"] == "EURUSD" and r["pips"] == "10.0" and r["profit"] == "5.00", r
    shutil.rmtree(d)

for t in [t_siteban, t_parse_raw, t_fetch_disabled, t_fix_offline]:
    t(); ok += 1; print("OK", t.__name__)
print(f"{ok}/4 test dat")
