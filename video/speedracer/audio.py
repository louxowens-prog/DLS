"""Soundtrack: an original, synthesized 1960s big band under the narration, and the race around it.

Every transition in edit.py gets a hit (a horn stab plus drums, and a whoosh on wipes). The announcer is put
through a stadium PA with the crowd swelling under him. Loudness is set with a static gain (no compressor),
so the contrast between the quiet explanations and the loud race moments survives.
Writes build/audio.wav (48 kHz stereo).
"""
import os
import wave

import numpy as np
from scipy import signal

import bigband as B
import jazz as J
import synth as S
from cues import C
from edit import EDIT, WIPE
from timeline import TL
from voice import SR as VSR

SR = B.SR
HERE = os.path.dirname(os.path.abspath(__file__))
N = int((TL.total + 0.5) * SR)
BAR = 4 * B.BEAT

# eight-bar loop in B-flat: Bb6 | G7b9 | Cm9 | F13 | Bb6 | Bb7 | Eb9 | Edim7
CHORDS = [[58, 62, 65, 67, 70, 74], [55, 59, 62, 65, 68, 71], [60, 63, 67, 70, 74], [53, 57, 63, 67, 74],
          [58, 62, 65, 67, 70, 74], [58, 62, 65, 68, 72], [63, 67, 70, 73, 77], [64, 67, 70, 73]]
ROOTS = [34, 31, 36, 29, 34, 34, 39, 40]


def db(v):
    return 10 ** (v / 20)


def chord_at(t):
    return CHORDS[int(t / BAR) % 8]


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


def short(sig, dur):
    """Choke a cymbal: fade it out by dur seconds so its tail never sits under the next line."""
    n = int(dur * SR)
    out = sig[: n].copy()
    out *= np.linspace(1, 0, len(out)) ** 1.5
    return out


def stereo_crowd(dur, seed=0):
    """A stadium on both sides: mostly independent roars in each ear, a little shared centre."""
    l, r, m = B.crowd(dur, seed=seed), B.crowd(dur, seed=seed + 101), B.crowd(dur, seed=seed + 202)
    return np.stack([0.8 * l + 0.45 * m, 0.8 * r + 0.45 * m]) * 0.9


def widen(x, amt):
    """Mid/side widener: the side is an all-pass-decorrelated copy of the mid, so the mono sum is untouched."""
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
    side = side + amt * S._hp(d, 180)                                     # keep the low end centred
    return np.stack([mid + side, mid - side])


def energy_curve():
    E = lambda k: TL.s(k)
    pts = [(0, 0.9), (1.0, 0.6), (C["go"] - 0.05, 0.75), (C["go"], 0.0), (C["go"] + 1.2, 0.0), (C["go"] + 1.22, 1.0), (E("h2"), 0.8), (E("d1"), 0.5),
           (E("d2"), 0.55), (E("d4"), 0.45), (E("d5"), 0.6), (E("d6"), 0.8), (E("d7"), 0.45), (E("e1"), 0.5), (E("e2"), 0.6),
           (E("a1"), 0.7), (E("t2"), 1.0), (E("t3"), 0.6), (E("t4"), 0.55), (E("t6"), 0.45), (E("u1"), 0.5), (E("u2"), 0.8),
           (E("u3"), 0.55), (E("a2"), 0.8), (E("v2"), 0.75), (C["crash"] - 0.02, 0.9), (C["crash"], 0.0), (C["crash"] + 1.0, 0.0),
           (C["crash"] + 1.02, 0.7), (E("v4"), 0.5), (E("w1"), 0.6), (E("a3"), 0.4), (E("w2"), 0.3), (E("f1"), 1.0),
           (C["end_card"], 1.0), (C["end_card"] + 0.4, 0.0), (C["end"], 0.0)]
    xs, ys = zip(*sorted(pts))
    return lambda t: float(np.interp(t, xs, ys))


