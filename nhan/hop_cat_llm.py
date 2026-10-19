# -*- coding: utf-8 -*-
"""hop_cat_llm.py - CHAY MA PYTHON DO LLM DICH ra (ham `tin_hieu(df)`) trong TIEN TRINH CON co rao (19/10/2026).

Khong bao gio exec ma LLM trong tien trinh chinh. Duong di:
  1. `kiem_ast(ma)`: chi cho mot so dang cu phap; cam import, ten / thuoc tinh bat dau "_", ham nguy hiem
     (open/exec/eval/getattr/...), module he thong, doc/ghi file cua pandas (read_* / to_csv ...), shift am (nhin truoc).
  2. `chay(ma, df, cat)`: tien trinh con `python -I <file nay>` voi bien moi truong RONG (khong co khoa nao), han giay,
     (POSIX) tran bo nho + CPU; builtins rut gon; chi co np / pd / math. Tra tin hieu tren df day du va tren cac doan
     df[:k] (de kiem khong nhin truoc).
"""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

CAM_TEN = {"open", "exec", "eval", "compile", "__import__", "getattr", "setattr", "delattr", "globals", "locals", "vars",
           "input", "breakpoint", "help", "exit", "quit", "memoryview", "type", "object", "super", "classmethod",
           "staticmethod", "property", "os", "sys", "subprocess", "shutil", "socket", "pathlib", "builtins", "importlib",
           "pickle", "urllib", "requests", "http", "ctypes", "threading", "multiprocessing", "signal", "resource", "io",
           "dir", "id", "hash", "format", "bytes", "bytearray"}
CHO_TO = {"to_numpy", "tolist", "to_list"}
CAM_THUOC_TINH = {"eval", "query", "load", "save", "savetxt", "loadtxt", "fromfile", "tofile", "genfromtxt", "memmap",
                  "lib", "ctypeslib", "testing", "f2py", "distutils", "system", "popen", "pipe", "style", "plot"}
NUT_CHO = (ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.Return, ast.Assign, ast.AugAssign, ast.AnnAssign,
           ast.Expr, ast.Name, ast.Load, ast.Store, ast.Del, ast.Constant, ast.Attribute, ast.Subscript, ast.Slice,
           ast.Call, ast.keyword, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare, ast.IfExp, ast.If, ast.For, ast.While,
           ast.Break, ast.Continue, ast.Pass, ast.List, ast.Tuple, ast.Dict, ast.Set, ast.ListComp, ast.DictComp,
           ast.SetComp, ast.GeneratorExp, ast.comprehension, ast.Lambda, ast.Starred,
           ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.USub, ast.UAdd, ast.Not, ast.Invert,
           ast.And, ast.Or, ast.BitAnd, ast.BitOr, ast.BitXor, ast.LShift, ast.RShift, ast.MatMult,
           ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn)
BUILTIN_CHO = ["abs", "min", "max", "range", "len", "float", "int", "bool", "round", "sum", "zip", "enumerate", "list",
               "dict", "tuple", "set", "sorted", "reversed", "any", "all", "map", "filter", "isinstance", "str",
               "ValueError", "ZeroDivisionError", "None", "True", "False"]


def kiem_ast(ma: str) -> list[str]:
    """-> danh sach loi (rong = qua). Can dung MOT ham top-level `tin_hieu(df)`."""
    try:
        cay = ast.parse(ma or "")
    except SyntaxError as e:
        return ["loi cu phap: %s" % e]
    loi = []
    for n in ast.walk(cay):
        if not isinstance(n, NUT_CHO):
            loi.append("cam cu phap %s" % type(n).__name__)
            continue
        if isinstance(n, ast.Name) and (n.id.startswith("_") or n.id in CAM_TEN):
            loi.append("cam ten %s" % n.id)
        if isinstance(n, ast.Attribute):
            a = n.attr
            if a.startswith("_") or a in CAM_THUOC_TINH or a in CAM_TEN or a.startswith("read_") or \
                    (a.startswith("to_") and a not in CHO_TO):
                loi.append("cam thuoc tinh .%s" % a)
            if a == "shift":
                pass
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "shift":
            for x in list(n.args) + [k.value for k in n.keywords if k.arg in (None, "periods")]:
                if isinstance(x, ast.UnaryOp) and isinstance(x.op, ast.USub):
                    loi.append("shift am (nhin truoc)")
                elif isinstance(x, ast.Constant) and isinstance(x.value, (int, float)) and x.value < 0:
                    loi.append("shift am (nhin truoc)")
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and len(n.value) > 2000:
            loi.append("chuoi qua dai")
    top = [x for x in cay.body if not (isinstance(x, ast.Expr) and isinstance(getattr(x, "value", None), ast.Constant))]
    if not any(isinstance(x, ast.FunctionDef) and x.name == "tin_hieu" for x in top):
        loi.append("khong co ham top-level tin_hieu(df)")
    for x in top:
        if not isinstance(x, (ast.FunctionDef, ast.Assign)):
            loi.append("top-level chi duoc def / gan hang: %s" % type(x).__name__)
    return sorted(set(loi))


