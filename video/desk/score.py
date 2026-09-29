"""The score and the sound of each register (style only: a minimalist, hypnotic score of the mid-80s kind).

The ostinato engine: repeating arpeggios in eighths grouped 3+3+2, a pulsing viola, a cello bass, a second-violin
triplet line crossing the duple pulse, brass swells, timpani and harp for the stage. A string quartet at first,
growing to full orchestra in the fiction scenes; every chapter builds layer by layer, then stops dead.

Registers sound different:
  present  room tone, rain on the window, a clock, the lamp switch, typing, a pencil - under a thin pulsing viola
  memory   near silence: a solo piano, a classroom murmur far off, chalk, the school bell
  fiction  the full ostinato, heightened, with wooden clappers when a set splits or turns and a temple bell
Japanese textures only as sparse accents: a temple bell at each chapter card, wooden clappers, a bamboo flute.
"""
import numpy as np

import orch as O
from orch import SR, _bp, _hp, _lp, midi, tx


# ------------------------------------------------------------------ instruments

def bowed(m, dur, amp=1.0, bright=1.0, seed=0, attack=0.03):
    """A bowed string note: two detuned saws and a whisper of bow noise, low-passed; vibrato blooms after the attack."""
    t = tx(dur + 0.08)
    rng = np.random.default_rng(seed)
    f0 = midi(m)
    vib = 1 + 0.0035 * np.sin(2 * np.pi * 5.6 * t + rng.uniform(0, 6)) * np.clip((t - 0.08) / 0.15, 0, 1)
    x = np.zeros(len(t))
    for d in (-5, 4):
        ph = np.cumsum(f0 * 2 ** (d / 1200) * vib) / SR + rng.uniform()
        x += 2 * (ph % 1.0) - 1
    x += _bp(rng.normal(0, 1, len(t)), 1500, 6000) * 0.08
    x = _lp(x, min(9000, 1400 + 2600 * bright + f0 * 1.5))
    env = np.clip(t / attack, 0, 1) * np.clip((dur + 0.08 - t) / 0.08, 0, 1)
    return amp * x * env * 0.12


def temple_bell(m=40, amp=1.0, dur=7.0):
    """A large bronze bell: inharmonic partials, slow beating, a very long decay."""
    t = tx(dur)
    f = midi(m)
    x = np.zeros(len(t))
    for r, d, g in ((1.0, 6.0, 1.0), (1.003, 6.0, 0.8), (2.0, 3.5, 0.5), (2.76, 2.8, 0.45), (4.07, 1.6, 0.3), (5.4, 1.0, 0.2), (6.8, 0.6, 0.12)):
        x += g * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d)
    x += _lp(np.random.default_rng(2).normal(0, 1, len(t)), 900) * np.exp(-t / 0.02) * 0.3
    return amp * x * 0.22


def clappers(amp=1.0, seed=0):
    """Two blocks of hard wood struck together, twice: the sound of a set about to change."""
    out = np.zeros(int(0.5 * SR))
    for k, o in enumerate((0.0, 0.16)):
        t = tx(0.18)
        rng = np.random.default_rng(seed + k)
        x = (np.sin(2 * np.pi * 1850 * t) * 0.7 + np.sin(2 * np.pi * 2930 * t) * 0.4) * np.exp(-t / 0.018)
        x += _bp(rng.normal(0, 1, len(t)), 1500, 7000) * np.exp(-t / 0.006) * 0.8
        i = int(o * SR)
        out[i:i + len(x)] += x * (1.0 if k == 0 else 0.85)
    return amp * out * 0.6


def wood_slide(dur=0.8, amp=1.0, seed=3):
    t = tx(dur)
    x = _bp(np.random.default_rng(seed).normal(0, 1, len(t)), 180, 1600)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.7
    return amp * x * env * 0.25


def rain(dur, amp=1.0, seed=5):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = _bp(rng.normal(0, 1, n), 900, 7000) * 0.12
    drops = np.zeros(n)
    idx = rng.integers(0, n, int(dur * 40))
    drops[idx] = rng.uniform(0.3, 1.0, len(idx))
    x += _bp(drops, 2000, 9000) * 0.8
    return amp * x


def room_tone(dur, amp=1.0, seed=7, hum=True):
    t = tx(dur)
    x = _lp(np.random.default_rng(seed).normal(0, 1, len(t)), 700) * 0.05
    if hum:
        x += 0.006 * np.sin(2 * np.pi * 50 * t)
    return amp * x


def traffic(dur, amp=1.0, seed=8):
    t = tx(dur)
    x = _lp(np.random.default_rng(seed).normal(0, 1, len(t)), 260)
    return amp * x * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t + 1)) * 0.3


