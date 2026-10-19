# -*- coding: utf-8 -*-
"""cau_llm.py - CAU NOI LLM cho buoc DICH cua ong dan (18/10/2026, sua 19/10/2026 de chay tren MAY NHA).

KHOA: lay giong qwen/cau_hinh.py + qwen/mo_hinh.py, doc TAI CHO, KHONG chep, KHONG in, KHONG ghi file:
  1. bien moi truong AIBOX_API_KEY;
  2. ~/.cc-switch/cc-switch.db (bang providers, ten chua `cc_switch_provider`, mac dinh "aibox"; mo READ-ONLY);
  3. proxy cloud tu chen khoa (BRAIN_LLM_PROXY = base url cua proxy) neu co.
Box KHONG co khoa: moi ham tra {"trang_thai": "CHUA_CHAY_DUOC"} va khong goi mang.
THAM SO (base_url, model, model_du_phong, temperature, max_tokens, timeout_giay, so_lan_thu_lai): config/qwen.json, roi
config/tri_tue.json (model_openai, max_tokens, timeout_giay), roi mac dinh duoi day. 403 / het quota -> model du phong.
Ket qua LLM chi la DU LIEU (spec JSON hoac ma Python ham `tin_hieu(df)`); spec qua `kiem_spec`, ma Python qua
`nhan/dich_llm.py` (kiem AST + chay trong tien trinh con khong co khoa) truoc khi dung.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import time
import urllib.error
import urllib.request
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
CC_SWITCH_DB = Path.home() / ".cc-switch" / "cc-switch.db"
TRAN_MA = 16000
MAC_DINH = {"cc_switch_provider": "aibox", "base_url": "https://api.ai-box.vn/v1", "model": "qwen3.7-flash",
            "model_du_phong": "qwen3.6-flash", "temperature": 0, "max_tokens": 8000, "timeout_giay": 420,
            "so_lan_thu_lai": 3, "qua_cau_noi": False}
#: so lan goi / token cua tien trinh nay (dich_llm ghi ra bao cao). KHONG chua khoa.
THONG_KE = {"so_lan_goi": 0, "so_lan_loi": 0, "token_vao": 0, "token_ra": 0, "doi_du_phong": 0, "theo_model": {}}


def cau_hinh(goc: Path | None = None) -> dict:
    """Tham so mo hinh: config/qwen.json > config/tri_tue.json > MAC_DINH. Khong co khoa trong cac file nay."""
    goc = Path(goc or GOC)
    c = dict(MAC_DINH)
    tt = goc / "config" / "tri_tue.json"
    if tt.exists():
        try:
            d = json.loads(tt.read_text(encoding="utf-8-sig"))
            for k_src, k in (("model_openai", "model"), ("max_tokens", "max_tokens"), ("timeout_giay", "timeout_giay"),
                             ("temperature", "temperature"), ("cc_switch_provider", "cc_switch_provider")):
                if d.get(k_src) not in (None, ""):
                    c[k] = d[k_src]
        except Exception:
            pass
    q = goc / "config" / "qwen.json"
    if q.exists():
        try:
            d = json.loads(q.read_text(encoding="utf-8-sig"))
            for k in MAC_DINH:
                if d.get(k) not in (None, ""):
                    c[k] = d[k]
        except Exception:
            pass
    if os.environ.get("BRAIN_LLM_MODEL"):
        c["model"] = os.environ["BRAIN_LLM_MODEL"]
    return c


def tu_cc_switch(ten: str = "aibox", db: Path | None = None) -> dict:
    """Nhu qwen/mo_hinh.tu_cc_switch: {khoa, ten, base_url, model} hoac {}. Mo read-only, khong ghi gi."""
    db = Path(db or CC_SWITCH_DB)
    if not db.exists():
        return {}
    cn = None
    try:
        cn = sqlite3.connect("file:%s?mode=ro" % db.as_posix(), uri=True)
        cn.row_factory = sqlite3.Row
        for r in cn.execute("SELECT name, settings_config FROM providers"):
            if ten.lower() not in str(r["name"] or "").lower():
                continue
            cfg = json.loads(r["settings_config"] or "{}")
            khoa = (cfg.get("auth") or {}).get("OPENAI_API_KEY") or ""
            if not khoa:
                continue
            tho = str(cfg.get("config") or "")
            u = re.search(r'base_url\s*=\s*"([^"]+)"', tho)
            m = re.search(r'^model\s*=\s*"([^"]+)"', tho, re.M)
            return {"khoa": khoa, "ten": r["name"], "base_url": (u.group(1) if u else "").rstrip("/"),
                    "model": m.group(1) if m else ""}
    except Exception:
        return {}
    finally:
        if cn is not None:
            try:
                cn.close()
            except Exception:
                pass
    return {}


def duong(c: dict | None = None) -> dict:
    """{khoa, base_url, model, model_du_phong, nguon} - nguon: "bien_moi_truong" | "cc_switch:<ten>" | "proxy" | "".
    Khoa chi nam trong dict tra ve (bo nho), khong ghi / in o dau ca."""
    c = c or cau_hinh()
    base = str(os.environ.get("AIBOX_BASE_URL") or c["base_url"]).rstrip("/")
    if os.environ.get("AIBOX_API_KEY"):
        return {"khoa": os.environ["AIBOX_API_KEY"], "base_url": base, "model": c["model"],
                "model_du_phong": c["model_du_phong"], "nguon": "bien_moi_truong"}
    cc = tu_cc_switch(c.get("cc_switch_provider") or "aibox")
    if cc.get("khoa"):
        b = cc.get("base_url") or base
        if not c.get("qua_cau_noi") and ("127.0.0.1" in b or "localhost" in b):
            b = base                                    # goi thang, khong qua cau noi Codex
        return {"khoa": cc["khoa"], "base_url": b.rstrip("/"), "model": c["model"] or cc.get("model") or MAC_DINH["model"],
                "model_du_phong": c["model_du_phong"], "nguon": "cc_switch:%s" % cc.get("ten")}
    if os.environ.get("BRAIN_LLM_PROXY"):
        return {"khoa": "", "base_url": os.environ["BRAIN_LLM_PROXY"].rstrip("/"), "model": c["model"],
                "model_du_phong": c["model_du_phong"], "nguon": "proxy"}
    return {"khoa": "", "base_url": base, "model": c["model"], "model_du_phong": c["model_du_phong"], "nguon": ""}


def co_khoa(c: dict | None = None) -> bool:
    return bool(duong(c)["nguon"])


def _che(s: str, khoa: str) -> str:
    """Xoa khoa (va moi chuoi giong khoa) khoi thong bao loi truoc khi ghi log."""
    s = str(s or "")
    if khoa:
        s = s.replace(khoa, "***")
    return re.sub(r"(sk-|Bearer\s+)[A-Za-z0-9_\-\.]{8,}", r"\1***", s)


def _http(url: str, headers: dict, body: bytes, timeout: float) -> tuple[int, dict | str]:
    """Client mac dinh (urllib). -> (ma HTTP, json | van ban loi). Test thay bang client gia."""
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=headers), timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read().decode("utf-8", "replace")[:500]
        except Exception:
            return e.code, str(e)
    except Exception as e:  # noqa: BLE001
        return 0, str(e)[:300]


def _het_quota(ma: int, tho: str) -> bool:
    t = str(tho).lower()
    return ma in (402, 403) or (ma == 429 and any(x in t for x in ("quota", "insufficient", "balance", "het han", "limit exceeded")))


def goi(nguoi_dung: str, he_thong: str | None = None, model: str | None = None, max_tokens: int | None = None,
        han_giay: int | None = None, client=None, c: dict | None = None) -> dict:
    """-> {"trang_thai": "OK"|"CHUA_CHAY_DUOC"|"LOI", "van_ban", "ghi_chu", "model", "token_vao", "token_ra"}.
    403 / 402 / 429-het-quota voi model chinh -> thu model du phong. Loi tam (5xx, mang) -> thu lai so_lan_thu_lai."""
    c = c or cau_hinh()
    d = duong(c)
    if not d["nguon"]:
        return {"trang_thai": "CHUA_CHAY_DUOC", "van_ban": "", "model": "", "token_vao": 0, "token_ra": 0,
                "ghi_chu": "khong co khoa (AIBOX_API_KEY / cc-switch '%s' / BRAIN_LLM_PROXY) - buoc dich chay tren may nha"
                           % c.get("cc_switch_provider")}
    client = client or _http
    h = {"Content-Type": "application/json"}
    if d["khoa"]:
        h["Authorization"] = "Bearer " + d["khoa"]
    ds_model = [model or d["model"]]
    if d.get("model_du_phong") and d["model_du_phong"] not in ds_model:
        ds_model.append(d["model_du_phong"])
    ghi = []
    for i_m, m in enumerate(ds_model):
        body = json.dumps({"model": m, "temperature": c.get("temperature", 0), "max_tokens": int(max_tokens or c["max_tokens"]),
                           "stream": False, "messages": [{"role": "system", "content": he_thong or HE_THONG},
                                                         {"role": "user", "content": nguoi_dung}]}).encode()
        for lan in range(max(1, int(c.get("so_lan_thu_lai", 3)))):
            t0 = time.time()
            THONG_KE["so_lan_goi"] += 1
            tm = THONG_KE["theo_model"].setdefault(m, {"so_lan_goi": 0, "token_vao": 0, "token_ra": 0})
            tm["so_lan_goi"] += 1
            ma, kq = client(d["base_url"] + "/chat/completions", h, body, float(han_giay or c["timeout_giay"]))
            if ma == 200 and isinstance(kq, dict):
                u = kq.get("usage") or {}
                tv, tr = int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0)
                THONG_KE["token_vao"] += tv; THONG_KE["token_ra"] += tr
                tm["token_vao"] += tv; tm["token_ra"] += tr
                ch = kq.get("choices") or [{}]
                txt = ((ch[0].get("message") or {}).get("content") or "").strip()
                cham_tran = tr >= int(max_tokens or c["max_tokens"]) - 5
                return {"trang_thai": "OK" if txt else "LOI", "van_ban": txt, "model": m, "token_vao": tv, "token_ra": tr,
                        "ghi_chu": "%.0fs%s%s" % (time.time() - t0, " CHAM_TRAN_TOKEN" if cham_tran else "",
                                                  " (du phong)" if i_m else "")}
            THONG_KE["so_lan_loi"] += 1
            ghi.append("%s HTTP %s: %s" % (m, ma, _che(kq if isinstance(kq, str) else json.dumps(kq)[:200], d["khoa"])[:160]))
            if _het_quota(ma, kq if isinstance(kq, str) else json.dumps(kq)):
                if i_m + 1 < len(ds_model):
                    THONG_KE["doi_du_phong"] += 1
                break                                   # sang model du phong, khong thu lai cung model
            if ma in (400, 401, 404):
                break
            time.sleep(min(2 ** lan, 8) if client is _http else 0)
    return {"trang_thai": "LOI", "van_ban": "", "model": ds_model[-1], "token_vao": 0, "token_ra": 0,
            "ghi_chu": " | ".join(ghi)[-400:]}


HE_THONG = (
    "Ban la ky su dich chien luoc giao dich. Doc MA NGUON (MQL4/MQL5/Pine/Python/freqtrade) va tra ve DUY NHAT mot JSON, "
    "khong giai thich. Khong bia: phan nao khong chac thi de trong va ghi vao 'chua_dich'.")

MAU_BOC = """Tra JSON dang:
{"loai": "he_hoan_thien|co_che|tien_ich|mo_ta",
 "spec": [ {"ten": str, "chieu": 1|-1, "vao": [{"trai": {...}, "phep": ">"|"<"|">="|"<="|"cat_len"|"cat_xuong", "phai": {...}}]} ],
 "python": "def tin_hieu(df):\\n    ...",
 "co_che": [ {"vai_tro": "nguon_lenh|bo_loc|moc_vung|quan_li|go_lenh", "ten": str, "mo_ta": str, "tham": {}} ],
 "quan_tri": {"tp": str, "sl": str, "dca": str, "hedge": str, "trailing": str, "chot_ro": str, "go_lenh": str},
 "tham_so": {"ten_input": [gia_tri_thap, mac_dinh, cao]},
 "chua_dich": [str]}
