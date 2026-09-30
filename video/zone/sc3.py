"""ROOM 4: BEFORE THE SYMPTOMS (early warnings, a false alarm, the caveats) and ROOM 5: THE SECOND LOOK (Mae's
colonoscopy: all clear, silence, the flag, found early)."""
import math

import numpy as np
import skia

import cast as K
import draw as D
import props as P
import sets
import zkit as Z
from common import ZStage, cam
from cues import C, SL, Wx
from draw import H, W, WHITE, ease, mix, paint, path, ramp
from script import PLATES
from timeline import TL
from zkit import BLACK, CHALK

S, E = TL.s, TL.e


# ------------------------------------------------------------------ ROOM 4

def s_ballroom(T, t, d):
    """Her Majesty the Early Bird holds court under the painted dawn; the Emcee presents."""
    st = ZStage()
    c = st.c
    sets.bd(st, "ballroom", sets.ballroom)
    K.early_bird(c, 820, 1500, 0.9, T)
    K.emcee(c, 230, 1580, 0.9, T, pose="present")
    K.mae(c, 520, 1590, 0.66, T, pose="stand", expr="happy", matte=True)
    P.placard(c, 540, 470, 820, ["EARLIER", "= more ways to treat"], None, T, k=ease(ramp(T, Wx("d1", "Earlier") - 0.2, Wx("d1", "Earlier") + 0.2)),
              seed=21, size=84)
    return st


def _kickline(c, T, y=1760, s=0.95, kinds=("pill", "skel", "pill", "skel", "pill")):
    for j, kd in enumerate(kinds):
        x = 130 + j * 205
        if kd is None:
            continue
        if kd == "pill":
            K.pill(c, x, y, s, T, phase=j * 0.5, label="Rx")
        else:
            K.skeleton(c, x, y, s * 0.42, T, phase=j * 0.5)


def s_s4_open(T, t, d):
    st = ZStage()
    c = st.c
    sets.bd(st, "ballroom", sets.ballroom)
    K.early_bird(c, 540, 1060, 0.7, T)
    _kickline(c, T, y=1420, s=0.8, kinds=("pill", "skel", None, "skel", "pill"))
    K.mae(c, 540, 1430, 0.55, T, pose="kick" if (T * 176 / 60) % 2 < 1 else "both_up", expr="happy", matte=True)
    return st


def _plate_shot(idx, pic=None):
    def f(T, t, d):
        st = ZStage()
        c = st.c
        sets.bd(st, "ballroom", sets.ballroom)
        c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK, 0.25))
        lines, src = PLATES[("s4", idx)]
        P.placard(c, 540, 700, 900, lines, src, T, k=ease(ramp(t, 0.0, 0.25)), seed=30 + idx, size=86)
        if pic:
            P.picture(c, pic, 540, 1120, 420, 300, T)
        _kickline(c, T, y=1800, s=0.8)
        return st
    return f


s_s4_sepsis = _plate_shot(1)
s_s4_kidney = _plate_shot(2)
s_s4_ecg = _plate_shot(3, "ecg")
s_s4_eye = _plate_shot(4, "retina")


def s_s4_roof(T, t, d):
    """Fix the roof before the rain: the Second Eye patches a painted roof under a cardboard rain cloud."""
    st = ZStage()
    c = st.c
    sets.bd(st, "ballroom", sets.ballroom)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK, 0.3))
    Z.blob(c, [(200, 1500), (200, 1100), (880, 1100), (880, 1500)], (200, 196, 188), T, 3, smooth=False)
    Z.blob(c, [(140, 1120), (540, 800), (940, 1120)], (90, 88, 86), T, 4, smooth=False)
    c.drawRect(skia.Rect.MakeLTRB(470, 1300, 610, 1500), paint(BLACK))
    k = ease(ramp(t, 0.2, 0.9))
    c.drawRect(skia.Rect.MakeLTRB(420, 930, 420 + 200 * k, 990), paint(WHITE))                     # the patch
    c.drawRect(skia.Rect.MakeLTRB(420, 930, 420 + 200 * k, 990), paint(BLACK, stroke=5))
    for cx in (330, 540, 750):                                          # the cloud, held back
        Z.circ(c, cx - 60 * (1 - k), 460, 130, (150, 148, 144), T, int(cx))
    rng = np.random.default_rng(int(T * 12))
    for i in range(30):
        x = rng.uniform(150, 930)
        y = 560 + ((T * 900 + i * 50) % 300)
        c.drawLine(x, y, x - 10, y + 40, paint(WHITE, 0.7 * (1 - k), stroke=4))
    K.second_eye(c, 860, 1540, 0.5, T, look=(-0.5, -0.6), pose="dance")
    return st


