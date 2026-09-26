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
    sr.sky(arr, [(0, (20, 10, 60)), (1, (80, 40, 160))])
    s = sr.surf(arr)
    k = ease(ramp(T, S("u1") + 0.3, S("u1") + 0.9))
    kl = ease(ramp(T, W("u1", "loop") - 0.3, W("u1", "loop") + 0.2))
    with s as c:
        cast.car_side(c, CX, 1330, 1.6, T, speed=0.1, **AI_CAR)
        # hood lid swinging up
        c.save()
        c.translate(CX + 260, 1150)
        c.rotate(-70 * k)
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
    """The agent loop as a 3D circuit with seven gates; the car laps faster and faster."""
    sr.sky(arr, [(0, (10, 5, 40)), (0.5, (60, 20, 130)), (1, (255, 80, 170))])
    s = sr.surf(arr)
    ang = 0.3 + 0.25 * t
    cam = track.Cam((7.2 * math.sin(ang), 5.6, 7.2 * math.cos(ang)), (0, -0.4, 0), fov=62, cy=820)
    ts = C["loop"]
    with s as c:
        P = track.draw_circuit(c, cam, T)
        n = len(P)
        cur = sum(1 for x in ts if T >= x - 0.05) - 1
        gates = []
        for k, lab in enumerate(LOOP):
            idx = int(k / 7 * n)
            p, z = cam.project(P[idx] + np.array([0, 0.9, 0]))
            gates.append((z, k, lab, p, idx))
        for z, k, lab, p, idx in sorted(gates, key=lambda g: -g[0]):
            lit = k <= cur
            sc = 9.0 / z
            q, _ = cam.project(P[idx])
            c.drawLine(q[0], q[1], p[0], p[1], paint(WHITE, stroke=6 * sc))
            f = sr.font("bungee-400", 44 * sc)
            w = f.measureText(lab) + 30 * sc
            rr = skia.Path()
            rr.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(p[0] - w / 2, p[1] - 60 * sc, w, 70 * sc), 14 * sc, 14 * sc))
            sr.glossy(c, rr, CANDY[k % len(CANDY)] if lit else (70, 60, 100), rim=WHITE, lw=4)
            c.drawString(lab, p[0] - w / 2 + 15 * sc, p[1] - 10 * sc, f, paint(WHITE if lit else (190, 180, 220)))
            if k == cur:
                c.drawCircle(p[0], p[1] - 22 * sc, 90 * sc, paint(WHITE, 0.25, blur=30 * sc))
        # the car: position along the circuit, faster each lap
        prog = (t * (0.35 + 0.1 * t)) % 1.0
        idx = int(prog * n)
        p, z = cam.project(P[idx])
        cast.car_front(c, p[0], p[1], 0.9 * 9.0 / z * 0.5, T, **FRONT)
        k_again = pop(T, W("u2", "again") - 0.1, 0.25)
        if k_again:
            sr.race_text(c, "...AND AGAIN!", CX, 1250, 90, fill=LEMON, scale=k_again)
        sr.race_text(c, "THE AGENT LOOP", CX, 380, 90, fill=WHITE)


MEMS = [("EPISODIC", "what happened", "happened", PINK), ("SEMANTIC", "what I know", "know", CYAN), ("PROCEDURAL", "how to do things", "how", LIME)]


def s_memory(arr, t, d, T):
    """Three memories, like three pit crews fuelling the car."""
    sr.sky(arr, [(0, (30, 15, 70)), (1, (90, 40, 170))])
    s = sr.surf(arr)
    with s as c:
        cast.car_side(c, CX, 1320, 0.9, T, speed=0.1, **AI_CAR)
        sr.race_text(c, "3 KINDS OF MEMORY", CX, 380, 84, fill=LEMON)
        for k, (name, desc, word, colr) in enumerate(MEMS):
            t0 = W("u3", word)
            kk = pop(T, t0 - 0.15, 0.25)
            x = 190 + k * 350
            if kk:
                panel = skia.Path()
                panel.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 160, 480, 320, 460), 26, 26))
                sr.glossy(c, panel, colr, rim=WHITE, lw=5)
                if k == 0:
                    I.clock(c, x, 640, 0.9, 7, int(T * 60) % 60)
                elif k == 1:
                    I.book(c, x, 650, 0.7, color=sr.BLUE, title="FACTS")
                else:
                    I.chip(c, x, 650, 0.9, "HOW-TO", color=LEMON)
                sr.plain(c, name, x, 830, 40, color=WHITE, fname="bungee-400")
                sr.plain(c, desc, x, 890, 34, color=INK, fname="rubik-800")
                # fuel hose to the car
                c.drawPath(sr.path(sr.bez((x, 940), (x, 1080), (CX - 40 + k * 40, 1180)), closed=False), paint(sr.darker(colr, 0.7), stroke=16))


