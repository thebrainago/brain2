# Ống dẫn một lệnh: từ kho Seeker tới MT5 và kho cơ chế (18/10/2026)

Mã: `nhan/ong_dan.py` (các bước) và `ong_dan.py` ở gốc (lệnh gọi). Trạng thái lưu trong `data/ong_dan/trang_thai.sqlite`. File này git bỏ qua. Mọi con số ở bước Python là **MÔ PHỎNG**. Phí là **PHÍ TẠM** cho tới khi máy nhà đo `reports/phi_san/`.

## Sơ đồ chuỗi

```
 data/cau_kho/ea_ra_co_che (EA MQL)   reports/KHO_*.json (kho GitHub đã kiểm kê)   EA BRAIN_XuLiLenh (MRZ/RSI/Donchian)
                 \                               |                                   /
                  +--------------------- (a) nhan --------------------------------+
                                                 ^
             THƯ MỤC NHẬP TAY (E:\brain2_nhap\, data/nhap_tay/, data/seeker_da_nguon/nhap_tay/): chủ dự án tự mở
             trang bị chặn bằng Chrome của mình, lưu EA / .set / statement / CSV lịch sử lệnh / trang HTML / .zip
                                                 |
                       (b) phan_loai: hệ hoàn thiện (0-3) > cơ chế (4) > tiện ích (6) > mô tả (8)
                                                 |
       (c) quyet_dinh:  noi_bo (BRAIN) | spec_dsl (dịch MQL không cần LLM) | llm (Python/Pine, cần khoá) | mt5_truc_tiep | bo_qua
                                                 |
       (d) toi_uu: grid/ngẫu nhiên có ngân sách trên tham số tín hiệu × quản lí (TP nhỏ, DCA, hedge, lot thật) × mã × khung
           engine: nhan/tai_khoan.chay_tk (lot thật, ký quỹ, stop-out, spread theo giờ, swap mua/bán, ×3, hoa hồng)
           OOS 30 % cuối chỉ là NHÃN
                                                 |
       (e) loc: sụt giảm < 65 % VÀ lãi > 15 %/năm, không chạm stop-out (config/nguong.json, tầng "loc_python")
              /                                                            \
        ĐẠT                                                               TRƯỢT
         |                                                                   |
 (f) sinh_mt5: .set + .ini (KIEM: Optimization=0;              (g) boc: tách nguồn lệnh / bộ lọc / mốc-vùng /
     TOI_UU: Optimization=1 hoặc 2, có khoảng tham số)             quản lí / gỡ lệnh -> data/kho_co_che/kho.sqlite
     -> reports/ong_dan/hang_cho_mt5.jsonl                         + reports/KHO_CO_CHE_TICH_LUY.md
         |                                                                   |
   máy nhà: mt5tools/chay_lien_tuc.py                      (h) to_hop: nguồn A [+ bộ lọc] + quản lí/gỡ [+ nguồn B gỡ chéo]
         |                                                     -> lọc 65/15 -> ĐẠT thì quay lại (f)
 (i) doc_mt5: sổ cái + reports/ong_dan/ket_qua_mt5/*.htm|*.xml -> chuẩn cuối 80/10 ở lot thật -> DAT_CUOI / TRUOT_CUOI
```

## Thư mục nhập tay (trang bị chặn)

Máy **không** vượt Cloudflare, captcha hay chặn bot, và **không** dùng Browser MCP, CDP hay cách nào khác để lách. Chủ dự án tự mở trang và lưu file vào thư mục nhập tay. Ống dẫn chỉ đọc văn bản, không bao giờ chạy mã được nhập vào.

- **Thư mục:**
  - Biến môi trường `BRAIN_NHAP_TAY`, nhiều thư mục cách nhau bằng `;`.
  - Nếu không đặt biến thì dùng `thu_muc_nhap_tay` trong `config/ong_dan.json`. Mặc định: `E:\brain2_nhap`, `data/nhap_tay` và `data/seeker_da_nguon/nhap_tay` (quy ước của tác vụ Seeker đa nguồn, chỉ đọc).
