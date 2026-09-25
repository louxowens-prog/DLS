"""Instruments for the soundtrack, all synthesized from scratch (no samples).

- brass(): ensemble trumpets/horns, additive, brighter as they get louder (the "blaze" of real brass)
- timpani(): modal drum with the inharmonic overtone ratios of a kettle drum
- organ(): pipe-organ pedal with 16'/8'/4' ranks
- cluster(): micropolyphonic choir/orchestra clusters in the manner of Ligeti (dense, drifting, no melody)
- breath(), hiss(), hum(), wind(), beep(), shatter(): the sound design
- reverb(): convolution with a synthetic hall impulse response
"""
import numpy as np
from scipy import signal

SR = 48000
_rng = np.random.default_rng(2001)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def adsr(n, a=0.02, d=0.1, s=0.8, r=0.2):
    e = np.ones(n) * s
    ia, idd, ir = int(a * SR), int(d * SR), int(r * SR)
    ia = min(ia, n)
    e[:ia] = np.linspace(0, 1, ia) ** 1.5 if ia else e[:ia]
    j = min(n, ia + idd)
    if j > ia:
        e[ia:j] = np.linspace(1, s, j - ia)
    if ir:
        k = max(0, n - ir)
        e[k:] *= np.linspace(1, 0, n - k) ** 2
    return e


def _lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), "low")
    return signal.lfilter(b, a, x)


def _hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def _bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi / (SR / 2), 0.99)], "band")
    return signal.lfilter(b, a, x)


def brass(f, dur, amp=1.0, players=4, horn=False, seed=0, rel=0.25):
    """Ensemble brass note. Spectral slope follows loudness (brighter when loud); players differ slightly in
    onset, tuning and drift, and the sustained tone swells, so the section does not sound like one oscillator."""
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    n = len(t)
    out = np.zeros(n)
    for p in range(players):
        lag = rng.uniform(0, 0.03)
        tt = np.clip(t - lag, 0, None)
        env = adsr(n, a=(0.05 if not horn else 0.11), d=0.18, s=0.78, r=rel)
        env = np.concatenate([np.zeros(int(lag * SR)), env])[:n]
        swell = 1 + 0.22 * np.clip((tt - 0.25) / max(0.3, dur - 0.5), 0, 1)
        pe = np.clip(env * swell * (0.85 + 0.15 * rng.random()), 0, 1.15)
        det = 2 ** (rng.normal(0, 5) / 1200)
        drift = 2 ** ((6 * np.sin(2 * np.pi * rng.uniform(0.2, 0.5) * t + rng.uniform(0, 6))) / 1200)
        scoop = 2 ** ((-35 * np.exp(-tt / 0.04)) / 1200)
        vib = 1 + 0.0028 * np.sin(2 * np.pi * rng.uniform(4.8, 5.6) * t + rng.uniform(0, 6)) * np.clip((tt - 0.45) / 0.5, 0, 1)
        freq = f * det * drift * scoop * vib
        ph = 2 * np.pi * np.cumsum(freq) / SR + rng.uniform(0, 6)
        slope = (2.5 if horn else 2.0) - (1.2 if horn else 1.6) * np.clip(pe, 0, 1)
        kmax = int(min(12500 if not horn else 6000, SR / 2 - 500) / f)
        v = np.zeros(n)
        for k in range(1, kmax + 1):
            form = 1 + (1.8 if not horn else 0.8) * np.exp(-((k * f - (1350 if not horn else 700)) / 750) ** 2)
            v += (k ** (-slope)) * form * np.sin(k * ph + rng.uniform(0, 0.4))
        blat = _bp(rng.normal(0, 1, n), 1200, 7000) * np.exp(-tt / 0.035) * (0.5 if not horn else 0.25) * (tt > 0)
        breath_ = _bp(rng.normal(0, 1, n), 1500, 6000) * 0.02 * pe
        out += (v + blat + breath_) * pe
    out /= players
    return amp * out / (np.max(np.abs(out)) + 1e-9)


def timpani(f, amp=1.0, dur=3.0, seed=0):
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    ratios = [1.0, 1.504, 1.742, 2.0, 2.245, 2.494, 2.8, 2.98]
    decays = [1.8, 1.2, 0.9, 0.75, 0.55, 0.45, 0.35, 0.3]
    gains = [1.0, 0.6, 0.35, 0.3, 0.18, 0.12, 0.08, 0.06]
    glide = 1 + 0.018 * np.exp(-t / 0.06)
    out = np.zeros(len(t))
    for r, d, g in zip(ratios, decays, gains):
        ph = 2 * np.pi * np.cumsum(f * r * glide) / SR + rng.uniform(0, 6)
        out += g * np.sin(ph) * np.exp(-t / d)
    thump = _lp(rng.normal(0, 1, len(t)), 900) * np.exp(-t / 0.018) * 1.2
    body = np.sin(2 * np.pi * f * 0.5 * t) * np.exp(-t / 0.25) * 0.25
    out = out + thump + body
    return amp * out / (np.max(np.abs(out)) + 1e-9)


