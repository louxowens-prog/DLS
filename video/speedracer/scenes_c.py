"""Under the hood (the agent loop), generalization head to head, the moving finish line, and the finish."""
import math

import numpy as np
import skia

import cast
import icons as I
import sr
import track
from common import E, S, W, talk
from cues import C
from scenes_a import AI_CAR, dusk
from scenes_b import FRONT
from sr import CANDY, CX, CYAN, H, INK, LEMON, LIME, PINK, RED, TANG, VIOLET, WHITE, ease, paint, pop, ramp

MEM_CAR = dict(body=VIOLET, stripe=LIME, number="99", driver="memorizer", books=True)


def s_hood(arr, t, d, T):
    """The hood pops open: it's not a chat window in there, it's a loop."""
    sr.sunburst(arr, T, cols=[(80, 40, 170), (40, 20, 100), (130, 60, 220)], cy=1250, rays=24, spin=0.35)
    s = sr.surf(arr)
    k = ease(ramp(T, S("u1") + 0.3, S("u1") + 0.9))
    kl = ease(ramp(T, W("u1", "loop") - 0.3, W("u1", "loop") + 0.2))
    with s as c:
        cast.car_side(c, CX, 1330, 1.6, T, speed=0.1, **AI_CAR)
        # hood lid swinging up
        c.save()
        c.translate(CX + 260, 1150)
        c.rotate(70 * k)                                                  # swings UP, clear of the captions
        hood = skia.Path()
        hood.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-360, -30, 380, 40), 16, 16))
        sr.glossy(c, hood, CYAN, lw=5)
        c.restore()
        # a chat bubble, crossed out
        if k > 0.2:
            bub = skia.Path()
            bub.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(150, 560, 360, 200), 40, 40))
            sr.glossy(c, bub, WHITE, top=WHITE, rim=PINK, spec=0.2, lw=5)
            sr.plain(c, "just a chatbot?", 330, 680, 38, color=INK, fname="rubik-800")
            if kl > 0:
                c.drawLine(160, 570, 500, 750, paint(RED, stroke=16))
        if kl > 0:
            cx0, cy0, r = 740, 700, 170 * kl
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeXYWH(cx0 - r, cy0 - r, 2 * r, 2 * r), 200, 300)
            c.drawPath(arc, paint(LIME, stroke=34))
            a = math.radians(140)
            c.drawPath(sr.path([(cx0 + r * math.cos(a) - 40, cy0 + r * math.sin(a) - 10), (cx0 + r * math.cos(a) + 30, cy0 + r * math.sin(a) - 50),
                                (cx0 + r * math.cos(a) + 20, cy0 + r * math.sin(a) + 30)]), paint(LIME))
            sr.race_text(c, "A LOOP", 740, 1000, 110, fill=LEMON, scale=kl)
        sr.race_text(c, "UNDER THE HOOD", CX, 400, 96, fill=WHITE)


LOOP = ["PERCEIVE", "MODEL", "PREDICT", "PLAN", "ACT", "OBSERVE", "LEARN"]


