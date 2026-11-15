# -*- coding: utf-8 -*-
"""Sinh EvoForward_H4.mq5 (forward demo 2 ung vien H4) tu luat DONG BANG trong nao.db."""
import json, os, sqlite3, sys
from pathlib import Path
GOC = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.insert(0, GOC)
from nhan import dich_mq5 as D, ngu_phap as NP
NP.KHO_CO_CHE = Path(os.environ.get("KHO_DSL", "/workspace/brain2/config/co_che_dsl.json"))
MA = [  # InpMaCoChe 0 = AUDCAD IBS, 1 = EURUSD MOC
 "AUDCAD.H4.mua_ibs_thap_kl_mong_khi_rsi_duoi_phan_vi_thap_atr_vua.vao0_phai_hang0.2_vao1_trai_n100_vao1_phai_hang0.3_vao2_trai_cua_n14_vao2_trai_n100_vao2_phai_hang0.35_vao3_trai_cua_n14_vao3_trai_n250_vao3_phai_hang0.3_vao4_trai_cua_n14_vao4_trai_n250_vao4_phai_hang0.7_ra0_phai_hang0.7_giu4",
 "EURUSD.H4.mat_can_bang_lenh_dong_cua.vao0_phai_hang20_vao1_phai_hang22_vao2_phai_hang0_vao3_trai_cua_n1_vao3_trai_n100_vao3_phai_hang0.8_vao4_trai_n200_vao4_phai_hang0.6_giu2",
]
c = sqlite3.connect("file:/workspace/brain2/nao.db?mode=ro", uri=True)
kho = {s["ten"]: s for s in NP.doc_kho()}
specs = []
for m in MA:
    t, ts = c.execute("SELECT template, tham_so FROM gia_thuyet WHERE ma=?", (m,)).fetchone()
    specs.append(dict(NP.ap_tham_so(kho[t], json.loads(ts or "{}")), ten=m))
ma, dat = D.sinh_ea(specs, "EvoForward_H4", khung="H4", them_mua_giu=False)
assert len(dat) == 2, [s.get("_khong_dich") for s in specs]
open(os.path.join(os.path.dirname(__file__), "EvoForward_H4.mq5"), "w", encoding="utf-8").write(ma)
print("ok", [d["ten"][:40] for d in dat])
