"""Instruments for a boom-bap / hip-hop score, synthesized from scratch (no samples).

drums     kick (pitch-dropped sine + click), snare (tone + noise + clap), swung hats, open hat
bass      808 (sine with a pitch dive, long decay, saturated so it survives phone speakers)
keys      electric piano (two-operator FM with a bell tine and tremolo), detuned-saw synth stabs
texture   vinyl crackle and hiss, a synthesized vocal 'ahh' to scratch, record backspins
comic fx  hits, whooshes, glitch zaps, a buzzer, spray-can rattle and hiss, stamps, a 'spider-sense' tingle
"""
import numpy as np
from scipy import signal

SR = 48000
BPM = 90.0
BEAT = 60.0 / BPM


def tx(d):
    return np.arange(int(max(0.0, d) * SR)) / SR


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), "low")
    return signal.lfilter(b, a, x)


def _hp(x, fc, order=2):
    b, a = signal.butter(order, max(10, fc) / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def _bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi / (SR / 2), 0.99)], "band")
    return signal.lfilter(b, a, x)


def env_exp(n, tau):
    return np.exp(-np.arange(n) / SR / tau)


# ------------------------------------------------------------------ drums

def kick(amp=1.0, seed=0, boom=0.35):
    t = tx(0.5)
    f = 48 + 90 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / boom)
    rng = np.random.default_rng(seed)
    click = _hp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t / 0.004) * 0.5
    x = np.tanh(2.2 * (body + click)) * 0.9
    return amp * x


def snare(amp=1.0, seed=0, tight=1.0):
    t = tx(0.45)
    rng = np.random.default_rng(seed)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t / (0.06 / tight)) * 0.6
    noise = _bp(rng.normal(0, 1, len(t)), 1200, 9000) * np.exp(-t / (0.16 / tight))
    clap = np.zeros(len(t))
    for k, d in enumerate((0.0, 0.011, 0.023)):
        i = int(d * SR)
        n = int(0.012 * SR)
        clap[i:i + n] += _bp(rng.normal(0, 1, n), 900, 3500) * (0.9 - 0.2 * k)
    x = tone + noise * 0.8 + clap * 0.6
    return amp * np.tanh(1.4 * x) * 0.8


def hat(amp=1.0, seed=0, open_=False):
    d = 0.32 if open_ else 0.05
    t = tx(d + 0.02)
    rng = np.random.default_rng(seed)
    x = _hp(rng.normal(0, 1, len(t)), 7000) * np.exp(-t / (0.09 if open_ else 0.014))
    # a little metallic ring
    for f in (8100, 10450, 12900):
        x += 0.12 * np.sin(2 * np.pi * f * t) * np.exp(-t / (0.08 if open_ else 0.012))
    return amp * x * 0.45


def tom(f0=110, amp=1.0, dur=0.6):
    t = tx(dur)
    f = f0 * (1 + 0.6 * np.exp(-t / 0.05))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    return amp * np.tanh(1.8 * x)


# ------------------------------------------------------------------ bass and keys

def bass808(f0, dur, amp=1.0, glide=0.0):
    """808: a sine that dives an octave into the note, long decay, gently saturated for audible harmonics."""
    t = tx(dur + 0.05)
    f = f0 * (1 + 1.0 * np.exp(-t / 0.03)) * (1 + glide * np.clip(t / max(dur, 1e-3), 0, 1))
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.exp(-t / 0.9) * np.clip(t / 0.004, 0, 1)
    env *= np.clip((dur + 0.05 - t) / 0.05, 0, 1)
    x = np.sin(ph) * env
    x = np.tanh(2.6 * x) / np.tanh(2.6)
    return amp * x


def epiano(notes, dur, amp=1.0, seed=0, bright=1.0):
    """Two-operator FM electric piano: a mellow tone with a decaying bell tine and a slow tremolo."""
    t = tx(dur + 0.6)
    rng = np.random.default_rng(seed)
    out = np.zeros(len(t))
    for m in notes:
        f = midi(m) * 2 ** (rng.normal(0, 3) / 1200)
        idx = (1.6 * bright) * np.exp(-t / 0.35) + 0.25
        car = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
        tine = np.sin(2 * np.pi * f * 14.0 * t) * np.exp(-t / 0.04) * 0.12 * bright
        env = np.exp(-t / 1.4) * np.clip(t / 0.003, 0, 1) * np.clip((dur + 0.6 - t) / 0.4, 0, 1)
        out += (car + tine) * env
    trem = 1 + 0.18 * np.sin(2 * np.pi * 4.6 * t)
    return amp * out * trem / max(1, len(notes)) ** 0.6


