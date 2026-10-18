# -*- coding: utf-8 -*-
"""nhap_tay.py - THU MUC NHAP TAY cua chu du an (18/10/2026).

Trang bi chan (Cloudflare, captcha, can dang nhap, render JS) thi KHONG vuot: chu du an tu mo bang Chrome cua minh, roi luu
vao thu muc nhap tay (vd tren may nha `E:\\brain2_nhap\\`). Cac loai nhan duoc:
  - EA / chi bao / thu vien: .mq4 .mq5 .mqh (va .ex4/.ex5 chi co ban bien dich -> chay thang MT5);
  - bo thong so: .set (gan voi EA cung ten neu co);
  - statement / bao cao tester: .htm .html (MT4 statement, MT5 report) -> danh sach lenh + dau hieu xu li lenh;
  - trang HTML luu tu trinh duyet -> tach khoi ma MQL (OnTick/OnInit) neu co, khong thi ghi la mo ta;
  - Python / Pine: .py .pine .txt (Pine) -> duong LLM.
Ham o day CHI DOC VAN BAN, khong bao gio chay ma nhap vao. Ma cua nguoi khac khong vao git: ban tach ra ghi vao
`data/nhap_tay/_tach/` (git bo qua). Thu muc cau hinh: bien moi truong BRAIN_NHAP_TAY (nhieu thu muc cach nhau `;`), neu
khong co thi `thu_muc_nhap_tay` trong config/ong_dan.json.
"""
from __future__ import annotations

import hashlib
import html as H
import json
import os
import re
from pathlib import Path

import pandas as pd

GOC = Path(__file__).resolve().parent.parent
TACH = GOC / "data" / "nhap_tay" / "_tach"
DUOI = {".mq4": "MQL4", ".mq5": "MQL5", ".mqh": "MQL5", ".ex4": "MQL4_EX", ".ex5": "MQL5_EX", ".set": "SET",
        ".htm": "HTML", ".html": "HTML", ".py": "Python", ".pine": "TradingView", ".txt": "TXT", ".csv": "CSV",
        ".zip": "ZIP"}
TRAN_BYTE = 20 * 1024 * 1024
_TG = r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}(?::\d{2})?)"


#: Thu muc nhap tay mac dinh. `data/seeker_da_nguon/nhap_tay/<nguon>/<id>.<duoi>` la quy uoc cua tac vu Seeker da nguon
#: (reports/URL_BI_CHAN.md) - o day CHI DOC, khong ghi vao do.
MAC_DINH = ["E:\\brain2_nhap", "data/nhap_tay", "data/seeker_da_nguon/nhap_tay"]


def thu_muc(cfg: dict | None = None) -> list[Path]:
    """Danh sach thu muc nhap tay dang ton tai (env BRAIN_NHAP_TAY > config)."""
    env = os.environ.get("BRAIN_NHAP_TAY")
    ds = env.split(";") if env else list((cfg or {}).get("thu_muc_nhap_tay") or MAC_DINH)
    ra = []
    for x in ds:
        x = x.strip()
        if not x:
            continue
        p = Path(x)
        if not p.is_absolute():
            p = GOC / p
        if p.exists() and p.is_dir():
            ra.append(p)
    return ra


def doc_vb(b: bytes) -> str:
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return b.decode("utf-16", errors="ignore")
    if len(b) > 8 and b[1:8:2] == b"\x00\x00\x00\x00":
        return b.decode("utf-16-le", errors="ignore")
    return b.decode("utf-8", errors="ignore")


def doc_set(vb: str) -> dict:
    """.set MT4/MT5 -> {ten: gia tri dau} (bo phan ||start||step||stop||Y)."""
    d = {}
    for dong in vb.splitlines():
        dong = dong.strip()
        if not dong or dong.startswith(";") or "=" not in dong:
            continue
        k, v = dong.split("=", 1)
        d[k.strip()] = v.split("||")[0].strip()
    return d


def _o(row: str) -> list[str]:
    return [H.unescape(re.sub(r"<[^>]+>", "", c)).strip().replace("\xa0", " ")
            for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S | re.I)]


