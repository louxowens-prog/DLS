"""Scenes 1: the cold open (gold medal, the clock), the question, the road of intelligence, how fast it's moving."""
import math

import numpy as np
import skia

import bg
import cast
import sv
from common import E, S, W, talk
from cues import C
from script import BOT, NAR
from sv import CYAN, INK, MAG, PAPER, WHITE, YEL, bez, ease, paint, path, pop, ramp, twos

LIME, ORANGE, RED = sv.LIME, sv.ORANGE, sv.RED


def impact(T, color, draw, cx=540, cy=900, word=None, wx=540, wy=420, wsize=230, rot=-8, line=INK, sil=INK):
    """An impact frame: flat colour, ink focus lines, the subject as a flat silhouette with a white rim."""
    st = sv.Stage(color)
    sv.impact_bg(st.c, color, cx, cy, T, line=line)
    sv.over(st.arr, sv.silhouette(draw, sil, rim=WHITE, rim_dx=12))
    if word:
        sv.sfx(st.c, word, wx, wy, wsize, rot=rot, fill=WHITE, fill2=YEL, dots=MAG)
    return st.arr


# ------------------------------------------------------------------ 1. gold

def s_gold(T, t, d):
    tg = C["gold"]
    arms_up = ((250, -40), (-70, 40))
    if tg <= T < tg + 3 / 24:
        return impact(T, YEL, lambda P: cast.bot(P, 540, 900, 2.3, T, medal=True, arms=arms_up, bounce=0),
                      cx=540, cy=820, word="POW!", wx=280, wy=300)
    st = sv.Stage((255, 214, 90))
    bg.cartoon_stage(st, T)
    c = st.c
    z = 1.0 + 0.06 * ease(t / d)
    P = st.pen()
    P.save()
    P.translate(540, 1100)
    P.scale(z, z)
    P.translate(-540, -1100)
    # podium: flat cartoon blocks
    for x0, w, h, num, col in ((140, 260, 180, "2", (200, 210, 230)), (400, 280, 300, "1", (255, 200, 40)), (680, 260, 130, "3", (230, 140, 80))):
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, 1560 - h, w, h + 40), 18, 18)
        c.drawRRect(r, paint(col))
        c.drawRRect(r, paint(INK, stroke=8))
        f = sv.font("luckiest-guy-400", 110)
        c.drawString(num, x0 + w / 2 - f.measureText(num) / 2, 1560 - h + 130, f, paint(INK))
    up = T >= tg - 0.1
    cast.bot(P, 540, 880, 1.9, T, medal=T >= tg - 0.15, arms=arms_up if up else ((200, 160), (-20, 20)),
             talk=0.0, expr="happy")
    P.restore()
    st.flush()
    bg.confetti(c, T, n=46)
    # the event banner hanging from the valance
    c.drawRect(skia.Rect.MakeLTRB(250, 150, 262, 250), paint(INK))
    c.drawRect(skia.Rect.MakeLTRB(818, 150, 830, 250), paint(INK))
    sv.label(c, "MATH OLYMPIAD", 540, 300, 64, fname="luckiest-guy-400", color=INK, bg=WHITE, edge=INK, tag="label", pad=22)
    sv.sfx(c, "POW!", 250, 560, 200, k=pop(T, tg + 3 / 24), rot=-12)
    if T > tg:
        cast._sparkle(c, 572, 1134, 44 + 12 * math.sin(twos(T) * 20), WHITE)
    return st.arr


# ------------------------------------------------------------------ 2. the clock

