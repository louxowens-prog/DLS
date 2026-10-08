"""Instruments for a 1982 horror-anthology score, all synthesized: analog pads and stabs (detuned saws through a
sweeping low-pass), an arpeggiator, a pulsing synth bass, risers; and the sound-effects box - wind, creaks, skittering
insects, wipers, an engine, a heart monitor, phone keypad tones, the low-battery chime, a cockpit warning, glass
cracking, a match, laboured breathing, a pill bottle's rattle, the assistant's wake chime."""
import numpy as np
from scipy import signal

from orch import SR, _bp, _hp, _lp, _noise, midi, tx


def _saw(f, t, seed=0, ph=None):
    rng = np.random.default_rng(abs(int(seed)))
    p = np.cumsum(np.broadcast_to(f, t.shape)) / SR + (rng.uniform() if ph is None else ph)
    return 2 * (p % 1.0) - 1


def _sweep_lp(x, f_start, f_end, order=2):
    """A low-pass whose cutoff glides from f_start to f_end (by cross-fading a dark and a bright copy)."""
    dark, bright = _lp(x, f_start, order), _lp(x, f_end, order)
    k = np.linspace(0, 1, len(x))
    return dark * (1 - k) + bright * k


def pad(notes, dur, amp=1.0, cut=(500, 2200), seed=0, attack=0.8, release=1.2, detune=9):
    """An analog string-machine pad: three detuned saws a note, slow attack, the filter opening across the chord."""
    t = tx(dur + release)
    out = np.zeros(len(t))
    for i, m in enumerate(notes):
        for d in (-detune, 0, detune * 0.8):
            f = midi(m) * 2 ** (d / 1200) * (1 + 0.003 * np.sin(2 * np.pi * (4.6 + i * 0.3) * t))
            out += _saw(f, t, seed + i * 7 + int(d))
    out = _sweep_lp(out, cut[0], cut[1])
    env = np.clip(t / attack, 0, 1) * np.clip((dur + release - t) / release, 0, 1)
    return amp * out * env * 0.07 / max(1, len(notes)) ** 0.5


def stab(notes, amp=1.0, dur=0.7, bright=5200, seed=0):
    """A synth brass stab: saw + square, a snapping filter envelope, a short tail."""
    t = tx(dur + 0.4)
    out = np.zeros(len(t))
    for i, m in enumerate(notes):
        f = midi(m)
        out += _saw(f * 1.004, t, seed + i) + 0.6 * np.sign(np.sin(2 * np.pi * f * 0.998 * t))
    fe = np.exp(-t / 0.12)
    dark, br = _lp(out, 500), _lp(out, bright)
    y = dark * (1 - fe) + br * fe
    env = np.clip(t / 0.004, 0, 1) * np.exp(-t / (dur * 0.6))
    return amp * y * env * 0.18 / max(1, len(notes)) ** 0.5


def pluck(m, amp=1.0, dur=0.25, bright=3000):
    """An arpeggiator note: a square-ish pluck with a fast filter close."""
    t = tx(dur + 0.15)
    f = midi(m)
    x = np.sign(np.sin(2 * np.pi * f * t)) * 0.7 + _saw(f, t, 1) * 0.5
    fe = np.exp(-t / 0.05)
    y = _lp(x, 400) * (1 - fe) + _lp(x, bright) * fe
    return amp * y * np.exp(-t / dur) * np.clip(t / 0.002, 0, 1) * 0.16


def bass(m, dur, amp=1.0):
    """A pulsing synth bass note: saw, sub sine, a quick filter blip."""
    t = tx(dur + 0.05)
    f = midi(m)
    x = _saw(f, t, 2) + 0.8 * np.sin(2 * np.pi * f * 0.5 * t)
    fe = np.exp(-t / 0.06)
    y = _lp(x, 180) * (1 - fe) + _lp(x, 900) * fe
    env = np.clip(t / 0.003, 0, 1) * np.clip((dur + 0.05 - t) / 0.04, 0, 1)
    return amp * y * env * 0.3


