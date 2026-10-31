# -*- coding: utf-8 -*-
"""Low-water watchdog for R1 SEEKER + QUANTLAB — CPU ~70-80%, MT5 headroom >=3GB.
Interval 30 min (owner pt33u). Adaptive workers. Handles Windows venv launcher+child pairs.
"""
from __future__ import annotations
import json, os, subprocess, sys, time, traceback
from pathlib import Path
from datetime import datetime

LAB = Path(r"E:\brain2_grok")
RUN = Path(r"E:\brain2_grok_seeker_run")
LOG_DIR = Path(r"E:\brain2_grok_log")
LOG = LOG_DIR / "watchdog_r1.log"
PIDF = LOG_DIR / "watchdog_r1.pid"
STOP = LOG_DIR / "watchdog_r1_DUNG"
STATUS = LOG_DIR / "watchdog_r1_status.json"
LOCK = LOG_DIR / "watchdog_r1.lock"

# Prefer real CPython (avoid venv launcher parent/child double-PID)
_PY312 = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python312" / "python.exe"
_VENV_PY = LAB / "venv" / "Scripts" / "python.exe"
PY = _PY312 if _PY312.exists() else (_VENV_PY if _VENV_PY.exists() else Path(sys.executable))

INTERVAL_SEC = 1800  # 30 min
RAM_MIN_FREE_GB = 3.0
CPU_TARGET_LO = 70.0
CPU_TARGET_HI = 80.0
SEEKER_WORKERS_MIN, SEEKER_WORKERS_MAX = 4, 8
QL_WORKERS_MIN, QL_WORKERS_MAX = 3, 6
SEEKER_CPU_LIMIT_BASE = 50
QL_CPU_LIMIT_BASE = 45

SK_SCRIPT = RUN / "chay_seeker_only.py"
QL_SCRIPT = RUN / "chay_quantlab_only.py"

def ghi(m):
    d = time.strftime("%Y-%m-%d %H:%M:%S ") + m
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        LOG.open("a", encoding="utf-8").write(d + "\n")
    except Exception:
        pass
    print(d, flush=True)

def cpu_ram():
    try:
        import psutil
        cpu = float(psutil.cpu_percent(interval=1.5))
        vm = psutil.virtual_memory()
        return cpu, vm.available / (1024**3), vm.percent
    except Exception:
        return 50.0, 8.0, 50.0

def leaf_script_pids(script_substr: str):
    """PIDs of leaf python processes running script (skip venv launcher parents)."""
    import psutil
    cands = []
    for p in psutil.process_iter(["pid", "name", "cmdline", "ppid"]):
        try:
            name = (p.info.get("name") or "").lower()
            if "python" not in name:
                continue
            cl = " ".join(p.info.get("cmdline") or [])
            # ignore one-liner diagnostics that merely mention the name
            if "-c" in (p.info.get("cmdline") or [])[:3]:
                continue
            if script_substr.lower() not in cl.lower():
                continue
            cands.append(p.info)
        except Exception:
            pass
    if not cands:
        return []
    cand_pids = {c["pid"] for c in cands}
    leaves = []
    parents_with_child = set()
    for c in cands:
        if c["pid"] in {x.get("ppid") for x in cands}:
            parents_with_child.add(c["pid"])
    for c in cands:
        if c["pid"] in parents_with_child:
            continue  # launcher
        leaves.append(c["pid"])
    return leaves

def kill_pids(pids, label=""):
    if not pids:
        return
    import psutil
    procs = []
    for pid in pids:
        try:
            procs.append(psutil.Process(pid))
            procs[-1].terminate()
        except Exception:
            pass
    gone, alive = psutil.wait_procs(procs, timeout=8)
    for p in alive:
        try:
            p.kill()
        except Exception:
            pass
    ghi("killed %s pids=%s" % (label, pids))

