"""Have we already built it? The rising water. Intelligence is not consciousness."""
import math

import numpy as np
import skia

import chars as CH
import mg
from mg import CX, H, INK, W, WHITE, ease, ramp
from cues import C
from scenes_1 import chalk_bg
from timeline import TL

S, E, Wd = TL.s, TL.e, TL.word


def s_nature(arr, t, d, T):
    mg.paper(arr, (235, 232, 222), 9)
    s = mg.surf(arr)
    with s as c:
        c.save()
        c.translate(CX, 900)
        c.rotate(-3 + 1.5 * math.sin(T))
        c.translate(-CX, -900)
        page = mg.rect_pts(90, 360, 900, 940)
        mg.fill(c, page, T, (250, 248, 240), 300, off=(12, 10))
        mg.stroke(c, page, T, 301, width=8, closed=True)
        mg.letters(c, "COMMENT · FEB 2026", CX, 450, T, size=42, fname="rubik-800", color=INK, outline=None, seed=302, jig=1, rot=1)
        mg.stroke(c, [(130, 480), (950, 480)], T, 303, width=6)
        mg.letters(c, "HUMAN-LEVEL AI", CX, 590, T, size=98, fname="bangers-400", color=INK, outline=None, seed=304, jig=2, rot=2)
        mg.letters(c, "IS ALREADY HERE", CX, 700, T, size=98, fname="bangers-400", color=mg.RED, outline=None, seed=305, jig=2, rot=2)
        mg.collage(c, "earth_ne2.jpg", mg.rect_pts(150, 760, 380, 300), T, seed=306, src=(950, 180), scale=0.9, border=0)
        for i in range(9):
            y = 780 + i * 34
            mg.stroke(c, [(570, y), (930 - (i % 3) * 40, y)], T, 310 + i, width=4, color=(120, 120, 120))
        for i in range(4):
            hx = 220 + i * 210
            head = mg.circle_pts(hx, 1130, 50, 24)
            mg.fill(c, head, T, [(245, 205, 170), (210, 160, 120), (240, 190, 150), (180, 130, 100)][i], 320 + i, off=(3, 3))
            mg.stroke(c, head, T, 324 + i, width=6, closed=True)
            c.drawCircle(hx - 16, 1125, 6, mg.paint(INK))
            c.drawCircle(hx + 16, 1125, 6, mg.paint(INK))
            mg.stroke(c, mg.bez((hx - 15, 1150), (hx, 1161), (hx + 15, 1150)), T, 328 + i, width=5)
        mg.note(c, "4 researchers, UC San Diego", CX, 1250, size=44)
        c.restore()
        mg.label(c, T, S("g1") + 0.3, ["NATURE, FEBRUARY 2026"])


