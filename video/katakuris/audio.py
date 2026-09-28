"""Soundtrack: a Japanese horror-comedy musical. Writes build/audio.wav (48 kHz stereo).

Beds (read off the edit):
  horror   the cold open: drone, thunder, clay squelches
  sitcom   a bright kayokyoku lounge bed under the family (organ, twang guitar, bass, brushes, glock)
  songs    s1 kayokyoku sing-along, s2 dream duet, s3 disco, s4 showtune finale - karaoke instrumentals with an
           'ahh / la-la' choir and a guide melody that follows the narrator's half-spoken words
  reprise  the s1 tune keeps playing, cheerfully, straight through the horror (warped a little, under a drone)
  enka     the letter chapter: tremolo strings, shakuhachi, shamisen, a slow sob of a groove
  disaster the sitcom bed keeps smiling under the four disasters, with a drone and the effects
Every transition and every scare gets a hit; scare hits go on their own band-limited bus, hot; the music drops away
under them. True dead air (every bus cut) three times. The crow caws whenever a small error becomes a big one.
"""
import os
import wave

import numpy as np
from scipy import signal

import kayo as P
from cues import C, ls
from edit import EDIT, HIT_CUTS, first
from script import MACH, MAMA, NAR, SONGS
from timeline import TL
from voice import SR as VSR

SR = P.SR
HERE = os.path.dirname(os.path.abspath(__file__))
N = int((TL.total + 0.6) * SR)
S, E, W = TL.s, TL.e, TL.word


def wide(fn, *a, seed=0, **k):
    """A stereo take of a noisy effect: an independent performance on each side (wide, and still mono-safe)."""
    return np.stack([fn(*a, seed=seed, **k), fn(*a, seed=seed + 101, **k)])


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


# ------------------------------------------------------------------ harmony

def chord(root, kind):
    iv = {"maj": (0, 4, 7), "min": (0, 3, 7), "maj7": (0, 4, 7, 11), "min7": (0, 3, 7, 10), "7": (0, 4, 7, 10)}[kind]
    return [root + i for i in iv]


PROG = {
    "kayo": [(65, "maj"), (62, "min"), (58, "maj"), (60, "7")],            # F  Dm  Bb  C7
    "sitcom": [(65, "maj7"), (62, "min7"), (67, "min7"), (60, "7")],        # Fmaj7 Dm7 Gm7 C7
    "enka": [(62, "min"), (67, "min"), (69, "7"), (62, "min")],             # Dm  Gm  A7  Dm
    "duet": [(58, "maj7"), (67, "min7"), (63, "maj7"), (65, "7")],          # Bbmaj7 Gm7 Ebmaj7 F7
    "disco": [(69, "min7"), (62, "min7"), (67, "maj"), (60, "maj7")],       # Am7 Dm7 G Cmaj7
    "show": [(60, "maj"), (69, "min"), (65, "maj"), (67, "7")],            # C  Am  F  G7
}
SCALE = {"kayo": [65, 67, 69, 72, 74], "sitcom": [65, 67, 69, 72, 74], "enka": [62, 64, 65, 69, 70],
         "duet": [70, 72, 74, 77, 79], "disco": [69, 72, 74, 76, 79], "show": [72, 74, 76, 79, 81]}


