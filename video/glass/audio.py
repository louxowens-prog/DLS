"""GLASS - the soundtrack. All original, all synthesized.

Score: a dark orchestral horror score (low strings, heavy brass that swells, a wordless choir, a tam-tam) braided with
a hypnotic North African-style trance - frame drums with gut snares, a goblet drum, metal castanets clattering in
triplets, hand claps, a double-reed horn, chanting voices - that builds chapter by chapter. A fragile melody in D hijaz
on a solo female voice opens the dream at dawn and keeps returning, more corrupted each time: on the reed, warped on
tape, bit-crushed, on an out-of-tune music box, blasted by brass and choir in the collapse, snapping off, and at last
slowed and alone. Long passages are near-silent, held on one sustained tone.

Sound: the white room humming, a heart monitor, breath inside a mask; water closing overhead, bubbles; wind across the
dunes and hissing sand; silk and capes; porcelain creaking; lens irises whirring open, camera shutters; glass cracking
and shattering; clockwork; reversed voices; heartbeats and deep rumbles. Four hard cuts to dead silence, each before a
scare: before her eyes open, before the scales slam, before the knock, and before the black glass.

Voices: the narrator close and warm; the Curator in a vast hall, slowed, deepened and layered; the machine dry; Nadia
in small cold rooms.
"""
import math
import os
import wave

import numpy as np
from scipy import signal

import doom as DM
import orch as O
import synth82 as Y
import trance as Tr
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
    return amp * 0.12 * x * np.clip(t / 1.2, 0, 1) * np.clip((dur - t) / 1.2, 0, 1)


def wide(x, d=0.011):
    """A mono sound spread across the stereo field (a delayed copy on one side)."""
    k = int(d * SR)
    return np.stack([x, np.concatenate([np.zeros(k), x])[: len(x)]])


# ------------------------------------------------------------------ moments

import sc_nadia as SN

T_TITLE = cut("c_dawn") + 0.5
T_EYES = cut("e_eyes")
T_SLAM = cut("t_scales") + 0.02
KNOCKS = SN.knocks()
T_COLLAPSE = cut("x_collapse")
T_CUT = cut("y_vitrine")
T_LUNGE = E("y3") + 0.02
SILENCES = [(E("e7") + 0.22, T_EYES - 0.005), (E("t5") + 0.22, T_SLAM - 0.005), (E("n10") + 0.05, KNOCKS[0] - 0.005),
            (T_CUT, T_CUT + 0.75), (E("y2") + 0.15, S("y3") - 0.55)]
BEAT = 0.2                                       # the trance's eighth note (12/8, a dotted quarter = 0.6 s)

_ONE = {}


def one(name, fn, k=4):
    """A cached one-shot with k seeded variants (so repeated drum strokes are never identical)."""
    if name not in _ONE:
        _ONE[name] = [fn(seed) for seed in range(k)]
    return _ONE[name]


BENDIR = {0: "dum", 7: "dum", 3: "tak", 6: "tak", 9: "tak", 10: "tak"}
DARB = {0: "doum", 6: "doum", 2: "tek", 5: "tek", 8: "tek", 11: "tek", 3: "ka", 9: "ka"}
KRAK = (0, 1, 3, 4, 6, 7, 9, 10)


def groove(bus, t0, t1, lv, k_fn=None, seed=0, until=None):
    """The trance: 12/8, a frame drum, a goblet drum, castanets, claps. lv: part -> gain (0 leaves it out);
    k_fn(t) -> 0..1 intensity."""
    dum = one("dum", lambda s: Tr.bendir("dum", 1.0, s))
    tak = one("tak", lambda s: Tr.bendir("tak", 1.0, s))
    doum = one("doum", lambda s: Tr.darbuka("doum", 1.0, s))
    tek = one("tek", lambda s: Tr.darbuka("tek", 1.0, s))
    ka = one("ka", lambda s: Tr.darbuka("ka", 1.0, s))
    kr = one("kr", lambda s: Tr.krakeb(1.0, s), 6)
    cl = one("cl", lambda s: Tr.clap(1.0, s))
    rng = np.random.default_rng(seed)
    step, t = 0, t0
    while t < t1:
        slot = step % 12
        k = 1.0 if k_fn is None else k_fn(t)
        hum_ = rng.normal(0, 0.006)
        if k > 0.01:
            if lv.get("bendir") and slot in BENDIR:
                s = dum if BENDIR[slot] == "dum" else tak
                bus.add(s[step % len(s)], t + hum_, lv["bendir"] * k * (1.0 if slot == 0 else 0.8), pan=0.45, until=until)
            if lv.get("darbuka") and slot in DARB:
                s = {"doum": doum, "tek": tek, "ka": ka}[DARB[slot]]
                bus.add(s[step % len(s)], t + hum_, lv["darbuka"] * k, pan=0.6, until=until)
            if lv.get("krakeb") and slot in KRAK:
                acc = 1.0 if slot % 3 == 0 else 0.65
                bus.add(kr[step % len(kr)], t + rng.normal(0, 0.004), lv["krakeb"] * k * acc, pan=0.3 + 0.4 * (step % 2), until=until)
            if lv.get("clap") and slot in (3, 9):
                bus.add(cl[step % len(cl)], t + hum_, lv["clap"] * k, pan=0.5, until=until)
        t += BEAT
        step += 1


