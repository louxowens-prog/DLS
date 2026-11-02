"""The house band of the underworld, synthesized (nothing sampled, every riff original): 1930s hot jazz crossed with
manic early-80s new wave and ska.

  hot jazz   tuba on the two-beat, banjo chunking, stride piano, a muted "wah-wah" trumpet, clarinet runs, brushes
  ska        offbeat guitar skank and organ, walking bass, trumpet and sax in unison, rimshots
  drag       a slow-drag blues: tuba, brushes, a wailing clarinet, a mournful wah trumpet
  new wave   driving eighth-note bass, a buzzy combo organ, tight snare and handclaps, horn stabs
  big band   the shout chorus: full horns, swing ride, walking bass, fills
A groove is rendered for any stretch of time on its own beat grid; `energy` (0..1, a function of time) thins it out
under speech and fills it up between the words. Riffs and stings mark the cuts.
"""
import math

import numpy as np
from scipy import signal

import orch as O

SR = O.SR
midi, tx = O.midi, O.tx


# ------------------------------------------------------------------ instruments

_ks = {}


def pluck(m, amp=1.0, dur=0.4, seed=0, damp=0.996):
    """One plucked string (cached per pitch and length): banjo and the ska guitar's chop."""
    key = (m, round(dur, 2), damp)
    if key not in _ks:
        rng = np.random.default_rng(seed + m)
        f = midi(m)
        p = max(2, int(SR / f))
        n = int(dur * SR)
        buf = rng.uniform(-1, 1, p)
        reps = n // p + 1
        rows = [buf.copy()]
        for _ in range(reps):
            buf = 0.5 * (buf + np.roll(buf, -1)) * damp
            rows.append(buf.copy())
        _ks[key] = np.concatenate(rows)[:n]
    return amp * _ks[key]


def strum(notes, amp=1.0, dur=0.3, damp=0.996, hp=300):
    n = int(dur * SR)
    out = np.zeros(n + int(0.03 * SR))
    for j, m in enumerate(notes):
        y = pluck(m, 1.0, dur, damp=damp)
        k = int(j * 0.005 * SR)
        out[k:k + len(y)] += y
    env = np.clip((dur + 0.03 - np.arange(len(out)) / SR) / 0.03, 0, 1)
    return amp * O._hp(out, hp) * env * 0.3 / max(1, len(notes)) ** 0.5


def wah(m, dur, amp=1.0, wahs=1, seed=0):
    """A muted trumpet with a plunger: a buzzy horn through a band-pass that opens and closes ('wah-wah')."""
    t = tx(dur + 0.05)
    f = midi(m) * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.15) / 0.2, 0, 1))
    ph = np.cumsum(f) / SR
    x = 2 * (ph % 1.0) - 1
    x = np.tanh(2.5 * x)
    open_ = 0.5 - 0.5 * np.cos(2 * np.pi * wahs * np.clip(t / max(dur, 0.05), 0, 1))
    fc = 500 + 1900 * open_
    y = np.zeros(len(t))
    seg = 256
    for i in range(0, len(t), seg):
        lo, hi = fc[i] * 0.6, min(fc[i] * 1.8, SR / 2 - 100)
        b, a = signal.butter(2, [lo / (SR / 2), hi / (SR / 2)], "band")
        y[i:i + seg] = signal.lfilter(b, a, x[max(0, i - 512):i + seg])[-len(x[i:i + seg]):]
    env = np.clip(t / 0.02, 0, 1) * np.clip((dur + 0.05 - t) / 0.05, 0, 1)
    return amp * y * env * 0.5


def organ(notes, dur, amp=1.0, buzz=1.0):
    """A combo organ (the new-wave kind): bright pulse waves, a fast vibrato."""
    t = tx(dur + 0.02)
    out = np.zeros(len(t))
    for m in notes:
        f = midi(m) * (1 + 0.005 * np.sin(2 * np.pi * 6.5 * t))
        ph = np.cumsum(f) / SR
        out += np.sign(np.sin(2 * np.pi * ph)) * 0.6 + np.sign(np.sin(4 * np.pi * ph)) * 0.25 * buzz
    out = O._lp(out, 3200)
    env = np.clip(t / 0.005, 0, 1) * np.clip((dur + 0.02 - t) / 0.02, 0, 1)
    return amp * out * env * 0.12 / max(1, len(notes)) ** 0.5


