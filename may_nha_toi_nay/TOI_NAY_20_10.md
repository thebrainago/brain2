# Tối nay 20/10/2026 - tin nhắn dán cho Claude Code trên máy nhà

Mở Claude Code ở gốc repo brain2 trên máy nhà (DESKTOP-05PNLGF), dán nguyên khối dưới đây.

---

```text
Tối nay 20/10/2026. Làm ĐÚNG THỨ TỰ, mỗi bước xong mới sang bước sau, ghi kết quả từng bước vào may_nha_toi_nay/NHAT_KY.md.
Quy tắc: không in/không commit khoá (AIBOX_API_KEY), không đọc E:\api.txt, không chạy mã EA của người khác ngoài
tester, mã người khác chỉ ở data/ (git bỏ qua), không tắt terminal XM chính và không tắt Claude, không mua gì.
Chỉ báo số ĐO ĐƯỢC; không đo được ghi "CHƯA ĐO ĐƯỢC".

1) Kéo bản mới, giữ phần mình sửa đêm qua:
   cd /d %USERPROFILE%\brain2
   git stash push -m "may_nha_20_10_truoc_pull"
   git pull --rebase origin main
   git diff --no-index E:\brain2_sao_luu\chay_lien_tuc.py.claude_23h45 mt5tools\chay_lien_tuc.py
   Đọc diff: phần nào của bản sao lưu 23h45 (Claude sửa đêm qua) mà bản mới trên main CHƯA có thì gộp tay vào
   mt5tools\chay_lien_tuc.py (không ghi đè phần mới của main), chạy python -m pytest -q test_nang_cap_20_10.py, đạt thì
   commit nhỏ "chay_lien_tuc: gop phan sua may nha 23h45" và push. Sau đó `git stash list`: mục stash còn lại chỉ
   pop nếu không đụng tệp vừa kéo về; đụng thì để nguyên và ghi NHAT_KY.md.

2) python -m pip install psutil

3) Chuyển thư mục tải về của Seeker sang ổ E (giữ đường dẫn tương đối):
   Đóng Seeker nếu đang chạy (TAT_THE_BRAIN.bat nếu cần), rồi:
   mkdir E:\brain2_seeker
   robocopy data\seeker_da_nguon\tai_ve E:\brain2_seeker\tai_ve /E /MOVE /R:1 /W:1
   (nếu data\seeker_da_nguon\tai_ve còn tồn tại và rỗng thì rmdir nó)
   mklink /J data\seeker_da_nguon\tai_ve E:\brain2_seeker\tai_ve
   dir data\seeker_da_nguon  -> phải thấy <JUNCTION> tai_ve [E:\brain2_seeker\tai_ve]

4) Kiểm trước khi chạy (in OK / LỖI / CẢNH BÁO từng mục; có một lệnh LLM rất nhỏ để thử quota):
   powershell -ExecutionPolicy Bypass -File may_nha_toi_nay\kiem_truoc_khi_chay.ps1
   Mục kiểm: git main + mới nhất, chay_lien_tuc.py so bản sao lưu, python + psutil, tai_ve là junction sang E:,
   ổ C/D trống >= 6 GB và E >= 20 GB, RAM trống >= 4 GB, slot p1 (D:\mt5_tester\p1), p7 (C:\mt5_tester\p7) có
   terminal và đã đăng nhập, slot dự phòng trên E: đăng nhập XM (có mã *micro), quota ai-box.
   Còn LỖI nào thì sửa (dọn ổ, đăng nhập slot E vào XM micro...) rồi chạy lại tới khi "TỔNG: OK".
   Riêng quota: nếu báo HẾT QUOTA (403) thì KHÔNG gọi LLM nữa (dich_llm chỉ kiểm lại cache), vẫn chạy MT5 bình thường;
   ghi vào NHAT_KY.md để chủ dự án nạp.

5) Chạy: mở tách rời may_nha_toi_nay\BAT_THE_BRAIN.bat -Den "07:00"
   (Start-Process, không chờ trong lệnh). Theo dõi may_nha_toi_nay\NHAT_KY.md và log phiên (đường dẫn trong
   may_nha_toi_nay\PHIEN_HIEN_TAI.txt).

6) Trong vòng 1 giờ sau khi bật: kiểm `git log origin/main --oneline -5 -- reports/phien` phải có commit
   reports/phien/PHIEN_20261020.md (và reports/UNG_VIEN.md) do vong_phien.ps1 đẩy. Chưa có sau 60 phút thì đọc
   vong_phien.log trong thư mục log phiên, sửa lỗi (thường là git push / xung đột), chạy
   python mt5tools/bao_cao_phien.py rồi push tay, ghi nguyên nhân vào NHAT_KY.md.

Sáng mai: tóm tắt đầu may_nha_toi_nay/KET_QUA_SANG.md (số việc MT5 xong, số ĐẠT/TRƯỢT/CHƯA ĐO ĐƯỢC trong
UNG_VIEN.md, lỗi gặp), commit và push.
```

---

## Ghi chú cho chủ dự án

- Bước 4 gửi một lệnh LLM `max_tokens=1` để thử quota. Muốn bỏ qua thì thêm `-BoQuaQuota`.
- Hôm nay trên main có mấy thay đổi ảnh hưởng tới đêm nay:
  - mô phỏng DCA khớp EA hơn (commit d9683b0a);
  - dich_llm có vòng sửa một lần và prompt phiên 3 (861677b5). Khi có quota, các thẻ HONG thuộc nhóm lỗi phía ta sẽ được dịch lại;
  - Seeker lọc trùng trước khi tải (e1730fe0).
