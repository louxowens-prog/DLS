"""The soundtrack: the band (band.py) and the cartoon effects placed against the edit, the voices, the mix.

The real world sounds normal: a quiet kitchen, a clock, birds, a street. Through the door the underworld is loud,
fast and echoey: a hot-jazz / ska / new-wave house band that never quite stops, a cartoon effect on every hit.
Two hard stops into silence, played as gags: after the rooster's false alarm, and in the tunnel before the flag.
Voices always sit well clear of the music (a slow duck plus a ride per line). Loudness -14 LUFS.
"""
import os
import wave

import numpy as np
from scipy import signal

import band as Bd
import fxlib as F
import orch as O
from cues import C, CARDS, EL, SL, Wx
from edit import EDIT, first, nxt
from script import CHORUS, DOC, EMCEE, EYE, MAE, OCTO
from timeline import TL
from voice import SR as VSR
from voice import speak_fx

SR = O.SR
HERE = os.path.dirname(os.path.abspath(__file__))
N = int((TL.total + 0.6) * SR)
S, E = TL.s, TL.e
f = first


def db(v):
    return 10 ** (v / 20)


def wide(fn, dur, *a, **k):
    seed = k.pop("seed", 1)
    return np.stack([fn(dur, *a, seed=seed, **k), fn(dur, *a, seed=seed + 101, **k)])


class Bus:
    def __init__(self):
        self.x = np.zeros((2, N))

    def add(self, sig, t, gain=1.0, pan=0.5):
        if sig is None:
            return
        if sig.ndim == 1:
            sig = np.stack([sig * np.sqrt(1 - pan), sig * np.sqrt(pan)]) * np.sqrt(2)
        i = int(t * SR)
        if i >= N or i + sig.shape[1] <= 0:
            return
        if i < 0:
            sig, i = sig[:, -i:], 0
        j = min(N, i + sig.shape[1])
        self.x[:, i:j] += gain * sig[:, : j - i]


def tts(text, voice, speed=1.0, pitch=0.0):
    w = speak_fx(text, voice, speed, pitch)
    return signal.resample_poly(w.astype(np.float64), SR, VSR)


# the gag silences: everything cut dead (music, effects, ambience)
SILENCES = [(C["crow"] + 0.62, S("d3") - 0.02), (E("f2") + 0.12, C["flag"] - 0.02)]


