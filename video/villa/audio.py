"""THE HOLLOW SCHOLARS - the soundtrack. All original, all synthesized.

Score: a melancholy 1970s Italian waltz theme in A minor (3/4, 80 bpm) that falls through a sighing line onto the
raised seventh. It comes on piano and strings, as a music box for the automaton clock and the loop of years, on
harpsichord in the labyrinth and the examination room, on organ at the Governess's door and in the clockwork, sung
by a wordless female voice in the gallery, over low drones; in the tutor's window and at the very end it turns to
A major. The whole score slowly warps out of tune (a creeping tape wow) as the years repeat. In the present day there
is no music at all - only a fluorescent hum and a clock.

Sound: tower bells and clock chimes, ticking, clockwork ratchets and grinding gears, wind through stone alleys,
heels echoing on stone and marble, a gate and doors creaking, mannequin joints, whispers, paper flurries, a hail of
examiners' stamps, quills scratching, candles, a beetle, porcelain and glass cracking. Hard cuts to dead silence
before the scares, before the title, at the door, and before the final lesson.

Voices: the narrator close and warm; the dream's characters dry and close like a 1970s Italian film dubbed into
English (band-limited, no room); the Governess faintly doubled; the present day's voices in a small hard room.
"""
import math
import os
import wave

import numpy as np
from scipy import signal

import fxlib as FXL
import instr as I
import orch as O
import synth82 as Y
from common import E, S, Wx
from edit import EDIT, cut, end
from timeline import TL
from voice import SR as VSR

SR = O.SR
HERE = os.path.dirname(os.path.abspath(__file__))
N_ = int((TL.total + 0.6) * SR)


def db(v):
    return 10 ** (v / 20)


class Bus:
    def __init__(self):
        self.x = np.zeros((2, N_))

    def add(self, sig, t, gain=1.0, pan=0.5, until=None):
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
                f = min(m, int(0.02 * SR))
                sig[:, m - f:] *= np.linspace(1, 0, f)
        i = int(round(t * SR))
        if i >= N_ or i + sig.shape[1] <= 0:
            return
        if i < 0:
            sig, i = sig[:, -i:], 0
        j = min(N_, i + sig.shape[1])
        self.x[:, i:j] += gain * sig[:, : j - i]


# ------------------------------------------------------------------ the theme

BEAT = 60 / 80
BAR = 3 * BEAT
AM, DM, GG, CC, FF, EE = [45, 57, 60, 64], [50, 57, 62, 65], [43, 55, 59, 62], [48, 55, 60, 64], [41, 57, 60, 65], [40, 56, 59, 64]
AMAJ, DMAJ, EMAJ = [45, 57, 61, 64], [50, 57, 62, 66], [40, 56, 59, 64]
CHORDS = [AM, DM, GG, CC, FF, DM, EE, AM]
MAJOR = [AMAJ, DMAJ, EMAJ, AMAJ, DMAJ, [49, 56, 61, 64], EMAJ, AMAJ]
THEME = [[(76, 2), (81, 1)], [(77, 1.5), (76, 0.5), (74, 1)], [(74, 2), (79, 1)], [(76, 3)],
         [(72, 1), (77, 1), (81, 1)], [(79, 1.5), (77, 0.5), (74, 1)], [(71, 1), (76, 1), (80, 1)], [(81, 3)]]
THEME_MAJ = [[(76, 2), (81, 1)], [(78, 1.5), (76, 0.5), (74, 1)], [(76, 2), (80, 1)], [(81, 3)],
             [(78, 1), (81, 1), (85, 1)], [(83, 1.5), (81, 0.5), (78, 1)], [(76, 1), (80, 1), (83, 1)], [(81, 3)]]


def _bars(t0, t1, start_bar=0):
    """(bar index in the 8-bar theme, bar start time) for each bar that begins in [t0, t1)."""
    out, t, b = [], t0, start_bar
    while t < t1 - 0.05:
        out.append((b % 8, t))
        t += BAR
        b += 1
    return out


def piano_theme(bus, t0, t1, level=1.0, start_bar=0, melody=True, major=False, seed=0, oct_=0):
    for b, tb in _bars(t0, t1, start_bar):
        ch = (MAJOR if major else CHORDS)[b]
        bus.add(O.piano([ch[0] - 12], BAR * 1.1, 0.55 * level, seed=b), tb, 1.0, 0.45, until=t1 + 1.5)
        for k in (1, 2):
            bus.add(O.piano(ch[1:], BEAT * 0.9, 0.28 * level, seed=b * 3 + k), tb + k * BEAT, 1.0, 0.55, until=t1 + 1.0)
        if melody:
            t = tb
            for m, beats in (THEME_MAJ if major else THEME)[b]:
                bus.add(O.piano([m + oct_], beats * BEAT * 1.2, 0.5 * level, seed=m + b), t, 1.0, 0.5, until=t1 + 1.2)
                t += beats * BEAT


