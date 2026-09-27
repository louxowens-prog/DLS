"""Instruments for a sweet 1970s pop score that keeps playing through a horror film. All synthesized (no samples).

band      a soft 70s kit (round kick, plate-reverbed snare, hats, tambourine), a bouncy electric bass, an electric
          piano, a grand piano, a string pad, a drawbar organ, a glockenspiel, 'ba-ba-ba' backing voices
the theme a gentle piano / music-box waltz, and a music box that can slow down and go out of tune
horror    a low detuned drone, scare hits (orchestra stab + timpani + cymbal), a heartbeat, whispers, a reverse swell
cartoon   boing, slide whistle, bike-horn honk, pop, wood block, cuckoo, clock tick and chime, a cat's meow and hiss,
          a stamp, a page turn, a camera click, typewriter keys
"""
import numpy as np
from scipy import signal

SR = 48000
BPM = 112.0
BEAT = 60.0 / BPM


def tx(d):
    return np.arange(int(max(0.0, d) * SR)) / SR


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), "low")
    return signal.lfilter(b, a, x)


def _hp(x, fc, order=2):
    b, a = signal.butter(order, max(10, fc) / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def _bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi / (SR / 2), 0.99)], "band")
    return signal.lfilter(b, a, x)


def _noise(n, seed=0):
    return np.random.default_rng(seed).normal(0, 1, n)


# ------------------------------------------------------------------ the band

def kick(amp=1.0, seed=0):
    t = tx(0.4)
    f = 55 + 70 * np.exp(-t / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    beater = _bp(_noise(len(t), seed), 800, 4000) * np.exp(-t / 0.006) * 0.25
    knock = np.sin(2 * np.pi * 160 * t) * np.exp(-t / 0.03) * 0.3
    return amp * np.tanh(1.6 * (body + beater + knock)) * 0.85


def snare(amp=1.0, seed=0):
    t = tx(0.5)
    tone = (np.sin(2 * np.pi * 185 * t) + 0.5 * np.sin(2 * np.pi * 330 * t)) * np.exp(-t / 0.05) * 0.5
    nz = _bp(_noise(len(t), seed), 1500, 9000) * np.exp(-t / 0.12) * 0.7
    return amp * (tone + nz)


def hat(amp=1.0, seed=0, open_=False):
    t = tx(0.35 if open_ else 0.08)
    x = _hp(_noise(len(t), seed), 7500) * np.exp(-t / (0.12 if open_ else 0.018))
    return amp * x * 0.4


def tambourine(amp=1.0, seed=0):
    t = tx(0.25)
    rng = np.random.default_rng(seed)
    x = np.zeros(len(t))
    for f in rng.uniform(6000, 11000, 6):
        x += np.sin(2 * np.pi * f * t + rng.uniform(0, 6))
    x = x * np.exp(-t / 0.06) * 0.15 + _hp(rng.normal(0, 1, len(t)), 6000) * np.exp(-t / 0.05) * 0.3
    return amp * x


def bass(m, dur, amp=1.0):
    """A round 70s electric bass: plucked, warm, a little growl on the attack."""
    t = tx(dur + 0.05)
    f = midi(m)
    ph = 2 * np.pi * f * t
    x = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    saw = _lp(2 * ((f * t) % 1.0) - 1, 900) * 0.3 * np.exp(-t / 0.08)
    env = np.exp(-t / 0.55) * np.clip(t / 0.004, 0, 1) * np.clip((dur + 0.05 - t) / 0.04, 0, 1)
    return amp * np.tanh(1.3 * (x + saw)) * env * 0.6


def epiano(notes, dur, amp=1.0, seed=0, bright=1.0):
    t = tx(dur + 0.6)
    rng = np.random.default_rng(seed)
    out = np.zeros(len(t))
    for m in notes:
        f = midi(m) * 2 ** (rng.normal(0, 3) / 1200)
        idx = 1.4 * bright * np.exp(-t / 0.35) + 0.2
        car = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
        tine = np.sin(2 * np.pi * f * 14.0 * t) * np.exp(-t / 0.04) * 0.1 * bright
        env = np.exp(-t / 1.3) * np.clip(t / 0.003, 0, 1) * np.clip((dur + 0.6 - t) / 0.4, 0, 1)
        out += (car + tine) * env
    trem = 1 + 0.15 * np.sin(2 * np.pi * 5.0 * t)
    return amp * out * trem / max(1, len(notes)) ** 0.6


def piano(notes, dur, amp=1.0, seed=0, detune=0.0):
    """A grand piano: stretched partials, each decaying faster the higher it is, a felt hammer thump."""
    t = tx(dur + 1.2)
    rng = np.random.default_rng(seed)
    out = np.zeros(len(t))
    for m in notes:
        f0 = midi(m) * 2 ** ((rng.normal(0, 2) + detune) / 1200)
        B = 0.0004
        for k in range(1, 9):
            fk = k * f0 * np.sqrt(1 + B * k * k)
            if fk > 12000:
                break
            out += np.sin(2 * np.pi * fk * t + rng.uniform(0, 6)) * (0.9 / k ** 1.1) * np.exp(-t / (1.6 / (1 + 0.45 * k)))
        out += _lp(rng.normal(0, 1, len(t)), 1200) * np.exp(-t / 0.01) * 0.08
    env = np.clip(t / 0.002, 0, 1) * np.clip((dur + 1.2 - t) / 0.3, 0, 1)
    return amp * out * env * 0.35 / max(1, len(notes)) ** 0.5


def strings(notes, dur, amp=1.0, seed=0):
    """A soft string section: detuned saws, slow bow attack, vibrato, low-passed warm."""
    t = tx(dur + 0.5)
    rng = np.random.default_rng(seed)
    out = np.zeros(len(t))
    for m in notes:
        for d in (-7, 0, 6):
            f = midi(m) * 2 ** (d / 1200)
            vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t + rng.uniform(0, 6))
            ph = np.cumsum(f * vib) / SR
            out += 2 * (ph % 1.0) - 1
    out = _lp(out, 2600)
    env = np.clip(t / 0.35, 0, 1) * np.clip((dur + 0.5 - t) / 0.5, 0, 1)
    return amp * out * env * 0.08 / max(1, len(notes)) ** 0.5


