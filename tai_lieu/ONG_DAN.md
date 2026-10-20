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
- `reports/ong_dan/viec_mt5/<thẻ>/` có `.set` và `.ini` để chạy tay. Thẻ nào chưa có EA biểu đạt được (nguồn lệnh ngoài, có bộ lọc hoặc ghép hai nguồn) thì có `CAN_EA_GHEP.md`, kèm CSV lệnh vào cho chế độ VAO_CSV (xem mục dưới).
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

## Chế độ VAO_CSV: EA đọc lệnh vào từ CSV (19/10/2026)

Chế độ này dành cho các thẻ `CHO_EA_GHEP`: hệ đạt lọc Python nhưng tín hiệu không viết được bằng MRZ / RSI / Donchian của EA. Đó là nguồn lệnh ngoài, hệ có bộ lọc, hoặc tổ hợp.

- **Python xuất** (`python3 ong_dan.py sinh_mt5`), mỗi thẻ và mỗi sàn có:
  - `viec_mt5/<thẻ>/od_<thẻ>_<sàn>_CSV_vao.csv`, gồm các cột `thoi_gian,ma,chieu,gia,nguon,lot`.
    - `thoi_gian` là giờ mở nến vào lệnh, tính theo giờ server của sàn. XM giữ nguyên giờ box (NY+7). Exness đổi sang GMT.
    - `gia` là giá BID tham khảo (open nến). `lot` là lot tầng đầu.
    - File ASCII, xuống dòng CRLF, sắp theo thời gian.
  - `.set` và `.ini` cùng tên.
    - `.set` dùng `InpVao=4` và tham số quản lí theo % giá, khớp `chay_tk`: `InpTPPct`, `InpBuocPct` (mức DCA cố định tính từ giá lệnh đầu), `InpTrailKichPct`, `InpTrailKhoangPct`, `InpMoKhoaPct`.
    - Có thêm `InpKhoaLaiKhongMoc=true`, `InpMarginMin=0` và giờ cấm theo sàn.
  - Một việc trong hàng chờ: `ea=XL`, `pha=KIEM_CSV`, có `csv_vao` và `python_ql`. Hàm `tu_ong_dan` của máy nhà tự nhận việc này.
- **EA** (`ea_demo/BRAIN_XuLiLenh.mq5` 1.10):
  - Đọc toàn bộ CSV lúc `OnInit`, từ `Common\Files` nếu `InpCsvChung=true` (cách tester đọc được), không thì từ `MQL5\Files`.
  - Mở rổ ở tick đầu tiên có thời gian ≥ `thoi_gian`.
    - Đang có rổ cùng chiều thì bỏ dòng, giống `mot_ro_moi_chieu`.
    - Trễ quá `InpCsvTreGiay` (mặc định một nến) thì bỏ dòng.
    - Gặp giờ cấm hoặc thị trường đóng thì thử lại ở tick sau.
  - Quản lí lệnh giữ nguyên: DCA, nhồi, trailing, hedge khoá / gỡ, TP rổ.
    - Mỗi lệnh mang tag tầng `XL_B#k`.
    - Lãi / lỗ đã chốt của lệnh khoá được cộng vào khi tính gỡ, giống `r.tich` của Python.
  - Lệnh vượt `SYMBOL_VOLUME_MAX` được tách thành nhiều lệnh, tối đa 50.
  - Khi chạy, EA ghi `<csv>_lenh_mt5.csv` (từng deal, có position id). Lúc `OnDeinit`, EA ghi `<csv>_gia.csv` (nến InpTF trong kỳ test, có spread).
- **Máy nhà** (`chay_lien_tuc.py`):
  - Trước khi chạy, chép CSV lệnh vào sang `%APPDATA%\MetaQuotes\Terminal\Common\Files`.
  - Chạy xong, chép `_lenh_mt5.csv` và `_gia.csv` về `reports/ong_dan/ket_qua_mt5/`, cùng chỗ với `.htm`.