def clock_face(c, x, y, r, T, hands=(10 * 30 + 5, 60), wobble=0.0):
    c.drawCircle(x + 14, y + 16, r, paint(INK))
    c.drawCircle(x, y, r, paint((255, 250, 236)))
    c.drawCircle(x, y, r, paint(INK, stroke=14))
    f = sv.font("bangers-400", r * 0.24)
    for i in range(12):
        a = math.radians(i * 30 - 60)
        s = str(i + 1)
        c.drawString(s, x + r * 0.78 * math.cos(a) - f.measureText(s) / 2, y + r * 0.78 * math.sin(a) + r * 0.09, f, paint(INK))
    for i in range(60):
        a = math.radians(i * 6)
        L = 0.1 if i % 5 == 0 else 0.05
        sv.ink(c, [(x + r * (0.95 - L) * math.cos(a), y + r * (0.95 - L) * math.sin(a)), (x + r * 0.95 * math.cos(a), y + r * 0.95 * math.sin(a))],
               6 if i % 5 == 0 else 3, taper=(0.1, 0.1))
    hh, mm = hands
    for ang, L, w in ((hh + wobble * 20, 0.5, 20), (mm - wobble * 30, 0.75, 13)):
        a = math.radians(ang - 90)
        sv.ink(c, [(x, y), (x + r * L * math.cos(a), y + r * L * math.sin(a))], w, taper=(0.05, 0.3))
    sa = math.radians(twos(T) * 36 - 90)
    sv.ink(c, [(x, y), (x + r * 0.85 * math.cos(sa), y + r * 0.85 * math.sin(sa))], 5, color=RED, taper=(0.05, 0.05))
    c.drawCircle(x, y, 14, paint(INK))


def s_clock(T, t, d):
    st = sv.Stage(PAPER)
    c = st.c
    q1 = [(34, 70), (1046, 70), (1046, 700), (34, 780)]
    q2 = [(34, 812), (1046, 732), (1046, 1890), (34, 1890)]
    # panel 1: the clock on a cyan dot field
    c.save()
    c.clipPath(path(q1), doAntiAlias=True)
    c.drawColor(sv.col((120, 230, 255)))
    st.shade("mag").drawPath(path(q1), paint(WHITE, 0.25))
    st.c.restore()
    st.flush()
    c.save()
    c.clipPath(path(q1), doAntiAlias=True)
    k1 = pop(T, S("h2") - 0.05)
    c.save()
    c.translate(540, 420)
    c.scale(k1, k1)
    clock_face(c, 0, 0, 280, T, wobble=0.25 * math.sin(twos(T) * 7) if T > C["thirteen"] else 0.0)
    c.restore()
    c.restore()
    # panel 2: the bot, stumped
    k2 = ramp(T, C["clock"] - 0.2, C["clock"] + 0.1)
    if k2 > 0:
        c.save()
        c.clipPath(path(q2), doAntiAlias=True)
        c.drawColor(sv.col((255, 214, 90)))
        c.drawCircle(540, 1150, 520, paint((255, 238, 160)))
        P = st.pen()
        wrong = T >= C["thirteen"] + 0.55
        cast.bot(P, 330 + 200 * (1 - ease(k2)), 1060, 1.3, T, talk=talk(T, BOT), look=(0.6, -0.8),
                 expr="confused" if not talk(T, BOT) > 0.1 else "happy", arms=((210, 60), (-110, -40)), eyes_x=wrong, bounce=0.4)
        for j in range(2):                                        # sweat drops, on twos
            yy = 800 + ((twos(T) * 90 + j * 60) % 120)
            c.drawPath(path([(520 + j * 44, yy - 26), (536 + j * 44, yy + 4), (504 + j * 44, yy + 4)]), paint((90, 200, 255)))
            c.drawCircle(520 + j * 44, yy + 4, 16, paint((90, 200, 255)))
            c.drawCircle(520 + j * 44, yy + 4, 16, paint(INK, stroke=4))
        c.restore()
        st.flush()
    sv.panel_border(c, q1)
    if k2 > 0:
        sv.panel_border(c, q2)
    if S("h3") - 0.1 <= T < E("h3") + 0.4:
        sv.bubble(c, "Is it… 13 o’clock?", 790, 930, tail=(540, 1000), size=54, k=pop(T, S("h3") - 0.1), maxw=380)
    if T >= C["thirteen"] + 0.55:
        sv.sfx(c, "BZZT!", 790, 1190, 170, k=pop(T, C["thirteen"] + 0.55), rot=8, fill=RED, fill2=(150, 0, 40), dots=YEL)
    return st.arr


# ------------------------------------------------------------------ 3. the question (our dimension)

