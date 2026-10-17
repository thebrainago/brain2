#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PHONG HOP - chu du an (chu toa), Claude va cac agent LLM khac hop bang VAN BAN. Chu toa chot cuoi cung.

  python phong_hop/hop.py mo <id> "<de bai>" [--tai-lieu a.md,b.md]   mo phien, ghi 00_DE_BAI.md (+ dinh kem tai lieu)
  python phong_hop/hop.py vong1 <id> [--tu deepseek | --tu deepseek,qwen | --tat-ca]   cac agent viet Y KIEN DOC LAP, song song
  python phong_hop/hop.py vong2 <id> [--tu ... | --tat-ca]     doc het Y KIEN VONG 1 roi DONG Y / BAC BO / BO SUNG tung nguoi + de xuat cuoi
      (khong co --tu: chi goi `mac_dinh_goi` trong thanh_vien.json = deepseek + qwen; chu du an 17/10)
  python phong_hop/hop.py them <id> <vong> <ten> <file|->   nap van ban cua thanh vien khong goi duoc (Claude trong chat, Grok, chu toa)
  python phong_hop/hop.py bien-ban-tho <id>   gop thanh BIEN_BAN_THO.md (bang lap truong + ma tran phan bien) cho chu toa doc
  python phong_hop/hop.py chot <id> "<quyet dinh>"   ghi QUYET_DINH.md cua chu toa
  python phong_hop/hop.py trang-thai <id>

Khoa API: bien moi truong AIBOX_API_KEY (de trong neu proxy cloud tu chen). KHONG luu khoa trong git.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

GOC = Path(__file__).resolve().parent
PHIEN = GOC / "phien"
BASE = os.environ.get("AIBOX_BASE_URL", "https://api.ai-box.vn/v1").rstrip("/")
KHOA = os.environ.get("AIBOX_API_KEY", "")
GIOI_HAN_TAI_LIEU = 14000     # ky tu moi tai lieu dinh kem
GIOI_HAN_Y_KIEN = 7000        # ky tu moi y kien dua cho nguoi khac doc

LAP_TRUONG = ("ĐỒNG Ý", "PHẢN ĐỐI", "ĐỀ XUẤT KHÁC", "CHƯA ĐỦ DỮ KIỆN")

LUAT_CHUNG = """Ban dang du mot PHONG HOP VIET VAN BAN (khong tro chuyen) ve du an THE BRAIN, cung chu du an (chu toa, nguoi chot cuoi cung), Claude va cac AI khac.

BOI CANH CHU DU AN: la trader giao dich TAY tren MT5 (Exness cent, XM micro), muc tieu duy nhat la LOI NHUAN. Thich: DCA, gong lenh, go lenh, hedge, nhoi lenh theo chieu gia chay, KET HOP nhieu phuong phap/he thong thay vi danh don he. Khong muon tieu chi hoc thuat nang ne.
The Brain = may THU THAP moi he thong/tin hieu vao lenh duoc (EA, chi bao, lich su giao dich...) roi KET HOP chung cung quan tri von, do o cap TAI KHOAN.

LUAT PHONG HOP:
1. Viet tieng Viet co dau, ngan gon, dung muc. Cam khen xa giao. Co y kien rieng, khong lap lai de bai.
2. Chi duoc BAC BO bang: (a) tien va rui ro tai khoan, (b) tinh kha thi/chi phi/thoi gian, (c) mau thuan voi muc dich cua chu du an, (d) du kien da cho trong tai lieu. CAM bac bo bang p-value, Holm, FDR, 'khong du y nghia thong ke', 'chua qua cong hoc thuat'.
3. Moi khang dinh gan nhan: [DO DUOC] (co trong tai lieu duoc dua), [LAP LUAN], [GIA DINH], [CHUA BIET]. Khong bia so, khong bia ten file/ham.
4. Neu thay chu toa hoac thanh vien khac hieu sai muc dich, noi thang.
"""

MAU_V1 = """Viet Y KIEN DOC LAP cua ban theo dung mau (toi da ~450 tu):
LẬP TRƯỜNG: <ĐỒNG Ý | PHẢN ĐỐI | ĐỀ XUẤT KHÁC | CHƯA ĐỦ DỮ KIỆN> (voi huong di/de xuat trong de bai)
## Ý chính
(toi da 5 gach)
## Lập luận
(co nhan [DO DUOC]/[LAP LUAN]/[GIA DINH]/[CHUA BIET])
## Rủi ro lớn nhất tôi thấy
## Đề xuất cụ thể (làm gì, thứ tự)
## Cần chủ tọa quyết
"""