- **Danh sách trang cần mở:**
  - `reports/URL_BI_CHAN.md` (tác vụ Seeker đa nguồn).
  - `reports/URL_BI_CHAN_THEM.md`, do `python tru/seeker.py url-bi-chan` sinh, và được tự chạy ở cuối `ong_dan.py chay`. File này gom tên miền bị chặn, các bản `khong_doc_duoc` trong nao.db, và ứng viên chỉ có URL. Trang trả phí đã bị loại.
  - Đặt tên file bắt đầu bằng mã của dòng (`U1a2b3c_...` hoặc id ở cột đầu) thì dòng đó được đánh dấu ĐÃ NHẬP.
- **Cách đọc từng loại** (`nhan/nhap_tay.py`):
  - `.mq4/.mq5` → thẻ EA, kèm `.set` cùng tên nếu có. EA nhập tay được ưu tiên 0, ngang EA BRAIN.
  - `.ex4/.ex5` → chạy thẳng MT5.
  - `.set` riêng lẻ → cơ chế quản lí (mô tả).
  - `.htm` (statement MT4 hoặc báo cáo MT5) và `.csv` (xuất lịch sử lệnh từ MQL5 Signals, Myfxbook, FX Blue…) → danh sách lệnh vào, cùng dấu hiệu DCA / martingale / hedge suy từ các lệnh chồng nhau. Lệnh được đưa vào Python làm **nguồn lệnh** rồi gắn quản lí theo phong cách chủ dự án (tối ưu trên mã box có giá).
  - Trang `.html` lưu tay → tách khối mã MQL (OnTick / OnInit) ghi vào `data/nhap_tay/_tach/`. Không có mã thì ghi là mô tả.
  - `.pine/.py` → đường LLM.
  - `.zip` → chỉ giải nén các đuôi trên, bỏ đường dẫn `..` và file thực thi.

## Lệnh

| Việc | Lệnh |
|---|---|
| Chạy hết các bước a → i, chạy tiếp được nếu bị dừng | `python3 ong_dan.py chay [--toi-da 10 --ngan-sach 40 --ngan-sach-to-hop 40]` |
| Từng bước | `python3 ong_dan.py nhan` · `phan_loai` · `quyet_dinh` · `toi_uu [--id <thẻ>]` · `loc` · `sinh_mt5` · `boc` · `to_hop` · `doc_mt5` |
| Xem trạng thái / ghi báo cáo | `python3 ong_dan.py trang_thai` · `python3 ong_dan.py bao_cao` (ghi `reports/ong_dan/TRANG_THAI.md`) |
| Dùng CSDL khác (thử) | `--db /tmp/x.sqlite` |

Cấu hình nằm ở `config/ong_dan.json`: dữ liệu giá mỗi mã, khung, tài khoản tạm, vốn, ngân sách và mẫu tên symbol theo sàn. Ngưỡng nằm ở `config/nguong.json`. Mỗi lần `chay` tối ưu thêm tối đa `toi_da_the_moi_lan` thẻ, mỗi thẻ `ngan_sach_moi_the` phép thử. Thẻ nào đã đủ phép thử thì không chạy lại. Phép thử nào đã lưu thì không tính lại.

## Hàng chờ MT5 và máy nhà

- `reports/ong_dan/hang_cho_mt5.jsonl` có hai loại việc:
  - Việc `ea=XL` (EA `BRAIN_XuLiLenh`) được `mt5tools/sinh_viec.py` (`tu_ong_dan`) đưa vào hàng chờ của `mt5tools/chay_lien_tuc.py`. Điểm ưu tiên là 60+, sau OOS và trên bước tìm thông số.
  - Việc `ea=NGOAI` là EA của người khác: chạy một lần để xuất danh sách lệnh, phải tải mã theo URL trước. Loại này **không** tự chạy.