def s_score(arr, t, d, T):
    mg.paper(arr, (230, 245, 230), 10)
    s = mg.surf(arr)
    with s as c:
        mg.letters(c, "HOW CLOSE TO AGI?", CX, 440, T, size=80, fname="bangers-400", color=INK, outline=WHITE, ow=8, seed=340)
        mg.note(c, "vs. a well-educated adult, across 10 abilities", CX, 510, size=40)
        for i, (name, val, key, col) in enumerate((("GPT-4", 27, "twenty-seven", mg.BLUE), ("GPT-5", 58, "fifty", mg.ORANGE))):
            y = 650 + i * 260
            g = ease(ramp(T, Wd("g2", key) - 0.3, Wd("g2", key) + 0.35))
            track = mg.rect_pts(120, y, 840, 120)
            mg.fill(c, track, T, WHITE, 341 + i, off=(6, 4))
            mg.stroke(c, track, T, 343 + i, width=8, closed=True)
            if g > 0.02:
                f = mg.rect_pts(128, y + 8, 824 * val / 100 * g, 104)
                mg.fill(c, f, T, col, 345 + i, off=(0, 0), shader=mg.crayon_shader(col, seed=20 + i, density=1.0))
            mg.letters(c, name, 150, y - 16, T, size=60, fname="permanent-marker-400", color=INK, outline=None, seed=347 + i, align="left")
            mg.letters(c, f"{int(val * g)}%", 900, y - 16, T, size=76, fname="bangers-400", color=col, ow=8, seed=349 + i, align="right")
        mg.stroke(c, [(952, 620), (952, 1170)], T, 351, width=6, color=mg.RED)
        mg.note(c, "AGI = 100%", 900, 1215, size=40, color=mg.RED)
        km = ease(ramp(T, Wd("g2", "memory") - 0.2, Wd("g2", "memory") + 0.2))
        if km > 0:
            box = mg.rect_pts(170, 1260, 740, 150)
            mg.fill(c, box, T, (255, 240, 240), 352, off=(6, 5), a=km)
            mg.stroke(c, box, T, 353, width=8, closed=True, color=mg.RED, a=km)
            mg.letters(c, "LONG-TERM MEMORY: ~0", CX, 1360, T, size=72, fname="bangers-400", color=mg.RED, outline=None, seed=354,
                       a=km, scale=mg.pop(T, Wd("g2", "memory") - 0.1, 0.25) or 0.001)
        mg.stamp(c, "NOT YET?", 540, 862, T, Wd("g2", "not"), color=mg.RED, size=66, rot=8)
        mg.label(c, T, S("g2") + 0.2, ["HENDRYCKS ET AL. 2025", "A DEFINITION OF AGI"])


def s_deepmind(arr, t, d, T):
    mg.paper(arr, (250, 250, 245), 11)
    s = mg.surf(arr)
    with s as c:
        for i in range(12):
            c.drawLine(120 + i * 75, 420, 120 + i * 75, 1220, mg.paint((170, 200, 230), 0.6, stroke=2))
        for i in range(12):
            c.drawLine(120, 420 + i * 72, 960, 420 + i * 72, mg.paint((170, 200, 230), 0.6, stroke=2))
        mg.stroke(c, [(150, 1220), (150, 420)], T, 360, width=10)
        mg.stroke(c, [(150, 1220), (980, 1220)], T, 361, width=10)
        mg.stroke(c, [(130, 450), (150, 420), (170, 450)], T, 362, width=10)
        mg.stroke(c, [(950, 1200), (980, 1220), (950, 1240)], T, 363, width=10)
        levels = ["EMERGING", "COMPETENT", "EXPERT", "VIRTUOSO", "SUPERHUMAN"]
        for i, lv in enumerate(levels):
            y = 1080 - i * 150
            mg.stroke(c, [(140, y), (160, y)], T, 364 + i, width=6)
            mg.note(c, lv, 180, y + 12, size=38, align="left")
        mg.letters(c, "PERFORMANCE", 95, 860, T, size=52, fname="bangers-400", color=mg.RED, outline=None, seed=370) if False else None
        c.save()
        c.translate(80, 900)
        c.rotate(-90)
        mg.letters(c, "PERFORMANCE", 0, 0, T, size=56, fname="bangers-400", color=mg.RED, outline=None, seed=370, spacing=3)
        c.restore()
        mg.letters(c, "GENERALITY", 560, 1300, T, size=56, fname="bangers-400", color=mg.BLUE, outline=None, seed=371, spacing=3)
        k = ease(ramp(T, S("g3") + 0.8, E("g3")))
        px, py = 250 + 520 * k, 1110 - 260 * k
        CH.jag(c, px, py, T, s=0.4, eyes="normal", mouth="smile", arms=(-150, 150), seed=372)
        mg.label(c, T, S("g3") + 0.1, ["GOOGLE DEEPMIND", "LEVELS OF AGI, 2023"])


