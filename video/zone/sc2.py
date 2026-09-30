"""ROOM 2: THE LIBRARY THAT NEVER SLEEPS (everything at once: the records and the literature) and
ROOM 3: TEN YEARS AT A GLANCE (Mae's decade, one number at a time, then all at once)."""
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
from sc1 import HB, YEARS
from timeline import TL
from zkit import BLACK, CHALK

S, E = TL.s, TL.e
FERRITIN = [96, 88, 80, 71, 62, 54, 45, 37, 29, 22]          # iron stores, ng/mL (all still in the usual range)
MCV = [92, 91, 90, 89, 88, 87, 86, 85, 84, 82]                # red-cell size, fL (normal 80-100)
PULSE = [64, 65, 66, 68, 69, 71, 72, 74, 76, 78]              # resting pulse (normal 60-100)


# ------------------------------------------------------------------ ROOM 2

DRAWERS = [("Symptoms", "SYMPTOMS"), ("pills", "PILLS"), ("lab", "LAB RESULTS"), ("old", "OLD DIAGNOSES"), ("genes", "GENES"),
           ("literature", "LITERATURE")]


def s_files(T, t, d):
    """Mae's file as a painted cabinet: each drawer shoots open as it is named; the last spills a mountain of journals."""
    st = ZStage()
    c = st.c
    sets.bd(st, "library", sets.library)
    x0, y0, w, hh = 330, 430, 560, 920
    K.mae(c, 150, 1600, 0.64, T, pose="point", expr="puzzled", matte=True)                           # "that's mine?"
    Z.cardboard(c, [(x0, y0), (x0 + w, y0 - 20), (x0 + w + 10, y0 + hh), (x0 - 6, y0 + hh + 10)], (150, 146, 140), T=T, seed=3)
    Z.letters(c, "MAE'S FILE", x0 + w / 2, y0 - 40, 64, "londrina-900", WHITE, T=T, seed=1, tag="file", outline=BLACK, ow=10)
    for j, (word, lab) in enumerate(DRAWERS):
        tw = Wx("b1", word) - 0.15
        k = ease(ramp(T, tw, tw + 0.2))
        yy = y0 + 30 + j * 145
        ox = 120 * k
        c.drawRect(skia.Rect.MakeLTRB(x0 + 30 + ox, yy, x0 + w - 30 + ox, yy + 125), paint((200, 196, 188)))
        c.drawRect(skia.Rect.MakeLTRB(x0 + 30 + ox, yy, x0 + w - 30 + ox, yy + 125), paint(BLACK, stroke=7))
        c.drawRect(skia.Rect.MakeLTRB(x0 + w / 2 - 50 + ox, yy + 92, x0 + w / 2 + 50 + ox, yy + 110), paint(BLACK))
        Z.letters(c, lab, x0 + w / 2 + ox, yy + 72, Z.fit(lab, "londrina-900", 60, w - 110), "londrina-900", BLACK if k < 0.5 else BLACK,
                  T=T, seed=j + 5, tag=f"dr{j}", a=0.35 + 0.65 * k)
    kl = ease(ramp(T, Wx("b1", "literature"), Wx("b1", "literature") + 0.6))
    if kl > 0:                                                          # the journals avalanche
        rng = np.random.default_rng(4)
        for i in range(40):
            bx = 540 + rng.uniform(-420, 420) * kl
            by = 1300 + rng.uniform(-60, 120) - 300 * (1 - kl) * rng.uniform(0.5, 1)
            c.save()
            c.translate(bx, by)
            c.rotate(rng.uniform(-40, 40))
            c.drawRect(skia.Rect.MakeLTRB(-60, -80, 60, 80), paint(tuple(int(v) for v in rng.uniform(70, 230, 1).repeat(3))))
            c.drawRect(skia.Rect.MakeLTRB(-60, -80, 60, 80), paint(BLACK, stroke=5))
            c.restore()
    return st


def _paper_rain(c, T, n=60, seed=0, speed=1.0):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x0 = rng.uniform(-50, W + 50)
        ph = rng.uniform(0, 1)
        y = ((T * speed * rng.uniform(0.25, 0.5) + ph) % 1.0) * (H + 300) - 150
        x = x0 + 40 * math.sin(T * 2 + i)
        c.save()
        c.translate(x, y)
        c.rotate(30 * math.sin(T * 3 + i))
        c.drawRect(skia.Rect.MakeLTRB(-40, -52, 40, 52), paint((240, 238, 230)))
        c.drawRect(skia.Rect.MakeLTRB(-40, -52, 40, 52), paint(BLACK, stroke=4))
        for j in range(4):
            c.drawLine(-28, -34 + j * 18, 28, -34 + j * 18, paint((130, 130, 130), stroke=3))
        c.restore()