def organ(notes, dur, amp=1.0, a=1.2, r=1.5):
    t = t_axis(dur)
    out = np.zeros(len(t))
    for m in notes:
        f = midi(m)
        for mult, g in ((0.5, 0.9), (1, 1.0), (2, 0.55), (3, 0.18), (4, 0.3), (6, 0.08), (8, 0.1)):
            if f * mult < 12000:
                out += g * np.sin(2 * np.pi * f * mult * t + mult)
    out *= adsr(len(t), a=a, d=0.2, s=1.0, r=r)
    return amp * out / (np.max(np.abs(out)) + 1e-9)


VOWELS = {  # (freq, bandwidth, gain) for a soprano/alto-ish choir
    "ah": [(800, 90, 1.0), (1150, 100, 0.5), (2900, 130, 0.25), (3900, 150, 0.12)],
    "oo": [(350, 70, 1.0), (600, 80, 0.25), (2700, 120, 0.05), (3800, 150, 0.03)],
    "eh": [(500, 70, 1.0), (1750, 100, 0.35), (2450, 120, 0.25), (3350, 150, 0.1)],
    "ee": [(300, 60, 1.0), (2300, 110, 0.3), (3000, 130, 0.25), (3700, 150, 0.12)],
}


def _voice_table(f0, vowel, strings=False, size=4096):
    kmax = int(min(7000, SR / 2 - 1000) / f0)
    k = np.arange(1, max(2, kmax + 1))
    if strings:
        a = k ** -1.1 * (1 + 0.8 * np.exp(-((k * f0 - 2500) / 1500) ** 2))
    else:
        env = sum(g / (1 + ((k * f0 - F) / (bw / 2)) ** 2) for F, bw, g in VOWELS[vowel])
        a = (k ** -1.2) * (0.06 + env)
    ph = np.linspace(0, 2 * np.pi, size, endpoint=False)
    tab = (a[:, None] * np.sin(k[:, None] * ph[None, :] + _rng.uniform(0, 6, len(k))[:, None])).sum(0)
    return tab / (np.max(np.abs(tab)) + 1e-9)


