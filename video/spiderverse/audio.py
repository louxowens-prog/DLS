"""Soundtrack: an original boom-bap / hip-hop score under the voices, arranged to the story, plus the comic
sound design (a hit on every sound word and transition, glitch zaps on the jumps between dimensions).

Voices: the narrator clean; the AI ring-modulated like a cartoon robot; the noir skeptic through an old
radio band with crackle. The music is carved out of the speech band whenever anyone talks, and the whole
thing is set to -14 LUFS with a static gain (no compressor pumping), true peak kept under -1.5 dBTP.
Writes build/audio.wav (48 kHz stereo).
"""
import os
import wave

import numpy as np
from scipy import signal

import hiphop as H
from cues import C
from edit import EDIT
from script import ANIME, BOT, NAR, NOIR
from timeline import TL
from voice import SR as VSR

SR = H.SR
HERE = os.path.dirname(os.path.abspath(__file__))
N = int((TL.total + 0.6) * SR)
BEAT = H.BEAT
STEP = BEAT / 4
BAR = BEAT * 4
S, E, W = TL.s, TL.e, TL.word

# F minor: Fm9 | Dbmaj9 | Bbm7 | C7b9   (808 roots kept above 55 Hz so phones still hear them)
CHORDS = [(56, 60, 63, 67), (53, 56, 60, 63), (56, 61, 65, 68), (52, 58, 61, 64)]
ROOTS = [41, 37, 34, 36]
# the summary lifts: Db | Eb | Fm | Fm(add9)
CHORDS2 = [(53, 56, 60, 65), (55, 58, 63, 67), (56, 60, 63, 68), (56, 60, 63, 67)]
ROOTS2 = [37, 39, 41, 41]


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


def section(t):
    """The arrangement: which groove plays at time t."""
    if t < C["scratch1"]:
        return "full"
    if t < S("j2") - 0.1:
        return "stop"
    if t < EDIT[6][0]:                       # until the noir glitch
        return "half"
    if t < EDIT[7][0]:
        return "noir"
    if t < EDIT[8][0]:
        return "full"
    if t < EDIT[13][0]:                      # until the question
        return "full"
    if t < C["brain"]:
        return "breakdown"
    if t < C["scratch2"]:
        return "full"
    if t < S("f2") - 0.25:
        return "stop"
    if t < C["end_card"] + 0.05:
        return "lift"
    return "stop"


def beat_grid(bus, bass, keys):
    rng = np.random.default_rng(7)
    nb = int(TL.total / STEP) + 1
    for s in range(nb):
        t = s * STEP
        sec = section(t)
        if sec == "stop":
            continue
        bar = int(t / BAR)
        st = s % 16
        chords, roots = (CHORDS2, ROOTS2) if sec == "lift" else (CHORDS, ROOTS)
        ch, root = chords[bar % 4], roots[bar % 4]
        swing = STEP * 0.14 if st % 2 else 0.0
        tt = t + swing
        half = sec in ("half", "breakdown")
        # drums
        kicks = (0, 7, 10) if not half else (0,)
        if sec == "breakdown":
            kicks = (0,) if bar % 2 == 0 else ()
        if st in kicks:
            bus.add(H.kick(1.0 if st == 0 else 0.8, seed=s), tt, 0.9)
        snares = (4, 12) if not half else (8,)
        if sec == "breakdown":
            snares = ()
        if st in snares:
            bus.add(H.snare(0.9, seed=s), tt, 0.62, pan=0.52)
        if sec != "breakdown":
            if st % 2 == 0 or (sec == "full" and C["speed"] - 0.5 < t < C["scratch1"]):
                acc = 1.0 if st % 4 == 2 else 0.7
                bus.add(H.hat(acc * rng.uniform(0.8, 1.0), seed=s, open_=(st == 14 and bar % 2 == 1)), tt, 0.35, pan=0.62)
        # 808 on the kicks
        if st in kicks and sec != "breakdown":
            dur = BEAT * (1.6 if st == 0 else 0.7)
            glide = -0.12 if (st == 10 and bar % 4 == 3) else 0.0
            bass.add(H.bass808(H.midi(root + (12 if st == 7 else 0)), dur, 1.0, glide=glide), tt, 0.55)
        # electric piano: a chord on 1, a lighter re-hit on the 'and' of 3
        if st == 0:
            keys.add(H.epiano(ch, BEAT * 3.2, 1.0, seed=bar, bright=1.1 if sec == "lift" else 0.9), tt, 0.33)
        if st == 10 and sec in ("full", "lift"):
            keys.add(H.epiano(ch[1:], BEAT * 1.2, 0.8, seed=bar + 99), tt, 0.2)


