"""XSB-20 US500 'Anh-style' system: K x 0.1 entry at data zones, DCA ladder (zigzag pctile / fibo / VP), fixed lot coef,
scalp partial TP + refill, burst hedge on confirmed zone break (no DCA while hedged, re-break not fresh), basket exit BE/+x,
DD budget + margin floor. M1 execution, M5 break signals. Long baskets only (never cut)."""
import numpy as np
from numba import njit
MAXZ=24; MAXH=300; MAXB=4000
# zigzag M15 k=2 down-leg depth percentiles (ATR15 units), XM 2019-01..2026-05 (out/zigzag_stats.json)
PCT=np.array([2.68,3.43,4.55,6.27,8.48,11.35,16.34,20.0,24.0,28.0])
FIB=np.array([0.382,0.5,0.618,0.786,1.0,1.272,1.618,2.0,2.618,3.618])
@njit(cache=True)
def ladder(H,Lo,a,zmode,vp,dmin,mg,maxL):
    cand=np.empty(64); n=0
    if zmode==0 or zmode==2 or zmode==3:
        for q in PCT: cand[n]=H-q*a; n+=1
    if zmode==1 or zmode==2 or zmode==3:
        leg=H-Lo
        if leg>0:
            for r in FIB: cand[n]=H-r*leg; n+=1
        if zmode==1:   # pad with pctile depths only beyond the deepest fib
            deep=FIB[-1]*leg if leg>0 else 0.0
            for q in PCT:
                if q*a>deep: cand[n]=H-q*a; n+=1
    if zmode==3:
        for v in vp:
            if v==v: cand[n]=v; n+=1
    z=np.sort(cand[:n])[::-1]
    out=np.empty(MAXZ); m=0
    for v in z:
        if H-v<dmin*a: continue
        if m>0 and out[m-1]-v<mg*a:
            continue
        out[m]=v; m+=1
        if m>=MAXZ or m>=maxL+4: break
    return out,m
