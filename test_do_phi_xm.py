import do_phi_xm as D


def test_doc_log(tmp_path):
    f = tmp_path / "log.csv"
    f.write_text("thoi_gian;ma;su_kien;khoi_luong;gia;bid;ask;spread_point;swap;hoa_hong;loi;ibs\n"
                 "2026.10.12 21:00;US500;kiem;0.00;0;5000.00000;5000.50000;50;0;0;0;0.1\n"
                 "2026.10.12 21:00;US500;vao;1.00;5000.60000;5000.00000;5000.50000;50;0.00;0.00;0.00;\n"
                 "2026.10.14 21:00;US500;ra;1.00;5010.00000;5010.00000;5010.50000;50;-2.00;0.00;9.40;\n")
    k = D.tom_tat(D.doc([str(f)]))["US500"]
    assert abs(k["spread_gia_tv"] - 0.5) < 1e-9 and k["lot_dem"] == 2 and abs(k["swap_moi_lot_dem"] + 1.0) < 1e-9
    assert abs(k["truot_vao_gia_tv"] - 0.1) < 1e-6
