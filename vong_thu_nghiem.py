#!/usr/bin/env python3
"""Vòng thí nghiệm tối thiểu (chạy được trên Linux, không cần MT5).

Quét mẫu EA → bóc tách cơ chế → sinh tín hiệu → mô phỏng Python → in kết quả.

Dùng để kiểm tra luồng liên tục trước khi nối với dữ liệu thật và bộ tối ưu.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from nhan import doc_ma as DM
from nhan import ngu_phap as NP
from nhan import mo_phong as MP
from nhan import chi_phi as CP


def du_lieu_gia_lap(n: int = 250, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    price = 1.10 + np.cumsum(rng.normal(0, 0.0015, n))
    idx = pd.date_range("2021-01-01", periods=n, freq="D")
    return pd.DataFrame({
        "open": price,
        "high": price + np.abs(rng.normal(0, 0.0008, n)),
        "low":  price - np.abs(rng.normal(0, 0.0008, n)),
        "close": price + rng.normal(0, 0.0004, n),
        "volume": rng.integers(200, 2000, n),
    }, index=idx)


def chay_mot_file(path: Path, df: pd.DataFrame) -> list[dict]:
    vb = path.read_text(encoding="utf-8", errors="ignore")
    r = DM.doc_chien_luoc(vb, nguon=path.name)
    ket_qua = []
    for spec in r.get("co_che", []):
        try:
            th = NP._dieu_kien(df, spec["vao"], mac_dinh=False).astype(float)
            cp = CP.MoHinhChiPhi(ma="EURUSD")
            kq = MP.chay(df, th, cp, ma="EURUSD", khung="D1")
            ket_qua.append({
                "file": path.name,
                "ten": spec.get("ten"),
                "so_dieu_kien": spec.get("so_dieu_kien"),
                "so_lenh": getattr(kq, "so_lenh", None),
                "phoi_nhiem": round(getattr(kq, "phoi_nhiem", 0), 3),
            })
        except Exception as e:
            ket_qua.append({"file": path.name, "ten": spec.get("ten"), "loi": str(e)})
    return ket_qua


def main():
    df = du_lieu_gia_lap()
    mau = Path("mau_thu")
    tong = []
    for f in sorted(mau.glob("*.mq5")):
        tong.extend(chay_mot_file(f, df))

    print(f"Tổng cơ chế chạy được: {len(tong)}")
    for x in tong:
        print(f"  {x.get('file','?'):45s} {x.get('ten','?'):30s} lenh={x.get('so_lenh')} phoi={x.get('phoi_nhiem')}")


if __name__ == "__main__":
    main()