def s_h2h(arr, t, d, T):
    """Head to head: the Memorizer (knows every track) versus the Learner (knows none, learns fast)."""
    track.stadium(arr, T, speed=0.9, pal=1)
    s = sr.surf(arr)
    kg = pop(T, S("v1") + 0.1, 0.3)
    with s as c:
        track.road_side(c, T, 1180, 1330, speed=0.9)
    track.near_wall(arr, T, 1330, speed=0.9)
    with s as c:
        cast.car_side(c, 330, 1260, 0.7, T, speed=2, **MEM_CAR)
        cast.car_side(c, 760, 1340, 0.75, T, speed=2, flames=True, **AI_CAR)
        if T < S("v2"):
            if kg:
                sr.race_text(c, "GENERALIZATION", CX, 620, 96, fill=LEMON, scale=kg)
                sr.flare(c, 860, 540, 0.8, T, tint=CYAN)
        else:
            k1 = pop(T, W("v2", "memorized") - 0.2, 0.25)
            k2 = pop(T, W("v2", "other") - 0.1, 0.25)
            for side, (kk, name, l1, l2, colr) in enumerate(((k1, "THE MEMORIZER", "tracks memorized:", "ALL OF THEM", VIOLET),
                                                             (k2, "THE LEARNER", "tracks raced: 0", "LEARNS FAST", sr.BLUE))):
                if not kk:
                    continue
                x = 60 + side * 500
                card = skia.Path()
                card.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, 480, 460, 300), 26, 26))
                sr.glossy(c, card, colr, rim=WHITE, lw=5)
                sr.plain(c, name, x + 230, 550, 40, color=WHITE, fname="bungee-400")
                sr.plain(c, l1, x + 230, 640, 36, color=WHITE, fname="rubik-800")
                sr.plain(c, l2, x + 230, 720, 50, color=LEMON, fname="bungee-400")
        # layered depth: the rival's face looms in the foreground
        cast.face(c, "memorizer", 1010, 950, 2.6, T, talk=0.0, look=(-0.8, 0.2), facing=-1, expr="grin")


def s_newtrack(arr, t, d, T):
    """A brand-new track. The Memorizer follows its old map and crashes (slow motion, then snap); the Learner adapts."""
    dusk(arr)
    cr = C["crash"]
    slow = cr <= T < cr + 0.7
    ts = cr + (T - cr) * 0.15 if slow else (T if T < cr else T - 0.6)
    s = sr.surf(arr)
    with s as c:
        track.road_front(c, ts, speed=1.6, curve=0.9 * math.sin(ts * 0.9))
        # the memorizer
        if T < cr:
            cast.car_front(c, CX - 220 + 60 * math.sin(T * 4), 1260, 0.6, T, body=VIOLET, number="99", driver="memorizer")
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
            sr.badge(c, "CRASH!", CX - 180, 900, T, cr, color=RED, size=90, rot=-8)
            if slow:
                c.drawRect(skia.Rect.MakeWH(sr.W, H), paint(INK, 0.15))
        # the learner reads the road
        lx = CX + 220 + 120 * math.sin(ts * 0.9)
        cast.car_front(c, lx, 1330, 0.75, T, **FRONT)
        if T > W("v3", "notices") - 0.1:
            c.save()
            c.translate(820, 560)
            c.rotate(5)
            m = skia.Path()
            m.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-180, -80, 360, 160), 18, 18))
            sr.glossy(c, m, (230, 255, 240), top=WHITE, rim=CYAN, spec=0.2, lw=5)
            sr.plain(c, "OLD MAP", 0, -10, 34, color=(120, 120, 140), fname="bungee-400")
            c.drawLine(-110, -24, 110, -24, paint(RED, stroke=8))
            sr.plain(c, "UPDATE: GO RIGHT", 0, 45, 32, color=sr.BLUE, fname="bungee-400")
            c.restore()
        cast.face(c, "ai", 20, 980, 2.0, T, talk=0.0, look=(0.9, -0.1), facing=1)
        sr.badge(c, "ADAPTS!", 800, 900, T, W("v3", "adapts") - 0.1, color=sr.LIME, size=70, rot=6)
        sr.race_text(c, "BRAND-NEW TRACK", CX, 380, 90, fill=WHITE)
        if not slow:
            sr.speed_lines(c, CX, 850, T, n=36, color=WHITE, r0=480, a=0.55, seed=11)


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
        hexes = [(250 + dx, 1040 + dy) for dx, dy in ((0, 0), (80, 46), (-80, 46), (0, 92), (80, -46), (-80, -46), (0, -92))]
        for k, (hx, hy) in enumerate(hexes):
            pts = [(hx + 46 * math.cos(i / 6 * 2 * math.pi), hy + 46 * math.sin(i / 6 * 2 * math.pi)) for i in range(6)]
            c.drawPath(sr.path(pts), paint(CANDY[k % len(CANDY)]))
            c.drawPath(sr.path(pts), paint(INK, stroke=5))
        sr.plain(c, "a NEW game", 250, 1200, 40, color=WHITE, fname="rubik-800")
        cast.face(c, "memorizer", 150, 1250, 0.75, T, look=(0.6, -0.4), expr="grin")
        sr.race_text(c, "?!", 370, 1000, 130, fill=LEMON)
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
        cast.face(c, "ai", 960, 1240, 0.7, T, talk=0.0, look=(-0.4, -0.6))
        sr.badge(c, "INTELLIGENCE!", 820, 560, T, W("v4", "intelligence") - 0.2, color=sr.LIME, size=50, rot=6)