def organ(notes, dur, amp=1.0):
    t = tx(dur + 0.1)
    out = np.zeros(len(t))
    for m in notes:
        f = midi(m)
        for k, g in ((1, 1.0), (2, 0.6), (3, 0.35), (4, 0.25), (6, 0.1)):
            out += g * np.sin(2 * np.pi * f * k * t)
    lesl = 1 + 0.12 * np.sin(2 * np.pi * 6.4 * t)
    env = np.clip(t / 0.01, 0, 1) * np.clip((dur + 0.1 - t) / 0.08, 0, 1)
    return amp * out * lesl * env * 0.12 / max(1, len(notes)) ** 0.5


def glock(m, amp=1.0):
    t = tx(1.2)
    f = midi(m)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.5) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.08)
    return amp * x * 0.35


def voices(vowel, m, dur, amp=1.0, seed=0):
    """'Ba-ba-ba' backing singers: a breathy vowel with vibrato (formant filtered pulse train)."""
    t = tx(dur + 0.1)
    f = midi(m) * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * t))
    ph = np.cumsum(f) / SR
    src = np.zeros(len(t))
    for k in range(1, 18):
        src += np.sin(2 * np.pi * k * ph) / k
    src += _noise(len(t), seed) * 0.05
    F = {"a": (800, 1150, 2900), "u": (350, 600, 2700), "o": (450, 800, 2830), "i": (270, 2140, 2950)}[vowel]
    out = sum(_bp(src, f0 * 0.85, f0 * 1.15) * g for f0, g in zip(F, (1.0, 0.6, 0.25)))
    env = np.clip(t / 0.04, 0, 1) * np.clip((dur + 0.1 - t) / 0.08, 0, 1)
    return amp * out * env * 0.6


