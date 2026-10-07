"""INELIGIBLE - the soundtrack. All original, all synthesized.

Score: a slow, crushing doom/drone score - downtuned distorted guitar chords in D Phrygian, a sub-bass you feel more
than hear, feedback squeals - under swelling 1980s analog synth pads and an arpeggiator. A fragile melody on a solo
female voice (A-F-E-D-C-A-Bb-A) opens the film pure and keeps coming back corrupted: wavering on warped tape,
bit-crushed, reversed, played wrong on glass bells, out of tune on a music box, and finally snapping off. Long
stretches are near-silent: wind, fire, one sustained tone.

Sound: wind in the pines, a crackling fire of paper, the hum of a fluorescent tube, whispered chanting under her voice,
heartbeats and breath, heavy metallic impacts (stamps, doors, armour), distant engines roaring past, feedback, deep
rumbles. Three hard cuts to dead silence: before the mask, before the system answers Iris, and before the eye opens.

Voices: the narrator close and hushed; Merit in a vast dark hall, her voice already slowed, deepened and layered; the
system dry and flat down a line; Iris in a small hard kitchen; the "why?" chorus wide and whispering.
"""
import math
import os
import wave

import numpy as np
from scipy import signal

import doom as DM
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
                f = min(m, int(0.03 * SR))
                sig[:, m - f:] *= np.linspace(1, 0, f)
        i = int(round(t * SR))
        if i >= N_ or i + sig.shape[1] <= 0:
            return
        if i < 0:
            sig, i = sig[:, -i:], 0
        j = min(N_, i + sig.shape[1])
        self.x[:, i:j] += gain * sig[:, : j - i]


def tone(m, dur, amp=1.0):
    """A long sustained sine, very quiet, very high: the sound of a room holding its breath."""
    t = np.arange(int(dur * SR)) / SR
    x = np.sin(2 * np.pi * O.midi(m) * t) * (1 + 0.002 * np.sin(2 * np.pi * 0.3 * t))
    return amp * 0.12 * x * np.clip(t / 1.5, 0, 1) * np.clip((dur - t) / 1.5, 0, 1)


def card_hit(mus, fx, t, root, seed=0, gong=1.0):
    """A chapter card: one crushing chord, its sub, a struck iron plate ringing like a gong."""
    fx.add(DM.reverse_cymbal(0.7, 0.6, seed=seed), t - 0.7)
    mus.add(DM.chord(root, 1.6, 1.0, seed=seed), t, until=t + 1.9)
    mus.add(DM.sub(root - 12, 1.6, 0.9, att=0.01, rel=0.5), t)
    fx.add(DM.metal_hit(0.9 * gong, seed=seed, size=1.7), t)
    fx.add(DM.boom(0.7), t)


def theme_at(mus, t, x, gain=1.0, pan=0.5, until=None):
    mus.add(x, t, gain, pan=pan, until=until)


# ------------------------------------------------------------------ the dead silences and the hits

T_HIT = 0.55                                    # the stamp in the hook
T_TITLE = cut("t_title")
T_MASK = S("v3") - 0.02
T_ANSWER = S("r3") - 0.02
T_ERUPT = cut("x_erupt")
T_EYE = cut("y_eye") + 0.03
T_STAMP = E("y2") + 0.02
SILENCES = [(E("v2") + 0.03, T_MASK - 0.005), (E("r2") + 0.06, T_ANSWER - 0.005), (E("x1") + 0.12, T_EYE - 0.005)]


