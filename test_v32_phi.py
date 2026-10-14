import numpy as np
from v30 import nap
from v32_luoi_moc import phi


def test_phi_standard_va_swap():
    df = nap("EURUSD", "H1")
    sp, sw, dem, uoc = phi("EURUSD", df)
    assert not uoc and len(sp) == 24 and (sp > 0).all()
    assert np.all(np.diff(dem) >= 0) and dem[-1] > len(set(df.index.normalize()))  # có đêm ×3
    sp2, _, _, uoc2 = phi("US500", nap("US500", "H1"))
    assert uoc2 and (sp2 > 0).all()