def _so(x: str) -> float | None:
    try:
        return float(str(x).split("/")[0].replace(" ", ""))
    except ValueError:
        return None


def _tg(x: str):
    return pd.to_datetime(str(x).replace(".", "-", 2), errors="coerce")


_COT = ["luc", "het", "ma", "chieu", "lot", "gia", "gia_dong"]
_DONG_MT4 = ("close", "t/p", "s/l", "close at stop", "so", "stop out")


def doc_lenh_html(vb: str) -> pd.DataFrame:
    """Statement / report -> lenh VAO [luc, het, ma, chieu, lot, gia, gia_dong] (het/gia_dong neu biet). Ho tro:
    MT5 report (Deals: Time | Deal | Symbol | Type | Direction | Volume | Price ...; out khop FIFO theo chieu, kieu hedging),
    MT4 statement (Ticket | Open Time | Type | Size | Item | Price | S/L | T/P | Close Time | Price ...),
    MT4 tester report (# | Time | Type | Order | Size | Price | S/L | T/P | Profit | Balance; symbol o dau bao cao).
    Khong nhan ra -> rong."""
    hang, mo, ve = [], {}, {}
    sym_bc = ""
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", vb, re.S | re.I):
        c = _o(row)
        if len(c) >= 2 and c[0].strip(":").lower() == "symbol" and not sym_bc:
            sym_bc = (c[1].split() or [""])[0]
            continue
        if len(c) < 6:
            continue
        if re.fullmatch(_TG, c[0]) and len(c) >= 7 and c[3].lower() in ("buy", "sell") and c[4].lower() in ("in", "out", "inout"):
            ch = 1 if c[3].lower() == "buy" else -1
            lot = _so(c[5]) or 0.0
            g = _so(c[6]) if len(c) > 6 else None
            if c[4].lower() in ("out", "inout"):
                con = lot                       # deal out chieu `ch` dong vi the chieu nguoc lai, FIFO
                q = mo.get((c[2], -ch), [])
                while con > 1e-9 and q:
                    k, l = q[0]
                    d = min(con, l)
                    con -= d
                    q[0][1] -= d
                    if q[0][1] <= 1e-9:
                        hang[k]["het"] = _tg(c[0])
                        hang[k]["gia_dong"] = g
                        q.pop(0)
            if c[4].lower() in ("in", "inout"):
                hang.append({"luc": _tg(c[0]), "het": pd.NaT, "ma": c[2], "chieu": ch, "lot": lot, "gia": g, "gia_dong": None})
                mo.setdefault((c[2], ch), []).append([len(hang) - 1, lot])
            continue
        if re.fullmatch(r"\d+", c[0]) and re.fullmatch(_TG, c[1]) and len(c) >= 6 and _so(c[4]) is not None \
                and re.fullmatch(r"\d+", c[3] or "x"):
            k = c[2].lower()                    # MT4 tester report
            if k in ("buy", "sell"):
                ve[c[3]] = len(hang)
                hang.append({"luc": _tg(c[1]), "het": pd.NaT, "ma": sym_bc or "?", "chieu": 1 if k == "buy" else -1,
                             "lot": _so(c[4]), "gia": _so(c[5]), "gia_dong": None})
            elif k in _DONG_MT4 and c[3] in ve and pd.isna(hang[ve[c[3]]]["het"]):
                hang[ve[c[3]]]["het"] = _tg(c[1])
                hang[ve[c[3]]]["gia_dong"] = _so(c[5])
            continue
        if re.fullmatch(r"\d+", c[0]) and re.fullmatch(_TG, c[1]) and c[2].lower() in ("buy", "sell"):
            het = _tg(c[8]) if len(c) > 8 and re.fullmatch(_TG, c[8]) else pd.NaT
            hang.append({"luc": _tg(c[1]), "het": het, "ma": c[4], "chieu": 1 if c[2].lower() == "buy" else -1,
                         "lot": _so(c[3]), "gia": _so(c[5]) if len(c) > 5 else None,
                         "gia_dong": _so(c[9]) if len(c) > 9 else None})
    if not hang:
        return pd.DataFrame(columns=_COT)
    df = pd.DataFrame(hang)
    return df.dropna(subset=["luc"]).sort_values("luc").reset_index(drop=True)


