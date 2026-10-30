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
#: 20/10/2026: tang moi lan doi prompt / chuan hoa -> the HONG vi loi phia ta (prompt, bo kiem) duoc kiem / dich lai.
PHIEN_PROMPT = 3
MAC_DINH = {"cc_switch_provider": "aibox", "base_url": "https://api.ai-box.vn/v1", "model": "qwen3.7-flash",
            "model_du_phong": "qwen3.6-flash", "temperature": 0, "max_tokens": 8000, "timeout_giay": 420,
            "so_lan_thu_lai": 3, "qua_cau_noi": False}
#: 20/10/2026 09:56 (chu du an): model DICH co dinh, manh, chon bang do (nhan/chon_model_llm.py tren may nha) ->
#: config/llm_dich.json. Tep nay thang config/qwen.json (qwen.json con dung cho he `q` khac, khong sua).
LLM_DICH = "llm_dich.json"
KHOA_DICH = ("model", "model_du_phong", "temperature", "max_tokens", "timeout_giay", "so_lan_thu_lai", "tran_ma",
             "chi_du_phong_khi_5xx", "so_lan_thu_429", "tham_so_them")
#: so lan goi / token cua tien trinh nay (dich_llm ghi ra bao cao). KHONG chua khoa.
THONG_KE = {"so_lan_goi": 0, "so_lan_loi": 0, "token_vao": 0, "token_ra": 0, "token_suy_luan": 0, "token_vao_cache": 0,
            "doi_du_phong": 0, "theo_model": {}}


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
    ld = goc / "config" / LLM_DICH
    if ld.exists():
        try:
            d = json.loads(ld.read_text(encoding="utf-8-sig"))
            for k in KHOA_DICH:
                if d.get(k) not in (None, ""):
                    c[k] = d[k]
            if d.get("model") and not d.get("model_du_phong"):
                c["model_du_phong"] = ""                # da khoa model manh: KHONG lui ve flash
        except Exception:
            pass
    if os.environ.get("BRAIN_LLM_MODEL"):
        c["model"] = os.environ["BRAIN_LLM_MODEL"]
        if os.environ.get("BRAIN_LLM_KHONG_DU_PHONG"):
            c["model_du_phong"] = ""
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
    try:
        from nhan import hang_cho_llm as HCL
        if HCL.dang_bat():
            return True
    except Exception:
        pass
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


#: 20/10/2026 21:10 (may nha): lan goi gan nhat bi tu choi vi HET QUOTA (402/403/429-quota) o MOI model da thu.
#: goi() tra CHUA_CHAY_DUOC (loi khong do the -> KHONG tinh LOI_LLM / BO_QUA) va ghi vao day; dich_llm.buoc_dich_llm
#: xoa dau luot, thay co -> bo qua phan con lai cua luot va ong_dan.py dich_llm tra rc=3 (dieu_phoi nghi roi lam Python).
#: Su co that 20/10 21:00: ai-box het quota -> 4 luot lien tiep ~470 the bi dem LOI_LLM, se thanh BO_QUA sau 3 lan.
HET_QUOTA: dict = {}


def _het_quota(ma: int, tho: str) -> bool:
    t = str(tho).lower()
    return ma in (402, 403) or (ma == 429 and any(x in t for x in ("quota", "insufficient", "balance", "het han", "limit exceeded")))


