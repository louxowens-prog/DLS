"""Shots for the opening and chapters I-II: HAL, the alignment, the dawn of mind, built not born."""
import math

import numpy as np
import skia

import gfx as G
from gfx import CX, H, W, ease, ramp
from cues import C
from timeline import TL

_cache = {}


def once(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


# ------------------------------------------------------------------ shared pieces

def label(c, t, lines, y=318, color=G.AMBER, size=23, speed=40.0):
    """Fact label: Eurostile-like caps typed on, with a hairline rule."""
    f = G.font("michroma-400", size)
    yy = y
    for i, s in enumerate(lines):
        n = int(max(0, t - 0.08 * i) * speed)
        if n <= 0:
            continue
        G.text(c, s[:n], CX, yy, f, color if i == 0 else G.GREY, a=1.0, track=3.0)
        yy += size * 1.75
    k = ease(ramp(t, 0.0, 0.35))
    c.drawLine(CX - 170 * k, y - size - 16, CX + 170 * k, y - size - 16, G.paint(color, 0.7, stroke=1.5))


def intertitle(arr, t, d, text, sub=None):
    s = G.canvas_of(arr)
    a = ease(ramp(t, 0.0, 0.18)) * (1 - ease(ramp(t, d - 0.15, d)))
    with s as c:
        G.text(c, text, CX, H * 0.47, G.font("jost-400", 62), a=a, track=12)
        if sub:
            G.text(c, sub, CX, H * 0.47 + 76, G.font("jost-300", 34), color=G.GREY, a=a, track=8)


def panel(c, x, y, w, h, code=None, color=G.CYAN, a=1.0, fill=(3, 7, 14)):
    """A Discovery-style display: dark glass, thin bezel, three-letter code."""
    c.drawRect(skia.Rect.MakeXYWH(x - 10, y - 10, w + 20, h + 20), G.paint((34, 36, 40), a))
    c.drawRect(skia.Rect.MakeXYWH(x - 10, y - 10, w + 20, h + 20), G.paint((90, 94, 100), a * 0.8, stroke=2))
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), G.paint(fill, a))
    if code:
        G.text(c, code, x + 18, y + 38, G.font("michroma-400", 22), color=color, a=a * 0.9, align="left", track=4)


def hal_eye(R, glow=1.0, pulse=0.0):
    """HAL 9000's lens: silver bezel, black gap, red glass with a hot yellow core and fisheye glints."""
    n = int(2 * R)
    y, x = np.mgrid[0:n, 0:n].astype(np.float32)
    x = (x - R + 0.5) / R
    y = (y - R + 0.5) / R
    r = np.sqrt(x * x + y * y)
    th = np.arctan2(y, x)
    img = np.zeros((n, n, 3), np.float32)
    bez = (r >= 0.74) & (r <= 1.0)
    metal = 0.42 + 0.30 * np.cos(2 * th - 0.9) + 0.12 * np.cos(6 * th)
    ridge = np.exp(-((r - 0.975) / 0.012) ** 2) * 0.5 + np.exp(-((r - 0.79) / 0.01) ** 2) * 0.35
    img[bez] = ((metal + ridge)[bez, None] * np.array([0.86, 0.88, 0.92]))
    gap = (r >= 0.68) & (r < 0.74)
    img[gap] = 0.02
    lens = r < 0.68
    g = glow * (1 + 0.06 * pulse)
    red = np.exp(-(r / 0.33) ** 2) * 1.25 * g + np.exp(-(r / 0.55) ** 2) * 0.28 * g
    core = np.exp(-(r / 0.07) ** 2) * 1.4 * g
    col = red[..., None] * np.array([1.0, 0.07, 0.02]) + core[..., None] * np.array([1.0, 0.86, 0.35])
    rings = (np.exp(-((r - 0.45) / 0.006) ** 2) * 0.18 + np.exp(-((r - 0.61) / 0.006) ** 2) * 0.12)
    col += rings[..., None] * np.array([0.9, 0.6, 0.5])
    # window reflections on the curved glass
    arc = np.exp(-((r - 0.52) / 0.035) ** 2) * np.exp(-((th + 2.35) / 0.28) ** 2) * 0.55
    arc2 = np.exp(-((r - 0.40) / 0.02) ** 2) * np.exp(-((th - 0.75) / 0.18) ** 2) * 0.25
    dot = np.exp(-(((x + 0.28) ** 2 + (y + 0.30) ** 2) / 0.0012)) * 0.9
    col += (arc + arc2 + dot)[..., None] * np.array([0.95, 0.95, 1.0])
    img[lens] = col[lens]
    alpha = np.clip((1 - r) * R + 0.5, 0, 1).astype(np.float32)
    return img, alpha


def monolith_path(cx, cy, w, h, persp=0.0):
    """Front face of the 1:4:9 slab; persp > 0 narrows the top (looking up at it)."""
    p = skia.Path()
    top = w * (1 - persp) / 2
    p.moveTo(cx - w / 2, cy + h / 2)
    p.lineTo(cx + w / 2, cy + h / 2)
    p.lineTo(cx + top, cy - h / 2)
    p.lineTo(cx - top, cy - h / 2)
    p.close()
    return p


