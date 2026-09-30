"""The real world (the kitchen, the phone, ten years of lab slips, the glove in the pantry door), the fall, the title,
and ROOM 1: THE HALL OF PICTURES (a second pair of eyes)."""
import math

import numpy as np
import skia

import cards as KD
import cast as K
import draw as D
import props as P
import sets
import zkit as Z
from common import ZStage, cam, cams, restore, save
from cues import C, CARDS, SL, Wx
from draw import H, W, WHITE, ease, mix, paint, path, ramp
from timeline import TL
from zkit import BLACK, CHALK

S, E = TL.s, TL.e
HB = [13.6, 13.5, 13.3, 13.2, 13.0, 12.8, 12.7, 12.5, 12.3, 12.1]        # Mae's hemoglobin, g/dL, 2016..2025 (all "normal")
YEARS = list(range(2016, 2026))


# ------------------------------------------------------------------ the real world

def s_phone(T, t, d):
    """Close on the kitchen table: her phone buzzes, a message lights it."""
    st = ZStage()
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.lin((0, 0), (0, H), [(150, 128, 108), (100, 84, 70)])))
    for k in range(9):
        c.drawLine(0, 200 + k * 200, W, 150 + k * 200, paint((120, 100, 84), 0.5, stroke=3))           # the grain of the table
    c.drawCircle(860, 1500, 150, paint((236, 234, 230)))                                             # a mug
    c.drawCircle(860, 1500, 110, paint((70, 50, 40)))
    c.save()
    cam(c, 1.0 + 0.05 * t / max(d, 0.1), 500, 900)
    P.phone(c, 500, 900, 1.35, T, lit=T > C["buzz"], buzz=float(0.15 < T % 1.2 < 0.7),
            msg=["CLINIC", "Your blood tests", "over 10 years", "show a pattern.", "Please come in", "this week."])
    c.restore()
    return st


def s_mae_phone(T, t, d):
    st = ZStage()
    c = st.c
    sets.bd(st, "kitchen", sets.kitchen, tex=False)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.25))
    K.mae_face(c, 520, 1330, 1.0, T, expr="puzzled", look=(0.5, 0.2))
    P.phone(c, 820, 1040, 0.5, T, lit=True, msg=None)
    return st