def s_loop(arr, t, d, T):
    """The agent loop as a glossy rainbow ring with seven gates spaced evenly around it; each gate lights as it's spoken,
    the car laps faster and faster, and the current step blazes in the middle."""
    sr.sunburst(arr, T, cols=[(70, 20, 140), (40, 10, 90), (120, 40, 200)], cy=900, rays=26, spin=0.25)
    s = sr.surf(arr)
    ts = C["loop"]
    cur = sum(1 for x in ts if T >= x - 0.05) - 1
    cx, cy, rx, ry = CX, 900, 380, 300
    tilt = 0.92 + 0.08 * math.sin(T * 0.8)
    with s as c:
        for j, colr in enumerate(CANDY):                            # the ring: seven candy lanes with a sheen
            r = 1.0 - (j - 3) * 0.045
            c.drawOval(skia.Rect.MakeXYWH(cx - rx * r, cy - ry * r * tilt, 2 * rx * r, 2 * ry * r * tilt), paint(colr, stroke=16))
        c.drawOval(skia.Rect.MakeXYWH(cx - rx * 1.16, cy - ry * 1.16 * tilt, 2 * rx * 1.16, 2 * ry * 1.16 * tilt), paint(WHITE, 0.7, stroke=5))
        c.drawOval(skia.Rect.MakeXYWH(cx - rx * 0.84, cy - ry * 0.84 * tilt, 2 * rx * 0.84, 2 * ry * 0.84 * tilt), paint(WHITE, 0.7, stroke=5))
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(cx - rx, cy - ry * tilt, 2 * rx, 2 * ry * tilt), -150, 70)
        c.drawPath(arc, paint(WHITE, 0.45, stroke=10, blur=4))
        # the car goes round, faster each lap
        prog = (0.1 + t * (0.18 + 0.05 * t)) % 1.0
        a = -math.pi / 2 + prog * 2 * math.pi
        px, py = cx + rx * math.cos(a), cy + ry * tilt * math.sin(a)
        cast.car_side(c, px, py + 30, 0.34, T, speed=2, facing=1 if math.cos(a + math.pi / 2) > 0 else -1, **AI_CAR)
        for k, lab in enumerate(LOOP):                               # gates, evenly spaced, labels outside the ring
            a = -math.pi / 2 + k / 7 * 2 * math.pi
            gx, gy = cx + rx * math.cos(a), cy + ry * tilt * math.sin(a)
            lx, ly = cx + (rx + 150) * math.cos(a), cy + (ry * tilt + 120) * math.sin(a)
            lit = k <= cur
            hot = k == cur
            f = sr.font("bungee-400", 40)
            w = f.measureText(lab) + 34
            lx = min(max(lx, w / 2 + 24), sr.W - w / 2 - 24)
            c.drawLine(gx, gy, lx, ly, paint(WHITE, 0.8, stroke=5))
            c.drawCircle(gx, gy, 16, paint(CANDY[k % len(CANDY)] if lit else (90, 80, 120)))
            pill = skia.Path()
            sc = 1.18 if hot else 1.0
            pill.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(lx - w * sc / 2, ly - 34 * sc, w * sc, 64 * sc), 16, 16))
            if hot:
                c.drawPath(pill, paint(CANDY[k % len(CANDY)], 0.6, blur=22))
            sr.glossy(c, pill, CANDY[k % len(CANDY)] if lit else (70, 60, 100), rim=WHITE, lw=4)
            c.drawString(lab, lx - f.measureText(lab) / 2, ly + 14, f, paint(WHITE if lit else (190, 180, 220)))
        if cur >= 0:
            kk = pop(T, ts[cur] - 0.05, 0.2)
            sr.race_text(c, LOOP[cur], cx, cy + 40, 110 if len(LOOP[cur]) < 7 else 90, fill=LEMON, scale=kk)
            sr.plain(c, f"step {cur + 1} of 7", cx, cy + 110, 36, color=WHITE, fname="bungee-400")
        k_again = pop(T, W("u2", "again") - 0.1, 0.25)
        if k_again:
            sr.race_text(c, "...AND AGAIN!", CX, 1300, 80, fill=PINK, scale=k_again)
        sr.race_text(c, "THE AGENT LOOP", CX, 380, 90, fill=WHITE)


MEMS = [("EPISODIC", "what happened", ("what", 0), PINK), ("SEMANTIC", "what I know", ("what", 1), CYAN),
        ("PROCEDURAL", "how to do things", ("how", 0), LIME)]