def band(bus, lead, choir, style, t0, t1, bpm, level=1.0, drums=True, song=None):
    """Play `style` in strict time from t0 to t1."""
    beat = 60.0 / bpm
    prog = PROG[style]
    nb = int((t1 - t0) / beat)
    rng = np.random.default_rng(int(t0 * 10))
    for b in range(nb):
        t = t0 + b * beat
        bar, bb = divmod(b, 4)
        root, kind = prog[bar % 4]
        ch = chord(root, kind)
        lo = [m - 12 for m in ch]
        if style in ("kayo", "sitcom"):
            if drums:
                if bb in (0, 2):
                    bus.add(P.kick(0.85, seed=b), t, 0.7 * level)
                if bb in (1, 3):
                    bus.add(P.snare(0.6, seed=b), t, 0.35 * level, pan=0.55)
                for h in (0, 0.5):
                    bus.add(P.hat(0.8 if h == 0 else 0.5, seed=b), t + h * beat, 0.22 * level, pan=0.3)
                if style == "kayo" and bb in (1, 3):
                    bus.add(P.tambourine(0.8, seed=b), t + 0.5 * beat, 0.25 * level, pan=0.75)
            bus.add(P.bass(root - 24 + (7 if bb in (1, 3) else 0), beat * 0.8), t, 0.55 * level)
            for k in range(2):
                bus.add(P.twang(ch[(bb * 2 + k) % len(ch)], beat * 0.45, seed=b * 2 + k), t + k * beat / 2, 0.32 * level,
                        pan=0.15 if k else 0.85)
            if bb == 0:
                bus.add(P.organ(lo, beat * 4 * 0.95), t, 0.5 * level, pan=0.45)
                bus.add(P.strings(ch, beat * 4, 1.0, seed=bar), t, 0.45 * level)
            if style == "kayo" and bb == 0 and bar % 2 == 0:
                bus.add(P.brass(ch, beat * 0.4, seed=bar), t, 0.9 * level, pan=0.6)
            if style == "sitcom" and bb == 2 and bar % 2 == 1:
                bus.add(P.glock(ch[-1] + 12, 0.8), t, 0.25 * level, pan=0.65)
        elif style == "enka":
            if bb in (0, 2):
                bus.add(P.bass(root - 24, beat * 1.6), t, 0.5 * level)
                bus.add(P.shamisen(ch[0], seed=b), t, 0.28 * level, pan=0.3)
            if drums and bb in (1, 3):
                bus.add(P.snare(0.25, seed=b), t, 0.18 * level, pan=0.55)
            for k in range(2):                                            # the guitar's lonely arpeggio
                bus.add(P.twang(ch[(bb * 2 + k) % len(ch)] - 12, beat * 0.5, seed=b * 3 + k, trem=False), t + k * beat / 2,
                        0.22 * level, pan=0.65)
            if bb == 0:
                s = P.strings(ch, beat * 4, 1.0, seed=bar)
                s = s * (1 + 0.5 * np.sin(2 * np.pi * 7.5 * np.arange(len(s)) / SR))   # tremolo bows
                bus.add(s, t, 0.7 * level)
            if bb == 0 and bar % 2 == 0:                                    # the shakuhachi phrase
                sc = SCALE["enka"]
                ph = [sc[4], sc[3], sc[2], sc[3]] if bar % 4 == 0 else [sc[3], sc[2], sc[1], sc[0]]
                for k, m in enumerate(ph):
                    lead.add(P.shakuhachi(m + 12, beat * (1.6 if k == 3 else 0.9), seed=bar + k), t + k * beat, 0.5 * level, pan=0.55)
        elif style == "duet":
            if drums:
                if bb == 0:
                    bus.add(P.kick(0.6, seed=b), t, 0.5 * level)
                if bb in (1, 3):
                    bus.add(P.snare(0.3, seed=b), t, 0.2 * level)
            bus.add(P.bass(root - 24, beat * 0.9), t, 0.45 * level)
            for k in range(4):
                bus.add(P.harp(ch[k % len(ch)] + (12 if k > 1 else 0)), t + k * beat / 4, 0.3 * level, pan=0.3 + 0.13 * k)
            if bb == 0:
                bus.add(P.strings(ch, beat * 4, 1.0, seed=bar), t, 0.7 * level)
                bus.add(P.epiano(ch, beat * 3, 0.9, seed=bar), t, 0.3 * level, pan=0.6)
                bus.add(P.glock(ch[-1] + 12, 0.8), t + beat * 2, 0.2 * level, pan=0.7)
        elif style == "disco":
            bus.add(P.kick(1.0, seed=b), t, 0.85 * level)
            bus.add(P.hat(0.9, seed=b, open_=True), t + beat / 2, 0.3 * level, pan=0.65)
            for q in (0.25, 0.75):
                bus.add(P.hat(0.5, seed=b + 7), t + q * beat, 0.15 * level, pan=0.35)
            if bb in (1, 3):
                bus.add(P.clap(1.0, seed=b), t, 0.5 * level, pan=0.5)
            for h in (0, 0.5):
                bus.add(P.bass(root - 24 + (12 if h else 0), beat * 0.42), t + h * beat, 0.6 * level)
            bus.add(P.clav([ch[(bb + 1) % len(ch)], ch[(bb + 2) % len(ch)]], beat * 0.2, seed=b), t + 0.25 * beat, 0.4 * level, pan=0.7)
            if bb == 1:
                bus.add(P.strings(ch, beat * 0.3, 1.0, seed=bar), t + 0.5 * beat, 1.1 * level, pan=0.4)
            if bb == 0:
                bus.add(P.brass(ch, beat * 0.3, seed=bar), t, 0.9 * level, pan=0.55)
                bus.add(P.strings([m + 12 for m in ch], beat * 4, 1.0, seed=bar + 3), t, 0.35 * level)
        elif style == "show":
            if bb == 0:
                bus.add(P.timpani(root - 24, 1.0), t, 0.6 * level)
                if bar % 2 == 0:
                    bus.add(P.cymbal(0.9, 1.5), t, 0.5 * level, pan=0.6)
            bus.add(P.bass(root - 24 + (7 if bb % 2 else 0), beat * 0.6), t, 0.5 * level)
            bus.add(P.snare(0.5 if bb % 2 else 0.3, seed=b), t, 0.25 * level)
            if bb in (1, 3):
                bus.add(P.piano(ch, beat * 0.4, 0.9, seed=b), t, 0.5 * level, pan=0.4)
                bus.add(P.brass(ch, beat * 0.35, seed=b, bright=1.2), t + beat * 0.5, 0.8 * level, pan=0.65)
            if bb == 0:
                bus.add(P.strings([m + 12 for m in ch], beat * 4, 1.0, seed=bar), t, 0.6 * level)
        if choir is not None and bb == 0 and style in ("kayo", "duet", "disco", "show"):   # 'ahh' pads on each bar
            v = "a" if style != "disco" else "o"
            for k, m in enumerate(ch[1:3]):
                choir.add(P.voices(v, m, beat * 3.6, 0.8, seed=bar + k), t, 0.16 * level, pan=0.08 + 0.84 * k)


