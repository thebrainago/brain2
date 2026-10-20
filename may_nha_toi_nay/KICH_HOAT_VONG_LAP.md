# Kích hoạt vòng lặp liên tục trên máy nhà (giao Claude, SAU phiên đêm 20→21/10/2026)

**Không làm trong lúc phiên đêm đang chạy.** Đợi `chay_toi_nay.ps1` kết thúc (tới 07:00, hoặc tới khi có TAT_THE_BRAIN). Không tắt máy. Chỉ được taskkill đúng PID. Không đụng claude.exe hay terminal XM chính.

1. `cd` vào repo brain2, chạy `git pull --rebase`. Kéo về: `nhan/so_co_che.py`, `nhan/ghep_cheo.py`, `config/dieu_phoi.json` (các mục `vong_lap`, `ghep_cheo`, `suc_khoe`) và `dieu_phoi_may_nha.py` mới.
2. Kiểm psutil: `py -c "import psutil"`. Nếu thiếu thì `pip install psutil`. Không có psutil thì RAM, việc đóng terminal bỏ rơi và việc phóng lại MT5 đều không hoạt động; chúng chỉ ghi CHƯA ĐO ĐƯỢC.
3. Chạy test, với `--basetemp=E:\tmp_pytest`: `py -m pytest -q test_vong_lap_ghep_cheo.py test_nang_cap_20_10.py`. Phải xanh hết.
4. Xây sổ từ cache THẬT của máy nhà: `py -m nhan.so_co_che xay`, rồi xem thử `py -m nhan.so_co_che tim --trang DAT_MT5 --n 20`.
5. Chạy khô một vòng: `py may_nha_toi_nay\dieu_phoi_may_nha.py --mot_lan --kho`. Đọc các dòng `[ong_dan]` và `[suc_khoe]`. Kiểm `suc_khoe` có định đóng terminal nào không. Nếu có, xác nhận PID đó là tester trong `mt5_tester`. **Đặt `BRAIN_TERMINAL_GIAO_DICH`** bằng đường dẫn terminal XM chính để chắc chắn nó không bao giờ bị chọn.
6. Bật như mọi tối: `BAT_THE_BRAIN.bat -Den "07:00"`. Bước 12 phóng bộ điều phối, và vòng lặp tự chạy.
7. Theo dõi `data\dieu_phoi\nhat_ky.jsonl`. Các dòng cần thấy: `ong_dan CHAY python|ghep|dich`, `ghep_cheo xong`, `suc_khoe ...`. Kiểm thêm `reports\kho_co_che\danh_muc_ghep.jsonl`.
8. Lùi về hành vi cũ: đặt `"vong_lap": {"bat": false}` (chỉ còn dich_llm). Muốn tắt riêng thì đặt `ghep_cheo.bat` hoặc `suc_khoe.bat` = false.
9. Cuối phiên: commit `reports/kho_co_che/*`, chỉ phần metadata. Không commit gì trong `data/`.
