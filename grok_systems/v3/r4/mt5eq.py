import sys,os,json,glob,numpy as np,pandas as pd
sys.path.insert(0,'/workspace/bt_3m/v3/code'); import bt
PV={'XAU':100.0,'US500':1.0}
def recon(csv,asset):
    D=bt.table(asset); ix=D.index; low=D.low.values; high=D.high.values; close=D.close.values; spr=D.spread_px.values
    d=pd.read_csv(csv); t=pd.to_datetime(d.time,format='%Y.%m.%d %H:%M:%S').dt.tz_localize('Europe/Athens',ambiguous=False,nonexistent='shift_forward').dt.tz_convert('UTC')
    n=len(ix); pv=PV[asset]; bal0=float(d.balance.iloc[0]-d.profit.iloc[0]-d.swap.iloc[0]-d.comm.iloc[0])
    bi=np.searchsorted(ix.values,t.values,side='right')-1
    ll=lc=sl=sc=0.0; bal=bal0; eqw=np.empty(n); eqc=np.empty(n); balser=np.empty(n)
    ev=list(zip(bi,d.type,d.dir,d.vol,d.price,d.profit,d.balance)); k=0; start=0
    def fl(sl_,h,l,c,sp,s):  # state s=(ll,lc,sl,sc)
        a,b,c_,d_=s; return pv*(a*l-b+d_-c_*(h+sp)), pv*(a*c-b+d_-c_*(c+sp))
    state=(0.0,0.0,0.0,0.0); balc=bal0
    # iterate bars in segments
    ev.append((n,None,None,0,0,0,0)); prev=0
    for (j,tp,dr,vol,price,profit,balafter) in ev:
        j=max(0,min(j,n)); 
        if j>prev:
            sl_=slice(prev,j); w,c=fl(None,high[sl_],low[sl_],close[sl_],spr[sl_],state)
            eqw[sl_]=balc+w; eqc[sl_]=balc+c; balser[sl_]=balc; prev=j
        if tp is None: break
        # apply deal
        a,b,c_,d_=state
        if dr=='in':
            if tp=='buy': a+=vol; b+=vol*price
            else: c_+=vol; d_+=vol*price
        else:
            if tp=='sell': e=price-profit/(vol*pv); a-=vol; b-=vol*e
            else: e=price+profit/(vol*pv); c_-=vol; d_-=vol*e
        state=(max(a,0),b if a>1e-9 else 0.0,max(c_,0),d_ if c_>1e-9 else 0.0); balc=balafter
        if j<n: # same-bar worst includes both states
            w1,c1=fl(None,high[j],low[j],close[j],spr[j],state); eqw[j]=min(eqw[j],balc+w1) if prev>j else balc+w1
    return pd.Series(eqw-bal0,index=ix),pd.Series(eqc-bal0,index=ix),pd.Series(balser-bal0,index=ix)
if __name__=='__main__':
    res={}
    for f in sorted(glob.glob('deals/v3b_*.csv')+glob.glob('deals/v3_*.csv')):
        nm=os.path.basename(f)[:-4]; a='XAU' if ('_x' in nm or nm.startswith('v3_x')) else 'US500'
        w,c,b=recon(f,a); pk=np.maximum.accumulate(c.values); dd=float(np.max(pk-w.values)); 
        res[nm]=dict(asset=a,final=float(c.iloc[-1]),dd_abs=dd,dd_bal=float(np.max(np.maximum.accumulate(b.values)-b.values)))
        print(nm,a,round(c.iloc[-1]),round(dd))
        pd.DataFrame({'ew':w,'ec':c}).to_parquet(f'eq_{nm}.parquet')
    json.dump(res,open('recon.json','w'),indent=1)
