"""Soundtrack: an original, synthesized 1960s big band under the narration, and the race around it.

Every transition in edit.py gets a hit (a horn stab plus drums, and a whoosh on wipes). The announcer is put
through a stadium PA with the crowd swelling under him. Loudness is set with a static gain (no compressor),
so the contrast between the quiet explanations and the loud race moments survives.
Writes build/audio.wav (48 kHz stereo).

Second pass (the default; SR_ORIG=1 rebuilds the first delivery bit for bit): pronunciation fixes (the fixed
readings, script.SAY, come in through the timeline), and a band that still reads on a phone under the narration.
The first mix carved the band 30 dB out of the speech band whenever anyone talked, so on a phone speaker the big
band sat ~20 dB under the voice and its brass all but vanished for 89% of the film. Now the band keeps its body
under the voice (only the consonant band is carved, lightly, and a spectral sidechain holds the music under the
voice only in the bands the two share), the walking bass has its finger attack, and the horns kick in the breaths
around the narrator the way a big band plays around a singer, with pickups into the section changes and engine
revs on the grid.
"""
import os
import wave

import numpy as np
from scipy import signal

import bigband as B
import jazz as J
import synth as S
from cues import C
from edit import EDIT, WIPE
from timeline import TL
from voice import SR as VSR, pauses

ORIG = os.environ.get("SR_ORIG") == "1"          # SR_ORIG=1 rebuilds the mix exactly as first delivered


def line_wav(key):
    """The line as heard: the timeline already holds the second-pass readings (script.SAY) unless SR_ORIG=1."""
    return TL.lines[key]["wav"]


SR = B.SR
HERE = os.path.dirname(os.path.abspath(__file__))
N = int((TL.total + 0.5) * SR)
BAR = 4 * B.BEAT

# eight-bar loop in B-flat: Bb6 | G7b9 | Cm9 | F13 | Bb6 | Bb7 | Eb9 | Edim7
CHORDS = [[58, 62, 65, 67, 70, 74], [55, 59, 62, 65, 68, 71], [60, 63, 67, 70, 74], [53, 57, 63, 67, 74],
          [58, 62, 65, 67, 70, 74], [58, 62, 65, 68, 72], [63, 67, 70, 73, 77], [64, 67, 70, 73]]
ROOTS = [34, 31, 36, 29, 34, 34, 39, 40]


def db(v):
    return 10 ** (v / 20)


def chord_at(t):
    return CHORDS[int(t / BAR) % 8]


class Bus:
    def __init__(self):
        self.x = np.zeros((2, N))

    def add(self, sig, t, gain=1.0, pan=0.5):
        if sig.ndim == 1:
            sig = np.stack([sig * np.sqrt(1 - pan), sig * np.sqrt(pan)]) * np.sqrt(2)
        i = int(t * SR)
        if i >= N or i + sig.shape[1] <= 0:
            return
        if i < 0:
            sig, i = sig[:, -i:], 0
        j = min(N, i + sig.shape[1])
        self.x[:, i:j] += gain * sig[:, : j - i]


def short(sig, dur):
    """Choke a cymbal: fade it out by dur seconds so its tail never sits under the next line."""
    n = int(dur * SR)
    out = sig[: n].copy()
    out *= np.linspace(1, 0, len(out)) ** 1.5
    return out


def stereo_crowd(dur, seed=0):
    """A stadium on both sides: mostly independent roars in each ear, a little shared centre."""
    l, r, m = B.crowd(dur, seed=seed), B.crowd(dur, seed=seed + 101), B.crowd(dur, seed=seed + 202)
    return np.stack([0.8 * l + 0.45 * m, 0.8 * r + 0.45 * m]) * 0.9


def widen(x, amt):
    """Mid/side widener: the side is an all-pass-decorrelated copy of the mid, so the mono sum is untouched."""
    mid = 0.5 * (x[0] + x[1])
    side = 0.5 * (x[0] - x[1])
    d = mid
    for ms, g in ((3.1, 0.6), (4.7, -0.55), (7.9, 0.5), (11.3, -0.45)):
        n = int(ms * SR / 1000)
        b = np.zeros(n + 1)
        a = np.zeros(n + 1)
        b[0], b[n] = -g, 1.0
        a[0], a[n] = 1.0, -g
        d = signal.lfilter(b, a, d)
    side = side + amt * S._hp(d, 180)                                     # keep the low end centred
    return np.stack([mid + side, mid - side])