def music_box(notes, rate=None, amp=1.0, seed=0, detune=None):
    """A music box playing (note, beats) pairs. rate: callable u->playback speed (1 = normal) to slow it down;
    detune: callable u->cents off pitch. u runs 0..1 over the tune."""
    step = 0.3
    total = sum(b for _, b in notes)
    t_on, pos, u = [], 0.0, 0.0
    for m, b in notes:
        r = rate(u) if rate else 1.0
        t_on.append((pos, m, r, detune(u) if detune else 0.0))
        pos += b * step / max(r, 0.2)
        u += b / total
    out = np.zeros(int((pos + 2.0) * SR))
    rng = np.random.default_rng(seed)
    for (p, m, r, dc) in t_on:
        f = midi(m) * r ** 0.5 * 2 ** ((dc + rng.normal(0, 4)) / 1200)
        t = tx(1.6)
        x = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 3.02 * t) * np.exp(-t / 0.06)
             + 0.15 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.02)) * np.exp(-t / 0.7)
        x[:40] *= np.linspace(0, 1, 40)
        j = int(p * SR)
        out[j:j + len(x)] += x
    return amp * out * 0.28


# ------------------------------------------------------------------ horror

def drone(dur, root=29, amp=1.0, seed=0):
    """A low, rotting cluster: detuned saws a semitone apart, slowly beating, with a rumble."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    out = np.zeros(len(t))
    for m, d in ((root, 0), (root + 1, 9), (root + 7, -6), (root + 12, 4), (root + 13, -11)):
        f = midi(m) * 2 ** (d / 1200)
        out += 2 * ((f * t + rng.uniform()) % 1.0) - 1
    out = _lp(out, 500) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.23 * t))
    out += _lp(rng.normal(0, 1, len(t)), 120) * 0.6
    env = np.clip(t / 0.8, 0, 1) * np.clip((dur - t) / 0.8, 0, 1)
    return amp * out * env * 0.25


def scare(amp=1.0, seed=0, notes=(41, 42, 47, 53, 54, 60, 61), body=1.0):
    """The scare hit: a dissonant orchestra stab, a timpani, a cymbal crash and a low boom. body stretches the tail."""
    t = tx(2.2 * body)
    rng = np.random.default_rng(seed)
    st = np.zeros(len(t))
    for m in notes:
        for d in (-9, 0, 8):
            f = midi(m) * 2 ** (d / 1200)
            st += 2 * ((f * t + rng.uniform()) % 1.0) - 1
    st = _lp(st, 3200) * np.exp(-t / (0.6 * body)) * 0.08
    timp = np.sin(2 * np.pi * np.cumsum(70 + 40 * np.exp(-t / 0.05)) / SR) * np.exp(-t / (0.5 * body)) * 0.9
    crash = _hp(rng.normal(0, 1, len(t)), 4000) * np.exp(-t / (0.7 * body)) * 0.25
    boom = np.sin(2 * np.pi * np.cumsum(45 + 30 * np.exp(-t / 0.1)) / SR) * np.exp(-t / (0.9 * body)) * 0.7
    return amp * np.tanh(1.3 * (st + timp + crash + boom))


def heartbeat(n=4, bpm=70, amp=1.0):
    gap = 60 / bpm
    out = np.zeros(int((n * gap + 0.6) * SR))
    for k in range(n):
        for off, g in ((0.0, 1.0), (0.22, 0.7)):
            t = tx(0.25)
            x = np.sin(2 * np.pi * np.cumsum(50 + 30 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.09) * g
            j = int((k * gap + off) * SR)
            out[j:j + len(x)] += x
    return amp * np.tanh(2 * out) * 0.8


def whispers(dur, amp=1.0, seed=0):
    """Breathy, unintelligible whispering: filtered noise with syllable-rate envelopes, left and right."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    out = np.zeros((2, len(t)))
    for ch in range(2):
        nz = rng.normal(0, 1, len(t))
        syl = np.abs(np.sin(2 * np.pi * rng.uniform(3, 5) * t + rng.uniform(0, 6))) ** 3
        out[ch] = (_bp(nz, 1800, 6000) * 0.6 + _bp(nz, 400, 1200) * 0.3) * syl
    env = np.clip(t / 0.5, 0, 1) * np.clip((dur - t) / 0.5, 0, 1)
    return amp * out * env * 0.35


