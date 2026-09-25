"""Shots for chapters III-IV: inside the machine, the prediction mission."""
import math

import numpy as np
import skia

import gfx as G
from gfx import CX, H, W, ease, ramp
from cues import C
from scenes_a import hal_eye, intertitle, label, once, panel
from timeline import TL


def s_int3(arr, t, d, T):
    intertitle(arr, t, d, "INSIDE THE MACHINE", "III")


RECORDS = ["ENCYCLOPEDIA  VOL 12  P 311", "PAPER  PHYSICS  1905", "NOVEL  CHAPTER 4", "FORUM  THREAD 88213",
           "CODE  PARSER.PY  L 204", "LETTER  1864", "RECIPE  BREAD", "PATENT  US 174465", "POEM  STANZA 3",
           "NEWS  MARCH 1969", "TEXTBOOK  ALGEBRA  P 57", "MANUAL  PUMP  REV B", "SCRIPT  SCENE 12", "WIKI  PARIS"]


def s_db(arr, t, d, T):
    s = G.canvas_of(arr)
    f = G.font("michroma-400", 21)
    with s as c:
        panel(c, 90, 430, 900, 820, code="MEM", color=G.CYAN)
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(90, 470, 900, 770))
        off = (t * 420) % 52
        for i in range(-1, 18):
            y = 520 + i * 52 - off
            idx = int(t * 420 / 52) + i
            G.text(c, f"{(idx * 7919) % 10 ** 9:09d}", 130, y, f, color=G.CYAN, a=0.8, align="left", track=1)
            G.text(c, RECORDS[idx % len(RECORDS)], 380, y, f, color=G.WHITE, a=0.75, align="left", track=1)
        c.restore()
        k = ease(ramp(T, TL.word("myth", "not") - 0.05, TL.word("myth", "not") + 0.25))
        if k > 0:
            c.drawRect(skia.Rect.MakeXYWH(90, 430, 900, 820), G.paint((0, 0, 0), 0.55 * k))
            c.drawLine(140, 1210, 940, 480, G.paint(G.HAL, k, stroke=10))
            G.text(c, "NOT A DATABASE", CX, 870, G.font("jost-500", 84), color=G.HAL, a=k, track=8,
                   glow=14 * k, glow_color=G.HAL)
        label(c, t, ["OPENAI: NO STORED COPIES", "(SOME TEXT CAN BE MEMORIZED)"])


def s_memory(arr, t, d, T):
    """HAL's Logic Memory Center: a red corridor of glowing modules. Each module is 'a number'."""
    s = G.canvas_of(arr)
    vx, vy = CX, 800
    z0 = (t * 0.55) % 1.0
    with s as c:
        c.drawRect(skia.Rect.MakeXYWH(0, 0, W, H), G.paint((18, 2, 2)))
        for i in range(16, -1, -1):
            za = i + 1 - z0
            if za <= 0.08:
                continue
            fog = 1 / (1 + 0.22 * za)

            def pr(u, v, z):
                return vx + u * 620 / z, vy + v * 620 / z
            for side in (-1, 1):
                for row in range(5):
                    v0 = -1.5 + row * 0.62
                    a1, b1 = pr(side * 1.0, v0 + 0.08, za + 0.12)
                    a2, b2 = pr(side * 1.0, v0 + 0.5, za + 0.82)
                    x0_, x1_ = sorted((a1, a2))
                    # modules are thin glass plates seen edge-on: draw as a trapezoid
                    p = skia.Path()
                    ta, tb = pr(side * 1.0, v0 + 0.08, za + 0.12)
                    tc, td = pr(side * 1.0, v0 + 0.08, za + 0.82)
                    te, tf = pr(side * 1.0, v0 + 0.5, za + 0.82)
                    tg, th = pr(side * 1.0, v0 + 0.5, za + 0.12)
                    p.moveTo(ta, tb)
                    p.lineTo(tc, td)
                    p.lineTo(te, tf)
                    p.lineTo(tg, th)
                    p.close()
                    flick = 0.75 + 0.25 * math.sin(i * 3.1 + row * 1.7 + t * 2.0)
                    c.drawPath(p, G.paint((255, 60 + 60 * (row % 2), 50), 0.55 * fog * flick))
                    c.drawPath(p, G.paint((255, 200, 180), 0.8 * fog, stroke=1.4))
            # floor & ceiling edges
            for v in (-1.6, 1.6):
                a1, b1 = pr(-1, v, za)
                a2, b2 = pr(1, v, za)
                c.drawLine(a1, b1, a2, b2, G.paint((120, 20, 20), fog, stroke=2))
    G.add_light(arr, G.radial(vx, vy, 260, (255, 40, 20), 0.45, 1.5))
    s = G.canvas_of(arr)
    with s as c:
        k = ease(ramp(T, TL.word("params", "billions") - 0.1, TL.word("params", "billions") + 0.3))
        c.drawRect(skia.Rect.MakeXYWH(0, 700, W, 250), G.paint((0, 0, 0), 0.55 * k))
        G.text(c, "175,000,000,000", CX, 830, G.font("jost-300", 104), a=k, track=4)
        G.text(c, "ADJUSTABLE NUMBERS · “PARAMETERS”", CX, 900, G.font("michroma-400", 22), color=(255, 180, 160), a=k, track=4)
        label(c, t, ["GPT-3 · 2020"], color=(255, 150, 120))


