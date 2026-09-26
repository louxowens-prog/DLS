"""Global timing: where every line lands (narrator and characters), plus the music-only beats between them.

The film look runs at 24 fps; characters are drawn "on twos" (12 drawings a second) while the camera moves on ones."""
import os
import re

from script import LINES, NAR, VOICES
from voice import SR, speak, word_times

FPS = 24
TWOS = 12
HERE = os.path.dirname(os.path.abspath(__file__))

PRE = {"h1": 0.35, "r1": 0.5, "s1": 0.3, "j1": 0.7, "d1": 0.6, "d3": 0.1, "a1": 0.8, "a6": 0.2, "x1": 0.6, "f1": 0.9, "f7": 0.5}
TAIL = 3.2


class Timeline:
    def __init__(self):
        self.lines = {}
        t = 0.0
        for key, who, spoken, caption, gap in LINES:
            t += PRE.get(key, 0.0)
            v, sp = VOICES[who]
            wav = speak(spoken, v, sp)
            d = len(wav) / SR
            words = word_times(spoken, wav)
            self.lines[key] = dict(start=t, end=t + d, wav=wav, spoken=spoken, caption=caption or spoken, voice=v, who=who,
                                   words=[(w, t + a, t + b) for w, a, b in words])
            t += d + gap
        self.total = t + TAIL
        self.order = [k for k, *_ in LINES]

    def who(self, key):
        return self.lines[key]["who"]

    def s(self, key):
        return self.lines[key]["start"]

    def e(self, key):
        return self.lines[key]["end"]

    def word(self, key, needle, nth=0):
        hits = [a for w, a, b in self.lines[key]["words"] if needle.lower() in w.lower()]
        return hits[min(nth, len(hits) - 1)] if hits else self.s(key)

    def next_start(self, key):
        i = self.order.index(key)
        return self.s(self.order[i + 1]) if i + 1 < len(self.order) else self.total

    def captions(self):
        """Caption chunks [(t0, t1, text, key)]: whole phrases, up to ~44 characters (two lines), held >= ~1.2 s."""
        out = []
        weak = {"a", "an", "the", "of", "to", "at", "from", "and", "or", "in", "on", "for", "with", "as", "is",
                "it's", "was", "that", "what", "by", "over", "every", "not", "can", "must", "we", "about", "be"}
        for key in self.order:
            L = self.lines[key]
            if L["who"] != NAR:                       # characters talk in speech bubbles, one bubble per line
                out.append((L["start"] - 0.08, L["end"] + 0.35, L["caption"], key))
                continue
            cw, sp = L["caption"].split(), L["words"]
            n, m = len(cw), len(sp)
            times = [(sp[min(m - 1, int(i * m / n))][1], sp[min(m - 1, max(0, int((i + 1) * m / n) - 1))][2])
                     for i in range(n)]
            txt = lambda g: " ".join(cw[i] for i in g)
            phrases, cur = [], []
            for i, w in enumerate(cw):
                cur.append(i)
                short_lead = len(cur) == 1 and len(w) <= 5 and w.endswith(",") and i < n - 1
                if (re.search(r"[,.?!:;…”]$", w) and not short_lead) or i == n - 1:
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
                out.append((t0 - 0.05, max(nxt - 0.02, times[g[-1]][1]), txt(g), key))
        return out


TL = Timeline()

if __name__ == "__main__":
    for k in TL.order:
        L = TL.lines[k]
        print(f"{k:5s} {L['start']:7.2f} {L['end']:7.2f}  {L['caption'][:70]}")
    print("total", round(TL.total, 2), "words", sum(len(TL.lines[k]["spoken"].split()) for k in TL.order))
