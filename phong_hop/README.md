# PHÒNG HỌP — anh (chủ tọa), Claude và các agent LLM khác họp bằng VĂN BẢN

**Cách dùng với anh (chỉ cần nói với Claude trong chat):**
1. "Họp về <chủ đề>" → Claude mở phiên, đính kèm tài liệu, viết ý kiến của mình **trước** (độc lập).
2. Claude mời các agent (Kimi, GLM, DeepSeek, Qwen qua AI Box; Grok qua git) viết ý kiến **vòng 1** độc lập.
3. **Vòng 2**: mỗi người đọc hết rồi `ĐỒNG Ý / BÁC BỎ / BỔ SUNG` từng người khác, nêu lỗi cụ thể, cập nhật đề xuất cuối. Bắt buộc phản biện, cấm khen xã giao.
4. Claude (thư ký) viết `BIEN_BAN.md`: đồng ý, bất đồng, điều mới, các câu **cần anh chốt**.
5. Anh nói "chốt: ..." → Claude ghi `QUYET_DINH.md`. Chỉ anh chốt; không agent nào tự quyết.

**Luật phòng họp** (nằm trong lời nhắc gửi cho mọi agent, `hop.py`): bác bỏ chỉ bằng *tiền / rủi ro tài khoản*, *tính khả thi*, *mâu thuẫn mục đích của anh*, *dữ kiện trong tài liệu*. **Cấm** bác bỏ bằng p-value / Holm / FDR. Mỗi khẳng định gắn nhãn `[ĐO ĐƯỢC] [LẬP LUẬN] [GIẢ ĐỊNH] [CHƯA BIẾT]`. Không bịa số.

**Thành viên** (`thanh_vien.json`, sửa model/vai không cần sửa code):
| Tên | Cách tham gia | Vai |
|---|---|---|
| claude | gõ tay trong chat, nạp bằng `hop.py them` | dẫn dắt, thư ký, có ý kiến riêng |
| grok | **tự ghi file qua git** vào `phien/<id>/vong<N>_grok.md` (xem `MOI_GROK.md` mỗi phiên) | phản biện hướng đi |
| kimi (`kimi-k3`) | `hop.py` gọi AI Box | trader thực chiến |
| glm (`glm-5.3`) | `hop.py` gọi AI Box | quản lí rủi ro tài khoản |
| deepseek (`ds/deepseek-v4-pro`) | `hop.py` gọi AI Box | kỹ sư hệ thống |
| qwen (`qwen3.8-max`) | `hop.py` gọi AI Box | tìm nguồn & ghép hệ |

**Lệnh** (`python phong_hop/hop.py ...`): `mo <id> "<đề bài>" [--tai-lieu a.md,b.md]` · `vong1 <id>` · `vong2 <id>` · `them <id> <vòng> <tên> <file|->` · `bien-ban-tho <id>` · `chot <id> "<quyết định>"` · `trang-thai <id>`. Một phiên (4 agent × 2 vòng) mất ~5 phút.

**Ghi chú kỹ thuật đã gặp:**
- Cổng AI Box cắt mọi yêu cầu **không-stream sau ~30 giây** (HTTP 502). `hop.py` đã dùng stream. Mô hình "suy nghĩ" (Kimi, GLM, DeepSeek, Qwen) tốn nhiều token cho suy nghĩ: để `max_tokens` ≥ 8000, nếu không ra văn bản rỗng hoặc bị cắt cuối.
- Khóa API: biến môi trường `AIBOX_API_KEY` (để trống khi proxy cloud tự chèn). **Không lưu khóa trong git.**
- Các agent LLM **không thấy repo**: tài liệu phải đính kèm bằng `--tai-lieu` (mỗi file cắt ở 14.000 ký tự).
- Trung thực: các agent đều là LLM, chưa ai từng giao dịch; vai trader là đóng vai. Họ có xu hướng đồng ý nhanh với tài liệu được đưa. Giá trị nằm ở điểm bổ sung và bất đồng ở vòng 2.

**Phiên đã họp:** `p001_huong_di` — hướng đi mới của The Brain (có `BIEN_BAN.md`, chờ anh chốt).
