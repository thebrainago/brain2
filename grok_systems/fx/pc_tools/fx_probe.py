# Probe NZDJPY tester via OpenProcess (no tasklist) and copy report if present.
import ctypes, datetime, json, os, shutil, sys, time
from ctypes import wintypes

COUT = r"C:\Users\DUNG\v3work\out\mt5"
P6 = r"E:\mt5_tester\p6"
OUT = r"E:\GrokWork\mt5_runs"
JOB = "fx_nzdjpy_ibs240_ldn"
PIDS = (21988, 7672)
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def hb(msg):
    os.makedirs(COUT, exist_ok=True)
    line = now()+" "+msg
    with open(os.path.join(COUT, "probe.log"), "a", encoding="utf-8") as f:
        f.write(line+"\n")
    with open(os.path.join(COUT, "probe_hb.txt"), "w", encoding="utf-8") as f:
        f.write(line+"\n")
    print(line, flush=True)

def proc_info(pid):
    h = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
    if not h:
        return {"pid": pid, "alive": False, "err": ctypes.get_last_error(), "path": ""}
    try:
        buf = ctypes.create_unicode_buffer(32768)
        size = wintypes.DWORD(32768)
        path = buf.value if kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)) else ""
        return {"pid": pid, "alive": True, "err": 0, "path": path}
    finally:
        kernel32.CloseHandle(h)

def report_info():
    out = []
    for folder in (P6, os.path.join(OUT, "reports"), os.path.join(COUT, "reports")):
        for ext in (".htm", ".html"):
            pth = os.path.join(folder, JOB+ext)
            if os.path.exists(pth):
                st = os.stat(pth)
                out.append({"path": pth, "size": st.st_size, "mtime": datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")})
    return out

def copy_if_new(src):
    os.makedirs(os.path.join(COUT, "reports"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "reports"), exist_ok=True)
    dst_c = os.path.join(COUT, "reports", os.path.basename(src))
    dst_e = os.path.join(OUT, "reports", os.path.basename(src))
    try:
        if os.path.abspath(src) != os.path.abspath(dst_e):
            shutil.copy2(src, dst_e)
    except OSError as e:
        hb("copy E fail "+str(e))
    try:
        shutil.copy2(src, dst_c)
    except OSError as e:
        hb("copy C fail "+str(e))
        return None
    return dst_c

def once():
    infos = [proc_info(p) for p in PIDS]
    reps = report_info()
    hb("procs="+json.dumps(infos, ensure_ascii=False)+" reports="+json.dumps(reps, ensure_ascii=False))
    return infos, reps

def main():
    loops = int(sys.argv[1]) if len(sys.argv)>1 else 180
    sleep_s = 15
    last_size = {}
    for i in range(loops):
        infos, reps = once()
        alive = any(x["alive"] and ("\\p6\\" in (x["path"] or "").lower() or x["path"]=="") for x in infos)
        # copy any report > 30k that is newer/bigger
        best = None
        for r in reps:
            if r["size"] > 30000:
                if r["path"] not in last_size or r["size"] != last_size.get(r["path"]):
                    best = r
                last_size[r["path"]] = r["size"]
        if best:
            dst = copy_if_new(best["path"])
            hb("copied %s size=%s -> %s" % (best["path"], best["size"], dst))
        if not any(x["alive"] for x in infos):
            # both dead — wait one more copy attempt
            time.sleep(5)
            infos, reps = once()
            big = [r for r in reps if r["size"]>30000]
            if big:
                newest = max(big, key=lambda r: r["mtime"]+"%012d"%r["size"])
                dst = copy_if_new(newest["path"])
                hb("FINAL report %s size=%s -> %s" % (newest["path"], newest["size"], dst))
                with open(os.path.join(COUT, "NZDJPY_READY.txt"), "w", encoding="utf-8") as f:
                    f.write(json.dumps({"report": dst or newest["path"], "size": newest["size"], "reps": reps, "infos": infos}, indent=2))
                return 0
            hb("both PIDs dead, no big report yet")
            # keep looping a few times in case file is being flushed
        time.sleep(sleep_s)
    hb("probe loops exhausted")
    return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        try:
            hb("FATAL "+type(e).__name__+": "+str(e))
        except Exception:
            pass
        raise
