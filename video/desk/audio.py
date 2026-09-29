"""The soundtrack: the arrangement (score.py) placed against the edit, the voices, and a clean, wide 1985 mix.

Each chapter builds layer by layer and stops dead: a hard cut to true silence before every chapter card (then a
temple bell under the card), and before the final image. Voices sit well clear of the music (a ride per line).
Loudness -14 LUFS, true peak under -1.5 dBTP.
"""
import os
import wave

import numpy as np
from scipy import signal

import orch as O
import score as Sc
from cues import C, CARDS, Wx
from edit import EDIT, first
from script import CLOCK, NAR, TEACHER, TUTOR
from timeline import TL
from voice import SR as VSR

SR = O.SR
HERE = os.path.dirname(os.path.abspath(__file__))
N = int((TL.total + 0.6) * SR)
S, E = TL.s, TL.e
f = first


def db(v):
    return 10 ** (v / 20)


def wide(fn, dur, *a, **k):
    """An ambience in true stereo: the same sound generated twice with different seeds."""
    seed = k.pop("seed", 1)
    return np.stack([fn(dur, *a, seed=seed, **k), fn(dur, *a, seed=seed + 101, **k)])


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


def nxt(name):
    """End of a shot (the start of the next one)."""
    i = next(k for k, e in enumerate(EDIT) if e[1] == name)
    return EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total


# the dead stops: music and ambience cut to nothing
STOPS = [E("o2") + 0.35, E("a7") + 0.25, E("b12") + 0.25, E("d7") + 0.25]
SILENCES = [(STOPS[i], CARDS[i][3] + 0.8) for i in range(4)] + [(E("e7") + 0.25, f("final") + 0.05)]


def dead_air():
    return SILENCES


