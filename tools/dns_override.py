# dns_override.py - VNPT often NXDOMAIN for fxblue/myfxbook; use 8.8.8.8 + static fallback
import re, socket, subprocess
_OV = {
    "www.myfxbook.com": "104.18.23.170",
    "myfxbook.com": "104.18.23.170",
    "api.fxblue.com": "13.248.219.22",
    "www.fxblue.com": "52.50.205.164",
}
def ensure(*hosts):
    for host in hosts:
        try:
            out = subprocess.check_output(["nslookup", host, "8.8.8.8"], text=True,
                                          stderr=subprocess.STDOUT, timeout=15)
            ips = [i for i in re.findall(r"Address:\s*(\d+\.\d+\.\d+\.\d+)", out)
                   if not i.startswith("8.8.")]
            if ips:
                _OV[host] = ips[0]
        except Exception:
            pass
    if not getattr(socket, "_brain_dns_patched", False):
        _orig = socket.getaddrinfo
        def _ga(host, *a, **k):
            return _orig(_OV.get(host, host), *a, **k)
        socket.getaddrinfo = _ga
        socket._brain_dns_patched = True
    return {h: _OV[h] for h in hosts if h in _OV}
