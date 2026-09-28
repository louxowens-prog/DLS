"""Scenes 2: a letter for you - the real Michigan case told in the second person (the enka ballad), then revealed."""
import math

import numpy as np
import skia

import bg
import cast
import kit
import kk
import ov
from cues import C
from kk import BLOOD, CREAM, HOT, INK, LEMON, ORANGE, PINK, SKY, WHITE, W, H, ease, paint, path, ramp, twos
from timeline import TL

S, E, Wd = TL.s, TL.e, TL.word


def _window_rain(c, T):
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(150, 260, 930, 890))
    kit.rain(c, T, 70, x0=150, x1=930, y0=260, y1=890)
    c.restore()


def _sheet_text(c, lines, x0, y0, x1, tag="sheet"):
    """Typewritten lines on a sheet: [(text, size, color, font)]."""
    y = y0
    for s, size, color, fname in lines:
        f, size, w = ov._fit(s, fname, size, x1 - x0 - 60)
        y += size * 1.25
        kk.text(c, s, (x0 + x1) / 2, y, size, fname, color, tag=tag)


def s_job(T, t, d):
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.apartment())
    _window_rain(c, T)
    filed = T >= Wd("d1", "file") - 0.1

    def content(c, x0, y0, x1, y1):
        if not filed:
            c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint((255, 190, 210)))
            _sheet_text(c, [("NOTICE", 64, BLOOD, "dela-400"), ("Your position", 44, INK, "special-elite-400"),
                            ("has been eliminated.", 44, INK, "special-elite-400"), ("Thank you!", 40, INK, "special-elite-400")],
                        x0, y0 + 30, x1)
        else:
            c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y0 + 110), paint((120, 190, 255)))
            _sheet_text(c, [("UNEMPLOYMENT", 50, WHITE, "rounded-900")], x0, y0 - 10, x1)
            _sheet_text(c, [("INSURANCE CLAIM", 46, INK, "rounded-900"), ("Name: YOU", 40, INK, "special-elite-400"),
                            ("Reason: laid off", 40, INK, "special-elite-400")], x0, y0 + 110, x1)
            k = kk.pop(T, Wd("d1", "insurance.") - 0.1, 0.2, 0.3)
            if k > 0:
                c.save()
                c.translate((x0 + x1) / 2, y1 - 110)
                c.scale(k, k)
                c.rotate(-6)
                kk.text(c, "✓ SUBMITTED", 0, 0, 52, "dela-400", (30, 150, 70), tag="sheet", outline=WHITE, ow=8)
                c.restore()

    cast.hands(c, T, 540, 900, 600, 640, shake=0.2, content=content)
    kit.tag_label(c, "DRAMATIZATION", 800, 300, 30, color=(60, 60, 90), rot=3)
    return st.arr


def s_letter(T, t, d):
    """Months later, a letter: a computer says you committed fraud. No human checked."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.apartment())
    _window_rain(c, T)
    opened = ramp(t, 0.9, 1.5)

    def content(c, x0, y0, x1, y1):
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(CREAM))
        _sheet_text(c, [("NOTICE OF", 44, INK, "rounded-900"), ("FRAUD", 90, BLOOD, "dela-400"),
                        ("DETERMINATION", 44, INK, "rounded-900")], x0, y0 + 10, x1)
        if T >= Wd("d2", "computer") - 0.1:
            _sheet_text(c, [("Decided by: COMPUTER", 36, INK, "special-elite-400")], x0, y0 + 300, x1)
        if T >= Wd("d2", "No") - 0.1:
            _sheet_text(c, [("Checked by a person: NO", 36, BLOOD, "special-elite-400")], x0, y0 + 360, x1)

    if opened <= 0:
        cast.envelope(c, 540, 1000 - 40 * math.sin(t * 6), 2.2, T, seed=3, label="OFFICIAL", color=(240, 230, 210))
    else:
        cast.hands(c, T, 540, 930 + 300 * (1 - ease(opened)), 640, 640, shake=0.35, content=content)
    kit.tag_label(c, "DRAMATIZATION", 800, 300, 30, color=(60, 60, 90), rot=3)
    return st.arr


def s_owe(T, t, d):
    """Pay it all back. Plus a penalty four times as big. Plus interest: the sum builds up in clay, line by line."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.dark_table())
    tt = twos(T)
    kk.clay_text(c, "YOU OWE", 540, 430, 80, (150, 160, 255), tt, seed=2, tag="owe")
    kit.tag_label(c, "ILLUSTRATIVE AMOUNT", 780, 290, 28, color=(90, 60, 110), rot=3)
    kk.clay_text(c, "$8,000", 540, 610, 130, (120, 210, 120), tt, seed=5, tag="owe")
    tp = C["penalty"] - 0.1
    if T >= tp:
        k = kk.pop(T, tp, 0.2, 0.25)
        c.save()
        c.translate(540, 790)
        c.scale(k, k)
        kk.clay_text(c, "+ 4× PENALTY", 0, 0, 92, (250, 170, 40), tt, seed=7, tag="owe")
        c.restore()
    te = tp + 0.7
    if T >= te:
        extra = max(0.0, T - C["interest"]) * 3100 if T >= C["interest"] else 0.0
        k = kk.pop(T, te, 0.2, 0.25)
        c.save()
        c.translate(540, 990)
        c.scale(k, k)
        kk.clay_text(c, f"= ${40000 + int(extra // 7 * 7):,}", 0, 0, 120, (240, 60, 60), tt, seed=9, tag="owe", max_w=780)
        c.restore()
    if T >= C["interest"] - 0.05:
        k = kk.pop(T, C["interest"] - 0.05, 0.2, 0.25)
        c.save()
        c.translate(540, 1170)
        c.scale(k, k)
        kk.clay_text(c, "+ INTEREST", 0, 0, 76, (250, 120, 200), tt, seed=11, tag="owe")
        c.restore()
    return st.arr