- `reports/ong_dan/viec_mt5/<thẻ>/` có `.set` và `.ini` để chạy tay. Thẻ nào chưa có EA biểu đạt được (nguồn lệnh ngoài, có bộ lọc hoặc ghép hai nguồn) thì có `CAN_EA_GHEP.md`.
- Các mức chuyển từ Python sang EA:
  - TP và bước DCA tính bằng % × giá tham chiếu (trung vị 2.000 nến cuối) → `InpTPGia` / `InpBuocGia`.
  - `InpMarginMin=0` để khớp với Python.
  - Giờ cấm đổi ngày lấy theo sàn: XM 23 → 2, Exness (GMT+0) 20 → 0.
- Máy nhà cần làm:
  1. `git pull` rồi biên dịch `ea_demo/BRAIN_XuLiLenh.mq5` vào `MQL5\Experts\BRAIN\` của từng slot.
  2. Đặt `BRAIN_SAN_TESTER=XM` (hoặc `Exness`) để slot chỉ nhận việc của sàn đã đăng nhập. Tài khoản tester phải là **hedging** (EA mở lệnh khoá ngược chiều).
  3. Chạy `python mt5tools/chay_lien_tuc.py --den 07:00`.
     - Kết quả `.htm` và `.xml` của việc ống dẫn được chép vào `reports/ong_dan/ket_qua_mt5/`.
     - Lúc hết hạn, các kết quả này được commit cùng sổ cái.
     - Việc tối ưu được chạy tối đa 6 giờ.
  4. Trên box hoặc máy nhà: `python3 ong_dan.py doc_mt5` để chấm theo chuẩn cuối 80/10.
- **Khi đã đo phí** (`python mt5tools/do_phi_san.py` trên tài khoản Exness cent và XM micro, ra `reports/phi_san/<server>/`):
  - Không phải sửa code. `tai_khoan.ho_so_phi` và `ho_so_tai_khoan` tự dùng `ma.csv`, `spread_gio.csv` và `san.json`, rồi đổi nhãn thành "ĐO".
  - Symbol thật lấy từ `ma_san.json`.
  - Xoá `data/ong_dan/trang_thai.sqlite` (hoặc dùng `--db` mới) rồi chạy lại `python3 ong_dan.py chay`, để mọi phép thử được tính lại với phí thật.

## LLM

`nhan/cau_llm.py` dùng chung kiểu gọi với `phong_hop`.
- Khoá lấy từ biến môi trường: `AIBOX_API_KEY`, `AIBOX_BASE_URL` và `BRAIN_LLM_MODEL` (tuỳ chọn).
- Không có khoá thì thẻ Python / Pine ở trạng thái `LLM` và được ghi **CHƯA CHẠY ĐƯỢC**, không gọi mạng.
- Mã MQL đơn giản đi đường không cần LLM (`doc_ma.doc_chien_luoc`).

## Giới hạn hiện tại

- Thư mục nhập tay `E:\brain2_nhap` nằm trên máy nhà. Box chỉ thấy `data/nhap_tay/` (git bỏ qua, vì mã của người khác không vào git). Muốn chạy trên box thì chép file sang, hoặc chạy `ong_dan.py` ngay trên máy nhà.

- Box chỉ có giá AUDCAD 2016–2026. EURGBP và NZDUSD chỉ có từ 01/2024 (2,77 năm), nên số trên hai mã này dao động mạnh.
- Engine Python tách lệnh vượt `lot_max` thành nhiều lệnh. EA hiện chặn ở `lot_max` (`ChuanLot`). Với rổ lớn, MT5 sẽ khoá ít hơn Python.
- Tổ hợp có bộ lọc hoặc nguồn ngoài chưa có EA chạy được. Cần chế độ "đọc CSV lệnh" của `BRAIN_XuLiLenh` (bước 7a của bản rà soát).
