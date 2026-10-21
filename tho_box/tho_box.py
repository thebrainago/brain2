# -*- coding: utf-8 -*-
"""tho_box.py - box lam THO PHU cho may nha (20/10/2026 toi, Grok Bot). Box khong co MT5.

Ba tien trinh (moi cai mot PID, nohup):
  python3 tho_box/tho_box.py dich   - dich_llm cac the o CUOI hang cho (may nha lam tu DAU), nhan viec truoc trong
                                      reports/phan_viec/NHAN_VIEC.jsonl; luong LLM tu giam khi gap 429.
  python3 tho_box/tho_box.py thu    - toi_uu Python (loc 65/15 sau phi) cac the da dich DAT, sinh viec MT5 vao
                                      reports/phan_viec/hang_cho_mt5_box.jsonl (+ .set/.ini/CSV trong reports/phan_viec/viec_mt5).
  python3 tho_box/tho_box.py day    - moi 20 phut: pytest test_phan_viec.py -> chep reports/phan_viec vao worktree
                                      rieng, commit, pull --rebase, push main (khong force). Chay trong worktree /workspace/brain2_box_wt (HEAD tach, data/ la symlink).
CSDL rieng cua box: data/ong_dan/tho_box.sqlite (chup tu CSDL may nha 20:38 20/10). Khoa LLM chi tu bien moi truong.
Khong sua dich_llm.py / ong_dan.py / dieu phoi: chi goi ham va doi duong dan ghi trong tien trinh nay.
"""
from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC))
os.chdir(GOC)

from nhan import phan_viec as PV  # noqa: E402

DB = GOC / "data" / "ong_dan" / "tho_box.sqlite"
LOG = GOC / "data" / "tho_box"
MAY = "box"
WT = GOC   # 20/10 21:10: tho chay NGAY trong worktree rieng (data -> symlink /workspace/brain2/data)


def ghi(ten: str, s: str) -> None:
    LOG.mkdir(parents=True, exist_ok=True)
    dong = "%s %s" % (time.strftime("%Y-%m-%dT%H:%M:%S"), s)
    print(dong, flush=True)
    with open(LOG / ("%s.jsonl" % ten), "a", encoding="utf-8") as f:
        f.write(json.dumps({"luc": time.strftime("%Y-%m-%dT%H:%M:%S"), "s": s}, ensure_ascii=False) + "\n")


def ket_noi():
    cn = sqlite3.connect(str(DB), timeout=120)
    cn.execute("PRAGMA busy_timeout=120000")
    return cn


# ------------------------------------------------------------------------------------------------ DICH
def vong_dich(luong: int, so_bam: int) -> dict:
    from nhan import dich_llm as DL
    from nhan import cau_llm as LLM
    DL.BAO_CAO = PV.THU_MUC / "DICH_LLM_BOX.md"          # khong ghi de bao cao cua may nha
    cn = ket_noi()
    goc_ds = DL.danh_sach_cho
    ds = [x for x in goc_ds(cn) if x["tep"] is not None]
    so = PV.doc_so("dich")
    chon, bam_chon = [], []
    for x in reversed(ds):                                 # tu CUOI hang
        h = DL.bam(x["tep"].read_bytes()[:800000])
        if PV.cua_may_khac("dich", h, MAY, so):
            continue
        if h not in bam_chon:
            if len(bam_chon) >= so_bam:
                continue
            bam_chon.append(h)
        chon.append(x)
    if not chon:
        cn.close()
        return {"cho": len(ds), "lam": 0}
    PV.nhan("dich", [(h, [x["the"]["id"] for x in chon if DL.bam(x["tep"].read_bytes()[:800000]) == h]) for h in bam_chon], MAY)
    DL.danh_sach_cho = lambda _cn, _c=chon: list(_c)
    q0 = LLM.THONG_KE.get("so_lan_429", 0)
    t0 = time.time()
    try:
        dem = DL.buoc_dich_llm(cn, luong=luong, in_ra=lambda s: ghi("dich", s))
    finally:
        DL.danh_sach_cho = goc_ds
        cn.close()
    dem["giay"] = round(time.time() - t0, 1)
    dem["so_429"] = LLM.THONG_KE.get("so_lan_429", 0) - q0
    dem["cho_truoc"] = len(ds)
    dem["luong"] = luong
    return dem


def het_quota() -> bool:
    from nhan import dich_llm as DL
    p = DL.CACHE / "nhat_ky.jsonl"
    try:
        d = json.loads(p.read_text(encoding="utf-8").splitlines()[-1])
    except Exception:
        return False
    return any("insufficient user quota" in str(x.get("ghi_chu") or "") for x in d.get("the") or [])