def score(mus, amb, fx):
    # ---------------------------------------------------------------- cold open: the hook, then the present
    fx.add(O.keys(int((E("o0a") - 0.35) / 0.08), gap=0.08, amp=0.55, seed=9), 0.15, 1.0, pan=0.55)
    Sc.ostinato(mus, 0.0, f("teaser_dial"), Sc.A_MIN, {"pulse": 0.4, "arp": 0.35}, bars_per_chord=2)
    Sc.ostinato(mus, f("teaser_dial"), f("open_lamp"), Sc.A_MIN, {"pulse": 0.55, "arp": 0.7, "bass": 0.6, "counter": 0.45,
                                                                  "brass": 0.4, "timp": 0.4})
    fx.add(Sc.clappers(amp=0.9, seed=11), f("teaser_dial") - 0.05, 1.0)
    to = f("open_lamp")
    amb.add(Sc.room_tone(STOPS[0] - to), to, 0.8)
    amb.add(wide(Sc.rain, STOPS[0] - to, amp=0.5), to, 1.0)
    fx.add(O.click(amp=1.2), C["lamp_on"] - 0.02, 1.0, pan=0.35)
    Sc.ostinato(mus, to, STOPS[0], Sc.A_MIN, {"pulse": 0.35}, bars_per_chord=2)
    for k in range(int(STOPS[0] - to)):
        fx.add(O.tick(amp=0.5, tock=k % 2), to + 0.3 + k, 1.0, pan=0.6)

    # ---------------------------------------------------------------- ONE: CROWD
    card = [c[3] for c in CARDS]
    for i, t in enumerate(card):                                        # a temple bell under each chapter card
        mus.add(Sc.temple_bell(40 + (0, 3, 5, 7)[i], amp=0.42), t + 0.8, 1.0, pan=0.5)
    t_class = f("class")
    amb.add(wide(Sc.murmur, C["bell"] - t_class, amp=0.4), t_class, 1.0)
    Sc.piano_motif(mus, t_class + 0.4, C["bell"] - 0.2, amp=0.7, step=1.7, seed=1)
    for k in range(10):
        fx.add(Sc.chalk(amp=0.6, seed=k), t_class + 0.8 + k * 0.9 + 0.2 * (k % 3), 1.0, pan=0.42)
    fx.add(O.alarm_bell(dur=0.95, amp=1.6), C["bell"], 1.0, pan=0.5)                     # the bell, first
    amb.add(wide(Sc.murmur, 1.6, amp=1.6, seed=4), C["bell"] + 0.3, 1.0)                      # chairs, bags, gone
    mus.add(O.piano([57], 2.0, amp=0.6, seed=9), S("a4"), 1.0, pan=0.45)
    tw = f("window")
    amb.add(wide(Sc.rain, nxt("window") - tw, amp=0.8, seed=8), tw, 1.0)
    amb.add(wide(Sc.traffic, nxt("window") - tw, amp=0.6), tw, 1.0)
    Sc.piano_motif(mus, tw + 0.5, nxt("window"), amp=0.6, step=1.9, seed=20)
    tp = f("prince")
    Sc.ostinato(mus, tp, f("aph1"), Sc.A_MIN, {"arp": Sc.ramp_up(tp, tp + 3, 0.3, 0.6), "bass": 0.5,
                                                "pulse": Sc.ramp_up(tp + 2, tp + 4, 0, 0.45),
                                                "brass": lambda t: 0.5 if t > Wx("a6", "ninety") - 0.3 else 0.0,
                                                "counter": Sc.ramp_up(C["split98"], C["split98"] + 1, 0, 0.4)})
    fx.add(Sc.clappers(amp=1.1), C["split98"] - 0.3, 1.0, pan=0.5)
    fx.add(Sc.wood_slide(1.6, amp=0.9), C["split98"], 1.0, pan=0.5)
    mus.add(O.timpani(45, amp=0.8), C["split98"] + 0.2, 1.0)
    Sc.ostinato(mus, f("aph1"), STOPS[1], Sc.A_MIN, {"arp": 0.6, "pulse": 0.45, "bass": 0.6, "counter": 0.45, "harp": 0.5,
                                                     "brass": 0.35})

    # ---------------------------------------------------------------- TWO: LIGHT
    t2 = f("clock1")
    amb.add(Sc.room_tone(f("car") - t2), t2, 0.8)
    amb.add(wide(Sc.rain, f("car") - t2, amp=0.35, seed=11), t2, 1.0)
    for k in range(int(f("car") - t2)):
        fx.add(O.tick(amp=0.4, tock=k % 2), t2 + 0.2 + k, 1.0, pan=0.62)
    n_keys = int((E("b2q") - C["type1"]) / 0.09)
    fx.add(O.keys(n_keys, gap=0.09, amp=0.5, seed=1), C["type1"], 1.0, pan=0.55)
    Sc.ostinato(mus, t2 + 0.3, f("car"), Sc.A_MIN, {"pulse": 0.35, "arp": Sc.ramp_up(S("b3") - 0.5, S("b3"), 0, 0.3)},
                bars_per_chord=2)
    tc = f("car")
    Sc.ostinato(mus, tc, f("type2"), Sc.A_MIN, {"pulse": 0.5, "arp": 0.65, "bass": 0.6, "counter": 0.45,
                                                "brass": Sc.ramp_up(C["speedo"], C["speedo"] + 0.5, 0, 0.45), "timp": 0.35})
    fx.add(Sc.clappers(amp=1.0, seed=3), C["turn"] - 0.35, 1.0)
    fx.add(Sc.wood_slide(1.1, amp=0.7), C["turn"] - 0.2, 1.0)
    t3 = f("type2")
    amb.add(Sc.room_tone(f("old_test") - t3), t3, 0.8)
    Sc.ostinato(mus, t3, f("old_test"), Sc.A_MIN, {"pulse": 0.35, "arp": 0.3, "bass": 0.3}, bars_per_chord=2)
    fx.add(O.keys(int((E("b4") - S("b4")) / 0.09), 0.09, amp=0.5, seed=2), S("b4"), 1.0, pan=0.55)
    fx.add(O.keys(int((E("b6") - S("b6")) / 0.09), 0.09, amp=0.5, seed=3), S("b6"), 1.0, pan=0.55)
    fx.add(O.keys(int((E("b7q") - C["type4"]) / 0.09), 0.09, amp=0.5, seed=4), C["type4"], 1.0, pan=0.55)
    for k in range(4):
        mus.add(O.harp(72 + k * 4, amp=0.5), Wx("b5", "steep") - 0.2 + k * 0.07, 1.0, pan=0.4)
    fx.add(Sc.pencil(1.4, amp=0.9), E("b6") + 0.3, 1.0, pan=0.62)
    for k in range(5):
        fx.add(Sc.ding(k < 4, amp=0.8), S("b7") + 0.25 + k * 0.18, 1.0, pan=0.62)
    mus.add(O.harp(76, amp=0.6), C["ring"], 1.0)
    mus.add(O.celesta(84, amp=0.7), C["fix"], 1.0)
    mus.add(O.celesta(88, amp=0.5), C["fix"] + 0.3, 1.0)
    to = f("old_test")
    mus.add(O.piano([45], 2.4, amp=0.6, seed=31), to + 0.1, 1.0, pan=0.5)
    tp2 = f("profile2")
    mus.add(O.strings([57, 60, 64], nxt("profile2") - tp2 + 0.3, amp=0.9, seed=2), tp2 - 0.2, 1.0, pan=0.45)
    tm = f("montage")
    ph = [tm, Wx("b11", "harder") - 0.2, Wx("b11", "chain") - 0.2, Wx("b11", "midnight") - 0.4]
    Sc.ostinato(mus, tm, f("aph2"), Sc.A_MIN, {"pulse": 0.45, "arp": Sc.ramp_up(ph[1], ph[1] + 0.5, 0.1, 0.55),
                                               "counter": Sc.ramp_up(ph[2], ph[2] + 0.5, 0, 0.45),
                                               "bass": Sc.ramp_up(ph[3], ph[3] + 0.5, 0.2, 0.6)})
    amb.add(Sc.room_tone(f("aph2") - tm), tm, 0.7)
    Sc.ostinato(mus, f("aph2"), STOPS[2], Sc.DAWN, {"pulse": 0.5, "arp": 0.7, "counter": 0.5, "bass": 0.7, "brass": 0.6,
                                                    "timp": 0.5, "harp": 0.6})

    # ---------------------------------------------------------------- THREE: DOUBT
    tb = f("box")
    Sc.ostinato(mus, tb, f("study"), Sc.DOUBT, {"pulse": 0.5, "arp": 0.5, "bass": 0.6, "brass": 0.35})
    for k in range(6):
        fx.add(O.whoosh(0.35, up=k % 2 == 0, seed=k, amp=0.35), tb + 0.6 + k * 0.5, 1.0, pan=0.3 + 0.1 * k)
    ts = f("study")
    Sc.ostinato(mus, ts, C["hints"] - 0.4, Sc.DOUBT, {"pulse": 0.45, "bass": 0.5, "arp": Sc.ramp_up(C["practice"], C["practice"] + 1, 0.1, 0.45)})
    for k in range(5):
        mus.add(O.harp(64 + k * 3, amp=0.45), C["practice"] + k * 0.1, 1.0, pan=0.35)
    for k in range(5):
        mus.add(O.piano([64 - k * 3], 1.0, amp=0.5, seed=40 + k), C["worse"] + k * 0.14, 1.0, pan=0.6)
    fx.add(Sc.clappers(amp=1.0, seed=5), C["hints"] - 0.8, 1.0)
    fx.add(Sc.wood_slide(1.2, amp=0.8), C["hints"] - 0.5, 1.0)
    Sc.ostinato(mus, C["hints"] - 0.4, f("rule"), Sc.DAWN, {"pulse": 0.4, "arp": 0.5, "bass": 0.5, "harp": 0.5})
    tr = f("rule")
    amb.add(Sc.room_tone(f("harvard") - tr), tr, 0.8)
    fx.add(O.keys(int((E("d3q") - S("d3q")) / 0.09), 0.09, amp=0.5, seed=6), S("d3q"), 1.0, pan=0.55)
    Sc.ostinato(mus, tr, f("harvard"), Sc.A_MIN, {"pulse": 0.35}, bars_per_chord=2)
    th = f("harvard")
    Sc.ostinato(mus, th, f("teacher_night"), Sc.DAWN, {"pulse": 0.45, "arp": 0.55, "bass": 0.55,
                                                       "counter": Sc.ramp_up(C["twice"] - 0.5, C["twice"], 0, 0.45),
                                                       "brass": Sc.ramp_up(C["twice"] - 0.5, C["twice"], 0, 0.45)})
    tn = f("teacher_night")
    amb.add(Sc.room_tone(f("cranes") - tn, amp=0.8), tn, 1.0)
    Sc.piano_motif(mus, tn + 0.3, f("cranes"), amp=0.6, step=1.6, seed=60)
    fx.add(Sc.pencil(f("cranes") - tn - 0.6, amp=0.7, seed=8), tn + 0.4, 1.0, pan=0.35)
    tcr = f("cranes")
    Sc.ostinato(mus, tcr, f("back_row"), Sc.DAWN, {"pulse": 0.35, "arp": 0.45, "bass": 0.45, "harp": 0.5,
                                                   "brass": Sc.ramp_up(C["six"] - 0.4, C["six"], 0, 0.35)})
    fx.add(Sc.paper_flutter(4.0, amp=0.8), C["cranes"], 1.0, pan=0.4)
    fx.add(Sc.paper_flutter(3.0, amp=0.6, seed=9), C["cranes"] + 1.5, 1.0, pan=0.65)
    mus.add(O.celesta(81, amp=0.8), C["flag"], 1.0, pan=0.7)
    tbr = f("back_row")
    Sc.piano_motif(mus, tbr + 0.1, STOPS[3], amp=0.6, step=0.9, seed=70)
    mus.add(O.strings([57, 60, 64, 69], STOPS[3] - tbr, amp=0.8, seed=5), tbr, 1.0, pan=0.5)

    # ---------------------------------------------------------------- FOUR: DAWN
    td = f("dawn")
    amb.add(Sc.room_tone(f("lamps") - td, amp=0.6, hum=False), td, 1.0)
    amb.add(wide(Sc.traffic, f("lamps") - td, amp=0.5, seed=12), td, 1.0)
    mus.add(O.shakuhachi(69, 1.6, amp=0.6, seed=1), td + 0.3, 1.0, pan=0.4)
    tl = f("lamps")
    Sc.ostinato(mus, tl, f("nigeria"), Sc.DAWN, {"pulse": 0.4, "arp": Sc.ramp_up(tl, tl + 4, 0.2, 0.55), "bass": 0.5,
                                                 "counter": Sc.ramp_up(f("language"), f("language") + 2, 0, 0.4)})
    from cues import WHO_TAGS
    for k, w in enumerate(WHO_TAGS):
        mus.add(O.celesta(76 + (0, 2, 4, 7, 9)[k], amp=0.8), w[0] + 0.2, 1.0, pan=0.3 + 0.1 * k)
    fx.add(Sc.clappers(amp=0.9, seed=7), Wx("e3", "translate") - 0.4, 1.0)
    fx.add(Sc.wood_slide(1.0, amp=0.8), Wx("e3", "translate") - 0.2, 1.0)
    mus.add(O.shakuhachi(72, 1.2, amp=0.45, seed=2), C["coach"], 1.0, pan=0.6)
    tn2 = f("nigeria")
    Sc.ostinato(mus, tn2, f("exam"), Sc.DAWN, {"pulse": 0.5, "arp": 0.65, "bass": 0.65, "counter": 0.5, "harp": 0.4,
                                               "brass": Sc.ramp_up(tn2, tn2 + 3, 0.2, 0.55), "timp": 0.35})
    te = f("exam")
    amb.add(Sc.room_tone(STOPS[3] * 0 + (E("e7") + 0.25) - te, amp=0.7, hum=False), te, 1.0)
    for k in range(int(E("e7") - te)):
        fx.add(O.tick(amp=0.45, tock=k % 2), te + 0.3 + k, 1.0, pan=0.55)
    fx.add(O.page(amp=0.6), te + 0.4, 1.0, pan=0.5)
    Sc.ostinato(mus, te + 1.0, E("e7") + 0.25, Sc.DAWN, {"pulse": 0.3}, bars_per_chord=2)
    fx.add(Sc.pencil(2.6, amp=0.8, seed=12), f("q1") + 0.2, 1.0, pan=0.6)
    mus.add(O.celesta(84, amp=0.8), C["inside"], 1.0)
    mus.add(O.strings([60, 64, 67], E("e7") + 0.25 - C["smile"], amp=0.9, seed=8), C["smile"] - 0.1, 1.0)
    fx.add(Sc.envelope_tear(amp=1.0), f("letter") + 0.1, 1.0, pan=0.5)

    # the final image: all three registers meet
    tf = f("final") + 0.05
    mus.add(Sc.temple_bell(36, amp=1.1, dur=9.0), tf, 1.0)
    mus.add(O.strings([48, 55, 62, 64, 67, 72], TL.total - tf, amp=1.2, seed=11), tf, 1.0, pan=0.5)
    Sc.ostinato(mus, tf + 0.3, TL.total - 1.0, Sc.FINAL, {"arp": Sc.ramp_up(tf, tf + 2, 0.2, 0.45), "harp": 0.4,
                                                        "bass": 0.4, "brass": 0.25})
    mus.add(O.timpani(36, amp=0.6), tf + 0.02, 1.0)