def la_la(choir, t, beat, style, n=4):
    """A 'la-la-la' pickup from the backing singers."""
    sc = SCALE[style]
    for k in range(n):
        choir.add(P.voices("a", sc[(k * 2) % len(sc)], beat * 0.4, 0.9, seed=k), t + k * beat / 2, 0.22, pan=0.1 + 0.27 * k)


def guide(lead, key, style):
    """The guide melody: one note per word of her half-spoken lyric, riding the song's pentatonic scale."""
    L = TL.lines[key]
    sc = SCALE[style]
    words = L["words"]
    n = len(words)
    idx = int(key.split("_")[1])
    timbre = {"kayo": "whistle", "duet": "flute", "disco": "synth", "show": "trumpet"}[style]
    for i, (w, a, b) in enumerate(words):
        u = i / max(1, n - 1)
        arc = np.sin(np.pi * u) * (3 if idx % 2 == 0 else 2)
        step = int(round(arc)) + (idx % 2)
        m = sc[min(len(sc) - 1, max(0, step))] + (12 if style == "disco" else 0)
        if i == n - 1:
            m = sc[0] if idx % 2 else sc[2]
        lead.add(P.lead(m, max(0.12, b - a) * 0.95, timbre, seed=i), a, 0.5, pan=0.5)


# ------------------------------------------------------------------ the arrangement

SONG_STYLE = {"s1": "kayo", "s2": "duet", "s3": "disco", "s4": "show"}
KAYO_THEME = [(77, 1), (79, 1), (81, 2), (84, 1), (81, 1), (79, 2), (77, 1), (74, 1), (77, 2), (72, 1), (74, 1), (77, 3)]


def dead_air():
    """True silence: every bus cut (only a voice may speak; here none does)."""
    return [(E("d4b") + 0.22, first("michigan") - 0.03),
            (E("s2") + 0.34, C["erupt"] - 0.03),
            (E("f2") + 0.22, S("f3") - 0.4)]


def arrangement(bus, lead, choir, hz):
    f = first
    # the cold open: horror
    hz.add(P.drone(f("card1") + 0.5, root=29, seed=1), 0.0, 0.8)
    # the sitcom bed under the family, up to the first song
    band(bus, None, None, "sitcom", f("family"), S("s1") - 0.02, 112, 0.7)
    # the songs
    for sk, st in SONG_STYLE.items():
        Sg = TL.songs[sk]
        band(bus, lead, choir, st, Sg["start"], Sg["end"] + (0.0 if sk != "s4" else 0.0), Sg["bpm"], 1.0)
        for l in Sg["lines"]:
            guide(lead, l["key"], st)
        la_la(choir, Sg["start"] + Sg["beat"] * max(0, SONGS[sk]["intro"] - 2), Sg["beat"], st)
        la_la(choir, Sg["end"] - Sg["beat"] * 2, Sg["beat"], st)
    # the s1 tune keeps playing, cheerfully, through the horror that follows it
    band(bus, None, choir, "kayo", E("s1"), f("card3"), TL.songs["s1"]["bpm"], 0.75)
    hz.add(P.drone(f("card3") - E("s1") + 0.5, root=31, seed=2), E("s1"), 0.7)
    # the enka ballad under the letter (it stops dead for the silence)
    band(bus, lead, None, "enka", f("job"), f("card4"), 70, 0.9)
    hz.add(P.drone(f("card4") - f("michigan"), root=26, seed=3), f("michigan"), 0.5)
    # the volcano: silence, then the earth itself
    hz.add(wide(P.rumble, S("s3") - C["erupt"], seed=4), C["erupt"], 1.0)
    # the sitcom bed again for the shrug; then it keeps smiling under the disasters
    band(bus, None, None, "sitcom", f("ads"), f("one"), 112, 0.65)
    band(bus, None, None, "sitcom", f("plane"), f("card6"), 112, 0.5, drums=True)
    hz.add(P.drone(f("card6") - f("plane"), root=28, seed=5), f("plane"), 0.8)
    # the build into the finale
    bus.add(P.snare_roll(S("s4") - f("rule2") - 0.1, 0.8), f("rule2") + 0.1, 0.5)
    bus.add(P.cymbal(1.0, S("s4") - f("rule2"), swell=True), f("rule2"), 0.6)
    # the payoff and the end
    hz.add(wide(P.rumble, f("end") - E("s4"), seed=6), E("s4"), 1.0)
    # the end card: the sing-along tune on a music box, slowing and sagging out of tune
    bus.add(P.music_box(KAYO_THEME, rate=lambda u: 1 - 0.55 * u, detune=lambda u: -90 * u * u, amp=1.0, seed=3),
            f("end") + 0.15, 0.55, pan=0.5)


