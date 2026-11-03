# -*- coding: utf-8 -*-
"""Thợ MT5 máy nhà (Windows) — lặp: pull -> nhận việc (khoá bằng commit) -> chạy MT5 Strategy Tester -> ghi kết quả -> push.

Chạy (Anh): may_nha\\CHAY_THO_MT5.cmd  — hoặc trực tiếp: python may_nha\\tho_mt5.py --slot D:\\mt5_tester\\p1            (slot = terminal MT5 portable ĐÃ ĐĂNG NHẬP XM)
       python may_nha\\tho_mt5.py --mot-lan                         (làm 1 việc rồi thoát, để thử)
An toàn: chỉ giết cây tiến trình DO CHÍNH THỢ PHÓNG (PID của mình) khi quá giờ; KHÔNG BAO GIỜ taskkill theo tên
(claude.exe, terminal64.exe XM của Anh đang chạy vẫn sống). Git: fetch + merge --ff-only, push thường, không force/rebase.
Hết việc -> tự sinh việc tinh chỉnh lot quanh mức tốt nhất đã đo; vẫn hết -> chờ 5 phút rồi kéo lại.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC / "may_nha"))
import hang_doi_git as HD  # noqa: E402

DD_MAX, CAGR_MIN = 80.0, 10.0


def log(s: str) -> None:
    dong = "[%s] %s" % (HD.bay_gio(), s)
    print(dong, flush=True)
    p = GOC / "hang_doi" / ("log_%s.txt" % socket.gethostname()); p.parent.mkdir(exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(dong + "\n")


def ram_trong_gb() -> float | None:
    """RAM trống thực tế (GB). Windows: GlobalMemoryStatusEx; Linux: /proc/meminfo. None nếu không đo được."""
    try:
        if os.name == "nt":
            import ctypes

            class _MS(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = _MS(); m.dwLength = ctypes.sizeof(_MS)
            if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
                return None
            return m.ullAvailPhys / 1024 ** 3
        for d in open("/proc/meminfo", encoding="ascii"):
            if d.startswith("MemAvailable:"):
                return int(d.split()[1]) / 1024 ** 2
    except Exception:
        return None
    return None


def nguong_ram_gb() -> float:
    """Ngưỡng RAM trống để NHẬN VIỆC MỚI (env BRAIN_RAM_TRONG_MIN_GB, mặc định 8). Anh yêu cầu giữ >= 6 GB."""
    try:
        return float(os.environ.get("BRAIN_RAM_TRONG_MIN_GB", "8") or 8)
    except ValueError:
        return 8.0


def du_ram_nhan_viec(nguong: float | None = None, do=None) -> tuple[bool, float | None]:
    """True nếu RAM trống > ngưỡng (không đo được -> không chặn)."""
    g = (do or ram_trong_gb)()
    n = nguong_ram_gb() if nguong is None else nguong
    return (g is None or g > n), g


def cho_du_ram(log_fn=None, ngu=time.sleep, do=None, buoc: int = 60, toi_da: int | None = None) -> bool:
    """Chờ tới khi RAM trống > ngưỡng. False nếu quá `toi_da` giây (None = chờ mãi)."""
    t = 0
    while True:
        ok, g = du_ram_nhan_viec(do=do)
        if ok:
            return True
        if log_fn and t % 600 == 0:
            log_fn("RAM trống %.2f GB <= ngưỡng %.1f GB -> chưa nhận việc mới" % (g, nguong_ram_gb()))
        if toi_da is not None and t >= toi_da:
            return False
        ngu(buoc); t += buoc


def gioi_han_maxbars(slot: Path, max_bars: int | None = None) -> bool:
    """Đặt [Charts] MaxBars trong <slot>/config/common.ini (giảm RAM terminal; không đổi tick/khoảng ngày của tester).
    env BRAIN_MAX_BARS (mặc định 50000). True nếu đã sửa."""
    mb = int(max_bars or os.environ.get("BRAIN_MAX_BARS", "50000") or 50000)
    f = slot / "config" / "common.ini"
    if not f.exists():
        return False
    raw = f.read_bytes()
    enc = "utf-16" if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else "utf-8"
    txt = raw.decode(enc, errors="replace").lstrip("\ufeff")
    out = []; trong = False; da = False; co_charts = False
    for d in txt.splitlines():
        s = d.strip()
        if s.startswith("["):
            if trong and not da:
                out.append("MaxBars=%d" % mb); da = True
            trong = s.lower() == "[charts]"; co_charts = co_charts or trong
        elif trong and s.lower().startswith("maxbars="):
            if s == "MaxBars=%d" % mb:
                return False
            d = "MaxBars=%d" % mb; da = True
        out.append(d)
    if not da:
        if not trong:
            out.append("[Charts]")
        out.append("MaxBars=%d" % mb)
    f.write_text("\r\n".join(out) + "\r\n", encoding=enc, newline="")
    return True


def don_cache_tester(slot: Path, giu_ngay: float = 2.0, bay_gio: float | None = None) -> int:
    """Xoá tệp cũ trong <slot>/Tester/cache (chỉ slot thợ đang giữ). Trả số tệp đã xoá."""
    d = slot / "Tester" / "cache"
    if not d.is_dir():
        return 0
    moc = (bay_gio or time.time()) - giu_ngay * 86400; n = 0
    for f in d.iterdir():
        try:
            if f.is_file() and f.stat().st_mtime < moc:
                f.unlink(); n += 1
        except OSError:
            pass
    return n


# ---------------- hàm thuần (có test) ----------------
def so_nam(tu: str, den: str) -> float:
    import datetime as dt
    a = dt.datetime.strptime(tu, "%Y.%m.%d"); b = dt.datetime.strptime(den, "%Y.%m.%d")
    return max((b - a).days / 365.25, 1e-6)


def cagr(von: float, net: float | None, nam: float) -> float | None:
    if net is None or von <= 0:
        return None
    cuoi = von + net
    return -100.0 if cuoi <= 0 else round(((cuoi / von) ** (1 / nam) - 1) * 100, 3)


def dd_pct(chuoi) -> float | None:
    """'1 234.56 (12.34%)' -> 12.34 (DD equity MT5)."""
    m = re.search(r"\(([\d.,\s]+)%\)", str(chuoi or ""))
    return float(m.group(1).replace(" ", "").replace(",", ".")) if m else None


_SLOT_CHI_HASH: set = set()      # slot mà tester đã báo 'symbol ...micro not exist' (tài khoản đang đăng nhập chỉ có '#')


def symbol_khong_co(slot: Path, ma: str, t0: float) -> bool:
    """Journal của slot (logs/*.log, UTF-16) có 'symbol <ma> not exist' ghi sau t0?"""
    for f in sorted((Path(slot) / "logs").glob("*.log"), key=lambda x: x.stat().st_mtime)[-1:]:
        if f.stat().st_mtime < t0:
            continue
        try:
            nd = f.read_bytes().decode("utf-16", errors="ignore")
        except OSError:
            continue
        if ("symbol %s not exist" % ma) in nd[-20000:]:
            return True
    return False


def ky_hieu_slot(slot: Path, ma: str) -> str:
    """03/11/2026: tài khoản XM của slot có thể chỉ có mã '#' (demo 345930355: không có *micro) -> tester báo
    'symbol ... not exist'. Dò danh sách symbol của slot (bases/<server>/symbols/symbols-*.dat); thiếu mã gốc -> đổi sang '#'."""
    if not ma:
        return ma
    import glob
    def co(t: str) -> bool:
        for f in glob.glob(str(Path(slot) / "bases" / "*" / "symbols" / "symbols-*.dat")):
            try:
                b = Path(f).read_bytes()
            except OSError:
                continue
            if t.encode("ascii") + b"\0" in b or t.encode("utf-16-le") + b"\0\0" in b:
                return True
        return any(Path(x).is_dir() for x in glob.glob(str(Path(slot) / "bases" / "*" / "history" / t)))
    if str(slot) in _SLOT_CHI_HASH and ma.lower().endswith("micro"):
        sys.path.insert(0, str(GOC / "mt5tools")); from sinh_viec import remap_ma_hash_demo
        return remap_ma_hash_demo(ma)
    if co(ma):
        return ma
    sys.path.insert(0, str(GOC / "mt5tools")); from sinh_viec import remap_ma_hash_demo
    moi = remap_ma_hash_demo(ma)
    if moi == ma:
        return ma
    if co(moi):
        return moi
    # symbols-*.dat của MT5 được mã hoá -> không dò được tên; suy theo lịch sử đã tải của slot:
    # có mã '#' mà không có mã '*micro' nào => tài khoản chỉ có '#'
    ls = [Path(x).name.lower() for x in glob.glob(str(Path(slot) / "bases" / "*" / "history" / "*"))]
    # không thấy mã *micro nào trong slot (slot mới chưa tải lịch sử cũng vậy) -> dùng '#' như các ini cũ
    # D:\mt5_tester\ini (tài khoản demo XM 345930355 chỉ có '#')
    if not any(x.endswith("micro") for x in ls):
        return moi
    return ma


def doi_ma_csv(noi_dung: str, ma_cu: str, ma_moi: str) -> str:
    """Đổi cột 'ma' của CSV lệnh vào từ mã việc sang mã thật của slot."""
    if ma_cu == ma_moi:
        return noi_dung
    dong = noi_dung.splitlines()
    if not dong or "ma" not in [c.strip() for c in dong[0].split(",")]:
        return noi_dung
    i = [c.strip() for c in dong[0].split(",")].index("ma"); out = [dong[0]]
    for d in dong[1:]:
        p = d.split(",")
        if len(p) > i and p[i].strip() == ma_cu:
            p[i] = ma_moi
        out.append(",".join(p))
    return "\n".join(out) + "\n"


def nhan_csv(noi_dung: str, k: float, chia_hash: bool = False) -> str:
    """Nhân cột lot của CSV lệnh vào với k (mã '#': lot micro > 0,5 chia 100 trước, như sinh_viec.dat_csv_vao)."""
    dong = noi_dung.splitlines()
    if not dong:
        return noi_dung
    cot = [c.strip() for c in dong[0].split(",")]
    if "lot" not in cot:
        return noi_dung
    i = cot.index("lot"); out = [dong[0]]
    for d in dong[1:]:
        if not d.strip():
            continue
        p = d.split(",")
        try:
            lv = float(p[i])
            if chia_hash and lv > 0.5:
                lv *= 0.01
            p[i] = ("%.4f" % (lv * k)).rstrip("0").rstrip(".")
        except (ValueError, IndexError):
            pass
        out.append(",".join(p))
    return "\n".join(out) + "\n"


def danh_gia(chay: list[dict]) -> dict:
    """Từ các lần chạy (mỗi k) -> k lớn nhất DD<80 và k nhỏ nhất đạt cả hai tiêu chí."""
    hop = [c for c in chay if c.get("cagr_pct") is not None and c.get("dd_pct") is not None]
    dat = [c for c in hop if c["dd_pct"] < DD_MAX and c["cagr_pct"] > CAGR_MIN]
    an_toan = [c for c in hop if c["dd_pct"] < DD_MAX]
    tot = max(dat, key=lambda c: c["cagr_pct"]) if dat else None
    tom = ("ĐẠT: k=%s CAGR %.2f%%/năm DD %.2f%%" % (tot["k"], tot["cagr_pct"], tot["dd_pct"]) if tot else
           ("TRƯỢT: không k nào DD<80%% và CAGR>10%%" if hop else "CHƯA ĐO ĐƯỢC"))
    return {"dat": bool(dat), "k_tot": tot["k"] if tot else None, "k_an_toan_max": max((c["k"] for c in an_toan), default=None),
            "tom_tat": tom}


def tinh_chinh(v: dict, kq: dict) -> dict | None:
    """Việc tự sinh khi hết hàng: dò k mịn giữa k an toàn lớn nhất và k kế tiếp (đã trượt DD)."""
    ks = sorted(float(x) for x in v.get("he_so_lot") or [])
    a = kq.get("k_an_toan_max")
    if a is None or v.get("tinh_chinh_lan", 0) >= 2:
        return None
    sau = [x for x in ks if x > a]
    b = sau[0] if sau else a * 1.5
    moi = sorted({round(a + (b - a) * t, 3) for t in (0.25, 0.5, 0.75)} - set(ks))
    if not moi:
        return None
    w = {k: v[k] for k in v if k not in ("may", "nhan_luc", "trang_thai", "xong_luc", "ket_qua")}
    w.update({"id": "%s_tc%d" % (v["id"], v.get("tinh_chinh_lan", 0) + 1), "he_so_lot": moi, "uu_tien": 1,
              "tinh_chinh_lan": v.get("tinh_chinh_lan", 0) + 1, "ghi_chu": "tự sinh: dò k mịn"})
    return w


# ---------------- chạy MT5 (dùng mt5tools) ----------------
def _mt5():
    sys.path.insert(0, str(GOC / "mt5tools"))
    import sinh_viec as SV, an_toan_tester as AT, chay_lien_tuc as CL, chay_lai_tren_san as CLS  # noqa: E401
    return SV, AT, CL, CLS


def tai_ma_nguon(slot: Path, v: dict) -> str | None:
    """Làn A nguồn ngoài (Code Base/GitHub): tải .mq5 công khai về slot MQL5/Experts/BRAIN/<ea_file>.mq5 (không đăng nhập)."""
    dich = slot / "MQL5" / "Experts" / "BRAIN"; dich.mkdir(parents=True, exist_ok=True)
    url = v.get("url_ex5") or v["url_ma_nguon"]
    f = dich / (v["ea_file"] + (".ex5" if v.get("url_ex5") else ".mq5"))
    if f.exists():
        return None
    try:
        rq = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        b = urllib.request.urlopen(rq, timeout=60).read()
        if v.get("url_ex5") and not b.startswith(b"EX5"):
            return "tệp tải về không phải .ex5"
        f.write_bytes(b)
    except Exception as e:
        return "tải mã nguồn hỏng: %s" % str(e)[:120]
    return None


def chuan_bi_ea(slot: Path, ea_file: str) -> str | None:
    """EA của repo (ea_demo/<ea>.mq5) -> slot MQL5/Experts/BRAIN, biên dịch nếu thiếu/cũ. Market\\X: phải có sẵn .ex5."""
    _, AT, _, _ = _mt5()
    if ea_file.lower().startswith("market\\") or ea_file.lower().startswith("market/"):
        return None if (slot / "MQL5" / "Experts" / (ea_file.replace("/", "\\").replace("\\", os.sep) + ".ex5")).exists() else "thiếu .ex5 Market"
    dich = slot / "MQL5" / "Experts" / "BRAIN"; dich.mkdir(parents=True, exist_ok=True)
    for f in (GOC / "ea_demo").glob("*.mqh"):
        shutil.copy2(f, dich / f.name)
    mq = GOC / "ea_demo" / (ea_file + ".mq5")
    if not mq.exists() and (dich / (ea_file + ".mq5")).exists():          # mã ngoài đã tải vào slot
        mq = dich / (ea_file + ".mq5")
    if not mq.exists():
        return None if (dich / (ea_file + ".ex5")).exists() else "thiếu %s" % mq.name
    if mq.parent != dich:
        shutil.copy2(mq, dich / mq.name)
    ex5 = dich / (ea_file + ".ex5")
    if ex5.exists() and ex5.stat().st_mtime >= mq.stat().st_mtime:
        return None
    me = slot / "metaeditor64.exe"
    if not me.exists():
        return "thiếu metaeditor64.exe trong slot"
    return AT.bien_dich(me, dich / mq.name) or None


def chay_mot_k(slot: Path, v: dict, k: float, cho_toi_da: int) -> dict:
    SV, AT, CL, CLS = _mt5()
    ten = re.sub(r"[^A-Za-z0-9_]", "", "hd_%s_k%s" % (v["id"], str(k).replace(".", "p")))[:60]
    ts = dict(v.get("ts") or {})
    lot_ten = v.get("tham_so_lot")
    if lot_ten and lot_ten in ts:
        ts[lot_ten] = round(float(ts[lot_ten]) * k, 6)
    ma = ky_hieu_slot(slot, v["ma"])
    if ma != v["ma"]:
        log("  mã %s không có trong slot -> dùng %s" % (v["ma"], ma))
    if v.get("che_do") == "ong_dan_csv":
        nguon = GOC / v["csv_vao"].replace("\\", "/")
        ten_csv = ten + "_vao.csv"
        common = SV.thu_muc_common(); common.mkdir(parents=True, exist_ok=True)
        (common / ten_csv).write_text(nhan_csv(doi_ma_csv(nguon.read_text(encoding="utf-8", errors="replace"), v["ma"], ma), k, ma.endswith("#")),
                                      encoding="utf-8", newline="\n")
        for duoi in ("_lenh_mt5.csv", "_gia.csv"):
            (common / (ten_csv + duoi)).unlink(missing_ok=True)
        ts["InpFileCsv"] = ten_csv
    if "InpTF" in ts:
        ts["InpTF"] = SV.TF[v["tf"]] if hasattr(SV, "TF") and v["tf"] in SV.TF else ts["InpTF"]
    vv = {"ea_file": v["ea_file"].replace("/", "\\") if v["ea_file"].lower().startswith("market") else "BRAIN\\" + v["ea_file"],
          "ma": ma, "tf": v["tf"], "tu": v["tu"], "den": v["den"], "model": int(v.get("model", 4)),
          "von": int(v.get("von") or 1000), "tien": v.get("tien") or "USD", "ts": ts}
    (slot / "MQL5" / "Profiles" / "Tester").mkdir(parents=True, exist_ok=True)
    (slot / "MQL5" / "Profiles" / "Tester" / (ten + ".set")).write_text(SV.file_set_ong_dan(vv), encoding="ascii", errors="replace")
    ini = SV.ini_ong_dan(vv, ten, AT.dong_don_bay(int(v.get("don_bay") or 500))).replace("Expert=BRAIN\\BRAIN\\", "Expert=BRAIN\\")
    ini = ini.replace("Expert=BRAIN\\Market", "Expert=Market")
    (slot / (ten + ".ini")).write_text(ini, encoding="ascii")
    AT.xoa_bao_cao_cu(slot, ten)
    try:                                                        # giảm RAM mỗi lần test
        if gioi_han_maxbars(slot):
            log("  đặt MaxBars=%s cho slot" % os.environ.get("BRAIN_MAX_BARS", "50000"))
        n_xoa = don_cache_tester(slot)
        if n_xoa:
            log("  xoá %d tệp Tester/cache cũ" % n_xoa)
    except Exception as e:
        log("  không giảm RAM được: %s" % str(e)[:200])
    t0 = time.time()
    pr = subprocess.Popen([str(slot / "terminal64.exe"), "/portable", "/config:" + str(slot / (ten + ".ini"))], creationflags=0x00000040)
    log("  phóng PID %d (%s k=%s)" % (pr.pid, v["id"], k))
    try:
        pr.wait(timeout=cho_toi_da)
    except subprocess.TimeoutExpired:
        CL.giet_cay(pr)                                         # chỉ cây tiến trình CỦA MÌNH
        return {"k": k, "loi": "qua_gio", "giay": int(time.time() - t0)}
    f = slot / (ten + ".htm")
    if not AT.bao_cao_moi(f, t0):
        if ma.lower().endswith("micro") and str(slot) not in _SLOT_CHI_HASH and symbol_khong_co(slot, ma, t0):
            _SLOT_CHI_HASH.add(str(slot))                       # tài khoản slot chỉ có '#' -> chạy lại k này bằng '#'
            log("  tester: %s không có trong tài khoản slot -> chạy lại bằng mã '#'" % ma)
            return chay_mot_k(slot, v, k, cho_toi_da)
        return {"k": k, "loi": "khong_bao_cao", "giay": int(time.time() - t0)}
    r = CL.doc_htm(f)
    deals = CLS.doc_deals(f.read_bytes().decode("utf-16", errors="ignore"))
    nam = so_nam(v["tu"], v["den"])
    dv = CLS.tong_ket_duong_von(deals, vv["von"], nam)
    import sys as _s; _s.path.insert(0, str(GOC))
    from nhan import dac_diem_he as DDH
    nam_tk = DDH.deals_theo_nam(deals)
    out = {"k": k, "lai_theo_nam": nam_tk["lai_theo_nam"], "ti_le_thang_pct": nam_tk["ti_le_thang_pct"], "net": r.get("net"), "pf": r.get("pf"), "lenh": r.get("lenh"), "dd_equity_mt5": r.get("dd"),
           "dd_pct": dd_pct(r.get("dd")), "cagr_pct": cagr(vv["von"], r.get("net"), nam), "sut_dong_lenh_pct": dv.get("sut_giam_pct"),
           "thang_te_nhat": dv.get("thang_te_nhat"), "chat_luong": r.get("chat_luong"), "giay": int(time.time() - t0), "bao_cao": f.name}
    ly = AT.phan_xu_ket_qua(r, out["giay"])
    if ly:
        out["loi"] = ly
    try:
        dich = GOC / "hang_doi" / "bao_cao"; dich.mkdir(exist_ok=True)
        shutil.copy2(f, dich / f.name)
        out["bao_cao_repo"] = str(dich / f.name)
    except OSError:
        pass
    return out


def lam_mt5_backtest(slot: Path, v: dict, cho: int) -> tuple[str, dict]:
    loi = tai_ma_nguon(slot, v) if (v.get("url_ma_nguon") or v.get("url_ex5")) else None
    loi = loi or chuan_bi_ea(slot, v["ea_file"])
    if loi:
        return "HONG", {"tom_tat": "CHƯA ĐO ĐƯỢC: " + loi}
    chay = [chay_mot_k(slot, v, float(k), cho) for k in v["he_so_lot"]]
    kq = {"chay": chay, **danh_gia([c for c in chay if not c.get("loi")])}
    return ("XONG" if any(not c.get("loi") for c in chay) else "HONG"), kq


def lam_demo(slot: Path, v: dict) -> tuple[str, dict]:
    """Demo Market chỉ tải được từ terminal đã đăng nhập MQL5 (Anh bấm 'Free Demo' trong tab Market một lần).
    Thợ tìm .ex5 vừa có trong MQL5/Experts/Market; thấy -> sinh việc backtest cho nó."""
    thu = slot / "MQL5" / "Experts" / "Market"
    tu_khoa = re.sub(r"[^a-z0-9]", "", str(v.get("ten_product") or "").lower())[:12]
    thay = [f for f in thu.glob("*.ex5")] if thu.exists() else []
    hop = [f for f in thay if tu_khoa and tu_khoa[:6] in re.sub(r"[^a-z0-9]", "", f.stem.lower())]
    if not hop:
        return "CHO_ANH", {"tom_tat": "CHƯA ĐO ĐƯỢC: chưa có .ex5 demo — Anh mở %s trong terminal (tab Market) bấm Free Demo" % v["url_product"]}
    ex = hop[0]
    return "XONG", {"tom_tat": "có demo %s" % ex.name, "ex5": ex.name, "sinh": [{
        "id": "bt_" + v["id"], "loai": "mt5_backtest", "lan": "co_ma_nguon", "uu_tien": int(v.get("uu_tien") or 5), "che_do": "ea_goc",
        "ea_file": "Market\\" + ex.stem, "ma": v.get("ma") or "EURUSD", "tf": v.get("tf") or "H1", "tu": "2016.01.01",
        "den": "2026.10.01", "model": 4, "von": 10000, "tien": "USD", "don_bay": 500, "ts": {}, "he_so_lot": [1.0],
        "uoc_phut": 45, "nguon": v.get("tin_hieu_id")}]}


def lam_myfxbook(v: dict) -> tuple[str, dict, dict]:
    rq = urllib.request.Request(v["url"], headers={"User-Agent": "Mozilla/5.0"})
    t = urllib.request.urlopen(rq, timeout=60).read().decode("utf-8", errors="replace")
    rel = "data/myfxbook/%s.html" % v["id"]
    return "XONG", {"tom_tat": "tải %d byte" % len(t), "tep": rel}, {rel: t}


def chon_slot(arg: str | None) -> Path:
    if arg:
        return Path(arg)
    _, _, CL, _ = _mt5()
    import quan_ly_slot as QS
    for s in QS.ds_slot():
        if Path(s, "terminal64.exe").exists() and CL.san_cua_slot(s) == "XM":
            return Path(s)
    raise SystemExit("Không thấy slot MT5 XM (đặt --slot D:\\mt5_tester\\xxx hoặc biến BRAIN_SLOTS)")


def ds_slot_xm() -> list[Path]:
    _, _, CL, _ = _mt5()
    import quan_ly_slot as QS
    return [Path(s) for s in QS.ds_slot() if Path(s, "terminal64.exe").exists() and CL.san_cua_slot(s) == "XM"]


def so_luong_song_song(yeu_cau: int | None, so_slot: int, so_cpu: int | None,
                        tran: int | None = None, ti_le_cpu: float | None = None) -> int:
    """Mặc định = số slot XM; trần `tran` (env BRAIN_TRAN_SONG_SONG, mặc định 10);
    trần theo CPU = ti_le_cpu * số luồng (env BRAIN_TI_LE_CPU, mặc định 0.8 -> nhắm 70-80% CPU)."""
    if tran is None:
        tran = int(os.environ.get("BRAIN_TRAN_SONG_SONG", "10") or 10)
    if ti_le_cpu is None:
        ti_le_cpu = float(os.environ.get("BRAIN_TI_LE_CPU", "0.8") or 0.8)
    tran_cpu = max(1, int((so_cpu or 2) * ti_le_cpu))
    n = so_slot if not yeu_cau else min(yeu_cau, so_slot)
    return max(0, min(n, max(1, tran), tran_cpu))


def het_luc(gio_chay: float | None, den_gio: str | None, bay_gio: float | None = None) -> float | None:
    """Mốc dừng nhận việc mới (epoch): --gio-chay H và/hoặc --den-gio HH:MM (giờ máy). Lấy mốc sớm hơn."""
    import datetime as dt
    t0 = bay_gio if bay_gio is not None else time.time()
    moc = []
    if gio_chay:
        moc.append(t0 + gio_chay * 3600)
    if den_gio:
        h, m = (int(x) for x in den_gio.split(":"))
        d = dt.datetime.fromtimestamp(t0).replace(hour=h, minute=m, second=0, microsecond=0)
        if d.timestamp() <= t0:
            d += dt.timedelta(days=1)
        moc.append(d.timestamp())
    return min(moc) if moc else None


def chay_song_song(a) -> None:
    slots = ds_slot_xm()
    n = so_luong_song_song(a.song_song or None, len(slots), os.cpu_count(), a.tran)
    if n == 0:
        raise SystemExit("Không thấy slot MT5 portable nào đăng nhập XM (BRAIN_SLOTS)")
    moc = het_luc(a.gio_chay, a.den_gio)
    con = []
    for s in slots[:n]:
        cmd = [sys.executable, str(Path(__file__).resolve()), "--slot", str(s), "--may", "%s_%s" % (a.may, s.name.lower()),
               "--cho-toi-da", str(a.cho_toi_da)] + (["--het-luc", str(moc)] if moc else [])
        p = subprocess.Popen(cmd, creationflags=0x00004000 if os.name == "nt" else 0)     # BELOW_NORMAL_PRIORITY_CLASS
        con.append(p); log("song song: thợ PID %d trên slot %s" % (p.pid, s))
        time.sleep(20)                                        # lệch pha để không cùng lúc kéo git
    ma = [p.wait() for p in con]
    log("song song: mọi thợ đã dừng (mã %s)" % ma)
    if moc and all(m == 3 for m in ma):
        sys.exit(3)


def in_tinh_trang() -> None:
    hd = GOC / "hang_doi"
    cho = [json.loads(f.read_text(encoding="utf-8")) for f in (hd / "can_test").glob("*.json")]
    print("Chờ: %d việc (~%.1f giờ ước)" % (len(cho), sum(HD.uoc_gio(v) for v in cho)))
    for d in sorted(hd.glob("dang_lam_*")):
        ds = [f.stem for f in d.glob("*.json")]
        print("Đang làm %s: %s" % (d.name[9:], ", ".join(ds) or "(trống)"))
    xong = [json.loads(f.read_text(encoding="utf-8")) for f in (hd / "da_test").glob("*.json")]
    from collections import Counter
    print("Xong: %d %s" % (len(xong), dict(Counter(x.get("trang_thai") for x in xong))))
    for x in sorted(xong, key=lambda x: x.get("xong_luc", ""))[-5:]:
        print("  %s %s: %s" % (x.get("xong_luc"), x["id"], (x.get("ket_qua") or {}).get("tom_tat")))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot"); ap.add_argument("--may", default=socket.gethostname().lower().replace(" ", "_"))
    ap.add_argument("--mot-lan", action="store_true"); ap.add_argument("--cho-toi-da", type=int, default=4 * 3600)
    ap.add_argument("--song-song", type=int, nargs="?", const=0, default=None,
                    help="chạy N thợ song song, mỗi slot XM một thợ (bỏ N = theo số slot XM, trần --tran và 80%% số luồng CPU)")
    ap.add_argument("--tran", type=int, default=None, help="trần số thợ song song (mặc định env BRAIN_TRAN_SONG_SONG hoặc 10)")
    ap.add_argument("--gio-chay", type=float, help="chỉ nhận việc mới trong H giờ"); ap.add_argument("--den-gio", help="HH:MM: ngừng nhận việc mới lúc này")
    ap.add_argument("--het-luc", type=float, help=argparse.SUPPRESS)
    ap.add_argument("--tinh-trang", action="store_true", help="in tiến độ hàng đợi rồi thoát")
    a = ap.parse_args()
    if a.tinh_trang:
        return in_tinh_trang()
    if not (GOC / ".tho_mt5_clone").exists():
        raise SystemExit("Chỉ chạy trong bản clone riêng của thợ (có tệp .tho_mt5_clone) — xem may_nha/README_THO_MT5.md")
    if a.song_song is not None and not a.slot:
        return chay_song_song(a)
    if a.het_luc is None:
        a.het_luc = het_luc(a.gio_chay, a.den_gio)
    slot = chon_slot(a.slot)
    hd = HD.HangDoi(GOC, a.may, log=log)
    log("thợ %s bắt đầu, slot %s" % (a.may, slot))
    while True:
        if a.het_luc and time.time() >= a.het_luc and not hd.dang_lam_cua_toi():
            log("hết khung giờ -> dừng (không nhận việc mới)"); sys.exit(3)
        v = (hd.dang_lam_cua_toi() or [None])[0]
        if v is None:                                           # chỉ nhận việc MỚI khi RAM trống > ngưỡng
            cho_du_ram(log)
            v = hd.nhan()
        if v is None:
            xong = sorted((GOC / "hang_doi" / "da_test").glob("*.json"))
            moi = []
            for f in xong:
                d = json.loads(f.read_text(encoding="utf-8"))
                if d.get("loai") == "mt5_backtest" and d.get("ket_qua"):
                    w = tinh_chinh(d, d["ket_qua"])
                    if w:
                        moi.append(w)
            for f in xong:                                       # demo Anh đã bấm tải sau đó -> sinh backtest
                d = json.loads(f.read_text(encoding="utf-8"))
                if d.get("loai") == "mql5_demo_download" and d.get("trang_thai") == "CHO_ANH" and not d.get("da_sinh"):
                    tt, kq = lam_demo(slot, d)
                    if tt == "XONG":
                        moi += kq.get("sinh", [])
            if moi and hd.them(moi[:10], "hang_doi: %s tự sinh %d việc dò k" % (a.may, len(moi[:10]))):
                continue
            log("hết việc -> chờ 5 phút")
            if a.mot_lan:
                return
            time.sleep(300); continue
        log("làm %s (%s)" % (v["id"], v["loai"]))
        them_tep: dict = {}
        try:
            if v["loai"] == "mt5_backtest":
                tt, kq = lam_mt5_backtest(slot, v, a.cho_toi_da)
            elif v["loai"] == "mql5_demo_download":
                tt, kq = lam_demo(slot, v)
            else:
                tt, kq, them_tep = lam_myfxbook(v)
        except Exception as e:                                  # không chết thợ vì một việc
            tt, kq = "HONG", {"tom_tat": "CHƯA ĐO ĐƯỢC: lỗi %s" % str(e)[:300]}
        sinh = kq.pop("sinh", None)
        tep_san = [c["bao_cao_repo"] for c in kq.get("chay", []) if c.get("bao_cao_repo")]
        if v["loai"] == "mt5_backtest":                        # đặc điểm tốt của hệ, kể cả khi trượt (tự động)
            try:
                sys.path.insert(0, str(GOC))
                from nhan import dac_diem_he as DDH
                for pth in DDH.tu_ket_qua_tho(v, kq):
                    them_tep[str(Path(pth).relative_to(GOC)).replace("\\", "/")] = Path(pth).read_text(encoding="utf-8")
            except Exception as e:
                log("  không ghi được đặc điểm hệ: %s" % str(e)[:200])
        hd.xong(v, kq, tt, them_tep, tep_san)
        if sinh:
            hd.them(sinh, "hang_doi: sinh việc từ %s" % v["id"])
        log("xong %s: %s — %s" % (v["id"], tt, kq.get("tom_tat")))
        if a.mot_lan:
            return


if __name__ == "__main__":
    main()