def s_s2_rain(T, t, d):
    st = ZStage()
    c = st.c
    sets.bd(st, "library", sets.library)
    _paper_rain(c, T, 70, 1)
    k = ease(ramp(t, 0.1, 0.5))
    n = int(1_000_000 * min(1.0, ramp(t, 0.1, 1.2)))
    P.placard(c, 540, 820, 860, [f"{n:,}", "new medical papers a year"], "MEDLINE, U.S. National Library of Medicine", T, k=k, seed=7, size=120)
    K.octopus(c, 540, 1560, 0.72, T)
    return st


def s_s2_day(T, t, d):
    """A doctor (live) at a desk, paper piling up to her chin: nearly 3,000 a day."""
    st = ZStage()
    c = st.c
    sets.bd(st, "library", sets.library)
    _paper_rain(c, T, 30, 2, 1.4)
    pile = 200 + 520 * ramp(t, 0.0, d)
    K.doctor(c, 540, 1880, 1.05, T, pose="shrug", expr="worried", seed=8, hair="bob", haircol=(50, 44, 40))
    rng = np.random.default_rng(9)
    y = 1880
    while y > 1880 - pile:
        w = rng.uniform(520, 640)
        c.save()
        c.translate(540 + rng.uniform(-30, 30), y)
        c.rotate(rng.uniform(-4, 4))
        c.drawRect(skia.Rect.MakeLTRB(-w / 2, -30, w / 2, 0), paint((236, 234, 226)))
        c.drawRect(skia.Rect.MakeLTRB(-w / 2, -30, w / 2, 0), paint(BLACK, stroke=4))
        c.restore()
        y -= 30
    P.placard(c, 540, 520, 760, ["NEARLY 3,000", "A DAY"], None, T, k=ease(ramp(t, 0.0, 0.3)), seed=11, size=110)
    return st


def s_s2_octo(T, t, d):
    """The octopus, in Mae's glasses, plucks the one page that fits and holds it up; it is painted gold."""
    st = ZStage()
    c = st.c
    sets.bd(st, "library", sets.library)
    K.octopus(c, 540, 1560, 0.95, T)
    k = ease(ramp(T, C["page"] - 0.3, C["page"] + 0.3))
    px, py = 540, 640 - 120 * k
    c.save()
    c.translate(px, py)
    c.rotate(-6 + 6 * k)
    c.scale(0.6 + 0.6 * k, 0.6 + 0.6 * k)
    c.drawRect(skia.Rect.MakeLTRB(-170, -220, 170, 220), paint((250, 248, 240)))
    c.drawRect(skia.Rect.MakeLTRB(-170, -220, 170, 220), paint(BLACK, stroke=8))
    Z.letters(c, "THE ONE", 0, -120, 70, "londrina-900", BLACK, T=T, seed=3, tag="page")
    Z.letters(c, "THAT FITS", 0, -40, 70, "londrina-900", BLACK, T=T, seed=4, tag="page")
    for j in range(6):
        c.drawLine(-130, 20 + j * 30, 130, 20 + j * 30, paint((120, 120, 120), stroke=4))
    Z.tinted(st.t, c, lambda tt: tt.drawRect(skia.Rect.MakeLTRB(-170, -220, 170, 220), paint((250, 200, 40), 0.8 * k)))
    c.restore()
    for i in range(12):                                                 # sparkle lines
        a = 2 * math.pi * i / 12 + T
        c.drawLine(px + 280 * math.cos(a) * k, py + 320 * math.sin(a) * k, px + 330 * math.cos(a) * k, py + 380 * math.sin(a) * k,
                   paint(WHITE, k, stroke=6))
    return st


def s_clash(T, t, d):
    """The page goes to the doctor (she decides); two pill bottles march in and bonk: CLASH! (it flags them)."""
    st = ZStage()
    c = st.c
    sets.bd(st, "library", sets.library)
    K.doctor(c, 210, 1580, 0.9, T, pose="reach", expr="calm", seed=8, hair="bob", haircol=(50, 44, 40))
    K.octopus(c, 900, 1560, 0.4, T)
    kc = ramp(T, C["clash"] - 0.9, C["clash"])
    xb = 150 * ease(kc)
    K.bottle(c, 450 + xb, 1180, 0.85, T, label="PILL A", tilt=-10 * (kc >= 1))
    K.bottle(c, 920 - xb, 1180, 0.85, T, label="PILL B", tilt=10 * (kc >= 1))
    kb = ease(ramp(T, C["clash"], C["clash"] + 0.2))
    if kb > 0:
        cx, cy = 685, 760
        pts = [(cx + (170 if i % 2 == 0 else 80) * kb * math.cos(i * math.pi / 8), cy + (150 if i % 2 == 0 else 70) * kb * math.sin(i * math.pi / 8))
               for i in range(16)]
        Z.blob(c, pts, WHITE, T, 5, smooth=False)
        Z.letters(c, "CLASH!", cx, cy + 26, 84 * kb, "londrina-900", BLACK, T=T, seed=9, tag="clash")
        Z.tinted(st.t, c, lambda tt: tt.drawPath(path(pts), paint((230, 40, 40), 0.85)))
    return st