- **Đối chiếu** (`python3 ong_dan.py doc_mt5`, kết quả ở `reports/ong_dan/DOI_CHIEU_MT5.md`):
  - Python chạy lại `chay_tk` trên **cùng CSV** và **cùng giá**, tức là nến EA xuất.
    - Spread theo giờ lấy từ nến EA. Thiếu nến thì dùng giá box và ghi "GIÁ KHÁC NGUỒN".
    - Phía Python dùng một nguồn chung và không gỡ chéo, giống EA.
  - Ghép 1-1 lệnh Python với position MT5 khi đủ cả bốn điều kiện:
    - cùng chiều và cùng loại (rổ hay khoá);
    - giờ mở lệch ≤ 1 nến;
    - giá mở lệch ≤ 3 × spread + 0,05 % giá;
    - lot lệch ≤ 1 bước.
  - Kết luận **KHOP** khi có ≥ 95 % lệnh ghép được và tổng lãi / lỗ lệch ≤ 10 %, hoặc ≤ 1 % vốn. Không đạt thì kết luận **LECH** và ghi lí do.
  - Báo cáo có trung vị độ lệch của nến mở, giá mở, nến đóng và lãi từng lệnh.
  - Tài khoản cent (USC) được chia 100 để quy về USD.
  - Sai số đặt ở `SAI_SO` trong `nhan/ong_dan.py`.

## LLM: bước dịch chạy trên máy nhà (19/10/2026)

Khoá ai-box chỉ có trên máy nhà. Box **không** giữ khoá, không đọc và không chép khoá; trên box, bước dịch báo CHƯA CHẠY ĐƯỢC và không gọi mạng.

- **Lấy khoá** (`nhan/cau_llm.py`, làm theo `qwen/cau_hinh.py` và `qwen/mo_hinh.py`), theo thứ tự:
  1. biến môi trường `AIBOX_API_KEY`;
  2. `~/.cc-switch/cc-switch.db`, provider có tên chứa `aibox`, mở chỉ đọc;
  3. proxy cloud `BRAIN_LLM_PROXY`.

  Khoá chỉ nằm trong bộ nhớ. Khoá không được in ra, và bị che (`***`) trong mọi thông báo lỗi.
- **Tham số** lấy từ `config/qwen.json`, thiếu thì lấy từ `config/tri_tue.json`:
  - model chính `qwen3.7-flash`, model dự phòng `qwen3.6-flash`;
  - `temperature` 0, `max_tokens`, `timeout_giay`, `so_lan_thu_lai`.

  Gặp lỗi 403, 402, hoặc 429 do hết quota thì chuyển sang model dự phòng. Lỗi tạm thời (5xx, mạng) thì thử lại.
- **`python ong_dan.py dich_llm [--gioi_han N] [--luong K]`** (`nhan/dich_llm.py`):
  - Hàng chờ gồm thẻ đường `llm` (Python, freqtrade, Pine) và EA MQL mà bộ dịch không-LLM bỏ qua ("bo dich khong ra chan"). Thứ tự: 28 hệ top của Seeker trước, rồi thẻ LLM, rồi EA.
  - Mỗi mã nguồn chỉ gọi LLM một lần. Cache theo sha256 của mã lưu ở `data/ong_dan/dich_llm/<hash>.json`. Nhiều thẻ cùng mã dùng chung một lần gọi.
  - LLM trả về spec DSL, hoặc khi spec không diễn đạt được thì trả hàm Python `tin_hieu(df)`. Kết quả được kiểm tự động trên giá mẫu (3.000 nến H1 cuối của mã đầu tiên có giá):
    - dạng đúng, giá trị trong {-1, 0, 1};
    - **không nhìn trước**: tín hiệu tính trên df[:k] với k = 50 %, 70 %, 90 % phải trùng tín hiệu tính trên toàn bộ;
    - ra ít nhất 3 lệnh.
  - Mã Python chạy trong hộp cát (`nhan/hop_cat_llm.py`):
    - kiểm AST trước: cấm import, cấm tên hay thuộc tính bắt đầu bằng `_`, cấm open/exec/eval/getattr, cấm đọc/ghi file của pandas, cấm shift âm;
    - chạy trong tiến trình con với biến môi trường rỗng (không có khoá), giới hạn thời gian và bộ nhớ, builtins rút gọn.
  - Thẻ đạt kiểm được đưa về bước `quyet_dinh` với đường `spec_dsl` hoặc `python_llm`, để `toi_uu` và `loc` chạy tiếp. Hệ đạt lọc sau đó chạy MT5 bằng VAO_CSV.
  - Thẻ không đạt được ghi lí do vào thẻ (`dich_llm`). Lỗi LLM thì lần sau gọi lại.
  - Số lần gọi, token vào/ra và số lần chuyển sang model dự phòng được ghi ở `reports/ong_dan/DICH_LLM.md` và `data/ong_dan/dich_llm/nhat_ky.jsonl`.
