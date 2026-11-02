"""Photographic eyes and mouths for the collage faces.

In Mind Game the characters' faces are photographs of real people pasted onto drawn bodies, mouths moving
with the voice. There are no photos of people here, so these features are rendered photo-real
(shaded eyeballs with fibrous irises and wet highlights, glossy lips, teeth) and pasted on as torn scraps.
"""
import math

import numpy as np
import skia
from PIL import Image
from scipy import ndimage

import mg

SKIN = (222, 176, 146)
_cache = {}


def _c(rgb, a=1.0):
    return skia.Color4f(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, a)


def _radial(cx, cy, r, cols, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(cx, cy), r, [c.toColor() for c in cols], pos)


def _linear(p0, p1, cols, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], [c.toColor() for c in cols], pos)


def _skin(w, h, seed, tone=SKIN):
    rng = np.random.default_rng(seed)
    n = ndimage.gaussian_filter(rng.normal(0, 1, (h, w)), 1.2) * 5 + ndimage.gaussian_filter(rng.normal(0, 1, (h, w)), 6) * 9
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h * 0.45) / (h / 2)) ** 2)
    shade = 1.06 - 0.22 * np.clip(d, 0, 1.4) ** 2
    img = (np.array(tone, np.float32)[None, None] + n[..., None]) * shade[..., None]
    out = np.zeros((h, w, 4), np.uint8)
    out[..., :3] = np.clip(img, 0, 255)
    out[..., 3] = 255
    return out


def eye(w, look=(0.0, 0.0), open_=1.0, iris=(96, 120, 70), seed=0):
    """A photographic eye with the skin around it, as an RGBA array (w x 0.78w)."""
    key = ("eye", int(w), round(look[0], 1), round(look[1], 1), round(open_, 2), iris, seed)
    if key in _cache:
        return _cache[key]
    S = 2
    W, H = int(w * S), int(w * 0.78 * S)
    arr = _skin(W, H, seed)
    cx, cy = W / 2, H * 0.54
    ew = W * 0.8
    oy = ew * 0.3 * open_
    sf = skia.Surface(arr)
    with sf as c:
        # brow ridge highlight and lid crease
        c.drawOval(skia.Rect.MakeXYWH(cx - ew * 0.55, cy - ew * 0.62, ew * 1.1, ew * 0.4), mg.paint((255, 225, 200), 0.25, blur=ew * 0.08))
        crease = mg.bez((cx - ew * 0.5, cy - ew * 0.02), (cx, cy - ew * 0.5 * max(0.4, open_) - ew * 0.06), (cx + ew * 0.5, cy - ew * 0.04))
        c.drawPath(mg.path_of(crease), mg.paint((120, 70, 60), 0.45, stroke=ew * 0.035, blur=ew * 0.025))
        up = mg.bez((cx - ew / 2, cy + ew * 0.02), (cx - ew * 0.1, cy - oy * 1.35), (cx + ew / 2, cy - ew * 0.03), n=40)
        lo = mg.bez((cx + ew / 2, cy - ew * 0.03), (cx + ew * 0.05, cy + oy * 0.95), (cx - ew / 2, cy + ew * 0.02), n=40)
        if open_ > 0.05:
            opening = mg.path_of(np.vstack([up, lo]), True)
            c.save()
            c.clipPath(opening, doAntiAlias=True)
            c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=_radial(cx, cy, ew * 0.55, [_c((246, 242, 236)), _c((232, 222, 214)), _c((196, 168, 160))], [0, 0.55, 1])))
            rng = np.random.default_rng(seed + 5)
            for _ in range(7):                                     # faint veins
                side = rng.choice([-1, 1])
                p0 = (cx + side * ew * 0.48, cy + rng.normal(0, ew * 0.04))
                p2 = (cx + side * ew * rng.uniform(0.2, 0.32), cy + rng.normal(0, ew * 0.08))
                vein = mg.bez(p0, ((p0[0] + p2[0]) / 2, p0[1] + rng.normal(0, ew * 0.05)), p2)
                c.drawPath(mg.path_of(vein), mg.paint((200, 80, 80), 0.25, stroke=S * 0.8))
            ix, iy, ir = cx + look[0] * ew * 0.2, cy - ew * 0.02 + look[1] * ew * 0.07, ew * 0.23
            dark = tuple(int(v * 0.45) for v in iris)
            light = tuple(min(255, int(v * 1.5 + 30)) for v in iris)
            c.drawCircle(ix, iy, ir, skia.Paint(AntiAlias=True, Shader=_radial(ix, iy, ir, [_c(light), _c(iris), _c(dark)], [0.25, 0.7, 1])))
            for k in range(90):                                    # iris fibres
                a = k / 90 * 2 * math.pi + rng.normal(0, 0.03)
                r0, r1 = ir * rng.uniform(0.35, 0.5), ir * rng.uniform(0.8, 0.98)
                col = light if k % 2 else dark
                c.drawLine(ix + r0 * math.cos(a), iy + r0 * math.sin(a), ix + r1 * math.cos(a), iy + r1 * math.sin(a),
                           mg.paint(col, 0.35, stroke=S * 0.9))
            c.drawCircle(ix, iy, ir, mg.paint((25, 20, 20), 0.8, stroke=ir * 0.12, blur=ir * 0.04))
            c.drawCircle(ix, iy, ir * 0.38, mg.paint((8, 6, 8)))
            # upper-lid shadow falling on the eyeball
            c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=_linear((0, cy - oy * 1.2), (0, cy - oy * 0.2),
                                                                          [_c((60, 30, 30), 0.55), _c((60, 30, 30), 0.0)])))
            c.drawOval(skia.Rect.MakeXYWH(ix - ir * 0.55, iy - ir * 0.6, ir * 0.42, ir * 0.32), mg.paint((255, 255, 255), 0.95, blur=ir * 0.05))
            c.drawCircle(ix + ir * 0.38, iy + ir * 0.35, ir * 0.08, mg.paint((255, 255, 255), 0.7, blur=ir * 0.03))
            c.restore()
            c.drawPath(mg.path_of(lo), mg.paint((236, 170, 160), 0.8, stroke=ew * 0.03, blur=ew * 0.008))
            c.drawPath(mg.path_of(lo + np.array([0, ew * 0.05])), mg.paint((110, 60, 50), 0.25, stroke=ew * 0.05, blur=ew * 0.03))
        # lash line and lashes
        c.drawPath(mg.path_of(up), mg.paint((28, 18, 18), 0.95, stroke=ew * 0.045, blur=ew * 0.006))
        rng = np.random.default_rng(seed + 9)
        for k in range(16):
            u = 0.1 + 0.85 * k / 15
            p = up[int(u * (len(up) - 1))]
            ang = -math.pi / 2 + (u - 0.5) * 1.6
            L = ew * rng.uniform(0.07, 0.11)
            lash = mg.bez(p, (p[0] + L * 0.6 * math.cos(ang - 0.3), p[1] + L * 0.6 * math.sin(ang - 0.3)),
                          (p[0] + L * math.cos(ang + 0.2), p[1] + L * math.sin(ang + 0.2)), n=6)
            c.drawPath(mg.path_of(lash), mg.paint((25, 15, 15), 0.85, stroke=S * 1.4))
    out = np.asarray(Image.fromarray(arr).resize((int(w), int(w * 0.78)), Image.LANCZOS))
    _cache[key] = out
    return out