def stab(notes, dur=0.22, amp=1.0, seed=0, cutoff=5200):
    """Detuned-saw chord stab with a fast filter drop (the brassy synth hit)."""
    t = tx(dur + 0.25)
    rng = np.random.default_rng(seed)
    x = np.zeros(len(t))
    for m in notes:
        for d in (-9, 0, 8):
            f = midi(m) * 2 ** (d / 1200)
            ph = (f * t + rng.uniform(0, 1)) % 1.0
            x += 2 * ph - 1
    env = np.exp(-t / (dur * 0.6)) * np.clip(t / 0.003, 0, 1)
    # a filter sweep, approximated by blending a bright and a dark copy
    bright = _lp(x, cutoff)
    dark = _lp(x, 900)
    k = np.exp(-t / 0.06)
    y = (bright * k + dark * (1 - k)) * env
    return amp * y / (3 * len(notes)) ** 0.7


def sub_drop(amp=1.0, dur=1.2):
    t = tx(dur)
    f = 30 + 70 * np.exp(-t / 0.25)
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.5)


def chime(notes, amp=1.0, step=0.07):
    """Bell arpeggio (sparkles, 'level up', 'share')."""
    n = int((len(notes) * step + 1.0) * SR)
    out = np.zeros(n)
    for i, m in enumerate(notes):
        t = tx(1.0)
        f = midi(m)
        x = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.1)) * np.exp(-t / 0.35)
        j = int(i * step * SR)
        out[j:j + len(x)] += x[: n - j]
    return amp * out * 0.4


# ------------------------------------------------------------------ texture

def crackle(dur, seed=0, rate=24.0, hiss=0.012):
    """Vinyl surface: a scatter of clicks and pops over a low hiss."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = _lp(rng.normal(0, 1, n), 5000) * hiss
    k = rng.poisson(rate * dur)
    for _ in range(k):
        i = rng.integers(0, n - 200)
        a = rng.uniform(0.03, 0.25) * (3.0 if rng.random() < 0.06 else 1.0)
        L = int(rng.uniform(20, 140))
        x[i:i + L] += a * rng.normal(0, 1, L) * np.exp(-np.arange(L) / (L / 4))
    return _hp(x, 300)


def vox_ahh(dur=0.9, f0=165.0, seed=3):
    """A synthesized sung 'ahh' (glottal buzz through vowel formants): the classic thing to scratch."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    f = f0 * (1 + 0.012 * np.sin(2 * np.pi * 5.2 * t))
    ph = np.cumsum(f) / SR
    buzz = 2 * (ph % 1.0) - 1
    buzz = buzz - _lp(buzz, 60)
    out = np.zeros(len(t))
    for fc, bw, g in ((800, 90, 1.0), (1150, 110, 0.6), (2900, 170, 0.25), (3300, 250, 0.15)):
        out += g * _bp(buzz, fc - bw, fc + bw, 2)
    out += 0.05 * _bp(rng.normal(0, 1, len(t)), 2000, 6000)
    env = np.clip(t / 0.02, 0, 1) * np.clip((dur - t) / 0.08, 0, 1)
    return out * env / (np.abs(out).max() + 1e-9)


def scratch(src, pattern, dur):
    """Turntablism: play `src` with a hand-moved position curve. pattern: list of (duration, from, to, fader)
    strokes in seconds of source time; the pitch follows the speed like vinyl."""
    out = []
    for d, a, b, fader in pattern:
        n = int(d * SR)
        u = np.linspace(0, 1, n)
        u = 0.5 - 0.5 * np.cos(np.pi * u)                         # the hand accelerates then slows
        pos = (a + (b - a) * u) * SR
        pos = np.clip(pos, 0, len(src) - 2)
        i = pos.astype(int)
        fr = pos - i
        seg = src[i] * (1 - fr) + src[i + 1] * fr
        out.append(seg * fader)
    x = np.concatenate(out) if out else np.zeros(1)
    return _hp(x, 120)[: int(dur * SR)]


