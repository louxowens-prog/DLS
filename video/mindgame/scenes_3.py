"""What's still missing, the frantic montage finale, the calm last shot, the end card."""
import math

import numpy as np
import skia

import chars as CH
import mg
from mg import CX, H, INK, W, WHITE, ease, ramp
from cues import C
from timeline import TL

S, E, Wd = TL.s, TL.e, TL.word


def tag(c, T, n, name, col, t0):
    """Big numbered header for each missing piece."""
    k = mg.pop(T, t0, 0.25)
    if k <= 0:
        return
    mg.letters(c, f"{n}", 130, 420, T, size=190 * k, fname="bangers-400", color=col, ow=14, seed=800 + n)
    mg.letters(c, name, 590, 390, T, size=86 * k if len(name) < 14 else 70 * k, fname="bangers-400", color=INK,
               outline=None, seed=810 + n, jig=1.5, rot=2, spacing=3)


def s_m0(arr, t, d, T):
    mg.burst(arr, CX, 900, T, colors=[mg.YELLOW, mg.ORANGE, mg.RED, mg.PINK], spin=1.0)
    s = mg.surf(arr)
    with s as c:
        hx, hy, R = CH.jag(c, CX, 1450, T, s=1.6, eyes="wide", mouth="o", arms=(-120, 120), seed=820)
        # puzzle holes in its head
        for i, (dx, dy) in enumerate(((-0.45, -0.55), (0.35, -0.7), (0.05, -0.2))):
            px, py = hx + dx * R, hy + dy * R
            hole = np.vstack([mg.circle_pts(px, py, 28, 20), mg.circle_pts(px + 30, py, 14, 10)])
            c.drawCircle(px, py, 32, mg.paint((25, 20, 30)))
            c.drawCircle(px + 32, py, 15, mg.paint((25, 20, 30)))
            mg.stroke(c, mg.circle_pts(px, py, 32, 20), T, 821 + i, width=5, closed=True)
        mg.letters(c, "WHAT'S", CX, 380, T, size=140, fname="bangers-400", color=WHITE, ow=14, seed=830, spacing=4)
        mg.letters(c, "MISSING?", CX, 540, T, size=160, fname="bangers-400", color=WHITE, ow=16, seed=831, spacing=4)


def s_m1(arr, t, d, T):
    mg.paper(arr, (235, 230, 250), 17)
    s = mg.surf(arr)
    with s as c:
        tag(c, T, 1, "MEMORY", mg.PURPLE, S("m1") - 0.1)
        for side, x in ((-1, 290), (1, 790)):
            bed = mg.rect_pts(x - 200, 1180, 400, 120)
            mg.fill(c, bed, T, (180, 200, 255) if side < 0 else (200, 240, 255), 840 + side, off=(6, 4))
            mg.stroke(c, bed, T, 842 + side, width=8, closed=True)
            mg.stroke(c, [(x - 200, 1300), (x - 200, 1360)], T, 844 + side, width=8)
            mg.stroke(c, [(x + 200, 1300), (x + 200, 1360)], T, 846 + side, width=8)
        CH.human(c, 290, 1210, T, s=0.62, mouth="smile", eyes="normal", seed=850, arms=(-160, 20))
        CH.jag(c, 790, 1210, T, s=0.6, eyes="wide", mouth="o", seed=851, arms=(-30, 30))
        # thought bubbles: memories vs blank
        mg.stroke(c, mg.circle_pts(290, 690, 170, 40, rx=190, ry=150), T, 852, width=8, closed=True)
        mg.collage(c, "earth_ne2.jpg", mg.rect_pts(170, 610, 120, 100), T, seed=853, src=(300, 100), scale=0.8, border=4)
        mg.collage(c, "moon.jpg", mg.rect_pts(300, 640, 120, 100), T, seed=854, src=(50, 30), scale=2.0, border=4)
        mg.note(c, "yesterday", 290, 790, size=40)
        mg.stroke(c, mg.circle_pts(790, 690, 170, 40, rx=190, ry=150), T, 855, width=8, closed=True)
        mg.letters(c, "?", 790, 740, T, size=150, fname="permanent-marker-400", color=mg.PURPLE, outline=None, seed=856)
        for k, (x, y) in enumerate(((290, 900), (300, 960), (790, 900), (780, 960))):
            mg.stroke(c, mg.circle_pts(x, y, 18 - 6 * (k % 2), 12), T, 857 + k, width=6, closed=True)