def rooftop(st, T, y=1320):
    c = st.c
    P = st.pen()
    ledge = path([(0, y), (sv.W, y - 30), (sv.W, sv.H), (0, sv.H)])
    P.fill(ledge, (84, 30, 110))
    P.sh["dot"].drawPath(ledge, paint(WHITE, 0.35))
    c.drawPath(path([(0, y), (sv.W, y - 30), (sv.W, y), (0, y + 30)]), paint((150, 60, 170)))
    sv.outline(c, path([(0, y), (sv.W, y - 30), (sv.W, y), (0, y + 30)]), 7)


def s_hookq(T, t, d):
    st = sv.Stage()
    bg.city(st, camx=40 * t, T=T)
    rooftop(st, T)
    st.flush()
    P = st.pen()
    tk = C["shake"]
    keys = [(0, "idle"), (tk, "shake"), (tk + 0.55, "point")]
    shake = 1.0 if tk <= twos(T) < tk + 0.55 else 0.0
    cast.hero(P, 470, 760, 1.28, T, talk=talk(T), arms=cast.arm_pose(T, keys), look=(0.5, 0.0), shake=shake,
              expr="wow" if T > tk + 0.55 else "neutral", smear_from=cast.arm_pose(T - 1 / 12, keys))
    st.flush()
    c = st.c
    if shake:
        sv.sfx(c, "SHAKA", 860, 520, 110, k=pop(T, tk), rot=10, fill=CYAN, fill2=(0, 130, 220), dots=WHITE)
        sv.sfx(c, "SHAKA", 790, 740, 90, k=pop(T, tk + 0.17), rot=-6, fill=CYAN, fill2=(0, 130, 220), dots=WHITE)
    if T < tk:
        sv.bubble(c, "?", 860, 380, tail=(700, 520), size=90, k=pop(T, S("h4") + 0.2), kind="thought", maxw=200)
    return st.arr


# ------------------------------------------------------------------ 4. the road of intelligence

STATIONS = ["CALCULATOR", "NARROW AI", "DEEP LEARNING", "FOUNDATION MODELS", "MULTIMODAL", "REASONING", "AGENTS", "AGI", "SUPERINTELLIGENCE"]
STX = [760 + i * 720 for i in range(9)]
ROAD_Y = 560                                   # road stripe height on the wall (wall coordinates)
WALL_Y0 = 330                                  # screen y of the wall top at zoom 1
LABEL_DY = -250
HERO_S = 0.6
HERO_HEAD = 1000 - 880 * HERO_S                # head centre (wall coords) so the feet stand on the sidewalk
SCOL = [(255, 240, 120), (255, 150, 60), MAG, (180, 90, 255), CYAN, LIME, (255, 90, 90), WHITE, WHITE]
PIN_X = STX[5] + 0.5 * (STX[6] - STX[5])


def road_y(x):
    return ROAD_Y + 26 * math.sin(x / 420.0)


