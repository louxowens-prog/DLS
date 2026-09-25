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
TITLE_HOLD = 1.75           # tutti chord + title card between "open" and "defs"
PRE = {"open": 0.3, "defs": 0.35 + TITLE_HOLD, "artif": 2.3, "myth": 0.35, "token": 0.35,
       "llama": 2.3, "just": 0.3, "close1": 0.3}
TAIL = 3.9                  # the final tutti + end card after the last line


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
        """Caption chunks [(t0, t1, text)]: phrases split at punctuation, balanced to <= ~30 chars."""
        out = []
        for key in self.order:
            L = self.lines[key]
            cw, sp = L["caption"].split(), L["words"]
            n, m = len(cw), len(sp)
            times = [(sp[min(m - 1, int(i * m / n))][1], sp[min(m - 1, max(0, int((i + 1) * m / n) - 1))][2])
                     for i in range(n)]
            groups, cur = [], []
            for i, w in enumerate(cw):
                cur.append(i)
                if re.search(r"[,.?!:;…”]$", w) or i == n - 1:
                    groups.append(cur)
                    cur = []
            txt = lambda g: " ".join(cw[i] for i in g)
            merged = []
            for g in groups:
                if merged and len(txt(merged[-1] + g)) <= 26 and not re.search(r"[.?!…]”?$", cw[merged[-1][-1]]):
                    merged[-1] = merged[-1] + g
                else:
                    merged.append(g)
            weak = {"a", "an", "the", "of", "to", "at", "from", "and", "or", "in", "on", "for", "with", "as",
                    "is", "it's", "was", "that", "what", "by", "over", "every", "not", "can", "must", "we"}

            def split(g):
                if len(txt(g)) <= 29 or len(g) < 2:
                    return [g]
                best, bi = None, 1
                for i in range(1, len(g)):
                    l, r = txt(g[:i]), txt(g[i:])
                    cost = abs(len(l) - len(r)) + (14 if cw[g[i - 1]].lower().strip("“”\"") in weak else 0) \
                        + (10 if cw[g[i - 1]].startswith("“") and not cw[g[i - 1]].endswith("”") else 0) \
                        + (14 if re.search(r"\d$", cw[g[i - 1]]) else 0)
                    if best is None or cost < best:
                        best, bi = cost, i
                return split(g[:bi]) + split(g[bi:])

            chunks = [c for g in merged for c in split(g)]
            for j, g in enumerate(chunks):
                t0 = times[g[0]][0]
                nxt = times[chunks[j + 1][0]][0] if j + 1 < len(chunks) else \
                    min(L["end"] + 0.35, self.next_start(key) - 0.05)
                out.append((t0 - 0.04, max(nxt - 0.02, times[g[-1]][1]), txt(g)))
        return out


TL = Timeline()

if __name__ == "__main__":
    for k in TL.order:
        L = TL.lines[k]
        print(f"{k:10s} {L['start']:7.2f} {L['end']:7.2f}")
    print("total", round(TL.total, 2))
    for c in TL.captions()[:12]:
        print(f"{c[0]:6.2f} {c[1]:6.2f} {c[2]}")
