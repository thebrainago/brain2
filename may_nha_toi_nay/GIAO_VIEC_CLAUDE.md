# Giao việc tối nay cho máy nhà (DESKTOP-05PNLGF) — đọc hết trước khi làm

Bạn là tác tử (Claude Code, hoặc Cursor) chạy **một mình qua đêm** trên máy nhà Windows của chủ dự án.
Bạn không có ngữ cảnh nào khác ngoài tệp này và các tệp nó chỉ tới. Mọi chữ cho người đọc viết **tiếng Việt có dấu**;
chú thích trong mã viết không dấu. Làm **lần lượt bước 0 → 11**. **Bước nào lỗi thì ghi lại và chuyển sang bước sau**, không dừng cả đêm vì một bước.

Script làm sẵn gần hết việc: `may_nha_toi_nay\chay_toi_nay.ps1` (gọi qua `chay_toi_nay.bat`). Việc của bạn là
chạy nó theo từng bước, đọc log, **sửa chỗ hỏng** (nhất là lỗi biên dịch EA ở bước 4), và viết tóm tắt sáng.

> **20/10/2026:** đọc mục 7 (chia việc Claude/Grok, hoà giải `chay_lien_tuc.py`, biến môi trường, bộ điều phối) trước bước 0.

---

## 1. Bối cảnh — đọc trước

1. `CHI_THI_CHU_DU_AN.md` (gốc repo) — chỉ thị của chủ dự án, thắng mọi luật khác. Mục tiêu chỉ là **lợi nhuận**.
   Phong cách chủ dự án: không cắt lỗ cứng, chốt lời nhỏ, DCA, hedge, gỡ.
2. `tai_lieu/ONG_DAN.md` — ống dẫn: kho → phân loại → dịch → tối ưu Python → lọc → hàng MT5 → kho cơ chế.
3. `tai_lieu/SLOT_TESTER.md`, `tai_lieu/CHAY_MAY_NHA.md`, `tai_lieu/VAN_HANH_MAY_NHA.md` — slot tester và cách chạy máy nhà.
4. `GHI_CHU_NANG_CAP_GROK.md` — nhật ký nâng cấp gần nhất (tác vụ VAO_CSV + dịch LLM 19/10/2026).

**Tiêu chí lọc:**
- Lọc Python (MÔ PHỎNG): sụt vốn tối đa (DD) **< 65%** và lãi **> 15%/năm**.
- Kết quả cuối (MT5, sau phí thật): DD **≤ 80%** và lãi **≥ 10%/năm**.
- p-value, Holm, FDR, placebo… **chỉ là nhãn**, không dùng để loại ý tưởng.

**Nhãn số liệu:** số từ Python ghi **MÔ PHỎNG**; phí chưa đo ghi **PHÍ TẠM**; thứ chưa đo ghi **CHƯA ĐO ĐƯỢC**.

---

## 2. Luật — không ngoại lệ

1. **Ổ C không được phình.** Dữ liệu, log, tạm, tải về đều để **D:** hoặc **E:** (script tự đặt TEMP sang `D:\brain2_tmp`).
   **CPU tối đa 90%** (`mt5tools/dieu_phoi_song_song.py` tự giảm tải; tiến trình Python để ưu tiên BelowNormal/Idle).
2. **Không đưa khoá hay mật khẩu vào git, không bao giờ in khoá** ra màn hình, log hay tệp. Không mở, không đọc `E:\api.txt`.
   Khoá chỉ lấy từ biến môi trường / cc-switch (mã đã làm sẵn trong `nhan/cau_llm.py`, tự che khoá trong log).
   Bước 0 chỉ báo **CÓ / KHÔNG**.
3. **Không vượt chặn bot**: không WARP, VPN, stealth, giải captcha, vượt Cloudflare. **Không đăng nhập** mạng xã hội
   hay Telegram. **Không mua gì.** Trang bị chặn thì ghi lại là bị chặn rồi đi tiếp.
4. **Đọc mã tải về trước khi chạy.** Mã của người khác **chỉ để trong `data/`** (git bỏ qua). Gói zip tối nay có mã người
   khác nên **KHÔNG được vào git**.
5. **Chỉ một phiên dùng MT5 tester tại một thời điểm.** Muốn dừng terminal thì chỉ `taskkill /PID <pid> /F` **theo PID của
   terminal tester** do chính bạn mở — không bao giờ `taskkill /IM terminal64.exe`, không đụng terminal giao dịch của chủ.
