"""The soundtrack: an original score, the sound collage against the edit, the voices, the mix.

The score is a toy band that keeps changing its mind: a brass march for the machines, the title, the headlines and
the medal; a lopsided waltz (the second beat always a little late) for the window, the faces, the answer-key cake and
the banquet; a harpsichord for the inside of the machine; an organ for the sober bits; a music box for the meadow
and for putting things back; a wordless choir for the reveals. Every snap of the dolls' joints creaks (read off the
choreography itself), the shears snip, the Oracle's teleprinter clatters, clocks tick, bells ring, the food fight
splats and the streamers crackle.

Two hard cuts to silence: after the march piles up the slips ('...less than two percent'), nothing but Zuza ('A hundred
slips. Maybe one confesses.'); and after the food fight, nothing but the narrator ('superhuman in one direction, and
brittle an inch away'). The voices always sit well clear of the music in the speech band. Loudness -14 LUFS.
"""
import json
import os
import wave

import numpy as np
from scipy import signal

import fxlib as FXL
import instr as I
import orch as O
from common import E, S, Wx
from edit import EDIT, FREEZES
from script import LILI, MACH, NAR, ZUZA
from timeline import TL
from voice import SR as VSR

SR = O.SR
HERE = os.path.dirname(os.path.abspath(__file__))
N_ = int((TL.total + 0.6) * SR)


def db(v):
    return 10 ** (v / 20)


def ramp(t, a, b):
    return float(np.clip((t - a) / (b - a), 0, 1)) if b > a else float(t >= a)


def cut(name):
    """Start of the shot with this name."""
    return next(e[0] for e in EDIT if e[1] == name)


def end(name):
    """End of the shot with this name: the next cut to a different shot (punch-ins 'name@z' are the same shot)."""
    i = next(j for j, e in enumerate(EDIT) if e[1] == name)
    j = i + 1
    while j < len(EDIT) and EDIT[j][1].partition("@")[0] == name:
        j += 1
    return EDIT[j][0] if j < len(EDIT) else TL.total


class Bus:
    def __init__(self):
        self.x = np.zeros((2, N_))

    def add(self, sig, t, gain=1.0, pan=0.5, until=None):
        """Mix a signal in at time t; until = a hard stop (a 12 ms fade) - every cue ends on its cut."""
        if sig is None:
            return
        sig = np.asarray(sig, dtype=np.float64)
        if sig.ndim == 1:
            sig = np.stack([sig * np.sqrt(1 - pan), sig * np.sqrt(pan)]) * np.sqrt(2)
        if until is not None:
            m = int((until - t) * SR)
            if m <= 0:
                return
            if m < sig.shape[1]:
                sig = sig[:, :m].copy()
                f = min(m, int(0.012 * SR))
                sig[:, m - f:] *= np.linspace(1, 0, f)
        i = int(round(t * SR))
        if i >= N_ or i + sig.shape[1] <= 0:
            return
        if i < 0:
            sig, i = sig[:, -i:], 0
        j = min(N_, i + sig.shape[1])
        self.x[:, i:j] += gain * sig[:, : j - i]


# ------------------------------------------------------------------ the big moments

T_SIL1 = cut("a_count")                 # the slips: march -> nothing
T_SIL2 = cut("d_still")                 # the food fight -> nothing
SILENCES = [(T_SIL1, cut("a_tracks") - 0.005), (T_SIL2, cut("e_clue") + 0.25)]
T_FREEZE = E("e3") + 0.3


def in_silence(t):
    return any(a <= t < b for a, b in SILENCES)


# ------------------------------------------------------------------ harmony and tunes

def chord(root, kind="maj"):
    return [root + i for i in {"maj": (0, 4, 7), "min": (0, 3, 7), "dom": (0, 4, 7, 10), "dim": (0, 3, 6, 9), "maj6": (0, 4, 7, 9)}[kind]]


def voicing(root, kind, lo=57):
    """The chord's tones folded into the octave above lo."""
    out = []
    for m in chord(root, kind):
        while m < lo:
            m += 12
        while m >= lo + 12:
            m -= 12
        out.append(m)
    return sorted(out)


# the march: 2/4 in B-flat, dotted and pompous, eight bars (None = rest)
MARCH = [[(65, .75), (65, .25), (70, .5), (74, .5)], [(77, 1.0), (74, .5), (70, .5)], [(72, .75), (72, .25), (75, .5), (79, .5)],
         [(77, 1.5), (None, .5)], [(79, .75), (77, .25), (75, .5), (74, .5)], [(72, .5), (74, .5), (75, .5), (76, .5)],
         [(77, .5), (82, .5), (81, .5), (72, .5)], [(70, 1.0), (None, 1.0)]]
MARCH_CH = [(46, "maj"), (46, "maj"), (41, "dom"), (41, "dom"), (51, "maj"), (48, "dom"), (41, "dom"), (46, "maj")]

# the daisy waltz: 3/4 in F, the film's tune (also the music box's)
DAISY = [[(72, 1), (77, 1), (76, 1)], [(74, 2), (72, 1)], [(70, 1), (74, 1), (72, 1)], [(69, 3)],
         [(67, 1), (70, 1), (69, 1)], [(67, 1), (65, 1), (64, 1)], [(65, 1), (69, 1), (72, 1)], [(77, 3)]]
DAISY_CH = [(41, "maj"), (46, "maj6"), (48, "dom"), (41, "maj"), (48, "dom"), (48, "dom"), (41, "maj"), (41, "maj")]
DAISY_FLAT = [n for bar in DAISY for n in bar]

# the harpsichord's thinking machine: D minor, broken chords
DM = [(50, "min"), (43, "min"), (45, "dom"), (50, "min"), (46, "maj"), (43, "min"), (45, "maj"), (45, "dom")]
CMAJ = [(48, "maj"), (45, "min"), (41, "maj"), (43, "dom")]
AMIN = [(45, "min"), (41, "maj"), (40, "dom"), (45, "min")]


class Grid:
    def __init__(self, t0, bpm, beats=4):
        self.t0, self.b, self.beats = t0, 60.0 / bpm, beats

    def at(self, bar, beat=0.0):
        return self.t0 + (bar * self.beats + beat) * self.b


# ------------------------------------------------------------------ the pieces

def march(mus, t0, t1, bpm=120, level=1.0, melody=True, drums=True, pah=True, tuba=True, lead="brass", stumble=True, crash=True,
          level_fn=None, transpose=0, bar0=0):
    """The toy brass band in 2/4: tuba oom, brass pah, snare and bass drum, the tune on brass doubled by a glockenspiel.
    stumble: every fourth bar the band trips over an extra half beat (it is a lopsided march)."""
    b = 60.0 / bpm
    t = t0
    bar = bar0
    lv = level_fn or (lambda _t: 1.0)
    while t < t1:
        root, kind = MARCH_CH[bar % 8]
        root += transpose
        L = level * lv(t)
        blen = 2.5 if (stumble and bar % 4 == 3) else 2.0
        if tuba:
            mus.add(O.tuba(root - 12 + 12 * (root < 40), b * 0.55, 0.9 * L), t, until=t1 + 0.03)
            mus.add(O.tuba(root - 5 + 12 * (root < 40), b * 0.55, 0.8 * L), t + b, until=t1 + 0.03)
        if pah:
            for pb in (0.5, 1.5) + ((2.0,) if blen > 2 else ()):
                mus.add(O.brass(voicing(root, kind, 55), b * 0.28, 0.55 * L, seed=bar, bright=0.7), t + pb * b, pan=0.4, until=t1 + 0.03)
        if drums:
            for k in range(int(blen)):
                mus.add(O.kick(0.55 * L, seed=bar), t + k * b, until=t1 + 0.03)
                mus.add(O.snare(0.28 * L, seed=bar * 3 + k), t + (k + 0.5) * b, pan=0.6, until=t1 + 0.03)
            if blen > 2:
                mus.add(O.snare(0.4 * L, seed=bar), t + 2.0 * b, until=t1 + 0.03)
                mus.add(O.snare(0.3 * L, seed=bar + 1), t + 2.25 * b, until=t1 + 0.03)
            if crash and bar % 8 == 0:
                mus.add(O.cymbal(0.45 * L, 1.4), t, pan=0.65, until=t1 + 0.03)
        if melody:
            p = 0.0
            for m, d in MARCH[bar % 8]:
                if m is not None:
                    if lead == "brass":
                        mus.add(I.trumpet(m + transpose, d * b * 0.9, 0.9 * L, seed=bar), t + p * b, pan=0.55, until=t1 + 0.03)
                        mus.add(O.glock(m + transpose + 12, 0.25 * L), t + p * b, pan=0.7, until=t1 + 0.03)
                    elif lead == "musette":
                        mus.add(I.musette([m + transpose, m + transpose - 4], d * b * 0.85, 1.4 * L, seed=bar), t + p * b, pan=0.55, until=t1 + 0.03)
                    else:
                        mus.add(O.glock(m + transpose + 12, 0.6 * L), t + p * b, pan=0.6, until=t1 + 0.03)
                p += d
        t += blen * b
        bar += 1


