"""An original 1970s prog-rock horror band, synthesized (nothing sampled, every riff and the lullaby original), and
the night's foley.

  the lullaby   a celesta and a music box in A minor, 3/4 - sweet, too perfect, slowing and going out of tune
  bouzouki      two steel courses (Karplus-Strong), picked in fast tremolo, in A Phrygian dominant
  tabla         dayan 'na' / 'tin' (ringing, pitched), bayan 'ge' (a bass stroke that bends), 'dha' (both); a frame drum
  synths        a droning, slowly sweeping analogue pad; a fuzz bass; a screaming lead for the crash-ins
  voices        a gang of six voices chanting invented words, pitched down and driven (growls); invented whispers
  foley         rain, thunder, creaking boards, footsteps, a heartbeat, breathing close to the mic, a clock, the desk
                bell, keys, a lock, the phone (taps, a notification, a dial tone and ringing), a neon buzz, cracking glass,
                coins, a tape rewinding, a siren, a hospital monitor, birds
  stings        the jump-scare hits: a dissonant stab, timpani, a cymbal, a violin screech
"""
import math

import numpy as np
from scipy import signal

import band as Bd
import orch as O
from voice import SR as VSR
from voice import chorus, speak_fx, whisper

SR = O.SR
midi, tx, _lp, _hp, _bp, _noise = O.midi, O.tx, O._lp, O._hp, O._bp, O._noise


def env_ad(n, a=0.005, d=0.3):
    t = np.arange(n) / SR
    return np.clip(t / a, 0, 1) * np.exp(-np.maximum(0, t - a) / d)


# ------------------------------------------------------------------ the lullaby

LULLABY = [(76, 1), (81, 1), (84, 1), (83, 2), (81, 1), (80, 1), (81, 1), (83, 1), (76, 3),
           (77, 1), (81, 1), (86, 1), (84, 2), (83, 1), (81, 1), (80, 1), (83, 1), (81, 3)]
DAWN = [(76, 1), (81, 1), (85, 1), (83, 2), (81, 1), (80, 1), (81, 1), (83, 1), (85, 3),
        (78, 1), (81, 1), (86, 1), (85, 2), (83, 1), (81, 1), (80, 1), (83, 1), (81, 3)]       # the same tune, in A major


def lullaby(bus, t0, beat=0.6, amp=1.0, notes=LULLABY, inst="celesta", rate=None, detune=None, pan=0.3, bars=None):
    """Place the lullaby from t0; inst 'celesta' or 'box'."""
    if inst == "box":
        y = O.music_box(notes, rate=rate, amp=amp, detune=detune)
        bus.add(y, t0, 1.0, pan=pan)
        return t0 + len(y) / SR
    t = t0
    for m, b in notes:
        bus.add(O.celesta(m, amp * 0.9, dur=1.6), t, 1.0, pan=pan)
        bus.add(O.celesta(m - 12, amp * 0.3, dur=1.2), t, 1.0, pan=pan)
        bus.add(O.celesta(m, amp * 0.35, dur=1.2), t + beat * 0.5, 1.0, pan=1.0 - pan)        # an echo, across the room
        t += b * beat
    return t


# ------------------------------------------------------------------ bouzouki

def bouzouki(m, dur, amp=1.0, trem=0.0, seed=0):
    """A steel-strung double course: two strings a few cents apart (the lower courses with an octave string),
    plucked once, or in fast tremolo (trem = picks per second)."""
    n = int((dur + 0.4) * SR)
    out = np.zeros(n)
    picks = [0.0] if trem <= 0 else list(np.arange(0, dur, 1.0 / trem))
    for k, p in enumerate(picks):
        L = min(0.5, dur - p + 0.35) if trem > 0 else dur + 0.4
        a = 1.0 if k == 0 else (0.62 if k % 2 else 0.5)
        for d_ in (-4, 5):
            y = Bd.pluck(m, 1.0, L, seed=seed + k, damp=0.9985) * a
            y = signal.resample_poly(y, 1000, int(1000 * 2 ** (d_ / 1200)))[: len(y)] if d_ else y
            j = int(p * SR)
            out[j:j + len(y)] += y[: n - j]
        if m < 62:
            y = Bd.pluck(m + 12, 0.5, L, seed=seed + 99 + k, damp=0.998) * a
            j = int(p * SR)
            out[j:j + len(y)] += y[: n - j]
    out = _hp(out, 180) + 0.4 * _bp(out, 2500, 6000)                    # the metallic, nasal top
    return amp * np.tanh(1.4 * out) * 0.35


