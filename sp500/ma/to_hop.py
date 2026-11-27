# Bo ghep (combiner): chon chan tot -> ghep don/cap/bo ba, danh gia CAGR/DD; chon CHI tren 2017-2021, 2022-2026 la OOS
import os, json, itertools, numpy as np, multiprocessing as mp
from cau_hinh import TAM
import dong_co as E, he
LEV=[2,3,5,8,10]
mid=np.searchsorted(E.days.values,np.datetime64('2022-01-01'))
n1=(E.days[mid-1]-E.days[0]).days/365.25; n2=(E.days[-1]-E.days[mid]).days/365.25
def doc():
    R=[]
    for f in ['luoi.jsonl','luoi2.jsonl','luoi3.jsonl']:
        p=os.path.join(TAM,f)
        if os.path.exists(p): R+=[json.loads(l) for l in open(p)]
    return R
def tinh(o): r,m,n=getattr(he,o['ho'])(E.che_do(o['che_do']),**o['tham_so']); return r,m
def sharpe(r): s=r.std(); return 0 if s==0 else r.mean()/s*np.sqrt(252)
if __name__=='__main__':
    R=doc(); print('tong bien the',len(R))
    ung=[o for o in R if o['lenh_nam']>=8 and o['theo_L'][0]['cagr_17_21']>0]
    print('chan duong o nua dau (L=1):',len(ung))
    with mp.Pool(6) as P: arr=P.map(tinh,ung,chunksize=8)
    sh1=[sharpe(a[0][:mid]) for a in arr]
    chon=[]
    for i in np.argsort(sh1)[::-1]:
        if len(chon)>=25: break
        if all(abs(np.corrcoef(arr[i][0][:mid],arr[j][0][:mid])[0,1])<0.6 for j in chon): chon.append(int(i))
    print('chan duoc chon (Sharpe nua dau, tuong quan<0,6):',len(chon))
    for i in chon: print('  ',ung[i]['ho'],ung[i]['che_do'],ung[i]['tham_so'],'Sh17-21=%.2f'%sh1[i],'Sh22-26=%.2f'%sharpe(arr[i][0][mid:]))
    kq=[]
    for k in (1,2,3):
        for bo in itertools.combinations(chon,k):
            r=sum(arr[i][0] for i in bo)/k; m=sum(arr[i][1] for i in bo)/k
            for L in LEV:
                a=E.ket_qua(r[:mid],m[:mid],L,nam=n1)
                if a['cagr']<=0.10 or a['dd']>=0.8: continue
                b=E.ket_qua(r[mid:],m[mid:],L,nam=n2); t=E.ket_qua(r,m,L)
                kq.append(dict(chan=[f"{ung[i]['ho']}|{ung[i]['che_do']}|{json.dumps(ung[i]['tham_so'])}" for i in bo],L=L,
                    cagr_17_21=round(a['cagr']*100,1),dd_17_21=round(a['dd']*100,1),cagr_22_26=round(b['cagr']*100,1),dd_22_26=round(b['dd']*100,1),
                    cagr=round(t['cagr']*100,1),dd=round(t['dd']*100,1),so_lenh=int(sum(ung[i]['so_lenh'] for i in bo))))
    dat=[x for x in kq if x['cagr_22_26']>10 and x['dd_22_26']<80]
    print('to hop dat o nua dau:',len(kq),' van dat o OOS 2022-2026:',len(dat))
    kq.sort(key=lambda x:-x['cagr_17_21']/max(x['dd_17_21'],5))
    # quy tac chon co dinh truoc: top 1 theo CAGR/DD nua dau cho moi L
    quy_tac={L:next((x for x in kq if x['L']==L),None) for L in LEV}
    json.dump(dict(tong_bien_the=len(R),chan=len(ung),chon=len(chon),to_hop_dat_nua_dau=len(kq),dat_ca_oos=len(dat),
                   chon_top1_nua_dau=quy_tac,top_theo_nua_dau=kq[:40],top_oos=sorted(dat,key=lambda x:-x['cagr_22_26']/max(x['dd_22_26'],5))[:40]),
              open(os.path.join(TAM,'to_hop.json'),'w'),ensure_ascii=False,indent=1)
    print('quy tac top1 nua dau moi L -> OOS:')
    for L,x in quy_tac.items():
        if x: print(L,x['cagr_17_21'],x['dd_17_21'],'| OOS',x['cagr_22_26'],x['dd_22_26'],'|',' + '.join(c[:70] for c in x['chan']))
    print('top 8 xep theo nua dau:')
    for x in kq[:8]: print(x['L'],x['cagr_17_21'],x['dd_17_21'],'| OOS',x['cagr_22_26'],x['dd_22_26'],'|',' + '.join(c[:70] for c in x['chan']))