def baby_scratch(src, strokes=4, stroke=0.11, depth=0.22, start=0.1):
    pat = []
    for k in range(strokes):
        pat.append((stroke, start, start + depth, 1.0))
        pat.append((stroke * 0.8, start + depth, start, 0.85 if k % 2 else 0.0))
    return scratch(src, pat, strokes * stroke * 1.8)


def backspin(x, dur=0.45):
    """A DJ backspin of the last bit of `x` (mono): played backwards, speeding up, rising in pitch."""
    n = int(dur * SR)
    src = x[-int(1.2 * SR):] if len(x) > int(1.2 * SR) else x
    L = len(src)
    rate = np.linspace(1.0, 4.0, n) ** 1.5
    pos = L - 1 - np.cumsum(rate)
    pos = np.clip(pos, 0, L - 2)
    i = pos.astype(int)
    fr = pos - i
    y = src[i] * (1 - fr) + src[i + 1] * fr
    return y * np.linspace(1, 0, n) ** 1.3


# ------------------------------------------------------------------ comic sound effects

def whoosh(dur=0.4, up=True, seed=0, amp=1.0):
    t = tx(dur)
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, len(t))
    out = np.zeros(len(t))
    fc = np.geomspace(300, 6000, 10) if up else np.geomspace(6000, 300, 10)
    seg = len(t) // 10 + 1
    for k in range(10):
        a, b = k * seg, min(len(t), (k + 1) * seg + 400)
        out[a:b] += _bp(n[a:b], fc[k] * 0.6, fc[k] * 1.4)[: b - a]
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.3
    return amp * out * env * 0.8


def hit(notes=(65, 68, 72, 75), amp=1.0, seed=0, big=False):
    """The comic HIT: kick + clap-snare + a chord stab (+ a sub drop when big)."""
    n = int(1.4 * SR)
    x = np.zeros(n)
    k = kick(1.0, seed)
    x[:len(k)] += k
    s = snare(0.8, seed + 1, tight=1.3)
    x[:len(s)] += s
    st = stab(notes, 0.28 if big else 0.18, 1.1, seed + 2)
    x[:len(st)] += st
    if big:
        sd = sub_drop(0.9)
        x[:len(sd)] += sd
        cr = _hp(np.random.default_rng(seed + 3).normal(0, 1, n), 5000) * np.exp(-np.arange(n) / SR / 0.35) * 0.35
        x += cr
    return amp * x


def zap(amp=1.0, seed=0):
    """Glitch zap between dimensions: an FM laser sweep, bitcrushed noise, and a stutter."""
    t = tx(0.42)
    rng = np.random.default_rng(seed)
    f = 3800 * np.exp(-t / 0.05) + 140
    car = np.sin(2 * np.pi * np.cumsum(f) / SR + 3 * np.sin(2 * np.pi * 31 * t))
    nz = rng.normal(0, 1, len(t))
    q = 5
    crushed = np.round(nz * q) / q
    crushed = np.repeat(crushed[::6], 6)[: len(t)]
    x = car * np.exp(-t / 0.12) * 0.7 + _bp(crushed, 800, 9000) * np.exp(-t / 0.09) * 0.5
    # stutter: repeat the first 35 ms three times
    L = int(0.035 * SR)
    chunk = x[:L].copy()
    for k in range(1, 4):
        i = int((0.14 + k * 0.045) * SR)
        x[i:i + L] += chunk * (0.8 ** k)
    return amp * np.tanh(1.5 * x) * 0.9


def buzzer(amp=1.0, dur=0.45):
    t = tx(dur)
    sq = np.sign(np.sin(2 * np.pi * 110 * t)) * 0.6 + np.sign(np.sin(2 * np.pi * 116.5 * t)) * 0.4
    x = _lp(sq, 2600) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 14 * t))) * np.clip((dur - t) / 0.05, 0, 1)
    return amp * x * 0.5


