"""Answer two (a general learner), the Dinner Grand Prix, transfer, and the coffee test."""
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
from sr import CANDY, CX, CYAN, H, INK, LEMON, LIME, PINK, RED, TANG, VIOLET, WHITE, ease, paint, pop, ramp

FRONT = {k: v for k, v in AI_CAR.items() if k != "stripe"}


def s_engine(arr, t, d, T):
    """The garage: under the hood, the part that matters. Pistons pump, sparks fly."""
    sr.sky(arr, [(0, (20, 10, 50)), (0.6, (60, 30, 120)), (1, (140, 60, 200))])
    s = sr.surf(arr)
    z = 1.0 + 0.25 * ease(t / d)
    with s as c:
        for k in range(10):
            c.drawRect(skia.Rect.MakeXYWH(k * 110 - 20, 0, 50, H), paint(CANDY[k % len(CANDY)], 0.1))
        c.save()
        c.translate(CX, 880)
        c.scale(z, z)
        c.translate(-CX, -880)
        I.engine_block(c, CX, 900, 1.9, T)
        rng = np.random.default_rng(int(T * 12))
        for k in range(14):
            a = rng.uniform(0, 2 * math.pi)
            r = rng.uniform(250, 480)
            c.drawLine(CX + 200 * math.cos(a), 900 + 150 * math.sin(a), CX + r * math.cos(a), 900 + r * math.sin(a),
                       paint(LEMON, 0.8, stroke=4))
        c.restore()
        sr.flare(c, 760, 650, 0.9, T, tint=PINK)
        sr.race_text(c, "ANSWER 2", CX, 380, 110, fill=LEMON)
        sr.lower_third(c, T, S("e1") + 0.2, E("e1") + 0.3, "TECHNOLOGY", "a truly general learner", color=CYAN, y=1230)


