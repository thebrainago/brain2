# usage: fx_mkq.py slot name sym sig sess gk bk maxN [name sym ...]   -> entries csv + queue json (EA BRAIN_XuLiLenh_fx, flatten Friday 21:00 server)
import sys,json,copy
sys.path.insert(0,'/workspace/bt_3m/fx/code')
import fx_mt5prep as P, fxlib as F
slot=sys.argv[1]; a=sys.argv[2:]; jobs=[]; exp=[]
base=json.load(open('/workspace/bt_3m/v3/mt5_ready/q_p6v3.json'))['jobs'][0]['params']
for i in range(0,len(a),7):
    name,sym,sig,sess,gk,bk,mN=a[i:i+7]; e,df=P.prep(sym,sig,sess,float(gk),float(bk),int(mN),name); exp.append(e)
    p=dict(base); p.update(dict(InpVao=4,InpTF=16385,InpLot0=1.0,InpNhoi=1,InpBuocGia=0,InpBuocATR=float(gk),InpGianBuoc=1.4,InpKieuLot=0,InpMaxTang=int(mN),InpTPGia=0,InpTPATR=float(bk),InpTuanKhoaGio=21,InpTuanDong='true',InpMagic=2026112990+len(jobs),InpFileLog=f'x_log_{name}.csv',InpFileCsv=f'brain2\\{name}_mt5.csv',InpCsvMa=sym,InpCsvTreGiay=180,InpXuatGia='false'))
    jobs.append(dict(name=name,expert='sp500\\BRAIN_XuLiLenh_fx.ex5',symbol=sym,period='M1',deposit='100000',params=p,desc=f'{sym} {sig} {sess} gap{gk}ATR60 tp{bk}ATR60 N{mN} flatten Fri21',group='fx',**{'from':'2026.06.01','to':'2026.11.27'}))
q=dict(slot=slot,slot_dir=f'E:\\mt5_tester\\{slot}',min_ram_start=10,min_ram_run=6,timeout_min=100,jobs=jobs)
json.dump(q,open(f'{F.FX}/mt5/q_{slot}_fx2.json','w'),indent=1); json.dump(exp,open(f'{F.FX}/mt5/exp_{slot}_fx2.json','w'),indent=1)