def energy_curve():
    E = lambda k: TL.s(k)
    pts = [(0, 0.9), (1.0, 0.6), (C["go"] - 0.05, 0.75), (C["go"], 0.0), (C["go"] + 1.2, 0.0), (C["go"] + 1.22, 1.0), (E("h2"), 0.8), (E("d1"), 0.5),
           (E("d2"), 0.55), (E("d4"), 0.45), (E("d5"), 0.6), (E("d6"), 0.8), (E("d7"), 0.45), (E("e1"), 0.5), (E("e2"), 0.6),
           (E("a1"), 0.7), (E("t2"), 1.0), (E("t3"), 0.6), (E("t4"), 0.55), (E("t6"), 0.45), (E("u1"), 0.5), (E("u2"), 0.8),
           (E("u3"), 0.55), (E("a2"), 0.8), (E("v2"), 0.75), (C["crash"] - 0.02, 0.9), (C["crash"], 0.0), (C["crash"] + 1.0, 0.0),
           (C["crash"] + 1.02, 0.7), (E("v4"), 0.5), (E("w1"), 0.6), (E("a3"), 0.4), (E("w2"), 0.3), (E("f1"), 1.0),
           (C["end_card"], 1.0), (C["end_card"] + 0.4, 0.0), (C["end"], 0.0)]
    xs, ys = zip(*sorted(pts))
    return lambda t: float(np.interp(t, xs, ys))


def walking_bass(bus, E, pluck=0.0):
    nb = int(TL.total / B.BEAT)
    rng = np.random.default_rng(3)
    for b in range(nb):
        t = b * B.BEAT
        if E(t) <= 0.02:
            continue
        bar, beat = divmod(b, 4)
        root = ROOTS[bar % 8]
        nxt = ROOTS[(bar + 1) % 8]
        ch = [m - 24 for m in CHORDS[bar % 8]]
        if beat == 0:
            m = root
        elif beat == 3:
            m = nxt + (1 if rng.random() < 0.5 else -1)                 # chromatic approach
        else:
            m = int(rng.choice([c for c in ch if 28 <= c <= 50] or [root + 7]))
        bus.add(B.upright(B.midi(m), B.BEAT * 0.95, seed=b), t, 0.55 * (0.7 + 0.3 * E(t)))
        if pluck:
            bus.add(B.pluck(B.midi(m), B.BEAT * 0.95), t, pluck * (0.7 + 0.3 * E(t)))


def pads(bus, E):
    """Sustained sax chords, two bars each, a soft bed under the voice."""
    nbar = int(TL.total / BAR)
    for k in range(0, nbar, 1):
        t = k * BAR
        if E(t + 0.1) <= 0.02:
            continue
        bus.add(B.pad(CHORDS[k % 8], BAR * 0.98, seed=k), t, 0.16)


def backgrounds(bus, E):
    """Big-band 'backgrounds': a trombone-and-sax 'bwaaa-ap' figure every other bar."""
    nbar = int(TL.total / BAR)
    for k in range(1, nbar, 2):
        t = k * BAR
        if E(t) < 0.3:
            continue
        ch = CHORDS[k % 8]
        bus.add(B.chord_hit(ch[:4], dur=B.BEAT * 1.4, kinds=("sax", "tbn", "sax"), seed=k * 3), t, 0.18)
        bus.add(B.chord_hit(ch[:4], dur=B.BEAT * 0.4, kinds=("sax", "tbn", "sax"), seed=k * 3 + 1), t + 2.5 * B.BEAT, 0.16)


def fanfare(bus, t_end, seed=0):
    """A trumpet call leading into an announcer line: Bb, D, F, Bb (with a doit)."""
    notes = [70, 74, 77, 82]
    d = 0.11
    t0 = t_end - d * 3 - 0.28
    for i, m in enumerate(notes):
        dur = d if i < 3 else 0.28
        bus.add(B.horn(B.midi(m), dur, "tpt", 0.55, doit=2 if i == 3 else 0, seed=seed + i), t0 + i * d, 0.5)
        bus.add(B.horn(B.midi(m - 12), dur, "tpt", 0.4, seed=seed + 10 + i), t0 + i * d, 0.35)


PLUCK = 0.2            # the bass's finger attack, against the 0.55 upright
COMP = 0.62            # the horn kicks in the breaths
BODY = 0.0             # how deep the band's 300 Hz - 1.1 kHz body is ducked under the voice (first pass: 0.97)
MID = 0.4              # and its 1.1 - 4 kHz consonant band (first pass: 0.97); the sidechain does the rest
UNMASK = 8.0           # dB the music is held under the voice in each band it shares (+6 dB in 1-5 kHz)