Uu tien 'spec'. Toan hang trong 'vao' dung ngu phap The Brain, vi du {"chi_bao": "gia", "cot": "close"},
{"chi_bao": "sma", "n": 50}, {"chi_bao": "ema", "n": 20}, {"chi_bao": "rsi", "n": 14}, hang so {"hang": 30}.
Chi bao co san: gia, sma, ema, wma, smma, rsi, atr, macd, bollinger, donchian, stochastic, cci, adx, keltner, supertrend,
zscore, cao_nhat, thap_nhat, tre, doi, doi_pct, gio, ngay_trong_tuan.
Chi khi spec KHONG dien dat duoc moi dien 'python': MOT ham `tin_hieu(df)` nhan DataFrame cot open/high/low/close (chi muc
thoi gian), tra mang cung do dai gia tri 1 (mua) / -1 (ban) / 0; chi dung numpy (np), pandas (pd), math; KHONG import,
KHONG doc file / mang; tin hieu tai nen i chi dung du lieu den het nen i (KHONG shift(-k), KHONG nhin truoc).
MA NGUON (%s):
```
%s
```"""


def _json_trong(van_ban: str) -> dict | None:
    m = re.search(r"\{.*\}", van_ban or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except ValueError:
        return None


def kiem_spec(sp: dict) -> list[str]:
    """Kiem toi thieu mot spec LLM tra ve truoc khi dung (khong exec gi)."""
    loi = []
    if not isinstance(sp, dict) or not sp.get("vao"):
        return ["spec khong co 'vao'"]
    for d in sp["vao"]:
        if not isinstance(d, dict) or d.get("phep") not in (">", "<", ">=", "<=", "cat_len", "cat_xuong"):
            loi.append("dieu kien hong: %s" % str(d)[:80])
    try:
        if int(sp.get("chieu", 1) or 1) not in (1, -1):
            loi.append("chieu khong phai 1/-1")
    except (TypeError, ValueError):
        loi.append("chieu khong phai so")
    return loi


def boc_tach(ma_nguon: str, ngon_ngu: str = "MQL5", client=None, c: dict | None = None) -> dict:
    """Ma nguon -> {trang_thai, loai, spec[], python, co_che[], quan_tri{}, tham_so{}, chua_dich[], model, token_*}."""
    r = goi(MAU_BOC % (ngon_ngu, (ma_nguon or "")[:TRAN_MA]), client=client, c=c)
    meta = {k: r.get(k) for k in ("model", "token_vao", "token_ra", "ghi_chu")}
    if r["trang_thai"] != "OK":
        return dict(meta, trang_thai=r["trang_thai"])
    d = _json_trong(r["van_ban"])
    if d is None:
        return dict(meta, trang_thai="LOI", ghi_chu="LLM khong tra JSON (%s)" % r.get("ghi_chu"))
    spec_ok = []
    for sp in d.get("spec") or []:
        loi = kiem_spec(sp)
        if loi:
            d.setdefault("chua_dich", []).extend(loi)
        else:
            spec_ok.append(sp)
    d["spec"] = spec_ok
    if not isinstance(d.get("python"), str):
        d["python"] = ""
    d.update(meta)
    d["trang_thai"] = "OK"
    d["nhan"] = "LLM (%s) - can MT5 xac nhan" % r.get("model")
    return d
