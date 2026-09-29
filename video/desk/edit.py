"""The edit: every shot, when it starts, its register (which film stock prints it) and how we get into it.

Registers: present (muted colour), memory (black and white), fiction (lacquer colour), card (the chapter cards).
Transitions: clean cuts between registers; fades to black only around the chapter cards (and before the last image).
Both the picture (shots.py) and the soundtrack (audio.py) read this list."""
from cues import C, CARDS, Wx
from timeline import TL

S, E = TL.s, TL.e

EDIT = [
    # cold open
    (0.0, "teaser_type", "present", "cut"),
    (S("o0b") - 0.1, "teaser_dial", "fiction", "cut"),
    (S("o2") - 0.15, "open_lamp", "present", "cut"),
    (Wx("o2", "my") - 0.1, "open_room", "present", "cut"),
    (Wx("o2", "And") - 0.1, "open_profile", "present", "cut"),
    # ONE: CROWD
    (CARDS[0][3], "card1", "card", "fade"),
    (S("a1") - 0.25, "class", "memory", "fade"),
    (S("a3") - 0.45, "question", "memory", "cut"),
    (C["bell"] - 0.02, "bell", "memory", "cut"),
    (S("a4") + 0.45, "hand_down", "memory", "cut"),
    (S("a5") - 0.2, "window", "memory", "cut"),
    (S("a6") - 0.15, "prince", "fiction", "cut"),
    (S("a7") - 0.3, "aph1", "fiction", "cut"),
    # TWO: LIGHT
    (CARDS[1][3], "card2", "card", "fade"),
    (S("b1") - 0.25, "clock1", "present", "fade"),
    (S("b2") - 0.1, "type1", "present", "cut"),
    (S("b3") - 0.15, "car", "fiction", "cut"),
    (S("b4") - 0.15, "type2", "present", "cut"),
    (S("b5") - 0.1, "graph", "present", "cut"),
    (S("b6") - 0.1, "type3", "present", "cut"),
    (E("b6") + 0.2, "paper", "present", "cut"),
    (C["type4"] - 0.15, "type4", "present", "cut"),
    (S("b8") - 0.1, "error", "present", "cut"),
    (S("b9") - 0.1, "old_test", "memory", "cut"),
    (Wx("b9", "Not") - 0.15, "profile2", "present", "cut"),
    (S("b11") - 0.1, "montage", "present", "cut"),
    (Wx("b11", "midnight") - 0.4, "teachback", "present", "cut"),
    (S("b12") - 0.3, "aph2", "fiction", "cut"),
    # THREE: DOUBT
    (CARDS[2][3], "card3", "card", "fade"),
    (S("d1") - 0.25, "box", "fiction", "fade"),
    (S("d2") - 0.1, "study", "fiction", "cut"),
    (S("d3") - 0.15, "rule", "present", "cut"),
    (S("d4") - 0.2, "harvard", "fiction", "cut"),
    (S("d5") - 0.3, "teacher_night", "memory", "cut"),
    (S("d6") - 0.1, "cranes", "fiction", "cut"),
    (S("d7") - 0.3, "back_row", "memory", "cut"),
    # FOUR: DAWN
    (CARDS[3][3], "card4", "card", "fade"),
    (S("e1") - 0.25, "dawn", "present", "fade"),
    (S("e2") - 0.1, "lamps", "fiction", "cut"),
    (S("e3") - 0.15, "language", "fiction", "cut"),
    (S("e4") - 0.15, "nigeria", "fiction", "cut"),
    (S("e5") - 0.2, "exam", "present", "cut"),
    (S("e6") - 0.1, "q1", "present", "cut"),
    (C["smile"] - 0.15, "smile", "present", "cut"),
    (S("e7") - 0.2, "letter", "present", "cut"),
    (E("e7") + 0.35, "black", "card", "cut"),
    (S("e8") - 0.3, "final", "fiction", "cut"),
    (E("e9") + 0.7, "end", "card", "fade"),
]
FADE = 0.45


def shot_at(t):
    cur = 0
    for i, e in enumerate(EDIT):
        if e[0] <= t:
            cur = i
    return cur


def first(name):
    return next(e[0] for e in EDIT if e[1] == name)