def station_icon(c, i, x, y, k):
    """Small spray-stencil icons inside the road nodes."""
    c.save()
    c.translate(x, y)
    c.scale(k, k)
    if i == 0:                                             # calculator
        c.drawRoundRect(skia.Rect.MakeLTRB(-34, -46, 34, 46), 10, 10, paint(INK))
        c.drawRect(skia.Rect.MakeLTRB(-24, -36, 24, -14), paint((150, 255, 170)))
        for r in range(3):
            for q in range(3):
                c.drawRect(skia.Rect.MakeXYWH(-24 + q * 17, -6 + r * 16, 13, 12), paint(WHITE))
    elif i == 1:                                           # narrow AI: a chess knight-ish target
        for rr, cc in ((40, WHITE), (28, INK), (16, WHITE), (6, INK)):
            c.drawCircle(0, 0, rr, paint(cc))
    elif i == 2:                                           # deep learning: a little network
        pts = [(-34, -26), (-34, 0), (-34, 26), (0, -14), (0, 14), (34, 0)]
        for a in pts[:3]:
            for b in pts[3:5]:
                sv.ink(c, [a, b], 4, taper=(0.1, 0.1))
        for b in pts[3:5]:
            sv.ink(c, [b, pts[5]], 4, taper=(0.1, 0.1))
        for p in pts:
            c.drawCircle(p[0], p[1], 8, paint(WHITE))
            c.drawCircle(p[0], p[1], 8, paint(INK, stroke=4))
    elif i == 3:                                           # foundation models: a stack
        for j in range(4):
            c.drawRoundRect(skia.Rect.MakeLTRB(-38, 24 - j * 18, 38, 38 - j * 18), 6, 6, paint([MAG, CYAN, YEL, WHITE][j]))
            c.drawRoundRect(skia.Rect.MakeLTRB(-38, 24 - j * 18, 38, 38 - j * 18), 6, 6, paint(INK, stroke=4))
    elif i == 4:                                           # multimodal: eye + speech
        c.drawOval(skia.Rect.MakeLTRB(-40, -22, 40, 22), paint(WHITE))
        c.drawCircle(0, 0, 13, paint(INK))
        c.drawOval(skia.Rect.MakeLTRB(-40, -22, 40, 22), paint(INK, stroke=5))
    elif i == 5:                                           # reasoning: a lightbulb
        c.drawCircle(0, -8, 26, paint(YEL))
        c.drawCircle(0, -8, 26, paint(INK, stroke=5))
        c.drawRect(skia.Rect.MakeLTRB(-12, 18, 12, 36), paint(INK))
    elif i == 6:                                           # agents: a cursor arrow
        c.drawPath(path([(-18, -34), (22, 4), (4, 6), (14, 30), (4, 34), (-6, 10), (-18, 22)]), paint(WHITE))
        c.drawPath(path([(-18, -34), (22, 4), (4, 6), (14, 30), (4, 34), (-6, 10), (-18, 22)]), paint(INK, stroke=5))
    else:                                                  # AGI / ASI: not painted yet
        f = sv.font("bangers-400", 70)
        c.drawString("?", -f.measureText("?") / 2, 26, f, paint(WHITE))
    c.restore()


def draw_road(c, T, reveal, st_alpha=1.0, zoom=1.0, labels=True):
    """The road stripe and its stations in wall coordinates. reveal[i] = 0..1 spray progress of station i."""
    last = max([i for i in range(9) if reveal[i] > 0] or [0])
    x_end = STX[last] + 60 if reveal[last] >= 1 or last == 0 else STX[last - 1] + (STX[last] - STX[last - 1]) * reveal[last]
    xs = np.linspace(STX[0] - 260, min(x_end, STX[6]), 80)
    for j, (dy, col) in enumerate(((-26, MAG), (0, YEL), (26, CYAN))):
        pts = [(x, road_y(x) + dy) for x in xs]
        if len(pts) > 1:
            sv.spray_stroke(c, pts, 30, col, seed=40 + j)
    if x_end > STX[6]:                                     # beyond agents: chalky dashed outline, not painted yet
        xe = np.linspace(STX[6], min(x_end, STX[8] + 200), 60)
        for k0 in range(0, len(xe) - 1, 4):
            seg = [(x, road_y(x)) for x in xe[k0:k0 + 3]]
            sv.ink(c, seg, 10, color=WHITE, taper=(0.3, 0.3), a=0.8)
    for i in range(9):
        k = reveal[i]
        if k <= 0:
            continue
        x, y = STX[i], road_y(STX[i])
        kk = min(1.0, k * 1.6)
        if i < 7:
            c.drawCircle(x + 8, y + 10, 78 * kk, paint(INK))
            c.drawCircle(x, y, 78 * kk, paint(SCOL[i]))
            c.drawCircle(x, y, 78 * kk, paint(INK, stroke=9))
        else:
            c.drawCircle(x, y, 78 * kk, paint(WHITE, 0.18))
            c.drawCircle(x, y, 78 * kk, paint(WHITE, 0.85, stroke=6))
            c.drawCircle(x, y, 110 * kk, paint(CYAN, 0.35, blur=24))
        station_icon(c, i, x, y, kk)
        size = 104 if len(STATIONS[i]) < 11 else (84 if len(STATIONS[i]) < 16 else 72)
        if not labels:
            continue
        if i < 7:
            sv.tag_text(c, STATIONS[i], x, y + LABEL_DY + (30 if i % 2 else 0), size, fill=SCOL[i], fill2=sv.darker(SCOL[i], 0.65),
                        rot=-5 + (i % 3) * 4, seed=i, prog=min(1.0, k), tag="station")
        else:                                             # not painted yet: chalk outline lettering
            p_, w_ = sv.text_path(STATIONS[i], "permanent-marker-400", size)
            b_ = p_.getBounds()
            c.save()
            c.translate(x - w_ / 2, y + LABEL_DY + 30)
            c.drawPath(p_, paint(WHITE, 0.95 * min(1.0, k), stroke=5))
            sv.reg_local(c, b_.left(), b_.top(), b_.right(), b_.bottom(), "station")
            c.restore()


