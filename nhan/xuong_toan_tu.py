# -*- coding: utf-8 -*-
"""xuong_toan_tu.py - CAC TOAN TU SINH TO HOP cua XUONG (22/10/2026, Claude).

Mot TOAN TU nhan tap CHA (cac he dat / gan dat, da keo lot + phan ra) va tra ve danh sach UNG VIEN (the moi, chua do).
Moi ung vien la mot the tuong thich ong dan: `tin_hieu` (co the la kieu to hop cua `xuong_tin_hieu`) + mot phep thu {ma, khung, tham, ql}.
RANG BUOC THIET KE: ung vien chi co MOT chuoi lenh vao + MOT bo quan li (khong go cheo giua nguon), de xuat CSV lenh vao va MT5
(EA BRAIN_XuLiLenh, VAO_CSV) xac nhan duoc.

Toan tu:
  cay_quan_li     vao cua A  x  quan li cua B (nguyen tu quan li da dang). Ma tran cay cheo; uu tien A "TIN_HIEU_GANH" x B "QUAN_LI_GANH".
  bo_phieu        K-trong-N tin hieu cua cac cha CUNG (ma, khung), vao khi >= k dong y.
  chuyen_che_do   A khi che do thi truong BAT, B khi TAT (hoac A bi chan khi TAT): bien dong / xu huong / gio / thu / khoang.
  khoang_cach     bo bot lenh gan nhau cua mot cha.
  dao             dao chieu mot cha (kiem tra he vao SAI chieu: phan ra / thi truong co the cho thay chieu nguoc moi lai).
  dot_bien        dot bien CAU TRUC quan li (them / bo hedge, them trailing, doi kieu lot, doi do sau DCA) - luoi tham so khong lam duoc.
  lai_ghep        lai ghep quan li cua hai cha cung cap / cung hoc (uniform crossover + dot bien nho), vao lay tu mot trong hai.
  chuyen_ma       dat cha len ma / khung khac (chua co du lieu thi bo).
Cac toan tu khong tu do: tra ve toi da `tran` ung vien, ngau nhien co hat giong, khong trung (id = bam noi dung).
"""
from __future__ import annotations

import hashlib
import json
import random
import time

from nhan import xuong_may as XM
from nhan import xuong_tin_hieu as XT

TEN_TOAN_TU = ("cay_quan_li", "bo_phieu", "chuyen_che_do", "khoang_cach", "dao", "dot_bien", "lai_ghep", "chuyen_ma")

CHE_DO = [
    {"ten": "bien_dong", "n": 14, "cua_so": 500, "q": 0.5, "cao": True}, {"ten": "bien_dong", "n": 14, "cua_so": 500, "q": 0.5, "cao": False},
    {"ten": "bien_dong", "n": 14, "cua_so": 500, "q": 0.75, "cao": False},
    {"ten": "xu_huong", "n": 100, "x": 2.0, "cao": True}, {"ten": "xu_huong", "n": 100, "x": 2.0, "cao": False},
    {"ten": "xu_huong", "n": 200, "x": 1.5, "cao": False},
    {"ten": "gio", "tu": 7, "den": 16}, {"ten": "gio", "tu": 13, "den": 22}, {"ten": "gio", "tu": 0, "den": 8},
    {"ten": "thu", "ds": [0, 1, 2]}, {"ten": "thu", "ds": [2, 3, 4]},
    {"ten": "khoang", "n": 200, "tu": 0.0, "den": 0.5}, {"ten": "khoang", "n": 200, "tu": 0.5, "den": 1.0},
]