def s_learner(arr, t, d, T):
    """Five quick clips: dropped somewhere new, learns by trying, remembers, picks up skills, carries them on."""
    beats = [W("e2", "Drop"), W("e2", "learns"), W("e2", "remembers"), W("e2", "picks"), W("e2", "carries"), W("e2", "keeps"),
             W("e2", "without")]
    i = max(0, sum(1 for b in beats if T >= b - 0.05) - 1)
    lt = T - beats[i]
    bgs = [[(0, (40, 200, 120)), (1, (230, 255, 120))], [(0, (255, 120, 60)), (1, (255, 230, 120))],
           [(0, (80, 40, 200)), (1, (200, 120, 255))], [(0, (0, 180, 255)), (1, (180, 255, 255))],
           [(0, (140, 200, 255)), (1, (255, 255, 255))], [(0, (255, 60, 150)), (1, (255, 200, 90))],
           [(0, (30, 20, 70)), (1, (90, 60, 160))]]
    sr.sky(arr, bgs[i])
    s = sr.surf(arr)
    with s as c:
        labels = ["DROPPED SOMEWHERE NEW", "LEARNS BY TRYING", "REMEMBERS", "NEW SKILLS, NOBODY TAUGHT", "CARRIES THEM ELSEWHERE",
                  "KEEPS IMPROVING", "NO REBUILD NEEDED"]
        if i == 0:                                          # parachute drop into a candy jungle
            for k in range(7):
                x = k * 170 + 40
                c.drawPath(sr.path([(x - 60, 1300), (x, 700 + 60 * (k % 3)), (x + 60, 1300)]), paint((30, 150, 90)))
                c.drawCircle(x, 720 + 60 * (k % 3), 70, paint(LIME))
            y = 520 + 780 * ease(lt / 0.8)
            sq = 0.2 if lt > 0.8 and lt < 1.0 else 0.0
            if lt < 0.8:
                c.drawPath(sr.path(sr.bez((CX - 220, y - 380), (CX, y - 520), (CX + 220, y - 380)).tolist() + [(CX, y - 200)]), paint(PINK))
            cast.car_side(c, CX, y + 20, 0.8 * (1 + sq), T, speed=0.2, **AI_CAR)
        elif i == 1:                                        # bump, bump, lightbulb
            bx = CX - 200 + 60 * math.sin(lt * 9)
            cast.car_side(c, bx, 1250, 0.8, T, speed=0.3, **AI_CAR)
            c.drawRect(skia.Rect.MakeXYWH(760, 900, 60, 350), paint(INK))
            sr.badge(c, "BONK", 700, 850, T, beats[1] + 0.2, color=TANG, size=50, rot=-10)
            I.bulb(c, bx + 40, 760, 1.0, lit=ease(ramp(lt, 0.4, 0.6)))
        elif i == 2:                                        # a memory chip lights up, a map appears in a bubble
            cast.car_side(c, CX - 120, 1250, 0.8, T, speed=0.5, **AI_CAR)
            I.chip(c, 760, 720, 1.2, "MEMORY", color=LIME)
            c.drawOval(skia.Rect.MakeXYWH(120, 560, 440, 280), paint(WHITE))
            c.drawPath(sr.path(sr.bez((170, 760), (300, 600), (500, 720)), closed=False), paint(PINK, stroke=12))
            c.drawCircle(500, 720, 18, paint(RED))
        elif i == 3:                                        # tools snap on: a wing, a snorkel, a ladder
            cast.car_side(c, CX, 1250, 0.9, T, speed=0.5, **AI_CAR)
            for k, (lab, colr) in enumerate((("WING", PINK), ("SNORKEL", LEMON), ("LADDER", LIME))):
                kk = pop(lt, 0.15 + 0.3 * k, 0.2)
                if kk:
                    sr.badge(c, lab, 240 + k * 300, 780, T, beats[3] + 0.15 + 0.3 * k, color=colr, size=46, rot=-6 + 6 * k)
        elif i == 4:                                        # through a portal onto a snowy track
            I.mountain(c, 300, 1150, 1.2)
            I.mountain(c, 820, 1150, 1.0, color=(230, 200, 255))
            c.drawOval(skia.Rect.MakeXYWH(620, 820, 300, 440), paint(VIOLET, stroke=40))
            c.drawOval(skia.Rect.MakeXYWH(620, 820, 300, 440), paint(CYAN, 0.6, blur=30, stroke=30))
            cast.car_side(c, 200 + 700 * ease(lt / 1.2), 1250, 0.8, T, speed=2, flames=True, **AI_CAR)
        elif i == 5:                                        # the skill gauge climbs
            I.speedo(c, CX, 850, 230, min(1.0, 0.15 + lt * 0.7), label="SKILL")
            lv = 1 + int(lt * 3)
            sr.race_text(c, f"LV {lv}", CX, 1250, 110, fill=LEMON)
        else:                                               # the pit crew has nothing to do
            cast.car_side(c, CX, 1200, 0.8, T, speed=0.3, **AI_CAR)
            for k in range(3):
                x = 220 + k * 320
                c.drawCircle(x, 820, 50, paint((255, 196, 160)))
                c.drawRect(skia.Rect.MakeXYWH(x - 50, 870, 100, 110), paint(RED))
                sr.plain(c, "z", x + 60, 760 - 20 * ((T * 2 + k) % 1), 50, color=WHITE, fname="bungee-400")
        sr.race_text(c, labels[i], CX, 420, 76 if len(labels[i]) < 18 else 62, fill=WHITE)
        sr.plain(c, f"{i + 1}/7", CX, 490, 34, color=WHITE, fname="bungee-400")


def s_facts(arr, t, d, T):
    """Stuffing in more facts: a car so loaded with books it can barely roll."""
    sr.sky(arr, [(0, (255, 200, 90)), (1, (255, 120, 90))])
    s = sr.surf(arr)
    with s as c:
        track.road_side(c, T * 0.2, 1180, 1330, speed=0.2)
        cast.car_side(c, CX - 40, 1300, 1.0, T, body=VIOLET, stripe=LIME, number="99", driver="memorizer", books=True, speed=0.2)
        for k in range(6):
            I.book(c, 250 + k * 110, 980 - 30 * (k % 2), 0.6, color=CANDY[k % len(CANDY)])
        sr.race_text(c, "MORE FACTS", CX, 480, 110, fill=WHITE)
        sr.badge(c, "NOT = GENERAL", CX, 680, T, S("e3") + 0.4, color=RED, size=62, rot=-4)


