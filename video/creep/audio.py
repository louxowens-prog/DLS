"""The soundtrack: an original 1982-style horror-anthology score, the sound collage against the edit, the voices, the
mix.

Score: an eerie piano motif in D minor (a falling figure that trips on a sharpened seventh), analog string-machine
pads and synth-brass stabs, an arpeggiator and a pulsing synth bass that drive the tales, a music box for the
margins and the moral, low rotting drones, a wordless choir for the reveals, a theremin wail for the ghost, and a
cheesy organ jingle for the mail-order back page. A stinger on every colour shock; thunder on every lightning flash.

Collage: storm (thunder, rain, wind), the flat (creaks, the lamp), the car (engine, wipers, the sat-nav), the swamp
(wind, insects), the dorm (typing, paper), the exam (a clock, footsteps), the clinic (a heart monitor, the spotter's
whine, the unplugging), the cockpit (warnings), the climax (glass, squelch, growl), the reader's night (a low-battery
chime, a match, a heartbeat, breathing, a rattling pill bottle, a keypad, a dial tone), page turns.

Hard cuts to dead silence: before 'Signal lost.'; before the climax; at the blackout. The exam hall is silent but for
a clock. Voices always well clear of the music. Loudness -14 LUFS.
"""
import os
import wave

import numpy as np
from scipy import signal

import fxlib as FXL
import instr as I
import orch as O
import synth82 as Y
from common import E, S, Wx
from edit import EDIT, FREEZE_D, LIGHTNING, PAGES, SHOCKS
from timeline import TL
from voice import SR as VSR

SR = O.SR
HERE = os.path.dirname(os.path.abspath(__file__))
N_ = int((TL.total + 0.6) * SR)


def db(v):
    return 10 ** (v / 20)


def cut(name):
    return next(e[0] for e in EDIT if e[1] == name)


def end(name):
    i = next(j for j, e in enumerate(EDIT) if e[1] == name)
    return EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total


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

T_SIG = cut("v_signal")                         # the road goes dead quiet ...
T_SIGNAL = S("v5")                              # ... until the sat-nav loses its signal
T_PRE = E("s7")                                 # silence before the thing on the screen
T_THING = cut("s_thing")                        # the loudest moment
T_BLACK = cut("r_dark")                         # the power dies
T_STILL = cut("r_still") + 0.56                 # the bottle has fallen; then nothing
SILENCES = [(T_SIG + 0.05, T_SIGNAL - 0.02), (T_PRE + 0.02, T_THING), (T_BLACK, S("r1") - 0.05), (T_STILL, S("r5") - 0.12)]
T_EXAM = cut("g_exam")


def in_silence(t):
    return any(a <= t < b for a, b in SILENCES)


# ------------------------------------------------------------------ harmony

BEAT = 60 / 84
DM, BB, GM, AA, FF, CC = [50, 57, 62, 65], [46, 53, 58, 62], [43, 55, 58, 62], [45, 52, 57, 61], [41, 53, 57, 60], [48, 55, 60, 64]
PROG = [DM, BB, GM, AA]
MOTIF = [(74, 1), (69, 0.5), (70, 0.5), (77, 1), (76, 1), (74, 1), (69, 1), (73, 1.5), (74, 2.5)]   # 9 beats


def motif(bus, t0, until, level=1.0, transpose=0, inst="piano", beat=BEAT, pan=0.42):
    t = t0
    while t < until:
        for m, b in MOTIF:
            if t >= until:
                return
            d = b * beat
            if inst == "piano":
                bus.add(O.piano([m + transpose], d), t, level, pan, until=until + 1.0)
            elif inst == "box":
                bus.add(O.music_box([(m + transpose + 12, b)], amp=1.0), t, level, pan, until=until + 1.0)
            t += d
        t += 1.5 * beat


def pads(bus, t0, t1, level=1.0, prog=PROG, bars=2.0, cut_=(500, 2000), seed=0, beat=BEAT):
    t, i = t0, 0
    d = bars * 4 * beat
    while t < t1:
        ch = prog[i % len(prog)]
        bus.add(Y.pad(ch, min(d, t1 - t) + 0.2, cut=cut_, seed=seed + i), t, level, 0.5, until=t1 + 0.4)
        t += d
        i += 1


def arp(bus, t0, t1, level=1.0, prog=PROG, bars=1.0, step=None, beat=BEAT, pattern=(0, 1, 2, 3, 2, 1), octave=12, pan=0.6):
    step = step or beat / 4
    t, k = t0, 0
    while t < t1:
        bar = int((t - t0) / (bars * 4 * beat))
        ch = prog[bar % len(prog)]
        m = ch[pattern[k % len(pattern)] % len(ch)] + octave
        bus.add(Y.pluck(m, 1.0), t, level, pan + 0.15 * np.sin(k * 0.7), until=t1)
        t += step
        k += 1


def pulse(bus, t0, t1, level=1.0, prog=PROG, bars=1.0, beat=BEAT):
    t = t0
    while t < t1:
        bar = int((t - t0) / (bars * 4 * beat))
        root = prog[bar % len(prog)][0] - 12
        bus.add(Y.bass(root, beat / 2 * 0.8), t, level, 0.5, until=t1)
        t += beat / 2


def ringback(dur):
    """A British ring: 400 + 450 Hz, on 0.4 s, off 0.2 s, on 0.4 s, off 2 s."""
    t = np.arange(int(dur * SR)) / SR
    ph = t % 3.0
    gate = ((ph < 0.4) | ((ph >= 0.6) & (ph < 1.0))).astype(float)
    gate = np.convolve(gate, np.ones(int(0.006 * SR)) / int(0.006 * SR), "same")
    return (np.sin(2 * np.pi * 400 * t) + np.sin(2 * np.pi * 450 * t)) * 0.07 * gate


def stinger(mus, fx, t, color="red", level=1.0):
    """The colour shock: an orchestra-and-synth stab, a choir shriek, a boom."""
    root = {"red": 50, "green": 49, "blue": 51, "violet": 48}.get(color, 50)
    mus.add(O.scare(1.0, seed=int(t * 10), notes=(root - 9, root - 8, root - 3, root + 3, root + 4, root + 10, root + 11)), t, 1.3 * level)
    mus.add(Y.stab([root, root + 1, root + 6, root + 12], 1.0, 0.9), t, 1.1 * level)
    mus.add(I.choir([root + 22, root + 23, root + 28], 1.2, 1.0, vowel="a", attack=0.02), t, 0.9 * level)


