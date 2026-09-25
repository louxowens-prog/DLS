#!/usr/bin/env python3
"""Render "THE ± ARC": a <2 min vertical (9:16) anime-style short teaching
arithmetic with positive and negative numbers.

Everything (frames, music, sound effects) is generated procedurally.

    pip install pillow numpy imageio-ffmpeg
    python3 make_video.py                 # full render -> out/the_plus_minus_arc.mp4
    python3 make_video.py --preview 3 17  # dump frames at t=3s and t=17s to out/preview/
"""
import math
import os
import subprocess
import sys
import wave

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "out")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

FONT_TITLE = "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"
FONT_MATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_JP = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

WHITE = (255, 255, 255)
BLACK = (12, 10, 22)
GOLD = (255, 204, 40)
LAV = (196, 138, 255)      # "shadow" purple, light enough to read on dark bgs
PURPLE = (150, 70, 255)
CYAN = (70, 235, 255)
PINK = (255, 60, 150)
RED = (235, 40, 60)
MINUS = "−"

# ---------------------------------------------------------------- helpers

class G:
    """Per-frame drawing context."""
    img = None
    draw = None
    fi = 0
    t0 = 0.0          # start time of the current scene (global seconds)
    shake = 0.0
    flash = 0.0
    invert = False


CUES = set()          # (global_time, kind) sound-effect cues collected while rendering


def cue(kind, at):
    CUES.add((round(G.t0 + at, 3), kind))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_cubic(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out_back(x, s=1.9):
    x = clamp(x) - 1
    return 1 + x * x * ((s + 1) * x + s)


def pop(t, at, d=0.3):
    return 0.0 if t < at else ease_out_back((t - at) / d)


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def fmt(v):
    return f"{MINUS}{-v}" if v < 0 else str(v)


def sign_color(v):
    if v >= 0:
        return mix((235, 235, 255), GOLD, clamp(v / 0.8))
    return mix((235, 235, 255), PURPLE, clamp(-v / 0.8))


_fonts = {}


def font(path, size):
    key = (path, max(8, int(size)))
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, key[1])
    return _fonts[key]


def stroke_for(size):
    return max(3, int(size * 0.075))


def fit_size(s, size, fnt, maxw=W - 90):
    f = font(fnt, size)
    bb = G.draw.multiline_textbbox((0, 0), s, font=f, stroke_width=stroke_for(size), spacing=int(size * 0.2))
    w = bb[2] - bb[0]
    return size * maxw / w if w > maxw else size


def text(xy, s, size, fill=WHITE, fnt=FONT_TITLE, shadow=None, stroke=None, anchor="mm"):
    if size < 8:
        return
    f = font(fnt, size)
    sw = stroke_for(size) if stroke is None else stroke
    kw = dict(font=f, stroke_width=sw, stroke_fill=BLACK, anchor=anchor, align="center", spacing=int(size * 0.2))
    if shadow:
        off = max(4, int(size * 0.06))
        G.draw.multiline_text((xy[0] + off, xy[1] + off), s, fill=shadow, **kw)
    G.draw.multiline_text(xy, s, fill=fill, **kw)


def ptext(t, at, xy, s, size, fill=WHITE, fnt=FONT_TITLE, shadow=None, until=None):
    """Text that pops in (overshoot) at `at` and vanishes at `until`."""
    if t < at or (until is not None and t >= until):
        return
    size = fit_size(s, size, fnt)
    text(xy, s, size * pop(t, at), fill, fnt, shadow)


def impact(t, at, strength=26, sound="boom", flash=0.55):
    cue(sound, at)
    dt = t - at
    if 0 <= dt < 0.4:
        G.shake = max(G.shake, strength * (1 - dt / 0.4))
    if 0 <= dt < 0.1:
        G.flash = max(G.flash, flash * (1 - dt / 0.1))


def slam(t, at, xy, s, size, fill=WHITE, fnt=FONT_TITLE, shadow=PINK, strength=26, sound="boom", until=None):
    """Text that crashes down from huge to normal size with a screen shake."""
    impact(t, at + 0.12, strength, sound)
    if t < at or (until is not None and t >= until):
        return
    size = fit_size(s, size, fnt)
    k = ease_out_cubic((t - at) / 0.12)
    text(xy, s, size * (2.4 - 1.4 * k), fill, fnt, shadow)


_rot_cache = {}


def rot_text(xy, s, size, angle, fill, fnt=FONT_JP):
    key = (s, int(size), int(angle), fill, fnt)
    if key not in _rot_cache:
        f = font(fnt, size)
        sw = stroke_for(size) + 3
        tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        bb = tmp.multiline_textbbox((0, 0), s, font=f, stroke_width=sw, spacing=0)
        w, h = bb[2] - bb[0] + 40, bb[3] - bb[1] + 40
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(layer).multiline_text((w / 2, h / 2), s, font=f, fill=fill, stroke_width=sw,
                                             stroke_fill=BLACK, anchor="mm", align="center", spacing=0)
        _rot_cache[key] = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    layer = _rot_cache[key]
    G.img.paste(layer, (int(xy[0] - layer.width / 2), int(xy[1] - layer.height / 2)), layer)


def star(x, y, s, col):
    q = s * 0.22
    G.draw.polygon([(x, y - s), (x + q, y - q), (x + s, y), (x + q, y + q),
                    (x, y + s), (x - q, y + q), (x - s, y), (x - q, y - q)], fill=col)


