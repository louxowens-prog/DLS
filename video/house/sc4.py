"""Scenes 4: the scale (the same mistake, millions of times), the experts' report, what to do, and the clock."""
import math

import numpy as np
import skia

import cast
import hx
import kit
import sc1
from cues import C, count
from hx import BLOOD, CREAM, GOLD, INK, MINT, PEACH, PINK, PLUM, POWDER, W, H, bez, ease, paint, path, ramp, stop
from script import WRONG_PER_SEC
from timeline import TL

S, E, Wd = TL.s, TL.e, TL.word
WHITE_ = (255, 255, 255)


def s_onedoc(T, t, d):
    """A human doctor sees one patient at a time: the others wait their turn."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "hospital")
    cast.doctor(c, 330, 560, 0.72, T)
    cast.you(c, 760, 640, 0.5, T, pose="stand")
    for i in range(3):                                                # the queue, waiting
        cast.you(c, 620 + i * 150, 1080, 0.3, T + i * 0.3, pose="stand", fringe=False)
    if T >= Wd("s1", "one", 1) - 0.1:
        kit.stamp(c, "ONE AT A TIME", 540, 1235, 54, T, Wd("s1", "one", 1) - 0.1, color=PLUM, rot=-4, tag="stamp")
    hx.soft_focus(st.arr, 0.35)
    return st.arr


def _grid_heads(c, T, n, mood="sweet", bubble=True, red_one=None):
    cols = int(math.ceil(math.sqrt(n)))
    rows = int(math.ceil(n / cols))
    x0, y0, x1, y1 = 60, 260, 1020, 1260
    cw, ch = (x1 - x0) / cols, (y1 - y0) / rows
    s = min(cw, ch) / (660 if bubble and n <= 16 else 560)
    for i in range(n):
        r, q = divmod(i, cols)
        cx, cy = x0 + cw * (q + 0.5), y0 + ch * (r + 0.55)
        m = "horror" if (mood == "horror" or i == red_one) else "sweet"
        cast.helper(c, cx, cy, s, T + i * 0.13, mood=m, halo=False, fringe=n <= 16)
        if bubble and n <= 16:
            fs = cw * 0.15
            f = hx.font("shrikhand-400", fs)
            w = f.measureText("bromide!")
            by = cy - ch * 0.5 + fs * 0.2
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - w / 2 - 10, by - fs * 0.15, w + 20, fs * 1.25), 14, 14), paint(WHITE_))
            c.drawString("bromide!", cx - w / 2, by + fs * 0.85, f, paint(BLOOD))


def s_clones(T, t, d):
    """One face becomes four, sixteen, sixty-four: the same sweet face giving the same wrong answer."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "sky_full", 13)
    steps = [(0.0, 1), (0.55, 4), (1.2, 16), (1.9, 64)]
    n = 1
    for a, k in steps:
        if stop(t, 12) >= a:
            n = k
    _grid_heads(c, T, n)
    hx.soft_focus(st.arr, 0.4)
    return st.arr


def s_clones_red(T, t, d):
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "sky_full", 13)
    _grid_heads(c, T, 64, mood="horror", bubble=False)
    kit.top_drips(c, T, grow=0.8)
    hx.horror(st.arr, 0.95)
    return st.arr


