"""Shared timing helpers: word times, and mouth movement from each character's actual voice (lip-sync on twos)."""
import numpy as np

from script import NAR
from timeline import TL
from voice import SR as VSR

S, E, W = TL.s, TL.e, TL.word
_env = {}


def _envelope(key):
    if key not in _env:
        a = np.abs(TL.lines[key]["wav"].astype(np.float32))
        hop = VSR // 12                                      # one value per drawing (on twos)
        n = len(a) // hop
        e = np.array([a[i * hop:(i + 1) * hop].mean() for i in range(n)])
        e = e / (np.percentile(e, 95) + 1e-9)
        _env[key] = np.clip(e, 0, 1)
    return _env[key]


def talk(T, who=NAR):
    """Mouth opening 0..1 for `who` at time T, stepped on twos like the drawings."""
    t2 = np.floor(T * 12 + 1e-6) / 12
    for key in TL.order:
        L = TL.lines[key]
        if L["who"] != who:
            continue
        if L["start"] <= t2 < L["end"]:
            e = _envelope(key)
            i = int((t2 - L["start"]) * 12)
            return float(e[min(i, len(e) - 1)])
    return 0.0


def speaking(T, key, pad=0.0):
    return TL.s(key) - pad <= T < TL.e(key) + pad
