"""Scenes 2: it has already happened - the lawyers and the invented cases, the courts, the airline."""
import math

import numpy as np
import skia

import cast
import hx
import kit
from cues import C
from hx import BLOOD, CREAM, GOLD, INK, PINK, PLUM, W, H, ease, paint, path, ramp, stop
from timeline import TL

S, E, Wd = TL.s, TL.e, TL.word


def s_court(T, t, d):
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "courtroom")
    cast.judge(c, 540, 660, 0.62, T, gavel=0.0)
    cast.suit_man(c, 270, 1050, 0.72, T, seed=0)
    cast.suit_man(c, 810, 1060, 0.7, T, suit=(110, 90, 60), tie=(160, 60, 40), hair=(40, 30, 20), seed=1)
    hx.soft_focus(st.arr, 0.25)
    return st.arr


def _brief(c, x, y, s, T, fake=False):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.rotate(-3)
    with hx.figure(c) as F:
        F.rrect(-380, -300, 380, 300, 6, (252, 250, 240))
    hx.text(c, "BRIEF FOR PLAINTIFF", 0, -220, 40, "special-elite-400", INK, tag="brief")
    hx.text(c, "Varghese v. China", 0, -110, 52, "fell-400-italic", INK, tag="brief")
    hx.text(c, "Southern Airlines", 0, -40, 52, "fell-400-italic", INK, tag="brief")
    hx.text(c, "(11th Cir. 2019)", 0, 40, 40, "special-elite-400", INK, tag="brief")
    for k in range(5):
        c.drawRect(skia.Rect.MakeLTRB(-320, 90 + k * 34, 320 - (k * 47) % 120, 100 + k * 34), paint(INK, 0.5))
    c.restore()


def s_brief(T, t, d):
    """An album insert: the brief with the case the chatbot made up (one of six in the real filing)."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "album_page", 3)
    _brief(c, 540, 720, 1.05, T)
    k = ease(ramp(t, 0.1, 1.2))
    c.save()                                                      # a magnifying glass slides over the citation
    c.translate(300 + 420 * k, 640)
    c.drawCircle(0, 0, 130, paint((200, 230, 255), 0.25))
    c.drawCircle(0, 0, 130, paint((120, 80, 40), stroke=18))
    c.drawLine(92, 92, 200, 200, paint((120, 80, 40), stroke=26))
    c.restore()
    cast.cat(c, 820, 1150, 0.5, T, eyes="red" if t > 0.8 else "gold")
    hx.soft_focus(st.arr, 0.25)
    return st.arr


def s_ask(T, t, d):
    """Split screen: the lawyer holds the case up and asks; the chatbot, sweetly, says yes."""
    n0 = len(hx.TEXT)
    left = hx.Stage()
    kit.backdrop(left, "courtroom")
    cast.suit_man(left.c, 540, 700, 0.95, T, face_mood="ask", seed=0)
    snap = T >= C["yes"] - 0.02
    n1 = len(hx.TEXT)
    right = hx.Stage()
    kit.backdrop(right, "sky_full", 9)
    nod = 12 * math.sin(stop(T, 8) * 14) if not snap else 0.0
    cast.helper(right.c, 540, 820 + nod, 0.95, T, talk=0.0, mood="horror" if snap and T < C["yes"] + 0.35 else "sweet")
    for i in range(3):
        kit.check(right.c, 400 + i * 140, 430, 0.8, T, Wd("c1", "real?") + i * 0.12)
    if snap and T < C["yes"] + 0.35:
        hx.horror(right.arr, 0.9)
    else:
        hx.soft_focus(right.arr, 0.4)
    return hx.split([left.arr, right.arr], "v", gap=14, color=CREAM, texts=[(n0, n1), (n1, len(hx.TEXT))])


def s_fine(T, t, d):
    return hx.title_card(["SANCTIONED", "$5,000"], size=96, sub="Mata v. Avianca · New York · 2023", sub_size=44, y_center=860)


def s_pile(T, t, d):
    """Filings rain down on the court, sped up; every one caught carrying invented material."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "courtroom")
    cast.judge(c, 540, 660, 0.62, T, gavel=0.5 + 0.5 * math.sin(stop(T, 12) * 12))
    rng = np.random.default_rng(7)
    tt = stop(T, 12) - stop(C["pile"], 12)
    for i in range(46):
        t0 = rng.uniform(-1.5, 3.8)
        age = tt * 2.0 - t0
        if age < 0:
            continue
        x = rng.uniform(80, 1000)
        y = min(1180 - (i % 6) * 22, -200 + age * 900)
        rot = rng.uniform(-30, 30) * (1 if y < 1100 else 0.3)
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        c.drawRect(skia.Rect.MakeLTRB(-110, -140, 110, 140), paint((252, 250, 240)))
        c.drawRect(skia.Rect.MakeLTRB(-110, -140, 110, 140), paint(INK, 0.4, stroke=3))
        for k in range(6):
            c.drawRect(skia.Rect.MakeLTRB(-80, -100 + k * 30, 80 - (k * 23) % 50, -92 + k * 30), paint(INK, 0.45))
        if y >= 1080:
            c.drawRect(skia.Rect.MakeLTRB(-90, -40, 90, 30), paint(BLOOD, 0.85, stroke=8))
        c.restore()
    k = hx.pop(T, C["pile"] + 1.2, 0.2, 0.2)
    if k > 0:
        c.save()
        c.translate(540, 420)
        c.scale(k, k)
        c.drawRect(skia.Rect.MakeLTRB(-400, -90, 400, 60), paint((24, 10, 20)))
        hx.ornate_frame(c, -390, -80, 390, 50, CREAM, w=3)
        hx.text(c, "AI Hallucination Cases database · June 2026", 0, -4, 36, "fell-400-italic", CREAM, tag="plaque")
        c.restore()
    hx.soft_focus(st.arr, 0.2)
    return st.arr