def reverse_swell(dur=1.2, amp=1.0, seed=0):
    x = _hp(_noise(int(dur * SR), seed), 2000) * np.exp(-tx(dur) / 0.4)
    return amp * x[::-1] * 0.5


# ------------------------------------------------------------------ cartoon & foley

def boing(amp=1.0):
    t = tx(0.6)
    f = 180 * (1 + 0.6 * np.sin(2 * np.pi * 14 * t) * np.exp(-t / 0.25)) * (1 + 0.8 * np.exp(-t / 0.05))
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.3) * 0.7


def slide_whistle(up=True, dur=0.5, amp=1.0):
    t = tx(dur)
    f = np.geomspace(500, 1800, len(t)) if up else np.geomspace(1800, 400, len(t))
    x = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.01 * np.sin(2 * np.pi * 6 * t))) / SR)
    x += _bp(_noise(len(t), 3), 800, 3000) * 0.08
    env = np.clip(t / 0.03, 0, 1) * np.clip((dur - t) / 0.06, 0, 1)
    return amp * x * env * 0.45


def honk(amp=1.0, n=1):
    """A bike horn: a squeezed reed, two quick honks."""
    out = []
    for k in range(n):
        t = tx(0.18)
        f = 380 * (1 + 0.05 * np.sin(2 * np.pi * 30 * t))
        ph = np.cumsum(f) / SR
        x = np.tanh(3 * np.sin(2 * np.pi * ph)) * np.clip(t / 0.01, 0, 1) * np.clip((0.18 - t) / 0.03, 0, 1)
        out.append(_bp(x, 300, 3000))
        out.append(np.zeros(int(0.06 * SR)))
    return amp * np.concatenate(out) * 0.6


def pop(amp=1.0):
    t = tx(0.08)
    f = 1200 * np.exp(-t / 0.02) + 300
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.02)


def woodblock(amp=1.0, f=900):
    t = tx(0.12)
    return amp * (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.3 * t)) * np.exp(-t / 0.025) * 0.8


def cuckoo(amp=1.0):
    """'Cu-ckoo': two soft whistle notes, a falling third."""
    out = []
    for m, d in ((81, 0.2), (77, 0.35)):
        t = tx(d)
        x = np.sin(2 * np.pi * midi(m) * t) + 0.2 * np.sin(4 * np.pi * midi(m) * t)
        out.append(x * np.clip(t / 0.02, 0, 1) * np.clip((d - t) / 0.08, 0, 1))
        out.append(np.zeros(int(0.05 * SR)))
    return amp * np.concatenate(out) * 0.5


def tick(amp=1.0, tock=False):
    t = tx(0.05)
    f = 1500 if tock else 2300
    return amp * (np.sin(2 * np.pi * f * t) + _bp(_noise(len(t), 1), 2000, 8000) * 0.5) * np.exp(-t / 0.006)


def clock_bell(amp=1.0, m=62):
    t = tx(2.5)
    f = midi(m)
    x = sum(np.sin(2 * np.pi * f * r * t) * g * np.exp(-t / d) for r, g, d in ((1, 1, 1.4), (2.0, 0.5, 0.8), (2.76, 0.4, 0.5), (5.4, 0.2, 0.2)))
    return amp * x * 0.35