def so_tac_gia_bao_cao(vb: str) -> dict:
    """So TONG HOP tac gia ghi trong bao cao (von dau, lai rong, sut giam, ky, khung) - SO TAC GIA, chua do."""
    o = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", vb[:400000], re.S | re.I):
        o += [x for x in _o(row) if x]
    ra = {}
    nhan = {"von_dau": ("initial deposit", "depósito inicial", "начальный депозит"),
            "lai_rong": ("total net profit", "beneficio neto", "чистая прибыль"),
            "sut_giam": ("maximal drawdown", "equity drawdown maximal", "reducción máxima de la equidad",
                         "максимальная просадка средств", "balance drawdown maximal"),
            "ky": ("period", "período", "период"), "pf": ("profit factor", "factor de beneficio", "прибыльность"),
            "so_lenh": ("total trades", "total de operaciones ejecutadas", "всего трейдов"),
            "ma": ("symbol", "símbolo", "символ")}
    for i, x in enumerate(o[:-1]):
        l = x.strip(":").strip().lower()
        for k, ds in nhan.items():
            if k not in ra and l in ds:
                ra[k] = o[i + 1]
    m = re.search(r"\((M\d+|H\d+|D1|W1|MN1?)\)|^(M\d+|H\d+|D1)\b", ra.get("ky", ""))
    if m:
        ra["khung"] = m.group(1) or m.group(2)
    m = re.findall(r"(\d{4}\.\d{2}\.\d{2})", ra.get("ky", ""))
    if len(m) >= 2:
        ra["tu"], ra["den"] = m[0], m[1]
    if ra:
        ra["nhan"] = "SỐ TÁC GIẢ (chưa đo)"
    return ra


def doc_lenh_csv(vb: str) -> pd.DataFrame:
    """Lich su lenh xuat CSV (MQL5 Signals Export, Myfxbook, FX Blue, ...) -> [luc, het, ma, chieu, lot]. Doan cot theo ten."""
    import io
    try:
        df = pd.read_csv(io.StringIO(vb), sep=None, engine="python")
    except Exception:
        return pd.DataFrame(columns=_COT)
    cot = {c: str(c).strip().lower() for c in df.columns}
    tg = [c for c, l in cot.items() if ("time" in l or "date" in l) and "duration" not in l]
    kieu = None
    for c in df.columns:
        v = df[c].astype(str).str.strip().str.lower()
        if len(v) and (v.str.startswith("buy") | v.str.startswith("sell")).mean() >= 0.5:
            kieu = c
            break
    ma = next((c for c, l in cot.items() if any(k in l for k in ("symbol", "item", "instrument"))), None)
    lot = next((c for c, l in cot.items() if any(k in l for k in ("volume", "lot", "size", "units"))), None)
    if not tg or kieu is None or ma is None:
        return pd.DataFrame(columns=_COT)
    v = df[kieu].astype(str).str.strip().str.lower()
    df = df[v.str.startswith("buy") | v.str.startswith("sell")]
    v = v.loc[df.index]
    ra = pd.DataFrame({"luc": pd.to_datetime(df[tg[0]].astype(str).str.replace(".", "-", n=2, regex=False), errors="coerce"),
                       "het": pd.to_datetime(df[tg[1]].astype(str).str.replace(".", "-", n=2, regex=False), errors="coerce")
                       if len(tg) > 1 else pd.NaT,
                       "ma": df[ma].astype(str), "chieu": v.map(lambda x: 1 if x.startswith("buy") else -1),
                       "lot": pd.to_numeric(df[lot], errors="coerce") if lot else None})
    gc = [c for c, l in cot.items() if "price" in l or l in ("gia", "open price", "close price")]
    ra["gia"] = pd.to_numeric(df[gc[0]], errors="coerce") if gc else None
    ra["gia_dong"] = pd.to_numeric(df[gc[1]], errors="coerce") if len(gc) > 1 else None
    return ra.dropna(subset=["luc"]).sort_values("luc").reset_index(drop=True)


