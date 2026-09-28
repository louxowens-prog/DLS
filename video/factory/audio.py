"""Soundtrack: a 1971 studio-musical score for a factory of thinking machines. Writes build/audio.wav (48 kHz stereo).

Cues (read off the edit):
  cold open   low strings and a slow celesta; a harp swell as she 'finds a way to think bigger'; a brass title sting
  grey town   a drab D-minor waltz: pizzicato bass, a lonely clarinet, the rain, a ticking clock
  the ticket  a celesta glissando, harp, and an 'ahh' choir blooming open
  newsreel    the film-leader beep, then a brassy march (tuba oom-pah, snare, trumpets) squeezed through an old speaker
  the host    a whimsical bassoon-and-pizzicato theme; low cello tremolo and a theremin when he turns menacing
  the ballad  (after dead silence at the door) harp, strings, celesta and a soft choir under the host's half-sung song
  the rooms   a light pizzicato underscore and each room's machine: whirring, stretching, pneumatic hiss and clunks,
              bubbling and an oven bell; comic effects for each guest's fate, and the same music-box phrase every time
  the chants  marimba, tuba oom-pah, woodblock and brushed snare; the workers' voices in a tiny layered chorus
  the tunnel  a dissonant organ cluster, theremin, reversed swells and a pulse that speeds up - then dead silence
  the end     warm strings, the ballad's tune on celesta and piano; a music box plays it out
Three true silences (every bus cut): the door, the end of the tunnel, the host's outburst.
A warm, slightly vintage mix: tape saturation, a gentle top-end roll-off, a wow on the strings, moderate width.
"""
import os
import wave

import numpy as np
from scipy import signal

import orch as P
from cues import C, ls
from edit import EDIT, first
from script import ANN, DOCTOR, FARMER, HOST, MIRROR, NAR, SONGS, STUDENT, WORKERS
from timeline import TL
from voice import SR as VSR

SR = P.SR
HERE = os.path.dirname(os.path.abspath(__file__))
N = int((TL.total + 0.6) * SR)
S, E, W = TL.s, TL.e, TL.word
f = first


def db(v):
    return 10 ** (v / 20)


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


def chord(root, kind):
    iv = {"maj": (0, 4, 7), "min": (0, 3, 7), "maj7": (0, 4, 7, 11), "min7": (0, 3, 7, 10), "7": (0, 4, 7, 10),
          "dim": (0, 3, 6), "add9": (0, 4, 7, 14)}[kind]
    return [root + i for i in iv]


PROG = {
    "ballad": [(65, "maj"), (62, "min"), (58, "maj7"), (60, "7")],        # F  Dm  Bbmaj7  C7
    "chant": [(60, "maj"), (65, "maj"), (67, "7"), (60, "maj")],          # C  F  G7  C
    "waltz": [(62, "min"), (58, "maj"), (55, "min"), (57, "7")],          # Dm  Bb  Gm  A7
    "host": [(65, "maj"), (70, "maj"), (60, "7"), (65, "maj")],           # F  Bb  C7  F
    "march": [(58, "maj"), (63, "maj"), (65, "7"), (58, "maj")],          # Bb  Eb  F7  Bb
    "room": [(67, "maj"), (64, "min"), (60, "maj"), (62, "7")],           # G  Em  C  D7
    "warm": [(65, "add9"), (62, "min7"), (58, "maj7"), (60, "7")],         # Fadd9 Dm7 Bbmaj7 C7
}
SCALE = {"ballad": [72, 74, 77, 79, 81, 84], "chant": [72, 74, 76, 79, 81, 84]}
BALLAD_TUNE = [(77, 1), (81, 1), (84, 2), (82, 1), (81, 1), (79, 2), (77, 1), (74, 1), (77, 2), (72, 1), (76, 1), (77, 3)]


# ------------------------------------------------------------------ building blocks