def draw_monolith(c, cx, cy, w, h, persp=0.0, side=0.0, rim=0.25, a=1.0):
    if side:
        q = skia.Path()
        d = w / 4 * side  # depth is 1/4 of the width
        top = w * (1 - persp) / 2
        q.moveTo(cx + w / 2, cy + h / 2)
        q.lineTo(cx + w / 2 + d, cy + h / 2 - d * 0.35)
        q.lineTo(cx + top + d * (1 - persp), cy - h / 2 - d * 0.35)
        q.lineTo(cx + top, cy - h / 2)
        q.close()
        c.drawPath(q, G.paint((16, 17, 20), a))
    p = monolith_path(cx, cy, w, h, persp)
    sh = skia.GradientShader.MakeLinear(
        [skia.Point(cx - w / 2, cy - h / 2), skia.Point(cx + w / 2, cy + h / 2)],
        [skia.Color4f(0.06, 0.06, 0.07, a), skia.Color4f(0.0, 0.0, 0.0, a), skia.Color4f(0.03, 0.03, 0.035, a)])
    pp = G.paint(shader=sh)
    c.drawPath(p, pp)
    c.drawPath(p, G.paint((120, 125, 135), a * rim, stroke=1.6))


# ------------------------------------------------------------------ 0. HAL wakes

def s_open(arr, t, d, T):
    k = ease(ramp(t, 0.0, 1.6))
    R = 330 + 40 * t / d
    img, al = hal_eye(int(R), glow=0.15 + 0.85 * k, pulse=math.sin(t * 3))
    G.over(arr, img, al * k, int(CX - R), int(820 - R))
    G.add_light(arr, G.radial(CX, 820, R * 0.9, (255, 40, 10), 0.35 * k, 2.0))
    s = G.canvas_of(arr)
    with s as c:
        a = ease(ramp(t, 1.0, 1.6))
        G.text(c, "HAL 9000", CX, 1260, G.font("michroma-400", 34), color=G.WHITE, a=a, track=10)
        G.text(c, "2001: A SPACE ODYSSEY  ·  1968", CX, 1312, G.font("michroma-400", 20), color=G.GREY, a=a, track=4)
        label(c, t - 1.6, ["DESIGNED WITH ADVICE FROM", "AI PIONEER MARVIN MINSKY"], y=300, size=21)


# ------------------------------------------------------------------ 1. the alignment (opening fanfare)

def _moon_layer():
    rgb, al, _, off = G.sphere(1500, kind="moon", light=(0.0, 0.55, -0.83), lon0=0.3, lat_tilt=1.25, ambient=0.012)
    return rgb, al, off


def _earth_layer():
    return G.sphere(300, kind="earth", light=(0.0, 0.62, -0.78), lon0=0.9, lat_tilt=0.35, atmo_gain=1.3)


def s_sunrise(arr, t, d, T):
    k = ease(t / d)
    G.stars(arr, dy=-40 * k, a=0.9)
    lift = 380 * (1 - ease(ramp(t, 0, 4.4)))          # camera tilts up: everything rises into place
    sun_y = 560 + lift + 120 * (1 - ease(ramp(t, 0.5, 4.3)))
    ey = 900 + lift
    erg, eal, eglow, eoff = once("earth", _earth_layer)
    # sun behind the earth, climbing over its limb
    sun = G.radial(CX, sun_y, 40, (255, 252, 240), 2.2, 2.0) + G.radial(CX, sun_y, 180, (255, 235, 210), 0.45, 1.3) \
        + G.radial(CX, sun_y, 520, (255, 220, 190), 0.12, 1.0)
    streak = np.exp(-((G._YY - sun_y) ** 2) / 30) * np.exp(-np.abs(G._XX - CX) / 330) * 0.35
    G.add_light(arr, sun + streak[..., None] * np.array([1, .96, .9], np.float32))
    G.over(arr, erg, eal, int(CX - eoff), int(ey - eoff))
    light = np.zeros((H, W, 3), np.float32)
    h, w = eal.shape
    x0, y0 = int(CX - eoff), int(ey - eoff)
    ya, yb = max(0, y0), min(H, y0 + h)
    light[ya:yb, x0:x0 + w] = eglow[ya - y0: yb - y0]
    G.add_light(arr, light)
    mrgb, mal, moff = once("moon", _moon_layer)
    my = 2560 + lift * 1.35
    G.over(arr, mrgb, mal, int(CX - moff), int(my - moff))
    s = G.canvas_of(arr)
    with s as c:
        a = ease(ramp(T, C["title"] - 0.02, C["title"] + 0.35)) * (1 - ease(ramp(T, C["int1"] - 0.3, C["int1"])))
        G.text(c, "WHAT IS", CX, 1235, G.font("jost-300", 42), a=a, track=24)
        G.text(c, "intelligence?", CX, 1350, G.font("cabin-400", 104), a=a, track=14)


# ------------------------------------------------------------------ I. the dawn of mind

def s_int1(arr, t, d, T):
    intertitle(arr, t, d, "THE DAWN OF MIND", "I")