def pin(c, x, y, k, s=1.0, T=0.0):
    """The 'you are here' marker: a map pin and a sign board, slammed onto the wall."""
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(s * k, s * k)
    c.drawPath(path([(0, 0), (-50, -110), (50, -110)]), paint(RED))
    c.drawCircle(0, -140, 66, paint(RED))
    c.drawCircle(0, -140, 26, paint(WHITE))
    c.drawPath(path(np.vstack([sv.ellipse(0, -140, 66, 66, 40)[20:], [(0, 0)]])), paint(INK, stroke=9))
    c.drawCircle(-20, -164, 12, paint(WHITE, 0.8))
    board = skia.Rect.MakeLTRB(-190, -470, 190, -330)
    sv.ink(c, [(0, -330), (0, -206)], 12)
    c.drawRect(board.makeOffset(10, 12), paint(INK))
    c.drawRect(board, paint(YEL))
    c.drawRect(board, paint(INK, stroke=8))
    f = sv.font("bangers-400", 62)
    for j, s_ in enumerate(("YOU ARE", "HERE")):
        c.drawString(s_, -f.measureText(s_) / 2, -410 + j * 62, f, paint(INK))
    sv.reg_local(c, -190, -470, 200, -330, "pin")
    c.restore()


def _cam_walk(T):
    ts = C["stations"]
    cx = 0.0
    for i, tw in enumerate(ts):
        target = STX[i] - 640
        k = ease(ramp(T, tw - 0.3, tw + 0.15 if i < 7 else tw + 0.3))
        if k > 0:
            cx = cx + (target - cx) * k
    return max(0.0, cx)


def road_view(T):
    """Camera on the wall: (centre x, centre y) in wall coordinates and zoom, eased on ones."""
    cy1 = 860 - WALL_Y0
    if T < S("r4") - 0.15:
        return _cam_walk(T) + 540, cy1, 1.0
    far = STX[8] - 640 + 540
    back = PIN_X - 620 + 540
    k = ease(ramp(T, S("r4") - 0.15, S("r4") + 0.15))
    cx = far + (back - far) * k
    # pull back (readable), then whip back down the road to where it started
    zk = ease(ramp(T, S("r5") + 0.3, S("r5") + 1.3))
    zoom = 1.0 + (0.5 - 1.0) * zk
    cx = cx + (PIN_X - cx) * zk
    cy = cy1 + (ROAD_Y - 80 - cy1) * zk
    wk = ease(ramp(T, W("r5", "Way") - 0.35, W("r5", "Way") + 0.35))
    cx = cx + (STX[1] + 560 - cx) * wk
    return cx, cy, zoom


def hero_wx(T):
    ts = C["stations"]
    if T < ts[0] - 0.3:
        return 140 + 190 * ease(ramp(T, S("r1"), ts[0] - 0.3))
    if T < ts[7] - 0.3:
        return _cam_walk(T) + 330
    if T < S("r4") - 0.15:
        return _cam_walk(ts[7] - 0.3) + 330
    return PIN_X - 330