def drone(bus, t0, t1, notes=(38, 45), gain=1.0, seed=0, att=1.0):
    bus.add(Tr.low_strings(list(notes), t1 - t0, 1.0, seed=seed, att=att), t0, gain, until=t1 + 0.6)


def card_hit(mus, fx, t, seed=0, big=1.0):
    """A chapter card: a frame drum and a goblet drum together, a reed cry, a tam-tam blooming, a low chord."""
    fx.add(DM.reverse_cymbal(0.6, 0.5, seed=seed), t - 0.6)
    mus.add(Tr.bendir("dum", 1.0, seed), t, 1.2 * big)
    mus.add(Tr.darbuka("doum", 1.0, seed), t, 0.9 * big)
    mus.add(Tr.tamtam(0.8 * big, 4.0, seed=seed), t, 1.0)
    mus.add(Tr.ghaita(74, 0.9, 1.0, seed=seed), t + 0.05, 0.8 * big, pan=0.4)
    mus.add(Tr.low_strings([38, 45, 50], 1.4, 1.0, seed=seed, att=0.05), t, 1.0 * big)


def theme_at(bus, t, x, gain=1.0, pan=0.5, until=None):
    bus.add(x, t, gain, pan=pan, until=until)


def score(mus, fx):
    rng = np.random.default_rng(3)
    # =========== the hook: a boom, a lock, a beep
    fx.add(DM.reverse_cymbal(0.35, 0.6, seed=1), -0.05)
    mus.add(DM.boom(1.0, 44.0, 2.0), 0.02, 0.9)
    mus.add(DM.sub(26, 1.2, 0.8, att=0.005, rel=0.6), 0.02)
    for k in range(3):                                            # the brackets closing in jerks
        fx.add(Tr.aperture(0.6, 0.12, seed=k), 0.1 + k * 0.16)
    fx.add(Tr.beep(1320, 0.18, 0.9), Wx("h1", "found") - 0.02)
    fx.add(Tr.beep(1760, 0.12, 0.6), Wx("h1", "found") + 0.18)
    # =========== the white room: hum, a heart monitor, breath in a mask
    room0, room1 = cut("h_lamp"), cut("c_sink")
    fx.add(Tr.hum(room1 - room0 + 0.5, 0.8), room0, until=room1 + 0.4)
    fx.add(Tr.monitor(room1 - room0, 64, 0.7), room0, until=room1)
    fx.add(Tr.mask_breath(room1 - room0 + 1.0, 0.9, 0.36), room0 - 0.2, until=room1 + 0.6)
    mus.add(tone(98, room1 - room0 + 1.0, 0.9), room0)
    # the room humming harder: machines, clicks, a whir
    fx.add(O.whir(1.4, 0.6, f=110.0), cut("c_monitors"))
    for k in range(5):
        fx.add(Tr.shutter(0.5, seed=k), cut("c_monitors") + 0.08 + k * 0.24, pan=0.3 + 0.1 * k)
    # =========== going under: the room muffles, water closes overhead, bubbles, the heartbeat slows
    t0, t1 = cut("c_sink"), cut("c_dawn")
    sub_ = np.concatenate([Tr.hum(t1 - t0, 0.7), np.zeros(1)])
    fx.add(Tr.underwater(sub_, 1.0), t0, 0.9)
    fx.add(Tr.bubbles(t1 - t0 + 0.3, 0.8, seed=2), t0)
    fx.add(O.whoosh(0.8, False, seed=1, amp=0.7), t0 - 0.1)
    fx.add(DM.heartbeat(4, 52, 0.9), t0 + 0.3)
    mus.add(O.rumble(t1 - t0 + 0.8, 0.6), t0)
    mus.add(Tr.choir([50, 57, 62], t1 - t0 + 0.5, 0.7, vowel="o", attack=1.6), t0 + 0.4)
    # =========== the desert at dawn: silence, wind, sand; the theme, pure; the title
    t0, t1 = cut("c_dawn"), cut("k_1")
    fx.add(Y.wind(t1 - t0 + 1.5, 0.7, seed=4), t0 - 0.2)
    fx.add(Tr.sand(t1 - t0 + 1.0, 0.8, seed=5), t0)
    theme_at(mus, t0 + 0.25, Tr.theme(0.36, 0.9, seed=1), 1.0, pan=0.45, until=t1 + 0.3)
    mus.add(Tr.low_strings([38, 50, 57], 2.2, 1.0, seed=2, att=0.3), T_TITLE - 0.05, 0.9)
    mus.add(Tr.tamtam(0.6, 4.0, seed=2), T_TITLE - 0.05)
    # =========== I. THE EYE (gold): the trance wakes, soft
    card_hit(mus, fx, cut("k_1"), seed=1)
    a, b = cut("e_list"), E("e7") + 0.22
    groove(mus, a, b, dict(bendir=0.55, krakeb=0.22), k_fn=lambda t: 0.6 + 0.4 * min(1.0, (t - a) / 12.0), seed=1, until=b)
    drone(mus, a, b, (38, 45), 0.8, seed=3)
    # the seven vitrines: a spotlight thunking on for each word
    for i, w in enumerate(("Cameras.", "Faces.", "Microphones.", "License", "Location.", "Clicks.", "Receipts.")):
        tw = Wx("e1", w) - 0.16 if i else cut("e_list")
        fx.add(DM.door_slam(0.22, seed=i), tw)
        fx.add(Tr.shutter(0.25, seed=i), tw + 0.02)
    # reed phrases in the air between lines
    mus.add(Tr.ghaita_phrase([(69, 1), (70, 0.5), (69, 0.5), (67, 1.5)], 0.22, 0.7, seed=4), E("e1") - 0.1, 0.5, pan=0.35)
    fx.add(O.whoosh(0.9, True, seed=3, amp=0.8), cut("e_keyhole") + 0.2)                     # rushing into the keyhole
    tk = Wx("e2", "house") - 0.2
    for k in range(9):                                                                         # eyes opening in the dark
        fx.add(Tr.aperture(0.35, 0.3, seed=k + 10), tk + k * 0.13 + rng.uniform(0, 0.05), pan=rng.uniform(0.2, 0.8))
    tn = Wx("e3", "Now") - 0.05
    fx.add(Tr.ticks(tn - cut("e_army"), 9.0, 0.7), cut("e_army"), until=tn + 0.1)              # the army at their screens
    fx.add(Tr.sand(2.4, 1.0, seed=7, gust=0.8), tn + 0.2)                                       # crumbling
    fx.add(Tr.shatter(0.35, seed=4, dur=1.8), tn + 0.25)
    fx.add(Tr.aperture(0.9, 0.6, seed=20), tn + 0.55)                                          # the one lens
    mus.add(DM.sub(26, 1.6, 0.6, att=0.3, rel=0.6), tn + 0.5)
    for i, w in enumerate(("Camera.", "Face.", "Behavior.", "Movement.", "Alert.")):            # five doors
        tw = Wx("e4", w)
        fx.add(O.whoosh(0.35, True, seed=i, amp=0.4), tw - 0.34)
        fx.add(DM.metal_hit(0.3, seed=i, size=0.9), tw - 0.17)
    fx.add(O.alarm_bell(1.2, 0.6), Wx("e4", "Alert.") + 0.05)
    for i, (w, _l, _p) in enumerate(__import__("sc_eye").NODES):                                # gold threads plucked
        mus.add(O.harp(Tr.HIJAZ[i % 8] + 12, 0.8, seed=i), Wx("e6", w) - 0.05, 0.7, pan=0.3 + 0.08 * i)
    mus.add(Tr.low_strings([50, 51, 54, 57], 1.8, 1.0, seed=5, att=1.4), cut("e_hand"), 1.2)    # the threads tightening
    fx.add(Tr.silk(1.8, 0.6, seed=3), cut("e_hand"))
    # silence; then her eyes: the iris whirring open, a brass stab and a choir shriek, then her drone
    fx.add(Tr.aperture(1.0, 0.5, seed=31), T_EYES)
    mus.add(Tr.brass_stab([38, 45, 51, 56], 1.0, seed=2, dur=0.9), T_EYES, 1.0)
    mus.add(Tr.choir([74, 75, 80], 1.2, 1.0, vowel="a", attack=0.02), T_EYES, 1.0)
    mus.add(DM.boom(1.0, 40.0, 2.2), T_EYES, 0.8)
    mus.add(Tr.choir([38, 45], E("e8") - T_EYES + 0.8, 0.8, vowel="o", attack=0.4), T_EYES + 0.3, 0.8)
    # =========== II. THE WORKHOUSE (emerald): the trance goes mechanical
    card_hit(mus, fx, cut("k_2"), seed=2)
    a, b = cut("w_corridor"), E("w6") + 0.2
    theme_at(mus, cut("k_2") + 0.2, Tr.ghaita_phrase([(m, bb) for m, bb in Tr.THEME], 0.24, 0.8, seed=8, vib=1.6), 0.55, pan=0.6, until=a + 2.0)
    groove(mus, a, b, dict(darbuka=0.55, krakeb=0.18), k_fn=lambda t: 0.6 + 0.4 * min(1.0, (t - a) / 10.0), seed=2, until=b)
    fx.add(Tr.ticks(S("w6") - 0.2 - a, 6.0, 0.55, seed=3), a, until=S("w6") - 0.2)                # clockwork under everything, until she speaks
    drone(mus, a, b, (38, 39), 0.75, seed=6)                                                      # D against Eb: unease
    for i, w in enumerate(("Keystrokes.", "Emails.", "Calls.", "face.", "bathroom")):            # instruments clicking on
        fx.add(DM.typewriter(3, 0.05, 0.28, seed=i), Wx("w2", w) - 0.24)
    tk = Wx("w3", "track") - 0.6
    for j in range(8):                                                                            # eight towers open their eyes
        mus.add(Tr.brass_stab([38 + (j % 2) * 7, 50], 0.5, seed=j, dur=0.3), tk + j * 0.12, 0.7)
        fx.add(Tr.aperture(0.3, 0.15, seed=40 + j), tk + j * 0.12)
    tf = Wx("w4", "firings") - 0.1
    fx.add(Tr.ticks(tf - cut("w_idle"), 4.0, 0.6, seed=8), cut("w_idle"), until=tf)
    fx.add(O.trapdoor(1.0), tf - 0.1)
    fx.add(O.whoosh(1.0, False, seed=8, amp=0.7), tf)
    fx.add(Tr.stamp(0.9), tf + 0.02)
    fx.add(O.pneumatic(0.6, seed=2), tf + 1.3)                                                    # the next one delivered
    t0 = cut("w_press")
    mus.add(Tr.brass_swell([38, 45, 50], E("w5") - t0 + 0.4, 0.9, seed=4, att=4.0), t0, 1.0)   # the ceiling sinking
    fx.add(O.rumble(E("w5") - t0 + 0.5, 0.8), t0)
    fx.add(DM.engine(E("w5") - t0, 0.4, seed=2, f0=40.0), t0)
    for k, tc in enumerate((S("w6") - 0.4, S("w6") - 0.18, E("w6") + 0.05, E("w6") + 0.25)):   # the smile forced wider in jerks
        fx.add(O._hp(Tr.porcelain_creak(0.6, seed=k), 4000), tc)
    # =========== III. THE ORACLE (royal): no drums - silk, choir, the theme warped
    card_hit(mus, fx, cut("k_3"), seed=3)
    a, b = cut("o_veils"), E("o6") + 0.2
    fx.add(Tr.silk(cut("o_points") - a + 0.6, 0.9, seed=4, rate=0.5), a)
    mus.add(Tr.choir([62, 66, 69], b - a, 0.6, vowel="a", attack=1.5), a, 0.8)
    drone(mus, a, b, (38, 45), 0.6, seed=7)
    theme_at(mus, a + 0.1, DM.wow(Tr.theme(0.4, 0.8, seed=3), depth=40.0, rate=0.5, flutter=6.0), 0.75, pan=0.4, until=cut("o_points") + 1.6)
    tp = Wx("o2", "four") - 0.1
    for j in range(4):                                                                            # four pins
        fx.add(O.whoosh(0.25, False, seed=j, amp=0.4), tp + j * 0.42 - 0.25)
        fx.add(DM.metal_hit(0.4, seed=j + 5, size=0.5), tp + j * 0.42)
        mus.add(DM.bell(86 - j * 2, 0.6, 2.0), tp + j * 0.42, 0.8)
    for i, (w, _t, _v) in enumerate(__import__("sc_oracle").INFER):                               # each guess engraved
        tw = Wx("o4", w) - 0.08
        mus.add(DM.bell(74 + [0, 3, 7, 10][i], 0.8, 2.5), tw, 0.8, pan=0.3 + 0.13 * i)
        fx.add(O.whir(0.5, 0.4, f=200.0 + 40 * i), tw)
    t0 = cut("o_mirror")
    fx.add(DM.whispers(b - t0, 0.8, seed=5), t0, 0.25)
    # =========== IV. THE SCALES (blood): the trance at full force, then everyone goes quiet
    card_hit(mus, fx, cut("k_4"), seed=4, big=1.3)
    a, b = cut("t_metro"), cut("t_library") + 1.6
    theme_at(mus, cut("k_4") + 0.15, DM.crush(DM.detune(Tr.theme(0.32, 0.8, seed=4), -0.4), bits=6, hold=4), 0.45, pan=0.55, until=a + 1.6)
    groove(mus, a, b, dict(bendir=0.75, darbuka=0.6, krakeb=0.35, clap=0.5), seed=4, until=b + 0.4)
    drone(mus, a, b + 0.8, (38, 45), 0.9, seed=8)
    pat = [("u", 1, 1.4), (None, 0.5, 0), ("a", 0.5, 1.0), ("u", 1, 1.1), (None, 1, 0)] * 2
    t = a
    while t < b - 1.0:
        mus.add(Tr.chant(pat, BEAT * 1.5, root=50, amp=1.0, seed=int(t)), t, 0.55)
        t += 7 * BEAT * 1.5
    mus.add(Tr.ghaita_phrase([(74, 1), (75, 0.5), (74, 0.5), (72, 1), (70, 1), (69, 2)], 0.2, 0.8, seed=12), cut("t_gate") + 0.1, 0.5, pan=0.4)
    mus.add(Tr.brass_swell([38, 45, 50, 57], 2.6, 0.9, seed=5, att=2.0), cut("t_metro") + 1.2, 0.8)
    td = Wx("t2", "detain") - 0.1
    fx.add(DM.metal_hit(0.8, seed=21, size=1.2), td + 0.25)                                      # the gate, the guards
    fx.add(DM.door_slam(0.7, seed=4), td + 0.6)
    fx.add(Y.alarm(0.8, 0.35, rate=6.0, f=1300.0), Wx("t3", "without") - 0.05)                  # FLAGGED
    tm = Wx("t4", "fifteen") - 0.1
    for i in range(15):                                                                           # fifteen matches, then wrong
        fx.add(Tr.stamp(0.35), tm + i * 0.07)
    tw = Wx("t4", "wrongly") - 0.1
    for i in range(15):
        fx.add(Tr.beep(330, 0.06, 0.35), tw + i * 0.05)
    tq = Wx("t5", "quiet:") - 0.1
    rngb = np.random.default_rng(3)
    for k in range(10):                                                                           # books shutting, one by one
        fx.add(DM.door_slam(0.22, seed=k), tq + rngb.uniform(0.0, 3.5), pan=rngb.uniform(0.2, 0.8))
    mus.add(tone(93, E("t5") - tq + 0.4, 0.8), tq)
    mus.add(DM.sub(26, E("t5") - tq, 0.4, att=1.5, rel=0.4), tq)
    # silence; then the scales slam; every exhibit turns its head
    mus.add(Tr.taiko(1.0, seed=1), T_SLAM, 1.0)
    mus.add(DM.boom(1.0, 36.0, 2.6), T_SLAM, 1.0)
    mus.add(Tr.tamtam(1.0, 5.0, seed=5), T_SLAM, 0.9)
    mus.add(Tr.choir([62, 63, 68, 74], 1.4, 1.0, vowel="a", attack=0.02), T_SLAM, 0.9)
    fx.add(DM.metal_hit(1.0, seed=31, size=1.6), T_SLAM)
    tt = Wx("t6", "Then") - 0.2
    for k in range(5):
        fx.add(O._hp(Tr.porcelain_creak(0.5, seed=k + 10, dur=0.2), 4500), tt + k * 0.11)
        fx.add(Tr.aperture(0.18, 0.1, seed=k + 60), tt + k * 0.11 + 0.05)
    mus.add(Tr.choir([38, 45], E("t6") - T_SLAM + 0.6, 0.8, vowel="o", attack=0.3), T_SLAM + 0.4, 0.7)
    # =========== the procession: her train whispering across the floor; a slow drum; the music box, out of tune
    a, b = cut("d_procession"), cut("n_mirror")
    fx.add(Tr.silk(b - a + 0.6, 1.0, seed=8, rate=0.35), a, 0.55)
    for k in range(int((b - a) / 1.2) + 1):
        mus.add(Tr.bendir("dum", 1.0, k), a + 0.1 + k * 1.2, 0.7)
    mus.add(Tr.choir([38, 45, 50], b - a + 0.4, 0.7, vowel="o", attack=1.0), a, 0.5)
    mb = O.music_box([(m + 12, bb) for m, bb in Tr.THEME], rate=lambda u: 1.0 - 0.35 * u, amp=0.9, seed=2, detune=lambda u: 70 * math.sin(u * 11))
    mus.add(mb, a + 0.15, 0.55, pan=0.6, until=b + 0.2)
    # =========== NADIA: the cold world - room tones, a sparse pulse, and every system's little sound
    a, b = cut("n_mirror"), cut("x_collapse")
    for k in range(int((cut("n_door") - a) / 0.6)):                                             # a low pulse, like a slow heart
        tt = a + 0.3 + k * 0.6
        mus.add(O.pizz(38, 0.8, seed=k), tt, 0.55 + 0.3 * k / 60.0)
        if k % 2 == 0:
            mus.add(DM.sub(26, 0.4, 0.25 + 0.2 * k / 60.0, att=0.01, rel=0.3), tt)
    mus.add(Tr.low_strings([50, 51], cut("n_door") - a, 0.7, seed=11, att=4.0), a, 0.6)
    fx.add(Tr.hum(cut("n_road") - a, 0.5), a)
    t0 = cut("n_road")
    fx.add(DM.engine(cut("n_call") - t0, 0.5, seed=3, f0=60.0), t0)
    for i in range(6):                                                                            # every junction: a shutter and a beep
        tt = t0 + 0.3 + i * (cut("n_call") - t0 - 0.4) / 6
        fx.add(Tr.shutter(0.5, seed=i), tt)
        fx.add(Tr.beep(1600, 0.05, 0.4), tt + 0.06)
    t0 = cut("n_call")
    fx.add(FX_MURMUR(cut("n_idle") - t0), t0, 0.6)
    for w in ("words,", "tone,", "face."):
        fx.add(Tr.beep(1200, 0.06, 0.45), Wx("n3", w) - 0.1)
    fx.add(Tr.ticks(Wx("n4", "Flagged:") - cut("n_idle"), 2.0, 0.6, seed=9), cut("n_idle"))
    fx.add(Y.error_tone(0.8), Wx("n4", "Flagged:") - 0.05)
    fx.add(DM.typewriter(8, 0.08, 0.5, seed=3), cut("n_union") + 0.2)
    fx.add(Y.error_tone(0.6), Wx("n5", "logs") - 0.3)
    for w in ("vitamins,", "unscented", "lotion."):                                              # the checkout
        fx.add(Tr.beep(2000, 0.07, 0.5), Wx("n6", w) - 0.1)
    fx.add(DM.sub(29, 1.2, 0.6, att=0.05, rel=0.6), Wx("n6", "lotion.") + 0.25)
    tx_ = cut("n_exhibit")                                                                         # the gallery breaks in
    mus.add(Tr.choir([62, 63, 69], 1.6, 0.8, vowel="a", attack=0.05), tx_, 0.7)
    mus.add(DM.bell(86, 0.8, 2.0), Wx("n6", "pregnant.") - 0.1, 0.7)
    fx.add(DM.vibrate(0.6, 0.5), cut("n_face") + 0.2)
    t0 = cut("n_vigil")
    fx.add(FX_MURMUR(cut("n_phone") - t0, quiet=True), t0, 0.5)
    fx.add(Tr.shutter(0.7, seed=9), Wx("n8", "matches") - 0.1)
    fx.add(Tr.beep(880, 0.25, 0.6), Wx("n8", "matches") + 0.25)
    t0 = cut("n_phone")
    tb = Wx("n9", "Baby") - 0.1
    fx.add(Y.error_tone(0.5), Wx("n9", "cut.") + 0.1)
    for k in range(14):                                                                           # notifications multiplying
        fx.add(DM.ding(0.25 + 0.02 * k, m=88 + (k % 3) * 3), tb + 0.08 * k ** 1.2, pan=rng.uniform(0.2, 0.8))
    # silence, then three knocks
    for k, tk_ in enumerate(KNOCKS):
        fx.add(Tr.knock(1.0, seed=k), tk_)
        mus.add(DM.sub(28, 0.35, 0.5, att=0.003, rel=0.25), tk_)
    t0 = cut("n_match")
    fx.add(O.siren(2.2, 0.35), t0 + 0.2)
    mus.add(Tr.low_strings([38, 39, 45], cut("x_collapse") - t0 + 0.4, 0.9, seed=12, att=1.0), t0, 0.9)
    fx.add(Y.alarm(0.6, 0.4, rate=5.0, f=1100.0), Wx("n11", "match") - 0.1)
    t0 = cut("n_scream")
    mus.add(Tr.brass_swell([38, 45, 51], cut("x_collapse") - t0 + 0.2, 0.9, seed=7, att=2.6), t0, 1.0)
    mus.add(DM.reverse_cymbal(1.4, 0.8, seed=6), T_COLLAPSE - 1.4)
    fx.add(Tr.glass_crack(0.9, seed=3), Wx("n12", "That's", 1) - 0.05)
    # =========== the collapse: drums, brass, chant, the theme as a war cry; glass and sand everywhere
    a, b = T_COLLAPSE, T_CUT
    groove(mus, a, b, dict(bendir=1.0, darbuka=0.8, krakeb=0.5, clap=0.7), seed=9, until=b)
    for k in range(int((b - a) / 0.6) + 1):
        mus.add(Tr.taiko(0.9 + 0.1 * (k % 2), seed=k), a + k * 0.6, 0.8 + 0.4 * (k / ((b - a) / 0.6)))
    mus.add(Tr.brass_swell([38, 45, 50, 57, 62], b - a, 1.0, seed=8, att=b - a - 0.6), a, 1.1)
    mus.add(Tr.choir([62, 66, 69, 74], b - a, 1.0, vowel="a", attack=1.5), a, 1.0)
    t = a
    while t < b - 0.6:
        mus.add(Tr.chant([("u", 1, 1.5), ("a", 0.5, 1.2), ("u", 0.5, 1.2), ("a", 1, 1.4)], BEAT * 1.5, root=50, seed=int(t * 10)), t, 0.7)
        t += 3 * BEAT * 1.5
    mus.add(Tr.ghaita_phrase([(m + 12, bb) for m, bb in Tr.THEME], 0.3, 1.0, seed=20, vib=2.0), a + 1.0, 0.75, pan=0.4)
    for i, (m, bb) in enumerate(Tr.THEME):                                                        # the theme hammered out by the brass
        tt = a + 1.6 + sum(x for _, x in Tr.THEME[:i]) * 0.3
        mus.add(Tr.brass_stab([m - 12, m], 0.9, seed=i, dur=bb * 0.3 * 0.95), tt, 0.7)
    fx.add(Tr.shatter(1.0, seed=8, dur=2.4), a + 0.02)
    fx.add(Tr.shatter(0.8, seed=9, dur=2.0), a + 0.6)
    fx.add(O.rumble(b - a, 1.0), a)
    fx.add(Tr.sand(b - a, 1.0, seed=10, gust=1.4), a + 0.9)
    fx.add(Y.wind(b - a, 0.9, seed=11), a + 0.9)
    for k in range(7):                                                                            # every door opening
        fx.add(DM.door_slam(0.5, seed=k + 20), S("x1") - 0.1 + 0.15 + k * 0.03, pan=0.2 + 0.1 * k)
    fx.add(Tr.aperture(0.8, 0.5, seed=70), S("x1") + 0.05)
    for k, key in enumerate(("o6", "e8", "t6")):                                                 # her own words, backwards, in the storm
        fx.add(wide(Tr.reversed_voice(TL.lines[key]["wav0"], VSR, pitch=-5.0 - k)), a + 0.25 + 0.55 * k, 0.45, until=S("x1") - 0.15)
    mus.add(DM.boom(1.0, 32.0, 1.0), b - 0.35, 1.0)
    # =========== the twist: the cut to silence; wind over salt; the theme snapping off; eight bells
    a, b = T_CUT + 0.75, cut("y_glass")
    fx.add(Y.wind(b - a + 0.5, 0.45, seed=12), a, until=E("y2") + 0.15)
    mus.add(tone(91, b - a, 0.9), a, until=E("y2") + 0.15)
    tg = Wx("y1", "real.") + 0.05
    fx.add(Tr.sand(1.6, 0.8, seed=13, gust=0.2), tg - 0.2)
    mus.add(DM.broken(Tr.theme(0.42, 0.8, seed=6), 0.55), a + 0.1, 0.7, until=tg + 0.4)
    tl = Wx("y1", "Every") - 0.1
    for i in range(8):
        mus.add(DM.bell(74 + Tr.HIJAZ[i] - 62, 0.5, 2.2), tl + i * 0.06 + 0.1, 0.7, pan=0.3 + 0.05 * i)
    t0 = cut("y_phone")
    mus.add(DM.sub(26, E("y2") - t0 + 0.2, 0.6, att=1.2, rel=0.2), t0)
    fx.add(DM.heartbeat(3, 62, 0.7), t0 + 0.3)
    fx.add(Y.wake_chime(0.4), Wx("y2", "hand") - 0.05)
    # silence; breath behind you; her whisper; the lunge
    t0 = S("y3") - 0.55
    fx.add(Tr.mask_breath(1.2, 1.1, 0.9, seed=4), t0, until=S("y3") + 0.12)                    # a breath behind you, then she speaks
    fx.add(wide(Tr.reversed_voice(TL.lines["y3"]["wav0"], VSR, pitch=-6.0)), t0, 0.12, until=S("y3"))
    fx.add(Tr.porcelain_creak(0.5, seed=30, dur=0.4), S("y3") - 0.5)
    mus.add(DM.sub(25, T_LUNGE - t0, 0.35, att=1.0, rel=0.1), t0, until=T_LUNGE)
    zr = cut("z_room") + 0.08                                                                     # cut off dead by the white room
    mus.add(Tr.brass_stab([37, 44, 50, 55, 61], 1.0, seed=9, dur=1.0), T_LUNGE, 1.0, until=zr)
    mus.add(Tr.choir([73, 74, 79, 80], 1.2, 1.0, vowel="a", attack=0.01), T_LUNGE, 1.0, until=zr)
    mus.add(DM.boom(1.0, 38.0, 2.4), T_LUNGE, 1.0, until=zr)
    fx.add(Tr.shatter(0.9, seed=12, dur=1.6), T_LUNGE, until=zr)
    fx.add(Tr.aperture(1.0, 0.3, seed=80), T_LUNGE - 0.02, until=zr)
    # =========== the white room again: hum, a slow monitor, one chord, the theme alone and slow
    a, b = cut("z_room"), TL.total
    fx.add(Tr.hum(b - a, 0.6), a)
    fx.add(Tr.monitor(b - a - 0.3, 58, 0.55), a + 0.3)
    mus.add(Tr.low_strings([38, 45, 53, 57], cut("z_final") - a + 1.0, 0.8, seed=14, att=1.6), a, 0.6)
    theme_at(mus, a + 0.6, Tr.theme(0.62, 0.7, seed=9, transpose=-2, breath=0.24), 0.6, pan=0.5, until=cut("z_final") + 0.2)
    # the last image: one long tone; a monitor flatlining
    t0 = cut("z_final")
    mus.add(tone(86, b - t0 + 0.3, 1.0), t0)
    mus.add(Tr.choir([50, 57], b - t0, 0.5, vowel="o", attack=1.0), t0, 0.6)
    fx.add(Tr.beep(1040, b - t0 - 0.4, 0.4), t0 + 0.6)


