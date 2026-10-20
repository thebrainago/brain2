# Box làm thợ phụ cho máy nhà (20/10/2026 tối)

Box không có MT5. Box nhận hai việc: dịch LLM (dich_llm) và thử Python lọc 65/15 sau phí. Các hệ đạt được đưa vào hàng MT5 của máy nhà.

- Mã: `tho_box/tho_box.py` (`dich`, `thu`, `day`) và `nhan/phan_viec.py`. Chạy trong worktree `/workspace/brain2_box_wt` (HEAD tách, `data` là symlink sang `/workspace/brain2/data`). Log ở `data/tho_box/*.log|jsonl`.
- CSDL riêng `data/ong_dan/tho_box.sqlite`, chụp từ CSDL máy nhà lúc 20:38 ngày 20/10 (CopyToBox, chỉ đọc).
- **Không trùng việc**:
  - Sổ `reports/phan_viec/NHAN_VIEC.jsonl` chỉ chứa metadata: `loai` dich (khoá = băm mã nguồn) hoặc thu_py (khoá = id thẻ), kèm máy và giờ. Khoá nào đã có trong sổ thì máy khác bỏ qua.
  - Box lấy việc từ CUỐI hàng `dich_llm.danh_sach_cho`, máy nhà lấy từ ĐẦU.
  - Phiên đêm 20/10 trên máy nhà chưa đọc sổ này. Phiên sau nên lọc hàng dịch và toi_uu bằng `phan_viec.cua_may_khac(..., "nha")`.
- **Hàng MT5 của box**: `reports/phan_viec/hang_cho_mt5_box.jsonl` dùng cùng định dạng với `reports/ong_dan/hang_cho_mt5.jsonl`, toàn việc VAO_CSV `KIEM_CSV` có CSV/.set/.ini trong `reports/phan_viec/viec_mt5/<thẻ>/`.
- **Máy nhà nhận việc (phiên sau)**: `git pull`, rồi đặt `BRAIN_HANG_BOX=1` (cùng `BRAIN_UU_TIEN_CSV=1` nếu muốn chạy trước) và chạy `python mt5tools/chay_lien_tuc.py`. `sinh_viec.tu_ong_dan` đọc thêm tệp của box và bỏ các tên trùng. Thiếu biến này thì hành vi giữ nguyên như cũ.
- **Hết quota ai-box** (HTTP 403 insufficient user quota): tiến trình `dich` tự dừng hẳn, để không làm tăng `dich_llm_loi_lan` (lên 3 lần thì thẻ bị BO_QUA oan). Nạp quota xong thì chạy lại: `cd /workspace/brain2_box_wt && nohup python3 tho_box/tho_box.py dich > data/tho_box/dich.log 2>&1 &`.