def s_road(T, t, d):
    st = sv.Stage()
    cwx, cwy, zoom = road_view(T)
    camx = cwx - 540
    whip = S("r4") - 0.15 <= T < S("r4") + 0.2 or W("r5", "Way") - 0.3 <= T < W("r5", "Way") + 0.3
    bg.city(st, camx=camx * 0.6, T=T, mid=True, train=False, camy=(1 - zoom) * -300)
    ts = C["stations"]
    reveal = [ramp(T, tw - 0.1, tw + 0.45) for tw in ts]
    P = st.pen()
    c = st.c
    P.save()
    P.translate(540, 860)
    P.scale(zoom, zoom)
    P.translate(-cwx, -cwy)
    c.drawRect(skia.Rect.MakeLTRB(-3000, bg.WALL_H + 600, bg.WALL_W + 3000, bg.WALL_H + 5000), paint((34, 12, 46)))
    c.drawImage(bg._cached("wall", bg._paint_wall), 0, 0)
    draw_road(c, T, reveal)
    k = ramp(T, W("r5", "Way") - 0.1, W("r5", "Way") + 0.5)
    if k > 0:                                                # the distance already covered, sprayed along the road
        xs = np.linspace(STX[1], PIN_X - 150, 50)
        pts = [(x, road_y(x) + 170) for x in xs]
        n = max(2, int(len(pts) * k))
        sv.spray_stroke(c, pts[:n], 34, WHITE, seed=77)
        if k >= 1:
            ay = road_y(PIN_X) + 170
            c.drawPath(path([(PIN_X - 190, ay - 70), (PIN_X - 60, ay), (PIN_X - 190, ay + 70)]), paint(WHITE))
    kp = pop(T, C["pin"], 0.3)
    if T >= C["pin"]:
        pin(c, PIN_X, road_y(PIN_X) - 50, kp, s=1.0 / max(zoom, 0.5) ** 0.6, T=T)
    # the writer: walks the wall with the camera (legs on twos), sprays each station, stays behind when the camera flies on
    if not whip:
        hx = hero_wx(T)
        moving = abs(hero_wx(T) - hero_wx(T - 1 / 12)) > 3
        painting = any(tw - 0.1 <= twos(T) < tw + 0.5 for tw in ts[:7])
        pose = "spray" if painting else ("point_up" if T >= C["pin"] else "idle")
        ph = twos(T) * 2 * math.pi * 1.7 if moving else 0.35
        n_on = sum(1 for tw in ts if tw <= T)
        look = (0.8, -0.3) if T < C["pin"] else (0.9, -0.6)
        cast.hero(P, hx, HERO_HEAD, HERO_S, T, talk=talk(T), arms=cast.ARM[pose], legs=ph,
                  spray=SCOL[max(0, n_on - 1)] if painting else None, look=look,
                  expr="wow" if C["pin"] <= T < C["pin"] + 1.2 else "neutral")
    P.restore()
    st.flush()
    if not whip and C["pin"] <= T < C["pin"] + 1.6:
        m = c.getTotalMatrix()
        hs = (hero_wx(T) - cwx) * zoom + 540, (HERO_HEAD - cwy) * zoom + 860
        sv.spidey(c, hs[0] + 6 * zoom, hs[1] - 40 * zoom, 150 * zoom, T, k=ease(ramp(T, C["pin"], C["pin"] + 0.25)), seed=2)
    if whip:
        sv.motion_lines(c, 0, 200, sv.W, 1300, T, n=40, color=WHITE, w=10, seed=7)
    if C["pin"] <= T < C["pin"] + 0.45:
        sv.sfx(c, "THWIP!", 820, 1110, 150, k=pop(T, C["pin"]), rot=-10, fill=WHITE, fill2=CYAN, dots=MAG)
    if T > W("r5", "Way") + 0.3:
        sv.label(c, "WE CAME THIS FAR", 520, 1240, 70, fname="bangers-400", color=INK, bg=YEL, edge=INK, rot=-3,
                 a=ease(ramp(T, W("r5", "Way") + 0.3, W("r5", "Way") + 0.6)))
    return st.arr


def s_pin_impact(T):
    return impact(T, MAG, lambda P: pin(P.c, 540, 1180, 1.0, s=1.6), cx=540, cy=900, line=INK)


# ------------------------------------------------------------------ 5. how fast

DW, DH = 1012, 1300                                   # a panel's design space; panels are cropped, never re-laid out
PLACED = {}
LAST_PLACE = [(0.0, 0.0, 1.0)]