def score(mus, fx):
    T = TL.total
    # ---------------- the hook: the stamp comes down
    fx.add(DM.reverse_cymbal(0.55, 0.9, seed=1), T_HIT - 0.55)
    fx.add(DM.rumble(0.6, 0.6, seed=2), 0.0)
    mus.add(DM.chord(38, 3.2, 1.1, seed=1), T_HIT)
    mus.add(DM.sub(26, 3.0, 1.0, att=0.01), T_HIT)
    fx.add(DM.metal_hit(1.0, seed=1), T_HIT)
    fx.add(DM.shriek(1.3, 1.0, seed=1), T_HIT)
    fx.add(DM.boom(1.0), T_HIT)
    fx.add(DM.feedback(2.6, 2350, 0.45, seed=1), T_HIT + 0.5)
    fx.add(DM.whoosh(0.6, False, 0.6, seed=2), T_HIT + 0.35)               # the stamp lifting away
    fx.add(DM.breath(2.0, 0.5, rate=0.8, seed=3), 1.4)                      # the Clerk breathing through its grille
    fx.add(DM.fire(1.2, 0.7, seed=4), 2.8)                                  # the file catching on the lamp
    # ---------------- cold open: wind, a sustained tone, the theme sung pure
    t0, t1 = cut("o_sky"), T_TITLE
    fx.add(DM.pines(t1 - t0 + 1.0, 1.0, seed=2), t0)
    mus.add(tone(93, t1 - t0 + 0.5, 1.0), t0)
    mus.add(DM.pad([50, 57, 60, 64, 69], t1 - t0 + 0.5, 0.55, cut=(300, 1100), att=2.0), t0 + 0.2)
    theme_at(mus, S("c1") - 0.35, DM.theme(amp=0.8, seed=1), until=t1)
    fx.add(DM.fire(t1 - cut("o_fire") + 0.4, 0.9, seed=5), cut("o_fire"))
    for word in ("hired,", "refused,"):                                    # each record catching as it is named
        fx.add(DM.whoosh(0.5, True, 0.5, seed=len(word)), Wx("c1", word) - 0.3)
        fx.add(DM.spark(0.6, seed=len(word)), Wx("c1", word) + 0.25)
    # ---------------- the title: a crushing chord
    fx.add(DM.reverse_cymbal(1.2, 1.0, seed=3), T_TITLE - 1.2)
    mus.add(DM.chord(38, 2.4, 1.2, seed=3), T_TITLE, until=cut("k_1") + 0.3)
    mus.add(DM.sub(26, 2.2, 1.0, att=0.01), T_TITLE)
    fx.add(DM.metal_hit(1.0, seed=2, size=1.4), T_TITLE)
    fx.add(DM.shriek(1.2, 0.8, seed=2), T_TITLE)
    fx.add(DM.crash(0.6, 2.5), T_TITLE)
    fx.add(DM.boom(0.9), T_TITLE)
    card_hit(mus, fx, cut("k_1"), 34, seed=11, gong=0.8)                    # I: down to Bb, cobalt
    # ---------------- I. THE INHERITANCE: pads in the dark, sparks, cards turning
    t0, t1 = cut("i_dreamer"), cut("k_2")
    fx.add(DM.rumble(t1 - t0, 0.5, seed=4), t0)
    for k, (notes, dt) in enumerate((([38, 50, 57, 62, 65], 4.0), ([34, 46, 53, 58, 62], 4.0), ([31, 43, 50, 55, 58], 4.0),
                                     ([33, 45, 52, 57, 61], 4.0), ([38, 50, 57, 62, 65], 4.0))):
        tt = t0 + k * 4.0
        if tt < cut("i_eyes"):
            mus.add(DM.pad(notes[1:], dt + 0.6, 0.7, cut=(350, 1500), att=1.0, seed=k), tt)
            mus.add(DM.sub(notes[0], dt, 0.5), tt)
    fx.add(DM.fire(cut("i_cards") - t0 + 0.3, 0.5, seed=6), t0)
    fx.add(DM.breath(2.5, 0.35, rate=0.6, seed=4), t0 + 0.2)                 # the sleeping face breathing in
    for w in ("prejudice,", "inequality,", "stereotypes,", "people", "never", "counted."):
        fx.add(DM.whoosh(0.35, True, 0.4, seed=len(w)), Wx("i1", w) - 0.3)
        mus.add(DM.bell(81 if w != "counted." else 80, 0.5, 2.0), Wx("i1", w) + 0.05)
    fx.add(I.teleprinter(cut("i_eyes") - cut("i_faces"), 0.25, rate=22), cut("i_faces"))       # the face-reader working
    fx.add(Y.beep(1800, 0.12, 0.6), Wx("i2", "wrong") - 0.05)
    fx.add(Y.beep(900, 0.3, 0.6), Wx("i2", "wrong") + 0.12)
    fx.add(Y.beep(2400, 0.08, 0.5), Wx("i2", "Lighter-skinned") + 0.3)
    # her eyes open: the theme again, warped
    t0 = cut("i_eyes")
    theme_at(mus, t0 - 0.1, DM.wow(DM.theme(amp=0.75, vowel="o", seed=2), depth=40, rate=0.45), until=cut("k_2"))
    mus.add(DM.pad([62, 65, 69, 72], cut("k_2") - t0 + 0.3, 0.55, cut=(300, 1200), att=0.8), t0)
    mus.add(DM.sub(26, cut("k_2") - t0, 0.6), t0)
    fx.add(DM.chant(cut("k_2") - t0 + 0.3, 0.8, seed=1), t0)
    fx.add(DM.heartbeat(5, 54, 0.7), t0 + 0.3)
    card_hit(mus, fx, cut("k_2"), 39, seed=12)                             # II: Eb, the flat second, red
    # ---------------- II. THE PATTERN: the doom riff
    t0, t1 = cut("p_portraits"), cut("k_3")
    DM.riff(mus, t0, cut("p_scrap"), [(38, 3, False), (39, 1, False), (38, 2, False), (36, 1, False), (34, 1, False)], bpm=60, amp=0.8, seed=20)
    mus.add(DM.sub(26, cut("p_scrap") - t0, 0.7), t0)
    mus.add(DM.pad([62, 65, 69, 74], cut("p_scrap") - t0, 0.45, cut=(400, 1600)), t0)
    fx.add(DM.rumble(t1 - t0, 0.4, seed=5), t0)
    fx.add(O.whoosh(0.8, True, seed=3, amp=0.6), cut("p_template") - 0.4)
    fx.add(DM.chant(cut("p_cv") - cut("p_template"), 0.5, seed=2), cut("p_template"))
    t0 = cut("p_cv")
    fx.add(O.whir(cut("p_scrap") - t0, 0.6, f=60), t0)                    # the reading machine's reels
    fx.add(I.teleprinter(cut("p_scrap") - t0 - 0.3, 0.45, rate=11), t0 + 0.2)
    tw = Wx("p2", "women's")
    fx.add(FXL.buzz(0.6, 0.9), tw + 0.05)                                  # marked down
    fx.add(DM.metal_hit(0.6, seed=8, size=0.7), tw + 0.1)
    mus.add(Y.stab([38, 39, 45], 0.8, dur=0.9, bright=1600), tw + 0.1)
    t0 = cut("p_scrap")
    fx.add(DM.power_down(1.1, 1.0), t0)
    fx.add(DM.spark(0.9, seed=3), t0 + 0.35)
    fx.add(DM.fire(1.4, 0.8, seed=7), t0 + 0.3)
    # her calm: the theme bit-crushed, a pad, chanting
    t0 = cut("p_calm")
    theme_at(mus, t0 + 0.1, DM.crush(DM.theme(amp=0.7, vowel="a", seed=3, transpose=-12), bits=4, hold=8), until=cut("p_door"))
    mus.add(DM.pad([50, 53, 57, 62], cut("p_door") - t0 + 0.5, 0.6, cut=(300, 1200)), t0)
    mus.add(DM.sub(26, cut("p_door") - t0, 0.6), t0)
    fx.add(DM.chant(cut("p_door") - t0, 0.6, seed=3), t0)
    # the door
    t_shut = Wx("p3", "discrimination.") + 0.2
    fx.add(DM.door_slam(1.0, seed=1), t_shut)
    mus.add(DM.chord(38, 2.0, 0.9, seed=31), t_shut, until=cut("p_proxy") + 0.8)
    fx.add(DM.boom(0.7), t_shut)
    # stand-ins
    t0 = cut("p_proxy")
    fx.add(O.whoosh(0.5, False, seed=4, amp=0.5), Wx("p4", "Delete") - 0.1)
    for w in ("postcode,", "hobby,", "gap"):
        fx.add(DM.metal_hit(0.55, seed=len(w), size=0.6), Wx("p4", w) + 0.05)
        mus.add(Y.stab([38, 39], 0.6, dur=0.6, bright=1400), Wx("p4", w) + 0.05)
    mus.add(DM.pad([38 + 12, 39 + 12, 45 + 12], t1 - t0, 0.5, cut=(300, 1000)), t0)
    mus.add(DM.sub(26, t1 - t0, 0.6), t0)
    card_hit(mus, fx, cut("k_3"), 36, seed=13)                             # III: C, magenta
    # ---------------- III. THE MULTITUDE
    t0 = cut("m_manager")
    for k in range(int((cut("m_army") - t0) / 1.3) + 1):                   # one man, one stamp, slowly
        tt = t0 + k * 1.3 + 0.75 * 1.3 * 0.5
        if tt < cut("m_army"):
            fx.add(FXL.thud(0.8, seed=k), tt)
    fx.add(FXL.room_tone(cut("m_army") - t0, 0.7, hum=True), t0)
    fx.add(O.tick(0.5), t0 + 0.5)
    mus.add(tone(86, cut("m_army") - t0 + 0.3, 0.8), t0)
    # the army: palm-muted chugs, unison stamps every two-thirds of a second, strobes buzzing, engines far off
    t0, t1 = cut("m_army"), cut("m_kaleido")
    DM.riff(mus, t0, t1, [(38, 2, True), (38, 1, False), (39, 1, False)], bpm=90, amp=0.9, seed=40)
    mus.add(DM.sub(26, t1 - t0, 0.8), t0)
    k = 1
    while t0 + k * (2 / 3) < cut("m_nist") + 0.2:
        tt = t0 + k * (2 / 3)
        fx.add(DM.metal_hit(0.7, seed=k, size=0.8), tt)
        fx.add(DM.kick(0.8, seed=k), tt)
        k += 1
    fx.add(DM.engine(6.0, 0.8, seed=1), t0 - 0.5)
    fx.add(FXL.buzz(cut("m_nist") - t0, 0.35), t0)
    fx.add(DM.crash(0.7, 2.0), t0)
    fx.add(DM.boom(0.8), t0)
    for w, m in (("speed", 38), ("scale", 39)):
        mus.add(DM.chord(m, 0.9, 0.7, seed=len(w)), Wx("m2", w) - 0.02, until=Wx("m2", w) + 0.9)
    # the kaleidoscope: chanting, a phasing pad, the theme reversed and sunk a semitone
    t0, t1 = cut("m_kaleido"), cut("k_4")
    fx.add(DM.chant(t1 - t0 + 0.3, 1.0, seed=4), t0)
    mus.add(DM.pad([50, 56, 62, 65], t1 - t0 + 0.4, 0.7, cut=(500, 2400), att=0.4), t0)
    theme_at(mus, t0 + 0.1, DM.detune(DM.theme(amp=0.6, vowel="o", seed=4)[::-1], -1.0), until=t1)
    mus.add(DM.sub(26, t1 - t0, 0.7), t0)
    card_hit(mus, fx, cut("k_4"), 33, seed=14)                             # IV: A, blood
    # ---------------- IV. THE VERDICT
    t0 = cut("v_doors")
    mus.add(DM.sub(26, cut("v_why") - t0, 0.8), t0)
    mus.add(DM.pad([50, 53, 56, 62], cut("v_why") - t0, 0.5, cut=(300, 900)), t0)
    for i, (label, word) in enumerate((("JOB", "job."), ("INSURANCE", "Insurance."), ("HOME", "home."), ("LOAN", "loan."),
                                       ("UNIVERSITY", "university."), ("BENEFITS", "Benefits."))):
        ts = Wx("v1", word) + 0.13
        fx.add(DM.door_slam(1.0, seed=i), ts)
        fx.add(DM.metal_hit(0.5, seed=i + 20, size=1.1), ts)
        mus.add(DM.chord([38, 39, 36, 34, 33, 38][i], 0.7, 0.75, seed=50 + i), ts, until=ts + 0.75)
    t0 = cut("v_why")
    fx.add(DM.feedback(E("v2") - t0 + 0.05, 2800, 0.7, seed=2), t0)         # rising into the silence
    fx.add(DM.chant(E("v2") - t0, 0.6, seed=5), t0)
    # the mask
    fx.add(DM.metal_hit(1.0, seed=3, size=1.2), T_MASK)
    fx.add(DM.shriek(1.5, 1.2, seed=3), T_MASK)
    fx.add(DM.boom(1.0), T_MASK)
    mus.add(DM.chord(39, 2.6, 1.2, seed=60), T_MASK, until=cut("v_vars") + 0.4)
    mus.add(DM.sub(27, 2.6, 1.0, att=0.01), T_MASK)
    fx.add(DM.feedback(1.4, 3100, 0.6, seed=3), T_MASK + 0.05)
    fx.add(FXL.buzz(cut("v_vars") - T_MASK, 0.5), T_MASK)                   # the strobe
    fx.add(DM.breath(2.6, 0.6, rate=1.1, seed=5), T_MASK + 0.2)
    # variables, a clerk, a score
    t0 = cut("v_vars")
    fx.add(I.teleprinter(cut("v_clerk") - t0, 0.5, rate=26), t0)
    mus.add(DM.pad([57, 62, 65, 69], cut("v_clerk") - t0 + 0.4, 0.6, cut=(500, 2200), att=0.3), t0)
    fx.add(FXL.room_tone(cut("v_dutch") - cut("v_clerk"), 0.6, hum=False), cut("v_clerk"))
    ts = Wx("v4", "You", 1) - 0.1
    mus.add(Y.stab([26, 38, 39], 1.0, dur=1.4, bright=1000), ts)
    fx.add(DM.metal_hit(0.7, seed=9, size=1.0), ts)
    # the canal houses: wind, a distant bell, letters under doors, windows going dark
    t0, t1 = cut("v_dutch"), cut("d_space")
    fx.add(DM.pines(t1 - t0, 0.6, seed=7), t0)
    fx.add(FXL.temple_bell(57, 0.35, 6.0), t0 + 0.4)
    mus.add(DM.pad([50, 53, 57, 60], t1 - t0, 0.55, cut=(300, 1100), att=1.5), t0)
    mus.add(DM.sub(26, t1 - t0, 0.5), t0)
    rng = np.random.default_rng(7)
    for k in range(9):
        tt = Wx("v5", "Tens") + k * 0.38 + rng.uniform(0, 0.2)
        fx.add(O.page(0.35, seed=k), tt)
        fx.add(O.click(0.25), tt + 0.25)
    fx.add(FXL.temple_bell(38, 0.8, 7.0), Wx("v5", "resigned.") - 0.1)        # a seat of government, tolling
    fx.add(DM.rumble(2.5, 0.6, seed=6), Wx("v5", "resigned."))
    # ---------------- the descent: the cosmos, an arpeggiator, glass bells, her voice
    t0, t1 = cut("d_space"), cut("r_kitchen")
    DM.arp(mus, t0 + 0.3, t1 - 0.6, [62, 65, 69, 72, 74], rate=8, amp=0.7)
    mus.add(DM.pad([50, 57, 62, 65, 69], t1 - t0, 0.8, cut=(600, 3000), att=0.6), t0)
    mus.add(DM.sub(26, t1 - t0, 0.5), t0)
    bt = t0 + 0.4
    for i, (m, b) in enumerate(DM.THEME):                                  # the theme on glass bells, one note wrong
        mm = m + 12 + (1 if i == 6 else 0)
        mus.add(DM.bell(mm, 0.6, 2.4), bt)
        bt += b * 0.42
    fx.add(DM.chant(t1 - t0, 0.5, seed=6), t0)
    fx.add(DM.whoosh(1.4, False, 0.9, seed=5), E("d1") + 0.1)                  # she falls
    fx.add(DM.rumble(1.6, 0.7, seed=7), E("d1") + 0.3)
    # ---------------- Iris: no music; a tube humming, a fridge, a clock, the dings of the night
    t0, t1 = cut("r_kitchen"), cut("r_scream")
    fx.add(DM.hum(t1 - t0, 0.9, seed=1), t0)
    fx.add(FXL.room_tone(t1 - t0, 0.5, hum=True), t0)
    tt = t0 + 0.3
    while tt < cut("r_slot"):
        fx.add(O.tick(0.35), tt)
        tt += 1.0
    t0 = cut("r_inbox")
    tt = t0 + 0.1
    while tt < cut("r_slot") - 0.2:
        fx.add(DM.ding(0.45, m=88), tt)
        tt += 0.7
    t0 = cut("r_slot")
    fx.add(O.whir(cut("r_why") - t0, 0.5, f=50), t0)
    for k in range(5):
        fx.add(DM.metal_hit(0.45, seed=k + 40, size=0.6), t0 + 0.2 + k * 0.33)
    fx.add(DM.chant(cut("r_why") - t0, 0.4, seed=7), t0)
    fx.add(DM.breath(2.2, 0.5, rate=1.0, seed=6), cut("r_why") - 0.1)
    fx.add(DM.boom(0.8), T_ANSWER)                                          # out of the silence: the answer
    fx.add(DM.metal_hit(0.6, seed=12, size=0.9), T_ANSWER)
    mus.add(DM.sub(27, 2.4, 0.8, att=0.02), T_ANSWER)
    fx.add(DM.feedback(1.6, 2600, 0.35, seed=4), T_ANSWER + 1.2)
    fx.add(DM.vibrate(0.9, 0.5), Wx("r4", "rental") - 0.25)
    fx.add(DM.vibrate(0.9, 0.5), Wx("r4", "loan:") - 0.25)
    t0 = cut("r_reasons")
    fx.add(DM.heartbeat(8, 92, 0.8), t0)
    box = O.music_box([(m + 12, b * 2.4) for m, b in DM.THEME], amp=0.5, detune=lambda u: 70.0 * u)
    mus.add(box, t0 + 0.2, 0.8, until=cut("r_scream"))
    mus.add(DM.sub(26, cut("r_scream") - t0, 0.5), t0)
    t0 = cut("r_scream")
    fx.add(DM.feedback(T_ERUPT - t0 + 0.2, 2200, 0.7, seed=5), t0)
    tq = Wx("r5", "qualified!")
    mus.add(DM.chord(38, 1.0, 1.0, seed=70, bend=-0.5), tq)
    fx.add(DM.metal_hit(0.8, seed=13), tq)
    # ---------------- the eruption: everything at once
    t0, t1 = T_ERUPT, E("x1") + 0.12
    fx.add(DM.crash(1.0, 3.0), t0)
    fx.add(DM.shriek(1.6, 1.0, seed=4), t0)
    fx.add(DM.boom(1.0), t0)
    DM.riff(mus, t0, t1, [(38, 1, True), (39, 0.5, False), (38, 0.5, False), (36, 1, True), (34, 1, False)], bpm=120, amp=1.0, seed=80)
    mus.add(DM.sub(26, t1 - t0, 1.0, att=0.02, rel=0.05), t0)
    beat = 0.5
    k = 0
    while t0 + k * beat < t1 - 0.05:
        tt = t0 + k * beat
        fx.add(DM.kick(1.0, seed=k), tt)
        if k % 2 == 1:
            fx.add(DM.tom(45 - (k % 4), 0.8, seed=k), tt)
        if k % 4 == 0:
            fx.add(DM.crash(0.5, 1.5, seed=k), tt)
        k += 1
    fx.add(DM.engine(t1 - t0 + 1.0, 1.0, seed=2, f0=56), t0 - 0.5)
    fx.add(DM.feedback(t1 - t0, 3300, 0.6, seed=6), t0)
    fx.add(DM.chant(t1 - t0, 1.0, seed=8), t0)
    for k in range(10):
        fx.add(DM.metal_hit(0.6, seed=k + 60, size=0.7 + 0.1 * (k % 3)), t0 + 0.11 + k * 0.44)
    # ---------------- the eye opens on you
    fx.add(DM.boom(1.0), T_EYE)
    fx.add(DM.shriek(1.2, 1.2, seed=5), T_EYE)
    fx.add(DM.metal_hit(0.9, seed=5, size=1.3), T_EYE)
    fx.add(DM.feedback(0.9, 3400, 0.8, seed=7), T_EYE)
    mus.add(DM.chord(39, 2.0, 1.0, seed=90), T_EYE, until=S("y1") + 1.6)
    mus.add(DM.sub(27, end("y_eye") - T_EYE, 0.9, att=0.01), T_EYE)
    fx.add(DM.chant(end("y_eye") - T_EYE, 0.9, seed=9), T_EYE + 0.3)
    mus.add(O.drone(end("y_eye") - T_EYE + 0.5, root=26, amp=0.8), T_EYE)
    tp = Wx("y1", "pause.")
    fx.add(DM.tape_stop(Y.riser(0.6, 0.6, f0=900, f1=1200), 0.5), tp - 0.05)
    fx.add(DM.whoosh(0.4, True, 0.6, seed=8), Wx("y1", "scroll.") - 0.1)
    # the dossier: a typewriter filling it in, then the stamp
    t0 = cut("y_dossier")
    for i in range(6):
        fx.add(DM.typewriter(5, 0.05, 0.7, seed=i), t0 + 0.15 + i * 0.22)
    mus.add(O.drone(T_STAMP - t0, root=26, amp=0.6), t0)
    fx.add(DM.metal_hit(1.0, seed=6), T_STAMP)
    fx.add(DM.shriek(1.2, 1.0, seed=6), T_STAMP)
    fx.add(DM.boom(1.0), T_STAMP)
    mus.add(DM.chord(38, 2.0, 1.1, seed=91), T_STAMP, until=cut("e_fire") + 0.8)
    mus.add(DM.sub(26, 2.0, 1.0, att=0.01), T_STAMP)
    # ---------------- the quiet: the fire, the theme sung once more and snapping off, warm pads
    t0, t1 = cut("e_fire"), T
    fx.add(DM.fire(t1 - t0, 0.9, seed=9), t0)
    fx.add(DM.pines(t1 - t0, 0.6, seed=10), t0)
    theme_at(mus, t0 + 0.4, DM.broken(DM.theme(amp=0.75, seed=5), cut=0.72), until=cut("e_tablet") + 2.0)
    for k, (notes, dt) in enumerate((([50, 57, 62, 65, 69], 4.5), ([46, 53, 58, 62, 65], 4.5), ([43, 50, 55, 58, 62], 4.5),
                                     ([45, 52, 57, 61, 64], 4.5), ([50, 57, 62, 66, 69], 5.0))):
        tt = cut("e_tablet") + k * 4.5
        if tt < cut("e_moon"):
            mus.add(DM.pad(notes, dt + 0.8, 0.6, cut=(350, 1400), att=1.2, seed=10 + k), tt)
    mus.add(DM.sub(26, cut("e_moon") - t0, 0.45), t0)
    for ln, word in (("VALID", "reliable,"), ("ACC", "transparent,"), ("EXP", "explainable,"), ("PRI", "privacy-enhanced,"), ("FAIR", "fair,")):
        mus.add(DM.bell(86, 0.45, 2.0), Wx("e1", word))
    mus.add(DM.bell(81, 0.4, 2.4), Wx("e1", "managed.") - 0.2)
    for w, m in (("data?", 74), ("checked", 72), ("appeal?", 69)):
        mus.add(DM.bell(m, 0.55, 2.4, ratio=2.0), Wx("e2", w))
    t_human = Wx("e2", "human") - 0.25
    fx.add(O.whir(t_human - cut("e_hand"), 0.6, f=80), cut("e_hand"))       # the stamp coming down
    fx.add(DM.metal_hit(0.7, seed=14, size=0.8), t_human)                   # caught
    fx.add(O.clunk(0.8, seed=2), t_human + 0.02)
    mus.add(DM.pad([50, 57, 62, 66, 69], cut("e_moon") - t_human + 0.5, 0.7, cut=(400, 1800), att=0.3), t_human)
    # the moon's eye opens, and the last image burns in
    t0 = cut("e_moon")
    fx.add(DM.boom(0.8), t0 + 0.3)
    mus.add(DM.chord(38, 2.4, 0.8, seed=99), t0 + 0.3, until=T - 0.1)
    fx.add(DM.feedback(T - t0 - 0.2, 2200, 0.5, seed=9), t0 + 0.2)
    fx.add(DM.chant(T - t0, 0.6, seed=10), t0)