def s_notif(arr, t, d, T):
    mg.paper(arr, (255, 150, 200), 12)
    s = mg.surf(arr)
    kx = ease(ramp(T, Wd("g4", "nine") + 0.4, Wd("g4", "nine") + 0.7))
    with s as c:
        ph = mg.rect_pts(270, 380, 540, 900)
        mg.fill(c, ph, T, (30, 30, 40), 380, off=(10, 8))
        mg.stroke(c, ph, T, 381, width=12, closed=True)
        scr = mg.rect_pts(300, 430, 480, 800)
        mg.fill(c, scr, T, (70, 110, 200), 382, off=(0, 0))
        mg.letters(c, "9:42", CX, 640, T, size=150, fname="rubik-800", color=WHITE, outline=None, seed=383, jig=1, rot=0)
        kn = ease(ramp(T, C["notif"] - 0.1, C["notif"] + 0.25))
        if kn > 0:
            y = 700 + 60 * kn
            card = mg.rect_pts(300, y, 480, 170)
            mg.fill(c, card, T, (245, 245, 250), 384, off=(4, 4))
            mg.stroke(c, card, T, 385, width=6, closed=True)
            mg.letters(c, "AGI ACHIEVED", CX, y + 85, T, size=64, fname="rubik-900", color=INK, outline=None, seed=386, jig=1, rot=1)
            mg.note(c, "now", 740, y + 40, size=30)
            mg.note(c, "Humanity · 9:42 AM", CX, y + 138, size=34, color=GREY_ if False else (90, 90, 100))
        if kx > 0:
            L = 520 * kx
            mg.stroke(c, [(CX - L / 2, 480), (CX + L / 2, 1220)], T, 390, width=34, color=mg.RED, double=False)
            mg.stroke(c, [(CX + L / 2, 480), (CX - L / 2, 1220)], T, 391, width=34, color=mg.RED, double=False)
            mg.letters(c, "NOPE", CX, 360, T, size=150, fname="bangers-400", color=mg.RED, ow=14, seed=392)


# ------------------------------------------------------------------ the rising water

PEAKS = [("CHESS", 110, 0.34), ("GO", 260, 0.42), ("VISION", 400, 0.48), ("TRANSLATION", 520, 0.53), ("WRITING", 620, 0.58),
         ("CODE", 720, 0.63), ("MATH", 810, 0.7), ("SCIENCE", 900, 0.74), ("COMPUTERS", 990, 0.8)]
LEFT = [("LONG-TERM PLANS", 300, 0.97), ("MEMORY", 620, 1.0), ("ROBOTICS", 880, 0.93)]


def mountains(c, T, level, peaks, seed=0, base=1450, top=470):
    for i, (name, x, hgt) in enumerate(peaks):
        yt = base - (base - top) * hgt
        m = np.array([(x - 150, base), (x - 60, yt + 90), (x - 25, yt + 20), (x, yt), (x + 30, yt + 40), (x + 80, yt + 70), (x + 150, base)])
        mg.fill(c, m, T, [(150, 120, 90), (130, 110, 90), (170, 140, 100)][i % 3], seed + i, off=(5, 4),
                shader=mg.crayon_shader((140, 110, 80), seed=40 + i % 3, density=0.95))
        mg.stroke(c, m, T, seed + 20 + i, width=7)
        under = yt > level
        mg.letters(c, name, x, yt - 22 - (48 if i % 2 else 0), T, size=32 if len(name) > 8 else 40, fname="bangers-400",
                   color=(170, 200, 240) if under else INK, outline=WHITE if not under else None, ow=6, seed=seed + 40 + i)


def water(c, T, level, seed=0, alpha=0.92):
    pts = [(0, H)]
    for i in range(0, W + 40, 40):
        pts.append((i, level + 14 * math.sin(i / 60 + T * 4) + 6 * math.sin(i / 23 - T * 7)))
    pts.append((W, H))
    arrp = np.array(pts, np.float32)
    mg.fill(c, arrp, T, mg.BLUE, seed, off=(0, 0), a=alpha, shader=mg.crayon_shader((60, 130, 255), seed=31, density=1.0))
    mg.stroke(c, arrp[1:-1], T, seed + 1, width=7, color=WHITE)


def s_water(arr, t, d, T):
    mg.paper(arr, (200, 230, 255), 13)
    s = mg.surf(arr)
    lvl = 1450 - 380 * ease(ramp(T, S("g5"), S("g6") + 0.2))
    with s as c:
        mountains(c, T, lvl, PEAKS, seed=400)
        water(c, T, lvl, seed=430)
        mg.letters(c, "RISING WATER", CX, 330, T, size=100, fname="bangers-400", color=mg.BLUE, ow=10, seed=440, spacing=4)