def bed(bus, style, t0, t1, bpm, level=1.0, parts=("pad",), seed=0):
    """A generic underscore in a style: pad, pizz bass, arpeggio, reed tune, glock, march, oom-pah, marimba."""
    beat = 60.0 / bpm
    prog = PROG[style]
    nb = int((t1 - t0) / beat)
    for b in range(0, nb, 4):
        root, kind = prog[(b // 4) % len(prog)]
        ch = chord(root, kind)
        t = t0 + b * beat
        d = min(4 * beat, t1 - t)
        if d <= 0.05:
            break
        if "pad" in parts:
            bus.add(P.strings(ch[:2], d, 1.0, seed=b), t, 0.45 * level, pan=0.25)
            bus.add(P.strings(ch[1:], d, 1.0, seed=b + 7), t, 0.45 * level, pan=0.75)
        if "pizz" in parts:
            for k in range(4):
                if t + k * beat < t1:
                    bus.add(P.pizz(ch[0] - 24 + (7 if k % 2 else 0), seed=b + k), t + k * beat, 0.5 * level, pan=0.28)
        if "arp" in parts:
            for k in range(8):
                if t + k * beat / 2 < t1:
                    bus.add(P.harp(ch[k % len(ch)] + (12 if k >= 4 else 0)), t + k * beat / 2, 0.35 * level, pan=0.15 + 0.1 * k)
        if "celesta" in parts:
            bus.add(P.celesta(ch[-1] + 12), t, 0.35 * level, pan=0.8)
        if "glock" in parts:
            for k in (0, 2):
                if t + k * beat < t1:
                    bus.add(P.glock(ch[k % len(ch)] + 24), t + k * beat, 0.18 * level, pan=0.82)
        if "reed" in parts:
            for k in range(2):
                if t + k * 2 * beat < t1:
                    bus.add(P.reed(ch[(k + b // 4) % len(ch)] + (0 if style != "waltz" else -12), beat * 1.8, seed=b + k,
                                   dark=style in ("host", "room")), t + k * 2 * beat, 0.5 * level, pan=0.72)
        if "oompah" in parts:
            for k in range(4):
                if t + k * beat < t1:
                    if k % 2 == 0:
                        bus.add(P.tuba(ch[0] - 24 + (7 if k == 2 else 0), beat * 0.8), t + k * beat, 0.6 * level, pan=0.4)
                    else:
                        bus.add(P.pizz(ch[1], seed=k), t + k * beat, 0.35 * level, pan=0.7)
        if "march" in parts:
            for k in range(4):
                if t + k * beat < t1:
                    bus.add(P.snare(0.35 + 0.25 * (k % 2), seed=b + k), t + k * beat, 0.5 * level, pan=0.5)
                    bus.add(P.snare(0.25, seed=b + k + 50), t + k * beat + beat / 2, 0.35 * level, pan=0.5)
            bus.add(P.brass(ch[1:] + [ch[0] + 12], beat * 1.5, 1.0, seed=b), t, 0.45 * level, pan=0.5)
            bus.add(P.brass([ch[0] + 12, ch[2] + 12], beat * 0.9, 1.0, seed=b + 1), t + 2.5 * beat, 0.35 * level, pan=0.55)
        if "marimba" in parts:
            for k in range(8):
                if t + k * beat / 2 < t1:
                    bus.add(P.marimba([ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 12][k % 4]), t + k * beat / 2, 0.5 * level,
                            pan=0.15 + 0.7 * (k % 2))
            for k in (1, 3):
                if t + k * beat < t1:
                    bus.add(P.woodblock(0.8, 1100), t + k * beat, 0.3 * level, pan=0.8)


def choir_ahh(bus, style, t0, t1, bpm, level=1.0):
    beat = 60.0 / bpm
    prog = PROG[style]
    for b in range(0, int((t1 - t0) / beat), 4):
        root, kind = prog[(b // 4) % len(prog)]
        ch = chord(root, kind)
        d = min(4 * beat, t1 - (t0 + b * beat))
        for i, m in enumerate(ch[:3]):
            bus.add(P.voices("a", m, d, 0.9, seed=b + i), t0 + b * beat, 0.16 * level, pan=0.12 + 0.38 * i)


def guide(bus, key, style, timbre="flute"):
    """A guide melody: one note per word of the half-sung lyric, riding the song's scale."""
    L = TL.lines[key]
    sc = SCALE[style]
    words = L["words"]
    n = len(words)
    idx = int(key.split("_")[1])
    for i, (w, a, b) in enumerate(words):
        u = i / max(1, n - 1)
        step = int(round(np.sin(np.pi * u) * (3 if idx % 2 == 0 else 2))) + (idx % 2)
        m = sc[min(len(sc) - 1, max(0, step))]
        if i == n - 1:
            m = sc[0] if idx % 2 else sc[2]
        if style == "ballad":
            bus.add(P.celesta(m + 12, 0.8), a, 0.35, pan=0.6)
            bus.add(P.lead(m, max(0.12, b - a) * 0.95, "flute", seed=i), a, 0.35, pan=0.45)
        else:
            bus.add(P.marimba(m + 12), a, 0.5, pan=0.55)


def music_box_cue(bus, t, level=1.0):
    """The recurring cue: the same four music-box notes every time a guest is dealt with."""
    bus.add(P.music_box([(84, 1), (79, 1), (76, 1), (72, 2)], amp=1.0, seed=3), t, 0.7 * level, pan=0.62)


def dead_air():
    """True silence: every bus cut (only a voice may speak; here none does)."""
    return [(E("g3") + 0.12, S("s1") - 0.02),
            (E("t1c") + 0.1, S("t2") - 0.06),
            (E("x1") + 0.08, S("x2") - 0.06)]


# ------------------------------------------------------------------ the score

def score(mus, lead, choir, amb):
    # cold open: low strings, a slow celesta; a harp swell as she finds a way
    mus.add(P.strings([50, 57, 62, 65], f("cold_glow") - 0.0, 1.0, seed=1), 0.0, 0.6)
    for k in range(8):
        mus.add(P.celesta([74, 77, 81, 77, 72, 74, 76, 74][k]), 0.2 + k * 0.55, 0.28, pan=0.6)
    for k in range(10):
        mus.add(P.harp([65, 69, 72, 77, 81, 84, 89, 93, 96, 101][k]), f("cold_glow") + 0.3 + k * 0.06, 0.28, pan=0.3 + 0.04 * k)
    mus.add(P.strings([65, 69, 72, 77], f("title") - f("cold_glow") + 0.3, 1.0, seed=2), f("cold_glow") + 0.2, 0.7)
    # the title sting
    mus.add(P.brass([58, 65, 70, 74], 1.2, 1.0, seed=3), f("title"), 0.9)
    mus.add(P.timpani(46, 1.0), f("title"), 0.8)
    mus.add(P.cymbal(1.0, 2.0), f("title") + 0.02, 0.5)
    # the grey town: a drab waltz, the rain
    bed(mus, "waltz", f("town"), f("wrapper"), 72, 0.8, ("pad", "pizz", "reed"), seed=4)
    rain_len = f("wrapper") - f("town") + 0.5
    nr = int(rain_len * SR)
    rain = np.stack([P._bp(P._noise(nr, 9), 1200, 8000), P._bp(P._noise(nr, 19), 1200, 8000)]) * 0.07
    amb.add(rain, f("town"), 1.0)
    for k in range(int((f("kitchen") - f("office")) / 0.5)):
        amb.add(P.tick(1.0, tock=k % 2 == 1), f("office") + k * 0.5, 0.35)
    # the ticket
    for k in range(14):
        mus.add(P.celesta(72 + [0, 2, 4, 5, 7, 9, 11][k % 7] + 12 * (k // 7)), C["ticket_flash"] - 0.2 + k * 0.045, 0.3, pan=0.3 + 0.03 * k)
    choir_ahh(choir, "ballad", C["ticket_flash"], f("news1"), 80, 1.3)
    mus.add(P.strings([65, 69, 72, 77], f("news1") - C["ticket_flash"], 1.0, seed=5), C["ticket_flash"], 0.7)
    # the newsreel: beep, march
    amb.add(P.beep(0.25), f("news1") + 0.05, 1.0)
    bed(mus, "march", f("news1") + 0.45, f("gates"), 116, 0.9, ("oompah", "march"), seed=6)
    # the host: whimsical, then menacing
    bed(mus, "host", f("gates"), f("host_menace"), 104, 0.8, ("pizz", "reed", "glock"), seed=7)
    mus.add(P.drone(E("g3") - f("host_menace") + 0.1, root=36, seed=2), f("host_menace"), 0.8)
    mus.add(P.theremin(330, 520, E("g3") - f("host_menace"), 1.0), f("host_menace"), 0.35, pan=0.6)
    # the ballad (the door opens in silence first)
    s1 = TL.songs["s1"]
    bed(mus, "ballad", s1["start"], s1["end"], s1["bpm"], 1.0, ("pad", "arp", "celesta"), seed=8)
    choir_ahh(choir, "ballad", s1["start"], s1["end"], s1["bpm"], 1.0)
    for l in s1["lines"]:
        guide(lead, l["key"], "ballad")
    mus.add(P.cymbal(1.0, 3.0, swell=True), s1["start"] - 0.02, 0.0)
    mus.add(P.timpani(41, 1.0), s1["start"] + 60 / s1["bpm"] * 4, 0.5)
    # after the song: the ballad chords carry "this is what it feels like"
    bed(mus, "ballad", s1["end"], f("plaque1"), 80, 0.75, ("pad", "arp"), seed=9)
    # the rooms: a light underscore, and each room's machine
    rooms = [("plaque1", "w1"), ("plaque2", "w2"), ("plaque3", "w3"), ("plaque4", "w4")]
    for k, (pl, sk) in enumerate(rooms):
        bed(mus, "room", f(pl), TL.songs[sk]["start"] - 0.05, 108, 0.55, ("pizz", "reed", "glock"), seed=10 + k)
    amb.add(P.whir(f("copier") + 2.0 - f("room1"), 1.0, 85), f("room1"), 0.8)
    for k in range(int((f("copier") - f("room1")) / 0.6)):
        amb.add(P.stretch(0.5, up=k % 2 == 0), f("room1") + k * 0.6, 0.25, pan=0.4 + 0.2 * (k % 2))
    for k in range(int((f("room2_flag") - f("room2")) / 1.43)):
        amb.add(P.clunk(1.0, seed=k), f("room2") + 0.3 + k * 1.43, 0.8)
        amb.add(P.pneumatic(1.0, seed=k), f("room2") + 0.9 + k * 1.43, 0.5, pan=0.3 + 0.4 * (k % 2))
    amb.add(P.whir(f("believer") - f("room2") + 3, 1.0, 60, seed=2), f("room2"), 0.6)
    for k in range(10):
        amb.add(P.celesta(96 + (k % 3) * 3), f("room3") + k * 0.4, 0.12, pan=0.2 + 0.06 * k)
    amb.add(P.bubbling(f("rusher") - f("room4_fizz") + 1.5, 1.0, seed=3), f("room4_fizz"), 0.7)
    amb.add(P.ding(1.0), f("room4_plan") + 0.9, 0.6)
    # the guests' fates, and the music box each time
    amb.add(P.gloop(1.0, 1), C["gulp"] - 0.05, 0.9)
    amb.add(P.stretch(1.1, 1.0, up=True), C["gulp"] + 0.05, 0.7)
    amb.add(P.boing(1.0), C["gulp_up"] + 0.35, 0.5)
    amb.add(P.slurp(0.9), C["sucked"], 1.0)
    amb.add(P.pneumatic(1.0, seed=9, dur=0.8), C["sucked"] + 0.2, 0.6)
    amb.add(P.slide_whistle(False, 1.3), C["shrink"], 0.55)
    amb.add(P.trapdoor(1.0), C["drop"] - 0.02, 0.9)
    for t in (C["gulp_up"] + 0.6, C["sucked"] + 0.9, C["shrink"] + 1.2, C["drop"] + 0.9):
        music_box_cue(amb, t)
    # the chants
    for sk in ("w1", "w2", "w3", "w4"):
        sg = TL.songs[sk]
        bed(mus, "chant", sg["start"], sg["end"], sg["bpm"], 1.0, ("oompah", "marimba"), seed=20)
        for l in sg["lines"]:
            guide(lead, l["key"], "chant")
        for k in range(int((sg["end"] - sg["start"]) / sg["beat"])):
            mus.add(P.snare(0.18, seed=k), sg["start"] + k * sg["beat"] + sg["beat"] / 2, 0.35, pan=0.5)
    # the tunnel
    t0, t1 = f("tunnel_in"), E("t1c") + 0.1
    mus.add(P.organ([36, 37, 42, 43, 48, 49], t1 - t0), t0, 0.9)
    for k in range(4):
        mus.add(P.theremin(300 + 90 * k, 900 - 120 * k, 2.6, 1.0, vib=6 + k), t0 + 0.5 + k * 2.3, 0.4, pan=0.2 + 0.2 * k)
    mus.add(P.reverse_swell(2.0), E("t1c") - 1.9, 0.8)
    tt, k = t0 + 0.4, 0
    while tt < t1 - 0.1:                                                  # a pulse that speeds up
        mus.add(P.timpani(34 + (k % 2) * 5, 1.0), tt, 0.55)
        tt += max(0.14, 0.75 - (tt - t0) * 0.06)
        k += 1
    # calm, the lesson, the appointment
    bed(mus, "warm", S("t2") - 0.05, f("lesson"), 72, 0.55, ("pad", "arp"), seed=30)
    bed(mus, "chant", f("lesson"), f("clinic"), 120, 0.45, ("marimba",), seed=31)
    for key in ("e1",):
        pass
    bed(mus, "warm", f("clinic"), f("anger"), 76, 0.7, ("pad", "reed"), seed=32)
    for k in range(8):
        mus.add(P.celesta(84 + [0, 4, 7, 12, 16, 19, 24, 28][k]), C["right_q"] + k * 0.06, 0.25, pan=0.3 + 0.05 * k)
    # the host explodes
    for k in range(4):
        mus.add(P.brass([49, 55, 61, 67] if k % 2 else [48, 54, 60, 66], 0.5, 1.0, seed=40 + k), f("anger") + 0.2 + k * 0.95, 0.9)
    mus.add(P.snare_roll(E("x1") - f("anger"), 0.9), f("anger"), 0.6)
    mus.add(P.cymbal(1.0, E("x1") - f("anger"), swell=True), f("anger"), 0.6)
    # the warm reveal, the ticket, the balcony, the true story, the end
    bed(mus, "warm", S("x2") - 0.05, f("end") + 0.1, 72, 0.9, ("pad", "arp"), seed=50)
    choir_ahh(choir, "warm", C["flip"], f("story1"), 72, 1.0)
    for k in range(12):
        mus.add(P.harp(65 + [0, 4, 7, 12, 16, 19, 24, 28, 31, 36, 40, 43][k]), C["flip"] + 0.2 + k * 0.05, 0.3, pan=0.3 + 0.03 * k)
    mus.add(P.timpani(41, 1.0), f("balcony"), 0.6)
    beat = 60 / 72
    for i, (m, b) in enumerate(BALLAD_TUNE):                            # the ballad's tune, on celesta, over the balcony
        tt = f("balcony") + sum(bb for _, bb in BALLAD_TUNE[:i]) * beat * 0.5
        if tt < f("story1"):
            mus.add(P.celesta(m, 1.0), tt, 0.4, pan=0.55)
    for i, (m, b) in enumerate(BALLAD_TUNE):                            # and on a quiet piano under the true story
        tt = f("story1") + 0.4 + sum(bb for _, bb in BALLAD_TUNE[:i]) * beat
        if tt < f("end"):
            mus.add(P.piano([m - 12], b * beat, 1.0, seed=i), tt, 0.35, pan=0.5)
    mus.add(P.music_box(BALLAD_TUNE, rate=lambda u: 1 - 0.3 * u, amp=1.0, seed=5), f("end") + 0.1, 0.55, pan=0.5)


# ------------------------------------------------------------------ voices

def _bp(x, lo, hi):
    return signal.sosfilt(signal.butter(2, [lo / (SR / 2), hi / (SR / 2)], "band", output="sos"), x)


def voices():
    out = np.zeros((2, N))
    for key in TL.order:
        L = TL.lines[key]
        who = L["who"]
        up = signal.resample_poly(L["wav"].astype(np.float64), SR, VSR)
        r = np.sqrt((up ** 2).mean()) + 1e-12
        lvl = {NAR: -17.0, HOST: -17.0, ANN: -17.5, WORKERS: -18.0, MIRROR: -17.0}.get(who, -17.0) + (1.5 if L["song"] else 0.0)
        if key == "x1":
            lvl += 3.0
        up = up * db(lvl) / r
        if who in (ANN, FARMER, STUDENT):                                # the newsreel's old speaker
            up = np.tanh(2.2 * _bp(up, 280, 3600) / (np.abs(up).max() + 1e-9)) * np.abs(up).max() * 0.8
        if key == "x1":
            up = np.tanh(1.8 * up / (np.abs(up).max() + 1e-9)) * np.abs(up).max()
        sig = np.stack([up, up])
        if who == WORKERS:                                               # a tiny chorus: the same voice, layered
            refrain = "Think" in L["spoken"] or "thinking's up" in L["spoken"]
            layers = [(0, 1.0, 0.5)] + ([(0.012, 0.8, 0.2), (0.021, 0.8, 0.8), (0.03, 0.6, 0.35)] if refrain else [(0.015, 0.4, 0.3)])
            sig = np.zeros((2, int(len(up) * 1.05) + int(0.05 * SR)))
            for k, (dl, g, pan) in enumerate(layers):
                o = int(dl * SR)
                v = signal.resample(up, int(len(up) * (1 + 0.012 * k))) if k else up
                sig[0, o:o + len(v)] += v * g * np.sqrt(1 - pan) * 1.2
                sig[1, o:o + len(v)] += v * g * np.sqrt(pan) * 1.2
        if who in (MIRROR, HOST) and (who == MIRROR or key in ("t1a", "t1b", "t1c", "t2", "g3")):
            tail = np.zeros((2, int(1.0 * SR)))
            sig = np.concatenate([sig, tail], axis=1)
            for k, (dl, g) in enumerate(((0.18, 0.3), (0.36, 0.16), (0.54, 0.08))):
                o = int(dl * SR)
                sig[k % 2, o:] += sig[0, :-o] * g
        i = int(L["start"] * SR)
        j = min(N, i + sig.shape[1])
        out[:, i:j] += sig[:, : j - i]
    return out


# ------------------------------------------------------------------ mix

def reverb(x, wet=0.1, rt60=0.8, seed=8):
    rng = np.random.default_rng(seed)
    t = np.arange(int(rt60 * 1.4 * SR)) / SR
    ir = np.stack([rng.normal(0, 1, len(t)) * np.exp(-6.9 * t / rt60) for _ in range(2)])
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    y = np.stack([signal.fftconvolve(x[c], ir[c])[: x.shape[1]] for c in range(2)])
    return x * (1 - wet) + y * wet


def vintage(x):
    """Tape warmth: gentle saturation, a soft top-end roll-off, a little wow."""
    x = np.tanh(1.3 * x) / 1.3
    x = signal.sosfilt(signal.butter(2, 10500 / (SR / 2), "low", output="sos"), x, axis=1)
    x = signal.sosfilt(signal.butter(2, 40 / (SR / 2), "high", output="sos"), x, axis=1)
    n = x.shape[1]
    t = np.arange(n) / SR
    d = 0.0009 * SR * (0.5 + 0.5 * np.sin(2 * np.pi * 0.45 * t))
    idx = np.clip(np.arange(n) - d, 0, n - 1)
    i0 = np.floor(idx).astype(int)
    fr = idx - i0
    i1 = np.clip(i0 + 1, 0, n - 1)
    return x[:, i0] * (1 - fr) + x[:, i1] * fr


def mono_safe(x, max_ratio=0.45, hop=1024):
    mid, side = 0.5 * (x[0] + x[1]), 0.5 * (x[0] - x[1])
    n = len(mid) // hop
    em = np.convolve((mid[: n * hop] ** 2).reshape(n, hop).mean(axis=1), np.ones(8) / 8, "same")
    es = np.convolve((side[: n * hop] ** 2).reshape(n, hop).mean(axis=1), np.ones(8) / 8, "same")
    g = np.minimum(1.0, np.sqrt(max_ratio * em / (es + 1e-12)))
    g = np.interp(np.arange(len(side)), np.arange(n) * hop + hop / 2, g)
    return np.stack([mid + side * g, mid - side * g])


def build():
    mus, lead, choir, amb = Bus(), Bus(), Bus(), Bus()
    score(mus, lead, choir, amb)
    music = reverb(mus.x, 0.18, 1.4) + reverb(lead.x, 0.25, 1.6) + reverb(choir.x, 0.35, 2.0)
    newsreel = np.zeros(N)                                               # the march through an old speaker
    newsreel[int(f("news1") * SR):int(f("gates") * SR)] = 1.0
    newsreel = np.convolve(newsreel, np.ones(SR // 20) / (SR // 20), "same")
    squeezed = np.stack([_bp(music[c], 300, 3800) for c in range(2)]).mean(axis=0, keepdims=True).repeat(2, axis=0) * 1.6
    music = music * (1 - newsreel) + squeezed * newsreel
    music = vintage(music) + reverb(amb.x, 0.15, 1.0)
    dead = np.ones(N)
    for a, b in dead_air():
        dead[int(a * SR):int(b * SR)] = 0.0
    dead = np.convolve(dead, np.ones(int(0.015 * SR)) / int(0.015 * SR), "same")
    music = music * dead

    vo = reverb(voices(), 0.07, 0.6) * dead                              # echoes don't ring into the silences
    from scipy.ndimage import maximum_filter1d
    raw = np.convolve(np.abs(vo.mean(axis=0)), np.ones(SR // 20) / (SR // 20), mode="same")
    raw = np.clip(raw / (np.percentile(raw[raw > 1e-5], 80) + 1e-9), 0, 1)
    env = maximum_filter1d(raw, size=int(0.45 * SR), origin=-int(0.12 * SR))
    env = np.convolve(env, np.ones(SR // 12) / (SR // 12), mode="same")
    insong = np.zeros(N)
    for Sg in TL.songs.values():
        insong[int(Sg["start"] * SR):int(Sg["end"] * SR)] = 1.0
    insong = np.convolve(insong, np.ones(SR // 5) / (SR // 5), "same")
    low = signal.lfilter(*signal.butter(2, 280 / (SR / 2), "low"), music)
    high = signal.lfilter(*signal.butter(2, 4200 / (SR / 2), "high"), music)
    mid = music - low - high
    k_mid = 0.85 - 0.2 * insong
    music = low * (1 - 0.35 * env) + mid * (1 - k_mid * env) + high * (1 - 0.5 * env)
    music = mono_safe(music)
    ref = music[:, int(f("town") * SR):int(f("news1") * SR)]
    g_mu = db(-21.0) / (np.sqrt((ref ** 2).mean()) + 1e-12)
    music = music * g_mu
    # ride the music under every line: speech >= 13 dB clear of it (in the speech band), sung lines >= 8 dB
    band = lambda x: signal.sosfilt(signal.butter(2, [300 / (SR / 2), 4000 / (SR / 2)], "band", output="sos"), x.mean(axis=0))
    bm, bv = band(music), band(vo)
    ride = np.ones(N)
    for key in TL.order:
        L = TL.lines[key]
        a, b = int(L["start"] * SR), int(L["end"] * SR)
        rv = np.sqrt((bv[a:b] ** 2).mean()) + 1e-12
        rm = np.sqrt((bm[a:b] ** 2).mean()) + 1e-12
        margin = 20 * np.log10(rv / rm)
        target = 8.0 if L["song"] else 13.0
        if margin < target:
            ride[max(0, a - int(0.12 * SR)):min(N, b + int(0.18 * SR))] = np.minimum(
                ride[max(0, a - int(0.12 * SR)):min(N, b + int(0.18 * SR))], db(margin - target))
    k = int(0.15 * SR)
    ride = np.convolve(np.pad(ride, k, mode="edge"), np.ones(k) / k, "same")[k:-k]
    music = music * ride
    mix = music + vo
    mix = loudness(mix, -14.0)
    tail = int(0.5 * SR)
    mix[:, -tail:] *= np.linspace(1, 0, tail) ** 2
    STEMS.update(music=music, vo=vo)
    return mix


STEMS = {}
CEIL = -1.8


def loudness(x, target):
    import pyloudnorm as pyln
    g = 1.0
    for _ in range(4):
        y = limit(x * g, db(CEIL))
        lufs = pyln.Meter(SR).integrated_loudness(y.T)
        g *= db(target - lufs)
    return limit(x * g, db(CEIL))


def limit(x, ceil, look=0.005, rel=0.12):
    """A look-ahead limiter on the true (4x oversampled) peak."""
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
