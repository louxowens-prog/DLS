"""The hook, answer one (define the finish line), and the measurement frameworks."""
import math

import numpy as np
import skia

import cast
import icons as I
import sr
import track
from common import E, S, W, talk
from cues import C
from sr import CANDY, CX, CYAN, H, INK, LEMON, LIME, PINK, RED, TANG, VIOLET, WHITE, ease, paint, pop, ramp

AI_CAR = dict(body=CYAN, stripe=WHITE, number="G")


def dusk(arr, sun=True):
    sr.sky(arr, [(0, (70, 20, 150)), (0.38, (255, 80, 170)), (0.52, (255, 190, 120)), (1, (255, 140, 90))], sun=(540, 700, 110) if sun else None)


# ------------------------------------------------------------------ hook

def s_grid(arr, t, d, T):
    """The starting grid: lights, revving cars, the flag... then a slow-motion launch that snaps to full speed."""
    go = C["go"]
    dusk(arr)
    # speed ramp: crawl for 0.6 s after the green light, then snap
    if T < go:
        u, spd = 0.0, 0.0
    elif T < go + 0.6:
        u, spd = (T - go) * 0.18, 0.1
    else:
        u, spd = 0.108 + (T - go - 0.6) * 2.4, 3.0
    s = sr.surf(arr)
    with s as c:
        track.road_front(c, u * 3, speed=1.0, curve=0.0)
        shake = 3 * math.sin(T * 70) if T < go else 0
        for k, (dx, body, num) in enumerate(((-330, PINK, "7"), (330, LEMON, "3"), (0, CYAN, "G"))):
            z = 1.0 + (u * 6 if k == 2 else u * 4.5)
            sc = 0.62 * z
            y = 1320 + 260 * (z - 1)
            x = CX + dx * z
            if y - 260 * sc > 2600:
                continue
            cast.car_front(c, x + shake * (k - 1), y, sc, T, body=body, number=num)
        # the light gantry
        c.drawRect(skia.Rect.MakeXYWH(140, 470, 800, 150), paint(INK))
        for i in range(3):
            on = T >= go - 2.4 + 0.8 * i
            green = T >= go
            colr = sr.LIME if green else (RED if on else (70, 30, 40))
            c.drawCircle(290 + i * 250, 545, 55, paint(colr))
            if on or green:
                c.drawCircle(290 + i * 250, 545, 120, paint(colr, 0.35, blur=40))
                sr.glint(c, 270 + i * 250, 525, 40, T)
        k = pop(T, 0.15, 0.3)
        if k > 0:
            sr.race_text(c, "THE RACE", CX, 330, 130, fill=LEMON, scale=k)
            sr.race_text(c, "TO AGI", CX, 440, 110, fill=CYAN, scale=k)
        if T >= go + 0.6:
            sr.speed_lines(c, CX, 900, T, n=70, color=WHITE, r0=300, seed=3)
        if go <= T < go + 0.6:
            sr.race_text(c, "GO!", CX, 820, 260, fill=sr.LIME, scale=1 + 0.3 * (T - go))


def s_race(arr, t, d, T):
    """Side-on race through the candy stadium; the cars jockey; then the question slams in."""
    track.stadium(arr, T, speed=1.2)
    s = sr.surf(arr)
    kq = pop(T, W("h1", "first") - 0.1, 0.3)
    with s as c:
        track.road_side(c, T, 1180, 1330, speed=1.2)
        sr.hlines(c, T, 700, 1180, n=26, a=0.55, seed=2)
        rng_bob = lambda k: 4 * math.sin(T * 30 + k)
        cast.car_side(c, 300 + 60 * math.sin(T * 1.3), 1250 + rng_bob(0), 0.62, T, body=PINK, number="7", speed=2)
        cast.car_side(c, 760 - 90 * math.sin(T * 1.1), 1318 + rng_bob(1), 0.8, T, body=LEMON, number="3", speed=2)
        cast.car_side(c, 520 + 140 * ease(t / d), 1420 + rng_bob(2), 1.0, T, speed=2, flames=True, **AI_CAR)
        sr.lower_third(c, T, S("h1") + 0.2, W("h1", "first") - 0.2, "LAP 1", "The race to build AGI", color=VIOLET, y=560)
        if kq > 0:
            c.drawCircle(CX, 760, 260 * kq, paint(shader=sr.rad((CX, 700), 260 * kq, [(255, 255, 255), LEMON, TANG])))
            c.drawCircle(CX, 760, 260 * kq, paint(INK, stroke=10))
            sr.race_text(c, "?", CX + 10, 860, 300, fill=PINK, scale=kq, skew=-0.1)
            sr.race_text(c, "STEP 1 = ?", CX, 1100, 90, fill=WHITE, scale=kq)