def FX_MURMUR(dur, quiet=False):
    import fxlib as FXL
    return FXL.murmur(dur, 0.5 if quiet else 0.8, seed=9)


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


LEVEL = {"NAR": -16.0, "CURATOR": -15.0, "SYSTEM": -16.5, "NADIA": -16.0}
LINE_LEVEL = {"n12": 4.0, "n7": -1.0, "n10": 2.0}                 # her breaking point louder than anything she has said; her whisper softer


def voices():
    """The narrator close and warm; the Curator in a vast hall; the machine dry; Nadia in small cold rooms."""
    buses = {k: np.zeros((2, N_)) for k in LEVEL}
    for key in TL.order:
        Ln = TL.lines[key]
        who = Ln["who"]
        up = signal.resample_poly(Ln["wav"].astype(np.float64), SR, VSR)
        r = np.sqrt((up ** 2).mean()) + 1e-12
        up = up * db(LEVEL.get(who, -16.0) + LINE_LEVEL.get(key, 0.0)) / r
        if who == "CURATOR":
            d = int(0.007 * SR)
            sig = np.stack([up, np.concatenate([np.zeros(d), up])[: len(up)] * 0.92])
        else:
            sig = np.stack([up, up])
        i = int(Ln["start"] * SR)
        j = min(N_, i + sig.shape[1])
        buses[who][:, i:j] += sig[:, : j - i]
    out = reverb(buses["NAR"], 0.06, 0.6, seed=3)
    out += reverb(buses["CURATOR"], 0.28, 4.0, seed=4, predelay=0.06)
    out += reverb(buses["SYSTEM"], 0.05, 0.22, seed=5)
    out += reverb(buses["NADIA"], 0.12, 0.42, seed=6)
    return out