def breaths():
    """Silences inside the lines, and the short gaps between them: where a big band kicks around a singer."""
    out = []
    for k in TL.order:
        L = TL.lines[k]
        out += [(L["start"] + a, L["start"] + b) for a, b in pauses(line_wav(k), 0.2)]
    for a_key, b_key in zip(TL.order, TL.order[1:]):
        if 0.2 <= TL.s(b_key) - TL.e(a_key) < 0.6:
            out.append((TL.e(a_key), TL.s(b_key)))
    return sorted(out)


def busy():
    """Moments that already have a hit or a set piece of their own: no kicks near them."""
    spans = [(t - 0.35, t + 0.35) for t, *_ in EDIT[1:]]
    spans += [(TL.s(k) - 0.7, TL.e(k) + 0.35) for k in ("a0", "a1", "a2", "a3")]      # fanfares and the announcer
    spans += [(TL.s(k), TL.e(k) + 0.1) for k in ("d6", "t2", "u2")]                   # gauges, hazards, the loop
    spans += [(TL.e(k) - 1.3, TL.e(k) + 0.6) for k in ("d2", "d3")]                   # "... Done." and its hit
    spans += [(0.0, C["go"] + 2.0), (C["crash"] - 1.0, C["crash"] + 1.4), (TL.e("w2"), C["end"])]
    return spans


def figure(bus, kind, t, room, ch, nxt, seed):
    """One big-band kick at t: the section voicing an octave up (trumpets on top), shaped by kind."""
    top = sorted(m + 12 for m in ch[-4:])
    hi = top[-1]
    if kind == "kick":
        bus.add(B.chord_hit(top, dur=min(0.12, room - 0.05), seed=seed), t, 0.55)
    elif kind == "fall":
        bus.add(B.chord_hit(top[-3:], dur=0.15, fall=4, seed=seed), t, 0.55)
    elif kind == "doit":
        bus.add(B.chord_hit(top, dur=0.13, doit=3, seed=seed), t, 0.5)
    elif kind == "punch":                                              # "ba-DAH": short, then long on the next eighth
        bus.add(B.chord_hit(top, dur=0.06, seed=seed), t, 0.45)
        bus.add(B.chord_hit(top, dur=0.13, seed=seed + 1), nxt, 0.55)
    elif kind == "shake":                                              # lead trumpet shakes, the section holds under it
        bus.add(B.shake(B.midi(hi), 0.27, seed=seed), t, 0.32)
        bus.add(B.chord_hit(top[:-1], dur=0.27, kinds=("sax", "tbn", "sax"), seed=seed + 3), t, 0.3)
    elif kind == "lick":                                               # sax soli: three chord tones up to the top
        tones = sorted({m for m in range(hi - 12, hi + 1) if m % 12 in {c % 12 for c in ch}})[-3:]
        for i, m in enumerate(tones):
            for o, g in ((0, 0.42), (-12, 0.32)):
                bus.add(B.horn(B.midi(m + o), 0.1, "sax", 0.6, seed=seed + 2 * i + (o < 0)), t + i * B.BEAT / 3, g)
    else:                                                              # rip: trombones slide up into the stab
        bus.add(B.horn(B.midi(top[0] - 12), 0.2, "tbn", 0.6, rip=7, seed=seed), t, 0.45)
        bus.add(B.horn(B.midi(top[1] - 12), 0.2, "tbn", 0.6, rip=7, seed=seed + 1), t, 0.4)
        bus.add(B.chord_hit(top, dur=0.12, seed=seed + 2), t + 0.09, 0.5)


def kicks(bus):
    """Horn kicks in the breaths, on the swing grid, with air between them; returns their times."""
    nb = int(TL.total / B.BEAT) + 2
    grid = np.array(sorted([b * B.BEAT for b in range(nb)] + [B.swing_pos(b, 1) for b in range(nb)]))
    spans = busy()
    long_figs = ("punch", "shake", "rip", "lick")
    placed, k = [], 0
    for a, b in breaths():
        if any(s0 < b and a < s1 for s0, s1 in spans) or (placed and a - placed[-1] < 1.4):
            continue
        cand = grid[(grid >= a + 0.03) & (grid <= b - 0.18)]
        if not len(cand):
            continue
        t = float(cand[0])
        room = b - 0.05 - t
        kind = long_figs[k % 4] if room >= 0.42 else (("fall", "doit")[k % 2] if room >= 0.26 else "kick")
        nxt = float(grid[grid > t + 0.01][0])
        figure(bus, kind, t, room, chord_at(t), nxt, seed=1000 + 10 * k)
        placed.append(t)
        k += 1
    return placed


