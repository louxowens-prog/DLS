"""What's still missing, the frantic montage finale, the calm last shot, the end card."""
import math

import numpy as np
import skia

import chars as CH
import fx3
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
        for i, (dx, dy) in enumerate(((-0.5, -0.62), (0.42, -0.7), (-0.02, -0.9))):
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
        cup_scrap(c, T, 230, 665, 100, seed=853, rot=-8)
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
            mg.stamp(c, "FOR GOOD", 560, 1100, T, Wd("m2", "good") - 0.1, color=mg.RED, size=70, rot=-6)
            mg.note(c, "(the AI stays put until it is retrained)", CX, 1010, size=36, color=(60, 80, 60))
        CH.human(c, 260, 1320, T, s=0.5, mouth="open" if k < 1 else "smile", seed=874, arms=(-160, 40 + 30 * math.sin(T * 6)))
        CH.jag(c, 830, 1320, T, s=0.5, eyes="normal", mouth="flat", seed=875, tilt=-8)


_cup = {}


def cup_photo(w):
    """The espresso cup from a CC0 photograph, cropped around the cup."""
    if w not in _cup:
        from PIL import Image
        im = Image.open(mg.TEX + "/coffee.jpg").convert("RGB").crop((160, 5, 425, 312))
        im = im.resize((w, int(w * im.size[1] / im.size[0])), Image.LANCZOS)
        a = np.asarray(im)
        _cup[w] = np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])
    return _cup[w]


def cup_scrap(c, T, x, y, w, seed=0, rot=0.0):
    img = cup_photo(w)
    h = img.shape[0]
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    mg.photo_scrap(c, img, 0, 0, mg.rect_pts(-w / 2 + 4, -h / 2 + 4, w - 8, h - 8), T, seed=seed, border=4)
    c.restore()


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
        cup_scrap(c, T, 540, 996, 112, seed=885)
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
                cup_scrap(c, T, bx, 648, 64, seed=897)
                mg.stroke(c, np.array([(bx - 80, 700), (bx - 55, 580), (bx + 55, 580), (bx + 80, 700)]), T, 899, width=5,
                          color=mg.RED, closed=True)
                mg.note(c, "still there", bx, 745, size=38, color=(30, 130, 60))
            elif kt <= 0:
                mg.letters(c, "?", bx, 690, T, size=130, fname="permanent-marker-400", color=mg.ORANGE, outline=None, seed=900)
            else:
                import scenes_2 as B
                mg.photo_scrap(c, B.earth_scrap(150, 1.3), bx - 60, 630, mg.circle_pts(bx - 60, 630, 70, 24), T, seed=901, border=4)
                cup_scrap(c, T, bx + 82, 628, 58, seed=902, rot=25 * math.sin(T * 3))
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
        l0, l1 = math.log10(2), math.log10(14 * 3600)
        pts = [(ox + 30 + (x1 - ox - 30) * u * k, Y(l0 + (l1 - l0) * u * k)) for u in np.linspace(0, 1, 24)]
        mg.stroke(c, pts, T, 940, width=11, color=mg.ORANGE)
        if k > 0.02:
            c.drawCircle(pts[-1][0], pts[-1][1], 14, mg.paint(mg.ORANGE))
        kd = mg.pop(T, Wd("m4", "doubles") - 0.1, 0.25)
        if kd > 0:
            c.save()
            c.translate(560, 990)
            c.rotate(-33)
            mg.note(c, "x2 every 4-7 months", 0, 0, size=42 * kd, color=mg.ORANGE)
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
            mg.fill(c, fl, T, [mg.RED, mg.ORANGE, mg.YELLOW][(k + mg.step(T)) % 3], 932 + k, off=(0, 0))
        for k in range(4):
            c.drawCircle(200 + k * 95, 1180, 18, mg.paint(WHITE))
            mg.stroke(c, mg.circle_pts(200 + k * 95, 1180, 18, 12), T, 960 + k, width=4, closed=True)
        mg.stroke(c, [(150, 985), (530, 985)], T, 965, width=10, color=(50, 50, 55))
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

def _card(c, T, text, col=mg.YELLOW, y=380):
    mg.letters(c, text, CX, y, T, size=120, fname="bangers-400", color=col, ow=14, seed=hash(text) % 997, spacing=3)