MAU_V2 = """Day la Y KIEN VONG 1 cua moi nguoi. Viet VAN BAN VONG 2 (toi da ~500 tu) theo mau:
Voi MOI thanh vien khac, MOT dong bat dau bang `@ten: ĐỒNG Ý` hoac `@ten: BÁC BỎ` hoac `@ten: BỔ SUNG`, roi ly do CU THE (trich diem ban dang noi toi). BAC BO thi chi ro loi nam o dau theo luat so 2. Khong duoc dong y het neu thuc su co lo hong.
Sau do:
LẬP TRƯỜNG CẬP NHẬT: <ĐỒNG Ý | PHẢN ĐỐI | ĐỀ XUẤT KHÁC | CHƯA ĐỦ DỮ KIỆN>
## Đề xuất cuối (toi da 7 gach, theo thu tu lam)
## Điều tôi đã đổi ý sau khi đọc người khác (neu co)
## Cần chủ tọa quyết
"""


def doc(p: Path, mac_dinh: str = "") -> str:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return mac_dinh


def thanh_vien() -> list[dict]:
    return json.loads((GOC / "thanh_vien.json").read_text(encoding="utf-8"))["thanh_vien"]


def thu_muc(id_: str) -> Path:
    p = PHIEN / id_
    if not p.exists():
        sys.exit(f"khong co phien {id_} (chay `mo` truoc)")
    return p


def goi_api(model: str, he_thong: str, nguoi_dung: str, max_tokens: int, thu_lai: int = 1) -> tuple[str, str]:
    """Tra (van_ban, ghi_chu). Dung STREAM: cong AI Box cat moi yeu cau khong-stream sau ~30 giay (HTTP 502), nen mo hinh 'suy nghi'
    sinh lau se hong. Mo hinh suy nghi co the het token truoc khi ra chu -> tang token 1 lan."""
    ghi = ""
    for lan in range(thu_lai + 1):
        body = json.dumps({"model": model, "temperature": 0.4, "max_tokens": max_tokens, "stream": True,
                           "messages": [{"role": "system", "content": he_thong}, {"role": "user", "content": nguoi_dung}]}).encode()
        h = {"Content-Type": "application/json"}
        if KHOA:
            h["Authorization"] = f"Bearer {KHOA}"
        txt = ""
        try:
            with urllib.request.urlopen(urllib.request.Request(f"{BASE}/chat/completions", data=body, headers=h), timeout=180) as r:
                for dong in r:
                    dong = dong.decode("utf-8", "replace").strip()
                    if not dong.startswith("data:") or dong.endswith("[DONE]"):
                        continue
                    try:
                        ch = json.loads(dong[5:]).get("choices") or []
                    except ValueError:
                        continue
                    if ch:
                        txt += (ch[0].get("delta") or {}).get("content") or ""
            txt = txt.strip()
            if txt:
                return txt, ghi
            ghi = f"content rong o lan {lan + 1} (het token vi suy nghi); "
            max_tokens = int(max_tokens * 1.8)
        except Exception as e:  # noqa: BLE001
            ghi = f"loi goi {model}: {str(e)[:160]}"
            if txt.strip():
                return txt.strip(), ghi + " (van ban bi cat giua chung)"
            time.sleep(3)
    return "", ghi


def ngu_canh(p: Path) -> str:
    s = "# ĐỀ BÀI\n" + doc(p / "00_DE_BAI.md")
    tl = p / "tai_lieu"
    if tl.exists():
        for f in sorted(tl.glob("*.md")):
            t = doc(f)
            s += f"\n\n# TÀI LIỆU ĐÍNH KÈM: {f.name}\n" + (t[:GIOI_HAN_TAI_LIEU] + ("\n...[cắt bớt]" if len(t) > GIOI_HAN_TAI_LIEU else ""))
    return s


