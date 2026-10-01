"""The soundtrack: the prog-rock horror band (prog.py) and the foley placed against the edit, the voices, the mix.

The score lives in extremes: a lullaby and a drone under the night, then the whole band crashing in at full volume
(the title; the reflection that stops; the hidden door opening) and cutting to dead silence. Three dead silences
(after the title; before the hidden door; when her heart stops) and five jump-scare stings (the phone on the floor,
the man who turns, the reflection, her own body, the phone that lights up by itself). Voices always sit well clear of
the music (a slow duck plus a ride per line). Loudness -14 LUFS.
"""
import os
import wave

import numpy as np
from scipy import signal

import fxlib as FX
import orch as O
import prog as P
from cues import C, E, S, Wx
from edit import EDIT, first, nxt
from script import AI, DISP, DOC, N, NORA, W as WH
from timeline import TL
from voice import SR as VSR

SR = O.SR
HERE = os.path.dirname(os.path.abspath(__file__))
N_ = int((TL.total + 0.6) * SR)
f = first


def db(v):
    return 10 ** (v / 20)


def wide(fn, dur, *a, **k):
    seed = k.pop("seed", 1)
    return np.stack([fn(dur, *a, seed=seed, **k), fn(dur, *a, seed=seed + 101, **k)])


class Bus:
    def __init__(self):
        self.x = np.zeros((2, N_))

    def add(self, sig, t, gain=1.0, pan=0.5):
        if sig is None:
            return
        if sig.ndim == 1:
            sig = np.stack([sig * np.sqrt(1 - pan), sig * np.sqrt(pan)]) * np.sqrt(2)
        i = int(t * SR)
        if i >= N_ or i + sig.shape[1] <= 0:
            return
        if i < 0:
            sig, i = sig[:, -i:], 0
        j = min(N_, i + sig.shape[1])
        self.x[:, i:j] += gain * sig[:, : j - i]


# dead silence: everything cut (music, foley, ambience)
SILENCES = [(C["dead1"] + 0.02, f("exterior") + 0.05), (C["dead2"], S("h1") - 0.25), (C["dead3"], C["rewind"] - 0.02)]
# the crash-ins: the score at full volume
CRASHES = [(C["title"], C["dead1"]), (C["sting3"], C["sting3"] + 0.95), (C["door_open"], S("x1") - 0.35)]


STG = []                                         # the stings: their own bus, never ducked, a dip in the music before each


def heartbeats(bus, t0, t1, bpm0, bpm1=None, amp=1.0, pan=0.5):
    bpm1 = bpm0 if bpm1 is None else bpm1
    t = t0
    while t < t1:
        u = (t - t0) / max(1e-6, t1 - t0)
        bpm = bpm0 + (bpm1 - bpm0) * u
        bus.add(O.heartbeat(1, bpm, amp), t, 1.0, pan=pan)
        t += 60.0 / bpm