6. **Chỉ báo số đo được thật.** Chưa đo thì ghi `CHƯA ĐO ĐƯỢC`. Không ước lượng, không bịa.
7. **Commit khi test qua** (`python -m pytest -q test_ong_dan.py test_dich_llm.py test_sinh_viec.py test_an_toan_tester.py`; hai test đóng gói zip tự bỏ qua ngoài box), `git pull --rebase`
   trước khi push, không `--force`. Ghi mọi việc vào `GHI_CHU_NANG_CAP_GROK.md` (hoặc `GHI_CHU_NANG_CAP_CLAUDE.md` nếu bạn
   muốn ghi chú riêng) **và** `may_nha_toi_nay/NHAT_KY.md` (script tự ghi một dòng cho mỗi việc; bạn ghi thêm nhận xét).
8. **Không tắt máy, không khởi động lại, không đăng xuất**, không cài driver, không đổi cài đặt Windows.
9. Thư mục `data/`, `reports/SEEKER_*`, `reports/URL_BI_CHAN.md` thuộc tác vụ Seeker: chỉ để các script Seeker ghi, không sửa tay.
10. Không `git stash` khi còn tiến trình nền đang ghi vào repo.

**Điều kiện dừng / giảm tải (sửa 20/10/2026 09:50):** KHÔNG còn giảm tải theo game. Máy chạy The Brain hết sức, hoặc tắt hẳn bằng `TAT_THE_BRAIN.bat`. Giới hạn duy nhất: RAM trống ≥ 4 GB, CPU < 95%, sàn ổ C/D 6 GB.

---

## 3. Cách chạy (sửa 19/10/2026 chiều, Claude: chạy hai pha, MT5 chạy nền suốt đêm)

Mở PowerShell tại gốc repo brain2 (thường là `%USERPROFILE%\brain2`).

**Quan trọng với tác tử (Claude Code):**
- Một lệnh shell của tác tử bị cắt sau vài phút (Claude Code: tối đa 10 phút một lệnh). Bước dài (đo phí ~1 giờ, dịch,
  tối ưu, MT5 tới 07:00) phải chạy **tách rời** bằng `Start-Process`, rồi theo dõi `NHAT_KY.md` và log. Đừng gọi
  `chay_toi_nay.bat` không tham số trong một lệnh chờ.
- Hết lượt trả lời thì tác tử đứng yên tới khi có tin nhắn mới. Muốn tự xem lại định kỳ: `/loop 30m` với câu
  "xem may_nha_toi_nay/NHAT_KY.md và log, sửa chỗ hỏng nếu sửa được". Script tự chạy hết các bước dù tác tử có xem hay không.

**Pha A (19:00 – khoảng 19:45), từng bước, có người hoặc tác tử nhìn:**
```powershell
$L = "D:\brain2_log"; New-Item -ItemType Directory -Force $L | Out-Null
foreach ($b in "0","1","2","3","4") {
  Start-Process cmd -ArgumentList "/c may_nha_toi_nay\chay_toi_nay.bat -Buoc $b > $L\pha_a_$b.txt 2>&1" -WindowStyle Minimized -Wait
  Get-Content may_nha_toi_nay\NHAT_KY.md -Tail 15
}
```
(`-Wait` trên Start-Process vẫn bị cắt nếu quá giờ của tác tử: bước 3 có thể lâu, khi đó bỏ `-Wait` và xem NHAT_KY sau.)
Bước 4 phải ra **0 lỗi** và `.ex5` mới ở mọi slot trước pha B; có lỗi thì sửa `ea_demo\BRAIN_XuLiLenh.mq5`, chạy lại `-Buoc 4`.

**Pha B (tách rời, tới 07:00 sáng):**
```powershell
Start-Process cmd -ArgumentList '/c may_nha_toi_nay\chay_toi_nay.bat -Buoc "5-11" -Den "07:00" > D:\brain2_log\pha_b.txt 2>&1' -WindowStyle Minimized
```
Thứ tự thật (theo vị trí trong script): **7** (mở hàng MT5 NỀN ngay, chạy tới 07:00) → **5** (dịch thử, rồi dịch nền;
sau mỗi lượt dịch có thẻ đạt, vòng nền tự chạy `ong_dan.py chay` nên việc MT5 mới vào hàng trong đêm) → **6** → **9**
(Dukascopy nền) → **10** → **8** (chờ hàng MT5 xong, tối đa 07:40) → **11** (commit + push).
Nếu sửa EA sau khi pha B đã chạy: chỉ cần `-Buoc 4` lại; việc MT5 kế tiếp tự dùng `.ex5` mới.

