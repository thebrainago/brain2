# -*- coding: utf-8 -*-
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.ticker import FuncFormatter

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONTB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
fm.fontManager.addfont(FONT); fm.fontManager.addfont(FONTB)
plt.rcParams.update({
    'font.family':'DejaVu Sans','axes.unicode_minus':False,
    'figure.dpi':140,'savefig.dpi':160,'axes.edgecolor':'#333',
    'axes.linewidth':0.6,'axes.grid':True,'grid.color':'#e6e6e6',
    'grid.linewidth':0.6,'axes.axisbelow':True,
})
OUT=Path('/workspace/bt_3m/v3/pdf/fig'); DATA=Path('/workspace/bt_3m/v3/pdf/data')
OFF=json.load(open(DATA/'official_months.json'))
COLS={
    'joint_safe':('#2e7d4f','An toàn'),
    'joint_bal':('#1f4e79','Cân bằng'),
    'joint_agg':('#c05621','Mạnh tay'),
    'joint_man':('#6b5b95','Đánh tay'),
}
THANG=['Thg 6','Thg 7','Thg 8','Thg 9','Thg 10','Thg 11']
KEYS_M=['2026-06','2026-07','2026-08','2026-09','2026-10','2026-11']

def usd(x,pos):
    v=x/1000
    return f'{v:.0f}k'

def load_daily(name):
    d=pd.read_csv(DATA/f'{name}_daily.csv',index_col=0,parse_dates=True)
    if d.index.tz is None:
        d.index=d.index.tz_localize('Asia/Ho_Chi_Minh')
    return d

def style(ax):
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.yaxis.set_major_formatter(FuncFormatter(usd))

# equity joint
fig,ax=plt.subplots(figsize=(10.2,3.55))
for k in ('joint_safe','joint_bal','joint_agg','joint_man'):
    d=load_daily(k); c,lab=COLS[k]
    ax.plot(d.index,d['ec'],color=c,lw=1.8,label=f"{lab}  +{OFF[k]['net']:,.0f} USD  (DD {OFF[k]['dd']:.1f}%)")
ax.set_title('Đường vốn gộp MT5 — vốn 100k, ghép vàng + SP500, 01/06–27/11/2026',fontsize=11,pad=6,loc='left',color='#123')
ax.set_ylabel('Lãi gộp (USD)'); style(ax)
ax.legend(loc='upper left',frameon=False,fontsize=8)
ax.set_xlim(load_daily('joint_bal').index[0], load_daily('joint_bal').index[-1])
fig.text(0.01,0.01,'Nguồn: MT5 100% real ticks, khóa hedge cuối tuần (W) bật cho giỏ. Không phải kết quả live.',fontsize=7,color='#555')
fig.savefig(OUT/'eq_joint100.png',bbox_inches='tight',facecolor='white',pad_inches=0.10)
plt.close()

# monthly joint
fig,ax=plt.subplots(figsize=(10.2,3.15))
x=np.arange(6); w=0.2
for i,k in enumerate(('joint_safe','joint_bal','joint_agg','joint_man')):
    vals=[OFF[k]['months'][m] for m in KEYS_M]
    ax.bar(x+(i-1.5)*w,vals,width=w,color=COLS[k][0],label=COLS[k][1],zorder=3)
ax.axhline(0,color='#333',lw=0.6)
ax.set_xticks(x,THANG); style(ax)
ax.set_ylabel('Lãi theo tháng (USD)')
ax.set_title('Lãi từng tháng (6/6 tháng dương) — số chính thức từ equity MT5 gộp',fontsize=10.5,pad=4,loc='left',color='#123')
ax.legend(ncol=4,loc='upper left',frameon=False,fontsize=8)
fig.text(0.01,0.01,'Nguồn: MT5 100% real ticks. Không phải kết quả live.',fontsize=7,color='#555')
fig.savefig(OUT/'mon_joint100.png',bbox_inches='tight',facecolor='white',pad_inches=0.10)
plt.close()

# equity split
pairs=[('joint_bal','#1f4e79','Ghép vàng + SP500'),
       ('xau_bal','#b8860b','Chỉ vàng (8 hệ)'),
       ('us_bal','#0e7c7b','Chỉ SP500 (5 hệ)')]
fig,ax=plt.subplots(figsize=(10.2,3.55))
for k,c,lab in pairs:
    d=load_daily(k)
    ax.plot(d.index,d['ec'],color=c,lw=1.9,label=f"{lab}  +{OFF[k]['net']:,.0f} USD  (DD {OFF[k]['dd']:.1f}%)")
ax.set_title('Cân bằng, vốn 100k: ghép hai tài sản so với đánh riêng',fontsize=11,pad=6,loc='left',color='#123')
ax.set_ylabel('Lãi gộp (USD)'); style(ax)
ax.legend(loc='upper left',frameon=False,fontsize=8)
ax.set_xlim(load_daily('joint_bal').index[0], load_daily('joint_bal').index[-1])
fig.text(0.01,0.01,'Nguồn: MT5 100% real ticks, vốn 100k mỗi danh mục (tối ưu riêng). Không phải kết quả live.',fontsize=7,color='#555')
fig.savefig(OUT/'eq_split100.png',bbox_inches='tight',facecolor='white',pad_inches=0.10)
plt.close()

# monthly split
fig,ax=plt.subplots(figsize=(10.2,3.15))
x=np.arange(6); w=0.24
for i,(k,c,lab) in enumerate(pairs):
    vals=[OFF[k]['months'][m] for m in KEYS_M]
    ax.bar(x+(i-1)*w,vals,width=w,color=c,label=lab,zorder=3)
ax.axhline(0,color='#333',lw=0.6)
ax.set_xticks(x,THANG); style(ax)
ax.set_ylabel('Lãi theo tháng (USD)')
ax.set_title('Cùng kịch bản Cân bằng: tháng 8 của SP500 yếu, vàng bù — lợi ích ghép chéo',fontsize=10.5,pad=4,loc='left',color='#123')
ax.legend(ncol=3,loc='upper left',frameon=False,fontsize=8)
fig.text(0.01,0.01,'Nguồn: MT5 100% real ticks. Không phải kết quả live.',fontsize=7,color='#555')
fig.savefig(OUT/'mon_split100.png',bbox_inches='tight',facecolor='white',pad_inches=0.10)
plt.close()
print('ok',sorted(p.name for p in OUT.glob('*.png')))