def s_m2(arr, t, d, T):
    mg.paper(arr, (225, 250, 225), 18)
    s = mg.surf(arr)
    with s as c:
        tag(c, T, 2, "KEEPS LEARNING", mg.GREEN, S("m2") - 0.1)
        # a new board game
        for i in range(4):
            for j in range(4):
                sq = mg.rect_pts(140 + i * 80, 540 + j * 80, 80, 80)
                if (i + j) % 2:
                    mg.fill(c, sq, T, (60, 140, 80), 860 + i * 4 + j, off=(0, 0))
        mg.stroke(c, mg.rect_pts(140, 540, 320, 320), T, 870, width=8, closed=True)
        # skill over one hour
        ox, oy, gw, gh = 560, 900, 400, 340
        mg.stroke(c, [(ox, oy - gh), (ox, oy), (ox + gw, oy)], T, 871, width=8)
        mg.note(c, "1 hour", ox + gw - 60, oy + 50, size=40)
        mg.note(c, "skill", ox - 10, oy - gh - 20, size=40)
        k = ease(ramp(T, S("m2") + 0.8, E("m2")))
        hum = [(ox + gw * u * k, oy - gh * 0.9 * (1 - math.exp(-3 * u * k))) for u in np.linspace(0, 1, 20)]
        mg.stroke(c, hum, T, 872, width=10, color=mg.RED)
        jagl = [(ox + gw * u * k, oy - gh * 0.35) for u in np.linspace(0, 1, 20)]
        mg.stroke(c, jagl, T, 873, width=10, color=mg.CYAN)
        CH.human(c, 300, 1400, T, s=0.55, mouth="open", seed=874, arms=(-160, 40))
        CH.jag(c, 760, 1400, T, s=0.55, eyes="normal", mouth="flat", seed=875)
        mg.note(c, "you: better, for good", 300, 1500 - 60, size=40, color=mg.RED) if False else None


def s_m3(arr, t, d, T):
    mg.paper(arr, (255, 235, 210), 19)
    s = mg.surf(arr)
    with s as c:
        tag(c, T, 3, "WORLD MODEL", mg.ORANGE, S("m3") - 0.1)
        table = mg.rect_pts(120, 1000, 840, 40)
        mg.fill(c, table, T, (190, 130, 80), 880, off=(5, 4))
        mg.stroke(c, table, T, 881, width=8, closed=True)
        for x in (180, 900):
            mg.stroke(c, [(x, 1040), (x, 1300)], T, 882 + x, width=10)
        lift = ease(ramp(T, Wd("m3", "Hidden") + 0.3, Wd("m3", "Hidden") + 0.7))
        cloth = np.array([(380, 1000), (430, 800 - 300 * lift), (650, 800 - 300 * lift), (700, 1000)])
        tele = ramp(T, Wd("m3", "teleport") - 0.4, Wd("m3", "teleport"))
        if lift < 0.5 or tele < 0.5:
            cup = np.array([(500, 870), (580, 870), (570, 1000), (510, 1000)])
            mg.fill(c, cup, T, WHITE, 885, off=(4, 3))
            mg.stroke(c, cup, T, 886, width=7, closed=True)
        mg.fill(c, cloth, T, mg.RED, 887, off=(5, 4), a=0.95)
        mg.stroke(c, cloth, T, 888, width=8, closed=True)
        hx, hy, R = CH.jag(c, 800, 1600 - 100, T, s=0.6, eyes="wide", mouth="o", seed=889)
        if tele >= 0.5:
            cup = np.array([(hx - 40, hy - R - 120), (hx + 40, hy - R - 120), (hx + 30, hy - R), (hx - 30, hy - R)])
            mg.fill(c, cup, T, WHITE, 890, off=(4, 3))
            mg.stroke(c, cup, T, 891, width=7, closed=True)
            mg.letters(c, "?!", hx + 110, hy - R - 60, T, size=110, fname="bangers-400", color=mg.RED, ow=10, seed=892)