VEC = [("CHINA", "BEIJING"), ("JAPAN", "TOKYO"), ("FRANCE", "PARIS"), ("ITALY", "ROME"), ("GERMANY", "BERLIN"),
       ("SPAIN", "MADRID")]


def s_vectors(arr, t, d, T):
    s = G.canvas_of(arr)
    f = G.font("jost-500", 32)
    with s as c:
        panel(c, 70, 430, 940, 820, code="VEC", color=G.CYAN)
        x0, y0, w, h = 110, 500, 860, 720
        for gx in range(9):
            c.drawLine(x0 + gx * w / 8, y0, x0 + gx * w / 8, y0 + h, G.paint((30, 60, 90), 0.6, stroke=1))
        for gy in range(9):
            c.drawLine(x0, y0 + gy * h / 8, x0 + w, y0 + gy * h / 8, G.paint((30, 60, 90), 0.6, stroke=1))
        t_yet = TL.word("capitals", "inside")
        rule_a = ease(ramp(t, 0.05, 0.3)) * (1 - ease(ramp(T, t_yet - 0.2, t_yet + 0.1)))
        if rule_a > 0:
            c.drawRect(skia.Rect.MakeXYWH(150, 760, 780, 190), G.paint((0, 0, 0), 0.9 * rule_a))
            G.text(c, "NO RULE ABOUT CAPITALS", CX, 845, G.font("jost-500", 46), a=rule_a, track=4)
            G.text(c, "WAS EVER PROGRAMMED", CX, 905, G.font("jost-500", 46), color=G.HAL, a=rule_a, track=4)
        pts_a = ease(ramp(T, t_yet - 0.1, t_yet + 0.4))
        when = {"FRANCE": TL.word("capitals", "Paris"), "JAPAN": TL.word("capitals", "Tokyo")}
        rest = TL.word("capitals", "Japan") + 0.3
        for i, (co, ca) in enumerate(VEC):
            yc = y0 + 80 + i * 112 + (i % 2) * 12
            xc = x0 + 190 + (i % 3) * 12
            xk, yk = xc + 400, yc - 46
            c.drawCircle(xc, yc, 10, G.paint(G.CYAN, pts_a))
            c.drawCircle(xk, yk, 9, G.paint(G.AMBER, pts_a))
            G.text(c, co.title(), xc - 20, yc + 11, f, color=G.CYAN, a=pts_a, align="right")
            G.text(c, ca.title(), xk + 20, yk + 11, f, color=G.AMBER, a=pts_a, align="left")
            ta = when.get(co, rest + 0.12 * i)
            k = ease(ramp(T, ta, ta + 0.45))
            if k > 0:
                ex, ey = xc + (xk - xc) * k, yc + (yk - yc) * k
                hl = co in when
                col = G.WHITE if hl else (140, 170, 200)
                c.drawLine(xc, yc, ex, ey, G.paint(col, 0.95, stroke=4 if hl else 2.5))
                ang = math.atan2(yk - yc, xk - xc)
                for s_ in (-1, 1):
                    c.drawLine(ex, ey, ex - 22 * math.cos(ang + s_ * 0.45), ey - 22 * math.sin(ang + s_ * 0.45),
                               G.paint(col, 0.95 * k, stroke=4 if hl else 2.5))
        label(c, t, ["SAME ARROW = SAME RELATION", "MIKOLOV 2013 · HERNANDEZ 2024"])