def caption(t, at, until, s, y=440, box=WHITE, size=54):
    """Manga speech-box caption."""
    if t < at or t >= until:
        return
    size = fit_size(s, size, FONT_TITLE, W - 170)
    a = ease_out_cubic((t - at) / 0.18)
    yy = y + (1 - a) * 50
    f = font(FONT_TITLE, size)
    sp = int(size * 0.25)
    bb = G.draw.multiline_textbbox((W / 2, yy), s, font=f, anchor="mm", align="center", spacing=sp)
    pad = 32
    r = [bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad]
    G.draw.rounded_rectangle([r[0] + 12, r[1] + 12, r[2] + 12, r[3] + 12], 30, fill=BLACK)
    G.draw.rounded_rectangle(r, 30, fill=box, outline=BLACK, width=7)
    G.draw.multiline_text((W / 2, yy), s, font=f, fill=BLACK, anchor="mm", align="center", spacing=sp)


def eq_parts(spec):
    parts = []
    for i, tok in enumerate(spec.split(" ")):
        if i:
            parts.append((" ", WHITE))
        if tok.startswith("(" + MINUS) or (tok.startswith(MINUS) and len(tok) > 1):
            parts.append((tok, LAV))
        elif tok[0].isdigit():
            parts.append((tok, GOLD))
        else:
            parts.append((tok, WHITE))
    parts.append((" ", WHITE))
    return parts


def eqn(t, at, y, spec, answer, t_ans, size=120, until=None):
    """Equation that pops in, shows a pulsing '?', then slams the answer."""
    impact(t, t_ans + 0.1, 24, "ding")
    if t < at or (until is not None and t >= until):
        return
    parts = eq_parts(spec)
    f0 = font(FONT_MATH, size)
    total = sum(f0.getlength(s) for s, _ in parts) + f0.getlength(answer)
    if total > W - 100:
        size *= (W - 100) / total
        total = W - 100
    sc = pop(t, at)
    size *= sc
    f = font(FONT_MATH, size)
    x = W / 2 - total * sc / 2
    for s, c in parts:
        G.draw.text((x, y), s, font=f, fill=c, stroke_width=stroke_for(size), stroke_fill=BLACK, anchor="lm")
        x += f.getlength(s)
    slot = x + f.getlength(answer) / 2
    if t < t_ans:
        k = 1 + 0.12 * math.sin(t * 14)
        text((slot, y), "?", size * k, CYAN, FONT_MATH)
    else:
        k = ease_out_cubic((t - t_ans) / 0.1)
        col = LAV if answer.startswith(MINUS) else GOLD
        text((slot, y), answer, size * (2.3 - 1.3 * k), col, FONT_MATH, shadow=PINK)


# ---------------------------------------------------------------- backgrounds

PALETTES = {
    "hook": ((22, 0, 18), (105, 0, 45), (70, 0, 38)),
    "arena": ((8, 12, 48), (38, 12, 80), (32, 34, 96)),
    "add": ((4, 26, 40), (8, 70, 84), (18, 70, 90)),
    "sub": ((34, 6, 40), (92, 18, 72), (86, 26, 88)),
    "mul": ((14, 4, 40), (70, 10, 60), (60, 22, 90)),
    "tip": ((2, 34, 30), (10, 86, 66), (20, 90, 76)),
    "speed": ((40, 0, 10), (120, 20, 20), (110, 34, 34)),
}
_grads = {}
_rng = np.random.default_rng(7)
LINES = [(a, l, w) for a, l, w in zip(_rng.uniform(0, 2 * math.pi, 72), _rng.uniform(0.2, 1, 72), _rng.uniform(5, 20, 72))]
SPARKS = [(x, y, s, sp) for x, y, s, sp in zip(_rng.uniform(0, W, 26), _rng.uniform(0, H, 26),
                                                 _rng.uniform(6, 16, 26), _rng.uniform(40, 140, 26))]


def gradient(top, bot):
    a = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(top) * (1 - a) + np.array(bot) * a).astype(np.uint8)
    return Image.fromarray(np.broadcast_to(arr, (H, W, 3)).copy())


def bg(name, t, speed=1.0, cx=W / 2, cy=H * 0.42):
    top, bot, line = PALETTES[name]
    if name not in _grads:
        _grads[name] = gradient(top, bot)
    G.img = _grads[name].copy()
    G.draw = d = ImageDraw.Draw(G.img)
    for i, (ang, ln, wid) in enumerate(LINES):
        flick = (math.sin(t * 18 * speed + i * 1.7) + 1) / 2
        if flick < 0.3:
            continue
        a = ang + t * 0.12 * speed
        r0 = 330 + (1 - ln) * 520 + flick * 90
        ux, uy = math.cos(a), math.sin(a)
        px, py = -uy, ux
        tip = (cx + ux * r0, cy + uy * r0)
        far = 1600
        d.polygon([tip, (cx + ux * far + px * wid, cy + uy * far + py * wid),
                   (cx + ux * far - px * wid, cy + uy * far - py * wid)], fill=line)
    for x, y, s, sp in SPARKS:
        yy = (y - t * sp) % H
        tw = 0.6 + 0.4 * math.sin(t * 6 + x)
        star(x, yy, s * tw, mix(line, WHITE, 0.45))


# ---------------------------------------------------------------- number line + Kazu

NL_Y, NL_MIN, NL_MAX, NL_PAD = 1185, -8, 8, 80
KR = 58  # Kazu radius


def nx(v):
    return NL_PAD + (v - NL_MIN) / (NL_MAX - NL_MIN) * (W - 2 * NL_PAD)