def ma_goc(sym: str) -> str:
    """AUDCADmicro / EURUSDc / XAUUSD# -> AUDCAD / EURUSD / XAUUSD."""
    m = re.match(r"([A-Za-z]{6})", sym or "")
    return m.group(1).upper() if m else (sym or "").upper()


def dau_hieu_lenh(df: pd.DataFrame) -> dict:
    """Suy ky thuat xu li lenh TU DANH SACH LENH (SUY TU STATEMENT, khong phai so do). Lenh chua biet luc dong coi nhu
    con mo 24 h.
    - dca / luoi: cung luc co >= 3 lenh cung chieu cung ma dang mo;
    - martingale: trong mot chuoi chong do, lot lenh sau > lot lenh truoc;
    - hedge: cung luc co lenh mua va lenh ban cung ma dang mo."""
    ra = {"so_lenh_vao": int(len(df)), "ma": sorted({ma_goc(x) for x in df["ma"]}) if len(df) else [], "ky_thuat": []}
    if not len(df):
        return ra
    het = df["het"].where(df["het"].notna(), df["luc"] + pd.Timedelta(hours=24))
    chong_max, mg, hedge = 1, False, False
    for _, g in df.assign(het_tinh=het, ma_g=df["ma"].map(ma_goc)).groupby("ma_g"):
        g = g.sort_values("luc")
        rows = list(g.itertuples())
        for i, r in enumerate(rows):
            dang = [x for x in rows[:i] if x.het_tinh > r.luc]
            cung = [x for x in dang if x.chieu == r.chieu]
            chong_max = max(chong_max, len(cung) + 1)
            if cung and r.lot and cung[-1].lot and r.lot > cung[-1].lot * 1.05:
                mg = True
            if any(x.chieu != r.chieu for x in dang):
                hedge = True
    ra["chong_cung_chieu_max"] = int(chong_max)
    if chong_max >= 3:
        ra["ky_thuat"].append("dca")
    if mg:
        ra["ky_thuat"].append("martingale")
    if hedge:
        ra["ky_thuat"].append("hedge")
    return ra


def _pip(ma: str, gia: float) -> float:
    m = ma_goc(ma)
    if m.startswith(("XAU", "GOLD")):
        return 0.1
    if m.startswith(("XAG", "SILVER")):
        return 0.01
    if m.endswith("JPY") or gia > 50:
        return 0.01
    return 0.0001


def _tv(x: list[float], q: float = 0.5) -> float | None:
    x = [float(v) for v in x if v is not None and v == v]
    return round(float(pd.Series(x).quantile(q)), 6) if x else None