def strings_bed(bus, t0, t1, level=1.0, start_bar=0, major=False, melody=False):
    for b, tb in _bars(t0, t1, start_bar):
        ch = (MAJOR if major else CHORDS)[b]
        bus.add(O.strings(ch, BAR + 0.3, 0.42 * level, seed=b), tb, 1.0, 0.5, until=t1 + 0.4)
        if melody:
            t = tb
            for m, beats in (THEME_MAJ if major else THEME)[b]:
                bus.add(O.strings([m], beats * BEAT + 0.2, 0.32 * level, seed=m), t, 1.0, 0.55, until=t1 + 0.4)
                t += beats * BEAT


def box_theme(bus, t0, t1, level=1.0, start_bar=0, cents=0.0, rate=1.0, major=False, oct_=12):
    """The music box: the melody an octave up, slower if rate < 1, out of tune by `cents`."""
    notes = []
    for b, tb in _bars(t0, t1 + 30, start_bar)[:8]:
        for m, beats in (THEME_MAJ if major else THEME)[b]:
            notes.append((m + oct_, beats * BEAT / 0.3))
    x = O.music_box(notes, rate=lambda u: rate, amp=level, detune=(lambda u: cents) if cents else None)
    bus.add(x, t0, 1.0, 0.6, until=t1)


def harpsi_ostinato(bus, t0, t1, level=1.0, start_bar=0, step=BEAT / 2, major=False):
    for b, tb in _bars(t0, t1, start_bar):
        ch = (MAJOR if major else CHORDS)[b]
        pat = [ch[1], ch[2], ch[3], ch[2] + 12, ch[3], ch[2]]
        for k, m in enumerate(pat):
            t = tb + k * step
            if t < t1:
                bus.add(I.harpsi(m + 12, 0.6, 0.35 * level, seed=k + b), t, 1.0, 0.35 + 0.3 * (k % 2))


def organ_chord(bus, t, dur, notes, level=1.0):
    bus.add(O.organ(notes, dur, 0.32 * level), t, 1.0, 0.5)


def voice_line(bus, t0, t1, level=1.0, start_bar=4):
    """The wordless female voice: the melody, long and breathy, on 'ah'."""
    for b, tb in _bars(t0, t1, start_bar):
        t = tb
        for m, beats in THEME[b]:
            bus.add(I.choir([m], beats * BEAT + 0.25, 0.3 * level, vowel="a", seed=m, attack=0.15), t, 1.0, 0.5, until=t1 + 0.5)
            t += beats * BEAT


def drone(bus, t0, t1, root=33, level=1.0):
    bus.add(O.drone(t1 - t0 + 0.6, root=root, amp=level), t0, 0.6, until=t1)


def stinger(mus, fx, t, level=1.0):
    """A scare: the orchestra's dissonant stab, an organ cluster, a choir's shriek, a low boom."""
    mus.add(O.scare(1.0 * level, seed=int(t * 10), notes=(45, 46, 51, 57, 58, 63, 64), drive=1.4), t, 1.0)
    mus.add(O.organ([57, 58, 63, 64, 69, 70], 1.6, 0.4 * level), t, 0.8)
    mus.add(I.choir([81, 82, 87], 1.4, 0.45 * level, vowel="a", attack=0.02, gliss=-3.0), t, 0.9)
    fx.add(Y.thud(1.0, f=42), t, 1.4 * level)


def chime(bus, t, level=1.0, m=69):
    """The clock's little chime (four falling notes), and a stroke of the bell."""
    for k, mm in enumerate((m + 7, m + 3, m + 5, m)):
        bus.add(O.clock_bell(0.5 * level, m=mm), t + k * 0.32, 1.0, 0.5)


def tower_bell(bus, t, level=1.0, m=45, dur=6.0):
    bus.add(FXL.temple_bell(m, level, dur), t, 1.0, 0.5)


def ticks(fx, t0, t1, level=1.0, rate=1.0, tock=True):
    k = 0
    t = t0
    while t < t1:
        fx.add(O.tick(1.0, tock=(k % 2 == 1) and tock), t, 0.35 * level, 0.5)
        t += 1.0 / rate
        k += 1


