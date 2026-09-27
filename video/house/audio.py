"""Soundtrack: a sweet 1970s pop band and a gentle piano/music-box theme that keep playing while the film turns to horror.

Arrangement (read off the edit):
  box      the music-box theme alone (the parlour, the mirror, the clock)
  band     the full sweet band: soft kit, bouncy bass, electric piano, strings, glockenspiel, 'ba-ba' voices
  thin     the band without drums (the kitchen, the purchase)
  horror   the band keeps playing, but warped (wow and flutter, dulled) under a rotting drone and whispers
  clinic   a low drone and a few piano notes
  silent   nothing at all - a sudden silence
Every transition gets a hit; every scare gets a scare hit; the cat's meow comes back whenever its eyes turn red.
The chatbot's voice is a sugary whisper with an echo; everything is set to -14 LUFS, true peak under -1.5 dBTP.
Writes build/audio.wav (48 kHz stereo).
"""
import os
import wave

import numpy as np
from scipy import signal

import pop70 as P
from cues import C
from edit import EDIT, first
from script import AI, DOC, NAR
from timeline import TL
from voice import SR as VSR

SR = P.SR
HERE = os.path.dirname(os.path.abspath(__file__))
N = int((TL.total + 0.6) * SR)
BEAT, STEP = P.BEAT, P.BEAT / 2
S, E, W = TL.s, TL.e, TL.word

CHORDS = [(65, 69, 72, 76), (62, 65, 69, 72), (58, 62, 65, 69), (60, 64, 67, 70)]     # Fmaj7 | Dm7 | Bbmaj7 | C7
ROOTS = [41, 38, 46, 36]
THEME = [(72, 1), (77, 1), (81, 2), (79, 1), (77, 1), (76, 1), (77, 1), (74, 1), (76, 1), (77, 1), (72, 1),
         (69, 1), (70, 1), (72, 2), (72, 1), (77, 1), (81, 1), (84, 1), (82, 1), (81, 1), (79, 1), (77, 1),
         (76, 1), (77, 1), (79, 1), (74, 1), (77, 4)]


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


def sections():
    f = first
    return [
        (0.0, f("eaten"), "box"), (f("eaten"), f("title"), "silent"),
        (f("title"), f("always"), "band"), (f("always"), f("court"), "thin"),
        (f("court"), f("fine"), "band"), (f("fine"), f("pile"), "silent"), (f("pile"), f("mirror"), "band"),
        (f("mirror"), f("kitchen"), "box"), (f("kitchen"), f("nowarning"), "thin"), (f("nowarning"), f("parcel"), "silent"),
        (f("parcel"), f("neighbor"), "thin"), (f("neighbor"), f("doctor"), "horror"), (f("doctor"), f("realcase"), "clinic"),
        (f("realcase"), f("onedoc"), "box"), (f("onedoc"), f("clones_red"), "band"), (f("clones_red"), f("globe"), "horror"),
        (f("globe"), f("thatclock"), "band"), (f("thatclock"), f("report"), "box"), (f("report"), f("burn"), "band"),
        (f("burn"), f("rumor"), "horror"), (f("rumor"), f("payoff"), "band"), (f("payoff"), f("trust"), "horror"),
        (f("trust"), TL.total + 1, "silent"),
    ]


SECTIONS = []


def section(t):
    for a, b, m in SECTIONS:
        if a <= t < b:
            return m
    return "silent"


# ------------------------------------------------------------------ the band