def acquire_lock():
    """Exclusive lock via atomic create. Stale lock (dead pid) is stolen."""
    my = os.getpid()
    for _ in range(5):
        try:
            fd = os.open(str(LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(my).encode())
            os.close(fd)
            return True
        except FileExistsError:
            try:
                old = int(LOCK.read_text(encoding="utf-8").strip().split()[0])
            except Exception:
                old = None
            if old and _pid_alive_watchdog(old):
                ghi("lock held by live watchdog pid=%s — I exit" % old)
                return False
            try:
                LOCK.unlink(missing_ok=True)
            except Exception:
                pass
            time.sleep(0.2)
        except Exception as e:
            ghi("lock err: %s" % e)
            return False
    return False

def _pid_alive_watchdog(pid):
    try:
        import psutil
        p = psutil.Process(pid)
        if not p.is_running():
            return False
        cl = " ".join(p.cmdline() or []).lower()
        return "watchdog_r1.py" in cl
    except Exception:
        return False

def adaptive_workers(cpu, free_gb):
    if free_gb < RAM_MIN_FREE_GB:
        return max(2, SEEKER_WORKERS_MIN - 1), max(2, QL_WORKERS_MIN - 1), 30, 25, "ram_protect"
    if free_gb >= 10 and cpu < CPU_TARGET_LO:
        return SEEKER_WORKERS_MAX, QL_WORKERS_MAX, 70, 65, "boost_hi"
    if free_gb >= 6 and cpu < CPU_TARGET_LO:
        return 7, 5, 65, 60, "boost_mid"
    if cpu > CPU_TARGET_HI + 5:
        return SEEKER_WORKERS_MIN, QL_WORKERS_MIN, 40, 35, "backoff"
    return 6, 4, 60, 55, "steady"

def _base_env(workers, cpu_lim):
    env = os.environ.copy()
    env["BRAIN_MAX_WORKERS"] = str(workers)
    env["BRAIN_CPU_LIMIT"] = str(cpu_lim)
    env["BRAIN_SO"] = str(RUN / "nao.db")
    env["BRAIN_DATA"] = str(LAB / "data")
    env["BRAIN_CACHE"] = str(RUN / "data_khung")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["TEMP"] = str(RUN / "tmp")
    env["TMP"] = str(RUN / "tmp")
    # point at venv site-packages when using base python
    venv = LAB / "venv"
    if venv.exists():
        env["VIRTUAL_ENV"] = str(venv)
        sp = venv / "Lib" / "site-packages"
        env["PYTHONPATH"] = str(sp) + os.pathsep + env.get("PYTHONPATH", "")
        env["PATH"] = str(venv / "Scripts") + os.pathsep + env.get("PATH", "")
    return env

def start_seeker(workers, cpu_lim):
    if not SK_SCRIPT.exists():
        ghi("MISSING %s" % SK_SCRIPT); return None
    env = _base_env(workers, cpu_lim)
    CREATE_NO_WINDOW = 0x08000000
    logf = (RUN / "seeker_only.log").open("a", encoding="utf-8")
    p = subprocess.Popen([str(PY), "-u", str(SK_SCRIPT)], cwd=str(LAB), env=env,
                         stdout=logf, stderr=subprocess.STDOUT, creationflags=CREATE_NO_WINDOW)
    ghi("started SEEKER pid=%s workers=%s cpu_limit=%s py=%s" % (p.pid, workers, cpu_lim, PY.name))
    return p.pid

def start_quantlab(workers, cpu_lim):
    if not QL_SCRIPT.exists():
        ghi("MISSING %s" % QL_SCRIPT); return None
    env = _base_env(workers, cpu_lim)
    env["BRAIN_QUET_TIEN_TRINH"] = str(workers)
    CREATE_NO_WINDOW = 0x08000000
    logf = (RUN / "quantlab_only.log").open("a", encoding="utf-8")
    p = subprocess.Popen([str(PY), "-u", str(QL_SCRIPT)], cwd=str(LAB), env=env,
                         stdout=logf, stderr=subprocess.STDOUT, creationflags=CREATE_NO_WINDOW)
    ghi("started QUANTLAB pid=%s workers=%s(BRAIN_QUET_TIEN_TRINH) cpu_limit=%s" % (p.pid, workers, cpu_lim))
    return p.pid

def tick():
    cpu, free_gb, ram_pct = cpu_ram()
    sk_w, ql_w, sk_cpu, ql_cpu, mode = adaptive_workers(cpu, free_gb)
    sk_pids = leaf_script_pids("chay_seeker_only")
    ql_pids = leaf_script_pids("chay_quantlab_only")
    # dedupe extras (keep newest leaf)
    if len(sk_pids) > 1:
        ghi("SEEKER extra leaves %s — keep newest" % sk_pids)
        kill_pids(sorted(sk_pids)[:-1], "seeker_dup")
        sk_pids = leaf_script_pids("chay_seeker_only")
    if len(ql_pids) > 1:
        ghi("QL extra leaves %s — keep newest" % ql_pids)
        kill_pids(sorted(ql_pids)[:-1], "ql_dup")
        ql_pids = leaf_script_pids("chay_quantlab_only")

    restarted = []
    if free_gb < RAM_MIN_FREE_GB:
        ghi("RAM protect free=%.1fGB < %.1f — skip new starts" % (free_gb, RAM_MIN_FREE_GB))
    else:
        if not sk_pids:
            start_seeker(sk_w, sk_cpu); restarted.append("seeker")
        if not ql_pids:
            start_quantlab(ql_w, ql_cpu); restarted.append("quantlab")
        elif cpu < 45 and free_gb >= 8 and mode.startswith("boost"):
            flag = LOG_DIR / "watchdog_last_boost.txt"
            last = 0.0
            try: last = float(flag.read_text().strip())
            except Exception: pass
            if time.time() - last > 3600:
                ghi("boost restart workers sk=%s ql=%s cpu=%.1f free=%.1f" % (sk_w, ql_w, cpu, free_gb))
                kill_pids(sk_pids + ql_pids, "boost")
                time.sleep(3)
                start_seeker(sk_w, sk_cpu)
                start_quantlab(ql_w, ql_cpu)
                flag.write_text(str(time.time()), encoding="utf-8")
                restarted.append("boost")

    sk_status = {}
    try:
        sk_status = json.loads((RUN / "sk_status.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    st = {
        "luc": time.strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_pct": round(cpu, 1),
        "ram_free_gb": round(free_gb, 2),
        "ram_pct": round(ram_pct, 1),
        "mode": mode,
        "seeker_workers": sk_w,
        "ql_workers": ql_w,
        "seeker_cpu_limit": sk_cpu,
        "ql_cpu_limit": ql_cpu,
        "seeker_pids": leaf_script_pids("chay_seeker_only"),
        "ql_pids": leaf_script_pids("chay_quantlab_only"),
        "restarted": restarted,
        "sk_status": sk_status,
        "interval_sec": INTERVAL_SEC,
        "py": str(PY),
    }
    STATUS.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    ghi("tick cpu=%.1f free=%.1fGB mode=%s sk=%s ql=%s restarted=%s moi=%s" % (
        cpu, free_gb, mode, st["seeker_pids"], st["ql_pids"], restarted, sk_status.get("moi")))
    return st

def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    RUN.mkdir(parents=True, exist_ok=True)
    if not acquire_lock():
        return 0
    PIDF.write_text(str(os.getpid()), encoding="utf-8")
    ghi("=== watchdog_r1 start pid=%s interval=%ss ram_min=%.1fGB py=%s ===" % (
        os.getpid(), INTERVAL_SEC, RAM_MIN_FREE_GB, PY))
    try:
        tick()
    except Exception as e:
        ghi("tick LOI: %s\n%s" % (e, traceback.format_exc()[-1500:]))
    while not STOP.exists():
        time.sleep(INTERVAL_SEC)
        if STOP.exists():
            break
        try:
            tick()
        except Exception as e:
            ghi("tick LOI: %s\n%s" % (e, traceback.format_exc()[-1500:]))
    ghi("=== watchdog_r1 stop ===")
    try:
        PIDF.unlink(missing_ok=True)
        LOCK.unlink(missing_ok=True)
    except Exception:
        pass
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