def sfx_track(fx, music_bus):
    E_ = EDIT
    # --- frame one: the band hits and a scratch
    fx.add(H.hit((65, 68, 72, 75), 1.0, seed=1, big=True), 0.0, 0.85)
    ahh = H.vox_ahh()
    fx.add(H.baby_scratch(ahh, strokes=3), 0.05, 0.55, pan=0.4)
    # --- transitions
    for i, (t, name, tr) in enumerate(E_[1:], 1):
        if tr == "glitch":
            fx.add(H.zap(1.0, seed=i), t - 0.18, 0.6, pan=0.35 + 0.3 * (i % 2))
        elif tr == "slide":
            fx.add(H.paper(1.0, seed=i), t - 0.05, 0.6, pan=0.7)
            fx.add(H.hit((65, 68, 72), 0.8, seed=i + 40), t + 0.14, 0.45)
        elif tr == "impact":
            fx.add(H.hit((63, 67, 70, 74), 1.0, seed=i + 50, big=True), t, 0.7)
        else:
            fx.add(H.hit((65, 68, 72), 0.9, seed=i + 60), t, 0.55)
    # --- the hook
    fx.add(H.hit((68, 72, 75, 80), 1.0, seed=3, big=True), C["gold"], 0.85)
    fx.add(H.chime([80, 84, 87, 92], 1.0), C["gold"] + 0.05, 0.5)
    for k in range(7):                                                   # the clock ticks
        fx.add(H.tick(1.0), S("h2") - 0.1 + k * 0.5, 0.45, pan=0.6)
    fx.add(H.buzzer(1.0), C["thirteen"] + 0.55, 0.55)
    fx.add(H.rattle(1.0, seed=2), C["shake"], 0.7, pan=0.62)
    fx.add(H.rattle(1.0, seed=3), C["shake"] + 0.17 + 0.3, 0.6, pan=0.55)
    # --- the road: a spray and a rising note for every station
    for i, ts in enumerate(C["stations"][:7]):
        fx.add(H.spray(0.45, 1.0, seed=i), ts - 0.05, 0.55, pan=0.7)
        fx.add(H.stab((65 + i * 2, 72 + i * 2), 0.14, 1.0, seed=i), ts, 0.5)
    for ts in C["stations"][7:]:
        fx.add(H.chime([84, 89, 91], 1.0), ts, 0.45)
    fx.add(H.whoosh(0.35, up=False, seed=4), S("r4") - 0.3, 0.6)
    fx.add(H.thwip(1.0), C["pin"] - 0.12, 0.8, pan=0.62)
    fx.add(H.hit((68, 72, 75, 80), 1.0, seed=5, big=True), C["pin"], 0.8)
    fx.add(H.tingle(1.0), C["pin"] + 0.05, 0.7)
    fx.add(H.whoosh(0.5, up=False, seed=6), W("r5", "Way") - 0.35, 0.6, pan=0.3)
    # --- speed
    fx.add(H.whoosh(0.9, up=True, seed=7), C["speed"] - 0.5, 0.7, pan=0.2)
    fx.add(H.hit((65, 68, 72), 1.0, seed=8), C["speed"], 0.6)
    fx.add(H.hit((65, 69, 72, 77), 1.0, seed=9), C["doubled"], 0.6)
    fx.add(H.hit((63, 67, 70), 0.9, seed=10), C["twelve"] - 0.2, 0.5)
    fx.add(H.riser(0.7, 1.0, seed=11), C["sixty"] - 0.75, 0.45)
    fx.add(H.hit((68, 72, 75, 80), 1.0, seed=12, big=True), C["sixty"] - 0.05, 0.75)
    # --- the record scratch: a backspin out of the beat, then the clock
    fx.add(H.scratch(ahh, [(0.09, 0.3, 0.05, 1.0), (0.07, 0.05, 0.25, 1.0), (0.1, 0.25, 0.0, 1.0)], 0.3), C["scratch1"] + 0.02, 0.7)
    for k in range(4):
        fx.add(H.tick(1.0), C["scratch1"] + 0.45 + k * 0.5, 0.55, pan=0.6)
    fx.add(H.hit((65, 68, 72), 0.9, seed=13), C["half"] - 0.2, 0.5)
    fx.add(H.hit((70, 74, 77), 0.9, seed=14), C["ninety"] - 0.2, 0.5)
    fx.add(H.whoosh(0.5, up=True, seed=15), S("j3") - 0.6, 0.55)
    fx.add(H.hit((68, 72, 75, 80), 1.0, seed=16, big=True), C["jagged"] - 0.1, 0.7)
    fx.add(H.chime([77, 81, 84, 89], 1.0), W("j3", "genius") - 0.05, 0.45)
    fx.add(H.buzzer(0.8, 0.3), W("j3", "baffled") - 0.05, 0.35)
    # --- the multiverse
    fx.add(H.chime([84, 88, 91, 96, 100], 1.0, step=0.05), S("d2") - 0.1, 0.45, pan=0.6)
    fx.add(H.tom(70, 1.0, 0.9), S("d2") + 0.05, 0.8)
    fx.add(H.hit((68, 72, 75, 80), 1.0, seed=17, big=True), S("d2") + 0.05, 0.6)
    fx.add(H.hit((65, 68, 72, 77), 1.0, seed=18, big=True), C["neither"], 0.75)
    fx.add(H.tingle(1.0), C["neither"] + 0.05, 0.7)
    fx.add(H.stamp(1.0), W("d4", "autocomplete") - 0.1, 0.7, pan=0.35)
    fx.add(H.stamp(1.0), W("d4", "fully") - 0.1, 0.7, pan=0.65)
    fx.add(H.whoosh(0.4, up=False, seed=19), C["new"] - 0.4, 0.55, pan=0.7)
    fx.add(H.hit((67, 70, 74, 79), 1.0, seed=20), C["new"] + 0.1, 0.6)
    # --- if AGI arrives
    fx.add(H.whoosh(0.5, up=True, seed=21), W("a1", "gets") - 0.1, 0.6)
    fx.add(H.chime([72, 76, 79, 84, 88], 1.0, step=0.06), W("a1", "top") - 0.1, 0.5)
    fx.add(H.stamp(1.0), C["agi"] - 0.25, 0.7)
    for k in range(5):                                                   # days and nights flying by
        fx.add(H.whoosh(0.3, up=k % 2 == 0, seed=30 + k), S("a2") + k * 0.42, 0.25, pan=0.3 + 0.1 * k)
    fx.add(H.chime([79, 84, 88], 1.0), S("a3") - 0.1, 0.4)
    for k, tt in enumerate([W("a4", "Thousands") + 0.25, C["copies"], W("a4", "work"), W("a4", "once")]):
        fx.add(H.stab((72 + 3 * k, 79 + 3 * k), 0.1, 1.0, seed=40 + k), tt, 0.5, pan=0.4 + 0.07 * k)
    fx.add(H.chime([76, 79, 83, 88, 91], 1.0, step=0.05), C["share"], 0.45)
    fx.add(H.riser(0.8, 1.0, seed=22), C["scale"] - 0.5, 0.4)
    fx.add(H.hit((68, 72, 75, 80), 1.0, seed=23), C["scale"] + 0.2, 0.6)
    for k in range(4):
        fx.add(H.tick(1.0), S("a5") + 0.3 * k, 0.5, pan=0.3 + 0.13 * k)
    fx.add(H.whoosh(0.4, up=True, seed=24), W("a5", "Google's") - 0.4, 0.5)
    fx.add(H.hit((70, 74, 77, 82), 1.0, seed=25, big=True), W("a5", "sped") - 0.05, 0.75)
    # --- the question
    fx.add(H.spray(0.6, 1.0, seed=26), W("a7", "can") - 0.1, 0.45, pan=0.7)
    fx.add(H.spray(0.5, 1.0, seed=27), W("a7", "But:") - 0.05, 0.55, pan=0.7)
    fx.add(H.tingle(1.0), W("a7", "intelligence") - 0.1, 0.7)
    fx.add(H.riser(C["brain"] - W("a7", "happens"), 1.0, seed=28), W("a7", "happens"), 0.45)
    fx.add(H.hit((65, 68, 72, 77), 1.0, seed=29, big=True), C["brain"], 1.0)
    # --- routes and the bar
    fx.add(H.whoosh(0.6, up=True, seed=31), C["asi_road"] - 0.3, 0.5)
    fx.add(H.paper(1.0, seed=32), S("x2") - 0.1, 0.55)
    for k, tr in enumerate(C["routes"]):
        fx.add(H.paper(1.0, seed=33 + k), tr - 0.15, 0.5, pan=0.3 + 0.13 * k)
        fx.add(H.stab((70 + 2 * k, 77 + 2 * k), 0.14, 1.0, seed=50 + k), tr, 0.45)
    fx.add(H.riser(2.2, 1.0, seed=34), C["orgs"] - 1.6, 0.4)
    fx.add(H.hit((65, 68, 72, 77), 1.0, seed=35, big=True), C["boom"], 1.0)
    # --- the whole map
    fx.add(H.scratch(ahh, [(0.1, 0.35, 0.05, 1.0), (0.08, 0.05, 0.3, 1.0), (0.12, 0.3, 0.0, 1.0)], 0.32), C["scratch2"] + 0.02, 0.7)
    fx.add(H.hit((68, 72, 75, 80), 1.0, seed=36, big=True), S("f1"), 0.6)
    fx.add(H.chime([77, 81, 84, 89], 1.0), W("f2", "already"), 0.4)
    for k, tw in enumerate([W("f4", "competent"), W("f4", "keeps"), W("f4", "works")]):
        fx.add(H.stamp(0.9), tw, 0.55, pan=0.4 + 0.1 * k)
    fx.add(H.hit((68, 72, 75, 80), 1.0, seed=37, big=True), C["general"] - 0.1, 0.8)
    fx.add(H.tingle(1.0), C["general"], 0.75)
    fx.add(H.spray(0.8, 1.0, seed=38), C["general"] - 0.05, 0.4, pan=0.6)
    # --- the end: one last scratch and a button
    fx.add(H.baby_scratch(ahh, strokes=2, stroke=0.1), C["end_card"] + 0.1, 0.5)
    fx.add(H.hit((65, 68, 72, 77), 1.0, seed=39, big=True), C["end_card"] + 0.45, 0.7)
    fx.add(H.chime([77, 81, 84, 89, 93], 1.0), C["end_card"] + 0.45, 0.4)
    fx.add(H.hit((65, 72, 77), 1.0, seed=41), C["end"] - 0.55, 0.6)


