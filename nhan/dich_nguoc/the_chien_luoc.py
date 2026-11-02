# -*- coding: utf-8 -*-
"""Xuất kết quả suy luận thành thẻ ứng viên theo hợp đồng có sẵn (nhan/hop_dong.py: TradeHistoryArtifact -> CandidateArtifact)."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from nhan import hop_dong as HD


def _iso(x):
    return str(x).replace(" ", "T") + ("" if "+" in str(x) or str(x).endswith("Z") else "Z")


def tao(df, ket_qua: dict, nguon_url: str, tai_khoan: str = "khong_ro"):
    bay_gio = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    rec = [{"record_id": f"t{i}", "record_type": "position", "occurred_at": _iso(r.mo_luc), "symbol": r.symbol,
            "side": r.chieu, "volume": float(r.lot), "price": float(r.gia_mo)} for i, r in enumerate(df.itertuples())]
    lich_su = HD.TradeHistoryArtifact(source_id="dich_nguoc:" + tai_khoan, source_url=nguon_url, provider="dich_nguoc",
                                      account_ref=tai_khoan, retrieved_at=bay_gio, records=rec)
    tq = ket_qua["tong_quat"]; pb = ket_qua.get("phan_biet") or {}
    top = list((pb.get("dac_trung_xep_hang") or {}).items())[:3]
    tom = (f"Kiểu lot: {tq['lot']['kieu_lot']} (hệ số trung vị {tq['lot']['he_so_lot_trung_vi']}), "
           f"bước lưới trung vị {tq['lot']['buoc_luoi_pip_trung_vi']} pip / {ket_qua.get('buoc_luoi_atr')} ATR, "
           f"hedge={tq['hedge']['co_hedge']}, TP trung vị {tq['tp_sl']['tp_pip_trung_vi']} pip. "
           f"Đặc trưng phân biệt hàng đầu: " + ", ".join(f"{k} (vào {v['vao_trung_vi']} vs ngẫu nhiên {v['ngau_nhien_trung_vi']}, AUC {v['auc_don']})" for k, v in top)
           + f". AUC cây CV5 = {pb.get('auc_cay_cv5', 'CHƯA ĐO ĐƯỢC')}.")
    auc = pb.get("auc_cay_cv5")
    tin = 0.2 if auc is None else max(0.05, min(0.9, (auc - 0.5) * 2))
    the = HD.CandidateArtifact(
        candidate_kind="method", title=f"[Dịch ngược] {tai_khoan}: {tq['lot']['kieu_lot']} trên {', '.join(list(tq['symbol'])[:3])}",
        summary=tom, source_artifact_fingerprints=[lich_su.fingerprint],
        evidence=[{"artifact_fingerprint": lich_su.fingerprint, "quote": f"{tq['so_lenh']} lệnh từ {tq['tu']} đến {tq['den']}",
                   "locator": "records", "note": "suy luận thống kê, không phải mã nguồn gốc"}],
        created_at=bay_gio, tags=["dich_nguoc", tq["lot"]["kieu_lot"]], extractor="nhan.dich_nguoc", extractor_version="1",
        confidence=round(tin, 3), metadata={"suy_luan": json.loads(json.dumps(ket_qua, default=str)), "nguon_url": nguon_url})
    return lich_su, the