- Bước `quyet_dinh` không gọi LLM nữa: thẻ Python/Pine chỉ được đánh dấu chờ `dich_llm`.
- **Máy nhà chạy theo thứ tự**:
  1. `git pull`;
  2. giải nén `goi_ea_ngoai_<ngày>.zip` vào gốc repo. Gói có mã nguồn các thẻ chờ dịch, bản chụp `data/ong_dan/trang_thai.sqlite`, cache dịch và giá H1 ở `data/ong_dan/gia_goi/`;
  3. `python ong_dan.py dich_llm` (chạy thử trước bằng `--gioi_han 50`);
  4. `python ong_dan.py chay`;
  5. commit `reports/` rồi push. `data/` không vào git.
- Khi không có file giá gốc của box, `gia()` tự đọc `data/ong_dan/gia_goi/<MA>_H1.csv.gz`. Bước `goi` chỉ chạy trên box.

## Giới hạn hiện tại

- Thư mục nhập tay `E:\brain2_nhap` nằm trên máy nhà. Box chỉ thấy `data/nhap_tay/` (git bỏ qua, vì mã của người khác không vào git). Muốn chạy trên box thì chép file sang, hoặc chạy `ong_dan.py` ngay trên máy nhà.

- Box chỉ có giá AUDCAD 2016–2026. EURGBP và NZDUSD chỉ có từ 01/2024 (2,77 năm), nên số trên hai mã này dao động mạnh.
- Từ 19/10/2026, cả Python và EA đều tách lệnh vượt `lot_max` / `SYMBOL_VOLUME_MAX` thành nhiều lệnh, tối đa 50 lệnh.
- Hệ ghép hai nguồn có gỡ chéo chỉ chạy được **gần đúng** ở VAO_CSV, vì EA gộp một rổ mỗi chiều và chưa gỡ chéo giữa các nguồn. Phần đối chiếu ghi chú "GẦN ĐÚNG" cho các hệ này.
- EA ở chế độ VAO_CSV **CHƯA BIÊN DỊCH**. Box không có MetaEditor và không có công cụ kiểm tra cú pháp MQL5; chỉ kiểm được ngoặc cân.

## Nguồn Seeker đa nguồn (19/10/2026)

- `python3 ong_dan.py nhan` đọc thêm `reports/SEEKER_DA_NGUON.json` cùng mã đã tải trong `data/seeker_da_nguon/tai_ve/`, qua bộ đọc `nhan/doc_seeker_da_nguon.py` (chỉ đọc, không chạy mã). Với mỗi ứng viên:
  - mỗi EA `.mq4`/`.mq5` có OnTick thành một thẻ (tối đa 12 EA, riêng 28 hệ top là 40), kèm các `.set` cùng tên hoặc cùng thư mục;
  - mỗi `.ex4`/`.ex5` không có mã thành một thẻ chạy thẳng MT5;
  - mỗi statement hoặc báo cáo tester (`.htm`, `.html`, `.csv`) có danh sách lệnh thành một thẻ STATEMENT, kèm kết quả dò ngược;
  - mã Python hoặc Pine sang đường LLM;
  - ứng viên không có file thành một thẻ ứng viên.
  - Bỏ các ứng viên trả phí.
  - `bang_chung_lai` của Seeker được giữ trong `so_tac_gia` (SỐ TÁC GIẢ, chưa đo), không trộn với số mô phỏng.
