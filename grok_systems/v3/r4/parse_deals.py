# stdlib only: parse MT5 tester htm deals -> csv (time,type,dir,vol,price,swap,comm,profit,balance). Run on PC.
import re,sys,os,glob,csv
src=sys.argv[1]; dst=sys.argv[2]; pat=sys.argv[3]; os.makedirs(dst,exist_ok=True)
for f in glob.glob(os.path.join(src,pat+'.htm')):
    b=open(f,'rb').read(); t=b.decode('utf-16') if b[:2] in (b'\xff\xfe',b'\xfe\xff') else b.decode('utf-8','ignore')
    rows=re.findall(r'<tr[^>]*>(.*?)</tr>',t,re.S); out=[]
    for r in rows:
        c=[re.sub(r'<[^>]+>','',x).replace('\xa0','').replace(' ','').strip() for x in re.findall(r'<td[^>]*>(.*?)</td>',r,re.S)]
        if len(c)==13 and re.match(r'\d{4}\.\d\d\.\d\d\d\d:\d\d:\d\d',c[0]) and c[4] in('in','out'):
            out.append([c[0][:10]+' '+c[0][10:],c[3],c[4],c[5],c[6],c[9],c[8],c[10],c[11],c[2]])
    with open(os.path.join(dst,os.path.basename(f)[:-4]+'.csv'),'w',newline='') as g:
        w=csv.writer(g); w.writerow(['time','type','dir','vol','price','swap','comm','profit','balance','sym']); w.writerows(out)
    print(os.path.basename(f),len(out))