LAPS = [("CALCULATION", "calculation"), ("CHESS", "chess"), ("LANGUAGE", "language"), ("VISION", "vision")]


def s_laps(arr, t, d, T):
    """Every lap a machine wins, the finish line jumps further away: 'that's just computation'."""
    track.stadium(arr, T, speed=1.0, pal=2)
    s = sr.surf(arr)
    with s as c:
        track.road_side(c, T, 1180, 1330, speed=1.0)
    track.near_wall(arr, T, 1330, speed=1.0)
    with s as c:
        cast.car_side(c, 420, 1330, 0.85, T, speed=2, flames=True, **AI_CAR)
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
    """The old joke, in neon: Tesler's theorem."""
    sr.sky(arr, [(0, (10, 5, 30)), (1, (60, 20, 90))])
    s = sr.surf(arr)
    with s as c:
        for k in range(30):
            x = (k * 83) % sr.W
            c.drawCircle(x, 300 + (k * 137) % 1100, 3, paint(WHITE, 0.6))
        k = pop(T, S("w2") - 0.1, 0.3)
        if k:
            c.save()
            c.translate(CX, 820)
            c.scale(k, k)
            p = skia.Path()
            p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-470, -300, 940, 560), 40, 40))
            c.drawPath(p, paint(PINK, stroke=16))
            c.drawPath(p, paint(PINK, 0.6, stroke=40, blur=22))
            for i, ln in enumerate(("“AI IS WHATEVER", "HASN'T BEEN", "DONE YET.”")):
                f = sr.font("monoton-400", 92)
                c.drawString(ln, -f.measureText(ln) / 2, -150 + i * 140, f, paint(CYAN))
            c.restore()
            sr.plain(c, "Tesler's theorem (via Hofstadter, 1979)", CX, 1180, 36, color=WHITE, fname="rubik-700")
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
            cast.car_front(c, CX, 1330, 0.6, T, **FRONT)
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
            z = 0.7 + 1.4 * ease(u / 1.2)
            cast.car_front(c, CX, 1330 + 200 * (z - 0.7), z, T, **FRONT)
            sr.speed_lines(c, CX, 900, T, n=60, color=WHITE, r0=380, seed=13)
            sr.flare(c, 820, 560, 1.1, T, tint=LEMON)


SOURCES = ["IBM Deep Blue vs Kasparov (1997)", "ImageNet: He et al., Microsoft (2015)", "Hendrycks et al., A Definition of AGI (2025)",
           "ARC Prize Foundation, ARC-AGI-3 (March 2026)", "Wozniak coffee test (Fast Company, 2010)",
           "Tesler's theorem (Hofstadter, Godel, Escher, Bach, 1979)"]


def s_end(arr, t, d, T):
    sr.sky(arr, [(0, (20, 10, 50)), (1, (70, 30, 130))])
    s = sr.surf(arr)
    with s as c:
        sr.race_text(c, "THE FIRST STEP", CX, 520, 110, fill=LEMON)
        sr.plain(c, "Define the finish line. Build a general learner.", CX, 610, 38, color=WHITE, fname="rubik-800")
        sr.plain(c, "SOURCES", CX, 760, 40, color=CYAN, fname="bungee-400")
        f = sr.font("rubik-500", 32)
        for i, ln in enumerate(SOURCES):
            c.drawString(ln, CX - f.measureText(ln) / 2, 830 + i * 48, f, paint((225, 225, 240)))
        f2 = sr.font("rubik-500", 27)
        for i, ln in enumerate(["Style homage to Speed Racer (2008, dir. the Wachowskis)", "All visuals, music and voices synthesized"]):
            c.drawString(ln, CX - f2.measureText(ln) / 2, 1180 + i * 40, f2, paint((170, 170, 190)))