def number_line(t, at=0.0, hi=None):
    p = ease_out_cubic((t - at) / 0.5)
    if p <= 0:
        return
    d = G.draw
    cx = W / 2
    half = (W / 2 - NL_PAD + 34) * p
    for x0, x1, col in ((cx - half, cx, PURPLE), (cx, cx + half, GOLD)):
        d.line([(x0, NL_Y), (x1, NL_Y)], fill=BLACK, width=20)
        d.line([(x0, NL_Y), (x1, NL_Y)], fill=col, width=10)
    if p >= 1:
        for s, col in ((-1, PURPLE), (1, GOLD)):
            xe = cx + s * (half + 16)
            d.polygon([(xe, NL_Y), (xe - s * 34, NL_Y - 22), (xe - s * 34, NL_Y + 22)], fill=col, outline=BLACK, width=4)
    for v in range(NL_MIN, NL_MAX + 1):
        x = nx(v)
        if abs(x - cx) > half:
            continue
        col = GOLD if v > 0 else LAV if v < 0 else WHITE
        h = 34 if v == 0 else 20
        d.line([(x, NL_Y - h), (x, NL_Y + h)], fill=BLACK, width=10)
        d.line([(x, NL_Y - h), (x, NL_Y + h)], fill=col, width=5)
        if hi is not None and v == hi:
            d.ellipse([x - 32, NL_Y + 58 - 32, x + 32, NL_Y + 58 + 32], fill=col, outline=BLACK, width=5)
            text((x, NL_Y + 58), fmt(v), 34, BLACK, FONT_MATH, stroke=0)
        else:
            text((x, NL_Y + 58), fmt(v), 32, col, FONT_MATH, stroke=4)


def arc_h(a, b):
    return min(210, 55 + 0.35 * abs(nx(b) - nx(a)))


def kstate(t, moves, v0):
    v, lift, face, moving, land, hop = v0, 0.0, 1, False, None, False
    for t0, t1, a, b, label, *_ in moves:
        if t < t0:
            break
        e = ease_in_out((t - t0) / (t1 - t0))
        v = a + (b - a) * e
        face = 1 if b >= a else -1
        hop = label is not None
        lift = 4 * arc_h(a, b) * e * (1 - e) if hop else 0.0
        moving = t < t1
        land = t1
    return v, lift, face, moving, land, hop


def move_arrow(t, m):
    t0, t1, a, b, label, col, clear = m
    if not label or t < t0 or t >= clear:
        return
    e = ease_in_out((t - t0) / (t1 - t0))
    xa, xb, h, y0 = nx(a), nx(b), arc_h(a, b), NL_Y - 12
    pts = [(xa + (xb - xa) * e * i / 40, y0 - 4 * h * (e * i / 40) * (1 - e * i / 40)) for i in range(41)]
    if e > 0.03:
        G.draw.line(pts, fill=BLACK, width=18, joint="curve")
        G.draw.line(pts, fill=col, width=9, joint="curve")
        (x1, y1), (x2, y2) = pts[-3], pts[-1]
        ln = math.hypot(x2 - x1, y2 - y1) or 1
        ux, uy = (x2 - x1) / ln, (y2 - y1) / ln
        s = 30
        G.draw.polygon([(x2 + ux * s * 0.6, y2 + uy * s * 0.6),
                        (x2 - ux * s - uy * s * 0.7, y2 - uy * s + ux * s * 0.7),
                        (x2 - ux * s + uy * s * 0.7, y2 - uy * s - ux * s * 0.7)], fill=col, outline=BLACK, width=4)
    text(((xa + xb) / 2, y0 - h - 2 * KR - 48), label, 66 * pop(t, t0), col, FONT_MATH, shadow=BLACK)