def s_take(T, t, d):
    """They take your wages. They take your tax refund: a big clay hand comes down and takes them out of your hands."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.apartment())
    _window_rain(c, T)
    tw, tr = Wd("d4", "wages.") - 0.35, C["refund"] - 0.15
    g1 = ramp(twos(T), tw, tw + 0.3)
    up1 = ramp(twos(T), tw + 0.4, tw + 0.75)
    g2 = ramp(twos(T), tr, tr + 0.3)
    up2 = ramp(twos(T), tr + 0.4, tr + 0.75)
    holding = (T < tw + 0.4) or (T >= tr - 0.6 and T < tr + 0.4)
    cast.you_clay(c, 540, 1290, 1.05, T, pose="hold" if holding else "empty", mood="worried" if T < tw + 0.4 else "sad", seed=12)
    hy = 1290 + (-390 - 20) * 1.05
    if T < tw + 0.4 or up1 < 1:
        if up1 < 1:
            for k in range(3):
                cast.money(c, 540 + k * 6, hy - k * 18 - 900 * up1, 0.9, T, seed=k, rot=-4 + k * 3)
    if tw <= T < tw + 0.8:
        kit.clay_hand(c, 540, hy - 60 - 700 * (1 - g1) - 900 * up1, 0.85, T, seed=2, grab=g1)
    if tr - 0.6 <= T and up2 < 1:
        k = kk.pop(T, tr - 0.6, 0.2, 0.3)
        c.save()
        c.translate(540, hy - 900 * up2)
        c.scale(k, k)
        cast.envelope(c, 0, 0, 0.8, T, seed=6, label=None, color=(90, 160, 240))
        kk.text(c, "TAX REFUND", 0, 12, 30, "dela-400", WHITE, tag="prop", outline=INK, ow=6)
        c.restore()
    if tr <= T < tr + 0.8:
        kit.clay_hand(c, 540, hy - 60 - 700 * (1 - g2) - 900 * up2, 0.85, T, seed=4, grab=g2)
    return st.arr


def s_wrong(T, t, d):
    """You did nothing wrong. The enka stage: a spotlight on you, slumped on a chair with the letter in your lap;
    paper snow; then nothing at all - not a sound."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.enka_stage())
    c.drawRect(skia.Rect.MakeWH(W, H), paint(INK, 0.5))
    kit.spotlight(c, 540, 0, 540, 1420, 330, (255, 245, 210), 0.45)
    with kk.keyed(c, halo=5) as F:
        F.rrect(400, 1080, 680, 1120, 12, (150, 90, 60))
        F.rrect(410, 760, 450, 1100, 10, (150, 90, 60))
        F.rrect(630, 760, 670, 1100, 10, (150, 90, 60))
        for x in (420, 660):
            F.rrect(x - 12, 1110, x + 12, 1400, 8, (120, 70, 45))
    cast.you_clay(c, 540, 1400, 0.95, T, pose="slump", mood="cry", seed=13)
    c.save()
    c.translate(540, 1125)
    c.rotate(-6)
    c.drawRect(skia.Rect.MakeLTRB(-80, -45, 80, 20), paint(CREAM))
    kk.text(c, "FRAUD", 0, -6, 30, "dela-400", BLOOD, tag="prop")
    c.restore()
    for i in range(6):                                                       # dry-ice fog
        x = (i * 230 + T * 40) % 1400 - 200
        c.drawOval(skia.Rect.MakeLTRB(x - 260, 1330, x + 260, 1560), paint(WHITE, 0.18, blur=30))
    kit.paper_snow(c, T, 70)
    return st.arr