def s_memory(arr, t, d, T):
    """Three memories, like three pit crews fuelling the car; each card lights as its phrase is spoken."""
    sr.sunburst(arr, T, cols=[(90, 40, 170), (50, 20, 110), (140, 60, 220)], cy=1300, rays=26, spin=0.3)
    s = sr.surf(arr)
    with s as c:
        sr.sparkles(c, T, n=10, seed=31, y0=250, y1=480)
        cast.car_side(c, CX, 1270, 0.95, T, speed=0.1, **AI_CAR)
        sr.race_text(c, "3 KINDS OF MEMORY", CX, 380, 84, fill=LEMON)
        for k, (name, desc, (word, nth), colr) in enumerate(MEMS):
            t0 = W("u3", word, nth)
            lit = ease(ramp(T, t0 - 0.1, t0 + 0.15))
            kk = 1 + 0.12 * math.sin(math.pi * min(1.0, max(0.0, (T - t0 + 0.1) / 0.3))) if lit > 0 else 1
            x = 190 + k * 350
            c.save()
            c.translate(x, 710)
            c.scale(kk, kk)
            panel = skia.Path()
            panel.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-160, -230, 320, 460), 26, 26))
            if lit > 0:
                c.drawPath(panel, paint(colr, 0.5 * lit, blur=26))
            sr.glossy(c, panel, colr if lit > 0.5 else (80, 60, 120), rim=WHITE, lw=5)
            if k == 0:
                I.clock(c, 0, -70, 0.9, 7, int(T * 60) % 60)
            elif k == 1:
                I.book(c, 0, -60, 0.7, color=sr.BLUE, title="FACTS")
            else:
                I.chip(c, 0, -60, 0.9, "HOW-TO", color=LEMON)
            sr.plain(c, name, 0, 120, min(40, 40 * 290 / sr.font("bungee-400", 40).measureText(name)), color=WHITE, fname="bungee-400")
            sr.plain(c, desc, 0, 180, min(34, 34 * 280 / sr.font("rubik-800", 34).measureText(desc)),
                     color=INK if lit > 0.5 else (200, 190, 230), fname="rubik-800")
            c.restore()
            if lit > 0:
                c.drawPath(sr.path(sr.bez((x, 940), (x, 1060), (CX - 40 + k * 40, 1150)), closed=False),
                           paint(sr.darker(colr, 0.7), lit, stroke=16))


def s_h2h(arr, t, d, T):
    """Head to head: the Memorizer (knows every track) versus the Learner (knows none, learns fast)."""
    track.stadium(arr, T, speed=0.9, pal=1)
    s = sr.surf(arr)
    kg = pop(T, S("v1") + 0.1, 0.3)
    with s as c:
        track.road_side(c, T, 1110, 1260, speed=0.9)
    track.near_wall(arr, T, 1260, speed=0.9)
    with s as c:
        cast.car_side(c, 330, 1190, 0.7, T, speed=2, **MEM_CAR)
        cast.car_side(c, 760, 1265, 0.75, T, speed=2, flames=True, **AI_CAR)
        if T < S("v2"):
            if kg:
                sr.race_text(c, "GENERAL-", 780, 900, 84, fill=LEMON, scale=kg)
                sr.race_text(c, "IZATION", 800, 1000, 84, fill=LEMON, scale=kg)
                sr.flare(c, 860, 820, 0.8, T, tint=CYAN)
        else:
            k1 = pop(T, W("v2", "memorized") - 0.2, 0.25)
            k2 = pop(T, W("v2", "other") - 0.1, 0.25)
            for side, (kk, name, l1, l2, colr, who) in enumerate(((k1, "THE MEMORIZER", "tracks memorized:", "ALL OF THEM", VIOLET, "memorizer"),
                                                                  (k2, "THE LEARNER", "tracks raced: 0", "LEARNS FAST", sr.BLUE, "ai"))):
                if not kk:
                    continue
                x = 60 + side * 500
                cast.face(c, who, x + 230, 470, 1.35 * kk, T, look=(0.6 if side == 0 else -0.6, 0.2), facing=1 if side == 0 else -1,
                          expr="grin")
                card = skia.Path()
                card.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, 640, 460, 300), 26, 26))
                sr.glossy(c, card, sr.darker(colr, 0.55), rim=sr.lighter(colr, 0.6), lw=5)
                c.drawRoundRect(skia.Rect.MakeXYWH(x + 30, 668, 400, 58), 16, 16, paint(INK, 0.85))
                sr.plain(c, name, x + 230, 712, 38, color=LEMON, fname="bungee-400")
                sr.plain(c, l1, x + 230, 800, 36, color=WHITE, fname="rubik-800")
                sr.plain(c, l2, x + 230, 880, 50, color=WHITE, fname="bungee-400")
        # layered depth: the rival's face looms in the foreground
        ko = ease(ramp(T, S("v2") - 0.2, S("v2") + 0.3))
        if ko < 1:
            cast.face(c, "memorizer", 250 - 700 * ko, 660, 3.3, T, talk=0.0, look=(0.9, 0.2), facing=1, expr="grin")