def do_nguoc(df: pd.DataFrame) -> dict:
    """DO NGUOC cach xu li lenh tu danh sach lenh (SUY TU STATEMENT, khong phai so do). Ro = chuoi lenh cung ma cung chieu
    chong len nhau (lenh sau mo khi lenh truoc con mo). Moi ro co >= 2 lenh cho:
      - buoc DCA: khoang gia giua hai lenh lien tiep (% gia va pip), ty le lan buoc di NGUOC (gia xau hon -> nhoi);
      - he so lot: lot lenh sau / lot lenh truoc;
      - TP ro: (gia dong binh quan - gia von binh quan) * chieu / gia von (%), chi tinh ro dong gan nhu cung luc;
      - so tang: so lenh trong ro.
    Them: gio mo lenh dau ro (gio SERVER cua tac gia), ma, thoi gian giu. Moi so la trung vi."""
    ra = {"nhan": "SUY TỪ STATEMENT (dò ngược, không phải số đo)", "so_lenh": int(len(df))}
    if not len(df):
        return ra
    df = df.copy()
    for c in ("gia", "gia_dong", "het"):
        if c not in df.columns:
            df[c] = None
    df["ma_g"] = df["ma"].map(ma_goc)
    df["het_tinh"] = pd.to_datetime(df["het"]).where(pd.to_datetime(df["het"]).notna(), df["luc"] + pd.Timedelta(hours=24))
    ra["ma"] = df["ma_g"].value_counts().head(8).to_dict()
    ro = []
    for (m, ch), g in df.groupby(["ma_g", "chieu"]):
        g = g.sort_values("luc")
        cur, het_max = [], None
        for r in g.itertuples():
            if cur and r.luc < het_max:
                cur.append(r)
                het_max = max(het_max, r.het_tinh)
            else:
                if cur:
                    ro.append((m, ch, cur))
                cur, het_max = [r], r.het_tinh
        if cur:
            ro.append((m, ch, cur))
    buoc_pct, buoc_pip, nguoc, he_so, tp_pct, tp_pip, tang, gio, giu = [], [], [], [], [], [], [], [], []
    for m, ch, rs in ro:
        tang.append(len(rs))
        gio.append(rs[0].luc.hour)
        giu.append((max(x.het_tinh for x in rs) - rs[0].luc).total_seconds() / 3600.0)
        for a, b in zip(rs, rs[1:]):
            if a.gia and b.gia:
                d = (b.gia - a.gia) * ch
                buoc_pct.append(abs(d) / a.gia * 100)
                buoc_pip.append(abs(d) / _pip(m, a.gia))
                nguoc.append(1.0 if d < 0 else 0.0)
            if a.lot and b.lot:
                he_so.append(b.lot / a.lot)
        dong = [x for x in rs if x.gia_dong and x.gia and x.lot]
        if dong and len(dong) == len(rs):
            t_het = [pd.Timestamp(x.het_tinh) for x in rs]
            if (max(t_het) - min(t_het)) <= pd.Timedelta(minutes=5) or len(rs) == 1:
                L = sum(x.lot for x in rs)
                von = sum(x.lot * x.gia for x in rs) / L
                dg = sum(x.lot * x.gia_dong for x in rs) / L
                tp_pct.append((dg - von) * ch / von * 100)
                tp_pip.append((dg - von) * ch / _pip(m, von))
    nhieu = [t for t in tang if t >= 2]
    ra.update({
        "so_ro": len(ro), "so_ro_nhieu_tang": len(nhieu), "tang_trung_vi": _tv(tang), "tang_max": max(tang) if tang else None,
        "tang_p90": _tv(tang, 0.9),
        "buoc_dca_pct": _tv(buoc_pct), "buoc_dca_pip": _tv(buoc_pip),
        "ty_le_buoc_nguoc": round(sum(nguoc) / len(nguoc), 3) if nguoc else None,
        "he_so_lot": _tv(he_so), "he_so_lot_max": round(max(he_so), 3) if he_so else None,
        "tp_ro_pct": _tv([x for x in tp_pct if x > 0]), "tp_ro_pip": _tv([x for x in tp_pip if x > 0]),
        "ty_le_ro_dong_lai": round(sum(1 for x in tp_pct if x > 0) / len(tp_pct), 3) if tp_pct else None,
        "lot_dau_trung_vi": _tv([rs[0].lot for _, _, rs in ro if rs[0].lot]),
        "giu_gio_trung_vi": _tv(giu),
    })
    if gio:
        h = pd.Series(gio).value_counts().sort_index()
        ra["gio_mo"] = {int(k): int(v) for k, v in h.items()}
        ra["gio_hoat_dong"] = [int(k) for k, v in h.items() if v >= max(1, 0.03 * len(gio))]
    if len(df) >= 2:
        ra["tu"], ra["den"] = str(df["luc"].min())[:16], str(df["het_tinh"].max())[:16]
    # goi y quan li cho Python (gan nhat voi KHONG_GIAN_QL), CHI de lam phep thu dau tien
    q = {}
    if ra["tp_ro_pct"]:
        q["tp_pct"] = round(ra["tp_ro_pct"] / 100, 5)
    if ra["buoc_dca_pct"] and (ra["ty_le_buoc_nguoc"] or 0) >= 0.5 and nhieu:
        q["dca_buoc_pct"] = round(ra["buoc_dca_pct"] / 100, 5)
        q["dca_toi_da"] = int(max(1, (ra["tang_p90"] or 2) - 1))
        q["dca_he_so_lot"] = round(min(max(ra["he_so_lot"] or 1.0, 1.0), 3.0), 3)
    if q:
        ra["ql_goi_y"] = q
    return ra