- Ưu tiên 0: 28 hệ top trong `SEEKER_DA_NGUON.md` và mọi statement có từng lệnh.
- Đọc được báo cáo tester MT4, statement MT4 và báo cáo MT5 (`ReportTester-*.html`, kể cả bản tiếng Tây Ban Nha, Nga, Trung). Dò ngược (`nhan/nhap_tay.do_nguoc`) cho ra:
  - bước DCA (pip và %), kèm tỉ lệ bước đi ngược giá;
  - hệ số lot;
  - TP rổ;
  - số tầng;
  - giờ mở lệnh;
  - mã.

  Kết quả có nhãn SUY TỪ STATEMENT. Kết quả nằm ở `reports/ong_dan/DO_NGUOC_STATEMENT.md` (`python3 ong_dan.py do_nguoc`). Quản lí dò ngược được dùng làm phép thử Python đầu tiên, chạy trong đúng khoảng thời gian của statement.
- Lọc 65/15 cần ít nhất 1 năm dữ liệu (`nam_du_lieu_toi_thieu`). Nếu ít hơn thì ghi CHƯA ĐO ĐƯỢC.
- Giá trên box gồm 26 mã:
  - AUDCAD từ 2016;
  - NZDUSD từ 2018;
  - còn lại từ 2024-01 (HistData M5, gộp H1, cache trong `data/ong_dan/gia_h1/`).
- Hợp đồng mỗi lot lấy theo `contract_size` đã đo (GOLDmicro là 1, SILVERmicro là 50).
- Việc MT5 cho EA ngoài (`ea=NGOAI`):
  - mỗi `.set` có sẵn thành một việc: `CHAY_SET`, hoặc `TOI_UU_SET` nếu `.set` có cờ `||Y`; mã và khung lấy từ tên `.set` và `Timeframe=`;
  - EA không có `.set` thành một việc `XUAT_LENH`.
  - Trường `tep_box` và `set_box` ghi đường dẫn trong `data/` trên box.
- Gói cho máy nhà: `python3 ong_dan.py goi` tạo `/workspace/goi_may_nha/goi_ea_ngoai_<ngày>.zip`, nằm ngoài git. Gói giữ nguyên cấu trúc `data/...`, kèm các `.mqh` được `#include`, `MANIFEST.json` và `HUONG_DAN.md`. Giải nén vào gốc repo trên máy nhà.
- Chạy nền theo đợt ngắn, chạy tiếp được: `nohup bash chay_nen_ong_dan.sh "12 16 20" 30 > /dev/null 2>&1 &`, log ghi vào `data/ong_dan/nen.log`. `toi_uu --lam-lai` mở lại các thẻ còn thiếu phép thử. Bị ngắt thì chạy lại đúng lệnh đó.

## Bộ điều phối tài nguyên máy nhà (20/10/2026)

`may_nha_toi_nay/dieu_phoi_may_nha.py` được `vong_phien.ps1` (bước 12 của `chay_toi_nay.ps1`) khởi động. Nó xoay vòng ba loại việc, mỗi chu kỳ `chu_ky_giay` (60 giây):

| Việc | Tài nguyên | Khi nào chạy |
|---|---|---|
| MT5 tester (`mt5tools/chay_lien_tuc.py`) | RAM, IO đĩa — ưu tiên 1 | Luôn chạy. Bộ điều phối chỉ ghi `data/dieu_phoi/muc_mt5.json` (tổng việc / real tick). `quan_ly_slot.slot_toi_da()` lấy mức nhỏ hơn giữa mức này và biến môi trường (tệp cũ hơn 10 phút thì bỏ qua). |
| dich_llm (`ong_dan.py dich_llm --gioi_han 200`) | Mạng/LLM, nhẹ | Liên tục, song song MT5, khi còn thẻ chờ dịch. Hết việc hoặc lỗi thì nghỉ 15 phút. |
| Seeker (`seeker_quet_nguon.py` → `ong_dan nhan/phan_loai/quyet_dinh` → dọn thô) | Mạng + ghi đĩa | Chỉ khi hàng MT5 < `hang_mt5_duoi` **hoặc** thẻ chưa dịch < `the_chua_dich_duoi`, **và** ổ thật của `thu_muc_tai_ve` còn > `o_toi_thieu_gb`, **và** chưa vượt `gb_tong_toi_da`. Tải quá `gb_moi_luot` thì dừng lượt. |

