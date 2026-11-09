import re,html,sys,json
from datetime import datetime
def num(x): return float(x.replace(' ','').replace('\xa0','')) if x.strip() else 0.0
def doc(path,dep,d0,d1):
    t=open(path,'rb').read().decode('utf-16')
    s=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',t)))
    g=lambda k: re.search(re.escape(k)+r':?\s*([^:]*?)\s{1}(?=[A-Z][a-z])',s)
    net=num(re.search(r'Total Net Profit: ([-\d .]+?) Balance',s).group(1))
    pf=re.search(r'Profit Factor: ([\d.]+)',s).group(1)
    ddm=re.search(r'Equity Drawdown Maximal: ([\d .]+) \(([\d.]+)%\)',s)
    ddr=re.search(r'Equity Drawdown Relative: ([\d.]+)% \(([\d .]+)\)',s)
    q=re.search(r'History Quality: ([^B]+?) Bars',s).group(1)
    tr=int(re.search(r'Total Trades: (\d+)',s).group(1))
    mh=re.search(r'Maximal position holding time: ([\d:]+)',s).group(1)
    hh=mh.split(':'); maxhold=(int(hh[0])+int(hh[1])/60)/24
    # deals table rows
    rows=re.findall(r'<tr[^>]*>(.*?)</tr>',t,re.S)
    deals=[];started=False
    for r in rows:
        c=[html.unescape(re.sub(r'<[^>]+>','',x)).strip() for x in re.findall(r'<td[^>]*>(.*?)</td>',r,re.S)]
        if len(c)>=13 and c[0]=='Time' and c[1]=='Deal': started=True; continue
        if started and len(c)>=13 and re.match(r'\d{4}\.\d\d\.\d\d',c[0]): deals.append(c)
    swap=sum(num(d[9]) for d in deals); comm=sum(num(d[8]) for d in deals); print('so_deal',len(deals),file=sys.stderr)
    lots=0;mx=0;maxpos=0;npos=0
    for d in deals:
        if d[3] not in ('buy','sell'): continue
        v=num(d[5]); 
        if d[4]=='in': lots+=v; npos+=1
        elif d[4]=='out': lots-=v; npos-=1
        mx=max(mx,lots); maxpos=max(maxpos,npos)
    endopen=[d for d in deals if 'end of test' in d[-1].lower()]
    yrs=(datetime.strptime(d1,'%Y-%m-%d')-datetime.strptime(d0,'%Y-%m-%d')).days/365.25
    cagr=((1+net/dep)**(1/yrs)-1)*100 if net>-dep else -100
    # yearly profit by out-deal time
    yp={}
    for d in deals:
        if d[3] in ('buy','sell'): yp[d[0][:4]]=yp.get(d[0][:4],0)+num(d[8])+num(d[9])+num(d[10])
    return dict(file=path,ky=f'{d0}..{d1}',nam=round(yrs,3),chat_luong=q,net=net,cagr_kep_pct=round(cagr,2),
        dd_eq_max=f'{ddm.group(1)} ({ddm.group(2)}%)',dd_eq_rel_pct=float(ddr.group(1)),pf=float(pf),lenh=tr,
        giu_max_ngay=round(maxhold,1),lot_mo_max=round(mx,2),so_vi_the_mo_max=maxpos,swap=round(swap,2),commission=round(comm,2),
        dong_cuoi_test=len(endopen),lai_theo_nam={k:round(v,1) for k,v in sorted(yp.items())},kiem_tong=round(sum(num(d[8])+num(d[9])+num(d[10]) for d in deals if d[3] in ('buy','sell')),1),
        dat=(max(float(ddm.group(2)),float(ddr.group(1)))<80 and cagr>10))
if __name__=='__main__':
    print(json.dumps(doc(sys.argv[1],float(sys.argv[2]),sys.argv[3],sys.argv[4]),ensure_ascii=False,indent=1))