def s_two(arr, t, d, T):
    """Split-screen slam: two answers."""
    k = ease(t / 0.3)
    arr[:, :, :3] = 0
    left = sr.new()
    sr.sky(left, [(0, (255, 60, 170)), (1, (255, 170, 60))])
    right = sr.new()
    sr.sky(right, [(0, (0, 190, 255)), (1, (110, 60, 255))])
    # diagonal split: left panel slides from the left, right from the right
    xx = np.arange(sr.W)[None, :]
    yy = np.arange(H)[:, None]
    edge = CX + (yy - 900) * 0.18
    m = (xx < edge - (1 - k) * 700)
    arr[..., :3] = np.where(m[..., None], left[..., :3], right[..., :3])
    s = sr.surf(arr)
    with s as c:
        c.drawPath(sr.path([(CX - 12 + (0 - 900) * 0.18, 0), (CX + 12 + (0 - 900) * 0.18, 0), (CX + 12 + (H - 900) * 0.18, H),
                            (CX - 12 + (H - 900) * 0.18, H)]), paint(shader=sr.lin((0, 0), (0, H), [WHITE, (170, 180, 210), WHITE])))
        a1 = pop(T, S("h2") + 0.05, 0.25)
        a2 = pop(T, S("h2") + 0.3, 0.25)
        if a1:
            sr.checker(c, 90, 600, 330, 200, n=6, m=4)
            c.drawRect(skia.Rect.MakeXYWH(80, 600, 12, 460), paint(INK))
            sr.race_text(c, "1", 250, 460, 170, fill=LEMON, scale=a1)
            sr.race_text(c, "SCIENCE", 260, 1000, 78, fill=WHITE, scale=a1)
            sr.plain(c, "define it", 260, 1070, 48, color=INK, fname="rubik-800")
        if a2:
            I.engine_block(c, 790, 770, 0.8, T)
            sr.race_text(c, "2", 800, 460, 170, fill=LEMON, scale=a2)
            sr.race_text(c, "TECH", 810, 1000, 78, fill=WHITE, scale=a2)
            sr.plain(c, "build it", 810, 1070, 48, color=WHITE, fname="rubik-800")


# ------------------------------------------------------------------ answer one: the finish line

def s_finish(arr, t, d, T):
    """The AI chases a finish line that keeps rolling away. The anchor's face towers in the foreground."""
    dusk(arr)
    s = sr.surf(arr)
    away = ease(ramp(T, W("d1", "Without") - 0.2, E("d1")))
    with s as c:
        track.road_front(c, T, speed=1.3, curve=0.15 * math.sin(T * 0.8))
        # the finish arch, on wheels, rolling away down the road
        z = 2.2 + 5.0 * away + 0.4 * math.sin(T * 3)
        sc = 1.0 / z
        ax, ay = CX + 60 * sc, 760 + 1160 * (1 / z) ** 0.9
        c.save()
        c.translate(ax, ay)
        c.scale(sc * 1.4, sc * 1.4)
        for side in (-1, 1):
            c.drawRect(skia.Rect.MakeXYWH(side * 520 - 22, -620, 44, 620), paint(WHITE))
            c.drawCircle(side * 520, 0, 40, paint(INK))
        sr.checker(c, -540, -700, 1080, 110, n=16, m=2)
        f = sr.font("bungee-400", 90)
        c.drawString("FINISH?", -f.measureText("FINISH?") / 2, -730, f, paint(WHITE))
        c.restore()
        cast.car_front(c, CX + 120 * math.sin(T * 1.6), 1330, 0.9, T, **{k: v for k, v in AI_CAR.items() if k != "stripe"})
        # layered depth: the anchor, huge, in the foreground
        cast.face(c, "host", 60, 1060, 3.0, T, talk=talk(T), look=(0.8, -0.2), facing=1)
        sr.lower_third(c, T, S("d1") + 0.1, W("d1", "Without") - 0.1, "ANSWER 1 · SCIENCE", "Define what counts", color=PINK, y=560)
        sr.badge(c, "GOALPOSTS MOVE!", 700, 560, T, W("d1", "move"), color=RED, size=56, rot=5)


