"""Global timing: every spoken line and the air between them (the descent that opens it, the title and the chapter
cards, the dead silences before the scares, the collapse, the last image). 24 fps."""
import os

import numpy as np

from script import FX, LINES, PITCH, SPEED, VOICES
from voice import SR, speak, speak_fx, whisper, word_times

FPS = 24
HERE = os.path.dirname(os.path.abspath(__file__))

# seconds of picture and music (no voice) before a line
PRE = {
    "h1": 0.35,                    # a porcelain face; a targeting box closes on it
    "h2": 0.15,
    "c1": 0.9,                    # the white room humming; the chair; she leans in
    "e1": 2.9,                    # going under: water, then a desert at dawn in silence; the title; chapter I
    "e8": 1.1,                    # dead silence; her eyes snap open; a beat; she speaks
    "w1": 1.25,                    # chapter II
    "w6": 0.3,
    "o1": 1.25,                    # chapter III
    "o6": 0.3,
    "t2": 1.25,                    # chapter IV
    "t6": 1.2,                    # dead silence; the scales slam; a beat; she speaks
    "d1": 0.8,
    "n1": 0.7,                    # the cold world: a bedroom at dawn, an alarm
    "n10": 0.2,
    "n11": 1.4,                   # dead silence; three knocks
    "n12": 0.1,
    "x1": 3.0,                    # the collapse: sandstorm, glass, drums, brass, chant
    "y1": 1.85,                    # cut to silence; the last vitrine; the melody, broken, alone
    "y3": 1.0,                    # dead silence; the black glass; something behind you
    "z1": 0.7,                    # the white room again
}
TIGHT = {"NAR": 0.33, "NADIA": 0.45}   # longest pause left inside a line, by speaker
TIGHT_LINE = {"h2": 0.6, "c1": 0.6, "y1": 0.55, "z1": 0.5, "z3": 0.45}   # where the guide lets a beat breathe
TAIL = 4.2                        # the last image: the endless room of chairs, the melody alone and slow


def _comb(x, delay_s, fb):
    d = max(1, int(delay_s * SR))
    y = np.copy(x).astype(np.float64)
    for i in range(d, len(y)):
        y[i] += fb * y[i - d]
    return y


def pv_shift(x, semis, n=1024, hop=256):
    """Pitch-shift by `semis` semitones keeping the duration: a phase vocoder stretch, then a resample."""
    from scipy import signal
    r = 2 ** (semis / 12)
    f, t, Z = signal.stft(x, SR, nperseg=n, noverlap=n - hop)
    steps = np.arange(0, Z.shape[1] - 1, 1 / r)
    mag = np.abs(Z)
    ph = np.angle(Z)
    omega = 2 * np.pi * hop * np.arange(Z.shape[0]) / n
    acc = ph[:, 0].copy()
    out = np.zeros((Z.shape[0], len(steps)), complex)
    for k, s in enumerate(steps):
        i = int(s)
        a = s - i
        m = (1 - a) * mag[:, i] + a * mag[:, i + 1]
        out[:, k] = m * np.exp(1j * acc)
        dp = ph[:, i + 1] - ph[:, i] - omega
        dp -= 2 * np.pi * np.round(dp / (2 * np.pi))
        acc += omega + dp
    _, y = signal.istft(out, SR, nperseg=n, noverlap=n - hop)
    y = signal.resample(y, int(len(y) / r))[: len(x)]
    return np.pad(y, (0, max(0, len(x) - len(y))))