def s_slips(T, t, d):
    """Ten years of lab slips spread on the table, every one stamped NORMAL."""
    st = ZStage()
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.lin((0, 0), (0, H), [(150, 128, 108), (100, 84, 70)])))
    c.save()
    cam(c, 1.0 + 0.04 * t / max(d, 0.1), 540, 960)
    rng = np.random.default_rng(2)
    for i, (yr, hb) in enumerate(zip(YEARS, HB)):
        k = ease(ramp(t, 0.15 * i, 0.15 * i + 0.3))
        if k <= 0:
            continue
        x = 150 + (i % 4) * 260 + rng.uniform(-20, 20)
        y = 470 + (i // 4) * 380 + rng.uniform(-20, 20)
        P.slip(c, x, y - 60 * (1 - k), 0.8, yr, f"{hb}", T, rot=rng.uniform(-10, 10), stamp_k=ease(ramp(t, 0.15 * i + 0.25, 0.15 * i + 0.4)))
    c.restore()
    return st


def s_scan(T, t, d):
    """The same ten slips, lined up; a bright bar reads all ten at once and a line joins them, sloping down."""
    st = ZStage()
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.lin((0, 0), (0, H), [(150, 128, 108), (100, 84, 70)])))
    for i, (yr, hb) in enumerate(zip(YEARS, HB)):
        P.slip(c, 140 + (i % 5) * 200, 560 + (i // 5) * 330, 0.62, yr, f"{hb}", T, rot=0, stamp_k=1.0)
    k = ramp(t, 0.1, 1.0)
    x = -50 + (W + 100) * k
    c.drawRect(skia.Rect.MakeLTRB(x - 30, 440, x + 30, 1020), paint(WHITE, 0.7, blur=12))
    kl = ease(ramp(t, 0.7, 1.6))
    if kl > 0:
        pts = [(120 + i * 93, 1130 + (13.6 - hb) * 140) for i, hb in enumerate(HB)]
        n = max(2, int(kl * 10))
        c.drawPath(path(pts[:n], closed=False), paint((250, 250, 250), stroke=8))
        for p in pts[:n]:
            c.drawCircle(*p, 10, paint(WHITE))
        Z.tinted(st.t, c, lambda tt: tt.drawPath(path(pts[:n], closed=False), paint((230, 40, 40), 0.9, stroke=24)))
    return st


def _pantry_inside(T, beckon=1.0, hand=True):
    def fn(c):
        Z.scribble(c, 760, 500, 1040, 1500, "spiral", col=(90, 90, 90), seed=5, a=0.7)
        if hand:
            c.drawCircle(900, 900, 220, paint(WHITE, 0.12, blur=60))
            K.gloved_hand(c, 860, 900, 0.8, T, rot=8, beckon=beckon, flip=True)
    return fn


def s_search(T, t, d):
    """Mae pats her pockets; behind her the pantry door creaks open on a dark full of painted spirals."""
    st = ZStage()
    c = st.c
    sets.bd(st, "kitchen", sets.kitchen, tex=False)
    op = ease(ramp(T, C["door_open"], C["door_open"] + 0.8))
    sets.pantry_door(c, 760, 380, 280, 1120, op, _pantry_inside(T, beckon=ramp(T, C["hand"], C["hand"] + 0.3), hand=T > C["hand"]))
    K.mae(c, 400, 1800, 1.18, T, pose="search", expr="puzzled")
    return st


def s_hand(T, t, d):
    """The glove, close: it dangles her glasses and beckons. Follow the glasses, Mae."""
    st = ZStage()
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((70, 64, 58)))
    c.drawRect(skia.Rect.MakeLTRB(160, 200, 920, 1720), paint((6, 6, 6)))
    Z.scribble(c, 160, 200, 920, 1720, "spiral", col=(80, 80, 80), seed=7, a=0.6)
    c.drawCircle(560, 900, 420, paint(WHITE, 0.16, blur=120))           # a shaft of light from the kitchen
    c.save()
    cam(c, 1.0 + 0.1 * t / max(d, 0.1), 540, 900)
    K.gloved_hand(c, 520, 820, 1.6, T, rot=4, beckon=1.0, flip=True)
    c.restore()
    return st


def s_fall(T, t, d):
    """Down the spiral: Mae tumbles, her glasses tumbling just ahead of her."""
    st = ZStage()
    c = st.c
    Z.spiral_bg(c, 540, 900, T, turns=6, cols=((226, 224, 216), (14, 14, 14)), speed=3.0)
    k = t / max(d, 0.1)
    c.save()
    c.translate(540 + 60 * math.sin(T * 5), 820 + 260 * k)
    c.rotate(T * 260)
    c.scale(0.95 - 0.35 * k, 0.95 - 0.35 * k)
    K.mae(c, 0, 500, 1.0, T, pose="both_up", expr="worried")
    c.restore()
    K.glasses(c, 540 - 150 * math.sin(T * 4), 1200 - 400 * k, 1.1 - 0.4 * k, rot=T * 400)
    return st


def s_title(T, t, d):
    """The Emcee's stage: she flings out an arm; THE SECOND LOOK drops in over her."""
    st = ZStage()
    c = st.c
    sets.bd(st, "stage", sets.stage)
    K.emcee(c, 540, 1760, 1.1, T, pose="present")
    KD.title_card(c, T, S("t1") + 0.3)
    return st


# ------------------------------------------------------------------ ROOM 1: THE HALL OF PICTURES

def _card(i):
    def f(T, t, d):
        st = ZStage()
        num, title, t0, t1 = CARDS[i]
        KD.intertitle(st.c, T, t0, t1, f"ROOM {num}", title, seed=i * 10)
        return st
    return f


s_card1, s_card2, s_card3, s_card4, s_card5 = (_card(i) for i in range(5))

LIST = [("X-rays", "xray"), ("CT", "ct"), ("MRI", "mri"), ("eye", "retina"), ("skin", "skin"), ("slides", "slide"), ("heart", "ecg")]
LABELS = {"xray": "X-RAY", "ct": "CT", "mri": "MRI", "retina": "EYE SCAN", "skin": "SKIN", "slide": "PATHOLOGY", "ecg": "HEART TRACING"}


def s_hall(T, t, d):
    """The skeleton chorus files in, each holding up a picture as the Emcee names it."""
    st = ZStage()
    c = st.c
    sets.bd(st, "hall", sets.hall)
    slots = [(170, 1010), (400, 1010), (630, 1010), (860, 1010), (280, 1390), (540, 1390), (800, 1390)]
    order = [0, 1, 2, 3, 4, 5, 6]
    for j, (word, kind) in enumerate(LIST):
        tw = Wx("a1", word) - 0.15
        k = ease(ramp(T, tw, tw + 0.25))
        if k <= 0:
            continue
        x, y = slots[order[j]]
        s = 0.4
        K.skeleton(c, x, y + 260 * (1 - k), s, T, phase=j * 0.3,
                   frame=lambda cc, kind=kind: P.picture(cc, kind, 0, -60, 420, 330, T))
        Z.letters(c, LABELS[kind], x, y - 1110 * s + 260 * (1 - k), 40, "londrina-900", WHITE, T=T, seed=j, tag=f"hl{j}",
                  outline=BLACK, ow=8)
    return st


def s_reader(T, t, d):
    """A radiologist (live) at a reading desk: films flip past faster and faster; a stopwatch reads 3 seconds."""
    st = ZStage()
    c = st.c
    sets.bd(st, "hall", sets.hall)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK, 0.35))
    kinds = ["xray", "ct", "mri", "mammo", "xray", "ct", "retina", "mri"]
    i = int(t * 6) % len(kinds)
    P.picture(c, kinds[i], 540, 560, 560, 460, T)
    K.doctor(c, 300, 1880, 1.05, T, pose="write", expr="worried", seed=5, hair="short", haircol=(40, 36, 34))
    c.drawRect(skia.Rect.MakeLTRB(30, 1330, 1050, 1920), paint((58, 54, 50)))                        # the reading desk
    c.drawRect(skia.Rect.MakeLTRB(30, 1320, 1050, 1350), paint((110, 104, 98)))
    cx, cy = 800, 960                                                   # the stopwatch
    c.drawCircle(cx, cy, 120, paint(WHITE))
    c.drawCircle(cx, cy, 120, paint(BLACK, stroke=10))
    c.drawRect(skia.Rect.MakeLTRB(cx - 20, cy - 160, cx + 20, cy - 120), paint(BLACK))
    a = -math.pi / 2 + 2 * math.pi * ((t % 3.0) / 3.0)
    c.drawLine(cx, cy, cx + 95 * math.cos(a), cy + 95 * math.sin(a), paint(BLACK, stroke=8))
    Z.letters(c, "3-4 SECONDS", cx, cy + 190, 56, "londrina-900", WHITE, T=T, seed=3, tag="sec", outline=BLACK, ow=8)
    Z.letters(c, "per image", cx, cy + 240, 40, "londrina-400", WHITE, T=T, seed=4, tag="sec", outline=BLACK, ow=6)
    return st


