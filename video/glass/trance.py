"""Instruments for GLASS. All synthesized, no samples, all original.

trance    a hypnotic North African-style ensemble: a frame drum with a gut snare (bendir), a goblet drum (doum, tek, ka),
          metal castanets clattering in triplets, hand claps, a double-reed horn (nasal, ornamented, scooping up into its
          notes), chanting voices on a rhythm of syllables
orchestra low strings, heavy brass that swells, a wordless choir, a tam-tam that blooms
the theme a fragile melody in D hijaz on a solo female voice, coming back more corrupted each time
sound     silk and capes, porcelain creaking, a lens iris whirring open, camera shutters, glass cracking and
          shattering, sand hissing, breath inside a mask, a body of water closing overhead, reversed voices, knocks
          on a door, a heart monitor, machine hum
"""
import numpy as np
from scipy import signal

import doom as DM
import instr as I
import orch as O
import synth82 as Y
from orch import SR, _bp, _hp, _lp, _noise, midi, tx

# D hijaz: D Eb F# G A Bb C
HIJAZ = [62, 63, 66, 67, 69, 70, 72, 74]
# the fragile theme: A Bb A G F# Eb D ... (beats)
THEME = [(69, 1.0), (70, 0.5), (69, 0.5), (67, 1.0), (66, 1.0), (63, 1.5), (62, 2.5)]


def _env(n, att, rel, dur):
    t = np.arange(n) / SR
    return np.clip(t / max(att, 1e-4), 0, 1) * np.clip((dur - t) / max(rel, 1e-4), 0, 1)


def swell(x, att=1.0, shape=2.0):
    """A crescendo: the sound grows in over att seconds."""
    t = np.arange(x.shape[-1]) / SR
    return x * np.clip(t / att, 0, 1) ** shape


# ------------------------------------------------------------------ drums

def bendir(stroke="dum", amp=1.0, seed=0):
    """A frame drum with a gut snare across the skin: dum (centre, deep), tak (edge, bright)."""
    rng = np.random.default_rng(seed)
    t = tx(0.9)
    if stroke == "dum":
        f = 74 * (1 + 0.28 * np.exp(-t / 0.05))
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.32) + 0.4 * np.sin(2 * np.pi * np.cumsum(f * 1.59) / SR) * np.exp(-t / 0.12)
        slap = _lp(rng.normal(0, 1, len(t)), 900) * np.exp(-t / 0.012) * 0.6
        buzz_amt = 0.35
    else:
        body = np.sin(2 * np.pi * 410 * t) * np.exp(-t / 0.06) * 0.5 + np.sin(2 * np.pi * 690 * t) * np.exp(-t / 0.04) * 0.3
        slap = _bp(rng.normal(0, 1, len(t)), 1200, 5200) * np.exp(-t / 0.02) * 0.9
        buzz_amt = 0.55
    rattle = (rng.random(len(t)) < 0.08).astype(float) * rng.normal(0, 1, len(t))
    buzz = _bp(rng.normal(0, 1, len(t)) * 0.5 + rattle, 1800, 6500) * np.exp(-t / 0.16) * buzz_amt
    return amp * np.tanh(1.3 * (body + slap + buzz)) * 0.8


def darbuka(stroke="doum", amp=1.0, seed=0):
    """A goblet drum: doum (the deep centre), tek (the sharp rim), ka (the softer rim, other hand)."""
    rng = np.random.default_rng(seed)
    t = tx(0.6)
    if stroke == "doum":
        f = 104 * (1 + 0.18 * np.exp(-t / 0.03))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.24) + 0.3 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * np.exp(-t / 0.08)
        x += _lp(rng.normal(0, 1, len(t)), 1200) * np.exp(-t / 0.01) * 0.4
    else:
        hi = stroke == "tek"
        x = _bp(rng.normal(0, 1, len(t)), 2200 if hi else 1500, 7000 if hi else 4200) * np.exp(-t / (0.012 if hi else 0.018))
        x += np.sin(2 * np.pi * (3100 if hi else 2300) * t) * np.exp(-t / 0.02) * 0.5
        x += np.sin(2 * np.pi * 620 * t) * np.exp(-t / 0.03) * 0.4
        x *= 1.0 if hi else 0.6
    return amp * np.tanh(1.5 * x) * 0.8


