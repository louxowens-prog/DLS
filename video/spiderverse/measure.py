"""Voice-vs-background per line: speech-band (300 Hz - 4 kHz) RMS of the voice stem over the music stem."""
import numpy as np

import audio as A
from timeline import TL

mix = A.build()
mu, vo = A.STEMS["music"], A.STEMS["vo"]
SR = A.SR


def band(x):
    return A.H._hp(A.H._lp(x.mean(axis=0) if x.ndim == 2 else x, 4000), 300)


bm, bv = band(mu), band(vo)
rows = []
for k in TL.order:
    a, b = int(TL.s(k) * SR), int(TL.e(k) * SR)
    rv = np.sqrt((bv[a:b] ** 2).mean()) + 1e-12
    rm = np.sqrt((bm[a:b] ** 2).mean()) + 1e-12
    rows.append((round(20 * np.log10(rv / rm), 1), k))
rows.sort()
print("lowest voice/background (dB):", rows[:6])
print("median:", np.median([r[0] for r in rows]))
L, R = mix
print("corr", round(np.corrcoef(L, R)[0, 1], 3))