def sfx(fx, hits):
    f = first
    jingle_kind = {"card3": "sad", "card6": "finale"}
    for i, (t, name, tr) in enumerate(EDIT[1:], 1):
        if tr == "card":
            fx.add(P.jingle(jingle_kind.get(name, "happy")), t, 0.55)
        elif tr == "star":
            fx.add(P.sparkle(1.0, seed=i), t - 0.05, 0.45, pan=0.6)
        elif tr == "spin":
            fx.add(P.whoosh(0.5, True, seed=i), t - 0.05, 0.55)
        elif tr == "flash":
            hits.append((t + 0.01, 1.0, 1.0, i))
        elif name.startswith("duet_"):                                  # cuts inside the dream: a harp glint
            for k in range(4):
                fx.add(P.harp(79 + [0, 4, 7, 12][k]), t - 0.02 + k * 0.04, 0.25, pan=0.35 + 0.1 * k)
        elif name in HIT_CUTS:
            hits.append((t, 0.9, 0.9, 40 + i))
            fx.add(P.squelch(1.0, seed=40 + i, dur=0.3), t + 0.03, 0.35)
        else:
            fx.add(P.pop(1.0), t, 0.3)
            fx.add(P.woodblock(0.8, 900 + 70 * (i % 5)), t, 0.28, pan=0.4 + 0.04 * (i % 5))
    # cold open
    hits.append((0.02, 1.0, 1.1, 1))
    fx.add(wide(P.thunder, 3.0, seed=1), 0.1, 0.55)
    for k in range(18):
        fx.add(P.squelch(0.7, seed=k, dur=0.2), 0.3 + k * 0.2, 0.16, pan=0.2 + 0.6 * ((k * 7) % 10) / 10)
    fx.add(P.boing(1.0), C["pop"], 0.45)
    fx.add(P.squelch(1.2, seed=40), C["pop"] + 0.02, 0.55)
    fx.add(P.crow(1.0, seed=1), C["pop"] + 0.6, 0.5, pan=0.3)
    # the family
    fx.add(P.crow(1.0, seed=2), C["dontask"] + 0.35, 0.55, pan=0.7)
    fx.add(P.stamp(1.3), C["stamp"], 0.8)
    fx.add(P.honk(1.0, 1), C["stamp"] + 0.25, 0.35, pan=0.6)
    fx.add(P.slide_whistle(False, 0.5), f("bow") + 0.05, 0.4)
    fx.add(P.sparkle(1.0, seed=3), C["tuesday"] - 0.05, 0.4)
    fx.add(P.clock_bell(1.0, 74), f("machine") + 0.8, 0.25)
    for k in range(4):
        fx.add(P.glock(96 + k, 0.8), f("machine") + 1.0 + k * 0.12, 0.2, pan=0.6)
    # song 1: the machine stamps on the beat
    s1 = TL.songs["s1"]
    for b in range(int((s1["end"] - ls("s1_1") + 0.1) / s1["beat"])):
        fx.add(P.stamp(0.6), ls("s1_1") - 0.1 + b * s1["beat"], 0.22, pan=0.65)
    # the flood
    fx.add(wide(P.thunder, 3.5, seed=2), f("flood") + 0.1, 0.8)
    for k in range(28):
        fx.add(P.squelch(0.8, seed=100 + k, dur=0.25), f("flood") + 0.2 + k * 0.14, 0.3, pan=0.15 + 0.7 * ((k * 3) % 10) / 10)
    hits.append((C["millions"], 0.9, 1.0, 5))
    fx.add(P.crow(1.0, seed=3), f("graves") + 0.3, 0.55, pan=0.5)
    fx.add(P.sparkle(1.0, seed=5), C["rule_right"] - 0.2, 0.5)
    fx.add(P.squelch(1.4, seed=7, dur=0.5), C["rule_wrong"] - 0.15, 0.7)
    fx.add(P.slide_whistle(False, 0.7), C["rule_wrong"] - 0.1, 0.35)
    tt, k = f("same") + 0.1, 0
    while tt < f("card3") - 0.2:                                        # the conveyor stamps, faster and faster
        fx.add(P.stamp(0.8), tt, 0.35, pan=0.6)
        fx.add(P.squelch(0.6, seed=200 + k, dur=0.18), tt + 0.02, 0.25, pan=0.6)
        tt += max(0.18, 0.62 - (tt - f("same")) * 0.07)
        k += 1
    fx.add(P.slide_whistle(True, 0.4), W("b4", "same") - 0.1, 0.3)
    # chapter 3: rain, typing, the letter
    nr = int((f("wrong") - f("job")) * SR)
    rain = np.stack([P._bp(P._noise(nr, 9), 1500, 9000), P._bp(P._noise(nr, 19), 1500, 9000)]) * 0.12
    fx.add(rain, f("job"), 0.8)
    fx.add(P.keys(14, 0.07, seed=4), W("d1", "file"), 0.45)
    fx.add(P.page(1.0, seed=2), f("letter") + 0.9, 0.5)
    fx.add(P.crow(1.0, seed=4), C["fraud_letter"] + 0.1, 0.5, pan=0.75)
    hits.append((C["no_human"], 0.8, 0.7, 7))
    fx.add(P.squelch(1.0, seed=11), C["penalty"], 0.5)
    hits.append((C["penalty"], 0.8, 0.6, 8))
    for k in range(6):
        fx.add(P.squelch(0.7, seed=20 + k, dur=0.18), C["interest"] + k * 0.12, 0.3)
    for tk in (W("d4", "wages.") - 0.3, C["refund"] - 0.1):
        fx.add(P.whoosh(0.35, False, seed=3), tk, 0.4)
        fx.add(P.squelch(1.2, seed=30, dur=0.4), tk + 0.3, 0.6)
        fx.add(P.whoosh(0.4, True, seed=4), tk + 0.45, 0.4)
    for k in range(20):
        fx.add(P.squelch(0.6, seed=300 + k, dur=0.2), f("michigan") + 0.3 + k * 0.2, 0.2, pan=0.3 + 0.4 * (k % 3) / 2)
    hits.append((C["forty"], 0.9, 0.9, 9))
    fx.add(P.stamp(1.6), C["eightyfive"], 0.9)
    hits.append((C["eightyfive"], 0.9, 0.9, 10))
    fx.add(wide(P.rumble, 1.6, seed=7), f("homes") + 0.2, 0.6)
    for k in range(5):
        fx.add(P.squelch(0.9, seed=400 + k, dur=0.35), f("homes") + 0.3 + k * 0.14, 0.35)
    hits.append((C["robodebt"], 0.9, 0.8, 11))
    # the duet
    for k in range(8):
        fx.add(P.harp(70 + [0, 4, 7, 11, 14, 17, 21, 24][k]), f("duet") - 0.1 + k * 0.05, 0.3, pan=0.3 + 0.05 * k)
    # the volcano: the duet is scratched off the record, dead air, then the mountain blows (the big sting)
    fx.add(P.scratch(0.32, seed=2), E("s2") - 0.02, 0.9)
    hits.append((C["erupt"], 1.5, 1.6, 12))
    fx.add(wide(P.thunder, 5.0, seed=5), C["erupt"] + 0.02, 1.2)
    fx.add(wide(P.rumble, 3.0, seed=15), C["erupt"], 1.2)                 # the ground itself, under the sting
    fx.add(P.timpani(36, 1.0), C["erupt"], 0.8)
    fx.add(P.cymbal(1.0, 3.0), C["erupt"] + 0.02, 0.6)
    fx.add(P.growl(2.0), C["erupt"] + 0.1, 0.5)
    for k in range(24):
        fx.add(P.squelch(0.8, seed=500 + k, dur=0.25), C["erupt"] + 0.2 + k * 0.15, 0.3, pan=0.2 + 0.6 * ((k * 7) % 10) / 10)
    hits.append((C["point"], 0.8, 0.6, 13))
    hits.append((C["onemil"], 1.0, 1.0, 14))
    # the disco: the dead climb out on the beat
    s3 = TL.songs["s3"]
    for k in range(4):
        fx.add(P.squelch(1.2, seed=600 + k, dur=0.4), s3["start"] + 0.4 + k * 0.5, 0.5, pan=0.2 + 0.2 * k)
    fx.add(P.growl(1.8), s3["start"] + 0.3, 0.4)
    fx.add(P.crow(1.0, seed=6), s3["end"] - 0.6, 0.4, pan=0.8)
    # chapter 5
    ad = [(84, 0.12), (88, 0.12), (91, 0.12), (96, 0.3)]
    for k, (m, d) in enumerate(ad):
        fx.add(P.glock(m, 0.9), f("ads") + 0.4 + k * 0.13, 0.3, pan=0.35)
    fx.add(P.slide_whistle(False, 0.5), W("f1", "shrug.") - 0.25, 0.4)
    fx.add(P.glock(100, 1.0), f("translate") + 0.3, 0.3)
    hits.append((C["attack"], 1.0, 0.8, 15))
    fx.add(P.siren(2.2), C["arrested"] - 0.1, 0.45)
    fx.add(P.squelch(1.3, seed=700, dur=0.5), f("one") + 0.05, 0.6)
    # the four disasters
    fx.add(P.dive(C["impact_plane"] - C["nose"] + 1.0), C["nose"] - 1.0, 0.42)
    t_push = C["nose"] - 1.0
    for k in range(int((C["impact_plane"] - t_push) / 0.55) + 1):
        fx.add(P.stamp(0.8), t_push + k * 0.55, 0.2)
    fx.add(P.alarm_bell(C["alarms"] - f("grid") - 0.2), f("grid") + 0.1, 0.4)
    fx.add(P.power_down(1.8), C["alarms"] + 0.1, 0.8)
    for k in range(9):
        fx.add(P.woodblock(0.8, 300), C["alarms"] + 0.25 + k * 0.12, 0.25, pan=0.1 + 0.1 * k)
    for k in range(int((f("radiation") - f("missile")) / 0.5)):
        fx.add(P.tick(1.0, tock=k % 2 == 1), f("missile") + k * 0.5, 0.5)
    fx.add(P.whoosh(1.4, False, seed=8), f("missile") + 0.3, 0.5, pan=0.8)
    fx.add(P.whoosh(1.0, True, seed=9), f("missile") + 1.3, 0.5, pan=0.4)
    fx.add(P.geiger(f("card6") - f("radiation"), rate=20), f("radiation"), 0.35)
    for k in range(6):
        fx.add(P.squelch(0.8, seed=800 + k, dur=0.2), C["p6"] + k * 0.12, 0.35, pan=0.15 + 0.14 * k)
    for key, i in (("p50", 17), ("p6", 19)):
        hits.append((C[key], 1.0, 1.0, i))
    for key, i in (("impact_plane", 20), ("impact_missile", 21)):              # the crashes land between words
        hits.append((C[key], 1.3, 0.9, i))
        fx.add(wide(P.thunder, 1.6, seed=i), C[key] + 0.02, 0.7)
        for k in range(8):
            fx.add(P.squelch(1.0, seed=1000 + i * 10 + k, dur=0.3), C[key] + 0.05 + k * 0.08, 0.35, pan=0.1 + 0.1 * k)
    fx.add(P.geiger(1.2, rate=90, seed=9), C["p6"], 0.5)
    # the rule
    for k, key in enumerate(("scale", "stakes", "smaller")):
        fx.add(P.woodblock(1.0, 600 + 150 * k), C[key] - 0.2, 0.45)
    # the finale
    s4 = TL.songs["s4"]
    t_press = ls("s4_3") + 0.7
    for k in range(6):
        fx.add(P.pop(1.0), s4["start"] + 0.6 + k * 0.9, 0.3, pan=0.2 + 0.12 * k)
    fx.add(P.stamp(1.6), t_press, 0.55)
    fx.add(P.power_down(1.2), t_press + 0.05, 0.4)
    fx.add(P.cymbal(1.0, 2.0), t_press + 0.1, 0.3)
    fx.add(P.applause(3.0), s4["end"] - 1.5, 0.35)
    # the payoff
    fx.add(P.growl(2.5), f("payoff") + 0.2, 0.7)
    fx.add(wide(P.thunder, 3.0, seed=7), f("payoff") + 0.1, 0.6)
    fx.add(P.crow(1.0, seed=8), f("payoff") + 1.1, 0.6, pan=0.75)
    # the end
    fx.add(P.applause(2.5), f("end") + 0.3, 0.3)
    fx.add(P.squelch(1.0, seed=900), f("end") + 1.6, 0.4)


