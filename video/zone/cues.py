"""Named moments the picture and the soundtrack both hit, and the word-level lookups."""
from script import CHAPTERS, SONGS
from timeline import TL

S, E = TL.s, TL.e


def Wx(key, word, nth=0):
    """Start of the nth word containing `word` (case-insensitive)."""
    hits = [a for w, a, b in TL.lines[key]["words"] if word.lower() in w.lower()]
    return hits[min(nth, len(hits) - 1)] if hits else S(key)


def SL(song, i):
    """Start of lyric line i of a song."""
    return TL.lines[f"{song}_{i}"]["start"]


def EL(song, i):
    return TL.lines[f"{song}_{i}"]["end"]


# the room intertitles: (number, title, card start, card end)
CARDS = []
for num, title, _, first in CHAPTERS:
    t1 = S(first) - 0.12
    CARDS.append((num, title, t1 - 1.35, t1))

C = {
    "buzz": 0.25,
    "hand": S("r3") + 0.5,
    "door_open": S("r3") + 0.2,
    "spot": SL("s1", 2) + 0.2,
    "stamp_decides": Wx("a3", "decides"),
    "clash": Wx("b2", "clash"),
    "page": SL("s2", 3) + 0.4,
    "all": SL("s3", 5),
    "evaluate": Wx("c2", "evaluated"),
    "crow": E("s4") + 0.25,
    "flag": S("f3") - 0.05,
    "found": S("s5"),
    "early_door": Wx("f6", "early"),
    "late_door": Wx("f6", "spreads"),
}
