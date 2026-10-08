"""A free-jazz band synthesized from scratch: drum kit, distorted bass, piano clusters, a saxophone that
squeals, and noise hits. Nothing sampled.

free_drums() plays pulse-free drumming whose density follows an energy curve, which is how free-jazz
drummers (think Han Bennink, Milford Graves) work: washes of cymbal, snare rolls, tom avalanches, bass-drum
bombs, no steady backbeat.
"""
import numpy as np
from scipy import signal

SR = 48000


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def _bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi / (SR / 2), 0.99)], "band")
    return signal.lfilter(b, a, x)


def _hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def _lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), "low")
    return signal.lfilter(b, a, x)


_R = np.random.default_rng(42)


# ------------------------------------------------------------------ kit

def kick(amp=1.0, seed=0):
    t = t_axis(0.5)
    f = 48 + 110 * np.exp(-t / 0.035)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    click = _hp(np.random.default_rng(seed).normal(0, 1, len(t)), 2500) * np.exp(-t / 0.003) * 0.5
    return amp * (body + click)


def snare(amp=1.0, seed=0, tight=1.0):
    rng = np.random.default_rng(seed)
    t = t_axis(0.35)
    noise = _bp(rng.normal(0, 1, len(t)), 1200, 9000) * np.exp(-t / (0.11 * tight))
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.06) * 0.6 + np.sin(2 * np.pi * 330 * t) * np.exp(-t / 0.04) * 0.3
    return amp * (noise * 0.9 + tone)


def tom(f, amp=1.0, seed=0):
    rng = np.random.default_rng(seed)
    t = t_axis(0.7)
    ff = f * (1 + 0.35 * np.exp(-t / 0.04))
    body = np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t / 0.3)
    stick = _bp(rng.normal(0, 1, len(t)), 800, 5000) * np.exp(-t / 0.01) * 0.4
    return amp * (body + stick)


_METAL = [205.3, 304.4, 369.6, 522.7, 540.0, 800.0]


def metal(dur, decay, lo, hi, seed=0, amp=1.0):
    """808-style metallic cluster of detuned square waves, band-limited: hi-hats and cymbals."""
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    x = np.zeros(len(t))
    k = rng.uniform(1.9, 2.3)
    for f in _METAL:
        x += np.sign(np.sin(2 * np.pi * f * k * t + rng.uniform(0, 6)))
    x = _bp(x, lo, hi) + _bp(rng.normal(0, 1, len(t)), lo, hi) * 0.5
    return amp * x * np.exp(-t / decay)


def hat(amp=1.0, seed=0, open_=False):
    return metal(0.45 if open_ else 0.12, 0.18 if open_ else 0.03, 6500, 13000, seed, amp)


def ride(amp=1.0, seed=0):
    rng = np.random.default_rng(seed)
    t = t_axis(1.6)
    x = metal(1.6, 0.9, 3000, 11000, seed, 0.6)
    ping = np.sin(2 * np.pi * rng.uniform(4300, 4700) * t) * np.exp(-t / 0.5) * 0.25
    return amp * (x + ping)


def crash(amp=1.0, seed=0):
    rng = np.random.default_rng(seed)
    t = t_axis(2.4)
    x = metal(2.4, 1.2, 2500, 14000, seed, 0.7) + _bp(rng.normal(0, 1, len(t)), 3000, 12000) * np.exp(-t / 0.9)
    return amp * x