def band(bus, keys, drones):
    rng = np.random.default_rng(7)
    nb = int(TL.total / STEP) + 1
    for s in range(nb):
        t = s * STEP
        sec = section(t)
        if sec not in ("band", "thin", "horror"):
            continue
        bar = int(t / (BEAT * 4))
        st = s % 8                                   # eighth notes in a 4/4 bar
        ch, root = CHORDS[bar % 4], ROOTS[bar % 4]
        swing = STEP * 0.1 if st % 2 else 0.0
        tt = t + swing
        drums = sec in ("band", "horror")
        if drums:
            if st in (0, 3, 4):
                bus.add(P.kick(0.9 if st == 0 else 0.7, seed=s), tt, 0.8)
            if st in (2, 6):
                bus.add(P.snare(0.8, seed=s), tt, 0.5, pan=0.55)
            bus.add(P.hat(0.9 if st % 2 == 0 else 0.6, seed=s, open_=(st == 7 and bar % 2 == 1)), tt, 0.3, pan=0.3 if st % 4 < 2 else 0.7)
            if st in (3, 7):
                bus.add(P.tambourine(0.8, seed=s), tt, 0.3, pan=0.78)
        # bass: root, fifth, octave - bouncy
        if st in (0, 3, 4, 6):
            m = root + {0: 0, 3: 7, 4: 12, 6: 7}[st]
            bus.add(P.bass(m, STEP * (1.6 if st in (0, 4) else 0.9)), tt, 0.55)
        # electric piano on the off-beats, strings pad per bar
        if st in (1, 3, 5, 7):
            keys.add(P.epiano(ch, STEP * 0.9, 0.9, seed=s, bright=0.9), tt, 0.22, pan=0.4 if st % 4 == 1 else 0.6)
        if st == 0:
            keys.add(P.strings(ch, BEAT * 4, 1.0, seed=bar), tt, 0.5)
            if sec == "band" and bar % 4 in (1, 3):
                for k, m in enumerate((ch[1] + 12, ch[2] + 12)):
                    keys.add(P.voices("a", m, BEAT * 0.45, 0.8, seed=bar + k), tt + BEAT * (1 + k), 0.22, pan=0.35 + 0.3 * k)
        # the theme on the piano, one note per beat, over the band
        if st % 2 == 0:
            beat_i = s // 2
            m, _ = THEME[beat_i % len(THEME)]
            if sec != "thin" or beat_i % 2 == 0:
                keys.add(P.piano([m], BEAT * 0.9, 0.9, seed=s), tt, 0.35 if sec != "horror" else 0.3, pan=0.45)
            if sec == "band" and beat_i % 8 == 0:
                keys.add(P.glock(m + 12, 0.9), tt, 0.2, pan=0.62)


def warp(x, depth_ms=9.0, rate=0.6):
    """Wow and flutter: the tape sags and wobbles (a slowly swinging delay line), so the sweet music goes seasick."""
    n = x.shape[1]
    t = np.arange(n) / SR
    d = (depth_ms / 1000 * SR) * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t) + 0.15 * np.sin(2 * np.pi * 5.3 * t))
    idx = np.arange(n) - d
    i0 = np.clip(np.floor(idx).astype(int), 0, n - 1)
    fr = idx - np.floor(idx)
    i1 = np.clip(i0 + 1, 0, n - 1)
    return x[:, i0] * (1 - fr) + x[:, i1] * fr


def music_boxes(box):
    """The music box: sweet in the parlour, slowing and going out of tune when the film turns."""
    for a, b, m in SECTIONS:
        if m == "box":
            k = 0
            t = a + 0.05
            while t < b - 0.3:
                seg = P.music_box(THEME, amp=1.0, seed=k)
                seg = seg[: int((b - t) * SR)]
                fade = np.clip((b - t - np.arange(len(seg)) / SR) / 0.3, 0, 1)
                box.add(seg * fade, t, 0.55, pan=0.45)
                t += len(seg) / SR
                k += 1
    # the slow, detuning versions
    for t0, dur in ((first("eaten") + 0.05, first("title") - first("eaten") - 0.05),
                    (first("neighbor"), 4.0), (first("payoff") + 0.5, first("trust") - first("payoff") - 0.5),
                    (first("end") + 0.2, TL.total - first("end") - 0.2)):
        seg = P.music_box(THEME[:12], rate=lambda u: 1.0 - 0.7 * u, detune=lambda u: -90 * u * u - 30 * u, amp=1.0, seed=int(t0))
        seg = seg[: int(dur * SR)]
        seg = seg * np.clip((dur - np.arange(len(seg)) / SR) / 0.4, 0, 1)
        box.add(seg, t0, 0.65, pan=0.5)


# ------------------------------------------------------------------ sound effects