def score(mus, amb, fx):
    STG.clear()
    # ---------------------------------------------------------------- cold open
    mus.add(P.drone(C["title"] + 0.2, 33, 1.2, seed=1), 0.0, 1.0)
    P.lullaby(mus, 0.25, beat=0.55, amp=0.45, notes=P.LULLABY[:6])
    heartbeats(fx, 0.4, C["sting1"], 64, 70, 0.5)
    amb.add(wide(FX.rain, C["title"], amp=0.35), 0.0, 1.0)
    fx.add(O.thunder(2.0, 0.6, seed=2), 1.25, 1.0, pan=0.3)
    STG.append((C["sting1"], P.sting(1.0, seed=1)))                                # jump scare 1: the phone on the floor
    fx.add(P.breath(1.6, 0.8, seed=2, shaky=1.0), C["sting1"] + 0.4, 1.0)
    mus.add(O.music_box(P.LULLABY[:8], rate=lambda u: 1 - 0.6 * u, detune=lambda u: -80 * u, amp=0.5), f("door100"), 1.0, pan=0.55)
    mus.add(P.whispers_inv(C["title"] - f("door100"), 0.6, seed=3), f("door100"), 1.0)
    # the title: the band crashes in at full volume ... then dead silence
    P.crash_in(mus, C["title"], C["dead1"] - C["title"], level=1.0, seed=2, words="Ahvenna! Sorah! Kelemai!")
    fx.add(O.thunder(2.2, 1.0, seed=3), C["title"], 1.0)

    # ---------------------------------------------------------------- the storm, the hotel
    te = f("exterior")
    amb.add(wide(FX.rain, f("lobby") - te + 0.4, amp=1.0), te, 1.0)
    amb.add(wide(P.wind, f("checks") - te, amp=0.8), te, 1.0)
    fx.add(O.thunder(3.0, 0.9, seed=4), C["storm"], 1.0, pan=0.35)
    for k in range(9):
        fx.add(P.footstep(0.45, seed=k, wet=True), te + 0.5 + k * 0.42, 1.0, pan=0.4 + 0.02 * k)
    fx.add(O.whir(2.5, amp=0.25, f=55), te, 1.0, pan=0.25)                         # the taxi pulling away
    mus.add(P.drone(f("lobby") - te, 33, 0.7, seed=5), te, 1.0)
    # a year of right answers: the lullaby, sweet; a chime on each one
    tc = f("checks")
    P.lullaby(mus, tc + 0.1, beat=0.5, amp=0.55, notes=P.LULLABY[:9])
    for k, w in (("p2", "Flights"), ("p2", "emails"), ("p2", "taxes"), ("p2", "fever")):
        fx.add(P.notify(0.5), Wx(k, w) - 0.1, 1.0, pan=0.6)
    # she stopped checking: the music box slows and goes out of tune
    mus.add(O.music_box(P.LULLABY[9:], rate=lambda u: 1 - 0.55 * u, detune=lambda u: -110 * u, amp=0.55), f("nocheck"), 1.0, pan=0.5)
    # the lobby: a big echoing room, a clock, the desk bell, 99 keys; the key that makes 100
    tl = f("lobby")
    amb.add(FX.room_tone(f("clock") - tl, amp=1.2), tl, 1.0)
    for k in range(int(f("clock") - tl)):
        fx.add(P.tick(0.4, k % 2), tl + 0.3 + k, 1.0, pan=0.7)
    fx.add(P.desk_bell(0.8), tl + 0.4, 1.0, pan=0.35)
    fx.add(P.bouzouki(64, 1.2, 0.6, trem=12), tl + 0.9, 1.0, pan=0.6)
    fx.add(P.keys_jingle(0.9), C["key_desk"] + 0.1, 1.0, pan=0.6)
    mus.add(P.drone(f("clock") - tl + 0.5, 34, 0.8, seed=6), tl, 1.0)

    # ---------------------------------------------------------------- RED: her room
    tr = f("clock")
    t_wall = f("spiral")
    amb.add(wide(FX.rain, t_wall - tr, amp=0.55), tr, 1.0)                         # rain on the window
    for k in range(int((f("type") - tr) / 1.0)):
        fx.add(P.tick(0.55, k % 2), tr + 0.1 + k, 1.0, pan=0.65)
    fx.add(O.thunder(2.5, 0.8, seed=6), S("r1") - 1.2, 1.0, pan=0.75)
    fx.add(O.thunder(2.5, 0.7, seed=7), S("r1") + 2.6, 1.0, pan=0.75)
    mus.add(P.drone(t_wall - tr, 33, 0.9, seed=7, sweep=0.06), tr, 1.0)
    heartbeats(fx, S("r1"), f("answer"), 84, 96, 0.7)
    fx.add(P.breath(1.4, 0.8, seed=3, shaky=1.0), Wx("r1", "sick"), 1.0)
    for k in range(14):                                                             # her thumb on the glass
        fx.add(P.tap(0.6, seed=k), f("type") + 0.4 + k * 0.17, 1.0, pan=0.55)
    fx.add(O.whoosh(0.25, True, 2, 0.3), E("r2") - 0.1, 1.0, pan=0.6)
    for k in range(6):                                                              # waiting: tabla, very soft
        mus.add(P.tabla("ge", 0.35, seed=k), f("faceglow") + 0.2 + k * 0.6, 1.0, pan=0.45)
    fx.add(P.notify(0.8), S("r4") - 0.15, 1.0, pan=0.55)                          # the answer arrives, sweetly
    P.lullaby(mus, S("r4") + 0.1, beat=0.6, amp=0.4, notes=P.LULLABY)              # and the lullaby comes back
    heartbeats(fx, f("relief"), f("liewall"), 92, 78, 0.5)
    for k in range(8):                                                              # the scale: low bass pulses
        mus.add(P.fuzz_bass(33, 0.5, 0.35), f("scale") + 0.3 + k * 1.0, 1.0)
    # through the wall: the same voice, muffled
    muff = P.tts_fx("This contract protects you.", "bf_emma*0.55+af_heart*0.45", 0.98, -0.5)
    muff = signal.sosfilt(signal.butter(4, 500 / (SR / 2), "low", output="sos"), muff) * 0.35
    fx.add(muff, Wx("r7", "voice") + 0.5, 1.0, pan=0.3)
    fx.add(P.board_creak(0.8, seed=1), E("r7") - 0.2, 1.0, pan=0.4)

    # ---------------------------------------------------------------- the stair, the corridor, ROOM 97
    ts = f("spiral")
    mus.add(O.theremin(220, 880, nxt("spiral") - ts + 0.2, amp=0.6), ts, 1.0, pan=0.5)
    mus.add(P.bouzouki(69, nxt("spiral") - ts, 0.6, trem=16), ts, 1.0, pan=0.65)
    mus.add(P.whispers_inv(nxt("spiral") - ts + 0.6, 0.9, seed=7), ts, 1.0)
    t97 = f("corr97")
    for k in range(6):
        fx.add(P.footstep(0.5, seed=10 + k), t97 + 0.15 + k * 0.4, 1.0, pan=0.45 + 0.1 * (k % 2))
        if k % 2:
            fx.add(P.board_creak(0.6, seed=k), t97 + 0.25 + k * 0.4, 1.0, pan=0.4)
    heartbeats(fx, t97, f("blue"), 96, 100, 0.6)
    mus.add(P.drone(f("turn") - t97, 32, 0.9, seed=8), t97, 1.0)
    tb = f("blue")
    fx.add(O.thunder(2.0, 0.6, seed=8), S("b2") + 0.6, 1.0, pan=0.5)

    def en(t):
        for k in TL.order:
            if TL.lines[k]["start"] - 0.1 <= t <= TL.lines[k]["end"] + 0.1:
                return 0.35
        return 1.0
    P.groove(mus, tb, f("turn") - 0.05, 0.2, level=0.7, light=True, seed=3, energy=en)
    fx.add(FX.pencil(nxt("pen") - f("pen"), 1.2), f("pen"), 1.0, pan=0.55)
    amb.add(wide(FX.paper_flutter, nxt("papers") - f("papers"), amp=0.6), f("papers"), 1.0)
    for k in range(6):
        fx.add(FX.thud(0.55, k), Wx("b3", "invented") - 0.2 + k * 0.15, 1.0, pan=0.3 + 0.08 * k)
    fx.add(FX.thud(1.2, 9), Wx("b3", "five") - 0.02, 1.0)
    fx.add(O.timpani(33, 0.8), Wx("b3", "five") - 0.02, 1.0)
    STG.append((C["sting2"], P.sting(1.0, seed=2)))                                # jump scare 2: he turns
    fx.add(P.growl_words("Sorah", 0.7), C["sting2"] + 0.1, 1.0)

    # ---------------------------------------------------------------- ROOM 98
    t98 = f("corr98")
    for k in range(6):
        fx.add(P.footstep(0.5, seed=20 + k), t98 + 0.1 + k * 0.42, 1.0, pan=0.45 + 0.1 * (k % 2))
    tg = f("green")
    P.groove(mus, t98 + 0.8, f("norahall"), 0.18, level=0.75, seed=5, energy=en)
    for k in range(14):
        fx.add(P.coin(0.8, seed=k), tg + 0.4 + k * 0.17, 1.0, pan=0.6)
    fx.add(P.neon_buzz(nxt("safe") - f("safe"), 1.0, flicker=1.0), f("safe"), 1.0, pan=0.5)
    fx.add(P.glass_crack(1.0), Wx("g3", "change") - 1.0, 1.0)
    amb.add(wide(P.wind, nxt("drain") - f("drain"), amp=0.6, seed=6), f("drain"), 1.0)
    for k in range(20):
        fx.add(P.coin(0.5, seed=40 + k), f("drain") + 0.2 + k * 0.4, 1.0, pan=0.3 + 0.03 * k)
    fx.add(P.coin(0.9, seed=99), f("vault") + 0.5, 1.0, pan=0.7)
    tn = f("norahall")
    heartbeats(fx, tn, f("mirrors"), 112, 120, 1.0)
    for k in range(3):
        fx.add(P.breath(1.5, 1.0, seed=10 + k, shaky=1.0), tn + 0.3 + k * 1.7, 1.0)
    mus.add(P.drone(f("mirrors") - tn, 32, 0.8, seed=9), tn, 1.0)

    for nm, bpm in (("nb1", 108), ("nb2", 116), ("nb3", 124)):
        tb_ = f(nm)
        heartbeats(fx, tb_, nxt(nm), bpm, bpm, 1.3)
        fx.add(P.breath(1.3, 1.3, seed=hash(nm) % 40, shaky=1.0), tb_ + 0.05, 1.0)
    # ---------------------------------------------------------------- ROOM 99: mirrors
    tm = f("mirrors")
    mus.add(P.drone(C["sting3"] - tm, 33, 0.9, seed=10, sweep=0.2), tm, 1.0)
    P.lullaby(mus, tm + 0.2, beat=0.5, amp=0.5, notes=P.LULLABY, inst="celesta", pan=0.35)
    mus.add(P.whispers_inv(C["sting3"] - tm, 0.8, seed=11), tm, 1.0)
    for k in range(int((C["sting3"] - tm) / (1 / 0.9))):                            # the nodding, in time
        fx.add(P.tick(0.25, k % 2), tm + k / 0.9, 1.0, pan=0.5)
    for k in range(6):
        mus.add(P.fuzz_bass(33, 0.4, 0.3), f("chart") + 1.2 + k * 1.3, 1.0)
    STG.append((C["sting3"], P.sting(1.0, seed=3)))                                # jump scare 3: the reflection
    P.crash_in(mus, C["sting3"], 0.95, level=1.0, seed=4, words="Anakré! Tovéh!")
    mus.add(P.drone(C["dead2"] - S("m4") + 0.1, 32, 0.6, seed=12), S("m4"), 1.0)
    fx.add(P.keys_jingle(0.7, seed=3), E("m4") - 0.1, 1.0, pan=0.55)
    # (dead silence)

    # ---------------------------------------------------------------- the hidden door: the paradox
    th = S("h1") - 0.25
    for k in ("h1", "h2", "h3"):
        fx.add(P.lock_click(1.0, seed=hash(k) % 50), S(k) - 0.1, 1.0, pan=0.5)
    mus.add(P.drone(C["door_open"] - th, 33, 1.0, seed=13, sweep=0.1), th, 1.0)
    mus.add(P.shepard(C["door_open"] - th, 1.0), th, 1.0)
    heartbeats(fx, th, C["door_open"], 100, 132, 0.8)
    for k in range(int((C["door_open"] - f("simulator")) / 0.4)):                   # tabla quickening
        mus.add(P.tabla("na" if k % 2 else "ge", 0.35 + 0.02 * k, seed=k), f("simulator") + k * 0.4 * (1 - 0.004 * k), 1.0, pan=0.45)
    fx.add(O.creak(1.2, 1.0, seed=5) if hasattr(O, "creak") else FX.creak(1.2, 1.0, seed=5), C["door_open"] - 0.3, 1.0, pan=0.4)
    # the door opens: the whole band, full volume, the truth in blazing colour
    P.crash_in(mus, C["door_open"], S("x1") - 0.35 - C["door_open"], level=1.0, seed=6, words="Ahvenna! Selenna! Ahvenna!")
    STG.append((C["sting4"], P.sting(1.0, seed=4)))                                # jump scare 4: her own body
    heartbeats(fx, S("h7"), S("x1") - 0.35, 132, 120, 1.2)

    # ---------------------------------------------------------------- the risk at 100%: she rested
    tx_ = S("x1") - 0.35
    amb.add(wide(FX.rain, C["dead3"] - tx_, amp=0.3), tx_, 1.0)
    heartbeats(fx, tx_, C["flat"], 70, 34, 1.0)
    fx.add(P.breath(2.6, 0.7, seed=20), tx_ + 0.2, 1.0)
    # (dead silence)

    # ---------------------------------------------------------------- the same night, once more
    trw = C["rewind"]
    fx.add(P.tape_rewind(f("same") - trw, 1.0), trw, 1.0)
    mus.add(O.music_box(P.LULLABY[::-1][:8], amp=0.4), trw, 1.0, pan=0.5)
    amb.add(wide(FX.rain, C["siren"] - trw, amp=0.5), trw, 1.0)
    heartbeats(fx, f("same"), f("dial"), 96, 104, 0.8)
    mus.add(P.drone(C["siren"] - f("same"), 33, 0.7, seed=14), f("same"), 1.0)
    for k in range(8):
        mus.add(P.tabla("ge", 0.4, seed=k), f("believe") + 0.1 + k * 0.45, 1.0, pan=0.45)
    td = f("dial")
    for k, dg in enumerate("911"):
        fx.add(P.dtmf(dg, 0.16, 1.0), td + 0.1 + k * 0.22, 1.0, pan=0.55)
    fx.add(P.ringback(0.8, 1.0), td + 0.8, 1.0, pan=0.55)
    # dawn: the siren, then birds and the lullaby in a major key
    tdw = C["siren"]
    fx.add(O.siren(3.0, 0.8), tdw - 0.3, 1.0, pan=0.6)
    fx.add(O.siren(2.0, 0.4), tdw + 2.6, 1.0, pan=0.7)
    amb.add(wide(FX.birds, f("coda") - tdw, amp=1.0), tdw + 0.4, 1.0)
    mus.add(P.drone(f("coda") - tdw, 45, 0.5, seed=15, sweep=0.05), tdw, 1.0)
    P.lullaby(mus, tdw + 0.3, beat=0.62, amp=0.5, notes=P.DAWN)
    P.lullaby(mus, f("window") + 0.1, beat=0.62, amp=0.55, notes=P.DAWN)
    for k in range(int((f("window") - f("hospital")) / (60 / 72))):
        fx.add(P.monitor_beep(0.8), f("hospital") + 0.2 + k * 60 / 72, 1.0, pan=0.3)
    for k in range(4):
        mus.add(P.bouzouki([69, 73, 76, 81][k], 1.0, 0.45, trem=10), f("three") + 0.3 + k * 1.5, 1.0, pan=0.62)
    # ---------------------------------------------------------------- the coda: dark again
    tco = f("coda")
    amb.add(wide(FX.rain, TL.total - tco, amp=0.5), tco, 1.0)
    fx.add(P.notify(0.6), S("e4") - 0.25, 1.0, pan=0.55)
    STG.append((C["sting5"], P.sting(1.0, seed=5)))                                # jump scare 5: the eye snaps open
    mus.add(P.whispers_inv(2.0, 1.0, seed=19), C["sting5"] + 0.3, 1.0)
    mus.add(O.music_box(P.LULLABY[:10], rate=lambda u: 1 - 0.6 * u, detune=lambda u: -120 * u, amp=0.5), f("end") + 0.2, 1.0)