def kazu(x, y, col, t, r=KR, face=1.0, squash=0.0, mood="normal"):
    if r < 4:
        return
    d = G.draw
    fx = max(0.12, abs(face))
    fdir = 1 if face >= 0 else -1
    rx, ry = r * (1 + squash) * fx, r * (1 - squash)
    for i in (3, 2, 1):
        rr = r + (8 + i * 12 + 5 * math.sin(t * 12 + i * 2)) * r / KR
        d.ellipse([x - rr * (1 + squash), y - rr * (1 - squash), x + rr * (1 + squash), y + rr * (1 - squash)],
                  outline=mix(col, BLACK, 0.2 + 0.22 * i), width=5)
    # headband tails flutter behind
    by = y - 0.5 * ry
    tx = x - fdir * rx * 0.8
    wv = math.sin(t * 15) * 0.18 * r
    for dy, ln in ((-0.08, 1.0), (0.14, 0.8)):
        d.polygon([(tx, by + dy * r - 0.1 * r), (tx - fdir * ln * r, by + dy * r - 0.3 * r + wv),
                   (tx - fdir * ln * 0.92 * r, by + dy * r + 0.05 * r + wv), (tx, by + dy * r + 0.12 * r)],
                  fill=RED, outline=BLACK, width=4)
    d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=col, outline=BLACK, width=6)
    d.ellipse([x - 0.62 * rx, y - 0.78 * ry, x - 0.3 * rx, y - 0.62 * ry], fill=mix(col, WHITE, 0.65))
    d.rounded_rectangle([x - rx * 0.93, by - 0.14 * r, x + rx * 0.93, by + 0.14 * r], int(0.08 * r) + 1,
                        fill=RED, outline=BLACK, width=4)
    if fx > 0.5:
        pw = 0.24 * r * fx
        d.rectangle([x - pw, by - 0.11 * r, x + pw, by + 0.11 * r], fill=(210, 215, 230), outline=BLACK, width=3)
        text((x, by), "±", 0.22 * r, BLACK, FONT_MATH, stroke=0)
    if fx < 0.35:
        return  # mid-spin: seen edge-on
    ex = fdir * 0.12 * rx
    blink = (t % 3.3) < 0.09 and mood in ("normal", "determined")
    for i in (-1, 1):
        cx, cy = x + ex + i * 0.33 * rx, y + 0.06 * ry
        ew, eh = 0.12 * r * fx, 0.23 * r
        if mood == "happy":
            d.line([(cx - ew * 1.2, cy + 0.04 * r), (cx, cy - 0.1 * r), (cx + ew * 1.2, cy + 0.04 * r)], fill=BLACK, width=6, joint="curve")
        elif blink:
            d.line([(cx - ew, cy), (cx + ew, cy)], fill=BLACK, width=6)
        elif mood == "shock":
            d.ellipse([cx - ew, cy - eh, cx + ew, cy + eh], fill=WHITE, outline=BLACK, width=4)
            d.ellipse([cx - 0.04 * r, cy - 0.04 * r, cx + 0.04 * r, cy + 0.04 * r], fill=BLACK)
        else:
            d.ellipse([cx - ew, cy - eh, cx + ew, cy + eh], fill=BLACK)
            d.ellipse([cx - ew * 0.75, cy + eh * 0.1, cx + ew * 0.75, cy + eh * 0.85], fill=(40, 90, 200))
            d.ellipse([cx + 0.01 * r, cy - 0.16 * r, cx + 0.11 * r, cy - 0.06 * r], fill=WHITE)
            d.ellipse([cx - 0.07 * r, cy + 0.07 * r, cx - 0.02 * r, cy + 0.12 * r], fill=WHITE)
        if mood == "determined":
            d.line([(cx + i * 0.17 * r, cy - 0.4 * r), (cx - i * 0.1 * r, cy - 0.28 * r)], fill=BLACK, width=7)
        d.ellipse([cx + i * 0.12 * r - 0.1 * r, cy + 0.26 * r, cx + i * 0.12 * r + 0.1 * r, cy + 0.33 * r], fill=(255, 130, 170))
    mx, my = x + ex, y + 0.36 * ry
    if mood == "shock":
        d.ellipse([mx - 0.07 * r, my - 0.04 * r, mx + 0.07 * r, my + 0.14 * r], fill=BLACK)
    elif mood == "determined":
        d.line([(mx - 0.12 * r, my), (mx + 0.12 * r, my - 0.03 * r)], fill=BLACK, width=6)
    else:
        d.arc([mx - 0.13 * r, my - 0.1 * r, mx + 0.13 * r, my + 0.1 * r], 10, 170, fill=BLACK, width=6)
    if mood == "happy":
        for k in range(4):
            a = t * 3 + k * math.pi / 2
            star(x + math.cos(a) * r * 1.6, y + math.sin(a) * r * 1.3, 14 + 5 * math.sin(t * 9 + k), GOLD)


def kazu_on_line(t, moves, v0, appear=0.0, mood="normal", face=None):
    """Draw arrows + Kazu riding the number line. Returns Kazu's current value."""
    for t0, t1, *_ in moves:
        cue("whoosh", t0)
    for m in moves:
        move_arrow(t, m)
    if t < appear:
        return None
    v, lift, fdir, moving, land, hop = kstate(t, moves, v0)
    sq = 0.0
    if moving and hop:
        sq = -0.12
    elif land is not None and hop and 0 <= t - land < 0.25:
        sq = 0.3 * (1 - (t - land) / 0.25)
    x, y = nx(v), NL_Y - 12 - KR - lift
    if moving:
        for k in (3, 2, 1):
            gv, gl, *_ = kstate(t - 0.04 * k, moves, v0)
            gr = KR * (1 - 0.12 * k)
            d = G.draw
            d.ellipse([nx(gv) - gr, NL_Y - 12 - KR - gl - gr, nx(gv) + gr, NL_Y - 12 - KR - gl + gr],
                      outline=sign_color(gv), width=4)
    bob = 0 if moving else math.sin(t * 5) * 5
    kazu(x, y + bob, sign_color(v), t, KR * pop(t, appear), fdir if face is None else face, sq, mood)
    return v


def technique_title(t, small, big, col):
    ptext(t, 0.0, (W / 2, 168), small, 50, col)
    slam(t, 0.05, (W / 2, 262), big, 108, WHITE, shadow=col, strength=16)


def settled(t, moves, v0):
    v, _, _, moving, _, _ = kstate(t, moves, v0)
    return None if moving else int(round(v))


# ---------------------------------------------------------------- scenes

def s_hook(t):
    bg("hook", t, speed=2.2)
    for i, (x, y, a) in enumerate([(120, 470, 12), (960, 420, -10), (130, 1480, -8), (950, 1530, 10)]):
        if t > 0.1 + i * 0.12:
            j = math.sin(t * 60 + i) * 5
            rot_text((x + j, y - j), "ゴ\nゴ\nゴ", 92, a, LAV)
    slam(t, 0.25, (W / 2, 640), "NEGATIVE", 165, PINK, shadow=CYAN)
    slam(t, 0.6, (W / 2, 815), "NUMBERS", 165, WHITE, shadow=PINK)
    ptext(t, 1.35, (W / 2, 985), "are NOT your enemy.", 74, WHITE)
    if t >= 2.5:
        k = ease_out_cubic((t - 2.5) / 0.15)
        x0, x1 = W / 2 - 520 * k, W / 2 + 520 * k
        G.draw.polygon([(x0 + 40, 1130), (x1 + 40, 1130), (x1 - 40, 1275), (x0 - 40, 1275)], fill=BLACK, outline=GOLD, width=6)
    slam(t, 2.5, (W / 2, 1203), "MASTER ± IN 90 SEC", 86, GOLD, shadow=PINK)
    ptext(t, 3.5, (W / 2, 1385), "EPISODE 1 · THE ± ARC", 56, CYAN)


