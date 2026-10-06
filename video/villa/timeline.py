"""Global timing: every spoken line and the air between them (the title, the deja vu beat in the alleys, the hard
silences, the door). The film runs at 24 fps."""
import os

import numpy as np

from script import FX, LINES, PITCH, SPEED, VOICES
from voice import SR, speak_fx, word_times

FPS = 24
HERE = os.path.dirname(os.path.abspath(__file__))

# seconds of picture and music (no voice) before a line
PRE = {
    "h1": 0.35,                   # the zoom into a porcelain graduate's painted eye
    "o1": 2.8,                    # the crack, a dead silence, the title card
    "l1": 0.55,                   # into the alleys
    "v1": 3.7,                    # deja vu: the same fountain three times, the mannequin at the glass; the villa gate
    "g1": 0.45,                   # the gallery, the camera dollying in
    "w1": 0.5,                    # the writing room
    "w3": 0.6,                    # the clock: YEAR TWO
    "w6": 0.6,                    # YEAR THREE
    "c1": 0.95,                   # FINAL YEAR; up into the clockwork
    "m1": 1.45,                   # the gears jam, dead silence, the falling mannequin
    "x1": 0.55,                   # the corridor to the locked door
    "r1": 1.75,                   # the door opens on white; dead silence; an office
    "r6": 0.3,                    # the rejections
    "p1": 0.45,                   # the dark window
    "e1": 1.2,                    # her face cracks; silence; the music box returns
}
TAIL = 2.6                        # the last chime of the clock, and FINE


def _comb(x, delay_s, fb):
    """A hollow tube: feedback comb filter."""
    d = max(1, int(delay_s * SR))
    y = np.copy(x).astype(np.float64)
    for i in range(d, len(y)):
        y[i] += fb * y[i - d]
    return y


def treat(wav, kind):
    """'pale': a little greyer and flatter; 'porcelain': the pitch flattened to a hum and a hollow resonance."""
    from scipy import signal
    w = wav.astype(np.float64)
    if kind == "pale":
        w = signal.sosfilt(signal.butter(2, 3800 / (SR / 2), "low", output="sos"), w)
        r = 2 ** (-0.35 / 12)
        w = signal.resample(w, int(len(w) / r))
    elif kind == "porcelain":
        f, t, Z = signal.stft(w, SR, nperseg=480, noverlap=320)
        _, robot = signal.istft(np.abs(Z), SR, nperseg=480, noverlap=320)       # zero phase: a monotone at the frame rate
        robot = robot[: len(w)]
        robot *= np.sqrt((w ** 2).mean() / ((robot ** 2).mean() + 1e-12))
        mixw = 0.45 * w + 0.55 * robot
        w = _comb(mixw, 0.0042, 0.45) * 0.7
    w *= np.sqrt((wav.astype(np.float64) ** 2).mean() / ((w ** 2).mean() + 1e-12))
    return w.astype(np.float32)


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
            wav = speak_fx(spoken, v, SPEED.get(key, sp), PITCH.get(key, pt))
            words = word_times(spoken, wav)
        wav0 = wav
        if key in FX:
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
