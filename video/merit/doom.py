"""Instruments for INELIGIBLE, a slow doom/drone score with 1980s synth pads. All synthesized, no samples.

doom      heavy distorted guitar power chords and palm-muted chugs (sawtooth and pulse strings, a pick, two gain
          stages, a speaker cabinet, double-tracked left and right), a sub-bass, a feedback squeal, big drums
synths    analog pads (detuned saws, a slow filter, chorus), an arpeggiator, a glass FM bell
the theme a fragile melody on a solo female voice ("ah", breathy, formant-synthesized) that comes back corrupted:
          wow and flutter, bit-crushing, reversal, detuning
sound     wind in the pines, a crackling fire, fluorescent hum, whispered chanting, heartbeats, breath, heavy metal
          impacts, door slams, distant engines, deep rumbles, notification chimes, a phone buzzing, a typewriter,
          a tape stopping
"""
import numpy as np
from scipy import signal

import instr as I
import orch as O
import synth82 as Y
from orch import SR, _bp, _hp, _lp, _noise, midi, tx

D, EB, E_, F, G_, A, BB, C = 38, 39, 40, 41, 43, 45, 46, 48       # guitar roots (D2 = 38)


def biquad(x, kind, f0, gain_db=0.0, q=0.8):
    A_ = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    al = np.sin(w0) / (2 * q)
    cw = np.cos(w0)
    if kind == "peak":
        b = [1 + al * A_, -2 * cw, 1 - al * A_]
        a = [1 + al / A_, -2 * cw, 1 - al / A_]
    elif kind == "notch":
        b = [1, -2 * cw, 1]
        a = [1 + al, -2 * cw, 1 - al]
    else:
        raise ValueError(kind)
    b, a = np.array(b) / a[0], np.array(a) / a[0]
    return signal.lfilter(b, a, x)


def _env(n, att, rel, dur_s):
    t = np.arange(n) / SR
    return np.clip(t / max(att, 1e-4), 0, 1) * np.clip((dur_s - t) / max(rel, 1e-4), 0, 1)


# ------------------------------------------------------------------ doom

def _string(m, dur, seed, palm=False, bend=0.0):
    t = tx(dur + 0.25)
    rng = np.random.default_rng(seed)
    out = np.zeros(len(t))
    for d in (-6, 0, 7):
        f = midi(m) * 2 ** (d / 1200) * (1 + 0.0015 * np.sin(2 * np.pi * rng.uniform(4, 6) * t + rng.uniform(0, 6)))
        if bend:
            f = f * 2 ** (bend * np.clip(t / 0.4, 0, 1) / 12)
        ph = np.cumsum(f) / SR + rng.uniform()
        saw = 2 * (ph % 1.0) - 1
        pulse = np.where((ph % 1.0) < 0.38, 1.0, -1.0)
        out += 0.6 * saw + 0.4 * pulse
    pick = _bp(rng.normal(0, 1, len(t)), 1800, 5000) * np.exp(-t / 0.008) * 2.0
    decay = np.exp(-t / (0.12 if palm else 3.5))
    return (out / 3 * decay + pick) * _env(len(t), 0.003, 0.12, dur + 0.25)


def _amp_cab(x, drive=22.0, palm=False):
    x = _hp(x, 90)
    x = biquad(x, "peak", 800, 4.0, 0.7)
    x = np.tanh(drive * x + 0.15) - np.tanh(0.15)
    x = np.tanh(2.2 * x)
    x = _lp(_lp(x, 5200, 2), 5200, 2)
    x = biquad(x, "peak", 110, 5.0, 1.0)
    x = biquad(x, "peak", 420, -5.0, 0.9)
    x = biquad(x, "peak", 2500, 3.0, 1.0)
    if palm:
        x = _lp(x, 1800)
    return x


def chord(root, dur, amp=1.0, palm=False, seed=0, drive=22.0, fifth=True, octave=True, bend=0.0):
    """A distorted power chord, double-tracked: (2, n) stereo."""
    takes = []
    for k in range(2):
        notes = [root] + ([root + 7] if fifth else []) + ([root + 12] if octave else [])
        x = sum(_string(m, dur, seed * 10 + k * 3 + i, palm=palm, bend=bend) for i, m in enumerate(notes))
        x = _amp_cab(x * 0.5, drive=drive, palm=palm)
        d = int((0.004 + 0.006 * k) * SR)
        takes.append(np.concatenate([np.zeros(d), x])[: len(x)])
    L, R = takes[0] * 0.95 + takes[1] * 0.3, takes[1] * 0.95 + takes[0] * 0.3
    return amp * 0.32 * np.stack([L, R])