def voices():
    vo = np.zeros(N)
    for key in TL.order:
        L = TL.lines[key]
        a = L["wav"].astype(np.float64)
        who = L["who"]
        if who == BOT:
            a = H.robotize(a, VSR)
        elif who == NOIR:
            a = H.old_radio(a, VSR)
        up = signal.resample_poly(a, SR, VSR)
        # level each line to the same speech loudness (the characters a touch hotter than the narrator)
        r = np.sqrt((up ** 2).mean()) + 1e-12
        tgt = {NAR: -18.0, BOT: -17.0, NOIR: -17.0, ANIME: -17.0}[who]
        up = up * db(tgt) / r
        i = int(L["start"] * SR)
        j = min(N, i + len(up))
        vo[i:j] += up[: j - i]
    return vo


def reverb(x, wet=0.1, rt60=0.8, seed=8):
    rng = np.random.default_rng(seed)
    t = np.arange(int(rt60 * 1.4 * SR)) / SR
    ir = np.stack([rng.normal(0, 1, len(t)) * np.exp(-6.9 * t / rt60) for _ in range(2)])
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    if x.ndim == 1:
        x = np.stack([x, x])
    y = np.stack([signal.fftconvolve(x[c], ir[c])[: x.shape[1]] for c in range(2)])
    return x * (1 - wet) + y * wet