def fut_doctor(arr, T):
    fx3.painterly(arr, [(0, (200, 235, 255)), (1, (240, 250, 255))], seed=41, T=T, n=1800, jit=10)
    s = mg.surf(arr)
    with s as c:
        mg.fill(c, mg.rect_pts(780, 520, 160, 160), T, WHITE, 1001, off=(4, 3))
        mg.fill(c, mg.rect_pts(840, 540, 40, 120), T, mg.RED, 1002, off=(0, 0))
        mg.fill(c, mg.rect_pts(800, 580, 120, 40), T, mg.RED, 1003, off=(0, 0))
        hx, hy, R = CH.jag(c, 480, 1290, T, s=1.15, arms=(-60, 120), mouth="smile", seed=1004, body_col=WHITE, head_col=mg.CYAN)
        mg.stroke(c, mg.bez((440, hy + R + 40), (480, hy + R + 170), (530, hy + R + 50)), T, 1005, width=9, color=(60, 60, 70))
        c.drawCircle(480, hy + R + 150, 18, mg.paint((160, 160, 170)))
        _card(c, T, "AI DOCTOR?")


def fut_mars(arr, T):
    mg.paper(arr, (255, 200, 120), 42)
    fx3.footage(arr, "rocket.jpg", T, (T * 0.4) % 1, rect=(40, 560, W - 80, 660), z0=1.05, z1=1.3, fy=0.35)
    s = mg.surf(arr)
    with s as c:
        _card(c, T, "MARS?", mg.RED)


def fut_friends(arr, T):
    fx3.painterly(arr, [(0, (255, 170, 120)), (0.6, (255, 220, 170)), (1, (250, 150, 170))], seed=43, T=T, n=1800, jit=10)
    s = mg.surf(arr)
    with s as c:
        CH.human(c, 420, 1250, T, s=0.95, arms=(-150, 150), mouth="open", seed=1010, tilt=8)
        CH.jag(c, 680, 1250, T, s=0.9, arms=(-150, 150), mouth="open", seed=1011, tilt=-8)
        for k in range(5):
            x, y = 300 + k * 120, 640 - 40 * math.sin(T * 6 + k)
            mg.letters(c, "♥" if False else "<3", x, y, T, size=60, fname="bangers-400", color=mg.PINK, ow=6, seed=1012 + k)
        _card(c, T, "FRIENDS?", mg.PINK)


def fut_memory(arr, T):
    mg.paper(arr, (230, 220, 255), 44)
    s = mg.surf(arr)
    import scenes_2 as B
    with s as c:
        book = mg.rect_pts(150, 560, 780, 480)
        mg.fill(c, book, T, (255, 250, 240), 1020, off=(8, 6))
        mg.stroke(c, book, T, 1021, width=8, closed=True)
        mg.stroke(c, [(540, 560), (540, 1040)], T, 1022, width=6)
        mg.photo_scrap(c, B.earth_scrap(200, 0.3), 330, 720, mg.rect_pts(240, 630, 180, 180), T, seed=1023, border=5)
        cup_scrap(c, T, 750, 720, 150, seed=1024, rot=-6)
        mg.note(c, "yesterday", 330, 880, size=44)
        mg.note(c, "last year", 750, 880, size=44)
        CH.jag(c, 540, 1330, T, s=0.6, mouth="smile", seed=1025, arms=(-150, 150))
        _card(c, T, "REMEMBERS?", mg.PURPLE)


def fut_science(arr, T):
    mg.paper(arr, (255, 190, 220), 45)
    fx3.footage(arr, "hubble.jpg", T, (T * 0.5) % 1, rect=(40, 560, W - 80, 660), z0=1.0, z1=1.5)
    s = mg.surf(arr)
    with s as c:
        _card(c, T, "DISCOVERIES?", mg.BLUE)


def fut_chores(arr, T):
    mg.paper(arr, (210, 250, 220), 46)
    s = mg.surf(arr)
    with s as c:
        hand = CH.robot(c, 380, 1280, T, s=1.3, arm=0.3 + 0.3 * math.sin(T * 8), seed=1030)
        shirt = np.array([(-90, -60), (-40, -80), (40, -80), (90, -60), (70, -20), (45, -30), (45, 70), (-45, 70), (-45, -30), (-70, -20)])
        mg.fill(c, shirt + (hand[0] + 90, hand[1] + 40), T, mg.RED, 1031, off=(4, 3))
        mg.stroke(c, shirt + (hand[0] + 90, hand[1] + 40), T, 1032, width=6, closed=True)
        _card(c, T, "CHORES?", mg.GREEN)


