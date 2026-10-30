# -*- coding: utf-8 -*-
"""tai_lich_su_trinh_duyet.py — Playwright fetch MQL5/Myfxbook history CSV on home.

Uses a persistent Chrome profile under E:\\brain2_grok_tin_hieu\\pw_profile
(copied from the user's logged-in Chrome profile). Does NOT extract/decrypt
cookies or tokens; drives the real browser UI (Export to CSV: History).

Disk: temp on E: first. BelowNormal priority expected from the caller.
Polite: --nghi >=5s. Cap: --toi-da 100/night. Filter age>=12m via list JSON.

Known blocks (as of 2026-10-30, Asia/Bangkok):
- MQL5: Export History requires community login. Home IP returns HTTP 403 on
  /en and /en/auth_login; signal pages may still load. MT5 Terminal only has
  bases/signals/signals.dat (catalog) — no trade-history CSV. Needs a logged-in
  session in the synced Chrome profile (or VPN/other egress for login).
- Myfxbook: page loads via browser + host-resolver DNS map, but #csvStatement
  opens a reCAPTCHA modal before getCSVFile(). Fully automated export blocked
  by captcha (no captcha bypass).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))
sys.path.insert(0, str(GOC / "tools"))

TIN_HIEU_GOC = Path(os.environ.get("BRAIN_TIN_HIEU") or r"E:\brain2_grok_tin_hieu")
PW_PROFILE = Path(os.environ.get("BRAIN_PW_PROFILE") or (TIN_HIEU_GOC / "pw_profile"))
MQL5_CSV = Path(os.environ.get("BRAIN_MQL5_CSV") or (TIN_HIEU_GOC / "data" / "mql5_csv"))
MYFX_CSV = Path(os.environ.get("BRAIN_MYFXBOOK_CSV") or (TIN_HIEU_GOC / "data" / "myfxbook_csv"))
TMP = TIN_HIEU_GOC / "tmp" / "pw_dl"
LOGS = TIN_HIEU_GOC / "logs"
CHROME_USER_DATA = Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "User Data"

# VNPT NXDOMAIN for myfxbook; MQL5 static IP helps some resolvers
HOST_RESOLVER = (
    "MAP www.myfxbook.com 104.18.23.170, "
    "MAP myfxbook.com 104.18.23.170, "
    "MAP static.mfbcdn.net 104.18.23.170, "
    "MAP www.mql5.com 36.255.76.151, "
    "MAP mql5.com 36.255.76.151, "
    "EXCLUDE localhost"
)

CHROME_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-extensions",
    "--no-first-run",
    "--no-default-browser-check",
    "--host-resolver-rules=" + HOST_RESOLVER,
]


def _chon_chrome_profile() -> Path | None:
    """Pick Chrome profile that already visited mql5/myfxbook (Preferences text only)."""
    if not CHROME_USER_DATA.is_dir():
        return None
    best = None
    score_best = -1
    for d in CHROME_USER_DATA.iterdir():
        if not d.is_dir():
            continue
        if d.name != "Default" and not d.name.startswith("Profile "):
            continue
        prefs = d / "Preferences"
        if not prefs.exists():
            continue
        try:
            txt = prefs.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        sc = 0
        if "mql5.com" in txt:
            sc += 2
        if "myfxbook.com" in txt:
            sc += 1
        if sc > score_best:
            score_best = sc
            best = d
    return best if score_best > 0 else None


def _chrome_dang_chay() -> bool:
    try:
        import subprocess
        r = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
            capture_output=True, text=True, timeout=15,
        )
        return "chrome.exe" in (r.stdout or "").lower()
    except Exception:
        return False


def dong_bo_pw_profile(*, force: bool = False, chi_cookies: bool = False) -> dict:
    """Copy selected Chrome profile → E:\\...\\pw_profile\\Default (no cookie decrypt).

    Skips Cache/GPUCache/Code Cache. Cookies may be locked while Chrome runs —
    when unlocked we re-copy Cookies preferentially.
    """
    src = _chon_chrome_profile()
    if src is None:
        return {"ok": False, "ly_do": "khong_tim_thay_profile_mql5_myfxbook"}
    dest_root = PW_PROFILE
    dest = dest_root / "Default"
    marker = dest_root / ".nguon_profile.txt"
    cookies_src = src / "Network" / "Cookies"
    cookies_dst = dest / "Network" / "Cookies"

    if chi_cookies and dest.exists() and cookies_src.exists():
        if _chrome_dang_chay():
            return {"ok": True, "src": str(src), "bo_qua": "chrome_dang_chay_cookies_khoa",
                    "cookies_bytes": cookies_dst.stat().st_size if cookies_dst.exists() else 0}
        try:
            cookies_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(cookies_src, cookies_dst)
            return {"ok": True, "src": str(src), "cookies_resync": True,
                    "cookies_bytes": cookies_dst.stat().st_size}
        except OSError as e:
            return {"ok": False, "ly_do": "cookies_resync_fail:%s" % e}

    if dest.exists() and not force and marker.exists():
        # still try soft cookies refresh if chrome idle
        soft = {}
        if not _chrome_dang_chay() and cookies_src.exists():
            try:
                cookies_dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(cookies_src, cookies_dst)
                soft = {"cookies_resync": True, "cookies_bytes": cookies_dst.stat().st_size}
            except OSError:
                soft = {"cookies_resync": False}
        return {"ok": True, "src": str(src), "dest": str(dest), "bo_qua": "da_co", **soft}

    dest_root.mkdir(parents=True, exist_ok=True)
    ls_src = CHROME_USER_DATA / "Local State"
    if ls_src.exists():
        try:
            shutil.copy2(ls_src, dest_root / "Local State")
        except OSError as e:
            (dest_root / "Local State").write_text("{}", encoding="utf-8")
            print("[pw_profile] Local State copy fail:", e)
    exclude_dir = {
        "Cache", "Code Cache", "GPUCache", "Service Worker",
        "DawnGraphiteCache", "DawnWebGPUCache", "GrShaderCache",
        "ShaderCache", "optimization_guide_prediction_model_store",
    }
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)
    copied = 0
    skipped = 0
    for root, dirs, files in os.walk(src):
        rel = Path(root).relative_to(src)
        dirs[:] = [x for x in dirs if x not in exclude_dir]
        out_dir = dest / rel
        out_dir.mkdir(parents=True, exist_ok=True)
        for fn in files:
            sp = Path(root) / fn
            dp = out_dir / fn
            try:
                shutil.copy2(sp, dp)
                copied += 1
            except OSError:
                skipped += 1
    marker.write_text("%s\n" % src, encoding="utf-8")
    return {"ok": True, "src": str(src), "dest": str(dest),
            "copied": copied, "skipped": skipped,
            "chrome_running": _chrome_dang_chay()}


def _doc_danh_sach_mql5(path: Path | None, tuoi_min_ngay: int) -> list[dict]:
    candidates = []
    if path:
        candidates.append(Path(path))
    data = Path(os.environ.get("BRAIN_DATA") or (GOC / "data"))
    candidates += [
        data / "tin_hieu_cong_khai" / "mql5" / "danh_sach_signals.json",
        GOC / "data" / "tin_hieu_cong_khai" / "mql5" / "danh_sach_signals.json",
        TIN_HIEU_GOC / "data" / "mql5" / "danh_sach_signals.json",
        TIN_HIEU_GOC / "code" / "data" / "tin_hieu_cong_khai" / "mql5" / "danh_sach_signals.json",
    ]
    for p in candidates:
        if p and p.exists():
            d = json.loads(p.read_text(encoding="utf-8"))
            he = d.get("he") or d.get("signals") or []
            ra = []
            for h in he:
                f = h.get("filter") or {}
                # list already age-filtered; keep signals whose filter floor >= tuoi_min
                tuoi = int(
                    h.get("tuoi_ngay")
                    or h.get("age_days")
                    or f.get("tuoi_min_ngay")
                    or tuoi_min_ngay
                )
                if tuoi < tuoi_min_ngay:
                    continue
                sid = str(h.get("signal_id") or h.get("id") or "")
                if not sid:
                    continue
                ra.append({
                    "signal_id": sid,
                    "url": h.get("url") or ("https://www.mql5.com/en/signals/%s" % sid),
                })
            return ra
    return []


def _da_co_csv(thu: Path, sid: str) -> Path | None:
    for pat in ("%s.csv" % sid, "%s.history.csv" % sid, "%s_history.csv" % sid):
        p = thu / pat
        if p.exists() and p.stat().st_size > 50:
            return p
    for p in thu.glob("*%s*.csv" % sid):
        if p.stat().st_size > 50:
            return p
    return None


def _soft_goto(page, url: str, *, retries: int = 4, wait_ms: int = 2000) -> dict:
    last = None
    for i in range(retries):
        try:
            resp = page.goto(url, wait_until="domcontentloaded", timeout=90000)
            page.wait_for_timeout(wait_ms)
            status = resp.status if resp else None
            body = ""
            try:
                body = page.content()[:1500]
            except Exception:
                pass
            title = ""
            try:
                title = page.title()
            except Exception:
                pass
            blocked = False
            ly = None
            if status in (403, 401):
                blocked = True
                ly = "http_%s" % status
            elif status == 404 or "page not found" in (title or "").lower():
                blocked = True
                ly = "http_404"
            elif re.search(r"access denied|cloudflare|attention required", body, re.I):
                blocked = True
                ly = "waf_or_denied"
            return {"ok": not blocked, "status": status, "ly_do": ly, "title": title, "url": page.url}
        except Exception as e:
            last = str(e)[:200]
            page.wait_for_timeout(2500)
    return {"ok": False, "ly_do": "goto_fail:%s" % last}


def _tim_nut_export(page):
    """Find 'Export to CSV: History' / similar on the signal page."""
    candidates = [
        page.get_by_role("link", name=re.compile(r"Export to CSV.*History", re.I)),
        page.get_by_role("link", name=re.compile(r"Export.*CSV", re.I)),
        page.get_by_text(re.compile(r"Export to CSV\s*:\s*History", re.I)),
        page.locator("a", has_text=re.compile(r"Export to CSV", re.I)),
        page.locator("a[href*='export']"),
        page.locator("a[href*='.csv']"),
        page.locator("#tab_history a[href*='csv'], a[data-export='history']"),
    ]
    for loc in candidates:
        try:
            if loc.count() and loc.first.is_visible():
                return loc.first
        except Exception:
            continue
    return None


def _mo_tab_history(page) -> None:
    # Prefer explicit tab ids used by MQL5
    for sel in ("#tab_history", "a[href='#history']", "[data-tab='history']"):
        try:
            loc = page.locator(sel)
            if loc.count():
                loc.first.click(timeout=5000)
                page.wait_for_timeout(800)
                return
        except Exception:
            pass
    for name in (r"Trading History", r"History", r"Trading", r"Trade History"):
        try:
            tab = page.get_by_role("tab", name=re.compile(name, re.I))
            if tab.count():
                tab.first.click(timeout=5000)
                page.wait_for_timeout(800)
                return
        except Exception:
            pass
        try:
            link = page.get_by_role("link", name=re.compile(name, re.I))
            if link.count():
                link.first.click(timeout=5000)
                page.wait_for_timeout(800)
                return
        except Exception:
            pass


def _check_login(page) -> bool:
    """Heuristic: logged-in pages show account menu / no Sign In CTA dominant."""
    try:
        url = page.url or ""
        if "login" in url.lower() or "auth_login" in url.lower():
            return False
        # MQL5 often shows need-auth class / Sign In when export gated
        try:
            if page.locator(".need-auth, [data-need-auth], .s-need-auth").count():
                return False
        except Exception:
            pass
        sign = page.get_by_role("link", name=re.compile(r"^(Sign In|Log in|Login)$", re.I))
        if sign.count() and sign.first.is_visible():
            av = page.locator("[class*='avatar'], [class*='userpic'], a[href*='/en/users/']")
            if av.count() == 0:
                return False
        return True
    except Exception:
        return True


def _kiem_tra_mt5_signals() -> dict:
    """Report whether MT5 Terminal exposes usable signal trade history (not just catalog)."""
    appdata = Path(os.environ.get("APPDATA", ""))
    root = appdata / "MetaQuotes" / "Terminal"
    if not root.is_dir():
        return {"ok": False, "ly_do": "khong_co_mt5_terminal"}
    catalogs = list(root.glob("*/bases/signals/signals.dat"))
    csvs = list(root.glob("*/bases/signals/**/*.csv"))
    hist = list(root.glob("*/MQL5/Files/**/*ignal*.csv"))
    return {
        "ok": False,
        "catalogs": len(catalogs),
        "csv_history": len(csvs) + len(hist),
        "ly_do": (
            "mt5_chi_co_signals.dat_catalog_khong_co_trade_history_csv"
            if catalogs and not (csvs or hist)
            else "mt5_khong_co_signal_history"
        ),
    }


def tai_mot_mql5(page, sid: str, url: str, out_dir: Path, tmp: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    for old in tmp.glob("*"):
        try:
            old.unlink()
        except OSError:
            pass
    dest = out_dir / ("%s.csv" % sid)
    if dest.exists() and dest.stat().st_size > 50:
        return {"signal_id": sid, "ok": True, "path": str(dest), "bo_qua": "da_co"}
    g = _soft_goto(page, url)
    if not g.get("ok"):
        return {"signal_id": sid, "ok": False, "ly_do": g.get("ly_do") or "goto_fail",
                "status": g.get("status")}
    if not _check_login(page):
        return {"signal_id": sid, "ok": False, "ly_do": "can_dang_nhap_mql5"}
    _mo_tab_history(page)
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(600)
    except Exception:
        pass
    nut = _tim_nut_export(page)
    if nut is None:
        for suffix in ("?tab=history", "#history", "/history"):
            try:
                g2 = _soft_goto(page, url.rstrip("/") + suffix, retries=2)
                if not g2.get("ok"):
                    continue
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                nut = _tim_nut_export(page)
                if nut:
                    break
            except Exception:
                continue
    if nut is None:
        snap = LOGS / ("mql5_no_export_%s.html" % sid)
        try:
            snap.write_text(page.content(), encoding="utf-8", errors="replace")
        except Exception:
            snap = None
        # Export absent when logged out
        logged = _check_login(page)
        return {
            "signal_id": sid, "ok": False,
            "ly_do": "khong_thay_nut_export" + ("" if logged else "_va_chua_login"),
            "snap": str(snap) if snap else None,
            "can_dang_nhap": not logged,
        }
    try:
        with page.expect_download(timeout=120000) as dl_info:
            nut.click()
        dl = dl_info.value
        tmp_path = tmp / (dl.suggested_filename or ("%s.history.csv" % sid))
        dl.save_as(tmp_path)
        shutil.move(str(tmp_path), str(dest))
        return {"signal_id": sid, "ok": True, "path": str(dest),
                "bytes": dest.stat().st_size}
    except Exception as e:
        return {"signal_id": sid, "ok": False, "ly_do": "download_fail:%s" % e}


def tai_myfxbook_mot(page, system_path: str, out_dir: Path, tmp: Path) -> dict:
    """Open a public Myfxbook system page and try Export → CSV (reCAPTCHA gated)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    sid = re.sub(r"[^\w\-]+", "_", system_path.strip("/"))[-80:]
    # Prefer trailing numeric system id as filename
    m = re.search(r"(\d+)/?$", system_path.strip())
    if m:
        sid = m.group(1)
    dest = out_dir / ("%s.csv" % sid)
    if dest.exists() and dest.stat().st_size > 50:
        return {"id": sid, "ok": True, "bo_qua": "da_co", "path": str(dest)}
    url = system_path if system_path.startswith("http") else (
        "https://www.myfxbook.com/members/" + system_path.lstrip("/"))
    g = _soft_goto(page, url, retries=4, wait_ms=3000)
    if not g.get("ok"):
        return {"id": sid, "ok": False, "ly_do": g.get("ly_do") or "goto_fail", "url": url}

    # Open filter/sliders dropdown that contains Export → CSV (#csvStatement)
    try:
        page.evaluate("""() => {
          const btn = document.querySelector(
            'button.filter-button[data-toggle="dropdown"], button.filter-button, #chartDropMenuButton');
          if (btn) btn.click();
          // force-show export section even if bootstrap animation lags
          const csv = document.getElementById('csvStatement');
          if (csv) {
            let n = csv;
            for (let i = 0; i < 8 && n; i++) {
              n.style.display = 'block';
              n.style.visibility = 'visible';
              n.classList.add('open', 'show');
              n = n.parentElement;
            }
          }
        }""")
        page.wait_for_timeout(800)
    except Exception:
        pass

    has_csv = False
    try:
        has_csv = page.locator("#csvStatement").count() > 0
    except Exception:
        pass
    if not has_csv:
        snap = LOGS / ("myfxbook_no_csv_%s.html" % sid)
        try:
            snap.write_text(page.content(), encoding="utf-8", errors="replace")
        except Exception:
            snap = None
        return {"id": sid, "ok": False, "ly_do": "khong_thay_csvStatement", "url": url,
                "snap": str(snap) if snap else None}

    # Click triggers captchaModal (reCAPTCHA) before getCSVFile — detect that
    try:
        page.locator("#csvStatement").click(force=True, timeout=8000)
        page.wait_for_timeout(1500)
    except Exception:
        # delegated jQuery handler on #chartContainerDiv
        try:
            page.evaluate("""() => {
              const a = document.getElementById('csvStatement');
              if (typeof jQuery !== 'undefined') {
                jQuery('#chartContainerDiv').find('#csvStatement').trigger('click');
              } else if (a) {
                a.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
              }
            }""")
            page.wait_for_timeout(1500)
        except Exception as e2:
            return {"id": sid, "ok": False, "ly_do": "click_csv_fail:%s" % e2}

    captcha = False
    try:
        captcha = page.evaluate("""() => {
          const m = document.getElementById('captchaModal');
          if (m) {
            const st = getComputedStyle(m);
            if ((st.display !== 'none' && m.classList.contains('in')) || m.classList.contains('show'))
              return true;
            if (m.getBoundingClientRect().width > 0 && st.display !== 'none') return true;
          }
          if (document.querySelector('.g-recaptcha, iframe[src*="recaptcha"], #googleCaptchaContainerStatements'))
            return true;
          return false;
        }""")
    except Exception:
        captcha = False

    if captcha:
        return {
            "id": sid, "ok": False, "url": url,
            "ly_do": "myfxbook_recaptcha_chan_export_tu_dong",
            "ghi_chu": "UI #csvStatement opens captchaModal; getCSVFile needs grecaptcha — no automated bypass",
        }

    # If somehow no captcha (rare), wait for download
    try:
        with page.expect_download(timeout=30000) as dl_info:
            page.locator("#csvStatement").click(force=True, timeout=5000)
        dl = dl_info.value
        tmp_path = tmp / (dl.suggested_filename or ("%s.csv" % sid))
        dl.save_as(tmp_path)
        shutil.move(str(tmp_path), str(dest))
        return {"id": sid, "ok": True, "path": str(dest), "bytes": dest.stat().st_size}
    except Exception as e:
        return {"id": sid, "ok": False, "ly_do": "download_fail_or_captcha:%s" % e, "url": url}