def s_arena(t):
    bg("arena", t, speed=0.8)
    moves = [(3.5, 4.2, 0, 3, "", GOLD, 99), (5.6, 6.5, 3, -3, "", LAV, 99)]
    number_line(t, 0.3, settled(t, moves, 0) if t > 0.9 else None)
    slam(t, 0.1, (W / 2, 250), "THE NUMBER LINE", 104, GOLD, shadow=PINK, strength=16)
    kazu_on_line(t, moves, 0, appear=0.7)
    ptext(t, 2.2, (nx(4.3), NL_Y + 150), "LIGHT (+) →", 52, GOLD)
    ptext(t, 2.4, (nx(-4.3), NL_Y + 150), "← SHADOW (" + MINUS + ")", 52, LAV)
    caption(t, 0.8, 3.4, "This is KAZU.\nZERO is home base.")
    caption(t, 3.4, 5.5, "RIGHT → numbers get BIGGER")
    caption(t, 5.5, 8.1, "LEFT → numbers get SMALLER\n(" + MINUS + "3 is LESS than " + MINUS + "1!)")


def s_add(t):
    bg("add", t)
    moves = [(1.3, 2.3, 3, 7, "+4", GOLD, 3.8), (3.75, 4.05, 7, 3, None, None, 0),
             (5.3, 6.6, 3, -2, MINUS + "5", LAV, 99)]
    technique_title(t, "TECHNIQUE 1", "ADDITION", CYAN)
    number_line(t, 0.0, settled(t, moves, 3))
    mood = "shock" if 6.1 <= t < 7.0 else "normal"
    kazu_on_line(t, moves, 3, appear=0.2, mood=mood)
    eqn(t, 0.3, 650, "3 + 4 =", "7", 2.4, until=3.8)
    eqn(t, 3.9, 650, "3 + (" + MINUS + "5) =", MINUS + "2", 6.8)
    if 6.1 <= t < 7.2:
        cue("pop", 6.1)
        rot_text((nx(-2) + 120, NL_Y - 260), "!?", 110, -12, CYAN)
    caption(t, 0.5, 3.8, "Adding a POSITIVE? Dash RIGHT →")
    caption(t, 3.9, 6.1, "Adding a NEGATIVE? Dash LEFT ←")
    caption(t, 6.1, 7.9, "Crossed ZERO → welcome to\nthe SHADOW REALM")
    caption(t, 7.9, 12.0, "+ positive → go RIGHT\n+ negative → go LEFT", y=1440, box=GOLD, size=56)


def s_sub(t):
    bg("sub", t)
    moves = [(1.2, 2.2, 6, 4, MINUS + "2", LAV, 3.6), (3.5, 3.8, 4, -2, None, None, 0),
             (4.8, 5.9, -2, -6, MINUS + "4", LAV, 7.2), (7.1, 7.4, -6, 5, None, None, 0),
             (10.1, 11.1, 5, 8, "+3", GOLD, 99)]
    technique_title(t, "TECHNIQUE 2", "SUBTRACTION", PINK)
    number_line(t, 0.0, settled(t, moves, 6))
    face = None
    if 9.0 <= t < 9.9:
        face = math.cos(2 * math.pi * (t - 9.0) / 0.9)   # two full turn-arounds
    cue("flip", 9.0)
    cue("flip", 9.45)
    kazu_on_line(t, moves, 6, appear=0.1, mood="determined" if t >= 7.3 else "normal", face=face)
    eqn(t, 0.3, 650, "6 " + MINUS + " 2 =", "4", 2.3, until=3.6)
    eqn(t, 3.7, 650, MINUS + "2 " + MINUS + " 4 =", MINUS + "6", 6.0, until=7.2)
    eqn(t, 7.3, 650, "5 " + MINUS + " (" + MINUS + "3) =", "8", 11.2)
    ptext(t, 9.9, (W / 2, 785), "= 5 + 3", 84, GOLD)
    if 7.4 <= t < 9.0:
        for i, (x, y, a) in enumerate([(110, 760, 10), (970, 760, -10)]):
            j = math.sin(t * 60 + i) * 5
            rot_text((x + j, y), "ゴ\nゴ\nゴ", 80, a, LAV)
    impact(t, 11.3, 40, "big", 0.9)
    G.invert = G.invert or 11.3 <= t < 11.37
    if 11.3 <= t < 13.2:
        rot_text((850, 900), "ドン!", 150 * pop(t, 11.3, 0.2), 14, GOLD)
    caption(t, 0.4, 3.6, "Subtracting a POSITIVE? Dash LEFT ←")
    caption(t, 3.7, 7.2, "Already negative? Go DEEPER\ninto the shadows")
    caption(t, 7.3, 9.0, "Minus a NEGATIVE?!")
    caption(t, 9.0, 11.3, "Two minuses = TWO flips\n→ facing RIGHT again!")
    caption(t, 11.4, 14.0, MINUS + " (" + MINUS + ") = +\nRemoving darkness = more LIGHT", y=1440, box=GOLD, size=56)


def sign_row(t, at, y, a, b, res, note):
    if t < at:
        return
    sc = pop(t, at)
    size = 90 * sc
    f = font(FONT_MATH, size)
    x = 60
    for s in (a, " × ", b, " = ", res):
        col = GOLD if s == "+" else LAV if s == MINUS else WHITE
        G.draw.text((x, y), s, font=f, fill=col, stroke_width=stroke_for(size), stroke_fill=BLACK, anchor="lm")
        x += f.getlength(s)
    col = GOLD if res == "+" else LAV
    text((830, y), note, 44 * sc, col, FONT_TITLE)