# ------------------------------------------------------------------ the mix

def smooth(x, sec):
    """A centred moving average over sec seconds (edges held), in linear time."""
    from scipy.ndimage import uniform_filter1d
    return uniform_filter1d(np.asarray(x, np.float64), size=max(1, int(sec * SR)), mode="nearest")


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


NEED = {"NAR": 9.5, "CURATOR": 13.0}             # the voice over the beds in the speech band (others: 11)
BED = -2.0                                       # the beds' ceiling between lines, against the average line (dB)
# (time, ceiling dB over the average line, seconds): the moments allowed to be loud
HITS = [(0.0, 15.0, 1.2), (T_TITLE - 0.05, 12.0, 1.6), (cut("k_1"), 10.0, 1.0), (cut("k_2"), 10.0, 1.2), (cut("k_3"), 10.0, 1.2),
        (cut("k_4"), 12.0, 1.2), (T_EYES, 18.0, 0.9), (T_SLAM, 18.0, 1.2)] + [(k, 17.0, 0.3) for k in KNOCKS] + [
        (T_COLLAPSE, 15.0, S("x1") - T_COLLAPSE), (E("x1") - 0.1, 15.0, T_CUT - E("x1") + 0.1), (T_LUNGE, 19.0, 0.4)]
SAT = {T_EYES: 4.0, T_SLAM: 5.0, T_LUNGE: 5.0, T_COLLAPSE: 3.0}
BOOST = {0.0: (3.0, 1.0), T_EYES: (5.0, 0.8), T_SLAM: (6.0, 1.1), T_COLLAPSE: (4.0, S("x1") - T_COLLAPSE), E("x1") - 0.1: (5.0, T_CUT - E("x1") + 0.1),
         T_LUNGE: (7.0, 0.4)}