def _galaxy_pts():
    rng = np.random.default_rng(71)
    groups = []
    centers = [(-0.75, -0.62, 0.0), (0.75, -0.62, 0.0), (-0.75, 0.62, 0.0), (0.75, 0.62, 0.0)]
    cols = [(0.75, 0.85, 1.0), (0.45, 1.0, 0.65), (1.0, 0.75, 0.35), (1.0, 0.35, 0.3)]
    P, Cl = [], []
    for (cx, cy, cz), col in zip(centers, cols):
        n = 2600
        p = rng.normal(0, 0.26, (n, 3)) + np.array([cx, cy, cz])
        P.append(p)
        Cl.append(np.tile(col, (n, 1)))
    bg = rng.uniform(-1.8, 1.8, (2500, 3))
    P.append(bg)
    Cl.append(np.tile((0.55, 0.58, 0.65), (2500, 1)))
    return np.concatenate(P).astype(np.float32), np.concatenate(Cl).astype(np.float32), centers


def s_galaxy(arr, t, d, T):
    P, Cl, centers = once("gal", _galaxy_pts)
    a = 0.10 + t * 0.05
    ca, sa = math.cos(a), math.sin(a)
    x = P[:, 0] * ca + P[:, 2] * sa
    z = -P[:, 0] * sa + P[:, 2] * ca + 3.4 - t * 0.12
    y = P[:, 1]
    f = 760
    sx = (CX + x / z * f).astype(int)
    sy = (820 + y / z * f).astype(int)
    ok = (sx >= 1) & (sx < W - 1) & (sy >= 1) & (sy < H - 1) & (z > 0.3)
    light = np.zeros((H, W, 3), np.float32)
    br = (3.2 / z[ok])[:, None] * Cl[ok]
    np.add.at(light, (sy[ok], sx[ok]), br)
    np.add.at(light, (sy[ok] + 1, sx[ok]), br * 0.4)
    np.add.at(light, (sy[ok], sx[ok] + 1), br * 0.4)
    np.add.at(light, (sy[ok] + 1, sx[ok] + 1), br * 0.25)
    from scipy import ndimage
    light += ndimage.gaussian_filter(light, (5, 5, 0)) * 2.2
    G.add_light(arr, light)
    s = G.canvas_of(arr)
    names = ["LANGUAGE", "CODE", "MATH", "CAUSE & EFFECT"]
    keys = ["language", "code", "math", "cause"]
    with s as c:
        for (cx, cy, cz), nm, kw in zip(centers, names, keys):
            xx = cx * ca + cz * sa
            zz = -cx * sa + cz * ca + 3.4 - t * 0.12
            px, py = CX + xx / zz * f, 820 + cy / zz * f
            k = ease(ramp(T, TL.word("map", kw) - 0.05, TL.word("map", kw) + 0.25))
            G.text(c, nm, px, py - 400 / zz, G.font("jost-500", 40), a=k, track=5, glow=8, glow_color=(0, 0, 0))
        label(c, t, ["A LEARNED MAP OF MEANING"])


def s_ae35(arr, t, d, T):
    img, al = once("hal_small", lambda: hal_eye(185, glow=1.0))
    G.over(arr, img, al, int(CX - 185), 420)
    G.add_light(arr, G.radial(CX, 605, 180, (255, 40, 10), 0.3, 2))
    s = G.canvas_of(arr)
    with s as c:
        panel(c, 110, 840, 860, 410, code="COM", color=G.HAL)
        f = G.font("michroma-400", 24)
        G.text(c, "AE-35 ANTENNA UNIT", CX, 925, G.font("michroma-400", 30), track=4)
        k1 = ease(ramp(t, 0.3, 0.6))
        G.text(c, "FAULT PREDICTED:", CX, 1000, G.font("jost-500", 38), color=G.HAL, a=k1, track=3)
        G.text(c, "100% FAILURE IN 72 HOURS", CX, 1050, G.font("jost-500", 38), color=G.HAL, a=k1, track=3)
        tr = TL.word("wrong", "rebuilds")
        k2 = ease(ramp(T, tr - 0.1, tr + 0.25))
        G.text(c, "TESTED: NO FAULT FOUND", CX, 1165, G.font("jost-500", 44), color=G.GREEN, a=k2, track=4)
        label(c, t, ["HAL, IN THE FILM:", "CONFIDENTLY WRONG"])