def score(mus, amb, fx):
    # ---------------------------------------------------------------- the real world: a quiet kitchen
    t_fall = f("fall")
    amb.add(F.room_tone(t_fall + 0.2, amp=1.0), 0.0, 1.0)
    amb.add(wide(F.birds, t_fall), 0.0, 0.8)
    for k in range(int(t_fall)):
        fx.add(O.tick(amp=0.35, tock=k % 2), 0.4 + k, 1.0, pan=0.7)
    for k in range(2):
        fx.add(F.buzz(0.55, 1.0), 0.15 + 1.2 * k, 1.0, pan=0.5)
    t_sl = f("slips")
    for i in range(10):
        fx.add(O.page(amp=0.5, seed=i), t_sl + 0.15 * i, 1.0, pan=0.3 + 0.04 * i)
        fx.add(F.thud(0.35, i), t_sl + 0.15 * i + 0.3, 1.0, pan=0.5)
    fx.add(F.scanner(1.0, 1.0), f("scan") + 0.1, 1.0, pan=0.5)
    fx.add(O.beep(0.12, 0.25, 1760), f("scan") + 1.1, 1.0)
    fx.add(F.creak(0.9, 1.0), C["door_open"], 1.0, pan=0.75)
    fx.add(Bd.xylo_run([84, 88, 91, 96], 0.05, 0.5), C["hand"], 1.0, pan=0.75)          # the first cartoon sound
    fx.add(O.slide_whistle(True, 0.5, 0.35), f("hand") + 0.3, 1.0, pan=0.6)

    # ---------------------------------------------------------------- the fall, the title
    fx.add(O.slide_whistle(False, 1.0, 0.9), t_fall + 0.05, 1.0, pan=0.5)
    fx.add(O.whoosh(1.0, False, 3, 0.8), t_fall, 1.0)
    mus.add(O.snare_roll(1.0, amp=0.8), t_fall + 0.1, 1.0)
    tt = f("title")
    Bd.fanfare(mus, tt, 1.0, key=53)
    fx.add(O.whoosh(0.3, True, 4, 0.6), tt - 0.15, 1.0)
    Bd.groove(mus, tt + 0.6, CARDS[0][2], "hotjazz", 188, energy=lambda t: 0.7, level=0.8)
    mus.add(tts("Ba-da-bop!", "chorus"), tt + 0.9, 0.5, pan=0.5)

    # ---------------------------------------------------------------- the room cards
    for i, (num, title, t0, t1) in enumerate(CARDS):
        Bd.card_sting(fx, t0, 1.0, i)
        fx.add(O.whoosh(0.3, i % 2 == 0, 10 + i, 0.4), t0 - 0.2, 1.0)                    # the iris

    # ---------------------------------------------------------------- ROOM 1: hot jazz
    s1 = TL.songs["s1"]
    Bd.groove(mus, f("hall"), s1["start"], "hotjazz", 188, energy=lambda t: 0.35, level=0.6, riffs=False)
    for j, (word, kind) in enumerate([("X-rays", 0), ("CT", 0), ("MRI", 0), ("eye", 0), ("skin", 0), ("slides", 0), ("heart", 0)]):
        tw = Wx("a1", word) - 0.15
        fx.add(Bd.xylo(72 + j * 2, 0.8), tw, 1.0, pan=0.3 + 0.07 * j)
        fx.add(O.pop(0.6), tw + 0.05, 1.0, pan=0.3 + 0.07 * j)
    tr = f("reader")
    for k in range(int((nxt("reader") - tr) * 6)):
        fx.add(O.page(amp=0.25, seed=k), tr + k / 6, 1.0, pan=0.35)
    for k in range(int(nxt("reader") - tr)):
        fx.add(O.tick(amp=0.4), tr + k, 1.0, pan=0.7)
    song(mus, "s1", "hotjazz")
    mus.add(tts("Doo-wah!", "chorus"), s1["start"] + 0.05, 0.6)
    fx.add(O.ding(0.7, 96), C["spot"], 1.0, pan=0.55)
    fx.add(O.whoosh(0.25, True, 5, 0.6), f("s1_spot") - 0.12, 1.0)
    Bd.groove(mus, s1["end"], CARDS[1][2] - 0.3, "hotjazz", 188, energy=lambda t: 0.3, level=0.55, riffs=False)
    for w in ("twenty-nine", "false"):
        fx.add(O.pop(0.7), Wx("a2", w) - 0.2, 1.0)
    fx.add(O.pop(0.7), E("a2") - 1.4, 1.0)
    fx.add(F.thud(1.0), C["stamp_decides"], 1.0)
    Bd.button(mus, CARDS[1][2] - 0.3, 0.8, key=53)

    # ---------------------------------------------------------------- ROOM 2: ska
    s2 = TL.songs["s2"]
    Bd.groove(mus, f("files"), s2["start"], "ska", 164, energy=lambda t: 0.35, level=0.6, riffs=False)
    for j, (word, _) in enumerate([("Symptoms", 0), ("pills", 0), ("lab", 0), ("old", 0), ("genes", 0), ("literature", 0)]):
        fx.add(O.woodblock(0.7, 700 + 60 * j), Wx("b1", word) - 0.15, 1.0, pan=0.4)
    fx.add(F.paper_flutter(1.6, amp=1.0), Wx("b1", "literature"), 1.0, pan=0.5)
    fx.add(F.thud(0.8), Wx("b1", "literature") + 0.5, 1.0)
    song(mus, "s2", "ska")
    amb.add(wide(F.paper_flutter, s2["end"] - s2["start"], amp=0.7), s2["start"], 1.0)
    for k, m in enumerate([84, 88, 91, 96, 100]):
        fx.add(O.celesta(m, 0.5), C["page"] - 0.2 + k * 0.06, 1.0, pan=0.4 + 0.05 * k)
    Bd.groove(mus, s2["end"], CARDS[2][2] - 0.3, "ska", 164, energy=lambda t: 0.3, level=0.5, riffs=False)
    fx.add(O.honk(0.8, 2), C["clash"] - 0.05, 1.0, pan=0.55)
    fx.add(O.cymbal(0.9, 1.2), C["clash"], 1.0, pan=0.55)
    Bd.button(mus, CARDS[2][2] - 0.3, 0.8, key=55)

    # ---------------------------------------------------------------- ROOM 3: the slow drag
    s3 = TL.songs["s3"]
    Bd.groove(mus, f("record"), s3["start"], "drag", 132, energy=lambda t: 0.3, level=0.55, riffs=False, melody=False)
    for i in range(10):
        fx.add(F.thud(0.5, i), f("record") + 0.25 * i + 0.3, 1.0, pan=0.3 + 0.04 * i)
    song(mus, "s3", "drag")
    fx.add(O.slide_whistle(False, nxt("s3_king") - f("s3_king") - 0.3, 0.3), f("s3_king") + 0.2, 1.0, pan=0.45)
    for k in range(int((nxt("s3_pills") - f("s3_pills")) * 132 / 60)):
        fx.add(O.woodblock(0.4, 1000 if k % 2 else 800), f("s3_pills") + k * 60 / 132, 1.0, pan=0.6)
    fx.add(O.boing(0.7), f("s3_scale") + 0.1, 1.0, pan=0.5)
    fx.add(O.heartbeat(4, 72, 0.9), f("s3_heart") + 0.2, 1.0, pan=0.5)
    for j in range(4):
        fx.add(F.thud(0.6, j), f("s3_fine") + 0.45 * j + 0.15, 1.0, pan=0.3 + 0.13 * j)
    fx.add(F.thud(1.0), f("s3_all") + 0.85, 1.0)
    mus.add(O.brass([50, 53, 56, 59], 0.6, amp=0.8, seed=9), f("s3_all") + 0.85, 1.0)             # a diminished stab
    fx.add(F.thud(1.2), C["evaluate"], 1.0)
    fx.add(O.cymbal(0.9, 1.4), C["evaluate"], 1.0)
    Bd.groove(mus, s3["end"] + 0.1, CARDS[3][2] - 0.3, "drag", 132, energy=lambda t: 0.25, level=0.45, riffs=False, melody=False)

    # ---------------------------------------------------------------- ROOM 4: new wave, and a false alarm
    s4 = TL.songs["s4"]
    Bd.groove(mus, f("ballroom"), s4["start"], "newwave", 176, energy=lambda t: 0.35, level=0.6, riffs=False)
    song(mus, "s4", "newwave")
    for i in range(1, 5):
        fx.add(O.pop(0.8), SL("s4", i) - 0.1, 1.0)
        fx.add(O.woodblock(0.6, 1100), SL("s4", i) - 0.05, 1.0, pan=0.6)
    fx.add(O.alarm_bell(0.6, 1.0), C["crow"] - 0.1, 1.0, pan=0.4)
    fx.add(tts("Cock-a-doodle-doo!", "am_puck", 1.1, 7.0) * 1.2, C["crow"] - 0.05, 1.0, pan=0.4)
    fx.add(O.honk(0.7, 1), C["crow"] + 0.35, 1.0, pan=0.65)
    # (dead silence until "Ahem.")
    Bd.groove(mus, S("d3") + 0.9, CARDS[4][2] - 0.3, "drag", 120, energy=lambda t: 0.2, level=0.4, riffs=False, melody=False)
    fx.add(O.pop(0.6), Wx("d3", "sepsis") - 0.3, 1.0)
    fx.add(O.pop(0.6), Wx("d3", "skin") - 0.3, 1.0)

    # ---------------------------------------------------------------- ROOM 5: the clinic, the tunnel, the flag
    tc = f("clinic")
    amb.add(F.room_tone(C["flag"] - tc, amp=1.2, hum=True), tc, 1.0)
    for k in range(int((C["flag"] - tc) / 0.9)):
        tb = tc + 0.3 + k * 0.9
        if not (E("f2") + 0.1 < tb < C["flag"]):
            fx.add(O.beep(0.08, 0.25, 1320), tb, 1.0, pan=0.7)                  # the monitor
    for k in range(6):
        mus.add(O.pizz(50 + (0, 3, 7, 10)[k % 4], amp=0.5), tc + 0.5 + k * 0.45, 1.0, pan=0.4)
    tn = f("tunnel")
    fx.add(O.whir(E("f2") + 0.1 - tn, amp=0.35, f=70), tn, 1.0)
    for k in range(3):
        fx.add(F.drip(0.6, k), tn + 0.4 + k * 0.5, 1.0, pan=0.3 + 0.2 * k)
    fx.add(O.ding(1.0, 100), C["flag"], 1.0, pan=0.55)
    fx.add(Bd.xylo_run([79, 84, 88, 91, 96], 0.05, 0.7), C["flag"] + 0.05, 1.0, pan=0.55)
    fx.add(O.whoosh(0.25, True, 6, 0.5), C["flag"] - 0.12, 1.0)
    for k in range(int((f("halved") - f("doclook")) / 0.9)):
        fx.add(O.beep(0.08, 0.2, 1320), f("doclook") + 0.2 + k * 0.9, 1.0, pan=0.7)
    th = f("halved")
    fx.add(O.pop(0.8), th + 0.05, 1.0)
    mus.add(O.snare_roll(TL.songs["s5"]["start"] - th, amp=0.7), th, 1.0)
    s5 = TL.songs["s5"]
    song(mus, "s5", "bigband")
    mus.add(tts("Ba-da-bop!", "chorus"), s5["start"] + 0.05, 0.6)
    Bd.groove(mus, s5["end"], f("door_back") + 1.2, "bigband", 196, energy=lambda t: 0.3, level=0.5, riffs=False)
    fx.add(F.creak(0.7, 0.6, seed=4), C["early_door"], 1.0, pan=0.35)

    # ---------------------------------------------------------------- back through the door: the real world, a year later
    tb = f("door_back")
    fx.add(O.whoosh(0.3, False, 7, 0.5), tb - 0.2, 1.0)
    amb.add(F.room_tone(f("bus") - tb, amp=1.0), tb, 1.0)
    amb.add(wide(F.birds, f("curtain") - tb, seed=5), tb, 1.0)
    band_bleed = Bus()                                                 # the band, still playing behind the pantry door
    Bd.groove(band_bleed, tb, f("curtain"), "bigband", 196, energy=lambda t: 0.6, level=0.7)
    y = signal.sosfilt(signal.butter(4, 700 / (SR / 2), "low", output="sos"), band_bleed.x, axis=1) * 0.5
    fade = np.ones(N)
    i0, i1 = int(f("bus") * SR), int((f("bus") + 2.0) * SR)
    fade[i0:i1] = np.linspace(1, 0.35, i1 - i0)
    fade[i1:] = 0.35
    mus.x += y * fade[None]
    tbus = f("bus")
    amb.add(wide(F.traffic, f("curtain") - tbus, amp=0.8, seed=9), tbus, 1.0)
    amb.add(wide(F.kids, f("curtain") - tbus, amp=1.0), tbus, 1.0)
    fx.add(O.honk(0.6, 2), tbus + 0.2, 1.0, pan=0.5)
    fx.add(O.ding(0.8, 101), f("glasses") + 1.0, 1.0, pan=0.6)             # the wink

    # ---------------------------------------------------------------- the curtain call
    tcur = f("curtain")
    Bd.fanfare(mus, tcur, 1.0, key=58)
    Bd.groove(mus, tcur + 0.4, f("end"), "bigband", 196, energy=lambda t: 0.55, level=0.8)
    amb.add(wide(O_applause, f("end") - tcur + 2.0, amp=0.6), tcur + 0.2, 1.0)
    mus.add(tts("Look twice!", "chorus"), tcur + 0.7, 0.8)
    Bd.button(mus, f("end"), 1.0, key=58)
    fx.add(O.projector(TL.total - f("end") - 0.5, 0.3), f("end") + 0.3, 1.0)