def waltz(mus, t0, t1, bpm=168, level=1.0, lead="musette", bass="tuba", limp=0.22, melody=True, transpose=0, organ=False,
          choir_pad=False, wobble=0.04, bar0=0, seed=0):
    """The lopsided waltz: oom on one, pah-pah on two and three - but two always lands late, and the tempo wobbles."""
    b0 = 60.0 / bpm
    warp = lambda p: np.interp(p, [0, 1, 2, 3], [0, 1 + limp, 2.05, 3])
    t = t0
    bar = bar0
    rng = np.random.default_rng(seed)
    while t < t1:
        b = b0 * (1 + wobble * np.sin(bar * 1.7 + seed) + rng.normal(0, wobble * 0.3))
        root, kind = DAISY_CH[bar % 8]
        root += transpose
        bm = root - 12 + 12 * (root < 38) + (7 if bar % 2 else 0)
        if bass == "tuba":
            mus.add(O.tuba(bm, b * 0.7, 0.9 * level), t, until=t1 + 0.03)
        else:
            mus.add(O.pizz(bm + 12, 1.2 * level, seed=bar), t, until=t1 + 0.03)
        for k in (1, 2):
            v = voicing(root, kind, 57)
            mus.add(I.musette(v, b * 0.32, 0.9 * level, seed=bar * 3 + k), t + warp(k) * b, pan=0.4, until=t1 + 0.03)
        if organ:
            mus.add(O.organ(voicing(root, kind, 53), b * 2.9, 0.35 * level), t, pan=0.5, until=t1 + 0.03)
        if choir_pad and bar % 2 == 0:
            mus.add(I.choir(voicing(root, kind, 60), b * 5.6, 0.5 * level, vowel="a", seed=bar), t, pan=0.5, until=t1 + 0.03)
        if melody:
            p = 0.0
            for m, d in DAISY[bar % 8]:
                st, en = warp(p) * b, warp(min(3, p + d)) * b
                mm = m + transpose
                if lead == "musette":
                    mus.add(I.musette([mm], (en - st) * 0.9, 1.5 * level, seed=bar), t + st, pan=0.6, until=t1 + 0.03)
                elif lead == "reed":
                    mus.add(O.reed(mm, (en - st) * 0.9, 1.1 * level, seed=bar), t + st, pan=0.6, until=t1 + 0.03)
                elif lead == "glock":
                    mus.add(O.glock(mm + 12, 0.7 * level), t + st, pan=0.6, until=t1 + 0.03)
                    mus.add(I.musette([mm], (en - st) * 0.9, 1.0 * level, seed=bar), t + st, pan=0.55, until=t1 + 0.03)
                elif lead == "brass":
                    mus.add(I.trumpet(mm, (en - st) * 0.85, 0.8 * level, seed=bar), t + st, pan=0.6, until=t1 + 0.03)
                    mus.add(O.glock(mm + 12, 0.35 * level), t + st, pan=0.7, until=t1 + 0.03)
                p += d
        t += 3 * b
        bar += 1


def harpsichord(mus, t0, t1, bpm=100, level=1.0, prog=DM, pattern=(0, 2, 1, 2, 3, 2, 1, 2), steps=8, bass=True, pan=0.45, lo=57):
    """Broken chords in sixteenths on the harpsichord: the machine thinking."""
    s = 60.0 / bpm / 4
    t = t0
    bar = 0
    while t < t1:
        root, kind = prog[bar % len(prog)]
        v = voicing(root, kind, lo)
        tones = v[:3] + [v[0] + 12]
        if bass:
            mus.add(I.harpsi(root - 12 + 12 * (root < 40), 1.2, 0.9 * level), t, pan=0.35, until=t1 + 0.03)
        for k in range(steps):
            tk = t + k * s
            if tk >= t1:
                break
            mus.add(I.harpsi(tones[pattern[k % len(pattern)]], 0.7, 0.7 * level, seed=k), tk, pan=pan, until=t1 + 0.03)
        t += steps * s
        bar += 1


INV_U = [77, 76, 74, 72, 74, 72, 70, 69, 70, 69, 67, 65, 67, 69, 70, 72]
INV_L = [50, 53, 57, 53, 55, 58, 62, 58, 48, 52, 55, 52, 53, 57, 60, 57]


def invention(mus, t0, t1, bpm=100, level=1.0):
    """Two voices at once, one in each ear, running in contrary motion: two tracks."""
    e = 60.0 / bpm / 2
    k = 0
    while t0 + k * e < t1:
        t = t0 + k * e
        mus.add(I.harpsi(INV_U[k % 16], 0.8, 0.75 * level, seed=k), t, pan=0.8, until=t1 + 0.03)
        mus.add(I.harpsi(INV_L[k % 16], 0.8, 0.8 * level, seed=k + 50), t + (e * 0.5 if k % 4 == 3 else 0), pan=0.2, until=t1 + 0.03)
        k += 1


CHORALE = [(53, 57, 60, 65), (53, 58, 62, 65), (52, 55, 60, 64), (50, 57, 62, 65), (46, 58, 62, 65), (48, 55, 60, 64), (53, 57, 60, 65)]


def chorale(mus, t0, t1, bpm=60, level=1.0, chords=CHORALE, beats=2):
    b = 60.0 / bpm
    i = 0
    while t0 + i * beats * b < t1:
        notes = chords[i % len(chords)]
        mus.add(O.organ(list(notes), beats * b * 0.97, 0.9 * level), t0 + i * beats * b, until=t1 + 0.03)
        mus.add(O.organ([notes[0] - 12], beats * b * 0.97, 0.5 * level), t0 + i * beats * b, until=t1 + 0.03)
        i += 1


def music_box(mus, t0, t1, level=1.0, beats=None, rate=None, detune=None, transpose=12, seed=0, pan=0.5):
    notes = [(m + transpose, d) for m, d in (DAISY_FLAT if beats is None else _first_beats(beats))]
    mus.add(O.music_box(notes, rate=rate, amp=level, seed=seed, detune=detune), t0, pan=pan, until=t1 + 0.03)


def _first_beats(n):
    out, acc = [], 0
    for m, d in DAISY_FLAT * 2:
        if acc >= n:
            break
        out.append((m, d))
        acc += d
    return out


def fanfare(mus, fx, t, level=1.0, transpose=0):
    """The chapter fanfare: a snare pickup, ta-ta-ta-taaa on the brass, timpani and a cymbal."""
    mus.add(O.snare_roll(0.22, 0.5 * level), t - 0.2)
    for k, m in enumerate((70, 74, 77)):
        mus.add(I.trumpet(m + transpose, 0.1, 0.9 * level, seed=k), t + k * 0.11, pan=0.55)
    mus.add(O.brass(voicing(46 + transpose, "maj", 62) + [82 + transpose], 0.55, 1.1 * level, seed=9), t + 0.33)
    mus.add(O.timpani(34 + transpose, 0.9 * level), t + 0.33)
    mus.add(O.glock(94 + transpose, 0.4 * level), t + 0.33, pan=0.7)
    fx.add(O.cymbal(0.5 * level, 1.3), t + 0.33, pan=0.6)


