"""Shared timing helpers: word times, and mouth movement from the actual voice (for lip-sync)."""
import numpy as np

from timeline import TL
from voice import SR as VSR

S, E, W = TL.s, TL.e, TL.word
FPS = 24
_env = {}


def _envelope(key):
    if key not in _env:
        a = np.abs(TL.lines[key]["wav"].astype(np.float32))
        hop = VSR // FPS
        n = len(a) // hop
        e = np.array([a[i * hop:(i + 1) * hop].mean() for i in range(n)])
        e = e / (np.percentile(e, 95) + 1e-9)
        _env[key] = np.clip(e, 0, 1)
    return _env[key]


def talk(T, who="host"):
    """Mouth opening 0..1 for the host (narrator lines) or the announcer (announcer lines) at time T."""
    for key in TL.order:
        L = TL.lines[key]
        is_ann = L["voice"] != "af_heart"
        if (who == "announcer") != is_ann:
            continue
        if L["start"] <= T < L["end"]:
            e = _envelope(key)
            i = int((T - L["start"]) * FPS)
            return float(e[min(i, len(e) - 1)])
    return 0.0