def ubass(m, dur, amp=1.0):
    """An upright bass, plucked: a round thump that dies away."""
    t = tx(dur + 0.2)
    f = midi(m)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    env = np.clip(t / 0.004, 0, 1) * np.exp(-t / 0.35) * np.clip((dur + 0.2 - t) / 0.08, 0, 1)
    return amp * np.tanh(1.4 * x) * env * 0.45


def ebass(m, dur, amp=1.0):
    """The new-wave bass: a picked, slightly driven electric."""
    t = tx(dur + 0.02)
    f = midi(m)
    ph = np.cumsum(np.full(len(t), f)) / SR
    x = O._lp(2 * (ph % 1.0) - 1, 900 + 1500 * np.exp(-t / 0.05).mean())
    env = np.clip(t / 0.003, 0, 1) * np.exp(-t / 0.25) * np.clip((dur + 0.02 - t) / 0.02, 0, 1)
    return amp * np.tanh(2.0 * x) * env * 0.4


def brush(amp=1.0, seed=0, dur=0.18):
    t = tx(dur)
    x = O._bp(O._noise(len(t), seed), 2500, 9000) * np.exp(-t / (dur * 0.35))
    return amp * x * 0.35


def rim(amp=1.0, seed=0):
    t = tx(0.08)
    return amp * (np.sin(2 * np.pi * 1700 * t) * np.exp(-t / 0.01) + O._bp(O._noise(len(t), seed), 2000, 8000) * np.exp(-t / 0.01) * 0.5) * 0.5


def clap(amp=1.0, seed=0):
    t = tx(0.2)
    x = np.zeros(len(t))
    for k in range(3):
        j = int(k * 0.009 * SR)
        x[j:] += O._bp(O._noise(len(t) - j, seed + k), 900, 5000) * np.exp(-np.arange(len(t) - j) / SR / 0.012)
    x += O._bp(O._noise(len(t), seed + 9), 900, 4000) * np.exp(-t / 0.08) * 0.4
    return amp * x * 0.5


def ride(amp=1.0, seed=0):
    t = tx(0.9)
    rng = np.random.default_rng(seed)
    x = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in rng.uniform(3000, 9000, 8)) / 8
    x = x * np.exp(-t / 0.35) + O._hp(rng.normal(0, 1, len(t)), 7000) * np.exp(-t / 0.05) * 0.4
    return amp * x * 0.25


def xylo(m, amp=1.0):
    t = tx(0.5)
    f = midi(m)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.12) + 0.3 * np.sin(2 * np.pi * f * 3.9 * t) * np.exp(-t / 0.04)
    return amp * x * 0.45


def xylo_run(ms, gap=0.045, amp=1.0):
    out = np.zeros(int((len(ms) * gap + 0.5) * SR))
    for i, m in enumerate(ms):
        x = xylo(m, amp * (0.7 + 0.3 * i / max(1, len(ms) - 1)))
        j = int(i * gap * SR)
        out[j:j + len(x)] += x
    return out


# ------------------------------------------------------------------ harmony

def triad(root, kind="maj"):
    third = 4 if kind in ("maj", "7") else 3
    ch = [root, root + third, root + 7]
    if kind == "7":
        ch.append(root + 10)
    return ch


STYLES = {
    #            bpm-free: progression as (root midi, kind) per bar, swing, key tonic
    "hotjazz": dict(prog=[(53, "maj"), (50, "7"), (55, "7"), (48, "7")], swing=0.62),        # F  D7  G7  C7
    "ska": dict(prog=[(55, "maj"), (52, "min"), (48, "maj"), (50, "maj")], swing=0.5),       # G  Em  C   D
    "drag": dict(prog=[(50, "min"), (55, "min"), (57, "7"), (50, "min")], swing=0.66),       # Dm Gm  A7  Dm
    "newwave": dict(prog=[(57, "min"), (53, "maj"), (48, "maj"), (55, "maj")], swing=0.5),   # Am F   C   G
    "bigband": dict(prog=[(58, "maj"), (55, "7"), (48, "min"), (53, "7")], swing=0.64),      # Bb G7  Cm  F7
}


class Grid:
    """A beat grid from t0 at bpm; beat(i) gives the time of beat i, with swung eighths."""

    def __init__(self, t0, bpm, swing=0.5):
        self.t0, self.beat_len, self.swing = t0, 60.0 / bpm, swing

    def t(self, beat, eighth=0):
        return self.t0 + (beat + (self.swing if eighth else 0.0)) * self.beat_len