- **Mức slot theo RAM:** gọi `R` là RAM trống. Tổng việc = slot đang bận + ⌊(R − 4)/1,2⌋ (tối đa 5). Việc real tick = slot đang bận + ⌊(R − 4)/2,5⌋ (tối đa 3). RAM < 4 GB thì không mở việc nặng mới. CPU ≥ 92% thì không thêm việc.
- **Không giảm tải theo game** (chủ dự án, 09:50 ngày 20/10/2026). Máy chỉ có hai trạng thái: chạy The Brain hết sức, hoặc tắt hẳn.
  - Tiến trình chạy ưu tiên Normal (không còn BelowNormal/Idle). CPU được dùng tới `cpu_cao_pct` (95%).
  - MT5 dùng mọi slot trong `BRAIN_SLOTS`, miễn RAM còn đủ. Chặn RAM 4 GB chỉ để chống swap và sập máy.
  - dich_llm chạy `luong` = 8 lời gọi song song. Khi gặp 429 (giới hạn tốc độ), `cau_llm.goi` lùi chờ 5→10→20…60 giây, thử tới `so_lan_thu_429` (6) lần và ghi `so_lan_429`. Khi hết quota (402/403/429 kèm "quota"), chuyển sang model dự phòng.
  - Sàn ổ C/D vẫn là 6 GB, dữ liệu lớn để trên E.
- **Bật / tắt:**
  - `may_nha_toi_nay\BAT_THE_BRAIN.bat`: xoá cờ rồi chạy `chay_toi_nay.bat` với mọi bước.
  - `may_nha_toi_nay\TAT_THE_BRAIN.bat`: tắt êm, theo thứ tự:
    1. Tạo cờ `TAT_THE_BRAIN.co`. `chay_lien_tuc` ngừng mở việc mới, việc đang chạy có tối đa 20 phút để xong. Hết hạn thì chỉ giết tester do chính nó mở. `dieu_phoi_may_nha` và `vong_phien` thoát vòng.
    2. Chờ tối đa 30 phút (`-ChoPhut`).
    3. Chỉ dừng các PID ghi trong `pid_*.txt` và `pid\*.pid` của log phiên, và chỉ khi tiến trình đó là python hoặc powershell.

    Script không bao giờ dừng terminal XM chính hay Claude.
- **Khoá:** dich_llm và ong_dan nhan dùng chung `may_nha_toi_nay/log/ong_dan_chay.lock` (PID) với bước 6 và `dich_llm_nen.ps1`. Không bao giờ hai tiến trình cùng ghi `trang_thai.sqlite`. Khi bộ điều phối bật, bước 5 không mở thêm `dich_llm_nen.ps1`.
- **Dọn thô** (`don_tho`), chạy sau khi nhan xong. Xoá các tệp cũ hơn 30 phút thuộc một trong ba loại:
  - tệp nén/thô `.zip .rar .7z .gz .bi5…`;
  - nhị phân lớn hơn 5 MB không phải mã;
  - tệp trùng sha1.

  Không xoá tệp nào là `nguon.tep`, `sets` hoặc `ea_lien_quan` của thẻ trong CSDL.
- **Ổ HDD E cho Seeker:** dừng Seeker, chuyển `data\seeker_da_nguon\tai_ve` sang `E:\brain2_seeker\tai_ve`, rồi `mklink /J data\seeker_da_nguon\tai_ve E:\brain2_seeker\tai_ve`. Đường dẫn tương đối của thẻ giữ nguyên, và bộ điều phối đo chỗ trống trên ổ thật (realpath).
- **Nhật ký:**
  - `data/dieu_phoi/nhat_ky.jsonl`: mỗi quyết định đổi kèm lý do.
  - `data/dieu_phoi/su_dung.jsonl`: mỗi chu kỳ một mẫu CPU/RAM/ổ/slot bận.
  - `bao_cao_phien.py` in bảng "Sử dụng tài nguyên 60 phút qua" và 8 quyết định gần nhất.