def place(st, P, r, focus, fn, T, bg_col, dh=DH, shade=None):
    """Draw panel content fn(st, P, T) (design space DW x dh) into screen rect r: whole ('contain') while the panel
    is big, cropped about a focus point ('cover') once it's squeezed into a strip."""
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    if h / dh >= 0.55:
        s = min(w / DW, h / dh)
        tx, ty = x0 + (w - DW * s) / 2, y0 + (h - dh * s) / 2
    else:
        s = max(w / DW, h / dh)
        tx = x0 + w / 2 - focus[0] * s
        ty = y0 + h / 2 - focus[1] * s
        tx = min(x0, max(x1 - DW * s, tx))
        ty = min(y0, max(y1 - dh * s, ty))
    q = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    P.save()
    P.clip(path(q))
    P.c.drawColor(sv.col(bg_col))
    if shade is not None:
        P.sh[shade[0]].drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(shader=sv.lin((0, y0), (0, y1), [(255, 255, 255, 0.0), (255, 255, 255, shade[1])])))
    P.translate(tx, ty)
    P.scale(s)
    fn(st, P, T)
    P.restore()
    PLACED[id(fn) if not hasattr(fn, "__name__") else fn.__name__] = (tx, ty, s)
    LAST_PLACE[0] = (tx, ty, s)
    return q


def _speed_a(st, P, T):
    c = P.c
    sv.motion_lines(c, 0, 40, DW, DH - 40, T, n=40, color=WHITE, w=16, seed=3)
    s = 1.25
    bx = -260 + 1600 * ramp(twos(T), S("s1") - 0.25, S("s1") + 1.3)
    by = 620
    for j in (3, 2, 1):                                     # multiples: earlier drawings of the bot trail behind it
        gx = bx - j * 150 * s
        c.drawRoundRect(skia.Rect.MakeLTRB(gx - 110 * s, by - 180 * s, gx + 110 * s, by + 160 * s), 50 * s, 50 * s, paint(WHITE, 0.25 + 0.12 * (3 - j)))
    cast.bot(P, bx, by, s, T, arms=((170, -60), (10, 60)), bounce=0.0, legs=True)
    board = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(bx - 140 * s, by + 262 * s, bx + 140 * s, by + 296 * s), 16, 16)
    c.drawRRect(board, paint(ORANGE))
    c.drawRRect(board, paint(INK, stroke=6))
    for wx in (-90, 90):
        c.drawCircle(bx + wx * s, by + 312 * s, 22 * s, paint(WHITE))
        c.drawCircle(bx + wx * s, by + 312 * s, 22 * s, paint(INK, stroke=5))
    sv.sfx(c, "ZOOM!", 730, 300, 150, k=pop(T, C["speed"]), rot=-6, fill=YEL, fill2=ORANGE, dots=MAG, pen=P)


def _speed_b(st, P, T):
    c = P.c
    sv.label(c, "HOW LONG A TASK AI AGENTS", DW / 2, 150, 62, fname="bangers-400", color=WHITE, pen=P)
    sv.label(c, "CAN FINISH ALONE", DW / 2, 222, 62, fname="bangers-400", color=YEL, pen=P)
    heights = [2 ** (i * 0.62) for i in range(9)]
    kb = ramp(T, S("s2") + 0.3, C["doubled"] + 0.4)
    base, top = 1110, 560
    for i, hgt in enumerate(heights):
        ki = ease(min(1.0, max(0.0, kb * 9 - i)))
        if ki <= 0:
            continue
        bh = (base - top) * hgt / heights[-1] * ki + 6
        x = 80 + i * 100
        rr = skia.Rect.MakeLTRB(x, base - bh, x + 72, base)
        c.drawRect(rr.makeOffset(8, 8), paint(INK))
        c.drawRect(rr, paint([CYAN, MAG, YEL][i % 3]))
        c.drawRect(rr, paint(INK, stroke=5))
    sv.label(c, "SECONDS", 120, base + 60, 46, fname="bangers-400", color=WHITE, pen=P)
    sv.label(c, "HOURS", 890, base + 60, 46, fname="bangers-400", color=WHITE, pen=P)
    sv.label(c, "2019", 120, base + 106, 34, fname="comic-neue-700", color=(220, 210, 255), pen=P)
    sv.label(c, "2025", 890, base + 106, 34, fname="comic-neue-700", color=(220, 210, 255), pen=P)
    sv.label(c, "METR · tasks finished half the time", DW / 2, base + 160, 30, fname="comic-neue-700", color=(220, 210, 255), tag="credit", pen=P)
    if T > C["doubled"]:
        sv.sfx(c, "x2 EVERY ~7 MONTHS", 420, 440, 84, k=pop(T, C["doubled"]), rot=-4, fill=YEL, fill2=ORANGE, dots=MAG, pen=P)