def fut_honest(arr, T):
    mg.burst(arr, CX, 900, T, colors=[(255, 240, 200), (255, 220, 150)], rays=12, spin=0.6)
    s = mg.surf(arr)
    with s as c:
        sign = mg.rect_pts(250, 560, 580, 220)
        mg.fill(c, sign, T, WHITE, 1040, off=(6, 4))
        mg.stroke(c, sign, T, 1041, width=8, closed=True)
        mg.letters(c, "I DON'T KNOW", CX, 700, T, size=86, fname="bangers-400", color=mg.PURPLE, outline=None, seed=1042)
        mg.stroke(c, [(540, 780), (540, 900)], T, 1043, width=10)
        CH.jag(c, 540, 1320, T, s=0.95, arms=(-170, 170), mouth="smile", seed=1044)
        _card(c, T, "HONEST?", mg.PURPLE)


def fut_giant(arr, T):
    mg.swirl(arr, T, colors=[mg.PINK, mg.ORANGE, mg.YELLOW, (255, 240, 220)], scale=1.2)
    s = mg.surf(arr)
    with s as c:
        for k in range(12):
            bw, bh = 70 + (k * 37) % 50, 120 + (k * 53) % 160
            b = mg.rect_pts(k * 92, 1300 - bh, bw, bh)
            mg.fill(c, b, T, (60, 60, 90), 1050 + k, off=(0, 0))
            mg.stroke(c, b, T, 1062 + k, width=5, closed=True)
        CH.jag(c, 540, 1320, T, s=2.2, arms=(-120, 120), mouth="o", eyes="wide", seed=1075)
        _card(c, T, "SUPER?", mg.RED, y=330)
    mg.fisheye(arr, 0.55)


FUTURES = [fut_doctor, fut_mars, fut_friends, fut_memory, fut_science, fut_chores, fut_honest, fut_giant]
_tex = {}


