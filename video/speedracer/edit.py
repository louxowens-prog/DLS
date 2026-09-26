"""The edit: every shot, when it starts, and how we get into it.

Transition types (the Speed Racer grammar):
  head:<who>  a giant face slides across the frame and wipes to the next shot
  iris        a circle closes on the old shot and opens on the new one
  split       the frame slams into a split screen
  cut         a hard cut on a hit
Both the picture (shots.py) and the soundtrack (audio.py) read this list, so every transition gets a hit.
"""
from cues import C
from timeline import TL

S, E, W = TL.s, TL.e, TL.word

EDIT = [
    # (start, shot name, transition in)
    (0.0, "grid", "cut"),
    (S("h2") - 0.3, "race", "cut"),
    (W("h2", "There"), "two", "split"),
    (S("d1"), "finish", "head:host"),
    (S("d2"), "chess", "head:announcer"),
    (S("d3"), "imagenet", "split"),
    (S("d4"), "fuzzy", "iris"),
    (S("d5"), "dash", "head:ai"),
    (S("d7"), "frameworks", "cut"),
    (W("d8", "ARC"), "arc", "split"),
    (S("e1"), "engine", "head:host"),
    (W("e2", "Drop"), "learner", "cut"),
    (S("e3"), "facts", "iris"),
    (S("a1"), "dinner", "head:announcer"),
    (S("t2"), "hazards", "cut"),
    (S("t3"), "skills", "split"),
    (S("t4"), "expedition", "head:ai"),
    (S("t5"), "transfer", "cut"),
    (S("t6"), "coffee", "iris"),
    (S("u1"), "hood", "head:announcer"),
    (S("u2"), "loop", "cut"),
    (S("u3"), "memory", "split"),
    (S("a2"), "h2h", "head:memorizer"),
    (W("v2", "Now,"), "newtrack", "cut"),
    (S("v4"), "chess2", "head:host"),
    (S("w1"), "laps", "iris"),
    (S("a3"), "joke", "head:announcer"),
    (S("f1"), "final", "head:ai"),
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