def _bp(x, lo, hi):
    return signal.sosfilt(signal.butter(2, [lo / (SR / 2), hi / (SR / 2)], "band", output="sos"), x)


def reverb(x, wet=0.1, rt60=0.8, seed=8):
    rng = np.random.default_rng(seed)
    t = np.arange(int(rt60 * 1.4 * SR)) / SR
    ir = np.stack([rng.normal(0, 1, len(t)) * np.exp(-6.9 * t / rt60) for _ in range(2)])
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    y = np.stack([signal.fftconvolve(x[c], ir[c])[: x.shape[1]] for c in range(2)])
    return x * (1 - wet) + y * wet


def voices():
    out = np.zeros((2, N))
    for key in TL.order:
        L = TL.lines[key]
        who = L["who"]
        up = signal.resample_poly(L["wav"].astype(np.float64), SR, VSR)
        r = np.sqrt((up ** 2).mean()) + 1e-12
        lvl = {NAR: -17.0, CLOCK: -19.0, TUTOR: -17.5, TEACHER: -18.5}.get(who, -17.0)
        up = up * db(lvl) / r
        if who == TUTOR:                                                 # a voice from a laptop speaker, but warm
            up = _bp(up, 150, 7500) * 1.1
        if who == CLOCK:
            up = _bp(up, 250, 6000) * 1.1
        sig = np.stack([up, up])
        if who == TEACHER:                                               # a classroom, remembered
            sig = reverb(sig, 0.35, 1.2, seed=3)
        i = int(L["start"] * SR)
        j = min(N, i + sig.shape[1])
        out[:, i:j] += sig[:, : j - i]
    return out