ICONS = ["CHESS", "GO", "VISION", "TRANSLATION", "WRITING", "CODE", "MATH", "SCIENCE", "COMPUTERS"]


def icon(c, name, T, x, y, s=1.0):
    if name == "CHESS":
        k = np.array([(-60, 120), (60, 120), (45, 60), (70, 10), (40, -80), (-10, -110), (-60, -60), (-30, -20), (-60, 20), (-45, 60)]) * s + (x, y)
        mg.fill(c, k, T, WHITE, 500, off=(6, 4))
        mg.stroke(c, k, T, 501, width=9, closed=True)
    elif name == "GO":
        for i in range(3):
            for j in range(3):
                col = INK if (i + j) % 2 else WHITE
                c.drawCircle(x + (i - 1) * 110 * s, y + (j - 1) * 110 * s, 46 * s, mg.paint(col))
                mg.stroke(c, mg.circle_pts(x + (i - 1) * 110 * s, y + (j - 1) * 110 * s, 46 * s, 20), T, 502 + i * 3 + j, width=6, closed=True)
    elif name == "VISION":
        eye = np.vstack([mg.bez((x - 170 * s, y), (x, y - 150 * s), (x + 170 * s, y)), mg.bez((x + 170 * s, y), (x, y + 150 * s), (x - 170 * s, y))])
        mg.fill(c, eye, T, WHITE, 510, off=(5, 4))
        mg.stroke(c, eye, T, 511, width=9, closed=True)
        c.drawCircle(x, y, 60 * s, mg.paint(mg.BLUE))
        c.drawCircle(x, y, 28 * s, mg.paint(INK))
    elif name == "TRANSLATION":
        for i, (txt, col) in enumerate((("HELLO", mg.YELLOW), ("HOLA", mg.GREEN))):
            bx, by_ = x - 150 * s + i * 170 * s, y - 80 * s + i * 120 * s
            bub = mg.rect_pts(bx - 120 * s, by_ - 60 * s, 250 * s, 120 * s)
            mg.fill(c, bub, T, col, 512 + i, off=(5, 4))
            mg.stroke(c, bub, T, 514 + i, width=8, closed=True)
            mg.letters(c, txt, bx + 5 * s, by_ + 22 * s, T, size=64 * s, fname="bangers-400", color=INK, outline=None, seed=516 + i)
    elif name == "WRITING":
        pen = np.array([(-30, -170), (30, -170), (30, 90), (0, 160), (-30, 90)]) * s + (x, y)
        mg.fill(c, pen, T, mg.YELLOW, 520, off=(5, 4))
        mg.stroke(c, pen, T, 521, width=9, closed=True)
        mg.stroke(c, [(x - 180 * s, y + 190 * s), (x - 60 * s, y + 160 * s), (x + 60 * s, y + 200 * s), (x + 180 * s, y + 170 * s)], T, 522, width=8)
    elif name == "CODE":
        mg.letters(c, "{ }", x, y + 70 * s, T, size=260 * s, fname="rubik-900", color=mg.GREEN, ow=12, seed=523)
    elif name == "MATH":
        mg.letters(c, "x²+y²", x, y + 50 * s, T, size=170 * s, fname="rubik-900", color=mg.ORANGE, ow=12, seed=524)
    elif name == "SCIENCE":
        fl = np.array([(-40, -170), (40, -170), (40, -40), (130, 140), (-130, 140), (-40, -40)]) * s + (x, y)
        mg.fill(c, fl, T, (200, 255, 210), 525, off=(5, 4))
        mg.stroke(c, fl, T, 526, width=9, closed=True)
        for k in range(3):
            c.drawCircle(x - 40 * s + k * 40 * s, y + 90 * s - k * 20 * s, 16 * s, mg.paint(mg.GREEN))
    elif name == "COMPUTERS":
        mon = mg.rect_pts(x - 180 * s, y - 130 * s, 360 * s, 240 * s)
        mg.fill(c, mon, T, (40, 44, 60), 527, off=(6, 4))
        mg.stroke(c, mon, T, 528, width=9, closed=True)
        cur = np.array([(0, 0), (0, 90), (22, 68), (40, 108), (58, 100), (40, 62), (70, 62)]) * s + (x - 20 * s, y - 60 * s)
        mg.fill(c, cur, T, WHITE, 529, off=(0, 0))
        mg.stroke(c, cur, T, 530, width=6, closed=True)


