# -*- coding: utf-8 -*-
"""Hàng đợi việc qua git (03/11/2026) — máy nhà (Windows, MT5, XM) lấy việc, chạy, đẩy kết quả; box sinh việc.

Cấu trúc:
  hang_doi/can_test/<id>.json        việc chờ (spec)
  hang_doi/dang_lam_<may>/<id>.json  việc máy <may> đã nhận (khoá = commit đã push được)
  hang_doi/da_test/<id>.json         việc xong + "ket_qua"
  hang_doi/so_cai.jsonl              sổ cái: mỗi lần nhận/xong/hỏng thêm một dòng
Khoá: nhận việc = git mv can_test -> dang_lam_<may> + commit + push. Push bị từ chối (máy khác nhanh hơn) -> bỏ commit
local, pull --ff-only, chọn việc khác. KHÔNG force push, KHÔNG rebase/autostash. Chỉ dùng trên bản clone RIÊNG của thợ
(có tệp .tho_mt5_clone) vì có `reset --hard origin/<nhánh>` để bỏ commit local CHƯA push của chính thợ.

Spec việc (JSON):
  id, loai: mt5_backtest | mql5_demo_download | myfxbook_fetch, uu_tien (lớn = làm trước), uoc_phut (ước mỗi lần chạy),
  mt5_backtest: che_do ong_dan_csv|ea_goc, ea_file, ma, tf, tu, den, model(4 = tick thật), von, tien, don_bay,
                ts (input EA), tham_so_lot (tên input lot), he_so_lot [k...], csv_vao (ong_dan_csv)
  mql5_demo_download: url_product, ten_product, tin_hieu_id, ma, tf
  myfxbook_fetch: url
"""
from __future__ import annotations
import datetime as dt
import json
import subprocess
import time
from pathlib import Path

LOAI = ("mt5_backtest", "mql5_demo_download", "myfxbook_fetch")
TRUONG_BAT_BUOC = {"mt5_backtest": ("ea_file", "ma", "tf", "tu", "den", "he_so_lot"),
                   "mql5_demo_download": ("url_product",), "myfxbook_fetch": ("url",)}


def bay_gio() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def kiem_spec(v: dict) -> list[str]:
    loi = []
    if not v.get("id") or not str(v["id"]).replace("_", "").replace("-", "").isalnum():
        loi.append("id rỗng / ký tự lạ")
    if v.get("loai") not in LOAI:
        loi.append("loai lạ: %s" % v.get("loai"))
        return loi
    loi += ["thiếu %s" % k for k in TRUONG_BAT_BUOC[v["loai"]] if v.get(k) in (None, "", [])]
    if v["loai"] == "mt5_backtest":
        if any(float(k) <= 0 for k in v.get("he_so_lot") or []):
            loi.append("he_so_lot phải > 0")
        if v.get("che_do") == "ong_dan_csv" and not v.get("csv_vao"):
            loi.append("ong_dan_csv cần csv_vao")
    return loi


def uoc_gio(v: dict) -> float:
    n = len(v.get("he_so_lot") or [1]) if v.get("loai") == "mt5_backtest" else 1
    return n * float(v.get("uoc_phut") or 10) / 60.0


