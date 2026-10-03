"""The lo-fi score, all synthesized and all original: bedroom synthpop and a hyperpop sting, glitchy chiptune, a
toy-keyboard music box over a cheap General-MIDI orchestra, a game-show jingle with slap bass and brass stabs, a PS1
drum-and-bass loop with FM bells, a public-access jingle, and clean-then-distorted pop-punk guitar for the turn.
Plus the canned audience (a laugh track built from many synthesized voices, applause), a rimshot, a cough."""
import math

import numpy as np
from scipy import signal

import band as B
import orch as O

SR = O.SR
midi, tx = O.midi, O.tx


# ------------------------------------------------------------------ oscillators and envelopes

def osc(kind, f, t, duty=0.5, ph=0.0):
    p = (f * t + ph) % 1.0 if np.isscalar(f) else (np.cumsum(f) / SR + ph) % 1.0
    if kind == "square":
        return np.where(p < 0.5, 1.0, -1.0)
    if kind == "pulse":
        return np.where(p < duty, 1.0, -1.0)
    if kind == "tri":
        return 4 * np.abs(p - 0.5) - 1
    if kind == "saw":
        return 2 * p - 1
    return np.sin(2 * np.pi * p)


def adsr(n, a=0.005, d=0.08, s=0.6, r=0.06):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    e = np.full(n + r, s)
    e[:a] = np.linspace(0, 1, max(1, a))[: min(a, len(e))] if a else e[:0]
    if a + d <= len(e):
        e[a:a + d] = np.linspace(1, s, max(1, d))
    e[n:] = np.linspace(s, 0, r)[: len(e) - n] if r else e[n:]
    return e


def note(kind, m, dur, amp=1.0, a=0.004, d=0.08, s=0.55, r=0.05, duty=0.5, vib=0.0, glide=0.0, lp=None):
    n = int(dur * SR)
    e = adsr(n, a, d, s, r)
    t = np.arange(len(e)) / SR
    f = midi(m) * (1 + vib * np.sin(2 * np.pi * 5.5 * t) * np.clip(t * 3, 0, 1))
    if glide:
        f = f * 2 ** (glide * np.exp(-t * 18) / 12)
    y = osc(kind, f, t, duty) * e * amp
    if lp:
        y = signal.sosfilt(signal.butter(2, min(0.99, lp / (SR / 2)), output="sos"), y)
    return y


def supersaw(notes, dur, amp=1.0, voices=7, spread=0.22, a=0.01, r=0.25, lp=6000):
    n = int(dur * SR)
    e = adsr(n, a, 0.15, 0.8, r)
    t = np.arange(len(e)) / SR
    out = np.zeros((2, len(e)))
    rng = np.random.default_rng(int(sum(notes)))
    for m in notes:
        for v in range(voices):
            det = (v / (voices - 1) - 0.5) * spread
            y = osc("saw", midi(m + det), t, ph=rng.uniform(0, 1))
            pan = v / (voices - 1)
            out[0] += y * np.sqrt(1 - pan)
            out[1] += y * np.sqrt(pan)
    out = signal.sosfilt(signal.butter(2, lp / (SR / 2), output="sos"), out, axis=1)
    return out * e * amp / (voices * len(notes)) * 2.2


def fm_bell(m, dur=1.2, amp=1.0, ratio=3.5, index=3.0):
    t = tx(dur)
    f = midi(m)
    env = np.exp(-t * 3.2)
    mod = index * np.exp(-t * 5) * np.sin(2 * np.pi * f * ratio * t)
    return np.sin(2 * np.pi * f * t + mod) * env * amp


def bitcrush(x, bits=6, down=4):
    y = np.repeat(x[..., ::down], down, axis=-1)[..., : x.shape[-1]]
    q = 2 ** (bits - 1)
    return np.round(y * q) / q


# ------------------------------------------------------------------ drums

def kick808(amp=1.0, dur=0.55, f0=150, f1=48):
    t = tx(dur)
    f = f1 + (f0 - f1) * np.exp(-t * 28)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5.5)
    return np.tanh(1.6 * y) * amp


