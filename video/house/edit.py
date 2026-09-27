"""The edit: every shot, when it starts, and how we get into it (a new picture every two or three seconds).

Transitions:
  cut     a hard cut on a hit
  iris    the old shot closes to a black circle, the new one opens out of it
  flip    a scrapbook page turns
  card    a silent-film title card
Split screens, freeze frames and album inserts happen inside the shots themselves.
Both the picture (shots.py) and the soundtrack (audio.py) read this list.
"""
from cues import C
from timeline import TL

S, E, W = TL.s, TL.e, TL.word

EDIT = [
    (0.0, "cold1", "cut"),                            # cold open: a flash-forward to the end of the true story
    (C["cold2"] - 0.1, "cold2", "cut"),
    (S("h1") - 0.08, "hook", "cut"),
    (C["eaten"], "eaten", "cut"),
    (S("h3") - 0.12, "title", "iris"),
    (W("h3", "And") - 0.1, "sure", "cut"),
    (S("l1") - 0.12, "album1", "cut"),
    (W("l1", "Invented") - 0.15, "album2", "flip"),
    (W("l1", "Broken") - 0.15, "album3", "flip"),
    (S("w1") - 0.12, "machine", "iris"),
    (C["reels"] - 0.1, "reels", "cut"),
    (C["ticket"] - 0.1, "ticket", "cut"),
    (S("w2") - 0.1, "exam", "cut"),
    (C["star"] - 0.1, "grade", "cut"),
    (S("w3") - 0.12, "always", "cut"),
    (S("c1") - 0.15, "court", "iris"),
    (W("c1", "chatbot") - 0.2, "brief", "cut"),
    (W("c1", "They") - 0.1, "ask", "cut"),
    (C["gavel"], "fine", "card"),
    (C["pile"], "pile", "cut"),
    (S("c3") - 0.12, "plane", "iris"),
    (C["pay"] - 0.1, "pay", "cut"),
    (S("p1") - 0.2, "mirror", "iris"),
    (S("p2") - 0.12, "kitchen", "cut"),
    (C["typed"] - 0.1, "typing", "cut"),
    (S("p3") - 0.1, "answer", "cut"),
    (C["bromide"] + 0.25, "cateyes", "cut"),
    (C["nowarn"] - 0.1, "nowarning", "cut"),
    (S("p5") - 0.12, "parcel", "cut"),
    (W("p5", "and") - 0.1, "sprinkle", "cut"),
    (W("p5", "Every") - 0.1, "calendar", "cut"),
    (S("p6") - 0.1, "bed", "cut"),
    (W("p6", "Your") - 0.1, "skin", "cut"),
    (C["neighbor"] - 0.3, "neighbor", "cut"),        # the horror cut lands in silence, before a word is said
    (C["see"] - 0.25, "visions", "cut"),
    (S("p8") - 0.1, "run", "cut"),
    (C["hold"] - 0.1, "hold", "iris"),
    (S("p9") - 0.15, "doctor", "cut"),
    (S("p10") - 0.12, "weeks", "cut"),
    (E("p10") + 0.35, "realcase", "card"),            # a black card held in silence, then 'This isn't a story.'
    (W("p11", "It") - 0.1, "casefile", "cut"),
    (W("p11", "doctors") - 0.3, "casezoom", "cut"),
    (S("p12") - 0.1, "doctest", "cut"),
    (S("s1") - 0.12, "onedoc", "iris"),
    (S("s2") - 0.12, "clones", "cut"),
    (C["atonce"] - 0.1, "clones_red", "cut"),
    (S("s3") - 0.12, "globe", "iris"),
    (S("s4") - 0.12, "hundred", "cut"),
    (W("s4", "that's") - 0.1, "counter", "cut"),
    (C["second"] - 0.1, "tick", "cut"),
    (S("s5") - 0.15, "thatclock", "iris"),
    (S("r1") - 0.12, "report", "cut"),
    (W("r1", "flags") - 0.1, "three", "cut"),
    (C["now"] - 0.1, "burn", "cut"),
    (S("r2") - 0.1, "crack", "cut"),
    (S("t1") - 0.12, "rumor", "iris"),
    (W("t1", "Ask") - 0.1, "source", "cut"),
    (S("t2") - 0.12, "doors", "cut"),
    (S("e1") - 0.15, "payoff", "iris"),
    (W("e1", "about") - 0.1, "count", "cut"),
    (E("e1") + 0.3, "trust", "cut"),
    (C["end"], "end", "card"),
]
IRIS = 0.42          # an iris: 0.21 s closing on the old shot, 0.21 s opening on the new
FLIP = 0.28          # a page turn


def shot_at(t):
    cur = 0
    for i, e in enumerate(EDIT):
        if e[0] <= t:
            cur = i
    return cur


def first(name):
    return next(t for t, n, _ in EDIT if n == name)