def _thumb(fn, T):
    """A small render of a future, for the tunnel walls (re-drawn on fours so it keeps boiling)."""
    k = (fn.__name__, mg.step(T) // 2 % 3)
    if k not in _tex:
        a = mg.new()
        prev = mg.STYLE
        mg.set_style(["cel", "crayon", "pencil"][hash(fn.__name__) % 3])
        fn(a, T)
        mg.set_style(prev)
        from PIL import Image
        small = np.asarray(Image.fromarray(a[..., :3]).resize((270, 480), Image.BILINEAR))
        _tex[k] = skia.Image.fromarray(np.ascontiguousarray(np.dstack([small, np.full(small.shape[:2], 255, np.uint8)])),
                                       colorType=skia.kRGBA_8888_ColorType)
    return _tex[k]


def tunnel(arr, T, u):
    """Flat-shaded CG tunnel with the futures pinned to its walls; the camera flies forward."""
    mg.swirl(arr, T * 1.4, colors=[mg.PURPLE, mg.PINK, mg.ORANGE, mg.YELLOW], scale=0.8, cx=CX, cy=900)
    zc = u * 14.0
    cam = fx3.Cam((0, 0, -zc), (0, 0, -zc - 5), fov=70, cy=900)
    s = mg.surf(arr)
    with s as c:
        for ring in range(12, -1, -1):
            z = -(int(zc / 2.2) * 2.2 + ring * 2.2)
            pts = [cam.project(p) for p in ((-2.2, -3.2, z), (2.2, -3.2, z), (2.2, 3.2, z), (-2.2, 3.2, z))]
            if min(zz for _, zz in pts) < 0.2:
                continue
            mg.stroke(c, np.array([p for p, _ in pts]), T, 1100 + ring, width=6, closed=True, color=WHITE, double=False)
        panels = []
        for i in range(16):
            z = -(3.0 + i * 1.9)
            side = (-1, 1)[i % 2]
            quad = [(side * 2.2, -1.2, z - 0.8), (side * 2.2, -1.2, z + 0.8), (side * 2.2, 1.6, z + 0.8), (side * 2.2, 1.6, z - 0.8)]
            if side < 0:
                quad = [quad[1], quad[0], quad[3], quad[2]]
            pr = [cam.project(p) for p in quad]
            if min(zz for _, zz in pr) < 0.3:
                continue
            panels.append((np.mean([zz for _, zz in pr]), i, [p for p, _ in pr]))
        for _, i, pp in sorted(panels, key=lambda x: -x[0]):
            img = _thumb(FUTURES[i % len(FUTURES)], T)
            m = skia.Matrix()
            src = [skia.Point(0, 480), skia.Point(270, 480), skia.Point(270, 0), skia.Point(0, 0)]
            dst = [skia.Point(float(p[0]), float(p[1])) for p in pp]
            if not m.setPolyToPoly(src, dst):
                continue
            c.save()
            c.concat(m)
            c.drawImage(img, 0, 0)
            c.restore()
            c.drawPath(mg.path_of(np.array(pp), True), mg.paint(INK, stroke=6))
        k = 0.35 + 1.1 * u
        CH.jag(c, CX, 1000 + 500 * k, T, s=k, arms=(-165, 165), eyes="wide", mouth="open", seed=1120, legs=0.6,
               squash=0.1 * math.sin(T * 20))


def s_finale(arr, t, d, T):
    """Mind Game's climax rush: a CG flight past possible futures, then cuts that get faster into the silence.

    Only light frames and no inversions, so the rush never becomes a strobe."""
    import scenes_1 as A
    import scenes_2 as B
    t_tun = 2.3
    if t < t_tun:
        mg.set_style("cel")
        tunnel(arr, T, t / t_tun)
        return
    tt = t - t_tun
    fr = int(tt * 24)
    # cut length tightens from 6 frames to 3
    edges, f, L = [], 0, 6.0
    while f <= fr:
        edges.append(f)
        f += int(round(L))
        L = max(3.0, L - 0.35)
    blk = len(edges) - 1
    pool = [(fn, "cel") for fn in FUTURES] + [
        (lambda a, T_: A.s_hook(a, 1.0, 2.0, 2.5), "cel"), (lambda a, T_: A.s_levels(a, 1.0, 2.0, C["stamps"][4] + 0.8), "print"),
        (lambda a, T_: B.s_c2(a, 3.0, 6.0, E("c2") - 0.3), "print"), (lambda a, T_: s_m3(a, 1.0, 2.0, E("m3") - 0.2), "cel"),
        (lambda a, T_: B.s_water2(a, 1.0, 2.0, E("g7") - 0.3), "crayon"), (lambda a, T_: A.s_nobody(a, 1.0, 2.0, E("a4") - 0.3), "crayon")]
    nf = len(FUTURES)
    fut = list(np.random.default_rng(5).permutation(nf)) + list(np.random.default_rng(6).permutation(nf))
    old_ = list(nf + np.random.default_rng(7).permutation(len(pool) - nf))
    order = []
    while fut or old_:                                   # two futures, then one callback to an earlier shot
        order += [fut.pop(0) for _ in range(min(2, len(fut)))] + ([old_.pop(0)] if old_ else [])
    fn, st = pool[order[blk % len(order)]]
    mg.set_style(["cel", "crayon", "pencil", "print"][blk % 4] if fn in FUTURES else st)
    fn(arr, T)
    from PIL import Image
    L0 = edges[-1]
    u = (fr - L0 + (tt * 24 - fr)) / 6.0
    z = 1.0 + 0.1 * min(1.0, u) + 0.03 * (blk % 2)
    jx, jy = mg.shake(T, 8, blk)
    w_, h_ = W / z, H / z
    x0 = min(max(0.0, (W - w_) / 2 + jx), W - w_)
    y0 = min(max(0.0, 880 - 880 / z + jy), H - h_)
    arr[..., :3] = np.asarray(Image.fromarray(arr[..., :3]).resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + w_, y0 + h_)))
    if blk % 3 == 2 and fn not in FUTURES:
        mg.fisheye(arr, 0.6)
    s = mg.surf(arr)
    with s as c:
        mg.speed_lines(c, CX, 880, T, n=24, color=WHITE, r0=560, seed=blk)


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
        B.mountains(c, T, lvl, B.LEFT, seed=970, lift=140)
        B.water(c, T, lvl, seed=980, alpha=1.0)
        top = 1450 - (1450 - 470) * 1.0
        CH.human(c, 575, top + 8, T, s=0.34, mouth="smile", seed=990, bob=False)
        CH.jag(c, 668, top + 8, T, s=0.32, eyes="normal", mouth="smile", seed=991, bob=False)


