"""Hybrid version of sim.run: MAIN ladder or distance+snap-to-zone ladder (pct/fib/ES-VP/options, weighted confluence),
integer indicator score S (gate entry/DCA, lot multiplier), deep-layer trim, exits: BE+y, score flip, opposite zone.
lmode=0 + all gates off reproduces sim.run (checked)."""
import numpy as np, sys
from numba import njit
sys.path.insert(0,'/workspace/sp500_sys')
from sim import PCT, FIB, ladder
MAXZ=24; MAXH=300; MAXB=6000
@njit(cache=True)
def ladder_h(H,Lo,a,fp,vpd,optr,G,ks,gmin,gmax,wP,wF,wV,wO,maxL):
    cz=np.empty(80); cw=np.empty(80); n=0
    for q in PCT: cz[n]=H-q*a; cw[n]=wP; n+=1
    leg=H-Lo
    if leg>0:
        for r in FIB: cz[n]=H-r*leg; cw[n]=wF; n+=1
    for v in vpd:
        if v==v and wV>0: cz[n]=v; cw[n]=wV; n+=1
    for v in optr:
        if v==v and wO>0: cz[n]=v; cw[n]=wO; n+=1
    conf=np.zeros(n)
    for x in range(n):
        for y in range(n):
            if abs(cz[x]-cz[y])<=0.3*a: conf[x]+=cw[y]
    out=np.empty(MAXZ); oc=np.zeros(MAXZ); m=0; prev=fp
    while m<min(MAXZ,maxL+3):
        tg=prev-G*a; best=-1; bc=-1.0; bd=1e18
        if ks>0:
            for x in range(n):
                z=cz[x]; gap=prev-z
                if abs(z-tg)<=ks*a and gap>=gmin*a and gap<=gmax*a and cw[x]>0:
                    if conf[x]>bc+1e-9 or (abs(conf[x]-bc)<1e-9 and abs(z-tg)<bd): best=x; bc=conf[x]; bd=abs(z-tg)
        if best>=0: out[m]=cz[best]; oc[m]=bc
        else: out[m]=tg; oc[m]=0.0
        prev=out[m]; m+=1
    return out,oc,m