# ------------------------------------------------------------------ voices

def robot(x):
    """The machine's voice: a metallic comb, a faint ring-modulation buzz."""
    d = int(0.0045 * SR)
    y = x.copy()
    for i in range(2):
        y[d:] += 0.4 * y[:-d]
    t = np.arange(len(x)) / SR
    return 0.45 * y / (np.max(np.abs(y)) + 1e-9) * np.max(np.abs(x)) + 0.55 * x + 0.12 * x * np.sin(2 * np.pi * 55 * t)


def voices():
    out = np.zeros((2, N))
    for key in TL.order:
        L = TL.lines[key]
        a = L["wav"].astype(np.float64)
        who = L["who"]
        up = signal.resample_poly(a, SR, VSR)
        r = np.sqrt((up ** 2).mean()) + 1e-12
        lvl = {NAR: -17.0, MAMA: -15.5, MACH: -13.5}[who] + (2.2 if L["song"] else 0.0)
        up = up * db(lvl) / r
        up = limit(up[None], db(lvl + 8.5), look=0.003, rel=0.06)[0]         # broadcast-style peak control on the voice
        if who == MACH:
            up = robot(up)
        sig = np.stack([up, up])
        echo = who == MACH or key in ("b2", "g2")
        if echo:                                                   # a slapback echo that trails off
            tail = np.zeros((2, int(1.0 * SR)))
            sig = np.concatenate([sig, tail], axis=1)
            taps = ((0.22, 0.2), (0.44, 0.1), (0.66, 0.05)) if who == MACH else ((0.22, 0.35), (0.44, 0.18), (0.66, 0.09))
            for k, (dl, g) in enumerate(taps):
                o = int(dl * SR)
                sig[k % 2, o:] += sig[0, :-o] * g
        if who == MAMA:
            sig = sig * np.array([[1.08], [0.92]])
        if who == MACH:
            sig = sig * np.array([[0.92], [1.08]])
        i = int(L["start"] * SR)
        j = min(N, i + sig.shape[1])
        out[:, i:j] += sig[:, : j - i]
    return out


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
    side = side + amt * signal.lfilter(*signal.butter(2, 200 / (SR / 2), "high"), d)
    return np.stack([mid + side, mid - side])