def riff(bus, t0, t1, pattern, bpm=60.0, amp=1.0, seed=0, until=None):
    """Play [(root, beats, palm)] from t0, looping, until t1."""
    beat = 60.0 / bpm
    t, i = t0, 0
    while t < t1 - 0.05:
        root, beats, palm = pattern[i % len(pattern)]
        dur = beats * beat
        if root is not None:
            if palm:
                n = int(beats * 2)
                for k in range(n):
                    bus.add(chord(root, beat / 2 * 0.8, amp * 0.9, palm=True, seed=seed + i * 7 + k, octave=False), t + k * beat / 2, 1.0,
                            until=min(t1, until or t1) + 0.2)
            else:
                bus.add(chord(root, min(dur, t1 - t) + 0.1, amp, seed=seed + i), t, 1.0, until=(until or t1) + 0.6)
        t += dur
        i += 1


def sub(m, dur, amp=1.0, att=0.4, rel=0.8):
    t = tx(dur)
    f = midi(m)
    x = np.sin(2 * np.pi * f * t) + 0.18 * np.sin(4 * np.pi * f * t) + 0.06 * np.sin(6 * np.pi * f * t)
    return amp * 0.6 * x * _env(len(t), att, rel, dur)


def feedback(dur, f0=2400.0, amp=1.0, seed=0, rise=1.0):
    """A feedback squeal: a whistle that swells out of nowhere, wavers, climbs and saturates."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    f = f0 * (1 + 0.04 * rise * t / dur) * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) + 0.002 * rng.normal(0, 1, len(t)).cumsum() / np.sqrt(len(t)))
    ph = np.cumsum(f) / SR
    x = np.sin(2 * np.pi * ph) + 0.3 * np.sin(4 * np.pi * ph)
    env = (np.clip(t / dur, 0, 1) ** 2.2) * np.clip((dur - t) / 0.05, 0, 1)
    return amp * np.tanh(3.0 * x * env) * 0.4


def boom(amp=1.0, f0=48.0, dur=2.6):
    """A deep sub impact you feel: a falling sine and a noise thump."""
    t = tx(dur)
    f = f0 * (1 + 1.5 * np.exp(-t / 0.06))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.8)
    x += _lp(_noise(len(t), 3), 200) * np.exp(-t / 0.08) * 0.8
    return amp * np.tanh(1.5 * x) * 0.9


def tom(m, amp=1.0, seed=0):
    t = tx(1.2)
    f = midi(m) * (1 + 0.6 * np.exp(-t / 0.05))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35)
    skin = _bp(_noise(len(t), seed), 300, 3000) * np.exp(-t / 0.03) * 0.4
    return amp * np.tanh(1.8 * (body + skin)) * 0.8


def kick(amp=1.0, seed=0):
    t = tx(0.9)
    f = 42 + 90 * np.exp(-t / 0.04)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.4)
    click = _bp(_noise(len(t), seed), 1500, 6000) * np.exp(-t / 0.005) * 0.4
    return amp * np.tanh(2.0 * (body + click)) * 0.9


def crash(amp=1.0, dur=3.0, seed=4):
    return O.cymbal(amp, dur, swell=False, seed=seed)


# ------------------------------------------------------------------ synths

def pad(notes, dur, amp=1.0, cut=(400, 1800), att=1.2, rel=1.5, seed=0):
    """An analog pad, chorused into stereo."""
    x = Y.pad(notes, dur, 1.0, cut=cut, seed=seed, attack=att, release=rel, detune=12)
    d = int(0.017 * SR)
    t = np.arange(len(x)) / SR
    mod = (0.006 * SR) * (1 + np.sin(2 * np.pi * 0.4 * t))
    idx = np.clip(np.arange(len(x)) - d - mod, 0, len(x) - 1)
    wet = np.interp(idx, np.arange(len(x)), x)
    return amp * np.stack([x * 0.8 + wet * 0.5, x * 0.5 + wet * 0.8]) * 0.5


def arp(bus, t0, t1, notes, rate=8.0, amp=1.0, bright=2600, pan=0.5):
    """An arpeggiator: the notes cycling up and down at `rate` per second."""
    seq = notes + notes[-2:0:-1]
    k, t = 0, t0
    while t < t1:
        bus.add(Y.pluck(seq[k % len(seq)], 1.0, dur=0.22, bright=bright), t, amp * 0.5, pan=pan + 0.15 * np.sin(k * 0.7))
        t += 1.0 / rate
        k += 1


def bell(m, amp=1.0, dur=3.0, ratio=3.5):
    """A glass FM bell."""
    t = tx(dur)
    f = midi(m)
    idx = 2.4 * np.exp(-t / 0.5) + 0.3
    x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * ratio * t))
    return amp * x * np.exp(-t / (dur * 0.35)) * np.clip(t / 0.003, 0, 1) * 0.35


# ------------------------------------------------------------------ the theme

THEME = [(69, 1.5), (77, 0.5), (76, 1.0), (74, 1.5), (72, 0.5), (69, 2.0), (70, 1.0), (69, 2.5)]   # A F E D C A Bb A


def solo(m, dur, amp=1.0, vowel="a", seed=0, breath=0.18, vib=1.0):
    """A solo female voice on one vowel: a soft glottal source, three formants, vibrato blooming, breath."""
    t = tx(dur + 0.3)
    rng = np.random.default_rng(seed)
    vb = (0.0065 * vib) * np.clip((t - 0.25) / 0.5, 0, 1)
    f = midi(m) * (1 + vb * np.sin(2 * np.pi * 5.4 * t + rng.uniform(0, 6))) * (1 + 0.002 * np.sin(2 * np.pi * 0.7 * t))
    ph = np.cumsum(f) / SR
    src = sum(np.sin(2 * np.pi * k * ph) / k ** 1.6 for k in range(1, 22))
    src += _bp(rng.normal(0, 1, len(t)), 1200, 7000) * breath
    F = {"a": ((900, 1.0), (1350, 0.55), (2900, 0.22), (3800, 0.1)), "o": ((480, 1.0), (900, 0.5), (2800, 0.15), (3600, 0.06)),
         "u": ((350, 1.0), (700, 0.35), (2700, 0.1), (3500, 0.05))}[vowel]
    out = sum(_bp(src, f0 * 0.88, f0 * 1.12) * g for f0, g in F)
    env = _env(len(t), 0.12, 0.35, dur + 0.3)
    return amp * out * env * 0.9


def theme(notes=None, beat=0.62, amp=1.0, vowel="a", seed=0, transpose=0, breath=0.18):
    """The fragile melody, sung."""
    notes = notes or THEME
    total = sum(b for _, b in notes) * beat + 0.6
    out = np.zeros(int(total * SR) + SR)
    t = 0.0
    for i, (m, b) in enumerate(notes):
        if m is not None:
            x = solo(m + transpose, b * beat * 1.05, 1.0, vowel=vowel, seed=seed + i, breath=breath)
            j = int(t * SR)
            out[j:j + len(x)] += x[: len(out) - j]
        t += b * beat
    return amp * out


def wow(x, depth=30.0, rate=0.6, flutter=8.0):
    """Tape wow and flutter: the pitch sagging and wavering by up to `depth` cents."""
    t = np.arange(len(x)) / SR
    cents = depth * np.sin(2 * np.pi * rate * t) + flutter * np.sin(2 * np.pi * 7.3 * t)
    r = 2 ** (cents / 1200)
    pos = np.cumsum(r)
    pos = pos - pos[0]
    pos = pos * (len(x) - 1) / pos[-1]
    return np.interp(pos, np.arange(len(x)), x)


def crush(x, bits=5, hold=6):
    """Bit-crushed and sample-held: the melody as if read off a broken chip."""
    y = np.repeat(x[::hold], hold)[: len(x)]
    q = 2 ** bits
    m = np.abs(y).max() + 1e-9
    return np.round(y / m * q) / q * m


def detune(x, semis):
    r = 2 ** (semis / 12)
    return signal.resample(x, int(len(x) / r))


def broken(x, cut=0.75):
    """The melody stopping short, as if the tape snapped: the end reversed and torn off."""
    n = int(len(x) * cut)
    tail = x[n:n + int(0.6 * SR)][::-1] * np.linspace(1, 0, min(len(x) - n, int(0.6 * SR)))
    return np.concatenate([x[:n], tail])


def tape_stop(x, dur=0.6):
    """The last `dur` seconds slowing to a halt."""
    n = int(dur * SR)
    if len(x) <= n:
        return x
    head, tail = x[:-n], x[-n:]
    t = np.linspace(0, 1, n)
    rate = (1 - t) ** 1.5
    pos = np.cumsum(rate)
    pos = pos / pos[-1] * (n - 1) * 0.55
    return np.concatenate([head, np.interp(pos, np.arange(n), tail) * (1 - t) ** 0.5])


# ------------------------------------------------------------------ sound

def pines(dur, amp=1.0, seed=0):
    """Wind through pines: a low gusting roar and the high hiss of needles."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    low = Y.wind(dur, 1.0, seed=seed)
    n = rng.normal(0, 1, len(t))
    gust = 0.4 + 0.6 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t + 1)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.37 * t))
    hiss = _bp(n, 2500, 7000) * gust * 0.35
    return amp * (low + hiss) * _env(len(t), 1.0, 1.0, dur)