def s_defs(arr, t, d, T):
    s = G.canvas_of(arr)
    n_on = int(ramp(T, TL.s("defs") + 0.1, TL.word("defs", "definitions") + 0.2) * 72)
    rng = np.random.default_rng(3)
    with s as c:
        cols, rows = 8, 9
        cw, ch = 112, 88
        x0, y0 = CX - cols * cw / 2, 430
        f = G.font("michroma-400", 15)
        fb = G.font("jost-500", 30)
        for i in range(72):
            cx_, cy_ = x0 + (i % cols) * cw, y0 + (i // cols) * ch
            on = i < n_on
            col = G.CYAN if on else G.DIM
            c.drawRect(skia.Rect.MakeXYWH(cx_ + 6, cy_ + 6, cw - 12, ch - 12), G.paint(col, 0.18 if on else 0.08))
            c.drawRect(skia.Rect.MakeXYWH(cx_ + 6, cy_ + 6, cw - 12, ch - 12), G.paint(col, 0.9 if on else 0.3, stroke=1.2))
            if on:
                G.text(c, f"DEF {i + 1:02d}", cx_ + cw / 2, cy_ + 36, f, color=G.WHITE, a=0.9, track=1)
                wl = int(rng.integers(20, 70))
                c.drawLine(cx_ + 18, cy_ + 56, cx_ + 18 + wl, cy_ + 56, G.paint(G.CYAN, 0.8, stroke=3))
        cnt = min(70, int(n_on * 70 / 72)) if n_on < 72 else 70
        G.text(c, f"{cnt}{'+' if n_on >= 72 else ''}", CX, 1300, G.font("jost-300", 150), color=G.WHITE, track=4)
        label(c, t, ["A COLLECTION OF DEFINITIONS", "OF INTELLIGENCE · LEGG & HUTTER, 2007"])


USEFUL = ["MODEL", "LEARN", "INFER", "ADAPT", "PLAN"]
USEFUL_SUB = ["THE WORLD", "FROM EXPERIENCE", "WHAT WASN'T SAID", "TO THE NEW", "TOWARD GOALS"]


def s_useful(arr, t, d, T, dim_all=False):
    s = G.canvas_of(arr)
    with s as c:
        for i, (wd, sub) in enumerate(zip(USEFUL, USEFUL_SUB)):
            y = 400 + i * 172
            on_t = TL.word("useful", ["model", "learn", "infer", "adapt", "plan"][i]) - TL.s("useful") if not dim_all else 1e9
            k = ease(ramp(t, on_t - 0.05, on_t + 0.2))
            panel(c, 150, y, 780, 140, code=["NAV", "MEM", "CNT", "GDE", "COM"][i], color=G.CYAN)
            col = G.WHITE
            G.text(c, wd, CX + 40, y + 86, G.font("jost-500", 64), color=col, a=0.12 + 0.88 * k, track=16,
                   glow=10 * k, glow_color=G.CYAN)
            G.text(c, sub, CX + 40, y + 124, G.font("michroma-400", 17), color=G.CYAN, a=0.9 * k, track=4)
        if not dim_all:
            label(c, t, ["A WORKING DEFINITION"], y=320)


def s_knowledge(arr, t, d, T):
    s_useful(arr, 0, d, T, dim_all=True)
    s = G.canvas_of(arr)
    with s as c:
        kt = TL.word("knowledge", "knowledge") - TL.s("knowledge")
        a = ease(ramp(t, kt - 0.1, kt + 0.15))
        c.drawRect(skia.Rect.MakeXYWH(0, 0, W, H), G.paint((0, 0, 0), 0.55 * a))
        G.text(c, "KNOWLEDGE", CX, 1005, G.font("jost-500", 96), color=G.HAL, a=a, track=14, glow=18, glow_color=G.HAL)
        G.text(c, "NOT ON THE LIST", CX, 1080, G.font("michroma-400", 26), color=G.WHITE, a=a * 0.9, track=8)


def s_drive(arr, t, d, T):
    k = t / d
    G.stars(arr, dx=20 * k, a=0.8)
    s = G.canvas_of(arr)
    words = ["ENCYCLOPEDIAS", "SCIENTIFIC PAPERS", "NOVELS", "PHOTOGRAPHS", "HISTORY", "MUSIC", "SOFTWARE", "LAW",
             "MAPS", "RECIPES", "POETRY", "PATENTS", "LETTERS", "FILMS", "MATHEMATICS", "MEDICINE"]
    rng = np.random.default_rng(8)
    with s as c:
        f = G.font("michroma-400", 20)
        for i in range(34):
            wd = words[i % len(words)]
            ang = rng.uniform(0, 2 * math.pi)
            sp = rng.uniform(0.5, 1.0)
            ph = (rng.uniform(0, 1) + k * sp * 1.6) % 1.0
            rad = 950 * (1 - ph) + 160
            x = CX + math.cos(ang) * rad * 0.8
            y = 860 + math.sin(ang) * rad
            G.text(c, wd, x, y, f, color=(170, 190, 230), a=0.7 * ph * (1 - ph) * 4 * 0.6, track=2)
        pass
    G.add_light(arr, G.radial(CX, 860, 330, (120, 160, 255), 0.55, 1.6) + G.radial(CX, 860, 120, (200, 220, 255), 0.35, 2))
    s = G.canvas_of(arr)
    with s as c:
        draw_monolith(c, CX, 860, 250 * (1 + 0.05 * k), 562 * (1 + 0.05 * k), persp=0.0, side=0.35, rim=0.9)
        label(c, t, ["EVERY BOOK · SONG · PROGRAM", "PERFECTLY STORED"])


def _dawn_sky():
    y = np.linspace(0, 1, H)[:, None]
    top = np.array([0.10, 0.03, 0.01])
    mid = np.array([0.78, 0.36, 0.10])
    hor = np.array([1.0, 0.82, 0.46])
    k = np.clip((y - 0.05) / 0.55, 0, 1) ** 1.3
    sky = top * (1 - k[..., None]) + mid * k[..., None]
    k2 = np.clip((y - 0.42) / 0.18, 0, 1) ** 1.5
    sky = sky * (1 - k2[..., None]) + hor * k2[..., None]
    sky = np.repeat(sky, W, axis=1)
    return sky.astype(np.float32)


HORIZON = 1190


def noise1d(n, knots, seed):
    rng = np.random.default_rng(seed)
    k = rng.random(knots + 1)
    from scipy.interpolate import CubicSpline
    return CubicSpline(np.linspace(0, n, knots + 1), k)(np.arange(n))


def _ridge():
    xs = np.arange(W + 1).astype(np.float32)
    n = 0.6 * noise1d(W + 1, 6, 31) + 0.3 * noise1d(W + 1, 18, 32) + 0.1 * noise1d(W + 1, 60, 33)
    r = HORIZON - 8 - n * 34
    return r


def _ground_tex():
    g = G.fbm(H - HORIZON + 40, W, octaves=5, seed=33, base=5)
    return (0.02 + 0.05 * g).astype(np.float32)


PROP = (12, 6, 4)


def dawn(arr, t, props=True, lever=0.0, child=0.0, plank_in=1.0, label_a=1.0):
    sky = once("dawnsky", _dawn_sky)
    arr[..., :3] = (sky * 255).astype(np.uint8)
    G.add_light(arr, G.radial(690, HORIZON - 40, 80, (255, 248, 220), 1.0, 2) +
                G.radial(690, HORIZON - 40, 380, (255, 190, 120), 0.32, 1.2))
    ridge = once("ridge", _ridge)
    gt = once("groundtex", _ground_tex)
    s = G.canvas_of(arr)
    with s as c:
        p = skia.Path()
        p.moveTo(0, H)
        for x in range(0, W + 1, 4):
            p.lineTo(x, ridge[x])
        p.lineTo(W, H)
        p.close()
        c.drawPath(p, G.paint((10, 5, 3)))
    # faint texture in the ground so it is not a flat black card
    y0 = HORIZON - 40
    sub = arr[y0:, :, :3].astype(np.float32) / 255
    mask = (sub.max(-1) < 0.06)[..., None]
    arr[y0:, :, :3] = (np.clip(np.where(mask, sub + gt[: H - y0, :, None] * np.array([1.0, 0.6, 0.4]), sub), 0, 1) * 255).astype(np.uint8)
    s = G.canvas_of(arr)
    with s as c:
        # the lever: log fulcrum and plank; far end goes down as the child pushes
        fx, py = 470, HORIZON - 64
        ang = 0.17 - 0.34 * lever
        L1, L2 = 215, 300
        nx, ny = fx - L1 * math.cos(ang), py + L1 * math.sin(ang)
        fx2, fy2 = fx + L2 * math.cos(ang), py - L2 * math.sin(ang)
        lift = max(0.0, (py + L1 * math.sin(0.17)) - ny) if plank_in >= 1 else 0.0
        # boulder
        bx, by = 250, HORIZON - lift
        c.save()
        c.translate(bx, by)
        c.rotate(-8 * lever)
        b = skia.Path()
        b.moveTo(-150, 0)
        b.cubicTo(-190, -70, -150, -175, -60, -210)
        b.cubicTo(0, -235, 60, -190, 95, -205)
        b.cubicTo(165, -170, 175, -80, 150, -10)
        b.cubicTo(140, 10, -120, 12, -150, 0)
        c.drawPath(b, G.paint(PROP))
        c.restore()
        if plank_in > 0:
            off = (1 - plank_in) * 420
            c.drawCircle(fx + off, HORIZON - 34, 34, G.paint(PROP))
            c.drawLine(nx + off, ny, fx2 + off, fy2, G.paint(PROP, stroke=22, cap_round=False))
            if child > 0:
                draw_child(c, fx2 + off, fy2, push=lever, a=child)
        if props:
            for i in range(3):
                c.save()
                c.translate(560 + i * 30, HORIZON)
                c.rotate(-8 + i * 5)
                c.drawRoundRect(skia.Rect.MakeXYWH(-11, -330, 22, 330), 4, 4, G.paint(PROP))
                c.restore()
            for r_, w_ in ((52, 12), (34, 10), (18, 8)):
                c.drawOval(skia.Rect.MakeXYWH(730 - r_ * 1.3, HORIZON - 30 - r_ * 0.55, 2.6 * r_, 1.1 * r_), G.paint(PROP, stroke=w_))
            pul = skia.Path()
            pul.addArc(skia.Rect.MakeXYWH(800, HORIZON - 300, 110, 110), 35, 250)
            c.drawPath(pul, G.paint(PROP, stroke=18, cap_round=False))
            c.drawCircle(855, HORIZON - 245, 13, G.paint(PROP))
            c.drawLine(855, HORIZON - 245, 885, HORIZON - 170, G.paint(PROP, stroke=10))
            c.drawLine(855, HORIZON - 230, 855, HORIZON, G.paint(PROP, stroke=16))
            fl = G.font("michroma-400", 19)
            for x, yy, s_ in ((250, 70, "ROCK"), (590, 70, "3 PLANKS"), (730, 118, "ROPE"), (870, 70, "BROKEN PULLEY")):
                G.text(c, s_, x, HORIZON + yy, fl, color=(255, 205, 160), a=0.9 * label_a, track=3)


def draw_child(c, hx, hy, push=0.0, a=1.0):
    """A child leaning on the lever end (hx, hy), as a silhouette."""
    col = PROP
    fx1, fx2 = hx + 95, hx + 150
    hip = (hx + 118, HORIZON - 118)
    sh = (hx + 58, HORIZON - 196 + 26 * push)
    head = (sh[0] - 24, sh[1] - 50)
    c.drawLine(hip[0], hip[1], fx1, HORIZON - 4, G.paint(col, a, stroke=30))
    c.drawLine(hip[0], hip[1], fx2, HORIZON - 4, G.paint(col, a, stroke=30))
    body = skia.Path()
    body.moveTo(hip[0] - 26, hip[1] + 14)
    body.lineTo(hip[0] + 26, hip[1] + 6)
    body.lineTo(sh[0] + 32, sh[1] + 8)
    body.lineTo(sh[0] - 30, sh[1] - 10)
    body.close()
    c.drawPath(body, G.paint(col, a))
    c.drawCircle(sh[0], sh[1], 30, G.paint(col, a))
    c.drawCircle(hip[0], hip[1], 26, G.paint(col, a))
    c.drawCircle(head[0], head[1], 36, G.paint(col, a))
    c.drawLine(sh[0], sh[1] + 6, hx + 6, hy - 12, G.paint(col, a, stroke=20))
    c.drawLine(sh[0] + 10, sh[1] + 10, hx + 22, hy - 10, G.paint(col, a, stroke=18))


def s_rock(arr, t, d, T):
    dawn(arr, t, props=True, plank_in=0.0)
    s = G.canvas_of(arr)
    with s as c:
        draw_monolith(c, 1000, HORIZON - 169, 150, 338, side=0.0, rim=0.25)
        label(c, t, ["TASK: LIFT THE ROCK"], color=(255, 220, 170))


def s_nothing(arr, t, d, T):
    dawn(arr, 0, props=True, plank_in=0.0)
    s = G.canvas_of(arr)
    with s as c:
        c.drawRect(skia.Rect.MakeXYWH(0, 0, W, H), G.paint((0, 0, 0), 0.35))
        draw_monolith(c, 1000, HORIZON - 169, 150, 338, side=0.0, rim=0.25)
        G.text(c, "NO OUTPUT", CX, 560, G.font("michroma-400", 30), color=(255, 225, 190), a=ease(ramp(t, 0.5, 0.8)), track=10)


def s_child(arr, t, d, T):
    tf = C["figure"] - C["child"]
    plank = ease(ramp(t, 0.1, tf))
    lev = ease(ramp(t, tf + 0.2, d - 0.3))
    dawn(arr, t, props=False, lever=lev, child=ease(ramp(t, 0.0, 0.5)), plank_in=plank)
    s = G.canvas_of(arr)
    with s as c:
        G.text(c, "GENERALIZATION", CX, 560, G.font("michroma-400", 30), color=(255, 225, 190),
               a=ease(ramp(T, TL.word("child", "generalization") - 0.1, TL.word("child", "generalization") + 0.3)), track=10)
        label(c, t, ["NEVER SEEN BEFORE. SOLVED."], color=(255, 220, 170))


def _bone_path():
    p = skia.Path()
    p.addRoundRect(skia.Rect.MakeXYWH(-150, -13, 300, 26), 13, 13)
    for sx in (-1, 1):
        p.addCircle(sx * 155, -16, 24)
        p.addCircle(sx * 160, 14, 21)
    return p


def s_bone(arr, t, d, T):
    y = np.linspace(0, 1, H)[:, None, None]
    sky = np.array([0.36, 0.55, 0.80]) * (1 - y) + np.array([0.80, 0.86, 0.92]) * y
    arr[..., :3] = (np.broadcast_to(sky, (H, W, 3)) * 255).astype(np.uint8)
    cl = once("bonecl", lambda: G.fbm(H // 4, W // 4, octaves=5, seed=41, base=3))
    clouds = np.clip((cl - 0.55) * 3, 0, 1)
    from scipy import ndimage
    cl_full = ndimage.zoom(clouds, 4, order=1)[:H, :W]
    G.add_light(arr, cl_full[..., None] * np.array([0.35, 0.3, 0.25], np.float32))
    k = t / d
    s = G.canvas_of(arr)
    with s as c:
        c.save()
        c.translate(CX + 60 - 140 * k, 1180 - 520 * (1 - (1 - k) ** 2))
        c.rotate(-200 + 170 * ease(k))
        c.scale(1.35, 1.35)
        sh = skia.GradientShader.MakeLinear([skia.Point(0, -30), skia.Point(0, 30)],
                                            [skia.Color4f(0.97, 0.94, 0.86, 1), skia.Color4f(0.62, 0.56, 0.46, 1)])
        c.drawPath(_bone_path(), G.paint(shader=sh))
        c.restore()


def satellite(c, x, y, ang, scale=1.0, a=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(scale, scale)
    body = skia.GradientShader.MakeLinear([skia.Point(0, -34), skia.Point(0, 34)],
                                          [skia.Color4f(0.95, 0.95, 0.97, a), skia.Color4f(0.55, 0.56, 0.6, a),
                                           skia.Color4f(0.18, 0.18, 0.2, a)])
    c.drawRoundRect(skia.Rect.MakeXYWH(-280, -30, 560, 60), 8, 8, G.paint(shader=body))
    for i, (px, w_) in enumerate(((-250, 50), (-120, 70), (40, 44), (170, 80))):
        c.drawRect(skia.Rect.MakeXYWH(px, -44, w_, 88), G.paint(shader=body))
        c.drawRect(skia.Rect.MakeXYWH(px, -44, w_, 88), G.paint((40, 40, 44), a, stroke=1.5))
    c.drawRect(skia.Rect.MakeXYWH(-40, -120, 22, 240), G.paint((70, 72, 80), a))
    for sy in (-1, 1):
        c.drawRect(skia.Rect.MakeXYWH(-80, sy * 120 - (60 if sy < 0 else 0), 100, 60), G.paint((50, 55, 70), a))
        for gx in range(5):
            c.drawLine(-80 + gx * 20, sy * 120 - (60 if sy < 0 else 0), -80 + gx * 20, sy * 120 + (0 if sy < 0 else 60),
                       G.paint((110, 115, 130), a, stroke=1))
    c.drawCircle(280, 0, 18, G.paint((200, 200, 205), a))
    c.restore()


def s_sat(arr, t, d, T):
    G.stars(arr, dx=-15 * t, a=0.9)
    G.put_sphere(arr, 900, 2350, 900, kind="earth", light=(-0.6, 0.6, 0.5), lon0=2.2, lat_tilt=0.4) if False else None
    erg = once("earth_big", lambda: G.sphere(1150, kind="earth", light=(-0.55, 0.55, 0.62), lon0=2.4, lat_tilt=0.5))
    rgb, al, glow, off = erg
    G.over(arr, rgb, al, int(700 - off), int(2600 - off))
    s = G.canvas_of(arr)
    with s as c:
        satellite(c, CX + 40 - 30 * t, 760 - 8 * t, -30 + 1.5 * t, scale=1.0)


def s_int2(arr, t, d, T):
    intertitle(arr, t, d, "BUILT, NOT BORN", "II")


def s_artif(arr, t, d, T):
    s = G.canvas_of(arr)
    with s as c:
        panel(c, 110, 560, 860, 560, code="LEX", color=G.AMBER)
        G.text(c, "ARTIFICIAL", CX, 740, G.font("jost-500", 100), a=ease(ramp(t, 0.0, 0.3)), track=10)
        k = ease(ramp(t, 1.1, 1.6))
        f2 = G.font("michroma-400", 30)
        G.text(c, "ARS  +  FACERE", CX, 880, f2, color=G.AMBER, a=k, track=8)
        G.text(c, "SKILL, ART     TO MAKE", CX, 940, G.font("michroma-400", 20), color=G.GREY, a=k, track=5)
        k2 = ease(ramp(T, TL.word("artif", "made") - 0.1, TL.word("artif", "made") + 0.2))
        G.text(c, "“MADE WITH SKILL”", CX, 1050, G.font("jost-400", 50), color=G.WHITE, a=k2, track=6)
        fk = ease(ramp(T, TL.word("artif", "fake") - 0.05, TL.word("artif", "fake") + 0.1))
        if fk > 0 and k2 < 0.5:
            G.text(c, "NOT FAKE", CX, 1050, G.font("jost-500", 56), color=G.HAL, a=fk * (1 - k2 * 2), track=8)
        label(c, t, ["LATIN: ARTIFICIALIS", "“OF OR BELONGING TO ART”"])


def s_corridor(arr, t, d, T):
    """Space-station corridor in one-point perspective, lit by its ceiling panels."""
    s = G.canvas_of(arr)
    vx, vy = CX, 820
    z0 = (t * 0.9) % 1.0
    with s as c:
        c.drawRect(skia.Rect.MakeXYWH(0, 0, W, H), G.paint((12, 12, 14)))
        for i in range(14, -1, -1):
            za, zb = i + 1 - z0, i + 2 - z0
            if za <= 0.05:
                continue
            def proj(u, v, z):
                return vx + u * 700 / z, vy + v * 700 / z
            sh = 1 / (1 + 0.28 * za)
            for (u0, v0, u1, v1, col) in ((-1, -1.4, 1, -1.4, (235, 235, 240)), (-1, 1.4, 1, 1.4, (200, 200, 205)),
                                          (-1, -1.4, -1, 1.4, (215, 215, 222)), (1, -1.4, 1, 1.4, (215, 215, 222))):
                p = skia.Path()
                a1, b1 = proj(u0, v0, za)
                a2, b2 = proj(u1, v1, za)
                a3, b3 = proj(u1, v1, zb)
                a4, b4 = proj(u0, v0, zb)
                p.moveTo(a1, b1)
                p.lineTo(a2, b2)
                p.lineTo(a3, b3)
                p.lineTo(a4, b4)
                p.close()
                cc = tuple(int(x * sh) for x in col)
                c.drawPath(p, G.paint(cc))
                c.drawPath(p, G.paint((0, 0, 0), 0.25, stroke=1.2))
            # ceiling light panel
            a1, b1 = proj(-0.55, -1.4, za + 0.15)
            a2, b2 = proj(0.55, -1.4, zb - 0.15)
            c.drawRect(skia.Rect.MakeLTRB(a1, b1, a2, b2), G.paint((255, 252, 240), min(1, sh * 1.6)))
            # red chairs along the floor, a nod to the station lounge
            if i % 3 == 0:
                a1, b1 = proj(-0.8, 1.05, za + 0.3)
                a2, b2 = proj(-0.45, 1.4, za + 0.5)
                c.drawRoundRect(skia.Rect.MakeLTRB(a1, b1, a2, b2), 8, 8, G.paint((200, 20, 30), sh))
                a1, b1 = proj(0.45, 1.05, za + 0.3)
                a2, b2 = proj(0.8, 1.4, za + 0.5)
                c.drawRoundRect(skia.Rect.MakeLTRB(a1, b1, a2, b2), 8, 8, G.paint((200, 20, 30), sh))
        ka = ease(ramp(t, 0.3, 0.6))
        c.drawRect(skia.Rect.MakeXYWH(0, 280, W, 76), G.paint((0, 0, 0), 0.75 * ka))
        G.text(c, "ARTIFICIAL LIGHT = REAL LIGHT", CX, 330, G.font("michroma-400", 24), color=G.AMBER, a=ka, track=4)


def s_heart(arr, t, d, T):
    s = G.canvas_of(arr)
    with s as c:
        panel(c, 90, 520, 900, 620, code="HIB", color=G.GREEN)
        G.text(c, "LIFE FUNCTIONS", 150, 640, G.font("michroma-400", 26), color=G.WHITE, align="left", track=5)
        G.text(c, "ARTIFICIAL HEART", 150, 690, G.font("michroma-400", 20), color=G.GREEN, align="left", track=4)
        period = 0.78
        path = skia.Path()
        x0, x1, yb = 130, 950, 930
        first = True
        for px in range(x0, x1, 3):
            tt = t - (x1 - px) / 520.0
            ph = (tt - 0.35) % period / period
            v = 0.0
            v += 0.12 * math.exp(-((ph - 0.12) / 0.03) ** 2)
            v -= 0.18 * math.exp(-((ph - 0.20) / 0.008) ** 2)
            v += 1.0 * math.exp(-((ph - 0.225) / 0.012) ** 2)
            v -= 0.3 * math.exp(-((ph - 0.25) / 0.01) ** 2)
            v += 0.25 * math.exp(-((ph - 0.45) / 0.05) ** 2)
            yy = yb - v * 150
            if first:
                path.moveTo(px, yy)
                first = False
            else:
                path.lineTo(px, yy)
        c.drawPath(path, G.paint(G.GREEN, 0.35, stroke=9, blur=6))
        c.drawPath(path, G.paint(G.GREEN, 1.0, stroke=3.2))
        c.drawCircle(x1, yb, 7, G.paint(G.WHITE))
        G.text(c, "PULSE 77", 950, 1100, G.font("michroma-400", 26), color=G.GREEN, align="right", track=4)
        G.text(c, "FLOW 5.1 L/MIN", 150, 1100, G.font("michroma-400", 26), color=G.GREEN, align="left", track=4)
        label(c, t, ["REALLY PUMPS BLOOD"], color=G.GREEN)


def s_station(arr, t, d, T):
    G.stars(arr, dx=10 * t, a=0.9)
    erg = once("earth_st", lambda: G.sphere(700, kind="earth", light=(0.7, 0.35, 0.62), lon0=4.0, lat_tilt=0.45))
    rgb, al, glow, off = erg
    G.over(arr, rgb, al, int(CX - off), int(1900 - off))
    s = G.canvas_of(arr)
    with s as c:
        cx, cy, rx, ry = CX, 760, 420, 150
        rot = t * 0.25
        # wheel: thick ring as two ellipses, spokes, hub
        for dy, col, wdt in ((10, (70, 72, 80), 46), (0, (215, 218, 225), 40)):
            c.drawOval(skia.Rect.MakeXYWH(cx - rx, cy - ry + dy, 2 * rx, 2 * ry), G.paint(col, stroke=wdt, cap_round=False))
        for i in range(56):
            a = rot + i * 2 * math.pi / 56
            x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
            if math.sin(a) > -0.2:
                c.drawRect(skia.Rect.MakeXYWH(x - 3, y - 2, 6, 4), G.paint((255, 245, 200), 0.85))
        for i in range(4):
            a = rot + i * math.pi / 2
            x, y = cx + rx * 0.93 * math.cos(a), cy + ry * 0.93 * math.sin(a)
            c.drawLine(cx, cy, x, y, G.paint((190, 192, 200), stroke=14, cap_round=False))
        c.drawOval(skia.Rect.MakeXYWH(cx - 70, cy - 30, 140, 60), G.paint((225, 228, 235)))
        c.drawRect(skia.Rect.MakeXYWH(cx - 18, cy - 230, 36, 200), G.paint((160, 162, 170)))
        c.drawOval(skia.Rect.MakeXYWH(cx - 60, cy - 250, 120, 44), G.paint((200, 202, 210)))
        label(c, t, ["NIST GLOSSARY: SYSTEMS THAT SOLVE TASKS", "NEEDING HUMAN-LIKE PERCEPTION, PLANNING,",
                     "LEARNING OR COMMUNICATION"], size=19)


PIECES = {  # a middlegame, drawn from white's side
    (0, 0): "♜", (0, 4): "♜", (0, 6): "♚", (1, 0): "♟", (1, 1): "♟", (1, 5): "♟", (1, 6): "♟", (1, 7): "♟",
    (2, 2): "♞", (2, 3): "♟", (3, 4): "♝", (4, 3): "♙", (4, 4): "♛", (5, 2): "♘", (5, 5): "♗",
    (6, 0): "♙", (6, 1): "♙", (6, 5): "♙", (6, 6): "♙", (6, 7): "♙", (7, 0): "♖", (7, 3): "♕", (7, 5): "♖", (7, 6): "♔",
}


def s_chess(arr, t, d, T):
    s = G.canvas_of(arr)
    with s as c:
        panel(c, 120, 470, 840, 840, code="CHS", color=G.CYAN)
        S0, x0, y0 = 94, 164, 520
        for r in range(8):
            for q in range(8):
                col = (185, 190, 200) if (r + q) % 2 == 0 else (60, 66, 80)
                c.drawRect(skia.Rect.MakeXYWH(x0 + q * S0, y0 + r * S0, S0, S0), G.paint(col))
        f = skia.Font(skia.Typeface.MakeFromFile("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), 78)
        mv = ease(ramp(t, 0.8, 1.6))
        for (r, q), pc in PIECES.items():
            if (r, q) == (5, 5):
                rr, qq = 5 - 3 * mv, 5 - 3 * mv   # bishop sweeps up the diagonal
            else:
                rr, qq = r, q
            white = pc in "♔♕♖♗♘♙"
            col = (255, 255, 255) if white else (10, 10, 14)
            G.text(c, pc, x0 + qq * S0 + S0 / 2, y0 + rr * S0 + S0 * 0.8, f, color=col, a=1.0,
                   glow=3 if not white else 0, glow_color=(255, 255, 255) if not white else None)
        label(c, t, ["DEEP BLUE DEFEATS KASPAROV", "IBM · MAY 1997"])


def s_go(arr, t, d, T):
    s = G.canvas_of(arr)
    rng = np.random.default_rng(19)
    with s as c:
        panel(c, 120, 470, 840, 840, code="GO", color=G.AMBER, fill=(170, 130, 70))
        S0, x0, y0 = 44, 144, 494
        for i in range(19):
            c.drawLine(x0 + i * S0, y0, x0 + i * S0, y0 + 18 * S0, G.paint((30, 20, 10), stroke=1.6))
            c.drawLine(x0, y0 + i * S0, x0 + 18 * S0, y0 + i * S0, G.paint((30, 20, 10), stroke=1.6))
        for a_ in (3, 9, 15):
            for b_ in (3, 9, 15):
                c.drawCircle(x0 + a_ * S0, y0 + b_ * S0, 5, G.paint((30, 20, 10)))
        n = int(ramp(t, 0.0, d * 0.85) * 60) + 20
        cells = rng.permutation(19 * 19)
        for k in range(n):
            q, r = cells[k] % 19, cells[k] // 19
            col = (15, 15, 18) if k % 2 == 0 else (240, 240, 235)
            c.drawCircle(x0 + q * S0, y0 + r * S0, 20, G.paint(col))
        label(c, t, ["ALPHAGO DEFEATS LEE SEDOL 4-1", "DEEPMIND · MARCH 2016"])


def _jupiter_layer():
    R = 520
    n = 2 * R
    y, x = np.mgrid[0:n, 0:n].astype(np.float32)
    x = (x - R) / R
    y = (y - R) / R
    rr = x * x + y * y
    z = np.sqrt(np.clip(1 - rr, 0, 1))
    lat = np.arcsin(np.clip(-y, -1, 1))
    turb = G.fbm(n, n, octaves=5, seed=51, base=4)
    bands = np.sin(lat * 14 + turb * 2.4) * 0.5 + 0.5
    c1 = np.array([0.86, 0.78, 0.64])
    c2 = np.array([0.62, 0.45, 0.32])
    col = c1 * bands[..., None] + c2 * (1 - bands[..., None])
    L = np.array([-0.75, 0.2, 0.62])
    L /= np.linalg.norm(L)
    ndl = np.clip(x * L[0] - y * L[1] + z * L[2], 0, 1)
    col = col * (ndl ** 0.9)[..., None]
    al = np.clip((1 - np.sqrt(rr)) * R, 0, 1)
    return col.astype(np.float32), al.astype(np.float32), R


def s_jupiter(arr, t, d, T):
    G.stars(arr, dy=-10 * t, a=0.8)
    rgb, al, R = once("jup", _jupiter_layer)
    G.over(arr, rgb, al, int(CX + 60 - R), int(1500 - R))
    s = G.canvas_of(arr)
    with s as c:
        for i, (mx, my, mr) in enumerate(((300, 700, 9), (400, 760, 7), (500, 820, 11), (610, 880, 8))):
            c.drawCircle(mx, my, mr, G.paint((225, 220, 210)))
        ang = -12 + 8 * t / d
        c.save()
        c.translate(CX + 40, 1190 + 20 * t / d)
        c.rotate(ang)
        draw_monolith(c, 0, 0, 150, 338, side=0.6, rim=0.25)
        c.restore()
        a = ease(ramp(T, TL.word("question", "general") - 0.1, TL.word("question", "general") + 0.3))
        G.text(c, "HOW GENERAL?", CX, 480, G.font("jost-500", 78), a=a, track=10)