SOURCES = ["Stanford HAI, AI Index 2026 (incl. ClockBench, OSWorld)", "IMO 2025 gold-level results (Google DeepMind, OpenAI)",
           "Nature Comment, Feb 2026 (UC San Diego)", "Hendrycks et al., A Definition of AGI (2025)",
           "Google DeepMind, Levels of AGI (2023)", "Butlin, Long et al., Consciousness in AI (2023)",
           "METR, AI time horizons (2025-26)", "OpenAI, Why Language Models Hallucinate (2025)"]
CREDITS = ["Style homage to Mind Game (2004, dir. Masaaki Yuasa)",
           "Photos: NASA (Blue Marble, Hubble), SpaceX launch (public domain),",
           "clock, espresso and gravel (CC0, via scikit-image)", "Music, voices and eye/mouth photos synthesized"]


def s_end(arr, t, d, T):
    mg.paper(arr, (25, 22, 30), 24)
    s = mg.surf(arr)
    with s as c:
        mg.letters(c, "JAGGED", CX, 640, T, size=200, fname="bangers-400", color=mg.YELLOW, ow=16, seed=995, spacing=6)
        mg.letters(c, "WHAT HAS ACTUALLY HAPPENED IN AI", CX, 740, T, size=48, fname="rubik-800", color=WHITE, outline=None, seed=996, jig=0.5, rot=0.3)
        f = mg.font("rubik-500", 31)
        mg.letters(c, "SOURCES", CX, 850, T, size=38, fname="rubik-800", color=mg.YELLOW, outline=None, seed=997, jig=0.5, rot=0.3)
        for i, ln in enumerate(SOURCES):
            c.drawString(ln, CX - f.measureText(ln) / 2, 905 + i * 44, f, mg.paint((225, 225, 235)))
        f2 = mg.font("rubik-500", 27)
        for i, ln in enumerate(CREDITS):
            c.drawString(ln, CX - f2.measureText(ln) / 2, 1300 + i * 38, f2, mg.paint((170, 170, 185)))


def insert_face(who, bg, text, t0, mouth=None):
    """Returns a shot function: a huge, boiling close-up of a character with a shouted word."""
    def shot(arr, t, dd, T):
        if bg == "burst":
            mg.burst(arr, CX, 800, T, spin=2.2)
        elif bg == "swirl":
            mg.swirl(arr, T * 1.5, scale=0.7)
        else:
            mg.paper(arr, bg, 25)
        s = mg.surf(arr)
        u = T - t0
        sq = 0.22 * math.exp(-7 * u) * math.cos(28 * u)
        with s as c:
            dx, dy = mg.shake(T, 14, 900)
            c.save()
            c.translate(dx, dy)
            mg.speed_lines(c, CX, 820, T, n=40, color=WHITE, r0=520, seed=901)
            if who == "jag":
                CH.jag(c, CX, 2050, T, s=3.3, eyes="spiral" if text == "?!" else "wide", mouth=mouth or ("o" if text != "!!" else "open"),
                       arms=(-150, 150), seed=902, squash=sq)
            else:
                CH.human(c, CX, 2150, T, s=3.0, mouth=mouth or "open", eyes="wide", seed=903, arms=(-160, 160), squash=sq)
            c.restore()
            if text:
                mg.letters(c, text, CX, 450, T, size=200, fname="bangers-400", color=mg.YELLOW, ow=18, seed=904,
                           scale=mg.pop(T, t0, 0.2) or 0.001)
    shot.__name__ = f"insert_{who}"
    return shot


def insert_talk(key):
    """Jag in extreme close-up, saying its line with a photographic mouth (the film's signature device)."""
    words = TL.lines[key]["words"]
    spans = [(a - 0.02, b - 0.04) for w, a, b in words]

    def shot(arr, t, dd, T):
        arr[..., :3] = mg.paper_tex((20, 18, 30), 26)
        s = mg.surf(arr)
        with s as c:
            o = 0.0
            for a, b in spans:
                if a <= T < b:
                    ph = (T - a) / max(0.05, b - a)
                    o = 0.25 + 0.7 * math.sin(ph * math.pi) * (0.7 + 0.3 * ((mg.step(T) % 2)))
            CH.jag(c, CX, 1990, T, s=3.1, eyes="wide", gaze=(0, 0), mouth="frown", talk=o, arms=(-20, 20), seed=906, bob=False)
    shot.__name__ = "insert_talk"
    return shot