def s_int4(arr, t, d, T):
    intertitle(arr, t, d, "THE PREDICTION MISSION", "IV")


TOKS = ["The", "Earth", "revolves", "around", "the"]


def _sentence(c, t_reveal, y=560, blank="", blank_col=G.AMBER, blank_a=1.0):
    f = G.font("jost-400", 50)
    widths = [G.text_width(w, f) + 34 for w in TOKS]
    total = sum(widths) + 10 * len(TOKS) + 140
    x = CX - total / 2
    rows = []
    for i, w in enumerate(TOKS):
        k = ease(ramp(t_reveal, i * 0.2, i * 0.2 + 0.2))
        c.drawRoundRect(skia.Rect.MakeXYWH(x, y - 52, widths[i], 72), 8, 8, G.paint(G.CYAN, 0.15 * k))
        c.drawRoundRect(skia.Rect.MakeXYWH(x, y - 52, widths[i], 72), 8, 8, G.paint(G.CYAN, 0.8 * k, stroke=2))
        G.text(c, w, x + widths[i] / 2, y, f, a=k)
        x += widths[i] + 10
    c.drawRoundRect(skia.Rect.MakeXYWH(x, y - 52, 140, 72), 8, 8, G.paint(G.AMBER, 0.9, stroke=2.5))
    if blank:
        G.text(c, blank, x + 70, y, f, color=blank_col, a=blank_a)
    else:
        if int(t_reveal * 2.5) % 2 == 0:
            c.drawLine(x + 70, y - 38, x + 70, y + 8, G.paint(G.AMBER, 1, stroke=3))
    return x


def s_tokens(arr, t, d, T):
    s = G.canvas_of(arr)
    with s as c:
        panel(c, 40, 470, 1000, 480, code="TOK", color=G.CYAN)
        rv = T - (TL.s("token") + 1.9)
        _sentence(c, rv if rv > 0 else -1, y=620)
        k0 = ease(ramp(t, 0.1, 0.4)) * (1 - ease(ramp(rv, -0.3, 0.0)))
        G.text(c, "NEXT TOKEN?", CX, 740, G.font("jost-500", 72), color=G.AMBER, a=k0, track=8)
        k = ease(ramp(T, TL.word("token", "part") - 0.1, TL.word("token", "part") + 0.2))
        G.text(c, "RARER WORDS SPLIT:", CX, 790, G.font("jost-500", 34), color=G.GREY, a=k, track=3)
        G.text(c, "TOKEN | IZATION", CX, 860, G.font("jost-400", 56), color=G.WHITE, a=k, track=6)
        label(c, t, ["1 TOKEN ≈ 3/4 OF A WORD".replace("≈", "~")])


CANDS0 = [("ocean", 0.31), ("moon", 0.22), ("corner", 0.12), ("sun", 0.07), ("clock", 0.05)]
CANDS1 = [("sun", 0.93), ("moon", 0.03), ("ocean", 0.01), ("corner", 0.01), ("clock", 0.0)]


