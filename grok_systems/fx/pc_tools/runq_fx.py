# Runner MT5 tick-real queue for one slot. Safe procs() (no Get-Process .Path / WMI).
# Writes results under E:\GrokWork\mt5_runs and a C: heartbeat/copy so agents can Read without E: access.
import json, os, re, subprocess, sys, time, shutil, csv, ctypes, datetime
from ctypes import wintypes

OUT = r"E:\GrokWork\mt5_runs"
COUT = r"C:\Users\DUNG\v3work\out\mt5"
SHARED = [r"E:\mt5_tester\p3", r"E:\mt5_tester\p5", r"E:\mt5_tester\p6",
          r"E:\brain2_grok\mt5_slots\g2", r"E:\brain2_grok\mt5_slots\g3", r"E:\brain2_grok\mt5_slots\g4"]

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL

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

def log(slot, msg):
    line = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + msg
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(COUT, exist_ok=True)
    with open(os.path.join(OUT, f"runq_{slot}.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")
    with open(os.path.join(COUT, "heartbeat.txt"), "w", encoding="utf-8") as f:
        f.write(line + "\n")
    try:
        with open(os.path.join(COUT, "runq_copy.log"), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass

class MS(ctypes.Structure):
    _fields_=[("l",ctypes.c_ulong),("load",ctypes.c_ulong),("tot",ctypes.c_ulonglong),("avail",ctypes.c_ulonglong),
              ("tp",ctypes.c_ulonglong),("ap",ctypes.c_ulonglong),("tv",ctypes.c_ulonglong),("av",ctypes.c_ulonglong),("ae",ctypes.c_ulonglong)]

def ram_gb():
    m=MS(); m.l=ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)); return m.avail/2**30

def procs():
    r = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True, timeout=20)
    out=[]
    for ln in r.stdout.splitlines():
        try:
            parts = next(csv.reader([ln]))
        except Exception:
            continue
        if len(parts) < 2:
            continue
        name = parts[0].lower()
        if name not in ("terminal64.exe", "metatester64.exe", "metaeditor64.exe"):
            continue
        try:
            pid = int(parts[1])
        except ValueError:
            continue
        pth = proc_path(pid)
        if pth:
            out.append((pid, pth))
    return out

def busy(slot_dir):
    group = SHARED if any(slot_dir.lower()==s.lower() for s in SHARED) else [slot_dir]
    return [(pid,p) for pid,p in procs() if any(p.lower().startswith(g.lower()+"\\") for g in group)]

def num(s):
    s = s.replace("\u00a0"," ").replace(" ","")
    try: return float(s)
    except: return None

def parse(htm):
    raw=open(htm,"rb").read()
    t = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8","ignore")
    t = re.sub(r"<[^>]+>"," ",t); t=re.sub(r"\s+"," ",t)
    def g(label, pat=r"(-?[\d ]+\.\d+)"):
        m = re.search(re.escape(label)+r"\s*"+pat, t); return m
    r={}
    m=g("Total Net Profit:"); r["net"]=num(m.group(1)) if m else None
    m=g("Profit Factor:"); r["pf"]=num(m.group(1)) if m else None
    m=re.search(r"Equity Drawdown Maximal:\s*(-?[\d ]+\.\d+)\s*\(([\d.]+)%\)",t)
    if m: r["eq_dd_abs"]=num(m.group(1)); r["eq_dd_pct"]=float(m.group(2))
    m=re.search(r"Balance Drawdown Maximal:\s*(-?[\d ]+\.\d+)\s*\(([\d.]+)%\)",t)
    if m: r["bal_dd_abs"]=num(m.group(1)); r["bal_dd_pct"]=float(m.group(2))
    m=g("Equity Drawdown Absolute:"); r["eq_dd_absolute"]=num(m.group(1)) if m else None
    m=re.search(r"Total Trades:\s*(\d+)",t); r["trades"]=int(m.group(1)) if m else None
    m=re.search(r"History Quality:\s*([^B]+?)\s*Bars",t); r["quality"]=m.group(1).strip() if m else None
    m=re.search(r"Initial Deposit:\s*([\d ]+\.\d+)",t); r["deposit_rep"]=num(m.group(1)) if m else None
    m=re.search(r"Period:\s*(\S+)\s*\(([\d.]+)\s*-\s*([\d.]+)\)",t)
    if m: r["period_rep"]=f"{m.group(1)} {m.group(2)}-{m.group(3)}"
    m=re.search(r"Maximal consecutive loss value:\s*(-?[\d ]+\.\d+)\s*\((\d+)\)",t)
    if m:
        r["max_consec_loss"]=num(m.group(1)); r["max_consec_loss_n"]=int(m.group(2))
    m=re.search(r"Average consecutive loss:\s*([\d.]+)",t)
    if m: r["avg_consec_loss"]=float(m.group(1))
    m=re.search(r"Largest loss trade:\s*(-?[\d ]+\.\d+)",t)
    if m: r["largest_loss_trade"]=num(m.group(1))
    return r

def mirror(slot):
    os.makedirs(COUT, exist_ok=True)
    for fn in (f"runq_{slot}.log", f"results_{slot}.jsonl"):
        src = os.path.join(OUT, fn)
        if os.path.exists(src):
            try: shutil.copy2(src, os.path.join(COUT, fn))
            except OSError: pass
    rd = os.path.join(OUT, "reports")
    if os.path.isdir(rd):
        dst = os.path.join(COUT, "reports")
        os.makedirs(dst, exist_ok=True)
        for name in os.listdir(rd):
            if name.startswith("fx_"):
                try: shutil.copy2(os.path.join(rd, name), os.path.join(dst, name))
                except OSError: pass