def chay_dich(luong: int = 4, so_bam: int = 16) -> None:
    rong = 0
    while True:
        try:
            d = vong_dich(luong, so_bam)
        except Exception as e:  # noqa: BLE001
            ghi("dich", "LOI vong: %s: %s" % (type(e).__name__, str(e)[:300]))
            time.sleep(120)
            continue
        ghi("dich", "VONG " + json.dumps({k: d.get(k) for k in ("cho_truoc", "lam", "goi_moi", "dat", "hong", "loi_llm",
                                                               "so_429", "giay", "luong", "token_vao", "token_ra")}))
        if het_quota():
            # 20/10/2026 21:00: ai-box 403 "insufficient user quota" -> DUNG HAN (goi lai chi lam tang dich_llm_loi_lan,
            # 3 lan -> the bi BO_QUA oan). Nap quota roi chay lai tien trinh nay.
            ghi("dich", "HET QUOTA ai-box (HTTP 403 insufficient user quota) -> dung tien trinh dich")
            return
        if (d.get("so_429") or 0) >= 3 and luong > 1:
            luong = max(1, luong // 2)
            ghi("dich", "429 nhieu -> giam luong con %d" % luong)
        elif (d.get("so_429") or 0) == 0 and luong < 4 and d.get("lam"):
            luong += 1
        if not d.get("lam"):
            rong += 1
            time.sleep(min(1800, 300 * rong))
        else:
            rong = 0


# ------------------------------------------------------------------------------------------------ THU PYTHON
def vong_thu(toi_da: int) -> dict:
    from nhan import ong_dan as OD
    cn = ket_noi()
    cac = [t for t, _, _, _ in OD.cac_the(cn, "quyet_dinh")
           if t.get("duong_dich") in ("spec_dsl", "python_llm") and t.get("loai") == "he_hoan_thien"]
    so = PV.doc_so("thu_py")
    cac = [t for t in cac if not PV.cua_may_khac("thu_py", t["id"], MAY, so)]
    cac.sort(key=lambda t: (int(t.get("uu_tien", 9)), t["id"]), reverse=True)   # may nha (neu chay) lam tu dau
    chon = cac[:toi_da]
    PV.nhan("thu_py", [(t["id"], [t["id"]]) for t in chon], MAY)
    t0 = time.time()
    for t in chon:
        OD.buoc_toi_uu(cn, toi_da=1, chi_id=t["id"], in_ra=lambda s: ghi("thu", s))
    dem = OD.buoc_loc(cn, in_ra=lambda s: ghi("thu", s)) if chon else {}
    moi = sinh_viec_box(cn) if chon else 0
    cn.close()
    return {"cho": len(cac), "lam": len(chon), "giay": round(time.time() - t0, 1), "loc": dem, "viec_moi": moi}


def sinh_viec_box(cn) -> int:
    """sinh_mt5 cua ong dan, nhung ghi vao hang/thu muc cua box; khong sinh viec EA NGOAI; khong ghi VIEC_MT5.md chung."""
    from nhan import ong_dan as OD
    tam = LOG / "hang_tam.jsonl"
    cu = set()
    for p in (OD.RA / "hang_cho_mt5.jsonl", PV.HANG_BOX):
        if p.exists():
            cu |= {json.loads(x).get("ten") for x in p.read_text(encoding="utf-8").splitlines() if x.strip()}
    tam.write_text("".join(json.dumps({"ten": t}) + "\n" for t in sorted(cu if cu else [])), encoding="utf-8")
    g = (OD.HANG_CHO, OD.VIEC, OD.ghi_viec_md)
    OD.HANG_CHO, OD.VIEC, OD.ghi_viec_md = tam, PV.THU_MUC / "viec_mt5", (lambda *_a, **_k: None)
    try:
        OD.buoc_sinh_mt5(cn, in_ra=lambda s: ghi("thu", s), toi_da_ngoai=0)
    finally:
        OD.HANG_CHO, OD.VIEC, OD.ghi_viec_md = g
    moi = [x for x in tam.read_text(encoding="utf-8").splitlines() if x.strip() and json.loads(x).get("ten") not in cu]
    if moi:
        with open(PV.HANG_BOX, "a", encoding="utf-8") as f:
            for x in moi:
                v = json.loads(x)
                v["may_sinh"] = MAY
                f.write(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n")
    giu = {v.get("the_id") for v in PV.doc_hang_box()}
    for d in (PV.THU_MUC / "viec_mt5").glob("*"):          # bo thu muc cua the cu may nha (CHO_EA_GHEP) bi sinh lai
        if d.is_dir() and d.name not in giu:
            shutil.rmtree(d)
    return len(moi)


def chay_thu(toi_da: int = 4) -> None:
    while True:
        try:
            d = vong_thu(toi_da)
        except Exception as e:  # noqa: BLE001
            ghi("thu", "LOI vong: %s: %s" % (type(e).__name__, str(e)[:300]))
            time.sleep(120)
            continue
        ghi("thu", "VONG " + json.dumps(d, ensure_ascii=False))
        if not d["lam"]:
            time.sleep(300)


# ------------------------------------------------------------------------------------------------ DAY LEN GIT
def git(*a, cwd=WT, kiem=True):
    r = subprocess.run(["git"] + list(a), cwd=str(cwd), capture_output=True, text=True, timeout=600)
    if kiem and r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), (r.stderr or r.stdout)[-400:]))
    return r.stdout