def tach_ma_html(vb: str) -> str:
    """Khoi ma MQL trong trang HTML luu tay (<pre>, <code>, <textarea>) co OnTick/OnInit/OnCalculate -> van ban ma."""
    khoi = re.findall(r"<(pre|code|textarea)[^>]*>(.*?)</\1>", vb, re.S | re.I)
    tot = ""
    for _, k in khoi:
        t = H.unescape(re.sub(r"<[^>]+>", "", k))
        if re.search(r"\bOn(Tick|Init|Calculate|Start)\s*\(", t) and len(t) > len(tot):
            tot = t
    return tot


def the_statement(df: pd.DataFrame, sha: str, so_tg: dict) -> dict:
    """Phan chung cua the STATEMENT: luu lenh ra _tach/<sha>_lenh.csv, dau hieu + do nguoc + so tac gia (rieng)."""
    TACH.mkdir(parents=True, exist_ok=True)
    dh = dau_hieu_lenh(df)
    f = TACH / ("%s_lenh.csv" % sha)
    df.reindex(columns=_COT).to_csv(f, index=False)
    dn = do_nguoc(df)
    ra = {"nen_tang": "STATEMENT", "loai_kiem_ke": "lich_su_lenh", "dau_hieu": dh, "do_nguoc": dn,
          "quan_tri_goc": dh["ky_thuat"], "tin_hieu": {"kieu": "lenh_ngoai", "tep": str(f), "ma": dh["ma"], "khoang": {}}}
    if so_tg:
        ra["so_tac_gia"] = so_tg
    if dn.get("ql_goi_y"):
        ra["ql_goi_y"] = dn["ql_goi_y"]
    return ra


