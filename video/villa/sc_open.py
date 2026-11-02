"""The opening: a porcelain graduate with nothing inside; the title; the square at nine o'clock, its automaton
scholars marching out for their diplomas; Clara, alone."""
import math

import numpy as np
import skia

import cast as CA
import gel as G
import kit as K
import props as PR
import sets as SE
from common import E, Layers, S, Wx, blink, talk, zoom
from edit import cut, end
from kit import AMBER, BLACK, COBALT, EMERALD, MAGENTA, H, W, mix, paint, ramp


def s_h_doll(T, idx):
    """Top marks. A perfect degree. And inside... nothing. The zoom lens creeps into a porcelain graduate's face; it
    cracks; a shard falls away onto black; the lens dives into the hole."""
    st = K.Stage((4, 2, 6))
    c = st.c
    G.pool(c, 220, 520, 760, (150, 20, 90), 0.55)
    G.pool(c, 900, 1400, 700, (30, 40, 160), 0.45)
    # a gilded frame behind, holding a diploma, out of focus
    c.save()
    PR.frame_gilt(c, 120, 260, 960, 1300, t=40, a=0.6)
    c.restore()
    t_in = Wx("h1", "inside")
    t_no = S("h2")
    t_end = cut("t_title")
    crack = 0.5 * K.ease(ramp(T, t_in - 0.1, t_in + 0.45)) + 0.5 * ramp(T, t_no - 0.05, t_no + 0.55)
    dive = ramp(T, t_end - 0.55, t_end)
    z = zoom(c, T, 0.0, t_no, 1.0, 1.32, cx=555, cy=860)
    if dive > 0:
        c.translate(570, 845)
        k = 1 + 9 * dive ** 2.2
        c.scale(k, k)
        c.translate(-570, -845)
    CA.face(c, 540, 870, 2.25, "doll", T, L=(255, 40, 160), R=(70, 100, 255), core=0.45, expr="blank", porc=1.0, crack=crack,
            amb=(40, 30, 46), gaze=(0.0, 0.05))
    c.restore()
    if dive > 0.7:
        c.drawPaint(paint((0, 0, 0), min(1.0, (dive - 0.7) / 0.3)))
    return st.arr


def s_t_title(T, idx):
    """THE HOLLOW SCHOLARS, in thin Italian capitals, out of the black."""
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("t_title")
    a = K.ease(ramp(T, t0 + 0.1, t0 + 0.7)) * (1 - ramp(T, end("t_title") - 0.25, end("t_title")))
    zoom(c, T, t0, end("t_title"), 1.0, 1.07, cx=540, cy=900)
    G.pool(c, 540, 900, 520, (140, 20, 70), 0.3 * a)
    K.text(c, "THE HOLLOW", 540, 860, 128, "italiana-400", (246, 232, 214), tag="title", a=a)
    K.text(c, "SCHOLARS", 540, 1010, 168, "italiana-400", (246, 232, 214), tag="title", a=a)
    c.drawLine(380, 1060, 700, 1060, paint((200, 30, 50), a, stroke=3))
    c.restore()
    return st.arr


def _parade(T):
    t0 = cut("q_square") + 0.6
    us = []
    for k in range(5):
        us.append((T - t0 - k * 0.55) * 0.42)
    return us


def s_q_square(T, idx):
    """Nine o'clock. The square at dusk; the zoom lens creeps toward the clock as it strikes."""
    st = K.Stage()
    c = st.c
    t0 = cut("q_square")
    zoom(c, T, t0, end("q_square") + 0.5, 1.0, 1.32, cx=540, cy=700)
    doors = K.ease(ramp(T, t0 + 0.5, t0 + 1.2))
    SE.square(c, T, doors=doors, parade=_parade(T), group=ramp(T, t0, end("q_clara")), clara=(470, 1492, 0.9),
              birds=T - (t0 + 0.4))
    c.restore()
    ka = K.ease(ramp(T, t0 + 0.5, t0 + 1.0)) * (1 - ramp(T, end("q_square") - 0.35, end("q_square")))
    if ka > 0:                                                  # the location super, as the old films did it
        K.text(c, "ITALIA, 1974", 540, 330, 64, "italiana-400", (250, 240, 226), tag="title", a=ka, outline=(20, 10, 24), ow=6)
    return st.arr


def s_q_clock(T, idx):
    """...and its little scholars march out for their diplomas: the automaton's stage, close."""
    st = K.Stage()
    c = st.c
    t0 = cut("q_clock")
    zoom(c, T, t0, end("q_clock"), 3.0, 3.6, cx=540, cy=850)
    SE.square(c, T, doors=1.0, parade=_parade(T), group=1.0)
    c.restore()
    return st.arr


def s_q_clara(T, idx):
    """Clara turns: her group is gone. Hello? The square behind her in soft colours."""
    L = Layers(2)
    t0 = cut("q_clara")
    bg = L.c(0)
    zoom(bg, T, t0, end("q_clara"), 2.2, 2.3, cx=640, cy=1250)
    SE.square(bg, T, doors=1.0, parade=None, group=1.0)
    bg.restore()
    fg = L.c(1)
    zoom(fg, T, t0, end("q_clara"), 1.0, 1.12, cx=540, cy=820)
    look = -0.6 + 1.2 * K.ease(ramp(T, t0, t0 + 0.6))
    CA.face(fg, 540, 860, 1.85, "clara", T, L=(255, 50, 160), R=(40, 220, 140), core=0.5, expr="dread",
            talk=talk(T, "CLARA"), blink=blink(T, 2), gaze=(look, -0.1))
    fg.restore()
    return L.compose(1.0, strength=14.0)