def pickup(bus, t_land, n=4, seed=0):
    """A brass pickup landing on a section change: the head of the theme (Bb C D F), swung, trumpets in octaves
    with a third below and trombones an octave down."""
    lead, third = [70, 72, 74, 77][-n:], [67, 69, 70, 74][-n:]
    times, t = [], t_land
    for i in range(n):
        t -= (1 - B.SWING) * B.BEAT if i % 2 == 0 else B.SWING * B.BEAT
        times.append(t)
    for i, tt in enumerate(times[::-1]):
        bus.add(B.horn(B.midi(lead[i]), 0.1, "tpt", 0.55, seed=seed + i), tt, 0.5)
        bus.add(B.horn(B.midi(third[i]), 0.1, "tpt", 0.45, seed=seed + 10 + i), tt, 0.32)
        bus.add(B.horn(B.midi(lead[i] - 12), 0.1, "tbn", 0.5, seed=seed + 20 + i), tt, 0.32)


STEMS = {}


def parts():
    """Everything before the mix: the band, the race, the kicks and the voices, each with its room."""
    E = energy_curve()
    band, fx, crowd_bus = Bus(), Bus(), Bus()
    T = TL.total

    drums = B.swing_kit(T, E, seed=5)
    band.add(np.stack([drums * 0.95, drums]), 0.0, 1.0)
    walking_bass(band, E, pluck=0.0 if ORIG else PLUCK)
    pads(band, E)
    backgrounds(band, E)
    comp = Bus()                     # horns in the breaths: ducked only while a word is actually sounding
    if not ORIG:
        kicks(comp)
        for key, n in (("d1", 3), ("e1", 4), ("u1", 4), ("w1", 4)):          # pickups into the section changes
            t_land = next(t for t, name, tr in EDIT if abs(t - TL.s(key)) < 0.3)
            pickup(comp, t_land, n, seed=1500 + 30 * n + int(t_land))
        pickup(comp, TL.s("h2") - 0.3, 3, seed=1590)                          # out of the launch, into the race
        a, b = next((a, b) for a, b in breaths() if TL.s("h1") + 1.5 < a < TL.e("h1") and b - a > 0.3)
        comp.add(B.rev(min(0.33, b - a - 0.03), seed=1601), a + 0.01, 0.22)  # revs on the grid, in the hook's breaths
        comp.add(B.rev(0.28, peak=8200, seed=1602), TL.e("h1") + 0.01, 0.22)

    # ---- the grid: revs, lights, the launch in slow motion, then everyone goes
    fx.add(B.chord_hit([58, 65, 70, 74, 77, 82], dur=0.5, seed=1, doit=2), 0.0, 0.9)          # frame one: the band hits
    fx.add(short(J.crash(seed=2), 0.6), 0.0, 0.6)
    fx.add(J.kick(seed=3), 0.0, 1.0)
    for k, t in enumerate((0.9, 2.6)):
        fx.add(B.passby(1.3, seed=4 + k), t, 0.16)
    crowd_bus.add(stereo_crowd(T, seed=4), 0.0, 1.0)
    for k in range(8):                                                       # snare roll into the launch
        fx.add(J.snare(seed=200 + k, tight=0.6), C["go"] - 0.8 + k * 0.1, 0.07 + 0.03 * k)
    fx.add(B.chord_hit([58, 65, 70, 74, 77, 82], dur=0.9, seed=7), C["go"], 0.9)
    fx.add(short(J.crash(seed=8), 0.8), C["go"], 0.6)
    fx.add(J.kick(seed=9), C["go"], 1.0)
    slow = B._lp(np.random.default_rng(10).normal(0, 1, int(1.2 * SR)), 260) * np.linspace(0.2, 1, int(1.2 * SR))
    fx.add(slow * 0.7, C["go"] + 0.05, 0.6)                                  # the slow-motion 'breath'
    fx.add(B.whoosh(0.4, up=True, seed=13), C["go"] + 0.85, 0.7)
    fx.add(B.chord_hit([70, 74, 77, 82], dur=0.3, seed=11), C["go"] + 1.2, 1.0)
    fx.add(short(J.crash(seed=12), 0.9), C["go"] + 1.2, 0.8)
    fx.add(J.kick(seed=14), C["go"] + 1.2, 1.0)
    fx.add(B.passby(0.8, seed=20), C["go"] + 1.15, 0.45)

    # ---- every transition: a stab, drums, and a whoosh on wipes
    for i, (t, name, tr) in enumerate(EDIT[1:], 1):
        ch = chord_at(t)
        top = [m + 12 for m in ch[-4:]]
        th = t                                                                # on the cut frame / the frame the wipe covers
        fx.add(B.chord_hit(top, dur=0.16, seed=300 + i, fall=3 if i % 5 == 0 else 0), th, 0.6)
        fx.add(J.kick(seed=i), th, 0.85)
        if tr.startswith("head") or tr == "iris":
            fx.add(B.whoosh(WIPE, seed=i, up=i % 2 == 0, rtl=tr.startswith("head")), t - WIPE / 2 - 0.06, 0.55)   # rides the face across
            fx.add(short(J.crash(seed=i), 0.3), th, 0.3)
        elif tr == "split":
            fx.add(J.snare(seed=i, tight=1.3), th, 0.7)
            fx.add(J.noise_hit(0.15, 800, 9000, seed=i), th, 0.3)
        else:
            fx.add(J.snare(seed=i, tight=1.2), th, 0.55)

    # ---- the announcer: a fanfare in, the crowd swells under him
    for k, key in enumerate(("a0", "a1", "a2", "a3")):
        if key != "a0":
            fanfare(fx, TL.s(key) - 0.02, seed=400 + 10 * k)
    fx.add(B.chord_hit([58, 65, 70, 74, 77, 82], dur=0.6, seed=450, doit=2), TL.e("a1") + 0.02, 0.9)
    fx.add(short(J.crash(seed=451), 0.6), TL.e("a1") + 0.02, 0.6)
    # 'done!' moments get the crowd
    for key in ("d2", "d3"):
        t = TL.e(key) + 0.02                                              # right after "Done."
        fx.add(B.chord_hit([70, 74, 77, 82], dur=0.4, doit=2, seed=int(t)), t, 0.6)
        fx.add(short(J.crash(seed=int(t)), 0.5), t, 0.4)

    # ---- the dashboard: a blip for every gauge
    for k, t in enumerate(C["gauges"]):
        fx.add(B.horn(B.midi(70 + [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17][k]), 0.1, "tpt", 0.5, seed=500 + k), t, 0.28)

    # ---- the dinner grand prix: every hazard is a hit
    for k, t in enumerate(C["hazards"]):
        ch = CHORDS[(k * 3) % 8]
        fx.add(B.chord_hit([m + 12 for m in ch[-3:]], dur=0.16, fall=4 if k in (5, 7) else 0, doit=2 if k == 3 else 0, seed=600 + k), t, 0.5)
        fx.add(J.snare(seed=610 + k, tight=0.9), t, 0.45)
        if k in (0, 4, 6):
            fx.add(B.screech(0.45, seed=620 + k), t + 0.05, 0.22)
    tw = C["hazards"][7]                                                     # the wine: slow motion, then snap
    fx.add(B.riser(0.5, seed=630), tw - 0.5, 0.3)
    fx.add(B.whoosh(1.0, up=False, seed=631), tw, 0.5)
    fx.add(B.chord_hit([70, 74, 77, 82], dur=0.25, seed=632), tw + 1.0, 0.8)
    fx.add(short(J.crash(seed=633), 0.5), tw + 1.0, 0.6)
    fx.add(J.kick(seed=635), tw + 1.0, 0.9)
    fx.add(B.passby(1.0, seed=634), TL.s("t5") - 1.2, 0.25)

    # ---- the loop: a climbing trumpet note at every checkpoint
    for k, t in enumerate(C["loop"]):
        fx.add(B.horn(B.midi(70 + [0, 2, 4, 5, 7, 9, 12][k]), 0.2, "tpt", 0.6, seed=700 + k), t, 0.45)
        fx.add(J.tom([196, 175, 156, 147, 131, 117, 98][k], seed=710 + k), t, 0.4)

    # ---- head to head: engines, the crash in slow motion, then the snap back
    fx.add(B.passby(1.8, seed=800), TL.s("v2") + 0.4, 0.18)
    fx.add(B.engine(2.0, lambda x: 2600 + 1800 * x, seed=801), C["crash"] - 2.0, 0.1)
    fx.add(B.screech(0.9, seed=802), C["crash"] - 0.8, 0.2)
    fx.add(B.smash(0.7, seed=803), C["crash"], 0.5)
    fx.add(short(J.crash(seed=804), 0.5), C["crash"], 0.5)
    fx.add(B.chord_hit([58, 65, 70, 74, 77], dur=0.3, seed=805), C["crash"] + 1.0, 0.9)
    fx.add(B.whoosh(0.4, up=True, seed=806), C["crash"] + 0.65, 0.5)

    # ---- the old joke: ba-dum-tss
    fx.add(B.rimshot(), TL.e("w2") + 0.05, 0.8)

    # ---- the finish: a shout chorus, then one last hit on the end card
    f0 = TL.s("f1") - 1.25
    riff = [(0, [70, 74, 77]), (0.5, [72, 75, 79]), (1.0, [74, 77, 82]), (1.75, [70, 74, 77, 82]), (2.5, [75, 79, 82]),
            (3.0, [74, 77, 81]), (3.5, [72, 76, 79]), (4.0, [70, 74, 77, 82])]
    for k, (beat, notes) in enumerate(riff):
        fx.add(B.chord_hit(notes, dur=0.3 if k < 7 else 0.9, seed=900 + k, doit=3 if k == 7 else 0), f0 + beat * B.BEAT * 1.0, 0.55 if f0 + beat * B.BEAT < TL.s("f1") - 0.1 else 0.14)
    crowd_bus.add(stereo_crowd(4.0, seed=901), f0, 0.8)
    fx.add(B.chord_hit([58, 65, 70, 74, 77, 82], dur=1.4, seed=910, doit=2), C["end_card"], 0.9)
    fx.add(J.crash(seed=911), C["end_card"], 0.7)
    fx.add(J.kick(seed=912), C["end_card"], 1.0)
    b_ = C["end"] - 0.6
    fx.add(B.chord_hit([58, 65, 70, 74, 77, 82], dur=0.25, seed=920), b_, 0.9)
    fx.add(J.kick(seed=921), b_, 1.0)
    fx.add(J.snare(seed=922, tight=1.3), b_, 0.8)
    if not ORIG:
        fx.add(B.rev(0.45, seed=1610), TL.e("e3") + 0.15, 0.3)                # the Dinner Grand Prix: engines up
        fx.add(B.rev(0.3, seed=1611), TL.e("u3") + 0.15, 0.3, pan=0.25)       # head to head: one car, then the other
        fx.add(B.rev(0.3, peak=8400, seed=1612), TL.e("u3") + 0.42, 0.3, pan=0.75)
        fx.add(B.passby(1.6, seed=1613), C["end_card"] + 0.35, 0.3)           # and away past the end card

    # ---- voices
    vo = np.zeros(N)
    ann = np.zeros(N)
    for key in TL.order:
        L = TL.lines[key]
        a = line_wav(key).astype(np.float64)
        if L["voice"] != "af_heart":
            a = B.pa(a, VSR)
        up = signal.resample_poly(a, SR, VSR)
        i = int(L["start"] * SR)
        j = min(N, i + len(up))
        (ann if L["voice"] != "af_heart" else vo)[i:j] += up[: j - i]
    vo = S._hp(vo, 70)
    speech = np.concatenate([vo[int(TL.s(k) * SR): int(TL.e(k) * SR)] for k in TL.order if TL.lines[k]["voice"] == "af_heart"])
    g_vo = db(-18) / (np.sqrt((speech ** 2).mean()) + 1e-12)
    aspeech = np.concatenate([ann[int(TL.s(k) * SR): int(TL.e(k) * SR)] for k in TL.order if TL.lines[k]["voice"] != "af_heart"])
    g_an = db(-15.5) / (np.sqrt((aspeech ** 2).mean()) + 1e-12)
    vo_st = S.reverb(vo * g_vo, wet=0.05, rt60=0.6)[:, :N]
    an_st = S.reverb(ann * g_an, wet=0.08, rt60=1.4)[:, :N]

    bandr = S.reverb(band.x, wet=0.12, rt60=1.2)[:, :N]
    fxr = S.reverb(fx.x, wet=0.04, rt60=0.7)[:, :N]
    compr = None if ORIG else widen(S.reverb(comp.x, wet=0.12, rt60=1.2)[:, :N], 0.5)
    return dict(vo=vo, ann=ann, vo_st=vo_st, an_st=an_st, bandr=bandr, fxr=fxr, compr=compr, crowd=crowd_bus.x,
                vo_dry=vo * g_vo + ann * g_an)