# ------------------------------------------------------------------ the dinner grand prix

def s_dinner(arr, t, d, T):
    """The Dinner Grand Prix: title card, then the house at the end of the rainbow road, and the invitation."""
    dusk(arr)
    s = sr.surf(arr)
    with s as c:
        track.road_front(c, T, speed=0.8)
        I.house(c, CX, 820, 0.9)
        k = pop(T, S("a1") + 0.1, 0.3)
        if k:
            sr.checker(c, 90, 250, 900, 60, n=18, m=2)
            sr.race_text(c, "THE DINNER", CX, 420, 110, fill=LEMON, scale=k)
            sr.race_text(c, "GRAND PRIX", CX, 540, 120, fill=PINK, scale=k)
        ki = ease(ramp(T, W("t1", "Six") - 0.2, W("t1", "Six") + 0.2))
        if ki > 0:
            c.save()
            c.translate(CX, 1000 + 300 * (1 - ki))
            c.rotate(-4 + 4 * ki)
            card = skia.Path()
            card.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-380, -150, 760, 300), 24, 24))
            sr.glossy(c, card, (255, 250, 240), top=WHITE, rim=PINK, spec=0.3, lw=6)
            sr.plain(c, "6 people. Tonight. 7:00", 0, -50, 48, color=INK, fname="bungee-400")
            sr.plain(c, "Make it a great evening.", 0, 30, 46, color=PINK, fname="rubik-800")
            sr.plain(c, "(no special benchmark)", 0, 100, 34, color=(110, 100, 130), fname="rubik-700")
            c.restore()
        cast.car_front(c, CX + 260, 1330, 0.55, T, **FRONT)


HAZARDS = ["6 GUESTS · 4 CHAIRS", "VEGETARIAN", "PEANUT ALLERGY", "STORE CLOSES 6:00", "OVEN RUNS HOT", "INGREDIENT MISSING",
           "GUEST LATE", "WINE SPILL!"]
HAZ_BG = [PINK, LIME, TANG, CYAN, RED, VIOLET, LEMON, (200, 20, 80)]


def s_hazards(arr, t, d, T):
    """Eight hazards in ten seconds. The car swerves through each; the wine spill goes to slow motion, then snaps."""
    hz = C["hazards"]
    i = max(0, sum(1 for b in hz if T >= b - 0.05) - 1)
    lt = T - hz[i]
    bg = HAZ_BG[i]
    sr.sky(arr, [(0, sr.darker(bg, 0.35)), (0.45, bg), (1, sr.lighter(bg, 0.6))])
    slow = i == 7 and lt < 0.85
    ts = hz[7] + (lt * 0.2 if slow else 0.17 + (lt - 0.85) * 1.5) if i == 7 else T
    s = sr.surf(arr)
    with s as c:
        track.road_front(c, ts, speed=1.8 if not slow else 0.3, curve=0.35 * math.sin(i * 1.7 + lt))
        ox = CX + 200 * math.sin(i * 2.1)
        oy = 1000
        if i == 0:
            for k in range(6):
                I.guest(c, 180 + k * 145, 900, 0.9, color=CANDY[k])
            for k in range(4):
                I.chair(c, 260 + k * 190, 1080, 1.1, broken=k == 3)
        elif i == 1:
            I.broccoli(c, ox, oy, 2.0)
        elif i == 2:
            I.peanut(c, ox, oy, 1.8)
        elif i == 3:
            I.clock(c, ox, oy - 40, 1.8, 6, int(lt * 40) % 60)
        elif i == 4:
            I.oven(c, ox, oy, 1.8, T)
        elif i == 5:
            c.drawRoundRect(skia.Rect.MakeXYWH(ox - 220, oy - 200, 440, 360), 20, 20, paint(WHITE))
            for k in range(3):
                c.drawRect(skia.Rect.MakeXYWH(ox - 200, oy - 120 + k * 110, 400, 10), paint(INK))
            sr.race_text(c, "?", ox, oy + 80, 260, fill=VIOLET)
        elif i == 6:
            c.drawRoundRect(skia.Rect.MakeXYWH(ox - 150, oy - 300, 300, 460), 20, 20, paint(sr.darker(TANG, 0.8)))
            c.drawCircle(ox + 100, oy - 60, 20, paint(LEMON))
            I.clock(c, ox + 260, oy - 280, 0.9, 7, 25)
        else:
            k = ease(lt / 0.85) if slow else 1.0
            I.wine(c, ox, oy, 2.0, tilt=70 * k, T=T, drops=k)
        lean = 14 * math.sin(i * 1.9 + lt * 3)
        c.save()
        c.translate(CX + 160 * math.sin(i * 1.3 + lt * 2), 1330)
        c.rotate(lean)
        cast.car_front(c, 0, 0, 0.85, ts, **FRONT)
        c.restore()
        sr.badge(c, HAZARDS[i], CX, 520, T, hz[i], color=sr.darker(bg, 0.6) if i != 6 else TANG, size=64 if len(HAZARDS[i]) < 14 else 50,
                 rot=-5 + 10 * (i % 2))
        sr.plain(c, f"HAZARD {i + 1}/8", CX, 350, 40, color=WHITE, fname="bungee-400")
        if not slow:
            sr.speed_lines(c, CX, 900, T, n=40, color=WHITE, r0=460, a=0.6, seed=i)
        if i == 7 and 0.85 <= lt < 1.0:
            c.drawRect(skia.Rect.MakeWH(sr.W, H), paint(WHITE, 0.6 * (1 - (lt - 0.85) / 0.15)))


