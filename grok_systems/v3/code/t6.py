import p5,time
PA={'x1':0.09,'x2':0.10,'u1':1.0,'u7':1.0}
t=time.time(); r=p5.evalport(PA,p5.POL0); print(time.time()-t,{k:(round(v,1) if isinstance(v,float) else v) for k,v in r.items()})