def mono_safe(x, max_ratio=0.5, hop=1024):
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


def build():
    mus, amb, fx = Bus(), Bus(), Bus()
    score(mus, amb, fx)
    music = reverb(mus.x, 0.28, 2.2) + reverb(fx.x, 0.12, 0.8) + amb.x
    music = signal.sosfilt(signal.butter(4, 45 / (SR / 2), "high", output="sos"), music, axis=1)
    music = np.tanh(1.1 * music) / 1.1                                   # a little tape warmth
    dead = np.ones(N)
    for a, b in dead_air():
        dead[int(a * SR):int(b * SR)] = 0.0
    k = int(0.012 * SR)
    dead = np.convolve(dead, np.ones(k) / k, "same")
    music = music * dead
    vo = presence(reverb(voices(), 0.06, 0.5), 3000, 2.0) * dead
    # a steady duck under speech (slow, so it never pumps), then a ride so each line sits 13 dB clear
    from scipy.ndimage import maximum_filter1d
    raw = np.convolve(np.abs(vo.mean(axis=0)), np.ones(SR // 20) / (SR // 20), mode="same")
    raw = np.clip(raw / (np.percentile(raw[raw > 1e-5], 80) + 1e-9), 0, 1)
    env = maximum_filter1d(raw, size=int(1.2 * SR), origin=-int(0.2 * SR))
    env = np.convolve(env, np.ones(SR // 3) / (SR // 3), mode="same")
    low = signal.lfilter(*signal.butter(2, 250 / (SR / 2), "low"), music)
    high = signal.lfilter(*signal.butter(2, 4500 / (SR / 2), "high"), music)
    mid = music - low - high
    music = low * (1 - 0.3 * env) + mid * (1 - 0.6 * env) + high * (1 - 0.35 * env)
    music = mono_safe(music, max_ratio=1.0)
    shape = np.zeros(N)                                                  # memory hushed, the stage swelling
    for i, (t0, name, reg, tr) in enumerate(EDIT):
        t1 = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total
        shape[int(t0 * SR):int(t1 * SR)] = {"memory": -5.0, "present": -1.5, "fiction": 2.5, "card": 0.0}[reg] + (1.5 if name == "final" else 0.0)
    k = int(0.25 * SR)
    shape = np.convolve(np.pad(shape, k, mode="edge"), np.ones(k) / k, "same")[k:-k]
    music = music * db(shape)[None]
    ref = music[:, int(f("prince") * SR):int(f("aph1") * SR)] / db(2.5)
    music = music * db(-19.0) / (np.sqrt((ref ** 2).mean()) + 1e-12)
    band = lambda x: signal.sosfilt(signal.butter(2, [300 / (SR / 2), 4000 / (SR / 2)], "band", output="sos"), x.mean(axis=0))
    bm, bv = band(music), band(vo)
    ride = np.ones(N)
    for key in TL.order:
        L = TL.lines[key]
        a, b = int(L["start"] * SR), int(L["end"] * SR)
        rv = np.sqrt((bv[a:b] ** 2).mean()) + 1e-12
        rm = np.sqrt((bm[a:b] ** 2).mean()) + 1e-12
        margin = 20 * np.log10(rv / rm)
        if margin < 14.0:
            lo, hi = max(0, a - int(0.25 * SR)), min(N, b + int(0.35 * SR))
            ride[lo:hi] = np.minimum(ride[lo:hi], db(margin - 14.0))
    k = int(0.4 * SR)
    ride = np.convolve(np.pad(ride, k, mode="edge"), np.ones(k) / k, "same")[k:-k]
    music = music * ride
    mix = music + vo
    mix = signal.sosfilt(signal.butter(4, 35 / (SR / 2), "high", output="sos"), mix, axis=1)
    shape = np.zeros(N)                                                  # the whole mix breathes with the registers too
    for i, (t0, name, reg, tr) in enumerate(EDIT):
        t1 = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total
        shape[int(t0 * SR):int(t1 * SR)] = {"memory": -2.5, "present": -0.8, "fiction": 1.5, "card": 0.0}[reg] + (1.5 if name == "final" else 0.0)
    k = int(0.3 * SR)
    shape = np.convolve(np.pad(shape, k, mode="edge"), np.ones(k) / k, "same")[k:-k]
    mix = mix * db(shape)[None]
    mix = loudness(mix, -14.0)
    tail = int(0.8 * SR)
    mix[:, -tail:] *= np.linspace(1, 0, tail) ** 2
    STEMS.update(music=music, vo=vo)
    return mix


STEMS = {}
CEIL = -1.6


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