def riser(dur, amp=1.0, seed=0, f0=200, f1=3000):
    t = tx(dur)
    k = (t / dur) ** 2
    n = _noise(len(t), seed)
    y = np.zeros(len(t))
    blocks = 24
    L = len(t) // blocks + 1
    for b in range(blocks):
        a, c = b * L, min(len(t), (b + 1) * L)
        fc = f0 + (f1 - f0) * ((b + 0.5) / blocks) ** 2
        y[a:c] = _bp(n[max(0, a - 400):c], fc * 0.8, fc * 1.2)[-(c - a):] if c > a else 0
    sw = _saw(f0 / 2 + (f1 / 4 - f0 / 2) * k, t, seed)
    return amp * (y * 0.6 + _lp(sw, 2000) * 0.15) * k


def wind(dur, amp=1.0, seed=0):
    """Wind: noise through a resonant band that drifts and gusts."""
    t = tx(dur)
    n = _noise(len(t), seed)
    out = np.zeros(len(t))
    for i, (lo, hi, rate) in enumerate(((250, 500, 0.13), (500, 900, 0.21), (900, 1600, 0.08))):
        g = 0.5 + 0.5 * np.sin(2 * np.pi * rate * t + i * 2.1) ** 2
        out += _bp(n, lo, hi) * g
    env = np.clip(t / 1.0, 0, 1) * np.clip((dur - t) / 1.0, 0, 1)
    return amp * out * env * 0.5