def murmur(dur, amp=1.0, seed=9):
    """A classroom, heard from inside: many small voices, chairs, a cough."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    x = np.zeros(len(t))
    for k in range(10):
        v = _bp(rng.normal(0, 1, len(t)), 300 + 60 * k, 1400 + 120 * k)
        e = np.clip(np.sin(2 * np.pi * rng.uniform(2.5, 5) * t + rng.uniform(0, 6)), 0, 1) ** 2
        e *= np.clip(np.sin(2 * np.pi * rng.uniform(0.1, 0.3) * t + rng.uniform(0, 6)), 0, 1)
        x += v * e
    return amp * x * 0.05


def chalk(amp=1.0, seed=0):
    t = tx(0.25)
    x = _bp(np.random.default_rng(seed).normal(0, 1, len(t)), 2500, 8000) * np.exp(-t / 0.05)
    return amp * x * 0.25


def pencil(dur, amp=1.0, seed=4):
    t = tx(dur)
    x = _bp(np.random.default_rng(seed).normal(0, 1, len(t)), 2500, 9000)
    e = np.clip(np.sin(2 * np.pi * 7 * t), 0, 1) ** 1.5 * np.clip(np.sin(2 * np.pi * 0.9 * t) + 0.6, 0, 1)
    return amp * x * e * 0.12


def paper_flutter(dur, amp=1.0, seed=6):
    t = tx(dur)
    x = _bp(np.random.default_rng(seed).normal(0, 1, len(t)), 600, 5000)
    e = (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t)) * np.sin(np.pi * np.clip(t / dur, 0, 1))
    return amp * x * e * 0.12


def envelope_tear(amp=1.0, seed=2):
    t = tx(0.7)
    rng = np.random.default_rng(seed)
    x = _bp(rng.normal(0, 1, len(t)), 1200, 7000) * (np.abs(rng.normal(0, 1, len(t))) > 1.2) * np.clip(1 - t / 0.7, 0, 1)
    return amp * x * 0.3


def ding(ok=True, amp=1.0):
    return O.celesta(84 if ok else 50, amp=amp * (0.5 if ok else 0.8), dur=0.8)


# ------------------------------------------------------------------ the ostinato engine

A_MIN = [(45, 57, 60, 64), (41, 57, 60, 65), (48, 55, 60, 64), (43, 55, 59, 62)]      # Am  F  C  G
DOUBT = [(45, 57, 60, 64), (46, 58, 62, 65), (45, 57, 60, 64), (40, 56, 59, 64)]      # Am  Bb Am E
DAWN = [(48, 55, 60, 64), (43, 55, 59, 62), (45, 57, 60, 64), (41, 57, 60, 65)]       # C   G  Am F
FINAL = [(48, 55, 62, 64, 67)]                                                        # C add9, held
ACC = [1.0, 0.55, 0.6, 0.9, 0.55, 0.6, 0.85, 0.55]                                    # 3 + 3 + 2 accents
ARP = [1, 2, 3, 2, 3, 1, 3, 2]


def ostinato(bus, t0, t1, prog, levels, bpm=120, bars_per_chord=1, seed=0):
    """Fill [t0, t1) with the ostinato. levels: {layer: level or level(t)}; layers pulse, arp, counter, bass, brass,
    timp, harp."""
    e8 = 60 / bpm / 2
    bar = e8 * 8
    lv = lambda name, t: (levels[name](t) if callable(levels[name]) else levels[name]) if name in levels else 0.0
    n = int((t1 - t0) / e8)
    for i in range(n):
        t = t0 + i * e8
        b = i // 8
        ch = prog[(b // bars_per_chord) % len(prog)]
        pos = i % 8
        root, tones = ch[0], ch[1:]
        acc = ACC[pos]
        if lv("pulse", t) > 0:
            bus.add(bowed(tones[0] - 12 + (7 if pos in (3, 6) else 0), e8 * 0.9, lv("pulse", t) * acc, bright=0.5, seed=i),
                    t, pan=0.62)
        if lv("arp", t) > 0:
            m = tones[ARP[pos] - 1] + (12 if b % 2 and pos > 4 else 0)
            bus.add(bowed(m + 12, e8 * 0.85, lv("arp", t) * acc, bright=0.9, seed=i + 7), t, pan=0.14)
        if lv("counter", t) > 0 and pos % 2 == 0:                          # three against two
            for k in range(3):
                bus.add(bowed(tones[k % len(tones)] + 12, e8 * 0.6, lv("counter", t) * 0.8, bright=1.0, seed=i * 3 + k),
                        t + k * e8 * 2 / 3, pan=0.88)
        if lv("bass", t) > 0 and pos in (0, 4):
            bus.add(bowed(root - 12 if root > 44 else root, e8 * 3.8, lv("bass", t), bright=0.4, seed=i + 3, attack=0.06), t, pan=0.74)
        if lv("brass", t) > 0 and pos == 0 and b % bars_per_chord == 0:
            bus.add(O.brass([root, tones[0], tones[1], tones[2]], bar * bars_per_chord * 0.95, amp=lv("brass", t), bright=0.6,
                            seed=b), t, pan=0.5)
        if lv("timp", t) > 0 and pos == 0:
            bus.add(O.timpani(root - 12 if root > 40 else root, amp=lv("timp", t)), t, pan=0.5)
        if lv("harp", t) > 0 and pos == 0 and b % bars_per_chord == 0:
            for k, m in enumerate(sorted(tones) + [x + 12 for x in sorted(tones)]):
                bus.add(O.harp(m + 12, amp=lv("harp", t) * 0.8), t + k * 0.06, pan=0.2 + 0.07 * k)


def ramp_up(a, b, lo=0.0, hi=1.0):
    return lambda t: lo + (hi - lo) * min(1.0, max(0.0, (t - a) / max(1e-3, b - a)))


def piano_motif(bus, t0, t1, amp=1.0, step=1.6, seed=0):
    """The memory theme: a few falling notes, far apart, in A minor."""
    notes = [76, 74, 72, 69, 71, 67, 69, 64]
    k = 0
    t = t0
    while t < t1 - 0.3:
        bus.add(O.piano([notes[k % len(notes)]], 1.6, amp=amp, seed=seed + k), t, pan=0.45)
        if k % 4 == 3:
            bus.add(O.piano([45, 52], 2.4, amp=amp * 0.5, seed=seed + 50 + k), t, pan=0.55)
        k += 1
        t += step
