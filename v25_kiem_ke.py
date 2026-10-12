# -*- coding: utf-8 -*-
"""Vong 25 buoc 1: kiem ke EA + doc bang bo doc HIEN CO (khong sua). Ra JSON co che (ngoai git)."""
import os,sys,json,time,glob
sys.path.insert(0,"/workspace/brain2")
from nhan import doc_ma as DM, cau_kho_ma as CK, mql4_chuan as MQ4
import re
G="/workspace/brain2/data/cau_kho/"
moc=time.mktime(time.strptime("2026-10-12 16:40","%Y-%m-%d %H:%M"))
bo={"github24":[d for d in glob.glob(G+"goi_github/*") if os.path.getmtime(d)>=moc],
    "mql5":glob.glob(G+"goi_mql5/*"),
    "ra_co_che":[G+"ea_ra_co_che/"+x["file"] for x in json.load(open(G+"ea_ra_co_che/NGUON.json"))]}
out={}
for k,ds in bo.items():
  L=[]
  for d in ds:
    fs=[d] if os.path.isfile(d) else [f for f in glob.glob(d+"/**/*",recursive=True) if f.lower().endswith((".mq5",".mq4"))]
    sets=[] if os.path.isfile(d) else [f for f in glob.glob(d+"/**/*.set",recursive=True)]
    for f in fs:
      try: vb=open(f,encoding="utf-8",errors="ignore").read()
      except Exception: continue
      if "OnTick" not in vb and "start()" not in vb and "OnCalculate" in vb: continue
      t=time.time()
      m4=CK.la_mql4(vb) or (f.lower().endswith(".mq4") and not re.search(r"\bCTrade\b|\bMqlTradeRequest\b",vb))
      try:
        dd=DM.doc_chien_luoc(MQ4.chuan_hoa(vb) if m4 else vb,nguon=f); sp=dd.get("co_che",[]) or []; ly=[str(x)[:80] for x in dd.get("chua_dien_dat_duoc",[]) or []]
      except Exception as e: sp=[]; ly=["loi "+type(e).__name__]
      L.append({"goi":d,"file":f,"so_spec":len(sp),"set":sets,"specs":sp,"mql4":bool(m4),"ly_do":ly[:5],"giay":round(time.time()-t,2)})
  out[k]=L; print(k,"goi",len(ds),"tep EA",len(L),"dich duoc",sum(x["so_spec"]>0 for x in L),"spec",sum(x["so_spec"] for x in L),flush=True)
json.dump(out,open(sys.argv[1] if len(sys.argv)>1 else "/workspace/v25_kiemke.json","w"),ensure_ascii=False,default=str)