def s_newtrack(arr, t, d, T):
    """A brand-new track. The Memorizer follows its old map and crashes (slow motion, then snap); the Learner adapts."""
    dusk(arr)
    cr = C["crash"]
    slow = cr <= T < cr + 1.0
    ts = cr + (T - cr) * 0.08 if slow else (T if T < cr else T - 0.92)
    s = sr.surf(arr)
    with s as c:
        track.road_front(c, ts, speed=1.6, curve=0.9 * math.sin(ts * 0.9))
        # the memorizer
        if T < cr:
            cast.car_front(c, CX - 220 + 60 * math.sin(T * 4), 1200, 0.6, T, body=VIOLET, number="99", driver="memorizer")
            c.save()
            c.translate(250, 560)
            c.rotate(-6)
            m = skia.Path()
            m.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-190, -80, 380, 160), 18, 18))
            sr.glossy(c, m, (255, 250, 230), top=WHITE, rim=VIOLET, spec=0.2, lw=5)
            sr.plain(c, "OLD MAP: GO LEFT", 0, 15, 36, color=INK, fname="bungee-400")
            c.restore()
        else:
            k = ramp(ts, cr, cr + 0.6)
            rng = np.random.default_rng(9)
            for j in range(16):                                    # glossy fragments tumbling
                a = rng.uniform(0, 2 * math.pi)
                r = 60 + 520 * k * rng.uniform(0.4, 1.0)
                x = CX - 220 + r * math.cos(a)
                y = 1180 + r * math.sin(a) * 0.7 - 300 * k + 500 * k * k
                c.save()
                c.translate(x, y)
                c.rotate(360 * k * rng.uniform(-1, 1))
                shard = skia.Path()
                shard.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-30, -16, 60, 32), 8, 8))
                sr.glossy(c, shard, [VIOLET, LIME, WHITE][j % 3], lw=3)
                c.restore()
            sr.badge(c, "CRASH!", 290, 960, T, cr, color=RED, size=90, rot=-8)
        # the learner reads the road
        lx = CX + 220 + 120 * math.sin(ts * 0.9)
        cast.car_front(c, lx, 1255, 0.75, T, **FRONT)
        if T > W("v3", "notices") - 0.1:
            c.save()
            c.translate(560, 1100)
            c.rotate(4)
            m = skia.Path()
            m.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-180, -80, 360, 160), 18, 18))
            sr.glossy(c, m, (230, 255, 240), top=WHITE, rim=CYAN, spec=0.2, lw=5)
            sr.plain(c, "OLD MAP", 0, -10, 34, color=(120, 120, 140), fname="bungee-400")
            c.drawLine(-110, -24, 110, -24, paint(RED, stroke=8))
            sr.plain(c, "UPDATE: GO RIGHT", 0, 45, 32, color=sr.BLUE, fname="bungee-400")
            c.restore()
        cast.face(c, "ai", 790, 640, 2.5, T, talk=0.0, look=(-0.9, 0.2), facing=-1)
        sr.badge(c, "ADAPTS!", 800, 1040, T, W("v3", "adapts") - 0.1, color=sr.LIME, size=70, rot=6)
        sr.race_text(c, "BRAND-NEW TRACK", CX, 380, 90, fill=WHITE)
        if not slow:
            sr.speed_lines(c, CX, 850, T, n=36, color=WHITE, r0=480, a=0.55, seed=11)
    if slow:
        sr.freeze(arr, min(1.0, (T - cr) / 0.15))
        with s as c:
            sr.focus_lines(c, CX - 220, 1150, T, a=0.3)
    sr.snap_flash(arr, T - cr - 1.0)
    with s as c:
        pass