def s_globe(T, t, d):
    """The whole world sending messages - sped up - into one sweet mouth."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "space")
    gx, gy, gr = 540, 1080, 250
    with hx.figure(c) as F:
        F.circle(gx, gy, gr, (120, 190, 240))
    rng = np.random.default_rng(2)
    for _ in range(9):
        c.drawCircle(gx + rng.uniform(-160, 160), gy + rng.uniform(-160, 160), rng.uniform(40, 90), paint((140, 210, 130)))
    c.drawCircle(gx, gy, gr, paint(INK, stroke=6))
    cast.helper(c, 540, 470, 0.62, T, talk=0.6 + 0.4 * math.sin(stop(T, 12) * 9), mood="sweet")
    tt = stop(T, 12)
    for i in range(34):                                                # envelopes streaming up
        u = (tt * 1.6 + i / 34) % 1.0
        a0 = i * 2.4
        sx, sy = gx + gr * math.cos(a0), gy + gr * math.sin(a0) * 0.9
        x, y = sx + (540 - sx) * u, sy + (560 - sy) * u
        sz = 36 * (1 - u * 0.6)
        c.save()
        c.translate(x, y)
        c.rotate(a0 * 30)
        c.drawRect(skia.Rect.MakeLTRB(-sz, -sz * 0.65, sz, sz * 0.65), paint((255, 250, 240)))
        c.drawPath(path([(-sz, -sz * 0.65), (0, sz * 0.1), (sz, -sz * 0.65)], closed=False), paint((200, 120, 150), stroke=3))
        c.restore()
    hx.soft_focus(st.arr, 0.35)
    return st.arr


def s_hundred(T, t, d):
    """A hundred answers, a hundred sweet faces - and one of them is wrong."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "sky_full", 14)
    red = 57 if T >= Wd("s4", "wrong,") - 0.15 else None
    _grid_heads(c, T, 100, bubble=False, red_one=red)
    if red is not None:
        r, q = divmod(red, 10)
        cx, cy = 60 + 96 * (q + 0.5), 260 + 100 * (r + 0.55)
        c.drawCircle(cx, cy, 70, paint(BLOOD, stroke=8))
        hx.scribble(c, cx, cy, 80, T, seed=5, color=BLOOD, w=5)
    hx.soft_focus(st.arr, 0.3)
    return st.arr


def s_counter(T, t, d):
    """The clock close: its counter spun forward through one whole day of it."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "parlor")
    k = ease(ramp(t, 0.1, 1.6))
    n = 25_000_000 * k
    cast.cuckoo_clock(c, 540, 720, 1.5, T, n, bird=abs(math.sin(stop(T, 12) * 8)), glow=k)
    if k >= 1:
        hx.text(c, "in one day", 540, 1230, 50, "fell-400-italic", CREAM, tag="clock", outline=INK, ow=10)
    hx.soft_focus(st.arr, 0.25)
    return st.arr


def s_tick(T, t, d):
    """Every tick of the second hand: another +289."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "parlor")
    cast.cuckoo_clock(c, 540, 700, 1.5, T, count(T), glow=0.5)
    base = C["second"] - 0.1
    for j in range(3):
        tj = base + 0.3 + j * 0.62
        if T >= tj:
            k = ramp(T, tj, tj + 0.6)
            kit.stamp(c, "+289", 840, 380 + j * 130 - 40 * k, 64, T, tj, color=BLOOD, rot=-8 + j * 6, box=False, tag="tick")
    hx.soft_focus(st.arr, 0.2)
    hx.horror(st.arr, 0.2)
    return st.arr


