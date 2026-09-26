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

def s_open(arr, t, d, T):
    """Frame one: the title over cars already racing at us. Then: where IS the finish line? Banners pop up everywhere."""
    dusk(arr)
    s = sr.surf(arr)
    kb = ease(ramp(T, W("h1", "nobody") - 0.15, W("h1", "nobody") + 0.35))
    with s as c:
        track.road_front(c, T, speed=1.6, curve=0.25 * math.sin(T * 0.9))
        # finish banners at different distances: nobody agrees which one counts
        for j, (z, dx, lab) in enumerate(((4.2, -900, "?"), (3.4, 850, "?"), (2.6, 0, "?"))):
            kj = pop(T, W("h1", "nobody") - 0.1 + 0.25 * j, 0.25)
            if not kj:
                continue
            sc = 1.0 / z * kj
            ax, ay = CX + dx / z, 760 + 1160 * (1 / z) ** 0.9
            c.save()
            c.translate(ax, ay)
            c.scale(sc * 1.3, sc * 1.3)
            for side in (-1, 1):
                c.drawRect(skia.Rect.MakeXYWH(side * 420 - 18, -560, 36, 560), paint(WHITE))
            sr.checker(c, -440, -640, 880, 100, n=14, m=2)
            f = sr.font("bungee-400", 200)
            c.drawString(lab, -f.measureText(lab) / 2, -300, f, paint(LEMON))
            c.restore()
        for k, (dx, body, num, ph) in enumerate(((-280, PINK, "7", 0.0), (300, LEMON, "3", 1.7), (20, CYAN, "G", 3.1))):
            bob = 30 * math.sin(T * 2.2 + ph)
            z = 1.0 + 0.18 * math.sin(T * 1.3 + ph)
            cast.car_front(c, CX + dx * z + 90 * math.sin(T * 1.8 + ph), 1270 + 120 * (z - 1) + bob * 0.3, 0.74 * z, T, body=body, number=num)
        sr.speed_lines(c, CX, 820, T, n=50, color=WHITE, r0=420, a=0.6, seed=4)
        sr.race_text(c, "THE RACE", CX, 330, 130, fill=LEMON)
        sr.race_text(c, "TO AGI", CX, 440, 110, fill=CYAN)
        if kb > 0.02:
            sr.race_text(c, "WHERE'S THE", CX, 560, 84, fill=WHITE, scale=kb)
            sr.race_text(c, "FINISH LINE?", CX, 660, 96, fill=PINK, scale=kb)
        sr.flare(c, 540, 700, 0.7, T, tint=LEMON)


def s_launch(arr, t, d, T):
    """'The race to AGI is ON!': a jump ramp; at the green light the cars freeze in mid-air (speed ramp), then snap."""
    go = C["go"]
    dusk(arr)
    if T < go:
        u = (T - (go - 1.6)) / 1.6 * 0.4
    elif T < go + 1.2:
        u = 0.4 + (T - go) * 0.04                            # near-freeze
    else:
        u = 0.448 + (T - go - 1.2) * 1.6                     # snap
    frozen = go <= T < go + 1.2
    s = sr.surf(arr)
    punch = 1.0 + 0.14 * max(0.0, 1 - (T - go - 1.2) / 0.3) if T >= go + 1.2 else 1.0
    with s as c:
        c.save()
        c.translate(CX, 900)
        c.scale(punch, punch)
        c.translate(-CX, -900)
        track.road_front(c, T * (0.05 if frozen else 1.0), speed=1.8, curve=0.0)
        # the ramp
        ramp_p = sr.path([(CX - 330, 1180), (CX + 330, 1180), (CX + 260, 1060), (CX - 260, 1060)])
        sr.glossy(c, ramp_p, (250, 250, 255), rim=CYAN, lw=6)
        for k, (dx, body, num) in enumerate(((-330, PINK, "7"), (330, LEMON, "3"), (0, CYAN, "G"))):
            air = max(0.0, u - 0.25) * 2.6
            h = 520 * math.sin(min(math.pi, air * 1.3)) if air > 0 else 0
            z = 1.0 + max(0.0, u - 0.2) * (3.0 if k == 2 else 2.2)
            x = CX + dx * z
            y = 1320 + 200 * (z - 1) - h
            if y - 260 * 0.66 * z > 2600:
                continue
            cast.car_front(c, x, y, 0.66 * z, T, body=body, number=num)
            if frozen:
                for j in range(5):
                    c.drawCircle(x + (j - 2) * 60, y + 30 + 25 * (j % 2), 22, paint(WHITE, 0.6, blur=6))
        c.restore()
        c.drawRect(skia.Rect.MakeXYWH(140, 470, 800, 150), paint(INK))
        for i in range(3):
            green = T >= go
            colr = sr.LIME if green else RED
            c.drawCircle(290 + i * 250, 545, 55, paint(colr))
            c.drawCircle(290 + i * 250, 545, 120, paint(colr, 0.35, blur=40))
            sr.glint(c, 270 + i * 250, 525, 40, T)
    if frozen:
        sr.freeze(arr, min(1.0, (T - go) / 0.15))
    with s as c:
        if frozen:
            sr.focus_lines(c, CX, 1000, T, a=0.3)
            sr.race_text(c, "GO!", CX, 900, 240, fill=sr.LIME, scale=1 + 0.05 * (T - go))
        elif T >= go + 1.2:
            sr.speed_lines(c, CX, 900, T, n=90, color=WHITE, r0=240, seed=3)
    sr.snap_flash(arr, T - go - 1.2)