def creak(dur=0.9, amp=1.0, seed=0, f0=90, f1=40):
    """A wooden creak: a slowing train of clicks through a woody resonance."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    rate = f0 + (f1 - f0) * t / dur + rng.normal(0, 4, len(t))
    ph = np.cumsum(rate) / SR
    clicks = (np.diff(np.floor(ph), prepend=0) > 0).astype(float)
    y = _bp(clicks, 500, 1400) * 6 + _bp(clicks, 1800, 2600) * 2
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.6
    return amp * y * env * 0.5


def skitter(dur, amp=1.0, seed=0, rate=40.0):
    """Insects scuttling: dense, irregular little clicks."""
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    out = np.zeros(n + 400)
    t = 0.0
    while t < dur:
        i = int(t * SR)
        k = np.exp(-np.arange(200) / 18.0) * rng.normal(0, 1, 200)
        out[i:i + 200] += k * rng.uniform(0.3, 1.0)
        t += rng.exponential(1 / rate)
    return amp * _hp(out[:n], 2500) * 0.6


def wiper(amp=1.0, seed=0):
    t = tx(0.5)
    n = _noise(len(t), seed)
    y = _bp(n, 600, 3000) * np.sin(np.pi * t / 0.5) ** 2
    thunk = np.sin(2 * np.pi * 80 * t) * np.exp(-((t - 0.48) / 0.01) ** 2)
    return amp * (y * 0.3 + thunk * 0.4)


def engine(dur, amp=1.0, seed=0):
    t = tx(dur)
    f = 32 + 2 * np.sin(2 * np.pi * 0.3 * t)
    y = _saw(f, t, seed) + 0.5 * _saw(f * 2.01, t, seed + 1)
    y = _lp(y, 220) + _lp(_noise(len(t), seed), 160) * 0.5
    env = np.clip(t / 0.5, 0, 1) * np.clip((dur - t) / 0.5, 0, 1)
    return amp * y * env * 0.25


def beep(f=1000.0, dur=0.09, amp=1.0):
    t = tx(dur)
    return amp * np.sin(2 * np.pi * f * t) * np.clip(t / 0.003, 0, 1) * np.clip((dur - t) / 0.006, 0, 1) * 0.3


def monitor(dur, bpm=70, amp=1.0, f=1040.0):
    """A heart monitor: a clean beep at the heart rate."""
    out = np.zeros(int(dur * SR) + SR)
    gap = 60.0 / bpm
    t = 0.0
    while t < dur:
        b = beep(f, 0.11, 1.0)
        i = int(t * SR)
        out[i:i + len(b)] += b
        t += gap
    return amp * out[:int(dur * SR)]


DTMF = {"1": (697, 1209), "2": (697, 1336), "3": (697, 1477), "4": (770, 1209), "5": (770, 1336), "6": (770, 1477), "7": (852, 1209),
        "8": (852, 1336), "9": (852, 1477), "0": (941, 1336)}


def dtmf(d, dur=0.16, amp=1.0):
    t = tx(dur)
    a, b = DTMF[d]
    return amp * (np.sin(2 * np.pi * a * t) + np.sin(2 * np.pi * b * t)) * 0.15 * np.clip((dur - t) / 0.005, 0, 1)


def dial_tone(dur, amp=1.0):
    t = tx(dur)
    return amp * (np.sin(2 * np.pi * 350 * t) + np.sin(2 * np.pi * 440 * t)) * 0.08 * np.clip(t / 0.01, 0, 1) * np.clip((dur - t) / 0.05, 0, 1)


def low_batt(amp=1.0):
    """The low-battery chime: two falling tones."""
    out = np.zeros(int(0.6 * SR))
    for k, f in enumerate((880.0, 587.0)):
        t = tx(0.22)
        x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.12) * np.clip(t / 0.004, 0, 1)
        i = int(k * 0.2 * SR)
        out[i:i + len(x)] += x
    return amp * out * 0.4


def wake_chime(amp=1.0):
    """The assistant waking up: a soft rising glassy blip."""
    t = tx(0.5)
    f = 700 * 2 ** (t / 0.5 * 1.2)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18) + 0.3 * np.sin(2 * np.pi * np.cumsum(f * 2) / SR) * np.exp(-t / 0.08)
    return amp * x * np.clip(t / 0.01, 0, 1) * 0.3


def error_tone(amp=1.0):
    """The sat-nav losing its signal: a harsh descending square buzz."""
    t = tx(0.7)
    f = 520 * 2 ** (-t / 0.7)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR))
    return amp * _lp(x, 3000) * np.clip(t / 0.005, 0, 1) * np.clip((0.7 - t) / 0.08, 0, 1) * 0.18


def whoop(dur, amp=1.0):
    """A cockpit warning: a rising two-tone whoop, repeated."""
    t = tx(dur)
    ph = (t % 0.5) / 0.5
    f = 400 + 600 * ph
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (ph < 0.85)
    return amp * _lp(x, 2500) * 0.15 * np.clip((dur - t) / 0.05, 0, 1)


def alarm(dur, amp=1.0, rate=4.0, f=1500.0):
    t = tx(dur)
    on = ((t * rate) % 1.0) < 0.5
    return amp * np.sin(2 * np.pi * f * t) * on * 0.2 * np.clip((dur - t) / 0.03, 0, 1)


def crack(amp=1.0, seed=0):
    """Glass cracking: a bright snap and a splintering tail."""
    t = tx(0.9)
    n = _noise(len(t), seed)
    snap = _hp(n, 2000) * np.exp(-t / 0.01)
    rng = np.random.default_rng(seed)
    tail = np.zeros(len(t))
    for _ in range(40):
        i = int(rng.uniform(0.01, 0.7) * SR)
        k = np.exp(-np.arange(300) / 30.0) * rng.normal(0, 1, 300)
        tail[i:i + 300] += k * rng.uniform(0.2, 0.7)
    return amp * (snap * 1.2 + _hp(tail, 3000) * np.exp(-t / 0.4)) * 0.6


def match(amp=1.0, seed=0):
    t = tx(1.2)
    n = _noise(len(t), seed)
    scratch = _bp(n, 1500, 6000) * np.exp(-((t - 0.08) / 0.06) ** 2)
    flare = _lp(n, 1500) * np.exp(-((t - 0.2) / 0.15) ** 2) * 0.8 + _lp(n, 600) * np.clip((t - 0.15) / 0.2, 0, 1) * np.exp(-t / 0.8) * 0.3
    return amp * (scratch + flare) * 0.6


def breath(dur, amp=1.0, rate=0.9, seed=0):
    """Laboured breathing: noisy in-and-out gasps."""
    t = tx(dur)
    n = _noise(len(t), seed)
    ph = (t * rate) % 1.0
    env = np.where(ph < 0.4, np.sin(np.pi * ph / 0.4) * 0.8, np.sin(np.pi * (ph - 0.4) / 0.6) * 0.5) ** 2
    y = _bp(n, 400, 2200) * env + _bp(n, 900, 1300) * env * 0.5
    return amp * y * 0.4 * np.clip((dur - t) / 0.2, 0, 1)


def rattle(dur, amp=1.0, seed=0, rate=11.0):
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    out = np.zeros(n + 2000)
    t = 0.0
    while t < dur:
        for _ in range(int(rng.integers(3, 8))):
            i = int((t + rng.uniform(0, 0.03)) * SR)
            k = np.sin(2 * np.pi * rng.uniform(2500, 4500) * np.arange(600) / SR) * np.exp(-np.arange(600) / 60.0)
            out[i:i + 600] += k * rng.uniform(0.3, 1)
        t += 1 / rate
    return amp * out[:n] * 0.3


def tick(amp=1.0):
    t = tx(0.03)
    return amp * _bp(_noise(len(t), 1), 2000, 5000) * np.exp(-t / 0.004) * 0.8


def buzz(dur, amp=1.0, seed=0):
    """Fluorescent lights failing: 100 Hz buzz with crackles."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    on = (rng.uniform(0, 1, int(dur * 20) + 1) > 0.4).repeat(int(SR / 20) + 1)[:len(t)]
    x = np.sign(np.sin(2 * np.pi * 100 * t)) * 0.3 + _hp(_noise(len(t), seed), 3000) * 0.2
    return amp * _lp(x, 4000) * on * 0.3