def s_predict(arr, t, d, T):
    s = G.canvas_of(arr)
    t_oc = TL.word("ocean", "Ocean")
    t_wr = TL.word("ocean", "Wrong")
    t_nu = TL.s("nudge")
    t_sun = C["sun"]
    morph = ease(ramp(T, t_nu + 0.3, t_sun - 0.1))
    with s as c:
        panel(c, 40, 440, 1000, 830, code="PRD", color=G.CYAN)
        if T < t_oc:
            blank, bc = "", G.AMBER
        elif T < t_sun:
            blank, bc = "ocean", G.HAL
        else:
            blank, bc = "Sun", G.AMBER
        _sentence(c, 5.0, y=560, blank=blank, blank_col=bc)
        f = G.font("jost-400", 40)
        fs = G.font("jost-500", 28)
        d0 = dict(CANDS0)
        d1 = dict(CANDS1)
        for i, (w_, _) in enumerate(CANDS0):
            p = d0[w_] * (1 - morph) + d1[w_] * morph
            y = 690 + i * 78
            G.text(c, w_, 250, y + 14, f, a=0.95, align="right")
            col = G.HAL if (w_ == "ocean" and T >= t_oc and morph < 0.5) else (G.AMBER if w_ == "sun" and morph > 0.5 else G.CYAN)
            c.drawRect(skia.Rect.MakeXYWH(280, y - 18, 640 * p, 40), G.paint(col, 0.9))
            G.text(c, f"{p * 100:.0f}%", 290 + 640 * p + 10, y + 12, fs, color=G.GREY, align="left")
        kw = ease(ramp(T, t_wr - 0.05, t_wr + 0.15)) * (1 - ease(ramp(T, t_nu, t_nu + 0.3)))
        if kw > 0:
            G.text(c, "WRONG", CX, 1190, G.font("jost-500", 84), color=G.HAL, a=kw, track=12, glow=12, glow_color=G.HAL)
        kd = ease(ramp(T, t_nu, t_nu + 0.3))
        if kd > 0:
            # a bank of dials, each nudged a little
            for j in range(18):
                cx_, cy_ = 190 + j * 41.0, 1170
                ang = -math.pi / 2 + 0.6 * math.sin(j * 1.9 + morph * 3.0)
                c.drawCircle(cx_, cy_, 17, G.paint(G.GREY, 0.6 * kd, stroke=2))
                c.drawLine(cx_, cy_, cx_ + 14 * math.cos(ang), cy_ + 14 * math.sin(ang), G.paint(G.WHITE, kd, stroke=2.5))
        label(c, t, ["GUESS · CHECK · ADJUST"])


def s_tilt(arr, t, d, T):
    G.stars(arr, a=0.7)
    sx, sy = CX, 900
    G.add_light(arr, G.radial(sx, sy, 34, (255, 250, 235), 2.0, 2) + G.radial(sx, sy, 160, (255, 220, 170), 0.4, 1.3))
    s = G.canvas_of(arr)
    with s as c:
        c.drawOval(skia.Rect.MakeXYWH(sx - 320, sy - 130, 640, 260), G.paint((120, 130, 150), 0.7, stroke=2))
    tilt = math.radians(23.4)
    for ex, name in ((sx - 320, "NORTHERN SUMMER"), (sx + 320, "NORTHERN WINTER")):
        dirx = (sx - ex) / abs(sx - ex)
        rgb, al, glow, off = once(f"tiltE{int(ex)}", lambda dirx=dirx: G.sphere(62, kind="earth", light=(dirx * 0.95, 0.0, 0.3),
                                                                             lon0=1.0, lat_tilt=0.0))
        G.over(arr, rgb, al, int(ex - off), int(sy - off))
        s = G.canvas_of(arr)
        with s as c:
            ax, ay = math.sin(tilt) * 110, -math.cos(tilt) * 110
            c.drawLine(ex - ax, sy - ay, ex + ax, sy + ay, G.paint(G.WHITE, 0.9, stroke=3))
            G.text(c, "N", ex + ax * 1.18, sy + ay * 1.18 - 4, G.font("michroma-400", 22), color=G.AMBER)
            k = ease(ramp(T, TL.s("tilt2"), TL.s("tilt2") + 0.3))
            G.text(c, name.split()[1], ex, sy + 175, G.font("jost-500", 32), color=G.AMBER if "SUMMER" in name else G.CYAN,
                   a=k, track=2)
    s = G.canvas_of(arr)
    with s as c:
        G.text(c, "…the north gets summer when", CX, 520, G.font("jost-400", 50), a=ease(ramp(t, 0, 0.3)))
        G.text(c, "it leans toward the Sun", CX, 590, G.font("jost-500", 50), color=G.AMBER,
               a=ease(ramp(T, TL.s("tilt2") - 0.05, TL.s("tilt2") + 0.2)))
        label(c, t, ["AXIAL TILT: 23.4°"])


