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


def chuan_bi_ea(slot: Path, ea_file: str) -> str | None:
    """EA của repo (ea_demo/<ea>.mq5) -> slot MQL5/Experts/BRAIN, biên dịch nếu thiếu/cũ. Market\\X: phải có sẵn .ex5."""
    _, AT, _, _ = _mt5()
    if ea_file.lower().startswith("market\\") or ea_file.lower().startswith("market/"):
        return None if (slot / "MQL5" / "Experts" / (ea_file.replace("/", "\\").replace("\\", os.sep) + ".ex5")).exists() else "thiếu .ex5 Market"
    dich = slot / "MQL5" / "Experts" / "BRAIN"; dich.mkdir(parents=True, exist_ok=True)
    for f in (GOC / "ea_demo").glob("*.mqh"):
        shutil.copy2(f, dich / f.name)
    mq = GOC / "ea_demo" / (ea_file + ".mq5")
    if not mq.exists():
        return None if (dich / (ea_file + ".ex5")).exists() else "thiếu %s" % mq.name
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
    if v.get("che_do") == "ong_dan_csv":
        nguon = GOC / v["csv_vao"].replace("\\", "/")
        ten_csv = ten + "_vao.csv"
        common = SV.thu_muc_common(); common.mkdir(parents=True, exist_ok=True)
        (common / ten_csv).write_text(nhan_csv(nguon.read_text(encoding="utf-8", errors="replace"), k, str(v["ma"]).endswith("#")),
                                      encoding="utf-8", newline="\n")
        for duoi in ("_lenh_mt5.csv", "_gia.csv"):
            (common / (ten_csv + duoi)).unlink(missing_ok=True)
        ts["InpFileCsv"] = ten_csv
    if "InpTF" in ts:
        ts["InpTF"] = SV.TF[v["tf"]] if hasattr(SV, "TF") and v["tf"] in SV.TF else ts["InpTF"]
    vv = {"ea_file": v["ea_file"].replace("/", "\\") if v["ea_file"].lower().startswith("market") else "BRAIN\\" + v["ea_file"],
          "ma": v["ma"], "tf": v["tf"], "tu": v["tu"], "den": v["den"], "model": int(v.get("model", 4)),
          "von": int(v.get("von") or 1000), "tien": v.get("tien") or "USD", "ts": ts}
    (slot / "MQL5" / "Profiles" / "Tester").mkdir(parents=True, exist_ok=True)
    (slot / "MQL5" / "Profiles" / "Tester" / (ten + ".set")).write_text(SV.file_set_ong_dan(vv), encoding="ascii", errors="replace")
    ini = SV.ini_ong_dan(vv, ten, AT.dong_don_bay(int(v.get("don_bay") or 500))).replace("Expert=BRAIN\\BRAIN\\", "Expert=BRAIN\\")
    ini = ini.replace("Expert=BRAIN\\Market", "Expert=Market")
    (slot / (ten + ".ini")).write_text(ini, encoding="ascii")
    AT.xoa_bao_cao_cu(slot, ten)
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
        return {"k": k, "loi": "khong_bao_cao", "giay": int(time.time() - t0)}
    r = CL.doc_htm(f)
    deals = CLS.doc_deals(f.read_bytes().decode("utf-16", errors="ignore"))
    nam = so_nam(v["tu"], v["den"])
    dv = CLS.tong_ket_duong_von(deals, vv["von"], nam)
    out = {"k": k, "net": r.get("net"), "pf": r.get("pf"), "lenh": r.get("lenh"), "dd_equity_mt5": r.get("dd"),
           "dd_pct": dd_pct(r.get("dd")), "cagr_pct": cagr(vv["von"], r.get("net"), nam), "sut_dong_lenh_pct": dv.get("sut_giam_pct"),
           "thang_te_nhat": dv.get("thang_te_nhat"), "chat_luong": r.get("chat_luong"), "giay": int(time.time() - t0), "bao_cao": f.name}
    ly = AT.phan_xu_ket_qua(r, out["giay"])
    if ly:
        out["loi"] = ly
    try:
        dich = GOC / "hang_doi" / "bao_cao"; dich.mkdir(exist_ok=True)
        shutil.copy2(f, dich / f.name)
    except OSError:
        pass
    return out


def lam_mt5_backtest(slot: Path, v: dict, cho: int) -> tuple[str, dict]:
    loi = chuan_bi_ea(slot, v["ea_file"])
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
        "id": "bt_" + v["id"], "loai": "mt5_backtest", "uu_tien": int(v.get("uu_tien") or 5), "che_do": "ea_goc",
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot"); ap.add_argument("--may", default=socket.gethostname().lower().replace(" ", "_"))
    ap.add_argument("--mot-lan", action="store_true"); ap.add_argument("--cho-toi-da", type=int, default=4 * 3600)
    a = ap.parse_args()
    if not (GOC / ".tho_mt5_clone").exists():
        raise SystemExit("Chỉ chạy trong bản clone riêng của thợ (có tệp .tho_mt5_clone) — xem may_nha/README_THO_MT5.md")
    slot = chon_slot(a.slot)
    hd = HD.HangDoi(GOC, a.may, log=log)
    log("thợ %s bắt đầu, slot %s" % (a.may, slot))
    while True:
        v = (hd.dang_lam_cua_toi() or [None])[0] or hd.nhan()
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
        hd.xong(v, kq, tt, them_tep)
        if sinh:
            hd.them(sinh, "hang_doi: sinh việc từ %s" % v["id"])
        log("xong %s: %s — %s" % (v["id"], tt, kq.get("tom_tat")))
        if a.mot_lan:
            return


if __name__ == "__main__":
    main()