def treat(wav, kind):
    """curator: the entity - her slowed voice doubled a hair sharp and flat, an octave below it like a shadow, a soft
    saturation; system: the same voice flattened into a machine's, down a telephone line; why: (built elsewhere)."""
    from scipy import signal
    w = wav.astype(np.float64)
    if kind == "curator":
        # not a woman any more: her voice dropped a further five semitones (formants and all, so it sounds vast),
        # an octave below that at equal weight, two doubles a quarter-tone apart, and her own voice at its old pitch
        # whispered on top, so something small and breathy speaks inside something huge
        from voice import whisper
        main = pv_shift(w, -5.0)
        low = pv_shift(main, -12.0)
        d1, d2 = int(0.017 * SR), int(0.029 * SR)
        up = signal.resample(main, int(len(main) / 2 ** (0.3 / 12)))[: len(w)]
        dn = signal.resample(main, int(len(main) / 2 ** (-0.3 / 12)))[: len(w)]
        up = np.concatenate([np.zeros(d1), up])[: len(w)]
        dn = np.concatenate([np.zeros(d2), dn])[: len(w)]
        up, dn = np.pad(up, (0, len(w) - len(up))), np.pad(dn, (0, len(w) - len(dn)))
        wh = whisper(w.astype(np.float32), keep=0.0, seed=11).astype(np.float64)
        wh = np.concatenate([np.zeros(int(0.009 * SR)), wh])[: len(w)]
        mixw = main + 0.45 * up + 0.45 * dn + 0.6 * low + 0.5 * wh
        # a lift at 2-4.5 kHz so the words stay crisp through the layers (the octave shadow is thinner too)
        mixw = mixw + 0.45 * signal.sosfilt(signal.butter(2, [2000 / (SR / 2), 4500 / (SR / 2)], "band", output="sos"), mixw)
        w = np.tanh(1.6 * mixw / (np.abs(mixw).max() + 1e-9))
    elif kind == "system":
        f, t, Z = signal.stft(w, SR, nperseg=480, noverlap=320)
        _, robot = signal.istft(np.abs(Z), SR, nperseg=480, noverlap=320)
        robot = robot[: len(w)]
        robot *= np.sqrt((w ** 2).mean() / ((robot ** 2).mean() + 1e-12))
        w = 0.55 * w + 0.45 * robot
        w = signal.sosfilt(signal.butter(4, [320 / (SR / 2), 3400 / (SR / 2)], "band", output="sos"), w)
        w = np.round(w / (np.abs(w).max() + 1e-9) * 48) / 48                 # a little crushed, like an old line
    elif kind in ("plead", "cry"):
        n = len(w)
        tt = np.arange(n) / SR
        # a voice on the edge of tears: the pitch trembling (6-7 Hz), a little breath through it
        cents = 35 * np.sin(2 * np.pi * 6.5 * tt) + 15 * np.sin(2 * np.pi * 2.3 * tt + 1)
        r = 2 ** (cents / 1200)
        pos = np.cumsum(r)
        pos = pos * (n - 1) / pos[-1]
        w = np.interp(pos, np.arange(n), w)
        rng = np.random.default_rng(5)
        breath = signal.sosfilt(signal.butter(2, [1500 / (SR / 2), 6000 / (SR / 2)], "band", output="sos"), rng.normal(0, 1, n))
        env = np.abs(signal.hilbert(w))
        env = np.convolve(env, np.ones(240) / 240, "same")
        w = w + breath * env * 0.35
        if kind == "cry":
            # she breaks: a ragged gasp, then the second "I'm qualified!" pitched up and pushed, the voice cracking
            # up into falsetto twice and catching, then sobs - three short shuddering breaths in and a broken moan
            from voice import pauses
            ps = pauses(wav, 0.15)
            cut = int(ps[0][1] * SR) if ps else n // 2
            head, tail = w[:cut], w[cut:]
            pk = np.abs(head).max()
            tail = pv_shift(tail, 4.0)
            hi = pv_shift(tail, 7.0)
            tl = np.arange(len(tail)) / SR
            brk = np.zeros(len(tail))
            for c0, wd in ((0.22, 0.11), (0.58, 0.14)):                        # two cracks up into falsetto
                brk += np.exp(-0.5 * ((tl - c0) / (wd / 2.5)) ** 2)
            brk = np.clip(brk, 0, 1)
            tail = tail * (1 - brk) + hi * brk * 0.8
            tail = tail * (1.0 + 1.4 * np.clip(tl / 0.2, 0, 1))                 # louder
            tail = np.tanh(2.6 * tail / (np.abs(tail).max() + 1e-9)) * pk * 1.9    # strained, pushed
            catch = (np.sin(2 * np.pi * 11 * tl + 1.0) > 0.75) * (tl > 0.4)    # the voice catching in the throat
            tail = tail * (1 - 0.45 * catch)
            def gasp(d, a, rise=True):
                m = int(d * SR)
                g = signal.sosfilt(signal.butter(2, [700 / (SR / 2), 5200 / (SR / 2)], "band", output="sos"), rng.normal(0, 1, m))
                e = np.linspace(0, 1, m) ** 0.6 if rise else np.hanning(m)
                e[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
                return g / (np.abs(g).max() + 1e-9) * e * a
            pre = gasp(0.32, 0.55 * pk)                                          # the gasp before she breaks
            sobs = []
            for k, d in enumerate((0.11, 0.1, 0.16)):                            # shuddering breaths in
                sobs += [gasp(d, (0.45 + 0.1 * k) * pk, rise=False), np.zeros(int(0.07 * SR))]
            moan = pv_shift(tail[-int(0.4 * SR):], -3.0)
            ml = np.arange(len(moan)) / SR
            moan = moan * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * ml)) * np.linspace(0.8, 0, len(moan)) * 0.6
            w = np.concatenate([head, np.zeros(int(0.06 * SR)), pre, tail, np.zeros(int(0.06 * SR))] + sobs + [moan])
            return (w * np.sqrt((wav.astype(np.float64) ** 2).mean() / ((head ** 2).mean() + 1e-12))).astype(np.float32)
    w *= np.sqrt((wav.astype(np.float64) ** 2).mean() / ((w ** 2).mean() + 1e-12))
    return w.astype(np.float32)