MITTEN = [(0.30, 0.38), (0.42, 0.33), (0.52, 0.38), (0.60, 0.35), (0.66, 0.44), (0.70, 0.56), (0.66, 0.65), (0.73, 0.70),
          (0.76, 0.82), (0.69, 0.96), (0.32, 0.98), (0.28, 0.86), (0.24, 0.71), (0.27, 0.56), (0.25, 0.46)]
UPPER = [(0.02, 0.20), (0.13, 0.12), (0.30, 0.14), (0.45, 0.18), (0.62, 0.15), (0.72, 0.23), (0.56, 0.28), (0.40, 0.28),
         (0.25, 0.32), (0.10, 0.32)]
OZ = [(0.05, 0.45), (0.12, 0.30), (0.25, 0.23), (0.35, 0.13), (0.45, 0.19), (0.50, 0.11), (0.58, 0.06), (0.62, 0.21),
      (0.75, 0.26), (0.82, 0.12), (0.88, 0.31), (0.95, 0.46), (0.92, 0.63), (0.82, 0.79), (0.70, 0.89), (0.58, 0.81),
      (0.48, 0.73), (0.35, 0.76), (0.20, 0.79), (0.08, 0.71), (0.03, 0.58)]


def _map(c, pts, x0, y0, w, h, color, T, seed):
    return kk.clay_poly(c, [(x0 + u * w, y0 + v * h) for u, v in pts], color, twos(T), seed, amp=6, prints=3, marks=3)


def _envelope_rain(c, T, t0, x0, x1, y_land, n=40, seed=2):
    tt = twos(T) - t0
    rng = np.random.default_rng(seed)
    for i in range(n):
        age = tt - i * 0.08
        if age < 0:
            continue
        x = rng.uniform(x0, x1)
        yl = y_land + rng.uniform(-160, 160)
        y = min(yl, -120 + age * age * 3000)
        cast.envelope(c, x, y, 0.36, T, seed=i, rot=rng.uniform(-40, 40), label=None)


def s_michigan(T, t, d):
    """This happened in Michigan: a clay map under a hard light, buried under red letters; 40,000; then 85% WRONG."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.dark_table())
    _map(c, UPPER, 140, 420, 800, 900, (120, 200, 110), T, 3)
    _map(c, MITTEN, 140, 420, 800, 900, (120, 200, 110), T, 4)
    _envelope_rain(c, T, T - t, 360, 760, 1060)
    ov.slam(c, "40,000+", 540, 470, 150, T, C["forty"] - 0.1, sub="DECIDED BY ALGORITHM")
    k = kk.pop(T, C["eightyfive"] - 0.1, 0.18, 0.25)
    if k > 0:
        c.save()
        c.translate(505, 1010)
        c.scale(k, k)
        c.rotate(-6)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-300, -100, 300, 42), 24, 24), paint(WHITE, 0.9))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-300, -100, 300, 42), 24, 24), paint(BLOOD, stroke=18))
        kk.text(c, "85% WRONG", 0, 0, 86, "dela-400", BLOOD, tag="stamp")
        c.restore()
    kit.plaque(c, "Michigan · MiDAS · 2013–2015", 540, 1250)
    return st.arr


def s_homes(T, t, d):
    """People lost their homes: the houses sink into the table; you stand outside yours with a box. Then Australia."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.dark_table())
    if T < C["robodebt"] - 0.1:
        for i, (x, y) in enumerate(((250, 900), (820, 880), (300, 1180))):
            sink = ramp(twos(T), T - t + 0.3 + i * 0.2, T - t + 2.6 + i * 0.2)
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(0, 0, W, y + 8))
            kit.clay_house(c, x, y, 0.8, T, seed=i * 5, sink=sink * 0.9)
            c.restore()
            kk.clay_ellipse(c, x, y + 6, 150, 26, (70, 50, 60), twos(T), seed=70 + i, prints=0, marks=1)
            if sink > 0.4:
                kit.tag_label(c, "FORECLOSED", x, y - 40, 28, color=BLOOD, rot=-6)
        cast.you_clay(c, 700, 1250, 0.62, T, pose="box", mood="cry", seed=14)
        hy = 1250 + (-390 + 10) * 0.62
        kk.clay_poly(c, [(610, hy - 50), (790, hy - 50), (790, hy + 60), (610, hy + 60)], (200, 150, 90), twos(T), seed=71, amp=3)
    else:
        _map(c, OZ, 110, 480, 860, 720, (230, 140, 80), T, 8)
        kk.clay_ellipse(c, 760, 1260, 50, 38, (230, 140, 80), twos(T), seed=9)
        _envelope_rain(c, T, C["robodebt"], 250, 850, 900, n=36, seed=5)
        ov.slam(c, "470,000", 540, 440, 140, T, Wd("d6", "hundreds") - 0.1, sub="WRONG DEBTS")
        kit.plaque(c, "Australia · Robodebt · 2016–2019", 540, 1250)
    return st.arr