@njit(cache=True)
def run(o,h,l,c,a5,a15,ah1,m5end,c5p,roll,zzlo,zzext,didx,vp,opt,S,flip,P,i0,i1):
    (zmode,K,coef,maxL,tp1,sfrac,bx,bxu,hmode,hN,hr,hcap,htp,hrecl,hexp,brk,spr,EQ0,ddb,mlf,lev,swl,sws,emode,refill,dmin,mg,
     lmode,G,ks,gmin,gmax,wP,wF,wV,wO,se,sd,shi,chi,mhi,sfd,flipx,oppx,deadw)=P
    K=int(K); maxL=int(maxL); hN=int(hN); hrecl=int(hrecl); hexp=int(hexp); zmode=int(zmode); lmode=int(lmode); deadw=int(deadw)
    lpx=np.zeros(40); lzone=np.zeros(40); lcore=np.zeros(40); ls=np.zeros(40); lsopen=np.zeros(40,np.bool_); lstp=np.zeros(40); lsfill=np.zeros(40); lsbar=np.zeros(40,np.int64)
    nl=0; zp=np.zeros(MAXZ); zc=np.zeros(MAXZ); nz=0; zbroken=np.zeros(MAXZ,np.bool_); znext=0; Hopen=0.0
    hp=np.zeros(MAXH); hl=np.zeros(MAXH); htpp=np.zeros(MAXH); hev=np.zeros(MAXH,np.int64); hbar=np.zeros(MAXH,np.int64); nh=0
    NE=MAXB*4; evL=np.zeros(NE); evst=np.zeros(NE,np.int64); evleft=np.zeros(NE,np.int64); evstop=np.zeros(NE,np.bool_); evlot=np.zeros(NE); ne=0
    dead=np.zeros(4000); deadi=np.zeros(4000,np.int64); nd=0
    real=0.0; hreal=0.0; sreal=0.0; peak=EQ0; maxdd=0.0; minml=1e18; minml100=1e18; blown=-1; blown100=-1; maxfl=0.0
    ntick=0; nhtick=0; nstp=0; ndcablk=0; nddblk=0; nmlwarn=0; maxlots=0.0; maxhl=0.0; maxlay=0
    bo=np.zeros(MAXB,np.int64); bc=np.zeros(MAXB,np.int64); blay=np.zeros(MAXB,np.int64); bworst=np.zeros(MAXB); bpnl=np.zeros(MAXB); blots=np.zeros(MAXB); nb=0; bstart_real=0.0
    inb=False; hrun=0.0; lastext=-1; eq=EQ0
    eqc=np.zeros(i1-i0)
    for i in range(i0,i1):
        a=a15[i-1]
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
        fl=(o[i]*bsum-bcost)
        for k in range(nh): fl+=(hp[k]-o[i]-spr)*hl[k]
        eqo=EQ0+real+fl; marg=(bsum+hs)*o[i]/lev; ml=eqo/marg*100.0 if marg>0 else 1e18
        canadd=True
        if fl<=-ddb: canadd=False; nddblk+=1
        if ml<mlf: canadd=False; nmlwarn+=1
        if not inb:
            if hrun>0 and zzlo[i]==zzlo[i] and a>0 and canadd and S[i]>=se:
                zz,m=ladder(hrun,zzlo[i],a,zmode,vp[didx[i]],dmin,mg,maxL)
                if m>0 and l[i]<=zz[0]:
                    fp=min(o[i],zz[0]); nz=0
                    if lmode==0:
                        for q in range(1,m):
                            if zz[q]<fp-mg*a*0.5: zp[nz]=zz[q]; zc[nz]=0.0; nz+=1
                        if nz==0: zp[0]=fp-mg*a; nz=1
                    else:
                        z2,c2,m2=ladder_h(hrun,zzlo[i],a,fp,vp[didx[i]],opt[i],G,ks,gmin,gmax,wP,wF,wV,wO,maxL)
                        for q in range(m2): zp[q]=z2[q]; zc[q]=c2[q]
                        nz=m2
                    zbroken[:]=False; znext=0; Hopen=hrun
                    mul=mhi if S[i]>=shi else 1.0
                    v=np.floor(K*0.1*mul/0.1+0.5)*0.1
                    s=np.floor(sfrac*v/0.1+1e-6)*0.1 if tp1>0 else 0.0
                    lpx[0]=fp+spr; lzone[0]=fp; lcore[0]=v-s; ls[0]=s; lsopen[0]=s>0; lsfill[0]=fp+spr; lstp[0]=fp+tp1*a; lsbar[0]=i; nl=1
                    ntick+=int(round(v/0.1)); inb=True; bo[nb]=i; blay[nb]=1; bworst[nb]=0.0; blots[nb]=v; bstart_real=real
        else:
            if nl<maxL and znext<nz and l[i]<=zp[znext]:
                if nh>0: ndcablk+=1; znext+=1
                elif not canadd: znext+=1
                elif S[i]>=sd:
                    fp=min(o[i],zp[znext])
                    mul=mhi if (S[i]>=shi or zc[znext]>=chi) else 1.0
                    v=np.floor(K*0.1*coef**nl*mul/0.1+0.5)*0.1
                    if v<0.1: v=0.1
                    sf=sfd if nl>=2 else sfrac
                    s=np.floor(sf*v/0.1+1e-6)*0.1 if tp1>0 else 0.0
                    lpx[nl]=fp+spr; lzone[nl]=fp; lcore[nl]=v-s; ls[nl]=s; lsopen[nl]=s>0; lsfill[nl]=fp+spr; lstp[nl]=fp+tp1*a; lsbar[nl]=i
                    nl+=1; ntick+=int(round(v/0.1)); blay[nb]=max(blay[nb],nl)
                    while znext<nz and zp[znext]>fp-0.5*mg*a: znext+=1
            if refill>0 and nh==0 and canadd:
                for k in range(nl):
                    if (not lsopen[k]) and ls[k]>0 and l[i]<=lzone[k] and i>lsbar[k]:
                        fp=min(o[i],lzone[k]); lsopen[k]=True; lsfill[k]=fp+spr; lstp[k]=fp+tp1*a; lsbar[k]=i; ntick+=int(round(ls[k]/0.1))
            for k in range(nl):
                if lsopen[k] and i>lsbar[k] and h[i]>=lstp[k]:
                    px=max(o[i],lstp[k]); pnl=(px-lsfill[k])*ls[k]; real+=pnl; sreal+=pnl; lsopen[k]=False; lsbar[k]=i; nstp+=1
        if hmode>0:
            for e in range(ne):
                if evleft[e]>0 and (not evstop[e]) and c[i-1]<evL[e] and nh<MAXH:
                    hs=0.0
                    for k in range(nh): hs+=hl[k]
                    v=evlot[e]
                    if hs+v<=hcap*bsum+1e-9 and v>=0.1:
                        hp[nh]=o[i]; hl[nh]=v; htpp[nh]=o[i]-htp*a5[i-1]; hev[nh]=e; hbar[nh]=i; nh+=1; nhtick+=int(round(v/0.1))
                    evleft[e]-=1
            k=0
            while k<nh:
                if i>hbar[k] and l[i]+spr<=htpp[k]:
                    px=min(o[i]+spr,htpp[k]); pnl=(hp[k]-px)*hl[k]; real+=pnl; hreal+=pnl
                    nh-=1; hp[k]=hp[nh]; hl[k]=hl[nh]; htpp[k]=htpp[nh]; hev[k]=hev[nh]; hbar[k]=hbar[nh]
                else: k+=1
        bsum=0.0; bcost=0.0
        for k in range(nl):
            bsum+=lcore[k]; bcost+=lcore[k]*lpx[k]
            if lsopen[k]: bsum+=ls[k]; bcost+=ls[k]*lsfill[k]
        hs=0.0; hfl_l=0.0; hfl_h=0.0
        for k in range(nh): hs+=hl[k]; hfl_l+=(hp[k]-l[i]-spr)*hl[k]; hfl_h+=(hp[k]-h[i]-spr)*hl[k]
        f1=(l[i]*bsum-bcost)+hfl_l; f2=(h[i]*bsum-bcost)+hfl_h; fw=min(f1,f2)
        weq=EQ0+real+fw
        if fw<maxfl: maxfl=fw
        if bsum>maxlots: maxlots=bsum
        if hs>maxhl: maxhl=hs
        if nl>maxlay: maxlay=nl
        if inb:
            if fw<bworst[nb]: bworst[nb]=fw
            if bsum>blots[nb]: blots[nb]=bsum
        mg_=(bsum+hs)*c[i]
        if mg_>0:
            m1=weq/(mg_/lev)*100.0; m2=weq/(mg_/100.0)*100.0
            if m1<minml: minml=m1
            if m2<minml100: minml100=m2
            if m2<=20.0 and blown100<0: blown100=i
        if peak-weq>maxdd: maxdd=peak-weq
        if weq<=0 and blown<0: blown=i
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
                            if i-deadi[j]<deadw and abs(dead[j]-L)<0.5*a: fresh=False; break
                        if nd<4000: dead[nd]=L; deadi[nd]=i; nd+=1
                        if fresh and ne<NE:
                            v=np.floor(hr*bsum/hN/0.1+1e-6)*0.1
                            if v<0.1: v=0.1
                            evL[ne]=L; evst[ne]=i; evleft[ne]=hN; evstop[ne]=False; evlot[ne]=v; ne+=1
                        break
                    elif c[i]<thr: zbroken[q]=True
        if roll[i]: real+=swl*bsum+sws*hs
        if inb and nh==0 and bsum>0:
            avg=bcost/bsum; x=bx*(ah1[i] if bxu==1 else a15[i])
            ex=c[i]>=avg+x
            if (not ex) and flipx>0 and flip[i] and c[i]>=avg: ex=True
            if (not ex) and oppx>0 and c[i]>=Hopen-0.25*a15[i] and c[i]>=avg: ex=True
            if ex:
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
    res=np.array([eq-EQ0,real,hreal,sreal,maxdd,minml,minml100,ntick,nhtick,nstp,ndcablk,nddblk,nmlwarn,maxlots,maxhl,blown,nb,ne,maxfl,maxlay,blown100])
    return res,eqc,bo[:nb],bc[:nb],blay[:nb],bworst[:nb],bpnl[:nb],blots[:nb]