def goi(nguoi_dung: str, he_thong: str | None = None, model: str | None = None, max_tokens: int | None = None,
        han_giay: int | None = None, client=None, c: dict | None = None, loai_viec: str = "dich_boc") -> dict:
    """-> {"trang_thai": "OK"|"CHUA_CHAY_DUOC"|"LOI"|"CHO", "van_ban", "ghi_chu", "model", "token_vao", "token_ra"}.
    403 / 402 / 429-het-quota voi model chinh -> thu model du phong. Loi tam (5xx, mang) -> thu lai so_lan_thu_lai.
    BRAIN_LLM_PROVIDER=hang_cho: xep file queue, khong goi mang."""
    c = c or cau_hinh()
    try:
        from nhan import hang_cho_llm as HCL
        if HCL.dang_bat() and client is None:
            return HCL.xep_hang(
                loai_viec or "dich_boc",
                he_thong if he_thong is not None else HE_THONG,
                nguoi_dung or "",
                tru="DICH_LLM",
                model_goi_y=str(model or c.get("model") or ""),
                ep_json=True,
                max_tokens=int(max_tokens or c.get("max_tokens") or 0) or None,
            )
    except Exception as e:  # noqa: BLE001 - khong de hang_cho pha goi API
        if (os.environ.get("BRAIN_LLM_PROVIDER") or "").strip().lower() in ("hang_cho", "file", "queue"):
            return {"trang_thai": "LOI", "van_ban": "", "model": "hang_cho", "token_vao": 0, "token_ra": 0,
                    "ghi_chu": "hang_cho loi: %s" % str(e)[:160], "pending": False}
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
    quota_m = []
    chi_5xx = bool(c.get("chi_du_phong_khi_5xx"))
    for i_m, m in enumerate(ds_model):
        if i_m and chi_5xx and not any((" HTTP 5" in g or " HTTP 0:" in g) for g in ghi if g.startswith(ds_model[i_m - 1] + " ")):
            break                                       # 20/10/2026: chi lui sang model du phong khi model chinh loi 5xx / mang
        bd = {"model": m, "temperature": c.get("temperature", 0), "max_tokens": int(max_tokens or c["max_tokens"]),
              "stream": False, "messages": [{"role": "system", "content": he_thong or HE_THONG},
                                            {"role": "user", "content": nguoi_dung}]}
        # 20/10/2026 (kiem chi phi): tham so them theo model, vd {"qwen3.7-max": {"enable_thinking": false}} hoac
        # {"*": {"thinking_budget": 4000}} - mac dinh rong = hanh vi cu. Do that: 90% token ra cua qwen3.7-max la suy luan.
        ts = c.get("tham_so_them") or {}
        if isinstance(ts, dict):
            for k_m in ("*", m):
                if isinstance(ts.get(k_m), dict):
                    bd.update({k: v for k, v in ts[k_m].items() if k not in ("model", "messages")})
        body = json.dumps(bd).encode()
        for lan in range(max(1, int(c.get("so_lan_thu_lai", 3)), int(c.get("so_lan_thu_429", 6)))):
            t0 = time.time()
            THONG_KE["so_lan_goi"] += 1
            tm = THONG_KE["theo_model"].setdefault(m, {"so_lan_goi": 0, "token_vao": 0, "token_ra": 0})
            tm["so_lan_goi"] += 1
            ma, kq = client(d["base_url"] + "/chat/completions", h, body, float(han_giay or c["timeout_giay"]))
            if ma == 200 and isinstance(kq, dict):
                u = kq.get("usage") or {}
                tv, tr = int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0)
                tsl = int((u.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0)
                tvc = int((u.get("prompt_tokens_details") or {}).get("cached_tokens") or 0)
                THONG_KE["token_vao"] += tv; THONG_KE["token_ra"] += tr
                THONG_KE["token_suy_luan"] = THONG_KE.get("token_suy_luan", 0) + tsl
                THONG_KE["token_vao_cache"] = THONG_KE.get("token_vao_cache", 0) + tvc
                tm["token_vao"] += tv; tm["token_ra"] += tr
                tm["token_suy_luan"] = tm.get("token_suy_luan", 0) + tsl
                ch = kq.get("choices") or [{}]
                txt = ((ch[0].get("message") or {}).get("content") or "").strip()
                cham_tran = tr >= int(max_tokens or c["max_tokens"]) - 5
                return {"trang_thai": "OK" if txt else "LOI", "van_ban": txt, "model": m, "token_vao": tv, "token_ra": tr,
                        "token_suy_luan": tsl, "token_vao_cache": tvc, "ghi_chu": "%.0fs%s%s" % (time.time() - t0, " CHAM_TRAN_TOKEN" if cham_tran else "",
                                                  " (du phong)" if i_m else "")}
            THONG_KE["so_lan_loi"] += 1
            ghi.append("%s HTTP %s: %s" % (m, ma, _che(kq if isinstance(kq, str) else json.dumps(kq)[:200], d["khoa"])[:160]))
            if _het_quota(ma, kq if isinstance(kq, str) else json.dumps(kq)):
                quota_m.append(m)
                if i_m + 1 < len(ds_model):
                    THONG_KE["doi_du_phong"] += 1
                break                                   # sang model du phong, khong thu lai cung model
            if ma in (400, 401, 404):
                break
            if ma == 429:
                # 20/10/2026: 429 gioi han toc do (khong phai het quota) -> lui dan 5,10,20..60 s, them luot thu, ghi thong ke
                THONG_KE["so_lan_429"] = THONG_KE.get("so_lan_429", 0) + 1
                time.sleep(min(5 * 2 ** lan, 60) if client is _http else 0)
                continue
            so_loi_khac = sum(1 for g in ghi if (" HTTP 429:" not in g) and g.startswith(m + " "))
            if so_loi_khac >= max(1, int(c.get("so_lan_thu_lai", 3))):
                break                                   # loi khac 429: giu so lan thu lai cu
            time.sleep(min(2 ** lan, 8) if client is _http else 0)
    da_thu = {g.split(" ", 1)[0] for g in ghi}
    if quota_m and da_thu and da_thu <= set(quota_m):
        HET_QUOTA.update(luc=time.strftime("%Y-%m-%dT%H:%M:%S"), ghi_chu=" | ".join(ghi)[-300:])
        return {"trang_thai": "CHUA_CHAY_DUOC", "van_ban": "", "model": ds_model[-1], "token_vao": 0, "token_ra": 0,
                "ghi_chu": "HET_QUOTA: " + " | ".join(ghi)[-380:]}
    return {"trang_thai": "LOI", "van_ban": "", "model": ds_model[-1], "token_vao": 0, "token_ra": 0,
            "ghi_chu": " | ".join(ghi)[-400:]}


HE_THONG = (
    "Ban la ky su dich chien luoc giao dich. Doc MA NGUON (MQL4/MQL5/Pine/Python/freqtrade) va tra ve DUY NHAT mot JSON, "
    "khong giai thich. Khong bia: phan nao khong chac thi de trong va ghi vao 'chua_dich'.")

MAU_BOC = """Tra JSON dang:
{"loai": "he_hoan_thien|co_che|tien_ich|mo_ta",
 "spec": [ {"ten": str, "chieu": 1|-1, "vao": [{"trai": {...}, "phep": ">"|"<"|">="|"<="|"cat_len"|"cat_xuong", "phai": {...}}]} ],
 "python": "def tin_hieu(df):\\n    ...",
 "luoi": {"che_do": "luoi_hai_chieu|luon_vao|mot_chieu", "chieu": "hai|mua|ban", "loc_python": "", "lot0": 0.01,
          "buoc_diem": 0, "toi_da": 0, "he_so_lot": 1.0, "tp_diem": 0, "hedge_khi_lo_pct": 0,
          "cat_lo_tien": 0, "nghi_gio": []},
 "co_che": [ {"vai_tro": "nguon_lenh|bo_loc|moc_vung|quan_li|go_lenh", "ten": str, "mo_ta": str, "tham": {}} ],
 "quan_tri": {"tp": str, "sl": str, "dca": str, "hedge": str, "trailing": str, "chot_ro": str, "go_lenh": str},
 "tham_so": {"ten_input": [gia_tri_thap, mac_dinh, cao]},
 "chua_dich": [str]}
Uu tien 'spec'. 'phep' CHI duoc la: ">", "<", ">=", "<=", "==", "!=", "cheo_len" (trai cat len tren phai), "cheo_xuong".
'chieu' la so 1 (mua) hoac -1 (ban); moi chieu mot spec rieng. Toan hang dung ngu phap The Brain, vi du
{"chi_bao": "gia", "cot": "close"}, {"chi_bao": "sma", "n": 50}, {"chi_bao": "ema", "n": 20}, {"chi_bao": "rsi", "n": 14},
hang so {"hang": 30}. Chi bao co san: gia, sma, ema, wma, smma, rsi, atr, macd, bollinger, donchian, stochastic, cci, adx,
keltner, supertrend, gio, ngay_trong_tuan. Toan tu BIEN DOI phai co truong "cua" (toan hang goc):
{"chi_bao": "tre", "n": 1, "cua": {...}} (gia tri nen truoc), {"chi_bao": "cao_nhat", "n": 20, "cua": {"chi_bao": "gia", "cot": "high"}},
thap_nhat, zscore, doi, doi_pct, tb, do_lech cung kieu.
Chi khi spec KHONG dien dat duoc moi dien 'python': MOT ham `tin_hieu(df)` nhan DataFrame cot open/high/low/close (chi muc
thoi gian), tra mang cung do dai gia tri 1 (mua) / -1 (ban) / 0; np, pd, math da co san - KHONG import, KHONG class,
KHONG doc file / mang; tin hieu tai nen i chi dung du lieu den het nen i (KHONG shift(-k), KHONG center=True, KHONG bfill,
KHONG dung gia tri cuoi chuoi nhu iloc[-1] / max() ca chuoi).
BAT BUOC (20/10/2026, do tren dau ra A/B: 14/30 ket qua OK ra 0 lenh):
- KHONG tra tin hieu gia (vd `return [0]*len(df)`, np.zeros): neu khong dich duoc thi de python "" va ghi ly do vao chua_dich.
- KHONG cung gia TUYET DOI cua mot ma (vd muc trung tam 5355.0 cua vang): bo may chay tren NHIEU ma khac thang gia ->
  quy muc gia ve tuong doi (phan tram gia, boi ATR, cao/thap nhat N nen gan nhat).
- EA LUOI / MARTINGALE / HEDGE KHONG CO TIN HIEU CHIEU (mo lenh vo dieu kien, mo ca mua va ban, luon co lenh): KHONG
  bia tin hieu - dien 'luoi' (de spec [] va python ""), giu DUNG mac dinh input cua tac gia, don vi nhu tac gia:
  buoc_diem / tp_diem theo Point (hoac buoc_pct / tp_pct phan cua gia, hoac tp_tien), tp_tien / cat_lo_tien la USD o lot0; toi_da = so lenh NHOI them (khong tinh lenh
  dau); he_so_lot = he so nhan lot moi tang; chieu "hai" = ro mua va ro ban doc lap; luon_vao = vao lai ngay sau khi
  chot ro; mot_chieu + chieu "mua"/"ban" khi tac gia chi mo mot chieu; co dieu kien chon chieu (vd gia > EMA) thi
  dat vao loc_python (ham tin_hieu(df) nhu tren: 1 cho ro mua, -1 cho ro ban). Martingale DAO CHIEU sau lenh lo:
  chua bieu dien duoc -> ghi chua_dich.
- EA luoi / DCA / martingale CO dieu kien vao lenh dau: dich DIEU KIEN MO LENH DAU (nguon_lenh) thanh tin hieu; luoi, nhoi,
  hedge, chot ro ghi vao 'quan_tri' (bo may quan li lenh tu lam). Tin hieu phai ra lenh that tren gia H1 thuong
  (it nhat vai lenh moi 1000 nen); dieu kien qua hiem (nhieu bo loc AND, nguong cuc tri) thi noi long ve mac dinh cua EA.
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


#: Phep so sanh ma bo may DSL (`nhan/ngu_phap._so_sanh`) THAT SU hieu. 20/10/2026: truoc day prompt va kiem_spec dung
#: "cat_len"/"cat_xuong" nhung ngu_phap chi biet "cheo_len"/"cheo_xuong" -> MOI spec giao cat (dang vao lenh pho bien
#: nhat cua EA) deu hong "phep so sanh khong biet: 'cat_len'" o buoc kiem.
PHEP_DUNG = (">", "<", ">=", "<=", "==", "!=", "cheo_len", "cheo_xuong")
BI_DANH_PHEP = {"cat_len": "cheo_len", "cat_xuong": "cheo_xuong", "cross_above": "cheo_len", "crosses_above": "cheo_len",
                "cross_up": "cheo_len", "crossover": "cheo_len", "crosses_over": "cheo_len", "cross_over": "cheo_len",
                "cross_below": "cheo_xuong", "crosses_below": "cheo_xuong", "cross_down": "cheo_xuong",
                "crossunder": "cheo_xuong", "crosses_under": "cheo_xuong", "cross_under": "cheo_xuong",
                "=": "==", "eq": "==", "<>": "!=", "gt": ">", "lt": "<", "ge": ">=", "le": "<="}
BI_DANH_CHIEU = {"mua": 1, "buy": 1, "long": 1, "1": 1, "+1": 1, "ban": -1, "sell": -1, "short": -1, "-1": -1}
#: Toan tu bien doi cua ngu_phap: BAT BUOC co truong "cua"; LLM hay bo -> mac dinh la gia dong cua (hoac cot da ghi).
BIEN_DOI = {"tb", "do_lech", "phuong_sai", "zscore", "phan_vi", "doi", "doi_pct", "tre", "cao_nhat", "thap_nhat",
            "tuyet_doi", "tong"}
BI_DANH_CB = {"price": "gia", "close": "gia", "highest": "cao_nhat", "lowest": "thap_nhat", "shift": "tre",
              "lag": "tre", "change": "doi", "roc": "doi_pct", "hour": "gio", "dayofweek": "ngay_trong_tuan"}


def _chuan_hoa_th(t):
    """Mot toan hang LLM -> dang ngu_phap hieu (khong exec gi). Chuoi so -> hang so."""
    if isinstance(t, (int, float)) and not isinstance(t, bool):
        return {"hang": float(t)}
    if isinstance(t, str):
        try:
            return {"hang": float(t)}
        except ValueError:
            return {"chi_bao": "gia", "cot": t.lower()} if t.lower() in ("open", "high", "low", "close") else t
    if not isinstance(t, dict):
        return t
    t = dict(t)
    if "hang" in t and isinstance(t["hang"], str):
        try:
            t["hang"] = float(t["hang"])
        except ValueError:
            pass
    cb = str(t.get("chi_bao", "")).lower()
    if cb in BI_DANH_CB:
        if cb == "close":
            t.setdefault("cot", "close")
        cb = BI_DANH_CB[cb]
    if cb:
        t["chi_bao"] = cb
    if cb in BIEN_DOI and "cua" not in t:
        t["cua"] = {"chi_bao": "gia", "cot": str(t.pop("cot", "close")).lower()}
    if isinstance(t.get("cua"), (dict, str, int, float)):
        t["cua"] = _chuan_hoa_th(t["cua"])
    return t


def chuan_hoa_spec(sp: dict) -> dict:
    """Chuan hoa spec LLM truoc kiem_spec / ngu_phap: bi danh phep, chieu chu ("buy"), toan tu bien doi thieu "cua"."""
    sp = dict(sp)
    ch = sp.get("chieu", 1)
    if isinstance(ch, str):
        sp["chieu"] = BI_DANH_CHIEU.get(ch.strip().lower(), ch)
    vao = sp.get("vao")
    if isinstance(vao, dict):
        vao = [vao]
    if isinstance(vao, list):
        moi = []
        for d in vao:
            if isinstance(d, dict):
                d = dict(d)
                p = str(d.get("phep", "")).strip()
                d["phep"] = BI_DANH_PHEP.get(p.lower(), p)
                for k in ("trai", "phai"):
                    if k in d:
                        d[k] = _chuan_hoa_th(d[k])
            moi.append(d)
        sp["vao"] = moi
    return sp


def kiem_spec(sp: dict) -> list[str]:
    """Kiem toi thieu mot spec LLM tra ve truoc khi dung (khong exec gi)."""
    loi = []
    if not isinstance(sp, dict) or not sp.get("vao"):
        return ["spec khong co 'vao'"]
    for d in sp["vao"]:
        if not isinstance(d, dict) or d.get("phep") not in PHEP_DUNG:
            loi.append("dieu kien hong: %s" % str(d)[:80])
    try:
        if int(sp.get("chieu", 1) or 1) not in (1, -1):
            loi.append("chieu khong phai 1/-1")
    except (TypeError, ValueError):
        loi.append("chieu khong phai so")
    return loi


_HAM_CHINH = re.compile(r"\b(OnTick|OnCalculate|OnBar|OnTimer|OnTrade|start|populate_\w+|next|on_bar|tin_hieu)\s*\(")
_KY_LENH = re.compile(r"OrderSend|trade\.(Buy|Sell|PositionOpen)|\.Buy\(|\.Sell\(|strategy\.(entry|order)|enter_long|"
                      r"enter_short|buy_signal|sell_signal|iCustom|iMA|iRSI|iBands|iMACD|iStochastic|iATR|iCCI|iADX")


def rut_gon_ma(vb: str, tran: int = TRAN_MA) -> str:
    """Ma nguon -> doan gui LLM <= tran ky tu. 20/10/2026: truoc day cat CUNG tran ky tu DAU file: EA MQL dai (thu vien,
    giao dien, khai bao) bi mat het OnTick / logic vao lenh -> LLM "khong ra spec hay python" (loai HONG pho bien).
    Nay: bo chu thich + dong trong; con dai thi giu (1) dong input/extern, (2) cac ham chinh (OnTick, OnCalculate,
    populate_*...) va ham co lenh/chi bao, (3) phan dau file cho du tran."""
    if len(vb or "") <= tran:
        return vb or ""
    t = re.sub(r"/\*.*?\*/", "", vb or "", flags=re.S)
    t = re.sub(r"(?m)^\s*//.*$", "", t)
    t = re.sub(r"(?m)[ \t]+$", "", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    if len(t) <= tran:
        return t
    dong = t.split("\n")
    giu = [x for x in dong if re.match(r"\s*(input|extern|sinput)\b", x)][:80]
    # tach ham theo ngoac nhon (MQL/Pine kieu C) hoac theo "def " (Python)
    khoi, i = [], 0
    while i < len(dong):
        x = dong[i]
        if _HAM_CHINH.search(x) or (re.match(r"\s*(def |[\w:<>\*&\s]+\()", x) and i + 1 < len(dong)):
            j, sau, mo = i, 0, False
            buf = []
            while j < len(dong) and j - i < 400:
                buf.append(dong[j]); sau += dong[j].count("{") - dong[j].count("}")
                mo = mo or "{" in dong[j]
                j += 1
                if mo and sau <= 0:
                    break
                if x.lstrip().startswith("def ") and j < len(dong) and dong[j] and not dong[j][:1].isspace():
                    break
            vb_k = "\n".join(buf)
            if _HAM_CHINH.search(x):
                khoi.append((0, vb_k))
            elif _KY_LENH.search(vb_k):
                khoi.append((1, vb_k))
            i = max(j, i + 1)
        else:
            i += 1
    ra = "\n".join(giu)
    for _, k in sorted(khoi, key=lambda z: z[0]):
        if len(ra) + len(k) + 1 > tran:
            continue
        ra += "\n" + k
    if len(ra) < tran:
        ra = t[: tran - len(ra) - 40] + "\n// ... (rut gon) ...\n" + ra
    return ra[:tran]


def boc_tach(ma_nguon: str, ngon_ngu: str = "MQL5", client=None, c: dict | None = None) -> dict:
    """Ma nguon -> {trang_thai, loai, spec[], python, co_che[], quan_tri{}, tham_so{}, chua_dich[], model, token_*}."""
    c = c or cau_hinh()
    r = goi(MAU_BOC % (ngon_ngu, rut_gon_ma(ma_nguon or "", int(c.get("tran_ma") or TRAN_MA))), client=client, c=c, loai_viec="dich_boc")
    meta = {k: r.get(k) for k in ("model", "token_vao", "token_ra", "token_suy_luan", "ghi_chu")}
    if r["trang_thai"] != "OK":
        return dict(meta, trang_thai=r["trang_thai"])
    d = _json_trong(r["van_ban"])
    if d is None:
        return dict(meta, trang_thai="LOI", ghi_chu="LLM khong tra JSON (%s)" % r.get("ghi_chu"))
    if not isinstance(d, dict):
        return dict(meta, trang_thai="LOI", ghi_chu="LLM tra JSON khong phai object")
    # 19/10/2026: LLM co the tra chua_dich = null / chuoi / list dict, spec = dict / chuoi -> truoc day AttributeError /
    # TypeError trong thread pool lam SAP ca luot dich_llm (va ca vong dich nen). Chuan hoa truoc khi dung.
    cd = d.get("chua_dich")
    d["chua_dich"] = [str(x) for x in cd] if isinstance(cd, list) else ([str(cd)] if cd else [])
    sp_ds = d.get("spec")
    sp_ds = sp_ds if isinstance(sp_ds, list) else ([sp_ds] if isinstance(sp_ds, dict) else [])
    spec_ok = []
    for sp in sp_ds:
        try:
            sp = chuan_hoa_spec(sp) if isinstance(sp, dict) else sp
            loi = kiem_spec(sp) if isinstance(sp, dict) else ["spec khong phai object"]
        except Exception as e:  # noqa: BLE001
            loi = ["kiem_spec loi: %s" % str(e)[:120]]
        if loi:
            d["chua_dich"].extend(str(x) for x in (loi if isinstance(loi, list) else [loi]))
        else:
            spec_ok.append(sp)
    d["spec"] = spec_ok
    if not isinstance(d.get("python"), str):
        d["python"] = ""
    if not isinstance(d.get("luoi"), dict):
        d["luoi"] = {}
    d.update(meta)
    d["trang_thai"] = "OK"
    d["nhan"] = "LLM (%s) - can MT5 xac nhan" % r.get("model")
    return d


MAU_SUA = """Ban dich truoc cua ban cho MA NGUON duoi day KHONG DAT khi chay tren gia mau (%s, %d nen, gia %.5g-%.5g).
CHAN DOAN (bo kiem tu dong):
%s
BAN DICH TRUOC (JSON):
```
%s
```
Sua theo chan doan va tra lai DUY NHAT mot JSON dung dang cu. Neu that su khong dich duoc thanh tin hieu tu gia OHLC thi
de spec [] va python "" va ghi ly do vao chua_dich (KHONG tra tin hieu gia toan 0).
MA NGUON (%s):
```
%s
```"""


def sua_lai(ma_nguon: str, ngon_ngu: str, truoc: dict, chan_doan: list, mo_ta_gia: tuple, client=None,
            c: dict | None = None) -> dict:
    """20/10/2026: hoi lai LLM MOT lan kem chan doan cua bo kiem (0 lenh / nhin truoc / loi chay). Dang tra nhu boc_tach."""
    c = c or cau_hinh()
    gon = {k: truoc.get(k) for k in ("loai", "spec", "python", "luoi", "quan_tri", "chua_dich")}
    nguon, n, lo, hi = mo_ta_gia
    nhac = MAU_SUA % (nguon, n, lo, hi, "\n".join("- " + str(x) for x in chan_doan),
                      json.dumps(gon, ensure_ascii=False)[:12000], ngon_ngu,
                      rut_gon_ma(ma_nguon or "", int(c.get("tran_ma") or TRAN_MA)))
    r = goi(nhac, client=client, c=c, loai_viec="dich_sua")
    meta = {k: r.get(k) for k in ("model", "token_vao", "token_ra", "token_suy_luan", "ghi_chu")}
    if r["trang_thai"] != "OK":
        return dict(meta, trang_thai=r["trang_thai"])
    d = _json_trong(r["van_ban"])
    if not isinstance(d, dict):
        return dict(meta, trang_thai="LOI", ghi_chu="LLM sua: khong tra JSON object")
    cd = d.get("chua_dich")
    d["chua_dich"] = [str(x) for x in cd] if isinstance(cd, list) else ([str(cd)] if cd else [])
    sp_ds = d.get("spec")
    sp_ds = sp_ds if isinstance(sp_ds, list) else ([sp_ds] if isinstance(sp_ds, dict) else [])
    d["spec"] = [chuan_hoa_spec(x) for x in sp_ds if isinstance(x, dict) and not kiem_spec(chuan_hoa_spec(x))]
    if not isinstance(d.get("python"), str):
        d["python"] = ""
    d.update(meta)
    d["trang_thai"] = "OK"
    d["nhan"] = "LLM (%s) - da sua 1 lan theo chan doan - can MT5 xac nhan" % r.get("model")
    return d
