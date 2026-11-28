import pandas as pd, numpy as np, json, sys
pd.set_option('display.width',300); pd.set_option('display.max_columns',50); pd.set_option('display.max_colwidth',60)
a=sys.argv[1]; R=pd.read_parquet(f'../results/battery_{a}.parquet')
def lab(s):
    p=json.loads(s); return (p['a'] if p['kind']=='single' else p['a'][:14]+'+'+p['b'][:14]+f"/W{p['W']}")+f" {p['adx']}/{p['sess']}"
R['lab']=R.prog.apply(lab)
cols=['lab','mg','net','dd_pct','A_net','B_net','npos','minm','sx_net','exness_raw_net','detr_net','rev_net','long_net','short_net','placebo_pct','placebo_med','gapup','delay2_net','nb']
R=R.sort_values('net',ascending=False)
ok=(R.net>0)&(R.so==0)&(R.A_net>0)&(R.B_net>0)&(R.npos>=5)&(R.sx_net>0)&(R.placebo_pct>=95)
print(a,len(R),'pass core',int(ok.sum()))
print(R[ok][cols].round(0).to_string())
print('--- not passing but top net'); print(R[~ok][cols].head(12).round(0).to_string())