PHRYG = [57, 58, 61, 62, 64, 65, 67, 69]                              # A Bb C# D E F G A


# ------------------------------------------------------------------ tabla and hand drums

def tabla(kind, amp=1.0, seed=0):
    t = tx(0.9)
    rng = np.random.default_rng(seed)
    if kind in ("na", "tin"):                                           # the dayan: a ringing, pitched stroke
        f = 560 if kind == "na" else 610
        x = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.02 * t) + 0.25 * np.sin(2 * np.pi * f * 3.01 * t))
        x *= np.exp(-t / (0.32 if kind == "tin" else 0.18))
        x += _bp(rng.normal(0, 1, len(t)), 2000, 7000) * np.exp(-t / 0.006) * 0.6
        return amp * x * 0.35
    if kind == "ge":                                                    # the bayan: a bass stroke whose pitch slides up
        f = 82 + 40 * (1 - np.exp(-t / 0.12))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35)
        x += _lp(rng.normal(0, 1, len(t)), 400) * np.exp(-t / 0.01) * 0.5
        return amp * np.tanh(1.5 * x) * 0.6
    if kind == "dha":
        return tabla("na", amp, seed) + tabla("ge", amp, seed)
    if kind == "tek":                                                   # a frame drum's rim
        x = _bp(rng.normal(0, 1, len(t)), 1500, 5000) * np.exp(-t / 0.02)
        return amp * x * 0.5
    if kind == "doum":
        x = np.sin(2 * np.pi * np.cumsum(70 + 50 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.25)
        return amp * np.tanh(2 * x) * 0.6
    return np.zeros(len(t))


# a 7/8 cycle (2 + 2 + 3), one stroke per eighth (None = rest)
TAAL7 = ["dha", "na", "ge", "tin", "dha", "na", "tin"]
TAAL7_LIGHT = ["ge", None, "na", None, "ge", "na", None]
BASS7 = [45, 45, 48, 45, 46, 43, 45]                                   # A A C A Bb G A


def fuzz_bass(m, dur, amp=1.0):
    t = tx(dur + 0.05)
    f = midi(m)
    x = 2 * ((f * t) % 1.0) - 1 + 0.6 * np.sign(np.sin(2 * np.pi * f * 0.5 * t))
    x = np.tanh(4.0 * _lp(x, 1400)) * np.clip(t / 0.005, 0, 1) * np.clip((dur + 0.05 - t) / 0.03, 0, 1)
    return amp * _lp(x, 2600) * 0.32


def groove(bus, t0, t1, eighth=0.2, level=1.0, bass=True, drums=True, zouk=True, light=False, seed=0, energy=None):
    """The band in 7/8: fuzz bass ostinato, tabla, bouzouki tremolo phrases. energy(t) 0..1 thins it under the voices."""
    t, k = t0, 0
    rng = np.random.default_rng(seed)
    while t < t1 - 0.02:
        e = energy(t) if energy else 1.0
        i = k % 7
        if drums:
            st = (TAAL7_LIGHT if light else TAAL7)[i]
            if st:
                bus.add(tabla(st, (1.0 if i in (0, 2, 4) else 0.7) * level * (0.6 + 0.4 * e), seed=k), t, 1.0, pan=0.28 + 0.44 * (i % 2))
            if not light and i == 4:
                bus.add(tabla("doum", 0.6 * level * e, seed=k), t, 1.0, pan=0.62)
        if bass:
            bus.add(fuzz_bass(BASS7[i], eighth * 0.9, (1.0 if i in (0, 2, 4) else 0.75) * level * (0.5 + 0.5 * e)), t, 1.0)
        if zouk and i == 0 and (k // 7) % 2 == 1 and e > 0.5:
            line = [PHRYG[j] + 12 for j in rng.permutation([0, 1, 2, 3, 4])[:3]]
            for q, m in enumerate(line):
                bus.add(bouzouki(m, eighth * 2.2, 0.8 * level * e, trem=14, seed=k + q), t + q * eighth * 2.3, 1.0, pan=0.82)
        t += eighth
        k += 1


def drone(dur, root=33, amp=1.0, seed=0, sweep=0.12):
    """The analogue pad: detuned saws on the root and fifth through a slowly breathing low-pass."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    x = np.zeros(len(t))
    for m, d in ((root, 0), (root, 7), (root + 7, -5), (root + 12, 3), (root + 12, -9)):
        f = midi(m) * 2 ** (d / 1200)
        x += 2 * ((f * t + rng.uniform()) % 1.0) - 1
    cut = 300 + 900 * (0.5 + 0.5 * np.sin(2 * np.pi * sweep * t))
    out = np.zeros(len(t))
    blk = 2048
    zi = None
    for i in range(0, len(t), blk):                                     # a filter that moves
        b, a = signal.butter(2, min(0.99, cut[i] / (SR / 2)), "low")
        if zi is None:
            zi = signal.lfilter_zi(b, a) * 0
        out[i:i + blk], zi = signal.lfilter(b, a, x[i:i + blk], zi=zi)
    env = np.clip(t / 1.0, 0, 1) * np.clip((dur - t) / 0.6, 0, 1)
    return amp * out * env * 0.12


def drone_st(dur, root=33, amp=1.0, seed=0, sweep=0.12):
    """The pad in stereo: two decorrelated voicings, left and right."""
    return np.stack([drone(dur, root, amp, seed, sweep), drone(dur, root, amp, seed + 57, sweep * 1.13)]) * 0.75


def lead(m0, m1, dur, amp=1.0):
    """A screaming analogue lead, sliding: the crash-in's top line."""
    t = tx(dur)
    f = midi(m0) * (midi(m1) / midi(m0)) ** np.clip(t / (dur * 0.5), 0, 1) * (1 + 0.01 * np.sin(2 * np.pi * 6 * t))
    ph = np.cumsum(f) / SR
    x = 2 * (ph % 1.0) - 1 + 0.5 * (2 * ((ph * 1.005) % 1.0) - 1)
    x = np.tanh(2.5 * _lp(x, 3500))
    return amp * x * np.clip(t / 0.02, 0, 1) * np.clip((dur - t) / 0.1, 0, 1) * 0.25


def crash_in(bus, t0, dur, level=1.0, seed=0, words="Ahvenna! Kolumé!"):
    """The score crashing in at full volume: a stab, the whole band in 7/8, the lead, the gang chanting invented words."""
    bus.add(O.scare(1.0 * level, seed=seed, body=1.2, drive=2.2), t0, 1.0)
    groove(bus, t0, t0 + dur, 0.17, level=1.25 * level, seed=seed)
    bus.add(lead(69, 81, dur, 0.9 * level), t0, 1.0, pan=0.55)
    bus.add(drone_st(dur + 0.3, 33, 2.2 * level, seed=seed, sweep=0.8), t0, 1.0)
    g = tts_fx(words, "chorus", 0.95, -5.0)
    bus.add(np.tanh(3.0 * g / (np.abs(g).max() + 1e-9)) * 0.5 * level, t0 + 0.1, 1.0)
    for k in range(int(dur / 0.17)):
        bus.add(O.hat(0.5 * level, seed=k, open_=k % 4 == 0), t0 + k * 0.17, 1.0, pan=0.6)


# ------------------------------------------------------------------ voices in the score

def tts_fx(text, voice, speed=1.0, pitch=0.0):
    w = chorus(text, speed) if voice == "chorus" else speak_fx(text, voice, speed)
    if abs(pitch) > 1e-3:
        r = 2 ** (pitch / 12)
        w = signal.resample(w, int(round(len(w) / r))).astype(np.float32)
    return signal.resample_poly(w.astype(np.float64), SR, VSR)


INVENTED = ["kelemai", "vorrin", "venti noh", "ahvenna", "miré sola", "tovéh", "anakré", "miravel"]


def whispers_inv(dur, amp=1.0, seed=0):
    """Breathy whispers of invented words, scattered left and right."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros((2, n))
    t = rng.uniform(0, 0.6)
    while t < dur - 0.6:
        w = INVENTED[int(rng.integers(len(INVENTED)))]
        v = speak_fx(w, ["am_onyx", "af_nicole", "bf_emma"][int(rng.integers(3))], 0.85, -2.0 + rng.uniform(-1, 1))
        y = signal.resample_poly(whisper(v, keep=0.05, seed=int(rng.integers(99))).astype(np.float64), SR, VSR)
        y = y / (np.sqrt((y ** 2).mean()) + 1e-9) * 0.05
        p = rng.uniform(0.1, 0.9)
        j = int(t * SR)
        m = min(len(y), n - j)
        out[0, j:j + m] += y[:m] * math.sqrt(1 - p)
        out[1, j:j + m] += y[:m] * math.sqrt(p)
        t += len(y) / SR + rng.uniform(0.3, 1.2)
    return amp * out


def growl_words(text, amp=1.0):
    """A low growl on invented words: a male voice pitched far down and driven."""
    g = tts_fx(text, "am_onyx", 0.8, -9.0)
    g = np.tanh(4 * g / (np.abs(g).max() + 1e-9))
    return amp * _lp(g, 2200) * 0.4


# ------------------------------------------------------------------ stings

def screech(dur=0.9, amp=1.0, seed=0):
    """A violin screech: a bowed, gritty high note sliding."""
    t = tx(dur)
    f = 2400 * (1 + 0.12 * t / dur) * (1 + 0.02 * np.sin(2 * np.pi * 9 * t))
    ph = np.cumsum(f) / SR
    x = sum(np.sin(2 * np.pi * k * ph) / k for k in range(1, 7))
    x = x * (1 + 0.6 * _noise(len(t), seed) * 0.3)
    return amp * np.tanh(2 * x) * np.clip(t / 0.01, 0, 1) * np.exp(-t / (dur * 0.6)) * 0.22


def sting(amp=1.0, seed=0):
    out = np.zeros(int(2.6 * SR))
    s = O.scare(1.0, seed=seed, body=1.1, drive=2.0)
    out[:len(s)] += s
    sc = screech(0.9, 0.8, seed)
    out[:len(sc)] += sc
    return amp * out


# ------------------------------------------------------------------ foley

def breath(dur=1.6, amp=1.0, seed=0, shaky=0.0):
    """Breathing close to the mic: an inhale, an exhale."""
    t = tx(dur)
    rng = np.random.default_rng(seed)
    nz = rng.normal(0, 1, len(t))
    inh = np.clip(t / (dur * 0.4), 0, 1) * (t < dur * 0.45)
    exh = np.sin(np.pi * np.clip((t - dur * 0.5) / (dur * 0.5), 0, 1)) * (t >= dur * 0.5)
    e = inh ** 1.5 * 0.7 + exh
    e *= 1 + shaky * 0.5 * np.sin(2 * np.pi * 9 * t)
    x = _bp(nz, 500, 2600) * 0.7 + _bp(nz, 2600, 6000) * 0.3
    return amp * x * e * 0.12


def footstep(amp=1.0, seed=0, wet=False):
    t = tx(0.35)
    rng = np.random.default_rng(seed)
    x = np.sin(2 * np.pi * (70 + 40 * np.exp(-t / 0.02)) * t) * np.exp(-t / 0.05)
    x += _bp(rng.normal(0, 1, len(t)), 300, 2500) * np.exp(-t / 0.03) * 0.5
    if wet:
        x += _bp(rng.normal(0, 1, len(t)), 2000, 8000) * np.exp(-t / 0.08) * 0.4
    return amp * x * 0.5


def board_creak(amp=1.0, seed=0):
    t = tx(0.6)
    rng = np.random.default_rng(seed)
    f = 180 + 60 * np.sin(2 * np.pi * 1.2 * t) + rng.uniform(-20, 20)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (0.5 + 0.5 * np.sin(2 * np.pi * 31 * t))
    return amp * _bp(x, 200, 1400) * np.sin(np.pi * t / 0.6) * 0.18


def tick(amp=1.0, tock=False):
    return O.tick(amp, tock)


def desk_bell(amp=1.0):
    t = tx(2.5)
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / d) * g for f, d, g in ((2100, 1.2, 1.0), (5300, 0.5, 0.4), (7800, 0.2, 0.2)))
    return amp * x * 0.25


def keys_jingle(amp=1.0, seed=0):
    rng = np.random.default_rng(seed)
    out = np.zeros(int(0.8 * SR))
    for k in range(7):
        t = tx(0.3)
        f = rng.uniform(3000, 7000)
        x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.06)
        j = int(rng.uniform(0, 0.4) * SR)
        out[j:j + len(x)] += x
    return amp * out * 0.12


def lock_click(amp=1.0, seed=0):
    t = tx(0.15)
    x = _bp(_noise(len(t), seed), 1500, 6000) * np.exp(-t / 0.008)
    x2 = _bp(_noise(len(t), seed + 1), 800, 3000) * np.exp(-np.maximum(0, t - 0.04) / 0.01) * (t > 0.04)
    return amp * (x + 0.7 * x2) * 0.6


def tap(amp=1.0, seed=0):
    t = tx(0.05)
    return amp * _bp(_noise(len(t), seed), 1500, 5000) * np.exp(-t / 0.006) * 0.25


def notify(amp=1.0):
    """The assistant's reply: a soft, too-pleasant two-note chime."""
    out = np.zeros(int(1.4 * SR))
    for k, m in enumerate((88, 93)):
        y = O.celesta(m, 0.8, dur=1.0)
        j = int(k * 0.11 * SR)
        out[j:j + len(y)] += y
    return amp * out


def dtmf(digit, dur=0.18, amp=1.0):
    lo = {"1": 697, "9": 852}[digit]
    hi = {"1": 1209, "9": 1477}[digit]
    t = tx(dur)
    return amp * (np.sin(2 * np.pi * lo * t) + np.sin(2 * np.pi * hi * t)) * 0.12


def ringback(dur=2.0, amp=1.0):
    t = tx(dur)
    on = ((t % 3.0) < 1.0)
    return amp * (np.sin(2 * np.pi * 440 * t) + np.sin(2 * np.pi * 480 * t)) * on * 0.06


def neon_buzz(dur, amp=1.0, flicker=0.0):
    t = tx(dur)
    x = np.sign(np.sin(2 * np.pi * 120 * t)) * 0.4 + 0.3 * np.sin(2 * np.pi * 240 * t)
    if flicker > 0:
        x *= (np.sin(2 * np.pi * 17 * t) > -0.2 * flicker)
    return amp * _bp(x, 100, 3000) * 0.05


def glass_crack(amp=1.0, seed=0):
    rng = np.random.default_rng(seed)
    t = tx(0.9)
    x = _bp(rng.normal(0, 1, len(t)), 2500, 9000) * (np.abs(rng.normal(0, 1, len(t))) > 1.6) * np.exp(-t / 0.2)
    x += _bp(rng.normal(0, 1, len(t)), 400, 2000) * np.exp(-t / 0.02) * 0.8
    return amp * x * 0.6


def coin(amp=1.0, seed=0):
    rng = np.random.default_rng(seed)
    t = tx(0.5)
    f = rng.uniform(2800, 4200)
    x = (np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 2.7 * t)) * np.exp(-t / 0.12)
    return amp * x * 0.12


def tape_rewind(dur=2.0, amp=1.0):
    """A reel spooling back: a rising, fluttering chirp with hiss."""
    t = tx(dur)
    f = 300 + 2600 * (t / dur) ** 1.5
    x = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.3 * np.sin(2 * np.pi * 23 * t))) / SR) * 0.4
    x += _hp(_noise(len(t), 4), 3000) * 0.2
    return amp * x * np.clip(t / 0.1, 0, 1) * np.clip((dur - t) / 0.08, 0, 1) * 0.5


def monitor_beep(amp=1.0):
    t = tx(0.12)
    return amp * np.sin(2 * np.pi * 1000 * t) * np.clip(t / 0.005, 0, 1) * np.clip((0.12 - t) / 0.02, 0, 1) * 0.1


def wind(dur, amp=1.0, seed=3):
    t = tx(dur)
    x = _bp(_noise(len(t), seed), 200, 900) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t + 1)) ** 2
    return amp * x * 0.25


def shepard(dur, amp=1.0, up=True):
    """A rising tone that never arrives: the paradox building."""
    t = tx(dur)
    out = np.zeros(len(t))
    for k in range(6):
        u = (k / 6 + (t / 8.0 if up else -t / 8.0)) % 1.0
        f = 55 * 2 ** (u * 6)
        g = np.sin(np.pi * u) ** 2
        out += g * np.sin(2 * np.pi * np.cumsum(f) / SR)
    return amp * out * np.clip(t / 0.5, 0, 1) * np.clip((dur - t) / 0.3, 0, 1) * 0.08