def s_mul(t):
    bg("mul", t)
    technique_title(t, "FINAL TECHNIQUE", "×  and  ÷", GOLD)
    caption(t, 0.4, 2.8, "No walking here.\nJust check the SIGNS.")
    rows = [("+", "+", "+", "friend of a friend\n= FRIEND", 1.0),
            (MINUS, MINUS, "+", "enemy of an enemy\n= FRIEND", 2.4),
            ("+", MINUS, MINUS, "friend of an enemy\n= ENEMY", 3.8),
            (MINUS, "+", MINUS, "enemy of a friend\n= ENEMY", 5.2)]
    for i, (a, b, res, note, at) in enumerate(rows):
        cue("pop", at)
        if t < 8.5:
            sign_row(t, at, 600 + i * 175, a, b, res, note)
    impact(t, 2.5, 14, "boom", 0.3)
    slam(t, 6.6, (W / 2, 1440), "SAME signs → +\nDIFFERENT signs → " + MINUS, 66, GOLD, shadow=PINK, strength=20)
    ex = [("(" + MINUS + "3) × (" + MINUS + "4) =", "12", 8.6), ("(" + MINUS + "3) × 4 =", MINUS + "12", 10.2),
          (MINUS + "20 ÷ 4 =", MINUS + "5", 11.8), (MINUS + "20 ÷ (" + MINUS + "4) =", "5", 13.4)]
    for i, (q, a, at) in enumerate(ex):
        eqn(t, at, 600 + i * 170, q, a, at + 1.0, size=96)


def s_tip(t):
    bg("tip", t)
    slam(t, 0.1, (W / 2, 290), "PRO TIP", 130, CYAN, shadow=PINK, strength=18)
    caption(t, 0.4, 5.0, "Lots of negatives? COUNT them.", y=470)
    ptext(t, 0.9, (W / 2, 690), "EVEN # of negatives → +", 70, GOLD)
    ptext(t, 1.5, (W / 2, 810), "ODD # of negatives → " + MINUS, 70, LAV)
    eqn(t, 2.1, 1030, "(" + MINUS + "1)×(" + MINUS + "1)×(" + MINUS + "1) =", MINUS + "1", 3.2, size=88)
    ptext(t, 3.4, (W / 2, 1170), "3 negatives = ODD → negative", 54, WHITE)


def s_speed_intro(t):
    bg("speed", t, speed=2.5)
    slam(t, 0.1, (W / 2, 700), "SPEED\nROUND", 190, GOLD, shadow=PINK, strength=34, sound="big")
    ptext(t, 0.9, (W / 2, 1040), "4 questions · 3 seconds each", 60, WHITE)
    ptext(t, 1.4, (W / 2, 1140), "(pause if you need to — no shame)", 44, CYAN)


def make_q(n, q, a, expl):
    def scene(t):
        bg("speed", t, speed=1.6)
        ptext(t, 0.0, (W / 2, 330), f"Q{n}/4", 84, CYAN, shadow=PINK)
        eqn(t, 0.1, 700, q, a, 3.6, size=130)
        if 0.6 <= t < 3.6:
            left = 3.6 - t
            cx, cy, r = W / 2, 1010, 120
            G.draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLACK, outline=(70, 70, 90), width=18)
            G.draw.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * (left % 1 or 1), fill=GOLD, width=18)
            text((cx, cy), str(math.ceil(left)), 130 * (1 + 0.25 * (1 - (left % 1))), WHITE, FONT_MATH)
        for k in range(3):
            cue("tick", 0.6 + k)
        if t >= 3.7:
            kazu(W / 2, 1010 + math.sin(t * 6) * 6, GOLD, t, KR * 1.5 * pop(t, 3.7), 1, 0, "happy")
        caption(t, 3.9, 6.6, expl, y=1290, size=52)
    return scene


def s_outro(t):
    bg("arena", t)
    slam(t, 0.1, (W / 2, 270), "CHEAT SHEET", 120, GOLD, shadow=PINK, strength=18)
    cards = [("ADD a negative → go LEFT ←", LAV, 0.7),
             ("SUBTRACT a negative → go RIGHT →", GOLD, 1.5),
             ("× ÷ :  SAME signs +,  DIFFERENT " + MINUS, CYAN, 2.3)]
    for i, (s, col, at) in enumerate(cards):
        cue("pop", at)
        if t < at:
            continue
        k = ease_out_back((t - at) / 0.3)
        y = 500 + i * 185
        x0 = W / 2 - 480 * k
        G.draw.rounded_rectangle([x0 + 10, y - 70 + 10, W - x0 + 10, y + 70 + 10], 26, fill=BLACK)
        G.draw.rounded_rectangle([x0, y - 70, W - x0, y + 70], 26, fill=(20, 16, 50), outline=col, width=7)
        text((W / 2, y), s, fit_size(s, 50, FONT_TITLE, 880) * k, col, FONT_TITLE)
    if t >= 3.0:
        kazu(W / 2, 1140 + math.sin(t * 5) * 6, GOLD, t, KR * 1.6 * pop(t, 3.0), 1, 0, "happy")
    slam(t, 3.8, (W / 2, 1345), "SAVE THIS for test day.", 72, WHITE, shadow=PINK, strength=14)
    ptext(t, 5.0, (W / 2, 1455), "Next: EP.2 — THE FRACTION ARC", 54, CYAN)
    ptext(t, 6.0, (W / 2, 1545), "Comment your speed-round score ↓", 44, WHITE)