def s_s1_dance(T, t, d):
    """TAKE ANOTHER LOOK: the Second Eye in Mae's glasses dances in front of the skeleton chorus line."""
    st = ZStage()
    c = st.c
    sets.bd(st, "hall", sets.hall)
    for j in range(5):
        K.skeleton(c, 140 + j * 200, 1250, 0.38, T, phase=j * 0.5,
                   frame=lambda cc, j=j: P.picture(cc, ["xray", "mri", "mammo", "ct", "retina"][j], 0, -60, 340, 260, T))
    K.second_eye(c, 540, 1760, 1.05, T, look=(0.3 * math.sin(T * 3), 0.1), pose="dance")
    return st


def s_s1_lung(T, t, d):
    """A chest X-ray, close: the Second Eye leans in from the side; a shadow the size of a grain of rice."""
    st = ZStage()
    c = st.c
    sets.bd(st, "hall", sets.hall)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK, 0.5))
    c.save()
    cam(c, 1.0 + 0.08 * t / max(d, 0.1), 540, 800)
    sp = P.picture(c, "xray", 520, 660, 720, 800, T, spot=True)
    c.restore()
    K.second_eye(c, 860, 1560, 0.62, T, look=(-0.8, -0.6), pose="point", target=sp)
    return st


def s_s1_spot(T, t, d):
    """Crash in on a mammogram: the glove points at one tiny speck; a red ring is painted round it."""
    st = ZStage()
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((14, 14, 14)))
    sp = P.picture(c, "mammo", 560, 700, 780, 880, T, spot=True)
    k = ease(ramp(T, C["spot"], C["spot"] + 0.35))
    if k > 0:
        r = 60 + 30 * (1 - k)
        c.drawCircle(sp[0], sp[1], r, paint(WHITE, k, stroke=8))
        Z.tinted(st.t, c, lambda tt: tt.drawCircle(sp[0], sp[1], r, paint((235, 30, 30), k, stroke=30)))
    K.second_eye(c, 200, 1560, 0.6, T, look=(0.8, -0.7), pose="point", target=(sp[0] - 60, sp[1] + 40))
    return st


