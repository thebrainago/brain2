# -*- coding: utf-8 -*-
"""tai_lich_su_trinh_duyet.py — Playwright fetch MQL5/Myfxbook history CSV on home.

Uses a persistent Chrome profile under E:\\brain2_grok_tin_hieu\\pw_profile
(copied from the user's logged-in Chrome profile). Does NOT extract/decrypt
cookies or tokens; drives the real browser UI (Export to CSV: History).

Disk: temp on E: first. BelowNormal priority expected from the caller.
Polite: --nghi >=5s. Cap: --toi-da 100/night. Filter age>=12m via list JSON.

Known blocks (as of 2026-10-30, Asia/Bangkok):
- MQL5: Export History + Trading history table require community login
  (.need-auth on public signal pages). Home IP returns HTTP 403 on /en and
  /en/auth_login; signal pages may still load. MT5 Terminal only has
  bases/signals/signals.dat (catalog) — no trade-history CSV. Needs a logged-in
  session in a synced Chrome profile (or VPN/other egress for login).
- Myfxbook CSV (#csvStatement): reCAPTCHA before getCSVFile() — no bypass.
- Myfxbook HTML History tab: WORKS without login. Dismiss #popupAdModal, click
  a[href="#historyCont"], parse #tradingHistoryTable (brokerTime cells), paginate.
  Cloudflare may intermittently RST; polite retries. Host-resolver DNS required.
"""
from __future__ import annotations

import argparse
import csv
import io
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



def _liet_ke_chrome_profiles() -> list[Path]:
    """All Chrome profile dirs (Default, Profile N) under User Data."""
    if not CHROME_USER_DATA.is_dir():
        return []
    ra = []
    for d in sorted(CHROME_USER_DATA.iterdir(), key=lambda x: x.name):
        if d.is_dir() and (d.name == "Default" or d.name.startswith("Profile ")):
            ra.append(d)
    return ra