WHY_VOICES = ["af_bella", "af_heart", "bf_emma", "af_sarah", "bf_lily", "af_nicole", "af_sky", "af_nova", "bf_alice", "af_river"]


def why_chorus(text):
    """Ten women whispering one word, not quite together."""
    rng = np.random.default_rng(7)
    parts = []
    for v in WHY_VOICES:
        x = speak(text, v, 1.0)
        x = whisper(x, keep=0.3, seed=len(parts))
        off = int(rng.uniform(0, 0.16) * SR)
        parts.append(np.concatenate([np.zeros(off, np.float32), x * rng.uniform(0.6, 1.0)]))
    n = max(len(p) for p in parts)
    out = sum(np.pad(p, (0, n - len(p))) for p in parts)
    return (out * 0.09 / (np.sqrt((out ** 2).mean()) + 1e-9)).astype(np.float32)


def tighten(wav, cap=0.45):
    """Shorten the long silences the voice leaves between sentences to `cap` seconds (the middle of each cut out,
    a short crossfade across the join), so the narration keeps its breath without dead air."""
    from voice import pauses
    out, last = [], 0
    xf = int(0.01 * SR)
    for a, b in pauses(wav, cap + 0.05):
        i0, i1 = int((a + cap / 2) * SR), int((b - cap / 2) * SR)
        out.append(wav[last:i0])
        last = i1
    out.append(wav[last:])
    y = out[0]
    for seg in out[1:]:
        if len(y) > xf and len(seg) > xf:
            fade = np.linspace(0, 1, xf, dtype=np.float32)
            y = np.concatenate([y[:-xf], y[-xf:] * (1 - fade) + seg[:xf] * fade, seg[xf:]])
        else:
            y = np.concatenate([y, seg])
    return y.astype(np.float32)


def _norm(w):
    return "".join(ch for ch in w.lower() if ch.isalnum() or ch == "'")