DOT_BIEN = {
    "them_hedge": lambda q: dict(q, hedge_khi_lo_pct=10.0, hedge_ti_le=1.0, mo_khoa_pct=0.005, hedge_max_lan=3),
    "bo_hedge": lambda q: dict(q, hedge_khi_lo_pct=0.0),
    "them_trailing": lambda q: dict(q, trail_kich_pct=0.002, trail_khoang_pct=0.001),
    "bo_trailing": lambda q: dict(q, trail_kich_pct=0.0),
    "lot_tuyen_tinh": lambda q: dict(q, dca_lot_tuyen_tinh=True, dca_toi_da=max(int(q.get("dca_toi_da") or 0), 3),
                                     dca_buoc_pct=q.get("dca_buoc_pct") or 0.005),
    "lot_deu": lambda q: dict(q, dca_lot_tuyen_tinh=False, dca_he_so_lot=1.0),
    "dca_sau_hon": lambda q: dict(q, dca_toi_da=min(int(q.get("dca_toi_da") or 0) + 3, 12), dca_buoc_pct=q.get("dca_buoc_pct") or 0.005),
    "dca_nong_hon": lambda q: dict(q, dca_toi_da=max(int(q.get("dca_toi_da") or 0) - 3, 0)),
    "buoc_rong": lambda q: dict(q, dca_buoc_pct=round((q.get("dca_buoc_pct") or 0.005) * 1.5, 5)) if q.get("dca_toi_da") else dict(q),
    "buoc_hep": lambda q: dict(q, dca_buoc_pct=round((q.get("dca_buoc_pct") or 0.005) / 1.5, 5)) if q.get("dca_toi_da") else dict(q),
    "tp_lon": lambda q: dict(q, tp_pct=round((q.get("tp_pct") or 0.003) * 1.6, 5)),
    "tp_nho": lambda q: dict(q, tp_pct=round((q.get("tp_pct") or 0.003) * 0.6, 5)),
}
TRUONG_LAI_GHEP = ("tp_pct", "dca_buoc_pct", "dca_toi_da", "dca_he_so_lot", "hedge_khi_lo_pct", "trail_kich_pct")


def tin_hieu_dong_goi(t: dict, thu: dict) -> dict:
    """tin_hieu cua the voi tham so TOT NHAT da chon nhet thang vao (kieu brain): de to hop khong phai mang theo `thu.tham` rieng."""
    th = json.loads(json.dumps(t["tin_hieu"]))
    if th.get("kieu") == "brain" and thu.get("tham"):
        th["tham"] = {**(th.get("tham") or {}), **thu["tham"]}
    th.pop("khoang", None)
    return th


def gan_ma(t: dict) -> bool:
    """The gan voi mot ma cu the (statement, lenh ngoai, EA ghi ro ma) -> khong cay sang ma khac."""
    th = t.get("tin_hieu") or {}
    return th.get("kieu") in ("lenh_ngoai",) or (isinstance(th.get("ma"), list) and th["ma"] and th.get("kieu") != "python_llm")


def the_moi(toan_tu: str, th: dict, ma: str, khung: str, ql: dict, cha: list[str], ten: str, tham: dict | None = None) -> dict:
    ql = XM.chuan_hoa_ql(ql)
    k = hashlib.sha1(json.dumps([th, ma, khung, tham or {}, ql], sort_keys=True, default=str).encode()).hexdigest()[:12]
    thu = {"ma": ma, "khung": khung, "tham": dict(tham or {}), "ql": ql}
    return {"id": "xg_" + k, "ten": ten[:150], "loai": "he_hoan_thien", "uu_tien": 2, "nen_tang": "XUONG", "duong_dich": "noi_bo",
            "tin_hieu": th, "nguon": {"kho": "xuong", "tep": ""}, "thanh_phan": list(cha), "ma_goi_y": [ma], "thu_goi_y": [thu],
            "xuong": {"toan_tu": toan_tu, "cha": list(cha), "mo_ta": XT.mo_ta(th)[:200], "luc": time.strftime("%Y-%m-%dT%H:%M:%S")},
            "_thu": thu}


class Cha:
    """Mot he cha: the + phep thu tot nhat da keo lot + nhan phan ra."""

    def __init__(self, t: dict, thu: dict, diem: float = 0.0, nhan: str | None = None):
        self.t, self.diem, self.nhan = t, diem, nhan
        self.id = t["id"]
        self.ma, self.khung = thu["ma"], thu["khung"]
        self.ql = {k: v for k, v in XM.chuan_hoa_ql(thu.get("ql")).items() if k != "lot_tren_1000"}     # lot duoc keo lai theo sut giam
        self.thu = {**thu, "ql": dict(self.ql), "tham": dict(thu.get("tham") or {})}

    def vao(self) -> dict:
        return tin_hieu_dong_goi(self.t, self.thu)


def _co_the_vao(c: Cha) -> bool:
    return (c.t.get("tin_hieu") or {}).get("kieu") not in ("lenh_ngoai", "luoi")


def _trong_so(c: Cha, nhan_mong: str) -> float:
    return (2.0 if c.nhan == nhan_mong else 1.0) + max(c.diem, 0.0) / 50.0