def s_s1_pair(T, t, d):
    """Two pairs of eyes: the radiologist (live) and the Second Eye (cartoon) side by side at the light box."""
    st = ZStage()
    c = st.c
    sets.bd(st, "hall", sets.hall)
    sp = P.picture(c, "mammo", 540, 560, 520, 540, T, spot=True)
    c.drawCircle(sp[0], sp[1], 42, paint(WHITE, stroke=6))
    Z.tinted(st.t, c, lambda tt: tt.drawCircle(sp[0], sp[1], 42, paint((235, 30, 30), 1.0, stroke=22)))
    K.doctor(c, 320, 1580, 0.92, T, pose="point", expr="calm", seed=5, haircol=(40, 36, 34))
    K.second_eye(c, 800, 1560, 0.6, T, look=(-0.6, -0.8), pose="dance")
    return st


def s_masai(T, t, d):
    """The Swedish trial, on placards held up by the chorus."""
    st = ZStage()
    c = st.c
    sets.bd(st, "hall", sets.hall)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK, 0.3))
    P.placard(c, 540, 560, 900, ["MAMMOGRAM SCREENING", "105,000+ women, Sweden", "with AI as a second reader:"],
              None, T, k=ease(ramp(t, 0.0, 0.3)), seed=1, size=64)
    k2 = ease(ramp(T, Wx("a2", "twenty-nine") - 0.2, Wx("a2", "twenty-nine") + 0.2))
    P.placard(c, 300, 1060, 460, ["29% MORE", "cancers found"], None, T, k=k2, rot=-4, seed=2, size=74)
    k3 = ease(ramp(T, Wx("a2", "false") - 0.2, Wx("a2", "false") + 0.2))
    P.placard(c, 780, 1080, 460, ["NO MORE", "false alarms"], None, T, k=k3, rot=4, seed=3, size=74)
    k4 = ease(ramp(T, E("a2") - 1.4, E("a2") - 1.0))
    P.placard(c, 540, 1330, 700, ["44% LESS", "reading work for doctors"], "MASAI trial · Lancet Digital Health, 2025", T, k=k4,
              seed=4, size=60)
    for j, x in enumerate((110, 950)):
        K.skeleton(c, x, 1560, 0.36, T, phase=j * 0.5)
    return st


def s_decides(T, t, d):
    """The doctor signs; the Eye only points. A stamp: THE DOCTOR DECIDES."""
    st = ZStage()
    c = st.c
    sets.bd(st, "hall", sets.hall)
    sp = P.picture(c, "mammo", 700, 640, 420, 460, T, spot=True)
    K.second_eye(c, 850, 1560, 0.55, T, look=(-0.5, -0.9), pose="point", target=sp)
    K.doctor(c, 330, 1600, 0.95, T, pose="write", expr="calm", seed=5, haircol=(40, 36, 34))
    P.stamp(c, "THE DOCTOR DECIDES", 470, 1180, 78, ramp(T, C["stamp_decides"] - 0.1, C["stamp_decides"] + 0.25), rot=-8,
            tint=st.t, tint_col=(40, 120, 230))
    return st