def cluster(dur, lo, hi, voices=32, vowels=("ah", "oo"), strings=False, seed=1, entry=0.45,
            drift=35.0, vib=12.0, air=0.15, fades=(1.5, 4.0)):
    """Ligeti-style micropolyphony: many voices on microtonally dense pitches, entering one by one,
    each slowly gliding; the texture is a shimmering, dissonant block with no melody."""
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    n = len(t)
    out = np.zeros((2, n))
    for v in range(voices):
        m = rng.uniform(lo, hi)
        f0 = midi(m)
        tab = _voice_table(f0, rng.choice(vowels), strings)
        # slow glide: random walk of a few cents, smoothed
        steps = np.cumsum(rng.normal(0, 1, n // 4800 + 2))
        walk = np.interp(np.arange(n), np.linspace(0, n, len(steps)), steps)
        walk = walk / (np.max(np.abs(walk)) + 1e-9) * drift
        vb = vib * np.sin(2 * np.pi * rng.uniform(4.2, 5.8) * t + rng.uniform(0, 6))
        freq = f0 * 2 ** ((walk + vb) / 1200)
        ph = (np.cumsum(freq) / SR * len(tab) + rng.uniform(0, len(tab))) % len(tab)
        i0 = ph.astype(int)
        fr = ph - i0
        x = tab[i0] * (1 - fr) + tab[(i0 + 1) % len(tab)] * fr
        t_in = rng.uniform(0, entry) * dur
        fade = rng.uniform(*fades)
        e = np.clip((t - t_in) / fade, 0, 1) ** 2
        e *= 1 + 0.18 * np.sin(2 * np.pi * rng.uniform(0.05, 0.3) * t + rng.uniform(0, 6))
        pan = rng.uniform(0.15, 0.85)
        out[0] += x * e * np.sqrt(1 - pan)
        out[1] += x * e * np.sqrt(pan)
    if air:
        breathy = _bp(rng.normal(0, 1, n), 700, 3500) * air
        out += breathy[None] * np.clip(t / (dur * 0.6), 0, 1)
    return out / (np.max(np.abs(out)) + 1e-9)


def breath(dur, seed=3, rate=3.6):
    """Astronaut breathing inside a helmet: inhale/exhale noise shaped by a small resonant space."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros(n)
    tt = rng.uniform(0, 0.4)
    while tt < dur:
        for kind in ("in", "out"):
            L = rng.uniform(1.0, 1.3) if kind == "in" else rng.uniform(1.2, 1.6)
            m = int(L * SR)
            i = int(tt * SR)
            if i >= n:
                break
            x = rng.normal(0, 1, m)
            if kind == "in":
                x = _bp(x, 500, 2600) + 0.25 * _bp(x, 1700, 2000)
                e = np.sin(np.linspace(0, np.pi, m)) ** 1.6
                g = 0.7
            else:
                x = _bp(x, 250, 1500) + 0.2 * _bp(x, 900, 1100)
                e = np.minimum(np.linspace(0, 6, m), 1) * np.linspace(1, 0, m) ** 1.3
                g = 1.0
            j = min(n, i + m)
            out[i:j] += (x * e * g)[: j - i]
            tt += L + (rng.uniform(0.15, 0.35) if kind == "in" else rng.uniform(0.5, 0.9))
    return out / (np.max(np.abs(out)) + 1e-9)


def hiss(dur, seed=4):
    n = int(dur * SR)
    return _hp(np.random.default_rng(seed).normal(0, 1, n), 3500) * 0.2


def hum(dur, seed=5):
    t = t_axis(dur)
    rng = np.random.default_rng(seed)
    x = sum(g * np.sin(2 * np.pi * f * t) for f, g in ((55, 1.0), (110, 0.5), (165, 0.25), (220, 0.12)))
    x += _lp(rng.normal(0, 1, len(t)), 300) * 0.6
    return x / (np.max(np.abs(x)) + 1e-9)


def wind(dur, seed=6):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = np.cumsum(rng.normal(0, 1, n))
    x = _hp(x, 40)
    x = _lp(x, 700)
    gust = np.interp(np.arange(n), np.linspace(0, n, 12), rng.uniform(0.4, 1.0, 12))
    x *= gust
    x += _bp(rng.normal(0, 1, n), 1200, 2400) * 0.04 * gust
    return x / (np.max(np.abs(x)) + 1e-9)


def beep(f=2400, dur=0.06, amp=1.0):
    t = t_axis(dur)
    return amp * np.sin(2 * np.pi * f * t) * adsr(len(t), 0.004, 0.01, 0.8, dur * 0.4)


def tick(amp=1.0, seed=0):
    rng = np.random.default_rng(seed)
    t = t_axis(0.03)
    return amp * _hp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t / 0.004)


def shatter(dur=1.8, seed=7):
    """Glass: a bright crack, a cloud of short high partials, then falling shards."""
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    n = len(t)
    out = np.zeros(n)
    out += _hp(rng.normal(0, 1, n), 1500) * np.exp(-t / 0.05) * 1.2
    for _ in range(90):
        f = rng.uniform(2500, 11000)
        st = rng.exponential(0.12)
        i = int(st * SR)
        if i >= n:
            continue
        tt = t[: n - i]
        out[i:] += rng.uniform(0.1, 0.5) * np.sin(2 * np.pi * f * tt) * np.exp(-tt / rng.uniform(0.01, 0.08))
    for _ in range(40):
        st = 0.15 + rng.exponential(0.35)
        i = int(st * SR)
        if i >= n:
            continue
        tt = t[: n - i]
        f = rng.uniform(3000, 9000)
        out[i:] += rng.uniform(0.05, 0.25) * np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.02)
    out += _lp(rng.normal(0, 1, n), 300) * np.exp(-t / 0.03) * 0.8
    return out / (np.max(np.abs(out)) + 1e-9)


def impulse_response(rt60=2.6, dur=3.5, seed=8, predelay=0.02, damp=4500):
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    ir = np.zeros((2, len(t)))
    for c in range(2):
        x = rng.normal(0, 1, len(t)) * np.exp(-6.9 * t / rt60)
        lo = _lp(x, damp * 0.35)
        hi = x - lo
        x = lo + hi * np.exp(-t / 0.35)
        ir[c] = x
    pd = int(predelay * SR)
    ir = np.concatenate([np.zeros((2, pd)), ir], axis=1)
    return ir / np.sqrt((ir ** 2).sum(axis=1, keepdims=True))


_IR = {}


def reverb(x, wet=0.35, rt60=2.6):
    """x: (2, n) or (n,). Returns (2, n + tail)."""
    if x.ndim == 1:
        x = np.stack([x, x])
    key = round(rt60, 2)
    if key not in _IR:
        _IR[key] = impulse_response(rt60)
    ir = _IR[key]
    y = np.stack([signal.fftconvolve(x[c], ir[c]) for c in range(2)])
    dry = np.zeros_like(y)
    dry[:, : x.shape[1]] = x
    return dry * (1 - wet) + y * wet * 0.9
