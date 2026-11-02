"""Instruments and the sound collage for the daisy film, all synthesized (no samples): a harpsichord, a musette
accordion, a wordless choir, a sad trombone; creaking doll joints, dressmaker's shears, a teleprinter, a ratchet,
crackling paper fire, smashing glass, apple crunches, chomps, cream-pie splats, a clang, a buzzer, a glass clink, a
robot servo, paper tearing. The toy brass band, the organ, the music box and the clocks come from orch.py."""
import numpy as np

import orch as O
from orch import SR, _bp, _hp, _lp, _noise, midi, tx

_KS = {}


def harpsi(m, dur=1.4, amp=1.0, seed=0):
    """One harpsichord note: an 8-foot and a 4-foot string plucked by a quill (Karplus-Strong, kept bright)."""
    key = (m, round(dur, 2))
    if key not in _KS:
        n = int((dur + 0.05) * SR)
        out = np.zeros(n)
        for k, (mm, g) in enumerate(((m, 1.0), (m + 12, 0.4))):
            f = midi(mm) * (1 + 0.0008 * k)
            p = max(2, int(round(SR / f)))
            rng = np.random.default_rng(seed + mm * 3 + k)
            b = _hp(rng.uniform(-1, 1, p * 4), 700)[-p:]
            b /= np.abs(b).max() + 1e-9
            damp = 0.9992 if mm < 55 else (0.9985 if mm < 72 else 0.997)
            rows = []
            for _ in range(n // p + 1):
                rows.append(b)
                b = (0.7 * b + 0.3 * np.roll(b, -1)) * damp
            out += g * np.concatenate(rows)[:n]
        t = tx(n / SR)[:n]
        click = _bp(_noise(n, seed + 5), 2000, 7000) * np.exp(-t / 0.003) * 0.4
        env = np.clip((dur + 0.05 - t) / 0.05, 0, 1)
        _KS[key] = (out + click) * env
    return amp * _KS[key] * 1.0


def musette(notes, dur, amp=1.0, seed=0):
    """A Paris musette accordion: three reeds per note, one flat, one true, one sharp, beating against each other."""
    t = tx(dur + 0.08)
    out = np.zeros(len(t))
    for m in notes:
        for d in (-12, 0, 13):
            f = midi(m) * 2 ** (d / 1200)
            ph = (f * t + np.random.default_rng(seed + int(m) * 7 + d).uniform()) % 1.0
            out += np.where(ph < 0.3, 1.0, -0.43)
    out = _lp(out - out.mean(), 3000)
    env = np.clip(t / 0.025, 0, 1) * np.clip((dur + 0.08 - t) / 0.06, 0, 1)
    return amp * out * env * 0.06 / max(1, len(notes)) ** 0.5


def choir(notes, dur, amp=1.0, vowel="a", seed=0, attack=0.3, gliss=0.0):
    """A wordless choir: three singers on every note, a little apart in pitch and vibrato; gliss in semitones."""
    n = int((dur + 0.1) * SR)
    out = np.zeros(n)
    for i, m in enumerate(notes):
        for k, dc in enumerate((-0.09, 0.0, 0.08)):
            v = O.voices(vowel, m + dc, dur, 1.0, seed=seed + 7 * i + k) if not gliss else _gliss_voice(vowel, m + dc, dur, gliss, seed + 7 * i + k)
            out[: len(v)] += v[:n]
    t = tx(n / SR)[:n]
    env = np.clip(t / attack, 0, 1) * np.clip((dur + 0.1 - t) / 0.25, 0, 1)
    return amp * out * env * 0.18 / max(1, len(notes)) ** 0.5


def _gliss_voice(vowel, m, dur, gliss, seed):
    t = tx(dur + 0.1)
    f = midi(m) * 2 ** (gliss * np.clip(t / dur, 0, 1) / 12) * (1 + 0.012 * np.sin(2 * np.pi * 6.5 * t))
    ph = np.cumsum(f) / SR
    src = sum(np.sin(2 * np.pi * k * ph) / k for k in range(1, 16)) + _noise(len(t), seed) * 0.05
    F = {"a": (800, 1150, 2900), "u": (350, 600, 2700), "o": (450, 800, 2830), "i": (270, 2140, 2950)}[vowel]
    return sum(_bp(src, f0 * 0.85, f0 * 1.15) * g for f0, g in zip(F, (1.0, 0.6, 0.25))) * 0.6


def trumpet(m, dur, amp=1.0, seed=0):
    return O.brass([m], dur, amp, seed=seed, bright=1.3)


def sad_trombone(amp=1.0):
    """Wah, wah, wah, waaah."""
    out = np.zeros(int(2.4 * SR))
    for i, (m, d) in enumerate(((53, 0.36), (52, 0.36), (51, 0.36), (50, 1.1))):
        x = O.brass([m], d, 1.0, seed=i, bright=0.5)
        if i == 3:
            t = tx(len(x) / SR)[: len(x)]
            x = x * (1 + 0.35 * np.sin(2 * np.pi * 6 * t) * np.clip((t - 0.15) / 0.3, 0, 1))
        j = int(i * 0.42 * SR)
        out[j:j + len(x)] += x[: len(out) - j]
    return amp * _lp(out, 1800) * 1.4


# ------------------------------------------------------------------ the collage

def joint(amp=1.0, seed=0, dur=None):
    """A doll's wooden joint: a short, dry stick-slip creak."""
    rng = np.random.default_rng(seed)
    d = dur or rng.uniform(0.11, 0.2)
    t = tx(d)
    f0 = rng.uniform(420, 820)
    f = f0 * (1 + rng.uniform(-0.3, 0.4) * t / d)
    rate = rng.uniform(45, 95)
    slip = np.maximum(0, np.sin(2 * np.pi * np.cumsum(np.full(len(t), rate) * (1 + 0.2 * rng.normal(0, 1, len(t)).cumsum() / np.sqrt(len(t)))) / SR)) ** 6
    src = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (0.25 + slip) + 0.6 * _noise(len(t), seed) * slip
    x = _bp(src, f0 * 0.8, min(9000, f0 * 5))
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 0.5
    return amp * x * env * 0.45


def snip(amp=1.0, seed=0):
    """Dressmaker's shears closing: the shear of the blades, a steel ping, the click of the pivot."""
    rng = np.random.default_rng(seed)
    t = tx(0.14)
    r = rng.uniform(0.94, 1.06)
    shear = _bp(rng.normal(0, 1, len(t)), 2500, 9500) * np.exp(-t / 0.016) * np.clip((0.07 - t) / 0.01, 0, 1)
    ping = sum(np.sin(2 * np.pi * f * r * t) * np.exp(-t / 0.035) * g for f, g in ((3150, 1.0), (4710, 0.5), (6930, 0.3)))
    tc = np.clip(t - 0.055, 0, None)
    click = _bp(rng.normal(0, 1, len(t)), 900, 4000) * np.exp(-tc / 0.004) * (t >= 0.055)
    return amp * (0.7 * shear + 0.1 * ping + 0.6 * click)


def teleprinter(dur, amp=1.0, seed=0, rate=13.0):
    """Keys hammering at a steady clip over the motor's hum."""
    n = max(1, int(dur * rate))
    k = O.keys(n, 1 / rate, 1.0, seed)
    hum = O.whir(len(k) / SR + 0.01, 0.7, 50, seed)[: len(k)]
    return amp * (k + hum)


def ratchet(dur, rate=26.0, amp=1.0, seed=0):
    """A clockwork ratchet: hard little clicks, very regular."""
    out = np.zeros(int((dur + 0.06) * SR))
    rng = np.random.default_rng(seed)
    for i in range(int(dur * rate)):
        x = O.tick(rng.uniform(0.5, 1.0), tock=bool(i % 2))
        j = int((i / rate + rng.normal(0, 0.002)) * SR)
        j = max(0, j)
        out[j:j + len(x)] += x[: len(out) - j]
    return amp * out * 0.6


def crackle(dur, amp=1.0, seed=0):
    """Paper streamers burning: a soft roar and dry pops."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    out = _lp(rng.normal(0, 1, n), 700) * 0.25
    for _ in range(int(dur * 45)):
        j = int(rng.integers(0, max(1, n - 600)))
        L = int(rng.integers(40, 400))
        out[j:j + L] += _hp(rng.normal(0, 1, L + 64), 1200)[64:] * rng.uniform(0.2, 1.0) * np.exp(-np.arange(L) / (L / 4))
    i = np.arange(n)
    env = np.clip(i / (0.15 * SR), 0, 1) * np.clip((n - i) / (0.1 * SR), 0, 1)
    return amp * out * env * 0.7


def smash(amp=1.0, seed=0):
    """A glass hitting the floor: a burst and a scatter of shards ringing."""
    rng = np.random.default_rng(seed)
    t = tx(0.9)
    out = _hp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t / 0.05) * 0.8
    for _ in range(45):
        t0 = rng.exponential(0.07)
        f = rng.uniform(2500, 9500)
        tt = t - t0
        out += np.where(tt > 0, np.sin(2 * np.pi * f * tt) * np.exp(-np.clip(tt, 0, None) / rng.uniform(0.02, 0.14)), 0) * rng.uniform(0.1, 0.4)
    th = O.clunk(0.5, seed)
    out[: len(th)] += th[: len(out)] * 0.5
    return amp * out * 0.5


def crunch(amp=1.0, seed=0):
    """A bite of apple (or of a daisy): a crisp, granular crack."""
    rng = np.random.default_rng(seed)
    t = tx(0.28)
    out = np.zeros(len(t))
    nz = _bp(rng.normal(0, 1, len(t)), 900, 6500)
    for _ in range(26):
        j = int(rng.uniform(0, 0.13) * SR)
        L = int(rng.uniform(0.003, 0.014) * SR)
        out[j:j + L] += nz[j:j + L] * rng.uniform(0.3, 1.0)
    return amp * out * np.exp(-t / 0.12) * 0.9


def chomp(amp=1.0, seed=0):
    """A wet mouthful of cake."""
    rng = np.random.default_rng(seed)
    t = tx(0.22)
    x = _bp(rng.normal(0, 1, len(t)), 300, 2500) * np.exp(-t / 0.05) + np.sin(2 * np.pi * np.cumsum(180 - 300 * t) / SR) * np.exp(-t / 0.04) * 0.5
    return amp * np.tanh(2 * x) * 0.5


def splat(amp=1.0, seed=0):
    """A cream pie, a jelly, a cake landing: a squelch on a low thump."""
    t = tx(0.3)
    thump = np.sin(2 * np.pi * np.cumsum(110 * np.exp(-t / 0.05) + 50) / SR) * np.exp(-t / 0.06)
    x = O.squelch(1.0, seed, 0.3)
    n = min(len(x), len(thump))
    return amp * (x[:n] + 0.8 * thump[:n])


def clang(amp=1.0, seed=0):
    """A small brass clock hitting the floorboards."""
    t = tx(1.2)
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / d) * g for f, d, g in ((523, 0.5, 1.0), (1381, 0.3, 0.6), (2213, 0.18, 0.4), (3417, 0.1, 0.3)))
    c = O.clunk(0.7, seed)
    x[: len(c)] += c[: len(x)]
    return amp * x * 0.4


def buzzer(amp=1.0, dur=0.45):
    t = tx(dur)
    x = np.sign(np.sin(2 * np.pi * 110 * t)) + np.sign(np.sin(2 * np.pi * 116.5 * t))
    return amp * _lp(x, 2200) * np.clip(t / 0.01, 0, 1) * np.clip((dur - t) / 0.03, 0, 1) * 0.2


def clink(amp=1.0, seed=0):
    rng = np.random.default_rng(seed)
    t = tx(0.6)
    r = rng.uniform(0.9, 1.1)
    x = sum(np.sin(2 * np.pi * f * r * t) * np.exp(-t / d) * g for f, d, g in ((2810, 0.25, 1.0), (5320, 0.12, 0.5), (8130, 0.05, 0.3)))
    return amp * x * 0.3


def servo(dur, amp=1.0, f0=180.0, f1=320.0, seed=0, wild=0.0):
    """A robot arm's motor: a geared whine sliding between two pitches (wild > 0: lurching)."""
    rng = np.random.default_rng(seed)
    t = tx(dur)
    f = f0 + (f1 - f0) * 0.5 * (1 - np.cos(np.pi * np.clip(t / dur, 0, 1)))
    if wild:
        f = f * (1 + wild * np.sin(2 * np.pi * np.cumsum(rng.uniform(2, 7, len(t))) / SR))
    ph = np.cumsum(f) / SR
    x = sum(np.sin(2 * np.pi * k * ph) / k for k in range(1, 7)) + 0.2 * np.sign(np.sin(2 * np.pi * 9 * ph))
    env = np.clip(t / 0.04, 0, 1) * np.clip((dur - t) / 0.06, 0, 1)
    return amp * _bp(x, 150, 3000) * env * 0.15


def tear(amp=1.0, seed=0, dur=0.5):
    """Paper torn along its length."""
    rng = np.random.default_rng(seed)
    t = tx(dur)
    nz = _bp(rng.normal(0, 1, len(t)), 900, 7000)
    am = (rng.uniform(0, 1, len(t)) > 0.86).astype(float)
    am = np.convolve(am, np.ones(60) / 60, "same")
    return amp * nz * (0.3 + 2.2 * am) * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.4 * 0.5


def tiptoe(amp=1.0, seed=0):
    return O.woodblock(amp * 0.5, f=700 + 90 * (seed % 3))


def flutter(dur, amp=1.0, seed=0):
    """Paper scraps in the air."""
    from fxlib import paper_flutter
    return paper_flutter(dur, amp * 2.2, seed)