def O_applause(dur, amp=1.0, seed=3):
    return O.applause(dur, amp, seed)


def song(bus, key, style):
    """A patter song: intro and outro full, the band thinned under each lyric line and filled between them."""
    Sg = TL.songs[key]
    spans = [(TL.lines[l["key"]]["start"] - 0.05, TL.lines[l["key"]]["end"] + 0.05, TL.lines[l["key"]]["who"]) for l in Sg["lines"]]

    def energy(t):
        for a, b, who in spans:
            if a <= t <= b:
                return 0.75 if who == CHORUS else 0.35
        return 1.0
    Bd.groove(bus, Sg["start"], Sg["end"], style, Sg["bpm"], energy=energy, level=1.0)
    Bd.button(bus, Sg["end"] - 0.02, 0.9, key={"hotjazz": 53, "ska": 55, "drag": 50, "newwave": 57, "bigband": 58}[style])


def _bp(x, lo, hi):
    return signal.sosfilt(signal.butter(2, [lo / (SR / 2), hi / (SR / 2)], "band", output="sos"), x)


def reverb(x, wet=0.1, rt60=0.8, seed=8):
    rng = np.random.default_rng(seed)
    t = np.arange(int(rt60 * 1.4 * SR)) / SR
    ir = np.stack([rng.normal(0, 1, len(t)) * np.exp(-6.9 * t / rt60) for _ in range(2)])
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    y = np.stack([signal.fftconvolve(x[c], ir[c])[: x.shape[1]] for c in range(2)])
    return x * (1 - wet) + y * wet