def widen(x, amt=0.5):
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
    side = side + amt * H._hp(d, 200)
    return np.stack([mid + side, mid - side])


def build():
    drums, bass, keys, fx = Bus(), Bus(), Bus(), Bus()
    beat_grid(drums, bass, keys)
    sfx_track(fx, drums)
    # vinyl crackle all the way through (louder when the beat stops)
    cr = np.stack([H.crackle(TL.total + 0.6, seed=1), H.crackle(TL.total + 0.6, seed=2)])[:, :N]
    crack_gain = np.full(N, db(-6))
    for a, b in ((C["scratch1"], S("j2") - 0.1), (C["scratch2"], S("f2") - 0.25)):
        crack_gain[int(a * SR):int(b * SR)] = db(4)
    crack_gain[int(EDIT[6][0] * SR):int(EDIT[7][0] * SR)] = db(6)            # the noir world is all crackle and rain
    rain = H._lp(np.random.default_rng(9).normal(0, 1, N), 3000) * 0.05
    rain_g = np.zeros(N)
    rain_g[int(EDIT[6][0] * SR):int(EDIT[7][0] * SR)] = 1.0
    rain_g = np.convolve(rain_g, np.ones(SR // 10) / (SR // 10), "same")

    band = widen(reverb(drums.x, 0.08, 0.6), 0.35) + widen(bass.x * 1.0, 0.0) + widen(reverb(keys.x, 0.18, 1.2), 0.8)
    # backspins: the beat spun backwards into the silence of each record-scratch freeze
    for ts in (C["scratch1"], C["scratch2"]):
        i = int(ts * SR)
        mono = band[:, :i].mean(axis=0)
        bs = H.backspin(mono, 0.42)
        band[:, i:i + len(bs)] += bs * 1.2
    # the noir world: the beat heard through a wall
    a, b = int(EDIT[6][0] * SR), int(EDIT[7][0] * SR)
    band[:, a:b] = H._lp(band[:, a:b], 700) * 1.3
    fxr = widen(reverb(fx.x, 0.12, 0.9), 0.5)
    music = band + fxr * db(1.0) + cr * crack_gain * 0.9 + np.stack([rain, np.roll(rain, 300)]) * rain_g

    vo = voices()
    vo_st = reverb(vo, 0.05, 0.5)
    # duck: carve the speech band out of the music while anyone talks (instant attack, look-ahead, smooth release)
    from scipy.ndimage import maximum_filter1d
    raw = np.convolve(np.abs(vo), np.ones(SR // 20) / (SR // 20), mode="same")
    raw = np.clip(raw / (np.percentile(raw[raw > 1e-5], 80) + 1e-9), 0, 1)
    env = maximum_filter1d(raw, size=int(0.45 * SR), origin=-int(0.12 * SR))
    env = np.convolve(env, np.ones(SR // 12) / (SR // 12), mode="same")
    talk = np.zeros(N)
    for key in TL.order:
        talk[int((TL.s(key) - 0.1) * SR): int((TL.e(key) + 0.12) * SR)] = 1.0
    r = int(0.08 * SR)
    swell = 1 + (db(6.0) - 1) * (1 - np.convolve(talk, np.ones(r) / r, mode="same"))

    def carve(x, depth_mid):
        low = H._lp(x, 280)
        high = H._hp(x, 4200)
        mid = x - low - high
        return low * (1 - 0.35 * env) + mid * (1 - depth_mid * env) + high * (1 - 0.6 * env)

    music = carve(music * swell, 0.86)
    ref = music[:, int(S("r2") * SR):int(E("r5") * SR)]
    g_mu = db(-19.3) / (np.sqrt((ref ** 2).mean()) + 1e-12)
    mix = music * g_mu + vo_st
    mix = loudness(mix, -14.0)
    tail = int(0.25 * SR)
    mix[:, -tail:] *= np.linspace(1, 0, tail) ** 2
    STEMS.update(music=music * g_mu, vo=vo_st)
    return mix


STEMS = {}


def loudness(x, target):
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
    mix = build()
    write(os.path.join(HERE, "build", "audio.wav"), mix)
    print("audio", round(mix.shape[1] / SR, 2), "s in", round(time.time() - t0, 1), "s")