def chip_noise(dur=0.08, amp=1.0, hi=True, seed=0):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    step = 2 if hi else 12                                         # the NES noise channel's 'period'
    x = np.repeat(np.sign(rng.normal(0, 1, n // step + 1)), step)[:n]
    return x * np.exp(-np.arange(n) / SR * (60 if hi else 18)) * amp


def chip_kick(amp=1.0):
    t = tx(0.12)
    f = 220 * np.exp(-t * 30) + 50
    return osc("tri", f, t) * np.exp(-t * 20) * amp


def drum_machine(kind, amp=1.0, seed=0):
    if kind == "k":
        return O.kick(amp, seed)
    if kind == "s":
        return O.snare(amp, seed)
    if kind == "h":
        return O.hat(amp * 0.7, seed)
    if kind == "o":
        return O.hat(amp * 0.7, seed, open_=True)
    if kind == "c":
        return O.clap(amp, seed)
    if kind == "8":
        return kick808(amp)
    return None


# ------------------------------------------------------------------ guitars

def guitar(m, dur=0.6, amp=1.0, seed=0):
    """A clean electric guitar note (plucked string, a little chorus)."""
    y = B.pluck(m, amp, dur, seed, 0.997)
    d = int(0.012 * SR)
    return np.stack([y, np.concatenate([np.zeros(d), y[:-d]]) * 0.9])


def power_chord(root, dur=0.5, amp=1.0, seed=0, palm=False):
    """A distorted power chord (root, fifth, octave) through a cabinet: the pop-punk sound."""
    x = sum(B.pluck(m, 1.0, dur + 0.2, seed + i, 0.9993 if not palm else 0.99) for i, m in enumerate((root, root + 7, root + 12)))
    x = np.tanh(6.0 * x / (np.abs(x).max() + 1e-9))
    x = signal.sosfilt(signal.butter(2, [90 / (SR / 2), 4200 / (SR / 2)], "band", output="sos"), x)
    n = int(dur * SR)
    x = x[: n + int(0.05 * SR)]
    x[n:] *= np.linspace(1, 0, len(x) - n)
    d = int(0.017 * SR)
    return np.stack([x, np.concatenate([np.zeros(d), x[:-d]])]) * amp * 0.35


# ------------------------------------------------------------------ the canned audience

_LAUGH = {}


def laugh_layer(seed=0):
    """One synthesized 'ha ha ha', from a random voice of the TTS set, pitched and timed a little differently."""
    from voice import SR as VSR, speak_fx
    rng = np.random.default_rng(seed)
    voices = ["af_bella", "af_sarah", "am_michael", "am_adam", "bf_emma", "bm_george", "af_nicole", "am_puck", "af_sky", "am_echo",
              "af_heart", "bm_lewis", "af_kore", "am_eric"]
    v = voices[int(rng.integers(0, len(voices)))]
    txt = ["Ha ha ha ha!", "Hah! Ha ha!", "Ho ho ho!", "Ha ha ha!", "Heh heh heh!", "Ah ha ha ha!", "Hee hee hee!"][int(rng.integers(0, 7))]
    w = speak_fx(txt, v, float(rng.uniform(1.1, 1.35)), float(rng.uniform(-2.5, 3.0)))
    return signal.resample_poly(w.astype(np.float64), SR, VSR)


def laugh(dur=2.2, amp=1.0, seed=0, n=22, swell=0.25):
    """A canned laugh: n voices piled up, staggered, band-limited like an old TV laugh track, with a quick swell and a
    long tail."""
    key = (round(dur, 2), seed, n)
    if key not in _LAUGH:
        rng = np.random.default_rng(seed + 1000)
        N = int((dur + 1.2) * SR)
        out = np.zeros((2, N))
        for i in range(n):
            w = laugh_layer(seed * 31 + i)
            off = int(abs(rng.normal(0.0, swell)) * SR)
            g = rng.uniform(0.4, 1.0)
            pan = rng.uniform(0.15, 0.85)
            j = min(N, off + len(w))
            out[0, off:j] += w[: j - off] * g * np.sqrt(1 - pan)
            out[1, off:j] += w[: j - off] * g * np.sqrt(pan)
        noise = np.random.default_rng(seed).normal(0, 1, (2, N)) * 0.02        # the room
        out = out + noise * (np.abs(out).mean() * 4)
        out = signal.sosfilt(signal.butter(3, [220 / (SR / 2), 5200 / (SR / 2)], "band", output="sos"), out, axis=1)
        env = np.ones(N)
        fade = int(0.6 * SR)
        env[int(dur * SR):] = 0
        env[int(dur * SR) - fade:int(dur * SR)] = np.linspace(1, 0, fade) ** 1.5
        out = out * env
        _LAUGH[key] = out / (np.sqrt((out ** 2).mean()) + 1e-9) * 0.1
    return _LAUGH[key] * amp


def applause(dur=2.0, amp=1.0, seed=3, sparse=False):
    """Canned applause, or (sparse) the five people in a basement clapping."""
    if not sparse:
        x = O.applause(dur, amp, seed)
        return np.stack([x, O.applause(dur, amp, seed + 7)])
    rng = np.random.default_rng(seed)
    N = int(dur * SR)
    out = np.zeros((2, N))
    for p in range(5):
        t = rng.uniform(0, 0.15)
        rate = rng.uniform(3.2, 4.5)
        pan = rng.uniform(0.2, 0.8)
        while t < dur - 0.1:
            c = O.clap(rng.uniform(0.5, 1.0), int(rng.integers(0, 99)))
            i = int(t * SR)
            j = min(N, i + len(c))
            out[0, i:j] += c[: j - i] * np.sqrt(1 - pan)
            out[1, i:j] += c[: j - i] * np.sqrt(pan)
            t += 1 / rate * rng.uniform(0.85, 1.15)
    fade = int(0.4 * SR)
    out[:, -fade:] *= np.linspace(1, 0, fade)
    return out * amp * 0.6


def rimshot(amp=1.0):
    """Ba-dum-tss: two toms and a crash."""
    out = np.zeros(int(1.6 * SR))
    for i, (f, t0) in enumerate(((180, 0.0), (130, 0.17))):
        t = tx(0.35)
        y = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.6 * np.exp(-t * 20))) / SR) * np.exp(-t * 9)
        y += O._noise(len(t), i) * np.exp(-t * 30) * 0.3
        j = int(t0 * SR)
        out[j:j + len(y)] += y
    cr = O.cymbal(1.0, 1.2, seed=9)
    j = int(0.36 * SR)
    out[j:j + len(cr)] += cr[: len(out) - j] * 0.8
    return out * amp


def cough(amp=1.0, seed=0):
    """One cough in an empty theatre: two short bursts of breath through a throat."""
    rng = np.random.default_rng(seed)
    out = np.zeros(int(0.7 * SR))
    for i, t0 in enumerate((0.0, 0.26)):
        n = int(0.16 * SR)
        x = rng.normal(0, 1, n)
        x = signal.sosfilt(signal.butter(2, [250 / (SR / 2), 1800 / (SR / 2)], "band", output="sos"), x)
        t = np.arange(n) / SR
        e = (1 - np.exp(-t * 400)) * np.exp(-t * 18)
        f = 140 + 30 * i
        y = x * e + 0.4 * np.sin(2 * np.pi * f * t) * e
        j = int(t0 * SR)
        out[j:j + n] += y * (1.0 if i == 0 else 0.7)
    return out * amp / (np.abs(out).max() + 1e-9)


# ------------------------------------------------------------------ the beat grid

class Grid:
    """Beats from t0 at bpm: when(bar, beat) -> seconds."""

    def __init__(self, t0, bpm):
        self.t0, self.b = t0, 60.0 / bpm

    def at(self, bar, beat=0.0):
        return self.t0 + (bar * 4 + beat) * self.b
