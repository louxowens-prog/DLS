"""The edit: every shot, when it starts, and how we get into it.

Transitions (the comic grammar):
  cut     a hard cut on a hit
  impact  two frames of a flat-colour impact flash, then the new shot
  slide   the new panel slides in over the old one, with an ink edge and a gutter
  glitch  a dimensional tear: RGB split, displaced slices, shards and flicker (for jumps between worlds)
Both the picture (shots.py) and the soundtrack (audio.py) read this list.
"""
from cues import C
from timeline import TL

S, E, W = TL.s, TL.e, TL.word

EDIT = [
    # (start, shot, transition in)
    (0.0, "gold", "cut"),
    (S("h2") - 0.12, "clock", "impact"),
    (S("h4") - 0.15, "hookq", "glitch"),
    (S("r1") - 0.35, "road", "slide"),
    (S("s1") - 0.25, "speed", "slide"),
    (C["scratch1"], "jagged", "cut"),
    (S("d1") - 0.35, "noir", "glitch"),
    (S("d2") - 0.12, "anime", "glitch"),
    (S("d3") - 0.22, "clash", "glitch"),
    (S("a1") - 0.45, "agi", "slide"),
    (S("a2") - 0.12, "nosleep", "impact"),
    (S("a4") - 0.12, "copies", "cut"),
    (S("a5") - 0.1, "evolve", "slide"),
    (S("a6") - 0.35, "question", "glitch"),
    (S("x1") - 0.45, "routes", "slide"),
    (S("x3") - 0.1, "bar", "cut"),
    (C["scratch2"], "summary", "glitch"),
    (S("f7") - 0.35, "outro", "slide"),
    (C["end_card"], "end", "glitch"),
]
GLITCH = 0.5          # seconds a dimensional glitch takes (centred on the cut)
SLIDE = 0.3           # seconds a panel takes to slide in


def shot_at(t):
    cur = 0
    for i, e in enumerate(EDIT):
        if e[0] <= t:
            cur = i
    return cur