def steps(fx, t0, t1, gap=0.5, level=1.0, seed=0, hard=True, pan=0.5):
    n = max(1, int((t1 - t0) / gap))
    fx.add(Y.footsteps(n, gap, 1.0, seed=seed, hard=hard), t0, level, pan, until=t1 + 0.3)


# ------------------------------------------------------------------ the dead silences

T_NOTHING = E("h2") + 0.08                     # after "nothing": silence, then the title
T_TITLE = cut("t_title")
T_SCARE1 = end("l_loop") - 0.62                # the mannequin at the glass
T_JAM = E("c4") + 0.25                         # the gears seize ...
T_SCARE2 = cut("c_scare")                      # ... and the falling graduate
T_WHITE = E("x1") + 1.15                       # the door opens on white
T_ROOM = S("r1") - 0.3                         # the present day's hum comes up
T_HOLLOW = E("p1") + 0.15                      # her reflection breaks open on nothing
T_LESSON = cut("e_slate") + 0.25
SILENCES = [(T_NOTHING, T_TITLE - 0.02), (T_SCARE1 - 0.24, T_SCARE1), (T_JAM, T_SCARE2), (T_WHITE, T_ROOM),
            (T_HOLLOW, T_LESSON)]


def score(mus, fx):
    T = TL.total
    # ---------------- the hook: a porcelain graduate; inside, nothing
    drone(mus, 0.0, T_NOTHING, root=33, level=0.8)
    for k, m in enumerate((88, 93, 92)):
        mus.add(O.music_box([(m, 2)], amp=0.5, detune=lambda u: 35.0), 0.3 + k * 1.0, 0.8, 0.5)
    fx.add(O.whispers(3.4, 0.6, seed=3), 0.2, 0.35)
    fx.add(Y.crack(0.9, seed=1), Wx("h1", "inside") - 0.05, 0.8)
    fx.add(Y.crack(1.0, seed=2), S("h2") - 0.02, 1.1)
    fx.add(I.clink(1.0, seed=3), S("h2") + 0.35, 0.6)
    fx.add(O.reverse_swell(0.6, 1.0, seed=4), T_NOTHING - 0.45, 0.6)
    # ---------------- the title: the theme's first chord, on organ, strings and the voice
    organ_chord(mus, T_TITLE, 2.2, [45, 57, 64, 69, 72], 1.2)
    mus.add(O.strings([57, 64, 69, 72], 2.2, 0.6), T_TITLE, 1.0)
    mus.add(I.choir([69, 72, 76], 2.0, 0.4, vowel="a", attack=0.2), T_TITLE + 0.1, 0.8)
    fx.add(Y.thud(1.0, f=40), T_TITLE, 1.0)
    # ---------------- the square at nine
    t0, t1 = cut("q_square"), cut("q_clara")
    piano_theme(mus, t0, cut("l_alley"), 0.9)
    strings_bed(mus, t0, cut("l_alley"), 0.6)
    for k in range(3):
        tower_bell(fx, t0 + 0.15 + k * 1.05, 0.9 - 0.15 * k)
    chime(fx, t0 + 3.5, 0.7)
    fx.add(I.flutter(1.6, 1.0, seed=3), t0 + 0.45, 0.8, 0.6)
    fx.add(Y.wind(cut("v_door") - t0, 1.0, seed=5), t0, 0.32)
    fx.add(I.ratchet(t1 - cut("q_clock"), rate=18, amp=0.8), cut("q_clock"), 0.55)
    fx.add(O.whir(t1 - cut("q_clock"), 0.6, f=70), cut("q_clock"), 0.4)
    box_theme(mus, cut("q_clock") + 0.1, t1 + 0.4, 0.6)
    steps(fx, t1 - 0.3, t1 + 0.4, gap=0.45, level=0.6, seed=2)
    # ---------------- the labyrinth
    t0 = cut("l_alley")
    steps(fx, t0, cut("l_window"), gap=0.5, level=0.85, seed=4)
    tower_bell(fx, t0 + 0.4, 0.3, m=50, dur=5.0)                          # a church bell, distant, somewhere in the maze
    tower_bell(fx, cut("l_stairs") + 1.6, 0.22, m=47, dur=5.0)
    harpsi_ostinato(mus, t0, cut("l_window"), 0.7)
    strings_bed(mus, cut("l_window"), cut("l_stairs"), 0.5, major=True)
    box_theme(mus, cut("l_window") + 0.2, cut("l_stairs"), 0.7, major=True)                   # the tutor's window: A major
    fx.add(FXL.paper_flutter(cut("l_name") - cut("l_stairs"), 1.0, seed=7), cut("l_stairs"), 0.6)
    for word, _ in (("Essays.", 0), ("Homework.", 0), ("Code.", 0), ("Reports.", 0)):
        fx.add(O.whoosh(0.5, True, seed=len(word), amp=0.8), Wx("l2", word) - 0.2, 0.7)
    harpsi_ostinato(mus, cut("l_stairs"), cut("l_name"), 0.8, step=BEAT / 3)
    strings_bed(mus, cut("l_stairs"), cut("l_name"), 0.6, melody=True)
    piano_theme(mus, cut("l_name"), cut("l_loop"), 0.6, start_bar=6, melody=True)
    drone(mus, cut("l_name"), cut("v_door"), root=33, level=0.7)
    # deja vu: the same three notes, a little more out of tune each time
    t0 = cut("l_loop")
    for k in range(3):
        mus.add(O.music_box([(88, 1), (93, 1), (92, 2)], amp=0.8, detune=lambda u, k=k: [0.0, 45.0, 100.0][k]), t0 + k * 0.58, 0.9, 0.5)
        fx.add(Y.footsteps(2, 0.22, 1.0, seed=k, hard=True), t0 + k * 0.58 + 0.05, 0.6)
    stinger(mus, fx, T_SCARE1, 1.0)
    fx.add(I.smash(1.0, seed=5), T_SCARE1 + 0.1, 0.9)
    # ---------------- the villa
    fx.add(Y.creak(1.4, 1.0, seed=3, f0=420, f1=180), cut("v_gate") + 0.2, 0.7)
    organ_chord(mus, cut("v_door"), E("v1") - cut("v_door") + 1.0, [33, 45, 52, 57], 0.8)
    fx.add(Y.creak(0.9, 1.0, seed=5, f0=110, f1=60), cut("v_door"), 0.7)
    fx.add(I.crackle(E("v1") - cut("v_door") + 0.5, 0.5, seed=2), cut("v_door"), 0.25)
    # ---------------- the gallery
    t0, t1 = cut("g_gallery"), cut("g_exam")
    steps(fx, t0, t1, gap=0.62, level=0.75, seed=6)
    voice_line(mus, t0, cut("g_double"), 0.9, start_bar=4)
    strings_bed(mus, t0, cut("w_desk"), 0.5, start_bar=4)
    for k in range(3):
        fx.add(I.joint(1.0, seed=k), t0 + 1.5 + k * 0.2, 0.6)
    t0 = cut("g_exam")
    fx.add(FXL.paper_flutter(3.2, 0.8, seed=9), t0, 0.45)
    harpsi_ostinato(mus, t0, Wx("g2", "On"), 0.8, step=BEAT / 3, start_bar=0)
    t94 = Wx("g2", "Ninety-four")
    for i in range(33):
        fx.add(O.stamp(1.0), t94 + 0.02 + i * 0.022, 0.32 if i % 2 else 0.22, 0.3 + 0.4 * ((i % 6) / 5))
    mus.add(Y.riser(1.4, 0.8, f0=80, f1=600), Wx("g2", "On") + 0.1, 0.4)
    fx.add(O.whispers(2.5, 0.8, seed=11), cut("g_double") + 0.4, 0.4)
    piano_theme(mus, cut("g_double"), cut("w_desk"), 0.55, start_bar=0, melody=False)
    # ---------------- the writing room: the same night, year after year
    t0, t1 = cut("w_desk"), cut("c_gears")
    fx.add(FXL.pencil(t1 - t0, 1.0, seed=4), t0, 0.22)
    fx.add(I.crackle(t1 - t0, 0.5, seed=3), t0, 0.18)
    ticks(fx, t0, t1, 0.8, rate=2.0)
    for k, (nm, cents, rate) in enumerate((("w_desk", 0.0, 1.0), ("w_desk2", 30.0, 0.95), ("w_desk3", 65.0, 0.88), ("w_final", 110.0, 0.8))):
        tc = cut(nm)
        chime(fx, tc, 0.6, m=69 - k)
        fx.add(Y.creak(0.7, 1.0, seed=20 + k, f0=230, f1=130), tc + 1.3 + 0.2 * k, 0.45, 0.62)     # a floorboard behind her
        box_theme(mus, tc + 0.15, end(nm) if nm != "w_desk3" else cut("w_ledger"), 0.75, cents=cents, rate=rate)
    strings_bed(mus, cut("w_shelves"), cut("w_desk3"), 0.45)
    t88 = Wx("w5", "Eighty-eight")
    rng = np.random.default_rng(88)
    for i in range(30):                                                      # the cabinet lighting up
        fx.add(O.celesta(int(rng.choice([81, 84, 86, 88, 91, 93, 96])), 0.35, dur=0.8), t88 + i * 0.03, 0.3, rng.uniform(0.2, 0.8))
    t18 = Wx("w5", "Nearly")
    for i in range(18):
        fx.add(Y.crack(0.3, seed=i), t18 + (i % 7) * 0.05 + i * 0.012, 0.25, rng.uniform(0.2, 0.8))
    fx.add(O.page(1.0, seed=2), cut("w_ledger") + 0.1, 0.6)
    tower_bell(fx, cut("w_final") + 0.05, 1.0, m=43, dur=5.0)
    mus.add(I.choir([69, 70, 75], 1.4, 0.5, vowel="a", attack=0.4), cut("w_final"), 0.7)
    # ---------------- the clockwork
    t0, t1 = cut("c_gears"), T_JAM
    ticks(fx, t0, t1, 1.0, rate=3.0)
    fx.add(I.ratchet(t1 - t0, rate=22, amp=1.0), t0, 0.35)
    fx.add(O.whir(t1 - t0, 1.0, f=55), t0, 0.5)
    drone(mus, t0, t1, root=33, level=0.9)
    organ_chord(mus, t0, cut("c_bug") - t0, [45, 52, 57, 60], 0.7)
    fx.add(I.servo(0.6, 0.6, 180, 320, seed=1), Wx("c2", "fifty") - 0.35, 0.4)
    fx.add(I.servo(0.7, 0.6, 180, 360, seed=2), Wx("c2", "Coding"), 0.4)
    fx.add(Y.skitter(cut("c_fix") - cut("c_bug"), 1.0, seed=3, rate=30), cut("c_bug"), 0.5)
    for k in range(4):
        fx.add(O.clunk(0.8, seed=k), cut("c_bug") + 0.3 + k * 0.45, 0.4)
    fx.add(Y.engine(E("c4") - S("c4") + 0.4, 1.0, seed=4), S("c4") - 0.2, 0.6)
    fx.add(Y.riser(0.5, 1.0, f0=900, f1=3200), E("c4") - 0.3, 0.5)                    # the screech as it seizes
    stinger(mus, fx, T_SCARE2 + 0.25, 1.1)
    fx.add(I.smash(1.0, seed=8), T_SCARE2 + 0.3, 1.0)
    # ---------------- the hall of mirrors
    t0, t1 = cut("m_mirrors"), cut("x_door")
    for k, m in enumerate((88, 91, 95, 100)):
        mus.add(O.celesta(m, 0.25, dur=2.0), t0 + 0.2 + k * 0.6, 0.5, 0.3 + 0.15 * k)
    mus.add(I.choir([64, 69, 72], cut("m_super") - t0 + 0.5, 0.35, vowel="o", attack=0.6), t0, 0.7, until=cut("m_super") + 0.6)
    for k in range(4):
        fx.add(O.reverse_swell(0.6, 0.6, seed=k), Wx("m1", "stop") - 0.2 + k * 0.25, 0.3)
    fx.add(Y.crack(0.8, seed=6), Wx("m1", "honest"), 0.7)
    fx.add(FXL.pencil(cut("x_door") - cut("m_super"), 1.0, seed=8), cut("m_super"), 0.35)
    fx.add(FXL.room_tone(cut("x_door") - Wx("m2", "employers"), 1.0, hum=True), Wx("m2", "employers") - 0.2, 0.5)
    # ---------------- the locked door
    t0 = cut("x_door")
    steps(fx, t0, E("x1"), gap=0.6, level=0.7, seed=9)
    drone(mus, t0, T_WHITE, root=34, level=0.7)
    fx.add(O.click(1.0), E("x1") + 0.1, 0.8)
    fx.add(O.clunk(1.0, seed=3), E("x1") + 0.18, 0.7)
    fx.add(Y.creak(1.0, 1.0, seed=8, f0=100, f1=50), E("x1") + 0.2, 0.7)
    mus.add(Y.riser(0.9, 1.0, f0=300, f1=5000), E("x1") + 0.25, 0.5, until=T_WHITE)
    # ---------------- the present day: no music; a hum, a clock
    t0, t1 = T_ROOM, cut("p_window")
    fx.add(FXL.room_tone(t1 - t0 + 0.4, 1.0, hum=True), t0, 0.8, until=t1 + 0.2)
    ticks(fx, t0, t1, 0.5, rate=1.0, tock=False)
    fx.add(O.page(1.0, seed=5), Wx("r2", "why") - 0.15, 0.5)
    fx.add(Y.breath(1.2, 0.6, rate=1.6, seed=2), E("r4") + 0.1, 0.25)
    fx.add(Y.thud(1.0, f=90), cut("r_thanks") + 0.9, 0.45)
    ta = cut("r_after")
    for k in range(6):
        fx.add(O.ding(0.6, m=96), ta + 0.05 + k * 0.3, 0.25)
    fx.add(FXL.paper_flutter(0.4, 1.0, seed=3), Wx("r6", "Fifty-three") - 0.15, 0.4)
    drone(mus, Wx("r6", "nothing") - 0.3, T_HOLLOW, root=33, level=0.7)
    # ---------------- the dark window
    t0 = cut("p_window")
    fx.add(FXL.traffic(T_HOLLOW - t0, 0.6, seed=4), t0, 0.25)
    box_theme(mus, t0 + 0.2, T_HOLLOW, 0.7, cents=140.0, rate=0.8)
    fx.add(O.whispers(T_HOLLOW - t0, 0.7, seed=12), t0 + 0.6, 0.3)
    mus.add(I.choir([57, 58, 64], 2.0, 0.4, vowel="o", attack=0.5), Wx("p1", "machine") - 0.2, 0.6)
    fx.add(Y.crack(1.0, seed=9), Wx("p1", "inside") - 0.04, 1.0)
    fx.add(I.smash(0.7, seed=10), Wx("p1", "inside") + 0.3, 0.5)
    # ---------------- the lesson: the theme in A major
    t0 = T_LESSON
    box_theme(mus, t0, cut("e_unesco") + 0.4, 0.6, major=True, rate=0.9)
    for k in range(12):
        fx.add(FXL.chalk(1.0, seed=k), S("e1") + 0.5 + k * 0.35, 0.35)
    fx.add(I.crackle(cut("e_clock") - t0, 0.4, seed=7), t0, 0.15)
    piano_theme(mus, cut("e_unesco"), cut("e_clock"), 0.7, major=True)
    strings_bed(mus, cut("e_unesco"), cut("e_clock") + 0.5, 0.55, major=True)
    t0 = cut("e_clock")
    tower_bell(fx, t0 + 0.3, 1.0, m=45, dur=6.0)
    fx.add(O.whir(cut("e_fine") - t0, 0.5, f=70), t0, 0.3)
    box_theme(mus, t0 + 0.4, cut("e_fine"), 0.55, cents=20.0, rate=0.9)
    fx.add(O.clunk(1.0, seed=6), cut("e_fine") - 0.25, 0.6)
    tower_bell(fx, cut("e_fine") + 0.15, 1.1, m=40, dur=7.0)
    mus.add(O.strings([45, 57, 64, 69], 1.8, 0.4), cut("e_fine") + 0.15, 0.8)