_SG = {}


def s_stargate(arr, t, d, T):
    """Slit-scan corridor: two walls of streaming colour converging on a vanishing slit."""
    if "grid" not in _SG:
        dx = G._XX - CX
        dy = G._YY - 830
        side = np.abs(dx)
        z = 260.0 / np.maximum(side, 2.0)
        v = dy * z / 260.0
        _SG["grid"] = (z.astype(np.float32), v.astype(np.float32), (dx > 0))
        rng = np.random.default_rng(81)
        _SG["pal"] = rng.random((64, 3)).astype(np.float32)
        _SG["bands"] = rng.random(4096).astype(np.float32)
    z, v, right = _SG["grid"]
    u = z + t * 9.0
    band_idx = ((v * 9.0 + np.sin(u * 0.15) * 1.5 + right * 17).astype(np.int64)) % 4096
    b = _SG["bands"][band_idx]
    hue = (b * 0.7 + u * 0.004 + right * 0.3) % 1.0
    # vivid slit-scan palette: orange, magenta, blue, cyan, yellow
    pal = np.array([[1.0, 0.45, 0.05], [0.95, 0.1, 0.55], [0.2, 0.3, 1.0], [0.1, 0.9, 0.95], [1.0, 0.9, 0.2],
                    [1.0, 0.45, 0.05]], np.float32)
    hp = hue * 5
    i0 = hp.astype(int)
    fr = (hp - i0)[..., None]
    col = pal[i0] * (1 - fr) + pal[np.minimum(i0 + 1, 5)] * fr
    stripes = 0.55 + 0.45 * np.sin(v * 60 + b * 20)
    streak = 0.6 + 0.4 * np.sin(u * 0.9 + b * 30)
    fog = np.clip(1.6 / (1 + z * 0.35), 0, 1)
    wall = np.clip(np.abs(v) < 3.2, 0, 1)
    light = col * (stripes * streak * fog * wall)[..., None] * 1.1
    ramp_in = ease(ramp(t, 0, 0.5))
    arr[..., :3] = (np.clip(light * ramp_in, 0, 1) * 255).astype(np.uint8)
    s = G.canvas_of(arr)
    with s as c:
        k = ease(ramp(T, TL.s("llama") - 0.3, TL.s("llama") + 0.1))
        c.drawRect(skia.Rect.MakeXYWH(0, 700, W, 300), G.paint((0, 0, 0), 0.7 * k))
        n = ramp(T, TL.s("llama"), TL.word("llama", "tokens"))
        val = int(15e12 * ease(n))
        G.text(c, f"{val:,}", CX, 840, G.font("jost-300", 84), a=k, track=2)
        G.text(c, "TOKENS OF TRAINING TEXT", CX, 912, G.font("jost-500", 32), color=G.AMBER, a=k, track=4)
        k2 = ease(ramp(T, TL.word("llama", "Over", 1) - 0.1, TL.word("llama", "Over", 1) + 0.3))
        c.drawRect(skia.Rect.MakeXYWH(0, 1010, W, 150), G.paint((0, 0, 0), 0.7 * k2))
        G.text(c, "200,000+ YEARS OF READING", CX, 1080, G.font("jost-400", 48), a=k2, track=3)
        G.text(c, "AT 8 HOURS A DAY", CX, 1132, G.font("jost-500", 30), color=G.GREY, a=k2, track=4)
        label(c, T - TL.s("llama") + 0.3, ["META · LLAMA 3 · 2024"])


def _dots100k():
    """100,000 points in a 400 x 250 grid: the model's training words; one point is a child's."""
    light = np.zeros((H, W, 3), np.float32)
    xs = np.linspace(90, W - 90, 400)
    ys = np.linspace(420, 1230, 250)
    gx, gy = np.meshgrid(xs, ys)
    xi, yi = gx.astype(int).ravel(), gy.astype(int).ravel()
    np.add.at(light, (yi, xi), np.array([0.45, 0.85, 1.0], np.float32) * 1.4)
    return light


