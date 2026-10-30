#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI mong: python tools/hang_cho_llm.py liet_ke|xem|tra_loi|thong_ke"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nhan.hang_cho_llm import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
