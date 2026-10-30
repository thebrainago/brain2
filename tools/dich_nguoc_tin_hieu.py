#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI: python tools/dich_nguoc_tin_hieu.py ... → nhan.dich_nguoc_tin_hieu"""
from __future__ import annotations
import runpy
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
if str(GOC) not in sys.path:
    sys.path.insert(0, str(GOC))
sys.argv[0] = str(GOC / "nhan" / "dich_nguoc_tin_hieu.py")
runpy.run_path(str(GOC / "nhan" / "dich_nguoc_tin_hieu.py"), run_name="__main__")