SKILLS = [("PERCEIVE", "perceive"), ("REASON", "reason"), ("ASK", "ask"), ("PLAN", "plan"), ("FIX", "fix"), ("IMPROVISE", "improvise"),
          ("REMEMBER", "remember"), ("LEARN", "learn")]


def s_skills(arr, t, d, T):
    """Eight-way split screen: each skill lights as it's named."""
    arr[..., :3] = (20, 10, 45)
    s = sr.surf(arr)
    with s as c:
        for k, (lab, word) in enumerate(SKILLS):
            col_i, row = k % 2, k // 2
            x, y = 60 + col_i * 490, 300 + row * 250
            t0 = W("t3", word)
            lit = ease(ramp(T, t0 - 0.08, t0 + 0.12))
            panel = skia.Path()
            panel.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, 470, 225), 22, 22))
            colr = CANDY[k % len(CANDY)]
            sr.glossy(c, panel, colr if lit > 0.5 else (60, 50, 90), rim=WHITE if lit > 0.5 else colr, lw=5)
            sc = 1 + 0.15 * pop(T, t0 - 0.08, 0.25) - 0.15 if lit else 1
            sr.race_text(c, lab, x + 235, y + 140, 70 * sc if len(lab) < 9 else 58 * sc, fill=WHITE if lit > 0.5 else (150, 140, 190),
                         shadow=lit > 0.5)