def viet(p: Path, vong: int, tv: dict, van_ban: str, ghi: str = ""):
    nd = f"<!-- thanh_vien: {tv['ten']} | vong: {vong} | mo_hinh: {tv.get('model', tv['loai'])} | {time.strftime('%Y-%m-%d %H:%M')} -->\n"
    if ghi:
        nd += f"<!-- ghi chu: {ghi} -->\n"
    (p / f"vong{vong}_{tv['ten']}.md").write_text(nd + (van_ban or "(KHÔNG CÓ VĂN BẢN — vắng mặt hoặc lỗi)") + "\n", encoding="utf-8")


def danh_sach_goi(chon: str | None, tat_ca: bool) -> list[dict]:
    """Chon agent loai api se duoc goi: --tu a,b  >  --tat-ca  >  mac_dinh_goi trong thanh_vien.json."""
    cac = json.loads((GOC / "thanh_vien.json").read_text(encoding="utf-8"))
    api = {t["ten"]: t for t in cac["thanh_vien"] if t["loai"] == "api"}
    if tat_ca:
        ten = list(api)
    elif chon:
        ten = [x.strip() for x in chon.split(",") if x.strip()]
    else:
        ten = cac.get("mac_dinh_goi") or list(api)
    xa_la = [x for x in ten if x not in api]
    if xa_la:
        sys.exit(f"khong co agent api ten: {', '.join(xa_la)}. Co: {', '.join(api)}")
    return [api[x] for x in ten]


def chay_vong(id_: str, vong: int, tvs: list[dict]):
    p = thu_muc(id_)
    print("  goi:", ", ".join(t["ten"] for t in tvs))
    boi_canh = ngu_canh(p)
    y1 = {}
    if vong == 2:
        for t in thanh_vien():
            f = p / f"vong1_{t['ten']}.md"
            if f.exists():
                y1[t["ten"]] = re.sub(r"^<!--.*?-->\n", "", doc(f), flags=re.S)[:GIOI_HAN_Y_KIEN]
        if not y1:
            sys.exit("chua co y kien vong 1")

    def mot(t):
        he = LUAT_CHUNG + f"\nVAI CUA BAN ({t['ten']}): {t['vai']}\n"
        if vong == 1:
            nd = boi_canh + "\n\n" + MAU_V1
        else:
            khac = "\n\n".join(f"===== Ý KIẾN VÒNG 1 của @{k} =====\n{v}" for k, v in y1.items())
            nd = boi_canh + "\n\n" + khac + f"\n\nBạn là @{t['ten']}. Thành viên khác: {', '.join('@'+k for k in y1 if k != t['ten'])}.\n" + MAU_V2
        txt, ghi = goi_api(t["model"], he, nd, int(t.get("max_tokens", 6000)))
        viet(p, vong, t, txt, ghi)
        return t["ten"], bool(txt), ghi

    with cf.ThreadPoolExecutor(max(1, len(tvs))) as ex:
        for ten, ok, ghi in ex.map(mot, tvs):
            print(f"  {ten:9s} {'OK ' if ok else 'LOI'} {ghi}")
    vang = [t["ten"] for t in thanh_vien() if t["loai"] != "api" and not (p / f"vong{vong}_{t['ten']}.md").exists()]
    if vang:
        print(f"  chua co van ban vong {vong} cua: {', '.join(vang)} (nap bang `them` hoac cho Grok ghi file qua git)")


def lap_truong(txt: str) -> str:
    m = re.search(r"LẬP TRƯỜNG(?: CẬP NHẬT)?\s*[:：]\s*\**\s*(ĐỒNG Ý|PHẢN ĐỐI|ĐỀ XUẤT KHÁC|CHƯA ĐỦ DỮ KIỆN)", txt, re.I)
    return m.group(1).upper() if m else "?"


def phan_bien(txt: str) -> list[tuple[str, str, str]]:
    return [(a, b.upper(), c.strip()) for a, b, c in re.findall(r"@(\w+)\s*[:：]\s*\**\s*(ĐỒNG Ý|BÁC BỎ|BỔ SUNG)\**\s*[—:\-–]*\s*(.*)", txt)]


