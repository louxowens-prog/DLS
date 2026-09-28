"""The edit: every shot, when it starts, and how we get into it.

Transitions (the cheap video mixer):
  cut    a hard cut
  flash  a hard cut on a white flash and a crash zoom (into horror)
  star   a star wipe: the new shot bursts out of a spinning star
  spin   the old shot tumbles away into the distance
  card   a hard cut to a variety-show chapter card
Both the picture (shots.py) and the soundtrack (audio.py) read this list."""
from cues import C, ls
from timeline import TL

S, E, W = TL.s, TL.e, TL.word

EDIT = [
    (0.0, "cold1", "cut"),
    (W("c0", "It") - 0.05, "cold2", "cut"),
    (E("c0") + 0.15, "card1", "card"),
    (S("a1") - 0.1, "family", "star"),
    (W("a1", "Don't") - 0.1, "crowsign", "cut"),
    (S("a2") - 0.1, "stamp", "cut"),
    (W("a2", "apology.") - 0.25, "bow", "cut"),
    (W("a2", "Fixed") - 0.1, "book1", "cut"),
    (E("a2") + 0.2, "card2", "card"),
    (S("b1") - 0.1, "machine", "star"),
    (S("s1"), "song1a", "spin"),
    (ls("s1_1") - 0.1, "song1b", "cut"),
    (ls("s1_2") - 0.1, "song1c", "cut"),
    (ls("s1_3") - 0.1, "song1d", "cut"),
    (S("b2") - 0.1, "flood", "flash"),
    (W("b2", "Millions.") - 0.1, "graves", "cut"),
    (S("b3") - 0.1, "rule", "cut"),
    (S("b4") - 0.1, "same", "cut"),
    (E("b4") + 0.25, "card3", "card"),
    (S("d1") - 0.1, "job", "star"),
    (S("d2") - 0.1, "letter", "cut"),
    (S("d3") - 0.1, "owe", "cut"),
    (S("d4") - 0.1, "take", "cut"),
    (W("d4", "You", 1) - 0.1, "wrong", "cut"),
    (S("d5") - 0.1, "michigan", "cut"),
    (S("d6") - 0.1, "homes", "cut"),
    (S("s2"), "card4", "card"),
    (S("s2") + 1.35, "duet", "star"),
    (E("s2"), "volcano", "cut"),
    (S("s3"), "disco_a", "flash"),
    (ls("s3_1") - 0.1, "disco_b", "cut"),
    (ls("s3_2") - 0.1, "disco_c", "cut"),
    (ls("s3_3") - 0.1, "disco_d", "cut"),
    (E("s3") + 0.08, "card5", "card"),
    (S("f1") - 0.1, "ads", "star"),
    (W("f1", "But") - 0.1, "translate", "cut"),
    (S("f2") - 0.1, "one", "cut"),
    (S("f3") - 0.1, "plane", "flash"),
    (S("f4") - 0.1, "grid", "cut"),
    (S("f5") - 0.1, "missile", "cut"),
    (S("f6") - 0.1, "radiation", "cut"),
    (E("f6") + 0.5, "card6", "card"),
    (S("g1") - 0.1, "rule2", "star"),
    (S("s4"), "finale_a", "spin"),
    (ls("s4_1") - 0.1, "finale_b", "cut"),
    (ls("s4_2") - 0.1, "finale_c", "cut"),
    (ls("s4_3") - 0.1, "finale_d", "cut"),
    (E("s4"), "payoff", "flash"),
    (E("g2") + 0.5, "end", "card"),
]
WIPE = {"star": 0.45, "spin": 0.5}
HORROR = {"cold1", "cold2", "flood", "graves", "same", "volcano", "disco_a", "disco_b", "disco_c", "disco_d", "plane",
          "grid", "missile", "radiation", "payoff", "wrong", "michigan", "homes", "one"}


def shot_at(t):
    cur = 0
    for i, e in enumerate(EDIT):
        if e[0] <= t:
            cur = i
    return cur


def first(name):
    return next(t for t, n, _ in EDIT if n == name)