def chay(ma: str, df, cat: list[int] | None = None, han_giay: int = 90) -> dict:
    """-> {"ok": bool, "day_du": [..], "doan": {k: [..]}, "loi": str}. Chi goi sau khi kiem_ast qua."""
    loi = kiem_ast(ma)
    if loi:
        return {"ok": False, "loi": "; ".join(loi)}
    with tempfile.TemporaryDirectory() as d:
        p = Path(d)
        df[["open", "high", "low", "close"]].to_csv(p / "gia.csv", index_label="time")
        (p / "ma.py").write_text(ma, encoding="utf-8")
        (p / "cat.json").write_text(json.dumps([int(k) for k in (cat or [])]), encoding="utf-8")
        env = {k: os.environ[k] for k in ("PATH", "SYSTEMROOT", "TEMP", "TMP") if k in os.environ}   # KHONG co khoa
        env.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", PYTHONHASHSEED="0")

        def _gioi_han():                                # POSIX: tran bo nho 2 GB, CPU = han_giay
            try:
                import resource
                resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
                resource.setrlimit(resource.RLIMIT_CPU, (han_giay, han_giay))
            except Exception:
                pass
        try:
            r = subprocess.run([sys.executable, "-I", str(Path(__file__).resolve()), str(p)], cwd=d, env=env,
                               capture_output=True, text=True, timeout=han_giay,
                               preexec_fn=_gioi_han if os.name == "posix" else None)
        except subprocess.TimeoutExpired:
            return {"ok": False, "loi": "qua han %ds" % han_giay}
        try:
            kq = json.loads((p / "ra.json").read_text(encoding="utf-8"))
        except Exception:
            return {"ok": False, "loi": "tien trinh con loi: %s" % (r.stderr or r.stdout)[-300:]}
    kq["ok"] = not kq.get("loi")
    return kq


def _main(thu_muc: str) -> None:                       # chay BEN TRONG tien trinh con
    import math
    import builtins
    import numpy as np
    import pandas as pd
    p = Path(thu_muc)
    ra = {}
    try:
        df = pd.read_csv(p / "gia.csv", index_col="time", parse_dates=["time"])
        cat = json.loads((p / "cat.json").read_text(encoding="utf-8"))
        ma = (p / "ma.py").read_text(encoding="utf-8")
        bi = {k: getattr(builtins, k) for k in BUILTIN_CHO if hasattr(builtins, k)}
        g = {"__builtins__": bi, "np": np, "pd": pd, "math": math, "__name__": "llm"}
        exec(compile(ma, "<llm>", "exec"), g)          # noqa: S102 - da qua kiem_ast, builtins rut gon, tien trinh rieng

        def mot(x):
            s = g["tin_hieu"](x.copy())
            s = np.asarray(s, dtype=float).reshape(-1)
            if len(s) != len(x):
                raise ValueError("do dai %d != %d" % (len(s), len(x)))
            return np.sign(np.nan_to_num(s)).astype(int).tolist()
        ra["day_du"] = mot(df)
        ra["doan"] = {str(k): mot(df.iloc[:k]) for k in cat}
    except Exception as e:  # noqa: BLE001
        ra = {"loi": "%s: %s" % (type(e).__name__, str(e)[:300])}
    (p / "ra.json").write_text(json.dumps(ra), encoding="utf-8")


if __name__ == "__main__":
    _main(sys.argv[1])