def _speed_c(st, P, T):
    c = P.c
    sv.label(c, "REAL COMPUTER TASKS", DW / 2, 150, 80, fname="bangers-400", color=INK, pen=P)
    sv.label(c, "OSWORLD · AI AGENTS", DW / 2, 220, 44, fname="bangers-400", color=WHITE, pen=P)
    val = 12 + (66.3 - 12) * ease(ramp(T, C["sixty"] - 0.35, C["sixty"] + 0.3))
    bx0, bx1, by = 60, 950, 420
    hx = bx0 + (bx1 - bx0) * 0.724
    sv.label(c, "HUMANS ~72%", hx, by - 46, 48, fname="bangers-400", color=INK, pen=P)
    c.drawRoundRect(skia.Rect.MakeLTRB(bx0, by, bx1, by + 110), 26, 26, paint(WHITE))
    if T >= C["twelve"] - 0.2:
        c.drawRoundRect(skia.Rect.MakeLTRB(bx0, by, bx0 + (bx1 - bx0) * val / 100, by + 110), 26, 26, paint(MAG))
        P.sh["dot"].drawRoundRect(skia.Rect.MakeLTRB(bx0, by + 55, bx0 + (bx1 - bx0) * val / 100, by + 110), 26, 26, paint(WHITE, 0.4))
    c.drawRoundRect(skia.Rect.MakeLTRB(bx0, by, bx1, by + 110), 26, 26, paint(INK, stroke=8))
    sv.ink(c, [(hx, by - 22), (hx, by + 140)], 12, color=INK)
    if T >= C["twelve"] - 0.2:
        sv.sfx(c, f"{int(round(val))}%", DW / 2 - 60, 760, 250, k=pop(T, C["twelve"] - 0.2), rot=-6,
               fill=YEL if val < 60 else WHITE, fill2=ORANGE if val < 60 else YEL, dots=MAG)
    sv.label(c, "in one year · Stanford AI Index 2026", DW / 2, 1010, 34, fname="comic-neue-700", color=INK, tag="credit", pen=P)


def s_speed(T, t, d):
    """A page that builds: each new panel slides up and squeezes the one before into a strip."""
    st = sv.Stage(PAPER)
    c = st.c
    P = st.pen()
    tb, tc = S("s2") - 0.25, S("s3") - 0.25
    kb = ease(ramp(T, tb, tb + 0.35))
    kc = ease(ramp(T, tc, tc + 0.35))
    top, bot, gap = 40, 1340, 22
    quads = []
    if kc < 1:
        a1 = bot + (330 - bot) * kb
        a0 = top + (-400 - top) * kc
        a1 = a1 + (-40 - a1) * kc
        quads.append(place(st, P, (34, a0, 1046, a1), (DW / 2, 620), _speed_a, T, (255, 90, 170)))
    if kb > 0:
        b0 = (bot + gap) + (330 + gap - (bot + gap)) * kb
        b0 = b0 + (top - b0) * kc
        b1 = bot + (560 - bot) * kc
        quads.append(place(st, P, (34, b0, 1046, b1), (DW / 2, 780), _speed_b, T, (40, 16, 90), shade=("mag", 0.4)))
    if kc > 0:
        c0 = (bot + gap) + (560 + gap - (bot + gap)) * kc
        n_before = len(sv.TEXT)
        quads.append(place(st, P, (34, c0, 1046, bot), (DW / 2, 520), _speed_c, T, (0, 190, 240), dh=1060))
        # lettering on the panel underneath is hidden where this one covers it
        sv.TEXT[:n_before] = [b for b in sv.TEXT[:n_before] if not (b[3] > c0 and b[1] < bot)]
    st.flush()
    for q in quads:
        sv.panel_border(c, q)
    return st.arr