def reverb(x, wet=0.1, rt60=0.8, seed=8):
    rng = np.random.default_rng(seed)
    t = np.arange(int(rt60 * 1.4 * SR)) / SR
    ir = np.stack([rng.normal(0, 1, len(t)) * np.exp(-6.9 * t / rt60) for _ in range(2)])
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    y = np.stack([signal.fftconvolve(x[c], ir[c])[: x.shape[1]] for c in range(2)])
    return x * (1 - wet) + y * wet


def voices():
    """Each voice its own treatment: the narrator close and dry; the Voice clean with a faint digital double; the
    whisperer wide and far back; the dispatcher down a phone line; Nora and the doctor in the room."""
    dry, wet = np.zeros((2, N_)), np.zeros((2, N_))
    for key in TL.order:
        L = TL.lines[key]
        who = L["who"]
        w0 = L["wav"]
        if who == N:                                                    # breath under her voice: closer, more of a whisper
            from voice import whisper
            br = whisper(w0, keep=0.0, seed=7)
            w0 = w0 + 0.12 * br * np.sqrt((w0 ** 2).mean() / ((br ** 2).mean() + 1e-12))
        up = signal.resample_poly(w0.astype(np.float64), SR, VSR)
        if who == DISP:
            up = signal.sosfilt(signal.butter(4, [350 / (SR / 2), 3200 / (SR / 2)], "band", output="sos"), up)
            up = np.tanh(2.0 * up / (np.abs(up).max() + 1e-9))
        r = np.sqrt((up ** 2).mean()) + 1e-12
        lvl = {N: -16.0, AI: -16.5, WH: -15.5, NORA: -16.5, DISP: -18.0, DOC: -16.5}.get(who, -17.0)
        up = up * db(lvl) / r
        sig = np.stack([up, up])
        if who == AI:                                                   # the polished double: a few ms, a few cents
            d = int(0.009 * SR)
            dbl = signal.resample(up, int(len(up) * 1.003))[: len(up)]
            sig = np.stack([up + 0.3 * np.concatenate([np.zeros(d), dbl[:-d]]), up + 0.3 * dbl])
        if who == WH:                                                   # wide, unsettled
            d = int(0.018 * SR)
            sig = np.stack([up, np.concatenate([np.zeros(d), up[:-d]])]) * np.array([[1.0], [0.85]])
        i = int(L["start"] * SR)
        j = min(N_, i + sig.shape[1])
        (wet if who in (WH, AI, DOC) else dry)[:, i:j] += sig[:, : j - i]
    return dry + reverb(wet, 0.18, 1.0, seed=5)


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
    music = mono_safe(reverb(mus.x, 0.25, 1.8) + reverb(fx.x, 0.15, 0.9), max_ratio=1.0) + amb.x     # the ambience stays wide
    music = signal.sosfilt(signal.butter(4, 35 / (SR / 2), "high", output="sos"), music, axis=1)
    music = np.tanh(1.1 * music) / 1.1
    # the crash-ins at full volume, the rest of the night far below them
    shape = np.full(N_, -12.0)
    for a, b in CRASHES:
        shape[int(a * SR):int(b * SR)] = 0.0
    k = int(0.02 * SR)
    shape = np.convolve(np.pad(shape, k, mode="edge"), np.ones(k) / k, "same")[k:-k]
    dead = np.ones(N_)
    for a, b in SILENCES:
        dead[int(a * SR):int(b * SR)] = 0.0
    k = int(0.006 * SR)
    dead = np.convolve(dead, np.ones(k) / k, "same")
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
    ref = music[:, int(C["title"] * SR):int(C["dead1"] * SR)]
    music = music * db(-9.0) / (np.sqrt((ref ** 2).mean()) + 1e-12) * db(shape)[None]
    band = lambda x: signal.sosfilt(signal.butter(2, [300 / (SR / 2), 4000 / (SR / 2)], "band", output="sos"), x.mean(axis=0))
    bm, bv = band(music), band(vo)
    ride = np.ones(N_)
    for key in TL.order:
        L = TL.lines[key]
        a, b = int(L["start"] * SR), int(L["end"] * SR)
        rv = np.sqrt((bv[a:b] ** 2).mean()) + 1e-12
        rm = np.sqrt((bm[a:b] ** 2).mean()) + 1e-12
        margin = 20 * np.log10(rv / rm)
        if margin < 15.0:
            lo, hi = max(0, a - int(0.15 * SR)), min(N_, b + int(0.25 * SR))
            ride[lo:hi] = np.minimum(ride[lo:hi], db(margin - 15.0))
    k = int(0.25 * SR)
    ride = np.convolve(np.pad(ride, k, mode="edge"), np.ones(k) / k, "same")[k:-k]
    music = music * ride * dead[None]
    # the stings: on their own, never ducked, 3 dB over the loudest speech, with the music dipped just before each
    def rms50(x):
        k_ = SR // 20
        e_ = np.sqrt(np.convolve(x ** 2, np.ones(k_) / k_, "same"))
        return e_
    vref = np.percentile(rms50(vo.mean(axis=0))[np.abs(vo.mean(axis=0)) > 1e-4], 95)
    stg = Bus()
    dip = np.ones(N_)
    for t_, sg in STG:
        sg = np.tanh(3.0 * sg / (np.abs(sg).max() + 1e-12)) / np.tanh(3.0)          # denser: more weight per peak
        pk = rms50(sg).max()
        stg.add(sg * vref * db(7.0) / (pk + 1e-12), t_, 1.0)
        i0, i1 = int((t_ - 0.25) * SR), int((t_ + 0.01) * SR)
        dip[i0:i1] = np.minimum(dip[i0:i1], db(-24))
    k = int(0.01 * SR)
    dip = np.convolve(np.pad(dip, k, mode="edge"), np.ones(k) / k, "same")[k:-k]
    music = music * dip[None]
    mix = music + vo + reverb(stg.x, 0.2, 1.4, seed=9) * dead[None]
    mix = signal.sosfilt(signal.butter(4, 30 / (SR / 2), "high", output="sos"), mix, axis=1)
    mix = loudness(mix, -14.0)
    a_, b_ = int((TL.total - 1.5) * SR), int(TL.total * SR)
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