def s_m4(arr, t, d, T):
    mg.paper(arr, (230, 240, 255), 20)
    s = mg.surf(arr)
    with s as c:
        tag(c, T, 4, "LONG-TERM GOALS", mg.BLUE, S("m4") - 0.1)
        # the ten-year road
        road = np.array([(60, 700), (1020, 560), (1020, 640), (60, 800)])
        mg.fill(c, road, T, (170, 170, 175), 900, off=(4, 3))
        mg.stroke(c, road, T, 901, width=7, closed=True)
        for k in range(10):
            x = 100 + k * 90
            mg.stroke(c, [(x, 752 - k * 14), (x + 40, 746 - k * 14)], T, 902 + k, width=6, color=WHITE)
        mg.letters(c, "10 YEARS", 330, 870, T, size=70, fname="bangers-400", color=mg.BLUE, ow=8, seed=915)
        mg.letters(c, "MD", 960, 520, T, size=90, fname="bangers-400", color=mg.RED, ow=8, seed=916)
        k = ramp(T, S("m4"), Wd("m4", "doubles"))
        CH.human(c, 140 + 700 * k, 760 - 100 * k, T, s=0.4, mouth="smile", seed=917, legs=0.4 * math.sin(T * 10))
        # the task-length curve: doubling about every 7 months
        kc = ease(ramp(T, Wd("m4", "doubles") - 0.2, Wd("m4", "doubles") + 0.8))
        ox, oy, gw, gh = 200, 1390, 700, 380
        mg.stroke(c, [(ox, oy - gh), (ox, oy), (ox + gw, oy)], T, 918, width=8)
        pts = [(ox + gw * u * kc, oy - gh * (2 ** (7 * u * kc) - 1) / (2 ** 7 - 1)) for u in np.linspace(0, 1, 40)]
        mg.stroke(c, pts, T, 919, width=10, color=mg.ORANGE)
        mg.note(c, "task length AI agents can finish", ox + 20, oy - gh - 25, size=38, align="left")
        mg.note(c, "x2 every ~7 months", ox + gw - 230, oy - 60, size=40, color=mg.ORANGE)
        kh = ease(ramp(T, Wd("m4", "hours") - 0.2, Wd("m4", "hours") + 0.2))
        if kh > 0:
            mg.stamp(c, "HOURS, NOT YEARS", CX, 1030, T, Wd("m4", "hours") - 0.1, color=mg.RED, size=80, rot=-5)
        mg.label(c, T, S("m4") + 1.0, ["METR, 2025-26"], y=300)