def meow(amp=1.0, dur=0.75):
    """A cat's meow: a voice-like source gliding up and down, the mouth opening from 'ee' to 'ah' to 'oo'."""
    t = tx(dur)
    u = t / dur
    f0 = 520 + 380 * np.sin(np.pi * np.clip(u * 1.1, 0, 1)) - 120 * u
    ph = np.cumsum(f0) / SR
    src = sum(np.sin(2 * np.pi * k * ph) / k ** 0.9 for k in range(1, 14))
    f1 = np.interp(u, [0, 0.3, 0.7, 1], [400, 900, 800, 450])
    f2 = np.interp(u, [0, 0.3, 0.7, 1], [2300, 1500, 1200, 900])
    out = np.zeros(len(t))
    seg = SR // 50
    for i in range(0, len(t), seg):
        s = src[i:i + seg + 256]
        y = _bp(s, f1[i] * 0.8, f1[i] * 1.25) + 0.6 * _bp(s, f2[i] * 0.85, f2[i] * 1.15)
        out[i:i + seg] += y[:len(out[i:i + seg])]
    env = np.clip(t / 0.05, 0, 1) * np.clip((dur - t) / 0.2, 0, 1)
    return amp * _lp(out, 5000) * env * 0.8


def hiss(amp=1.0, dur=0.7):
    t = tx(dur)
    return amp * _bp(_noise(len(t), 11), 2500, 9000) * np.clip(t / 0.03, 0, 1) * np.exp(-t / 0.3) * 0.6


def stamp(amp=1.0):
    t = tx(0.3)
    x = np.sin(2 * np.pi * np.cumsum(90 + 60 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.07)
    x += _bp(_noise(len(t), 5), 200, 2000) * np.exp(-t / 0.02) * 0.6
    return amp * np.tanh(2 * x)


def page(amp=1.0, seed=0):
    t = tx(0.28)
    nz = _noise(len(t), seed)
    x = _bp(nz, 1500, 8000) * np.sin(np.pi * np.clip(t / 0.28, 0, 1)) ** 2 * 0.6
    slap = _bp(nz, 300, 3000) * np.exp(-np.clip(t - 0.2, 0, None) / 0.01) * (t > 0.2) * 0.8
    return amp * (x + slap)


def click(amp=1.0):
    """A camera shutter for the freeze frames."""
    out = np.zeros(int(0.12 * SR))
    for off in (0.0, 0.06):
        t = tx(0.03)
        x = _bp(_noise(len(t), 7), 1500, 9000) * np.exp(-t / 0.005)
        j = int(off * SR)
        out[j:j + len(x)] += x
    return amp * out


def keys(n, gap=0.09, amp=1.0, seed=0):
    rng = np.random.default_rng(seed)
    out = np.zeros(int((n * gap + 0.2) * SR))
    for k in range(n):
        t = tx(0.05)
        x = _bp(rng.normal(0, 1, len(t)), 1000, 6000) * np.exp(-t / 0.008) + np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.01) * 0.3
        j = int((k * gap + rng.uniform(-0.02, 0.02)) * SR)
        j = max(0, j)
        out[j:j + len(x)] += x
    return amp * out * 0.6


def whoosh(dur=0.4, up=True, seed=0, amp=1.0):
    t = tx(dur)
    n = _noise(len(t), seed)
    out = np.zeros(len(t))
    fc = np.geomspace(300, 6000, 10) if up else np.geomspace(6000, 300, 10)
    seg = len(t) // 10 + 1
    for k in range(10):
        a, b = k * seg, min(len(t), (k + 1) * seg + 400)
        out[a:b] += _bp(n[a:b], fc[k] * 0.6, fc[k] * 1.4)[: b - a]
    return amp * out * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.3 * 0.8


def sting(notes=(77, 81, 84), amp=1.0):
    """A sweet 'ta-da' for the cheerful whiplash cuts: glockenspiel and a string swell."""
    n = int(1.6 * SR)
    out = np.zeros(n)
    for i, m in enumerate(notes):
        g = glock(m, 1.0)
        j = int(i * 0.06 * SR)
        out[j:j + len(g)] += g[: n - j]
    s = strings([m - 12 for m in notes], 0.8, 1.0)
    out[:len(s)] += s[:n]
    return amp * out


def projector(dur, amp=1.0):
    """The film running through the gate: a soft rhythmic clatter at 24 frames a second."""
    t = tx(dur)
    clat = (np.sin(2 * np.pi * 24 * t) > 0.6).astype(float)
    x = _bp(_noise(len(t), 21), 800, 4000) * clat * 0.25 + _lp(_noise(len(t), 22), 300) * 0.15
    return amp * x
