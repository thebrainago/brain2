# Chay tren MAY NHA. Keo tick ESZ6 (aggTrades, co chieu chu dong B/S) tu Fxaurum gateway ws://127.0.0.1:9001/
# CHI RPC doc (aggTrades). KHONG syncTicks/syncHistory. Gom ngay tren may nha thanh dac trung tung phut:
#   o h l c, vol, vol_mua, vol_ban, delta, so_lenh, lon_mua/lon_ban (qty>=NGUONG_LON), max_qty,
#   va ho so khoi luong theo gia moi phien (gia, vol_mua, vol_ban) de dung POC/VAH/VAL/absorption.
# python keo_tick_esz6.py <thu_muc_ra> [YYYYMMDD_tu] [YYYYMMDD_den]
import asyncio, json, os, sys, csv, collections
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import websockets
URL="ws://127.0.0.1:9001/"; NY=ZoneInfo("America/New_York")
OUT=sys.argv[1]; D0=sys.argv[2] if len(sys.argv)>2 else "20260820"; D1=sys.argv[3] if len(sys.argv)>3 else "20261127"
NGUONG_LON=20; LIM=50000
os.makedirs(OUT,exist_ok=True)
async def rpc(ws,method,params,rid,timeout=180):
    await ws.send(json.dumps({"method":method,"params":params,"id":rid}))
    end=asyncio.get_event_loop().time()+timeout
    while True:
        m=json.loads(await asyncio.wait_for(ws.recv(),timeout=max(1,end-asyncio.get_event_loop().time())))
        if "stream" in m: continue
        if m.get("id")==rid: return m
async def phien(ws,d,rid):
    t0=int(datetime(d.year,d.month,d.day,8,0,tzinfo=NY).timestamp()*1000)
    t1=int(datetime(d.year,d.month,d.day,16,15,tzinfo=NY).timestamp()*1000)
    t_rth=int(datetime(d.year,d.month,d.day,9,30,tzinfo=NY).timestamp()*1000)
    phut={}; hs=collections.defaultdict(lambda:[0,0]); seen=set(); cur=t0; n=0; trang=0
    # API tra ve LIM tick CUOI CUNG trong [start,end] -> phan trang LUI tu t1 ve t0
    cur=t1
    while cur>t0:
        rid+=1; m=await rpc(ws,"aggTrades",{"exchange":"CME","symbol":"ESZ6","startTime":t0,"endTime":cur,"limit":LIM},rid)
        rs=m.get("result") or []
        if m.get("status",200)!=200: return None,rid,f"status {m.get('status')} {m.get('error')}"
        moi=0; first=cur
        for r in rs:
            r=list(r)+[None]*(6-len(r)); tms,p,q,s,_,tu=r[:6]
            k=tu if tu is not None else (tms,p,q,s)
            if k in seen: continue
            seen.add(k); moi+=1; n+=1; first=min(first,tms)
            p=float(p); q=float(q); mua= s=="B"
            mi=tms//60000
            a=phut.get(mi)
            if a is None: a=phut[mi]=[None,p,p,None,0,0,0,0,0,0,0,10**15,0]
            # thu tu lui: giu tick som nhat lam open, muon nhat lam close
            if tms<=a[11]: a[11]=tms; a[0]=p
            if tms>=a[12]: a[12]=tms; a[3]=p
            a[1]=max(a[1],p); a[2]=min(a[2],p); a[4]+=q
            if mua: a[5]+=q
            else: a[6]+=q
            a[7]+=1
            if q>=NGUONG_LON:
                if mua: a[8]+=q
                else: a[9]+=q
            a[10]=max(a[10],q)
            if tms>=t_rth: hs[p][0 if mua else 1]+=q
        trang+=1
        if len(rs)<LIM or moi==0: break
        cur=first
    return (phut,hs,n,trang),rid,None
async def main():
    d=datetime.strptime(D0,"%Y%m%d"); dE=datetime.strptime(D1,"%Y%m%d"); rid=1000
    async with websockets.connect(URL,max_size=2**30,ping_interval=20,open_timeout=15) as ws:
        while d<=dE:
            ten=d.strftime("%Y%m%d"); f1=os.path.join(OUT,f"phut_{ten}.csv")
            if d.weekday()<5 and not os.path.exists(f1):
                t=datetime.now()
                try:
                    kq,rid,loi=await phien(ws,d,rid)
                except Exception as e:
                    kq,loi=None,repr(e)
                if kq and kq[2]>0:
                    phut,hs,n,trang=kq
                    with open(f1+".tmp","w",newline="") as f:
                        w=csv.writer(f); w.writerow(["phut_ms","o","h","l","c","vol","vol_mua","vol_ban","so_lenh","lon_mua","lon_ban","max_qty"])
                        for mi in sorted(phut): a=phut[mi]; w.writerow([mi*60000,a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8],a[9],a[10]])
                    with open(os.path.join(OUT,f"hoso_{ten}.csv"),"w",newline="") as f:
                        w=csv.writer(f); w.writerow(["gia","vol_mua","vol_ban"])
                        for p in sorted(hs): w.writerow([p,hs[p][0],hs[p][1]])
                    os.replace(f1+".tmp",f1)
                print(ten,"tick",kq[2] if kq else 0,"trang",kq[3] if kq else 0,"loi",loi,"giay",round((datetime.now()-t).total_seconds()),flush=True)
            d+=timedelta(days=1)
asyncio.run(main())