def s_race(arr, t, d, T):
    """Side-on race through the candy stadium, the driver's giant face in the foreground; then the question slams in."""
    track.stadium(arr, T, speed=1.2)
    s = sr.surf(arr)
    kq = pop(T, W("h2", "first") - 0.1, 0.3)
    with s as c:
        track.road_side(c, T, 1180, 1330, speed=1.2)
    track.near_wall(arr, T, 1330, speed=1.2)
    with s as c:
        sr.hlines(c, T, 700, 1180, n=26, a=0.55, seed=2)
        rng_bob = lambda k: 4 * math.sin(T * 30 + k)
        cast.car_side(c, 500 + 60 * math.sin(T * 1.3), 1250 + rng_bob(0), 0.62, T, body=PINK, number="7", speed=2)
        cast.car_side(c, 860 - 90 * math.sin(T * 1.1), 1318 + rng_bob(1), 0.8, T, body=LEMON, number="3", speed=2)
        cast.car_side(c, 640 + 140 * ease(t / d), 1420 + rng_bob(2), 1.0, T, speed=2, flames=True, **AI_CAR)
        # layered depth: the Generalist's driver, huge in the foreground, the race sharp behind
        cast.face(c, "ai", 250, 640, 3.3, T, talk=0.0, look=(0.9, 0.1), facing=1)
        if kq > 0:
            c.drawCircle(770, 700, 220 * kq, paint(shader=sr.rad((770, 640), 220 * kq, [(255, 255, 255), LEMON, TANG])))
            c.drawCircle(770, 700, 220 * kq, paint(INK, stroke=10))
            sr.race_text(c, "?", 780, 790, 260, fill=PINK, scale=kq, skew=-0.1)
            sr.race_text(c, "STEP 1?", 770, 1020, 90, fill=WHITE, scale=kq)


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
        cast.face(c, "host", 190, 1030, 3.3, T, talk=talk(T), look=(0.8, -0.2), facing=1)
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
            I.chess_king(c, x, 1030, 2.1) if i % 2 else I.chess_knight(c, x, 1030, 2.1)
    sr.streak(arr, 22, 700, 1150)
    with s as c:
        for i in range(12):
            for j in range(3):
                x = i * 100 - (T * 1800) % 200
                c.drawRect(skia.Rect.MakeXYWH(x, 1180 + j * 50, 100, 50), paint(WHITE if (i + j) % 2 else INK))
        cast.car_side(c, 480 + 200 * ease(ramp(T, S("d2"), W("d2", "Done"))), 1330, 0.95, T, speed=2, flames=True, **AI_CAR)
    track.near_wall(arr, T, 1340, speed=1.0)
    with s as c:
        sr.race_text(c, "CHESS", CX, 400, 130, fill=WHITE)
        sr.plain(c, "Finish line: beat the world champion", CX, 480, 42, color=WHITE, fname="rubik-800")
        k = pop(T, W("d2", "Nineteen") - 0.05, 0.25)
        if k:
            sr.race_text(c, "1997", 300, 900, 150, fill=LEMON, scale=k)
        sr.badge(c, "DONE!", 780, 700, T, W("d2", "Done"), color=sr.LIME, size=80, rot=-7)
        if T > W("d2", "Done"):
            sr.flare(c, 780, 660, 1.0, T, tint=LEMON)
        sr.lower_third(c, T, S("d2") + 0.2, E("d2") + 0.2, "DEEP BLUE BEATS KASPAROV", "IBM, May 1997", color=sr.BLUE, y=600)


