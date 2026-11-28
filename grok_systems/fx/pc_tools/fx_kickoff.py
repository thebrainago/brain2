# Diagnose + safely clear hung p6/runq + start patched runq_fx for q_p6_fx2.json.
# Never touch XM main terminal, claude.exe, or Sierra. No env/secrets printed.
import csv, ctypes, datetime, json, os, shutil, subprocess, sys, time
from ctypes import wintypes

COUT = r"C:\Users\DUNG\v3work\out\mt5"
OUT = r"E:\GrokWork\mt5_runs"
P6 = r"E:\mt5_tester\p6"
PY = r"C:\Users\DUNG\AppData\Local\Programs\Python\Python312\python.exe"
QFILE = r"E:\GrokWork\mt5_runs\q_p6_fx2.json"
RUNQ_FX = r"E:\GrokWork\mt5_runs\runq_fx.py"
SRC_RUNQ = r"C:\Users\DUNG\v3work\out\runq_fx.py"
SRC_Q = r"C:\Users\DUNG\v3work\out\q_p6_fx2.json"

TARGET_TERM = {8884}   # only if path is p6 terminal64.exe
TARGET_RUNQ = {11396}  # only if cmdline contains runq.py
NEVER_PIDS = {13548}
NEVER_NAME = {"claude.exe", "sierrachartfxaurum.exe", "sierrachart.exe"}
NEVER_PATH_SUB = [
    r"c:\program files\xm global mt5",
    r"sierrachartfxaurum",
    r"\claude.exe",
]
FX_JOBS = ("fx_ger40_z15_asia", "fx_us30_z240_ny", "fx_nzdjpy_ibs240_ldn")

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_VM_READ = 0x0010
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL

class MS(ctypes.Structure):
    _fields_=[("l",ctypes.c_ulong),("load",ctypes.c_ulong),("tot",ctypes.c_ulonglong),("avail",ctypes.c_ulonglong),
              ("tp",ctypes.c_ulonglong),("ap",ctypes.c_ulonglong),("tv",ctypes.c_ulonglong),("av",ctypes.c_ulonglong),("ae",ctypes.c_ulonglong)]

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def hb(msg, also_log=True):
    os.makedirs(COUT, exist_ok=True)
    line = now() + " " + msg
    with open(os.path.join(COUT, "kickoff.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")
    with open(os.path.join(COUT, "heartbeat.txt"), "w", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)

def ram_gb():
    m=MS(); m.l=ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.avail/2**30, m.tot/2**30

def proc_path(pid):
    h = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
    if not h:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(32768)
        size = wintypes.DWORD(32768)
        if kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
            return buf.value
        return ""
    finally:
        kernel32.CloseHandle(h)

def tasklist_rows():
    r = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True, timeout=20)
    rows = []
    for ln in r.stdout.splitlines():
        try:
            parts = next(csv.reader([ln]))
        except Exception:
            continue
        if len(parts) < 2:
            continue
        try:
            pid = int(parts[1])
        except ValueError:
            continue
        rows.append({"name": parts[0], "pid": pid, "mem": parts[4] if len(parts)>4 else ""})
    return rows

def cmdline(pid, timeout=8):
    # WMIC can hang; hard-timeout. Do not use Get-Process .Path.
    try:
        r = subprocess.run(
            ["wmic", "process", "where", f"ProcessId={int(pid)}", "get", "CommandLine", "/value"],
            capture_output=True, text=True, timeout=timeout,
        )
        for ln in (r.stdout or "").splitlines():
            if ln.startswith("CommandLine="):
                return ln[len("CommandLine="):].strip()
        return ""
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERR:{type(e).__name__}"

def forbidden(pid, path, name):
    if int(pid) in NEVER_PIDS:
        return True
    nl = (name or "").lower()
    pl = (path or "").lower()
    if nl in NEVER_NAME:
        return True
    for s in NEVER_PATH_SUB:
        if s in pl:
            return True
    return False

def is_p6_terminal(path):
    return (path or "").lower().replace("/", "\\") == (P6 + r"\terminal64.exe").lower()

def is_p6_child(path):
    pl = (path or "").lower().replace("/", "\\")
    root = P6.lower() + "\\"
    return pl.startswith(root) and pl.endswith(".exe")

def is_runq(path, cmd):
    blob = ((path or "") + " " + (cmd or "")).lower()
    return "runq.py" in blob or "runq_fx.py" in blob

