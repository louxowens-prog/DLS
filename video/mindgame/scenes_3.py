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
        hx, hy, R = CH.jag(c, CX, 1450, T, s=1.6, eyes="wide", mouth="o", arms=(-158, 158), seed=820, tilt=4 * math.sin(T * 5))
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
        import scenes_2 as B
        mg.photo_scrap(c, B.earth_scrap(130, 0.3), 230, 660, mg.rect_pts(170, 605, 120, 110), T, seed=853, border=4)
        mg.photo_scrap(c, B.earth_scrap(130, 2.4), 355, 690, mg.rect_pts(295, 635, 120, 110), T, seed=854, border=4)
        mg.note(c, "yesterday", 290, 790, size=40)
        mg.stroke(c, mg.circle_pts(790, 690, 170, 40, rx=190, ry=150), T, 855, width=8, closed=True)
        mg.letters(c, "?", 790, 740, T, size=150, fname="permanent-marker-400", color=mg.PURPLE, outline=None, seed=856)
        for k, (x, y) in enumerate(((290, 900), (300, 960), (790, 900), (780, 960))):
            mg.stroke(c, mg.circle_pts(x, y, 18 - 6 * (k % 2), 12), T, 857 + k, width=6, closed=True)


def s_m2(arr, t, d, T):
    mg.paper(arr, (225, 250, 225), 18)
    s = mg.surf(arr)
    with s as c:
        tag(c, T, 2, "CONTINUAL LEARNING", mg.GREEN, S("m2") - 0.1)
        # a new board game
        for i in range(4):
            for j in range(4):
                sq = mg.rect_pts(120 + i * 80, 560 + j * 80, 80, 80)
                if (i + j) % 2:
                    mg.fill(c, sq, T, (60, 140, 80), 860 + i * 4 + j, off=(0, 0))
        mg.stroke(c, mg.rect_pts(120, 560, 320, 320), T, 870, width=8, closed=True)
        mg.note(c, "a new game", 280, 930, size=40)
        # skill over one hour
        ox, oy, gw, gh = 540, 900, 400, 340
        mg.stroke(c, [(ox, oy - gh), (ox, oy), (ox + gw, oy)], T, 871, width=8)
        mg.note(c, "1 hour", ox + gw - 60, oy + 50, size=40)
        mg.note(c, "skill", ox + 10, oy - gh - 20, size=40, align="left")
        k = ease(ramp(T, S("m2") + 0.8, Wd("m2", "better") + 0.2))
        hum = [(ox + gw * u * k, oy - gh * 0.9 * (1 - math.exp(-3 * u * k))) for u in np.linspace(0, 1, 20)]
        mg.stroke(c, hum, T, 872, width=10, color=mg.RED)
        jagl = [(ox + gw * u * k, oy - gh * 0.3) for u in np.linspace(0, 1, 20)]
        mg.stroke(c, jagl, T, 873, width=10, color=mg.CYAN)
        if k > 0.05:
            mg.letters(c, "YOU", hum[-1][0] - 10, hum[-1][1] - 22, T, size=50, fname="bangers-400", color=mg.RED, ow=6, seed=876)
            mg.letters(c, "AI", jagl[-1][0] - 10, jagl[-1][1] + 60, T, size=50, fname="bangers-400", color=mg.CYAN, ow=6, seed=877)
        kg = mg.pop(T, Wd("m2", "good") - 0.1, 0.25)
        if kg > 0:
            mg.stamp(c, "FOR GOOD", 740, 1090, T, Wd("m2", "good") - 0.1, color=mg.RED, size=70, rot=-6)
            mg.note(c, "(the AI stays where it was until it is retrained)", CX, 1200, size=34, color=(70, 90, 70))
        CH.human(c, 260, 1320, T, s=0.5, mouth="open" if k < 1 else "smile", seed=874, arms=(-160, 40 + 30 * math.sin(T * 6)))
        CH.jag(c, 830, 1320, T, s=0.5, eyes="normal", mouth="flat", seed=875, tilt=-8)