def fire(dur, amp=1.0, seed=0):
    t = tx(dur)
    roar = _lp(_noise(len(t), seed + 1), 300) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.7 * t)) * 0.6
    return amp * (I.crackle(dur, 1.0, seed=seed) + roar * _env(len(t), 0.5, 0.5, dur))


def hum(dur, amp=1.0, seed=0, flicker=0.3):
    """Fluorescent hum: mains harmonics, a ballast buzz, the tube ticking as it flickers."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    x = sum(np.sin(2 * np.pi * 120 * k * t + rng.uniform(0, 6)) / k ** 1.2 for k in range(1, 9)) * 0.3
    buzz = np.sign(np.sin(2 * np.pi * 120 * t)) * 0.05
    x = x + _bp(buzz, 1000, 6000)
    if flicker > 0:
        for _ in range(int(dur * 1.2 * flicker)):
            j = int(rng.integers(0, max(1, len(t) - 2000)))
            x[j:j + 1500] += _hp(rng.normal(0, 1, 1500), 2000) * np.exp(-np.arange(1500) / 300) * 0.5
    return amp * x * _env(len(t), 0.05, 0.05, dur)


def chant(dur, amp=1.0, seed=0):
    """Whispered chanting under her voice: a ring of breathy syllables pulsing at a slow ritual pace, a low murmur."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    out = np.zeros((2, len(t)))
    pulse = np.abs(np.sin(np.pi * 1.6 * t)) ** 6
    for ch in range(2):
        nz = rng.normal(0, 1, len(t))
        syl = np.abs(np.sin(2 * np.pi * rng.uniform(2.5, 3.5) * t + rng.uniform(0, 6))) ** 4
        out[ch] = (_bp(nz, 1600, 5200) * 0.6 + _bp(nz, 300, 900) * 0.4) * (0.3 * syl + 0.7 * pulse)
    hum_ = I.choir([45, 52], dur, 0.5, vowel="o", seed=seed, attack=1.0)[: len(t)]
    hum_ = np.pad(hum_, (0, len(t) - len(hum_)))
    out += np.stack([hum_, hum_]) * 0.6
    return amp * out * _env(len(t), 0.6, 0.6, dur) * 0.6


