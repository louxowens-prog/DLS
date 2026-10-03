"""The soundtrack: the lo-fi score (lofi.py), the foley against the edit, the canned audience, the voices, the mix.

Every chapter has its own cheap music: bedroom synthpop and a hyperpop title sting; a toy music box over a General-MIDI
orchestra for 1994; chiptune for the paper chapter; a woodwind-and-pizzicato MIDI orchestra for the clay; a slap-bass
game-show groove for NOD-TV; chiptune again for MS Paint and a PS1 drum-and-bass loop for the boat; a public-access
jingle, then clean emo guitar for the turn, and distorted pop-punk power chords for the last joke.

Two hard cuts from loud chaos into awkward silence, played as jokes: the GM orchestra swelling over Weizenbaum's
warning, a record scratch, nothing ('I was nine. Very normal.'); and the fireworks for the musical, then an empty
theatre (one cough; 'It was not.'). The laugh track and applause drop out at the sincere turn and come back for the
last joke. Voices always sit at least 15 dB clear of the music in the speech band. Loudness -14 LUFS.
"""
import os
import wave

import numpy as np
from scipy import signal

import band as B
import fxlib as FXL
import lofi as L
import orch as O
from common import E, S, Wx
from edit import EDIT
from script import AFF, ANN, DOC, DOCTOR, DOT, KID, MET
from timeline import TL
from voice import SR as VSR

SR = O.SR
HERE = os.path.dirname(os.path.abspath(__file__))
N_ = int((TL.total + 0.6) * SR)
midi = O.midi


def db(v):
    return 10 ** (v / 20)


def cut(name):
    """Start time of the (first) shot with this name."""
    return next(e[0] for e in EDIT if e[1] == name)


class Bus:
    def __init__(self):
        self.x = np.zeros((2, N_))

    def add(self, sig, t, gain=1.0, pan=0.5):
        if sig is None:
            return
        sig = np.asarray(sig, dtype=np.float64)
        if sig.ndim == 1:
            sig = np.stack([sig * np.sqrt(1 - pan), sig * np.sqrt(pan)]) * np.sqrt(2)
        i = int(round(t * SR))
        if i >= N_ or i + sig.shape[1] <= 0:
            return
        if i < 0:
            sig, i = sig[:, -i:], 0
        j = min(N_, i + sig.shape[1])
        self.x[:, i:j] += gain * sig[:, : j - i]


# ------------------------------------------------------------------ the big moments

T_TITLE = E("o2") + 0.1
T_SCRATCH = E("a7") + 0.4
T_CH2 = cut("p_shapes")
T_CH3 = cut("k_cake")
T_CH4 = cut("f_bumper")
T_FIRE = S("d9") - 0.05
T_EMPTY = cut("f_empty")
T_CH5 = cut("m_morals")
T_PS1 = cut("ps1_boat")
T_BARS = cut("v_bars")
T_STAGE = cut("v_stage")
T_TURN = S("f4") - 0.1
T_JOKE = cut("v_joke")
T_RIM = E("f9") + 0.08
T_END = cut("end")

# dead silence: everything but the voices (and the one cough)
SILENCES = [(T_SCRATCH + 0.42, T_CH2 - 0.02), (T_EMPTY, T_CH5 - 0.02)]
# the crash-ins: their own bus, loud
CRASH_SPANS = [(T_TITLE, cut("c1_kid") + 0.3), (T_CH4 + 0.5, S("d2") - 0.05), (T_FIRE, T_EMPTY), (T_RIM, TL.total)]


def chord_notes(root, kind="maj"):
    return [root + i for i in {"maj": (0, 4, 7), "min": (0, 3, 7), "maj7": (0, 4, 7, 11), "add9": (0, 4, 7, 14)}[kind]]


# ------------------------------------------------------------------ the score, section by section

def synthpop(mus, t0, t1, bpm=112, key=60, level=1.0, drums=True):
    """Bedroom synthpop: a soft drum machine, a round synth bass, airy pulse chords. I-vi-IV-V."""
    G = L.Grid(t0, bpm)
    prog = [(0, "maj"), (-3, "min"), (5, "maj"), (7, "maj")]
    bar = 0
    while G.at(bar) < t1:
        r, kind = prog[bar % 4]
        root = key + r
        for b in range(4):
            t = G.at(bar, b)
            if t >= t1:
                break
            if drums:
                mus.add(L.drum_machine("k", 0.55 * level), t) if b in (0, 2) else None
                mus.add(L.drum_machine("c", 0.35 * level, seed=b), t) if b in (1, 3) else None
                mus.add(L.drum_machine("h", 0.25 * level, seed=b), t + G.b / 2)
            mus.add(L.note("tri", root - 24, G.b * 0.9, 0.4 * level, s=0.8), t)
        for k, m in enumerate(chord_notes(root, kind)):
            mus.add(L.note("pulse", m, G.b * 3.6, 0.07 * level, a=0.02, d=0.3, s=0.5, r=0.3, duty=0.25, lp=3000), G.at(bar), pan=0.3 + 0.2 * k)
        bar += 1