def krakeb(amp=1.0, seed=0):
    """Metal castanets: two iron plates clacking - a click and a short inharmonic ring."""
    rng = np.random.default_rng(seed)
    t = tx(0.25)
    ring = sum(np.sin(2 * np.pi * f * rng.uniform(0.98, 1.02) * t + rng.uniform(0, 6)) * np.exp(-t / d) / (k + 1)
               for k, (f, d) in enumerate(((2210, 0.05), (3480, 0.04), (5120, 0.03), (6870, 0.02))))
    click = _hp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t / 0.004)
    return amp * (ring * 0.7 + click * 0.8) * 0.6


def clap(amp=1.0, seed=0):
    return O.clap(amp, seed)


# ------------------------------------------------------------------ the reed and the voices

def ghaita(m, dur, amp=1.0, seed=0, grace=True, vib=1.0, scoop=True):
    """A double-reed horn: a buzzing, nasal tone, a little scoop up into the note, a quick upper grace note, vibrato."""
    rng = np.random.default_rng(seed)
    t = tx(dur + 0.08)
    f0 = midi(m)
    pitch = np.ones(len(t))
    if scoop:
        pitch *= 2 ** (-0.6 * np.exp(-t / 0.035) / 12)
    if grace and dur > 0.25:
        g = (t > 0.0) & (t < 0.055)
        pitch[g] *= 2 ** (2 / 12)
    pitch *= 1 + 0.008 * vib * np.sin(2 * np.pi * 6.2 * t + rng.uniform(0, 6)) * np.clip((t - 0.15) / 0.3, 0, 1)
    ph = np.cumsum(f0 * pitch) / SR
    duty = 0.28
    src = np.where((ph % 1.0) < duty, 1.0, -0.4) + 0.4 * (2 * (ph % 1.0) - 1)
    src = src - np.mean(src)
    buzz = _bp(rng.normal(0, 1, len(t)), 2500, 7000) * (0.5 + 0.5 * np.sin(2 * np.pi * ph)) * 0.15
    x = _bp(src, 900, 1400) * 1.0 + _bp(src, 2100, 2900) * 0.8 + _bp(src, 3300, 4200) * 0.45 + _hp(src, 300) * 0.25 + buzz
    x = np.tanh(2.2 * x)
    env = _env(len(t), 0.02, 0.06, dur + 0.08)
    return amp * x * env * 0.3


def ghaita_phrase(notes, beat, amp=1.0, seed=0, vib=1.0):
    """A run of ghaita notes [(midi, beats)]; None is a breath."""
    total = sum(b for _, b in notes) * beat + 0.3
    out = np.zeros(int(total * SR) + SR)
    t = 0.0
    for i, (m, b) in enumerate(notes):
        if m is not None:
            x = ghaita(m, b * beat * 0.98, 1.0, seed=seed + i, grace=(i % 2 == 0), vib=vib)
            j = int(t * SR)
            out[j:j + len(x)] += x[: len(out) - j]
        t += b * beat
    return amp * out


def chant(pattern, beat, root=50, amp=1.0, seed=0):
    """Chanting voices on a rhythm of syllables: pattern [(vowel or None, beats, accent)]. A low drone of voices
    under it on the root and fifth."""
    total = sum(b for _, b, _ in pattern) * beat + 0.4
    n = int(total * SR) + SR
    out = np.zeros(n)
    rng = np.random.default_rng(seed)
    t = 0.0
    for i, (v, b, acc) in enumerate(pattern):
        if v is not None:
            d = max(0.12, b * beat * 0.85)
            for k, dm in enumerate((0.0, 0.07, -0.06, 12.0)):
                x = O.voices(v, root + dm + (7 if (k == 1 and acc > 1.2) else 0), d, 1.0, seed=seed + i * 5 + k)
                e = _env(len(x), 0.015, 0.06, d)
                h = _bp(rng.normal(0, 1, len(x)), 800, 3500) * np.exp(-np.arange(len(x)) / SR / 0.03) * 0.5    # the breathy onset
                j = int(t * SR) + int(rng.uniform(0, 0.012) * SR)
                seg = (x * e + h) * acc * (0.6 if k == 3 else 1.0)
                out[j:j + len(seg)] += seg[: n - j]
        t += b * beat
    drone = I.choir([root - 12, root - 5], total, 0.5, vowel="o", seed=seed + 99, attack=0.8)
    out[: len(drone)] += drone[:n] * 0.6
    return amp * out * 0.35


def solo(m, dur, amp=1.0, vowel="a", seed=0, breath=0.16):
    return DM.solo(m, dur, amp, vowel=vowel, seed=seed, breath=breath)