def thud(amp=1.0, f=55.0):
    t = tx(0.6)
    return amp * np.sin(2 * np.pi * np.cumsum(f + 60 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.15) * 0.9


def earth(amp=1.0, seed=0):
    """Earth falling on a coffin lid: a dull thud and a shower of grit."""
    t = tx(1.0)
    th = np.zeros(len(t))
    d = thud(1.0, 45)
    th[:len(d)] = d
    return amp * (th * 0.8 + _lp(_noise(len(t), seed), 1800) * np.exp(-t / 0.35) * 0.3)


def footstep(amp=1.0, seed=0, hard=True):
    """A heel on a hard floor (or a softer step): a click, a low knock, a scuff."""
    t = tx(0.35)
    rng = np.random.default_rng(seed)
    n = _noise(len(t), seed)
    click = _bp(n, 1800, 5000) * np.exp(-t / 0.008) * (1.0 if hard else 0.4)
    knock = np.sin(2 * np.pi * np.cumsum(110 + 60 * np.exp(-t / 0.01)) / SR) * np.exp(-t / 0.04)
    scuff = _bp(n, 600, 2500) * np.exp(-((t - 0.06) / 0.04) ** 2) * 0.3
    return amp * (click * 0.8 + knock * 0.7 + scuff) * rng.uniform(0.8, 1.1) * 0.6


def footsteps(n, gap=0.55, amp=1.0, seed=0, hard=True):
    out = np.zeros(int((n * gap + 0.5) * SR))
    for k in range(n):
        s = footstep(1.0, seed + k, hard)
        i = int(k * gap * SR)
        out[i:i + len(s)] += s * (0.85 if k % 2 else 1.0)
    return amp * out
