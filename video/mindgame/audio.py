"""Soundtrack: synthesized free jazz (drums, fuzz bass, piano clusters, sax), noise hits, and hard silences.

Writes build/audio.wav (48 kHz stereo) with the narration mixed in.
"""
import os
import wave

import numpy as np
from scipy import signal

import jazz as J
import synth as S
from cues import C
from timeline import TL
from voice import SR as VSR

SR = J.SR
HERE = os.path.dirname(os.path.abspath(__file__))
N = int((TL.total + 0.5) * SR)


def db(v):
    return 10 ** (v / 20)


class Bus:
    def __init__(self):
        self.x = np.zeros((2, N))

    def add(self, sig, t, gain=1.0, pan=0.5):
        if sig.ndim == 1:
            sig = np.stack([sig * np.sqrt(1 - pan), sig * np.sqrt(pan)]) * np.sqrt(2)
        i = int(t * SR)
        if i >= N or i < 0:
            return
        j = min(N, i + sig.shape[1])
        self.x[:, i:j] += gain * sig[:, : j - i]


def energy_curve():
    """Drum/bass energy over the whole piece (0 = silent, 1 = everything at once)."""
    pts = [
        (0.0, 0.95), (0.3, 0.45), (C["clock"] - 0.3, 0.3), (TL.s("h2"), 0.25), (C["half"], 0.12), (TL.s("h3") - 0.4, 0.55),
        (C["title"], 0.95), (TL.s("a1") - 0.05, 0.9), (TL.s("a1") + 0.3, 0.4), (TL.s("a4"), 0.2), (TL.s("a5"), 0.4),
        (TL.s("l1"), 0.25), (TL.s("l4"), 0.35), (C["wait_stop"] - 0.02, 0.7), (C["wait_stop"], 0.0), (C["wait"] + 0.6, 0.0),
        (C["wait"] + 0.5, 0.38), (TL.s("g4"), 0.25), (C["water"], 0.45), (TL.s("g6"), 0.7), (TL.e("g6"), 0.8),
        (TL.s("g7"), 0.5), (C["silence"] - 1.5, 0.35), (C["silence"] - 0.01, 0.65), (C["silence"], 0.0),
        (TL.s("c2") - 0.2, 0.0), (TL.s("c2"), 0.14), (TL.s("c3") - 0.35, 0.16), (TL.s("c3") - 0.3, 0.0),
        (TL.s("c4") - 0.1, 0.0), (TL.s("c4"), 0.12), (TL.s("c5"), 0.16), (C["missing"] - 2.2, 0.3), (C["missing"] - 1.05, 0.5),
        (C["missing"] - 1.0, 0.0), (C["missing"] - 0.01, 0.0), (C["missing"], 0.75), (TL.s("m1"), 0.4), (TL.s("m6"), 0.45),
        (TL.e("m6"), 0.6), (C["finale"], 0.85), (TL.s("f1") - 0.5, 1.0), (C["final_silence"] - 0.01, 1.0),
        (C["final_silence"], 0.0), (C["end"], 0.0),
    ]
    xs, ys = zip(*sorted(pts))
    return lambda t: float(np.interp(t, xs, ys))


def dead_stops():
    """Intervals where the whole band is cut dead."""
    return [(C["wait_stop"], C["wait"] + 0.6), (C["silence"], TL.s("c2") - 0.15), (TL.s("c3") - 0.3, TL.s("c4") - 0.1),
            (C["missing"] - 1.0, C["missing"] - 0.01), (C["final_silence"], C["end_card"] - 0.01)]