def _plane(c, x, y, s, T):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with hx.figure(c) as F:
        F.oval(-380, -90, 380, 90, (250, 240, 250))
        F.poly([(-60, -40), (60, -40), (-120, -260), (-190, -260)], (255, 170, 200))
        F.poly([(-60, 40), (60, 40), (-120, 240), (-190, 240)], (255, 150, 190))
        F.poly([(-330, -40), (-280, -40), (-380, -200), (-420, -200)], (255, 170, 200))
    for k in range(6):
        c.drawCircle(-200 + k * 60, -20, 16, paint((120, 180, 230)))
    c.drawCircle(290, -20, 70, paint((170, 220, 255)))
    c.restore()
    cast.helper(c, x + 290 * s, y - 20 * s, 0.26 * s, T, halo=False, fringe=False)


def s_plane(T, t, d):
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "sky_full", 11)
    x = -250 + 1350 * ramp(stop(T, 8), stop(T - t, 8), stop(T - t, 8) + d)
    _plane(c, x, 700, 0.95, T)
    k = hx.pop(T, Wd("c3", "refund") - 0.1, 0.2, 0.2)
    if k > 0:                                                    # the policy it made up flutters down
        c.save()
        c.translate(560, 1080)
        c.rotate(-4 + 2 * math.sin(stop(T, 8) * 6))
        c.scale(k, k)
        with hx.figure(c) as F:
            F.rrect(-320, -160, 320, 160, 12, (255, 236, 170))
        hx.text(c, "REFUND POLICY", 0, -55, 58, "shrikhand-400", PLUM, tag="ticket")
        hx.text(c, "apply up to 90 days after you fly", 0, 75, 36, "special-elite-400", INK, tag="ticket")
        c.restore()
        hx.sparkle(c, 250, 950, 40, T, seed=2)
        hx.sparkle(c, 860, 1180, 34, T, seed=3)
    hx.soft_focus(st.arr, 0.45)
    return st.arr


def s_pay(T, t, d):
    """The airline pays: coins pour from the plane, stop-motion, into a tribunal's tray."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "sky_full", 11)
    _plane(c, 540, 480, 0.85, T)
    rng = np.random.default_rng(13)
    tt = stop(T, 12) - stop(C["pay"] - 0.1, 12)
    for i in range(40):
        t0 = rng.uniform(0, 1.2)
        age = tt - t0
        if age < 0:
            continue
        x = 540 + rng.uniform(-120, 120) + age * rng.uniform(-60, 60)
        y = min(1120 - rng.uniform(0, 60), 560 + age * 1100)
        c.drawOval(skia.Rect.MakeLTRB(x - 30, y - 30, x + 30, y + 30), paint(GOLD))
        c.drawOval(skia.Rect.MakeLTRB(x - 30, y - 30, x + 30, y + 30), paint((180, 120, 30), stroke=5))
    with hx.figure(c) as F:
        F.rrect(250, 1120, 830, 1230, 20, (200, 140, 90))
    hx.text(c, "Moffatt v. Air Canada · 2024", 540, 1200, 40, "fell-400-italic", CREAM, tag="source")
    hx.soft_focus(st.arr, 0.35)
    return st.arr