def s_montage(arr, t, d, T):
    times = C["montage"]
    i = max(0, sum(1 for x in times if T >= x - 0.05) - 1)
    name = ICONS[min(i, len(ICONS) - 1)]
    style = i % 4
    if style == 0:
        mg.burst(arr, CX, 800, T, spin=2.0)
    elif style == 1:
        mg.paper(arr, (255, 214, 60), 14)
    elif style == 2:
        arr[..., :3] = (20, 20, 28)
    else:
        mg.swirl(arr, T, scale=0.8)
    s = mg.surf(arr)
    local = T - (times[i] - 0.05)
    lvl = 1700 - 900 * ease(ramp(local, 0.05, 0.45))
    with s as c:
        dx, dy = mg.shake(T, 12, 600 + i)
        c.save()
        c.translate(dx, dy)
        icon(c, name, T, CX, 800, 1.5)
        c.restore()
        water(c, T, lvl, seed=610 + i, alpha=0.75)
        mg.letters(c, name, CX, 420, T, size=130 if len(name) < 9 else 100, fname="bangers-400",
                   color=[WHITE, mg.RED, mg.YELLOW, WHITE][style], ow=14, seed=620 + i, spacing=4)


def s_water2(arr, t, d, T):
    mg.paper(arr, (255, 200, 150), 15)
    s = mg.surf(arr)
    lvl = 1450 - (1450 - 470) * 0.62
    with s as c:
        mountains(c, T, lvl, LEFT, seed=650)
        water(c, T, lvl, seed=680)
        raft = mg.rect_pts(330, lvl + 150, 420, 46)
        mg.fill(c, raft, T, (170, 120, 70), 690, off=(4, 3))
        mg.stroke(c, raft, T, 691, width=7, closed=True)
        CH.human(c, 440, lvl + 150, T, s=0.42, mouth="open", seed=692, arms=(-150, 40))
        CH.jag(c, 650, lvl + 150, T, s=0.42, eyes="normal", mouth="open", seed=693, arms=(-40, 150))
        ka = ramp(T, Wd("g7", "arguing") - 0.3, Wd("g7", "arguing"))
        if ka > 0:
            for txt, x, y, col in (("NOT YET!", 300, 1200, mg.RED), ("IT'S AGI!", 790, 1130, mg.CYAN)):
                bub = mg.rect_pts(x - 170, y - 70, 340, 120)
                mg.fill(c, bub, T, WHITE, 694 + x, off=(5, 4))
                mg.stroke(c, bub, T, 695 + x, width=7, closed=True)
                mg.letters(c, txt, x, y + 20, T, size=66, fname="bangers-400", color=col, outline=INK, ow=6, seed=696 + x)
        mg.label(c, T, S("g7") + 0.1, ["WHAT'S STILL DRY?"])


# ------------------------------------------------------------------ intelligence is not consciousness

CHALK = (235, 238, 230)


def s_c1(arr, t, d, T):
    chalk_bg(arr)
    s = mg.surf(arr)
    with s as c:
        CH.jag(c, CX, 1350, T, s=1.1, eyes="normal", mouth="flat", style="line", seed=700) if False else None
        c.save()
        CH_line_jag(c, CX, 1380, T, 1.1)
        c.restore()
        mg.letters(c, "CONSCIOUS?", CX, 560, T, size=150, fname="permanent-marker-400", color=CHALK, outline=None, seed=701, jig=2, rot=3)