def s_chess(arr, t, d, T):
    """1997: a finish line you could see. Giant chess pieces line a checkerboard track."""
    sr.sky(arr, [(0, (20, 30, 120)), (0.55, (80, 170, 255)), (1, (230, 240, 255))])
    s = sr.surf(arr)
    with s as c:
        off = (T * 900) % 300
        for i in range(-1, 6):
            x = i * 300 - off
            I.chess_king(c, x, 1040, 1.6) if i % 2 else I.chess_knight(c, x, 1040, 1.6)
    sr.streak(arr, 60, 700, 1150)
    with s as c:
        for i in range(12):
            for j in range(3):
                x = i * 100 - (T * 1800) % 200
                c.drawRect(skia.Rect.MakeXYWH(x, 1180 + j * 50, 100, 50), paint(WHITE if (i + j) % 2 else INK))
        cast.car_side(c, 480 + 200 * ease(ramp(T, S("d2"), W("d2", "Done"))), 1330, 0.95, T, speed=2, flames=True, **AI_CAR)
        sr.race_text(c, "CHESS", CX, 400, 130, fill=WHITE)
        sr.plain(c, "Finish line: beat the world champion", CX, 480, 42, color=WHITE, fname="rubik-800")
        k = pop(T, W("d2", "Nineteen") - 0.05, 0.25)
        if k:
            sr.race_text(c, "1997", CX, 700, 170, fill=LEMON, scale=k)
        sr.badge(c, "DONE!", 760, 900, T, W("d2", "Done"), color=sr.LIME, size=80, rot=-7)
        if T > W("d2", "Done"):
            sr.flare(c, 760, 860, 1.0, T, tint=LEMON)
        sr.lower_third(c, T, S("d2") + 0.2, E("d2") + 0.2, "DEEP BLUE BEATS KASPAROV", "IBM, May 1997", color=sr.BLUE, y=1170)


def s_imagenet(arr, t, d, T):
    """2015: beat humans on a standard picture test. Split screen: the pictures fly by, the scoreboard ticks."""
    sr.sky(arr, [(0, (255, 90, 170)), (1, (255, 200, 90))])
    s = sr.surf(arr)
    with s as c:
        kinds = ["cat", "dog", "car", "bird", "flower"]
        for i in range(8):
            x = (i * 260 - T * 700) % (sr.W + 260) - 130
            I.tile(c, x, 700, 1.0, kinds[i % 5], T)
            sr.plain(c, kinds[i % 5].upper(), x, 860, 36, color=INK, fname="bungee-400")
    sr.streak(arr, 16, 560, 880)
    with s as c:
        c.drawRect(skia.Rect.MakeXYWH(0, 930, sr.W, 12), paint(WHITE))
        sr.race_text(c, "IMAGE RECOGNITION", CX, 440, 84, fill=WHITE)
        board = skia.Path()
        board.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(90, 980, 900, 260), 24, 24))
        sr.glossy(c, board, (40, 20, 90), rim=CYAN, lw=6)
        sr.plain(c, "ERROR RATE (IMAGENET)", CX, 1040, 38, color=CYAN, fname="bungee-400")
        k = ease(ramp(T, S("d3") + 0.6, W("d3", "Twenty")))
        sr.plain(c, "HUMANS  5.1%", 330, 1150, 50, color=WHITE, fname="bungee-400")
        sr.plain(c, f"AI  {26 - (26 - 3.6) * k:.1f}%", 760, 1150, 50, color=LEMON, fname="bungee-400")
        sr.badge(c, "2015 · DONE!", CX, 1300 - 30, T, W("d3", "Done"), color=sr.LIME, size=70, rot=4)


