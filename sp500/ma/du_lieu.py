# Chuan bi du lieu US500 (HistData SPXUSD BID M5, gio EST co dinh) -> bang ngay phien NY
import os
from cau_hinh import TAM, NGUON_M5
import pandas as pd, numpy as np
d = pd.read_parquet(NGUON_M5)
idx = d.index.tz_localize('Etc/GMT+5').tz_convert('America/New_York')
d.index = idx
d['ngay'] = idx.date
t = idx.hour*60 + idx.minute
d['phut'] = t
rth = d[(t >= 570) & (t < 960)].copy()           # 09:30-16:00 NY
rth.to_parquet(os.path.join(TAM,'rth_m5.parquet'))
g = rth.groupby('ngay')
day = pd.DataFrame({'o': g.open.first(), 'h': g.high.max(), 'l': g.low.min(), 'c': g.close.last(), 'n': g.size()})
day = day[day.n >= 60]
day.index = pd.to_datetime(day.index)
day.to_parquet(os.path.join(TAM,'ngay.parquet'))
print(len(rth), len(day), day.index[0], day.index[-1])