def title_sting(cr, fx, t):
    """Hyperpop: a supersaw stab, an 808 drop, a gang 'HEY!' pitched up and stuttered, glitter."""
    from voice import speak_fx
    cr.add(L.supersaw(chord_notes(72, "add9") + [60], 0.9, 1.0), t)
    cr.add(L.kick808(1.0, 0.9, 180, 40), t)
    cr.add(O.snare_roll(0.35, 0.6), t - 0.36)
    hey = signal.resample_poly(speak_fx("Hey!", "chorus", 1.1, 7.0).astype(np.float64), SR, VSR)
    hey = L.bitcrush(hey / (np.abs(hey).max() + 1e-9), 8, 2)
    for k, dt in enumerate((0.0, 0.11, 0.22)):
        cr.add(hey[: int(0.1 * SR) if k < 2 else len(hey)] * (0.7 if k < 2 else 1.0), t + 0.18 + dt)
    for k in range(8):
        fx.add(O.sparkle(0.5, seed=k), t + 0.1 + k * 0.09, 1.0, pan=0.2 + 0.08 * k)


def lullaby(mus, fx, t0, t1, level=1.0):
    """1994: a toy keyboard's music box over a cheap GM string pad. An original tune in F."""
    bpm = 92
    G = L.Grid(t0, bpm)
    tune = [72, 69, 70, 72, 74, 72, 70, 69, 67, 69, 70, 65, 67, 69, 70, 72]
    prog = [(53, "maj"), (58, "maj"), (60, "maj"), (53, "maj")]
    bar = 0
    while G.at(bar) < t1:
        root, kind = prog[bar % 4]
        mus.add(O.strings(chord_notes(root, kind), G.b * 4, 0.16 * level, seed=bar), G.at(bar))
        for b in range(8):
            t = G.at(bar, b / 2)
            if t >= t1:
                break
            m = tune[(bar * 8 + b) % len(tune)]
            if b % 2 == 0 or bar % 2:
                mus.add(O.music_box([(m, 1)], amp=0.35 * level), t, pan=0.6)
        bar += 1


def gm_swell(cr, t0, t1):
    """The cheap GM orchestra builds over Weizenbaum's warning: strings, brass, a timpani roll, a cymbal swell."""
    d = t1 - t0
    cr.add(O.strings([53, 57, 60, 65], d, 0.5), t0)
    cr.add(O.brass([53, 60, 65], d, 0.45), t0 + d * 0.35)
    for k in range(int(d * 14)):
        cr.add(O.timpani(41, 0.15 + 0.6 * k / (d * 14)), t0 + k / 14)
    cr.add(O.cymbal(0.9, d + 0.3, swell=True), t0)