@njit(cache=True)
def run(o,h,l,c,a5,a15,ah1,m5end,c5p,roll,zzlo,zzext,didx,vp,P,i0,i1):
    (zmode,K,coef,maxL,tp1,sfrac,bx,bxu,hmode,hN,hr,hcap,htp,hrecl,hexp,brk,spr,EQ0,ddb,mlf,lev,swl,sws,emode,refill,dmin,mg)=P
    K=int(K); maxL=int(maxL); hN=int(hN); hrecl=int(hrecl); hexp=int(hexp); zmode=int(zmode); emode=int(emode)
    # layers
    lpx=np.zeros(40); lzone=np.zeros(40); lcore=np.zeros(40); ls=np.zeros(40); lsopen=np.zeros(40,np.bool_); lstp=np.zeros(40); lsfill=np.zeros(40); lsbar=np.zeros(40,np.int64)
    nl=0; zp=np.zeros(MAXZ); nz=0; zbroken=np.zeros(MAXZ,np.bool_); znext=0
    # hedges
    hp=np.zeros(MAXH); hl=np.zeros(MAXH); htpp=np.zeros(MAXH); hev=np.zeros(MAXH,np.int64); hbar=np.zeros(MAXH,np.int64); nh=0
    evL=np.zeros(MAXB*4); evst=np.zeros(MAXB*4,np.int64); evleft=np.zeros(MAXB*4,np.int64); evstop=np.zeros(MAXB*4,np.bool_); evlot=np.zeros(MAXB*4); ne=0
    dead=np.zeros(2000); deadi=np.zeros(2000,np.int64); nd=0
    real=0.0; hreal=0.0; sreal=0.0; peak=EQ0; maxdd=0.0; minml=1e18; minml100=1e18; blown=-1
    ntick=0; nhtick=0; nstp=0; ndcablk=0; nddblk=0; nmlwarn=0; maxlots=0.0; maxhl=0.0
    # basket records: open, close, layers, worst float, pnl, maxlots
    bo=np.zeros(MAXB,np.int64); bc=np.zeros(MAXB,np.int64); blay=np.zeros(MAXB,np.int64); bworst=np.zeros(MAXB); bpnl=np.zeros(MAXB); blots=np.zeros(MAXB); nb=0; bstart_real=0.0
    inb=False; hrun=0.0; lastext=-1
    eqc=np.zeros(i1-i0)
    for i in range(i0,i1):
        a=a15[i-1]
        # running high since last confirmed M15 zigzag low (extremum bar), known up to i-1
        if zzext[i]!=lastext:
            lastext=zzext[i]; hrun=0.0
            for j in range(zzext[i],i): 
                if h[j]>hrun: hrun=h[j]
        elif h[i-1]>hrun: hrun=h[i-1]
        bsum=0.0; bcost=0.0
        for k in range(nl):
            bsum+=lcore[k]; bcost+=lcore[k]*lpx[k]
            if lsopen[k]: bsum+=ls[k]; bcost+=ls[k]*lsfill[k]
        hs=0.0
        for k in range(nh): hs+=hl[k]
        # floating & margin at bar open (for gating)
        fl=(o[i]*bsum-bcost)
        for k in range(nh): fl+=(hp[k]-o[i]-spr)*hl[k]
        eqo=EQ0+real+fl
        marg=(bsum+hs)*o[i]/lev
        ml=eqo/marg*100.0 if marg>0 else 1e18
        canadd=True
        if fl<=-ddb: canadd=False; nddblk+=1
        if ml<mlf: canadd=False; nmlwarn+=1
        # ---- entry when flat
        if not inb:
            ok=False; z1=0.0
            if emode==1: ok=True; z1=o[i]
            elif hrun>0 and zzlo[i]==zzlo[i] and a>0:
                zz,m=ladder(hrun,zzlo[i],a,zmode,vp[didx[i]],dmin,mg,maxL)
                if m>0 and l[i]<=zz[0]: ok=True; z1=zz[0]
            if ok and canadd:
                fp=min(o[i],z1)
                if emode==1:
                    nz=0
                    for q in range(1,MAXZ):
                        zp[nz]=fp-q*1.5*ah1[i-1]; nz+=1
                else:
                    zz,m=ladder(hrun,zzlo[i],a,zmode,vp[didx[i]],dmin,mg,maxL)
                    nz=0
                    for q in range(1,m):
                        if zz[q]<fp-mg*a*0.5: zp[nz]=zz[q]; nz+=1
                    if nz==0:
                        zp[0]=fp-mg*a; nz=1
                zbroken[:]=False; znext=0
                v=np.floor(K*0.1*1.0/0.1+1e-6)*0.1
                s=np.floor(sfrac*v/0.1+1e-6)*0.1 if tp1>0 else 0.0
                lpx[0]=fp+spr; lzone[0]=fp; lcore[0]=v-s; ls[0]=s; lsopen[0]=s>0; lsfill[0]=fp+spr; lstp[0]=fp+tp1*a; lsbar[0]=i; nl=1
                ntick+=int(round(v/0.1)); inb=True; bo[nb]=i; blay[nb]=1; bworst[nb]=0.0; blots[nb]=v; bstart_real=real
        else:
            # ---- DCA at next zone (a zone touched while hedged / DD-blocked is skipped, not filled later)
            if nl<maxL and znext<nz and l[i]<=zp[znext]:
                if nh>0: ndcablk+=1; znext+=1
                elif not canadd: znext+=1
                else:
                    fp=min(o[i],zp[znext])
                    v=np.floor(K*0.1*coef**nl/0.1+0.5)*0.1
                    if v<0.1: v=0.1
                    s=np.floor(sfrac*v/0.1+1e-6)*0.1 if tp1>0 else 0.0
                    lpx[nl]=fp+spr; lzone[nl]=fp; lcore[nl]=v-s; ls[nl]=s; lsopen[nl]=s>0; lsfill[nl]=fp+spr; lstp[nl]=fp+tp1*a; lsbar[nl]=i
                    nl+=1; ntick+=int(round(v/0.1)); blay[nb]=max(blay[nb],nl)
                    while znext<nz and zp[znext]>fp-0.5*mg*a: znext+=1
            # ---- scalp refill
            if refill>0 and nh==0 and canadd:
                for k in range(nl):
                    if (not lsopen[k]) and ls[k]>0 and l[i]<=lzone[k] and i>lsbar[k]:
                        fp=min(o[i],lzone[k]); lsopen[k]=True; lsfill[k]=fp+spr; lstp[k]=fp+tp1*a; lsbar[k]=i; ntick+=int(round(ls[k]/0.1))
            # ---- scalp TP (from next bar after fill)
            for k in range(nl):
                if lsopen[k] and i>lsbar[k] and h[i]>=lstp[k]:
                    px=max(o[i],lstp[k]); pnl=(px-lsfill[k])*ls[k]; real+=pnl; sreal+=pnl; lsopen[k]=False; lsbar[k]=i; nstp+=1
        # ---- hedge burst entries (one order per bar while below level & not stopped)
        if hmode>0:
            for e in range(ne):
                if evleft[e]>0 and (not evstop[e]) and c[i-1]<evL[e] and nh<MAXH:
                    hs=0.0
                    for k in range(nh): hs+=hl[k]
                    v=evlot[e]
                    if hs+v<=hcap*bsum+1e-9 and v>=0.1:
                        hp[nh]=o[i]; hl[nh]=v; htpp[nh]=o[i]-htp*a5[i-1]; hev[nh]=e; hbar[nh]=i; nh+=1; nhtick+=int(round(v/0.1))
                    evleft[e]-=1
            # hedge TP intrabar (not on entry bar)
            k=0
            while k<nh:
                if i>hbar[k] and l[i]+spr<=htpp[k]:
                    px=min(o[i]+spr,htpp[k]); pnl=(hp[k]-px)*hl[k]; real+=pnl; hreal+=pnl
                    nh-=1; hp[k]=hp[nh]; hl[k]=hl[nh]; htpp[k]=htpp[nh]; hev[k]=hev[nh]; hbar[k]=hbar[nh]
                else: k+=1
        # ---- recompute exposure, worst-case equity, margin
        bsum=0.0; bcost=0.0
        for k in range(nl):
            bsum+=lcore[k]; bcost+=lcore[k]*lpx[k]
            if lsopen[k]: bsum+=ls[k]; bcost+=ls[k]*lsfill[k]
        hs=0.0; hfl_l=0.0; hfl_h=0.0
        for k in range(nh): hs+=hl[k]; hfl_l+=(hp[k]-l[i]-spr)*hl[k]; hfl_h+=(hp[k]-h[i]-spr)*hl[k]
        weq=min(EQ0+real+(l[i]*bsum-bcost)+hfl_l, EQ0+real+(h[i]*bsum-bcost)+hfl_h)
        if bsum>maxlots: maxlots=bsum
        if hs>maxhl: maxhl=hs
        if inb:
            f=weq-(EQ0+real)
            if f<bworst[nb]: bworst[nb]=f
            if bsum>blots[nb]: blots[nb]=bsum
        mg_=(bsum+hs)*c[i]
        if mg_>0:
            m1=weq/(mg_/lev)*100.0; m2=weq/(mg_/100.0)*100.0
            if m1<minml: minml=m1
            if m2<minml100: minml100=m2
        if peak-weq>maxdd: maxdd=peak-weq
        if weq<=0 and blown<0: blown=i
        # ---- end-of-bar: break detection / reclaim / expiry (M5 close)
        if hmode>0:
            for e in range(ne):
                if m5end[i] and c[i]>evL[e]:
                    if hrecl==0: evstop[e]=True
                    else:
                        evstop[e]=True; evleft[e]=0
                        k=0
                        while k<nh:
                            if hev[k]==e and c[i]>evL[e]+0.25*a:
                                pnl=(hp[k]-c[i]-spr)*hl[k]; real+=pnl; hreal+=pnl
                                nh-=1; hp[k]=hp[nh]; hl[k]=hl[nh]; htpp[k]=htpp[nh]; hev[k]=hev[nh]; hbar[k]=hbar[nh]
                            else: k+=1
                if i-evst[e]>=hexp and evst[e]>=0:
                    evleft[e]=0; k=0
                    while k<nh:
                        if hev[k]==e:
                            pnl=(hp[k]-c[i]-spr)*hl[k]; real+=pnl; hreal+=pnl
                            nh-=1; hp[k]=hp[nh]; hl[k]=hl[nh]; htpp[k]=htpp[nh]; hev[k]=hev[nh]; hbar[k]=hbar[nh]
                        else: k+=1
                    evst[e]=-1
            if inb and m5end[i]:
                for q in range(nz):
                    if zbroken[q]: continue
                    L=zp[q]; thr=L-brk*a
                    if c[i]<thr and c5p[i]>=thr:
                        zbroken[q]=True
                        fresh=True
                        for j in range(nd):
                            if i-deadi[j]<2880 and abs(dead[j]-L)<0.5*a: fresh=False; break
                        if nd<2000: dead[nd]=L; deadi[nd]=i; nd+=1
                        if fresh and ne<MAXB*4:
                            v=np.floor(hr*bsum/hN/0.1+1e-6)*0.1
                            if v<0.1: v=0.1
                            evL[ne]=L; evst[ne]=i; evleft[ne]=hN; evstop[ne]=False; evlot[ne]=v; ne+=1
                        break
                    elif c[i]<thr: zbroken[q]=True
        # ---- swap
        if roll[i]: real+=swl*bsum+sws*hs
        # ---- basket exit (no hedge open)
        if inb and nh==0 and bsum>0:
            avg=bcost/bsum; x=bx*(ah1[i] if bxu==1 else a15[i])
            if c[i]>=avg+x:
                real+=(c[i]*bsum-bcost)
                bc[nb]=i; bpnl[nb]=real-bstart_real; nb+=1; inb=False; nl=0; nz=0
                if nb>=MAXB: nb=MAXB-1
        eq=EQ0+real
        for k in range(nl):
            eq+=(c[i]-lpx[k])*lcore[k]
            if lsopen[k]: eq+=(c[i]-lsfill[k])*ls[k]
        for k in range(nh): eq+=(hp[k]-c[i]-spr)*hl[k]
        eqc[i-i0]=eq
        if eq>peak: peak=eq
    if inb:
        bc[nb]=-1; bpnl[nb]=eq-EQ0-bstart_real; nb+=1
    res=np.array([eq-EQ0,real,hreal,sreal,maxdd,minml,minml100,ntick,nhtick,nstp,ndcablk,nddblk,nmlwarn,maxlots,maxhl,blown,nb,ne])
    return res,eqc,bo[:nb],bc[:nb],blay[:nb],bworst[:nb],bpnl[:nb],blots[:nb]