**Tham số / biến môi trường ghi đè** (khi tự dò sai):

| Tham số | Biến môi trường | Mặc định dò |
|---|---|---|
| `-Repo` | `BRAIN_REPO` | thư mục cha của `may_nha_toi_nay` |
| `-TheBrain` | `THE_BRAIN_DIR` | `C:\Research SP500\lab` |
| `-Python` | `BRAIN_PY` | `.venv` của repo → `%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe` → `python` trên PATH |
| `-Mt5Exness` | `BRAIN_MT5_EXNESS` | `D:\mt5_tester\exness_cent\terminal64.exe` (dò thư mục tên có "exness") |
| `-Mt5Xm` | `BRAIN_MT5_XM` | `D:\mt5_tester\xm_micro\terminal64.exe` (dò thư mục tên có "xm") |
| `-MetaEditor` | `BRAIN_METAEDITOR` | `metaeditor64.exe` trong từng slot |
| `-Slots` | `BRAIN_SLOTS` | `D:\mt5_tester\p1;D:\mt5_tester\p2;E:\mt5_tester\p3;E:\mt5_tester\p4` |
| `-GoiZip` | `BRAIN_GOI_ZIP` | `goi_ea_ngoai_*.zip` mới nhất trong `D:\brain2_goi`, `E:\brain2_goi`, `Downloads` |
| `-ThuMucLog` | `BRAIN_LOG_DIR` | `D:\brain2_log\toi_nay_<ngày>` (hoặc E:) |

Khác: `-GioiHanThu 20` (bước 5), `-LuongLlm 4`, `-ToiDa 30` (bước 6), `-ChoDichXong`, `-KhongPush`.

Log chi tiết từng lệnh: `<ThuMucLog>\<bước>.out.txt` / `.err.txt`. Tiến trình nền ghi PID ở `<ThuMucLog>\pid_<tên>.txt`;
muốn dừng thì `Stop-Process -Id <pid>` đúng PID đó.

---

## 4. Các bước

### Bước 0 — Kiểm máy
`python may_nha_toi_nay/kiem_may.py --mt5 --terminal <XM> --terminal <Exness>` (script gọi sẵn). Ghi vào NHAT_KY:
- dung lượng trống C:, D:, E: (C: dưới 15 GB thì không ghi thêm gì vào C);
- phiên bản Python, các gói `numpy pandas MetaTrader5 psutil pyarrow requests` có/không (thiếu thì `pip install` gói đó, chỉ gói chuẩn từ PyPI);
- MT5 Exness và XM: tìm thấy không, đã đăng nhập không, **tài khoản có phải hedging không** (tester cần hedging cho DCA/hedge);
- mỗi slot tester `p1..p4` đang đăng nhập server nào (chỉ đọc dòng `Server=` trong `config\common.ini`);
- `AIBOX_API_KEY` có/không, cc-switch provider `aibox` có/không — **chỉ CÓ/KHÔNG**.

### Bước 1 — git pull
`git -C <brain2> pull --rebase` và `git -C "C:\Research SP500\lab" pull --rebase` (the-brain, nhánh `claude/autonomous-trading-system-rzzt7h`).
Pull lỗi vì có thay đổi chưa commit: xem `git status`, commit thay đổi của chính máy nhà nếu hợp lệ, rồi pull lại. Không `reset --hard`.

### Bước 2 — Gói zip
Gói: **`goi_ea_ngoai_20261019.zip`** (29,5 MB, 3.073 tệp: mã 2.306 thẻ chờ dịch, ảnh chụp `trang_thai.sqlite`,
cache dịch, giá gói `data/ong_dan/gia_goi/`).