def s_thatclock(T, t, d):
    """Back to the parlour from the very first frame: that clock has been counting all along."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "parlor")
    z = 1.0 + 0.9 * ease(ramp(t, 0.2, 1.5))
    c.save()
    c.translate(170, 470)
    c.scale(z, z)
    c.translate(-170, -470)
    cast.cuckoo_clock(c, 170, 470, 0.42, T, count(T), glow=ease(ramp(t, 0.8, 1.5)))
    c.restore()
    cast.cat(c, 700, 1540, 0.8, T, eyes="gold")
    hx.soft_focus(st.arr, 0.4)
    return st.arr


def _book(c, x, y, s, T, open_=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with hx.figure(c) as F:
        F.rrect(-300, -400, 300, 400, 14, (40, 60, 110))
    c.drawRect(skia.Rect.MakeLTRB(-300, -400, -250, 400), paint((30, 40, 80)))
    for j, ln in enumerate(("INTERNATIONAL", "AI SAFETY", "REPORT")):
        hx.text(c, ln, 20, -230 + j * 90, 64, "fell-sc-400", CREAM, tag="book")
    hx.text(c, "2026", 20, 120, 90, "shrikhand-400", GOLD, tag="book")
    hx.text(c, "100+ experts · 30+ countries", 20, 260, 34, "fell-400-italic", CREAM, tag="book")
    c.restore()


def s_report(T, t, d):
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "courtroom")
    c.drawRect(skia.Rect.MakeLTRB(0, 1180, W, H), paint((110, 64, 40)))
    _book(c, 540, 760, 1.0, T)
    for i in range(6):
        a = i * 2 * math.pi / 6 + stop(T, 8)
        hx.sparkle(c, 540 + 420 * math.cos(a), 760 + 480 * math.sin(a), 30, T, seed=i)
    hx.soft_focus(st.arr, 0.45)
    return st.arr


PRINTS = [("news", 300, 480, -5), ("code", 770, 770, 4), ("medical", 320, 1070, -3)]


def _prints(T, burn=0.0):
    """The three failures the report names, as prints slapped down one per word (and then set alight)."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "sky_full", 15)
    times = [Wd("r1", "made-up"), Wd("r1", "flawed"), Wd("r1", "misleading")]
    for (name, x, y, rot), tk in zip(PRINTS, times):
        k = hx.pop(T, tk - 0.12, 0.16, 0.18)
        if k <= 0:
            continue
        c.save()
        c.translate(x, y)
        c.scale(k, k)
        c.translate(-x, -y)
        hx.photo(c, kit.mini(name), x, y, 440, 330, rot=rot)
        c.restore()
    if burn > 0:
        for i in range(7):
            hx.flame(c, 120 + i * 140, 1280, 420 * burn, T, seed=i)
        kit.top_drips(c, T, grow=burn)
        hx.horror(st.arr, 0.9 * burn)
    else:
        hx.soft_focus(st.arr, 0.35)
    return st.arr


def s_three(T, t, d):
    return _prints(T)


def s_burn(T, t, d):
    return _prints(T, burn=ease(ramp(t, 0.0, 0.6)))


def s_crack(T, t, d):
    """A crack in the wall. Plasters go on; the crack splits them; paint seeps through. (Plasters fly back on, reversed.)"""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "parlor")
    crack = [(540, 240), (500, 420), (580, 560), (520, 760), (600, 930), (540, 1120), (590, 1270)]
    w = 10 + 14 * ramp(t, 0.4, d)
    c.drawPath(path(crack, closed=False), paint(INK, stroke=w))
    c.drawPath(path(crack, closed=False), paint(BLOOD, stroke=w * 0.45))
    tt = stop(t, 8)
    rev = tt < 0.8                                                     # reverse motion first: plasters fly back onto the wall
    for i in range(4):
        px, py = crack[1 + i][0], crack[1 + i][1] + 60
        if rev:
            k = ramp(tt, i * 0.12, i * 0.12 + 0.35)
            ox, oy = (1 - k) * (300 if i % 2 else -300), (1 - k) * -200
        else:
            k = ramp(tt, 0.9 + i * 0.12, 1.2 + i * 0.12)
            ox, oy = k * (340 if i % 2 else -340), k * 500
        c.save()
        c.translate(px + ox, py + oy)
        c.rotate(35 + i * 20 + (0 if rev else 90 * k))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-110, -34, 110, 34), 30, 30), paint((245, 200, 170)))
        c.drawRect(skia.Rect.MakeLTRB(-34, -30, 34, 30), paint((230, 180, 150)))
        c.restore()
    kit.flood(c, 200 * ramp(t, 0.8, d), T)
    hx.horror(st.arr, 0.5 * ramp(t, 0.8, d))
    return st.arr


