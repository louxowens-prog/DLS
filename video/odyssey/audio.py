"""Soundtrack: synthesized Zarathustra-style fanfares, Ligeti-style clusters, breathing, silence.

Writes build/audio.wav (48 kHz stereo) with the narration mixed in and loudness left for ffmpeg to
normalise. Music and effects are ducked under the voice; some passages are true digital silence.
"""
import os
import wave

import numpy as np
from scipy import signal

import synth as S
from cues import C
from timeline import TL
from voice import SR as VSR

SR = S.SR
HERE = os.path.dirname(os.path.abspath(__file__))
N = int((TL.total + 0.5) * SR)


class Bus:
    def __init__(self):
        self.x = np.zeros((2, N))

    def add(self, sig, t, gain=1.0, pan=0.5):
        if sig.ndim == 1:
            sig = np.stack([sig * np.sqrt(1 - pan), sig * np.sqrt(pan)]) * np.sqrt(2)
        i = int(t * SR)
        if i >= N:
            return
        j = min(N, i + sig.shape[1])
        self.x[:, i:j] += gain * sig[:, : j - i]


def db(v):
    return 10 ** (v / 20)


def fanfare(bus, t0, scale=1.0, full=True):
    """Compressed Also-sprach-Zarathustra gesture (Strauss, 1896, public domain), re-synthesised:
    organ pedal already sounding; trumpets C-G-C; C major -> C minor; timpani; F-G -> tutti C major."""
    g = scale
    bus.add(S.brass(S.midi(60), 0.75, players=4, seed=1), t0, 0.55 * g)
    bus.add(S.brass(S.midi(67), 0.75, players=4, seed=2), t0 + 0.62, 0.6 * g)
    bus.add(S.brass(S.midi(72), 1.1, players=4, seed=3, rel=0.35), t0 + 1.24, 0.7 * g)
    # chord: major third then minor third, horns underneath
    for m, s in ((48, 4), (55, 5), (60, 6), (64 + 12, 7)):
        bus.add(S.brass(S.midi(m), 0.5, players=3, horn=m < 70, seed=s), t0 + 2.05, 0.45 * g)
    for m, s in ((48, 8), (55, 9), (60, 10), (63 + 12, 11)):
        bus.add(S.brass(S.midi(m), 0.62, players=3, horn=m < 70, seed=s, rel=0.3), t0 + 2.5, 0.5 * g)
    bus.add(S.organ([36, 43, 48, 55, 60, 63, 67], 1.1, a=0.08, r=0.4), t0 + 2.05, 0.18 * g)
    # timpani: alternating C and G, crescendo
    for i in range(8):
        bus.add(S.timpani(S.midi(36 if i % 2 == 0 else 43), dur=2.2, seed=20 + i), t0 + 3.02 + i * 0.115,
                (0.35 + 0.08 * i) * g)
    if not full:
        return
    bus.add(S.brass(S.midi(65), 0.24, players=4, seed=30), t0 + 3.95, 0.7 * g)
    bus.add(S.brass(S.midi(67), 0.24, players=4, seed=31), t0 + 4.15, 0.75 * g)
    tut = t0 + 4.35
    for m, s in ((36, 40), (48, 41), (55, 42), (60, 43), (64, 44), (67, 45), (72, 46), (76, 47), (79, 48)):
        bus.add(S.brass(S.midi(m), 2.3, players=3, horn=m < 62, seed=s, rel=1.2), tut, (0.42 if m >= 60 else 0.5) * g)
    bus.add(S.organ([24, 36, 43, 48, 55, 60, 64, 67, 72], 3.4, a=0.05, r=2.0), tut, 0.42 * g)
    strings = S.cluster(3.0, 60, 60.01, voices=10, strings=True, seed=50, entry=0.0, drift=3, vib=8, air=0)
    maj = sum(S.cluster(3.0, m, m + 0.02, voices=6, strings=True, seed=51 + m, entry=0.0, drift=3, vib=8, air=0)
              for m in (48, 55, 64, 67, 72, 76))
    k = min(strings.shape[1], maj.shape[1])
    bus.add((strings[:, :k] + maj[:, :k]) * S.adsr(k, 0.03, 0.3, 0.8, 1.6)[None], tut, 0.22 * g)
    for i in range(6):
        bus.add(S.timpani(S.midi(36), dur=2.0, seed=60 + i), tut + i * 0.07, 0.3 * g * (1 - i / 7))


def pedal(bus, t0, dur, gain=0.5):
    """Organ pedal C + bass-drum rumble that opens the fanfare."""
    t = S.t_axis(dur)
    sw = np.clip(t / (dur * 0.85), 0, 1) ** 1.6
    x = S.organ([24, 36], dur, a=0.01, r=0.4) * (0.35 + 0.65 * sw)
    rum = S._lp(np.random.default_rng(9).normal(0, 1, len(t)), 90) * (0.4 + 0.6 * sw)
    rum /= np.max(np.abs(rum)) + 1e-9
    bus.add(x * 0.8 + rum * 0.6, t0, gain)


