"""Global timing: every spoken line, the pauses between them (the title, the dead silences, the room changes).
The film runs at 24 fps."""
import os

from script import LINES, PITCH, SPEED, VOICES, W
from voice import SR, speak_fx, whisper, word_times

FPS = 24
HERE = os.path.dirname(os.path.abspath(__file__))

PRE = {
    "o1": 0.55,                   # the eye opens first
    "p1": 3.1,                    # the title crashes in, then dead silence, then the rain
    "r1": 1.7,                    # the red room: a clock at 2:07, lightning
    "b1": 2.6,                    # the spiral stair, the corridor
    "g1": 1.4,                    # the jump-scare in Room 97, the corridor
    "m1": 2.2,
    "m4": 1.0,                    # the reflection that stops nodding, and looks at us
    "h1": 1.9,                    # dead silence: the key in the wallpaper
    "h6": 1.9,                    # the door opens on blazing colour
    "x1": 0.4,
    "d1": 7.2,                    # the heartbeat stops; dead silence; the rewind
    "d5": 1.6,                    # sirens into the dawn
    "e1": 0.6,
    "e4": 0.6,
}
TAIL = 5.0


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
        wav = speak_fx(spoken, v, SPEED.get(key, sp), PITCH.get(key, pt))
        if who == W:
            wav = whisper(wav)
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
        print(f"{k:4s} {L['who']:4s} {L['start']:7.2f} {L['end']:7.2f}  {L['shown'][:80]}")
    print("total", round(TL.total, 2), "words", sum(len(TL.lines[k]["spoken"].split()) for k in TL.order))
