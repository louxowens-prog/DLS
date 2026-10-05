"""Global timing: every spoken line and the pauses between them (the title, the chapter cards, the hard silences).
The film runs at 24 fps."""
import os

from script import CACKLE, LINES, PITCH, SPEED, VOICES
from voice import SR, cackle, speak_fx, word_times

FPS = 24
HERE = os.path.dirname(os.path.abspath(__file__))

PRE = {
    "c1": 0.45,                   # lightning: the screaming doctor on the cover, the camera pulling back
    "c3": 0.3,                    # Nora on her sofa with the comic, the storm at the window
    "v1": 0.7,                    # a page turns: tale one's title panel
    "v5": 1.15,                   # dead silence on the dark road, then the signal goes
    "g1": 0.7,                    # a page turns: tale two
    "g6": 0.75,                   # the exam hall, silent but for the examiner's heels
    "s1": 0.7,                    # a page turns: tale three
    "r1": 3.35,                   # a second of dead silence, the thing on the screen - the loudest moment - then the power dies
    "r2": 0.6,                    # silence in the dark flat
    "m1": 0.8,                    # the comic closes; the quiet beat
    "m5": 0.6,                    # the back page: the mail-order ads
}
TAIL = 1.45


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
        if key in CACKLE:
            wav = cackle(v, seed=CACKLE[key])
            d = len(wav) / SR
            words = [(spoken, 0.0, d)]
        else:
            wav = speak_fx(spoken, v, SPEED.get(key, sp), PITCH.get(key, pt))
            d = len(wav) / SR
            words = word_times(spoken, wav)
        self.lines[key] = dict(start=t, end=t + d, wav=wav, spoken=spoken, who=who, voice=v,
                               caption=(caption or spoken).replace("|", ""), breaks=caption or spoken,
                               shown=spoken, words=[(w, t + a, t + b) for w, a, b in words])
        self.order.append(key)

    # ---- lookups
    def who(self, key):
        return self.lines[key]["who"]

    def s(self, key):
        return self.lines[key]["start"]

    def e(self, key):
        return self.lines[key]["end"]

    def word(self, key, needle, nth=0):
        hits = [a for w, a, b in self.lines[key]["words"] if needle.lower() in w.lower()]
        return hits[min(nth, len(hits) - 1)] if hits else self.s(key)

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
            times = [(sp[min(m - 1, int(i * m / nw))][1], sp[min(m - 1, max(0, int((i + 1) * m / nw) - 1))][2]) for i in range(nw)]
            groups, cur = [], []
            for i in range(nw):
                cur.append(i)
                if ends[i] or i == nw - 1:
                    groups.append(cur)
                    cur = []
            nxt_start = self.lines[self.order[n + 1]]["start"] if n + 1 < len(self.order) else self.total
            for j, g in enumerate(groups):
                t0 = times[g[0]][0]
                t1 = times[groups[j + 1][0]][0] if j + 1 < len(groups) else min(L["end"] + 0.35, nxt_start - 0.05)
                out.append((t0 - 0.05, max(t1 - 0.02, times[g[-1]][1]), " ".join(cw[i] for i in g), key))
        return out


TL = Timeline()

if __name__ == "__main__":
    for k in TL.order:
        L = TL.lines[k]
        d = L["end"] - L["start"]
        n = len(L["spoken"].split())
        print(f"{k:4s} {L['who']:6s} {L['start']:7.2f} {d:5.2f}s {n / d * 60:4.0f}wpm  {L['shown'][:70]}")
    sp = sum(TL.e(k) - TL.s(k) for k in TL.order)
    nw = sum(len(TL.lines[k]["spoken"].split()) for k in TL.order)
    print("total", round(TL.total, 2), "speech", round(sp, 1), "words", nw, "avg wpm", round(nw / sp * 60))
