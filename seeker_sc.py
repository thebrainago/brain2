# -*- coding: utf-8 -*-
"""seeker_sc.py - SEEKER ho so nguon "sierra_chart" (18/11/2026): tim he/setup orderflow Sierra Chart cho GC/ES/NQ.

Linh vuc moi = bo nguon + bo tu khoa moi, dung lai `tru/seeker.py` (`_lay`, `dau_hieu_van_hanh`).
Chi nguon CONG KHAI: GitHub API (repo + code search qua `gh` da dang nhap), Reddit JSON cong khai, arXiv API.
Khong dang nhap trang nao, khong tai/chay file nhi phan; chi tai file ma nguon .cpp/.h/.txt/.md vao data/ (gitignore).
Gap 403/429 -> dung nguon do, khong thu lai (seeker_unblock/README.md).

Chay:  python3 seeker_sc.py quet            -> data/sc_seeker/ung_vien.json
       python3 seeker_sc.py tai [N]         -> tai ma nguon N repo diem cao -> data/sc_seeker/ma/
       python3 seeker_sc.py kiem-ke         -> phan loai ACSIL (chi_bao/ea) + tu khoa orderflow
"""
from __future__ import annotations
import json, re, subprocess, sys, time, urllib.parse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tru import seeker as S

GOC = Path(__file__).resolve().parent / "data" / "sc_seeker"
GOC.mkdir(parents=True, exist_ok=True)
UA_THAT = {"User-Agent": "TheBrain-Seeker/1.0 (research; contact via github thebrainago)"}

TU_KHOA_GH_REPO = ["sierra chart ACSIL", "sierrachart study", "sierra chart orderflow", "sierrachart footprint",
                   "sierra chart volume profile", "sierra chart delta", "ACSIL", "sierrachart", "sierra chart indicator",
                   "sierra chart trading system", "sierra chart absorption", "sierra chart market profile"]
TU_KHOA_GH_CODE = ["SCSFExport absorption", "SCSFExport imbalance", "SCSFExport delta divergence",
                   "SCSFExport initial balance", "SCSFExport VWAP band", "SCSFExport iceberg",
                   "SCSFExport market depth", "SCSFExport footprint", "SCSFExport exhaustion",
                   "SCSFExport \"BuyEntry\"", "SCSFExport trapped", "SCSFExport opening range"]
REDDIT = [("FuturesTrading", "sierra chart setup"), ("FuturesTrading", "order flow setup"),
          ("FuturesTrading", "absorption"), ("FuturesTrading", "footprint imbalance"),
          ("orderflow", "setup"), ("orderflow", "absorption"), ("Daytrading", "sierra chart order flow"),
          ("FuturesTrading", "initial balance"), ("FuturesTrading", "delta divergence")]
ARXIV = ["order flow imbalance futures intraday", "order book imbalance E-mini", "trade flow toxicity futures",
         "volume profile intraday futures", "initial balance opening range futures"]
LOC = re.compile(r"absorp|imbalanc|delta|footprint|iceberg|vwap|profile|tpo|initial.?balance|\bib\b|opening.?range|"
                 r"exhaust|trap|sweep|depth|dom|cvd|order.?flow|big.?trade|large.?trade|stop.?run|poc|value.?area", re.I)


def gh(path: str) -> dict | None:
    r = subprocess.run(["gh", "api", "-H", "Accept: application/vnd.github+json", path], capture_output=True, text=True)
    if r.returncode != 0:
        print("GH loi", path[:80], r.stderr[:120]); return None
    return json.loads(r.stdout)