def s_fuzzy(arr, t, d, T):
    """'Be intelligent': the finish banner melts into a blur."""
    dusk(arr, sun=False)
    s = sr.surf(arr)
    with s as c:
        track.road_front(c, T * 0.3, speed=0.4)
        sr.checker(c, 140, 520, 800, 120, n=12, m=2)
        sr.race_text(c, "BE INTELLIGENT", CX, 760, 100, fill=WHITE)
    k = ease(ramp(T, S("d4") + 0.4, E("d4")))
    if k > 0:
        from scipy import ndimage
        band = arr[420:900, :, :3].astype(np.float32)
        wob = np.sin(np.arange(band.shape[0])[:, None] / 18 + T * 8) * 30 * k
        idx = (np.arange(band.shape[1])[None, :] + wob).astype(int) % band.shape[1]
        band = band[np.arange(band.shape[0])[:, None], idx]
        band = ndimage.gaussian_filter(band, (8 * k, 8 * k, 0))
        arr[420:900, :, :3] = band.astype(np.uint8)
    with s as c:
        cast.car_front(c, CX, 1330, 0.95, T, **{k2: v for k2, v in AI_CAR.items() if k2 != "stripe"})
        sr.badge(c, "FUZZY!", 780, 1000, T, W("d4", "fuzzy") - 0.1, color=VIOLET, size=80, rot=8)


# ------------------------------------------------------------------ the dashboard

GAUGES = ["REASONING", "MEMORY", "SPATIAL", "LANGUAGE", "LEARNING\nSPEED", "PLANNING", "SOCIAL", "PERCEPTION", "TRANSFER",
          "NEW\nPROBLEMS", "LONG-TERM\nAUTONOMY"]


def s_dash(arr, t, d, T):
    """Cockpit view: the road streaks past the windscreen; eleven gauges light up one by one."""
    dusk(arr)
    s = sr.surf(arr)
    with s as c:
        track.road_front(c, T, speed=1.6, curve=0.2 * math.sin(T * 0.7), y_bottom=1150)
    sr.streak(arr, 30, 300, 700)
    with s as c:
        dash = sr.path([(0, 760), (sr.W, 760), (sr.W, H), (0, H)])
        c.drawPath(dash, paint(shader=sr.lin((0, 760), (0, H), [(60, 40, 110), (20, 10, 40)])))
        c.drawRect(skia.Rect.MakeXYWH(0, 752, sr.W, 16), paint(shader=sr.lin((0, 752), (0, 768), [WHITE, (150, 160, 190)])))
        sr.race_text(c, "THE AGI DASHBOARD", CX, 700, 70, fill=LEMON)
        pos = [(150 + i * 260, 900) for i in range(4)] + [(150 + i * 260, 1110) for i in range(4)] + [(280 + i * 260, 1300) for i in range(3)]
        for i, (lab, (gx, gy)) in enumerate(zip(GAUGES, pos)):
            t0 = C["gauges"][i]
            lit = ease(ramp(T, t0 - 0.05, t0 + 0.15))
            val = 0.15 + 0.7 * lit + 0.05 * math.sin(T * 9 + i) * lit
            I.gauge(c, gx, gy, 78, val, lab, lit, T, color=CANDY[i % len(CANDY)])
        sr.lower_third(c, T, S("d5") + 0.05, C["gauges"][0] - 0.05, "A REAL TEST", "needs a whole dashboard", color=TANG, y=560)


# ------------------------------------------------------------------ frameworks and ARC

def s_frameworks(arr, t, d, T):
    """Broadcast studio card: one framework scores AI against a well-educated adult."""
    sr.sky(arr, [(0, (30, 20, 90)), (0.5, (90, 40, 170)), (1, (255, 90, 170))])
    s = sr.surf(arr)
    with s as c:
        for k in range(14):
            x = (k * 90 + T * 200) % 1260 - 90
            c.drawRect(skia.Rect.MakeXYWH(x, 0, 30, H), paint(CANDY[k % len(CANDY)], 0.12))
        card = skia.Path()
        card.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(80, 420, 920, 760), 36, 36))
        sr.glossy(c, card, (250, 245, 255), top=WHITE, rim=CYAN, spec=0.4, lw=7)
        sr.plain(c, "A DEFINITION OF AGI", CX, 520, 56, color=VIOLET, fname="bungee-400")
        sr.plain(c, "Hendrycks et al., 2025", CX, 580, 36, color=INK, fname="rubik-700")
        # the meter: 0% -> 100% = a well-educated adult
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(150, 700, 780, 90), 45, 45), paint((230, 225, 245)))
        k = ease(ramp(T, W("d7", "scores") - 0.2, W("d7", "adult") + 0.2))
        if k > 0.01:
            fill = skia.Path()
            fill.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(150, 700, 780 * k, 90), 45, 45))
            sr.glossy(c, fill, PINK, rim=LEMON, lw=0)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(150, 700, 780, 90), 45, 45), paint(INK, stroke=6))
        sr.plain(c, "0%", 170, 850, 40, color=INK, fname="bungee-400", align="left")
        sr.plain(c, "100%", 930, 850, 40, color=INK, fname="bungee-400", align="right")
        kk = pop(T, W("d7", "well-educated") - 0.1, 0.25)
        if kk:
            cast.face(c, "host", 800, 1010, 0.9 * kk, T, talk=0, look=(-0.6, 0), facing=-1, expr="smile")
            sr.plain(c, "= a well-educated adult", 400, 1030, 44, color=INK, fname="rubik-800")
            sr.plain(c, "across 10 kinds of ability", 400, 1090, 36, color=(80, 70, 110), fname="rubik-700")


