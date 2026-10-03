"""Back through the door: the kitchen, then the street a year later in hand-tinted colour, the glasses, the curtain
call on the Emcee's stage, the screening placard, and the end card."""
import math

import numpy as np
import skia

import cards as KD
import cast as K
import draw as D
import props as P
import sets
import zkit as Z
from common import ZStage, cam
from cues import C
from draw import H, W, WHITE, ease, mix, paint, path, ramp
from timeline import TL
from zkit import BLACK, CHALK

S, E = TL.s, TL.e


def s_door_back(T, t, d):
    """The pantry door bangs open from inside; Mae steps back into her kitchen, glasses in her hand."""
    st = ZStage()
    c = st.c
    sets.bd(st, "kitchen_day", lambda cc: sets.kitchen(cc, day=True), tex=False)
    op = ease(ramp(t, 0.0, 0.4))
    sets.pantry_door(c, 760, 380, 280, 1120, op, lambda cc: Z.scribble(cc, 760, 380, 1040, 1500, "stars", col=(200, 200, 200), seed=3))
    k = ease(ramp(t, 0.3, d))
    K.mae(c, 880 - 380 * k, 1800, 1.15, T, pose="walk" if k < 0.95 else "stand", expr="happy")
    K.glasses(c, 880 - 380 * k + 150, 1250, 0.45, rot=20)
    return st


def s_bus(T, t, d):
    """One year later, in colour: Mae at the wheel of her school bus, glasses on, waving; kids at the windows."""
    st = ZStage()
    c = st.c
    sets.bd(st, "bus_day", sets.bus_day, tex=False)
    c.save()
    cam(c, 1.0 + 0.05 * t / max(d, 0.1), 540, 1300)
    bx, by, bs = 540, 1560, 1.05
    P.bus_front(c, bx, by, bs, T)
    r = P.windshield_mask(bx, by, bs)
    c.save()
    c.clipRect(r)
    c.drawRect(r, paint((60, 70, 80)))
    for j, x in enumerate((230, 330, 760, 860)):                        # kids in the seats behind her
        c.drawCircle(x, 820 + 20 * math.sin(T * 5 + j), 50, paint((220, 180, 150) if j % 2 else (150, 110, 90)))
        c.drawCircle(x, 780 + 20 * math.sin(T * 5 + j), 52, paint(((60, 40, 30), (200, 160, 80), (30, 30, 30), (120, 70, 40))[j]))
    K.mae(c, 540, 1540, 0.62, T, pose="wave", glasses_on=True, expr="happy", outfit="uniform")
    c.restore()
    c.restore()
    k = ease(ramp(t, 0.1, 0.4))
    Z.letters(c, "ONE YEAR LATER", 540, 360, 84 * (0.7 + 0.3 * k), "londrina-900", WHITE, T=T, seed=2, tag="later", outline=BLACK, ow=12, a=k)
    return st


def s_glasses(T, t, d):
    """Close: she pushes her glasses up her nose, and winks."""
    st = ZStage()
    c = st.c
    sets.bd(st, "bus_day", sets.bus_day, tex=False)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((240, 200, 60), 0.5))
    push = ease(ramp(t, 0.2, 0.7))
    K.mae_face(c, 540, 1380, 1.12, T, expr="happy", glasses_on=push > 0.5, wink=ramp(t, 1.0, 1.2) * (1 - ramp(t, 1.6, 1.8)))
    if push <= 0.5:
        K.glasses(c, 540, 1380 - 1.12 * 205 + 200 * (1 - push * 2), 1.12 * 1.02)
    return st


def s_curtain(T, t, d):
    """Curtain call in hand-tinted colour: the Emcee, Mae (glasses on), the Second Eye, the whole chorus; LOOK TWICE."""
    st = ZStage()
    c = st.c
    sets.bd(st, "stage_col", sets.stage)
    for j in range(5):
        K.pill(c, 110 + j * 215, 1320, 0.7, T, phase=j * 0.5, label="Rx", col=((250, 200, 200), (200, 230, 250), (250, 240, 170),
                                                                                 (200, 250, 210), (240, 210, 250))[j])
    K.emcee(c, 230, 1580, 0.86, T, pose="bow")
    K.mae(c, 540, 1580, 0.84, T, pose="wave", glasses_on=True, expr="happy", matte=True)
    K.second_eye(c, 850, 1560, 0.52, T, pose="dance", glasses_on=False)
    k = ease(ramp(t, 0.2, 0.6))
    Z.letters(c, "LOOK TWICE", 540, 520, 150 * (0.8 + 0.2 * k), "limelight-400", (255, 230, 90), T=T, seed=9, tag="twice",
              outline=BLACK, ow=16, a=k, jitter=0.5)
    return st


def s_screening(T, t, d):
    st = ZStage()
    c = st.c
    sets.bd(st, "stage_col", sets.stage)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK, 0.35))
    P.placard(c, 540, 640, 900, ["45 OR OLDER?", "ask about colon screening"], "U.S. Preventive Services Task Force, 2021", T,
              k=ease(ramp(t, 0.0, 0.3)), seed=61, size=100)
    K.second_eye(c, 540, 1540, 0.6, T, pose="dance", look=(0.0, -0.5))
    return st


def s_end(T, t, d):
    st = ZStage()
    KD.end_card(st.c, T, T - t)
    return st