def in_zone(t):
    """Is time t in the underworld (echo on the voices)?"""
    for i, e in enumerate(EDIT):
        t1 = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total
        if e[0] <= t < t1:
            return e[2] != "real"
    return False


def voices():
    dry, wet = np.zeros((2, N)), np.zeros((2, N))
    for key in TL.order:
        L = TL.lines[key]
        who = L["who"]
        up = signal.resample_poly(L["wav"].astype(np.float64), SR, VSR)
        r = np.sqrt((up ** 2).mean()) + 1e-12
        lvl = {EMCEE: -16.5, MAE: -17.0, DOC: -17.5, EYE: -17.5, OCTO: -17.0, CHORUS: -16.0}.get(who, -17.0)
        up = up * db(lvl) / r
        sig = np.stack([up, up])
        if who == CHORUS:                                               # a gang, a little wide
            d = int(0.011 * SR)
            sig = np.stack([up, np.concatenate([np.zeros(d), up[:-d]])])
        if who == DOC and key.startswith("f"):
            sig = sig * 1.0
        i = int(L["start"] * SR)
        j = min(N, i + sig.shape[1])
        zone = in_zone(L["start"] + 0.1)
        (wet if zone or who == EMCEE else dry)[:, i:j] += sig[:, : j - i]
    return dry + reverb(wet, 0.22, 1.1, seed=5)


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