def _launch_ctx(p, *, headed: bool = True):
    return p.chromium.launch_persistent_context(
        user_data_dir=str(PW_PROFILE),
        channel="chrome",
        headless=not headed,
        accept_downloads=True,
        downloads_path=str(TMP),
        ignore_https_errors=True,
        args=CHROME_ARGS,
        viewport={"width": 1365, "height": 900},
    )


def chay_mql5(*, toi_da: int = 100, nghi: float = 5.0, danh_sach: Path | None = None,
              tuoi_min_ngay: int = 365, headed: bool = True, force_profile: bool = False,
              in_ra=print) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"ok": False, "ly_do": "thieu_playwright",
                "huong_dan": "pip install playwright && playwright install chrome"}

    sync = dong_bo_pw_profile(force=force_profile)
    in_ra("[pw_profile] %s" % json.dumps(sync, ensure_ascii=False))
    if not sync.get("ok"):
        return {"ok": False, "ly_do": sync.get("ly_do"), "profile": sync,
                "mt5": _kiem_tra_mt5_signals()}

    ds = _doc_danh_sach_mql5(danh_sach, tuoi_min_ngay)[:toi_da]
    if not ds:
        return {"ok": False, "ly_do": "danh_sach_rong", "mt5": _kiem_tra_mt5_signals()}

    MQL5_CSV.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    ket = {"ok": True, "he": [], "loi": [], "bo_qua": [], "can_dang_nhap": False}

    with sync_playwright() as p:
        ctx = _launch_ctx(p, headed=headed)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        warm = _soft_goto(page, "https://www.mql5.com/en", retries=3)
        in_ra("[mql5] warm %s" % json.dumps(warm, ensure_ascii=False))
        logged = _check_login(page) if warm.get("ok") else False
        # Home IP often 403 on /en — try a public signal page as session probe
        if not warm.get("ok") or warm.get("ly_do") == "http_403":
            probe = ds[0]["url"] if ds else "https://www.mql5.com/en/signals/2265877"
            warm2 = _soft_goto(page, probe, retries=3)
            in_ra("[mql5] probe %s" % json.dumps(warm2, ensure_ascii=False))
            logged = _check_login(page) if warm2.get("ok") else False
            if not warm2.get("ok"):
                ket["ok"] = False
                ket["ly_do"] = "mql5_home_ip_403_hoac_goto_fail"
                ket["warm"] = warm
                ket["probe"] = warm2
                ket["mt5"] = _kiem_tra_mt5_signals()
                ket["thieu"] = (
                    "MQL5 community login session in Chrome profile; "
                    "home IP blocks /en and /en/auth_login (403). "
                    "MT5 has signals.dat catalog only, no trade-history CSV."
                )
                snap = LOGS / "mql5_login_wall.html"
                try:
                    snap.write_text(page.content(), encoding="utf-8", errors="replace")
                    ket["snap"] = str(snap)
                except Exception:
                    pass
                ctx.close()
                return ket

        if not logged:
            ket["can_dang_nhap"] = True
            ket["ok"] = False
            ket["ly_do"] = "profile_chua_login_mql5"
            ket["mt5"] = _kiem_tra_mt5_signals()
            ket["thieu"] = (
                "Logged-in MQL5 community session missing from "
                "E:\\brain2_grok_tin_hieu\\pw_profile (and source Chrome profile). "
                "Login endpoints 403 from home IP — login from another network/VPN "
                "in normal Chrome, then re-run with --force-profile. "
                "MT5 Terminal does not expose signal trade history CSV."
            )
            snap = LOGS / "mql5_login_wall.html"
            try:
                snap.write_text(page.content(), encoding="utf-8", errors="replace")
                ket["snap"] = str(snap)
            except Exception:
                pass
            ctx.close()
            return ket

        for i, h in enumerate(ds):
            if i:
                time.sleep(max(nghi, 5.0))
            r = tai_mot_mql5(page, h["signal_id"], h["url"], MQL5_CSV, TMP)
            in_ra("[mql5_csv] %s" % json.dumps(r, ensure_ascii=False))
            if r.get("bo_qua"):
                ket["bo_qua"].append(r)
            elif r.get("ok"):
                ket["he"].append(r)
            else:
                ket["loi"].append(r)
                if r.get("ly_do") == "can_dang_nhap_mql5" or r.get("can_dang_nhap"):
                    ket["can_dang_nhap"] = True
                    break
        ctx.close()

    try:
        for old in TMP.glob("*"):
            old.unlink()
    except OSError:
        pass
    ket["tong_ok"] = len(ket["he"])
    ket["tong_loi"] = len(ket["loi"])
    ket["tong_bo_qua"] = len(ket["bo_qua"])
    if ket["can_dang_nhap"] and ket["tong_ok"] == 0:
        ket["ok"] = False
        ket["mt5"] = _kiem_tra_mt5_signals()
    return ket