# ------------------------------------------------------------------------------------------------------------- toan tu
def cay_quan_li(cha: list[Cha], rng: random.Random, tran: int, atoms: list[dict] | None = None) -> list[dict]:
    """Vao cua A x quan li cua B. `atoms` = danh sach {"ql", "tu", "nhan"} (quan li da dang); mac dinh lay tu chinh cac cha."""
    vao = [c for c in cha if _co_the_vao(c)]
    atoms = atoms or [{"ql": c.ql, "tu": c.id, "nhan": c.nhan} for c in cha]
    ra, thay = [], set()
    if not vao or not atoms:
        return ra
    w_v = [_trong_so(c, "TIN_HIEU_GANH") for c in vao]
    w_q = [2.0 if a.get("nhan") == "QUAN_LI_GANH" else 1.0 for a in atoms]
    for _ in range(tran * 6):
        if len(ra) >= tran:
            break
        a = rng.choices(vao, w_v)[0]
        q = rng.choices(atoms, w_q)[0]
        if q["tu"] == a.id or XM.chuan_hoa_ql(q["ql"]) == a.ql:
            continue
        x = the_moi("cay_quan_li", a.vao(), a.ma, a.khung, q["ql"], [a.id, q["tu"]],
                    "Cấy: vào %s × quản lí %s" % (a.t.get("ten", a.id)[:40], str(q["tu"])[:30]))
        if x["id"] not in thay:
            thay.add(x["id"])
            ra.append(x)
    return ra


def _nhom_ma(cha: list[Cha]) -> dict:
    g = {}
    for c in cha:
        if _co_the_vao(c):
            g.setdefault((c.ma, c.khung), []).append(c)
    return g


def bo_phieu(cha: list[Cha], rng: random.Random, tran: int, **_) -> list[dict]:
    ra = []
    for (ma, kh), ds in _nhom_ma(cha).items():
        if len(ds) < 2:
            continue
        ds = sorted(ds, key=lambda c: -c.diem)
        for a in range(len(ds)):
            for b in range(a + 1, len(ds)):
                for cs in (2, 6):
                    th = {"kieu": "bo_phieu", "nguon": [ds[a].vao(), ds[b].vao()], "k": 2, "cua_so": cs}
                    ra.append(the_moi("bo_phieu", th, ma, kh, ds[a].ql, [ds[a].id, ds[b].id],
                                      "2/2 phiếu: %s + %s" % (ds[a].id[:20], ds[b].id[:20])))
        if len(ds) >= 3:
            for tri in [ds[i:i + 3] for i in range(0, min(len(ds) - 2, 3))]:
                for k in (2, 3):
                    th = {"kieu": "bo_phieu", "nguon": [c.vao() for c in tri], "k": k, "cua_so": 3}
                    ra.append(the_moi("bo_phieu", th, ma, kh, tri[0].ql, [c.id for c in tri], "%d/3 phiếu: %s…" % (k, tri[0].id[:20])))
    rng.shuffle(ra)
    return _bo_trung(ra)[:tran]


def chuyen_che_do(cha: list[Cha], rng: random.Random, tran: int, **_) -> list[dict]:
    ra = []
    for c in cha:
        if not _co_the_vao(c):
            continue
        for cd in rng.sample(CHE_DO, min(5, len(CHE_DO))):
            th = {"kieu": "chuyen_che_do", "a": c.vao(), "b": None, "che_do": cd}
            ra.append(the_moi("chuyen_che_do", th, c.ma, c.khung, c.ql, [c.id], "Chế độ %s: chỉ %s" % (cd["ten"], c.id[:24])))
    for (ma, kh), ds in _nhom_ma(cha).items():
        for a in ds:
            for b in ds:
                if a.id == b.id:
                    continue
                for cd in rng.sample(CHE_DO, min(3, len(CHE_DO))):
                    th = {"kieu": "chuyen_che_do", "a": a.vao(), "b": b.vao(), "che_do": cd}
                    ra.append(the_moi("chuyen_che_do", th, ma, kh, a.ql, [a.id, b.id],
                                      "Chế độ %s: %s ⇄ %s" % (cd["ten"], a.id[:18], b.id[:18])))
    rng.shuffle(ra)
    return _bo_trung(ra)[:tran]


