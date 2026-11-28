# Watch the in-flight NZDJPY p6 test after runq_fx crashed on tasklist timeout.
# Do not kill the tester. No full-system tasklist. Never touch 13548/claude/Sierra.
import csv, datetime, json, os, re, shutil, subprocess, sys, time

COUT = r"C:\Users\DUNG\v3work\out\mt5"
OUT = r"E:\GrokWork\mt5_runs"
P6 = r"E:\mt5_tester\p6"
TERM_PID = 21988
AGENT_PID = 7672
RUNQ_DEAD = 1528
JOB = "fx_nzdjpy_ibs240_ldn"
START_KNOWN = datetime.datetime(2026, 11, 28, 21, 16, 30)
TIMEOUT_MIN = 100

def now():
    return datetime.datetime.now()

def hb(msg):
    os.makedirs(COUT, exist_ok=True)
    line = now().strftime("%Y-%m-%d %H:%M:%S ") + msg
    with open(os.path.join(COUT, "watch.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")
    with open(os.path.join(COUT, "heartbeat.txt"), "w", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)

def pid_alive(pid, timeout=8):
    try:
        r = subprocess.run(
            ["tasklist", "/FI", f"PID eq {int(pid)}", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=timeout,
        )
        out = (r.stdout or "").strip()
        if not out or "No tasks" in out or "Khong" in out:
            return False
        try:
            parts = next(csv.reader([out.splitlines()[0]]))
            return int(parts[1]) == int(pid)
        except Exception:
            return str(pid) in out
    except subprocess.TimeoutExpired:
        return None  # unknown
    except Exception:
        return None

def num(s):
    s = s.replace("\u00a0"," ").replace(" ","")
    try:
        return float(s)
    except Exception:
        return None

def parse(htm):
    raw = open(htm, "rb").read()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff") or (len(raw)>3 and raw[1:2]==b"\x00"):
        t = raw.decode("utf-16")
    else:
        t = raw.decode("utf-8", "ignore")
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t)
    def g(label, pat=r"(-?[\d ]+\.\d+)"):
        m = re.search(re.escape(label)+r"\s*"+pat, t)
        return m
    r = {}
    m = g("Total Net Profit:")
    r["net"] = num(m.group(1)) if m else None
    m = g("Profit Factor:")
    r["pf"] = num(m.group(1)) if m else None
    m = re.search(r"Equity Drawdown Maximal:\s*(-?[\d ]+\.\d+)\s*\(([\d.]+)%\)", t)
    if m:
        r["eq_dd_abs"] = num(m.group(1)); r["eq_dd_pct"] = float(m.group(2))
    m = re.search(r"Balance Drawdown Maximal:\s*(-?[\d ]+\.\d+)\s*\(([\d.]+)%\)", t)
    if m:
        r["bal_dd_abs"] = num(m.group(1)); r["bal_dd_pct"] = float(m.group(2))
    m = re.search(r"Total Trades:\s*(\d+)", t)
    r["trades"] = int(m.group(1)) if m else None
    m = re.search(r"History Quality:\s*([^B]+?)\s*Bars", t)
    r["quality"] = m.group(1).strip() if m else None
    m = re.search(r"Largest loss trade:\s*(-?[\d ]+\.\d+)", t)
    if m:
        r["largest_loss_trade"] = num(m.group(1))
    return r

def collect():
    found = None
    for folder in (P6, os.path.join(OUT, "reports")):
        for ext in (".htm", ".html"):
            pth = os.path.join(folder, JOB + ext)
            if os.path.exists(pth) and os.path.getsize(pth) > 30000:
                found = pth
                break
        if found:
            break
    # also any new file
    if not found:
        pth = os.path.join(P6, JOB + ".htm")
        if os.path.exists(pth):
            found = pth
    return found

def copy_out(src):
    os.makedirs(os.path.join(OUT, "reports"), exist_ok=True)
    os.makedirs(os.path.join(COUT, "reports"), exist_ok=True)
    dst_e = os.path.join(OUT, "reports", os.path.basename(src))
    if os.path.abspath(src) != os.path.abspath(dst_e):
        try:
            shutil.copy2(src, dst_e)
        except OSError as e:
            hb("copy E reports fail "+str(e))
            dst_e = src
    dst_c = os.path.join(COUT, "reports", os.path.basename(src))
    try:
        shutil.copy2(src if not os.path.exists(dst_e) else dst_e, dst_c)
    except OSError as e:
        hb("copy C reports fail "+str(e))
    for extra in (".png", "-hst.png", "-holding.png", "-mfemae.png"):
        pth = os.path.join(P6, JOB + extra)
        if os.path.exists(pth):
            try:
                shutil.copy2(pth, os.path.join(OUT, "reports", os.path.basename(pth)))
                shutil.copy2(pth, os.path.join(COUT, "reports", os.path.basename(pth)))
            except OSError:
                pass
    return dst_e, dst_c

def append_result(rec):
    resf = os.path.join(OUT, "results_p6.jsonl")
    # skip if a good line already exists
    if os.path.exists(resf):
        for ln in open(resf, encoding="utf-8"):
            try:
                j = json.loads(ln)
            except Exception:
                continue
            if j.get("name")==JOB and j.get("net") is not None and (j.get("trades") or 0)>0:
                hb("results already has good "+JOB+" net="+str(j.get("net")))
                shutil.copy2(resf, os.path.join(COUT, "results_p6.jsonl"))
                return
    with open(resf, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False)+"\n")
    try:
        shutil.copy2(resf, os.path.join(COUT, "results_p6.jsonl"))
    except OSError:
        pass