def build():
    E = energy_curve()
    band, fx = Bus(), Bus()
    T = TL.total

    drums = J.free_drums(T, E, seed=7)
    bass = J.free_bass(T, lambda t: E(t) * 0.9, seed=11)
    band.add(np.stack([drums * 0.9, drums]), 0.0, 1.0)
    band.add(bass, 0.0, 0.55)

    # ---- the hook: impact, the clock, the scratch, the title hit
    fx.add(J.noise_hit(0.5, 200, 9000, seed=1), 0.0, 0.8)
    fx.add(J.kick(), 0.0, 1.0)
    fx.add(J.crash(seed=2), 0.02, 0.6)
    band.add(J.cluster_stab(64, 6, seed=3), 0.02, 0.35)
    for k in range(8):
        fx.add(J.tick(), C["clock"] - 0.1 + 0.5 * k, 0.25)
    fx.add(J.scratch(0.45, seed=4), C["half"] - 0.05, 0.5)
    fx.add(J.crash(seed=5), C["title"], 0.45)
    fx.add(J.kick(), C["title"], 1.0)
    band.add(J.cluster_stab(52, 8, 2.4, seed=6), C["title"], 0.3)
    band.add(J.sax(233, 1.1, squeal=1.0, seed=7), C["title"] + 0.2, 0.18)

    # ---- the ladder of levels: a stamp on every answer
    for i, t in enumerate(C["stamps"]):
        fx.add(J.snare(seed=20 + i), t, 0.8)
        fx.add(J.kick(seed=30 + i), t, 0.8)
        fx.add(J.noise_hit(0.2, 800, 8000, seed=40 + i), t, 0.35)

    # ---- "But wait." hard stop, then the notification and the water
    fx.add(J.scratch(0.35, seed=50), C["wait_stop"] - 0.35, 0.45)
    fx.add(J.ping(), C["notif"], 0.45)
    fx.add(J.riser(TL.s("g6") - C["water"] + 0.2, seed=51), C["water"], 0.45)
    for i, t in enumerate(C["montage"]):
        fx.add(J.crash(seed=60 + i) if i % 3 == 0 else J.snare(seed=60 + i), t - 0.04, 0.2)
        fx.add(J.kick(seed=70 + i), t - 0.04, 0.45)
    band.add(J.sax(311, 1.6, squeal=1.3, seed=8), TL.s("g6") + 0.5, 0.16)

    # ---- consciousness: silence, one piano note at a time, the robot, the octopus
    for k, key in enumerate(("c1", "c2", "c3", "c4", "c5")):
        band.add(J.piano([57 + (k * 5) % 12], 2.5, seed=80 + k), TL.s(key) - 0.05, 0.22)
    fx.add(J.bubbles(1.4, seed=90), C["octopus"], 0.25)

    # ---- what's missing: restart, and an accent for each item
    fx.add(J.kick(), C["missing"], 1.0)
    fx.add(J.crash(seed=100), C["missing"], 0.5)
    for i, t in enumerate(C["items"]):
        fx.add(J.tom([196, 150, 118, 92, 150, 196][i], seed=110 + i), t - 0.08, 0.7)
        fx.add(J.bass_note(55 * 2 ** ((i * 3 % 12) / 12), 0.35, seed=120 + i), t - 0.08, 0.4)

    # ---- finale: everything at once, building for seven seconds, then nothing
    f0, f9 = C["finale"], C["final_silence"]
    n = int((f9 - f0) / 0.55)
    for k in range(n):
        band.add(J.cluster_stab(40 + (7 * k) % 24, 7, 1.0, seed=130 + k), f0 + 0.55 * k, 0.22 + 0.2 * k / n)
    for k, t in enumerate(np.arange(f0, f9 - 0.3, 1.1)):
        fx.add(J.crash(seed=150 + k), t, 0.35)
        fx.add(J.kick(seed=160 + k), t, 0.9)
    band.add(J.sax(262, 1.8, squeal=1.6, seed=9), f0 + 0.1, 0.2)
    band.add(J.sax(349, 1.6, squeal=2.0, seed=10), f0 + 2.6, 0.2)
    fx.add(J.noise_hit(0.6, 200, 10000, seed=140), f0, 0.6)
    fx.add(J.riser(f9 - f0, seed=143), f0, 0.4)
    t, gap = f9 - 1.6, 0.16
    while t < f9 - 0.04:                                    # snare roll that tightens into the cut
        fx.add(J.snare(seed=int(t * 100), tight=1.3), t, 0.45)
        t += gap
        gap = max(0.045, gap * 0.85)
    fx.add(J.crash(seed=141), C["end_card"], 0.6)
    fx.add(J.kick(), C["end_card"], 1.0)
    band.add(J.cluster_stab(45, 9, 1.2, seed=142), C["end_card"], 0.3)
    # the button: one hard hit to end on
    b = C["end"] - 0.55
    fx.add(J.kick(seed=144), b, 1.0)
    fx.add(J.snare(seed=145, tight=1.4), b, 0.8)
    fx.add(J.noise_hit(0.3, 300, 9000, seed=146), b, 0.5)
    band.add(J.cluster_stab(52, 9, 0.5, seed=147), b, 0.35)

    # ---- mix
    bandr = S.reverb(band.x, wet=0.14, rt60=1.1)[:, :N]
    fxr = S.reverb(fx.x, wet=0.12, rt60=0.9)[:, :N]

    vo = np.zeros(N)
    for key in TL.order:
        L = TL.lines[key]
        a = L["wav"].astype(np.float64)
        if L["voice"] != "af_heart":
            tt = np.arange(len(a)) / VSR
            a = a * (0.55 + 0.45 * np.sin(2 * np.pi * 92 * tt))           # ring-modulated machine voice
            d = int(0.011 * VSR)
            a = a + 0.5 * np.concatenate([np.zeros(d), a[:-d]])
        up = signal.resample_poly(a, SR, VSR)
        i = int(L["start"] * SR)
        j = min(N, i + len(up))
        vo[i:j] += up[: j - i]
    vo = S._hp(vo, 70)
    vo[int(C["silence"] * SR): int((C["missing"] - 0.3) * SR)] *= db(-2)
    vo[int((TL.s("g6") - 0.05) * SR): int((TL.e("g6") + 0.05) * SR)] *= db(3)       # the spoken list rides over the montage
    vo_st = S.reverb(vo, wet=0.06, rt60=0.7)[:, :N]

    env = np.convolve(np.abs(vo), np.ones(SR // 8) / (SR // 8), mode="same")
    env = np.clip(env / (np.percentile(env[env > 1e-4], 90) + 1e-9), 0, 1)
    env = np.convolve(env, np.ones(SR // 5) / (SR // 5), mode="same")
    duck = 1 - 0.8 * env

    # the band swells in the gaps between lines and into each dead stop
    talk = np.zeros(N)
    for key in TL.order:
        talk[int((TL.s(key) - 0.12) * SR): int((TL.e(key) + 0.15) * SR)] = 1.0
    ramp_ = int(0.08 * SR)
    swell = 1 + (db(3.5) - 1) * (1 - np.convolve(talk, np.ones(ramp_) / ramp_, mode="same"))
    tsm = np.convolve(talk, np.ones(ramp_) / ramp_, mode="same")
    for a_, b_ in dead_stops()[:4]:
        i0, i1 = int((a_ - 2.0) * SR), int(a_ * SR)
        k = np.linspace(0, 1, i1 - i0)
        swell[i0:i1] *= 1 + (db(4) - 1) * k * (1 - tsm[i0:i1]) + (db(1.5) - 1) * k * tsm[i0:i1]
    swell[int(C["finale"] * SR): int((TL.s("f1") - 0.1) * SR)] *= db(1.5)
    swell[int((TL.s("g6") - 0.2) * SR): int((TL.e("g6") + 0.3) * SR)] *= db(1.5)

    gate = np.ones(N)
    for a_, b_ in dead_stops():
        gate[int(a_ * SR): int(b_ * SR)] = 0.0
    gate[int((TL.s("f1") - 0.1) * SR): int(C["final_silence"] * SR)] *= db(-6)
    gate[: int(TL.e("h2") * SR)] *= db(-4)                                   # the hook: voice first
    gate[int((TL.s("h3") - 0.05) * SR): int(TL.e("h3") * SR)] *= db(-5)
    gate[int((TL.s("l4") - 0.05) * SR): int(TL.e("l4") * SR)] *= db(-2)
    gate[int(C["silence"] * SR): int(C["missing"] * SR)] *= db(-5)            # the consciousness band stays sparse and low
    gate = np.convolve(gate, np.ones(int(0.004 * SR)) / int(0.004 * SR), mode="same")
    keep = np.zeros(N)
    keep[int(C["silence"] * SR): int((C["missing"] - 0.01) * SR)] = 1.0

    speech = np.concatenate([vo[int(TL.s(k) * SR): int(TL.e(k) * SR)] for k in TL.order])
    g_vo = db(-18) / (np.sqrt((speech ** 2).mean()) + 1e-12)
    loud = bandr[:, int(C["finale"] * SR): int(TL.s("f1") * SR)] + fxr[:, int(C["finale"] * SR): int(TL.s("f1") * SR)]
    g_mu = db(-14) / (np.sqrt((loud ** 2).mean()) + 1e-12)

    pianos = Bus()
    for k, key in enumerate(("c1", "c2", "c3", "c4", "c5")):
        pianos.add(J.piano([57 + (k * 5) % 12], 2.5, seed=80 + k), TL.s(key) - 0.05, 0.22)
    pianos.add(J.bubbles(1.4, seed=90), C["octopus"], 0.25)
    pianos_r = S.reverb(pianos.x, wet=0.3, rt60=2.0)[:, :N]

    mix = (bandr + fxr) * duck * swell * g_mu * gate + pianos_r * keep * g_mu * 1.4 + vo_st * g_vo
    mix = loudness(mix, -14.0)
    tail = int(0.25 * SR)
    mix[:, -tail:] *= np.linspace(1, 0, tail) ** 2
    return mix, vo


def loudness(x, target):
    """Static gain to the target integrated loudness (no dynamic compression), then a peak limiter."""
    import pyloudnorm as pyln
    for _ in range(2):
        lufs = pyln.Meter(SR).integrated_loudness(x.T)
        x = limit(x * db(target - lufs), db(-2.6))
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