**Gói ở đâu:** tải lên Google Drive **không làm được** (kết nối Drive của Grok Bot chỉ đọc, không nhận tệp). Đã tạo sẵn
thư mục Drive `brain2_may_nha` (https://drive.google.com/drive/folders/1Wj-pbjBdb4kqpJay2p8WxMVbiBKFNQNB) nhưng **thư mục
đang trống**. **Grok Bot sẽ chép gói vào `D:\brain2_goi\` khi máy nhà kết nối với Grok Bot.** Nếu chủ dự án tự tải gói về
chỗ khác thì truyền `-GoiZip <đường dẫn>`.

Script: sao lưu `data\ong_dan\trang_thai.sqlite` sang `D:\brain2_backup\trang_thai_<giờ>.sqlite` **trước**, giải nén ra thư
mục tạm trên D:, rồi chỉ chép cây `data\` vào repo (không đè mã nguồn). Không thấy gói → bước này ghi `CHƯA CHẠY ĐƯỢC`,
các bước sau vẫn chạy trên dữ liệu đang có (bước 5 khi đó có ít thẻ có mã).

### Bước 3 — Đo phí sàn thật
`python mt5tools/do_phi_san.py <terminal> --ngay-tick 14 --tp-gia 5 --ngay-lich-su 365` cho **Exness cent** rồi **XM micro**
(như `may_nha/DO_PHI_SAN.cmd`). Terminal phải đang đăng nhập (đăng nhập là việc của chủ; bạn không nhập mật khẩu).
Kết quả vào `reports/phi_san/<server>/` (`ma.csv`: spread, swap, hoa hồng, contract_size, lot min/max/step; `spread_gio.csv`).
`nhan/tai_khoan.ho_so_phi` **tự** dùng tệp này và đổi nhãn `PHÍ TẠM` → `ĐO (<server>)` — không cần sửa code.
Kiểm: mở `ma.csv`, xem cột `hop_dong`, `lot_min`, `swap_mua/ban` có giá trị thật. Ghi vào NHAT_KY.
Kết quả tối ưu đã có trong `trang_thai.sqlite` vẫn tính bằng PHÍ TẠM — **không xoá DB**; ghi vào KET_QUA_SANG đề xuất tính lại.
Một sàn không đo được → ghi `CHƯA ĐO ĐƯỢC` cho sàn đó.

### Bước 4 — Biên dịch EA
`ea_demo\BRAIN_XuLiLenh.mq5` (bản 1.10 có chế độ VAO_CSV, **chưa biên dịch lần nào**). Script chép vào
`<slot>\MQL5\Experts\BRAIN\` rồi chạy trong thư mục `<slot>\MQL5`:

```
metaeditor64.exe /compile:Experts\BRAIN\BRAIN_XuLiLenh.mq5 /log:Experts\BRAIN\BRAIN_XuLiLenh.log
```

**Bẫy:** đường dẫn tuyệt đối trong `/compile:` trả rc=0 mà không làm gì. Phải dùng đường dẫn **tương đối**, cwd = `MQL5`
(xem `ea_tu_dong.py` dòng ~140). Đọc log (UTF-16) — dòng `N errors, M warnings`. Có lỗi: **sửa `ea_demo\BRAIN_XuLiLenh.mq5`
trong repo** (không sửa bản trong slot), chạy lại `-Buoc 4` tới khi 0 lỗi và `.ex5` mới xuất hiện ở mọi slot. Commit bản sửa
(`git add ea_demo/BRAIN_XuLiLenh.mq5`), ghi nguyên nhân từng lỗi vào GHI_CHU.

### Bước 5 — Dịch bằng LLM
Thử trước: `python ong_dan.py dich_llm --gioi_han 20 --luong 4` (lượt thử lỗi / quá giờ vẫn mở dịch nền). Kiểm `reports/ong_dan/DICH_LLM.md`:
tỉ lệ `DAT` / `HONG` / `LOI_LLM`, số token, model dùng (qwen3.7-flash, tự lùi qwen3.6-flash khi 403/402/hết quota).
Thẻ đạt phải qua kiểm tự động (không nhìn trước ở cắt 50/70/90%, ≥ 3 lệnh). Nếu `LOI_LLM` chiếm gần hết → dừng, ghi lý do.
Ổn thì script mở **nền** `may_nha_toi_nay\dich_llm_nen.ps1` (lặp `dich_llm --gioi_han 200`, chạy lại được nhờ cache theo
sha256; dừng khi hết hàng hoặc 3 lượt liền không làm được thẻ nào). Không có khoá → `CHƯA CHẠY ĐƯỢC`, sang bước 6.

### Bước 6 — Ống dẫn
`python ong_dan.py chay --toi-da 30` (tối ưu Python các thẻ mới dịch + lọc 65/15 ở lot thật + sinh việc MT5 + kho cơ chế).
Có thể chạy lại sau khi dịch nền làm thêm được nhiều thẻ.

### Bước 7 — Hàng MT5 (NỀN, mở ngay sau bước 4)
Chỉ khi **không có phiên nào khác đang dùng tester**. Script mở **một** `python mt5tools/chay_lien_tuc.py --den 07:00`
chạy nền (PID ở `pid_mt5.txt`). **Mỗi slot tự lấy việc đúng sàn nó đăng nhập** (đọc `Server=` trong `config\common.ini`
của slot): slot XM lấy việc XM và việc cũ V24, slot Exness chỉ lấy việc Exness của ống dẫn. Hai sàn chạy song song cả
đêm, không chia đôi giờ, không xoá tick giữa đêm. `BRAIN_UU_TIEN_CSV=1` đẩy việc `KIEM_CSV` (đối chiếu lệnh Python ↔ MT5
của các hệ đạt) lên đầu. Quá 07:00 thì không mở việc mới; quá 07:20 thì dừng đúng PID việc còn chạy và ghi `qua_gio_het_han`
(CHƯA ĐO ĐƯỢC, đêm sau chạy lại). Slot chưa đăng nhập XM/Exness → chỉ chạy việc cũ; không slot nào đăng nhập → `CHƯA ĐO ĐƯỢC`.

### Bước 8 — Đọc kết quả MT5
Chờ hàng MT5 nền kết thúc (tối đa 07:40), rồi `python ong_dan.py doc_mt5` rồi `python ong_dan.py bao_cao`. Xem `reports/ong_dan/DOI_CHIEU_MT5.md` (sai số cho phép:
±1 nến, 3×spread + 0,05% giá, 1 bước lot, ≥ 95% lệnh khớp, chênh lãi/lỗ ≤ 10% hoặc ≤ 1% vốn).

### Bước 9 — Tải Dukascopy (nền)
`python tai_dukascopy_tick_m1.py --luong 4` với `DU_LIEU_CHUAN=D:\du_lieu_chuan`, ưu tiên Idle. Script tự dừng khi ổ
còn dưới 15 GB. Đây là trang công khai, không cần đăng nhập.

### Bước 10 — Seeker từ máy nhà
Box bị chặn IP ở vài nguồn (`reports/SEEKER_BOX_DO.json`, mục `ok: false`: arxiv, quantconnect, RSS Financial Hacker,
RSS reddit quant, gestaltu). Chạy lại **chỉ các nguồn đó** từ máy nhà: `python seeker_quet_nguon.py --chi <ds> --ep`
(tôn trọng robots.txt, ≥ 4 giây/yêu cầu). Chỉ đọc trang công khai bình thường; bị chặn thì ghi lại, không vượt.
Rồi đọc thêm tệp tay trong `E:\brain2_nhap` qua `python ong_dan.py nhan` → `phan_loai` → `quyet_dinh`.

### Bước 11 — Commit + tóm tắt sáng
Script sinh khung `may_nha_toi_nay/KET_QUA_SANG.md` (bảng trạng thái từng bước + trích báo cáo), quét diff tìm chuỗi giống
khoá, rồi `git add reports/ may_nha_toi_nay/NHAT_KY.md may_nha_toi_nay/KET_QUA_SANG.md GHI_CHU_*.md`, commit,
`git pull --rebase`, push. **Không bao giờ add `data/` hay tệp zip.**
Sau đó **bạn viết thêm phần tóm tắt cho người** ở đầu KET_QUA_SANG.md (tiếng Việt có dấu, ngắn):
đã đo phí chưa (số thật), EA biên dịch được chưa, dịch được bao nhiêu thẻ / đạt bao nhiêu, bao nhiêu việc MT5 chạy xong,
hệ nào qua lọc cuối (DD ≤ 80%, ≥ 10%/năm sau phí) — **chỉ số đo được**, còn lại `CHƯA ĐO ĐƯỢC`; việc chủ cần làm
(đăng nhập slot nào, cấp khoá…). Commit + push lần nữa.

---

## 5. Khi gặp sự cố

| Sự cố | Làm gì |
|---|---|
| Bước lỗi | Ghi NHAT_KY (lệnh, mã lỗi, 5 dòng cuối log), sang bước sau. |
| Thiếu gói Python | `pip install <gói>` (PyPI chính thức), ghi lại. |
| Terminal chưa đăng nhập | Không tự nhập mật khẩu. Ghi `CHƯA ĐO ĐƯỢC`, để chủ đăng nhập. |
| Tester treo > 2 giờ một việc | Dừng **đúng PID** terminal tester đó, ghi lại; `chay_lien_tuc.py` tự làm việc kế. |
| Ổ D/E còn < 15 GB | Dừng Dukascopy (Stop-Process PID trong `pid_dukascopy.txt`). |
| Push bị từ chối | `git pull --rebase` rồi push lại; xung đột thì giữ bản của cả hai, không `--force`. |
| Trang web chặn / captcha | Ghi bị chặn, bỏ qua. |

## 6. Đã biết, chưa sửa (19/10/2026 chiều, Claude rà soát) — ghi vào KET_QUA_SANG nếu gặp

- Đối chiếu Python ↔ MT5 của việc **Exness** vẫn dùng hồ sơ tài khoản XM (stop-out, ký quỹ) ở phía Python
  (`ong_dan.chay_python_csv`); lệch ở phần ký quỹ/stop-out với Exness là do đó, không phải lỗi EA.
- `do_phi_san.py` chưa ghi hoa hồng theo lot → tài khoản có hoa hồng (Raw/Zero) bị tính hoa hồng 0.
- Mã EA dài hơn 16.000 ký tự chỉ được gửi phần đầu cho LLM (`cau_llm.TRAN_MA`) → thẻ dịch từ mã cắt cụt.
- Hộp cát chạy mã LLM trên Windows **không** có giới hạn bộ nhớ/CPU hay cách ly thư mục (chỉ trên Linux). Đã chặn thêm
  đường gọi phương thức theo tên chuỗi (`.apply("to_csv", ...)`), nhưng vẫn coi mã LLM là mã lạ: không chạy bằng tay ngoài hộp cát.
- Số liệu tối ưu cũ trong `trang_thai.sqlite` tính bằng PHÍ TẠM; sau bước 3 thẻ mới tính bằng phí ĐO → `tot_nhat` có thể trộn hai loại.

---

## 7. Cập nhật 20/10/2026 (Grok Bot) — đọc TRƯỚC phiên tối nay

### 7.1 Chia việc (chủ dự án duyệt)
- **Claude (máy nhà):** chạy hàng MT5 và các script trên máy nhà (`chay_toi_nay.ps1`), sửa lỗi cục bộ khi chạy.
- **Grok Bot (box):** sửa mã trong repo, theo dõi, viết báo cáo, đẩy lên `main`.
- **Ai sửa một tệp NGAY TRÊN máy nhà thì phải ghi vào `may_nha_toi_nay/NHAT_KY.md` TRƯỚC khi sửa:** giờ, tên tệp, lý do. Sau đó commit nhỏ và `git pull --rebase` trước khi push. Không sửa đè việc của người kia.

### 7.2 Hoà giải `mt5tools/chay_lien_tuc.py` sửa cục bộ đêm 19/10
Đêm 19/10 trên máy nhà có bản sửa cục bộ, đã sao lưu ở `E:\brain2_sao_luu\chay_lien_tuc.py.claude_23h45`. Bản trong `main` hôm nay đã viết lại phần slot/ổ đĩa/tầng. Làm theo thứ tự:
1. `git stash push mt5tools/chay_lien_tuc.py -m "claude_19_10"`, rồi `git pull --rebase`.
2. `git diff stash@{0} -- mt5tools/chay_lien_tuc.py` (hoặc so với tệp sao lưu) để xem bản cục bộ đã thêm gì.
3. Ý nào chưa có trong bản mới (đường slot, xoá REP khi đầy ổ, …) thì đưa vào bằng biến môi trường ở mục 7.3, không sửa cứng. Phải sửa mã thì ghi NHAT_KY trước, kèm test.
4. `git stash drop` chỉ sau khi đã đối chiếu xong.

### 7.3 Biến môi trường (mặc định trong ngoặc)
| Biến | Ý nghĩa |
|---|---|
| `BRAIN_SLOTS` (`D:\mt5_tester\p1;C:\mt5_tester\p7;E:\mt5_tester\p3;E:\mt5_tester\p6;E:\mt5_tester\p4`) | Thứ tự slot. `chay_toi_nay.ps1` xuất sẵn biến này. |
| `BRAIN_O_SSD` (`C,D`) / `BRAIN_SAN_TRONG_GB` (6) / `BRAIN_SAN_TRONG_HDD_GB` (3) | Sàn chỗ trống. Thiếu chỗ thì dọn theo bậc (log → tick → lịch sử). Vẫn thiếu thì bỏ slot đó. |
| `BRAIN_RAM_MIN_GB` (4) / `BRAIN_RAM_TANG2_GB` (6) | RAM tối thiểu để mở việc mới. |
| `BRAIN_HAI_TANG` (1), `BRAIN_TANG1_MODEL` (1 = OHLC M1), `BRAIN_TANG1_SLOT` (5), `BRAIN_TANG2_SLOT` (3) | Lọc hai tầng. |
| `BRAIN_TANG1_DD_MAX` (95), `BRAIN_TANG1_NET_MIN` (0) | Ngưỡng qua tầng 1. |
| `BRAIN_LANH_DIR` (`E:\lanh_tu_D\rep`) | Nơi chuyển `.htm` cũ đến lúc đầu phiên. |
| `BRAIN_REP_DIR`, `BRAIN_LOG_LIEN_TUC` | Đường dẫn báo cáo / log của `chay_lien_tuc`. |
| `BRAIN_MUC_MT5` | Tệp mức slot do `dieu_phoi_may_nha.py` ghi (mặc định `data\dieu_phoi\muc_mt5.json`). |

### 7.4 Việc cần làm tối nay
1. `pip install psutil` (bộ điều phối và chặn RAM cần nó).
2. Chuyển thư mục tải về của Seeker sang ổ E (xem `tai_lieu/ONG_DAN.md`, mục "Bộ điều phối"): dừng Seeker, `robocopy data\seeker_da_nguon\tai_ve E:\brain2_seeker\tai_ve /E /MOVE`, rồi `mklink /J data\seeker_da_nguon\tai_ve E:\brain2_seeker\tai_ve`. Ghi NHAT_KY.
3. Bật bằng `may_nha_toi_nay\BAT_THE_BRAIN.bat` (tương đương `chay_toi_nay.bat` và xoá cờ tắt). Tắt bằng `TAT_THE_BRAIN.bat`: tắt êm, chỉ dừng PID ống dẫn, không đụng XM chính hay Claude. Không còn giảm tải khi chủ dự án chơi game. Máy chạy hết sức: ưu tiên Normal, CPU tới 95%, slot MT5 theo RAM. Khi chạy:
   - Bước 12 mở `vong_phien.ps1`. Nó viết báo cáo mỗi 60 phút và khởi động `dieu_phoi_may_nha.py`, nên Seeker và dich_llm chạy theo tài nguyên, không còn cố định 2 giờ.
   - Bước 5 chỉ dịch thử rồi giao phần còn lại cho bộ điều phối.
4. `ong_dan.py dich_llm` chạy lại sẽ tự kiểm lại các thẻ cache cũ bằng bộ chuẩn hoá mới, không tốn lượt gọi. Lượt gọi mới dùng prompt phiên 2. Sáng mai ghi vào KET_QUA_SANG: tỉ lệ ĐẠT và bảng nhóm lý do trong `reports/ong_dan/DICH_LLM.md`.
5. Chạy lại 3 việc EURUSD# (`od_skst299b0817f66d4096`, `od_skst48a4616b10a6ff9c`, `od_skst4ac0c7fd10781af4`): `ong_dan.py doc_mt5` ghi `reports/ong_dan/chay_lai_mt5.json`, rồi `sinh_viec` tự đưa chúng vào lại hàng với symbol `EURUSDmicro`.
6. Bước 11 giờ tự đặt danh tính git nếu thiếu và báo đúng khi commit/push hỏng. Kiểm tra `git log -1` sau phiên.
7. Thử bộ điều phối không chạy gì: `python may_nha_toi_nay\dieu_phoi_may_nha.py --mot_lan --kho`. Xem `data\dieu_phoi\nhat_ky.jsonl`.
8. Bước 13 (mới) chọn model LLM mạnh cố định. Nếu nó báo CHƯA CHỌN ĐƯỢC: chạy `python nhan\chon_model_llm.py --chi_liet_ke`, chép **tên model** (không chép khoá) vào KET_QUA_SANG, rồi sửa `uu_tien` trong `config\llm_dich.json` cho khớp. Ghi NHAT_KY trước khi sửa.