def mono_safe(x, max_ratio=0.45, hop=1024):
    """Wide, but never phasey: wherever the side outweighs ~0.36 of the mid (L/R correlation under ~0.47), the side
    is pulled back, so a phone speaker summing to mono loses at most ~1.3 dB."""
    mid, side = 0.5 * (x[0] + x[1]), 0.5 * (x[0] - x[1])
    n = len(mid) // hop
    em = np.convolve((mid[: n * hop] ** 2).reshape(n, hop).mean(axis=1), np.ones(8) / 8, "same")
    es = np.convolve((side[: n * hop] ** 2).reshape(n, hop).mean(axis=1), np.ones(8) / 8, "same")
    g = np.minimum(1.0, np.sqrt(max_ratio * em / (es + 1e-12)))
    g = np.interp(np.arange(len(side)), np.arange(n) * hop + hop / 2, g)
    side = side * g
    return np.stack([mid + side, mid - side])


def reverb(x, wet=0.1, rt60=0.8, seed=8):
    rng = np.random.default_rng(seed)
    t = np.arange(int(rt60 * 1.4 * SR)) / SR
    ir = np.stack([rng.normal(0, 1, len(t)) * np.exp(-6.9 * t / rt60) for _ in range(2)])
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    y = np.stack([signal.fftconvolve(x[c], ir[c])[: x.shape[1]] for c in range(2)])
    return x * (1 - wet) + y * wet