def warp_depth(t):
    """How far out of tune the score has drifted (cents) at time t: the creeping wow of years repeating."""
    pts = [(0, 0), (30, 6), (55, 18), (80, 32), (110, 45), (140, 45), (146, 80), (152, 20), (TL.total, 15)]
    xs, ys = zip(*pts)
    return np.interp(t, xs, ys)


def warp(x):
    t = np.arange(x.shape[1]) / SR
    f = 0.55
    A = warp_depth(t) / (1731.0 * 2 * np.pi * f)
    d = A * np.sin(2 * np.pi * f * t) + 0.3 * A * np.sin(2 * np.pi * 1.7 * t + 1)
    src = np.clip(np.arange(x.shape[1]) - d * SR, 0, x.shape[1] - 1)
    return np.stack([np.interp(src, np.arange(x.shape[1]), x[ch]) for ch in range(2)])


# ------------------------------------------------------------------ voices

def reverb(x, wet=0.1, rt60=0.8, seed=8):
    rng = np.random.default_rng(seed)
    t = np.arange(int(rt60 * 1.4 * SR)) / SR
    ir = np.stack([rng.normal(0, 1, len(t)) * np.exp(-6.9 * t / rt60) for _ in range(2)])
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    y = np.stack([signal.fftconvolve(x[c], ir[c])[: x.shape[1]] for c in range(2)])
    return x * (1 - wet) + y * wet