# ------------------------------------------------------------------ voices

def reverb(x, wet=0.1, rt60=0.8, seed=8, predelay=0.0):
    rng = np.random.default_rng(seed)
    t = np.arange(int(rt60 * 1.4 * SR)) / SR
    ir = np.stack([rng.normal(0, 1, len(t)) * np.exp(-6.9 * t / rt60) for _ in range(2)])
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    if predelay > 0:
        ir = np.concatenate([np.zeros((2, int(predelay * SR))), ir], axis=1)
    y = np.stack([signal.fftconvolve(x[c], ir[c])[: x.shape[1]] for c in range(2)])
    return x * (1 - wet) + y * wet


LEVEL = {"NAR": -16.0, "MERIT": -15.0, "SYSTEM": -16.5, "IRIS": -16.0, "WHY": -17.5}


def voices():
    """The narrator close and hushed; Merit in a vast dark hall; the system dry; Iris in a small kitchen; the chorus
    wide."""
    buses = {k: np.zeros((2, N_)) for k in ("NAR", "MERIT", "SYSTEM", "IRIS", "WHY")}
    for key in TL.order:
        Ln = TL.lines[key]
        who = Ln["who"]
        up = signal.resample_poly(Ln["wav"].astype(np.float64), SR, VSR)
        r = np.sqrt((up ** 2).mean()) + 1e-12
        up = up * db(LEVEL.get(who, -16.0)) / r
        if who == "WHY":                                                     # spread wide: two slightly different copies
            d = int(0.011 * SR)
            sig = np.stack([up, np.concatenate([np.zeros(d), up])[: len(up)]])
        elif who == "MERIT":
            d = int(0.007 * SR)
            sig = np.stack([up, np.concatenate([np.zeros(d), up])[: len(up)] * 0.92])
        else:
            sig = np.stack([up, up])
        i = int(Ln["start"] * SR)
        j = min(N_, i + sig.shape[1])
        buses[who][:, i:j] += sig[:, : j - i]
    out = reverb(buses["NAR"], 0.06, 0.6, seed=3)
    out += reverb(buses["MERIT"], 0.3, 3.2, seed=4, predelay=0.04)
    out += reverb(buses["SYSTEM"], 0.07, 0.25, seed=5)
    out += reverb(buses["IRIS"], 0.13, 0.45, seed=6)
    out += reverb(buses["WHY"], 0.28, 1.6, seed=7)
    return out


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