def s_m3(arr, t, d, T):
    mg.paper(arr, (255, 235, 210), 19)
    s = mg.surf(arr)
    drop = ease(ramp(T, S("m3") + 0.3, S("m3") + 0.8))
    kh = ramp(T, Wd("m3", "Hidden") - 0.1, Wd("m3", "Hidden") + 0.2)
    kt = ramp(T, Wd("m3", "teleport") - 0.5, Wd("m3", "teleport") - 0.2)
    with s as c:
        tag(c, T, 3, "WORLD MODEL", mg.ORANGE, S("m3") - 0.1)
        table = mg.rect_pts(330, 1060, 420, 34)
        mg.fill(c, table, T, (190, 130, 80), 880, off=(5, 4))
        mg.stroke(c, table, T, 881, width=8, closed=True)
        for x in (370, 710):
            mg.stroke(c, [(x, 1094), (x, 1290)], T, 882 + x, width=10)
        cup = np.array([(500, 930), (580, 930), (570, 1060), (510, 1060)])
        mg.fill(c, cup, T, WHITE, 885, off=(4, 3))
        mg.stroke(c, cup, T, 886, width=7, closed=True)
        cy = 700 + 330 * drop
        cloth = np.array([(430, cy + 30), (470, cy - 110), (610, cy - 110), (650, cy + 30)]) if drop < 1 else \
            np.array([(450, 1060), (480, 900), (600, 900), (630, 1060)])
        mg.fill(c, cloth, T, mg.RED, 887, off=(5, 4), a=0.97)
        mg.stroke(c, cloth, T, 888, width=8, closed=True)
        # what each of them thinks is under the cloth
        for who, bx, x0 in (("you", 250, 190), ("ai", 820, 880)):
            if kh <= 0:
                continue
            k = ease(kh)
            bub = mg.circle_pts(bx, 640, 0, 40, rx=200 * k + 1, ry=140 * k + 1)
            mg.fill(c, bub, T, WHITE, 893 + bx, off=(0, 0))
            mg.stroke(c, bub, T, 894 + bx, width=7, closed=True)
            for j, (px, py, r) in enumerate(((x0, 990, 10), (x0 + (bx - x0) * 0.35, 870, 16))):
                mg.stroke(c, mg.circle_pts(px, py, r, 12), T, 895 + bx + j, width=6, closed=True)
            if k < 0.9:
                continue
            if who == "you":
                mc = np.array([(bx - 30, 600), (bx + 30, 600), (bx + 24, 690), (bx - 24, 690)])
                mg.fill(c, mc, T, WHITE, 897, off=(3, 3))
                mg.stroke(c, mc, T, 898, width=6, closed=True)
                mg.stroke(c, np.array([(bx - 80, 700), (bx - 55, 580), (bx + 55, 580), (bx + 80, 700)]), T, 899, width=5,
                          color=mg.RED, closed=True)
                mg.note(c, "still there", bx, 745, size=38, color=(30, 130, 60))
            elif kt <= 0:
                mg.letters(c, "?", bx, 690, T, size=130, fname="permanent-marker-400", color=mg.ORANGE, outline=None, seed=900)
            else:
                import scenes_2 as B
                mg.photo_scrap(c, B.earth_scrap(150, 1.3), bx - 60, 630, mg.circle_pts(bx - 60, 630, 70, 24), T, seed=901, border=4)
                mc = np.array([(bx + 60, 590), (bx + 110, 600), (bx + 95, 675), (bx + 50, 665)])
                mg.fill(c, mc, T, WHITE, 902, off=(3, 3))
                mg.stroke(c, mc, T, 903, width=6, closed=True)
                mg.note(c, "in orbit?!", bx, 745, size=38, color=mg.RED)
        CH.human(c, 190, 1330, T, s=0.5, mouth="smile", seed=904, gaze=(1, -1), arms=(-30, 60))
        CH.jag(c, 880, 1330, T, s=0.5, eyes="spiral" if kt > 0 else "wide", mouth="o", seed=889, gaze=(-1, -1), tilt=6)


def s_m4(arr, t, d, T):
    if T < Wd("m4", "The") - 0.05:
        s_road(arr, T)
    else:
        s_horizon(arr, T)


def s_road(arr, T):
    """Ten years of medical school: a long road, a calendar shedding pages."""
    mg.paper(arr, (230, 240, 255), 20)
    s = mg.surf(arr)
    with s as c:
        tag(c, T, 4, "LONG-TERM GOALS", mg.BLUE, S("m4") - 0.1)
        road = np.array([(40, 1150), (1040, 700), (1040, 800), (40, 1290)])
        mg.fill(c, road, T, (170, 170, 175), 900, off=(4, 3))
        mg.stroke(c, road, T, 901, width=7, closed=True)
        for k in range(10):
            x = 90 + k * 95
            y = 1215 - k * 44
            mg.stroke(c, [(x, y), (x + 40, y - 18)], T, 902 + k, width=6, color=WHITE)
            mg.note(c, f"yr {k + 1}", x + 20, y - 60, size=30, color=(60, 70, 100))
        k = ramp(T, S("m4") + 0.3, Wd("m4", "The") - 0.1)
        hx = 110 + 780 * k
        CH.human(c, hx, 1220 - 440 * k * 1.0 + 0, T, s=0.45, mouth="smile", seed=917, legs=0.45 * math.sin(T * 12),
                 arms=(-40 + 30 * math.sin(T * 12), 40 - 30 * math.sin(T * 12)))
        # calendar
        cal = mg.rect_pts(640, 470, 300, 210)
        mg.fill(c, cal, T, WHITE, 918, off=(5, 4))
        mg.stroke(c, cal, T, 919, width=7, closed=True)
        mg.fill(c, mg.rect_pts(640, 470, 300, 50), T, mg.RED, 920, off=(0, 0))
        yr = 2026 + int(10 * ease(k))
        mg.letters(c, str(yr), 790, 640, T, size=90, fname="rubik-900", color=INK, outline=None, seed=921, jig=1, rot=1)
        mg.letters(c, "MD", 960, 650, T, size=80, fname="bangers-400", color=mg.RED, ow=8, seed=916) if k >= 1 else None
        mg.letters(c, "10 YEARS", 300, 640, T, size=96, fname="bangers-400", color=mg.BLUE, ow=10, seed=915)


