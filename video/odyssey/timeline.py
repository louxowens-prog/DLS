"""Global timing: where every narration line lands, plus the music-only beats between them."""
import json
import os
import re

from script import LINES
from voice import SR, speak, word_times

FPS = 24
VOICE = "af_heart"
SPEED = 1.24
HERE = os.path.dirname(os.path.abspath(__file__))

# Seconds of music/visual-only time inserted before a line.
TITLE_HOLD = 0.6            # tutti chord + title card between "open" and "defs"
PRE = {"open": 0.25, "defs": 2.15 + TITLE_HOLD, "nothing": 1.3, "artif": 2.3, "myth": 0.35, "token": 0.35,
       "llama": 2.3, "just": 0.3, "close1": 0.3}
TAIL = 3.8                  # the final tutti + end card after the last line


class Timeline:
    def __init__(self):
        self.lines = {}
        t = 0.0
        for key, spoken, caption, gap in LINES:
            t += PRE.get(key, 0.0)
            wav = speak(spoken, VOICE, SPEED)
            d = len(wav) / SR
            words = word_times(spoken, wav)
            cap = caption or spoken
            self.lines[key] = dict(start=t, end=t + d, wav=wav, spoken=spoken, caption=cap,
                                   words=[(w, t + a, t + b) for w, a, b in words])
            t += d + gap
        self.total = t + TAIL
        self.order = [k for k, *_ in LINES]

    def s(self, key):
        return self.lines[key]["start"]

    def e(self, key):
        return self.lines[key]["end"]

    def word(self, key, needle, nth=0):
        """Start time of the nth word in line `key` that contains `needle` (case-insensitive)."""
        hits = [a for w, a, b in self.lines[key]["words"] if needle.lower() in w.lower()]
        return hits[min(nth, len(hits) - 1)] if hits else self.s(key)

    def next_start(self, key):
        i = self.order.index(key)
        return self.s(self.order[i + 1]) if i + 1 < len(self.order) else self.total

    def captions(self):
        """Caption chunks [(t0, t1, text)]: whole phrases, up to ~44 characters (two lines), held >= ~1.2 s."""
        out = []
        weak = {"a", "an", "the", "of", "to", "at", "from", "and", "or", "in", "on", "for", "with", "as", "is",
                "it's", "was", "that", "what", "by", "over", "every", "not", "can", "must", "we", "set", "about"}
        for key in self.order:
            L = self.lines[key]
            cw, sp = L["caption"].split(), L["words"]
            n, m = len(cw), len(sp)
            times = [(sp[min(m - 1, int(i * m / n))][1], sp[min(m - 1, max(0, int((i + 1) * m / n) - 1))][2])
                     for i in range(n)]
            txt = lambda g: " ".join(cw[i] for i in g)
            # phrases end at punctuation
            phrases, cur = [], []
            for i, w in enumerate(cw):
                cur.append(i)
                if re.search(r"[,.?!:;…”]$", w) or i == n - 1:
                    phrases.append(cur)
                    cur = []

            def split(g):
                if len(txt(g)) <= 44 or len(g) < 2:
                    return [g]
                best, bi = None, 1
                for i in range(1, len(g)):
                    l, r = txt(g[:i]), txt(g[i:])
                    cost = abs(len(l) - len(r)) + (30 if cw[g[i - 1]].lower().strip("“”\"") in weak else 0) \
                        + (30 if re.search(r"\d$", cw[g[i - 1]]) else 0)
                    if best is None or cost < best:
                        best, bi = cost, i
                return split(g[:bi]) + split(g[bi:])

            pieces = [p for g in phrases for p in split(g)]
            # merge neighbours while the result still fits and a piece is too short to read
            merged = []
            for p in pieces:
                if merged:
                    prev = merged[-1]
                    dur_prev = times[prev[-1]][1] - times[prev[0]][0]
                    dur_p = times[p[-1]][1] - times[p[0]][0]
                    lim = 52 if (dur_p < 0.7 or dur_prev < 0.7) else 44
                    if len(txt(prev + p)) <= lim and (dur_prev < 1.2 or dur_p < 0.8):
                        merged[-1] = prev + p
                        continue
                merged.append(p)
            for j, g in enumerate(merged):
                t0 = times[g[0]][0]
                nxt = times[merged[j + 1][0]][0] if j + 1 < len(merged) else \
                    min(L["end"] + 0.45, self.next_start(key) - 0.05)
                out.append((t0 - 0.05, max(nxt - 0.02, times[g[-1]][1]), txt(g)))
        return out


TL = Timeline()

if __name__ == "__main__":
    for k in TL.order:
        L = TL.lines[k]
        print(f"{k:10s} {L['start']:7.2f} {L['end']:7.2f}")
    print("total", round(TL.total, 2))
    for c in TL.captions()[:12]:
        print(f"{c[0]:6.2f} {c[1]:6.2f} {c[2]}")