def build():
    mus, amb, fx = Bus(), Bus(), Bus()
    score(mus, amb, fx)
    zone = np.zeros(N)                                                  # the underworld's room: a big echoey hall
    for i, e in enumerate(EDIT):
        t1 = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total
        if e[2] != "real":
            zone[int(e[0] * SR):int(t1 * SR)] = 1.0
    music = reverb(mus.x, 0.22, 1.6) + reverb(fx.x, 0.15, 0.9) + amb.x
    music = signal.sosfilt(signal.butter(4, 40 / (SR / 2), "high", output="sos"), music, axis=1)
    music = np.tanh(1.2 * music) / 1.2                                  # a little tape drive
    dead = np.ones(N)
    for a, b in SILENCES:
        dead[int(a * SR):int(b * SR)] = 0.0
    k = int(0.008 * SR)
    dead = np.convolve(dead, np.ones(k) / k, "same")
    music = music * dead
    vo = presence(voices(), 3000, 2.5)
    from scipy.ndimage import maximum_filter1d
    raw = np.convolve(np.abs(vo.mean(axis=0)), np.ones(SR // 20) / (SR // 20), mode="same")
    raw = np.clip(raw / (np.percentile(raw[raw > 1e-5], 80) + 1e-9), 0, 1)
    env = maximum_filter1d(raw, size=int(1.0 * SR), origin=-int(0.2 * SR))
    env = np.convolve(env, np.ones(SR // 4) / (SR // 4), mode="same")
    low = signal.lfilter(*signal.butter(2, 250 / (SR / 2), "low"), music)
    high = signal.lfilter(*signal.butter(2, 4500 / (SR / 2), "high"), music)
    mid = music - low - high
    music = low * (1 - 0.3 * env) + mid * (1 - 0.6 * env) + high * (1 - 0.35 * env)
    music = mono_safe(music, max_ratio=1.0)
    ref = music[:, int(TL.songs["s1"]["start"] * SR):int(TL.songs["s1"]["end"] * SR)]
    music = music * db(-18.0) / (np.sqrt((ref ** 2).mean()) + 1e-12)
    band = lambda x: signal.sosfilt(signal.butter(2, [300 / (SR / 2), 4000 / (SR / 2)], "band", output="sos"), x.mean(axis=0))
    bm, bv = band(music), band(vo)
    ride = np.ones(N)
    for key in TL.order:
        L = TL.lines[key]
        a, b = int(L["start"] * SR), int(L["end"] * SR)
        rv = np.sqrt((bv[a:b] ** 2).mean()) + 1e-12
        rm = np.sqrt((bm[a:b] ** 2).mean()) + 1e-12
        margin = 20 * np.log10(rv / rm)
        target = 12.0 if L["who"] == CHORUS else 14.0
        if margin < target:
            lo, hi = max(0, a - int(0.2 * SR)), min(N, b + int(0.3 * SR))
            ride[lo:hi] = np.minimum(ride[lo:hi], db(margin - target))
    k = int(0.35 * SR)
    ride = np.convolve(np.pad(ride, k, mode="edge"), np.ones(k) / k, "same")[k:-k]
    music = music * ride
    mix = music + vo
    mix = signal.sosfilt(signal.butter(4, 35 / (SR / 2), "high", output="sos"), mix, axis=1)
    shape = np.where(zone > 0, 1.0, -2.0)                                # the real world a little quieter than the zone
    k = int(0.3 * SR)
    shape = np.convolve(np.pad(shape, k, mode="edge"), np.ones(k) / k, "same")[k:-k]
    mix = mix * db(shape)[None]
    mix = loudness(mix, -14.0)
    a_, b_ = int((TL.total - 1.8) * SR), int(TL.total * SR)
    mix[:, a_:b_] *= np.linspace(1, 0, b_ - a_) ** 2
    mix[:, b_:] = 0.0
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
