"""The edit: every shot, when it starts, and how we get into it.

Transition types (the Speed Racer grammar):
  head:<who>  a giant face slides across the frame and wipes to the next shot
  iris        a circle closes on the old shot and opens on the new one
  split       the frame slams into a split screen
  cut         a hard cut on a hit
Both the picture (shots.py) and the soundtrack (audio.py) read this list, so every transition gets a hit.
"""
from cues import C
from script import LINES
from timeline import TL

S, E, W = TL.s, TL.e, TL.word
_KEYS = [k for k, *_ in LINES]


def L(key):
    """Transition just ahead of a line: the wipe's cover frame and its hit share one moment, in the breath before
    the first word (up to 0.25 s early), so the hit never masks the word and never lands off the picture."""
    i = _KEYS.index(key)
    gap = S(key) - E(_KEYS[i - 1]) if i else 0.3
    return S(key) - min(0.25, max(0.06, 0.6 * gap))


def Wd(key, word):
    """A cut on a word lands a hair before it, so the hit leads the syllable."""
    return W(key, word) - 0.08


EDIT = [
    # (start, shot name, transition in)
    (0.0, "open", "cut"),
    (S("a0") - 0.2, "launch", "cut"),
    (S("h2") - 0.3, "race", "cut"),
    (Wd("h2", "There"), "two", "split"),
    (L("d1"), "finish", "head:host"),
    (L("d2"), "chess", "head:announcer"),
    (L("d3"), "imagenet", "split"),
    (L("d4"), "fuzzy", "iris"),
    (L("d5"), "dash", "head:ai"),
    (L("d7"), "frameworks", "cut"),
    (Wd("d8", "ARC"), "arc", "split"),
    (L("e1"), "engine", "head:host"),
    (Wd("e2", "Drop"), "learner", "cut"),
    (L("e3"), "facts", "iris"),
    (L("a1"), "dinner", "head:announcer"),
    (L("t2"), "hazards", "cut"),
    (L("t3"), "skills", "split"),
    (L("t4"), "expedition", "head:ai"),
    (L("t5"), "transfer", "cut"),
    (L("t6"), "coffee", "iris"),
    (L("u1"), "hood", "head:announcer"),
    (L("u2"), "loop", "cut"),
    (L("u3"), "memory", "split"),
    (L("a2"), "h2h", "head:memorizer"),
    (Wd("v2", "Now,"), "newtrack", "cut"),
    (L("v4"), "chess2", "head:host"),
    (L("w1"), "laps", "iris"),
    (L("a3"), "joke", "head:announcer"),
    (L("f1"), "final", "head:ai"),
    (C["end_card"], "end", "iris"),
]
WIPE = 0.55          # seconds a head wipe or iris takes (centred on the cut)


def shot_at(t):
    cur = EDIT[0]
    for e in EDIT:
        if e[0] <= t:
            cur = e
    return cur


def next_start(start):
    for i, e in enumerate(EDIT):
        if e[0] == start:
            return EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total + 1.0
    return TL.total + 1.0
