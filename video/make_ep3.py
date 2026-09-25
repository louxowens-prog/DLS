#!/usr/bin/env python3
"""Render EP.3 "THE ASCENSION ARC": a <2 min vertical short on exponents and radicals,
anime energy meets Catholic kitsch (stained glass, glory rays, votive candles, holy cards,
Latin chapter titles, a haloed mascot, organ + choir + bells). Reuses make_video.py.

    python3 make_ep3.py                  # full render -> out/the_ascension_arc.mp4
    python3 make_ep3.py --preview 3 17   # dump frames to out/preview/the_ascension_arc/
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

import make_video as E
from make_video import (BLACK, FONT_MATH, G, GOLD, KR, W, H, WHITE, cue, ease_out_back, ease_out_cubic,
                        fit_size, font, impact, kazu, pop, rot_text, slam, star, stroke_for, text)

FONT_SERIF = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
CRIMSON = (200, 20, 50)
ROSE = (255, 120, 165)
SKY = (120, 180, 255)
CREAM = (250, 238, 205)
GOLD_D = (170, 120, 20)
INK = (90, 10, 24)
JEWELS = [(170, 20, 40), (30, 60, 170), (20, 120, 70), (200, 150, 30), (110, 40, 150), (20, 110, 140), (190, 70, 30)]

# ---------------------------------------------------------------- the chapel (background)

_glass = {}
GLASS = {  # scene key -> (seed, jewel weights)
    "hook": (11, [4, 1, 0, 3, 1, 0, 2]), "blue": (12, [1, 4, 1, 1, 1, 2, 0]), "violet": (13, [1, 1, 0, 1, 4, 1, 0]),
    "red": (14, [4, 1, 0, 2, 1, 0, 2]), "green": (15, [0, 1, 4, 1, 1, 2, 0]), "teal": (16, [0, 2, 1, 1, 1, 4, 0]),
    "mixed": (17, [1, 1, 1, 1, 1, 1, 1]),
}


def stained(seed, weights):
    rng = np.random.default_rng(seed)
    w, h, n = 216, 384, 64
    px, py = rng.uniform(0, w, n), rng.uniform(0, h, n)
    yy, xx = np.mgrid[0:h, 0:w]
    lab = ((xx[..., None] - px) ** 2 + (yy[..., None] - py) ** 2).argmin(-1)
    p = np.array(weights, float) / sum(weights)
    cols = np.array([JEWELS[i] for i in rng.choice(len(JEWELS), n, p=p)], float) * rng.uniform(0.7, 1.15, (n, 1))
    img = cols[lab]
    img[(lab != np.roll(lab, 1, 0)) | (lab != np.roll(lab, 1, 1))] = (14, 8, 14)
    arr = np.asarray(Image.fromarray(img.clip(0, 255).astype(np.uint8)).resize((W, H), Image.NEAREST)).astype(float)
    Y, X = np.mgrid[0:H, 0:W]
    light = 0.21 + 0.27 * np.exp(-(((X - W / 2) / (W * 0.6)) ** 2 + ((Y - H * 0.3) / (H * 0.45)) ** 2))
    return Image.fromarray((arr * light[..., None]).clip(0, 255).astype(np.uint8))


CANDLES = [(170, 1790), (355, 1812), (540, 1790), (725, 1812), (910, 1790)]
_glow = Image.new("L", (W, H), 0)
_gd = ImageDraw.Draw(_glow)
for _x, _y in CANDLES:
    _gd.ellipse([_x - 110, _y - 200, _x + 110, _y + 20], fill=120)
GLOW = _glow.filter(ImageFilter.GaussianBlur(40))


def chapel(key, t, rc=(W / 2, 300), ray_alpha=50, speed=0.1):
    if key not in _glass:
        _glass[key] = stained(*GLASS[key])
    G.img = _glass[key].copy()
    G.draw = d = ImageDraw.Draw(G.img)
    m = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(m)
    n = 32
    for i in range(n):
        a0 = t * speed + i * 2 * math.pi / n
        a1 = a0 + math.pi / n
        md.polygon([rc, (rc[0] + 2200 * math.cos(a0), rc[1] + 2200 * math.sin(a0)),
                    (rc[0] + 2200 * math.cos(a1), rc[1] + 2200 * math.sin(a1))], fill=ray_alpha)
    md.ellipse([rc[0] - 150, rc[1] - 150, rc[0] + 150, rc[1] + 150], fill=ray_alpha + 30)
    G.img.paste((255, 214, 120), mask=ImageChops.lighter(m, GLOW))
    for x, y, s, sp in E.SPARKS:
        yy = (y - t * sp * 0.6) % H
        star(x, yy, s * (0.6 + 0.4 * math.sin(t * 6 + x)), (255, 225, 140))
    # holy-card border
    for inset, wd, col in ((22, 12, BLACK), (22, 6, GOLD), (40, 3, GOLD_D)):
        d.rectangle([inset, inset + 12, W - inset, H - inset], outline=col, width=wd)
    for x, y in ((34, 46), (W - 34, 46), (34, H - 34), (W - 34, H - 34)):
        d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=CRIMSON, outline=GOLD, width=5)
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=GOLD)
    d.rectangle([W / 2 - 6, 22, W / 2 + 6, 74], fill=GOLD, outline=BLACK, width=3)
    d.rectangle([W / 2 - 20, 34, W / 2 + 20, 46], fill=GOLD, outline=BLACK, width=3)
    # votive candles
    for i, (x, y) in enumerate(CANDLES):
        d.rounded_rectangle([x - 42, y - 50, x + 42, y + 50], 14, fill=CRIMSON, outline=BLACK, width=5)
        d.rectangle([x - 30, y - 36, x - 20, y + 36], fill=(245, 100, 120))
        d.ellipse([x - 38, y - 58, x + 38, y - 42], fill=CREAM, outline=BLACK, width=3)
        fh = 34 * (1 + 0.15 * math.sin(t * 23 + i * 1.9) + 0.08 * math.sin(t * 37 + i))
        d.ellipse([x - 11, y - 56 - fh * 1.6, x + 11, y - 50], fill=(255, 185, 60))
        d.ellipse([x - 5, y - 56 - fh, x + 5, y - 54], fill=(255, 250, 225))


# ---------------------------------------------------------------- typography


def serif_text(xy, s, size, fill, shadow=CRIMSON):
    text(xy, s, size, fill, FONT_SERIF, shadow=shadow)


def ptext(t, at, xy, s, size, fill=CREAM, fnt=FONT_SERIF, shadow=None, until=None):
    if t < at or (until is not None and t >= until):
        return
    size = fit_size(s, size, fnt)
    text(xy, s, size * pop(t, at), fill, fnt, shadow)


def book_title(t, small, big, col=GOLD):
    ptext(t, 0.0, (W / 2, 172), small, 50, ROSE)
    slam(t, 0.05, (W / 2, 268), big, 112, col, FONT_SERIF, shadow=CRIMSON, strength=16, sound="bell")


def scroll(t, at, until, s, y=430, size=52):
    """Parchment scroll caption."""
    if t < at or t >= until:
        return
    size = fit_size(s, size, FONT_SERIF, W - 200)
    yy = y + (1 - ease_out_cubic((t - at) / 0.18)) * 50
    f = font(FONT_SERIF, size)
    sp = int(size * 0.2)
    d = G.draw
    bb = d.multiline_textbbox((W / 2, yy), s, font=f, anchor="mm", align="center", spacing=sp)
    r = [bb[0] - 44, bb[1] - 26, bb[2] + 44, bb[3] + 26]
    d.rectangle([r[0] + 12, r[1] + 12, r[2] + 12, r[3] + 12], fill=BLACK)
    d.rectangle(r, fill=CREAM, outline=GOLD_D, width=6)
    d.rectangle([r[0] + 10, r[1] + 10, r[2] - 10, r[3] - 10], outline=GOLD_D, width=2)
    for x in (r[0], r[2]):
        d.ellipse([x - 22, r[1] - 8, x + 22, r[3] + 8], fill=(228, 205, 160), outline=GOLD_D, width=5)
        d.ellipse([x - 8, r[1] + 6, x + 8, r[3] - 6], outline=GOLD_D, width=3)
    d.multiline_text((W / 2, yy), s, font=f, fill=INK, anchor="mm", align="center", spacing=sp)


# ---------------------------------------------------------------- math tokens
# str | ("p", base, exp) | ("r", radicand[, index]) | ("rc", coef, radicand) | ("f", num, den)


def str_col(s):
    if any(c.isalpha() for c in s) and len(s) <= 4:
        return SKY
    if any(c.isdigit() for c in s):
        return GOLD
    return WHITE


def tok_w(it, s):
    if isinstance(it, str):
        return font(FONT_MATH, s).getlength(it)
    k = it[0]
    if k == "p":
        return font(FONT_MATH, s).getlength(it[1]) + font(FONT_MATH, s * 0.58).getlength(it[2]) + s * 0.05
    if k == "r":
        return s * 0.55 + font(FONT_MATH, s).getlength(it[1]) + s * 0.12
    if k == "rc":
        return font(FONT_MATH, s).getlength(it[1]) + s * 0.04 + tok_w(("r", it[2]), s)
    f = font(FONT_MATH, s * 0.72)
    return max(f.getlength(it[1]), f.getlength(it[2])) + s * 0.34


def _str(x, y, s, size, col):
    G.draw.text((x, y), s, font=font(FONT_MATH, size), fill=col, stroke_width=stroke_for(size),
                stroke_fill=BLACK, anchor="lm")


def tok_draw(x, y, it, s):
    if isinstance(it, str):
        _str(x, y, it, s, str_col(it))
        return
    k = it[0]
    if k == "p":
        _str(x, y, it[1], s, str_col(it[1]))
        _str(x + font(FONT_MATH, s).getlength(it[1]) + s * 0.03, y - s * 0.42, it[2], s * 0.58, ROSE)
    elif k == "r":
        wr = font(FONT_MATH, s).getlength(it[1])
        x0 = x + 0.03 * s
        pts = [(x0, y + 0.02 * s), (x0 + 0.1 * s, y - 0.04 * s), (x0 + 0.25 * s, y + 0.42 * s),
               (x0 + 0.45 * s, y - 0.6 * s), (x + 0.55 * s + wr + 0.08 * s, y - 0.6 * s)]
        lw = max(3, int(s * 0.08))
        G.draw.line(pts, fill=BLACK, width=lw + 7, joint="curve")
        G.draw.line(pts, fill=WHITE, width=lw, joint="curve")
        if len(it) > 2 and it[2]:
            text((x0 + 0.13 * s, y - 0.3 * s), it[2], s * 0.36, ROSE, FONT_MATH)
        _str(x + 0.55 * s, y, it[1], s, str_col(it[1]))
    elif k == "rc":
        _str(x, y, it[1], s, GOLD)
        tok_draw(x + font(FONT_MATH, s).getlength(it[1]) + s * 0.04, y, ("r", it[2]), s)
    else:
        w = tok_w(it, s)
        cx = x + w / 2
        text((cx, y - s * 0.44), it[1], s * 0.72, GOLD, FONT_MATH)
        text((cx, y + s * 0.48), it[2], s * 0.72, GOLD, FONT_MATH)
        lw = max(4, int(s * 0.08))
        G.draw.line([(x + s * 0.08, y), (x + w - s * 0.08, y)], fill=BLACK, width=lw + 7)
        G.draw.line([(x + s * 0.08, y), (x + w - s * 0.08, y)], fill=GOLD, width=lw)


def mrow(t, at, y, items, answer=None, t_ans=None, size=110, until=None, cx=W / 2, sound="ding"):
    if answer is not None:
        impact(t, t_ans + 0.1, 24, sound)
    if t < at or (until is not None and t >= until):
        return
    gap = 0.2
    allit = items + ([answer] if answer is not None else [])

    def total(sz):
        return sum(tok_w(i, sz) for i in allit) + sz * gap * (len(allit) - 1)

    tw = total(size)
    if tw > W - 110:
        size *= (W - 110) / tw
    size *= pop(t, at)
    if size < 8:
        return
    x = cx - total(size) / 2
    for it in items:
        tok_draw(x, y, it, size)
        x += tok_w(it, size) + size * gap
    if answer is None:
        return
    slot = x + tok_w(answer, size) / 2
    if t < t_ans:
        text((slot, y), "?", size * (1 + 0.12 * math.sin(t * 14)), ROSE, FONT_MATH)
    else:
        s2 = size * (2.3 - 1.3 * ease_out_cubic((t - t_ans) / 0.1))
        tok_draw(slot - tok_w(answer, s2) / 2, y, answer, s2)


# ---------------------------------------------------------------- props


def saint(x, y, t, r, mood="happy"):
    """Kazu with a gilded halo."""
    if r < 4:
        return
    hy, hr = y - 0.35 * r, 1.3 * r
    d = G.draw
    d.ellipse([x - hr - 6, hy - hr - 6, x + hr + 6, hy + hr + 6], fill=BLACK)
    d.ellipse([x - hr, hy - hr, x + hr, hy + hr], fill=GOLD_D)
    d.ellipse([x - hr * 0.88, hy - hr * 0.88, x + hr * 0.88, hy + hr * 0.88], fill=(255, 238, 170))
    for i in range(16):
        a = t * 0.8 + i * math.pi / 8
        d.line([(x + math.cos(a) * hr * 0.6, hy + math.sin(a) * hr * 0.6),
                (x + math.cos(a) * hr * 0.86, hy + math.sin(a) * hr * 0.86)], fill=GOLD, width=4)
    kazu(x, y, GOLD, t, r, 1, 0, mood)


def candle_row(t, at, n, y=1110, step=175):
    """Votive candles that light one by one (one per multiplication)."""
    x0 = W / 2 - step * (n - 1) / 2
    for i in range(n):
        cue("bell", at + i * 0.6)
    d = G.draw
    for i in range(n):
        x = x0 + i * step
        a = at + i * 0.6
        k = pop(t, 0.0)
        d.rounded_rectangle([x - 50 * k, y - 60, x + 50 * k, y + 60], 16, fill=(60, 20, 40), outline=BLACK, width=5)
        if t >= a:
            d.rounded_rectangle([x - 44, y - 54, x + 44, y + 54], 12, fill=CRIMSON)
            fh = 44 * pop(t, a) * (1 + 0.15 * math.sin(t * 23 + i))
            d.ellipse([x - 15, y - 62 - fh * 1.5, x + 15, y - 58], fill=(255, 185, 60), outline=BLACK, width=3)
            d.ellipse([x - 6, y - 62 - fh, x + 6, y - 62], fill=(255, 250, 225))
            text((x, y + 110), str(2 ** (i + 1)), 56 * pop(t, a), GOLD, FONT_MATH)
            if i:
                text((x - step / 2, y + 110), "×2", 34 * pop(t, a), ROSE, FONT_MATH)
        d.ellipse([x - 44, y - 64, x + 44, y - 50], fill=CREAM, outline=BLACK, width=3)


def tiles(t, at, cx, cy, side, n, until=None):
    """n x n stained-glass square."""
    if until is not None and t >= until:
        return
    c = side / n
    for i in range(n * n):
        cue("pop", at + i * 0.08)
        a = at + i * 0.08
        if t < a:
            continue
        r, q = divmod(i, n)
        k = pop(t, a) * 0.46
        x, y = cx - side / 2 + (q + 0.5) * c, cy - side / 2 + (r + 0.5) * c
        col = tuple(min(255, int(v * 1.35)) for v in JEWELS[(i * 3) % len(JEWELS)])
        G.draw.rectangle([x - c * k, y - c * k, x + c * k, y + c * k], fill=col, outline=BLACK, width=7)
    la = at + n * n * 0.08 + 0.2
    if t >= la:
        text((cx, cy + side / 2 + 50), str(n), 64 * pop(t, la), ROSE, FONT_MATH)
        text((cx - side / 2 - 50, cy), str(n), 64 * pop(t, la), ROSE, FONT_MATH)


def panel(t, at, py, numeral, title):
    cue("bell", at)
    if t < at:
        return
    k = ease_out_back((t - at) / 0.3)
    x0, x1 = W / 2 - 480 * k, W / 2 + 480 * k
    if x1 - x0 < 80:
        return
    d = G.draw
    d.rounded_rectangle([x0 + 10, py - 135 + 10, x1 + 10, py + 135 + 10], 24, fill=BLACK)
    d.rounded_rectangle([x0, py - 135, x1, py + 135], 24, fill=(45, 12, 30), outline=GOLD, width=7)
    d.rounded_rectangle([x0 + 12, py - 123, x1 - 12, py + 123], 18, outline=GOLD_D, width=2)
    d.ellipse([x0 + 34, py - 48, x0 + 130, py + 48], fill=CRIMSON, outline=GOLD, width=5)
    text((x0 + 82, py + 2), numeral, 46, GOLD, FONT_SERIF)
    text((W / 2 + 50, py - 84), title, fit_size(title, 46, FONT_SERIF, 760) * min(1, k), CREAM, FONT_SERIF)


# ---------------------------------------------------------------- scenes


def s_hook(t):
    chapel("hook", t, rc=(W / 2, 760), ray_alpha=70, speed=0.35)
    slam(t, 0.2, (W / 2, 600), "EXPONENTS", 140, GOLD, FONT_SERIF, shadow=CRIMSON, sound="choir")
    ptext(t, 0.6, (W / 2, 735), "&", 90, CREAM)
    slam(t, 0.9, (W / 2, 870), "RADICALS", 140, GOLD, FONT_SERIF, shadow=CRIMSON)
    mrow(t, 1.8, 1090, [("p", "2", "10"), "="], "1024", 2.6, size=130, sound="choir")
    ptext(t, 3.3, (W / 2, 1290), "EPISODE 3 · THE ASCENSION ARC", 54, CREAM)
    ptext(t, 3.9, (W / 2, 1370), "~ ad astra per exponentes ~", 40, ROSE)
    if t >= 3.0:
        saint(W / 2, 1540, t, 50 * pop(t, 3.0))


def s_power(t):
    chapel("blue", t)
    book_title(t, "LIBER I", "THE POWER")
    scroll(t, 0.3, 6.6, "Exponent = REPEATED multiplication", y=410)
    mrow(t, 0.3, 610, [("p", "2", "5")], size=170)
    ptext(t, 1.0, (W / 2, 775), "BASE (2) = what you multiply", 52, GOLD, until=6.6)
    ptext(t, 1.6, (W / 2, 855), "EXPONENT (5) = how many times", 52, ROSE, until=6.6)
    if t < 6.6:
        candle_row(t, 2.5, 5)
    mrow(t, 2.4, 1390, ["2·2·2·2·2", "="], "32", 5.6, size=90, until=6.6)
    # the classic mistake
    mrow(t, 6.8, 900, [("p", "2", "5"), "≠", "2 × 5"], size=120)
    impact(t, 7.6, 36, "big", 0.8)
    if t >= 7.6:
        rot_text((W / 2, 1100), "HERESY!", 140 * pop(t, 7.6, 0.2), 10, CRIMSON, FONT_SERIF)
    ptext(t, 8.4, (W / 2, 1300), "32 vs 10. Not even close.", 56, CREAM)
    scroll(t, 6.6, 11.0, "Never multiply base × exponent!", y=410)


def s_ladder(t):
    chapel("violet", t)
    book_title(t, "LIBER II", "THE STAIRWAY")
    vals = [("3", "8"), ("2", "4"), ("1", "2"), ("0", "1"), ("−1", ("f", "1", "2")), ("−2", ("f", "1", "4"))]
    times = [0.4, 1.0, 1.6, 3.0, 6.0, 7.0]
    d = G.draw
    for i, ((e, v), at) in enumerate(zip(vals, times)):
        y = 560 + i * 140
        cx = W / 2 - 170 + i * 62
        if t >= at:
            k = ease_out_cubic((t - at) / 0.25)
            d.rectangle([cx - 210 * k, y + 60, cx + 210 * k, y + 72], fill=GOLD, outline=BLACK, width=3)
            if i:
                ptext(t, at, (cx + 290, y - 70), "÷2 ↓", 38, ROSE, FONT_MATH)
        mrow(t, at, y, [("p", "2", e), "="], v, at + 0.45, size=84, cx=cx,
             sound="choir" if e == "0" else "ding")
    scroll(t, 0.3, 3.0, "Each step DOWN = ÷ 2", y=420)
    scroll(t, 3.0, 5.8, "So ANYTHING⁰ = 1  (not 0!)", y=420)
    scroll(t, 5.8, 9.2, "Keep going → NEGATIVE exponents", y=420)
    scroll(t, 9.2, 13.0, "Negative exponent = FLIP it", y=420)
    mrow(t, 9.4, 1480, [("p", "2", "−2"), "=", ("f", "1", "2²"), "="], ("f", "1", "4"), 10.6, size=90)


def s_laws(t):
    chapel("red", t)
    ptext(t, 0.0, (W / 2, 172), "LEX EXPONENTIUM", 50, ROSE)
    slam(t, 0.05, (W / 2, 268), "THE 3 COMMANDMENTS", 96, GOLD, FONT_SERIF, shadow=CRIMSON, strength=16, sound="bell")
    laws = [(590, "I", "× same base → ADD the exponents", [("p", "x", "2"), "·", ("p", "x", "3"), "="],
             ("p", "x", "5"), "(x·x)(x·x·x) = five x's", 0.5),
            (900, "II", "÷ same base → SUBTRACT the exponents", [("p", "x", "5"), "÷", ("p", "x", "2"), "="],
             ("p", "x", "3"), "5 − 2 = 3", 5.0),
            (1210, "III", "power of a power → MULTIPLY them", [("p", "(x²)", "3"), "="],
             ("p", "x", "6"), "2 × 3 = 6", 9.5)]
    for py, num, title, items, ans, sub, at in laws:
        panel(t, at, py, num, title)
        mrow(t, at + 0.4, py + 8, items, ans, at + 1.7, size=84, cx=W / 2 + 50)
        ptext(t, at + 2.1, (W / 2 + 50, py + 104), sub, 32, ROSE, FONT_MATH)
    slam(t, 13.0, (W / 2, 1450), "SAME BASE ONLY!", 76, GOLD, FONT_SERIF, shadow=CRIMSON, strength=20)


def s_roots(t):
    chapel("green", t)
    book_title(t, "LIBER III", "THE ROOT")
    scroll(t, 0.3, 3.0, "√ UNDOES a square.", y=420)
    tiles(t, 0.6, W / 2, 760, 320, 3, until=6.0)
    mrow(t, 2.2, 1090, [("p", "3", "2"), "=", "9"], size=90, until=6.0)
    mrow(t, 3.0, 1240, [("r", "9"), "="], "3", 4.2, size=100, until=6.0)
    scroll(t, 3.0, 6.0, "Ask: what number × ITSELF = 9?", y=420)
    for i, (rad, ans, at) in enumerate((("25", "5", 6.2), ("49", "7", 7.0), ("100", "10", 7.8))):
        mrow(t, at, 600 + i * 140, [("r", rad), "="], ans, at + 0.6, size=88)
    scroll(t, 6.0, 9.6, "Perfect squares = instant roots", y=420)
    mrow(t, 9.8, 1080, [("r", "8", "3"), "="], "2", 11.2, size=110)
    ptext(t, 11.6, (W / 2, 1240), "because 2·2·2 = 8", 50, CREAM)
    scroll(t, 9.6, 14.0, "Little 3 = CUBE root (× itself 3 times)", y=420)


def s_simplify(t):
    chapel("teal", t)
    book_title(t, "LIBER IV", "SIMPLIFY")
    scroll(t, 0.3, 3.2, "Pull out the PERFECT square", y=420)
    mrow(t, 0.5, 600, [("r", "50")], size=110)
    mrow(t, 1.4, 760, ["=", ("r", "25·2")], size=100)
    mrow(t, 2.4, 920, ["=", ("r", "25"), "·", ("r", "2")], size=100)
    mrow(t, 3.4, 1080, ["="], ("rc", "5", "2"), 4.4, size=110, sound="choir")
    scroll(t, 3.2, 6.2, "√25 = 5 escapes → 5√2", y=420)
    scroll(t, 6.2, 11.0, "SECRET: roots are exponents in disguise", y=420)
    mrow(t, 6.5, 1270, [("r", "x"), "="], ("p", "x", "½"), 7.6, size=110, sound="choir")
    mrow(t, 8.4, 1450, [("p", "x", "½"), "·", ("p", "x", "½"), "=", ("p", "x", "1")], size=72)
    ptext(t, 9.0, (W / 2, 1560), "(Commandment I: ½ + ½ = 1)", 40, ROSE)


def s_speed_intro(t):
    chapel("red", t, rc=(W / 2, 760), ray_alpha=70, speed=0.4)
    slam(t, 0.1, (W / 2, 700), "SPEED\nROUND", 180, GOLD, FONT_SERIF, shadow=CRIMSON, strength=34, sound="big")
    ptext(t, 0.9, (W / 2, 1040), "4 questions · 3 seconds each", 58, CREAM)
    ptext(t, 1.4, (W / 2, 1130), "(pause if you need to — no judgment)", 42, ROSE)


def make_q(n, items, answer, expl):
    def scene(t):
        chapel("mixed", t, rc=(W / 2, 700), ray_alpha=55, speed=0.2)
        ptext(t, 0.0, (W / 2, 330), f"Q{n}/4", 84, GOLD, shadow=CRIMSON)
        mrow(t, 0.1, 680, items, answer, 3.6, size=130)
        if 0.6 <= t < 3.6:
            left = 3.6 - t
            cx, cy, r = W / 2, 1030, 120
            G.draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLACK, outline=(90, 60, 40), width=18)
            G.draw.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * (left % 1 or 1), fill=GOLD, width=18)
            text((cx, cy), str(math.ceil(left)), 130 * (1 + 0.25 * (1 - (left % 1))), CREAM, FONT_MATH)
        for k in range(3):
            cue("tick", 0.6 + k)
        if t >= 3.7:
            saint(W / 2, 1060 + math.sin(t * 6) * 6, t, KR * 1.4 * pop(t, 3.7))
        scroll(t, 3.9, 6.4, expl, y=1320, size=50)
    return scene


def s_outro(t):
    chapel("mixed", t)
    slam(t, 0.1, (W / 2, 262), "CHEAT SHEET", 120, GOLD, FONT_SERIF, shadow=CRIMSON, strength=18, sound="choir")
    cards = [("aⁿ = a × a × a …  (n times)", GOLD, 0.6),
             ("a⁰ = 1       a⁻ⁿ = 1 / aⁿ", ROSE, 1.3),
             ("×: ADD    ÷: SUBTRACT    ( )ⁿ: MULTIPLY", SKY, 2.0),
             ("√ undoes ²      √x = x^(1/2)", CREAM, 2.7)]
    for i, (s, col, at) in enumerate(cards):
        cue("bell", at)
        if t < at:
            continue
        k = ease_out_back((t - at) / 0.3)
        y = 470 + i * 160
        x0 = W / 2 - 480 * k
        if W - 2 * x0 < 80:
            continue
        G.draw.rounded_rectangle([x0 + 10, y - 60 + 10, W - x0 + 10, y + 60 + 10], 24, fill=BLACK)
        G.draw.rounded_rectangle([x0, y - 60, W - x0, y + 60], 24, fill=(45, 12, 30), outline=col, width=7)
        text((W / 2, y), s, fit_size(s, 46, FONT_MATH, 860) * min(1, k), col, FONT_MATH)
    if t >= 3.3:
        saint(W / 2, 1200 + math.sin(t * 5) * 6, t, KR * 1.3 * pop(t, 3.3))
    slam(t, 4.0, (W / 2, 1380), "Amen. Save this.", 80, GOLD, FONT_SERIF, shadow=CRIMSON, strength=14)
    ptext(t, 5.0, (W / 2, 1480), "Next: EP.4 — THE ALGEBRA ARC", 54, CREAM)
    ptext(t, 5.8, (W / 2, 1560), "Comment your speed-round score ↓", 44, ROSE)


SCENES = [
    (5.0, s_hook),
    (11.0, s_power),
    (13.0, s_ladder),
    (16.0, s_laws),
    (14.0, s_roots),
    (11.0, s_simplify),
    (2.5, s_speed_intro),
    (6.4, make_q(1, [("p", "3", "4"), "="], "81", "3·3·3·3 = 81")),
    (6.4, make_q(2, [("p", "7", "0"), "="], "1", "Anything to the power 0 = 1")),
    (6.4, make_q(3, [("p", "x", "3"), "·", ("p", "x", "4"), "="], ("p", "x", "7"), "Same base, × → ADD: 3 + 4 = 7")),
    (6.4, make_q(4, [("r", "144"), "="], "12", "12 × 12 = 144")),
    (9.5, s_outro),
]

# ---------------------------------------------------------------- sound: organ, choir, bells over the beat

SR = E.SR


def _tt(d):
    return np.arange(int(d * SR)) / SR


def _choir(freqs, d):
    x = _tt(d)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * x)
    y = np.zeros_like(x)
    for f in freqs:
        for det in (-0.003, 0.0, 0.004):
            ph = 2 * np.pi * f * (1 + det) * np.cumsum(vib) / SR
            y += np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.35 * np.sin(3 * ph) + 0.2 * np.sin(4 * ph)
    env = np.minimum(1, x / 0.3) * np.minimum(1, (d - x) / 0.4)
    return y * env / (len(freqs) * 3)


def _bell(f, d=2.2):
    x = _tt(d)
    parts = [(0.5, 0.6, 1.2), (1, 1, 1.8), (1.19, 0.5, 2.5), (1.5, 0.4, 3), (2, 0.35, 3.5), (2.51, 0.2, 5), (3, 0.15, 6)]
    y = sum(a * np.sin(2 * np.pi * f * r * x) * np.exp(-x * dc) for r, a, dc in parts)
    return y * np.minimum(1, x / 0.003) / 2


def extra_sfx(sr):
    return {"bell": (_bell(392), 0.35), "choir": (_choir([293.66, 369.99, 440.0, 587.33], 1.6) + 0.5 * _bell(587.33, 1.6), 0.6)}


def music_fn(n):
    out = np.zeros(n)
    rng = np.random.default_rng(5)
    total = E.TOTAL

    def add(sig, t, g):
        i = int(t * SR)
        if i < n:
            j = min(n, i + len(sig))
            out[i:j] += sig[: j - i] * g

    def organ(freqs, d):
        x = _tt(d)
        y = sum(a * np.sin(2 * np.pi * f * h * x) for f in freqs
                for h, a in ((1, 1), (2, 0.6), (3, 0.35), (4, 0.3), (6, 0.15), (8, 0.12)))
        return y * np.minimum(1, x / 0.08) * np.minimum(1, (d - x) / 0.15) / len(freqs)

    def chime(f, d=0.9):
        x = _tt(d)
        return (np.sin(2 * np.pi * f * x) * np.exp(-x * 3) + 0.5 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 6)
                + 0.25 * np.sin(2 * np.pi * f * 5.4 * x) * np.exp(-x * 9))

    def noise(d, hp=False):
        z = rng.standard_normal(int(d * SR))
        return np.diff(z, prepend=0) / 2 if hp else z

    x = _tt(0.35)
    kick = np.sin(2 * np.pi * np.cumsum(45 + 120 * np.exp(-x * 28)) / SR) * np.exp(-x * 9)
    x = _tt(0.2)
    snare = 0.6 * noise(0.2) * np.exp(-x * 22) * 0.5 + 0.4 * np.sin(2 * np.pi * 190 * x) * np.exp(-x * 30)
    x = _tt(0.05)
    hat = noise(0.05, True) * np.exp(-x * 90)

    # intro: cathedral organ swell + choir, bell toll
    dm = [146.83, 174.61, 220.0, 293.66]
    x = _tt(5.0)
    add(organ(dm + [73.42], 5.0) * np.minimum(1, x / 2.0), 0, 0.5)
    add(_choir(dm, 5.0), 0, 0.35)
    for k in range(3):
        add(_bell(196.0), 0.1 + k * 1.6, 0.4)

    beat = 60 / 140
    bars = [(73.42, [146.83, 174.61, 220.0]), (58.27, [116.54, 146.83, 174.61]),
            (87.31, [174.61, 220.0, 261.63]), (65.41, [130.81, 164.81, 196.0])]
    arp = [0, 1, 2, 1, 0, 2, 1, 2]
    t, bar = 5.0, 0
    while t < total:
        root, tones = bars[bar % 4]
        bl = 4 * beat
        add(organ(tones, bl), t, 0.22)
        add(_choir(tones, bl), t, 0.12)
        for b in range(4):
            tb = t + b * beat
            add(kick, tb, 0.9)
            if b in (1, 3):
                add(snare, tb, 0.55)
            for h in (0, 0.5):
                add(hat, tb + h * beat, 0.15 if h == 0 else 0.25)
                xb = _tt(0.2)
                add((np.sin(2 * np.pi * root * xb) + 0.4 * np.sin(4 * np.pi * root * xb)) * np.exp(-xb * 6),
                    tb + h * beat, 0.35)
        for q in range(8):
            add(chime(tones[arp[q]] * 4), t + q * beat / 2, 0.06)
        t += bl
        bar += 1
    fade = int(1.5 * SR)
    end = int(total * SR)
    out[end - fade:end] *= np.linspace(1, 0, fade)
    out[end:] = 0
    return out


if __name__ == "__main__":
    E.main("the_ascension_arc.mp4", SCENES, music_fn, extra_sfx)