def groove(bus, t0, t1, style, bpm, energy=lambda t: 1.0, level=1.0, seed=0, riffs=True, melody=True):
    """Render a style's groove from t0 to t1 on its own grid. energy(t) 0..1 thins or fills it."""
    S = STYLES[style]
    G = Grid(t0, bpm, S["swing"])
    B = G.beat_len
    nbeats = int((t1 - t0) / B)
    rng = np.random.default_rng(seed)
    for b in range(nbeats):
        t = G.t(b)
        if t >= t1 - 0.05:
            break
        e = max(0.0, min(1.0, energy(t)))
        bar, beat = divmod(b, 4)
        root, kind = S["prog"][bar % len(S["prog"])]
        ch = triad(root, kind)
        up = [m + 12 for m in ch]
        if style == "hotjazz":
            if beat in (0, 2):                                                  # the two-beat: root, then the fifth
                bus.add(O.tuba(root - 12 if beat == 0 else root - 5, B * 0.9, amp=0.9 * level), t, pan=0.45)
            bus.add(strum(up, 0.8 * level * (0.6 + 0.4 * e), 0.22), t, pan=0.62)
            if beat in (1, 3):
                bus.add(brush(0.8 * level, seed + b), t, pan=0.55)
                bus.add(O.piano(up + [up[0] + 12], 0.18, amp=0.5 * level * e, seed=b), t, pan=0.35)
            else:
                bus.add(O.piano([root - 12], 0.25, amp=0.55 * level * e, seed=b + 1), t, pan=0.35)
                bus.add(O.kick(0.35 * level, b), t)
            bus.add(O.hat(0.25 * level, b), G.t(b, 1), pan=0.6)
            if melody and e > 0.6 and beat == 0 and bar % 2 == 1:                  # a clarinet run up to the next chord
                for k, m in enumerate([ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[0] + 24]):
                    bus.add(O.reed(m, B * 0.45, amp=0.55 * level * e, seed=b + k), G.t(b + k // 2, k % 2), pan=0.3)
            if riffs and e > 0.6 and beat == 2 and bar % 2 == 0:                  # the muted trumpet answers: wah-wah
                bus.add(wah(ch[2] + 12, B * 0.9, 0.7 * level * e, wahs=1), t, pan=0.7)
                bus.add(wah(ch[1] + 12, B * 0.9, 0.7 * level * e, wahs=1), t + B, pan=0.7)
        elif style == "ska":
            walk = [root - 12, root - 12 + 4 if kind == "maj" else root - 12 + 3, root - 12 + 7, root - 12 + 9]
            bus.add(ubass(walk[beat], B * 0.9, 0.9 * level), t, pan=0.5)
            bus.add(strum(up, 0.9 * level, 0.09, damp=0.99, hp=700), G.t(b, 1), pan=0.68)           # the skank, on the off-beat
            bus.add(organ(up, B * 0.3, 0.6 * level * e), G.t(b, 1), pan=0.32)
            bus.add(O.hat(0.3 * level, b), t, pan=0.6)
            bus.add(O.hat(0.22 * level, b + 7), G.t(b, 1), pan=0.6)
            if beat == 2:
                bus.add(O.kick(0.55 * level, b), t)
                bus.add(rim(0.7 * level, b), t, pan=0.45)
            if riffs and e > 0.6 and beat == 0 and bar % 2 == 0:                  # trumpet and sax in unison
                for k, m in enumerate([ch[2] + 12, ch[1] + 12, ch[0] + 12, ch[1] + 12]):
                    bus.add(O.brass([m], B * 0.4, amp=0.55 * level * e, seed=b + k, bright=0.8), G.t(b + 2 + k // 2, k % 2), pan=0.4)
        elif style == "drag":
            if beat in (0, 2):
                bus.add(O.tuba(root - 12 if beat == 0 else root - 5, B * 1.6, amp=0.9 * level), t, pan=0.45)
                bus.add(O.kick(0.3 * level, b), t)
            bus.add(brush(0.9 * level, seed + b, 0.35), t, pan=0.55)
            bus.add(O.piano(up, 0.3, amp=0.45 * level * e, seed=b), G.t(b, 1), pan=0.35)
            if melody and e > 0.5 and beat == 0:                                  # the clarinet wails over the bar
                m = [ch[2] + 12, ch[1] + 12, ch[0] + 12, ch[2]][bar % 4]
                bus.add(O.reed(m, B * 2.8, amp=0.5 * level * e, seed=b), t + B * 0.5, pan=0.3)
            if riffs and e > 0.5 and beat == 2 and bar % 2 == 1:
                bus.add(wah(ch[1] + 12, B * 1.6, 0.6 * level * e, wahs=2), t, pan=0.7)
        elif style == "newwave":
            for k in range(2):                                                 # driving eighths, octave bounce
                bus.add(ebass(root - 12 + (12 if k else 0), B * 0.45, 0.85 * level), G.t(b, k), pan=0.5)
                bus.add(O.hat(0.3 * level, b * 2 + k), G.t(b, k), pan=0.62)
            if beat in (0, 2):
                bus.add(O.kick(0.8 * level, b), t)
            else:
                bus.add(O.snare(0.5 * level, b), t, pan=0.5)
                bus.add(clap(0.6 * level * e, b), t, pan=0.45)
            if beat == 0:
                bus.add(organ(up, B * 3.6, 0.7 * level * (0.4 + 0.6 * e)), t, pan=0.35)
            if riffs and e > 0.6 and beat == 3 and bar % 2 == 1:                  # horn stabs into the next bar
                bus.add(O.brass(up, B * 0.35, amp=0.6 * level * e, seed=b), G.t(b, 1), pan=0.6)
        elif style == "bigband":
            walk = [root - 12, root - 12 + 2, root - 12 + 4 if kind != "min" else root - 12 + 3, root - 12 + 7]
            bus.add(ubass(walk[beat], B * 0.95, 0.9 * level), t, pan=0.5)
            bus.add(ride(0.5 * level, b), t, pan=0.62)
            if beat in (1, 3):
                bus.add(O.hat(0.4 * level, b), t, pan=0.62)
                bus.add(ride(0.3 * level, b + 5), G.t(b, 1), pan=0.62)
            if beat == 0:
                bus.add(O.kick(0.4 * level, b), t)
            if riffs and e > 0.5 and beat in (0, 2):                              # the shout: brass and saxes
                voicing = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[0] + 24]
                bus.add(O.brass(voicing, B * (0.9 if beat == 0 else 0.4), amp=0.75 * level * e, seed=b), t, pan=0.5)
                if beat == 2:
                    bus.add(O.snare(0.5 * level, b), G.t(b, 1), pan=0.45)
            elif e > 0.3 and beat == 3:
                bus.add(O.piano(up, 0.2, amp=0.4 * level, seed=b), t, pan=0.35)


def fanfare(bus, t, level=1.0, key=53):
    """A ta-da: brass chord with a drum hit and a cymbal."""
    bus.add(O.snare_roll(0.5, amp=0.6 * level), t - 0.5, pan=0.5)
    bus.add(O.brass([key, key + 4, key + 7, key + 12], 1.2, amp=1.0 * level, seed=3), t, pan=0.5)
    bus.add(O.tuba(key - 12, 1.0, amp=1.0 * level), t, pan=0.45)
    bus.add(O.cymbal(0.9 * level, 2.0), t, pan=0.5)
    bus.add(O.kick(0.9 * level), t)


def button(bus, t, level=1.0, key=53):
    """The end of a number: two short stabs (the 'shave and a haircut' kind of cadence is avoided; just a hit)."""
    bus.add(O.brass([key - 5, key, key + 4, key + 7], 0.3, amp=0.9 * level, seed=5), t, pan=0.5)
    bus.add(O.kick(0.8 * level), t)
    bus.add(O.cymbal(0.7 * level, 1.2), t, pan=0.5)


def card_sting(bus, t, level=1.0, n=0):
    """Under each hand-lettered room card: a xylophone run up and a woodblock pair."""
    base = [72, 74, 76, 79, 81, 84, 86, 88][n % 3:]
    bus.add(xylo_run(base[:6], 0.04, 0.9 * level), t + 0.05, pan=0.5)
    bus.add(O.woodblock(0.8 * level, 900), t + 0.45, pan=0.4)
    bus.add(O.woodblock(0.8 * level, 1200), t + 0.62, pan=0.6)