def dubbed(x):
    """A 1970s dub: close, dry, band-limited, a touch of tape saturation."""
    y = signal.sosfilt(signal.butter(3, [150 / (SR / 2), 6500 / (SR / 2)], "band", output="sos"), x)
    return np.tanh(1.6 * y / (np.abs(y).max() + 1e-9)) * (np.abs(y).max() + 1e-9) / 1.25


def doubled(x):
    """The Governess: a second, slightly detuned copy of her voice a few milliseconds behind."""
    d = int(0.009 * SR)
    r = 2 ** (-0.12 / 12)
    y2 = signal.resample(x, int(len(x) / r))[: len(x)]
    y2 = np.concatenate([np.zeros(d), y2])[: len(x)]
    return x * 0.8 + y2 * 0.4


DREAM = ("CLARA", "GOV")


def voices():
    """The narrator close with a little warmth; the dream's people dubbed; the present day in a small hard room."""
    nar, dub, room = np.zeros((2, N_)), np.zeros((2, N_)), np.zeros((2, N_))
    t_real0, t_real1 = cut("r_room"), cut("p_window")
    for key in TL.order:
        Ln = TL.lines[key]
        who = Ln["who"]
        up = signal.resample_poly(Ln["wav"].astype(np.float64), SR, VSR)
        real = t_real0 <= Ln["start"] < t_real1
        if who in DREAM and not real:
            up = dubbed(up)
            if who == "GOV":
                up = doubled(up)
        r = np.sqrt((up ** 2).mean()) + 1e-12
        up = up * db({"NAR": -16.0, "GOV": -16.5, "CLARA": -16.0}.get(who, -16.0)) / r
        pan = {"GOV": 0.56, "CLARA": 0.47, "INT1": 0.46, "INT2": 0.54}.get(who, 0.5)
        sig = np.stack([up * np.sqrt(1 - pan), up * np.sqrt(pan)]) * np.sqrt(2)
        i = int(Ln["start"] * SR)
        j = min(N_, i + sig.shape[1])
        tgt = nar if who == "NAR" else (room if real or who in ("INT1", "INT2") else dub)
        if key == "o3":                                                    # "Hello?" into an empty square
            tgt = room
        tgt[:, i:j] += sig[:, : j - i]
    nar = reverb(nar, 0.07, 0.7, seed=3)
    room = reverb(room, 0.14, 0.45, seed=5)
    return nar + dub + room