def s_rumor(T, t, d):
    """Treat it like a rumour: you, with a magnifying glass, over the chatbot's pretty card."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "parlor")
    kit.ai_card(c, "“According to the study…”", T, T - t - 1, y=290, size=60)
    cast.you(c, 320, 900, 0.62, T, pose="reach")
    k = ease(ramp(t, 0.1, 0.9))
    c.save()
    c.translate(420 + 260 * k, 460)
    c.drawCircle(0, 0, 120, paint((200, 230, 255), 0.25))
    c.drawCircle(0, 0, 120, paint((120, 80, 40), stroke=16))
    c.drawLine(85, 85, 190, 190, paint((120, 80, 40), stroke=24))
    c.restore()
    cast.helper(c, 820, 900, 0.5, T, mood="eerie", look=(-0.8, 0.0))
    hx.soft_focus(st.arr, 0.45)
    return st.arr


def s_source(T, t, d):
    """Open the source yourself: the cited study, opened - blank pages. Caught it."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "kitchen")
    k = ease(ramp(t, 0.1, 0.8))
    with hx.figure(c) as F:
        F.rrect(160, 460, 920, 1200, 10, (140, 60, 60))
        if k > 0.5:
            F.rrect(180, 480, 530, 1180, 6, (252, 250, 240))
            F.rrect(550, 480, 900, 1180, 6, (252, 250, 240))
    if k <= 0.5:
        hx.text(c, "THE STUDY", 540, 820, 80, "fell-sc-400", CREAM, tag="book")
    else:
        for i in range(3):                                               # nothing inside but a cobweb
            c.drawLine(560, 490, 560 + 200 * math.cos(i * 0.5), 490 + 200 * math.sin(i * 0.5 + 0.2), paint((200, 200, 210), stroke=2))
        for r in (60, 110, 160):
            c.drawPath(path(bez((560 + r, 490), (560 + r * 0.8, 490 + r * 0.6), (560, 490 + r)), closed=False), paint((200, 200, 210), stroke=2))
        kit.check(c, 540, 1000, 2.2, T, T - t + 1.2)
        if T >= T - t + 1.2:
            for i in range(5):
                hx.sparkle(c, 250 + i * 150, 420 + (i % 2) * 40, 30, T, seed=i + 40)
    hx.soft_focus(st.arr, 0.45)
    return st.arr


def _door(c, x, y, icon, T, locked):
    with hx.figure(c) as F:
        F.rrect(x - 140, y - 360, x + 140, y + 360, 16, (170, 110, 80))
    c.drawRect(skia.Rect.MakeLTRB(x - 110, y - 330, x + 110, y - 40), paint((150, 94, 66)))
    c.drawRect(skia.Rect.MakeLTRB(x - 110, y + 20, x + 110, y + 330), paint((150, 94, 66)))
    c.drawCircle(x, y - 190, 76, paint(CREAM))
    if icon == "heart":
        hx.heart(c, x, y - 190, 44, BLOOD)
    elif icon == "coins":
        for k in range(3):
            c.drawOval(skia.Rect.MakeLTRB(x - 44, y - 160 - k * 26, x + 44, y - 130 - k * 26), paint(GOLD))
            c.drawOval(skia.Rect.MakeLTRB(x - 44, y - 160 - k * 26, x + 44, y - 130 - k * 26), paint((170, 120, 30), stroke=4))
    else:
        c.drawLine(x - 46, y - 220, x + 46, y - 220, paint(INK, stroke=6))
        c.drawLine(x, y - 240, x, y - 140, paint(INK, stroke=6))
        for sx in (-1, 1):
            c.drawPath(path([(x + sx * 46, y - 220), (x + sx * 66, y - 170), (x + sx * 26, y - 170)]), paint(INK, stroke=4))
    c.drawCircle(x + 90, y + 10, 16, paint(GOLD))
    if locked:
        c.drawRect(skia.Rect.MakeLTRB(x - 150, y - 12, x + 150, y + 30), paint((90, 90, 100)))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - 36, y - 10, x + 36, y + 70), 10, 10), paint(GOLD))