NEED = {"NAR": 9.5, "MERIT": 10.0}               # the voice over the beds in the speech band (others: 11)
BED = -4.0                                       # the beds' ceiling between lines, against the average line (dB)
# (time, ceiling dB over the average line, seconds): the moments allowed to be loud
HITS = [(T_HIT, 16.0, 1.4), (T_TITLE, 15.0, 1.4), (cut("k_2"), 10.0, 1.2), (cut("k_3"), 10.0, 1.2), (cut("k_4"), 10.0, 1.2),
        (cut("m_army"), 9.0, 2.3), (T_MASK, 18.0, 1.2), (T_ANSWER, 11.0, 0.6), (T_ERUPT, 16.0, 1.95), (T_EYE, 18.0, 0.5),
        (T_STAMP, 17.0, 1.3), (cut("e_moon") + 0.3, 8.0, 2.0)]
SAT = {T_HIT: 2.5, T_TITLE: 2.0, T_MASK: 4.0, T_ERUPT: 3.0, T_EYE: 4.0, T_STAMP: 3.5}
BOOST = {T_HIT: (5.0, 1.3), T_TITLE: (5.0, 1.3), cut("k_2"): (3.0, 1.2), cut("k_3"): (3.0, 1.2), cut("k_4"): (3.0, 1.2),
         cut("m_army"): (3.0, 2.3), T_MASK: (6.0, 1.1), T_ANSWER: (3.0, 0.6), T_ERUPT: (6.0, 1.9), T_EYE: (6.0, 0.5),
         T_STAMP: (6.0, 1.2), cut("e_moon") + 0.3: (2.0, 2.0)}