def build():
    music, sfx = Bus(), Bus()
    T = TL.total

    # ---------------------------------------------------------------- opening
    pedal(music, 0.0, C["fanfare"] + 0.6, 0.55)
    fanfare(music, C["fanfare"])

    # ---------------------------------------------------------------- I. the dawn of mind
    wstart = C["int1"] + 0.3
    sfx.add(S.wind(C["silence"] - wstart + 0.1, seed=11), wstart, db(-20))
    for i, w in enumerate(("model", "learn", "infer", "adapt", "plan")):
        sfx.add(S.beep(2200 + 180 * i, 0.07), TL.word("useful", w), db(-24))
    for k in range(10):
        sfx.add(S.tick(seed=k), TL.s("defs") + 0.25 * k, db(-28))
    # the monolith: a Requiem-like choir cluster that swells, then is cut off dead
    req = S.cluster(C["silence"] - C["monolith"] + 0.4, 62, 86, voices=40, vowels=("ah", "eh", "ee"),
                    seed=12, entry=0.35, drift=45, vib=18, air=0.25)
    req *= np.clip(np.linspace(0, 1, req.shape[1]), 0.08, 1)[None] ** 1.3
    low = S.cluster(req.shape[1] / SR, 40, 58, voices=18, vowels=("oo", "ah"), seed=13, entry=0.2, drift=30, vib=10, air=0.1)
    k = min(req.shape[1], low.shape[1])
    music.add(req[:, :k] * 0.8 + low[:, :k] * 0.5, C["monolith"], db(-9))
    # the tool moment: the fanfare motif returns while the child solves it
    sfx.add(S.wind(C["cut"] - C["child"], seed=14), C["child"], db(-22))
    fanfare(music, C["figure"] - 0.2, scale=0.75, full=False)
    tut = C["bone"] - 0.05
    for m, s in ((36, 70), (48, 71), (55, 72), (60, 73), (64, 74), (67, 75), (72, 76)):
        music.add(S.brass(S.midi(m), C["cut"] - tut + 0.3, players=3, horn=m < 62, seed=s, rel=0.05), tut, 0.36)
    music.add(S.organ([24, 36, 48, 55, 60, 64, 67], C["cut"] - tut + 0.3, a=0.05, r=0.02), tut, 0.3)

    # ---------------------------------------------------------------- II. built, not born
    sfx.add(S.hum(TL.e("light") - TL.s("light") + 0.4), TL.s("light") - 0.1, db(-30))
    b = C["heart"]
    while b < TL.e("light") + 0.4:
        sfx.add(S.beep(1000, 0.09), b + 0.35, db(-22))
        b += 0.78
    for k in range(6):
        sfx.add(S.tick(seed=30 + k), TL.s("chess") + 0.35 + 0.55 * k, db(-20))
    for k in range(8):
        sfx.add(S.tick(seed=40 + k), C["alphago"] + 0.1 + 0.18 * k, db(-22))
    lux = S.cluster(TL.e("question") - TL.s("question") + 2.2, 67, 84, voices=26, vowels=("oo", "ah"),
                    seed=15, entry=0.3, drift=25, vib=6, air=0.12)
    music.add(lux, TL.s("question") - 0.2, db(-15))

    # ---------------------------------------------------------------- III. inside the machine
    for k in range(18):
        sfx.add(S.beep(1800 + 300 * (k % 5), 0.035), TL.s("myth") + 0.2 * k, db(-30))
    br0 = TL.s("params") - 0.6
    br1 = TL.word("capitals", "Yet")
    sfx.add(S.breath(br1 - br0, rate=3.6), br0, db(-14))
    sfx.add(S.hiss(br1 - br0), br0, db(-30))
    sfx.add(S.hum(br1 - br0), br0, db(-26))
    for w in ("Paris", "France", "Tokyo", "Japan"):
        sfx.add(S.beep(2600, 0.05), TL.word("capitals", w), db(-24))
    stars = S.cluster(TL.e("map") - TL.s("map") + 1.8, 76, 96, voices=24, vowels=("ee", "oo"),
                      seed=16, entry=0.25, drift=20, vib=5, air=0.08)
    music.add(stars, TL.s("map") - 0.2, db(-17))
    sfx.add(S.hum(TL.e("wrong") - TL.s("wrong") + 0.3), TL.s("wrong") - 0.1, db(-27))
    for k in range(3):
        sfx.add(S.beep(880, 0.18), TL.s("wrong") + 0.6 + k * 0.3, db(-24))

    # ---------------------------------------------------------------- IV. the prediction mission
    for k in range(7):
        sfx.add(S.tick(seed=50 + k), TL.s("token") + 1.9 + 0.2 * k, db(-22))
    sfx.add(S.beep(220, 0.35), TL.word("ocean", "Wrong"), db(-20))
    for k in range(10):
        sfx.add(S.tick(seed=60 + k), TL.s("nudge") + 0.1 + 0.16 * k, db(-24))
    sfx.add(S.beep(1568, 0.5) + S.beep(2093, 0.5), C["sun"], db(-22))
    # the Star Gate: an Atmospheres-like orchestral cluster at full stretch, then nothing
    sg = C["stargate_end"] - C["stargate"]
    atm = S.cluster(sg, 55, 100, voices=48, strings=True, seed=17, entry=0.25, drift=60, vib=22, air=0.2)
    atm *= np.clip(np.arange(atm.shape[1]) / SR / 1.2, 0, 1)[None]
    music.add(atm, C["stargate"], db(-10))
    earthc = S.cluster(TL.e("surprise") - TL.s("surprise") + 0.8, 60, 79, voices=22, vowels=("oo",),
                       seed=18, entry=0.3, drift=20, vib=5, air=0.08)
    music.add(earthc, TL.s("surprise") - 0.3, db(-17))
    sfx.add(S.shatter(), C["shatter"], db(-6))

    # ---------------------------------------------------------------- V. beyond the next word
    for k in range(10):
        sfx.add(S.tick(seed=70 + k), TL.s("just") + 0.15 + 0.14 * k, db(-24))
    for k in range(12):
        sfx.add(S.beep(3000 + 500 * (k % 3), 0.03), TL.s("shakes") + 0.3 * k + 0.1, db(-32))
    for tt, f in ((C["dallas"], 1760), (C["texas"], 1976), (C["austin"], 2349)):
        sfx.add(S.beep(f, 0.12), tt, db(-20))
    sfx.add(S.beep(2637, 0.1), TL.word("rhyme", "last"), db(-22))
    req2 = S.cluster(TL.e("jagged") - TL.s("philo") + 0.6, 64, 88, voices=34, vowels=("ah", "eh"),
                     seed=19, entry=0.4, drift=40, vib=14, air=0.2)
    req2 *= np.clip(np.linspace(0, 1, req2.shape[1]), 0.1, 1)[None]
    music.add(req2, TL.s("philo") - 0.3, db(-13))

    # ---------------------------------------------------------------- the close
    pedal(music, C["close"], C["fanfare2"] - C["close"] + 0.6, 0.5)
    fanfare(music, C["fanfare2"])

    # ---------------------------------------------------------------- mix
    mus = S.reverb(music.x, wet=0.32, rt60=2.8)[:, :N]
    fx = S.reverb(sfx.x, wet=0.18, rt60=1.2)[:, :N]

    vo = np.zeros(N)
    for key in TL.order:
        L = TL.lines[key]
        a = L["wav"].astype(np.float64)
        up = signal.resample_poly(a, SR, VSR)
        i = int(L["start"] * SR)
        j = min(N, i + len(up))
        vo[i:j] += up[: j - i]
    vo = S._hp(vo, 70)
    vo /= np.max(np.abs(vo)) + 1e-9
    # a touch of room on the voice so it sits inside the picture, not on top of it
    vo_st = S.reverb(vo, wet=0.08, rt60=0.9)[:, :N]

    env = np.convolve(np.abs(vo), np.ones(SR // 8) / (SR // 8), mode="same")
    env = np.clip(env / (np.percentile(env[env > 1e-4], 90) + 1e-9), 0, 1)
    env = np.convolve(env, np.ones(SR // 5) / (SR // 5), mode="same")
    duck_m = 1 - 0.62 * env
    duck_f = 1 - 0.35 * env

    # true silences: the choir cut, the space after the match cut, the beat before the shatter
    gate = np.ones(N)
    for a, b in ((C["silence"], C["child"] - 0.15), (C["cut"], C["int2"] + 0.2),
                 (TL.e("glass") + 0.05, C["shatter"] - 0.01)):
        gate[int(a * SR): int(b * SR)] = 0.0
    fade = int(0.004 * SR)
    gate = np.convolve(gate, np.ones(fade) / fade, mode="same")

    # levels: speech sits at a steady -19 dBFS RMS; the fanfare tutti peaks around -14 dBFS RMS
    speech = np.concatenate([vo[int(TL.s(k) * SR): int(TL.e(k) * SR)] for k in TL.order])
    g_vo = db(-17) / (np.sqrt((speech ** 2).mean()) + 1e-12)
    tut = mus[:, int(C["title"] * SR): int((C["title"] + 1.5) * SR)]
    g_mu = db(-13.0) / (np.sqrt((tut ** 2).mean()) + 1e-12)
    mix = (mus * duck_m * g_mu + fx * duck_f * g_mu) * gate + vo_st * g_vo
    mix = limit(mix, db(-1.2))
    # end: let the final chord ring out, then fade
    tail = int(1.2 * SR)
    mix[:, -tail:] *= np.linspace(1, 0, tail) ** 2
    return mix, vo


def limit(x, ceil, look=0.005, rel=0.12):
    """Look-ahead peak limiter (stereo-linked)."""
    pk = np.max(np.abs(x), axis=0)
    need = np.minimum(1.0, ceil / (pk + 1e-12))
    la = int(look * SR)
    # hold the minimum over the look-ahead window, then release smoothly
    from scipy.ndimage import minimum_filter1d
    g = minimum_filter1d(need, size=2 * la + 1)
    a = np.exp(-1 / (rel * SR))
    out = np.empty_like(g)
    cur = 1.0
    for i in range(0, len(g), 64):          # block-wise release keeps this fast
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