class Timeline:
    def __init__(self):
        self.lines, self.order = {}, []
        t = 0.0
        for key, who, spoken, caption, gap in LINES:
            t += PRE.get(key, 0.0)
            self._line(key, who, spoken, caption, t)
            t = self.lines[key]["end"] + gap
        self.total = t + TAIL

    def _line(self, key, who, spoken, caption, t):
        v, sp, pt = VOICES[who]
        if spoken.startswith("="):
            src = self.lines[spoken[1:]]
            spoken, caption = src["spoken"], src["breaks"]
            wav = src["wav0"]
            words = [(w, a - src["start"], b - src["start"]) for w, a, b in src["words"]]
        else:
            wav = why_chorus(spoken) if v == "chorus" else speak_fx(spoken, v, SPEED.get(key, sp), PITCH.get(key, pt))
            if who in TIGHT:
                wav = tighten(wav, TIGHT_LINE.get(key, TIGHT[who]))
            words = word_times(spoken, wav)
        wav0 = wav
        if key in FX and FX[key] != "why":
            wav = treat(wav, FX[key])
            k = len(wav) / len(wav0)
            words = [(w, a * k, b * k) for w, a, b in words]
        d = len(wav) / SR
        self.lines[key] = dict(start=t, end=t + d, wav=wav, wav0=wav0, spoken=spoken, who=who, voice=v,
                               caption=(caption or spoken).replace("|", ""), breaks=caption or spoken,
                               words=[(w, t + a, t + b) for w, a, b in words])
        self.order.append(key)

    # ---- lookups
    def who(self, key):
        return self.lines[key]["who"]

    def s(self, key):
        return self.lines[key]["start"]

    def e(self, key):
        return self.lines[key]["end"]

    def captions(self):
        """Caption chunks [(t0, t1, text, key)]: whole phrases, split where the script puts a |."""
        out = []
        for n, key in enumerate(self.order):
            L = self.lines[key]
            raw = [w for w in L["breaks"].split(" ") if w]
            cw, sp = [w.rstrip("|") for w in raw if w != "|"], L["words"]
            ends = []
            for w in raw:
                if w == "|":
                    ends[-1] = True
                else:
                    ends.append(w.endswith("|"))
            nw, m = len(cw), len(sp)
            groups, cur = [], []
            for i in range(nw):
                cur.append(i)
                if ends[i] or i == nw - 1:
                    groups.append(cur)
                    cur = []
            nxt_start = self.lines[self.order[n + 1]]["start"] if n + 1 < len(self.order) else self.total
            # where each chunk starts in the recording: match the chunk's last word (or the next chunk's first word)
            # among the spoken words, so a caption's figures ("94%" for "ninety-four percent") don't skew the timing
            starts, pos = [0], 0
            for j in range(len(groups) - 1):
                g, g2 = groups[j], groups[j + 1]
                est, at = pos + len(g), None
                hits = [k + 1 for k in range(pos, m) if _norm(sp[k][0]) == _norm(cw[g[-1]])]
                if hits and abs(min(hits, key=lambda k: abs(k - est)) - est) <= 3:
                    at = min(hits, key=lambda k: abs(k - est))
                if at is None:
                    hits = [k for k in range(pos + 1, m) if _norm(sp[k][0]) == _norm(cw[g2[0]])]
                    if hits and abs(min(hits, key=lambda k: abs(k - est)) - est) <= 3:
                        at = min(hits, key=lambda k: abs(k - est))
                if at is None:
                    at = min(m - 1, int(g2[0] * m / nw))
                starts.append(min(m - 1, max(pos + 1, at)))
                pos = starts[-1]
            for j, g in enumerate(groups):
                t0 = sp[starts[j]][1]
                last = sp[starts[j + 1] - 1][2] if j + 1 < len(groups) else sp[-1][2]
                t1 = sp[starts[j + 1]][1] if j + 1 < len(groups) else min(L["end"] + 0.35, nxt_start - 0.05)
                out.append((t0 - 0.05, max(t1 - 0.02, last), " ".join(cw[i] for i in g), key))
        return out


TL = Timeline()

if __name__ == "__main__":
    for k in TL.order:
        L = TL.lines[k]
        d = L["end"] - L["start"]
        n = len(L["spoken"].split())
        print(f"{k:4s} {L['who']:6s} {L['start']:7.2f} {d:5.2f}s {n / d * 60:4.0f}wpm  {L['spoken'][:70]}")
    sp = sum(TL.e(k) - TL.s(k) for k in TL.order)
    nw = sum(len(TL.lines[k]["spoken"].split()) for k in TL.order)
    print("total", round(TL.total, 2), "speech", round(sp, 1), "words", nw, "avg wpm", round(nw / sp * 60))