def bien_ban_tho(id_: str):
    p = thu_muc(id_)
    ten = [t["ten"] for t in thanh_vien()]
    o = [f"# BIÊN BẢN THÔ — phiên {id_}", "", "_Tự gộp từ các văn bản; thư ký (Claude) viết `BIEN_BAN.md` dựa trên file này. Chủ tọa chốt ở `QUYET_DINH.md`._", "",
         "## Đề bài", doc(p / "00_DE_BAI.md").strip(), "", "## Lập trường (vòng 1 → vòng 2)", "", "| Thành viên | Vòng 1 | Vòng 2 |", "|---|---|---|"]
    for t in ten:
        v1, v2 = doc(p / f"vong1_{t}.md"), doc(p / f"vong2_{t}.md")
        o.append(f"| {t} | {lap_truong(v1) if v1 else '—'} | {lap_truong(v2) if v2 else '—'} |")
    o += ["", "## Ma trận phản biện vòng 2 (người nói → người bị nói)", "", "| Từ | Tới | Thái độ | Lý do |", "|---|---|---|---|"]
    for t in ten:
        for toi, thai_do, ly_do in phan_bien(doc(p / f"vong2_{t}.md")):
            o.append(f"| {t} | {toi} | {thai_do} | {ly_do[:260].replace('|', '/')} |")
    for vong, tieu_de in ((2, "Đề xuất cuối của từng thành viên (vòng 2)"), (1, "Ý chính vòng 1 (nếu chưa có vòng 2)")):
        o += ["", f"## {tieu_de}"]
        for t in ten:
            txt = re.sub(r"^<!--.*?-->\n", "", doc(p / f"vong{vong}_{t}.md"), flags=re.S).strip()
            if txt:
                o += ["", f"### @{t}", txt]
        if vong == 2 and any((p / f"vong2_{t}.md").exists() for t in ten):
            break
    (p / "BIEN_BAN_THO.md").write_text("\n".join(o) + "\n", encoding="utf-8")
    print("da ghi", p / "BIEN_BAN_THO.md")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="lenh", required=True)
    a = sp.add_parser("mo"); a.add_argument("id"); a.add_argument("de_bai"); a.add_argument("--tai-lieu", default="")
    for k in ("vong1", "vong2"):
        a = sp.add_parser(k); a.add_argument("id")
        a.add_argument("--tu", default="", help="chi goi cac agent nay, vd deepseek hoac deepseek,qwen")
        a.add_argument("--tat-ca", action="store_true", help="goi het agent api (kimi, glm, deepseek, qwen)")
    for k in ("bien-ban-tho", "trang-thai"):
        sp.add_parser(k).add_argument("id")
    a = sp.add_parser("them"); [a.add_argument(x) for x in ("id", "vong", "ten", "file")]
    a = sp.add_parser("chot"); a.add_argument("id"); a.add_argument("quyet_dinh")
    g = ap.parse_args()
    if g.lenh == "mo":
        p = PHIEN / g.id
        (p / "tai_lieu").mkdir(parents=True, exist_ok=True)
        (p / "00_DE_BAI.md").write_text(f"# Phiên {g.id}\n\n_Mở lúc {time.strftime('%Y-%m-%d %H:%M')}. Chủ tọa: chủ dự án._\n\n{g.de_bai}\n", encoding="utf-8")
        for f in [x for x in g.tai_lieu.split(",") if x.strip()]:
            src = Path(f)
            (p / "tai_lieu" / src.name).write_text(doc(src), encoding="utf-8")
        print("da mo", p)
    elif g.lenh in ("vong1", "vong2"):
        chay_vong(g.id, int(g.lenh[-1]), danh_sach_goi(g.tu, g.tat_ca))
    elif g.lenh == "them":
        p = thu_muc(g.id)
        txt = sys.stdin.read() if g.file == "-" else doc(Path(g.file))
        tv = next((t for t in thanh_vien() if t["ten"] == g.ten), {"ten": g.ten, "loai": "tay"})
        viet(p, int(g.vong), tv, txt.strip())
        print("da nap", p / f"vong{g.vong}_{g.ten}.md")
    elif g.lenh == "bien-ban-tho":
        bien_ban_tho(g.id)
    elif g.lenh == "chot":
        p = thu_muc(g.id)
        (p / "QUYET_DINH.md").write_text(f"# QUYẾT ĐỊNH CỦA CHỦ TỌA — phiên {g.id}\n\n_{time.strftime('%Y-%m-%d %H:%M')}_\n\n{g.quyet_dinh}\n", encoding="utf-8")
        print("da ghi", p / "QUYET_DINH.md")
    elif g.lenh == "trang-thai":
        p = thu_muc(g.id)
        for f in sorted(p.glob("*.md")):
            print(f"  {f.name:34s} {f.stat().st_size:7d} byte")


if __name__ == "__main__":
    main()