def s_false_alarm(T, t, d):
    """The Alarm Rooster crows at a perfectly healthy dancing pill. The band stops dead. The pill shrugs."""
    st = ZStage()
    c = st.c
    sets.bd(st, "ballroom", sets.ballroom)
    crow = ramp(T, C["crow"] - 0.1, C["crow"]) * (1 - ramp(T, C["crow"] + 0.9, C["crow"] + 1.1))
    K.rooster(c, 330, 1450, 1.1, T, crow=crow)
    frozen = T > C["crow"] + 0.2
    K.pill(c, 800, 1450, 1.2, C["crow"] + 0.2 if frozen else T, label="OK")
    ka = ease(ramp(T, C["crow"] + 0.1, C["crow"] + 0.3))
    if ka > 0:
        Z.letters(c, "FALSE ALARM!", 560, 760, 110 * ka, "londrina-900", WHITE, T=T, seed=8, tag="false", outline=BLACK, ow=14)
    return st


def s_caveat(T, t, d):
    """Placards: one sepsis alarm missed two-thirds of cases in an outside test; skin tools trained on light skin
    miss more on dark skin."""
    st = ZStage()
    c = st.c
    sets.bd(st, "ballroom", sets.ballroom)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK, 0.45))
    k1 = ease(ramp(T, Wx("d3", "sepsis") - 0.3, Wx("d3", "sepsis")))
    P.placard(c, 540, 760, 900, ["ONE SEPSIS ALARM", "missed 2 of 3 cases", "in an outside test"],
              "Wong et al. · JAMA Internal Medicine, 2021", T, k=k1, seed=41, size=100)
    K.rooster(c, 170, 1560, 0.45, T, crow=0.0)
    return st


def s_caveat_b(T, t, d):
    st = ZStage()
    c = st.c
    sets.bd(st, "ballroom", sets.ballroom)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK, 0.45))
    P.placard(c, 540, 760, 900, ["SKIN AI", "trained on light skin", "misses more on dark skin"],
              "Daneshjou et al. · Science Advances, 2022", T, k=ease(ramp(t, 0.0, 0.2)), seed=42, size=100)
    P.picture(c, "skin", 300, 1230, 260, 200, T)
    P.picture(c, "skin", 780, 1230, 260, 200, T)
    return st


def s_charge(T, t, d):
    """Test them like medicines: a doctor (live) in charge, the Second Eye at her elbow."""
    st = ZStage()
    c = st.c
    sets.bd(st, "ballroom", sets.ballroom)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK, 0.3))
    K.doctor(c, 330, 1600, 0.98, T, pose="hips", expr="calm", seed=12, hair="short", haircol=(30, 28, 26), skin=(150, 110, 88))
    K.second_eye(c, 820, 1540, 0.55, T, look=(-0.6, -0.3), pose="dance")
    P.placard(c, 540, 360, 880, ["TEST IT LIKE A MEDICINE", "and keep a doctor in charge"], None, T,
              k=ease(ramp(t, 0.1, 0.4)), seed=43, size=76)
    return st


# ------------------------------------------------------------------ ROOM 5

def s_clinic(T, t, d):
    """Mae asleep on the table; a masked doctor at the scope; the Second Eye, in her glasses, watching the monitor."""
    st = ZStage()
    c = st.c
    sets.bd(st, "clinic", sets.clinic)
    P.monitor(c, 470, 420, 400, 300, lambda cc: _mini_tunnel(cc, T, 400, 300, lesion=False))
    K.second_eye(c, 670, 396, 0.36, T, look=(-0.3, 0.9), pose="stand")                               # perched on the monitor
    K.doctor(c, 900, 1500, 0.85, T, pose="reach", masked=True, seed=14)
    K.mae_asleep(c, 610, 1230, 1.35, T)
    return st


def s_tunnel(T, t, d):
    """The scope's view, a painted tunnel ride through the folds; all clear so far. Then nothing moves but us."""
    st = ZStage()
    c = st.c
    sets.tunnel(c, T, tunnel_u(T), lesion=True, flag=0.0, reveal=0.0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 900), 900, [(0, 0, 0, 0.0), (0, 0, 0, 0.0), (0, 0, 0, 0.9)], [0, 0.6, 1])))
    return st


def s_flag(T, t, d):
    """This tiny region deserves another look: the box snaps onto a flat growth hiding in a fold (painted green)."""
    st = ZStage()
    c = st.c
    c.save()
    cam(c, 1.0 + 0.25 * ease(ramp(t, 0.6, 1.8)), 790, 1070)
    sets.tunnel(c, T, tunnel_u(min(T, C["flag"])), lesion=True, flag=ramp(T, C["flag"], C["flag"] + 0.25), tint=st.t,
                reveal=ramp(T, C["flag"] + 0.1, C["flag"] + 0.6))
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 900), 900, [(0, 0, 0, 0.0), (0, 0, 0, 0.0), (0, 0, 0, 0.9)], [0, 0.6, 1])))
    k = ease(ramp(T, C["flag"] + 0.1, C["flag"] + 0.4))
    if k > 0:
        Z.letters(c, "TAKE ANOTHER LOOK", 540, 470, 84 * k, "londrina-900", WHITE, T=T, seed=5, tag="flagt", outline=BLACK, ow=12)
    return st


def tunnel_u(T):
    """How far down the tunnel we are: gliding while the doctor talks, then barely creeping in the silence."""
    from edit import first
    tf, stop = first("tunnel"), S("f2") + 1.3
    return 0.9 * (min(T, stop) - tf) + 0.25 * max(0.0, T - stop)