def page_turn(fx, t, level=1.0):
    fx.add(O.page(1.0, seed=int(t)), t, 0.8 * level, 0.6)
    fx.add(O.whoosh(0.4, True, seed=int(t), amp=0.6), t + 0.05, 0.45 * level, 0.4)


def score(mus, fx, nosil):
    # ---------------- cold open: storm, the cover and its hook
    t_end = cut("o_window")
    fx.add(FXL.rain(t_end + 0.2, 0.7), 0.0, 0.9)
    mus.add(O.drone(6.8, root=26, amp=1.0), 0.1, 0.9, until=Wx("c1", "fewer"))
    pads(mus, 0.5, Wx("c1", "fewer"), 0.8, prog=[DM, BB], bars=1.5, cut_=(400, 1600))
    motif(mus, 0.7, Wx("c1", "fewer") - 0.1, 0.9)
    mus.add(Y.riser(1.6, 0.8), Wx("c1", "fewer") - 1.6, 0.8)
    fx.add(Y.creak(1.0, 1.0, seed=1), cut("o_noai") + 0.4, 0.6, 0.3)
    fx.add(O.click(1.0), Wx("c1", "working") + 0.25, 1.2, 0.7)
    fx.add(O.power_down(0.8, 1.0), Wx("c1", "working") + 0.27, 0.6, 0.7)
    fx.add(O.squelch(1.0, seed=2, dur=0.4), Wx("c1", "working") + 0.6 + 0.35, 0.7, 0.6)
    # ---------------- the reader, the host at the window
    t0, t1 = cut("o_window"), cut("o_muse")
    fx.add(FXL.rain(t1 - t0 + 0.5, 0.8, seed=6), t0, 1.0)
    fx.add(Y.wind(t1 - t0 + 1.0, 1.0, seed=2), t0, 0.7)
    pads(mus, t0, t1, 1.0, prog=[DM, GM, AA, DM], bars=0.75, cut_=(600, 2600))
    motif(mus, S("c2") - 0.1, t1, 1.0, inst="piano")
    pulse(mus, S("c2"), t1, 0.8, prog=[DM, GM, AA, DM], bars=0.75)
    mus.add(I.choir([62, 65, 69, 74], 1.6, 1.0, vowel="a", attack=0.05), Wx("c2", "Atrophy") + 0.2, 1.0, until=t1 + 0.5)
    mus.add(Y.stab([50, 57, 62, 65, 69], 1.0, 1.2), Wx("c2", "Atrophy") + 0.2, 1.0)
    # ---------------- the assistant, Nora
    t0, t1 = cut("o_muse"), cut("o_skills")
    fx.add(FXL.rain(t1 - t0 + 0.3, 0.5, seed=7), t0, 0.7)
    fx.add(FXL.room_tone(t1 - t0, 1.0), t0, 1.0)
    pads(mus, t0, t1, 0.6, prog=[DM, BB], bars=0.6, cut_=(300, 1000))
    fx.add(Y.wake_chime(1.0), S("c3") - 0.35, 1.2, 0.65)
    fx.add(O.whoosh(0.35, False, seed=3, amp=0.7), Wx("c4", "summarise"), 0.8, 0.3)
    fx.add(O.page(1.0, seed=9), Wx("c4", "summarise") + 0.4, 1.0, 0.2)
    # ---------------- the skills handed over
    t0, t1 = cut("o_skills"), cut("o_before")
    page_turn(fx, t0)
    pulse(mus, t0 + 0.1, t1, 1.0, prog=[DM, DM, BB, AA], bars=0.5)
    pads(mus, t0, Wx("c5", "lose"), 0.7, prog=[DM, BB], bars=1.0, cut_=(500, 2400))
    words = ("Write", "Navigate", "Remember", "Decide", "Hand")
    for i, w in enumerate(words[:4]):                                   # a stab in the gap after each word, not on it
        t_hit = Wx("c5", words[i + 1]) - 0.16
        mus.add(Y.stab([62 + i * 2, 69 + i * 2], 1.0, 0.25), t_hit, 0.45)
    fx.add(Y.riser(0.9, 0.7, f0=400, f1=2500), Wx("c5", "Hand") - 0.2, 0.7)
    for i in range(4):
        fx.add(O.slurp(0.5, 0.8), Wx("c5", "Hand") + 0.2 * i + 0.2, 0.6, 0.3 + 0.13 * i)
    mus.add(I.choir([74, 70, 67, 62], 2.0, 1.0, vowel="o", attack=0.3, gliss=-5), Wx("c5", "lose") - 0.3, 0.8, until=t1)
    mus.add(O.drone(2.0, root=26, amp=1.0), Wx("c5", "lose") - 0.4, 0.8, until=t1)
    # ---------------- it happened before
    t0, t1 = cut("o_before"), cut("o_more")
    page_turn(fx, t0)
    arp(mus, t0 + 0.1, t1, 0.8, prog=[DM, BB, GM, AA], bars=0.5, pattern=(0, 2, 1, 3))
    pulse(mus, t0 + 0.1, t1, 0.7, prog=[DM, BB, GM, AA], bars=0.5)
    for k, ch in enumerate("4x7"):
        fx.add(Y.beep(1800 + 200 * k, 0.05), Wx("c6", "calculators") + 0.1 * k, 0.8, 0.4)
    fx.add(Y.beep(1300, 0.12), Wx("c6", "GPS") + 0.1, 0.8, 0.6)
    fx.add(Y.beep(1650, 0.12), Wx("c6", "GPS") + 0.25, 0.8, 0.6)
    fx.add(O.keys(5, 0.08, 1.0, seed=2), Wx("c6", "routes") + 0.1, 0.8, 0.5)
    # ---------------- AI can take far more
    t0, t1 = cut("o_more"), cut("v_title")
    mus.add(O.drone(t1 - t0 + 0.6, root=25, amp=1.0), t0, 1.2, until=t1 + 0.3)
    mus.add(Y.pad([38, 45, 50, 51], t1 - t0, 1.0, cut=(300, 3000), attack=0.2), t0, 1.0, until=t1 + 0.3)
    # ---------------- tale one
    t0, t1 = cut("v_title"), cut("v_car")
    page_turn(fx, t0)
    mus.add(I.choir([62, 65, 70], t1 - t0, 1.0, vowel="a", attack=0.4), t0 + 0.2, 0.9, until=t1 + 0.3)
    mus.add(Y.stab([50, 57, 62, 65], 1.0, 1.0), S("v1") + 0.6, 0.8)
    motif(mus, S("v1") - 0.1, t1, 0.8, inst="piano", beat=BEAT * 0.8)
    fx.add(Y.wind(t1 - t0 + 0.5, 0.8, seed=3), t0, 0.6)
    # the car
    t0, t1 = cut("v_car"), cut("v_map")
    fx.add(Y.engine(cut("v_signal") - t0 + 0.2, 1.0), t0, 1.1, until=cut("v_signal") + 0.05)
    fx.add(FXL.rain(cut("v_signal") - t0, 0.9, seed=8), t0, 0.9, until=cut("v_signal") + 0.05)
    k = 0
    while t0 + 0.2 + k * 0.91 < t1:
        fx.add(Y.wiper(1.0, seed=k), t0 + 0.2 + k * 0.91, 0.8, 0.3 + 0.4 * (k % 2))
        k += 1
    fx.add(Y.wake_chime(0.8), S("v2") - 0.3, 1.0, 0.7)
    arp(mus, t0, cut("v_signal"), 0.85, prog=[DM, DM, BB, AA], bars=1.0, pattern=(0, 1, 2, 3, 2, 1, 0, 2))
    pulse(mus, t0, cut("v_signal"), 0.8, prog=[DM, DM, BB, AA])
    pads(mus, t0, cut("v_signal"), 0.6, prog=[DM, BB, GM, AA], bars=1.0, cut_=(400, 1500))
    # the map panel: freeze
    t0 = cut("v_map")
    fx.add(O.stamp(1.0), t0 + 0.05, 0.9, 0.5)
    for k in range(3):
        fx.add(O.page(0.6, seed=20 + k), Wx("v4", "three") + 0.25 * k, 0.6, 0.7)
    mus.add(O.music_box([(m + 12, b) for m, b in MOTIF], amp=1.0), Wx("v4", "worse"), 0.5, 0.4, until=cut("v_signal"))
    # SILENCE ... then the signal goes
    t0 = T_SIGNAL
    fx.add(Y.error_tone(1.0), t0 - 0.02, 1.2, 0.5)
    stinger(mus, fx, t0 - 0.02, "red", 0.7)
    fx.add(O.heartbeat(4, 100, 1.0), t0 + 0.4, 0.8)
    t0, t1 = cut("v_cross"), cut("v_cabbie")
    fx.add(Y.wind(t1 - t0 + 0.8, 1.2, seed=4), t0 - 0.6, 1.0)
    fx.add(Y.footsteps(3, 0.38, 1.0, seed=6), t0 + 0.05, 0.7, 0.4)                # Vera's heels on the wet road
    fx.add(Y.skitter(t1 - t0, 0.6, seed=4, rate=12), t0, 0.4, 0.8)
    mus.add(O.drone(t1 - t0 + 1.0, root=26, amp=1.0), t0 - 0.8, 1.0, until=t1)
    mus.add(I.choir([61, 62, 68], t1 - t0, 1.0, vowel="u", attack=0.5), t0, 0.7, until=t1)
    # the cabbies: a warmer turn - use it and it grows
    t0, t1 = cut("v_cabbie"), cut("v_bones")
    page_turn(fx, t0)
    pads(mus, t0 + 0.1, t1, 0.8, prog=[[50, 57, 62, 66], [47, 54, 59, 62], [43, 55, 59, 62], [45, 52, 57, 61]], bars=0.9, cut_=(700, 2600))
    arp(mus, t0 + 0.2, t1, 0.6, prog=[[50, 57, 62, 66], [47, 54, 59, 62], [43, 55, 59, 62], [45, 52, 57, 61]], bars=0.9, pattern=(0, 1, 2, 3))
    fx.add(FXL.rain(Wx("v7", "grow") - t0, 0.5, seed=9), t0, 0.6, until=Wx("v7", "grow"))
    mus.add(I.choir([66, 69, 74], 1.4, 1.0, vowel="a", attack=0.2), Wx("v7", "grow"), 0.7, until=t1)
    mus.add(O.sparkle(1.0, seed=3), Wx("v7", "grows"), 0.8)
    # fifteen years on
    t0, t1 = cut("v_bones"), cut("g_title")
    fx.add(Y.wind(t1 - t0 + 0.5, 1.0, seed=5), t0, 0.9)
    fx.add(Y.skitter(t1 - t0, 1.0, seed=5, rate=25), t0, 0.5, 0.7)
    fx.add(Y.creak(1.4, 1.0, seed=3, f0=70, f1=30), t0 + 0.6, 0.8, 0.3)
    fx.add(Y.creak(1.1, 1.0, seed=4, f0=60, f1=35), Wx("v8", "Recalculating") - 0.4, 0.7, 0.7)
    mus.add(O.drone(t1 - t0, root=26, amp=1.0), t0, 1.0, until=t1)
    mus.add(I.choir([62, 63, 69], Wx("v8", "forever") - t0, 1.0, vowel="o", attack=1.5), t0, 0.8, until=Wx("v8", "forever"))
    for k in range(6):
        fx.add(Y.beep(1100, 0.06), t0 + 0.3 + k * 0.8, 0.35, 0.5)
    # ---------------- tale two
    t0, t1 = cut("g_title"), cut("g_dorm")
    page_turn(fx, t0)
    mus.add(O.theremin(500, 900, S("g1") - t0, 1.0), t0 + 0.05, 0.7, until=S("g1") + 0.1)
    mus.add(O.theremin(600, 1000, t1 - E("g1"), 1.0), E("g1") + 0.05, 0.6, until=t1 + 0.2)
    mus.add(Y.stab([49, 56, 61, 64], 1.0, 1.0), E("g1") + 0.02, 0.8)
    pads(mus, t0, t1, 0.7, prog=[GM, AA], bars=0.6)
    # the dorm: 2 a.m.
    t0, t1 = cut("g_dorm"), cut("g_exam")
    fx.add(FXL.room_tone(t1 - t0, 1.0, hum=True), t0, 1.0)
    for k in range(int((cut("g_split") - t0) / 0.5)):
        fx.add(O.tick(0.5, tock=k % 2 == 1), t0 + k * 0.5, 0.5, 0.2)
    fx.add(O.keys(10, 0.09, 1.0, seed=4), S("g2") + 0.3, 1.0, 0.5)
    pulse(mus, t0, cut("g_split"), 0.7, prog=[GM, GM, AA, DM])
    motif(mus, t0 + 0.2, cut("g_split"), 0.6, transpose=-7, inst="piano")
    fx.add(O.reverse_swell(1.0, 1.0), cut("g_ghost") - 0.9, 0.8, 0.6)
    fx.add(FXL.paper_flutter(2.0, 1.0), cut("g_ghost") + 0.2, 0.9, 0.7)
    fx.add(O.keys(30, 0.06, 1.0, seed=5), cut("g_ghost") + 0.6, 0.9, 0.6, until=cut("g_split"))
    mus.add(O.theremin(600, 1100, cut("g_split") - cut("g_ghost"), 1.0), cut("g_ghost") + 0.2, 0.6, until=cut("g_split"))
    mus.add(Y.stab([62, 66, 69], 1.0, 0.5), Wx("g3", "Nine") - 0.05, 0.8)
    # help vs write
    mus.add(Y.stab([62, 66, 69, 74], 1.0, 1.0, bright=6000), Wx("g3", "Help") - 0.1, 0.9)
    mus.add(I.choir([66, 69, 74], 1.6, 1.0, vowel="a", attack=0.2), Wx("g3", "Help"), 0.6, until=Wx("g3", "Write"))
    mus.add(Y.stab([49, 50, 56], 1.0, 1.0, bright=1800), Wx("g3", "Write") - 0.1, 1.0)
    mus.add(O.drone(1.6, root=26), Wx("g3", "Write"), 0.8, until=cut("g_quote"))
    # the words crawl away
    t0, t1 = cut("g_quote"), cut("g_chart")
    pads(mus, t0, t1, 0.7, prog=[GM, DM, AA, DM], bars=0.8, cut_=(400, 1400))
    mus.add(O.music_box([(m + 5, b) for m, b in MOTIF], amp=1.0, detune=lambda u: -40 * u), t0 + 0.3, 0.5, 0.4, until=t1)
    fx.add(Y.skitter(t1 - Wx("g4", "couldn't") + 1.6, 1.3, seed=6, rate=60), Wx("g4", "couldn't") - 1.6, 0.9, 0.5, until=t1)
    mus.add(Y.stab([50, 53, 56], 1.0, 0.8), Wx("g4", "83%") - 0.05, 1.0)
    # the chart: up, then down into the grave
    t0, t1 = cut("g_chart"), cut("g_exam")
    page_turn(fx, t0)
    pulse(mus, t0 + 0.1, Wx("g5", "Take") - 0.1, 0.8, prog=[GM, AA])
    fx.add(Y.riser(Wx("g5", "lifted") + 0.4 - (t0 + 0.6), 0.8, f0=300, f1=2400), t0 + 0.6, 0.8)
    mus.add(Y.stab([62, 66, 69, 74], 1.0, 0.8, bright=6000), Wx("g5", "lifted") + 0.3, 0.9)
    mus.add(I.choir([74, 70, 66, 62], 1.8, 1.0, vowel="o", gliss=-7), Wx("g5", "Take") - 0.1, 0.8)
    mus.add(O.timpani(38, 1.0), Wx("g5", "17%") + 0.15, 1.2)
    fx.add(Y.earth(1.0), Wx("g5", "17%") + 0.2, 1.1)
    mus.add(O.drone(t1 - Wx("g5", "17%"), root=26), Wx("g5", "17%"), 0.8, until=t1)
    # the exam: silence but for the clock
    t0, t1 = T_EXAM, cut("g_blank")
    fx.add(FXL.room_tone(t1 - t0, 0.6, hum=False), t0, 1.0)
    for k in range(int((t1 - t0) / 0.5) + 1):
        fx.add(O.tick(1.0, tock=k % 2 == 1), t0 + 0.05 + k * 0.5, 0.9, 0.7)
    fx.add(Y.footsteps(4, 0.42, 1.0, seed=3), t0 + 0.08, 1.0, 0.62)          # the examiner's heels in the silence
    mus.add(Y.pad([43, 50, 55], t1 - S("g6"), 1.0, cut=(200, 700), attack=1.0), S("g6"), 0.6, until=t1)
    # blank
    t0, t1 = cut("g_blank"), cut("g_puppet")
    fx.add(O.heartbeat(5, 140, 1.0), t0 + 0.1, 1.0)
    mus.add(O.strings([86, 87, 93], t1 - t0, 1.0), t0, 0.8, until=t1)
    # the puppet
    t0, t1 = cut("g_puppet"), cut("s_title")
    mus.add(O.music_box([(m, b) for m, b in MOTIF], rate=lambda u: 1 - 0.55 * u, detune=lambda u: -90 * u, amp=1.0), t0 + 0.2, 0.7, 0.5,
            until=t1)
    mus.add(O.drone(t1 - t0, root=26), t0, 0.7, until=t1)
    fx.add(FXL.paper_flutter(1.4, 1.0, seed=3), t0, 0.8, 0.5)
    for k in range(5):
        fx.add(Y.creak(0.5, 0.8, seed=10 + k, f0=110, f1=70), t0 + 1.4 + k * 0.62, 0.4, 0.3 + 0.1 * k)
    mus.add(I.choir([62, 65, 69, 74], 1.4, 1.0, vowel="a", attack=0.2), Wx("g8", "Now") - 0.05, 0.6, until=t1)
    # ---------------- tale three
    t0, t1 = cut("s_title"), cut("s_clinic")
    page_turn(fx, t0)
    mus.add(Y.stab([47, 54, 59, 62], 1.0, 1.0), S("s1") + 0.4, 0.8)
    mus.add(I.choir([59, 62, 66], t1 - t0, 1.0, vowel="u", attack=0.4), t0 + 0.2, 0.8, until=t1 + 0.2)
    motif(mus, S("s1") - 0.1, t1, 0.7, transpose=-3, inst="piano")
    # the clinic
    t0, t1 = cut("s_clinic"), cut("s_shout")
    fx.add(Y.monitor(cut("s_unplug") - t0, 72, 1.0), t0, 0.5, 0.65)
    fx.add(Y.engine(cut("s_unplug") - t0, 0.4, seed=3), t0, 0.4)
    pulse(mus, t0, t1, 0.75, prog=[BB, BB, AA, AA])
    pads(mus, t0, t1, 0.7, prog=[BB, AA, DM, AA], bars=0.8)
    fx.add(O.stamp(1.0), Wx("s2", "22%") + 0.5, 1.2, 0.6)
    fx.add(Y.thud(1.0), Wx("s2", "22%") + 0.5, 0.6)
    t_pull = Wx("s2", "without") - 0.05
    fx.add(O.click(1.0), t_pull, 1.2, 0.8)
    fx.add(O.power_down(1.0, 1.0), t_pull + 0.02, 0.8, 0.7)
    fx.add(Y.beep(1040, 1.2), t_pull + 0.4, 0.25, 0.65)
    mus.add(Y.stab([45, 51, 56], 1.0, 1.0, bright=2000), Wx("s2", "22%") - 0.05, 1.0)
    mus.add(O.timpani(33, 1.0), Wx("s2", "22%") - 0.05, 0.9)
    mus.add(Y.stab([46, 53, 58], 1.0, 0.7), Wx("s2", "28%") - 0.05, 0.8)
    # show me!
    t0, t1 = cut("s_shout"), cut("s_pilot")
    for k in range(int((t1 - t0) / (np.pi / 9)) + 1):
        tb = t0 + (np.pi / 18) + k * np.pi / 9
        fx.add(O.clunk(1.0, seed=k), tb, 0.9, 0.7)
    # the cockpit
    t0, t1 = cut("s_pilot"), cut("s_years")
    page_turn(fx, t0)
    fx.add(Y.engine(t1 - t0, 1.0, seed=5), t0, 0.8)
    fx.add(FXL.rain(t1 - t0, 0.9, seed=11), t0, 0.7)
    pads(mus, t0, Wx("s5", "quit"), 0.7, prog=[GM, AA], bars=1.0, cut_=(300, 900))
    motif(mus, t0 + 0.3, Wx("s5", "quit") - 0.1, 0.5, transpose=-12, inst="box")
    fx.add(Y.whoop(t1 - Wx("s5", "quit"), 1.0), Wx("s5", "quit") + 0.1, 0.9, 0.5, until=t1)
    fx.add(Y.alarm(t1 - Wx("s5", "quit"), 1.0, rate=5), Wx("s5", "quit") + 0.3, 0.5, 0.6, until=t1)
    mus.add(O.scare(1.0, seed=8), Wx("s5", "quit") - 0.05, 1.0)
    mus.add(O.drone(t1 - Wx("s5", "quit"), root=27), Wx("s5", "quit"), 0.9, until=t1)
    fx.add(O.heartbeat(5, 120, 1.0), Wx("s5", "when"), 0.8)
    # twenty years later
    t0, t1 = cut("s_years"), cut("s_junior")
    page_turn(fx, t0)
    fx.add(Y.monitor(t1 - t0, 58, 1.0, f=880), t0 + 0.2, 0.5, 0.65)
    mus.add(O.music_box([(m - 2, b) for m, b in MOTIF], amp=1.0, detune=lambda u: -30 * u), t0 + 0.3, 0.6, 0.4, until=cut("s_ward"))
    pads(mus, t0, t1, 0.6, prog=[GM, DM], bars=1.0, cut_=(300, 1000))
    fx.add(Y.buzz(t1 - Wx("s6", "without") + 0.1, 1.0), Wx("s6", "without") - 0.1, 0.8, 0.4)
    fx.add(O.power_down(1.0, 1.0), Wx("s6", "without") + 0.3, 0.6, 0.7)
    # I can't see anything ... (silence) ... the thing
    t0, t1 = cut("s_junior"), T_PRE
    fx.add(Y.alarm(t1 - t0, 1.0, rate=6, f=1300), t0, 0.6, 0.6, until=t1)
    mus.add(O.drone(t1 - t0, root=27), t0, 1.0, until=t1)
    mus.add(Y.riser(t1 - t0, 1.0, f0=200, f1=2600), t0, 1.0, until=t1)
    t0, t1 = T_THING, T_BLACK
    stinger(mus, fx, t0, "red", 1.4)
    fx.add(Y.crack(1.0, seed=1), t0 + 0.02, 1.6, 0.5)
    fx.add(O.thunder(2.2, 1.0, seed=9), t0, 1.4, until=t1)
    fx.add(O.growl(t1 - t0, 1.0), t0 + 0.15, 1.6, until=t1)
    fx.add(I.smash(1.0, seed=3), t0 + 0.38, 1.4, 0.4)
    fx.add(O.squelch(1.0, seed=4, dur=0.5), t0 + 0.75, 1.5, 0.6)
    fx.add(I.splat(1.0, seed=5), t0 + 1.3, 1.6, 0.4)
    fx.add(O.squelch(1.0, seed=6, dur=0.6), t0 + 1.35, 1.5, 0.6)
    mus.add(I.choir([74, 75, 80, 81], t1 - t0, 1.0, vowel="a", attack=0.05), t0 + 0.1, 1.2, until=t1)
    mus.add(O.scare(1.0, seed=12, drive=2.0), t0 + 1.3, 1.4, until=t1)
    mus.add(Y.pad([38, 39, 44, 50, 51], t1 - t0, 1.0, cut=(800, 4000), attack=0.05), t0, 1.4, until=t1)
    # ---------------- the reader: no music to speak of. Just the night.
    t0 = S("r1") - 0.1
    fx.add(Y.low_batt(1.0), t0, 1.1, 0.5)
    fx.add(Y.low_batt(1.0), t0 + 0.9, 0.9, 0.5)
    t_die = Wx("r1", "Nora") + 0.35
    fx.add(O.power_down(0.6, 1.0), t_die, 0.6, 0.5)
    r_end = T_STILL + 0.02
    fx.add(FXL.rain(r_end - t_die + 0.5, 0.45, seed=12), t_die, 0.6)
    mus.add(O.drone(r_end - t_die, root=24), t_die + 0.2, 0.5, until=r_end)
    fx.add(Y.match(1.0), cut("r_real") + 0.1, 1.1, 0.6)
    fx.add(I.crackle(r_end - cut("r_real") - 0.5, 0.5), cut("r_real") + 0.6, 0.35, 0.6)
    fx.add(O.heartbeat(int((r_end - S("r2")) / 0.75), 80, 1.0), S("r2"), 0.6, until=cut("r_still") + 0.3)
    fx.add(Y.breath(cut("r_pill") - cut("r_father"), 1.0, rate=1.4), cut("r_father"), 0.9, 0.5)
    t_dead = cut("r_still") + 0.15
    fx.add(Y.breath(t_dead - cut("r_muse") + 0.1, 1.0, rate=1.9, seed=4), cut("r_muse"), 1.1, 0.42, until=t_dead)    # gasping, then not
    fx.add(Y.thud(1.0, f=110), cut("r_still") + 0.36, 0.45, 0.35)                                 # the bottle hits the floor
    fx.add(Y.rattle(0.2, 1.0, seed=3, rate=34), cut("r_still") + 0.36, 0.8, 0.3)                  # tablets skittering
    for k in range(int((cut("r_door") - cut("r_father")) / 0.4)):
        fx.add(Y.tick(1.0), cut("r_father") + 0.1 + k * 0.4, 0.6, 0.8)
    fx.add(Y.rattle(cut("r_call") - cut("r_pill"), 1.0, rate=9), cut("r_pill"), 0.8, 0.4, until=cut("r_call"))
    fx.add(Y.footsteps(2, 0.45, 1.0, seed=9, hard=False), cut("r_door") - 0.05, 0.9, 0.5)
    fx.add(Y.creak(1.4, 1.0, seed=7, f0=50, f1=25), cut("r_door") + 0.35, 1.0, 0.4)
    fx.add(FXL.rain(cut("r_number") - cut("r_door"), 1.2, seed=13), cut("r_door") + 0.3, 1.0, until=cut("r_number"))
    fx.add(Y.wind(cut("r_number") - cut("r_door") + 0.5, 1.0, seed=8), cut("r_door"), 0.7, until=cut("r_number") + 0.3)
    for k, d in enumerate("999"):                                                              # 999, fast, panicking
        fx.add(Y.dtmf(d, 0.12), cut("r_call") + 0.05 + 0.17 * k, 1.0, 0.6)
    fx.add(ringback(0.9), cut("r_call") + 0.6, 0.6, 0.6, until=Wx("r3", "Forty") - 0.1)            # the ring, then answered
    for k, d in enumerate("07"):                                                               # her sister: 0, 7 ... nothing
        fx.add(Y.dtmf(d), cut("r_number") + 0.25 + 0.35 * k, 1.0, 0.6)
    fx.add(Y.dial_tone(cut("r_muse") - cut("r_number") - 1.4), cut("r_number") + 1.4, 0.5, 0.5, until=cut("r_muse"))
    # the host in the glass, the turn on the reader
    t0, t1 = cut("r_pocket"), cut("m_close")
    fx.add(O.reverse_swell(1.4, 1.0), t0 + 0.1, 0.8)
    mus.add(O.drone(t1 - t0, root=25), t0, 0.9, until=t1)
    mus.add(I.choir([61, 62, 67], cut("r_point") - t0, 1.0, vowel="u", attack=0.8), t0 + 0.2, 0.8, until=cut("r_point") + 0.2)
    stinger(mus, fx, cut("r_point"), "green", 0.9)
    mus.add(Y.pad([37, 44, 49, 50], t1 - cut("r_point"), 1.0, cut=(400, 2400), attack=0.1), cut("r_point"), 0.9, until=t1)
    # ---------------- the moral: the music box alone, then gently hopeful
    t0, t1 = cut("m_close"), cut("m_host")
    mus.add(O.music_box([(m, b) for m, b in MOTIF] * 2, amp=1.0, rate=lambda u: 0.75), t0 + 0.4, 0.9, 0.5, until=cut("m_habits"))
    pads(mus, t0 + 0.5, cut("m_habits"), 0.45, prog=[DM, BB, GM, AA], bars=1.0, cut_=(300, 900))
    fx.add(I.crackle(cut("m_habits") - t0, 0.4), t0, 0.3, 0.3)
    page_turn(fx, cut("m_habits"))
    hope = [[50, 57, 62, 66], [46, 53, 58, 62], [43, 55, 59, 62], [45, 52, 57, 61]]
    pads(mus, cut("m_habits"), t1, 0.6, prog=hope, bars=0.75, cut_=(600, 2200))
    arp(mus, cut("m_habits") + 0.1, t1, 0.5, prog=hope, bars=0.75, pattern=(0, 2, 1, 3), pan=0.55)
    for w in ("explain", "Draft", "Find", "sum"):
        mus.add(O.celesta(86 if w != "sum" else 90, 1.0), Wx("m2", w) - 0.1, 0.5, 0.6)
    # ---------------- the host's last word
    t0, t1 = cut("m_host"), cut("m_back")
    stinger(mus, fx, t0, "violet", 1.0)
    mus.add(O.organ([50, 57, 62, 65, 69], t1 - t0), t0 + 0.1, 0.9, until=t1 + 0.2)
    mus.add(I.choir([62, 65, 69, 74], t1 - t0, 1.0, vowel="a", attack=0.1), t0 + 0.2, 0.8, until=t1 + 0.2)
    # ---------------- the back page: a cheesy mail-order organ jingle
    t0, t1 = cut("m_back"), TL.total
    page_turn(fx, t0)
    jb = 60 / 132
    prog = [[48, 52, 55, 60], [45, 48, 52, 57], [41, 45, 48, 53], [43, 47, 50, 55]]
    t, k = t0 + 0.3, 0
    tune = [72, 76, 79, 76, 77, 76, 74, 72, 69, 72, 74, 76, 74, 72, 71, 67]
    while t < t1 - 1.6:
        ch = prog[(k // 4) % 4]
        mus.add(O.organ(ch[1:], jb * 0.5), t, 0.5, 0.45, until=t1 - 1.5)
        mus.add(Y.bass(ch[0] - 12, jb * 0.5), t, 0.6, 0.5, until=t1 - 1.5)
        mus.add(O.glock(tune[k % len(tune)], 1.0), t, 0.5, 0.6, until=t1 - 1.5)
        t += jb
        k += 1
    fx.add(O.thunder(2.4, 1.0, seed=31), S("m4b") + 0.6, 1.0)
    t_end = E("m5") + 0.3
    mus.add(Y.stab([50, 57, 62, 65, 69], 1.0, 1.4), t_end, 1.0)
    fx.add(O.thunder(2.0, 1.0, seed=14), t_end, 0.9, until=t1)
    # ---------------- the live action freezing into a comic panel before each page turn: a snap and a hit
    for i, e in enumerate(EDIT):
        if i > 0 and e[2] == "page" and EDIT[i - 1][1] not in PAGES:
            tf = e[0] - FREEZE_D
            fx.add(O.click(1.0), tf, 0.9, 0.5)
            mus.add(Y.stab([50, 57, 62], 1.0, 0.5, bright=3000), tf, 0.5)
    # ---------------- thunder on the lightning, and the stingers on the colour shocks
    for t, s in LIGHTNING:
        if t < 0.1 or abs(t - T_THING) < 0.5:
            fx.add(O.thunder(2.6, 1.0, seed=int(t * 7)), max(0.0, t), 1.0 * s, until=None)
        else:
            fx.add(O.thunder(2.6, 1.0, seed=int(t * 7)), t, 0.9 * s)
    for t, col in SHOCKS:
        if abs(t - T_THING) < 0.5 or abs(t - cut("m_host")) < 0.3:
            continue
        stinger(mus, fx, t, col, 0.9)


def host_room(x):
    """The host: a theatrical hall, long and dark."""
    return reverb(x, 0.18, 1.2, seed=11)


def phone_voice(x):
    """The assistant: a small speaker - band-limited, a glassy shimmer, slightly doubled."""
    t = np.arange(len(x)) / SR
    y = signal.sosfilt(signal.butter(4, [320 / (SR / 2), 5200 / (SR / 2)], "band", output="sos"), x)
    d = int(0.011 * SR)
    y2 = np.zeros_like(y)
    y2[d:] = y[:-d]
    return y * 0.85 + y2 * 0.3 * (1 + 0.2 * np.sin(2 * np.pi * 0.7 * t))


def reverb(x, wet=0.1, rt60=0.8, seed=8):
    rng = np.random.default_rng(seed)
    t = np.arange(int(rt60 * 1.4 * SR)) / SR
    ir = np.stack([rng.normal(0, 1, len(t)) * np.exp(-6.9 * t / rt60) for _ in range(2)])
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    y = np.stack([signal.fftconvolve(x[c], ir[c])[: x.shape[1]] for c in range(2)])
    return x * (1 - wet) + y * wet


PANS = {"NORA": 0.48, "VERA": 0.42, "KIT": 0.5, "PROF": 0.6, "HALE": 0.44, "JUNIOR": 0.42, "MUSE": 0.58}


def voices():
    """The narrator close and dry; the host in her echoing hall; the cast with a little room; the assistant in a box."""
    dry, room, hall = np.zeros((2, N_)), np.zeros((2, N_)), np.zeros((2, N_))
    for key in TL.order:
        Ln = TL.lines[key]
        who = Ln["who"]
        up = signal.resample_poly(Ln["wav"].astype(np.float64), SR, VSR)
        if who == "MUSE":
            up = phone_voice(up)
        r = np.sqrt((up ** 2).mean()) + 1e-12
        up = up * db({"NAR": -16.0, "HOST": -15.5, "MUSE": -16.5}.get(who, -16.0)) / r
        pan = PANS.get(who, 0.5)
        sig = np.stack([up * np.sqrt(1 - pan), up * np.sqrt(pan)]) * np.sqrt(2)
        i = int(Ln["start"] * SR)
        j = min(N_, i + sig.shape[1])
        tgt = dry if who == "NAR" else (hall if who == "HOST" else room)
        tgt[:, i:j] += sig[:, : j - i]
    # a last echo of the cackle as the comic closes
    L4 = TL.lines["m4b"]
    cack = signal.resample_poly(L4["wav"].astype(np.float64), SR, VSR)
    cack = cack * db(-22.0) / (np.sqrt((cack ** 2).mean()) + 1e-12)
    i = int((E("m5") + 0.9) * SR)
    j = min(N_, i + len(cack))
    hall[:, i:j] += np.stack([cack, cack])[:, : j - i]
    return dry + reverb(room, 0.12, 0.5, seed=5) + host_room(hall)


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
CEIL = -3.0
RELIEF_DB, FX_DB = 14.0, -23.0
NEED = {"NAR": 10.0, "HOST": 12.0}                 # the voice's margin over the bed in the speech band (the cast: 15)


def buses():
    path = os.path.join(HERE, "build", "buses.npz")
    if os.environ.get("CS_CACHE") == "load" and os.path.exists(path):
        d = np.load(path)
        return d["mus"].astype(np.float64), d["fx"].astype(np.float64), d["ns"].astype(np.float64)
    mus, fx, nosil = Bus(), Bus(), Bus()
    score(mus, fx, nosil)
    if os.environ.get("CS_CACHE"):
        np.savez(path, mus=mus.x.astype(np.float32), fx=fx.x.astype(np.float32), ns=nosil.x.astype(np.float32))
    return mus.x, fx.x, nosil.x


def build():
    mus_x, fx_x, ns_x = buses()
    music = mono_safe(reverb(mus_x, 0.2, 1.4), max_ratio=1.0)
    music = signal.sosfilt(signal.butter(4, 32 / (SR / 2), "high", output="sos"), music, axis=1)
    music = np.tanh(1.1 * music) / 1.1
    fxx = reverb(fx_x, 0.1, 0.6, seed=3)
    fxx = signal.sosfilt(signal.butter(4, 35 / (SR / 2), "high", output="sos"), fxx, axis=1)
    vo = compress(presence(voices(), 3000, 2.5))
    # levels: the music where it plays for itself (the host's welcome), the collage under it
    ref = music[:, int(cut("o_host") * SR):int(end("o_host") * SR)]
    music = music * db(-15.0) / (np.sqrt((ref ** 2).mean()) + 1e-12)
    on = np.abs(fxx).max(axis=0) > 1e-4
    fxx = fxx * db(FX_DB) / (np.sqrt((fxx[:, on] ** 2).mean()) + 1e-12)
    music_pre, fx_pre = music.copy(), fxx.copy()
    from scipy.ndimage import maximum_filter1d
    raw = np.convolve(np.abs(vo.mean(axis=0)), np.ones(SR // 20) / (SR // 20), mode="same")
    raw = np.clip(raw / (np.percentile(raw[raw > 1e-5], 80) + 1e-9), 0, 1)
    env = smooth(maximum_filter1d(raw, size=int(0.8 * SR), origin=-int(0.15 * SR)), 0.2)
    low = signal.lfilter(*signal.butter(2, 250 / (SR / 2), "low"), music)
    high = signal.lfilter(*signal.butter(2, 4500 / (SR / 2), "high"), music)
    mid = music - low - high
    music = low * (1 - 0.3 * env) + mid * (1 - 0.6 * env) + high * (1 - 0.35 * env)
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
            rf[lo:hi] = np.minimum(rf[lo:hi], db(0.85 * gain[key]))
        r, rf = smooth(r, 0.15), smooth(rf, 0.15)
        r = r * act + np.minimum(1.0, r * db(RELIEF_DB)) * (1 - act)
        rf = rf * act + np.minimum(1.0, rf * db(RELIEF_DB)) * (1 - act)
        return r, rf

    for _ in range(8):
        ride, ride_fx = rides()
        bb = bmus * ride + bfx * ride_fx
        short = False
        for key in TL.order:
            a, b = spans[key]
            margin = 20 * np.log10((np.sqrt((bv[a:b] ** 2).mean()) + 1e-12) / (np.sqrt((bb[a:b] ** 2).mean()) + 1e-12))
            need = NEED.get(TL.lines[key]["who"], 15.0)
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
    lo_ = signal.lfilter(*signal.butter(2, 250 / (SR / 2), "low"), music)
    hi_ = signal.lfilter(*signal.butter(2, 4500 / (SR / 2), "high"), music)
    music = (music - lo_ - hi_) * ride[None] + (lo_ + hi_) * np.sqrt(ride)[None]
    # the climax: the loudest moment in the film
    boost = np.ones(N_)
    boost[int(T_THING * SR):int(T_BLACK * SR)] = db(4.0)
    boost = smooth(boost, 0.01)
    trim, trim_fx = np.ones(N_), np.ones(N_)
    for a, b in ((cut("r_real"), T_STILL), (cut("m_close"), cut("m_habits"))):
        trim[int(a * SR):int(b * SR)] = db(-5.0)
        trim_fx[int(a * SR):int(b * SR)] = db(-4.0)
    trim, trim_fx = smooth(trim, 0.3), smooth(trim_fx, 0.3)
    music = music * dead[None] * boost[None] * trim[None]
    fxx = fxx * ride_fx[None] * dead[None] * boost[None] * trim_fx[None]
    ns = ns_x * db(-24.0) / (np.abs(ns_x).max() + 1e-12) if np.abs(ns_x).max() > 0 else ns_x
    rng = np.random.default_rng(21)
    hiss = signal.sosfilt(signal.butter(2, [400 / (SR / 2), 6000 / (SR / 2)], "band", output="sos"), rng.normal(0, 1, N_))
    hiss = hiss * db(-62.0) * (1 - dead)
    mix = (music + fxx + vo + ns) * dead[None] + np.stack([hiss, hiss])
    mix = macro(mix)
    report(music_pre, fx_pre, music, fxx, vo)
    mix = signal.sosfilt(signal.butter(4, 30 / (SR / 2), "high", output="sos"), mix, axis=1)
    mix = signal.sosfilt(signal.butter(2, 15000 / (SR / 2), "low", output="sos"), mix, axis=1)
    mix = crush_climax(mix)
    mix = loudness(mix, -14.0)
    mix = post_macro(mix, margin=5.0)
    a_, b_ = int((TL.total - 0.4) * SR), int(TL.total * SR)
    mix[:, a_:b_] *= np.linspace(1, 0, b_ - a_) ** 2
    mix[:, b_:] = 0.0
    STEMS.update(music=music, fx=fxx, vo=vo)
    return mix


def momentary(x, win=0.4, hop=0.05):
    """A K-weighting-ish momentary loudness (dB) every hop seconds."""
    y = signal.sosfilt(signal.butter(2, 100 / (SR / 2), "high", output="sos"), x.mean(axis=0))
    y = y + signal.sosfilt(signal.butter(2, 2000 / (SR / 2), "high", output="sos"), y) * 0.6
    w, h = int(win * SR), int(hop * SR)
    p = np.convolve(y ** 2, np.ones(w) / w, "same")[::h]
    return 10 * np.log10(p + 1e-12), h


def macro(mix, under=6.0):
    """Keep the climax the loudest moment by a clear margin: anywhere else whose momentary loudness comes within
    `under` dB of the climax's peak is ridden down (smoothly) before the loudness normalisation and the limiter."""
    m, h = momentary(mix)
    a, b = int(T_THING * SR / h), int(T_BLACK * SR / h)
    peak = m[a:b].max()
    g = np.minimum(0.0, (peak - under) - m)
    g[a:b] = 0.0
    from scipy.ndimage import minimum_filter1d
    g = minimum_filter1d(g, size=9)
    g = np.convolve(g, np.ones(7) / 7, "same")
    gain = np.interp(np.arange(mix.shape[1]), np.arange(len(g)) * h, 10 ** (g / 20))
    print(f"macro: climax peak {peak:.1f} dB; frames ridden: {(g < -0.5).sum()} of {len(g)}")
    return mix * gain[None]


def crush_climax(mix, drive=2.0):
    """The thing bursting out of the screen: saturate it hard so it is dense and loud under the same peak ceiling."""
    w = np.zeros(mix.shape[1])
    a, b = int(T_THING * SR), int(T_BLACK * SR)
    w[a:b] = 1.0
    w = smooth(w, 0.02)
    sat = np.tanh(drive * mix / (np.abs(mix[:, a:b]).max() + 1e-9)) * np.abs(mix[:, a:b]).max()
    return mix * (1 - w)[None] + sat * w[None]


def post_macro(mix, margin=3.5):
    """After the limiter: anywhere outside the climax whose momentary loudness is within `margin` dB of the climax's
    loudest moment is ridden down, so the climax is plainly the loudest thing in the film."""
    m, h = momentary(mix)
    a, b = int(T_THING * SR / h), int(T_BLACK * SR / h)
    peak = m[a:b].max()
    g = np.minimum(0.0, (peak - margin) - m)
    g[a:b] = 0.0
    from scipy.ndimage import minimum_filter1d
    g = minimum_filter1d(g, size=11)
    g = np.convolve(g, np.ones(9) / 9, "same")
    gain = np.interp(np.arange(mix.shape[1]), np.arange(len(g)) * h, 10 ** (g / 20))
    print(f"post-macro: climax {peak:.1f} dB; frames ridden {(g < -0.3).sum()} of {len(g)}, deepest {g.min():.1f} dB")
    return mix * gain[None]


def report(music_pre, fx_pre, music, fxx, vo):
    band = lambda x: signal.sosfilt(signal.butter(2, [300 / (SR / 2), 4000 / (SR / 2)], "band", output="sos"), x.mean(axis=0))
    bb, bv = band(music + fxx), band(vo)
    rms = lambda y: 20 * np.log10(np.sqrt((y ** 2).mean()) + 1e-9)
    low = []
    for key in TL.order:
        Ln = TL.lines[key]
        a, b = int(Ln["start"] * SR), int(Ln["end"] * SR)
        mg = rms(bv[a:b]) - rms(bb[a:b])
        if mg < NEED.get(Ln["who"], 15.0) - 1.0:
            low.append(f"{key} {mg:.1f}")
    print("lines under the margin:", ", ".join(low) or "none")
    rows = []
    for i, e in enumerate(EDIT):
        a, b = int(e[0] * SR), int((EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total) * SR)
        rows.append(f"{e[1]:>14s} pre: mus {rms(music_pre[:, a:b]):6.1f} fx {rms(fx_pre[:, a:b]):6.1f} | mix: mus {rms(music[:, a:b]):6.1f} "
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


def aac_safe(x, target=-2.2, rates=("192k", "256k"), rounds=3):
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