- **Cần** `pip install psutil` trên máy nhà. Thiếu psutil thì CPU/RAM ghi CHƯA ĐO ĐƯỢC và giữ mức slot cấu hình.
- **Thử không chạy gì:** `python may_nha_toi_nay/dieu_phoi_may_nha.py --mot_lan --kho`.

## Lọc MT5 hai tầng, đối chiếu Python↔MT5 (20/10/2026)

- **Tầng 1:**
  - Model=1 (OHLC M1), tên việc `<ten>_T1`, tối đa `BRAIN_TANG1_SLOT` (5) slot.
  - Báo cáo đặt ở `reports/ong_dan/ket_qua_mt5/tang1/`, không xuất CSV.
  - Qua khi net > `BRAIN_TANG1_NET_MIN` (0) **và** DD < `BRAIN_TANG1_DD_MAX` (95%).
- **Tầng 2:** việc đã qua tầng 1 chạy real tick (Model=4), tối đa `BRAIN_TANG2_SLOT` (3), được cộng +300 điểm ưu tiên.
- **Lãi MT5 khi đối chiếu** lấy net trong `.htm` (gồm cả stop-out), không cộng từ CSV.
- **Symbol báo cáo khác symbol việc** (vd `EURUSD#` so với `EURUSDmicro`):
  - gắn kết luận `SAI_SYMBOL` (CHƯA ĐO ĐƯỢC);
  - lot quy đổi ×100 (hợp đồng chuẩn so với micro);
  - việc được ghi vào `reports/ong_dan/chay_lai_mt5.json`, và `sinh_viec` bỏ các dòng sổ cái cũ của nó để chạy lại.
- **%/năm** tính theo kỳ in trong báo cáo (Period). Thêm cột `lai_kep_pct_nam`.
- **Mô phỏng Python (MÔ PHỎNG):**
  - cặp chéo quy đổi lãi về USD bằng `tien_moi_1_gia_lot_min` đo được;
  - không vào lại trong cùng nến vừa chạm TP/trailing khi bật `mot_ro_moi_chieu`;
  - đòn bẩy lấy theo `san_mt5.XM.don_bay` (500).

## Model LLM cố định cho dich_llm (20/10/2026)

- `config/llm_dich.json` là cấu hình dịch, thắng `config/qwen.json`. Các trường: `model`, `model_du_phong`, `chi_du_phong_khi_5xx`, `max_tokens` 32000, `timeout_giay` 900, `tran_ma` 60000 ký tự, `temperature` 0, `uu_tien` (regex), `loai_tru`, `ab`. Khi `model` để rỗng, dịch vẫn dùng `qwen.json` (flash).
- `python nhan/chon_model_llm.py`: GET `/models` (không in khoá) → xếp hạng → A/B 3 ứng viên × 20 EA mẫu cố định (theo thứ tự sha1). Chọn model có số ĐẠT cao nhất; hoà thì chọn model nhanh hơn. Kết quả ghi vào `config/llm_dich.json` và `reports/ong_dan/CHON_MODEL_LLM.{json,md}`. Các tuỳ chọn: `--chi_liet_ke`, `--neu_cu_hon_gio 24`, `--so_mau N`.
- Bước 13 của `chay_toi_nay.ps1` chạy script này mỗi ngày một lần. `bao_cao_phien.py` in model đang dùng và bảng A/B.
- Đổi model thì thẻ HONG cũ (nhóm lỗi phía ta) vào lại hàng. Cache spec của model khác bị gọi lại nếu có khoá.
- Đang khoá (20/10/2026, A/B thật trên box): `qwen3.7-max`, dự phòng 5xx/timeout `kimi-k2.7-code`. Số đo xem `reports/ong_dan/CHON_MODEL_LLM.md`.