def s_m5(arr, t, d, T):
    mg.paper(arr, (255, 230, 220), 21)
    s = mg.surf(arr)
    with s as c:
        tag(c, T, 5, "GROUNDING", mg.RED, S("m5") - 0.1)
        stove = mg.rect_pts(140, 980, 400, 260)
        mg.fill(c, stove, T, (90, 90, 100), 930, off=(6, 4))
        mg.stroke(c, stove, T, 931, width=8, closed=True)
        rng = np.random.default_rng(mg.step(T))
        for k in range(7):
            x = 200 + k * 48
            h = 90 + 50 * rng.random()
            fl = np.array([(x - 22, 980), (x, 980 - h), (x + 22, 980)])
            mg.fill(c, fl, T, mg.PSY[(k + mg.step(T)) % 4], 932 + k, off=(0, 0))
        kt = ease(ramp(T, Wd("m5", "touched") - 0.2, Wd("m5", "touched")))
        CH.human(c, 520, 1450, T, s=0.6, mouth="open" if kt > 0.5 else "smile", eyes="wide" if kt > 0.5 else "normal",
                 seed=940, arms=(-40, -120 + 60 * kt))
        if kt > 0.5:
            mg.letters(c, "HOT!!", 330, 820, T, size=150, fname="bangers-400", color=mg.RED, ow=14, seed=941, jig=10, rot=10)
        book = mg.rect_pts(640, 620, 330, 240)
        mg.fill(c, book, T, WHITE, 942, off=(6, 4))
        mg.stroke(c, book, T, 943, width=7, closed=True)
        mg.stroke(c, [(805, 620), (805, 860)], T, 944, width=6)
        mg.note(c, "hot (adj.)", 720, 700, size=38)
        mg.note(c, "high in", 720, 750, size=32)
        mg.note(c, "temperature", 720, 790, size=32)
        CH.jag(c, 810, 1450, T, s=0.55, eyes="normal", mouth="flat", seed=945, arms=(-150, 150))


def s_m6(arr, t, d, T):
    mg.paper(arr, (240, 240, 240), 22)
    s = mg.surf(arr)
    with s as c:
        tag(c, T, 6, "\"I DON'T KNOW\"", mg.PURPLE, S("m6") - 0.1)
        # scoreboard: guessing beats honesty under accuracy-only grading
        board = mg.rect_pts(120, 560, 840, 330)
        mg.fill(c, board, T, (30, 60, 40), 950, off=(7, 5))
        mg.stroke(c, board, T, 951, width=9, closed=True)
        mg.letters(c, "TYPICAL TEST SCORING", CX, 640, T, size=56, fname="bangers-400", color=WHITE, outline=None, seed=952, spacing=2)
        kr = ease(ramp(T, Wd("m6", "reward") - 0.3, Wd("m6", "reward")))
        mg.letters(c, "LUCKY GUESS  +1", CX, 750, T, size=62, fname="rubik-800", color=mg.YELLOW, outline=None, seed=953, jig=1, rot=0.5, a=kr)
        mg.letters(c, "\"I DON'T KNOW\"  0", CX, 840, T, size=62, fname="rubik-800", color=(255, 150, 150), outline=None, seed=954, jig=1, rot=0.5, a=kr)
        hx, hy, R = CH.jag(c, 330, 1470, T, s=0.6, eyes="normal", mouth="open", seed=955, arms=(-40, 150))
        bub = mg.rect_pts(420, 930, 520, 200)
        mg.fill(c, bub, T, WHITE, 956, off=(5, 4))
        mg.stroke(c, bub, T, 957, width=7, closed=True)
        mg.note(c, "Definitely 1847!", 680, 1010, size=52)
        mg.note(c, "(a confident guess)", 680, 1070, size=36, color=(120, 120, 120))
        mg.label(c, T, S("m6") + 1.0, ["OPENAI RESEARCH, 2025"], y=300)


# ------------------------------------------------------------------ finale