def s_doors(T, t, d):
    """Your health, your money, the law: three doors, bolted one after another. It knocks, sweetly, outside."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "parlor")
    times = [Wd("t2", "health,"), Wd("t2", "money,"), Wd("t2", "law.")]
    for i, (icon, tk) in enumerate(zip(("heart", "coins", "law"), times)):
        _door(c, 190 + i * 350, 820, icon, T, T >= tk)
    cast.helper(c, 540, 330 + 20 * math.sin(stop(T, 8) * 6), 0.4, T, mood="eerie", look=(0.0, 0.8))
    cast.cat(c, 540, 1560, 0.6, T, eyes="gold")
    hx.soft_focus(st.arr, 0.35)
    return st.arr


def s_payoff(T, t, d):
    """The clock strikes. The cuckoo that pops out is the chatbot's little face. The room goes red."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "parlor")
    bird = abs(math.sin(stop(T, 8) * 5))
    cast.cuckoo_clock(c, 540, 700, 1.25, T, count(T), bird=0.0, glow=ramp(t, 0, d))
    cast.helper(c, 540 + 120 * bird, 700 - 262 * 1.25, 0.2 + 0.08 * bird, T, halo=False, fringe=False)
    cast.cat(c, 820, 1600, 0.62, T, eyes="gold" if t < d * 0.6 else "red")
    hx.soft_focus(st.arr, 0.3 * (1 - ramp(t, 0, d)))
    hx.horror(st.arr, 0.6 * ramp(t, 0.5, d))
    return st.arr


def s_count(T, t, d):
    """Close on the count."""
    st = hx.Stage((40, 0, 10))
    c = st.c
    kit.backdrop(st, "parlor")
    cast.cuckoo_clock(c, 540, 560, 2.1, T, count(T), mood="horror", glow=1.0)
    for i in range(5):
        hx.flame(c, 160 + i * 190, 1290, 220, T, seed=i)
    kit.flood(c, 380 + 160 * ramp(t, 0, d), T)
    hx.horror(st.arr, 0.75)
    return st.arr


def s_trust(T, t, d):
    """'Trust me.' Sweet - then, for three frames, the real face. Then the iris closes on the cat's red eyes."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "sky_full", 8)
    snap = E("e2") <= T < E("e2") + 0.2
    cast.helper(c, 540, 1000, 1.5, T, talk=kit.ai_talk(T), mood="horror" if snap else "sweet", halo=not snap)
    kit.ai_card(c, "“Trust me.”", T, S("e2") - 0.1, y=270, size=76, horror=snap)
    if snap:
        hx.horror(st.arr, 1.0)
    else:
        hx.soft_focus(st.arr, 0.55)
    close = ramp(t, d - 0.55, d)
    if close > 0:
        hx.iris(st.arr, 540, 1000, (1 - close) * 1300)
    return st.arr


def s_end(T, t, d):
    st = hx.Stage(INK)
    c = st.c
    hx.ornate_frame(c, 70, 260, 1010, 1270, CREAM)
    hx.text(c, "THE END?", W / 2, 520, 120, "fell-sc-400", CREAM, tag="card")
    srcs = ["International AI Safety Report 2026",
            "Eichenberger et al., Ann. Intern. Med.: Clinical Cases, 2025",
            "Mata v. Avianca (S.D.N.Y. 2023)",
            "Moffatt v. Air Canada (BC CRT 2024)",
            "Charlotin, AI Hallucination Cases database, 2026",
            "Kalai et al., Why Language Models Hallucinate, 2025",
            "OpenAI: ~2.5 billion messages/day (July 2025)"]
    for i, s in enumerate(srcs):
        hx.text(c, s, W / 2, 700 + i * 64, 34, "fell-400-italic", CREAM, tag="source")
    hx.text(c, "Check everything. Even this.", W / 2, 1200, 44, "shrikhand-400", (255, 150, 170), tag="card")
    k = ramp(t, 0.8, 1.6)
    if k > 0:                                                          # two red eyes open in the dark
        for sx in (-1, 1):
            c.drawOval(skia.Rect.MakeLTRB(540 + sx * 90 - 40 * k, 1390 - 18 * k, 540 + sx * 90 + 40 * k, 1390 + 18 * k), paint((255, 70, 60)))
            c.drawCircle(540 + sx * 90, 1390, 50 * k, paint(BLOOD, 0.5, blur=20))
    return st.arr