def theme(beat=0.55, amp=1.0, seed=0, transpose=0, vowel="a", notes=None, breath=0.16):
    """The fragile melody on a solo female voice."""
    notes = notes or THEME
    total = sum(b for _, b in notes) * beat + 0.6
    out = np.zeros(int(total * SR) + SR)
    t = 0.0
    for i, (m, b) in enumerate(notes):
        if m is not None:
            x = DM.solo(m + transpose, b * beat * 1.05, 1.0, vowel=vowel, seed=seed + i, breath=breath)
            j = int(t * SR)
            out[j:j + len(x)] += x[: len(out) - j]
        t += b * beat
    return amp * out


# ------------------------------------------------------------------ the orchestra

def low_strings(notes, dur, amp=1.0, seed=0, att=0.6):
    """Cellos and basses: dark detuned saws, a slow bow, rosin grit."""
    t = tx(dur + 0.6)
    rng = np.random.default_rng(seed)
    out = np.zeros(len(t))
    for m in notes:
        for d in (-9, -2, 5, 11):
            f = midi(m) * 2 ** (d / 1200) * (1 + 0.003 * np.sin(2 * np.pi * rng.uniform(4.5, 5.5) * t + rng.uniform(0, 6)))
            ph = np.cumsum(f) / SR + rng.uniform()
            out += 2 * (ph % 1.0) - 1
    out = _lp(out, 1400) + _bp(rng.normal(0, 1, len(t)), 1500, 4000) * 0.03
    env = np.clip(t / att, 0, 1) ** 1.5 * np.clip((dur + 0.6 - t) / 0.6, 0, 1)
    return amp * out * env * 0.09 / max(1, len(notes)) ** 0.5


def brass_swell(notes, dur, amp=1.0, seed=0, att=1.2, bright=0.8):
    """Heavy brass swelling from nothing to a roar."""
    x = O.brass(notes, dur, 1.0, seed=seed, bright=bright)
    return amp * swell(x, att, 2.2)


def brass_stab(notes, amp=1.0, seed=0, dur=0.7):
    return O.brass(notes, dur, amp, seed=seed, bright=1.4)


def choir(notes, dur, amp=1.0, vowel="a", seed=0, attack=0.6):
    return I.choir(notes, dur, amp, vowel=vowel, seed=seed, attack=attack)


def tamtam(amp=1.0, dur=6.0, seed=0, f0=58.0):
    """A tam-tam: struck soft, it blooms - the shimmer grows after the stroke, then a long dark wash."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    out = np.zeros(len(t))
    for k in range(40):
        f = f0 * (1 + k * rng.uniform(0.9, 1.6)) ** 1.15
        if f > 9000:
            break
        bloom = np.clip(t / (0.15 + 0.02 * k), 0, 1) * np.exp(-t / (dur * rng.uniform(0.2, 0.5)))
        out += np.sin(2 * np.pi * f * t * (1 + 0.0008 * np.sin(2 * np.pi * rng.uniform(0.2, 1.0) * t)) + rng.uniform(0, 6)) * bloom / (1 + 0.15 * k)
    hit = _lp(rng.normal(0, 1, len(t)), 400) * np.exp(-t / 0.05) * 0.8
    return amp * np.tanh(0.8 * out + hit) * 0.5


def taiko(amp=1.0, seed=0, f0=52.0):
    """A huge low drum for the collapse."""
    rng = np.random.default_rng(seed)
    t = tx(1.6)
    f = f0 * (1 + 0.5 * np.exp(-t / 0.04))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.5) + _lp(rng.normal(0, 1, len(t)), 500) * np.exp(-t / 0.02) * 0.7
    return amp * np.tanh(1.6 * x) * 0.9


# ------------------------------------------------------------------ sound

def silk(dur, amp=1.0, seed=0, rate=0.6):
    """Heavy silk and a cape in slow motion: broad swishes of rustle and the low push of moving cloth."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    wave = 0.5 + 0.5 * np.sin(2 * np.pi * rate * t + rng.uniform(0, 6)) * np.sin(2 * np.pi * rate * 0.37 * t + 1.0)
    rust = _bp(rng.normal(0, 1, len(t)), 2200, 9000) * (0.25 + 0.75 * wave ** 2)
    crinkle = (rng.random(len(t)) < 0.002 * (0.3 + wave)) * rng.normal(0, 1, len(t))
    push = _lp(rng.normal(0, 1, len(t)), 220) * wave * 1.5
    return amp * (rust * 0.5 + _hp(crinkle, 3000) * 0.6 + push) * _env(len(t), 0.4, 0.5, dur) * 0.5


