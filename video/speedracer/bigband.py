"""A brassy 1960s big band, synthesized: trumpets, trombones, saxes, walking bass, swing drums, plus the race:
engines, tyre screech, whooshes, crowd roar, and the stadium-PA treatment for the announcer. Nothing sampled;
all riffs are original.
"""
import numpy as np
from scipy import signal

import jazz as J

SR = J.SR
BPM = 168
BEAT = 60 / BPM
SWING = 0.64                                   # long-short eighths


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tx(d):
    return np.arange(int(d * SR)) / SR


def _lp(x, fc):
    b, a = signal.butter(2, min(fc / (SR / 2), 0.99), "low")
    return signal.lfilter(b, a, x)


def _bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi / (SR / 2), 0.99)], "band")
    return signal.lfilter(b, a, x)


# ------------------------------------------------------------------ horns

KINDS = {                       # (harmonics, brightness, detune cents, odd-only, breath)
    "tpt": (28, 1.0, 7, False, 0.04),
    "tbn": (22, 0.55, 5, False, 0.03),
    "sax": (20, 0.6, 9, True, 0.06),
}


def horn(f0, dur, kind="tpt", amp=1.0, accent=1.0, fall=0.0, doit=0.0, seed=0):
    """One brass note: a sawtooth whose brightness blooms on the attack (the 'blat'), a small pitch scoop,
    late vibrato, breath noise, and optional fall-off or doit at the end."""
    nh, bright, cents, odd, br = KINDS[kind]
    rng = np.random.default_rng(seed)
    rel = 0.09
    t = tx(dur + rel)
    n = len(t)
    env = np.minimum(1, t / 0.018) * np.exp(-t * 0.6)
    env *= np.clip((dur + rel - t) / rel, 0, 1)
    blat = accent * np.exp(-t / 0.07)
    bright_t = bright * (0.35 + 0.65 * np.minimum(1, t / 0.03)) * (0.75 + 0.6 * blat)
    pitch = 1 - 0.03 * np.exp(-t / 0.035)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.6 * t) * np.clip((t - 0.22) / 0.2, 0, 1)
    bend = np.ones(n)
    if fall:
        k = np.clip((t - dur * 0.55) / (dur * 0.45 + rel), 0, 1)
        bend *= 2 ** (-fall * k ** 1.6 / 12)
    if doit:
        k = np.clip((t - dur * 0.6) / (dur * 0.4 + rel), 0, 1)
        bend *= 2 ** (doit * k ** 1.4 / 12)
    out = np.zeros(n)
    for voice in (-1, 1):
        f = f0 * pitch * vib * bend * 2 ** (voice * cents / 2400)
        ph = 2 * np.pi * np.cumsum(f) / SR + rng.uniform(0, 6.28)
        for h in range(1, nh + 1):
            if odd and h % 2 == 0 and h > 2:
                continue
            if f0 * h > SR * 0.45:
                break
            w = (1 / h) * np.exp(-(h - 1) / (3 + 14 * bright_t))
            out += w * np.sin(h * ph)
    breath = _bp(rng.normal(0, 1, n), 1200, 6000) * br * env
    return amp * (out * env * 0.5 + breath)


def chord_hit(notes, dur=0.28, kinds=("tpt", "tbn", "sax"), amp=1.0, fall=0.0, doit=0.0, seed=0):
    """A section stab: trumpets on top, trombones and saxes below."""
    notes = sorted(notes)
    parts = []
    for i, m in enumerate(notes):
        k = kinds[0] if i >= len(notes) - 2 else (kinds[1] if i < 2 else kinds[2])
        parts.append(horn(midi(m), dur, k, 1.0 / len(notes) ** 0.5, fall=fall, doit=doit, seed=seed + i))
    L = max(len(p) for p in parts)
    out = np.zeros(L)
    for p in parts:
        out[:len(p)] += p
    return amp * out


def pad(notes, dur, amp=1.0, seed=0):
    """Soft sustained sax-section chord for under the narration."""
    L = int((dur + 0.1) * SR)
    out = np.zeros(L)
    for i, m in enumerate(notes):
        h = horn(midi(m), dur, "sax", 0.5, accent=0.2, seed=seed + i)
        out[:len(h)] += h[:L]
    return amp * _lp(out, 2600)