# ------------------------------------------------------------------ the mix

def smooth(x, sec):
    k = max(1, int(sec * SR))
    return np.convolve(np.pad(x, k, mode="edge"), np.ones(k) / k, "same")[k:-k]


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


def presence(x, f0=3000, gain_db=2.0, q=0.9):
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    al = np.sin(w0) / (2 * q)
    b = np.array([1 + al * A, -2 * np.cos(w0), 1 - al * A])
    a = np.array([1 + al / A, -2 * np.cos(w0), 1 - al / A])
    return signal.lfilter(b / a[0], a / a[0], x, axis=1)


NEED = {"NAR": 11.0}                              # the voice over the bed in the speech band (characters: 13)
BED = -3.0                                        # the beds' ceiling between lines, against the average line (dB)
HITS = [(T_TITLE, 4.0, 1.6), (T_SCARE1, 11.0, 1.3), (T_SCARE2 + 0.25, 11.0, 1.3)]   # (time, ceiling dB, seconds)
CEIL = -2.0
STEMS = {}


def buses():
    path = os.path.join(HERE, "build", "buses.npz")
    if os.environ.get("HV_CACHE") == "load" and os.path.exists(path):
        d = np.load(path)
        return d["mus"].astype(np.float64), d["fx"].astype(np.float64)
    mus, fx = Bus(), Bus()
    score(mus, fx)
    if os.environ.get("HV_CACHE"):
        np.savez(path, mus=mus.x.astype(np.float32), fx=fx.x.astype(np.float32))
    return mus.x, fx.x