def tada(mus, t, level=1.0, minor=False, transpose=0):
    if minor:
        mus.add(O.tuba(41 + transpose, 0.2, 0.9 * level), t)
        mus.add(O.brass([62 + transpose, 65 + transpose, 68 + transpose], 0.5, 0.8 * level, seed=3, bright=0.5), t + 0.18)
        mus.add(O.tuba(36 + transpose, 0.5, 0.9 * level), t + 0.18)
    else:
        mus.add(O.brass([65 + transpose, 69 + transpose, 72 + transpose], 0.12, 0.9 * level, seed=1), t)
        mus.add(O.brass([70 + transpose, 74 + transpose, 77 + transpose, 82 + transpose], 0.6, 1.0 * level, seed=2), t + 0.15)
        mus.add(O.glock(94 + transpose, 0.4 * level), t + 0.15, pan=0.7)


def stab(mus, t, root, kind="maj", level=1.0, dur=0.3, until=None):
    mus.add(O.brass(voicing(root, kind, 58), dur, 0.9 * level, seed=int(root), bright=1.1), t, until=until)
    mus.add(O.tuba(root - 12 + 12 * (root < 40), dur, 0.8 * level), t, until=until)


# ------------------------------------------------------------------ the dolls' joints, read off the choreography

def doll_moves():
    """Every pose change of the duo in the film, with who and what pose: (t, who, pose). Found by running every shot
    a few times with a spy on common.girl; cached against the shot sources."""
    import hashlib
    srcs = ["sc0.py", "sc1.py", "sc2.py", "edit.py", "timeline.py", "script.py", "common.py"]
    h = hashlib.md5(b"".join(open(os.path.join(HERE, f), "rb").read() for f in srcs)).hexdigest()
    path = os.path.join(HERE, "build", "moves.json")
    if os.path.exists(path):
        d = json.load(open(path))
        if d.get("hash") == h:
            return [tuple(x) for x in d["moves"]]
    from multiprocessing import Pool
    jobs = []
    for i, e in enumerate(EDIT):
        t0, t1 = e[0], (EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total)
        ts = list(np.arange(t0 + 0.03, t1, 0.5)) + [t1 - 0.03]
        jobs += [(e[1], float(t), t0, t1) for t in ts]
    with Pool(4) as p:
        res = p.map(_spy, jobs)
    moves = sorted(set(m for r in res for m in r))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(dict(hash=h, moves=moves), open(path, "w"))
    return moves


def _spy(job):
    name, T, t0, t1 = job
    import common as C
    import shots
    out = []
    orig = C.girl

    def spy(c, who, x, y, s, T_, keys=None, P="stand", **kw):
        if keys:
            ks = sorted(keys, key=lambda k: k[0])
            for t, p in ks[1:]:
                if t0 <= t < t1:
                    out.append((round(float(t), 4), who, p if isinstance(p, str) else "custom"))
        return orig(c, who, x, y, s, T_, keys, P, **kw)

    C.girl = spy
    try:
        shots.SHOTS[name.partition("@")[0]](T, 0)
    finally:
        C.girl = orig
    return out


def joints(doll, nosil):
    """A creak on every snap of a joint; and what the pose does: claps clap, steps tiptoe, eats crunch, throws whoosh."""
    moves = doll_moves()
    words = [(a, b) for k in TL.order for _, a, b in TL.lines[k]["words"]]
    on_word = lambda t: any(a - 0.03 <= t <= b for a, b in words)
    for i, (t, who, pose) in enumerate(moves):
        if t < T_FREEZE:
            bus = nosil if in_silence(t) else doll
            pan = 0.3 if who == "zuza" else 0.7
            if on_word(t):                                                 # under a word: a short dry click, not a squeal
                bus.add(I.joint(0.3, seed=i * 7 + 3, dur=0.05), t, pan=pan)
                bus.add(O.woodblock(0.14, 1500 if who == "zuza" else 1800), t, pan=pan)
            else:
                bus.add(I.joint(0.75, seed=i * 7 + (1 if who == "zuza" else 2), dur=0.13 if who == "lili" else None), t, pan=pan)
            if pose == "clap":
                bus.add(O.clap(0.5, seed=i), t + 0.06, pan=pan)
            elif pose in ("step_l", "step_r"):
                bus.add(I.tiptoe(0.8, seed=i), t + 0.04, pan=pan)
            elif pose == "eat":
                bus.add(I.crunch(0.8, seed=i), t + 0.18, pan=pan)
            elif pose in ("throw", "throw2"):
                bus.add(O.whoosh(0.25, True, seed=i, amp=0.5), t, pan=pan)
    return moves


# ------------------------------------------------------------------ the cue sheet

