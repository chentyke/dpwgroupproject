from __future__ import annotations

import ctypes
import gc
import sys


def trim_process_memory() -> None:
    gc.collect()
    if not sys.platform.startswith("linux"):
        return

    try:
        libc = ctypes.CDLL("libc.so.6")
        libc.malloc_trim(0)
    except Exception:
        return