def main():
    os.makedirs(COUT, exist_ok=True)
    hb("watch start term=%s agent=%s" % (TERM_PID, AGENT_PID))
    deadline = START_KNOWN + datetime.timedelta(minutes=TIMEOUT_MIN + 5)
    last_state = None
    while now() < deadline:
        t_alive = pid_alive(TERM_PID)
        a_alive = pid_alive(AGENT_PID)
        state = "term=%s agent=%s" % (t_alive, a_alive)
        if state != last_state:
            hb("state "+state+" elapsed=%ds" % int((now()-START_KNOWN).total_seconds()))
            last_state = state
        else:
            # heartbeat anyway every loop
            hb("still "+state+" elapsed=%ds" % int((now()-START_KNOWN).total_seconds()))
        if t_alive is True:
            time.sleep(20)
            continue
        if t_alive is None:
            hb("pid check unknown, retry")
            time.sleep(10)
            continue
        # terminal gone
        time.sleep(3)
        src = collect()
        if not src:
            hb("terminal gone but no report yet, wait 15s")
            time.sleep(15)
            src = collect()
        if not src:
            hb("NO report for "+JOB)
            with open(os.path.join(COUT, "NZDJPY_NO_REPORT.txt"), "w", encoding="utf-8") as f:
                f.write(now().strftime("%Y-%m-%d %H:%M:%S no report\n"))
            return 2
        dst_e, dst_c = copy_out(src)
        rec = dict(name=JOB, slot="p6", symbol="NZDJPY#", from_="2026.06.01", to="2026.11.27",
                   secs=int((now()-START_KNOWN).total_seconds()), stop="", report=dst_e)
        try:
            rec.update(parse(dst_c if os.path.exists(dst_c) else src))
        except Exception as e:
            rec["parse_err"] = str(e)
        rec["pass"] = bool(rec.get("net") is not None and rec.get("net")>0 and rec.get("trades"))
        append_result(rec)
        hb("DONE %s net=%s dd=%s trades=%s q=%s file=%s" % (
            JOB, rec.get("net"), rec.get("eq_dd_pct"), rec.get("trades"), rec.get("quality"), dst_c))
        with open(os.path.join(COUT, "NZDJPY_DONE.txt"), "w", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False, indent=2))
        return 0
    # timeout: do not auto-kill unless still our p6 tester after 100 min — parent may decide
    hb("WATCH TIMEOUT — tester may still be running, not killing")
    with open(os.path.join(COUT, "NZDJPY_TIMEOUT.txt"), "w", encoding="utf-8") as f:
        f.write(now().strftime("%Y-%m-%d %H:%M:%S timeout, left tester running\n"))
    return 3

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        try:
            hb("FATAL "+type(e).__name__+": "+str(e))
        except Exception:
            pass
        raise
