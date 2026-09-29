"""Named moments the picture and the soundtrack both hit, the countdown, the use tags, and who is talking."""
import math

from script import CHAPTERS, USES, WHO
from timeline import TL

S, E, W = TL.s, TL.e, TL.word


def Wx(key, word, nth=0):
    """Start of the nth word containing `word` (case-insensitive)."""
    hits = [a for w, a, b in TL.lines[key]["words"] if word.lower() in w.lower()]
    return hits[min(nth, len(hits) - 1)] if hits else S(key)


def talk(who, T):
    for k in TL.order:
        L = TL.lines[k]
        if L["who"] == who and L["start"] - 0.02 <= T <= L["end"]:
            for w, a, b in L["words"]:
                if a <= T <= b:
                    return 0.35 + 0.65 * abs(math.sin((T - a) / max(0.08, (b - a)) * math.pi * max(1, len(w) // 3)))
            return 0.0
    return 0.0


# the chapter cards: (number word, title, Japanese, card start, card end); a fade to black either side
CARDS = []
for num, title, jp, first in CHAPTERS:
    t1 = S(first) - 0.25
    CARDS.append((num, title, jp, t1 - 2.05, t1))

C = {
    "lamp_on": S("o2") - 0.08,
    "bell": E("a3") + 0.02,
    "hand_up": S("a3") - 0.4,
    "split98": E("a6") + 0.1,
    "type1": S("b2q"),
    "odo": Wx("b3", "odometer"),
    "speedo": Wx("b3", "speedometer"),
    "turn": E("b3") + 0.15,
    "type2": S("b4"),
    "drag": Wx("b5", "Drag"),
    "type3": S("b6"),
    "marks": S("b7") - 0.2,
    "type4": S("b7q"),
    "ring": Wx("b8", "inside"),
    "fix": Wx("b8", "Multiply"),
    "box": S("d1b") + 0.2,
    "practice": Wx("d2", "practice"),
    "worse": Wx("d2", "seventeen"),
    "hints": E("d2") + 0.2,
    "rule": S("d3"),
    "twice": Wx("d4b", "twice"),
    "less_time": Wx("d4b", "less"),
    "cranes": Wx("d6", "grade"),
    "flag": Wx("d6", "flag"),
    "six": Wx("d6", "six"),
    "forty": S("e3"),
    "nigeria": S("e4"),
    "smile": S("e6b"),
    "inside": Wx("e6", "inside"),
    "letter": S("e7"),
    "coach": Wx("e3b", "coach"),
    "conv": Wx("e3b", "play"),
    "open": E("e3") + 0.15,
    "final": S("e8") - 0.25,
}

# the countdown on screen in the present: (from T, clock time)
CLOCKS = [(0.0, "21:40"), (S("b1") - 0.2, "21:52"), (S("b6") + 0.8, "22:31"), (S("b7") - 0.2, "22:58"),
          (S("b11") - 0.1, "23:10"), (Wx("b11", "midnight") - 0.3, "00:04"), (S("d1") - 0.3, "00:12"), (S("d3") - 0.3, "00:21"),
          (S("e1") - 0.2, "07:30"), (S("e5") - 0.2, "09:00")]


def clock_at(T):
    cur = CLOCKS[0][1]
    for t, s in CLOCKS:
        if T >= t:
            cur = s
    return cur


def left_until_exam(hhmm):
    h, m = map(int, hhmm.split(":"))
    mins = (9 * 60 - (h * 60 + m)) % (24 * 60)
    if mins == 0:
        return "THE EXAM"
    return f"{mins // 60} h {mins % 60:02d} min to the exam"


def _tagtimes(items):
    out = []
    for i, (k, w, lab) in enumerate(items):
        t0 = Wx(k, w) - 0.15
        out.append([t0, None, i + 1, lab])
    for i in range(len(out)):
        nxt = out[i + 1][0] if i + 1 < len(out) else 1e9
        out[i][1] = min(nxt, out[i][0] + 3.0)
    return out


USE_TAGS = _tagtimes(USES)
WHO_TAGS = _tagtimes(WHO)
APHORISMS = {"a7", "b12", "d7", "e8", "e9"}          # spoken and written big on screen (no caption)
NO_CAPTION = APHORISMS | {"b4", "b6", "b2q", "b7q", "d3q", "b1", "e1", "e5"}   # typed prompts and clock times are on screen