def free_drums(dur, energy, seed=0):
    """Pulse-free drumming. energy(t) -> 0..1 (a function of seconds) sets density and loudness."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros(n)

    def put(sig, t, g):
        i = int(t * SR)
        if 0 <= i < n:
            j = min(n, i + len(sig))
            out[i:j] += g * sig[: j - i]

    t = 0.0
    while t < dur:
        e = float(np.clip(energy(t), 0, 1))
        if e < 0.02:
            t += 0.05
            continue
        rate = 3 + 17 * e
        t += rng.exponential(1 / rate)
        r = rng.random()
        g = 0.35 + 0.65 * e * rng.uniform(0.6, 1.0)
        if r < 0.30:
            put(ride(seed=int(rng.integers(1e6))), t, 0.35 * g)
        elif r < 0.52:
            put(snare(seed=int(rng.integers(1e6)), tight=rng.uniform(0.6, 1.2)), t, 0.45 * g)
        elif r < 0.60 and e > 0.35:
            # a snare roll, crescendo
            m = int(rng.integers(5, 14))
            for k in range(m):
                put(snare(seed=int(rng.integers(1e6)), tight=0.5), t + k * rng.uniform(0.028, 0.045), 0.18 * g * (0.4 + k / m))
            t += m * 0.035
        elif r < 0.72:
            f = rng.choice([92, 118, 150, 196])
            put(tom(f, seed=int(rng.integers(1e6))), t, 0.5 * g)
        elif r < 0.78 and e > 0.5:
            # tom avalanche
            for k, f in enumerate([220, 180, 150, 118, 92]):
                put(tom(f, seed=int(rng.integers(1e6))), t + k * 0.06, 0.45 * g)
            t += 0.3
        elif r < 0.88:
            put(kick(seed=int(rng.integers(1e6))), t, 0.7 * g)
        elif r < 0.96:
            put(hat(seed=int(rng.integers(1e6)), open_=rng.random() < 0.3), t, 0.3 * g)
        else:
            put(crash(seed=int(rng.integers(1e6))), t, 0.3 * g)
    return out


# ------------------------------------------------------------------ bass, piano, sax, noise

def bass_note(f0, dur, amp=1.0, glide=0.0, drive=4.0, seed=0):
    """Distorted electric bass: saw + sub, pitch glide, tanh fuzz, a resonant low-pass."""
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    f = f0 * 2 ** (glide * np.clip(t / max(dur, 1e-3), 0, 1))
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = sum(((-1) ** (k + 1)) * np.sin(k * ph) / k for k in range(1, 18))
    x = saw * 0.7 + np.sin(ph) * 0.8
    env = np.minimum(1, t / 0.006) * np.exp(-t / max(0.2, dur * 0.8))
    x = np.tanh(drive * x * env) / np.tanh(drive)
    x = _lp(x, 1800) + _bp(x, 600, 1400) * 0.3
    x += _bp(rng.normal(0, 1, len(t)), 1500, 5000) * env * 0.03
    return amp * x


def free_bass(dur, energy, seed=0, root=40):
    """A bass line with no bar lines: chromatic walks, leaps, slides, and silences."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros(n)
    t, note = 0.0, root
    while t < dur:
        e = float(np.clip(energy(t), 0, 1))
        if e < 0.05:
            t += 0.1
            continue
        d = rng.uniform(0.12, 0.55) * (1.3 - e)
        step = rng.choice([-3, -2, -1, 1, 2, 3, 5, 7, -5, -7])
        note = int(np.clip(note + step, root - 7, root + 12))
        f = 440 * 2 ** ((note - 69) / 12)
        sig = bass_note(f, d * 1.3, glide=rng.choice([0, 0, 0, 0.08, -0.08, 0.25]), seed=int(rng.integers(1e6)))
        i = int(t * SR)
        j = min(n, i + len(sig))
        out[i:j] += (0.5 + 0.5 * e) * sig[: j - i]
        t += d + (rng.exponential(0.25) if rng.random() < 0.25 * (1 - e) else 0)
    return out


def piano(notes, dur=1.8, amp=1.0, seed=0):
    """Struck-string piano: stretched (inharmonic) partials, faster decay for higher partials, hammer thump."""
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    out = np.zeros(len(t))
    for m in notes:
        f = 440 * 2 ** ((m - 69) / 12)
        B = 0.0004
        for k in range(1, 16):
            fk = k * f * np.sqrt(1 + B * k * k)
            if fk > 12000:
                break
            out += (1 / k ** 1.2) * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6)) * np.exp(-t * (1.2 + 0.5 * k))
    out += _lp(rng.normal(0, 1, len(t)), 1200) * np.exp(-t / 0.01) * 0.6
    return amp * out / (np.max(np.abs(out)) + 1e-9)


