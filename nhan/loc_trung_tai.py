"""LOC TRUNG TRUOC KHI TAI (Seeker) - 20/10/2026.

Chu du an: "Seeker pre-download dedupe (repo full_name / commit sha / file-hash list qua metadata GitHub API)".
Truoc khi `git clone` / tai zip mot kho GitHub, chi doc METADATA (khong tai ma):
  1. /repos/{full_name}  -> id (khong doi khi doi ten / chuyen chu), full_name chuan, fork + parent, nhanh mac dinh;
  2. /commits/{nhanh}    -> sha commit dau nhanh (tree sha);
  3. /git/trees/{tree}?recursive=1 -> danh sach blob sha cua file MA (mq4/mq5/mqh/pine/py/cs...).
Bo qua khi: cung repo id / cung full_name da tai cung sha; cung tree sha (fork y nguyen, ban sao); hoac >= NGUONG_TRUNG
file ma trung blob sha voi cac kho da tai (fork khong sua gi dang ke). So dang ky: data/seeker_da_nguon/da_tai.jsonl
(git bo qua - data/). Khong co mang / API loi -> CHUA_DO_DUOC, mac dinh CHO TAI (khong chan nham).
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
SO_DANG_KY = GOC / "data" / "seeker_da_nguon" / "da_tai.jsonl"
DUOI_MA = (".mq4", ".mq5", ".mqh", ".pine", ".py", ".cs", ".ex4", ".ex5", ".txt", ".set")
NGUONG_TRUNG = 0.9
API = "https://api.github.com"


def _get_mac_dinh(url: str, timeout: int = 20):
    h = {"Accept": "application/vnd.github+json", "User-Agent": "the-brain-seeker"}
    tk = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tk:
        h["Authorization"] = "Bearer " + tk          # chi doc tu bien moi truong, khong ghi ra dau
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8", "ignore"))
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:  # noqa: BLE001
        return 0, None


def metadata(full_name: str, get=None) -> dict:
    """-> {trang_thai OK|KHONG_CO|CHUA_DO_DUOC, id, full_name, fork, parent, nhanh, sha, tree, blob{path: sha}}."""
    get = get or _get_mac_dinh
    ma, r = get("%s/repos/%s" % (API, full_name))
    if ma == 404:
        return {"trang_thai": "KHONG_CO", "full_name": full_name}
    if ma != 200 or not isinstance(r, dict):
        return {"trang_thai": "CHUA_DO_DUOC", "full_name": full_name, "ghi_chu": "HTTP %s" % ma}
    m = {"trang_thai": "OK", "id": r.get("id"), "full_name": str(r.get("full_name") or full_name),
         "fork": bool(r.get("fork")), "parent": ((r.get("parent") or {}).get("full_name")),
         "nhanh": r.get("default_branch") or "main", "kich_thuoc_kb": r.get("size")}
    ma, c = get("%s/repos/%s/commits/%s" % (API, m["full_name"], m["nhanh"]))
    if ma == 200 and isinstance(c, dict):
        m["sha"] = c.get("sha")
        m["tree"] = ((c.get("commit") or {}).get("tree") or {}).get("sha")
    if m.get("tree"):
        ma, t = get("%s/repos/%s/git/trees/%s?recursive=1" % (API, m["full_name"], m["tree"]))
        if ma == 200 and isinstance(t, dict):
            m["blob"] = {x["path"]: x["sha"] for x in t.get("tree", [])
                         if x.get("type") == "blob" and str(x.get("path", "")).lower().endswith(DUOI_MA)}
    return m


def doc_so(p: Path | None = None) -> list[dict]:
    p = Path(p or SO_DANG_KY)
    if not p.exists():
        return []
    ra = []
    for x in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            ra.append(json.loads(x))
        except ValueError:
            continue
    return ra


def ghi_so(m: dict, duong_dan: str = "", p: Path | None = None) -> None:
    p = Path(p or SO_DANG_KY)
    p.parent.mkdir(parents=True, exist_ok=True)
    d = {k: m.get(k) for k in ("id", "full_name", "sha", "tree", "fork", "parent")}
    d.update(blob=sorted(set((m.get("blob") or {}).values())), duong_dan=duong_dan, luc=time.strftime("%Y-%m-%dT%H:%M:%S"))
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")


def nen_tai(full_name: str, get=None, so: list[dict] | None = None, nguong: float = NGUONG_TRUNG) -> tuple[bool, str, dict]:
    """-> (co nen tai, ly do, metadata). Chi doc metadata; KHONG tai ma."""
    so = doc_so() if so is None else so
    m = metadata(full_name, get=get)
    if m["trang_thai"] == "KHONG_CO":
        return False, "KHONG_CO tren GitHub (404)", m
    ten = full_name.lower()
    if m["trang_thai"] != "OK":
        if any(str(x.get("full_name") or "").lower() == ten for x in so):
            return False, "TRUNG full_name (API %s, khong do duoc sha)" % m.get("ghi_chu"), m
        return True, "CHUA_DO_DUOC metadata (%s) - van tai" % m.get("ghi_chu"), m
    for x in so:
        cung_kho = (m.get("id") and x.get("id") == m["id"]) or str(x.get("full_name") or "").lower() in (ten, m["full_name"].lower())
        if cung_kho and (not m.get("sha") or x.get("sha") == m.get("sha")):
            return False, "TRUNG kho %s cung commit %s" % (x.get("full_name"), str(m.get("sha"))[:10]), m
        if m.get("tree") and x.get("tree") == m["tree"]:
            return False, "TRUNG cay file (tree %s) voi %s" % (m["tree"][:10], x.get("full_name")), m
    bl = set((m.get("blob") or {}).values())
    if bl:
        da = set()
        for x in so:
            da.update(x.get("blob") or [])
        ti = len(bl & da) / len(bl)
        if ti >= nguong:
            return False, "TRUNG %.0f%% file ma (%d/%d blob sha) voi kho da tai" % (100 * ti, len(bl & da), len(bl)), m
        return True, "MOI (%d file ma, trung %.0f%%)" % (len(bl), 100 * ti), m
    return True, "MOI (khong thay file ma trong cay / khong doc duoc cay)", m