def bao_cao() -> None:
    """reports/phan_viec/TRANG_THAI_BOX.md - chi so DO tu log."""
    def doc(ten):
        p = LOG / ("%s.jsonl" % ten)
        return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []
    vd = [json.loads(x["s"][5:]) for x in doc("dich") if x["s"].startswith("VONG ")]
    vt = [json.loads(x["s"][5:]) for x in doc("thu") if x["s"].startswith("VONG ")]
    so = PV.doc_so()
    hang = PV.doc_hang_box()
    L = ["# Thợ phụ box — trạng thái (tự sinh %s, giờ VN)" % time.strftime("%Y-%m-%d %H:%M"), "",
         "Số MÔ PHỎNG Python, PHÍ theo ống dẫn. Box không có MT5.", "",
         "- Đã nhận (NHAN_VIEC.jsonl): %d khoá" % len(so),
         "- Vòng dịch: %d; thẻ làm %d; gọi mới %d; ĐẠT %d; HỎNG %d; LỖI_LLM %d; 429 %d; giây %.0f" % (
             len(vd), sum(v.get("lam") or 0 for v in vd), sum(v.get("goi_moi") or 0 for v in vd),
             sum(v.get("dat") or 0 for v in vd), sum(v.get("hong") or 0 for v in vd),
             sum(v.get("loi_llm") or 0 for v in vd), sum(v.get("so_429") or 0 for v in vd), sum(v.get("giay") or 0 for v in vd)),
         "- Vòng thử Python: %d; thẻ %d; việc MT5 mới %d" % (len(vt), sum(v.get("lam") or 0 for v in vt),
                                                              sum(v.get("viec_moi") or 0 for v in vt)),
         "- Việc trong hang_cho_mt5_box.jsonl: %d" % len(hang), ""]
    for v in hang[-30:]:
        py = v.get("python") or {}
        L.append("  - `%s` %s %s %s: %s%%/năm, DD %s%%" % (v.get("ten"), v.get("san"), v.get("ma"), v.get("tf"),
                                                         py.get("lai_pct_nam"), py.get("sut_giam_pct")))
    (PV.THU_MUC / "TRANG_THAI_BOX.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def vong_day() -> str:
    bao_cao()
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "test_phan_viec.py"], cwd=str(GOC),
                       capture_output=True, text=True, timeout=600)
    if r.returncode:
        return "test TRUOT -> khong commit: %s" % r.stdout[-300:]
    git("add", "reports/phan_viec", "nhan/phan_viec.py", "test_phan_viec.py", "tho_box/tho_box.py")
    if not git("status", "--porcelain", "--", "reports/phan_viec", "nhan/phan_viec.py", "test_phan_viec.py",
               "tho_box/tho_box.py").strip():
        return "khong co gi moi"
    git("commit", "-m", "tho_box: so nhan viec + hang MT5 box (%s)" % time.strftime("%H:%M"))
    for _ in range(3):
        git("pull", "--rebase", "origin", "main")
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "test_phan_viec.py"], cwd=str(GOC),
                           capture_output=True, text=True, timeout=600)
        if r.returncode:
            return "test TRUOT sau rebase -> khong push: %s" % r.stdout[-300:]
        r = subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=str(WT), capture_output=True, text=True, timeout=600)
        if r.returncode == 0:
            return "da day " + git("rev-parse", "--short", "HEAD").strip()
        time.sleep(20)
    return "push loi: %s" % r.stderr[-300:]


def chay_day(chu_ky: int = 1200) -> None:
    while True:
        try:
            ghi("day", vong_day())
        except Exception as e:  # noqa: BLE001
            ghi("day", "LOI: %s: %s" % (type(e).__name__, str(e)[:300]))
        time.sleep(chu_ky)


if __name__ == "__main__":
    lenh = sys.argv[1] if len(sys.argv) > 1 else ""
    if not DB.exists():
        shutil.copy2(GOC / "data" / "may_nha_chup" / "trang_thai_nha.sqlite", DB)
    if lenh == "dich":
        chay_dich(int(os.environ.get("THO_BOX_LUONG", "4")))
    elif lenh == "thu":
        chay_thu()
    elif lenh == "day":
        chay_day()
    elif lenh == "mot_vong_dich":
        print(vong_dich(int(os.environ.get("THO_BOX_LUONG", "4")), int(os.environ.get("THO_BOX_BAM", "2"))))
    elif lenh == "mot_vong_thu":
        print(vong_thu(1))
    else:
        print(__doc__)