def sfx(fx):
    # a hit on every transition
    horror_shots = {"eaten", "neighbor", "visions", "run", "hold", "clones_red", "burn", "count"}
    for i, (t, name, tr) in enumerate(EDIT[1:], 1):
        if name in horror_shots:
            fx.add(P.scare(1.0, seed=i), t, 0.8)
        elif tr == "iris":
            fx.add(P.glock(84, 1.0), t - 0.2, 0.35, pan=0.4)
            fx.add(P.glock(89, 1.0), t - 0.12, 0.35, pan=0.6)
            fx.add(P.woodblock(0.8, 700), t, 0.4)
        elif tr == "flip":
            fx.add(P.page(1.0, seed=i), t - 0.05, 0.6, pan=0.7)
        elif tr == "card":
            fx.add(P.piano([53, 60, 65, 69], 1.2, 1.0, seed=i), t, 0.55)
            fx.add(P.stamp(1.0), t, 0.5)
        else:
            fx.add(P.pop(1.0), t, 0.35, pan=0.5)
            fx.add(P.woodblock(0.8, 900 + 60 * (i % 5)), t, 0.3, pan=0.4 + 0.05 * (i % 5))
    # the hook and the burning study
    fx.add(P.meow(1.0), C["eaten"] + 0.3, 0.45, pan=0.55)
    fx.add(P.hiss(1.0), C["eaten"] + 0.9, 0.35)
    fx.add(P.sting((77, 81, 84, 89), 1.0), first("title") + 0.1, 0.5)
    fx.add(P.stamp(1.0), W("h3", "sure") - 0.05, 0.5, pan=0.5)
    # the album: every photo slapped in with a shutter click
    for k, ti in enumerate(C["items"]):
        fx.add(P.click(1.0), ti - 0.08, 0.5, pan=0.3 + 0.05 * k)
        fx.add(P.stamp(0.8), ti - 0.03, 0.35)
    # the word machine
    fx.add(P.keys(10, 0.05), first("machine") + 0.3, 0.25)
    for k in range(3):
        fx.add(P.woodblock(1.0, 1200), C["reels"] + 0.25 + [0, 0.35, 0.75][k], 0.45)
        fx.add(P.glock(88 + 2 * k, 1.0), C["reels"] + 0.27 + [0, 0.35, 0.75][k], 0.3)
    fx.add(P.slide_whistle(False, 0.45), W("w1", "isn't") - 0.1, 0.45)
    fx.add(P.meow(1.0), W("w1", "isn't") + 0.25, 0.35, pan=0.7)
    fx.add(P.stamp(1.0), C["star"], 0.55)
    fx.add(P.glock(96, 1.0), C["star"] + 0.35, 0.4)
    fx.add(P.scare(1.0, seed=31), E("w3") + 0.02, 0.7)
    # the court
    fx.add(P.meow(1.0), first("brief") + 0.8, 0.3, pan=0.7)
    for k in range(3):
        fx.add(P.pop(1.0), W("c1", "real?") + k * 0.12, 0.4, pan=0.4 + 0.1 * k)
    fx.add(P.scare(1.0, seed=33), C["yes"] - 0.02, 0.6)
    fx.add(P.woodblock(1.0, 400), C["gavel"], 0.9)
    fx.add(P.woodblock(1.0, 380), C["gavel"] + 0.2, 0.7)
    fx.add(P.whoosh(1.8, up=False, seed=3), C["pile"] + 0.1, 0.35)
    for k in range(10):
        fx.add(P.page(0.7, seed=40 + k), C["pile"] + 0.3 + k * 0.33, 0.25, pan=0.2 + 0.06 * k)
    fx.add(P.slide_whistle(True, 0.7), first("plane") + 0.2, 0.3, pan=0.3)
    fx.add(P.sting((84, 88, 91), 1.0), W("c3", "refund") - 0.1, 0.35)
    for k in range(12):
        fx.add(P.glock(90 + (k * 5) % 12, 0.8), C["pay"] + k * 0.09, 0.2, pan=0.3 + 0.04 * k)
    # the personal part
    fx.add(P.keys(30, 0.055, seed=2), C["typed"] + 0.05, 0.35)
    fx.add(P.sting((77, 81, 84, 88), 1.0), S("p3") - 0.35, 0.25)
    fx.add(P.meow(1.0), E("p3") + 0.02, 0.6, pan=0.5)
    fx.add(P.click(1.0), first("nowarning"), 0.6)
    fx.add(P.stamp(1.2), first("parcel") + 0.35, 0.6)
    fx.add(P.boing(1.0), first("parcel") + 0.5, 0.45)
    fx.add(P.sting((81, 84, 89), 1.0), first("parcel") + 0.55, 0.35)
    for k in range(10):
        fx.add(P.tambourine(0.8, seed=k), first("sprinkle") + k * 0.16, 0.35, pan=0.6)
    fx.add(P.whoosh(1.0, up=True, seed=5), first("calendar"), 0.35)
    for k in range(6):
        fx.add(P.tick(1.0, tock=k % 2 == 1), first("bed") + k * 0.3, 0.5)
    fx.add(P.honk(1.0, 2), first("neighbor") + 0.8, 0.45, pan=0.7)
    fx.add(P.hiss(1.0), first("neighbor") + 0.3, 0.4, pan=0.3)
    fx.add(P.slide_whistle(False, 0.6), C["see"], 0.4, pan=0.3)
    fx.add(P.boing(1.0), C["see"] + 0.6, 0.4, pan=0.7)
    fx.add(P.reverse_swell(1.0), C["hear"] - 0.9, 0.6)
    fx.add(P.heartbeat(8, 80), first("neighbor"), 0.7)
    fx.add(P.heartbeat(4, 130), first("run"), 0.7)
    for k in range(8):
        fx.add(P.woodblock(0.8, 300 + 40 * (k % 2)), first("run") + k * 0.13, 0.4, pan=0.3 + 0.4 * (k % 2))
    fx.add(P.stamp(1.5), first("hold") + 0.02, 0.9)
    fx.add(P.scare(0.8, seed=51, notes=(38, 39, 45)), C["level"] + 0.4, 0.5)
    for k in range(21):
        fx.add(P.stamp(0.5), first("weeks") + 0.05 + k * 0.07, 0.25, pan=0.3 + 0.02 * k)
    fx.add(P.click(1.0), first("casefile"), 0.5)
    fx.add(P.click(1.0), first("casezoom"), 0.5)
    # the scale
    fx.add(P.stamp(1.0), W("s1", "one", 1) - 0.1, 0.5)
    for k, a in enumerate((0.55, 1.2, 1.9)):
        fx.add(P.pop(1.0), first("clones") + a, 0.5, pan=0.3 + 0.2 * k)
    fx.add(P.whoosh(3.8, up=True, seed=9), first("globe") + 0.2, 0.25)
    fx.add(P.honk(1.0, 1), W("s4", "wrong,") - 0.15, 0.45, pan=0.6)
    for k in range(28):
        fx.add(P.tick(1.0, tock=k % 2 == 1), first("counter") + k * 0.06, 0.35)
    fx.add(P.cuckoo(1.0), first("counter") + 1.7, 0.5)
    for k in range(3):
        tj = C["second"] - 0.1 + 0.3 + k * 0.62
        fx.add(P.tick(1.5), tj, 0.7)
        fx.add(P.stamp(0.8), tj + 0.02, 0.4)
    for k in range(int((first("report") - first("thatclock")) / 0.5)):
        fx.add(P.tick(1.2, tock=k % 2 == 1), first("thatclock") + k * 0.5, 0.55)
    fx.add(P.cuckoo(1.0), C["clock"], 0.45)
    fx.add(P.organ([53, 60, 65, 69], 2.5, 1.0), first("report"), 0.5)
    for k, wd in enumerate(("made-up", "flawed", "misleading")):
        fx.add(P.click(1.0), W("r1", wd) - 0.14, 0.4)
        fx.add(P.stamp(0.9), W("r1", wd) - 0.1, 0.4, pan=0.3 + 0.2 * k)
    fx.add(P.whoosh(1.4, up=False, seed=11), first("burn"), 0.4)
    fx.add(P.boing(1.0), first("crack") + 0.2, 0.35, pan=0.3)
    fx.add(P.boing(1.0), first("crack") + 1.2, 0.35, pan=0.7)
    fx.add(P.scare(0.7, seed=61), first("crack") + 1.1, 0.45)
    fx.add(P.page(1.0, seed=7), first("source") + 0.1, 0.5)
    fx.add(P.sting((77, 81, 84, 89), 1.0), first("source") + 1.2, 0.4)
    for k, wd in enumerate(("health,", "money,", "law.")):
        fx.add(P.stamp(1.2), W("t2", wd), 0.55, pan=0.3 + 0.2 * k)
        fx.add(P.woodblock(1.0, 350), W("t2", wd) + 0.05, 0.4)
    for k in range(4):
        fx.add(P.woodblock(0.8, 500), first("doors") + 0.5 + k * 0.25, 0.25, pan=0.5)
    # the clock strikes
    for k in range(3):
        fx.add(P.clock_bell(1.0, 62 - 5 * k), first("payoff") + 0.1 + k * 0.9, 0.55)
        fx.add(P.cuckoo(1.0), first("payoff") + 0.4 + k * 0.9, 0.45)
    fx.add(P.meow(1.0), first("payoff") + 0.6 * (first("count") - first("payoff")), 0.4, pan=0.7)
    fx.add(P.drone(first("trust") - first("count"), root=27, amp=1.0, seed=2), first("count"), 0.7)
    fx.add(P.scare(1.2, seed=71), E("e2") + 0.02, 0.9)
    fx.add(P.meow(1.0), E("e2") + 0.4, 0.6)
    fx.add(P.projector(TL.total - first("end")), first("end"), 0.6)
    fx.add(P.scare(0.6, seed=81, notes=(29, 30, 36)), TL.total - 2.2, 0.35)