SCENES = [
    (5.0, s_hook),
    (8.1, s_arena),
    (12.0, s_add),
    (14.0, s_sub),
    (16.0, s_mul),
    (5.0, s_tip),
    (2.5, s_speed_intro),
    (6.6, make_q(1, MINUS + "7 + 10 =", "3", "Start at " + MINUS + "7, dash RIGHT 10 → 3")),
    (6.6, make_q(2, MINUS + "4 " + MINUS + " 6 =", MINUS + "10", "Already negative → go 6 DEEPER")),
    (6.6, make_q(3, "8 " + MINUS + " (" + MINUS + "2) =", "10", "Minus a minus = PLUS → 8 + 2")),
    (6.6, make_q(4, "(" + MINUS + "6) × (" + MINUS + "2) =", "12", "SAME signs → POSITIVE")),
    (10.0, s_outro),
]
TOTAL = sum(d for d, _ in SCENES)

_yy, _xx = np.mgrid[0:H, 0:W]
_vd = np.sqrt(((_xx - W / 2) / (W * 0.62)) ** 2 + ((_yy - H / 2) / (H * 0.62)) ** 2)
VIGNETTE = (256 * np.clip(1.15 - 0.55 * _vd ** 2, 0.45, 1.0)).astype(np.uint16)[:, :, None]
del _yy, _xx, _vd
WHITE_IMG = Image.new("RGB", (W, H), WHITE)
SCENE_CUT_FLASH = True   # anime-style white flash + whoosh on every cut
POST_FX = None           # optional fn(arr, fi, t, scene_idx, t_local) -> arr, applied last


def render_frame(fi):
    t = fi / FPS
    start = 0.0
    for idx, (dur, fn) in enumerate(SCENES):
        if t < start + dur or idx == len(SCENES) - 1:
            break
        start += dur
    G.fi, G.t0, G.shake, G.flash, G.invert = fi, start, 0.0, 0.0, False
    tl = t - start
    fn(tl)
    if idx > 0 and SCENE_CUT_FLASH:
        cue("whoosh", 0.0)
        if tl < 0.1:
            G.flash = max(G.flash, 0.8 * (1 - tl / 0.1))
    # retention progress bar
    G.draw.rectangle([0, 0, W, 12], fill=BLACK)
    G.draw.rectangle([0, 0, int(W * t / TOTAL), 12], fill=PINK)
    img = G.img
    if G.shake > 0.5:
        dx = int(math.sin(fi * 12.9) * G.shake)
        dy = int(math.cos(fi * 7.3) * G.shake)
        shaken = Image.new("RGB", (W, H), BLACK)
        shaken.paste(img, (dx, dy))
        img = shaken
    if G.invert:
        img = ImageOps.invert(img)
    if G.flash > 0.01:
        img = Image.blend(img, WHITE_IMG, min(1.0, G.flash))
    arr = (np.asarray(img).astype(np.uint16) * VIGNETTE >> 8).astype(np.uint8)
    if POST_FX is not None:
        arr = POST_FX(arr, fi, t, idx, tl)
    return arr


# ---------------------------------------------------------------- audio

SR = 44100