def _sha(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()[:16]


def la_bao_cao(vb: str) -> bool:
    v = vb[:200000]
    if re.search(r'content="strategy tester"', v, re.I):
        return True                                       # MT5 ReportTester-*.html (moi ngon ngu)
    return bool(re.search(r"Strategy Tester Report|Closed Transactions|Statement|Báo cáo|Deals|Probador|Тестер|测试报告", v)) and \
        bool(re.search(r"Profit|Lợi nhuận|Beneficio|Прибыль|利润|盈利", v))


def quet(cac_thu_muc: list[Path], da_co: set[str] | None = None) -> list[dict]:
    """Quet thu muc nhap tay -> list THE (dang cua nhan/ong_dan). `da_co`: id the da nhan (bo qua)."""
    da_co = da_co or set()
    tep = []
    for d in cac_thu_muc:
        for p in sorted(d.rglob("*")):
            if p.is_file() and p.suffix.lower() in DUOI and TACH not in p.parents and p.stat().st_size <= TRAN_BYTE:
                tep.append(p)
    theo_ten = {}
    for p in tep:
        theo_ten.setdefault(p.stem.lower(), []).append(p)
    the = []
    TACH.mkdir(parents=True, exist_ok=True)
    # .zip: chi GIAI NEN (khong chay gi) cac file co duoi nhan duoc vao _tach/<sha>/, roi xu li nhu file thuong
    for p in [q for q in tep if q.suffix.lower() == ".zip"]:
        import zipfile
        try:
            d = TACH / ("zip_" + _sha(p.read_bytes()))
            with zipfile.ZipFile(p) as z:
                for nf in z.namelist():
                    q = Path(nf)
                    if q.suffix.lower() in DUOI and q.suffix.lower() != ".zip" and ".." not in q.parts and not q.is_absolute():
                        info = z.getinfo(nf)
                        if info.file_size <= TRAN_BYTE:
                            (d / q).parent.mkdir(parents=True, exist_ok=True)
                            (d / q).write_bytes(z.read(nf))
            tep += [x for x in sorted(d.rglob("*")) if x.is_file()]
        except Exception:
            continue
    tep = [q for q in tep if q.suffix.lower() != ".zip"]
    for p in tep:
        b = p.read_bytes()
        sha = _sha(b)
        tid = "nhap_" + sha
        if tid in da_co:
            continue
        duoi = p.suffix.lower()
        loai_tep = DUOI[duoi]
        mu = re.match(r"(U[0-9a-f]{6})(?:[_\- .]|$)", p.name)       # ma dong trong reports/URL_BI_CHAN.md
        goc = {"id": tid, "ten": "Nhập tay: %s" % p.name, "nguon": {"kho": "nhap_tay", "tep": str(p), "url": ""},
               "nhap_tay": {"tep": str(p), "loai_tep": loai_tep, "sha1": sha, "ma_url": mu.group(1) if mu else None,
                            "ten_goc": p.stem, "nguon_tay": p.parent.name},
               "nhan": ["NHẬP TAY"]}
        if loai_tep in ("MQL4", "MQL5"):
            vb = doc_vb(b)
            goc["nen_tang"] = loai_tep
            sets = [q for q in theo_ten.get(p.stem.lower(), []) if q.suffix.lower() == ".set"]
            if sets:
                goc["set_goc"] = doc_set(doc_vb(sets[0].read_bytes()))
            if not re.search(r"\bOnTick\s*\(", vb):
                goc["loai_kiem_ke"] = "chi_bao" if re.search(r"\bOnCalculate\s*\(", vb) else "thu_vien"
        elif loai_tep in ("MQL4_EX", "MQL5_EX"):
            goc.update(nen_tang=loai_tep.split("_")[0], chi_bien_dich=True, loai_kiem_ke="ea",
                       ghi_chu="chỉ có file biên dịch: chạy thẳng MT5 trên máy nhà")
        elif loai_tep == "SET":
            ten_ea = [q for q in theo_ten.get(p.stem.lower(), []) if q.suffix.lower() in (".mq4", ".mq5", ".ex4", ".ex5")]
            if ten_ea:
                continue                                  # da gan vao the EA cung ten
            goc.update(nen_tang="SET", loai_kiem_ke="tham_so", set_goc=doc_set(doc_vb(b)))
        elif loai_tep == "HTML":
            vb = doc_vb(b)
            if la_bao_cao(vb):
                goc.update(the_statement(doc_lenh_html(vb), sha, so_tac_gia_bao_cao(vb)))
            else:
                ma = tach_ma_html(vb)
                if ma:
                    nt = "MQL4" if re.search(r"\bstart\s*\(|OrderSend\s*\([^)]*,\s*OP_", ma) else "MQL5"
                    f = TACH / ("%s.%s" % (sha, "mq4" if nt == "MQL4" else "mq5"))
                    f.write_text(ma, encoding="utf-8")
                    goc.update(nen_tang=nt, nguon={"kho": "nhap_tay", "tep": str(f), "url": "", "trang_goc": str(p)})
                else:
                    goc.update(nen_tang="HTML", loai_kiem_ke="mo_ta")
        elif loai_tep == "CSV":
            df = doc_lenh_csv(doc_vb(b))
            if len(df):
                goc.update(the_statement(df, sha, {}))
            else:
                goc.update(nen_tang="CSV", loai_kiem_ke="mo_ta")
        elif loai_tep == "Python":
            goc["nen_tang"] = "Python"
        else:  # .pine / .txt
            vb = doc_vb(b)
            goc["nen_tang"] = "TradingView" if (duoi == ".pine" or re.search(r"//@version=\d", vb)) else "TXT"
            if goc["nen_tang"] == "TXT":
                goc["loai_kiem_ke"] = "mo_ta"
        the.append(goc)
    return the


def tin_hieu_lenh_ngoai(th: dict, df: pd.DataFrame, ma: str) -> "np.ndarray":
    """Lenh tu statement -> tin hieu tren nen `df` cua `ma`: lenh luc T -> s[i] o nen co open[i+1] la nen dau >= T."""
    import numpy as np
    s = np.zeros(len(df), int)
    try:
        lenh = pd.read_csv(th["tep"], parse_dates=["luc"])
    except Exception:
        return s
    lenh = lenh[lenh["ma"].map(ma_goc) == ma.upper()]
    if not len(lenh):
        return s
    j = df.index.searchsorted(pd.DatetimeIndex(lenh["luc"]))      # nen dau tien >= T
    for k, ch in zip(j, lenh["chieu"]):
        if 1 <= k < len(df):
            s[k - 1] = int(ch)
    return s
