"""Global timing: every spoken line, every patter song (bars, downbeats, the lyric lines on them), the gaps.
The film runs at 24 fps."""
import math
import os

from script import CHAPTERS, LINES, PITCH, SONGS, SPEED, VOICES, LYRIC_SHOWN

SONG = "SONG"
from voice import SR, speak_fx, word_times

FPS = 24
HERE = os.path.dirname(os.path.abspath(__file__))

PRE = {c[3]: 1.5 for c in CHAPTERS}                 # room for each room's hand-lettered intertitle
PRE.update({"t1": 0.0, "r1": 1.5, "g1": 0.3})        # r1: the phone buzzes first
TAIL = 4.6


class Timeline:
    def __init__(self):
        self.lines, self.songs, self.order = {}, {}, []
        t = 0.0
        for key, who, spoken, caption, gap in LINES:
            t += PRE.get(key, 0.0)
            if who == SONG:
                t = self._song(key, t) + gap
                continue
            self._line(key, who, spoken, caption, t)
            t = self.lines[key]["end"] + gap
        self.total = t + TAIL

    def _line(self, key, who, spoken, caption, t, song=None, shown=None):
        v, sp, pt = VOICES[who]
        wav = speak_fx(spoken, v, SPEED.get(key, sp), PITCH.get(key, pt))
        d = len(wav) / SR
        words = word_times(spoken, wav)
        self.lines[key] = dict(start=t, end=t + d, wav=wav, spoken=spoken, who=who, voice=v, song=song,
                               caption=(caption or spoken).replace("|", ""), breaks=caption or spoken,
                               shown=shown or spoken, words=[(w, t + a, t + b) for w, a, b in words])
        self.order.append(key)

    def _song(self, key, t0):
        """A song in strict time: `intro` beats, then each lyric line on an even beat, as many beats as it needs."""
        S = SONGS[key]
        beat = 60.0 / S["bpm"]
        b = S["intro"]
        lines = []
        for i, (who, text) in enumerate(S["lines"]):
            k = f"{key}_{i}"
            self._line(k, who, text, None, t0 + b * beat + 0.03, song=key, shown=LYRIC_SHOWN.get(text, text))
            d = self.lines[k]["end"] - self.lines[k]["start"]
            nb = max(4, 2 * math.ceil((d + 0.22) / beat / 2))
            lines.append(dict(key=k, beat0=b, beats=nb))
            b += nb
        b += S["outro"]
        self.songs[key] = dict(start=t0, end=t0 + b * beat, beat=beat, bar=4 * beat, bpm=S["bpm"], style=S["style"],
                               beats=b, lines=lines)
        return t0 + b * beat

    # ---- lookups
    def who(self, key):
        return self.lines[key]["who"]

    def s(self, key):
        return self.songs[key]["start"] if key in self.songs else self.lines[key]["start"]

    def e(self, key):
        return self.songs[key]["end"] if key in self.songs else self.lines[key]["end"]

    def word(self, key, needle, nth=0):
        hits = [a for w, a, b in self.lines[key]["words"] if needle.lower() in w.lower()]
        return hits[min(nth, len(hits) - 1)] if hits else self.s(key)

    def song_at(self, t):
        for k, S in self.songs.items():
            if S["start"] <= t < S["end"]:
                return k
        return None

    def captions(self):
        """Caption chunks [(t0, t1, text, key)] for spoken (non-song) narration: whole phrases, <= ~50 chars."""
        import re
        out = []
        speech = [k for k in self.order if self.lines[k]["song"] is None]
        for n, key in enumerate(speech):
            L = self.lines[key]
            raw = [w for w in L["breaks"].split(" ") if w]                       # (a no-break space holds "737 MAX" together)
            cw, sp = [w.rstrip("|") for w in raw], L["words"]
            nw, m = len(cw), len(sp)
            times = [(sp[min(m - 1, int(i * m / nw))][1], sp[min(m - 1, max(0, int((i + 1) * m / nw) - 1))][2]) for i in range(nw)]
            groups, cur = [], []
            for i, w in enumerate(cw):
                cur.append(i)
                if raw[i].endswith("|") or i == nw - 1:
                    groups.append(cur)
                    cur = []
            nxt_start = self.lines[speech[n + 1]]["start"] if n + 1 < len(speech) else self.total
            song_next = min([S["start"] for S in self.songs.values() if S["start"] >= L["end"] - 0.01] or [self.total])
            for j, g in enumerate(groups):
                t0 = times[g[0]][0]
                t1 = times[groups[j + 1][0]][0] if j + 1 < len(groups) else min(L["end"] + 0.4, nxt_start - 0.05, song_next - 0.02)
                out.append((t0 - 0.05, max(t1 - 0.02, times[g[-1]][1]), " ".join(cw[i] for i in g), key))
        return out


TL = Timeline()

if __name__ == "__main__":
    for k in TL.order:
        L = TL.lines[k]
        print(f"{k:6s} {L['who']:4s} {L['start']:7.2f} {L['end']:7.2f}  {L['shown'][:70]}")
    for k, S in TL.songs.items():
        print(k, S["style"], round(S["start"], 2), round(S["end"], 2), "beats", S["beats"], [l["beats"] for l in S["lines"]])
    print("total", round(TL.total, 2), "words", sum(len(TL.lines[k]["spoken"].split()) for k in TL.order))