def cluster_stab(center, width=6, dur=1.6, seed=0):
    return piano(list(range(center - width // 2, center + width // 2 + 1)), dur, seed=seed)


def sax(f0, dur, squeal=0.0, amp=1.0, seed=0):
    """Tenor-sax-like tone: reed buzz through two formants, breath, vibrato; `squeal` bends up into overblow."""
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    bend = 2 ** (squeal * np.clip((t - 0.1) / max(0.1, dur * 0.6), 0, 1))
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t / 0.3, 0, 1)
    f = f0 * bend * vib
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.zeros(len(t))
    for k in range(1, 30):
        fk = k * f0 * bend.mean()
        if fk > 10000:
            break
        form = np.exp(-((fk - 1100) / 500) ** 2) + 0.6 * np.exp(-((fk - 2600) / 700) ** 2) + 0.15
        x += form / k ** 0.7 * np.sin(k * ph)
    x = np.tanh(2.5 * x / (np.max(np.abs(x)) + 1e-9))
    x += _bp(rng.normal(0, 1, len(t)), 1500, 6000) * 0.15
    env = np.minimum(1, t / 0.04) * np.minimum(1, (dur - t) / 0.08)
    return amp * x * env


def noise_hit(dur=0.35, lo=300, hi=9000, amp=1.0, seed=0):
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    x = _bp(rng.normal(0, 1, len(t)), lo, hi) * np.exp(-t / (dur * 0.35))
    return amp * x / (np.max(np.abs(x)) + 1e-9)


def riser(dur=1.5, amp=1.0, seed=0):
    """Noise sweep upward: rising water."""
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    x = rng.normal(0, 1, len(t))
    out = np.zeros(len(t))
    blk = 2048
    for i in range(0, len(t), blk):
        k = i / len(t)
        lo = 200 + 3000 * k ** 2
        out[i:i + blk] = _bp(x[i:i + blk], lo, lo * 2.5)[: len(out[i:i + blk])]
    env = (t / dur) ** 1.5
    return amp * out * env / (np.max(np.abs(out * env)) + 1e-9)


def scratch(dur=0.4, amp=1.0, seed=0):
    """Record scratch: band-limited noise whose playback speed swings back and forth."""
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    src = _bp(rng.normal(0, 1, len(t) * 3), 400, 4000)
    pos = np.cumsum(1.5 + 1.4 * np.sin(2 * np.pi * 7 * t)).astype(int) % len(src)
    x = src[pos] * np.sin(np.pi * t / dur)
    return amp * x / (np.max(np.abs(x)) + 1e-9)


def ping(amp=1.0):
    """Phone notification: two soft sine tones."""
    t = t_axis(0.5)
    x = np.sin(2 * np.pi * 1318.5 * t) * np.exp(-t / 0.12) * (t < 0.2) + \
        np.sin(2 * np.pi * 1760 * t) * np.exp(-np.clip(t - 0.12, 0, None) / 0.2) * (t >= 0.12)
    return amp * x


def tick(amp=1.0):
    t = t_axis(0.05)
    return amp * np.sin(2 * np.pi * 2200 * t) * np.exp(-t / 0.006)


def bubbles(dur=1.2, amp=1.0, seed=0):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros(n)
    for _ in range(int(dur * 14)):
        f = rng.uniform(400, 1400)
        L = int(rng.uniform(0.03, 0.08) * SR)
        tt = np.arange(L) / SR
        b = np.sin(2 * np.pi * np.cumsum(f * (1 + 2.5 * tt / tt[-1])) / SR) * np.exp(-tt / 0.02)
        i = int(rng.uniform(0, dur - 0.1) * SR)
        out[i:i + L] += b[: n - i]
    return amp * out