def quet() -> list[dict]:
    uv: dict[str, dict] = {}
    def them(d):
        k = d["url"]
        if k in uv: uv[k]["diem"] += 0.5; uv[k]["tu_khoa"].append(d["tu_khoa"][0]); return
        uv[k] = d
    for t in TU_KHOA_GH_REPO:
        j = gh("search/repositories?per_page=50&q=" + urllib.parse.quote(t))
        for it in (j or {}).get("items", []):
            mo = f"{it.get('full_name')} {it.get('description') or ''} {' '.join(it.get('topics') or [])}"
            them({"nguon": "github_repo", "url": it["html_url"], "repo": it["full_name"], "tieu_de": it["full_name"],
                  "tom_tat": (it.get("description") or "")[:300], "sao": it.get("stargazers_count", 0),
                  "cap_nhat": it.get("pushed_at"), "tu_khoa": [t],
                  "diem": 1 + min(it.get("stargazers_count", 0) / 50, 3) + (1.5 if LOC.search(mo) else 0)})
        time.sleep(2.5)
    for t in TU_KHOA_GH_CODE:
        j = gh("search/code?per_page=50&q=" + urllib.parse.quote(t + " language:C++"))
        for it in (j or {}).get("items", []):
            rp = it["repository"]["full_name"]
            them({"nguon": "github_code", "url": it["html_url"], "repo": rp, "tieu_de": f"{rp}/{it['path']}",
                  "tom_tat": it["path"], "sao": None, "tu_khoa": [t], "diem": 1.5 + (1.5 if LOC.search(it["path"]) else 0)})
        time.sleep(7)                                     # code search: 10 luot/phut
    import requests
    for sub, q in REDDIT:
        u = f"https://www.reddit.com/r/{sub}/search.json?q={urllib.parse.quote(q)}&restrict_sr=1&sort=top&t=all&limit=50"
        try:
            r = requests.get(u, headers=UA_THAT, timeout=25)
        except Exception as e:
            print("reddit loi", e); continue
        if r.status_code in (403, 429):
            print("reddit chan", r.status_code, "-> dung nguon"); break
        if r.status_code != 200: continue
        for c in r.json().get("data", {}).get("children", []):
            d = c["data"]; txt = (d.get("title", "") + " " + d.get("selftext", ""))
            if not LOC.search(txt): continue
            them({"nguon": "reddit", "url": "https://www.reddit.com" + d["permalink"], "tieu_de": d.get("title"),
                  "tom_tat": d.get("selftext", "")[:1500], "sao": d.get("score"), "tu_khoa": [f"r/{sub}:{q}"],
                  "diem": 0.5 + min((d.get("score") or 0) / 100, 2) + (1 if re.search(r"\bentry\b|\bstop\b|\btarget\b|rule", txt, re.I) else 0)})
        time.sleep(4)
    for q in ARXIV:
        u = "http://export.arxiv.org/api/query?max_results=15&search_query=all:" + urllib.parse.quote(q)
        x = S._lay(u)
        for m in re.finditer(r"<entry>.*?<id>(.*?)</id>.*?<title>(.*?)</title>.*?<summary>(.*?)</summary>", x or "", re.S):
            them({"nguon": "arxiv", "url": m.group(1).strip(), "tieu_de": " ".join(m.group(2).split()),
                  "tom_tat": " ".join(m.group(3).split())[:600], "sao": None, "tu_khoa": [q], "diem": 0.3})
        time.sleep(3)
    ds = sorted(uv.values(), key=lambda d: -d["diem"])
    (GOC / "ung_vien.json").write_text(json.dumps(ds, ensure_ascii=False, indent=1))
    print("ung vien:", len(ds), {n: sum(1 for d in ds if d["nguon"] == n) for n in {d["nguon"] for d in ds}})
    return ds


DUOI_MA = (".cpp", ".h", ".hpp", ".txt", ".md", ".py")


def tai(n: int = 40) -> None:
    ds = json.loads((GOC / "ung_vien.json").read_text())
    repo = []
    for d in ds:
        if d.get("repo") and d["repo"] not in repo: repo.append(d["repo"])
    for rp in repo[:n]:
        info = gh(f"repos/{rp}")
        if not info: continue
        cay = gh(f"repos/{rp}/git/trees/{info['default_branch']}?recursive=1") or {}
        tep = [t for t in cay.get("tree", []) if t["type"] == "blob" and t["path"].lower().endswith(DUOI_MA) and t.get("size", 0) < 600_000][:150]
        dich = GOC / "ma" / rp.replace("/", "__")
        for t in tep:
            u = f"https://raw.githubusercontent.com/{rp}/{info['default_branch']}/{urllib.parse.quote(t['path'])}"
            p = dich / t["path"]; p.parent.mkdir(parents=True, exist_ok=True)
            if p.exists(): continue
            r = subprocess.run(["curl", "-sfL", "--max-time", "30", "-o", str(p), u])
            if r.returncode: print("  khong tai", u)
        (dich / "_META.json").write_text(json.dumps({"repo": rp, "sao": info.get("stargazers_count"), "license": (info.get("license") or {}).get("spdx_id"),
                                                    "pushed_at": info.get("pushed_at"), "mo_ta": info.get("description")}, ensure_ascii=False))
        print("TAI", rp, len(tep))


def kiem_ke() -> None:
    ra = []
    for p in sorted((GOC / "ma").rglob("*")):
        if not p.is_file() or not p.suffix.lower() in (".cpp", ".h", ".hpp"): continue
        vb = S.doc_van_ban_ma(p.read_bytes())
        d = S.dau_hieu_van_hanh(vb, p.name)
        if d["nen_tang"] != "SierraChart": continue
        studies = re.findall(r"SCSFExport\s+(\w+)", vb)
        names = re.findall(r'sc\.GraphName\s*=\s*"([^"]+)"', vb)
        kw = sorted({m.group(0).lower() for m in LOC.finditer(vb)})
        ra.append({"tep": str(p.relative_to(GOC)), **d, "so_study": len(studies), "ten": names[:8], "tu_khoa_of": kw[:20]})
    (GOC / "kiem_ke.json").write_text(json.dumps(ra, ensure_ascii=False, indent=1))
    print("tep ACSIL:", len(ra), "ea:", sum(r["loai"] == "ea" for r in ra), "chi_bao:", sum(r["loai"] == "chi_bao" for r in ra))


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else "quet"
    {"quet": quet, "kiem-ke": kiem_ke}.get(c, lambda: tai(int(sys.argv[2]) if len(sys.argv) > 2 else 40))()