# ------------------------------------------------------------------ ROOM 3

def s_record(T, t, d):
    """Ten slips pinned up the clock room's wall, 2016 to 2025; one at a time, each gets its NORMAL stamp."""
    st = ZStage()
    c = st.c
    sets.bd(st, "clockroom", sets.clockroom)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK, 0.25))
    for i, (yr, hb) in enumerate(zip(YEARS, HB)):
        x = 140 + (i % 5) * 200
        y = 820 + (i // 5) * 430
        k = ramp(t, 0.25 * i, 0.25 * i + 0.3)
        P.slip(c, x, y, 0.78, yr, f"{hb}", T, rot=((i * 37) % 11) - 5, stamp_k=ease(k))
    K.second_eye(c, 540, 1560, 0.42, T, look=(-0.2, -0.8), pose="stand", blink=float((T % 2.1) < 0.12))
    return st


def _year(c, T, i, line, sub=None):
    """The year, and this year's number, on a placard at the top."""
    P.placard(c, 540, 470, 760, [str(YEARS[i]), line] + ([sub] if sub else []), None, T, k=1.0, seed=i, size=110)


def s_s3_king(T, t, d):
    """King Hemoglobin (painted red) shrinks a little every year as the calendar flips; his number slips."""
    st = ZStage()
    c = st.c
    sets.bd(st, "clockroom", sets.clockroom)
    i = min(9, int(ramp(t, 0.2, d - 0.3) * 10))
    _year(c, T, i, f"hemoglobin {HB[i]}", "(still in the normal range)")
    K.king_heme(c, 540, 1330, 1.35 * (1 - 0.35 * i / 9), T, tint=st.t)
    return st


def s_s3_iron(T, t, d):
    """Her iron stores sinking: the King's treasure chest of iron coins, a few fewer every year."""
    st = ZStage()
    c = st.c
    sets.bd(st, "clockroom", sets.clockroom)
    i = min(9, int(ramp(t, 0.1, d - 0.3) * 10))
    _year(c, T, i, f"iron stores {FERRITIN[i]}", "(still in the normal range)")
    Z.blob(c, [(260, 1330), (260, 1040), (820, 1040), (820, 1330)], (110, 90, 70), T, 3, smooth=False)       # the chest
    Z.blob(c, [(240, 1040), (300, 920), (780, 920), (840, 1040)], (90, 72, 56), T, 4, smooth=False)
    n = int(round(FERRITIN[i] / 96 * 21))
    for k in range(n):                                                  # the coins still in it
        x = 330 + (k % 7) * 70
        y = 990 - (k // 7) * 56
        Z.circ(c, x, y, 34, (200, 196, 186), T, k, ow=5)
        D.text(c, "Fe", x, y + 12, 32, "londrina-900", BLACK, tag="fe")
    K.king_heme(c, 920, 1330, 0.42, T, tint=st.t)
    return st


def s_s3_cells(T, t, d):
    """Her red cells shrinking a size: a chorus line of blood cells (painted red), a little smaller each year."""
    st = ZStage()
    c = st.c
    sets.bd(st, "clockroom", sets.clockroom)
    i = min(9, int(ramp(t, 0.1, d - 0.3) * 10))
    _year(c, T, i, f"red-cell size {MCV[i]}", "(still in the normal range)")
    s = 0.62 * (MCV[i] / 92) ** 3
    for j in range(4):
        K.king_heme(c, 180 + j * 240, 1330 - 30 * (j % 2), s, T, tint=st.t, crown=False, seed=20 + j)
    return st


def s_s3_heart(T, t, d):
    st = ZStage()
    c = st.c
    sets.bd(st, "clockroom", sets.clockroom)
    i = min(9, int(ramp(t, 0.1, d - 0.3) * 10))
    _year(c, T, i, f"resting pulse {PULSE[i]}")
    K.heart_metro(c, 540, 1320, 1.7, T, bpm=PULSE[i], tint=st.t)
    return st


CHARTS = [("HEMOGLOBIN", HB, ("13.6", "12.1")), ("IRON STORES", FERRITIN, ("96", "22")), ("RED-CELL SIZE", MCV, ("92", "82")),
          ("RESTING PULSE", PULSE, ("64", "78"))]


def s_s3_fine(T, t, d):
    """One at a time: each chart alone, each marked 'fine'."""
    st = ZStage()
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((30, 30, 30)))
    for j, (title, vals, labs) in enumerate(CHARTS):
        x0, y0 = 60 + (j % 2) * 490, 420 + (j // 2) * 520
        k = ease(ramp(t, 0.45 * j, 0.45 * j + 0.3))
        if k <= 0:
            continue
        P.chart(c, x0, y0, 470, 470, vals, T, k=1.0, title=title, fine=k, seed=j * 3, labels=labs)
    return st


def s_s3_all(T, t, d):
    """All at once: the four drifts on one board, one lane each, every arrow pointing the wrong way; painted red."""
    st = ZStage()
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((30, 30, 30)))
    x0, y0, w = 60, 460, 960
    k = ease(ramp(t, 0.05, 0.6))
    warn = ease(ramp(t, 0.5, 0.9))
    for j, (title, vals, labs) in enumerate(CHARTS):
        top = y0 + j * 210
        c.drawRect(skia.Rect.MakeLTRB(x0, top, x0 + w, top + 190), paint((20, 20, 20)))
        c.drawRect(skia.Rect.MakeLTRB(x0, top, x0 + w, top + 190), paint(BLACK, stroke=6))
        Z.letters(c, title, x0 + 20, top + 50, 40, "londrina-900", CHALK, T=T, seed=j, align="left", tag=f"al{j}")
        v = np.array(vals, float)
        v = (v - v.min()) / (np.ptp(v) + 1e-9)
        pts = [(x0 + 360 + 520 * i / 9, top + 160 - 120 * vv) for i, vv in enumerate(v)]
        n = max(2, int(k * 10))
        c.drawPath(path(Z.wob(pts[:n], 2, j, T), closed=False), paint((236, 234, 226), stroke=7))
        if n == 10:
            ex, ey = pts[-1]
            dy = -1 if vals[-1] > vals[0] else 1
            c.drawPath(path([(ex + 10, ey + dy * 30), (ex + 40, ey), (ex + 10, ey - dy * 30)]), paint(CHALK))
        if warn > 0:
            Z.tinted(st.t, c, lambda tt, pts=pts, n=n: tt.drawPath(path(pts[:n], closed=False), paint((230, 40, 40), warn, stroke=22)))
    P.stamp(c, "WARNING SIGN", 540, 370, 96, ramp(t, 0.8, 1.1), rot=-6, tint=st.t)
    return st


def s_evaluate(T, t, d):
    """The Second Eye slams its stamp on Mae's folder: EVALUATE NOW."""
    st = ZStage()
    c = st.c
    sets.bd(st, "clockroom", sets.clockroom)
    Z.cardboard(c, [(170, 620), (880, 600), (900, 1240), (160, 1260)], (214, 196, 150), T=T, seed=4, corrugate=False)
    Z.letters(c, "MAE, 56", 520, 760, 90, "londrina-900", BLACK, T=T, seed=6, tag="folder")
    Z.letters(c, "10 years of results", 520, 850, 50, "londrina-400", BLACK, T=T, seed=7, tag="folder")
    ks = ramp(T, C["evaluate"] - 0.25, C["evaluate"])
    K.second_eye(c, 850, 1540, 0.55, T, look=(-0.6, -0.4), pose="stamp", stamp=ease(ks))
    P.stamp(c, "EVALUATE NOW", 520, 1080, 100, ramp(T, C["evaluate"], C["evaluate"] + 0.3), rot=-7, tint=st.t)
    return st


def s_flagtool(T, t, d):
    st = ZStage()
    c = st.c
    sets.bd(st, "clockroom", sets.clockroom)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK, 0.3))
    P.placard(c, 540, 820, 900, ["BLOOD-COUNT TREND TOOLS", "have flagged colon cancer", "up to a year before",
                                 "the usual diagnosis"], "Hornbrook et al. · Digestive Diseases and Sciences, 2017", T,
              k=ease(ramp(t, 0.0, 0.3)), seed=12, size=66)
    K.king_heme(c, 230, 1520, 0.62, T, tint=st.t)
    K.second_eye(c, 850, 1540, 0.5, T, look=(-0.6, -0.4), pose="dance")
    return st