def metal_hit(amp=1.0, seed=0, size=1.0):
    """A heavy metallic impact: a struck iron plate's inharmonic ring, a thud, a burst of grit."""
    t = tx(2.4 * size)
    rng = np.random.default_rng(seed)
    ring = np.zeros(len(t))
    for k, (r, d) in enumerate(((1.0, 0.9), (2.32, 0.6), (3.87, 0.45), (5.41, 0.3), (7.1, 0.2))):
        f = 180 / size * r * rng.uniform(0.97, 1.03)
        ring += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-t / (d * size)) / (k + 1)
    thud = np.sin(2 * np.pi * np.cumsum(60 + 80 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.15)
    grit = _bp(rng.normal(0, 1, len(t)), 1500, 8000) * np.exp(-t / 0.03)
    return amp * np.tanh(1.4 * (ring * 0.6 + thud * 1.0 + grit * 0.7)) * 0.9


def door_slam(amp=1.0, seed=0):
    t = tx(1.6)
    rng = np.random.default_rng(seed)
    body = np.sin(2 * np.pi * np.cumsum(70 + 50 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.25)
    wood = _bp(rng.normal(0, 1, len(t)), 200, 1500) * np.exp(-t / 0.05) * 0.8
    latch = _bp(rng.normal(0, 1, len(t)), 2000, 6000) * np.exp(-np.maximum(0, t - 0.04) / 0.01) * (t > 0.04) * 0.3
    return amp * np.tanh(1.6 * (body + wood + latch)) * 0.9


def engine(dur, amp=1.0, seed=0, f0=48.0):
    """A distant engine roaring past: a low rough saw, throttle surges, a slow doppler, mostly felt."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    thr = 1 + 0.25 * np.sin(2 * np.pi * 0.35 * t) + 0.1 * np.sin(2 * np.pi * 1.3 * t)
    dop = 1 + 0.06 * np.tanh((t - dur / 2) / (dur / 6)) * -1
    f = f0 * thr * dop
    ph = np.cumsum(f) / SR
    x = (2 * (ph % 1.0) - 1) + 0.5 * (2 * ((ph * 2) % 1.0) - 1) + _lp(rng.normal(0, 1, len(t)), 300) * 0.5
    x = _lp(np.tanh(2.2 * x), 700)
    pass_env = np.exp(-((t - dur / 2) / (dur / 3)) ** 2)
    return amp * x * pass_env * 0.5


def rumble(dur, amp=1.0, seed=1):
    return O.rumble(dur, amp, seed)


def ding(amp=1.0, m=88):
    a, b = bell(m, amp, 1.2, ratio=2.0), bell(m + 7, amp * 0.5, 1.2, ratio=2.0)
    return a + b


def vibrate(amp=1.0, dur=0.5):
    t = tx(dur)
    x = np.sign(np.sin(2 * np.pi * 160 * t)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 4 * t)))
    return amp * _bp(x, 100, 1200) * 0.35


def typewriter(n, gap=0.09, amp=1.0, seed=0):
    return O.keys(n, gap, amp, seed=seed)


def whoosh(dur=0.5, up=True, amp=1.0, seed=0):
    return O.whoosh(dur, up, seed=seed, amp=amp)


def heartbeat(n=4, bpm=70, amp=1.0):
    return O.heartbeat(n, bpm, amp)


def breath(dur, amp=1.0, rate=0.9, seed=0):
    return Y.breath(dur, amp, rate=rate, seed=seed)


def whispers(dur, amp=1.0, seed=0):
    return O.whispers(dur, amp, seed=seed)


def reverse_cymbal(dur=1.4, amp=1.0, seed=0):
    t = tx(dur)
    x = _hp(_noise(len(t), seed), 3000) * np.exp(-t / 0.5)
    return amp * x[::-1] * 0.6


def power_down(dur=1.2, amp=1.0):
    return O.power_down(dur, amp)


def spark(amp=1.0, seed=0):
    t = tx(0.5)
    rng = np.random.default_rng(seed)
    x = np.zeros(len(t))
    for _ in range(14):
        j = int(rng.integers(0, len(t) - 400))
        x[j:j + 300] += _hp(rng.normal(0, 1, 300), 3000) * np.exp(-np.arange(300) / 60)
    return amp * x * 0.6


def shriek(dur=1.5, amp=1.0, seed=0):
    """A scare's top end, what a phone speaker plays: high bowed strings scraping in semitones and tritones and a hiss
    of breaking glass, all at once, fading fast."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    strings = np.zeros(len(t))
    for m in (86, 87, 92, 93, 98, 99):
        f = midi(m)
        vib = 1 + 0.006 * np.sin(2 * np.pi * rng.uniform(5, 7) * t + rng.uniform(0, 6))
        ph = np.cumsum(f * vib) / SR + rng.uniform()
        strings += (2 * (ph % 1.0) - 1) * (0.7 + 0.3 * np.sin(2 * np.pi * rng.uniform(9, 13) * t))
    strings = _bp(strings, 900, 7000) / 6
    glass = _bp(rng.normal(0, 1, len(t)), 2200, 7500) * np.exp(-t / 0.18)
    env = np.minimum(1, t / 0.004) * np.exp(-t / 0.5)
    return amp * np.tanh(2.4 * (strings * 1.4 + glass * 0.8) * env)