def mixdown(P):
    """The mix: ducking, swells, the crowd, the voices, loudness. P holds the stems from parts()."""
    vo, ann, vo_st, an_st, bandr, fxr, compr = (P[k] for k in ("vo", "ann", "vo_st", "an_st", "bandr", "fxr", "compr"))
    crowd = P["crowd"]
    from scipy.ndimage import maximum_filter1d
    allv = np.abs(vo) + np.abs(ann)
    raw = np.convolve(allv, np.ones(SR // 20) / (SR // 20), mode="same")
    raw = np.clip(raw / (np.percentile(raw[raw > 1e-5], 80) + 1e-9), 0, 1)
    # instant attack with 0.15 s look-ahead, held through short gaps, smooth release
    env = maximum_filter1d(raw, size=int(0.45 * SR), origin=-int(0.12 * SR))
    env = np.convolve(env, np.ones(SR // 12) / (SR // 12), mode="same")
    duck = 1 - 0.88 * env
    talk = np.zeros(N)
    for key in TL.order:
        talk[int((TL.s(key) - 0.12) * SR): int((TL.e(key) + 0.15) * SR)] = 1.0
    r = int(0.08 * SR)
    swell = 1 + (db(7.0) - 1) * (1 - np.convolve(talk, np.ones(r) / r, mode="same"))
    gate = np.ones(N)
    gate[int(C["crash"] * SR): int((C["crash"] + 1.0) * SR)] = 0.0                  # the slow-motion crash: band cut dead
    gate[int(C["go"] * SR + 0.05 * SR): int((C["go"] + 1.2) * SR)] *= 0.1
    gate = np.convolve(gate, np.ones(int(0.004 * SR)) / int(0.004 * SR), mode="same")
    crowd_env = np.full(N, db(-22))
    for key in ("a0", "a1", "a2", "a3"):
        i0, i1 = int((TL.s(key) - 0.4) * SR), int((TL.e(key) + 0.9) * SR)
        crowd_env[i0:i1] = db(-9)
    crowd_env[: int(TL.e("h1") * SR)] = db(-18)
    crowd_env[int((C["go"] + 1.2) * SR): int((C["go"] + 2.2) * SR)] = db(-2)
    crowd_env[int(TL.e("f1") * SR):] = db(-8)
    crowd_env = np.convolve(crowd_env, np.ones(SR // 3) / (SR // 3), mode="same")

    loud = bandr[:, int(TL.s("t2") * SR): int(TL.e("t2") * SR)]
    g_mu = db(-19) / (np.sqrt((loud ** 2).mean()) + 1e-12)
    def carve(x, depth_mid):
        """Duck the speech band (300 Hz - 4 kHz) hard and the lows/highs gently."""
        low = S._lp(x, 300)
        high = S._hp(x, 4000)
        mid = x - low - high
        return low * (1 - 0.5 * env) + mid * (1 - depth_mid * env) + high * (1 - 0.7 * env)
    def presence(x, gain_db):
        """Give the horns their bite (2-5 kHz) only between lines, where nothing needs to be understood."""
        return x + S._hp(S._lp(x, 5000), 2000) * (db(gain_db) - 1) * (1 - env)

    def carve_body(x):
        """Second pass: the band keeps its body (300 Hz - 1.1 kHz) under the voice, where a phone speaker plays
        it, and only the consonant band (1.1 - 4 kHz), which carries the words, is carved deep."""
        low = S._lp(x, 300)
        body = S._lp(x, 1100) - low
        high = S._hp(x, 4000)
        mid = x - low - body - high
        return low * (1 - 0.5 * env) + body * (1 - BODY * env) + mid * (1 - MID * env) + high * (1 - 0.7 * env)
    band_mix = presence(widen(bandr, 0.7), 5.0) * swell * gate
    band_mix = carve(band_mix, 0.97) if ORIG else carve_body(band_mix)
    music = band_mix * db(-3.5) \
        + carve(presence(widen(fxr, 0.45), 3.0) * (0.7 + 0.3 * swell / db(7.0)), 0.9) * db(4.0)
    if not ORIG:
        # the kicks: a fast envelope (10 ms, held ~30 ms each side) ducks them only under an actual word
        fr = np.convolve(allv, np.ones(SR // 100) / (SR // 100), mode="same")
        fr = np.clip(4 * fr / (np.percentile(fr[fr > 1e-5], 80) + 1e-9), 0, 1)
        env_f = np.convolve(maximum_filter1d(fr, size=int(0.065 * SR)), np.ones(SR // 66) / (SR // 66), mode="same")
        music = music + (compr + S._hp(S._lp(compr, 5000), 2000) * (db(4.0) - 1)) * (1 - 0.92 * env_f) * COMP
    beds = music * g_mu + crowd * crowd_env * g_mu * 0.5 * duck
    if not ORIG:
        beds = unmask(beds, P["vo_dry"])                                    # keyed by the words, not their room
        STEMS.update(band=beds, fx=np.zeros_like(beds), crowd=np.zeros_like(beds), vo=vo_st + an_st)
    else:
        STEMS.update(band=music * g_mu, fx=np.zeros_like(music),
                     crowd=crowd * crowd_env * g_mu * 0.5 * duck, vo=vo_st + an_st)
    mix = beds + vo_st + an_st
    mix = loudness(mix, -14.0)
    tail = int(0.2 * SR)
    mix[:, -tail:] *= np.linspace(1, 0, tail) ** 2
    return mix, vo


def build():
    return mixdown(parts())


def unmask(music, voice, floor_db=-24.0):
    """Spectral sidechain. Per third-octave band and ~11 ms frame, hold the music under the voice wherever the voice
    has energy in that band (UNMASK dB in the body, 6 dB more in the 1-5 kHz band that carries the consonants, less
    in the bass and the air), and leave it alone everywhere else: the band plays at full body around and between
    the words, and the words always clear it. Gains attack within a frame and release over ~40 ms, smoothed across
    neighbouring bands. The kicks in the breaths are left alone."""
    nper, hop = 2048, 512
    f, _, V = signal.stft(voice, SR, nperseg=nper, noverlap=nper - hop)
    _, _, M = signal.stft(music, SR, nperseg=nper, noverlap=nper - hop)
    pv, pm = np.abs(V) ** 2, (np.abs(M) ** 2).mean(axis=0)
    centres = 125 * 2 ** (np.arange(20) / 3)                                  # 125 Hz ... 10 kHz
    lo, hi = centres * 2 ** (-1 / 6), centres * 2 ** (1 / 6)
    vb = np.stack([pv[(f >= a) & (f < b)].sum(0) for a, b in zip(lo, hi)])
    mb = np.stack([pm[(f >= a) & (f < b)].sum(0) for a, b in zip(lo, hi)])
    vb = np.maximum(vb, np.concatenate([vb[:, 1:], vb[:, -1:]], axis=1))       # one frame of look-ahead
    rel = np.exp(-hop / SR / 0.04)
    for t in range(1, vb.shape[1]):                                           # release ~40 ms: a word's tail
        vb[:, t] = np.maximum(vb[:, t], vb[:, t - 1] * rel)
    margin = np.select([centres < 250, centres < 1000, centres <= 5000], [UNMASK - 8.0, UNMASK, UNMASK + 6.0],
                       UNMASK - 2.0)[:, None]                                 # the bass barely matters to the words
    tot = vb.sum(0)
    speaking = tot > 10 ** (-3.0) * np.percentile(tot, 99)                    # the words, not the breaths between
    relevant = (vb > vb.max(0, keepdims=True) * 10 ** (-3.5)) & speaking   # bands within 35 dB of the voice's peak
    g = np.where(relevant, 10 * np.log10(np.clip(vb * 10 ** (-margin / 10) / (mb + 1e-20), 10 ** (floor_db / 10), 1.0)), 0.0)
    g = 0.25 * np.vstack([g[:1], g[:-1]]) + 0.5 * g + 0.25 * np.vstack([g[1:], g[-1:]])     # no sharp spectral holes
    gb = np.interp(np.log2(np.maximum(f, 1.0)), np.log2(centres), np.arange(20))   # each bin's place between bands
    i0 = np.clip(np.floor(gb).astype(int), 0, 18)
    w = np.clip(gb - i0, 0, 1)[:, None]
    gbin = g[i0] * (1 - w) + g[i0 + 1] * w
    gbin *= np.clip((f - 60) / 65, 0, 1)[:, None]                             # nothing below ~60 Hz, full from 125 Hz
    _, y = signal.istft(M * 10 ** (gbin / 20)[None], SR, nperseg=nper, noverlap=nper - hop)
    return y[:, :music.shape[1]]


def loudness(x, target):
    import pyloudnorm as pyln
    for _ in range(2):
        lufs = pyln.Meter(SR).integrated_loudness(x.T)
        x = limit(x * db(target - lufs), db(-3.3))
    return x


def limit(x, ceil, look=0.005, rel=0.12):
    from scipy.ndimage import minimum_filter1d
    pk = np.max(np.abs(x), axis=0)
    need = np.minimum(1.0, ceil / (pk + 1e-12))
    la = int(look * SR)
    g = minimum_filter1d(need, size=2 * la + 1)
    a = np.exp(-1 / (rel * SR))
    out = np.empty_like(g)
    cur = 1.0
    for i in range(0, len(g), 64):
        blk = g[i:i + 64]
        m = blk.min()
        cur = m if m < cur else cur * a ** 64 + (1 - a ** 64) * min(1.0, m)
        out[i:i + 64] = np.minimum(blk, cur)
    return x * out[None]


def write(path, x):
    x = np.clip(x, -1, 1)
    data = (x.T * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    import time
    t0 = time.time()
    os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
    mix, vo = build()
    write(os.path.join(HERE, "build", "audio.wav"), mix)
    print("audio", mix.shape[1] / SR, "s in", round(time.time() - t0, 1), "s")
