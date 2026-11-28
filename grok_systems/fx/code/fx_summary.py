import sys,glob,json,numpy as np,pandas as pd
sys.path.insert(0,'.'); import fx_select as X
pd.set_option('display.width',250)
out={}
S=pd.concat([pd.read_parquet(f) for f in glob.glob('/workspace/bt_3m/fx/results/screen_*.parquet')]); S['grp']=S.sym.map(X.grp)
q=S[(S.I_n>=80)&(S.O_n>=30)]
out['scalp']=dict(syms=int(S.sym.nunique()),configs=int(len(q)),IS_pos=float((q.I_e>0).mean()),OOS_pos=float((q.O_e>0).mean()),both=float(((q.I_e>0)&(q.O_e>0)).mean()),median_IS_exp_atr=float(q.I_e.median()),median_OOS_exp_atr=float(q.O_e.median()))
t=q[(q.I_e>0)&(q.I_pf>1.15)&(q.I_t>2.0)]; out['scalp']['IS_selected']=int(len(t)); out['scalp']['OOS_positive']=int((t.O_e>0).sum())
for tag in ('bask','pl0','mir'):
    R=X.load(tag); qq,s,o=X.passes(R); g=qq.groupby('grp').apply(lambda d: dict(n=len(d),IS=float((d.netI>0).mean()),OOS=float((d.netO>0).mean()),both=float(((d.netI>0)&(d.netO>0)).mean()))).to_dict()
    out[tag]=dict(syms=int(R.sym.nunique()),configs=int(len(qq)),IS_sel=int(len(s)),OOS_pass=int(len(o)),groups=g,passers=o.sort_values('cO',ascending=False)[['sym','sig','sess','gk','bk','maxN','nb','netI','ddI','netO','ddO']].head(12).round(0).to_dict('records'))
json.dump(out,open('/workspace/bt_3m/fx/results/summary.json','w'),indent=1,default=str)
print(json.dumps({k:{kk:vv for kk,vv in v.items() if kk!='passers'} for k,v in out.items()},indent=1,default=str)[:3500])