def warp(x, depth_ms=8.0, rate=0.5):
    n = x.shape[1]
    t = np.arange(n) / SR
    d = (depth_ms / 1000 * SR) * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t) + 0.15 * np.sin(2 * np.pi * 5.3 * t))
    idx = np.arange(n) - d
    i0 = np.clip(np.floor(idx).astype(int), 0, n - 1)
    fr = idx - np.floor(idx)
    i1 = np.clip(i0 + 1, 0, n - 1)
    return x[:, i0] * (1 - fr) + x[:, i1] * fr


def next_word(t):
    return min([a for k in TL.order for w, a, b in TL.lines[k]["words"] if a > t - 0.02] or [TL.total])


def hit_signal(gain, body, seed, t):
    """A scare hit: dense and loud but band-limited (no codec overshoot). Every hit sits in a pause between words;
    when the next word is close, the tail is short so it never sits on her voice."""
    g = 6.0 * gain
    b = body if next_word(t) - t > 0.9 or body > 1.5 else 0.45
    x = P.scare(1.0, seed=seed, body=b, drive=3.2)
    n = int(0.16 * SR)                                                  # the slam itself: a dense, clipped low boom
    tt = np.arange(n) / SR
    slam = np.tanh(6.0 * (np.sin(2 * np.pi * np.cumsum(62 + 90 * np.exp(-tt / 0.03)) / SR)
                          + 0.6 * np.random.default_rng(seed).normal(0, 1, n))) * np.clip((0.16 - tt) / 0.06, 0, 1)
    x[:n] = np.tanh(2.0 * (x[:n] + 0.8 * slam))
    x = signal.sosfilt(signal.butter(4, 7000 / (SR / 2), "low", output="sos"), x)
    x = signal.sosfilt(signal.butter(2, 22 / (SR / 2), "high", output="sos"), x)
    x = np.tanh(2.5 * x) / np.tanh(2.5)                                 # squeezed dense: loud for its whole first 50 ms
    x = signal.sosfilt(signal.butter(4, 6000 / (SR / 2), "low", output="sos"), x)   # band-limited again: no codec overshoot
    x[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    return x * g * 1.7


def build():
    band_bus, lead_bus, choir_bus, fx, hz, hb = Bus(), Bus(), Bus(), Bus(), Bus(), Bus()
    arrangement(band_bus, lead_bus, choir_bus, hz)
    hits = []
    sfx(fx, hits)
    for t, gain, body, seed in hits:
        hb.add(hit_signal(gain, body, seed, t), t, 1.0, pan=0.5)
    music = reverb(band_bus.x, 0.12, 0.9) + reverb(lead_bus.x, 0.2, 1.2) + reverb(choir_bus.x, 0.3, 1.6)
    # the s1 reprise under the horror: seasick and dulled
    mask = np.zeros(N)
    for a, b in ((E("s1"), first("card3")), (first("plane"), first("card6"))):
        mask[int(a * SR):int(b * SR)] = 1.0
    mask = np.convolve(mask, np.ones(SR // 10) / (SR // 10), "same")
    warped = signal.lfilter(*signal.butter(2, 2600 / (SR / 2), "low"), warp(music, 8.0, 0.45))
    music = music * (1 - mask) + warped * mask * 0.9
    # the band drops away under every scare hit, then creeps back
    duck = np.ones(N)
    for t, *_ in hits:
        p0 = int((t - 0.3) * SR)                                         # the suck-out: the band drops away just before
        duck[max(0, p0):max(0, int((t - 0.01) * SR))] *= np.linspace(1.0, 0.15, max(1, int((t - 0.01) * SR) - max(0, p0)))
        i0, i1 = int((t - 0.01) * SR), int((t + 0.45) * SR)
        duck[max(0, i0):min(N, i1)] *= 0.3
        rec = np.linspace(0.3, 1.0, int(0.5 * SR))
        j1 = min(N, i1 + len(rec))
        duck[i1:j1] *= rec[: j1 - i1]
    music = music * duck
    music = music + reverb(fx.x, 0.15, 1.0) + reverb(hz.x * duck, 0.3, 2.0)
    music = signal.lfilter(*signal.butter(2, 35 / (SR / 2), "high"), music)
    dead = np.ones(N)
    for a, b in dead_air():
        dead[int(a * SR):int(b * SR)] = 0.0
    dead = np.convolve(dead, np.ones(int(0.015 * SR)) / int(0.015 * SR), "same")
    music = music * dead

    vo = reverb(voices(), 0.06, 0.5)
    from scipy.ndimage import maximum_filter1d
    raw = np.convolve(np.abs(vo.mean(axis=0)), np.ones(SR // 20) / (SR // 20), mode="same")
    raw = np.clip(raw / (np.percentile(raw[raw > 1e-5], 80) + 1e-9), 0, 1)
    env = maximum_filter1d(raw, size=int(0.45 * SR), origin=-int(0.12 * SR))
    env = np.convolve(env, np.ones(SR // 12) / (SR // 12), mode="same")
    insong = np.zeros(N)
    for Sg in TL.songs.values():
        insong[int(Sg["start"] * SR):int(Sg["end"] * SR)] = 1.0
    insong = np.convolve(insong, np.ones(SR // 5) / (SR // 5), "same")
    talk = np.zeros(N)
    for key in TL.order:
        talk[int((TL.s(key) - 0.1) * SR): int((TL.e(key) + 0.12) * SR)] = 1.0
    r = int(0.12 * SR)
    swell = 1 + (db(4.0) - 1) * (1 - np.convolve(talk, np.ones(r) / r, mode="same")) * (1 - insong)
    music = music * swell
    low = signal.lfilter(*signal.butter(2, 280 / (SR / 2), "low"), music)
    high = signal.lfilter(*signal.butter(2, 4200 / (SR / 2), "high"), music)
    mid = music - low - high
    k_mid = 0.9 - 0.25 * insong                                          # sung lines carve a little less
    music = low * (1 - 0.4 * env) + mid * (1 - k_mid * env) + high * (1 - 0.6 * env)
    duck = np.zeros(N)                                                   # ...but under every sung line the band steps back:
    for sk, dd in (("s1", -3.0), ("s2", -8.0), ("s3", -3.0), ("s4", -3.5)):   # the duet furthest, so the machine is heard
        for l in TL.songs[sk]["lines"]:
            duck[int((TL.s(l["key"]) - 0.1) * SR):int((TL.e(l["key"]) + 0.15) * SR)] = 1 - db(dd)
    duck = np.convolve(duck, np.ones(SR // 8) / (SR // 8), "same")
    music = music * (1 - duck)
    music = mono_safe(widen(music, 1.15))
    ref = music[:, int(S("a1") * SR):int(E("b1") * SR)]
    g_mu = db(-23.0) / (np.sqrt((ref ** 2).mean()) + 1e-12)
    vad = np.convolve(np.abs(vo.mean(axis=0)), np.ones(int(0.015 * SR)) / int(0.015 * SR), mode="same")
    vad = np.clip(vad / (np.percentile(vad[vad > 1e-5], 70) + 1e-9), 0, 1)
    vad = maximum_filter1d(vad, size=int(0.09 * SR), origin=-int(0.02 * SR))
    vad = np.convolve(vad, np.ones(int(0.02 * SR)) / int(0.02 * SR), mode="same")
    lines_on = np.zeros(N)
    for key in TL.order:
        lines_on[max(0, int((TL.s(key) - 0.04) * SR)):int(TL.e(key) * SR)] = 1.0
    protect = np.zeros(N)
    for t, *_ in hits:
        protect[max(0, int((t - 0.01) * SR)):int((t + 0.14) * SR)] = 1.0
    lines_on = np.maximum(lines_on * (1 - protect), vad)
    lines_on = np.convolve(lines_on, np.ones(int(0.05 * SR)) / int(0.05 * SR), mode="same")
    # the hit bus runs far over the ceiling (that is what makes it slam); under a line it is taken right down
    hits_x = reverb(hb.x, 0.12, 0.9) * dead * (1 - 0.995 * lines_on)
    # while anyone speaks or sings, everything but the hits stays well under the hits' ceiling
    speech = np.zeros(N)
    for key in TL.order:
        speech[max(0, int((TL.s(key) - 0.05) * SR)):int((TL.e(key) + 0.1) * SR)] = 1.0
    for t, *_ in hits:
        speech[max(0, int((t - 0.02) * SR)):int((t + 0.5) * SR)] = 0.0
    mix = loudness(music * g_mu + vo, hits_x * g_mu, speech, -15.5)
    tail = int(0.4 * SR)
    mix[:, -tail:] *= np.linspace(1, 0, tail) ** 2
    STEMS.update(music=music * g_mu, hits=hits_x * g_mu, vo=vo)
    return mix


STEMS = {}


CEIL, SPEECH_CEIL = -1.9, -9.2


def loudness(a, h, speech, target):
    """Normalise to `target` LUFS: the speech and music under a region limiter (SPEECH_CEIL while a line is on),
    then the hits on top, the whole under a true-peak limiter at CEIL."""
    import pyloudnorm as pyln
    g = 1.0
    ceil = np.where(speech > 0.5, db(SPEECH_CEIL), db(CEIL))
    for _ in range(4):
        x = limit(limit(a * g, ceil) + h * g, db(CEIL))
        lufs = pyln.Meter(SR).integrated_loudness(x.T)
        g *= db(target - lufs)
    return limit(limit(a * g, ceil) + h * g, db(CEIL))


def limit(x, ceil, look=0.005, rel=0.12):
    """A look-ahead limiter on the true (4x oversampled) peak."""
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