def run(qfile):
    q=json.load(open(qfile,encoding="utf-8")); slot=q["slot"]; sd=q["slot_dir"]
    resf=os.path.join(OUT,f"results_{slot}.jsonl")
    done=set()
    if os.path.exists(resf):
        for ln in open(resf,encoding="utf-8"):
            try: done.add(json.loads(ln)["name"])
            except: pass
    os.makedirs(os.path.join(OUT,"reports"),exist_ok=True)
    os.makedirs(COUT, exist_ok=True)
    log(slot, f"RUNQ_FX start q={qfile} already_done={sorted(done)}")
    mirror(slot)
    for job in q["jobs"]:
        n=job["name"]
        if n in done:
            log(slot, f"SKIP {n} already in results"); continue
        if os.path.exists(os.path.join(OUT,"STOP")): log(slot,"STOP file -> dung"); return
        w=0
        while True:
            b=busy(sd); r=ram_gb()
            if not b and r>=q.get("min_ram_start",10): break
            if w%3==0: log(slot,f"CHO {n}: busy={b} ram={r:.1f}")
            w+=1; time.sleep(15)
        setp=os.path.join(sd,"MQL5","Profiles","Tester",n+".set")
        os.makedirs(os.path.dirname(setp), exist_ok=True)
        with open(setp,"w",encoding="utf-8") as f:
            for k,v in job["params"].items(): f.write(f"{k}={v}\n")
        ini=os.path.join(sd,n+".ini")
        with open(ini,"w",encoding="utf-8") as f:
            f.write("[Tester]\n"+f"Expert={job['expert']}\nExpertParameters={n}.set\nSymbol={job['symbol']}\nPeriod={job['period']}\n"
                    f"Model=4\nExecutionMode=0\nOptimization=0\nOptimizationCriterion=0\nFromDate={job['from']}\nToDate={job['to']}\n"
                    f"ForwardMode=0\nDeposit={job['deposit']}\nCurrency=USD\nLeverage=1:500\nReport={n}\nReplaceReport=1\nShutdownTerminal=1\nVisual=0\n")
        for ext in (".htm",".html"):
            pth=os.path.join(sd,n+ext)
            if os.path.exists(pth): os.remove(pth)
        r0=ram_gb(); t0=time.time()
        p=subprocess.Popen([os.path.join(sd,"terminal64.exe"),"/portable",f"/config:{ini}"],cwd=sd)
        log(slot,f"START {n} PID {p.pid} ram={r0:.1f}")
        minram=r0; stop=""; agents=set()
        while p.poll() is None:
            time.sleep(10); m=ram_gb(); minram=min(minram,m)
            for pid,pp in procs():
                if pp.lower().startswith(sd.lower()+"\\") and pp.lower().endswith("metatester64.exe"): agents.add(pid)
            if m<q.get("min_ram_run",6) or time.time()-t0>q.get("timeout_min",75)*60:
                stop=f"KILL ram={m:.1f} min={int((time.time()-t0)/60)}"
                for a in agents: subprocess.run(["taskkill","/PID",str(a),"/F"],capture_output=True)
                subprocess.run(["taskkill","/PID",str(p.pid),"/F"],capture_output=True); break
            if int(time.time()-t0) % 60 < 12:
                log(slot, f"RUN {n} elapsed={int(time.time()-t0)}s ram={m:.1f} pid={p.pid} agents={list(agents)}")
        time.sleep(5)
        for a in agents:
            subprocess.run(["taskkill","/PID",str(a),"/F"],capture_output=True)
        secs=int(time.time()-t0)
        rec=dict(name=n, slot=slot, group=job.get("group"), desc=job.get("desc"), expert=job["expert"], symbol=job["symbol"],
                 period=job["period"], from_=job["from"], to=job["to"], deposit=job["deposit"], params=job["params"],
                 secs=secs, ram_min=round(minram,1), stop=stop)
        rep=None
        for ext in (".htm",".html"):
            pth=os.path.join(sd,n+ext)
            if os.path.exists(pth): rep=pth
        if rep:
            try: rec.update(parse(rep))
            except Exception as e: rec["parse_err"]=str(e)
            dst=os.path.join(OUT,"reports",os.path.basename(rep)); shutil.move(rep,dst); rec["report"]=dst
            for extra in [os.path.join(sd,n+s) for s in (".png","-hst.png","-holding.png","-mfemae.png")]:
                if os.path.exists(extra): shutil.move(extra,os.path.join(OUT,"reports",os.path.basename(extra)))
        else: rec["report"]=None
        dep=float(job["deposit"]); net=rec.get("net"); dd=rec.get("eq_dd_pct")
        rec["pass"]= bool(net is not None and net>0 and dd is not None and dd<80 and not stop)
        with open(resf,"a",encoding="utf-8") as f: f.write(json.dumps(rec,ensure_ascii=False)+"\n")
        log(slot,f"DONE {n} secs={secs} net={net} dd={dd} trades={rec.get('trades')} pf={rec.get('pf')} q={rec.get('quality')} ram_min={minram:.1f} {stop}")
        mirror(slot)
    log(slot,"HET HANG DOI")
    mirror(slot)
    with open(os.path.join(COUT, "ALL_QUEUE_DONE.txt"), "w", encoding="utf-8") as f:
        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ALL QUEUE DONE\n"))

if __name__=="__main__":
    run(sys.argv[1])