def khoang_cach(cha: list[Cha], rng: random.Random, tran: int, **_) -> list[dict]:
    ra = []
    for c in cha:
        if _co_the_vao(c):
            for tt in (6, 24, 72):
                ra.append(the_moi("khoang_cach", {"kieu": "khoang_cach", "nguon": c.vao(), "toi_thieu": tt}, c.ma, c.khung, c.ql, [c.id],
                                  "Giãn %d nến: %s" % (tt, c.id[:30])))
    rng.shuffle(ra)
    return _bo_trung(ra)[:tran]


def dao(cha: list[Cha], rng: random.Random, tran: int, **_) -> list[dict]:
    ra = [the_moi("dao", {"kieu": "dao", "nguon": c.vao()}, c.ma, c.khung, c.ql, [c.id], "Đảo chiều: %s" % c.id[:40])
          for c in cha if _co_the_vao(c)]
    rng.shuffle(ra)
    return _bo_trung(ra)[:tran]


def dot_bien(cha: list[Cha], rng: random.Random, tran: int, **_) -> list[dict]:
    ra = []
    for c in cha:
        for ten, f in DOT_BIEN.items():
            q = f(dict(c.ql))
            if XM.chuan_hoa_ql(q) == c.ql:
                continue
            ra.append(the_moi("dot_bien", c.vao(), c.ma, c.khung, q, [c.id], "Đột biến %s: %s" % (ten, c.id[:30]),
                              tham=c.thu.get("tham")))
    rng.shuffle(ra)
    return _bo_trung(ra)[:tran]


def lai_ghep(cha: list[Cha], rng: random.Random, tran: int, **_) -> list[dict]:
    ra = []
    if len(cha) < 2:
        return ra
    for _i in range(tran * 4):
        if len(ra) >= tran:
            break
        a, b = rng.sample(cha, 2)
        if not _co_the_vao(a):
            continue
        q = dict(a.ql)
        for k in TRUONG_LAI_GHEP:
            if k in b.ql and rng.random() < 0.5:
                q[k] = b.ql[k]
        if q.get("dca_toi_da") and not q.get("dca_buoc_pct"):
            q["dca_buoc_pct"] = b.ql.get("dca_buoc_pct") or 0.005
        for k, f in (("tp_pct", 0.2), ("dca_buoc_pct", 0.2)):          # dot bien nho ±20 %
            if q.get(k) and rng.random() < 0.5:
                q[k] = round(q[k] * (1 + rng.uniform(-f, f)), 5)
        if XM.chuan_hoa_ql(q) in (a.ql, b.ql):
            continue
        ra.append(the_moi("lai_ghep", a.vao(), a.ma, a.khung, q, [a.id, b.id], "Lai: vào %s × quản lí lai %s" % (a.id[:24], b.id[:24]),
                          tham=a.thu.get("tham")))
    return _bo_trung(ra)[:tran]


def chuyen_ma(cha: list[Cha], rng: random.Random, tran: int, tai_san: list[tuple] | None = None, **_) -> list[dict]:
    """tai_san: danh sach (ma, khung) co du lieu."""
    ra = []
    for c in cha:
        if gan_ma(c.t) or not _co_the_vao(c):
            continue
        for ma, kh in (tai_san or []):
            if (ma, kh) != (c.ma, c.khung):
                ra.append(the_moi("chuyen_ma", c.vao(), ma, kh, c.ql, [c.id], "Chuyển %s: %s→%s %s" % (c.id[:24], c.ma, ma, kh),
                                  tham=c.thu.get("tham")))
    rng.shuffle(ra)
    return _bo_trung(ra)[:tran]


def _bo_trung(ds: list[dict]) -> list[dict]:
    thay, ra = set(), []
    for x in ds:
        if x["id"] not in thay:
            thay.add(x["id"])
            ra.append(x)
    return ra


TOAN_TU = {"cay_quan_li": cay_quan_li, "bo_phieu": bo_phieu, "chuyen_che_do": chuyen_che_do, "khoang_cach": khoang_cach, "dao": dao,
           "dot_bien": dot_bien, "lai_ghep": lai_ghep, "chuyen_ma": chuyen_ma}


def sinh(ten: str, cha: list[Cha], rng: random.Random, tran: int, **kw) -> list[dict]:
    return TOAN_TU[ten](cha, rng, tran, **kw)