def synth_audio(path, music_fn=None, extra_sfx=None):
    """music_fn(n_samples) -> np.ndarray replaces the default score; extra_sfx(SR) -> {kind: (signal, gain)}."""
    n = int((TOTAL + 1.5) * SR)
    music, sfx = np.zeros(n), np.zeros(n)
    rng = np.random.default_rng(3)

    def tt(d):
        return np.arange(int(d * SR)) / SR

    def add(buf, sig, t, g=1.0):
        i = int(t * SR)
        if i >= len(buf):
            return
        j = min(len(buf), i + len(sig))
        buf[i:j] += sig[: j - i] * g

    def bandnoise(d, lo, hi):
        x = rng.standard_normal(int(d * SR))
        spec = np.fft.rfft(x)
        f = np.fft.rfftfreq(len(x), 1 / SR)
        spec[(f < lo) | (f > hi)] = 0
        y = np.fft.irfft(spec, len(x))
        return y / (np.abs(y).max() + 1e-9)

    def tone(freq, d, harm=(1.0,), decay=8.0, attack=0.005):
        x = tt(d)
        y = sum(a * np.sin(2 * np.pi * freq * (k + 1) * x) for k, a in enumerate(harm))
        return y * np.exp(-x * decay) * np.minimum(1, x / attack)

    x = tt(0.35)
    kick = np.sin(2 * np.pi * np.cumsum(45 + 120 * np.exp(-x * 28)) / SR) * np.exp(-x * 9)
    x = tt(0.2)
    snare = 0.7 * bandnoise(0.2, 800, 9000) * np.exp(-x * 22) + 0.4 * np.sin(2 * np.pi * 190 * x) * np.exp(-x * 30)
    x = tt(0.05)
    hat = bandnoise(0.05, 7000, 16000) * np.exp(-x * 90)

    # intro: menacing drone + heartbeat + riser into the drop at 5s
    drop = 5.0
    x = tt(drop)
    drone = (np.sin(2 * np.pi * 55 * x) + 0.5 * np.sin(2 * np.pi * 110.3 * x) + 0.3 * np.sin(2 * np.pi * 82.4 * x))
    add(music, drone * np.minimum(1, x / 1.0) * 0.3, 0)
    for k in range(5):
        add(music, kick, k * 1.0 + 0.1, 0.9)
        add(music, kick, k * 1.0 + 0.32, 0.6)
    riser = bandnoise(4.0, 500, 6000) * np.linspace(0, 1, int(4.0 * SR)) ** 3
    add(music, riser, 1.0, 0.35)

    # main loop: 150 BPM, "royal road" IV-V-iii-vi progression, chiptune arp
    beat = 60 / 150
    chords = [(87.31, [349.23, 440.00, 523.25]), (98.00, [392.00, 493.88, 587.33]),
              (82.41, [329.63, 392.00, 493.88]), (110.00, [440.00, 523.25, 659.25])]
    arp = [0, 1, 2, 1]
    t, bar = drop, 0
    while t < TOTAL:
        root, tones = chords[bar % 4]
        for b in range(4):
            tb = t + b * beat
            add(music, kick, tb, 0.9)
            if b in (1, 3):
                add(music, snare, tb, 0.5)
            for h in (0, 0.5):
                add(music, hat, tb + h * beat, 0.18 if h == 0 else 0.3)
                add(music, tone(root * (2 if h else 1), 0.19, (1, 0.5, 0.3), decay=6), tb + h * beat, 0.33)
            for q in range(4):
                note = tones[arp[q]] * (2 if (bar // 2) % 2 else 1)
                add(music, tone(note, 0.1, (1, 0, 1 / 3, 0, 1 / 5, 0, 1 / 7), decay=18), tb + q * beat / 4, 0.07)
        for f in tones:
            x = tt(4 * beat)
            add(music, np.sin(2 * np.pi * f / 2 * x) * np.minimum(1, x / 0.3) * np.exp(-x * 0.4), t, 0.06)
        t += 4 * beat
        bar += 1
    fade_n = int(1.5 * SR)
    end = int(TOTAL * SR)
    music[end - fade_n:end] *= np.linspace(1, 0, fade_n)
    music[end:] = 0

    # sound effects
    x = tt(0.7)
    boom = (np.sin(2 * np.pi * np.cumsum(30 + 70 * np.exp(-x * 12)) / SR) * np.exp(-x * 5)
            + 0.5 * bandnoise(0.7, 40, 1500) * np.exp(-x * 10))
    x = tt(1.2)
    big = (np.sin(2 * np.pi * np.cumsum(28 + 90 * np.exp(-x * 8)) / SR) * np.exp(-x * 3)
           + 0.35 * bandnoise(1.2, 3000, 14000) * np.exp(-x * 4))
    x = tt(0.35)
    whoosh = bandnoise(0.35, 400, 3500) * np.sin(np.pi * x / 0.35) ** 2
    tick = tone(1800, 0.06, (1, 0.3), decay=60) + tone(900, 0.06, decay=60) * 0.5
    ding = tone(1318.5, 0.8, (1,), decay=5) + tone(1975.5, 0.8, decay=6) * 0.6 + tone(2637, 0.8, decay=9) * 0.3
    x = tt(0.08)
    popf = np.sin(2 * np.pi * np.cumsum(400 + 1400 * x / 0.08) / SR) * np.exp(-x * 30)
    x = tt(0.18)
    flip = np.sin(2 * np.pi * np.cumsum(600 + 2400 * (x / 0.18) ** 2) / SR) * np.sin(np.pi * x / 0.18)
    bank = {"boom": (boom, 0.55), "big": (big, 0.9), "whoosh": (whoosh, 0.3), "tick": (tick, 0.5),
            "ding": (ding + 0.4 * np.pad(boom, (0, len(ding) - len(boom))), 0.4), "pop": (popf, 0.35), "flip": (flip, 0.35)}
    if extra_sfx is not None:
        bank.update(extra_sfx(SR))
    if music_fn is not None:
        music = music_fn(n)
    for at, kind in sorted(CUES):
        sig, g = bank[kind]
        add(sfx, sig, at, g)

    out = music * 0.5 + sfx
    out = np.tanh(out * 1.1)
    out = out / (np.abs(out).max() + 1e-9) * 0.93
    out = out[: int((TOTAL + 0.2) * SR)]
    pcm = (np.stack([out, out], axis=1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# ---------------------------------------------------------------- main

def main(out_name="the_plus_minus_arc.mp4", scenes=None, music_fn=None, extra_sfx=None):
    """Render `scenes` (default: this episode) to out/<out_name>. Other episodes import this module
    and call main() with their own scene list."""
    global SCENES, TOTAL
    if scenes is not None:
        SCENES = scenes
        TOTAL = sum(d for d, _ in SCENES)
    os.makedirs(OUT_DIR, exist_ok=True)
    stem = os.path.splitext(out_name)[0]
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        pdir = os.path.join(OUT_DIR, "preview", stem)
        os.makedirs(pdir, exist_ok=True)
        for s in sys.argv[2:]:
            arr = render_frame(int(float(s) * FPS))
            Image.fromarray(arr).resize((W // 2, H // 2)).save(os.path.join(pdir, f"t{float(s):06.2f}.png"))
        return
    silent = os.path.join(OUT_DIR, f"_{stem}_video.mp4")
    audio = os.path.join(OUT_DIR, f"_{stem}_audio.wav")
    final = os.path.join(OUT_DIR, out_name)
    nframes = int(round(TOTAL * FPS))
    enc = subprocess.Popen([FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                            "-crf", os.environ.get("VIDEO_CRF", "23"), "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    for fi in range(nframes):
        enc.stdin.write(render_frame(fi).tobytes())
        if fi % 150 == 0:
            print(f"frame {fi}/{nframes}", flush=True)
    enc.stdin.close()
    enc.wait()
    synth_audio(audio, music_fn, extra_sfx)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", silent, "-i", audio, "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final], check=True)
    os.remove(silent)
    os.remove(audio)
    print(f"done: {final} ({TOTAL:.1f}s)")


if __name__ == "__main__":
    main()
