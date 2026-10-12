import numpy as np, pandas as pd, v24


def test_cum_chat_hon_doc_lap():
    # 50 tuan, moi tuan 20 lenh giong het nhau -> SE cum lon hon SE doc lap
    rng = np.random.default_rng(0); w = rng.normal(0.001, 0.01, 50)
    t = np.repeat(pd.date_range("2020-01-06", periods=50, freq="W-MON"), 20); r = np.repeat(w, 20)
    p, G = v24.p_cum(t, r)
    from scipy.stats import norm
    p_dl = 1 - norm.cdf(r.mean() / (r.std(ddof=1) / np.sqrt(len(r))))
    assert G == 50 and p > p_dl


def test_bps():
    assert v24.bps_of("EURUSD_X") == 1.5e-4 and v24.bps_of("NZDCAD_X") == 4e-4 and v24.bps_of("iGSPC") == 1e-4 and v24.bps_of("NG_F") == 1e-3