def score(mus, fx, nosil):
    from sc0 import STEP_T
    c, e = cut, end

    # ---- the machines: two and a half seconds of gears, jump-cut every quarter second, the duo pasted in
    tm = c("o_strip")
    fx.add(I.ratchet(tm, 26, 0.4), 0.0, until=tm)
    fx.add(O.whir(tm + 0.2, 0.9, 62), 0.0, until=tm + 0.05)
    for b in range(int(tm / 0.25) + 1):
        t = b * 0.25
        if t >= tm:
            break
        k = b % 4
        mus.add(O.snare(0.35, seed=b), t, until=tm)
        fx.add(I.joint(0.7, seed=900 + b), t, pan=0.3 if k == 0 else 0.7)
        if k == 0:
            stab(mus, t, [46, 41, 51][b // 4 % 3], "maj" if b // 4 % 3 != 1 else "dom", 0.8, 0.22, until=tm)
            mus.add(O.timpani(34, 0.6), t, until=tm)
            fx.add(I.snip(0.7, 950 + b), t + 0.06, pan=0.35)
        elif k == 1:
            fx.add(I.snip(0.8, 960 + b), t + 0.05, pan=0.6)
            fx.add(I.snip(0.6, 970 + b), t + 0.15, pan=0.6)
        elif k == 2:
            mus.add(O.glock([84, 88, 91][b // 4 % 3], 0.5), t, pan=0.7, until=tm)
        else:
            fx.add(O.clunk(0.45, seed=b), t, pan=0.5)
    fx.add(O.cymbal(0.45, 1.0), 2.0, until=tm + 0.05)
    fx.add(O.pneumatic(0.35, 0, 0.3), 0.6)
    fx.add(O.pneumatic(0.35, 1, 0.3), 1.6)

    ti = next(e[0] for e in EDIT[1:] if e[1] == "o_gears")             # the machines again, between two steps
    fx.add(I.ratchet(0.3, 30, 0.4, seed=3), ti, until=ti + 0.32)
    fx.add(O.clunk(0.5, seed=4), ti, pan=0.4)
    fx.add(O.tick(0.6, tock=True), ti + 0.15, pan=0.6)
    for a, _ in FREEZES:                                                  # the projector catches on each freeze frame
        fx.add(O.click(0.55), a, pan=0.5)

    # ---- the Oracle types its reasoning; the harpsichord thinks
    fx.add(O.pop(0.4), c("o_strip"))
    harpsichord(mus, c("o_strip"), S("o3") - 0.05, bpm=104, level=0.5)
    for i, (k, w0, w1) in enumerate(STEP_T):
        a, b = Wx(k, w0) - 0.05, Wx(k, w1) + 0.3
        fx.add(I.teleprinter(b - a, 0.45, seed=i), a, pan=0.55)
        fx.add(O.ding(0.25, 96), b, pan=0.6)
    mus.add(O.glock(84, 0.5), E("o2") + 0.02, pan=0.7)
    mus.add(O.glock(91, 0.5), E("o2") + 0.12, pan=0.7)
    mus.add(O.tuba(34, 0.45, 1.0), E("o3") + 0.02, until=c("o_window") + 0.3)

    # ---- the painted window: the waltz comes in, the choir on 'painting'
    waltz(mus, c("o_window"), e("o_window"), bpm=172, level=0.55, lead="musette", bass="pizz")
    fx.add(O.pop(0.35), Wx("o4", "window") - 0.15, pan=0.6)
    tp = Wx("o4", "painting") - 0.15
    mus.add(I.choir([65, 69, 72, 77], e("o_window") - tp, 0.9, vowel="a", attack=0.15), tp, until=e("o_window"))
    fx.add(O.stamp(0.45), tp, pan=0.5)
    fx.add(O.page(0.5, seed=2), tp + 0.4, pan=0.45)

    # ---- the title: snip-snip, a fanfare, cut-out letters popping on
    t = c("title")
    fx.add(I.snip(0.8, 1), t)
    fx.add(I.snip(0.7, 2), t + 0.13)
    fx.add(I.flutter(0.6, 0.6, 3), t + 0.05)
    fanfare(mus, fx, t + 0.25)
    mus.add(I.choir([70, 74, 77, 82], 1.1, 0.6, vowel="a", attack=0.2), t + 0.58, until=e("title"))
    fx.add(O.pop(0.4), t + 0.05)
    fx.add(O.pop(0.4), t + 0.4)

    # ---- 1. THE PAINTED WINDOW
    t = c("a_cut")
    fx.add(O.pop(0.35), t)
    for k in range(3):
        fx.add(I.snip(0.6, 10 + k), t + 0.28 + k * 0.52, pan=0.35)
    harpsichord(mus, t, e("a_open"), bpm=100, level=0.45)
    t = c("a_open")
    for k in range(5):
        fx.add(I.snip(0.55, 20 + k), t + 0.05 + k * 0.21, pan=0.5)
    fx.add(I.joint(0.8, 5, 0.32), t + 1.0, pan=0.55)
    fx.add(O.page(0.5, seed=4), t + 1.05)
    mus.add(I.choir([62, 65, 69], 1.4, 0.6, vowel="o", attack=0.2), t + 1.05, until=e("a_open"))
    fx.add(O.page(0.45, seed=5), Wx("a2", "more") - 0.1)
    fx.add(O.stamp(0.45), Wx("a2", "recording") - 0.2)

    sneak(mus, c("a_shortcut"), e("a_shortcut"))
    fx.add(O.page(0.4, seed=6), Wx("a3", "shortcut") - 0.1)
    fx.add(O.slurp(0.45, 0.5), S("a4") + 0.18)
    fx.add(O.gloop(0.6), S("a4") + 0.45)
    mus.add(O.glock(89, 0.4), S("a4") + 0.5, pan=0.6)

    # the slips: the march piles up and up - then the cut to silence
    t0, t1 = c("a_used"), e("a_used")
    march(mus, t0, t1, bpm=126, level=0.9, level_fn=lambda tt: 0.45 + 0.55 * ramp(tt, t0, t1), stumble=True)
    a, b = Wx("a5", "almost") - 0.2, Wx("a5", "time") + 0.1
    fx.add(O.slide_whistle(True, b - a, 0.45), a, pan=0.3)
    fx.add(O.page(0.4, seed=7), Wx("a5", "almost") - 0.1)
    for i in range(6):
        ti = S("a5") + 0.3 + i * 0.7
        if ti < Wx("a5", "under"):
            fx.add(I.teleprinter(0.3, 0.35, seed=30 + i), ti, pan=0.55)
            fx.add(I.flutter(0.8, 0.5, 30 + i), ti + 0.1, pan=0.3 + 0.08 * i)
    tl = Wx("a5", "under") - 0.05
    fx.add(O.stamp(0.6), tl)
    fx.add(O.cymbal(0.45, 1.2), tl, pan=0.6)
    mus.add(O.brass([58, 61, 66, 71], 0.6, 0.8, seed=4, bright=0.6), tl, until=t1)
    fx.add(O.keys(8, 0.06, 0.35, seed=8), Wx("a5", "reasoning"), until=t1)

    # (silence) - then the scissors cut us into the wiring, and the harpsichord plays in two voices at once
    t = c("a_tracks")
    fx.add(I.snip(0.8, 40), t)
    fx.add(I.snip(0.7, 41), t + 0.12)
    fx.add(I.flutter(0.5, 0.6, 40), t + 0.05)
    invention(mus, t, e("a_tracks"), bpm=100, level=0.6)
    fx.add(O.pop(0.45), Wx("a7", "thirty") - 0.1)
    tt = Wx("a7", "two") - 0.1
    td = Wx("a7", "digit") + 0.2
    for j in range(2):
        fx.add(I.ratchet(max(0.1, td - (tt + j * 0.35)), 9 + 3 * j, 0.35, seed=j), tt + j * 0.35, pan=0.25 + 0.5 * j)
    fx.add(O.tubular(91, 0.5), Wx("a7", "digit") + 0.1, pan=0.6)

    t0, t1 = c("a_carry"), e("a_carry")
    march(mus, t0, t1, bpm=112, level=0.45, drums=False, lead="musette", stumble=False, crash=False)
    fx.add(I.teleprinter(E("a8") + 0.1 - S("a8"), 0.3, seed=50), S("a8"), pan=0.55, until=t1)
    mus.add(O.tuba(31, 0.4, 1.1), c("a_didnot"), until=c("a_didnot") + 0.6)

    t0, t1 = c("a_notfake"), e("a_notfake")
    chorale(mus, t0, t1, bpm=66, level=0.5)
    for i in range(4):
        fx.add(O.pop(0.25), S("a11") + 0.25 + i * 0.25, pan=0.4 + 0.07 * i)
    tn = Wx("a11", "isn't") - 0.1
    mus.add(O.organ([60, 61, 63, 64, 66], 0.8, 0.8), tn, until=t1)
    fx.add(O.stamp(0.5), tn)

    t0, t1 = c("a_faces"), e("a_faces")
    waltz(mus, t0, t1, bpm=176, level=0.55, lead="reed", bass="pizz", seed=3, bar0=0)
    ts = Wx("a12", "Secretly") - 0.1
    fx.add(O.whoosh(0.35, True, seed=3, amp=0.6), ts)
    fx.add(O.slide_whistle(True, 0.35, 0.35), ts + 0.05, pan=0.6)
    for k, m in enumerate((88, 91, 96)):
        mus.add(O.glock(m, 0.45), Wx("a13", "earrings") - 0.1 + k * 0.08, pan=0.7)

    t0, t1 = c("a_interp"), e("a_interp")
    harpsichord(mus, t0, t1, bpm=132, level=0.42, prog=DM[::2] + DM[1::2])
    fx.add(O.keys(int((t1 - t0) * 6), 1 / 6, 0.12, seed=9), t0, pan=0.4, until=t1)
    th = Wx("a14", "That") - 0.1
    mus.add(I.choir([62, 66, 69, 74], t1 - th, 0.8, vowel="a", attack=0.12), th, until=t1)
    fx.add(O.pop(0.45), th)

    refrain(mus, fx, c("a_refrain"), e("a_refrain"), seed=1)

    # ---- 2. THE ANSWER-KEY CAKE
    t = c("b_card")
    fx.add(I.snip(0.8, 60), t)
    fx.add(I.snip(0.7, 61), t + 0.12)
    fanfare(mus, fx, t + 0.22, transpose=2)
    t0, t1 = c("b_banners"), e("b_banners")
    march(mus, t0, t1, bpm=126, level=1.0)
    for tm in (S("b1") - 0.16, Wx("b1", "Human") - 0.17, Wx("b1", "PhD") - 0.17):
        fx.add(O.stamp(0.55), tm)
        fx.add(O.cymbal(0.45, 1.0), tm, pan=0.62)
    t0, t1 = c("b_iq"), e("b_iq")
    march(mus, t0, t1, bpm=126, level=0.5, melody=False, pah=False, crash=False, bar0=3)
    fx.add(FXL.pencil(0.35, 0.6), Wx("b2", "But") + 0.3, pan=0.55)

    t0, t1 = c("b_broken"), e("b_broken")
    harpsichord(mus, t0, t1, bpm=100, level=0.45, prog=DM[4:] + DM[:4])
    k = 0
    while t0 + 0.2 + k * 0.24 < min(t1, S("b3") + 4.0):
        fx.add(I.snip(0.3, 70 + k), t0 + 0.2 + k * 0.24, pan=0.35)
        k += 1
    for j in range(3):
        tc = S("b3") + 1.2 + j * 1.2
        fx.add(I.snip(0.8, 90 + j), tc, pan=0.35)
        fx.add(I.flutter(1.0, 0.5, 90 + j), tc + 0.05, pan=0.3 + 0.2 * j)
    fx.add(O.stamp(0.55), Wx("b3", "two") - 0.1)

    t0, t1 = c("b_months"), Wx("b5", "beaten") - 0.1
    fx.add(O.pop(0.35), t0)
    n = 22
    for i in range(n):                                               # the harpsichord runs faster and faster
        u = i / n
        ti = t0 + (t1 - t0) * (1 - (1 - u) ** 1.7)
        mus.add(I.harpsi([62, 65, 69, 74, 77, 81][i % 6] + (i // 6) * 2, 0.4, 0.6), ti, pan=0.4)
    for i in range(6):
        ti = S("b5") + 0.4 + i * (t1 - S("b5") - 0.4) / 6
        fx.add(I.tear(0.45, seed=i, dur=0.25), ti, pan=0.3 + 0.08 * i)
        fx.add(O.whoosh(0.3, True, seed=i, amp=0.35), ti + 0.05, pan=0.7 - 0.08 * i)
    stab(mus, t1, 46, "dom", 0.9, 0.35, until=e("b_months"))
    fx.add(O.cymbal(0.4, 1.0), t1, pan=0.6, until=e("b_months"))

    t0, t1 = c("b_leak"), e("b_feed")
    waltz(mus, t0, t1, bpm=164, level=0.55, lead="musette", bass="tuba", seed=5)
    a, b = Wx("b6", "leak") - 0.2, S("b7") - 0.1
    k = 0
    while a + k * 0.32 < b:
        fx.add(O.squelch(0.25, seed=k, dur=0.2), a + k * 0.32, pan=0.6)
        k += 1
    tada(mus, S("b7") - 0.1, 0.8)
    tb = S("b8")
    for k in range(3):
        fx.add(I.chomp(0.7, seed=k), tb + 0.2 + k * 0.25, pan=0.5)
    fx.add(O.gloop(0.5), tb + 1.0)
    fx.add(O.pop(0.4), tb + 1.0, pan=0.6)

    t0, t1 = c("b_fresh"), e("b_fresh")
    harpsichord(mus, t0, t1, bpm=133, level=0.42, prog=CMAJ, pattern=(0, 1, 2, 3, 2, 1, 0, 1))
    k = 0
    while t0 + k * 0.9 < t1:
        fx.add(O.stamp(0.35), t0 + k * 0.9, pan=0.5)
        fx.add(O.page(0.3, seed=k), t0 + k * 0.9 + 0.15, pan=0.5)
        k += 1
    fx.add(I.joint(0.35, 77, min(4.0, t1 - t0)), t0, pan=0.62, until=t1)
    fx.add(O.page(0.4, seed=12), Wx("b8", "fresh") - 0.1)
    mus.add(O.glock(84, 0.4), Wx("b8", "fresh") - 0.1, pan=0.7)

    t0, t1 = c("b_94"), e("b_94")
    tb = Wx("b9", "But") - 0.1
    mus.add(O.organ([53, 57, 60, 65], tb - t0, 0.45), t0, until=tb)
    for i in range(5):
        mus.add(O.marimba(65 + [0, 2, 4, 5, 7][i], 0.6), S("b9") + i * 0.12, pan=0.35)
    fx.add(O.stamp(0.5), S("b9") + 0.3)
    for k in range(3):
        fx.add(I.snip(0.7, 100 + k), tb + 0.62 + k * 0.17, pan=0.4)
    fx.add(I.tear(0.5, seed=9, dur=0.45), tb + 0.65)
    mus.add(I.sad_trombone(0.7), tb + 1.15, until=t1)

    refrain(mus, fx, c("b_refrain"), e("b_refrain"), seed=2)

    # ---- 3. THE GOLD MEDAL CLOCK
    t = c("c_card")
    fx.add(I.snip(0.8, 110), t)
    fx.add(I.snip(0.7, 111), t + 0.12)
    fanfare(mus, fx, t + 0.22, transpose=4)
    t0, t1 = c("c_medal"), e("c_medal")
    march(mus, t0, t1, bpm=120, level=0.8)
    tpin = Wx("c1", "gold") - 0.15
    fx.add(O.cymbal(0.5, 1.4), tpin, pan=0.6)
    for k, m in enumerate((82, 86, 89, 94)):
        mus.add(O.glock(m, 0.4), tpin + k * 0.06, pan=0.7)
    fx.add(I.flutter(2.5, 0.5, 120), tpin)
    fx.add(O.stamp(0.45), tpin + 0.02)

    for k in range(int((e("c_tuesday") - c("c_clock")) / 0.5) + 1):   # the clock, alone
        fx.add(O.tick(0.9, tock=bool(k % 2)), c("c_clock") + k * 0.5, pan=0.5, until=e("c_tuesday"))
    k3 = lambda u: S("c3") + u * (E("c3") - S("c3"))
    fx.add(I.teleprinter(k3(0.6) - k3(0.0), 0.4, seed=130), k3(0.0), pan=0.55)
    fx.add(I.teleprinter(k3(1.0) - k3(0.7), 0.4, seed=131), k3(0.7), pan=0.55)
    fx.add(O.ding(0.35, 96), E("c3") + 0.02, pan=0.6)

    t0, t1 = c("c_score"), e("c_score")
    harpsichord(mus, t0, t1, bpm=120, level=0.6, prog=CMAJ, pattern=(0, 2, 1, 2))
    for k in range(int((t1 - t0) / 0.5)):
        fx.add(O.tick(0.4, tock=bool(k % 2)), t0 + k * 0.5, pan=0.6, until=t1)
    fx.add(O.slide_whistle(True, 0.7, 0.35), Wx("c4", "best") - 0.2, pan=0.35)
    fx.add(O.slide_whistle(True, 0.75, 0.4), Wx("c4", "Humans") - 0.2, pan=0.65)

    t0, t1 = c("c_proofs"), e("c_proofs")
    fx.add(O.pop(0.35), t0)
    tada(mus, Wx("c5", "yes") + 0.25, 0.8)
    tada(mus, E("c5") + 0.02, 0.8, minor=True)
    tno = Wx("c5", "no") - 0.05
    fx.add(O.whoosh(0.3, False, seed=5, amp=0.4), tno + 0.1, pan=0.3)
    fx.add(I.clang(0.7), tno + 0.48, pan=0.3)

    t0, t1 = c("c_jagged"), e("c_jagged")
    mus.add(I.choir([62, 65, 68, 71], t1 - t0, 0.6, vowel="u", attack=0.6), t0, until=t1)
    music_box(mus, t0, t1, 0.55, beats=18, detune=lambda u: 45 * np.sin(u * 9), transpose=12, seed=7)
    fx.add(FXL.pencil(0.8, 0.5), S("c6"), pan=0.6)
    tf = Wx("c6", "For") - 0.1
    fx.add(I.tear(0.7, seed=12, dur=0.55), tf)
    fx.add(O.whoosh(0.4, True, seed=12, amp=0.4), tf)
    tj = Wx("c6", "jagged") - 0.1
    fx.add(O.stamp(0.55), tj)
    for m in (50, 51, 56, 57, 62, 63):
        mus.add(I.harpsi(m, 1.0, 0.6), tj, pan=0.5, until=t1)

    t0, t1 = c("c_agents"), e("c_agents")
    harpsichord(mus, t0, t1, bpm=120, level=0.55, prog=AMIN, pattern=(0, 1, 2, 1))
    fx.add(O.whir(t1 - t0, 0.35, 60), t0, until=t1)
    tb0 = Wx("c7", "still")
    for k in range(int((t1 - tb0) / 0.6)):                               # the terminal's beeps, after the first words
        fx.add(O.beep(0.04, 0.08, 1400 + 300 * (k % 3)), tb0 + k * 0.6, pan=0.6, until=t1)
    for i, w in enumerate(("fail", "one", "three")):
        tw = Wx("c7", w) - 0.15
        fx.add(O.stamp(0.45), tw, pan=0.3 + 0.2 * i)
        if i < 2:
            mus.add(O.ding(0.3, 91), tw + 0.05, pan=0.4 + 0.2 * i)
        else:
            fx.add(I.buzzer(0.6), tw + 0.05, pan=0.7)

    t0, t1 = c("c_sim"), e("c_sim")
    music_box(mus, t0, t1, 0.75, beats=12, transpose=19, seed=8)
    k = 0
    while t0 + k * 0.7 < t1:
        fx.add(I.servo(0.5, 0.6, 200, 330, seed=k), t0 + k * 0.7, pan=0.35, until=t1)
        fx.add(O.woodblock(0.35, 1200), t0 + k * 0.7 + 0.55, pan=0.6, until=t1)
        k += 1
    fx.add(O.pop(0.4), Wx("c7", "eighty") - 0.1)

    t0, t1 = c("c_real"), e("c_real")
    music_box(mus, t0, t1, 0.75, beats=12, transpose=19, seed=9, rate=lambda u: max(0.3, 1 - 0.9 * u), detune=lambda u: -120 * u)
    fx.add(I.servo(t1 - t0, 0.55, 200, 260, seed=3, wild=0.35), t0, pan=0.35, until=t1)
    fx.add(O.boing(0.35), t0 + 0.3, pan=0.6)
    fx.add(I.splat(0.6, seed=4), t0 + 0.9, pan=0.6)
    fx.add(I.smash(0.7, seed=5), t0 + 0.97, pan=0.75)
    fx.add(O.stamp(0.45), Wx("c7", "twelve") - 0.1)

    # ---- the banquet: a grand waltz, then the food fight, then nothing
    t0, t1 = c("d_feast"), e("d_feast")
    fx.add(I.snip(0.8, 140), t0)
    fx.add(I.snip(0.7, 141), t0 + 0.12)
    waltz(mus, t0, t1, bpm=156, level=0.7, lead="glock", bass="tuba", organ=True, choir_pad=False, seed=8)
    rng = np.random.default_rng(14)
    tt = t0 + 0.4
    while tt < t1:
        fx.add(I.clink(0.45, seed=int(tt * 10)), tt, pan=rng.uniform(0.3, 0.7))
        tt += rng.uniform(0.5, 1.1)
    k = 0
    while S("d2") - 0.05 + k * 0.35 < S("d3"):
        fx.add(I.snip(0.4, 150 + k), S("d2") - 0.05 + k * 0.35, pan=0.3)
        k += 1
    fx.add(I.chomp(0.5, seed=3), E("d4") + 0.08, pan=0.7)

    t0, t1 = c("d_fight"), c("d_still")
    march(mus, t0, t1, bpm=176, level=0.8, stumble=False, bar0=4)
    tf = c("d_fire")                                                      # the streamers go up
    fx.add(I.crackle(c("d_pie") - tf, 1.0, seed=7), tf, pan=0.5, until=c("d_pie"))
    fx.add(O.whoosh(0.5, True, seed=33, amp=0.6), tf, pan=0.4)
    tp_ = c("d_pie")                                                      # the pie
    fx.add(O.whoosh(0.28, True, seed=34, amp=0.6), tp_, pan=0.2)
    fx.add(I.splat(1.0, seed=35), tp_ + 0.28, pan=0.5)
    fx.add(O.slide_whistle(False, 0.4, 0.4), tp_ + 0.3, pan=0.6)
    tk = c("d_cake")                                                      # the cake, on the beat
    fx.add(I.snip(1.0, 36), tk + 0.22, pan=0.5)
    fx.add(O.stamp(0.5), tk + 0.24)
    fx.add(I.splat(0.6, seed=37), tk + 0.5, pan=0.3)
    mus.add(I.choir([72, 76, 79, 84], t1 - t0, 0.6, vowel="a", attack=0.05, gliss=5), t0, until=t1)
    music_box(mus, t0, t1, 0.4, rate=lambda u: 2.2, transpose=24, seed=11)
    fx.add(I.crackle(t1 - t0 - 0.1, 0.6, seed=1), t0 + 0.1, pan=0.6, until=t1)
    fx.add(FXL.creak(t1 - t0, 0.5, seed=3), t0, pan=0.5, until=t1)
    rng = np.random.default_rng(15)
    tt = t0
    while tt < t1:
        fx.add(I.splat(rng.uniform(0.25, 0.5), seed=int(tt * 100)), tt, pan=rng.uniform(0.2, 0.8), until=t1)
        tt += rng.uniform(0.09, 0.2)
    for k in range(int((t1 - t0) / 0.2) + 1):                            # every beat a new pose: creaks and throws
        tk = t0 + k * 0.2
        fx.add(I.joint(0.6, seed=500 + k), tk, pan=0.3 if k % 2 else 0.7, until=t1)
        if k % 2 == 0:
            fx.add(O.whoosh(0.22, True, seed=k, amp=0.45), tk, pan=0.5, until=t1)
    for k in range(int((t1 - t0) / 0.45) + 1):
        fx.add(O.cymbal(0.28, 0.8, seed=k), t0 + k * 0.45, pan=0.4 + 0.2 * (k % 2), until=t1)
    fx.add(I.smash(0.5, seed=6), t0 + 0.8, pan=0.3, until=t1)
    fx.add(I.smash(0.45, seed=7), t0 + 1.7, pan=0.7, until=t1)
    mus.add(O.snare_roll(t1 - t0, 0.4), t0, until=t1)

    # (silence) - then putting things back: the music box, quietly, a beat with no words
    t0 = c("e_clue") + 0.25
    t1 = e("e_clock")
    music_box(mus, t0, t1, 0.8, rate=lambda u: 0.82, transpose=12, seed=12)
    mus.add(O.organ([53, 57, 60], t1 - t0, 0.2), t0, until=t1)
    tk = c("e_mend") + 0.9                                                 # the daisy chain, mended
    mus.add(O.glock(89, 0.45), tk, pan=0.6)
    mus.add(O.glock(96, 0.35), tk + 0.08, pan=0.65)
    for k in range(8):
        fx.add(O.page(0.3, seed=200 + k), t0 + 0.1 + k * 0.42, pan=0.3 + 0.08 * k)
    ts = Wx("e1", "score") - 0.25
    fx.add(O.whoosh(0.3, False, seed=21, amp=0.35), ts + 0.2)
    fx.add(I.clink(0.55, seed=21), ts + 0.8, pan=0.55)
    fx.add(O.page(0.35, seed=22), Wx("e1", "mind") - 0.1)
    tc = Wx("e1", "check") - 0.25
    fx.add(O.tick(0.5), tc + 0.5)
    fx.add(O.clock_bell(0.4, 74), tc + 0.8, pan=0.65)
    fx.add(O.page(0.35, seed=23), Wx("e1", "clock") - 0.1)

    t0, t1 = c("e_dedication"), e("e_dedication")
    chorale(mus, t0, t1, bpm=50, level=0.7, chords=[(53, 57, 60, 65), (53, 58, 62, 65), (53, 57, 60, 65)], beats=2)
    fx.add(O.projector(t1 - t0, 0.25), t0, until=t1)

    # the meadow, the last line, the freeze, THE END - and the Oracle's last piece of reasoning
    t0 = c("e_end")
    fx.add(O.pop(0.35), t0)
    music_box(mus, t0 + 0.15, T_FREEZE, 0.55, transpose=12, seed=13)
    fx.add(FXL.birds(T_FREEZE - t0, 1.4, seed=5), t0, until=T_FREEZE)
    fx.add(I.crunch(0.8, seed=31), E("e3") - 0.05, pan=0.3)
    fx.add(O.click(0.6), T_FREEZE)
    tb = T_FREEZE + 0.08
    mus.add(O.brass(voicing(46, "maj", 62) + [82], 0.9, 1.1, seed=12), tb)
    mus.add(O.tuba(34, 0.9, 1.0), tb)
    mus.add(O.timpani(34, 0.9), tb)
    mus.add(O.glock(94, 0.45), tb, pan=0.7)
    fx.add(O.cymbal(0.5, 1.6), tb, pan=0.6)
    tp = T_FREEZE + 0.3
    fx.add(I.teleprinter(0.45, 0.45, seed=300), tp, pan=0.55)
    fx.add(O.ding(0.4, 96), tp + 0.48, pan=0.6)


def sneak(mus, t0, t1):
    """Tiptoeing: pizzicato on the off-beats, a bassoon creeping up in D minor."""
    b = 60.0 / 132
    line = [50, None, 45, None, 50, 53, 52, None, 50, None, 45, None, 49, 52, 50, None]
    bsn = [(38, 2), (41, 2), (40, 2), (37, 2)]
    k = 0
    while t0 + k * b / 2 < t1:
        m = line[k % 16]
        if m is not None:
            mus.add(O.pizz(m, 1.0, seed=k), t0 + k * b / 2, pan=0.4, until=t1 + 0.03)
        k += 1
    t = t0
    i = 0
    while t < t1:
        m, d = bsn[i % 4]
        mus.add(O.reed(m + 12, d * b * 0.8, 0.9, seed=i, dark=True), t, pan=0.6, until=t1 + 0.03)
        t += d * b
        i += 1


def refrain(mus, fx, t0, t1, seed=0):
    """The meadow refrain: the music box plays the opening of the daisy tune; birds."""
    fx.add(O.pop(0.35), t0)
    music_box(mus, t0 + 0.08, t1, 0.6, beats=8, transpose=12, seed=seed)
    fx.add(FXL.birds(t1 - t0, 1.4, seed=seed), t0, until=t1)


# ------------------------------------------------------------------ voices and the mix

def oracle(x):
    """The Oracle: a little tin speaker - band-limited, a faint ring, a short metallic slap."""
    t = np.arange(len(x)) / SR
    y = x * (0.82 + 0.18 * np.sin(2 * np.pi * 47 * t))
    y = signal.sosfilt(signal.butter(4, [260 / (SR / 2), 4200 / (SR / 2)], "band", output="sos"), y)
    d = int(0.007 * SR)
    out = y.copy()
    for k in range(1, 4):
        out[k * d:] += (0.32 ** k) * y[:-k * d]
    return out


def reverb(x, wet=0.1, rt60=0.8, seed=8):
    rng = np.random.default_rng(seed)
    t = np.arange(int(rt60 * 1.4 * SR)) / SR
    ir = np.stack([rng.normal(0, 1, len(t)) * np.exp(-6.9 * t / rt60) for _ in range(2)])
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    y = np.stack([signal.fftconvolve(x[c], ir[c])[: x.shape[1]] for c in range(2)])
    return x * (1 - wet) + y * wet


def voices():
    """The narrator close and dry; the duo with a little room; the Oracle through its tin speaker."""
    dry, wet = np.zeros((2, N_)), np.zeros((2, N_))
    for key in TL.order:
        Ln = TL.lines[key]
        who = Ln["who"]
        up = signal.resample_poly(Ln["wav"].astype(np.float64), SR, VSR)
        if who == MACH:
            up = oracle(up)
        r = np.sqrt((up ** 2).mean()) + 1e-12
        lvl = {NAR: -16.0, ZUZA: -16.0, LILI: -16.0, MACH: -16.5}.get(who, -16.0)
        up = up * db(lvl) / r
        pan = {ZUZA: 0.44, LILI: 0.56}.get(who, 0.5)
        sig = np.stack([up * np.sqrt(1 - pan), up * np.sqrt(pan)]) * np.sqrt(2)
        i = int(Ln["start"] * SR)
        j = min(N_, i + sig.shape[1])
        (wet if who in (ZUZA, LILI, MACH) else dry)[:, i:j] += sig[:, : j - i]
    return dry + reverb(wet, 0.1, 0.6, seed=5)


def compress(x, ratio=2.5, pct=70, rel=0.15):
    m = np.abs(x).max(axis=0)
    k = int(0.02 * SR)
    env = np.sqrt(np.convolve(m ** 2, np.ones(k) / k, "same")) + 1e-9
    thr = np.percentile(env[env > 1e-4], pct)
    gain = np.where(env > thr, (env / thr) ** (1 / ratio - 1), 1.0)
    from scipy.ndimage import minimum_filter1d
    gain = minimum_filter1d(gain, size=int(0.01 * SR))
    a = int(rel * SR)
    gain = np.convolve(np.pad(gain, a, mode="edge"), np.ones(a) / a, "same")[a:-a]
    return x * gain[None]


def mono_safe(x, max_ratio=1.0, hop=1024):
    mid, side = 0.5 * (x[0] + x[1]), 0.5 * (x[0] - x[1])
    n = len(mid) // hop
    em = np.convolve((mid[: n * hop] ** 2).reshape(n, hop).mean(axis=1), np.ones(8) / 8, "same")
    es = np.convolve((side[: n * hop] ** 2).reshape(n, hop).mean(axis=1), np.ones(8) / 8, "same")
    g = np.minimum(1.0, np.sqrt(max_ratio * em / (es + 1e-12)))
    g = np.interp(np.arange(len(side)), np.arange(n) * hop + hop / 2, g)
    return np.stack([mid + side * g, mid - side * g])


def presence(x, f0=3000, gain_db=2.0, q=0.9):
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    al = np.sin(w0) / (2 * q)
    b = np.array([1 + al * A, -2 * np.cos(w0), 1 - al * A])
    a = np.array([1 + al / A, -2 * np.cos(w0), 1 - al / A])
    return signal.lfilter(b / a[0], a / a[0], x, axis=1)


def smooth(x, sec):
    k = max(1, int(sec * SR))
    return np.convolve(np.pad(x, k, mode="edge"), np.ones(k) / k, "same")[k:-k]


STEMS = {}
CEIL = -2.3
NEED, RELIEF_DB, FX_DB, DOLL_DB = 8.0, 14.0, -24.0, -21.0        # the voice's margin over the bed in the speech band; how far the bed comes back in a pause


def buses():
    """The score, collage and silence-proof buses (cached in build/ when DZ_CACHE is set, to re-mix quickly)."""
    path = os.path.join(HERE, "build", "buses.npz")
    if os.environ.get("DZ_CACHE") == "load" and os.path.exists(path):
        d = np.load(path)
        return d["mus"].astype(np.float64), d["fx"].astype(np.float64), d["ns"].astype(np.float64), d["doll"].astype(np.float64)
    mus, fx, nosil, doll = Bus(), Bus(), Bus(), Bus()
    score(mus, fx, nosil)
    joints(doll, nosil)
    if os.environ.get("DZ_CACHE"):
        np.savez(path, mus=mus.x.astype(np.float32), fx=fx.x.astype(np.float32), ns=nosil.x.astype(np.float32),
                 doll=doll.x.astype(np.float32))
    return mus.x, fx.x, nosil.x, doll.x


def build():
    mus_x, fx_x, ns_x, doll_x = buses()
    music = mono_safe(reverb(mus_x, 0.16, 1.1), max_ratio=1.0)
    music = signal.sosfilt(signal.butter(4, 35 / (SR / 2), "high", output="sos"), music, axis=1)
    music = np.tanh(1.1 * music) / 1.1
    fxx = reverb(fx_x, 0.08, 0.5, seed=3)
    fxx = signal.sosfilt(signal.butter(4, 40 / (SR / 2), "high", output="sos"), fxx, axis=1)
    vo = compress(presence(voices(), 3000, 2.5))
    # levels: the band where it plays for itself (the headline march), the collage a little under it
    ref = music[:, int(cut("b_banners") * SR):int(end("b_banners") * SR)]
    music = music * db(-16.0) / (np.sqrt((ref ** 2).mean()) + 1e-12)
    fight = np.zeros(N_, bool)
    fight[int(cut("d_fight") * SR):int(end("d_fight") * SR)] = True
    on = (np.abs(fxx).max(axis=0) > 1e-4) & ~fight
    fxx = fxx * db(FX_DB) / (np.sqrt((fxx[:, on] ** 2).mean()) + 1e-12)
    music_pre, fx_pre = music.copy(), fxx.copy()
    # duck the music under the words: slow, by band
    from scipy.ndimage import maximum_filter1d
    raw = np.convolve(np.abs(vo.mean(axis=0)), np.ones(SR // 20) / (SR // 20), mode="same")
    raw = np.clip(raw / (np.percentile(raw[raw > 1e-5], 80) + 1e-9), 0, 1)
    env = smooth(maximum_filter1d(raw, size=int(0.8 * SR), origin=-int(0.15 * SR)), 0.2)
    low = signal.lfilter(*signal.butter(2, 250 / (SR / 2), "low"), music)
    high = signal.lfilter(*signal.butter(2, 4500 / (SR / 2), "high"), music)
    mid = music - low - high
    music = low * (1 - 0.3 * env) + mid * (1 - 0.6 * env) + high * (1 - 0.35 * env)
    # then ride each line, music and collage together, until the voice has its margin in the speech band
    band = lambda x: signal.sosfilt(signal.butter(2, [300 / (SR / 2), 4000 / (SR / 2)], "band", output="sos"), x.mean(axis=0))
    bv = band(vo)
    bmus, bfx = band(music), band(fxx)
    gain = {k: 0.0 for k in TL.order}
    spans = {k: (int(TL.lines[k]["start"] * SR), int(TL.lines[k]["end"] * SR)) for k in TL.order}
    va = np.convolve(np.abs(vo.mean(axis=0)), np.ones(SR // 50) / (SR // 50), mode="same")
    active = va > 0.08 * np.percentile(va[va > 1e-5], 60)
    active = maximum_filter1d(active.astype(np.uint8), size=int(0.16 * SR)).astype(float)
    act = smooth(active, 0.05)

    def rides():
        r, rf = np.ones(N_), np.ones(N_)
        for key in TL.order:
            a, b = spans[key]
            lo, hi = max(0, a - int(0.12 * SR)), min(N_, b + int(0.12 * SR))
            r[lo:hi] = np.minimum(r[lo:hi], db(gain[key]))
            rf[lo:hi] = np.minimum(rf[lo:hi], db(0.8 * gain[key]))
        r, rf = smooth(r, 0.15), smooth(rf, 0.15)
        r = r * act + np.minimum(1.0, r * db(RELIEF_DB)) * (1 - act)         # in a pause the bed comes back up
        rf = rf * act + np.minimum(1.0, rf * db(RELIEF_DB)) * (1 - act)
        return r, rf

    for _ in range(6):
        ride, ride_fx = rides()
        bb = bmus * ride + bfx * ride_fx
        short = False
        for key in TL.order:
            a, b = spans[key]
            margin = 20 * np.log10((np.sqrt((bv[a:b] ** 2).mean()) + 1e-12) / (np.sqrt((bb[a:b] ** 2).mean()) + 1e-12))
            Ln = TL.lines[key]                                             # the duo's punchlines get the most room
            need = (19.0 if Ln["end"] - Ln["start"] < 1.6 else 16.0) if Ln["who"] in (ZUZA, LILI) else NEED
            if margin < need:
                gain[key] -= (need - margin) + 0.4
                short = True
        if not short:
            break
    ride, ride_fx = rides()
    dead = np.ones(N_)
    for a, b in SILENCES:
        dead[int(a * SR):int(b * SR)] = 0.0
    dead = np.convolve(dead, np.ones(int(0.004 * SR)) / int(0.004 * SR), "same")
    # the ride bites hardest in the speech band; the tuba below and the glockenspiel above keep more of their level
    lo_ = signal.lfilter(*signal.butter(2, 250 / (SR / 2), "low"), music)
    hi_ = signal.lfilter(*signal.butter(2, 4500 / (SR / 2), "high"), music)
    music = (music - lo_ - hi_) * ride[None] + (lo_ + hi_) * np.sqrt(ride)[None]
    music = music * dead[None]
    fxx = fxx * ride_fx[None] * dead[None]
    # the dolls' joints: their own bus, ducked only a little - they are short, and they are the joke
    dollx = reverb(doll_x, 0.06, 0.4, seed=4)
    don = np.abs(dollx).max(axis=0) > 1e-4
    dollx = dollx * db(DOLL_DB) / (np.sqrt((dollx[:, don] ** 2).mean()) + 1e-12)
    dollx = dollx * ((ride_fx ** 0.4) * (1 - act * (1 - db(-8.0))))[None] * dead[None]   # full between words, lower under them
    ns = ns_x * db(-24.0) / (np.abs(ns_x).max() + 1e-12)
    # in the silences, not digital zero: the faint hiss of the optical track, a tick of dust now and then
    rng = np.random.default_rng(21)
    hiss = signal.sosfilt(signal.butter(2, [400 / (SR / 2), 6000 / (SR / 2)], "band", output="sos"), rng.normal(0, 1, N_))
    pops = (rng.uniform(0, 1, N_) > 0.99985) * rng.uniform(-1, 1, N_) * 6
    hiss = (hiss + signal.sosfilt(signal.butter(2, 3000 / (SR / 2), "high", output="sos"), pops)) * db(-50.0)
    hiss = hiss * (1 - dead)
    mix = music + fxx + dollx + vo + ns + np.stack([hiss, hiss])
    report(music_pre, fx_pre, music, fxx, vo)
    mix = signal.sosfilt(signal.butter(4, 30 / (SR / 2), "high", output="sos"), mix, axis=1)
    mix = signal.sosfilt(signal.butter(2, 15000 / (SR / 2), "low", output="sos"), mix, axis=1)
    mix = loudness(mix, -14.0)
    a_, b_ = int((TL.total - 0.5) * SR), int(TL.total * SR)
    mix[:, a_:b_] *= np.linspace(1, 0, b_ - a_) ** 2
    mix[:, b_:] = 0.0
    STEMS.update(music=music, fx=fxx, vo=vo, doll=dollx, ns=ns)
    return mix


def report(music_pre, fx_pre, music, fxx, vo):
    """Per line: the voice's margin over the bed in the speech band; per shot: music, collage and voice levels."""
    band = lambda x: signal.sosfilt(signal.butter(2, [300 / (SR / 2), 4000 / (SR / 2)], "band", output="sos"), x.mean(axis=0))
    bb, bv = band(music + fxx), band(vo)
    rms = lambda y: 20 * np.log10(np.sqrt((y ** 2).mean()) + 1e-9)
    low = []
    for key in TL.order:
        Ln = TL.lines[key]
        a, b = int(Ln["start"] * SR), int(Ln["end"] * SR)
        mg = rms(bv[a:b]) - rms(bb[a:b])
        if mg < NEED - 1.0:
            low.append(f"{key} {mg:.1f}")
    print("lines under the margin:", ", ".join(low) or "none")
    rows = []
    for i, e in enumerate(EDIT):
        a, b = int(e[0] * SR), int((EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total) * SR)
        rows.append(f"{e[1]:>13s} pre: mus {rms(music_pre[:, a:b]):6.1f} fx {rms(fx_pre[:, a:b]):6.1f} | mix: mus {rms(music[:, a:b]):6.1f} "
                    f"fx {rms(fxx[:, a:b]):6.1f} vo {rms(vo[:, a:b]):6.1f}")
    print("\n".join(rows))


def loudness(x, target):
    import pyloudnorm as pyln
    g = 1.0
    for _ in range(4):
        y = limit(x * g, db(CEIL))
        lufs = pyln.Meter(SR).integrated_loudness(y.T)
        g *= db(target - lufs)
    return limit(x * g, db(CEIL))


def limit(x, ceil, look=0.005, rel=0.12):
    from scipy.ndimage import minimum_filter1d
    up = signal.resample_poly(x, 4, 1, axis=1)
    pk = np.max(np.abs(up), axis=0).reshape(-1, 4).max(axis=1)[: x.shape[1]]
    if len(pk) < x.shape[1]:
        pk = np.pad(pk, (0, x.shape[1] - len(pk)), mode="edge")
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


def aac_safe(x, target=-1.7, rates=("192k", "256k"), rounds=3):
    """Round-trip the mix through the AAC encoder at the bitrates we deliver and pull down (briefly, smoothly) any spot
    where the codec's overshoot would land above the target true peak."""
    import subprocess
    import tempfile
    from scipy.ndimage import minimum_filter1d
    for _ in range(rounds):
        g = np.ones(x.shape[1])
        with tempfile.TemporaryDirectory() as d:
            write(os.path.join(d, "a.wav"), x)
            for br in rates:
                subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", os.path.join(d, "a.wav"), "-c:a", "aac", "-b:a", br,
                                os.path.join(d, "a.m4a")], check=True)
                raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", os.path.join(d, "a.m4a"), "-f", "f32le", "-ac", "2", "-ar",
                                      str(SR), "-"], check=True, capture_output=True).stdout
                y = np.frombuffer(raw, np.float32).reshape(-1, 2).T
                n = min(y.shape[1], x.shape[1])
                up = signal.resample_poly(y[:, :n], 4, 1, axis=1)
                pk = np.abs(up).max(axis=0)[: 4 * n].reshape(-1, 4).max(axis=1)
                gg = np.ones(x.shape[1])
                gg[:n] = np.minimum(1.0, db(target) / (pk + 1e-12))
                g = np.minimum(g, gg)
        if g.min() > 0.995:
            break
        g = minimum_filter1d(g, size=int(0.04 * SR))
        g = smooth(g, 0.03)
        x = x * g[None]
    return x


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
    mix = aac_safe(build())
    write(os.path.join(HERE, "build", "audio.wav"), mix)
    for k, v in STEMS.items():
        write(os.path.join(HERE, "build", f"stem_{k}.wav"), v / (np.abs(v).max() + 1e-9) * 0.9)
    print("audio", round(mix.shape[1] / SR, 2), "s in", round(time.time() - t0, 1), "s")
