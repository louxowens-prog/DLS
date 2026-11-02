"""Mix checks: speech-band voice-to-background ratio per line, section levels and the silences."""
import sys
import wave

import numpy as np
from scipy import signal

import synth as S
from cues import C
from timeline import TL

w = wave.open("build/audio.wav")
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(float).mean(1) / 32767
vo = np.zeros(len(x))
for k in TL.order:
    L = TL.lines[k]
    up = signal.resample_poly(L["wav"].astype(float), 48000, 24000)
    i = int(L["start"] * 48000)
    j = min(len(x), i + len(up))
    vo[i:j] += up[:j - i]
vo = S._hp(vo, 70)
res = []
for k in TL.order:
    a, b = int(TL.s(k) * 48000), int(TL.e(k) * 48000)
    v, m = vo[a:b], x[a:b]
    g = (v @ m) / (v @ v + 1e-12)
    bg = m - g * v
    bb, vv = S._bp(bg, 300, 4000), S._bp(g * v, 300, 4000)
    res.append((round(10 * np.log10((vv ** 2).mean() / ((bb ** 2).mean() + 1e-12)), 1), k))
res.sort()
print("lowest voice/background (dB):", res[:6])


def rms(a, b):
    s = x[int(a * 48000):int(b * 48000)]
    return round(20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-12), 1)


print("speech", rms(TL.s("a1"), TL.e("a1")), "montage", rms(TL.s("g6"), TL.e("g6")),
      "finale gap", rms(C["finale"], TL.s("f1")), "hook hit", rms(0, 0.35))
print("silence 'but wait'", rms(C["wait"] + 0.05, C["wait"] + 0.4), "final silence gap", rms(TL.e("f2") + 0.02, C["end_card"] - 0.02))