def horror_layers(hz):
    for a, b, m in SECTIONS:
        if m == "horror":
            hz.add(P.drone(b - a + 0.8, root=29, seed=int(a)), a, 0.6)
            hz.add(P.whispers(b - a, seed=int(a)), a, 0.5)
        elif m == "clinic":
            hz.add(P.drone(b - a + 0.5, root=34, seed=int(a)), a, 0.4)
            for k in range(int((b - a) / 1.2)):
                hz.add(P.piano([[57, 60, 64, 62][k % 4]], 1.2, 0.8, seed=k), a + 0.3 + k * 1.2, 0.3, pan=0.4)


# ------------------------------------------------------------------ voices

def voices():
    out = np.zeros((2, N))
    for key in TL.order:
        L = TL.lines[key]
        a = L["wav"].astype(np.float64)
        who = L["who"]
        up = signal.resample_poly(a, SR, VSR)
        r = np.sqrt((up ** 2).mean()) + 1e-12
        up = up * db({NAR: -18.0, AI: -13.5, DOC: -17.0}[who]) / r
        if who == AI:                                   # the sugary whisper: doubled, echoing
            d = int(0.011 * SR)
            dbl = np.concatenate([np.zeros(d), up])[:len(up)]
            st = np.stack([up * 0.85 + dbl * 0.35, up * 0.85 - dbl * 0.1])
            tail = np.zeros((2, int(1.2 * SR)))
            st = np.concatenate([st, tail], axis=1)
            for k, (dl, g) in enumerate(((0.19, 0.35), (0.38, 0.2), (0.57, 0.1))):
                o = int(dl * SR)
                st[k % 2, o:] += st[0, :-o] * g if o < st.shape[1] else 0
            sig = st
        else:
            sig = np.stack([up, up])
        i = int(L["start"] * SR)
        j = min(N, i + sig.shape[1])
        out[:, i:j] += sig[:, : j - i]
    return out