def CH_line_jag(c, x, y, T, s):
    """Jag drawn in chalk: outlines only."""
    R = 110 * s
    hx, hy = x, y - 330 * s
    top = [(xx, hy - R * h) for xx, h in zip(np.linspace(hx - R, hx + R, 11), [0.2, 0.95, 0.35, 0.75, 0.15, 1.05, 0.3, 0.8, 0.25, 0.65, 0.2])]
    head = np.vstack([np.array(top), mg.circle_pts(hx, hy, R, 30, a0=0.0, a1=math.pi)])
    mg.stroke(c, head, T, 710, width=6, color=CHALK, closed=True, amp=3.2)
    for side in (-1, 1):
        mg.stroke(c, mg.circle_pts(hx + side * 0.33 * R, hy + 0.05 * R, 22 * s, 16), T, 711 + side, width=5, color=CHALK, closed=True)
        c.drawCircle(hx + side * 0.33 * R, hy + 0.05 * R, 8 * s, mg.paint(CHALK))
    mg.stroke(c, [(hx - 28 * s, hy + 0.45 * R), (hx + 28 * s, hy + 0.45 * R)], T, 714, width=5, color=CHALK)
    torso = mg.rect_pts(x - 50 * s, y - 232 * s, 100 * s, 94 * s)
    mg.stroke(c, torso, T, 715, width=6, color=CHALK, closed=True, amp=3.2)
    for side in (-1, 1):
        mg.stroke(c, mg.bez((x + side * 30 * s, y - 140 * s), (x + side * 44 * s, y - 70 * s), (x + side * 40 * s, y)), T, 716 + side, width=6, color=CHALK)
        mg.stroke(c, mg.bez((x + side * 50 * s, y - 220 * s), (x + side * 95 * s, y - 180 * s), (x + side * 110 * s, y - 120 * s)), T, 718 + side, width=6, color=CHALK)
    return hx, hy, R


def s_c2(arr, t, d, T):
    chalk_bg(arr)
    s = mg.surf(arr)
    items = [("INTELLIGENCE", "solving problems", "Intelligence", mg.YELLOW),
             ("SELF-AWARENESS", "modeling yourself", "Self-awareness", mg.CYAN),
             ("CONSCIOUSNESS", "something it's like to be you", "Consciousness", mg.PINK)]
    with s as c:
        for i, (big, small, key, col) in enumerate(items):
            k = ease(ramp(T, Wd("c2", key) - 0.15, Wd("c2", key) + 0.15))
            if k <= 0:
                continue
            y = 480 + i * 300
            box = mg.rect_pts(110, y - 90, 860, 230)
            mg.stroke(c, box, T, 720 + i, width=6, color=CHALK, closed=True, amp=3.0)
            mg.letters(c, big, CX, y + 10, T, size=90, fname="permanent-marker-400", color=col, outline=None, seed=725 + i, jig=1.5, rot=2)
            mg.note(c, small, CX, y + 90, size=48, color=CHALK)
        mg.note(c, "three different things", CX, 1330, size=44, color=(170, 175, 170))


def s_c3(arr, t, d, T):
    chalk_bg(arr)
    s = mg.surf(arr)
    with s as c:
        msg = "I AM FRIGHTENED."
        n = int(max(0.0, T - S("c3j") + 0.05) * 22)
        paper_ = mg.rect_pts(170, 420, 740, 260)
        mg.fill(c, paper_, T, (245, 240, 225), 740, off=(0, 0))
        mg.stroke(c, paper_, T, 741, width=5, color=CHALK, closed=True)
        mg.letters(c, msg[:n], 215, 580, T, size=74, fname="rubik-800", color=INK, outline=None, seed=742, jig=0.8, rot=0.5, align="left")
        hx, hy, R = CH_line_jag(c, CX, 1400, T, 1.05)
        # inside the head: nothing at all?
        kin = ease(ramp(T, S("c4") - 0.1, S("c4") + 0.3))
        if kin > 0:
            c.drawCircle(hx, hy + 5, R * 0.62 * kin, mg.paint((0, 0, 0), 0.9))
            mg.letters(c, "?", hx, hy + 45, T, size=110 * kin, fname="permanent-marker-400", color=CHALK, outline=None, seed=743)
            mg.note(c, "...and feel nothing?", CX, 1560 - 120, size=52, color=CHALK) if False else None


