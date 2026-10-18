# -*- coding: utf-8 -*-
"""may_nha_tuy_chon.py - PHAN "MAY NHA" port tu the-brain: WARP + mo phong nguoi + DNS-over-HTTPS. TAT MAC DINH.

Chi dung tren MAY NHA cua chu du an (Windows, trinh duyet that cua chinh chu du an), KHONG dung tren box/cloud.
Bat bang hai dieu kien cung luc:  bien moi truong BRAIN_MAY_NHA=1  VA  os.name == 'nt'.
Thieu mot trong hai -> moi ham tra False / nem `ChuaBat`, khong lam gi.

Thanh phan (giu nguyen ma cu, chi boc them cong tat):
  * WARP: `nhan/day_chuyen.bat_warp()` goi `warp-cli connect` (Cloudflare WARP da cai o may nha). Ghi chu the-brain:
    Myfxbook bi nha mang chan DNS -> can WARP; nhung WARP DOI IP co the huy phien MQL5 va mql5.com chan dai IP WARP.
  * (NGHI HUU 18/10/2026, CAM DUNG) Mo phong nguoi `nghi_huu/simulator_nguoi.py` - trai luat khong vuot chong bot.
  * DNS vuot: `nhan/dns_vuot.py` (DoH cho ten mien bi ISP dau doc DNS, giu SNI/TLS that).
Luat brain2 (12/10/2026): box KHONG ne Cloudflare, KHONG VPN, KHONG trinh duyet an, KHONG gia nguoi. Nguon ghi
"BI CHAN - can chay may nha" trong reports/SEEKER_QUET_NGUON.md la viec cho may nha; chu du an tu quyet dinh co
chay cac cong cu nay hay khong va tu chiu trach nhiem ToS cua tung trang.
"""
from __future__ import annotations

import os


class ChuaBat(RuntimeError):
    pass


def duoc_bat() -> bool:
    return os.environ.get("BRAIN_MAY_NHA") == "1" and os.name == "nt"


def _can():
    if not duoc_bat():
        raise ChuaBat("may_nha_tuy_chon dang TAT (can BRAIN_MAY_NHA=1 tren Windows may nha)")


def bat_warp(in_ra=print) -> bool:
    if not duoc_bat():
        return False
    from nhan import day_chuyen as DC
    return bool(DC.bat_warp(in_ra=in_ra))


def tat_warp() -> bool:
    if not duoc_bat():
        return False
    import subprocess
    exe = r"C:\Program Files\Cloudflare\Cloudflare WARP\warp-cli.exe"
    return subprocess.run([exe, "disconnect"], capture_output=True).returncode == 0


def mo_phong_nguoi(url: str, **kw):
    """NGHI HUU 18/10/2026: `simulator_nguoi.py` (gia chuot/phim de qua chong bot) TRAI LUAT, da chuyen vao nghi_huu/.
    Ham nay chi con bao loi - khong goi bat ky bo vuot chan nao."""
    raise RuntimeError("mo_phong_nguoi da NGHI HUU (luat cam vuot Cloudflare / chong bot). Dung Browser MCP tren may nha.")


def dns_vuot():
    _can()
    from nhan import dns_vuot as DV
    return DV