def kiem_tra_login_mql5_moi_profile(*, headed: bool = False, in_ra=print) -> dict:
    """Open a copy of each Chrome profile and check mql5.com header login state.

    Does not decrypt cookies. Copies Preferences+Cookies into a temp pw dir while
    Chrome may be running (best effort; locked Cookies are skipped).
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"ok": False, "ly_do": "thieu_playwright"}

    ket = {"ok": True, "profiles": [], "logged": []}
    chrome_running = _chrome_dang_chay()
    for src in _liet_ke_chrome_profiles():
        prefs = src / "Preferences"
        has_mql = False
        if prefs.exists():
            try:
                has_mql = "mql5.com" in prefs.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                pass
        entry = {"name": src.name, "path": str(src), "prefs_mql5": has_mql,
                 "chrome_running": chrome_running}
        if not has_mql:
            entry["login"] = False
            entry["bo_qua"] = "prefs_khong_co_mql5"
            ket["profiles"].append(entry)
            continue
        tmp_prof = TIN_HIEU_GOC / "tmp" / ("pw_probe_" + src.name.replace(" ", "_"))
        if tmp_prof.exists():
            shutil.rmtree(tmp_prof, ignore_errors=True)
        tmp_prof.mkdir(parents=True, exist_ok=True)
        dest = tmp_prof / "Default"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "Network").mkdir(exist_ok=True)
        for name in ("Preferences", "Secure Preferences"):
            f = src / name
            if f.exists():
                try:
                    shutil.copy2(f, dest / name)
                except OSError as e:
                    entry["copy_err"] = str(e)
        for name in ("Cookies", "Cookies-journal"):
            for base in (src / "Network", src):
                f = base / name
                if f.exists():
                    try:
                        shutil.copy2(f, dest / "Network" / name)
                    except OSError as e:
                        entry["cookies_locked"] = str(e)
        ls = CHROME_USER_DATA / "Local State"
        if ls.exists():
            try:
                shutil.copy2(ls, tmp_prof / "Local State")
            except OSError:
                pass
        try:
            with sync_playwright() as p:
                ctx = p.chromium.launch_persistent_context(
                    user_data_dir=str(tmp_prof), channel="chrome",
                    headless=not headed, ignore_https_errors=True,
                    args=CHROME_ARGS, viewport={"width": 1200, "height": 800},
                )
                page = ctx.pages[0] if ctx.pages else ctx.new_page()
                g = _soft_goto(page, "https://www.mql5.com/en/signals/2265877", retries=3)
                entry["goto"] = g
                if g.get("ok"):
                    need = False
                    try:
                        need = page.locator(".need-auth").count() > 0
                    except Exception:
                        pass
                    logged = _check_login(page) and not need
                    # header hint
                    hdr = page.evaluate("""() => ({
                      signIn: [...document.querySelectorAll('a')].some(a =>
                        /sign in|log in/i.test((a.textContent||'').trim())),
                      avatar: !!document.querySelector('.avatar, .userpic, .header-profile, [class*=\"UserName\"]'),
                      needAuth: !!document.querySelector('.need-auth'),
                    })""")
                    entry["header"] = hdr
                    entry["login"] = bool(logged and not hdr.get("needAuth") and hdr.get("avatar"))
                else:
                    entry["login"] = False
                ctx.close()
        except Exception as e:
            entry["login"] = False
            entry["loi"] = str(e)
        try:
            shutil.rmtree(tmp_prof, ignore_errors=True)
        except OSError:
            pass
        ket["profiles"].append(entry)
        if entry.get("login"):
            ket["logged"].append(src.name)
        in_ra("[mql5_profile] %s login=%s" % (src.name, entry.get("login")))
        time.sleep(2.0)
    ket["ok"] = True
    ket["co_profile_login"] = len(ket["logged"]) > 0
    return ket


def _dong_popup_myfxbook(page) -> None:
    """Dismiss ad/cookie modals that intercept History tab clicks (#popupAdModal)."""
    try:
        page.evaluate("""() => {
          for (const id of ['popupAdModal','adModal','cookieModal','newsletterModal']) {
            const m = document.getElementById(id);
            if (!m) continue;
            m.classList.remove('in','show');
            m.style.display = 'none';
            m.setAttribute('aria-hidden','true');
          }
          document.querySelectorAll('.modal-backdrop, .ad-modal.in').forEach(el => {
            el.classList.remove('in','show');
            el.style.display = 'none';
            try { el.remove(); } catch (e) {}
          });
          document.body.classList.remove('modal-open');
          document.body.style.removeProperty('padding-right');
        }""")
        page.wait_for_timeout(200)
    except Exception:
        pass


_PARSE_HISTORY_ROWS_JS = r"""() => {
  const tb = document.getElementById('tradingHistoryTable')
    || document.querySelector('#historyCont table');
  if (!tb) return {n: 0, rows: []};
  const out = [];
  for (const tr of tb.querySelectorAll('tbody tr')) {
    const cells = [...tr.children];
    if (cells.length < 8) continue;
    const brokerTimes = cells.filter(td => td.classList.contains('brokerTime'))
      .map(td => td.textContent.trim());
    const openTime = (brokerTimes[0] || '').replace(/\s+/g, ' ');
    const closeTime = (brokerTimes[1] || '').replace(/\s+/g, ' ');
    const vals = cells.slice(4).map(td => td.textContent.trim().replace(/\s+/g, ' '));
    const symbol = vals[0] || '';
    const action = vals[1] || '';
    const lots = vals[2] || '';
    const openPrice = vals[3] || '';
    const closePrice = vals[4] || '';
    const pips = vals[5] || '';
    const profit = vals[6] || '';
    const duration = vals[7] || '';
    const gain = vals[8] || '';
    const al = action.toLowerCase();
    if (!symbol && (al.includes('withdrawal') || al.includes('deposit') || al.includes('balance'))) {
      continue;
    }
    // Keep rows with a symbol; Action may be Buy/Sell/Long/Short or icon-only
    if (!symbol) continue;
    if (al && !(/buy|sell|long|short/.test(al)) && /(withdraw|deposit|balance|credit)/.test(al)) continue;
    out.push({
      open_time: openTime, close_time: closeTime, symbol, action, lots,
      open_price: openPrice, close_price: closePrice, pips, profit, duration, gain,
    });
  }
  const size = document.getElementById('historySize')?.value || null;
  const pages = [...document.querySelectorAll('#historyCont a.paging-btn, #historyCont .pagination a, #historyCont a')]
    .map(a => a.textContent.trim()).filter(t => /^\d+$/.test(t) || /next|>|»/i.test(t));
  return {n: out.length, rows: out, size, pages};
}"""


def _rows_to_csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    fields = ["Open time", "Close time", "Symbol", "Buy/sell", "Lots",
              "Open price", "Close price", "Pips", "Profit", "Trade duration", "Gain"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields)
    w.writeheader()
    for r in rows:
        w.writerow({
            "Open time": r.get("open_time", ""),
            "Close time": r.get("close_time", ""),
            "Symbol": r.get("symbol", ""),
            "Buy/sell": r.get("action", ""),
            "Lots": r.get("lots", ""),
            "Open price": r.get("open_price", ""),
            "Close price": r.get("close_price", ""),
            "Pips": r.get("pips", ""),
            "Profit": r.get("profit", ""),
            "Trade duration": r.get("duration", ""),
            "Gain": r.get("gain", ""),
        })
    return buf.getvalue()


def tai_myfxbook_html_history(page, system_path: str, out_dir: Path) -> dict:
    """Scrape public History tab HTML table (no CSV/captcha). Visitor-equivalent.

    Dismisses #popupAdModal, clicks a[href="#historyCont"], parses
    #tradingHistoryTable using brokerTime cells, paginates via page links.
    Stops if a captcha modal appears on the History path.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    sid = re.sub(r"[^\w\-]+", "_", system_path.strip("/"))[-80:]
    m = re.search(r"(\d+)/?$", system_path.strip())
    if m:
        sid = m.group(1)
    dest = out_dir / ("%s_history.csv" % sid)
    if dest.exists() and dest.stat().st_size > 50:
        return {"id": sid, "ok": True, "bo_qua": "da_co", "path": str(dest), "nguon": "html"}
    url = system_path if system_path.startswith("http") else (
        "https://www.myfxbook.com/members/" + system_path.lstrip("/"))
    g = _soft_goto(page, url, retries=5, wait_ms=4000)
    if not g.get("ok"):
        return {"id": sid, "ok": False, "ly_do": g.get("ly_do") or "goto_fail",
                "url": url, "nguon": "html"}

    # Cloudflare challenge page?
    try:
        title = page.title() or ""
        if re.search(r"just a moment|attention required|cloudflare", title, re.I):
            page.wait_for_timeout(12000)
            title = page.title() or ""
            if re.search(r"just a moment|attention required", title, re.I):
                return {"id": sid, "ok": False, "ly_do": "cloudflare_challenge",
                        "url": url, "nguon": "html"}
    except Exception:
        pass

    _dong_popup_myfxbook(page)

    # Arm listener BEFORE click so we catch systemPageGetHistoryFirstPage.json
    hist_xhr = {"status": None, "url": None}

    def _on_resp(resp):
        try:
            u = resp.url or ""
            if "systemPageGetHistory" in u or "GetHistory" in u or "tradingHistory" in u:
                hist_xhr["status"] = resp.status
                hist_xhr["url"] = u
        except Exception:
            pass

    try:
        page.on("response", _on_resp)
    except Exception:
        pass

    try:
        page.evaluate("""() => {
          const a = document.querySelector('a[href="#historyCont"], #tabHistory a[name="history"]');
          if (a) {
            a.click();
            if (typeof jQuery !== 'undefined') jQuery(a).tab('show');
          }
          // also try direct tab show / filterHistory if exposed
          try {
            if (typeof filterHistoryParams !== 'undefined' && typeof loadHistory === 'function') {
              loadHistory();
            }
          } catch (e) {}
        }""")
    except Exception as e:
        return {"id": sid, "ok": False, "ly_do": "click_history_fail:%s" % e,
                "url": url, "nguon": "html"}

    # Wait for table / first-page XHR (up to ~45s; CF/XHR can be slow)
    rows_all: list[dict] = []
    got = None
    for i in range(90):
        page.wait_for_timeout(500)
        # captcha on history? (unusual; CSV path has it)
        try:
            if page.evaluate("""() => {
              const m = document.getElementById('captchaModal');
              if (!m) return false;
              const st = getComputedStyle(m);
              return (st.display !== 'none' && (m.classList.contains('in') || m.classList.contains('show')));
            }"""):
                return {"id": sid, "ok": False, "ly_do": "myfxbook_captcha_tren_history",
                        "url": url, "nguon": "html", "xhr": hist_xhr}
        except Exception:
            pass
        try:
            got = page.evaluate(_PARSE_HISTORY_ROWS_JS)
        except Exception:
            got = None
        if got and got.get("n", 0) > 0:
            break
        # table present with deposit-only / empty tbody after XHR
        try:
            meta = page.evaluate("""() => ({
              size: document.getElementById('historySize')?.value ?? null,
              hasTb: !!document.getElementById('tradingHistoryTable'),
              nTr: document.querySelectorAll('#tradingHistoryTable tbody tr').length,
            })""")
            if hist_xhr.get("status") == 200 and meta.get("hasTb") and i > 10:
                # XHR done; accept whatever parser returns (maybe 0 after filter)
                if got is None:
                    got = {"n": 0, "rows": [], "size": meta.get("size")}
                break
            if meta.get("size") is not None and str(meta.get("size")) == "0":
                got = {"n": 0, "rows": [], "size": "0"}
                break
        except Exception:
            pass
    if not got:
        snap = LOGS / ("myfxbook_no_history_%s.html" % sid)
        try:
            snap.write_text(page.content(), encoding="utf-8", errors="replace")
        except Exception:
            snap = None
        return {"id": sid, "ok": False, "ly_do": "khong_thay_tradingHistoryTable",
                "url": url, "snap": str(snap) if snap else None, "nguon": "html"}

    rows_all.extend(got.get("rows") or [])
    # Paginate by clicking page numbers / Next (visitor UI)
    seen = {json.dumps(r, sort_keys=True) for r in rows_all}
    for pg in range(2, 50):
        _dong_popup_myfxbook(page)
        clicked = False
        try:
            clicked = page.evaluate("""(pg) => {
              const links = [...document.querySelectorAll(
                '#historyCont a, #historyCont .pagination a, #history .pagination a')];
              let a = links.find(x => x.textContent.trim() === String(pg));
              if (!a) {
                a = links.find(x => /^(next|>|»)$/i.test(x.textContent.trim())
                  && !/disabled|prev/i.test(x.className||''));
              }
              if (!a) return false;
              a.click();
              return true;
            }""", pg)
        except Exception:
            clicked = False
        if not clicked:
            break
        page.wait_for_timeout(2200)
        try:
            cur = page.evaluate(_PARSE_HISTORY_ROWS_JS)
        except Exception:
            break
        new_rows = cur.get("rows") or []
        if not new_rows:
            break
        added = 0
        for r in new_rows:
            k = json.dumps(r, sort_keys=True)
            if k not in seen:
                rows_all.append(r)
                seen.add(k)
                added += 1
        if added == 0:
            break
        time.sleep(1.2)

    if not rows_all:
        raw_sample = None
        try:
            raw_sample = page.evaluate("""() => {
              const tb = document.getElementById('tradingHistoryTable');
              if (!tb) return null;
              const tr = tb.querySelector('tbody tr');
              if (!tr) return {nTr: tb.querySelectorAll('tbody tr').length};
              return {
                nTr: tb.querySelectorAll('tbody tr').length,
                cells: [...tr.children].map(td => ({
                  cls: td.className, t: (td.textContent||'').trim().replace(/\\s+/g,' ').slice(0,80)
                })),
              };
            }""")
        except Exception:
            pass
        snap = LOGS / ("myfxbook_empty_hist_%s.html" % sid)
        try:
            snap.write_text(page.content(), encoding="utf-8", errors="replace")
        except Exception:
            snap = None
        return {"id": sid, "ok": False, "ly_do": "history_rong_hoac_chi_deposit",
                "url": url, "size": got.get("size"), "xhr": hist_xhr,
                "raw_sample": raw_sample, "snap": str(snap) if snap else None,
                "nguon": "html"}

    csv_text = _rows_to_csv(rows_all)
    dest.write_text(csv_text, encoding="utf-8")
    # also jsonl next to csv for debugging
    jl = out_dir / ("%s_history.jsonl" % sid)
    with jl.open("w", encoding="utf-8") as f:
        for r in rows_all:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return {
        "id": sid, "ok": True, "path": str(dest), "jsonl": str(jl),
        "so_lenh": len(rows_all), "bytes": dest.stat().st_size, "nguon": "html",
        "url": url,
    }


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
                  in_ra=print, html: bool = True, csv_export: bool = False) -> dict:
    """Fetch Myfxbook histories. Default: HTML History tab (no captcha).

    csv_export=True still tries #csvStatement but expects reCAPTCHA block.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"ok": False, "ly_do": "thieu_playwright"}
    MYFX_CSV.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    ket = {"ok": True, "he": [], "loi": [], "bo_qua": [], "phuong_thuc": []}
    with sync_playwright() as p:
        ctx = _launch_ctx(p, headed=headed)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        for i, sp in enumerate(paths):
            if i:
                time.sleep(max(nghi, 5.0))
            r = None
            if html:
                r = tai_myfxbook_html_history(page, sp, MYFX_CSV)
                in_ra("[myfxbook_html] %s" % json.dumps(r, ensure_ascii=False))
                ket["phuong_thuc"].append("html")
            if (r is None or not r.get("ok")) and csv_export:
                r2 = tai_myfxbook_mot(page, sp, MYFX_CSV, TMP)
                in_ra("[myfxbook_csv] %s" % json.dumps(r2, ensure_ascii=False))
                ket["phuong_thuc"].append("csv")
                if r2.get("ok") or r is None:
                    r = r2
            if r is None:
                r = {"ok": False, "ly_do": "khong_co_phuong_thuc"}
            if r.get("bo_qua"):
                ket["bo_qua"].append(r)
            elif r.get("ok"):
                ket["he"].append(r)
            else:
                ket["loi"].append(r)
        ctx.close()
    ket["tong_ok"] = len(ket["he"])
    ket["tong_loi"] = len(ket["loi"])
    ket["tong_bo_qua"] = len(ket["bo_qua"])
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
                    help="Myfxbook system paths (HTML History scrape by default)")
    ap.add_argument("--myfxbook-csv-export", action="store_true",
                    help="Also try #csvStatement (usually reCAPTCHA-blocked)")
    ap.add_argument("--kiem-tra-mql5-profiles", action="store_true",
                    help="Probe every Chrome profile for live mql5.com login")
    ap.add_argument("--chi-myfxbook", action="store_true",
                    help="Skip MQL5; only run Myfxbook paths")
    a = ap.parse_args(argv)

    if a.kiem_tra_mt5:
        print(json.dumps(_kiem_tra_mt5_signals(), ensure_ascii=False, indent=2))
        return 0
    if a.kiem_tra_mql5_profiles:
        print(json.dumps(kiem_tra_login_mql5_moi_profile(
            headed=not a.headless), ensure_ascii=False, indent=2))
        return 0
    if a.resync_cookies:
        print(json.dumps(dong_bo_pw_profile(chi_cookies=True), ensure_ascii=False, indent=2))
        return 0
    if a.chi_dong_bo_profile:
        print(json.dumps(dong_bo_pw_profile(force=a.force_profile), ensure_ascii=False, indent=2))
        return 0

    kq = {"ok": True, "tong_ok": 0}
    if not a.chi_myfxbook:
        kq = chay_mql5(
            toi_da=a.toi_da,
            nghi=a.nghi,
            danh_sach=Path(a.danh_sach) if a.danh_sach else None,
            tuoi_min_ngay=a.tuoi_min_ngay,
            headed=not a.headless,
            force_profile=a.force_profile,
        )
        print(json.dumps(kq, ensure_ascii=False, indent=2))

    my_ok = 0
    if a.myfxbook is not None:
        my = chay_myfxbook(
            a.myfxbook, nghi=a.nghi, headed=not a.headless,
            html=True, csv_export=a.myfxbook_csv_export)
        print(json.dumps({"myfxbook": my}, ensure_ascii=False, indent=2))
        my_ok = my.get("tong_ok") or 0

    return 0 if kq.get("ok") or kq.get("tong_ok", 0) > 0 or my_ok > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