def s_octo(arr, t, d, T):
    mg.paper(arr, (230, 245, 255), 16)
    sw = arr.copy()
    mg.swirl(sw, T * 1.3, colors=[mg.PINK, mg.ORANGE, mg.PURPLE, mg.RED, mg.YELLOW], scale=0.6, cx=CX, cy=850)
    # octopus mask: mantle + 8 arms
    mask = np.zeros((H, W, 4), np.uint8)
    ms = skia.Surface(mask)
    with ms as c:
        c.drawOval(skia.Rect.MakeXYWH(CX - 190, 560, 380, 420), mg.paint(WHITE))
        for k in range(8):
            a0 = math.pi * (0.1 + 0.8 * k / 7)
            pts = [(CX + 150 * math.cos(a0), 900 + 60 * math.sin(a0))]
            for j in range(1, 7):
                r = 150 + j * 52
                a = a0 + 0.35 * math.sin(T * 2 + k + j * 0.6)
                pts.append((CX + r * math.cos(a) * 1.05, 900 + r * math.sin(a) * 0.9))
            p = mg.path_of(pts)
            c.drawPath(p, mg.paint(WHITE, stroke=64 - 0 * k))
    m = mask[..., 0:1].astype(np.float32) / 255
    arr[..., :3] = (arr[..., :3] * (1 - m) + sw[..., :3] * m).astype(np.uint8)
    s = mg.surf(arr)
    with s as c:
        for side in (-1, 1):
            c.drawCircle(CX + side * 70, 760, 34, mg.paint(WHITE))
            c.drawCircle(CX + side * 70 + 6, 764, 16, mg.paint(INK))
        mg.letters(c, "NO ALGEBRA.", CX, 360, T, size=90, fname="bangers-400", color=mg.PURPLE, ow=10, seed=760)
        mg.letters(c, "STILL FEELS?", CX, 470, T, size=90, fname="bangers-400", color=mg.PINK, ow=10, seed=761)


def s_c5(arr, t, d, T):
    chalk_bg(arr)
    s = mg.surf(arr)
    # the theories the 2023 report drew its indicator properties from
    inds = ["recurrent processing", "global workspace", "higher-order theories", "predictive processing",
            "attention schema", "agency & embodiment"]
    ticks = [None] * len(inds)
    with s as c:
        mg.letters(c, "CONSCIOUSNESS CHECKLIST", CX, 450, T, size=70, fname="permanent-marker-400", color=CHALK, outline=None, seed=770, jig=1)
        for i, (name, ok) in enumerate(zip(inds, ticks)):
            y = 560 + i * 95
            k = ease(ramp(T, S("c5") + 0.15 * i, S("c5") + 0.15 * i + 0.2))
            if k <= 0:
                continue
            box = mg.rect_pts(170, y, 60, 60)
            mg.stroke(c, box, T, 771 + i, width=5, color=CHALK, closed=True)
            mg.letters(c, "?", 200, y + 52, T, size=58, fname="permanent-marker-400", color=mg.YELLOW, outline=None, seed=780 + i)
            mg.note(c, name, 260, y + 46, size=50, color=CHALK, align="left")
        kt = ease(ramp(T, Wd("c5", "accepted") - 0.3, Wd("c5", "accepted")))
        if kt > 0:
            box = mg.rect_pts(150, 1180, 780, 170)
            mg.stroke(c, box, T, 790, width=7, color=mg.RED, closed=True)
            mg.letters(c, "NO ACCEPTED TEST", CX, 1290, T, size=86, fname="bangers-400", color=mg.RED, outline=None, seed=791,
                       scale=mg.pop(T, Wd("c5", "accepted") - 0.2, 0.25) or 0.001)
        mg.label(c, T, S("c5") + 0.1, ["BUTLIN, LONG ET AL. 2023", "INDICATORS FROM 5+ THEORIES"])
