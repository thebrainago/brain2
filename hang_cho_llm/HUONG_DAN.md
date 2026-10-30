# Hang cho LLM (file queue) — huong dan cho worker (Evolution bot)

Khong can API key. He thong ghi yeu cau vao `cho/`; ban doc, tra loi, CLI ghi vao `xong/`.

## Bat che do

```bash
export BRAIN_LLM_PROVIDER=hang_cho
# roi chay dieu_phoi / tru NGHI / ong_dan dich_llm
```

## Thu muc

| Thu muc | Y nghia |
|---------|---------|
| `hang_cho_llm/cho/<id>.json` | Yeu cau dang cho (id = bam loai+he_thong+nhac, 24 hex) |
| `hang_cho_llm/xong/<id>.json` | Tra loi hop le — lan goi sau cua cung bam se nhan |
| `hang_cho_llm/loi/<id>.json` | Tra loi bi tu choi validate |

## CLI (tu goc repo)

```bash
python -m nhan.hang_cho_llm liet_ke          # danh sach cho, cu nhat truoc + size
python -m nhan.hang_cho_llm xem <id>         # in full request JSON
python -m nhan.hang_cho_llm tra_loi <id> <file>
python -m nhan.hang_cho_llm thong_ke
# tuong duong: python tools/hang_cho_llm.py ...
```

## Quy trinh worker

1. `liet_ke` — lay `id` dau (cu nhat).
2. `xem <id>` — doc `he_thong`, `nhac`, `loai_viec`, `schema_mong_doi`, `ep_json`.
3. Sinh cau tra loi dung **dung format** loai viec (duoi).
4. Luu vao file (vd `/tmp/tl.json`) roi:
   `python -m nhan.hang_cho_llm tra_loi <id> /tmp/tl.json`
5. Neu CLI in `trang_thai: LOI` — xem `loi/` va sua; khong xoa `cho/` bang tay neu chua xong.

File tra loi chap nhan:

- Van ban thuan (neu loai text / tri_tue_hoi khong ep JSON)
- JSON `{"van_ban": "..."}` hoac `{"json": {...}}`
- Object ket qua thang (vd `{"de_xuat":[...],"ly_do_chon":"..."}`)

## Format theo `loai_viec`

### `nghi_de_xuat` (tru NGHI)

Bat buoc JSON object:

```json
{
  "de_xuat": [
    {
      "ten": "ten_snake_case",
      "ho": "ten_ho",
      "co_che": "mo ta AI TRA TIEN, dang A KHI B",
      "vao": [ {"trai": {...}, "phep": ">", "phai": {...}} ],
      "giu": 5,
      "nguon": ""
    }
  ],
  "ly_do_chon": "mot doan ngan"
}
```

`de_xuat` phai la list. Ton trong rang buoc trong `nhac` (khong de xuat lai co che da co, nguon URL phai khop tai lieu neu co).

### `dich_boc` / `dich_sua` (dich_llm / cau_llm)

JSON dich chien luoc (nhu `cau_llm.MAU_BOC`):

```json
{
  "loai": "he_hoan_thien|co_che|tien_ich|mo_ta",
  "spec": [],
  "python": "",
  "luoi": {},
  "co_che": [],
  "quan_tri": {},
  "tham_so": {},
  "chua_dich": []
}
```

Chi JSON, khong markdown giai thich. Neu khong dich duoc: `spec=[]`, `python=""`, ghi ly do vao `chua_dich`.

### `tri_tue_hoi`

Van ban tu do; neu `ep_json=true` thi chi mot khoi JSON hop le.

### `khac`

Van ban tu do theo `nhac`.

## Luu y

- Cung bam (cung prompt+task) chi tao **mot** file cho; goi lai se nhan `CHO` cho toi khi co `xong/`.
- Khong commit file trong `cho/`, `xong/`, `loi/` (gitignore).
- Khong in / ghi API key vao hang cho.