class HangDoi:
    def __init__(self, goc: Path, may: str, git=None, nhanh: str = "main", log=print):
        self.goc, self.may, self.nhanh, self.log = Path(goc), may, nhanh, log
        self.hd = self.goc / "hang_doi"
        self._git = git or self._git_that

    # ---------- git ----------
    def _git_that(self, *a: str) -> tuple[int, str]:
        r = subprocess.run(["git", *a], cwd=str(self.goc), capture_output=True, text=True, encoding="utf-8", errors="replace")
        return r.returncode, (r.stdout + r.stderr).strip()

    def dong_bo(self) -> bool:
        """Kéo bản mới nhất. Chỉ ff-only; lệch (do commit local chưa push của chính thợ) -> bỏ commit local."""
        for lan in range(5):
            c, _ = self._git("fetch", "origin", self.nhanh)
            if c == 0:
                c, out = self._git("merge", "--ff-only", "origin/" + self.nhanh)
                if c == 0:
                    return True
                self._git("reset", "--hard", "origin/" + self.nhanh)    # clone riêng: chỉ mất commit local chưa push của thợ
                return True
            time.sleep(min(60, 5 * 2 ** lan))
        return False

    def giao_dich(self, ap_dung, thong_diep: str, lan_toi_da: int = 6) -> bool:
        """dong_bo -> ap_dung() (sửa tệp, trả danh sách đường dẫn hoặc False nếu không còn hợp lệ) -> commit -> push.
        Push hỏng -> dong_bo (bỏ commit local) rồi làm lại từ đầu."""
        for lan in range(lan_toi_da):
            if not self.dong_bo():
                continue
            tep = ap_dung()
            if tep is False:
                return False
            self._git("add", "-A", "--", *[str(p) for p in tep])
            c, out = self._git("commit", "-m", thong_diep, "--", *[str(p) for p in tep])
            if c != 0 and "nothing" in out:
                return True
            c, out = self._git("push", "origin", "HEAD:" + self.nhanh)
            if c == 0:
                return True
            self.log("push bị từ chối (lần %d) -> đồng bộ lại" % (lan + 1))
            time.sleep(3 + 2 * lan)
        return False

    # ---------- hàng đợi ----------
    def thu_muc(self, ten: str) -> Path:
        p = self.hd / ten
        p.mkdir(parents=True, exist_ok=True)
        return p

    def ds_cho(self) -> list[dict]:
        out = []
        for f in sorted(self.thu_muc("can_test").glob("*.json")):
            try:
                v = json.loads(f.read_text(encoding="utf-8"))
            except ValueError:
                continue
            if not kiem_spec(v):
                out.append(v)
        return sorted(out, key=lambda v: (-float(v.get("uu_tien") or 0), v["id"]))

    def dang_lam_cua_toi(self) -> list[dict]:
        return [json.loads(f.read_text(encoding="utf-8")) for f in sorted(self.thu_muc("dang_lam_" + self.may).glob("*.json"))]

    def _so_cai(self, su_kien: str, v: dict, them: dict | None = None) -> Path:
        p = self.hd / "so_cai.jsonl"
        rec = {"luc": bay_gio(), "may": self.may, "su_kien": su_kien, "id": v["id"], "loai": v.get("loai")}
        rec.update(them or {})
        with p.open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return p

    def nhan(self, chap_nhan=lambda v: True) -> dict | None:
        """Nhận việc ưu tiên cao nhất mà thợ làm được. Trả spec hoặc None (hết việc)."""
        da_thu: set = set()
        for _ in range(10):
            self.dong_bo()
            ung = [v for v in self.ds_cho() if v["id"] not in da_thu and chap_nhan(v)]
            if not ung:
                return None
            v = ung[0]; da_thu.add(v["id"])
            kq: dict = {}

            def ap():
                src = self.hd / "can_test" / (v["id"] + ".json")
                if not src.exists():
                    return False                                       # máy khác đã nhận
                spec = json.loads(src.read_text(encoding="utf-8"))
                spec.update({"may": self.may, "nhan_luc": bay_gio()})
                dst = self.thu_muc("dang_lam_" + self.may) / src.name
                dst.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
                src.unlink()
                kq["spec"] = spec
                return [src, dst, self._so_cai("nhan", spec)]
            if self.giao_dich(ap, "hang_doi: %s nhận %s" % (self.may, v["id"])):
                if kq.get("spec"):
                    return kq["spec"]
        return None

    def xong(self, v: dict, ket_qua: dict, trang_thai: str = "XONG", tep_them: dict | None = None) -> bool:
        """Chuyển dang_lam_<may> -> da_test kèm kết quả. tep_them {đường dẫn tương đối: nội dung str}."""
        def ap():
            src = self.hd / ("dang_lam_" + self.may) / (v["id"] + ".json")
            dst = self.thu_muc("da_test") / (v["id"] + ".json")
            out = dict(v); out.update({"trang_thai": trang_thai, "xong_luc": bay_gio(), "ket_qua": ket_qua})
            dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
            if src.exists():
                src.unlink()
            tep = [src, dst, self._so_cai(trang_thai.lower(), v, {"tom_tat": ket_qua.get("tom_tat")})]
            for rel, nd in (tep_them or {}).items():
                p = self.goc / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(nd, encoding="utf-8"); tep.append(p)
            return tep
        return self.giao_dich(ap, "hang_doi: %s %s %s" % (self.may, trang_thai.lower(), v["id"]))

    def them(self, specs: list[dict], thong_diep: str = "hang_doi: thêm việc") -> int:
        """Thêm việc (bỏ việc trùng id đã có ở bất kỳ thư mục)."""
        n = {"n": 0}

        def ap():
            co = {f.stem for f in self.hd.glob("*/*.json")}
            tep = []
            for v in specs:
                if kiem_spec(v) or v["id"] in co:
                    continue
                p = self.thu_muc("can_test") / (v["id"] + ".json")
                p.write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8"); tep.append(p)
                tep.append(self._so_cai("them", v)); n["n"] += 1
            return tep or False
        self.giao_dich(ap, thong_diep)
        return n["n"]


def ghi_cuc_bo(goc: Path, specs: list[dict]) -> int:
    """Box: ghi spec vào hang_doi/can_test (không git) — commit thủ công cùng thay đổi khác."""
    d = Path(goc) / "hang_doi" / "can_test"; d.mkdir(parents=True, exist_ok=True)
    co = {f.stem for f in (Path(goc) / "hang_doi").glob("*/*.json")}
    n = 0
    so = Path(goc) / "hang_doi" / "so_cai.jsonl"
    with so.open("a", encoding="utf-8", newline="\n") as f:
        for v in specs:
            loi = kiem_spec(v)
            if loi:
                raise ValueError("%s: %s" % (v.get("id"), loi))
            if v["id"] in co:
                continue
            (d / (v["id"] + ".json")).write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
            f.write(json.dumps({"luc": bay_gio(), "may": "box", "su_kien": "them", "id": v["id"], "loai": v["loai"]}, ensure_ascii=False) + "\n")
            n += 1
    return n
