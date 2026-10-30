# MQL5 Signals — export lịch sử (GUI, máy nhà)

Session browser user đã login MQL5 được **cấp phép dùng**. Không trích cookie/token từ profile.

## Bước

1. Mở Chrome/Edge đã login https://www.mql5.com
2. Mở danh sách đã lọc: `data/tin_hieu_cong_khai/mql5/danh_sach_signals.json` (46 signal, age≥1y, DD&lt;50%, real)
3. Với mỗi `signal_id`: https://www.mql5.com/en/signals/<id>
4. Tab **History** → **Export / CSV / Download**
5. Lưu vào `E:\brain2_grok_tin_hieu\data\mql5_csv\<signal_id>.csv`
6. Chạy quét:
   ```
   E:\brain2_grok\venv\Scripts\python.exe -m nhan.thu_thap_tin_hieu_cong_khai --nap-mql5-csv E:\brain2_grok_tin_hieu\data\mql5_csv
   E:\brain2_grok\venv\Scripts\python.exe -m nhan.dich_nguoc_tin_hieu --chi-xep mql5_csv <id> --track auto --kho-gia E:\brain2_grok\data
   ```

Nếu không có nút Export: MT5 → tab Signal → History → Save as Report (CSV), chỉ demo **345930355**.