def s_doclook(T, t, d):
    """The doctor leans to the monitor: flat, hiding in a fold, easy to miss."""
    st = ZStage()
    c = st.c
    sets.bd(st, "clinic", sets.clinic)
    P.monitor(c, 480, 380, 520, 400, lambda cc: _mini_tunnel(cc, T, 520, 400))
    K.doctor(c, 330, 1600, 1.0, T, pose="point", masked=True, seed=14)
    K.second_eye(c, 860, 1540, 0.45, T, look=(-0.3, -0.9), pose="dance")
    return st


def _mini_tunnel(c, T, w, h, lesion=True):
    """The monitor's picture: the same tunnel, small."""
    s = skia.Surface(W, H)
    cc = s.getCanvas()
    sets.tunnel(cc, T, tunnel_u(min(T, C["flag"])), lesion=lesion, flag=1.0 if lesion else 0.0, reveal=1.0)
    img = s.makeImageSnapshot()
    c.save()
    c.scale(w / 900, h / 700)
    c.translate(-110, -560)
    c.drawImage(img, 0, 0)
    c.restore()


def s_halved(T, t, d):
    st = ZStage()
    c = st.c
    sets.bd(st, "clinic", sets.clinic)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK, 0.4))
    P.placard(c, 540, 520, 900, ["GROWTHS MISSED", "without AI: 32%"], None, T, k=ease(ramp(t, 0.0, 0.3)), seed=51, size=110)
    K.doctor(c, 540, 1660, 0.74, T, pose="shrug", masked=True, seed=14)
    return st


def s_halved_b(T, t, d):
    st = ZStage()
    c = st.c
    sets.bd(st, "clinic", sets.clinic)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK, 0.4))
    P.placard(c, 540, 700, 900, ["WITH AI: 15.5%", "about half as many missed"], "Wallace et al. · Gastroenterology, 2022", T,
              k=ease(ramp(t, 0.0, 0.2)), seed=52, size=110)
    K.second_eye(c, 540, 1540, 0.6, T, look=(0.0, -0.6), pose="dance")
    return st


def s_s5_found(T, t, d):
    """FOUND IT EARLY: every creature in the film in one kick line, confetti, the Emcee out front."""
    st = ZStage()
    c = st.c
    sets.bd(st, "stage", sets.stage)
    K.skeleton(c, 110, 1300, 0.38, T, phase=0.0)
    K.octopus(c, 330, 1300, 0.42, T)
    K.emcee(c, 190, 1580, 0.9, T, pose="kick")
    K.king_heme(c, 610, 1320, 0.65, T, tint=st.t)
    K.pill(c, 800, 1300, 0.8, T, phase=0.5, label="Rx")
    K.rooster(c, 960, 1300, 0.42, T)
    K.second_eye(c, 800, 1580, 0.5, T, pose="dance")
    K.mae(c, 470, 1600, 0.62, T, pose="both_up", glasses_on=False, expr="happy", matte=True)
    rng = np.random.default_rng(3)
    for i in range(80):
        x = rng.uniform(0, W)
        y = ((T * rng.uniform(150, 300) + rng.uniform(0, H)) % (H + 100)) - 50
        c.save()
        c.translate(x, y)
        c.rotate(T * 200 + i * 30)
        col = tuple(int(v) for v in rng.uniform(80, 255, 3))
        c.drawRect(skia.Rect.MakeLTRB(-10, -6, 10, 6), paint(col))
        c.restore()
    return st


def s_doors(T, t, d):
    """Two painted doors: FOUND EARLY (9 in 10 alive at five years) and FOUND LATE (1 in 8). Mae walks to the first."""
    st = ZStage()
    c = st.c
    sets.bd(st, "stage", sets.stage)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK, 0.35))
    ke = ease(ramp(T, C["early_door"] - 0.2, C["early_door"] + 0.3))
    kl = ease(ramp(T, C["late_door"] - 0.2, C["late_door"] + 0.3))
    P.door2(c, 110, 760, 360, 620, "FOUND EARLY", "9 in 10 alive at 5 years", ke * 0.9, T, seed=1, lit=True)
    P.door2(c, 610, 760, 360, 620, "SPREAD FAR", "about 1 in 8 at 5 years", 0.0, T, seed=3, lit=False)
    Z.tinted(st.t, c, lambda tt: tt.drawRect(skia.Rect.MakeLTRB(110, 760, 470, 1380), paint((250, 210, 60), 0.6 * ke)))
    if kl < 0.5:
        pass
    else:
        c.drawRect(skia.Rect.MakeLTRB(610, 760, 970, 1380), paint(BLACK, 0.4 * kl))
    x = 700 - 400 * ease(ramp(t, 0.8, d - 0.3))
    K.mae(c, x, 1860, 0.72, T, pose="walk", expr="calm", matte=True)
    D.text(c, "5-year survival, colon cancer · American Cancer Society / SEER", 540, 520, 34, "londrina-400", CHALK, tag="src")
    return st
