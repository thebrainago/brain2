# SIMULATED basket engine (no hard SL): DCA ladder + hedge + trim(chot non) + prune(tia) + basket close (chot tong).
# Conservative intrabar order: adverse extreme first (DCA/hedge fills, worst equity, stop-out), then favorable exits.
# Bars are XM BID; ask = bid + spread. All numbers produced are SIMULATED (MT5 tick-real is final arbiter).
import numpy as np
from numba import njit
MAXP=64
# P: 0 L0 1 mult 2 gap 3 gstep 4 maxN 5 btp 6 trim 7 prune_k 8 hedge_on 9 hgap 10 hr 11 htp 12 cd 13 comp
#    14 pv 15 lev 16 EQ0 17 topup 18 topup_trig 19 swl 20 sws 21 slip 22 sprmul 23 dsig 24 maxlots 25 gap_atr 26 triple_dow
@njit(cache=True)
def pos_pnl(p,spr,e,lt,sd,pv):
    if sd>0: return (p-e)*lt*pv
    return (e-(p+spr))*lt*pv
@njit(cache=True)
def run(o,h,l,c,spr0,atr,sig,roll,dow,fl,P):
    n=len(c)
    L0=P[0];mult=P[1];gap=P[2];gstep=P[3];maxN=int(P[4]);btp=P[5];trim=P[6];prune_k=P[7]
    hon=P[8];hgap=P[9];hr=P[10];htp=P[11];cd=int(P[12]);comp=P[13];pv=P[14];lev=P[15];EQ0=P[16]
    topup=P[17];ttrig=P[18];swl=P[19];sws=P[20];slip=P[21];sprm=P[22];dsig=P[23];maxlots=P[24];gatr=P[25];tdow=int(P[26]); hsk=P[27]; hsusd=P[28]; dlusd=P[29]
    fe=0.0; bal0=EQ0; day0=EQ0; dblock=False; nhs=0; nfl=0; ndl=0
    pe=np.zeros(MAXP);pl=np.zeros(MAXP);ps=np.zeros(MAXP);ph=np.zeros(MAXP)
    np_=0; bal=EQ0; dep=EQ0; tu_left=topup; d=0; nlay=0; last_e=0.0; bank=0.0; cool=0
    opn=np.zeros(n,np.int64); eq_c=np.zeros(n); eq_w=np.zeros(n); netl=np.zeros(n); depa=np.full(n,EQ0)
    nb=0; nwin=0; norders=0; blown=0; maxlay=0; maxlot=0.0; peak=EQ0; mdd=0.0; mddu=0.0
    for i in range(1,n):
        spr=spr0[i]*sprm; sl_=slip*spr
        # swap at rollover (XM server midnight); triple on tdow
        if roll[i] and np_>0:
            m=3.0 if dow[i]==tdow else 1.0
            for k in range(np_):
                bal+= (swl if ps[k]>0 else sws)*pl[k]*m
        # equity-based lot
        eqn=bal
        for k in range(np_): eqn+=pos_pnl(o[i],spr,pe[k],pl[k],ps[k],pv)
        if roll[i]:
            day0=eqn; dblock=False
        # weekend hedge-lock (fl==2): open opposite hedge for net exposure; unwind when window ends
        if fl[i]==2 and np_>0:
            hw=False; nn_=0.0
            for k in range(np_):
                if ph[k]==2: hw=True
                nn_+=ps[k]*pl[k]
            if (not hw) and abs(nn_)>1e-9 and np_<MAXP:
                hd=-1 if nn_>0 else 1
                fpx=o[i]-sl_ if hd<0 else o[i]+spr+sl_
                pe[np_]=fpx;pl[np_]=abs(nn_);ps[np_]=hd;ph[np_]=2;np_+=1;nfl+=1
        if fl[i]==0 and np_>0:
            k=0
            while k<np_:
                if ph[k]==2:
                    fpx=o[i]-sl_ if ps[k]>0 else o[i]+sl_
                    bal+=pos_pnl(fpx,spr,pe[k],pl[k],ps[k],pv)
                    np_-=1
                    if k!=np_:
                        pe[k]=pe[np_];pl[k]=pl[np_];ps[k]=ps[np_];ph[k]=ph[np_]
                else: k+=1
        if fl[i]==1 and np_>0:
            for k in range(np_):
                fp0=o[i]-sl_ if ps[k]>0 else o[i]+sl_
                bal+=pos_pnl(fp0,spr,pe[k],pl[k],ps[k],pv)
            np_=0;nlay=0;bank=0.0;nfl+=1
        scale=1.0
        if comp>0: scale=max(1.0,eqn/EQ0)
        g_=gap
        if gatr>0 and atr[i]>0: g_=max(gap*0.5,gatr*atr[i])
        # new basket at open
        if np_==0 and cool<=0 and sig[i-1]!=0 and fl[i]==0 and (not dblock):
            d=int(sig[i-1]); lt=max(0.01,np.floor(L0*scale*100+1e-9)/100)
            fill=o[i]+spr+sl_ if d>0 else o[i]-sl_
            pe[0]=fill;pl[0]=lt;ps[0]=d;ph[0]=0;np_=1;nlay=1;last_e=fill;bank=0.0;nb+=1;norders+=1;fe=fill;bal0=bal;opn[i]=d
        if cool>0: cool-=1
        if np_>0:
            adv=l[i] if d>0 else h[i]
            added=False
            # DCA adds
            while nlay<maxN and fl[i]==0:
                step=g_*gstep**(nlay-1)
                lvl=last_e-d*step
                if (d>0 and adv<=lvl) or (d<0 and adv>=lvl):
                    if dsig>0 and sig[i-1]==-d: break
                    tot=0.0
                    for k in range(np_):
                        if ph[k]==0: tot+=pl[k]
                    lt=max(0.01,np.floor(L0*scale*mult**nlay*100+1e-9)/100)
                    if maxlots>0 and tot+lt>maxlots: break
                    if np_>=MAXP: break
                    px0=min(lvl,o[i]) if d>0 else max(lvl,o[i])
                    fill=px0+spr+sl_ if d>0 else px0-sl_
                    pe[np_]=fill;pl[np_]=lt;ps[np_]=d;ph[np_]=0;np_+=1;nlay+=1;last_e=lvl;norders+=1;added=True
                else: break
            # hedge
            if hon>0:
                hact=False
                for k in range(np_):
                    if ph[k]>0: hact=True
                if (not hact) and nlay>=maxN and np_<MAXP:
                    lvl=last_e-d*hgap
                    if (d>0 and adv<=lvl) or (d<0 and adv>=lvl):
                        tot=0.0
                        for k in range(np_):
                            if ph[k]==0: tot+=pl[k]
                        lt=max(0.01,np.floor(tot*hr*100+1e-9)/100)
                        px0=min(lvl,o[i]) if d>0 else max(lvl,o[i])
                        fill=px0-sl_ if d>0 else px0+spr+sl_
                        pe[np_]=fill;pl[np_]=lt;ps[np_]=-d;ph[np_]=1;np_+=1;norders+=1;added=True
            # ---- risk stops (new): price stop beyond ladder, basket USD stop, daily loss kill
            if np_>0 and (hsk>0 or hsusd>0 or dlusd>0):
                aa=0.0; nlx=0.0
                for k in range(np_):
                    if ps[k]>0: aa+=-pe[k]*pl[k]*pv; nlx+=pl[k]*pv
                    else: aa+=(pe[k]-spr)*pl[k]*pv; nlx-=pl[k]*pv
                cand=0.0; have=False; kind=0
                if hsk>0:
                    S=0.0
                    for j in range(maxN-1): S+=gap*gstep**j
                    S+=hsk*gap
                    pst=fe-d*S
                    if (d>0 and l[i]<=pst) or (d<0 and h[i]>=pst):
                        cand=pst; have=True; kind=1
                for t in range(2):
                    thr=-1e18
                    if t==0 and hsusd>0: thr=bal0-hsusd-bal
                    if t==1 and dlusd>0: thr=day0-dlusd-bal
                    if thr>-1e17 and nlx!=0:
                        pp=(thr-aa)/nlx
                        hit=(nlx>0 and l[i]<=pp) or (nlx<0 and h[i]>=pp)
                        if hit:
                            if (not have) or (d>0 and pp>cand) or (d<0 and pp<cand): cand=pp; have=True; kind=2+t
                if have:
                    fp=cand
                    if d>0 and fp>o[i]: fp=o[i]
                    if d<0 and fp<o[i]: fp=o[i]
                    fp=fp-sl_ if d>0 else fp+sl_
                    for k in range(np_): bal+=pos_pnl(fp,spr,pe[k],pl[k],ps[k],pv)
                    np_=0;nlay=0;bank=0.0;cool=cd
                    if kind==3: dblock=True; ndl+=1
                    else: nhs+=1
            # worst-case equity in bar (both extremes)
            e1=bal;e2=bal
            for k in range(np_):
                e1+=pos_pnl(l[i],spr,pe[k],pl[k],ps[k],pv); e2+=pos_pnl(h[i],spr,pe[k],pl[k],ps[k],pv)
            ew=min(e1,e2); pw=l[i] if e1<e2 else h[i]
            lg=0.0;sh=0.0
            for k in range(np_):
                if ps[k]>0: lg+=pl[k]
                else: sh+=pl[k]
            marg=max(lg,sh)*pv*c[i]/lev
            if tu_left>0 and (ew<ttrig*EQ0 or ew<marg):
                bal+=tu_left; dep+=tu_left; ew+=tu_left; tu_left=0.0
            if marg>0 and ew<0.5*marg:
                for k in range(np_): bal+=pos_pnl(pw,spr,pe[k],pl[k],ps[k],pv)
                np_=0;nlay=0;blown+=1;cool=cd
                eq_w[i]=bal; eq_c[i]=bal; depa[i]=dep
                if peak-(bal-(dep-EQ0))>mddu: mddu=peak-(bal-(dep-EQ0))
                if peak>0 and (peak-(bal-(dep-EQ0)))/peak>mdd: mdd=(peak-(bal-(dep-EQ0)))/peak
                if bal<=0:
                    for j in range(i,n): eq_c[j]=bal; eq_w[j]=bal; depa[j]=dep
                    break
                continue
            ewn=ew-(dep-EQ0)
            if peak-ewn>mddu: mddu=peak-ewn
            if peak>0 and (peak-ewn)/peak>mdd: mdd=(peak-ewn)/peak
            eq_w[i]=ew
            if nlay>maxlay: maxlay=nlay
            if lg+sh>maxlot: maxlot=lg+sh
            # favorable: trim newest main layer (chot non)
            fav=h[i] if d>0 else l[i]
            if trim>0 and nlay>=2 and not added:
                kk=-1
                if True:
                    best=-1e18
                    for k in range(np_):
                        if ph[k]==0 and pe[k]*(-d)>best: best=pe[k]*(-d); kk=k
                tp=pe[kk]+d*trim
                if (d>0 and fav>=tp) or (d<0 and fav<=tp):
                    px_=tp if d>0 else tp-spr
                    pr=pos_pnl(px_,spr,pe[kk],pl[kk],ps[kk],pv)
                    bal+=pr; bank+=pr
                    np_-=1
                    if kk!=np_:
                        pe[kk]=pe[np_];pl[kk]=pl[np_];ps[kk]=ps[np_];ph[kk]=ph[np_]
                    nlay-=1
                    # new last entry = most adverse remaining main layer
                    ext=0.0;first=True
                    for k in range(np_):
                        if ph[k]==0:
                            if first or (d>0 and pe[k]<ext) or (d<0 and pe[k]>ext): ext=pe[k]; first=False
                    last_e=ext-(spr if d>0 else 0.0)
            # basket close (chot tong): solve price where floating+bank >= btp*mainlots*pv
            tot=0.0; a=0.0; nl=0.0
            for k in range(np_):
                if ph[k]==0: tot+=pl[k]
                if ps[k]>0: a+=-pe[k]*pl[k]*pv; nl+=pl[k]*pv
                else: a+=(pe[k]-spr)*pl[k]*pv; nl-=pl[k]*pv
            tgt=btp*tot*pv-bank
            closed=False
            if added: pass
            elif np_>0 and nl!=0:
                ps_=(tgt-a)/nl
                if (nl>0 and h[i]>=ps_ and ps_>=l[i]) or (nl<0 and l[i]<=ps_ and ps_<=h[i]):
                    fp=ps_; closed=True
                elif (nl>0 and ps_<l[i]) or (nl<0 and ps_>h[i]):
                    fp=o[i]; closed=True
            elif np_>0 and a>=tgt:
                fp=c[i]; closed=True
            if closed:
                s=0.0
                for k in range(np_): s+=pos_pnl(fp,spr,pe[k],pl[k],ps[k],pv)
                bal+=s
                if s+bank>0: nwin+=1
                np_=0;nlay=0;cool=cd;bank=0.0
            if np_>0:
                # hedge TP at close
                for k in range(np_):
                    if ph[k]==1:
                        pr=pos_pnl(c[i],spr,pe[k],pl[k],ps[k],pv)
                        if pr>=htp*pl[k]*pv:
                            bal+=pr; bank+=pr; np_-=1
                            if k!=np_:
                                pe[k]=pe[np_];pl[k]=pl[np_];ps[k]=ps[np_];ph[k]=ph[np_]
                            break
                # prune (tia): use bank to close the worst main layer
                if prune_k>0 and nlay>=2:
                    worst=1e18;kw=-1
                    for k in range(np_):
                        if ph[k]==0:
                            pr=pos_pnl(c[i],spr,pe[k],pl[k],ps[k],pv)
                            if pr<worst: worst=pr;kw=k
                    if kw>=0 and worst<0 and bank>=prune_k*(-worst):
                        bal+=worst; bank+=worst; np_-=1
                        if kw!=np_:
                            pe[kw]=pe[np_];pl[kw]=pl[np_];ps[kw]=ps[np_];ph[kw]=ph[np_]
                        nlay-=1
        else:
            eq_w[i]=bal
        ec=bal; nn=0.0
        for k in range(np_):
            ec+=pos_pnl(c[i],spr,pe[k],pl[k],ps[k],pv); nn+=ps[k]*pl[k]
        eq_c[i]=ec; netl[i]=nn; depa[i]=dep
        if eq_w[i]==0: eq_w[i]=ec
        pk=ec-(dep-EQ0)
        if pk>peak: peak=pk
    eq_c[0]=EQ0; eq_w[0]=EQ0
    return opn,eq_c,eq_w,netl,depa,np.array([nb,nwin,norders,blown,maxlay,maxlot,mdd,mddu,dep,nhs,nfl,ndl])