def mouth(w, open_=0.0, smile=0.0, seed=0):
    """A photographic mouth, RGBA array (w x 0.62w). open_ 0..1, smile -1..1."""
    open_ = round(min(1.0, max(0.0, open_)) * 12) / 12
    key = ("mouth", int(w), open_, round(smile, 1), seed)
    if key in _cache:
        return _cache[key]
    S = 2
    W, H = int(w * S), int(w * 0.62 * S)
    arr = _skin(W, H, seed + 1)
    cx, cy = W / 2, H * 0.5
    mw = W * 0.36 * (1 - 0.12 * open_)
    gap = open_ * W * 0.26
    cy_c = cy - smile * W * 0.05
    sf = skia.Surface(arr)
    with sf as c:
        # philtrum and chin shading
        for side in (-1, 1):
            c.drawLine(cx + side * mw * 0.14, cy - W * 0.3, cx + side * mw * 0.12, cy - W * 0.12, mg.paint((180, 120, 100), 0.35, stroke=S * 3, blur=S * 3))
        c.drawOval(skia.Rect.MakeXYWH(cx - mw * 0.6, cy + W * 0.17 + gap, mw * 1.2, W * 0.1), mg.paint((150, 95, 80), 0.3, blur=W * 0.03))
        top_line = np.array([(cx - mw, cy_c), (cx - mw * 0.45, cy - W * 0.075), (cx - mw * 0.14, cy - W * 0.095), (cx, cy - W * 0.075),
                             (cx + mw * 0.14, cy - W * 0.095), (cx + mw * 0.45, cy - W * 0.075), (cx + mw, cy_c)])
        top_line = np.vstack([mg.bez(top_line[i], (top_line[i] + top_line[i + 1]) / 2, top_line[i + 1], n=8) for i in range(6)])
        inner_up = mg.bez((cx + mw, cy_c), (cx + mw * 0.5, cy - gap * 0.55), (cx - mw * 0.5, cy - gap * 0.55), (cx - mw, cy_c), n=30)
        inner_lo = mg.bez((cx - mw, cy_c), (cx - mw * 0.5, cy + gap * 0.75 + W * 0.012), (cx + mw * 0.5, cy + gap * 0.75 + W * 0.012), (cx + mw, cy_c), n=30)
        bottom = mg.bez((cx + mw, cy_c), (cx + mw * 0.6, cy + gap * 0.62 + W * 0.15), (cx - mw * 0.6, cy + gap * 0.62 + W * 0.15), (cx - mw, cy_c), n=30)
        top_line[:, 1] -= gap * 0.25
        if gap > 1:
            inside = mg.path_of(np.vstack([inner_up[::-1], inner_lo[::-1]]), True)
            c.drawPath(inside, mg.paint((45, 12, 18)))
            c.save()
            c.clipPath(inside, doAntiAlias=True)
            ty = cy - gap * 0.42 - W * 0.02
            th = min(gap * 0.32, W * 0.055) + W * 0.02
            c.drawRect(skia.Rect.MakeXYWH(cx - mw * 0.8, ty, mw * 1.6, th),
                       skia.Paint(Shader=_linear((0, ty), (0, ty + th), [_c((248, 243, 232)), _c((214, 204, 188))])))
            for k in range(-3, 4):
                c.drawLine(cx + k * mw * 0.2, ty, cx + k * mw * 0.2, ty + th, mg.paint((150, 140, 130), 0.5, stroke=S * 1.2))
            if open_ > 0.4:
                c.drawOval(skia.Rect.MakeXYWH(cx - mw * 0.55, cy + gap * 0.2, mw * 1.1, gap * 0.7), mg.paint((175, 70, 80), 0.95, blur=S * 2))
            c.restore()
        up_lip = mg.path_of(np.vstack([top_line, inner_up]), True)
        lo_lip = mg.path_of(np.vstack([inner_lo, bottom]), True)
        c.drawPath(up_lip, skia.Paint(AntiAlias=True, Shader=_linear((0, cy - W * 0.1), (0, cy - gap * 0.5), [_c((176, 88, 92)), _c((128, 50, 62))])))
        c.drawPath(lo_lip, skia.Paint(AntiAlias=True, Shader=_linear((0, cy + gap * 0.5), (0, cy + gap * 0.5 + W * 0.15), [_c((150, 60, 70)), _c((196, 104, 108)), _c((170, 88, 92))], [0, 0.5, 1])))
        c.drawOval(skia.Rect.MakeXYWH(cx - mw * 0.35, cy + gap * 0.7 + W * 0.045, mw * 0.6, W * 0.04), mg.paint((255, 235, 235), 0.45, blur=W * 0.012))
        c.drawOval(skia.Rect.MakeXYWH(cx - mw * 0.3, cy - W * 0.075 - gap * 0.25, mw * 0.25, W * 0.02), mg.paint((255, 225, 225), 0.3, blur=W * 0.008))
        c.drawPath(mg.path_of(np.vstack([inner_up[::-1]])), mg.paint((70, 25, 30), 0.8, stroke=S * 2.2, blur=S))
        for side in (-1, 1):
            c.drawCircle(cx + side * mw, cy_c, S * 5, mg.paint((110, 50, 50), 0.5, blur=S * 3))
    out = np.asarray(Image.fromarray(arr).resize((int(w), int(w * 0.62)), Image.LANCZOS))
    _cache[key] = out
    return out


def paste(c, img, cx, cy, T, seed=0, border=4.0, rot=0.0, shadow=True):
    """Paste a feature photo as a torn scrap centred at (cx, cy)."""
    h, w = img.shape[:2]
    seed = abs(int(seed))
    rng = np.random.default_rng(seed)
    pts = np.array([(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]) * 0.92
    pts = mg.resample(pts, 10.0, closed=True)
    pts = pts + rng.normal(0, max(1.0, w * 0.018), pts.shape)
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    mg.photo_scrap(c, img, 0, 0, pts, T, seed=seed, border=border, shadow=shadow)
    c.restore()


def envelope(key_times, T):
    """Mouth opening from a list of (t0, t1) talking spans: chatters on twos while inside a span."""
    for a, b in key_times:
        if a <= T < b:
            rng = np.random.default_rng(mg.step(T) + int(a * 10))
            return float(rng.uniform(0.25, 1.0))
    return 0.0