def s_childdata(arr, t, d, T):
    field = once("dots100k", _dots100k)
    reveal = ease(ramp(t, 0.0, 0.8))
    G.add_light(arr, field * reveal)
    s = G.canvas_of(arr)
    kc = ease(ramp(T, TL.word("childdata", "hundred") - 0.2, TL.word("childdata", "hundred") + 0.2))
    with s as c:
        c.drawRect(skia.Rect.MakeXYWH(0, 400, W, 850), G.paint((0, 0, 0), 0.8 * kc))
        x, y = CX + 3, 826
        c.drawCircle(x, y, 26, G.paint(G.AMBER, 0.55 * kc, blur=10))
        c.drawCircle(x, y, 5, G.paint(G.AMBER, kc))
        G.text(c, "A CHILD", x, y - 52, G.font("jost-500", 40), color=G.AMBER, a=kc, track=4)
        G.text(c, "100,000 DOTS: ONE MODEL'S TRAINING TEXT", CX, 1300 - 40, G.font("jost-500", 30), color=G.CYAN,
               a=(1 - kc) * reveal, track=2)
        label(c, t, ["1 DOT = A CHILD'S WORDS", "FRANK, 2023 · META, 2024"])


def s_earth(arr, t, d, T):
    G.stars(arr, a=0.8)
    R = 420
    lon = 0.4 + t * 0.06
    G.put_sphere(arr, CX, 830, R, kind="earth", light=(-0.55, 0.35, 0.76), lon0=lon, lat_tilt=0.35, cloud_shift=t * 0.004)
    s = G.canvas_of(arr)
    with s as c:
        label(c, t, ["PREDICT THE TEXT,", "LEARN THE WORLD"])


def s_glass(arr, t, d, T):
    s = G.canvas_of(arr)
    words = ["The", "glass", "hit", "the", "concrete,", "and…"]
    f = G.font("jost-400", 64)
    ws = TL.lines["glass"]["words"]
    tsh = C["shatter"]
    with s as c:
        if T >= tsh:
            e = T - tsh
            rng = np.random.default_rng(5)
            ix, iy = CX + 60, 760
            c.save()
            c.clipRect(skia.Rect.MakeXYWH(0, 0, W, 1270))
            grow = ease(min(1.0, e / 0.08))
            for i in range(26):
                ang = rng.uniform(0, 2 * math.pi)
                L = rng.uniform(300, 1300) * grow
                path = skia.Path()
                path.moveTo(ix, iy)
                x, y = ix, iy
                for j in range(5):
                    ang += rng.normal(0, 0.18)
                    x += math.cos(ang) * L / 5
                    y += math.sin(ang) * L / 5
                    path.lineTo(x, y)
                c.drawPath(path, G.paint((200, 210, 230), 0.55, stroke=rng.uniform(1.0, 2.6)))
            for r_ in (60, 140, 260):
                c.drawCircle(ix, iy, r_ * grow, G.paint((220, 230, 255), 0.25, stroke=1.2))
            c.restore()
            fl = max(0.0, 1 - e / 0.12)
            if fl > 0:
                c.drawRect(skia.Rect.MakeXYWH(0, 0, W, H), G.paint((255, 255, 255), 0.5 * fl))
        shown = sum(1 for w, a_, b_ in ws if T >= a_ - 0.05)
        l1 = " ".join(words[:min(3, shown)])
        l2 = " ".join(words[3:max(3, shown)])
        c.drawRect(skia.Rect.MakeXYWH(0, 620, W, 470), G.paint((0, 0, 0), 0.55 if T >= tsh else 0.0, blur=20))
        G.text(c, l1, CX, 700, f, glow=10, glow_color=(0, 0, 0))
        G.text(c, l2, CX, 790, f, glow=10, glow_color=(0, 0, 0))
        k = ease(ramp(T, TL.s("glass2") - 0.05, TL.s("glass2") + 0.2))
        G.text(c, "shattered.", CX, 930, G.font("jost-500", 84), color=G.AMBER, a=k, track=4, glow=10, glow_color=(0, 0, 0))
        G.text(c, "YOU PREDICTED IT TOO", CX, 1040, G.font("jost-500", 36), color=G.GREY, a=k, track=4)
