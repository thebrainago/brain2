import numpy as np, pandas as pd, v16

def test_e_he_danh_muc_trong_0_1():
    g = pd.Series(1.0, index=pd.bdate_range("2019-01-01", "2020-12-31"))
    e = v16.e_he("DANH_MUC_4", g); assert e.min() >= 0 and e.max() <= 1 and len(e) == len(g)
    t = v16.e_he("DAU_CUOI_THANG", g); assert set(np.unique(t)) <= {0.0, 1.0}