def s_chess2(arr, t, d, T):
    """Split screen: memorized every chess game but can't learn a new one, vs never saw chess but learns it."""
    xx = np.arange(sr.W)[None, :]
    yy = np.arange(H)[:, None]
    left = xx < CX + (yy - 900) * 0.12
    a = sr.new()
    sr.sky(a, [(0, (60, 20, 100)), (1, (150, 60, 200))])
    b = sr.new()
    sr.sky(b, [(0, (0, 150, 255)), (1, (120, 240, 255))])
    arr[..., :3] = np.where(left[..., None], a[..., :3], b[..., :3])
    s = sr.surf(arr)
    with s as c:
        sr.race_text(c, "MEMORIZER", 250, 420, 64, fill=WHITE)
        sr.race_text(c, "LEARNER", 830, 420, 64, fill=WHITE)
        I.book(c, 250, 700, 1.4, color=VIOLET, title="EVERY\nCHESS\nGAME")
        hexes = [(250 + dx, 1070 + dy) for dx, dy in ((0, 0), (70, 40), (-70, 40), (0, 80), (70, -40), (-70, -40), (0, -80))]
        for k, (hx, hy) in enumerate(hexes):
            pts = [(hx + 40 * math.cos(i / 6 * 2 * math.pi), hy + 40 * math.sin(i / 6 * 2 * math.pi)) for i in range(6)]
            c.drawPath(sr.path(pts), paint(CANDY[k % len(CANDY)]))
            c.drawPath(sr.path(pts), paint(INK, stroke=5))
        sr.plain(c, "a NEW game", 250, 912, 36, color=WHITE, fname="rubik-800")
        cast.face(c, "memorizer", 150, 1215, 0.6, T, look=(0.6, -0.4), expr="grin")
        sr.race_text(c, "?!", 400, 1150, 110, fill=LEMON)
        sr.badge(c, "NOT GENERAL", 260, 560, T, W("v4", "Not") - 0.05, color=RED, size=54, rot=-6)
        I.book(c, 830, 700, 0.9, color=TANG, title="HOW TO\nPLAY")
        k = ease(ramp(T, W("v4", "Never") - 0.1, E("v4")))
        cs = 62
        for i in range(4):
            for j in range(4):
                c.drawRect(skia.Rect.MakeXYWH(706 + i * cs, 920 + j * cs, cs, cs), paint(WHITE if (i + j) % 2 else INK))
        c.drawRect(skia.Rect.MakeXYWH(706, 920, 4 * cs, 4 * cs), paint(INK, stroke=6))
        if k > 0.3:
            I.chess_king(c, 706 + 2.5 * cs + 60 * k, 920 + 1.5 * cs, 0.42)
        if k > 0.7:
            sr.race_text(c, "WIN!", 830, 1230, 80, fill=sr.LIME)
        cast.face(c, "ai", 640, 1250, 0.55, T, talk=0.0, look=(0.4, -0.6))
        sr.badge(c, "INTELLIGENCE!", 820, 560, T, W("v4", "intelligence") - 0.2, color=sr.LIME, size=50, rot=6)


LAPS = [("CALCULATION", "calculation"), ("CHESS", "chess"), ("LANGUAGE", "language"), ("VISION", "vision")]


def s_laps(arr, t, d, T):
    """Every lap a machine wins, the finish line jumps further away: 'that's just computation'."""
    track.stadium(arr, T, speed=1.0, pal=2)
    s = sr.surf(arr)
    with s as c:
        track.road_side(c, T, 1110, 1260, speed=1.0)
    track.near_wall(arr, T, 1260, speed=1.0)
    with s as c:
        cast.car_side(c, 420, 1262, 0.85, T, speed=2, flames=True, **AI_CAR)
        done = [lab for lab, w in LAPS if T >= W("w1", w) - 0.05]
        for k, lab in enumerate(done):
            y = 480 + k * 90
            f = sr.font("bungee-400", 48)
            c.drawRoundRect(skia.Rect.MakeXYWH(80, y - 52, f.measureText(lab) + 110, 70), 16, 16, paint(WHITE))
            c.drawString(lab, 100, y, f, paint(INK))
            c.drawCircle(125 + f.measureText(lab), y - 17, 22, paint(sr.LIME))
        n = len(done)
        fx = 820 + (n * 60) % 200 + 100 * ease(ramp(T, W("w1", "move") - 0.1, W("w1", "move") + 0.5))
        c.drawRect(skia.Rect.MakeXYWH(fx, 700, 18, 480), paint(WHITE))
        sr.checker(c, fx + 18, 700, 180, 110, n=6, m=4)
        sr.badge(c, "“JUST COMPUTATION”", CX, 1050, T, W("w1", "just") - 0.1, color=VIOLET, size=54, rot=-4)
        sr.race_text(c, "THE MOVING FINISH LINE", CX, 380, 70, fill=LEMON)


