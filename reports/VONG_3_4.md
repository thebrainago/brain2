# Vòng 3 & Vòng 4 — thiết kế kiểm sâu tiếp theo

Lúc: 2026-10-30 (Asia/Bangkok, UTC+7).  
Mục tiêu vận hành: **~1000 strategy/ngày → ≥5 ứng viên**; vòng 2 nhắm **~50 hệ gốc**.

## Ranh giới các vòng

| Vòng | Đầu vào | Việc làm | Đầu ra | Ai chạy |
|---|---|---|---|---|
| **1** | SEEKER / NGHI / Quantlab | Backtest MT5 1 lần (Model=4 ưu tiên) | `so_cai` PASS/FAIL | `chay_lien_tuc.py` + `hang_cho_mt5.jsonl` |
| **2** | PASS vòng 1 | Lưới tham số ±20–50 %, TF, cặp (#), OOS, xác nhận real-tick | `hang_cho_vong2.jsonl` (`vong=2`) | `tools/vong2.py`; runner khi `BRAIN_VONG2=1` |
| **3** | Survivor vòng 2 (vẫn PASS) | **Tổ hợp danh mục 2–4 hệ** + walk-forward + Monte Carlo + stress spread/slippage/phí | `reports/vong3/*`, việc stress MT5 `vong=3` | `tools/vong3.py` (+ `nhan.vong2.danh_muc_v2` / MC) |
| **4** | Survivor vòng 3 | **Sẵn sàng forward demo** trên **XM demo 345930355 only** — check live-like (symbol #, đòn bẩy, session, lot min, không Exness) | checklist + việc demo `vong=4` | `tools/vong4.py` |

Pass rule (mọi vòng, nhãn): lãi sau phí > 0, max DD ≤ 80 %, ≥ 10 %/năm. FDR/placebo/Holm = nhãn, không cổng.

## Vòng 3 — portfolio + stress (scaffold: `tools/vong3.py`)

1. **Chọn survivor R2**: đọc `so_cai` where `vong=2` (hoặc `pha` ∈ V2_*) và vẫn PASS; tối thiểu 1 xác nhận tick / OOS ổn.
2. **Tổ hợp**: `danh_muc_v2` equal-risk + trọng số đơn giản (1/n, 1/DD, 1/vol ngày); 2–4 hệ; hệ đơn vị đánh giá = **tổ hợp**.
3. **Walk-forward**: 3 đoạn (in / gap / out) trên equity rebuild từ lệnh MT5.
4. **Monte Carlo**: xáo thứ tự lệnh ≥500 đường; phân vị DD / lãi.
5. **Stress MT5** (việc `pha=V3_STRESS`, `vong=3`): spread ×1.5, hoa hồng +2–7 USD/100k, slippage 1–2 pip — tái chạy survivor trên cùng kỳ.
6. Báo cáo: `reports/vong3/VONG3_*.md`.

Chưa merge vào queue live cho đến khi R2 có ≥10 survivor ổn định.

## Vòng 4 — demo forward readiness (scaffold: `tools/vong4.py`)

Chỉ **demo 345930355** (XM, ký hiệu `#`). Không live, không Exness.

Checklist tự động:

- Symbol tồn tại trên demo (`EURUSD#` … `GOLD.i#`)
- Lot min / step / stops level khớp `InpLot0`
- Đòn bẩy báo cáo = cấu hình (1:500)
- Session `InpGioCam*` theo giờ server demo
- Magic / comment tách từng hệ trong tổ hợp
- File CSV tín hiệu (nếu InpVao=4) sync được sang Common\Files
- Không tối ưu lại trên cửa sổ forward; chỉ theo dõi drift DD/APY 2–4 tuần

Đầu ra: `reports/vong4/CHECKLIST_*.md` + việc `pha=V4_DEMO`, `vong=4` (1 lần xác nhận ngắn kỳ trước khi gắn chart).

## Learning loop (đã có)

`python tools/hoc_tu_so_cai.py` → `data/bai_hoc.json` + `reports/BAI_HOC.md` + thẻ `nhan.bai_hoc`.  
`tools/vong2.py` đọc `trong_so` để ưu tiên family/tf/ma thắng. Chạy lại sau mỗi phiên MT5.

## Throughput

| | |
|---|---|
| 6 slot MT5 | ~8–12 phút/job trung bình → ~720–1080 job/ngày |
| Vòng 2 lean (`--gon --top 50`) | ~12–18 job/hệ × 50 ≈ 600–900 việc (giữ slot noãn ½–1 ngày) |
| Kỳ vọng PASS thô | dùng `ti_le_pass` từ BAI_HOC; điều chỉnh `--top` / SEEKER priors để ≥5 ứng viên/ngày |

## Runner / queue

- **Không** ghi `hang_cho_mt5.jsonl` trực tiếp (worker khác sở hữu).
- Vòng 2: `E:\brain2_grok\reports\vong2\hang_cho_vong2.jsonl` + `BRAIN_VONG2=1` (+ optional `BRAIN_VONG2_UU_TIEN=1`).
- Vòng 3/4: `reports/vong3/hang_cho_vong3.jsonl`, `reports/vong4/hang_cho_vong4.jsonl` (cùng schema, `vong=3|4`); sinh_viec mở rộng tương tự khi sẵn sàng.
