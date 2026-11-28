import sys; sys.argv=[sys.argv[0],'XAU']
import r5lib as R,bt,numpy as np,pandas as pd
D1=bt.table('XAU'); D2=bt.table('US500'); z1=np.zeros(len(D1),np.int64); z2=np.zeros(len(D2),np.int64)
res={}
for n in ('g1','g2','g3','g4','u10','u11','u12','u1','u7'):
    a=R.S[n][0]; D=D1 if a=='XAU' else D2; z=z1 if a=='XAU' else z2
    for lab,fl in (('base',z),('W',R.flat_arr(D,mode=2))):
        o=R.run2(n,D,fl); ec=o['ec']; dd=(np.maximum.accumulate(ec)-o['ew']).max()/o['cap']*100
        res[(n,lab)]=pd.Series(ec,index=D.index).resample('1D').last().diff().fillna(0)
        print(n,lab,'lot',R.REF[n],'net',round(ec[-1]),'dd%',round(dd,1),flush=True)
df=pd.DataFrame({n:res[(n,'W')] for n in ('g1','g2','g3','g4','u10','u11','u12','u1','u7')}).fillna(0)
print(df.corr().round(2))