def s_joke(arr, t, d, T):
    """The old joke: the announcer under a spotlight, then Tesler's theorem in neon."""
    sr.sunburst(arr, T, cols=[(60, 20, 110), (30, 10, 60)], cy=1500, rays=28, spin=0.2)
    s = sr.surf(arr)
    kq = pop(T, S("w2") - 0.1, 0.3)
    with s as c:
        for side in (-1, 1):                                       # spotlights
            c.drawPath(sr.path([(CX + side * 420, 0), (CX + side * 320, 0), (CX + side * 60, 1250), (CX + side * 360, 1250)]),
                       paint(LEMON, 0.16, blur=18))
        rng = np.random.default_rng(5)
        for j in range(160):                                        # the crowd, in silhouette
            x = rng.uniform(0, sr.W)
            c.drawCircle(x, 1280 + rng.uniform(0, 80), rng.uniform(26, 40), paint((20, 10, 40)))
        if kq <= 0.01:
            cast.face(c, "announcer", CX, 800, 2.6, T, talk=talk(T, "announcer"), look=(0.2, 0.1), expr="wow")
            c.drawRoundRect(skia.Rect.MakeXYWH(CX + 170, 980, 80, 150), 24, 24, paint(shader=sr.lin((0, 980), (0, 1130), [WHITE, (150, 160, 190)])))
            c.drawRect(skia.Rect.MakeXYWH(CX + 200, 1130, 20, 150), paint(INK))
            sr.race_text(c, "THE ANNOUNCER", CX, 380, 70, fill=LEMON)
        else:
            c.save()
            c.translate(CX, 820)
            c.scale(kq, kq)
            p = skia.Path()
            p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-480, -310, 960, 580), 40, 40))
            c.drawPath(p, paint((15, 5, 30), 0.85))
            c.drawPath(p, paint(PINK, stroke=16))
            c.drawPath(p, paint(PINK, 0.6, stroke=40, blur=22))
            f = sr.font("righteous-400", 96)
            for i, ln in enumerate(("\u201cAI IS WHATEVER", "HASN'T BEEN", "DONE YET.\u201d")):
                w = f.measureText(ln)
                c.drawString(ln, -w / 2, -150 + i * 140, f, paint(CYAN, 0.6, blur=10))
                c.drawString(ln, -w / 2, -150 + i * 140, f, paint((210, 255, 255)))
            c.restore()
            sr.plain(c, "Tesler's theorem (via Hofstadter, 1979)", CX, 1190, 36, color=WHITE, fname="rubik-700")
        kb = pop(T, E("w2") + 0.05, 0.2)
        if kb:
            sr.badge(c, "BA-DUM-TSS!", 760, 470, T, E("w2") + 0.05, color=TANG, size=56, rot=8)