def fsize(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return None

def listdir_sizes(root, pred=None, limit=80):
    out = []
    try:
        names = os.listdir(root)
    except OSError as e:
        return [f"ERR {root}: {e}"]
    for name in names:
        if pred and not pred(name):
            continue
        pth = os.path.join(root, name)
        try:
            if os.path.isdir(pth):
                # recurse one level for tick months
                sub = []
                try:
                    for n2 in os.listdir(pth):
                        p2 = os.path.join(pth, n2)
                        if os.path.isfile(p2):
                            sub.append(f"  {n2} {os.path.getsize(p2)}")
                except OSError:
                    pass
                out.append(f"{name}/")
                out.extend(sub[:40])
            else:
                out.append(f"{name} {os.path.getsize(pth)}")
        except OSError as e:
            out.append(f"{name} ERR {e}")
        if len(out) >= limit:
            break
    return out

def copy_if(src, dst):
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except OSError as e:
        hb(f"copy fail {src} -> {dst}: {e}")
        return False

def tail_copy(src, dst, max_bytes=200_000):
    try:
        n = os.path.getsize(src)
        with open(src, "rb") as f:
            if n > max_bytes:
                f.seek(n - max_bytes)
            data = f.read()
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as f:
            f.write(data)
        return n
    except OSError as e:
        hb(f"tail fail {src}: {e}")
        return None

def strip_fx_results(resf):
    if not os.path.exists(resf):
        hb("no results jsonl to strip")
        return 0
    keep, removed = [], []
    for ln in open(resf, encoding="utf-8"):
        s = ln.strip()
        if not s:
            continue
        try:
            rec = json.loads(s)
        except Exception:
            keep.append(ln if ln.endswith("\n") else ln + "\n")
            continue
        name = rec.get("name") or ""
        if name in FX_JOBS:
            trades = rec.get("trades")
            net = rec.get("net")
            stop = rec.get("stop") or ""
            report = rec.get("report")
            # Rerun if 0 trades, missing report, killed, or unreadable net
            bad = (trades == 0) or (not report) or bool(stop) or (net is None)
            if bad:
                removed.append(rec)
                continue
        keep.append(json.dumps(rec, ensure_ascii=False) + "\n")
    bak = resf + ".bak_fx2_" + datetime.datetime.now().strftime("%H%M%S")
    shutil.copy2(resf, bak)
    copy_if(bak, os.path.join(COUT, os.path.basename(bak)))
    with open(resf, "w", encoding="utf-8") as f:
        f.writelines(keep)
    hb(f"stripped {len(removed)} fx result line(s): " + json.dumps([
        {"name": r.get("name"), "trades": r.get("trades"), "net": r.get("net"), "stop": r.get("stop")}
        for r in removed
    ], ensure_ascii=False))
    return len(removed)

def main():
    os.makedirs(COUT, exist_ok=True)
    hb("kickoff start")
    avail, tot = ram_gb()
    hb(f"ram_avail={avail:.2f}GB tot={tot:.2f}GB")

    rows = tasklist_rows()
    with open(os.path.join(COUT, "tasklist.txt"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(f"{r['pid']}|{r['name']}|{r['mem']}\n")
    interesting = []
    names_keep = {
        "terminal64.exe", "metatester64.exe", "metaeditor64.exe",
        "python.exe", "pythonw.exe", "claude.exe",
        "sierrachartfxaurum.exe", "sierrachart.exe",
    }
    want_pids = TARGET_TERM | TARGET_RUNQ | NEVER_PIDS
    for r in rows:
        if r["name"].lower() in names_keep or r["pid"] in want_pids:
            interesting.append(r)
    details = []
    for r in interesting:
        path = proc_path(r["pid"])
        cmd = ""
        if r["name"].lower() in ("python.exe", "pythonw.exe") or r["pid"] in TARGET_RUNQ:
            cmd = cmdline(r["pid"])
        rec = {"pid": r["pid"], "name": r["name"], "mem": r["mem"], "path": path, "cmd": cmd}
        details.append(rec)
    with open(os.path.join(COUT, "pids_fx.txt"), "w", encoding="utf-8") as f:
        for rec in details:
            f.write("{pid}|{name}|{path}|{cmd}\n".format(**rec))
    hb("pid snapshot written (" + str(len(details)) + " rows)")

    # Kill only confirmed hung p6 / our runq
    killed = []
    for rec in details:
        pid, path, name, cmd = rec["pid"], rec["path"], rec["name"], rec["cmd"]
        if forbidden(pid, path, name):
            hb(f"LEAVE protected {pid} {name} {path}")
            continue
        do_kill = False
        reason = ""
        if pid in TARGET_TERM and is_p6_terminal(path):
            do_kill, reason = True, "target 8884 is p6 terminal"
        elif pid in TARGET_RUNQ and is_runq(path, cmd):
            do_kill, reason = True, "target 11396 is runq"
        elif is_p6_child(path) and name.lower() in ("terminal64.exe", "metatester64.exe"):
            # leftover p6 tester/agent from the hung 18:58 run (PID may have changed)
            do_kill, reason = True, "p6 tester/agent still ours"
        if do_kill:
            hb(f"KILL {pid} {name} {path} reason={reason}")
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True, timeout=15)
            killed.append(pid)
            time.sleep(1)
    hb(f"killed={killed}")

    # Diagnosis: ticks, logs, reports, CSVs, InpTF
    diag = []
    def add(title, lines):
        diag.append(title)
        diag.extend(lines if isinstance(lines, list) else [str(lines)])
        diag.append("")

    add("RAM", [f"avail={avail:.2f} tot={tot:.2f}"])
    add("killed", [str(killed)])

    # queue
    qpath = QFILE if os.path.exists(QFILE) else SRC_Q
    try:
        q = json.load(open(qpath, encoding="utf-8"))
        tfs = [(j["name"], j["params"].get("InpTF"), j["symbol"], j["from"], j["to"]) for j in q["jobs"]]
        add("queue", [qpath, "slot="+q.get("slot",""), "timeout="+str(q.get("timeout_min")), str(tfs)])
    except Exception as e:
        add("queue ERR", [str(e)])
        q = None

    ticks_root = os.path.join(P6, "bases")
    add("p6 bases", listdir_sizes(ticks_root, limit=120))
    # typical: bases\XMGlobal-MT5 10\ticks\GER40Cash#
    # walk a few known symbols
    for sym in ("GER40Cash#", "US30Cash#", "NZDJPY#", "GER40Cash", "US30Cash", "NZDJPY"):
        # find tick dirs
        found = []
        if os.path.isdir(ticks_root):
            for srv in os.listdir(ticks_root):
                td = os.path.join(ticks_root, srv, "ticks", sym)
                if os.path.isdir(td):
                    found.append(td)
                    add(f"ticks {sym} {td}", listdir_sizes(td, limit=40))
        if not found:
            add(f"ticks {sym}", ["KHONG CO"])

    logdir = os.path.join(P6, "Tester", "logs")
    add("tester logs dir", listdir_sizes(logdir, limit=40) if os.path.isdir(logdir) else ["KHONG CO"])
    if os.path.isdir(logdir):
        for name in os.listdir(logdir):
            pth = os.path.join(logdir, name)
            if os.path.isfile(pth):
                sz = os.path.getsize(pth)
                if sz >= 20 * 1024 * 1024:
                    bak = os.path.join(OUT, f"tester_log_{name}.bak_kickoff")
                    try:
                        os.makedirs(OUT, exist_ok=True)
                        shutil.move(pth, bak)
                        hb(f"moved huge tester log {pth} size={sz} -> {bak}")
                    except OSError as e:
                        hb(f"move log fail {pth}: {e}")
                else:
                    tail_copy(pth, os.path.join(COUT, "testerlog_" + name + ".tail"), 200_000)

    agentlog = os.path.join(P6, "Tester", "Agent-64", "logs")
    # also common agent paths
    for root, dns, fns in os.walk(os.path.join(P6, "Tester")):
        if os.path.basename(root).lower() == "logs":
            add("found logs " + root, listdir_sizes(root, limit=30))
            for name in fns:
                pth = os.path.join(root, name)
                try:
                    sz = os.path.getsize(pth)
                except OSError:
                    continue
                if sz >= 20 * 1024 * 1024 and "tester_log_" not in pth:
                    # already moved current Tester\logs maybe
                    pass
                if sz < 50_000_000:
                    safe = "agent_" + os.path.basename(root) + "_" + name + ".tail"
                    tail_copy(pth, os.path.join(COUT, safe), 200_000)
        # don't walk forever
        if root.count(os.sep) - os.path.join(P6, "Tester").count(os.sep) > 3:
            dns.clear()

    csv_dir = r"C:\Users\DUNG\AppData\Roaming\MetaQuotes\Terminal\Common\Files\brain2"
    add("common csv " + csv_dir, listdir_sizes(csv_dir, pred=lambda n: n.startswith("fx_") or "nzd" in n.lower() or "us30" in n.lower() or "ger" in n.lower(), limit=40) if os.path.isdir(csv_dir) else ["KHONG CO"])

    if os.path.exists(os.path.join(OUT, "runq_p6.log")):
        n = tail_copy(os.path.join(OUT, "runq_p6.log"), os.path.join(COUT, "runq_p6.log.tail"), 300_000)
        copy_if(os.path.join(OUT, "runq_p6.log"), os.path.join(COUT, "runq_p6.log"))
        add("runq_p6.log", [f"bytes={n}"])
    else:
        add("runq_p6.log", ["KHONG CO"])
    if os.path.exists(os.path.join(OUT, "results_p6.jsonl")):
        copy_if(os.path.join(OUT, "results_p6.jsonl"), os.path.join(COUT, "results_p6.jsonl.before"))
        add("results_p6.jsonl before", open(os.path.join(OUT, "results_p6.jsonl"), encoding="utf-8").read().splitlines()[-20:])
    else:
        add("results_p6.jsonl", ["KHONG CO"])

    reports = os.path.join(OUT, "reports")
    if os.path.isdir(reports):
        add("reports", listdir_sizes(reports, pred=lambda n: n.startswith("fx_"), limit=40))
        dst = os.path.join(COUT, "reports")
        os.makedirs(dst, exist_ok=True)
        for name in os.listdir(reports):
            if name.startswith("fx_"):
                copy_if(os.path.join(reports, name), os.path.join(dst, name))
    else:
        add("reports", ["KHONG CO"])

    with open(os.path.join(COUT, "diagnosis.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(diag) + "\n")
    hb("diagnosis written")

    # Copy patched runner and queue onto E:
    if os.path.exists(SRC_RUNQ):
        copy_if(SRC_RUNQ, RUNQ_FX)
    if os.path.exists(SRC_Q) and not os.path.exists(QFILE):
        copy_if(SRC_Q, QFILE)
    if not os.path.exists(QFILE):
        hb("FATAL no q_p6_fx2.json")
        return 2
    if not os.path.exists(RUNQ_FX):
        hb("FATAL no runq_fx.py on E:")
        return 2
    if not os.path.exists(PY):
        hb("FATAL no python at " + PY)
        return 2

    nstrip = strip_fx_results(os.path.join(OUT, "results_p6.jsonl"))
    hb(f"strip done removed={nstrip}")

    avail, tot = ram_gb()
    hb(f"pre-start ram_avail={avail:.2f}GB")
    if avail < 6.0:
        hb("FATAL ram under 6GB, will not start")
        return 3

    # If p6 still busy after kills, wait briefly
    for i in range(6):
        still = []
        for r in tasklist_rows():
            if r["name"].lower() in ("terminal64.exe", "metatester64.exe"):
                path = proc_path(r["pid"])
                if is_p6_child(path) or is_p6_terminal(path):
                    still.append((r["pid"], path))
        if not still:
            break
        hb(f"p6 still busy {still}, wait")
        time.sleep(5)
    else:
        hb("WARN p6 still busy after wait; runq_fx will wait for free slot")

    stdout = open(os.path.join(COUT, "runq_fx_stdout.txt"), "w", encoding="utf-8")
    stderr = open(os.path.join(COUT, "runq_fx_stderr.txt"), "w", encoding="utf-8")
    flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200) | 0x00000008  # DETACHED_PROCESS
    proc = subprocess.Popen(
        [PY, RUNQ_FX, QFILE],
        cwd=COUT,
        stdin=subprocess.DEVNULL,
        stdout=stdout,
        stderr=stderr,
        creationflags=flags,
        close_fds=False,
    )
    with open(os.path.join(COUT, "runq_fx.pid"), "w", encoding="utf-8") as f:
        f.write(str(proc.pid) + "\n")
    hb(f"started runq_fx pid={proc.pid} q={QFILE}")
    time.sleep(3)
    # confirm alive
    still_alive = any(r["pid"] == proc.pid for r in tasklist_rows())
    hb(f"runq_fx alive={still_alive}")
    if os.path.exists(os.path.join(COUT, "heartbeat.txt")):
        hb("kickoff finished ok")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        try:
            hb("FATAL " + type(e).__name__ + ": " + str(e))
        except Exception:
            pass
        raise
