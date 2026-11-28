import sys,os,json,itertools,p5,r5lib as R
PORTS={'PortA':{'x1':0.09,'x2':0.10,'u1':1.0,'u7':1.0},
 'PortB85':{'x1':0.04,'x4':0.06,'xs1':0.48,'xs2':0.85,'u1':2.2,'u2':0.17,'u6':1.4,'u7':4.25},
 'NEW4':{'g1':0.12,'g2':0.12,'u10':2.5,'u11':2.0},
 'PortD0':{'x1':0.05,'x4':0.05,'g1':0.10,'g2':0.10,'xs1':0.48,'xs2':0.85,'u1':2.2,'u7':3.0,'u10':2.0,'u11':1.5,'u6':1.0,'u2':0.17}}
nm=sys.argv[1]; f=f'{R.R5}/pol_{nm}.json'
res=json.load(open(f)) if os.path.exists(f) else {}
for fm,hsk,hs,dl,mn in itertools.product((0,2),(0,1,2),(0,8,12),(0,4,6,8),(0,1)):
    key=f'{fm}|{hsk}|{hs}|{dl}|{mn}'
    if key in res: continue
    pol=dict(flat=fm,hsk=float(hsk),hs=float(hs),dl=float(dl),minusN=mn)
    r=p5.evalport(PORTS[nm],pol); res[key]={k:v for k,v in r.items()}
    if len(res)%12==0: json.dump(res,open(f,'w'),default=float)
json.dump(res,open(f,'w'),default=float); print('POL DONE',nm)