def s_final(arr, t, d, T):
    """Paint the finish line; the learner blasts across it and the road fans out into every track."""
    dusk(arr)
    tp = W("f1", "Paint")
    tb = W("f1", "Then")
    s = sr.surf(arr)
    kp = ease(ramp(T, tp - 0.1, tp + 0.9))
    with s as c:
        if T < tb:
            track.road_front(c, T * 0.3, speed=0.3)
            y = 1080
            sr.checker(c, 140, y, 800 * kp, 90, n=int(12 * max(kp, 0.1)) or 1, m=2)
            I.roller(c, 140 + 800 * kp, y + 45, 1.0)
            sr.race_text(c, "STEP 1:", CX, 420, 100, fill=WHITE)
            sr.race_text(c, "PAINT THE FINISH LINE", CX, 540, 70, fill=LEMON)
            cast.car_front(c, CX, 1235, 0.6, T, **FRONT)
        else:
            u = T - tb
            for k in range(5):                                          # the road fans out into many tracks
                ang = (k - 2) * 0.35
                c.save()
                c.translate(CX, 1300)
                c.rotate(math.degrees(ang))
                c.translate(-CX, -1300)
                c.save()
                c.clipRect(skia.Rect.MakeXYWH(CX - 90, 300, 180, 1000))
                track.road_front(c, T, speed=2.0, width=0.5)
                c.restore()
                c.restore()
            sr.race_text(c, "RACE ANY TRACK", CX, 420, 96, fill=LEMON)
            for k in range(5):
                I.firework(c, 200 + k * 180, 600 - 80 * (k % 2), 180, T, tb + 0.2 * k, color=CANDY[k])
            z = 0.7 + 0.75 * ease(u / 1.2)
            cast.car_front(c, CX, 1225 + 50 * (z - 0.7), z, T, **FRONT)
            sr.speed_lines(c, CX, 900, T, n=60, color=WHITE, r0=380, seed=13)
            sr.flare(c, 820, 560, 1.1, T, tint=LEMON)


SOURCES = ["IBM Deep Blue vs Kasparov (1997)", "ImageNet: He et al., Microsoft (2015)", "Hendrycks et al., A Definition of AGI (2025)",
           "ARC Prize Foundation, ARC-AGI-3 (March 2026)", "Wozniak coffee test (Fast Company, 2010)",
           "Tesler's theorem (Hofstadter, G\u00f6del, Escher, Bach, 1979)"]


def s_end(arr, t, d, T):
    sr.sunburst(arr, T, cols=[(40, 18, 90), (22, 10, 55), (60, 25, 120)], cy=520, rays=26, spin=0.5)
    s = sr.surf(arr)
    t0 = C["end_card"]
    with s as c:
        sr.sparkles(c, T, n=18, seed=77, y0=240, y1=1500, a=0.7)
        # a kart laps the card
        u = ((T - t0) / 1.4) % 1.0
        sr.hlines(c, T, 330, 420, n=8, a=0.4, seed=19)
        cast.car_side(c, -220 + 1520 * u, 420, 0.55, T, speed=2, flames=True, **AI_CAR)
        kt = 1 + 0.04 * math.sin((T - t0) * 6)
        sr.race_text(c, "THE FIRST STEP", CX, 540, 110, fill=LEMON, scale=kt)
        sr.plain(c, "Define the finish line. Build a general learner.", CX, 610, 38, color=WHITE, fname="rubik-800")
        sr.plain(c, "SOURCES", CX, 760, 40, color=CYAN, fname="bungee-400")
        f = sr.font("rubik-500", 32)
        for i, ln in enumerate(SOURCES):
            c.drawString(ln, CX - f.measureText(ln) / 2, 830 + i * 48, f, paint((225, 225, 240)))
        f2 = sr.font("rubik-500", 27)
        for i, ln in enumerate(["A style homage to the Wachowskis' 2008 racing film", "All visuals, music and voices synthesized"]):
            c.drawString(ln, CX - f2.measureText(ln) / 2, 1180 + i * 40, f2, paint((170, 170, 190)))
        # the question for the comments
        kc = pop(T, t0 + 0.45, 0.3)
        if kc:
            pulse = 1 + 0.035 * math.sin((T - t0) * 9)
            c.save()
            c.translate(CX, 1370)
            c.scale(kc * pulse, kc * pulse)
            plate = skia.Path()
            plate.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-450, -110, 900, 215), 34, 34))
            sr.glossy(c, plate, (150, 25, 110), top=(215, 60, 160), rim=LEMON, spec=0.12, lw=6)
            sr.plain(c, "WHAT TRACK WOULD YOU", 0, -42, 46, color=WHITE, fname="bungee-400")
            sr.plain(c, "TEST AN AI ON?", 0, 18, 46, color=LEMON, fname="bungee-400")
            sr.plain(c, "Tell us in the comments", 0, 72, 32, color=WHITE, fname="rubik-800")
            c.restore()
