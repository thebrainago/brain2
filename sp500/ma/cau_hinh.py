# Duong dan dung chung cho module sp500 (doi bang bien moi truong)
import os
TAM = os.environ.get('SP500_TAM', '/workspace/sp500_2711')          # thu muc tam (parquet, jsonl lon) - KHONG commit
NGUON_M5 = os.environ.get('SP500_M5', '/workspace/quet_intraday/m5/spxusd.parquet')  # HistData SPXUSD BID M5
os.makedirs(TAM, exist_ok=True)