def build():
    mus_x, fx_x = buses()
    music = warp(reverb(mus_x, 0.24, 2.0, seed=2))
    music = signal.sosfilt(signal.butter(4, 35 / (SR / 2), "high", output="sos"), music, axis=1)
    fxx = reverb(fx_x, 0.16, 1.1, seed=3)
    fxx = signal.sosfilt(signal.butter(4, 35 / (SR / 2), "high", output="sos"), fxx, axis=1)
    vo = compress(presence(voices(), 3200, 2.5))
    # levels: the title chord sets the music's scale; the effects sit under it
    ref = music[:, int(T_TITLE * SR):int((T_TITLE + 1.5) * SR)]
    music = music * db(-13.0) / (np.sqrt((ref ** 2).mean()) + 1e-12)
    on = np.abs(fxx).max(axis=0) > 1e-4
    fxx = fxx * db(-24.0) / (np.sqrt((fxx[:, on] ** 2).mean()) + 1e-12)
    # duck the beds under every line until the voice clears them by NEED dB in the speech band
    band = lambda x: signal.sosfilt(signal.butter(2, [300 / (SR / 2), 4000 / (SR / 2)], "band", output="sos"), x.mean(axis=0))
    bv, bm, bf = band(vo), band(music), band(fxx)
    gain = {k: 0.0 for k in TL.order}
    spans = {k: (int(TL.s(k) * SR), int(TL.e(k) * SR)) for k in TL.order}

    def rides():
        r = np.ones(N_)
        for key in TL.order:
            a, b = spans[key]
            lo, hi = max(0, a - int(0.15 * SR)), min(N_, b + int(0.15 * SR))
            r[lo:hi] = np.minimum(r[lo:hi], db(gain[key]))
        return smooth(r, 0.18)

    for _ in range(10):
        ride = rides()
        bb = (bm + bf) * ride
        short = False
        for key in TL.order:
            a, b = spans[key]
            mg = 20 * np.log10((np.sqrt((bv[a:b] ** 2).mean()) + 1e-12) / (np.sqrt((bb[a:b] ** 2).mean()) + 1e-12))
            need = NEED.get(TL.who(key), 13.0)
            if mg < need:
                gain[key] -= (need - mg) + 0.3
                short = True
        if not short:
            break
    ride = rides()
    music, fxx = music * ride[None], fxx * ride[None]
    # between the lines the beds stay under the voice (quietly menacing, not loud); only the title and the two scares
    # are let through, so they are by far the loudest things in the film
    from scipy.ndimage import minimum_filter1d
    v_rms = np.sqrt(np.mean([(vo[:, int(TL.s(k) * SR):int(TL.e(k) * SR)] ** 2).mean() for k in TL.order]))
    beds = music + fxx
    env = np.sqrt(smooth((beds ** 2).mean(axis=0), 0.4)) + 1e-9
    tgt = np.full(N_, v_rms * db(BED))
    for t, lvl, dur in HITS:
        tgt[int((t - 0.05) * SR):int((t + dur) * SR)] = v_rms * db(lvl)
    lev = minimum_filter1d(np.minimum(1.0, tgt / env), size=int(0.3 * SR))
    lev = smooth(lev, 0.12)
    music, fxx = music * lev[None], fxx * lev[None]
    mix = music + fxx + vo
    mix = signal.sosfilt(signal.butter(4, 30 / (SR / 2), "high", output="sos"), mix, axis=1)
    dead = np.ones(N_)
    for a, b in SILENCES:
        dead[int(a * SR):int(b * SR)] = 0.0
    dead = np.convolve(dead, np.ones(int(0.004 * SR)) / int(0.004 * SR), "same")
    rng = np.random.default_rng(21)
    hiss = signal.sosfilt(signal.butter(2, [400 / (SR / 2), 6000 / (SR / 2)], "band", output="sos"), rng.normal(0, 1, N_))
    mix = mix * dead[None] + np.stack([hiss, hiss]) * db(-72) * (1 - dead)[None]
    mix = loudness(mix, -14.0)
    a_, b_ = int((TL.total - 0.5) * SR), int(TL.total * SR)
    mix[:, a_:b_] *= np.linspace(1, 0, b_ - a_) ** 2
    mix[:, b_:] = 0.0
    STEMS.update(music=music, fx=fxx, vo=vo)
    report(music, fxx, vo)
    return mix


def report(music, fxx, vo):
    band = lambda x: signal.sosfilt(signal.butter(2, [300 / (SR / 2), 4000 / (SR / 2)], "band", output="sos"), x.mean(axis=0))
    bb, bv = band(music + fxx), band(vo)
    rms = lambda y: 20 * np.log10(np.sqrt((y ** 2).mean()) + 1e-9)
    low = []
    for key in TL.order:
        a, b = int(TL.s(key) * SR), int(TL.e(key) * SR)
        mg = rms(bv[a:b]) - rms(bb[a:b])
        if mg < NEED.get(TL.who(key), 13.0) - 1.0:
            low.append(f"{key} {mg:.1f}")
    print("lines under the margin:", ", ".join(low) or "none")


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


def loudness(x, target):
    import pyloudnorm as pyln
    g = 1.0
    for _ in range(4):
        y = limit(x * g, db(CEIL))
        lufs = pyln.Meter(SR).integrated_loudness(y.T)
        g *= db(target - lufs)
    return limit(x * g, db(CEIL))


def aac_safe(x, target=-1.6, rates=("192k", "256k"), rounds=3):
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
