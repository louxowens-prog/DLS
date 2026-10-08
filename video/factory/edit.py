"""The edit: every shot, when it starts, and how we get into it.

Transitions of the period:
  cut       a hard cut
  dissolve  a slow cross-dissolve (0.6 s)
  iris      a black iris closes on the old shot and opens on the new one (0.9 s)
  leader    a flash of film leader (the countdown) into the newsreel
Both the picture (shots.py) and the soundtrack (audio.py) read this list."""
from cues import C, Wx, ls
from timeline import TL

S, E, W = TL.s, TL.e, TL.word

EDIT = [
    (0.0, "cold_kitchen", "cut"),
    (C["doors"] - 0.1, "cold_doors", "cut"),
    (S("c1") - 0.1, "cold_glow", "dissolve"),
    (E("c1") + 0.15, "title", "cut"),
    (S("a1") - 0.35, "town", "iris"),
    (W("a1", "Three") - 0.1, "office", "cut"),
    (W("a1", "no") - 0.1, "office_clock", "cut"),
    (S("a3") - 0.1, "kitchen", "dissolve"),
    (W("a3", "Four") - 0.1, "letter_close", "cut"),
    (S("b1") - 0.1, "shop", "cut"),
    (C["ticket_flash"] - 0.25, "wrapper", "cut"),
    (S("b2") - 0.1, "ticket", "cut"),
    (S("n1") - 0.55, "news1", "leader"),
    (S("n2") - 0.05, "news2", "cut"),
    (S("n3") - 0.05, "news_farmer", "cut"),
    (S("n4") - 0.05, "news_student", "cut"),
    (S("g1") - 0.6, "gates", "iris"),
    (S("g2") - 0.1, "host_rule", "cut"),
    (S("g3") - 0.1, "host_menace", "cut"),
    (E("g3") + 0.1, "door", "cut"),
    (ls("s1_0") - 1.0, "wonder_wide", "dissolve"),
    (ls("s1_2") - 0.1, "wonder_river", "cut"),
    (ls("s1_3") - 0.1, "wonder_pan", "cut"),
    (ls("s1_4") - 0.1, "wonder_guests", "cut"),
    (ls("s1_5") - 0.1, "wonder_host", "cut"),
    (S("r0") - 0.2, "wonder_you", "dissolve"),
    (S("h1") - 0.45, "plaque1", "dissolve"),
    (S("r1") - 0.1, "room1", "cut"),
    (W("r1", "It") - 0.1, "room1_letter", "cut"),
    (S("k1") - 0.3, "copier", "cut"),
    (S("w1"), "chant1", "cut"),
    (S("h2") - 0.45, "plaque2", "dissolve"),
    (S("r2") - 0.1, "room2", "cut"),
    (W("r2", "with") - 0.1, "room2_flag", "cut"),
    (S("r2b") - 0.1, "room2_clock", "cut"),
    (S("k2") - 0.3, "believer", "cut"),
    (S("w2"), "chant2", "cut"),
    (S("h3") - 0.45, "plaque3", "dissolve"),
    (S("r3") - 0.1, "room3", "cut"),
    (S("k3") - 0.3, "yesman", "cut"),
    (S("w3"), "chant3", "cut"),
    (S("h4") - 0.45, "plaque4", "dissolve"),
    (S("r4") - 0.1, "room4_fizz", "cut"),
    (C["plan"] - 0.6, "room4_plan", "cut"),
    (S("k4") - 0.3, "rusher", "cut"),
    (S("w4"), "chant4", "cut"),
    (E("w4") + 0.1, "tunnel_in", "iris"),
    (S("t1a") - 0.1, "tunnel", "cut"),
    (E("t1c") + 0.08, "tunnel_black", "cut"),
    (S("t2") - 0.15, "tunnel_calm", "cut"),
    (S("e1") - 0.2, "lesson", "dissolve"),
    (Wx("e1", "In") - 0.1, "lesson_study", "cut"),
    (Wx("e1", "Used") - 0.15, "lesson_well", "cut"),
    (S("p1") - 0.35, "clinic", "iris"),
    (S("p2") - 0.1, "doctor", "cut"),
    (S("p3") - 0.15, "dad_home", "dissolve"),
    (S("x1") - 0.35, "anger", "cut"),
    (S("x2") - 0.2, "warm", "cut"),
    (S("x3") - 0.1, "ticket_flip", "cut"),
    (S("z1") - 0.2, "balcony", "dissolve"),
    (S("y1") - 0.3, "story1", "iris"),
    (S("y2") - 0.1, "story2", "dissolve"),
    (S("y3") - 0.1, "story3", "dissolve"),
    (S("y4") - 0.3, "end", "dissolve"),
]
TRANS = {"dissolve": 0.6, "iris": 0.9, "leader": 0.5}
NEWSREEL = {"news1", "news2", "news_farmer", "news_student"}
GREY = {"town", "office", "office_clock", "kitchen", "letter_close", "shop", "wrapper"}   # the grey world


def shot_at(t):
    cur = 0
    for i, e in enumerate(EDIT):
        if e[0] <= t:
            cur = i
    return cur


def first(name):
    return next(t for t, n, _ in EDIT if n == name)