def chiptune(mus, t0, t1, bpm=140, key=57, level=1.0, minor=True, seed=0):
    """Glitchy chiptune: square-wave arpeggios, a triangle bass, the noise channel on the hats, a pulse lead."""
    G = L.Grid(t0, bpm)
    prog = [(0, "min"), (-4, "maj"), (3, "maj"), (-2, "maj")] if minor else [(0, "maj"), (5, "maj"), (-3, "min"), (7, "maj")]
    lead = [12, 10, 7, 10, 12, 15, 14, 10]
    bar = 0
    while G.at(bar) < t1:
        r, kind = prog[bar % 4]
        notes = chord_notes(key + r, kind)
        for s in range(16):
            t = G.at(bar, s / 4)
            if t >= t1:
                break
            m = notes[s % 3] + 12 * ((s // 3) % 2)
            mus.add(L.note("square", m, G.b / 4 * 0.8, 0.07 * level, s=0.6, r=0.01), t, pan=0.4)
            if s % 2 == 0:
                mus.add(L.chip_noise(0.04, 0.08 * level, True, seed + s), t, pan=0.6)
            if s % 8 == 4:
                mus.add(L.chip_noise(0.12, 0.14 * level, False, seed + s), t)
            if s % 8 == 0:
                mus.add(L.chip_kick(0.5 * level), t)
        mus.add(L.note("tri", key + r - 12, G.b * 3.8, 0.35 * level, s=0.9), G.at(bar))
        if bar % 2 == 1:
            for k in range(4):
                mus.add(L.note("pulse", key + r + lead[(bar + k) % 8], G.b * 0.9, 0.06 * level, duty=0.125, vib=0.01), G.at(bar, k), pan=0.55)
        bar += 1


def midi_orch(mus, t0, t1, bpm=100, key=62, level=1.0):
    """The clay chapter: pizzicato bass, a bassoon tune, celesta sprinkles - a cheap MIDI orchestra's 'whimsy'."""
    G = L.Grid(t0, bpm)
    prog = [(0, "maj"), (7, "maj"), (9, "min"), (5, "maj")]
    tune = [7, 9, 11, 12, 11, 9, 7, 4, 5, 7, 9, 7, 5, 4, 2, 0]
    bar = 0
    while G.at(bar) < t1:
        r, kind = prog[bar % 4]
        for b in range(4):
            t = G.at(bar, b)
            if t >= t1:
                break
            mus.add(O.pizz(key + r - 24 + (7 if b % 2 else 0), 0.45 * level, seed=b), t)
            mus.add(O.reed(key + tune[(bar * 4 + b) % 16], G.b * 0.9, 0.18 * level, seed=b), t, pan=0.4)
            if b == 2:
                mus.add(O.celesta(key + 24 + tune[(bar * 4) % 16], 0.12 * level), t + G.b / 2, pan=0.7)
        bar += 1


def gameshow(mus, t0, t1, bpm=118, key=58, level=1.0):
    """NOD-TV's groove: slap bass, a clav, a drum machine, brass stabs on the two-bar turnaround."""
    G = L.Grid(t0, bpm)
    prog = [(0, "maj"), (5, "maj"), (2, "min"), (7, "maj")]
    bar = 0
    while G.at(bar) < t1:
        r, kind = prog[bar % 4]
        for s in range(8):
            t = G.at(bar, s / 2)
            if t >= t1:
                break
            if s in (0, 3, 4, 7):
                mus.add(B.ebass(key + r - 24 + (12 if s == 7 else 0), G.b * 0.45, 0.5 * level), t)
            if s % 2 == 1:
                mus.add(O.clav(chord_notes(key + r, kind), G.b * 0.3, 0.16 * level, seed=s), t, pan=0.65)
            mus.add(L.drum_machine("h", 0.22 * level, seed=s), t, pan=0.6)
            if s in (0, 4):
                mus.add(L.drum_machine("k", 0.5 * level, seed=s), t)
            if s in (2, 6):
                mus.add(L.drum_machine("s", 0.35 * level, seed=s), t)
        if bar % 2 == 1:
            mus.add(O.brass(chord_notes(key + r + 12, kind), G.b * 0.5, 0.25 * level, seed=bar), G.at(bar, 3.5))
        bar += 1


def nod_jingle(cr, t):
    """'N-O-D T-V!': a brass fanfare on a major arpeggio, a slap-bass drop, a chime."""
    for k, m in enumerate((70, 74, 77, 82)):
        cr.add(O.brass([m, m - 12], 0.18 if k < 3 else 0.9, 0.7, seed=k), t + k * 0.14)
    cr.add(L.kick808(0.9), t + 0.42)
    cr.add(O.cymbal(0.7, 1.4), t + 0.42)
    cr.add(L.fm_bell(94, 1.2, 0.5), t + 0.42)


def fireworks(cr, fx, t0, t1):
    """'What a brilliant idea!' The whole studio goes off: a fanfare, rockets, bangs, whistles, applause."""
    cr.add(O.brass([70, 74, 77, 82], t1 - t0, 0.7), t0)
    cr.add(L.supersaw([70, 74, 77, 82], t1 - t0, 0.7), t0)
    rng = np.random.default_rng(4)
    for k in range(9):
        t = t0 + rng.uniform(0.0, t1 - t0 - 0.2)
        fx.add(O.whoosh(0.3, True, k, 0.5), t - 0.25, 1.0, pan=rng.uniform(0.2, 0.8))
        bang = O._noise(int(0.4 * SR), k) * np.exp(-np.arange(int(0.4 * SR)) / SR * 14)
        cr.add(np.tanh(3 * bang) * 0.6, t, 1.0, pan=rng.uniform(0.2, 0.8))
    cr.add(L.kick808(1.0, 0.8), t0)


def ps1_loop(mus, fx, t0, t1, level=1.0):
    """The PS1 boat race: a fast breakbeat, a sub bass, FM bells, the engine, the pickups."""
    bpm = 170
    G = L.Grid(t0, bpm)
    pat = "k.h.s.hkk.h.s.h."
    bar = 0
    while G.at(bar) < t1:
        for s in range(16):
            t = G.at(bar, s / 4)
            if t >= t1:
                break
            c = pat[s]
            if c == "k":
                mus.add(L.drum_machine("k", 0.55 * level), t)
            elif c == "s":
                mus.add(L.drum_machine("s", 0.45 * level, seed=s), t)
            elif c == "h":
                mus.add(L.drum_machine("h", 0.25 * level, seed=s), t, pan=0.6)
        root = [45, 45, 41, 43][bar % 4]
        mus.add(L.note("sine", root - 12, G.b * 3.8, 0.5 * level, s=0.9), G.at(bar))
        for k in range(2):
            mus.add(L.fm_bell(root + 24 + [7, 12, 10, 3][(bar + k) % 4], 0.8, 0.18 * level), G.at(bar, k * 2), pan=0.3 + 0.4 * k)
        bar += 1
    eng = np.sin(2 * np.pi * np.cumsum(90 + 12 * np.sin(2 * np.pi * 1.2 * L.tx(t1 - t0))) / SR)
    eng = np.tanh(2.5 * eng) * 0.12 * level
    fx.add(signal.sosfilt(signal.butter(2, 900 / (SR / 2), output="sos"), eng), t0)


def jingle99(cr, mus, t):
    """Channel 99's public-access jingle: a cheesy organ and a glockenspiel, slightly out of tune."""
    tune = [(72, 0.0), (76, 0.18), (79, 0.36), (84, 0.54), (83, 0.9), (79, 1.08), (81, 1.26), (79, 1.44)]
    for m, dt in tune:
        cr.add(O.glock(m + 0.15, 0.5), t + dt, 1.0, pan=0.6)
        cr.add(O.organ([m - 12, m - 5], 0.2, 0.18), t + dt)
    cr.add(O.organ([48, 55, 60, 64], 1.7, 0.2), t)


def emo(mus, t0, t1, level=1.0, bpm=80, key=52):
    """The turn: clean guitar arpeggios, E - C#m - A - B, nothing else."""
    G = L.Grid(t0, bpm)
    prog = [(0, "maj"), (9, "min"), (5, "maj"), (7, "maj")]
    patt = [0, 2, 1, 2, 3, 2, 1, 2]
    bar = 0
    while G.at(bar) < t1:
        r, kind = prog[bar % 4]
        notes = [key + r - 12] + chord_notes(key + r, kind)
        for s in range(8):
            t = G.at(bar, s / 2)
            if t >= t1:
                break
            mus.add(L.guitar(notes[patt[s]] + (12 if patt[s] else 0), G.b * 1.2, 0.22 * level, seed=s), t)
        bar += 1


def pop_punk(cr, t0, t1, key=40):
    """The last joke's band: distorted power chords, fast, with a crash on every bar."""
    bpm = 168
    G = L.Grid(t0, bpm)
    prog = [0, 9, 5, 7]
    bar = 0
    while G.at(bar) < t1:
        root = key + prog[bar % 4]
        for s in range(8):
            t = G.at(bar, s / 2)
            if t >= t1:
                break
            cr.add(L.power_chord(root, G.b * 0.45, 1.0, seed=s, palm=(s % 2 == 1)), t)
            cr.add(L.drum_machine("h", 0.3, seed=s), t, pan=0.6)
            if s in (0, 4):
                cr.add(L.drum_machine("k", 0.7, seed=s), t)
            if s in (2, 6):
                cr.add(L.drum_machine("s", 0.6, seed=s), t)
        cr.add(O.cymbal(0.5, 1.0, seed=bar), G.at(bar))
        bar += 1


# ------------------------------------------------------------------ the whole thing

def score(mus, fx, crowd, cr, nosil):
    # ---- cold open: the phone starts recording
    fx.add(O.beep(0.12, 0.35, 1400.0), 0.03, 1.0, pan=0.6)
    synthpop(mus, 0.0, T_TITLE + 0.1, level=0.8)
    fx.add(O.click(0.8), S("o2") + 1.0, 1.0)                                     # the freeze frame: a shutter
    fx.add(B.xylo_run([84, 88, 91], 0.05, 0.25), S("o2") + 1.0)
    fx.add(O.whoosh(0.45, True, 1, 0.8), T_TITLE - 0.05)
    title_sting(cr, fx, T_TITLE)
    crowd.add(L.applause(2.4, 0.9, seed=3), T_TITLE + 0.1)
    # ---- 1994
    fx.add(O.page(0.9, seed=1), cut("c1_kid"))
    lullaby(mus, fx, cut("c1_kid") + 0.2, T_SCRATCH - 4.6, level=0.9)
    for k in range(10):                                                          # the kid typing, the PC answering
        fx.add(O.keys(1, 0.0, 0.5, seed=k), S("a2") + k * 0.12, 1.0, pan=0.55)
    fx.add(O.beep(0.08, 0.3, 880.0), S("a3") - 0.15, 1.0)
    for k in range(18):
        fx.add(O.beep(0.03, 0.12, 1200.0 + 200 * (k % 3)), S("a3") + k * 0.12, 1.0, pan=0.6)
    fx.add(B.xylo_run([79, 84, 88, 91, 96], 0.05, 0.4), Wx("a4", "listened") - 0.05)
    tb = Wx("a4", "body") - 0.6
    for k in range(4):                                                           # eyes, hair, mouth, mirror: boing
        fx.add(O.boing(0.45), tb + k * (1.05 / 4), 1.0, pan=0.4 + 0.1 * k)
    fx.add(O.whoosh(0.3, False, 2, 0.5), cut("c1_eliza"))
    for k in range(4):
        fx.add(O.page(0.4, seed=k + 3), S("a5") + 1.0 + k * 0.35, 1.0, pan=0.3 + 0.15 * k)
    fx.add(O.stamp(1.0), Wx("a5", "nothing") - 0.05)
    crowd.add(L.laugh(1.6, 0.9, seed=2, n=18), E("a6") - 0.05)
    for k in range(int((E("a7") - S("a7") - 0.4) * 9)):                          # the typewriter
        fx.add(O.keys(1, 0.0, 0.45, seed=k + 40), S("a7") + 0.2 + k / 9, 1.0, pan=0.5)
    gm_swell(cr, S("a7") + 0.3, T_SCRATCH + 0.02)
    fx.add(O.scratch(0.42, 1.2), T_SCRATCH)
    # ---- paper
    fx.add(O.whoosh(0.5, True, 3, 0.9), T_CH2)
    chiptune(mus, T_CH2 + 0.3, S("b5") - 0.1, level=0.85)
    for k, t in enumerate((Wx("b1", "saw"), Wx("b1", "bully"))):
        fx.add(O.pop(0.6), t, 1.0, pan=0.4 + 0.2 * k)
    crowd.add(L.laugh(1.2, 0.8, seed=4, n=14), E("b1") + 0.02)
    fx.add(O.pop(0.7), Wx("b2", "says") - 0.1)
    for k in range(6):                                                           # paper pieces glued on
        fx.add(O.page(0.35, seed=k + 9), Wx("b2", "brain") - 0.2 + k * 0.32, 1.0, pan=0.6)
    fx.add(O.slide_whistle(True, 1.0, 0.4), Wx("b3", "plays") - 0.1)
    fx.add(O.whoosh(0.4, True, 5, 0.6), S("b4") - 0.1)
    fx.add(FXL.pencil(0.8, 0.6, seed=4), Wx("b4", "co-authoring"))
    fx.add(O.whoosh(0.3, False, 6, 0.6), S("b5") - 0.1)
    mus.add(L.note("square", 84, 0.15, 0.08), S("b5") - 0.05)
    crowd.add(L.laugh(1.8, 0.85, seed=6, n=22), E("b5") - 0.1)
    # ---- clay
    fx.add(O.page(0.9, seed=12), T_CH3)
    midi_orch(mus, T_CH3 + 0.4, E("c4") - 0.1, level=0.9)
    fx.add(O.squelch(0.8, seed=1), Wx("c1", "Layers") - 0.05)
    for k, t in enumerate((S("c2") - 0.1, Wx("c2", "People") - 0.15, Wx("c2", "company") - 0.15)):
        fx.add(O.squelch(0.9, seed=k + 3, dur=0.3), t + 0.4)
    fx.add(O.slide_whistle(False, 0.5, 0.35), Wx("c2", "you") - 0.4)
    fx.add(O.squelch(1.0, seed=9, dur=0.4), Wx("c2", "you") + 0.1)
    fx.add(O.ding(0.7), Wx("c3", "preferred") - 0.1)
    fx.add(O.slide_whistle(False, 0.9, 0.4), Wx("c3", "bigger") - 0.4)                # the giant cake sags
    crowd.add(L.laugh(1.4, 0.6, seed=8, n=14), E("c3") - 0.05)
    fx.add(O.squelch(0.7, seed=12), Wx("c4", "Shaped") - 0.2)
    fx.add(O.whoosh(0.3, True, 8, 0.6), cut("k_rater"))
    # ---- NOD-TV
    fx.add(O.whoosh(0.5, False, 9, 0.8), T_CH4)
    for k in range(6):
        fx.add(O.beep(0.04, 0.12, 700.0 + 120 * k), T_CH4 + 0.05 + k * 0.08, 1.0)
    nod_jingle(cr, T_CH4 + 0.55)
    crowd.add(L.applause(2.2, 1.0, seed=5), S("d1") - 0.05)
    gameshow(mus, S("d2") - 0.2, T_FIRE - 0.1, level=0.85)
    for k in range(3):
        fx.add(O.click(0.6), Wx("d2", "Rating") + k * 0.66, 1.0, pan=0.6)
        fx.add(O.ding(0.35, m=96), Wx("d2", "Rating") + k * 0.66 + 0.04, 1.0, pan=0.6)
    fx.add(O.whoosh(0.35, True, 10, 0.7), S("d3") - 0.15)
    for k in range(14):                                                          # thumbs-ups flying in
        fx.add(O.ding(0.18, m=91 + (k % 4) * 2), S("d4") + 0.1 + k * 0.08, 1.0, pan=0.2 + 0.05 * k)
    crowd.add(L.applause(1.4, 0.8, seed=6), S("d5") - 0.05)
    crowd.add(L.laugh(1.6, 0.9, seed=10, n=20), E("d5") + 0.02)
    fx.add(L.fm_bell(96, 1.5, 0.35), Wx("d6", "tell") - 0.2)
    for k in range(int((E("d8") - Wx("d8", "should")) * 9)):
        fx.add(O.keys(1, 0.0, 0.35, seed=k + 70), Wx("d8", "should") + k / 9, 1.0, pan=0.4)
    fireworks(cr, fx, T_FIRE, T_EMPTY)
    crowd.add(L.applause(T_EMPTY - T_FIRE + 0.5, 1.3, seed=7), T_FIRE)
    nosil.add(L.cough(0.5, seed=3), T_EMPTY + 0.45, 1.0, pan=0.7)                 # the only sound in the theatre
    # ---- MS Paint, PS1
    fx.add(O.whoosh(0.5, True, 11, 0.9), T_CH5)
    chiptune(mus, T_CH5 + 0.3, T_PS1 - 0.1, bpm=128, key=64, level=0.75, minor=True, seed=5)
    for t in np.arange(T_CH5 + 0.2, T_PS1 - 0.3, 0.42):
        fx.add(O.click(0.25), float(t), 1.0, pan=0.62)                          # the mouse, drawing
    for k in range(4):                                                           # wrong-answer buzzers on each 'isn't'
        t = [S("e3"), Wx("e3", "Engagement") - 0.3, Wx("e3", "Test") - 0.3, Wx("e3", "Obeying") - 0.35][k] + 0.35
        fx.add(O.honk(0.3, 1), t, 1.0, pan=0.5)
    fx.add(O.ding(0.6), Wx("e2", "Goodhart") - 0.2)
    fx.add(O.whoosh(0.8, True, 12, 0.7), Wx("e4", "games") - 0.1)
    ps1_loop(mus, fx, T_PS1, E("e5") + 0.1, level=0.9)
    for k in range(int((E("e5") - T_PS1) / 0.87)):
        fx.add(L.note("square", 84 + (k % 3) * 4, 0.08, 0.12), T_PS1 + 0.3 + k * 0.87, 1.0, pan=0.6)
    for k in range(6):
        fx.add(O.beep(0.1, 0.18, 660.0), T_PS1 + 0.5 + k * 0.67, 1.0, pan=0.5)
    fx.add(O.whoosh(0.6, True, 13, 0.9), Wx("e5", "fire") - 0.3)
    fire = O._noise(int((E("e5") - Wx("e5", "fire") + 0.3) * SR), 3)
    fire = signal.sosfilt(signal.butter(2, [300 / (SR / 2), 3000 / (SR / 2)], "band", output="sos"), fire) * 0.12
    fx.add(fire * (np.random.default_rng(3).random(len(fire)) > 0.7), Wx("e5", "fire") - 0.1)
    for k, m in enumerate((72, 76, 79, 84, 88)):
        fx.add(L.note("square", m, 0.12, 0.12), Wx("e5", "Outscoring") - 0.1 + k * 0.08, 1.0)
    # ---- CHANNEL 99
    fx.add(O.beep(T_STAGE - T_BARS - 0.75, 0.25, 1000.0), T_BARS)
    fx.add(O.clunk(0.7), T_BARS + 0.55)
    jingle99(cr, mus, T_BARS + 0.62)
    crowd.add(L.applause(2.6, 0.9, seed=8, sparse=True), T_STAGE + 0.2)
    synthpop(mus, T_STAGE + 1.2, T_TURN, bpm=96, key=55, level=0.55, drums=False)
    crowd.add(L.laugh(1.4, 0.55, seed=12, n=12), E("f2") - 0.1)
    crowd.add(L.laugh(1.2, 0.5, seed=14, n=12), E("f3") - 0.15)
    emo(mus, T_TURN + 0.2, S("f7") - 0.6, level=1.0)
    mus.add(L.guitar(52, 3.0, 0.3) + L.guitar(59, 3.0, 0.22) + L.guitar(64, 3.0, 0.2), S("f7") - 1.2)    # one chord rings out
    fx.add(O.whoosh(0.3, True, 14, 0.4), S("f7") - 0.55)
    fx.add(L.rimshot(1.0), T_RIM)
    crowd.add(L.laugh(2.8, 1.1, seed=16, n=26), T_RIM + 0.15)
    crowd.add(L.applause(TL.total - T_RIM, 1.1, seed=9), T_RIM + 0.3)
    pop_punk(cr, T_RIM + 0.35, TL.total - 0.2)
    fx.add(O.whoosh(0.45, True, 15, 0.8), T_END)


def robot(x):
    """DOCTOR, through a 1994 sound card: ring-modulated, crushed to 8 bits and a low sample rate, band-limited."""
    t = np.arange(len(x)) / SR
    y = x * (0.7 + 0.3 * np.sin(2 * np.pi * 38 * t))
    y = L.bitcrush(y / (np.abs(y).max() + 1e-9), 7, 4) * np.abs(x).max()
    return signal.sosfilt(signal.butter(4, [280 / (SR / 2), 3600 / (SR / 2)], "band", output="sos"), y)


def reverb(x, wet=0.1, rt60=0.8, seed=8):
    rng = np.random.default_rng(seed)
    t = np.arange(int(rt60 * 1.4 * SR)) / SR
    ir = np.stack([rng.normal(0, 1, len(t)) * np.exp(-6.9 * t / rt60) for _ in range(2)])
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    y = np.stack([signal.fftconvolve(x[c], ir[c])[: x.shape[1]] for c in range(2)])
    return x * (1 - wet) + y * wet


def voices():
    """Each voice its own treatment: Dot close and dry (a little room in the basement); DOCTOR through a 1994 sound
    card; the announcer big, with a plate; AFFIRMA polished with a digital double; Mr. Metric a bit blown out."""
    dry, wet = np.zeros((2, N_)), np.zeros((2, N_))
    for key in TL.order:
        Ln = TL.lines[key]
        who = Ln["who"]
        up = signal.resample_poly(Ln["wav"].astype(np.float64), SR, VSR)
        if who == DOCTOR:
            up = robot(up)
        if who == MET:
            up = np.tanh(1.8 * up / (np.abs(up).max() + 1e-9))
        r = np.sqrt((up ** 2).mean()) + 1e-12
        lvl = {DOT: -16.0, ANN: -15.0, DOCTOR: -17.0, KID: -16.5, DOC: -16.0, AFF: -16.0, MET: -16.0}.get(who, -16.5)
        up = up * db(lvl) / r
        sig = np.stack([up, up])
        if who == AFF:
            d = int(0.008 * SR)
            dbl = signal.resample(up, int(len(up) * 1.004))[: len(up)]
            sig = np.stack([up + 0.3 * np.concatenate([np.zeros(d), dbl[:-d]]), up + 0.3 * dbl])
        i = int(Ln["start"] * SR)
        j = min(N_, i + sig.shape[1])
        basement = key.startswith("f") and who in (DOT, DOC)
        (wet if (who in (ANN, AFF) or basement) else dry)[:, i:j] += sig[:, : j - i]
    return dry + reverb(wet, 0.14, 0.9, seed=5)


def compress(x, ratio=2.5, pct=70, att=0.005, rel=0.15):
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
CEIL = -1.8


def build():
    mus, fx, crowd, cr, nosil = Bus(), Bus(), Bus(), Bus(), Bus()
    score(mus, fx, crowd, cr, nosil)
    music = mono_safe(reverb(mus.x, 0.18, 1.2) + reverb(fx.x, 0.1, 0.6), max_ratio=1.0)
    music = signal.sosfilt(signal.butter(4, 35 / (SR / 2), "high", output="sos"), music, axis=1)
    music = np.tanh(1.1 * music) / 1.1
    vo = compress(presence(voices(), 3000, 2.5))
    # the music sits under the words: a slow duck, then a ride per line to keep 15 dB in the speech band
    from scipy.ndimage import maximum_filter1d
    raw = np.convolve(np.abs(vo.mean(axis=0)), np.ones(SR // 20) / (SR // 20), mode="same")
    raw = np.clip(raw / (np.percentile(raw[raw > 1e-5], 80) + 1e-9), 0, 1)
    env = maximum_filter1d(raw, size=int(0.8 * SR), origin=-int(0.15 * SR))
    env = smooth(env, 0.2)
    low = signal.lfilter(*signal.butter(2, 250 / (SR / 2), "low"), music)
    high = signal.lfilter(*signal.butter(2, 4500 / (SR / 2), "high"), music)
    mid = music - low - high
    music = low * (1 - 0.3 * env) + mid * (1 - 0.6 * env) + high * (1 - 0.35 * env)
    ref = music[:, int(S("b1") * SR):int(E("b3") * SR)]
    music = music * db(-15.0) / (np.sqrt((ref ** 2).mean()) + 1e-12)
    # the canned audience: between the lines, under the words
    crowd_x = reverb(crowd.x, 0.12, 0.8, seed=13)
    crowd_x = crowd_x * db(-17.0) / (np.sqrt((crowd_x[crowd_x != 0] ** 2).mean()) + 1e-12)
    # the crash-ins: driven, loud
    crx = reverb(cr.x, 0.2, 1.2, seed=11)
    crx = signal.sosfilt(signal.butter(4, 35 / (SR / 2), "high", output="sos"), crx, axis=1)
    crx = mono_safe(crx, max_ratio=1.0)
    crx = np.tanh(4.0 * crx / (np.percentile(np.abs(crx[np.abs(crx) > 1e-4]), 99.5) + 1e-9)) / np.tanh(4.0)
    seg = crx[:, int(T_TITLE * SR):int((T_TITLE + 0.9) * SR)]
    crx = crx * db(0.0) / (np.sqrt((seg ** 2).mean()) + 1e-12)
    crx = signal.sosfilt(signal.butter(2, 12000 / (SR / 2), "low", output="sos"), crx, axis=1)
    bed = music + crowd_x + crx
    band = lambda x: signal.sosfilt(signal.butter(2, [300 / (SR / 2), 4000 / (SR / 2)], "band", output="sos"), x.mean(axis=0))
    bm, bv = band(bed), band(vo)
    ride = np.ones(N_)
    for key in TL.order:
        Ln = TL.lines[key]
        a, b = int(Ln["start"] * SR), int(Ln["end"] * SR)
        rv = np.sqrt((bv[a:b] ** 2).mean()) + 1e-12
        rm = np.sqrt((bm[a:b] ** 2).mean()) + 1e-12
        margin = 20 * np.log10(rv / rm)
        if margin < 16.0:
            lo, hi = max(0, a - int(0.12 * SR)), min(N_, b + int(0.12 * SR))
            ride[lo:hi] = np.minimum(ride[lo:hi], db(margin - 16.0))
    ride = smooth(ride, 0.15)
    dead = np.ones(N_)
    for a, b in SILENCES:
        dead[int(a * SR):int(b * SR)] = 0.0
    dead = np.convolve(dead, np.ones(int(0.004 * SR)) / int(0.004 * SR), "same")
    bed = bed * ride[None] * dead[None]
    mix = bed + vo + nosil.x * db(-17.0) / (np.abs(nosil.x).max() + 1e-12)
    mix = signal.sosfilt(signal.butter(4, 30 / (SR / 2), "high", output="sos"), mix, axis=1)
    mix = signal.sosfilt(signal.butter(2, 15000 / (SR / 2), "low", output="sos"), mix, axis=1)
    mix = loudness(mix, -14.0)
    a_, b_ = int((TL.total - 1.2) * SR), int(TL.total * SR)
    mix[:, a_:b_] *= np.linspace(1, 0, b_ - a_) ** 2
    mix[:, b_:] = 0.0
    STEMS.update(music=music, vo=vo, crowd=crowd_x, crash=crx)
    return mix


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
    mix = build()
    write(os.path.join(HERE, "build", "audio.wav"), mix)
    print("audio", round(mix.shape[1] / SR, 2), "s in", round(time.time() - t0, 1), "s")