# ------------------------------------------------------------------ rhythm section

def upright(f0, dur, amp=1.0, seed=0):
    t = tx(dur + 0.15)
    env = np.exp(-t / 0.35) * np.minimum(1, t / 0.004)
    x = np.sin(2 * np.pi * f0 * t) + 0.45 * np.sin(4 * np.pi * f0 * t) + 0.15 * np.sin(6 * np.pi * f0 * t)
    thump = J._lp(np.random.default_rng(seed).normal(0, 1, len(t)), 400) * np.exp(-t / 0.015) * 0.5
    return amp * (x * env + thump)


def swing_pos(beat_i, eighth=0):
    """Time of an eighth note inside the swing grid."""
    return beat_i * BEAT + (SWING * BEAT if eighth else 0)


def swing_kit(dur, energy, seed=0):
    """Ride 'ding, ding-a ding', hi-hat foot on 2 and 4, feathered kick, snare comping; density follows energy."""
    rng = np.random.default_rng(seed)
    out = np.zeros(int((dur + 1) * SR))

    def put(sig, t, g):
        i = int(t * SR)
        if 0 <= i < len(out):
            j = min(len(out), i + len(sig))
            out[i:j] += g * sig[: j - i]
    nb = int(dur / BEAT)
    for b in range(nb):
        t = b * BEAT
        e = energy(t)
        if e <= 0.01:
            continue
        put(J.ride(seed=b % 7), t, 0.22 * (0.6 + 0.4 * e))
        if b % 2 == 1:
            put(J.ride(seed=b % 5 + 9), swing_pos(b, 1), 0.14 * (0.6 + 0.4 * e))
            put(J.hat(seed=b % 3), t, 0.18)
        put(J.kick(seed=b % 4), t, 0.18 * e)                                  # feathered
        if rng.random() < 0.25 + 0.5 * e:
            put(J.snare(seed=b, tight=0.6), swing_pos(b, rng.integers(0, 2)), 0.08 + 0.25 * e * rng.random())
        if e > 0.75 and b % 8 == 7:                                           # fill into the next phrase
            for k in range(4):
                put(J.snare(seed=b * 5 + k, tight=0.7), t + k * BEAT / 4, 0.3 + 0.1 * k)
    return out[: int(dur * SR)]


# ------------------------------------------------------------------ the race

def engine(dur, rpm, amp=1.0, seed=0):
    """A racing engine: a pulse train at the firing rate with growl and exhaust noise; rpm is a function of t."""
    t = tx(dur)
    r = np.array([rpm(x) for x in t[::240]])
    r = np.interp(np.arange(len(t)), np.arange(len(r)) * 240, r)
    f = r / 60 * 3                                                      # six-cylinder firing rate
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sign(np.sin(ph)) * 0.4 + np.sin(ph) * 0.6 + 0.3 * np.sin(2 * ph + 0.3) + 0.2 * np.sin(0.5 * ph)
    x = np.tanh(2.2 * x)
    noise = _bp(np.random.default_rng(seed).normal(0, 1, len(t)), 200, 3000) * 0.25
    x = _lp(x + noise * (0.5 + 0.5 * np.sin(ph / 3)), 3800)
    return amp * x


def passby(dur=1.6, f_lo=160, f_hi=320, amp=1.0, seed=0):
    """A car screaming past: Doppler pitch drop and a volume swell, panned left to right."""
    c = dur / 2
    rpm = lambda x: (f_hi if x < c else f_lo + (f_hi - f_lo) * np.exp(-(x - c) * 4)) * 20 + 800 * np.exp(-((x - c) / 0.18) ** 2)
    e = engine(dur, rpm, seed=seed)
    t = tx(dur)
    vol = 1 / (1 + ((t - c) / 0.28) ** 2)
    x = e * vol
    pan = 1 / (1 + np.exp(-(t - c) * 6))
    return amp * np.stack([x * np.sqrt(1 - pan), x * np.sqrt(pan)]) * 1.4


