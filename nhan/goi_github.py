# -*- coding: utf-8 -*-
"""goi_github.py - NGUON GOI EA MQL5 + .set TU GITHUB CONG KHAI (SEEKER, 11/10/2026).

Do 11/10/2026 (cau_kho tren box): Code Base MQL5 trang 1-2 cho 67 EA, chi **1** EA MQL5 co
`.set` cua tac gia (co_set_mql5=1). GitHub co nhieu repo EA MQL5 kem `.set` (search
`language:MQL5` ra ~600 repo "expert advisor"). Mo-dun nay la NGUON THU HAI cho cau kho:
  1. tim repo (`/search/repositories`, truy van chot truoc trong `TRUY_VAN_GH`), xep theo
     `truy_van_seeker.diem_tieu_de` cua ten+mo ta (chi la THU TU tai);
  2. MOT luot Git Trees cho moi repo -> chi giu repo co >= 1 `.mq5`;
  3. tai qua raw.githubusercontent.com (khong ton luot API): moi `.mq5` co `OnTick` -> mot goi
     `thu_muc/<owner>__<repo>__<ten>/` gom file EA + moi `.mqh` cua repo (phang theo ten goc,
     dung quy tac `tep_thieu_that`) + `.set` GHEP DUOC (xem `ghep_set`) + `GOI.json`.
Khong giai nen, khong chay ma, khong dang nhap. Token (neu co) chi qua bien moi truong
(`bi_mat.dau_github`), KHONG ghi dau ca. Tren 60 luot/gio khi khong token -> `tran_repo`.
Day chi la NGUON (them ung vien); cong giu cua vong lap KHONG doi; bo doc KHONG doi.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from urllib.parse import quote

GH = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
UA = "brain2-seeker/1.0 (+https://github.com/thebrainago/brain2)"

#: Truy van chot truoc (khong doi theo ket qua). Uu tien EA co .set / backtest (he da co so).
TRUY_VAN_GH = (
    "expert advisor set file language:MQL5",
    "EA backtest language:MQL5",
    "expert advisor strategy language:MQL5",
    "mt5 ea set",
    "expert advisor language:MQL5",
)
TRAN_BYTE = 400_000
TRAN_MQ5_MOI_REPO = 8
TRAN_MQH_MOI_REPO = 40
_RX_ONTICK = re.compile(r"\bvoid\s+OnTick\s*\(")


def _get(url: str, params: dict | None = None, timeout: int = 30, json_: bool = True):
    import requests
    from nhan import bi_mat as BM
    h = {"User-Agent": UA}
    if url.startswith(GH):
        h["Accept"] = "application/vnd.github+json"
        h.update(BM.dau_github())
    r = requests.get(url, params=params or {}, timeout=timeout, headers=h)
    if r.status_code != 200:
        return None, "HTTP %d" % r.status_code
    return (r.json() if json_ else r.content), None


def ghep_set(ea_path: str, ds_mq5: list[str], ds_set: list[str]) -> list[str]:
    """`.set` thuoc EA `ea_path` (quy tac CAU TRUC, chot truoc, khong nhin noi dung):
      (a) ten .set bat dau bang ten goc EA (khong phan biet hoa thuong), o bat ky dau trong repo;
      (b) hoac .set nam CUNG thu muc voi EA khi thu muc do co DUNG MOT .mq5.
    Tra moi .set khop; `cau_kho_ma.set_cua_goi` chi nhan khi goi co DUNG MOT .set."""
    goc = ea_path.rsplit("/", 1)[-1].rsplit(".", 1)[0].lower()
    cha = ea_path.rsplit("/", 1)[0] if "/" in ea_path else ""
    cung_cha = [m for m in ds_mq5 if (m.rsplit("/", 1)[0] if "/" in m else "") == cha]
    ra = []
    for s in ds_set:
        ten = s.rsplit("/", 1)[-1].lower()
        s_cha = s.rsplit("/", 1)[0] if "/" in s else ""
        if ten.startswith(goc) or (s_cha == cha and len(cung_cha) == 1):
            ra.append(s)
    return ra


def _ten_an_toan(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s)[:100]


def _giai(b: bytes) -> str | None:
    from nhan import ma_nguon as MN
    return MN._giai_ma_van_ban(b)


def tai_github_goi(thu_muc, han_giay: float = 120.0, so_repo: int = 20,
                   truy_van: list[dict] | None = None, nghi_giay: float = 1.0,
                   get=None, in_ra=print) -> dict:
    """Mot luot nguon GitHub -> goi EA trong `thu_muc`. `get(url, params, json_)` thay duoc cho
    test. Manifest `NGUON_GH.json` (repo da xem -> khong ton luot lai; repo moi day -> xem lai
    khi `pushed_at` doi). Tra bang dem."""
    from nhan import truy_van_seeker as TV
    get = get or (lambda u, p=None, j=True: _get(u, p, json_=j))
    d = Path(thu_muc)
    d.mkdir(parents=True, exist_ok=True)
    pm = d / "NGUON_GH.json"
    try:
        man = json.loads(pm.read_text(encoding="utf-8")) if pm.exists() else {}
    except Exception:
        man = {}
    t0 = time.time()
    bao = {"truy_van": 0, "repo_thay": 0, "repo_xem": 0, "repo_co_mq5": 0, "ea_moi": 0,
           "ea_co_set": 0, "tep": 0, "loi": []}
    ung: dict[str, dict] = {}
    for q in TRUY_VAN_GH:
        if time.time() - t0 > han_giay * 0.25:
            break
        j, loi = get(GH + "/search/repositories", {"q": q, "sort": "updated", "per_page": 50})
        bao["truy_van"] += 1
        if loi:
            bao["loi"].append("search:%s" % loi)
            break                                   # 403/422 search: dung, khong quay vong
        for r in (j or {}).get("items", []):
            ung.setdefault(r["full_name"], r)
        if nghi_giay:
            time.sleep(nghi_giay)
    bao["repo_thay"] = len(ung)

    def _diem(r):
        return TV.diem_tieu_de("%s %s" % (r.get("name", ""), r.get("description") or ""),
                               truy_van)
    ds = sorted(ung.values(), key=lambda r: (-_diem(r), -int(r.get("stargazers_count") or 0)))
    for r in ds:
        if bao["repo_xem"] >= so_repo:
            bao["tran_repo"] = True
            break
        if time.time() - t0 > han_giay:
            bao["het_gio"] = True
            break
        fn = r["full_name"]
        cu = man.get(fn)
        if cu and cu.get("pushed_at") == r.get("pushed_at"):
            continue
        nhanh = r.get("default_branch") or "main"
        t, loi = get(GH + "/repos/%s/git/trees/%s" % (fn, quote(nhanh)), {"recursive": "1"})
        bao["repo_xem"] += 1
        if loi:
            bao["loi"].append("%s:%s" % (fn, loi))
            if loi in ("HTTP 403", "HTTP 429"):
                break                               # het han muc: dung, khong danh dau repo
            man[fn] = {"pushed_at": r.get("pushed_at"), "loi": loi}
            continue
        cay = [n for n in (t or {}).get("tree", []) if n.get("type") == "blob"
               and int(n.get("size") or 0) <= TRAN_BYTE]
        p_mq5 = [n["path"] for n in cay if n["path"].lower().endswith(".mq5")]
        p_mqh = [n["path"] for n in cay if n["path"].lower().endswith(".mqh")]
        p_set = [n["path"] for n in cay if n["path"].lower().endswith(".set")]
        ghi = {"pushed_at": r.get("pushed_at"), "mq5": len(p_mq5), "set": len(p_set), "ea": []}
        if not p_mq5:
            man[fn] = ghi
            continue
        bao["repo_co_mq5"] += 1
        mqh_cache: dict[str, str] = {}
        for p in p_mq5[:TRAN_MQ5_MOI_REPO]:
            b, loi = get("%s/%s/%s/%s" % (RAW, fn, quote(nhanh), quote(p)), None, False)
            src = _giai(b) if b else None
            if not src or not _RX_ONTICK.search(src):
                continue                            # chi bao / script / tai hong: khong phai EA
            goi = d / _ten_an_toan("%s__%s" % (fn.replace("/", "__"),
                                               p.rsplit(".", 1)[0].replace("/", "_")))
            goi.mkdir(parents=True, exist_ok=True)
            tep = {p.rsplit("/", 1)[-1]: src}
            sets = ghep_set(p, p_mq5, p_set)
            for s in sets[:5]:
                bs, _ = get("%s/%s/%s/%s" % (RAW, fn, quote(nhanh), quote(s)), None, False)
                vs = _giai(bs) if bs else None
                if vs:
                    tep[s.rsplit("/", 1)[-1]] = vs
            from nhan import cau_kho_ma as CK
            if p_mqh and CK.tep_include_ngoai(src):
                for h in p_mqh[:TRAN_MQH_MOI_REPO]:
                    if h not in mqh_cache:
                        bh, _ = get("%s/%s/%s/%s" % (RAW, fn, quote(nhanh), quote(h)), None, False)
                        mqh_cache[h] = (_giai(bh) if bh else None) or ""
                    if mqh_cache[h]:
                        tep.setdefault(h.rsplit("/", 1)[-1], mqh_cache[h])
            for ten, vb in tep.items():
                (goi / _ten_an_toan(ten)).write_text(vb, encoding="utf-8")
            n_set = sum(1 for k in tep if k.lower().endswith(".set"))
            meta = {"id": "gh:%s:%s" % (fn, p), "revision": "github-%s@%s" % (fn, nhanh),
                    "url": "https://github.com/%s/blob/%s/%s" % (fn, nhanh, quote(p)),
                    "tieu_de": "%s — %s" % (fn, r.get("description") or ""),
                    "nen_tang": "mt5", "nguon": "github", "tep": sorted(tep),
                    "sao": int(r.get("stargazers_count") or 0), "co_zip": False,
                    "chi_zip": False, "anh": [], "anh_ket_qua": [], "bo": [],
                    "diem_tieu_de": _diem(r), "luc": time.strftime("%Y-%m-%d %H:%M:%S")}
            (goi / "GOI.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1),
                                          encoding="utf-8")
            ghi["ea"].append(p)
            bao["ea_moi"] += 1
            bao["ea_co_set"] += 1 if n_set else 0
            bao["tep"] += len(tep)
        man[fn] = ghi
        if nghi_giay:
            time.sleep(nghi_giay)
    pm.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    bao["giay"] = round(time.time() - t0, 1)
    if not bao["loi"]:
        bao.pop("loi")
    in_ra("tai_github_goi: %s" % bao)
    return bao