def walking_bass(bus, E):
    nb = int(TL.total / B.BEAT)
    rng = np.random.default_rng(3)
    for b in range(nb):
        t = b * B.BEAT
        if E(t) <= 0.02:
            continue
        bar, beat = divmod(b, 4)
        root = ROOTS[bar % 8]
        nxt = ROOTS[(bar + 1) % 8]
        ch = [m - 24 for m in CHORDS[bar % 8]]
        if beat == 0:
            m = root
        elif beat == 3:
            m = nxt + (1 if rng.random() < 0.5 else -1)                 # chromatic approach
        else:
            m = int(rng.choice([c for c in ch if 28 <= c <= 50] or [root + 7]))
        bus.add(B.upright(B.midi(m), B.BEAT * 0.95, seed=b), t, 0.55 * (0.7 + 0.3 * E(t)))


def pads(bus, E):
    """Sustained sax chords, two bars each, a soft bed under the voice."""
    nbar = int(TL.total / BAR)
    for k in range(0, nbar, 1):
        t = k * BAR
        if E(t + 0.1) <= 0.02:
            continue
        bus.add(B.pad(CHORDS[k % 8], BAR * 0.98, seed=k), t, 0.16)


def backgrounds(bus, E):
    """Big-band 'backgrounds': a trombone-and-sax 'bwaaa-ap' figure every other bar."""
    nbar = int(TL.total / BAR)
    for k in range(1, nbar, 2):
        t = k * BAR
        if E(t) < 0.3:
            continue
        ch = CHORDS[k % 8]
        bus.add(B.chord_hit(ch[:4], dur=B.BEAT * 1.4, kinds=("sax", "tbn", "sax"), seed=k * 3), t, 0.18)
        bus.add(B.chord_hit(ch[:4], dur=B.BEAT * 0.4, kinds=("sax", "tbn", "sax"), seed=k * 3 + 1), t + 2.5 * B.BEAT, 0.16)


def fanfare(bus, t_end, seed=0):
    """A trumpet call leading into an announcer line: Bb, D, F, Bb (with a doit)."""
    notes = [70, 74, 77, 82]
    d = 0.11
    t0 = t_end - d * 3 - 0.28
    for i, m in enumerate(notes):
        dur = d if i < 3 else 0.28
        bus.add(B.horn(B.midi(m), dur, "tpt", 0.55, doit=2 if i == 3 else 0, seed=seed + i), t0 + i * d, 0.5)
        bus.add(B.horn(B.midi(m - 12), dur, "tpt", 0.4, seed=seed + 10 + i), t0 + i * d, 0.35)


STEMS = {}


