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
    a_ = L["wav"].astype(float)
    if L["voice"] != "af_heart":
        import bigband
        a_ = bigband.pa(a_, 24000)
    up = signal.resample_poly(a_, 48000, 24000)
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


print("explainer d7", rms(TL.s("d7"), TL.e("d7")), "hazards t2", rms(TL.s("t2"), TL.e("t2")),
      "loop u2", rms(TL.s("u2"), TL.e("u2")), "finale f1", rms(TL.s("f1"), TL.e("f1")), "grid", rms(0.9, C["go"]))
print("crash slow-mo", rms(C["crash"] + 0.3, C["crash"] + 0.65), "end card", rms(C["end_card"], C["end"] - 0.7))