def screech(dur=0.8, amp=1.0, seed=0):
    t = tx(dur)
    rng = np.random.default_rng(seed)
    f = 2300 + 500 * np.sin(2 * np.pi * 7 * t) + rng.normal(0, 60, len(t)).cumsum() * 0.02
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    x = x * (0.6 + 0.4 * rng.random(len(t))) + _bp(rng.normal(0, 1, len(t)), 1500, 6000) * 0.4
    env = np.minimum(1, t / 0.03) * np.clip((dur - t) / 0.2, 0, 1)
    return amp * x * env * 0.5


def smash(dur=1.4, amp=1.0, seed=0):
    rng = np.random.default_rng(seed)
    t = tx(dur)
    x = _bp(rng.normal(0, 1, len(t)), 150, 9000) * np.exp(-t / 0.25)
    for k in range(9):
        t0 = rng.uniform(0, 0.5)
        f = rng.uniform(600, 3200)
        i = int(t0 * SR)
        tt = t[: len(t) - i]
        x[i:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt / rng.uniform(0.05, 0.3)) * 0.4
    return amp * np.tanh(x * 1.5) + amp * J.kick(seed=seed)[: len(t)] * 0.8 if False else amp * (np.tanh(x * 1.5) + np.pad(J.kick(seed=seed), (0, max(0, len(t) - int(0.5 * SR))))[: len(t)] * 0.8)


def whoosh(dur=0.5, amp=1.0, up=True, seed=0):
    """Filtered-noise sweep for wipes, panned across the stereo field."""
    rng = np.random.default_rng(seed)
    t = tx(dur)
    n = rng.normal(0, 1, len(t))
    out = np.zeros(len(t))
    fc = np.linspace(400, 5000, 12) if up else np.linspace(5000, 400, 12)
    seg = len(t) // 12 + 1
    for k in range(12):
        i0, i1 = k * seg, min(len(t), (k + 1) * seg + 400)
        out[i0:i1] += _bp(n[i0:i1], fc[k] * 0.6, fc[k] * 1.4)[: i1 - i0] * (1 if k < 11 else 0.5)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    x = out * env
    pan = t / dur
    return amp * np.stack([x * np.sqrt(1 - pan), x * np.sqrt(pan)]) * 1.4


def crowd(dur, amp=1.0, seed=0):
    """Stadium roar: band-limited noise with slow surges and a scatter of cheers."""
    rng = np.random.default_rng(seed)
    t = tx(dur)
    base = _bp(rng.normal(0, 1, len(t)), 250, 2600, 3)
    surge = 0.7 + 0.3 * np.convolve(rng.normal(0, 1, len(t) // 2400 + 2), np.ones(3) / 3, "same")
    surge = np.interp(np.arange(len(t)), np.arange(len(surge)) * 2400, surge)
    x = base * surge
    for k in range(int(dur * 14)):
        t0 = rng.uniform(0, dur)
        f = rng.uniform(500, 1400)
        L = int(rng.uniform(0.15, 0.5) * SR)
        i = int(t0 * SR)
        if i + L >= len(x):
            continue
        tt = np.arange(L) / SR
        v = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.1 * np.sin(2 * np.pi * 6 * tt))) / SR)
        x[i:i + L] += _bp(v * rng.normal(1, 0.3, L), 400, 3000) * np.sin(np.pi * tt / tt[-1]) * 0.25
    return amp * x


def riser(dur, amp=1.0, seed=0):
    return J.riser(dur, amp, seed)


def rimshot(amp=1.0):
    """Ba-dum-tss."""
    out = np.zeros(int(1.6 * SR))
    for t, sig, g in ((0.0, J.snare(seed=1, tight=0.5), 0.8), (0.16, J.tom(150, seed=2), 0.7), (0.32, J.kick(seed=3), 0.8),
                      (0.32, J.crash(seed=4), 0.55)):
        i = int(t * SR)
        j = min(len(out), i + len(sig))
        out[i:j] += g * sig[: j - i]
    return amp * out


def pa(x, sr):
    """Stadium PA voice: band-limited, driven, with a slapback off the grandstand."""
    y = _bp(x, 320, 3600, 2)
    y = np.tanh(y * 3.0) * 0.6
    d = int(0.085 * sr)
    y = y + 0.28 * np.concatenate([np.zeros(d), y[:-d]])
    return y