def chay_myfxbook(paths: list[str], *, nghi: float = 5.0, headed: bool = True,
                  in_ra=print) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"ok": False, "ly_do": "thieu_playwright"}
    MYFX_CSV.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    ket = {"ok": True, "he": [], "loi": [], "bo_qua": []}
    with sync_playwright() as p:
        ctx = _launch_ctx(p, headed=headed)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        for i, sp in enumerate(paths):
            if i:
                time.sleep(max(nghi, 5.0))
            r = tai_myfxbook_mot(page, sp, MYFX_CSV, TMP)
            in_ra("[myfxbook_csv] %s" % json.dumps(r, ensure_ascii=False))
            if r.get("bo_qua"):
                ket["bo_qua"].append(r)
            elif r.get("ok"):
                ket["he"].append(r)
            else:
                ket["loi"].append(r)
        ctx.close()
    ket["tong_ok"] = len(ket["he"])
    ket["tong_loi"] = len(ket["loi"])
    if ket["tong_ok"] == 0 and ket["loi"]:
        ket["ok"] = False
    return ket


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--toi-da", type=int, default=100)
    ap.add_argument("--nghi", type=float, default=5.0)
    ap.add_argument("--tuoi-min-ngay", type=int, default=365)
    ap.add_argument("--danh-sach", default="")
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--force-profile", action="store_true")
    ap.add_argument("--chi-dong-bo-profile", action="store_true")
    ap.add_argument("--resync-cookies", action="store_true")
    ap.add_argument("--kiem-tra-mt5", action="store_true")
    ap.add_argument("--myfxbook", nargs="*", default=None,
                    help="Optional Myfxbook system paths to also fetch")
    a = ap.parse_args(argv)

    if a.kiem_tra_mt5:
        print(json.dumps(_kiem_tra_mt5_signals(), ensure_ascii=False, indent=2))
        return 0
    if a.resync_cookies:
        print(json.dumps(dong_bo_pw_profile(chi_cookies=True), ensure_ascii=False, indent=2))
        return 0
    if a.chi_dong_bo_profile:
        print(json.dumps(dong_bo_pw_profile(force=a.force_profile), ensure_ascii=False, indent=2))
        return 0

    kq = chay_mql5(
        toi_da=a.toi_da,
        nghi=a.nghi,
        danh_sach=Path(a.danh_sach) if a.danh_sach else None,
        tuoi_min_ngay=a.tuoi_min_ngay,
        headed=not a.headless,
        force_profile=a.force_profile,
    )
    print(json.dumps(kq, ensure_ascii=False, indent=2))

    if a.myfxbook is not None:
        my = chay_myfxbook(a.myfxbook, nghi=a.nghi, headed=not a.headless)
        print(json.dumps({"myfxbook": my}, ensure_ascii=False, indent=2))

    return 0 if kq.get("ok") or kq.get("tong_ok", 0) > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