def s_finale(arr, t, d, T):
    """Frantic montage: earlier shots re-cut every few frames in clashing styles, as in the film's climax."""
    import scenes_1 as A
    import scenes_2 as B
    pool = [(A.s_gold, S("h1") + 1.0), (A.s_clock, C["half"] + 0.3), (A.s_title, C["title"] + 0.3),
            (A.s_agents, E("a2") - 0.3), (A.s_robot, E("a3")), (A.s_levels, E("l4") - 0.2),
            (B.s_score, E("g2") - 0.2), (B.s_montage, C["montage"][5] + 0.2), (B.s_water2, E("g7") - 0.3),
            (B.s_octo, E("c4") - 0.3), (s_m0, E("m0")), (s_m3, E("m3") - 0.2), (s_m5, E("m5") - 0.2),
            (B.s_montage, C["montage"][2] + 0.2), (A.s_nobody, E("a4") - 0.3)]
    blk = int(T * 24) // 3
    rng = np.random.default_rng(blk)
    fn, tt = pool[int(rng.integers(len(pool)))]
    fn(arr, 1.0, 2.0, tt + (T - C["finale"]) * 0.3)
    fx = blk % 5
    if fx == 1:
        arr[..., :3] = 255 - arr[..., :3]
    elif fx == 2:
        pal = np.array([mg.RED, mg.YELLOW, mg.CYAN, mg.PURPLE], np.uint8)
        lum = arr[..., :3].mean(-1)
        arr[..., :3] = pal[(lum / 64).astype(int).clip(0, 3)]
    elif fx == 3:
        mg.fisheye(arr, 0.7)
    s = mg.surf(arr)
    with s as c:
        mg.speed_lines(c, CX, 880, T, n=30, color=WHITE if fx != 1 else INK, r0=520, seed=blk)


def s_final(arr, t, d, T):
    mg.paper(arr, (255, 205, 160), 23)
    y = np.linspace(0, 1, H)[:, None, None]
    sky = np.array([255, 150, 120]) * (1 - y) + np.array([255, 220, 170]) * y
    arr[..., :3] = (arr[..., :3] * 0.4 + sky * 0.6).astype(np.uint8)
    s = mg.surf(arr)
    lvl = 1450 - (1450 - 470) * 0.66
    import scenes_2 as B
    with s as c:
        c.drawCircle(CX, 640, 150, mg.paint((255, 240, 200)))
        B.mountains(c, T, lvl, B.LEFT, seed=970)
        B.water(c, T, lvl, seed=980, alpha=1.0)
        top = 1450 - (1450 - 470) * 1.0
        CH.human(c, 575, top + 8, T, s=0.34, mouth="smile", seed=990, bob=False)
        CH.jag(c, 668, top + 8, T, s=0.32, eyes="normal", mouth="smile", seed=991, bob=False)


SOURCES = ["Stanford HAI, AI Index 2026", "Nature Comment, Feb 2026 (UC San Diego)", "Hendrycks et al., A Definition of AGI (2025)",
           "Google DeepMind, Levels of AGI (2023)", "Butlin, Long et al., Consciousness in AI (2023)",
           "METR, AI time horizons (2025-26)", "OpenAI, Why Language Models Hallucinate (2025)"]


def s_end(arr, t, d, T):
    mg.paper(arr, (25, 22, 30), 24)
    s = mg.surf(arr)
    with s as c:
        mg.letters(c, "JAGGED", CX, 820, T, size=230, fname="bangers-400", color=mg.YELLOW, ow=18, seed=995, spacing=6)
        mg.letters(c, "WHAT HAS ACTUALLY HAPPENED IN AI", CX, 930, T, size=50, fname="rubik-800", color=WHITE, outline=None, seed=996, jig=0.5, rot=0.3)
        f = mg.font("rubik-500", 30)
        mg.letters(c, "SOURCES", CX, 1040, T, size=36, fname="rubik-800", color=mg.YELLOW, outline=None, seed=997, jig=0.5, rot=0.3)
        for i, ln in enumerate(SOURCES):
            c.drawString(ln, CX - f.measureText(ln) / 2, 1095 + i * 40, f, mg.paint((215, 215, 225)))
        f2 = mg.font("rubik-500", 26)
        for i, ln in enumerate(["Style homage to Mind Game (2004, dir. Masaaki Yuasa)", "Music and voice synthesized"]):
            c.drawString(ln, CX - f2.measureText(ln) / 2, 1410 + i * 36, f2, mg.paint((170, 170, 180)))