CEIL = -2.0
STEMS = {}


def buses():
    path = os.path.join(HERE, "build", "buses.npz")
    if os.environ.get("MB_CACHE") == "load" and os.path.exists(path):
        d = np.load(path)
        return d["mus"].astype(np.float64), d["fx"].astype(np.float64)
    mus, fx = Bus(), Bus()
    score(mus, fx)
    if os.environ.get("MB_CACHE"):
        np.savez(path, mus=mus.x.astype(np.float32), fx=fx.x.astype(np.float32))
    return mus.x, fx.x


def build():
    mus_x, fx_x = buses()
    music = reverb(mus_x, 0.22, 2.4, seed=2)
    music = signal.sosfilt(signal.butter(4, 28 / (SR / 2), "high", output="sos"), music, axis=1)
    fxx = reverb(fx_x, 0.18, 1.4, seed=3)
    fxx = signal.sosfilt(signal.butter(4, 28 / (SR / 2), "high", output="sos"), fxx, axis=1)
    vo = compress(presence(voices(), 3200, 2.5))
    # levels: the title chord sets the music's scale; the effects sit a little under it
    ref = music[:, int(T_TITLE * SR):int((T_TITLE + 1.2) * SR)]
    music = music * db(-12.0) / (np.sqrt((ref ** 2).mean()) + 1e-12)
    on = np.abs(fxx).max(axis=0) > 1e-4
    fxx = fxx * db(-16.0) / (np.sqrt((fxx[:, on] ** 2).mean()) + 1e-12)
    # the scares: saturate the hit itself (same peak, far less crest) so it lands as a wall of sound, not a click;
    # done before the ducking, so a line that follows a scare still clears it
    for t, drive in SAT.items():
        a, b = int((t - 0.02) * SR), int((t + 1.1) * SR)
        beds = music[:, a:b] + fxx[:, a:b]
        pk = np.abs(beds).max() + 1e-9
        sat = np.tanh(drive * beds / pk) / np.tanh(drive) * pk
        w = np.ones(b - a)
        f = int(0.15 * SR)
        w[-f:] = np.linspace(1, 0, f)
        gain = (w * (sat - beds) + beds) / np.where(np.abs(beds) < 1e-9, 1e-9, beds)
        gain = np.clip(gain, 0, 8)
        music[:, a:b] *= gain
        fxx[:, a:b] *= gain
    # the eruptions: the hits pushed up hard before the limiter, so they land as walls of sound far above the voice
    for t, (gdb, dur) in BOOST.items():
        a, b = max(0, int((t - 0.03) * SR)), min(N_, int((t + dur) * SR))
        env = np.ones(b - a)
        f = int(0.03 * SR)
        env[:f] = np.linspace(0, 1, f)
        env[-int(0.25 * SR):] = np.linspace(1, 0, int(0.25 * SR))
        g = 1 + (db(gdb) - 1) * env
        music[:, a:b] *= g[None]
        fxx[:, a:b] *= g[None]
    # duck the beds under every line until the voice clears them by NEED dB in the speech band. The beds are split
    # into a wide speech band (ducked fully) and the rest (bass and air, ducked far less); the margin is measured on
    # what the split will actually leave in the speech band, so the ride converges on the real result
    band = lambda x: signal.sosfilt(signal.butter(2, [300 / (SR / 2), 4000 / (SR / 2)], "band", output="sos"), x.mean(axis=0))
    sos = signal.butter(2, [160 / (SR / 2), 6000 / (SR / 2)], "band", output="sos")
    music_b, fxx_b = signal.sosfiltfilt(sos, music, axis=1), signal.sosfiltfilt(sos, fxx, axis=1)
    bv = band(vo)
    B1, B2 = band(music_b + fxx_b), band((music - music_b) + (fxx - fxx_b))
    gain = {k: 0.0 for k in TL.order}
    spans = {k: (int(TL.s(k) * SR), int(TL.e(k) * SR)) for k in TL.order}

    def rides():
        r = np.ones(N_)
        for key in TL.order:
            a, b = spans[key]
            lo, hi = max(0, a - int(0.15 * SR)), min(N_, b + int(0.15 * SR))
            r[lo:hi] = np.minimum(r[lo:hi], db(gain[key]))
        return smooth(r, 0.18)

    for _ in range(14):
        ride = rides()
        bb = B1 * ride + B2 * ride ** 0.35
        short = False
        for key in TL.order:
            a, b = spans[key]
            mg = 20 * np.log10((np.sqrt((bv[a:b] ** 2).mean()) + 1e-12) / (np.sqrt((bb[a:b] ** 2).mean()) + 1e-12))
            need = NEED.get(TL.who(key), 11.0)
            if mg < need:
                gain[key] -= (need - mg) + 0.3
                short = True
        if not short:
            break
    ride = rides()
    ride_rest = ride ** 0.35
    music = music_b * ride[None] + (music - music_b) * ride_rest[None]
    fxx = fxx_b * ride[None] + (fxx - fxx_b) * ride_rest[None]
    # between the lines the beds stay under the voice; the hits are let through, by far the loudest moments
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
    mix = signal.sosfilt(signal.butter(4, 25 / (SR / 2), "high", output="sos"), mix, axis=1)
    dead = np.ones(N_)
    for a, b in SILENCES:
        dead[int(a * SR):int(b * SR)] = 0.0
    dead = np.convolve(dead, np.ones(int(0.004 * SR)) / int(0.004 * SR), "same")
    rng = np.random.default_rng(21)
    hiss = signal.sosfilt(signal.butter(2, [400 / (SR / 2), 6000 / (SR / 2)], "band", output="sos"), rng.normal(0, 1, N_))
    mix = mix * dead[None] + np.stack([hiss, hiss]) * db(-72) * (1 - dead)[None]
    mix = loudness(mix, -14.0)
    a_, b_ = int((TL.total - 1.0) * SR), int(TL.total * SR)
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
        if mg < NEED.get(TL.who(key), 11.0) - 1.0:
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