def s_expedition(arr, t, d, T):
    """Next week, a new track: the same skills fly from the dinner panel to the expedition panel."""
    sr.sky(arr, [(0, (120, 200, 255)), (0.6, (230, 245, 255)), (1, (255, 255, 255))])
    s = sr.surf(arr)
    with s as c:
        I.mountain(c, 280, 820, 1.2)
        I.mountain(c, 800, 820, 1.4, color=(210, 190, 255))
        track.road_side(c, T, 820, 900, speed=1.0)
        cast.car_side(c, 520 + 100 * math.sin(T), 900, 0.7, T, speed=2, flames=True, **AI_CAR)
        c.drawRect(skia.Rect.MakeXYWH(440 + 100 * math.sin(T) - 10, 690, 8, 110), paint(INK))
        c.drawPath(sr.path([(440 + 100 * math.sin(T), 690), (520 + 100 * math.sin(T), 715), (440 + 100 * math.sin(T), 740)]), paint(RED))
        sr.race_text(c, "SCIENCE EXPEDITION", CX, 380, 74, fill=sr.BLUE)
        sr.plain(c, "new track, same skills", CX, 450, 38, color=INK, fname="rubik-800")
        # split: dinner panel (left) -> expedition panel (right)
        for side, (lab, colr) in enumerate((("DINNER", PINK), ("EXPEDITION", CYAN))):
            x = 60 + side * 520
            p = skia.Path()
            p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, 960, 440, 330), 24, 24))
            sr.glossy(c, p, colr, rim=WHITE, lw=5)
            sr.plain(c, lab, x + 220, 1010, 40, color=WHITE, fname="bungee-400")
        chips = [("SCHEDULING", "scheduling"), ("BUDGETS", "budgets"), ("BACKUP PLANS", "backup"), ("PEOPLE'S NEEDS", "needs"), ("RISK", "risk")]
        for k, (lab, word) in enumerate(chips):
            t0 = W("t4", word)
            m = ease(ramp(T, t0 - 0.15, t0 + 0.35))
            y = 1060 + k * 46
            x = 280 + 520 * m
            f = sr.font("bungee-400", 30)
            w = f.measureText(lab) + 30
            c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - 30, w, 40), 12, 12, paint(WHITE))
            c.drawString(lab, x - w / 2 + 15, y + 2, f, paint(INK))


def s_transfer(arr, t, d, T):
    """The jump from one track to another, in slow motion at the top, then a snap."""
    dusk(arr)
    u = t / d
    slow = 0.25 < u < 0.7
    uu = 0.25 + (u - 0.25) * 0.3 if slow else (u if u <= 0.25 else 0.385 + (u - 0.7) * 2.05)
    s = sr.surf(arr)
    with s as c:
        track.road_side(c, T, 1180, 1330, speed=1.5)
        c.drawRect(skia.Rect.MakeXYWH(470, 1170, 140, 200), paint((20, 10, 40)))
        x = 150 + 800 * min(1.0, uu)
        y = 1250 - 480 * math.sin(math.pi * min(1.0, uu))
        cast.car_side(c, x, y, 0.8, T, speed=2, flames=True, **AI_CAR)
        sr.plain(c, "DINNER", 200, 1100, 44, color=WHITE, fname="bungee-400")
        sr.plain(c, "EXPEDITION", 860, 1100, 44, color=WHITE, fname="bungee-400")
        sr.race_text(c, "TRANSFER", CX, 460, 130, fill=LEMON)
        sr.race_text(c, "= GENERALITY", CX, 590, 100, fill=CYAN)
        if not slow:
            sr.hlines(c, T, 700, 1150, n=24, a=0.7, seed=5)


def s_coffee(arr, t, d, T):
    """Wozniak's coffee test: walk into a stranger's home and make a cup of coffee."""
    sr.sky(arr, [(0, (255, 230, 190)), (1, (255, 180, 150))])
    s = sr.surf(arr)
    with s as c:
        for k in range(4):
            c.drawRoundRect(skia.Rect.MakeXYWH(90 + k * 230, 560, 200, 220), 18, 18, paint(sr.lighter(CANDY[k], 0.4)))
            c.drawRoundRect(skia.Rect.MakeXYWH(90 + k * 230, 560, 200, 220), 18, 18, paint(INK, stroke=5))
            c.drawCircle(170 + k * 230, 670, 10, paint(INK))
        c.drawRect(skia.Rect.MakeXYWH(0, 1040, sr.W, 60), paint((200, 120, 80)))
        I.cup(c, 700, 960, 1.1, T)
        rx = 330 + 30 * math.sin(T * 3)
        c.drawLine(rx, 1300, rx + 180, 1010, paint((200, 205, 225), stroke=30))
        c.drawCircle(rx + 190, 995, 34, paint(CYAN))
        sr.glint(c, 760, 860, 40, T)
        sr.lower_third(c, T, S("t6") + 0.3, E("t6") + 0.3, "THE COFFEE TEST", "Steve Wozniak, 2010", color=TANG, y=420)
        sr.race_text(c, "ANY KITCHEN.", CX, 1250, 90, fill=WHITE)