HZ = [("1 sec", 0.0), ("1 min", 1.78), ("1 hour", 3.56), ("1 day", 4.94), ("1 month", 6.41), ("1 year", 7.5), ("10 years", 8.5)]


def s_horizon(arr, T):
    """METR time horizons on a log scale: doubling every ~7 months, still far below a ten-year goal."""
    mg.paper(arr, (240, 236, 255), 26)
    s = mg.surf(arr)
    ox, x1, y0, dec = 250, 900, 1180, 73.0
    Y = lambda lg: y0 - lg * dec
    with s as c:
        tag(c, T, 4, "LONG-TERM GOALS", mg.BLUE, S("m4") - 1)
        mg.note(c, "longest tasks AI agents finish (half the time)", CX, 500, size=38)
        mg.stroke(c, [(ox, Y(8.9)), (ox, y0), (x1 + 40, y0)], T, 918, width=8)
        for i, (lab, lg) in enumerate(HZ):
            mg.stroke(c, [(ox - 14, Y(lg)), (ox + 6, Y(lg))], T, 930 + i, width=5)
            mg.note(c, lab, ox - 24, Y(lg) + 12, size=32, align="right", color=INK if lab != "10 years" else mg.RED)
        mg.note(c, "2019", ox + 30, y0 + 44, size=34)
        mg.note(c, "2026", x1, y0 + 44, size=34)
        k = ease(ramp(T, Wd("m4", "length") - 0.1, Wd("m4", "months")))
        l0, l1 = math.log10(2), math.log10(3 * 3600)
        pts = [(ox + 30 + (x1 - ox - 30) * u * k, Y(l0 + (l1 - l0) * u * k)) for u in np.linspace(0, 1, 24)]
        mg.stroke(c, pts, T, 940, width=11, color=mg.ORANGE)
        if k > 0.02:
            c.drawCircle(pts[-1][0], pts[-1][1], 14, mg.paint(mg.ORANGE))
        kd = mg.pop(T, Wd("m4", "doubles") - 0.1, 0.25)
        if kd > 0:
            c.save()
            c.translate(560, 1000)
            c.rotate(-27)
            mg.note(c, "x2 every ~7 months", 0, 0, size=42 * kd, color=mg.ORANGE)
            c.restore()
        # the goal: ten years, way up the scale
        mg.stroke(c, [(x1 - 40, Y(8.5)), (x1 + 40, Y(8.5))], T, 941, width=8, color=mg.RED)
        mg.note(c, "becoming a doctor", x1 - 10, Y(8.5) - 20, size=36, color=mg.RED, align="right")
        kh = ease(ramp(T, Wd("m4", "hours") - 0.2, Wd("m4", "hours") + 0.4))
        if kh > 0:
            ytop = Y(l1) - (Y(l1) - Y(8.5)) * kh
            for j in range(int((Y(l1) - ytop) / 28)):
                ya = Y(l1) - 20 - j * 28
                c.drawLine(x1, ya, x1, ya - 14, mg.paint(mg.RED, 0.9, stroke=6))
            mg.stamp(c, "HOURS, NOT YEARS", 560, 700, T, Wd("m4", "hours") - 0.1, color=mg.RED, size=76, rot=-4)
        mg.label(c, T, Wd("m4", "The") + 0.2, ["METR TIME HORIZONS, 2025-26"], y=300)


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
        CH.human(c, 520, 1360, T, s=0.6, mouth="open" if kt > 0.5 else "smile", eyes="wide" if kt > 0.5 else "normal",
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
        CH.jag(c, 820, 1360, T, s=0.55, eyes="normal", mouth="flat", seed=945, arms=(-150, 150), tilt=-6)


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
        hx, hy, R = CH.jag(c, 300, 1360, T, s=0.6, eyes="normal", mouth="open", seed=955, arms=(-40, 150), tilt=5)
        bub = mg.rect_pts(420, 930, 520, 200)
        mg.fill(c, bub, T, WHITE, 956, off=(5, 4))
        mg.stroke(c, bub, T, 957, width=7, closed=True)
        mg.note(c, "Definitely 1847!", 680, 1010, size=52)
        mg.note(c, "(a confident guess)", 680, 1070, size=36, color=(120, 120, 120))
        mg.label(c, T, S("m6") + 1.0, ["OPENAI RESEARCH, 2025"], y=300)


# ------------------------------------------------------------------ finale

def s_finale(arr, t, d, T):
    """Frantic montage: earlier shots re-cut every few frames in clashing styles, as in the film's climax.

    Only light shots, no inversions, and cuts on fours, so the rush never becomes a strobe."""
    import scenes_1 as A
    import scenes_2 as B
    pool = [(A.s_gold, S("h1") + 1.0, "cel"), (A.s_clock, C["half"] + 0.6, "pencil"), (A.s_agents, E("a2") - 0.3, "crayon"),
            (A.s_robot, E("a3"), "pencil"), (A.s_levels, E("l4") + 1.5, "cel"), (B.s_score, E("g2") - 0.2, "crayon"),
            (B.s_montage, C["montage"][5] + 0.2, "print"), (B.s_water2, E("g7") - 0.3, "crayon"),
            (B.s_octo, E("c4") - 0.3, "print"), (s_m0, E("m0"), "cel"), (s_m3, E("m3") - 0.2, "cel"),
            (s_m5, E("m5") - 0.2, "crayon"), (A.s_nobody, E("a4") - 0.3, "crayon"), (B.s_nature, E("g1") - 0.3, "print"),
            (s_m2, E("m2") - 0.2, "pencil"), (B.s_notif, E("g4") - 0.2, "cel")]
    blk = int(T * 24) // 4
    rng = np.random.default_rng(blk)
    last = int(np.random.default_rng(blk - 1).integers(len(pool)))
    i = int(rng.integers(len(pool) - 1))
    i = i + 1 if i >= last else i
    fn, tt, st = pool[i]
    mg.set_style(st)
    fn(arr, 1.0, 2.0, tt + (T - C["finale"]) * 0.3)
    fx = blk % 4
    if fx == 1:
        pal = np.array([mg.YELLOW, mg.PINK, mg.CYAN, (255, 250, 235)], np.uint8)
        lum = arr[..., :3].mean(-1)
        arr[..., :3] = pal[(lum / 64).astype(int).clip(0, 3)]
    elif fx == 3:
        mg.fisheye(arr, 0.7)
    s = mg.surf(arr)
    with s as c:
        mg.speed_lines(c, CX, 880, T, n=30, color=WHITE, r0=520, seed=blk)


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
        for i, ln in enumerate(["Style homage to Mind Game (2004, dir. Masaaki Yuasa)", "Earth imagery: NASA Blue Marble",
                                "Music and voice synthesized"]):
            c.drawString(ln, CX - f2.measureText(ln) / 2, 1410 + i * 36, f2, mg.paint((170, 170, 180)))


def insert_face(who, bg, text, t0):
    """Returns a shot function: a huge, boiling close-up of a character with a shouted word."""
    def shot(arr, t, dd, T):
        if bg == "burst":
            mg.burst(arr, CX, 800, T, spin=2.2)
        elif bg == "swirl":
            mg.swirl(arr, T * 1.5, scale=0.7)
        else:
            mg.paper(arr, bg, 25)
        s = mg.surf(arr)
        with s as c:
            dx, dy = mg.shake(T, 14, 900)
            c.save()
            c.translate(dx, dy)
            mg.speed_lines(c, CX, 820, T, n=40, color=WHITE, r0=520, seed=901)
            if who == "jag":
                CH.jag(c, CX, 2050, T, s=3.3, eyes="spiral" if text == "?!" else "wide", mouth="o" if text != "!!" else "open",
                       arms=(-150, 150), seed=902)
            else:
                CH.human(c, CX, 2150, T, s=3.0, mouth="open", eyes="wide", seed=903, arms=(-160, 160))
            c.restore()
            if text:
                mg.letters(c, text, CX, 470, T, size=220, fname="bangers-400", color=mg.YELLOW, ow=18, seed=904,
                           scale=mg.pop(T, t0, 0.2) or 0.001)
    shot.__name__ = f"insert_{who}"
    return shot