def porcelain_creak(amp=1.0, seed=0, dur=0.35):
    """Glazed porcelain grinding against itself: stick-slip chirps and a dry squeal."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    gate = np.zeros(len(t))
    k = 0
    while k < len(t):
        L = int(rng.uniform(0.004, 0.02) * SR)
        gate[k:k + L] = rng.uniform(0.4, 1.0)
        k += L + int(rng.uniform(0.004, 0.03) * SR)
    f = 2400 + 900 * np.sin(2 * np.pi * 3 * t)
    sq = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
    x = (_bp(rng.normal(0, 1, len(t)), 2500, 7500) + sq) * gate
    return amp * x * _env(len(t), 0.01, 0.05, dur) * 0.7


def aperture(amp=1.0, dur=0.45, seed=0, open_=True):
    """A lens iris whirring open: a tiny motor rising, ratcheting clicks, a final tick."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    f = (900 + 1500 * (t / dur)) if open_ else (2400 - 1500 * (t / dur))
    motor = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + _bp(rng.normal(0, 1, len(t)), 2000, 6000) * 0.15
    clicks = np.zeros(len(t))
    for c in np.arange(0.0, dur - 0.02, 0.025):
        j = int(c * SR)
        clicks[j:j + 60] += np.exp(-np.arange(60) / 10) * rng.uniform(0.5, 1.0)
    tick = np.zeros(len(t))
    j = int((dur - 0.03) * SR)
    tick[j:j + 200] = np.exp(-np.arange(200) / 25)
    return amp * (motor * _env(len(t), 0.01, 0.03, dur) + _hp(clicks, 2000) * 0.6 + _hp(tick, 1500) * 1.0) * 0.6


def shutter(amp=1.0, seed=0):
    """A camera shutter: two crisp mechanical clicks and a little spring ring."""
    rng = np.random.default_rng(seed)
    t = tx(0.12)
    x = np.zeros(len(t))
    for c, g in ((0.0, 1.0), (0.035, 0.7)):
        j = int(c * SR)
        n = len(t) - j
        x[j:] += _hp(rng.normal(0, 1, n), 2500) * np.exp(-np.arange(n) / SR / 0.004) * g
        x[j:] += np.sin(2 * np.pi * 4200 * np.arange(n) / SR) * np.exp(-np.arange(n) / SR / 0.012) * 0.3 * g
    return amp * x * 0.7


def glass_crack(amp=1.0, seed=0):
    """Glass giving way: a sharp tick, a splintering run, the high ring of the pane."""
    rng = np.random.default_rng(seed)
    t = tx(0.9)
    x = np.zeros(len(t))
    for k in range(14):
        j = int((0.02 * k + rng.uniform(0, 0.015) * k) * SR)
        if j >= len(t):
            break
        n = len(t) - j
        x[j:] += _hp(rng.normal(0, 1, n), 3000) * np.exp(-np.arange(n) / SR / 0.003) * rng.uniform(0.3, 1.0)
    ring = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / 0.25) for f in rng.uniform(3000, 7500, 5)) * 0.08
    return amp * (x + ring) * 0.8


def shatter(amp=1.0, seed=0, dur=2.2):
    """A sheet of glass exploding: the crash, then a long rain of tinkling shards."""
    rng = np.random.default_rng(seed)
    t = tx(dur)
    crash = _hp(rng.normal(0, 1, len(t)), 1500) * np.exp(-t / 0.12) * 1.2 + _lp(rng.normal(0, 1, len(t)), 400) * np.exp(-t / 0.06) * 0.8
    tink = np.zeros(len(t))
    for k in range(160):
        t0 = rng.uniform(0.0, dur * 0.85) ** 1.6 / dur ** 0.6
        j = int(t0 * SR)
        n = min(int(0.15 * SR), len(t) - j)
        if n <= 0:
            continue
        f = rng.uniform(2500, 9000)
        tink[j:j + n] += np.sin(2 * np.pi * f * np.arange(n) / SR) * np.exp(-np.arange(n) / SR / rng.uniform(0.01, 0.05)) * rng.uniform(0.1, 0.5) * np.exp(-t0 / dur * 2)
    return amp * np.tanh(crash + tink) * 0.7