def s_arc(arr, t, d, T):
    """ARC-AGI-3: games with no instructions and no goals. People solve them all; top AI, under one percent."""
    sr.sky(arr, [(0, (10, 10, 40)), (1, (40, 20, 100))])
    s = sr.surf(arr)
    rng = np.random.default_rng(4)
    grid = rng.integers(0, 7, (10, 10))
    with s as c:
        sr.race_text(c, "ARC-AGI-3", CX, 380, 110, fill=CYAN)
        sr.plain(c, "Launched March 2026 · ARC Prize Foundation", CX, 450, 34, color=WHITE, fname="rubik-700")
        cs, gx, gy = 58, CX - 5 * 58, 520
        ax = int((T * 3) % 10)
        ay = int((T * 1.7) % 10)
        for i in range(10):
            for j in range(10):
                v = grid[j, i]
                colr = [(30, 30, 60), PINK, LEMON, CYAN, LIME, TANG, VIOLET][v]
                c.drawRoundRect(skia.Rect.MakeXYWH(gx + i * cs + 3, gy + j * cs + 3, cs - 6, cs - 6), 8, 8, paint(colr))
        c.drawRoundRect(skia.Rect.MakeXYWH(gx + ax * cs, gy + ay * cs, cs, cs), 10, 10, paint(WHITE, stroke=8))
        c.drawRoundRect(skia.Rect.MakeXYWH(gx + ax * cs, gy + ay * cs, cs, cs), 10, 10, paint(WHITE, 0.4, blur=10))
        sr.badge(c, "NO INSTRUCTIONS", 300, 1180, T, W("d8", "instructions") - 0.1, color=RED, size=44, rot=-5)
        sr.badge(c, "NO GOALS", 800, 1180, T, W("d8", "goals") - 0.1, color=RED, size=44, rot=6)
        if T > W("d8", "People") - 0.1:
            k = ease(ramp(T, W("d8", "People") - 0.1, W("d8", "People") + 0.4))
            ov = sr.path([(0, 480), (sr.W, 480), (sr.W, 1300), (0, 1300)])
            c.drawPath(ov, paint(INK, 0.75 * k))
            for side, (lab, val, colr, t0) in enumerate((("PEOPLE", 1.0, LIME, W("d8", "People")), ("TOP AI*", 0.006, RED, W("d8", "top")))):
                kk = ease(ramp(T, t0, t0 + 0.6))
                x = 300 + side * 480
                sr.plain(c, lab, x, 620, 56, color=WHITE, fname="bungee-400")
                c.drawRoundRect(skia.Rect.MakeXYWH(x - 70, 700, 140, 480), 20, 20, paint((60, 50, 90)))
                hh = 480 * val * kk
                if hh > 2:
                    bar = skia.Path()
                    bar.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 70, 1180 - hh, 140, hh), 20, 20))
                    sr.glossy(c, bar, colr, lw=4)
                if kk > 0.5:
                    sr.plain(c, "SOLVE ALL" if side == 0 else "UNDER 1%", x, 1250, 50, color=colr, fname="bungee-400")
            if T > W("d8", "top") + 0.3:
                sr.plain(c, "* frontier models, at launch", 780, 1295, 30, color=WHITE, fname="rubik-700")
