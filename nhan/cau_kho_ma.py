# -*- coding: utf-8 -*-
"""CAU KHO MA: kho ma nguon SEEKER -> bo doc MQL5 cau truc (`doc_ma`) -> vong lap.

VI SAO CO FILE NAY (11/10/2026).

SEEKER da thu ve kho ma nguon that (bao cao 14/09: 1.308 ban `ma_nguon`,
27,6 trieu ky tu; 05/09: 389 artifact `code`, trong do 82 file la chien luoc
dat lenh). Nhung tu do toi nay kho do CHI duoc doc bang hai duong cu:

  - `bien_dich_ung_vien`: khop TU KHOA vao mau co san (`nhan/mau.py`) - khong
    doc dieu kien that cua EA;
  - `boc_ma_llm`: LLM boc (phan_loai_ma do: 32% file ra co che, khong tat dinh).

Con bo doc MQL5 cau truc `nhan/doc_ma.doc_chien_luoc` - tat dinh, chi dich khi
chac, da do 59,1% tren `mau_thu` va 38,2% tren 34 diem vao ngoai - thi chua tung
chay tren kho cua SEEKER. Va `vong_thu_nghiem.py` chi doc thu muc `mau_thu/`.
Tuc vong "quet dau vao -> boc -> kiem -> giu" bi DUT o ngay khau dau: cai SEEKER
quet ve khong bao gio toi duoc vong lap.

File nay noi khau do, va chi lam dung bon viec:

  1. GOM: doc ma MQL5 tu so cai (artifact `code`, `noi_dung` kieu `ma_nguon`)
     hoac tu mot thu muc `.mq5` (vd thu muc SEEKER tai ve).
  2. KHU TRUNG theo van tay NOI DUNG da chuan hoa (bo chu thich, khoang trang),
     khong theo ten/URL: cung mot EA dang lai nhieu noi chi duoc dem MOT lan, va
     file trung voi `mau_thu/` khong duoc dem lai (tranh tu cham diem bang dap an).
  3. PHAN LAN + DO: `phan_loai_ma.phan_loai_mot` (chi bao / chien luoc / quan
     tri / tien ich), bo MQL4 (bo doc chi hieu MQL5 - ghi ro, khong dem la that
     bai cua bo doc), roi `doc_ma.doc_chien_luoc` tren moi EA dat lenh. So do
     CUNG dinh nghia voi `mau_thu/do_moc.py`: diem vao dich duoc / diem vao tim
     thay.
  4. XUAT: EA ra >= 1 co che duoc chep sang thu muc `--xuat` kem `NGUON.json`
     (provenance: url, revision, van tay) de chay
     `python vong_thu_nghiem.py --mau <thu_muc>`. Cong giu cua vong lap KHONG
     doi - file nay khong noi long gi, chi them dau vao.

RANH GIOI (giong `ma_nguon.py`, `doc_ma.py`): CHI DOC VAN BAN. Khong chay,
khong bien dich, khong import ma tai ve. So cai chi DOC (khong ghi). Bo doc
khong duoc chinh cho vua kho nay: kho la phep do tong quat hoa, khong phai dap an.

    python -m nhan.cau_kho_ma --tu-so                     # kho trong nao.db
    python -m nhan.cau_kho_ma --thu-muc DIR [--thu-muc DIR2]
    python -m nhan.cau_kho_ma --tu-so --xuat data/seeker_mq5 --bao-cao reports/CAU_KHO_MA.md
    python -m nhan.cau_kho_ma --tai-mql5 data/seeker_tho --so-trang 3 --xuat data/seeker_mq5
        # khong co nao.db (cloud/Linux): quet MQL5 Code Base bang bo tai cua SEEKER
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))

from nhan import doc_ma as DM                    # noqa: E402
from nhan import phan_loai_ma as PL              # noqa: E402

#: Tran kich thuoc (ky tu) - cung y nghia `ma_nguon.TRAN_BYTE`: tren muc nay
#: gan nhu chac la thu vien dinh kem, doc_ma tren no chi ton thoi gian.
TRAN_KY_TU = 400_000
SAN_KY_TU = 200

#: Dau hieu MQL4 (khong co trong MQL5). Bo doc chi hieu MQL5: file MQL4 duoc bo
#: qua co GHI LY DO, khong bi dem la "bo doc that bai".
_MQL4 = re.compile(r"\b(OP_BUY|OP_SELL|OP_BUYSTOP|OP_SELLSTOP|MODE_TRADES|SELECT_BY_POS"
                   r"|MODE_HISTORY)\b|\bint\s+start\s*\(\s*\)")
_MQL5 = re.compile(r"\bCTrade\b|\bMqlTradeRequest\b|\bORDER_TYPE_(BUY|SELL)\b"
                   r"|\bPositionsTotal\s*\(|\bCopyBuffer\s*\(|\bOnTick\s*\(")
_CHU_THICH = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)


def van_tay(src: str) -> str:
    """Van tay NOI DUNG: bo chu thich + moi khoang trang, sha1 16 ky tu.

    Hai ban chi khac chu thich / thut dong / ban quyen dau file la MOT EA.
    (Chuoi chua `//` - vd URL trong Print - cung bi cat; chi anh huong van tay,
    khong anh huong noi dung dem di doc.)
    """
    s = src.replace("\r\n", "\n").lstrip("\ufeff")
    s = _CHU_THICH.sub("", s)
    s = re.sub(r"\s+", "", s)
    return hashlib.sha1(s.encode("utf-8", "ignore")).hexdigest()[:16]


def la_mql4(src: str) -> bool:
    """MQL4 khi co hang/ham chi MQL4 co ma KHONG co dau hieu MQL5 nao.

    File lai (vd `#ifdef __MQL4__`) co dau hieu MQL5 -> van coi la MQL5.
    """
    return bool(_MQL4.search(src)) and not _MQL5.search(src)


# ---------------------------------------------------------------- GOM ----
def _ban_ghi(ten: str, src: str, url: str = "", revision: str = "",
             nguon: str = "") -> dict:
    return {"ten": ten, "src": src, "url": url, "revision": revision,
            "nguon": nguon}


def gom_tu_so(so=None) -> list[dict]:
    """Doc ma MQL5 tu so cai: artifact `code` + `noi_dung` kieu `ma_nguon*`.

    Chi DOC. `so` mac dinh la `nhan.so` (nao.db); test truyen so gia.
    """
    if so is None:
        from nhan import so as so
    ra = []
    try:
        hang = so.nhieu("SELECT id,payload FROM artifact WHERE artifact_type='code'")
    except Exception:
        hang = []
    for x in hang:
        try:
            p = json.loads(x["payload"])
        except Exception:
            continue
        con = p.get("payload") or p
        src = con.get("content") or ""
        if not isinstance(src, str):
            continue
        duong = str(con.get("path") or con.get("ten") or x["id"])
        ra.append(_ban_ghi(duong, src, str(con.get("repository_url") or ""),
                           str(con.get("revision") or ""), "artifact:%s" % x["id"]))
    try:
        hang = so.nhieu("SELECT id,url,kieu,van_ban FROM noi_dung "
                        "WHERE kieu LIKE 'ma_nguon%' AND van_ban IS NOT NULL")
    except Exception:
        hang = []
    for x in hang:
        src = x["van_ban"] or ""
        url = x["url"] or ""
        # chi giu thu trong giong ma MQL (noi_dung con chua ma Pine/Python)
        if not re.search(r"\bOnTick\s*\(|\bOnInit\s*\(|#property\s", src):
            continue
        ten = url.rstrip("/").rsplit("/", 1)[-1] or ("noi_dung_%s" % x["id"])
        ra.append(_ban_ghi(ten, src, url, "", "noi_dung:%s" % x["id"]))
    return ra


def gom_tu_thu_muc(thu_muc) -> list[dict]:
    """Moi file `.mq5`/`.mq4` duoi `thu_muc` (de quy). `.mqh` la header - bo."""
    goc = Path(thu_muc)
    ra = []
    for p in sorted(goc.rglob("*")):
        if p.suffix.lower() not in (".mq5", ".mq4") or not p.is_file():
            continue
        b = p.read_bytes()
        if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
            src = b.decode("utf-16", "ignore")          # MetaEditor hay luu UTF-16
        else:
            src = b.decode("utf-8", "ignore")
        ra.append(_ban_ghi(str(p.relative_to(goc)), src, "", "", "tep:%s" % p))
    return ra


def tai_mql5(thu_muc, so_trang: int = 1, muc: str = "experts", nghi_giay: float = 1.5,
             in_ra=print, han_giay: float | None = None, trang_dau: int = 1) -> dict:
    """QUET DAU VAO KHONG CAN nao.db: MQL5 Code Base -> `thu_muc/<id>_<ten>.mq5`.

    Dung CHINH bo tai cua SEEKER (`ma_nguon.liet_ke_mql5` + `tai_ma_nguon`: chi
    file don .mq5/.mq4, khong giai nen zip, co tran/san kich thuoc), nen chay
    duoc tren cloud/Linux noi `nao.db` trong. Bai da co file (theo so bai) thi
    BO QUA - chay lai chi lay bai moi. Provenance ghi vao `NGUON_TAI.json`.
    Chi ghi file van ban trong `thu_muc`; khong chay gi. `han_giay`: tran thoi
    gian (het thi dung, ghi `het_gio`; bai chua tai se lay o luot sau).
    """
    from nhan import ma_nguon as MN
    d = Path(thu_muc)
    d.mkdir(parents=True, exist_ok=True)
    pm = d / "NGUON_TAI.json"
    try:
        man = json.loads(pm.read_text(encoding="utf-8")) if pm.exists() else {}
    except Exception:
        man = {}
    co = {p.name.split("_", 1)[0] for p in d.glob("*.mq[45]")}
    bao = Counter()
    het = (time.time() + han_giay) if han_giay else None
    for trang in range(max(1, trang_dau), max(1, trang_dau) + max(1, so_trang)):
        if het is not None and time.time() >= het:
            bao["het_gio"] += 1                     # tran thoi gian: luot sau lam tiep
            break
        ds = MN.liet_ke_mql5(muc, trang)
        bao["trang"] += 1
        if not ds:
            break
        for b in ds:
            bao["thay"] += 1
            if str(b["id"]) in co or str(b["id"]) in man:
                bao["da_co"] += 1
                continue
            if het is not None and time.time() >= het:
                bao["het_gio"] += 1
                break
            if nghi_giay:
                time.sleep(nghi_giay)
            r = MN.tai_ma_nguon(b)
            if not r:
                bao["khong_tai_duoc"] += 1
                man[str(b["id"])] = {**b, "ok": False}
                continue
            ten = "%s_%s" % (b["id"], re.sub(r"[^A-Za-z0-9_.-]+", "_", r["ten_file"])[:80])
            (d / ten).write_text(r["noi_dung"], encoding="utf-8")
            co.add(str(b["id"]))
            man[str(b["id"])] = {**b, "ok": True, "file": ten, "so_byte": r["so_byte"],
                                 "luc": time.strftime("%Y-%m-%d %H:%M:%S")}
            bao["moi"] += 1
    pm.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    in_ra("tai_mql5 %s: %s" % (muc, dict(bao)))
    return dict(bao)


def _url_tu_nguon_tai(ban_ghi: list[dict], thu_muc) -> None:
    """Gan url/revision tu `NGUON_TAI.json` cho file tai bang `tai_mql5`."""
    pm = Path(thu_muc) / "NGUON_TAI.json"
    if not pm.exists():
        return
    try:
        man = json.loads(pm.read_text(encoding="utf-8"))
    except Exception:
        return
    theo_file = {v.get("file"): v for v in man.values() if v.get("ok")}
    for b in ban_ghi:
        v = theo_file.get(Path(b["ten"]).name)
        if v and not b["url"]:
            b["url"] = v.get("url", "")
            b["revision"] = "mql5-code-%s" % v.get("id", "")


# ---------------------------------------------------------------- DO -----
def _van_tay_mau_thu() -> set:
    """Van tay cua `mau_thu/**.mq5` - file trung thi KHONG dem lai."""
    mau = LAB / "mau_thu"
    return {van_tay(p.read_text(encoding="utf-8", errors="ignore"))
            for p in mau.rglob("*.mq5")}


#: Module ma ket qua `doc_chien_luoc` phu thuoc - doi mot file la doc lai ca kho.
_MODULE_BO_DOC = ("doc_ma", "chot_mql", "fss_mql", "goi_ham_mql", "ro_mql", "ngu_phap",
                  "thu_hoi_thanh_phan", "phan_loai_ma")


def phien_ban_bo_doc() -> str:
    """Van tay ma nguon bo doc (sha1 16 ky tu) - khoa cua bo nho dem `do_kho`."""
    h = hashlib.sha1()
    for ten in _MODULE_BO_DOC:
        p = LAB / "nhan" / f"{ten}.py"
        if p.exists():
            h.update(p.read_bytes())
    return h.hexdigest()[:16]


def _tom_tat_doc(d: dict) -> dict:
    return {k: d.get(k) for k in ("co_che", "so_vao_lenh", "so_vao_lenh_co_co_che",
                                  "phan_loai_vao_lenh", "chua_dien_dat_duoc")}


def do_kho(ban_ghi: list[dict], bo_mau_thu: bool = True, bo_nho: dict | None = None) -> dict:
    """Pheu: tong -> trung -> co/kich thuoc -> MQL4 -> lan -> doc_ma.

    Tra dict co `pheu`, `lan`, `so` (cung dinh nghia `do_moc`), `ly_do`, `ds`
    (moi file mot dong, khong kem ma nguon) va `xuat` (file ra >= 1 co che,
    KEM ma nguon de chep ra).

    `bo_nho` (tuy chon, cho tru chay dinh ky): dict `van_tay@phien_ban_bo_doc ->
    tom tat doc_chien_luoc`. File da doc bang CUNG ma bo doc khong doc lai; doi
    bo doc (khoa khac) thi doc lai ca kho. So do ra GIONG HET khong dung bo nho.
    """
    pb = phien_ban_bo_doc() if bo_nho is not None else ""
    pheu = Counter()
    lan = Counter()
    loai = Counter()
    ly_do = Counter()
    thoat = Counter()
    so = Counter()
    ds, xuat = [], []
    da = {}
    mau = _van_tay_mau_thu() if bo_mau_thu else set()
    for b in ban_ghi:
        pheu["tong"] += 1
        src = b["src"] or ""
        if not (SAN_KY_TU <= len(src) <= TRAN_KY_TU):
            pheu["bo_kich_thuoc"] += 1
            continue
        vt = van_tay(src)
        if vt in da:
            pheu["trung_noi_dung"] += 1
            da[vt]["ban_sao"] += 1
            continue
        dong = {"ten": b["ten"], "url": b["url"], "revision": b["revision"],
                "nguon": b["nguon"], "van_tay": vt, "ban_sao": 0}
        da[vt] = dong
        if vt in mau:
            pheu["trung_mau_thu"] += 1
            dong["ket_qua"] = "trung_mau_thu"
            ds.append(dong)
            continue
        pheu["duy_nhat"] += 1
        if la_mql4(src):
            pheu["mql4_bo_qua"] += 1
            dong["ket_qua"] = "mql4_bo_qua"
            ds.append(dong)
            continue
        z = PL.phan_loai_mot(src, b["ten"])
        lan[z["lan"]] += 1
        dong["lan"] = z["lan"]
        if not z["bang_dau_hieu"].get("dat_lenh") or z["lan"] == PL.CHI_BAO:
            dong["ket_qua"] = "khong_dat_lenh"
            ds.append(dong)
            continue
        pheu["ea_dat_lenh"] += 1
        t0 = time.time()
        khoa = f"{vt}@{pb}"
        try:
            if bo_nho is not None and khoa in bo_nho:
                d = bo_nho[khoa]
                pheu["tu_bo_nho"] += 1
            else:
                d = DM.doc_chien_luoc(src, nguon=b["ten"])
                if bo_nho is not None:
                    bo_nho[khoa] = json.loads(json.dumps(_tom_tat_doc(d), default=str))
        except Exception as e:              # loi bo doc = tin hieu sua, khong nuot
            pheu["loi_bo_doc"] += 1
            dong["ket_qua"] = "loi_bo_doc"
            dong["loi"] = "%s: %s" % (type(e).__name__, str(e)[:160])
            ds.append(dong)
            continue
        dong["giay"] = round(time.time() - t0, 2)
        cc = d.get("co_che", []) or []
        vl = int(d.get("so_vao_lenh", 0) or 0)
        vc = int(d.get("so_vao_lenh_co_co_che", 0) or 0)
        so["vao_lenh"] += vl
        so["vao_co"] += vc
        so["co_che"] += len(cc)
        for k, v in (d.get("phan_loai_vao_lenh") or {}).items():
            loai[k] += v
        for x in d.get("chua_dien_dat_duoc", []) or []:
            ly_do[str(x)[:70]] += 1
        for sp in cc:
            k_ra = "ro" if sp.get("ro") else "sltp" if sp.get("sltp") else \
                "dk_ra" if sp.get("ra") else "dong_pip" if sp.get("dong_mo_pip") else \
                "giu_co_dinh"
            thoat[k_ra] += 1
        dong.update({"vao_lenh": vl, "vao_co": vc, "co_che": len(cc),
                     "ho": sorted({sp.get("ho", "") for sp in cc})})
        if vl:
            pheu["co_diem_vao"] += 1
        if cc:
            pheu["ra_co_che"] += 1
            dong["ket_qua"] = "ra_co_che"
            xuat.append({**dong, "src": src})
        else:
            dong["ket_qua"] = "chua_dich" if vl else "khong_thay_diem_vao"
        ds.append(dong)
    return {"pheu": dict(pheu), "lan": dict(lan), "loai_vao_lenh": dict(loai),
            "so": dict(so), "ly_do": dict(ly_do.most_common(15)),
            "thoat": dict(thoat), "ds": ds, "xuat": xuat}


def ty_le(r: dict) -> float | None:
    """Diem vao dich duoc / diem vao tim thay (dinh nghia `do_moc`). None = chua do."""
    vl = r["so"].get("vao_lenh", 0)
    return (r["so"].get("vao_co", 0) / vl) if vl else None


# ---------------------------------------------------------------- XUAT ---
def _ten_an_toan(ten: str) -> str:
    goc = Path(ten.replace("\\", "/")).name
    goc = re.sub(r"[^A-Za-z0-9_.-]+", "_", goc)[:80] or "ea"
    return goc if goc.lower().endswith(".mq5") else goc + ".mq5"


def xuat(r: dict, thu_muc) -> Path:
    """Chep EA ra co che vao `thu_muc` + `NGUON.json`. Ten = <van_tay>_<ten>.mq5.

    Chi ghi trong `thu_muc` (tao neu chua co); file cu cung van tay bi ghi de
    bang dung noi dung do (idempotent). Khong xoa gi.
    """
    d = Path(thu_muc)
    d.mkdir(parents=True, exist_ok=True)
    nguon = []
    for x in r["xuat"]:
        ten = "%s_%s" % (x["van_tay"], _ten_an_toan(x["ten"]))
        (d / ten).write_text(x["src"], encoding="utf-8")
        nguon.append({k: x[k] for k in ("ten", "url", "revision", "nguon", "van_tay",
                                        "vao_lenh", "vao_co", "co_che", "ho")}
                     | {"file": ten})
    p = d / "NGUON.json"
    p.write_text(json.dumps(nguon, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


# ---------------------------------------------------------------- IN -----
def bao_cao_md(r: dict, tieu_de: str = "") -> str:
    P, S = r["pheu"], r["so"]
    tl = ty_le(r)
    L = ["# CAU KHO MA - kho SEEKER qua bo doc MQL5 cau truc (`doc_ma`)",
         "*%s*  %s" % (time.strftime("%Y-%m-%d %H:%M"), tieu_de), "",
         "## Pheu", "",
         "| buoc | so |", "|---|---|"]
    for k in ("tong", "bo_kich_thuoc", "trung_noi_dung", "trung_mau_thu", "duy_nhat",
              "mql4_bo_qua", "ea_dat_lenh", "loi_bo_doc", "co_diem_vao", "ra_co_che"):
        L.append("| %s | %d |" % (k, P.get(k, 0)))
    L += ["", "## Lan (phan_loai_ma, file duy nhat MQL5)", ""]
    L += ["- %s: %d" % (k, v) for k, v in sorted(r["lan"].items(), key=lambda x: -x[1])]
    L += ["", "## So chinh (cung dinh nghia `mau_thu/do_moc.py`)", "",
          "- diem vao tim thay: %d" % S.get("vao_lenh", 0),
          "- diem vao dich duoc: %d  -> **%s**" % (
              S.get("vao_co", 0), "chua do" if tl is None else "%.1f%%" % (100 * tl)),
          "- co che ra: %d (tu %d EA)" % (S.get("co_che", 0), P.get("ra_co_che", 0)),
          "- phan loai diem vao: %s" % json.dumps(r["loai_vao_lenh"], ensure_ascii=False),
          "- loi ra theo EA: %s" % json.dumps(r["thoat"], ensure_ascii=False),
          "", "## Ly do chua dich (top)", ""]
    L += ["- %dx `%s`" % (v, k) for k, v in r["ly_do"].items()]
    L += ["", "## EA ra co che", ""]
    for x in r["xuat"]:
        L.append("- `%s` vao %d/%d, co che %d, ho %s %s" % (
            x["ten"], x["vao_co"], x["vao_lenh"], x["co_che"], ",".join(x["ho"]),
            x["url"]))
    loi = [x for x in r["ds"] if x.get("ket_qua") == "loi_bo_doc"]
    if loi:
        L += ["", "## Loi bo doc (can sua doc_ma)", ""]
        L += ["- `%s`: %s" % (x["ten"], x["loi"]) for x in loi]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Kho ma SEEKER -> doc_ma -> vong lap")
    ap.add_argument("--tu-so", action="store_true", help="doc kho trong nao.db (chi doc)")
    ap.add_argument("--thu-muc", action="append", default=[],
                    help="thu muc .mq5 (lap lai duoc)")
    ap.add_argument("--tai-mql5", metavar="DIR",
                    help="QUET truoc: tai bai MOI tu MQL5 Code Base vao DIR (bo qua bai da co)")
    ap.add_argument("--so-trang", type=int, default=1, help="so trang danh sach cho --tai-mql5")
    ap.add_argument("--muc", default="experts", help="danh muc MQL5 Code Base (experts)")
    ap.add_argument("--xuat", help="chep EA ra co che vao day (+ NGUON.json)")
    ap.add_argument("--bao-cao", help="ghi bao cao markdown vao file nay")
    ap.add_argument("--json", help="ghi ket qua (khong kem ma nguon) ra file nay")
    ap.add_argument("--giu-mau-thu", action="store_true",
                    help="KHONG bo file trung mau_thu (mac dinh bo)")
    a = ap.parse_args(argv)
    if not a.tu_so and not a.thu_muc and not a.tai_mql5:
        ap.error("can --tu-so, --thu-muc hoac --tai-mql5")
    bg = []
    if a.tu_so:
        bg += gom_tu_so()
    if a.tai_mql5:
        a.thu_muc.append(a.tai_mql5)
        tai_mql5(a.tai_mql5, so_trang=a.so_trang, muc=a.muc)
    for t in a.thu_muc:
        g = gom_tu_thu_muc(t)
        _url_tu_nguon_tai(g, t)
        bg += g
    r = do_kho(bg, bo_mau_thu=not a.giu_mau_thu)
    md = bao_cao_md(r, " + ".join((["nao.db"] if a.tu_so else []) + a.thu_muc))
    print(md)
    if a.xuat:
        print("xuat:", xuat(r, a.xuat), "(%d EA) -> python vong_thu_nghiem.py --mau %s"
              % (len(r["xuat"]), a.xuat))
    if a.bao_cao:
        Path(a.bao_cao).write_text(md, encoding="utf-8")
    if a.json:
        Path(a.json).write_text(json.dumps({k: v for k, v in r.items() if k != "xuat"},
                                           ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