def rattle(amp=1.0, seed=0, n=4, gap=0.085):
    """Spray-can shake: the mixing bead clacking."""
    rng = np.random.default_rng(seed)
    out = np.zeros(int((n * gap + 0.2) * SR))
    for k in range(n):
        t = tx(0.06)
        x = _bp(rng.normal(0, 1, len(t)), 2500, 8000) * np.exp(-t / 0.01)
        x += 0.5 * np.sin(2 * np.pi * rng.uniform(3200, 4200) * t) * np.exp(-t / 0.02)
        i = int(k * gap * SR)
        out[i:i + len(x)] += x
    return amp * out


def spray(dur=0.5, amp=1.0, seed=0):
    t = tx(dur)
    rng = np.random.default_rng(seed)
    x = _bp(rng.normal(0, 1, len(t)), 3000, 11000)
    env = np.clip(t / 0.03, 0, 1) * np.clip((dur - t) / 0.12, 0, 1)
    return amp * x * env * 0.5


def thwip(amp=1.0, seed=0):
    t = tx(0.22)
    rng = np.random.default_rng(seed)
    f = 400 * np.exp(t / 0.06)
    tone = np.sin(2 * np.pi * np.cumsum(np.minimum(f, 5000)) / SR) * np.exp(-t / 0.05)
    nz = _bp(rng.normal(0, 1, len(t)), 1500, 9000) * np.exp(-t / 0.03)
    return amp * (tone * 0.6 + nz * 0.7)


def stamp(amp=1.0):
    t = tx(0.3)
    x = np.sin(2 * np.pi * np.cumsum(90 + 60 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.07)
    x += _bp(np.random.default_rng(5).normal(0, 1, len(t)), 200, 2000) * np.exp(-t / 0.02) * 0.6
    return amp * np.tanh(2 * x)


def tick(amp=1.0):
    t = tx(0.03)
    return amp * np.sin(2 * np.pi * 2600 * t) * np.exp(-t / 0.004)


def tingle(amp=1.0, dur=0.9):
    """The spider-sense: a shimmering high cluster with fast tremolo, swelling in."""
    t = tx(dur)
    x = np.zeros(len(t))
    for f in (1760, 2217, 2637, 3322):
        x += np.sin(2 * np.pi * f * t + 2 * np.sin(2 * np.pi * 7 * t))
    x *= 0.5 + 0.5 * np.sin(2 * np.pi * 28 * t)
    env = np.clip(t / 0.08, 0, 1) * np.exp(-np.clip(t - 0.08, 0, None) / 0.35)
    return amp * x * env * 0.25


def riser(dur, amp=1.0, seed=0):
    t = tx(dur)
    rng = np.random.default_rng(seed)
    nz = rng.normal(0, 1, len(t))
    out = np.zeros(len(t))
    fc = np.geomspace(400, 9000, 16)
    seg = len(t) // 16 + 1
    for k in range(16):
        a, b = k * seg, min(len(t), (k + 1) * seg + 400)
        out[a:b] += _bp(nz[a:b], fc[k] * 0.7, fc[k] * 1.3)[: b - a]
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(200, 1200, len(t))) / SR) * 0.3
    return amp * (out + tone) * (t / max(dur, 1e-3)) ** 2 * 0.7


def paper(amp=1.0, seed=0):
    """A panel slapped down: a paper swish and a slap."""
    x = whoosh(0.18, up=False, seed=seed, amp=0.6)
    t = tx(0.12)
    slap = _bp(np.random.default_rng(seed).normal(0, 1, len(t)), 400, 5000) * np.exp(-t / 0.012)
    out = np.zeros(len(x) + len(slap))
    out[:len(x)] += x
    out[len(x) - 400:len(x) - 400 + len(slap)] += slap
    return amp * out


def robotize(x, sr, rate=38.0, mix=0.45):
    t = np.arange(len(x)) / sr
    ring = x * np.sin(2 * np.pi * rate * t)
    return x * (1 - mix) + ring * mix * 1.6


def old_radio(x, sr):
    b, a = signal.butter(2, [300 / (sr / 2), 3400 / (sr / 2)], "band")
    y = signal.lfilter(b, a, x)
    return np.tanh(2.0 * y) / 2.0 * 1.6