def widen(x, amt=0.5):
    """Decorrelate the sides a little (all-pass chain on the mid, added to the side) so the band feels wide."""
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
    side = side + amt * signal.lfilter(*signal.butter(2, 200 / (SR / 2), "high"), d)
    return np.stack([mid + side, mid - side])


def reverb(x, wet=0.1, rt60=0.8, seed=8):
    rng = np.random.default_rng(seed)
    t = np.arange(int(rt60 * 1.4 * SR)) / SR
    ir = np.stack([rng.normal(0, 1, len(t)) * np.exp(-6.9 * t / rt60) for _ in range(2)])
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    y = np.stack([signal.fftconvolve(x[c], ir[c])[: x.shape[1]] for c in range(2)])
    return x * (1 - wet) + y * wet


def build():
    SECTIONS[:] = sections()
    band_bus, keys_bus, box_bus, fx, hz = Bus(), Bus(), Bus(), Bus(), Bus()
    band(band_bus, keys_bus, hz)
    music_boxes(box_bus)
    sfx(fx)
    horror_layers(hz)
    music = reverb(band_bus.x, 0.12, 0.9) + reverb(keys_bus.x, 0.22, 1.4) + reverb(box_bus.x, 0.3, 1.8)
    # in the horror the sweet music keeps going - seasick and dulled
    mask = np.zeros(N)
    for a, b, m in SECTIONS:
        if m == "horror":
            mask[int(a * SR):int(b * SR)] = 1.0
    mask = np.convolve(mask, np.ones(SR // 10) / (SR // 10), "same")
    warped = warp(music, 9.0, 0.55)
    warped = signal.lfilter(*signal.butter(2, 2200 / (SR / 2), "low"), warped)
    music = music * (1 - mask) + warped * mask * 0.85
    # sudden silences: the music drops out completely
    gate = np.ones(N)
    for a, b, m in SECTIONS:
        if m == "silent":
            gate[int(a * SR):int(b * SR)] = 0.0
    gate = np.convolve(gate, np.ones(int(0.02 * SR)) / int(0.02 * SR), "same")
    music = music * gate
    music = music + reverb(fx.x, 0.15, 1.0) * db(0.5) + reverb(hz.x, 0.3, 2.0)
    music = signal.lfilter(*signal.butter(2, 35 / (SR / 2), "high"), music)

    vo = reverb(voices(), 0.06, 0.5)
    from scipy.ndimage import maximum_filter1d
    raw = np.convolve(np.abs(vo.mean(axis=0)), np.ones(SR // 20) / (SR // 20), mode="same")
    raw = np.clip(raw / (np.percentile(raw[raw > 1e-5], 80) + 1e-9), 0, 1)
    env = maximum_filter1d(raw, size=int(0.45 * SR), origin=-int(0.12 * SR))
    env = np.convolve(env, np.ones(SR // 12) / (SR // 12), mode="same")
    talk = np.zeros(N)                                  # the music swells up in the gaps between lines
    for key in TL.order:
        talk[int((TL.s(key) - 0.1) * SR): int((TL.e(key) + 0.12) * SR)] = 1.0
    r = int(0.12 * SR)
    music = music * (1 + (db(5.0) - 1) * (1 - np.convolve(talk, np.ones(r) / r, mode="same")))
    low = signal.lfilter(*signal.butter(2, 280 / (SR / 2), "low"), music)
    high = signal.lfilter(*signal.butter(2, 4200 / (SR / 2), "high"), music)
    mid = music - low - high
    music = low * (1 - 0.4 * env) + mid * (1 - 0.92 * env) + high * (1 - 0.65 * env)
    music = widen(music, 0.7)
    ref = music[:, int(S("l1") * SR):int(E("w2") * SR)]
    g_mu = db(-23.5) / (np.sqrt((ref ** 2).mean()) + 1e-12)
    mix = music * g_mu + vo
    mix = loudness(mix, -14.0)
    tail = int(0.4 * SR)
    mix[:, -tail:] *= np.linspace(1, 0, tail) ** 2
    STEMS.update(music=music * g_mu, vo=vo)
    return mix


STEMS = {}


def loudness(x, target):
    import pyloudnorm as pyln
    for _ in range(2):
        lufs = pyln.Meter(SR).integrated_loudness(x.T)
        x = limit(x * db(target - lufs), db(-2.4))
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
    mix = build()
    write(os.path.join(HERE, "build", "audio.wav"), mix)
    print("audio", round(mix.shape[1] / SR, 2), "s in", round(time.time() - t0, 1), "s")