BOOST.update({k: (5.0, 0.3) for k in KNOCKS})
CEIL = -1.5
TARGET = -15.0
# the hushed passages, pulled down (voice and all): the desert at dawn, the oracle, the salt flat after the collapse
QUIET = [(cut("c_dawn") + 0.1, cut("k_1") - 0.15, -4.5), (T_CUT + 0.75, cut("y_glass"), -4.5), (cut("z_room") + 0.2, TL.total, -3.5)]
STEMS = {}
STEM_GAIN = [1.0]


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
    music = reverb(mus_x, 0.24, 2.6, seed=2)
    music = signal.sosfilt(signal.butter(4, 28 / (SR / 2), "high", output="sos"), music, axis=1)
    fxx = reverb(fx_x, 0.16, 1.2, seed=3)
    fxx = signal.sosfilt(signal.butter(4, 28 / (SR / 2), "high", output="sos"), fxx, axis=1)
    vo = compress(presence(voices(), 3200, 2.5))
    # levels: the chapter IV trance sets the music's scale; the effects sit a little under it
    ref = music[:, int(cut("t_metro") * SR):int((cut("t_metro") + 4.0) * SR)]
    music = music * db(-15.0) / (np.sqrt((ref ** 2).mean()) + 1e-12)
    on = np.abs(fxx).max(axis=0) > 1e-4
    fxx = fxx * db(-17.0) / (np.sqrt((fxx[:, on] ** 2).mean()) + 1e-12)
    lp = signal.butter(4, 90 / (SR / 2), "low", output="sos")
    for t in SAT:
        a, b = max(0, int((t - 0.05) * SR)), min(N_, int((t + 1.3) * SR))
        w = np.ones(b - a)
        f = int(0.05 * SR)
        w[:f] = np.linspace(0, 1, f)
        w[-int(0.25 * SR):] = np.linspace(1, 0, int(0.25 * SR))
        for x in (music, fxx):
            x[:, a:b] -= 0.6 * w[None] * signal.sosfiltfilt(lp, x[:, a:b], axis=1)
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
    for t, (gdb, dur) in BOOST.items():
        a, b = max(0, int((t - 0.03) * SR)), min(N_, int((t + dur) * SR))
        env = np.ones(b - a)
        f = min(b - a, int(0.03 * SR))
        env[:f] = np.linspace(0, 1, f)
        g2 = min(b - a, int(0.25 * SR))
        env[-g2:] = np.minimum(env[-g2:], np.linspace(1, 0, g2))
        g = 1 + (db(gdb) - 1) * env
        music[:, a:b] *= g[None]
        fxx[:, a:b] *= g[None]
    # duck the beds under every line until the voice clears them by NEED dB in the speech band
    band = lambda x: signal.sosfilt(signal.butter(2, [300 / (SR / 2), 4000 / (SR / 2)], "band", output="sos"), x.mean(axis=0))
    sos = signal.butter(4, [300 / (SR / 2), 4000 / (SR / 2)], "band", output="sos")
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

    for _ in range(30):
        ride = rides()
        bb = B1 * ride + B2 * ride ** 0.12
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
    ride_rest = ride ** 0.12
    music = music_b * ride[None] + (music - music_b) * ride_rest[None]
    fxx = fxx_b * ride[None] + (fxx - fxx_b) * ride_rest[None]
    from scipy.ndimage import minimum_filter1d
    v_rms = np.sqrt(np.mean([(vo[:, int(TL.s(k) * SR):int(TL.e(k) * SR)] ** 2).mean() for k in TL.order]))
    beds = music + fxx
    env = np.sqrt(smooth((beds ** 2).mean(axis=0), 0.4)) + 1e-9
    tgt = np.full(N_, v_rms * db(BED))
    for t, lvl, dur in HITS:
        tgt[max(0, int((t - 0.05) * SR)):int((t + dur) * SR)] = v_rms * db(lvl)
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
    music, fxx, vo = music * dead[None], fxx * dead[None], vo * dead[None]
    qg = np.ones(N_)
    for a, b, g in QUIET:
        qg[int(a * SR):int(b * SR)] = db(g)
    qg = smooth(qg, 0.6)
    mix = mix * qg[None]
    music, fxx, vo = music * qg[None], fxx * qg[None], vo * qg[None]
    pre = np.sqrt((mix ** 2).mean()) + 1e-12
    mix = loudness(mix, TARGET)
    STEM_GAIN[0] = (np.sqrt((mix ** 2).mean()) + 1e-12) / pre
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


def aac_safe(x, target=-1.2, rates=("192k", "256k"), rounds=3):
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
    from scipy.io import wavfile
    for k, v in STEMS.items():                                      # at their true level in the mix, as float (pre-limiter peaks kept)
        wavfile.write(os.path.join(HERE, "build", f"stem_{k}.wav"), SR, (v * STEM_GAIN[0]).T.astype(np.float32))
    print("audio", round(mix.shape[1] / SR, 2), "s in", round(time.time() - t0, 1), "s")