def sand(dur, amp=1.0, seed=0, gust=0.4):
    """Sand hissing across the dunes, rising and falling in gusts."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    g = 0.5 + 0.5 * np.sin(2 * np.pi * gust * t + rng.uniform(0, 6)) * np.sin(2 * np.pi * gust * 0.43 * t + 2)
    x = _bp(rng.normal(0, 1, len(t)), 3500, 11000) * (0.3 + 0.7 * g)
    return amp * x * _env(len(t), 0.5, 0.5, dur) * 0.35


def mask_breath(dur, amp=1.0, rate=0.32, seed=0):
    """Breathing inside a mask: slow, close, a hollow resonance round every breath and the tick of a valve."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    ph = (t * rate) % 1.0
    inh = np.clip(np.sin(np.pi * ph / 0.42), 0, 1) * (ph < 0.42)
    exh = np.clip(np.sin(np.pi * (ph - 0.48) / 0.45), 0, 1) * (ph >= 0.48) * (ph < 0.93)
    nz = rng.normal(0, 1, len(t))
    air = _bp(nz, 500, 2600) * inh ** 1.5 * 0.9 + _bp(nz, 300, 1500) * exh ** 1.5 * 0.7
    b, a = signal.iirpeak(780 / (SR / 2), 6)
    air = air + signal.lfilter(b, a, air) * 1.4
    valve = np.zeros(len(t))
    for k in range(int(dur * rate) + 1):
        j = int((k / rate + 0.48 / rate) * SR)
        if j < len(t) - 100:
            valve[j:j + 100] += np.exp(-np.arange(100) / 12)
    return amp * (air + _hp(valve, 1500) * 0.3) * _env(len(t), 0.3, 0.3, dur) * 0.5


def underwater(x, depth=1.0):
    """Muffle a sound as if heard from under water: low-passed, a slow wobble."""
    y = _lp(x, 1800 - 1450 * depth, order=4)
    t = np.arange(len(y)) / SR
    return y * (1 + 0.15 * depth * np.sin(2 * np.pi * 0.7 * t))


def bubbles(dur, amp=1.0, seed=0, rate=9.0):
    return O.bubbling(dur, amp, seed=seed, rate=rate)


def reversed_voice(wav, sr_in, pitch=-5.0, amp=1.0):
    """A voice played backwards, slowed and pitched down into something that isn't speech any more."""
    from scipy import signal as sg
    x = np.asarray(wav, np.float64)[::-1]
    x = sg.resample_poly(x, SR, sr_in)
    r = 2 ** (pitch / 12)
    x = sg.resample(x, int(len(x) / r))
    x = x / (np.abs(x).max() + 1e-9)
    return amp * x * 0.5


def knock(amp=1.0, seed=0):
    """A fist on a door: a deep wooden thud, a knuckle crack, the door shuddering in its frame."""
    rng = np.random.default_rng(seed)
    t = tx(0.7)
    f = 95 * (1 + 0.3 * np.exp(-t / 0.02))
    thud = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12) + 0.5 * np.sin(2 * np.pi * np.cumsum(f * 2.3) / SR) * np.exp(-t / 0.05)
    crack = _bp(rng.normal(0, 1, len(t)), 900, 4500) * np.exp(-t / 0.008) * 0.9
    rattle = _bp(rng.normal(0, 1, len(t)), 300, 1500) * np.exp(-t / 0.09) * (np.sin(2 * np.pi * 31 * t) > 0) * 0.35
    return amp * np.tanh(2.0 * (thud + crack + rattle)) * 0.95


def stamp(amp=1.0, seed=0):
    """A rubber stamp / a mechanical stamp slamming down."""
    return O.stamp(amp)


def beep(f=1000.0, dur=0.09, amp=1.0):
    return Y.beep(f, dur, amp)


def monitor(dur, bpm=64, amp=1.0, f=1040.0):
    return Y.monitor(dur, bpm=bpm, amp=amp, f=f)


def hum(dur, amp=1.0, seed=0):
    return DM.hum(dur, amp, seed=seed, flicker=0.05)


def ticks(dur, rate=6.0, amp=1.0, seed=0):
    """Clockwork: an escapement ticking, a gear train whirring under it."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    out = np.zeros(len(t))
    for k in range(int(dur * rate)):
        j = int(k / rate * SR)
        n = min(int(0.03 * SR), len(t) - j)
        out[j:j + n] += _hp(rng.normal(0, 1, n), 2500) * np.exp(-np.arange(n) / SR / 0.003) * (1.0 if k % 2 else 0.7)
    whirr = O.whir(dur, 0.3, f=140.0, seed=seed)[: len(t)]
    out[: len(whirr)] += whirr
    return amp * out * 0.6
