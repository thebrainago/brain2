from nhan.nang_lot import (phat_lai_co_dinh, phat_lai_lai_kep, xap_xi_tuyen_tinh, tim_k, dat, doc_deals_htm, cagr_pct)


def test_co_dinh_k1_khop_net():
    kq = phat_lai_co_dinh(1000, [100, -50, 150], 1, 2)
    assert abs(kq["cagr"] - cagr_pct(1200, 1000, 2)) < 1e-9
    assert abs(kq["dd"] - 50 / 1100 * 100) < 1e-9 and not kq["chay"]


def test_co_dinh_nhan_k_va_chay():
    kq = phat_lai_co_dinh(1000, [100, -50, 150], 3, 2)
    assert abs(kq["cagr"] - cagr_pct(1600, 1000, 2)) < 1e-9
    assert phat_lai_co_dinh(1000, [100, -600], 2, 1)["chay"]  # 1200 -> 0 = cháy


def test_lai_kep():
    kq = phat_lai_lai_kep(1000, [0.1, -0.05], 2, 1)
    assert abs(kq["cagr"] - (1.2 * 0.9 - 1) * 100) < 1e-9
    assert phat_lai_lai_kep(1000, [-0.6], 2, 1)["chay"]


def test_xap_xi():
    kq = xap_xi_tuyen_tinh(500, 1000, 5, 10, 4)
    assert abs(kq["dd"] - 40) < 1e-9 and abs(kq["cagr"] - cagr_pct(3000, 1000, 5)) < 1e-9
    assert xap_xi_tuyen_tinh(500, 1000, 5, 30, 4)["chay"]


def test_tim_k():
    kc, kd, kdat, _ = tim_k(lambda k: xap_xi_tuyen_tinh(200, 1000, 4, 10, k))
    assert kc == min(kdat) and kd == max(kdat) and kd < 8 and kc > 1
    assert all(dat(xap_xi_tuyen_tinh(200, 1000, 4, 10, k)) for k in kdat)
    assert tim_k(lambda k: xap_xi_tuyen_tinh(-100, 1000, 4, 10, k))[2] == []


def test_doc_deals():
    row = "<tr><td>{}</td><td>1</td><td>X</td><td>buy</td><td>out</td><td>0.1</td><td>1</td><td>1</td><td>0.00</td><td>0.00</td><td>{}</td><td>{}</td><td></td></tr>"
    h = "<table>" + row.format("2024.01.01 00:00:00", "10 000.00", "10 000.00") + row.format("2024.01.02 00:00:00", "50.00", "10 050.00") + "</table>"
    von, pnl = doc_deals_htm(h.encode("utf-16"))
    assert von == 10000 and pnl == [50]