def s_imagenet(arr, t, d, T):
    """2015: beat humans on a standard picture test. Split screen: the pictures fly by, the scoreboard ticks."""
    sr.sky(arr, [(0, (255, 90, 170)), (1, (255, 200, 90))])
    s = sr.surf(arr)
    with s as c:
        kinds = ["cat", "dog", "car", "bird", "flower"]
        for i in range(5):
            x = (i * 268 - T * 700) % (5 * 268) - 130
            I.tile(c, x, 700, 1.0, kinds[i % 5], T)
    sr.streak(arr, 12, 560, 880)
    with s as c:
        for i in range(5):
            x = (i * 268 - T * 700) % (5 * 268) - 130
            sr.plain(c, kinds[i % 5].upper(), x, 860, 36, color=INK, fname="bungee-400")
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

GAUGES = ["REASONING", "MEMORY", "SPATIAL", "LANGUAGE", "LEARNING SPD", "PLANNING", "SOCIAL", "PERCEPTION", "TRANSFER",
          "NEW PROBLEMS", "AUTONOMY"]
LEVELS = [0.82, 0.3, 0.55, 0.9, 0.35, 0.6, 0.65, 0.72, 0.4, 0.45, 0.2]


def s_dash(arr, t, d, T):
    """Cockpit view: the road streaks past the windscreen; eleven gauges swing up one by one, each to its own level."""
    dusk(arr)
    s = sr.surf(arr)
    with s as c:
        track.road_front(c, T, speed=1.6, curve=0.2 * math.sin(T * 0.7), y_bottom=1150)
    sr.streak(arr, 30, 300, 700)
    with s as c:
        # rear-view mirror: the driver's eyes on the road
        m = skia.Path()
        m.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(290, 250, 500, 190), 60, 60))
        c.save()
        c.clipPath(m, doAntiAlias=True)
        c.drawRect(skia.Rect.MakeXYWH(290, 250, 500, 190), paint(shader=sr.lin((0, 250), (0, 440), [(60, 30, 120), (20, 10, 50)])))
        cast.face(c, "ai", 540, 420, 1.9, T, talk=0.0, look=(0, -0.2))
        c.restore()
        c.drawPath(m, paint(shader=sr.lin((0, 250), (0, 440), [WHITE, (140, 150, 190), WHITE]), stroke=14))
        c.drawRect(skia.Rect.MakeXYWH(530, 220, 20, 34), paint(INK))
        shake = 3 * math.sin(T * 40)
        c.save()
        c.translate(0, shake)
        dash = sr.path([(0, 760), (sr.W, 760), (sr.W, H), (0, H)])
        c.drawPath(dash, paint(shader=sr.lin((0, 760), (0, H), [(60, 40, 110), (20, 10, 40)])))
        c.drawRect(skia.Rect.MakeXYWH(0, 752, sr.W, 16), paint(shader=sr.lin((0, 752), (0, 768), [WHITE, (150, 160, 190)])))
        sr.race_text(c, "THE AGI DASHBOARD", CX, 700, 70, fill=LEMON)
        pos = [(128 + i * 244, 880) for i in range(4)] + [(128 + i * 244, 1080) for i in range(4)] + [(250 + i * 244, 1280) for i in range(3)]
        for i, (lab, (gx, gy)) in enumerate(zip(GAUGES, pos)):
            t0 = C["gauges"][i]
            lit = ease(ramp(T, t0 - 0.05, t0 + 0.12))
            sweep = ramp(T, t0 - 0.05, t0 + 0.35)
            over = math.sin(sweep * math.pi) * 0.12 if sweep < 1 else 0
            val = 0.05 + (LEVELS[i] - 0.05) * ease(sweep) + over + 0.02 * math.sin(T * 11 + i) * lit
            colr = CANDY[i % len(CANDY)]
            if lit > 0:
                c.drawCircle(gx, gy, 108, paint(colr, 0.4 * lit, blur=28))
            I.gauge(c, gx, gy, 86, val, "", lit, T, color=colr)
            f = sr.font("bungee-400", 21)
            w = f.measureText(lab)
            c.drawString(lab, gx - w / 2, gy + 52, f, paint(WHITE if lit > 0.5 else (170, 165, 200)))
        c.restore()


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
        abil = ["KNOWLEDGE", "READING", "MATH", "REASONING", "WORKING MEM", "LONG-TERM MEM", "RECALL", "VISION", "HEARING", "SPEED"]
        # flow the chips into centred rows so long labels never collide
        f = sr.font("bungee-400", 22)
        rows, cur = [], []
        for j, lab in enumerate(abil):
            w = f.measureText(lab) + 20
            if cur and sum(ww for _, _, ww in cur) + 12 * len(cur) + w > 820:
                rows.append(cur)
                cur = []
            cur.append((j, lab, w))
        rows.append(cur)
        place = []
        for r, row in enumerate(rows):
            xx = CX - (sum(ww for _, _, ww in row) + 12 * (len(row) - 1)) / 2
            for j, lab, w in row:
                place.append((j, lab, w, xx + w / 2, 650 + r * 52))
                xx += w + 12
        for j, lab, w, cx_, cy_ in place:
            kj = pop(T, S("d7") + 0.12 * j, 0.2)
            if not kj:
                continue
            c.save()
            c.translate(cx_, cy_)
            c.scale(kj, kj)
            c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -24, w, 38), 10, 10, paint(CANDY[j % len(CANDY)]))
            c.drawString(lab, -w / 2 + 10, 4, f, paint(WHITE))
            c.restore()
        # the scale: 100% = a well-educated adult; the real scores fill in as they're spoken
        x0, x1 = 170, 910
        for j, (name, val, word, colr) in enumerate((("GPT-4", 0.27, "twenty-seven", sr.BLUE), ("GPT-5", 0.57, "fifty-seven", PINK))):
            y = 820 + j * 120
            sr.plain(c, name, x0, y - 12, 34, color=INK, fname="bungee-400", align="left")
            c.drawRoundRect(skia.Rect.MakeXYWH(x0, y, x1 - x0, 56), 28, 28, paint((230, 225, 245)))
            kk = ease(ramp(T, W("d7", word) - 0.6, W("d7", word) + 0.2))
            if kk > 0.01:
                bar = skia.Path()
                bar.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y, (x1 - x0) * val * kk, 56), 28, 28))
                sr.glossy(c, bar, colr, rim=sr.lighter(colr, 0.7), lw=0)
                sr.plain(c, f"{int(round(100 * val * kk))}%", x0 + (x1 - x0) * val * kk + 12, y + 44, 38, color=colr, fname="bungee-400", align="left")
            c.drawRoundRect(skia.Rect.MakeXYWH(x0, y, x1 - x0, 56), 28, 28, paint(INK, stroke=5))
        c.drawLine(x1, 770, x1, 1010, paint(RED, stroke=6))
        sr.plain(c, "100% = a well-educated adult", x1, 1070, 34, color=RED, fname="rubik-800", align="right")
        kk = pop(T, W("d7", "well-educated") - 0.1, 0.25)
        if kk:
            cast.face(c, "host", 230, 1100, 0.45 * kk, T, talk=0, look=(0.6, 0), expr="smile")


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
        kp = ease(ramp(T, W("d8", "Human") - 0.1, W("d8", "Human") + 0.3))
        if kp < 0.5:
            sr.badge(c, "NO INSTRUCTIONS", 300, 1180, T, W("d8", "instructions") - 0.1, color=RED, size=44, rot=-5)
            sr.badge(c, "NO STATED GOALS", 780, 1180, T, W("d8", "stated") - 0.1, color=RED, size=44, rot=6)
        if T > W("d8", "Human") - 0.1:
            k = kp
            ov = skia.Path()
            ov.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(60, 485, sr.W - 120, 785), 30, 30))
            c.drawPath(ov, paint((24, 16, 60), k))
            c.drawPath(ov, paint(CYAN, k, stroke=6))
            for side, (lab, val, colr, t0) in enumerate((("HUMAN TESTERS", 1.0, LIME, W("d8", "Human")), ("TOP AI*", 0.006, RED, W("d8", "top")))):
                kk = ease(ramp(T, t0, t0 + 0.6))
                x = 300 + side * 480
                sr.plain(c, lab, x, 595, 56 if len(lab) < 9 else 42, color=WHITE, fname="bungee-400")
                c.drawRoundRect(skia.Rect.MakeXYWH(x - 70, 670, 140, 470), 20, 20, paint((60, 50, 90)))
                hh = 470 * val * kk
                if hh > 2:
                    bar = skia.Path()
                    bar.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 70, 1140 - hh, 140, hh), 20, 20))
                    sr.glossy(c, bar, colr, lw=4)
                if kk > 0.5:
                    sr.plain(c, "SOLVED ALL" if side == 0 else "UNDER 1%", x, 1205, 50, color=colr, fname="bungee-400")
            if T > W("d8", "top") + 0.3:
                sr.plain(c, "* frontier models, at launch", 780, 1248, 30, color=WHITE, fname="rubik-700")