def build():
    E = energy_curve()
    band, fx, crowd_bus = Bus(), Bus(), Bus()
    T = TL.total

    drums = B.swing_kit(T, E, seed=5)
    band.add(np.stack([drums * 0.95, drums]), 0.0, 1.0)
    walking_bass(band, E)
    pads(band, E)
    backgrounds(band, E)

    # ---- the grid: revs, lights, the launch in slow motion, then everyone goes
    fx.add(B.chord_hit([58, 65, 70, 74, 77, 82], dur=0.5, seed=1, doit=2), 0.0, 0.9)          # frame one: the band hits
    fx.add(short(J.crash(seed=2), 0.6), 0.0, 0.6)
    fx.add(J.kick(seed=3), 0.0, 1.0)
    for k, t in enumerate((0.9, 2.6)):
        fx.add(B.passby(1.3, seed=4 + k), t, 0.16)
    crowd_bus.add(stereo_crowd(T, seed=4), 0.0, 1.0)
    for k in range(8):                                                       # snare roll into the launch
        fx.add(J.snare(seed=200 + k, tight=0.6), C["go"] - 0.8 + k * 0.1, 0.07 + 0.03 * k)
    fx.add(B.chord_hit([58, 65, 70, 74, 77, 82], dur=0.9, seed=7), C["go"], 0.9)
    fx.add(short(J.crash(seed=8), 0.8), C["go"], 0.6)
    fx.add(J.kick(seed=9), C["go"], 1.0)
    slow = B._lp(np.random.default_rng(10).normal(0, 1, int(1.2 * SR)), 260) * np.linspace(0.2, 1, int(1.2 * SR))
    fx.add(slow * 0.7, C["go"] + 0.05, 0.6)                                  # the slow-motion 'breath'
    fx.add(B.whoosh(0.4, up=True, seed=13), C["go"] + 0.85, 0.7)
    fx.add(B.chord_hit([70, 74, 77, 82], dur=0.3, seed=11), C["go"] + 1.2, 1.0)
    fx.add(short(J.crash(seed=12), 0.9), C["go"] + 1.2, 0.8)
    fx.add(J.kick(seed=14), C["go"] + 1.2, 1.0)
    fx.add(B.passby(0.8, seed=20), C["go"] + 1.15, 0.45)

    # ---- every transition: a stab, drums, and a whoosh on wipes
    for i, (t, name, tr) in enumerate(EDIT[1:], 1):
        ch = chord_at(t)
        top = [m + 12 for m in ch[-4:]]
        th = t                                                                # on the cut frame / the frame the wipe covers
        fx.add(B.chord_hit(top, dur=0.16, seed=300 + i, fall=3 if i % 5 == 0 else 0), th, 0.6)
        fx.add(J.kick(seed=i), th, 0.85)
        if tr.startswith("head") or tr == "iris":
            fx.add(B.whoosh(WIPE, seed=i, up=i % 2 == 0, rtl=tr.startswith("head")), t - WIPE / 2 - 0.06, 0.55)   # rides the face across
            fx.add(short(J.crash(seed=i), 0.3), th, 0.3)
        elif tr == "split":
            fx.add(J.snare(seed=i, tight=1.3), th, 0.7)
            fx.add(J.noise_hit(0.15, 800, 9000, seed=i), th, 0.3)
        else:
            fx.add(J.snare(seed=i, tight=1.2), th, 0.55)

    # ---- the announcer: a fanfare in, the crowd swells under him
    for k, key in enumerate(("a0", "a1", "a2", "a3")):
        if key != "a0":
            fanfare(fx, TL.s(key) - 0.02, seed=400 + 10 * k)
    fx.add(B.chord_hit([58, 65, 70, 74, 77, 82], dur=0.6, seed=450, doit=2), TL.e("a1") + 0.02, 0.9)
    fx.add(short(J.crash(seed=451), 0.6), TL.e("a1") + 0.02, 0.6)
    # 'done!' moments get the crowd
    for key in ("d2", "d3"):
        t = TL.e(key) + 0.02                                              # right after "Done."
        fx.add(B.chord_hit([70, 74, 77, 82], dur=0.4, doit=2, seed=int(t)), t, 0.6)
        fx.add(short(J.crash(seed=int(t)), 0.5), t, 0.4)

    # ---- the dashboard: a blip for every gauge
    for k, t in enumerate(C["gauges"]):
        fx.add(B.horn(B.midi(70 + [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17][k]), 0.1, "tpt", 0.5, seed=500 + k), t, 0.28)

    # ---- the dinner grand prix: every hazard is a hit
    for k, t in enumerate(C["hazards"]):
        ch = CHORDS[(k * 3) % 8]
        fx.add(B.chord_hit([m + 12 for m in ch[-3:]], dur=0.16, fall=4 if k in (5, 7) else 0, doit=2 if k == 3 else 0, seed=600 + k), t, 0.5)
        fx.add(J.snare(seed=610 + k, tight=0.9), t, 0.45)
        if k in (0, 4, 6):
            fx.add(B.screech(0.45, seed=620 + k), t + 0.05, 0.22)
    tw = C["hazards"][7]                                                     # the wine: slow motion, then snap
    fx.add(B.riser(0.5, seed=630), tw - 0.5, 0.3)
    fx.add(B.whoosh(1.0, up=False, seed=631), tw, 0.5)
    fx.add(B.chord_hit([70, 74, 77, 82], dur=0.25, seed=632), tw + 1.0, 0.8)
    fx.add(short(J.crash(seed=633), 0.5), tw + 1.0, 0.6)
    fx.add(J.kick(seed=635), tw + 1.0, 0.9)
    fx.add(B.passby(1.0, seed=634), TL.s("t5") - 1.2, 0.25)

    # ---- the loop: a climbing trumpet note at every checkpoint
    for k, t in enumerate(C["loop"]):
        fx.add(B.horn(B.midi(70 + [0, 2, 4, 5, 7, 9, 12][k]), 0.2, "tpt", 0.6, seed=700 + k), t, 0.45)
        fx.add(J.tom([196, 175, 156, 147, 131, 117, 98][k], seed=710 + k), t, 0.4)

    # ---- head to head: engines, the crash in slow motion, then the snap back
    fx.add(B.passby(1.8, seed=800), TL.s("v2") + 0.4, 0.18)
    fx.add(B.engine(2.0, lambda x: 2600 + 1800 * x, seed=801), C["crash"] - 2.0, 0.1)
    fx.add(B.screech(0.9, seed=802), C["crash"] - 0.8, 0.2)
    fx.add(B.smash(0.7, seed=803), C["crash"], 0.5)
    fx.add(short(J.crash(seed=804), 0.5), C["crash"], 0.5)
    fx.add(B.chord_hit([58, 65, 70, 74, 77], dur=0.3, seed=805), C["crash"] + 1.0, 0.9)
    fx.add(B.whoosh(0.4, up=True, seed=806), C["crash"] + 0.65, 0.5)

    # ---- the old joke: ba-dum-tss
    fx.add(B.rimshot(), TL.e("w2") + 0.05, 0.8)

    # ---- the finish: a shout chorus, then one last hit on the end card
    f0 = TL.s("f1") - 1.25
    riff = [(0, [70, 74, 77]), (0.5, [72, 75, 79]), (1.0, [74, 77, 82]), (1.75, [70, 74, 77, 82]), (2.5, [75, 79, 82]),
            (3.0, [74, 77, 81]), (3.5, [72, 76, 79]), (4.0, [70, 74, 77, 82])]
    for k, (beat, notes) in enumerate(riff):
        fx.add(B.chord_hit(notes, dur=0.3 if k < 7 else 0.9, seed=900 + k, doit=3 if k == 7 else 0), f0 + beat * B.BEAT * 1.0, 0.55 if f0 + beat * B.BEAT < TL.s("f1") - 0.1 else 0.14)
    crowd_bus.add(stereo_crowd(4.0, seed=901), f0, 0.8)
    fx.add(B.chord_hit([58, 65, 70, 74, 77, 82], dur=1.4, seed=910, doit=2), C["end_card"], 0.9)
    fx.add(J.crash(seed=911), C["end_card"], 0.7)
    fx.add(J.kick(seed=912), C["end_card"], 1.0)
    b_ = C["end"] - 0.6
    fx.add(B.chord_hit([58, 65, 70, 74, 77, 82], dur=0.25, seed=920), b_, 0.9)
    fx.add(J.kick(seed=921), b_, 1.0)
    fx.add(J.snare(seed=922, tight=1.3), b_, 0.8)

    # ---- voices
    vo = np.zeros(N)
    ann = np.zeros(N)
    for key in TL.order:
        L = TL.lines[key]
        a = L["wav"].astype(np.float64)
        if L["voice"] != "af_heart":
            a = B.pa(a, VSR)
        up = signal.resample_poly(a, SR, VSR)
        i = int(L["start"] * SR)
        j = min(N, i + len(up))
        (ann if L["voice"] != "af_heart" else vo)[i:j] += up[: j - i]
    vo = S._hp(vo, 70)
    speech = np.concatenate([vo[int(TL.s(k) * SR): int(TL.e(k) * SR)] for k in TL.order if TL.lines[k]["voice"] == "af_heart"])
    g_vo = db(-18) / (np.sqrt((speech ** 2).mean()) + 1e-12)
    aspeech = np.concatenate([ann[int(TL.s(k) * SR): int(TL.e(k) * SR)] for k in TL.order if TL.lines[k]["voice"] != "af_heart"])
    g_an = db(-15.5) / (np.sqrt((aspeech ** 2).mean()) + 1e-12)
    vo_st = S.reverb(vo * g_vo, wet=0.05, rt60=0.6)[:, :N]
    an_st = S.reverb(ann * g_an, wet=0.08, rt60=1.4)[:, :N]

    # ---- mix
    bandr = S.reverb(band.x, wet=0.12, rt60=1.2)[:, :N]
    fxr = S.reverb(fx.x, wet=0.04, rt60=0.7)[:, :N]
    from scipy.ndimage import maximum_filter1d
    allv = np.abs(vo) + np.abs(ann)
    raw = np.convolve(allv, np.ones(SR // 20) / (SR // 20), mode="same")
    raw = np.clip(raw / (np.percentile(raw[raw > 1e-5], 80) + 1e-9), 0, 1)
    # instant attack with 0.15 s look-ahead, held through short gaps, smooth release
    env = maximum_filter1d(raw, size=int(0.45 * SR), origin=-int(0.12 * SR))
    env = np.convolve(env, np.ones(SR // 12) / (SR // 12), mode="same")
    duck = 1 - 0.88 * env
    talk = np.zeros(N)
    for key in TL.order:
        talk[int((TL.s(key) - 0.12) * SR): int((TL.e(key) + 0.15) * SR)] = 1.0
    r = int(0.08 * SR)
    swell = 1 + (db(7.0) - 1) * (1 - np.convolve(talk, np.ones(r) / r, mode="same"))
    gate = np.ones(N)
    gate[int(C["crash"] * SR): int((C["crash"] + 1.0) * SR)] = 0.0                  # the slow-motion crash: band cut dead
    gate[int(C["go"] * SR + 0.05 * SR): int((C["go"] + 1.2) * SR)] *= 0.1
    gate = np.convolve(gate, np.ones(int(0.004 * SR)) / int(0.004 * SR), mode="same")
    crowd_env = np.full(N, db(-22))
    for key in ("a0", "a1", "a2", "a3"):
        i0, i1 = int((TL.s(key) - 0.4) * SR), int((TL.e(key) + 0.9) * SR)
        crowd_env[i0:i1] = db(-9)
    crowd_env[: int(TL.e("h1") * SR)] = db(-18)
    crowd_env[int((C["go"] + 1.2) * SR): int((C["go"] + 2.2) * SR)] = db(-2)
    crowd_env[int(TL.e("f1") * SR):] = db(-8)
    crowd_env = np.convolve(crowd_env, np.ones(SR // 3) / (SR // 3), mode="same")

    loud = bandr[:, int(TL.s("t2") * SR): int(TL.e("t2") * SR)]
    g_mu = db(-19) / (np.sqrt((loud ** 2).mean()) + 1e-12)
    def carve(x, depth_mid):
        """Duck the speech band (300 Hz - 4 kHz) hard and the lows/highs gently."""
        low = S._lp(x, 300)
        high = S._hp(x, 4000)
        mid = x - low - high
        return low * (1 - 0.5 * env) + mid * (1 - depth_mid * env) + high * (1 - 0.7 * env)
    def presence(x, gain_db):
        """Give the horns their bite (2-5 kHz) only between lines, where nothing needs to be understood."""
        return x + S._hp(S._lp(x, 5000), 2000) * (db(gain_db) - 1) * (1 - env)
    music = carve(presence(widen(bandr, 0.7), 5.0) * swell * gate, 0.97) * db(-3.5) \
        + carve(presence(widen(fxr, 0.45), 3.0) * (0.7 + 0.3 * swell / db(7.0)), 0.9) * db(4.0)
    mix = music * g_mu + crowd_bus.x * crowd_env * g_mu * 0.5 * duck + vo_st + an_st
    STEMS.update(band=music * g_mu, fx=np.zeros_like(music),
                 crowd=crowd_bus.x * crowd_env * g_mu * 0.5 * duck, vo=vo_st + an_st)
    mix = loudness(mix, -14.0)
    tail = int(0.2 * SR)
    mix[:, -tail:] *= np.linspace(1, 0, tail) ** 2
    return mix, vo


def loudness(x, target):
    import pyloudnorm as pyln
    for _ in range(2):
        lufs = pyln.Meter(SR).integrated_loudness(x.T)
        x = limit(x * db(target - lufs), db(-3.3))
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
    mix, vo = build()
    write(os.path.join(HERE, "build", "audio.wav"), mix)
    print("audio", mix.shape[1] / SR, "s in", round(time.time() - t0, 1), "s")
