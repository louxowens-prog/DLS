"""Collage: shapes cut from coloured paper (with a cast shadow and a slight lift at the edge), photographs cut out
with a white border, a printer's halftone, a pair of dressmaker's scissors, a frame sliced into pieces that drift
apart, and paper scraps flying through the shot."""
import math

import numpy as np
import skia

import kit as K
from kit import INK, WHITE, H, W, mix, paint, path, smooth


def torn(pts, seed=0, amp=4.0, step=14):
    """Roughen a polygon's edge like torn paper."""
    rng = K.rng_at(seed, 41)
    out = []
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        L = math.hypot(x1 - x0, y1 - y0)
        k = max(1, int(L / step))
        nx, ny = -(y1 - y0) / (L + 1e-6), (x1 - x0) / (L + 1e-6)
        for j in range(k):
            u = j / k
            d = rng.uniform(-amp, amp)
            out.append((x0 + (x1 - x0) * u + nx * d, y0 + (y1 - y0) * u + ny * d))
    return out


def paper(c, pts, color, seed=0, shadow=True, edge="cut", lift=1.0, a=1.0, grain=True):
    """A piece of coloured paper: cut (clean edge) or torn (rough edge, a white fibrous rim)."""
    if edge == "torn":
        rim = torn(pts, seed, 5.0)
        p_rim = path(rim)
        p = path(torn(pts, seed + 1, 3.0))
    else:
        p = path(pts)
        p_rim = None
    if shadow:
        c.save()
        c.translate(5 * lift, 8 * lift)
        c.drawPath(p_rim or p, paint(INK, 0.32 * a, blur=5 + 3 * lift))
        c.restore()
    if p_rim is not None:
        c.drawPath(p_rim, paint((248, 244, 232), a))
    c.drawPath(p, paint(color, a))
    if grain:
        c.save()
        c.clipPath(p, doAntiAlias=True)
        b = p.computeTightBounds()
        rng = K.rng_at(seed, 7)
        for _ in range(int(min(60, b.width() * b.height() / 4000))):
            x, y = rng.uniform(b.left(), b.right()), rng.uniform(b.top(), b.bottom())
            c.drawCircle(x, y, rng.uniform(4, 14), paint(mix(color, WHITE if rng.random() < 0.5 else INK, 0.06), 0.5 * a, blur=4))
        c.restore()
    return p


def rect_pts(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def cut_letters(c, s, x, y, size, colors, seed=0, fname="abril-400", tag="cut", jitter=1.0, shadow=True, a=1.0, max_w=None):
    """A word cut out of paper letter by letter, each letter a different colour, tilted a little, on a shadow."""
    f = K.font(fname, size)
    w = f.measureText(s)
    if max_w and w > max_w:
        size *= max_w / w
        f = K.font(fname, size)
        w = f.measureText(s)
    rng = K.rng_at(seed, 13)
    xx = x - w / 2
    for i, ch in enumerate(s):
        cw = f.measureText(ch)
        if ch != " ":
            c.save()
            c.translate(xx + cw / 2, y + rng.uniform(-4, 4) * jitter)
            c.rotate(rng.uniform(-7, 7) * jitter)
            colr = colors[i % len(colors)]
            if shadow:
                c.drawString(ch, -cw / 2 + 4, 6, f, paint(INK, 0.35 * a, blur=4))
            c.drawString(ch, -cw / 2, 0, f, paint((250, 246, 234), a, stroke=size * 0.08))
            c.drawString(ch, -cw / 2, 0, f, paint(colr, a))
            c.restore()
        xx += cw
    K.reg_local(c, x - w / 2, y - size * 0.8, x + w / 2, y + size * 0.25, tag)
    return w


def halftone(rgb, cell=7, ink=(28, 24, 26), paper_=(240, 232, 214)):
    """A newspaper print of an image: dots that grow in the dark."""
    h, w = rgb.shape[:2]
    l = (rgb[..., 0] * 0.3 + rgb[..., 1] * 0.59 + rgb[..., 2] * 0.11) / 255.0
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = (xx + yy) / (cell * 1.41), (xx - yy) / (cell * 1.41)
    d = np.sqrt((u - np.round(u)) ** 2 + (v - np.round(v)) ** 2)
    on = d < (1 - l) * 0.62
    out = np.empty((h, w, 3), np.float32)
    out[:] = paper_
    out[on] = ink
    return out.astype(np.uint8)


def photo(c, img, x, y, w, h, ang=0.0, border=14, a=1.0, shadow=True, src=None):
    """A cut-out photograph: an image (RGBA numpy) placed in a w x h box with a white border, tilted ang degrees."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    if shadow:
        c.drawRect(skia.Rect.MakeXYWH(-w / 2 - border + 6, -h / 2 - border + 9, w + 2 * border, h + 2 * border), paint(INK, 0.35 * a, blur=8))
    c.drawRect(skia.Rect.MakeXYWH(-w / 2 - border, -h / 2 - border, w + 2 * border, h + 2 * border), paint((250, 248, 240), a))
    im = K.image(img)
    p = skia.Paint()
    p.setAlphaf(a)
    srect = skia.Rect.MakeXYWH(*src) if src else skia.Rect.MakeWH(img.shape[1], img.shape[0])
    c.drawImageRect(im, srect, skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), skia.SamplingOptions(skia.FilterMode.kLinear), p)
    c.restore()


def scissors(c, x, y, ang, open_=0.5, s=1.0, a=1.0):
    """Dressmaker's shears: black handles, steel blades; open_ 0 (shut) .. 1 (wide); ang = direction of the points."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    op = 4 + 22 * open_
    for sgn in (-1, 1):
        c.save()
        c.rotate(sgn * op / 2)
        blade = smooth([(0, -9), (190, -4 * sgn - 2), (230, 0), (190, 4), (0, 9)])
        c.drawPath(blade, paint(shader=K.lin((0, -9), (0, 9), [(236, 238, 242), (150, 156, 166), (96, 100, 110)]), a=a))
        c.drawPath(blade, paint((60, 62, 70), 0.6 * a, stroke=1.5))
        c.drawPath(K.capsule(-10, 0, -90, sgn * 16, 16, 18), paint((26, 24, 28), a))
        c.drawOval(skia.Rect.MakeLTRB(-170, sgn * 18 - 30, -80, sgn * 18 + 30), paint((26, 24, 28), a, stroke=14))
        c.restore()
    c.drawCircle(0, 0, 9, paint((200, 196, 186), a))
    c.drawCircle(0, 0, 4, paint((80, 80, 86), a))
    c.restore()


def cut_up(arr, k, seed=0, n=5, cx=W / 2, cy=H / 2, spread=1.0, bg=(16, 12, 14), under=None):
    """The frame sliced by n straight scissor cuts into pieces that drift and turn apart as k goes 0 -> 1 (over a
    plain dark ground, or over the frame `under`)."""
    if k <= 0:
        return arr
    rng = K.rng_at(seed, 31)
    pieces = [[(0, 0), (W, 0), (W, H), (0, H)]]
    for _ in range(n):
        a = rng.uniform(0, math.pi)
        px, py = cx + rng.uniform(-260, 260), cy + rng.uniform(-420, 420)
        nx, ny = math.cos(a), math.sin(a)
        new = []
        for poly in pieces:
            L, R = _split(poly, px, py, nx, ny)
            new += [q for q in (L, R) if len(q) >= 3]
        pieces = new
    if under is not None:
        out = np.ascontiguousarray(under.copy())
    else:
        out = np.zeros_like(arr)
        out[..., :3] = bg
        out[..., 3] = 255
    s = skia.Surface(out)
    c = s.getCanvas()
    img = K.image(arr)
    for i, poly in enumerate(pieces):
        mx = sum(p[0] for p in poly) / len(poly)
        my = sum(p[1] for p in poly) / len(poly)
        dx, dy = (mx - cx), (my - cy)
        dist = math.hypot(dx, dy) + 1e-6
        r2 = K.rng_at(seed, i, 77)
        mv = 60 + 120 * r2.random()
        ox, oy = dx / dist * mv * k * spread, dy / dist * mv * k * spread
        rot = r2.uniform(-9, 9) * k * spread
        c.save()
        c.translate(mx + ox, my + oy)
        c.rotate(rot)
        c.translate(-mx, -my)
        p = path(poly)
        c.save()
        c.translate(6, 10)
        c.drawPath(p, paint(INK, 0.5, blur=8))
        c.restore()
        c.save()
        c.clipPath(p, doAntiAlias=True)
        c.drawImage(img, 0, 0)
        c.restore()
        c.drawPath(p, paint((250, 246, 236), 0.9, stroke=5))
        c.restore()
    return out


def _split(poly, px, py, nx, ny):
    """Split a convex polygon by the line through (px, py) with normal (nx, ny)."""
    L, R = [], []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        da = (a[0] - px) * nx + (a[1] - py) * ny
        db = (b[0] - px) * nx + (b[1] - py) * ny
        (L if da >= 0 else R).append(a)
        if (da >= 0) != (db >= 0):
            u = da / (da - db)
            q = (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
            L.append(q)
            R.append(q)
    return L, R


def scraps(c, T, t0, seed=0, n=24, area=(0, 0, W, H), colors=((236, 120, 140), (250, 196, 30), (150, 190, 226), (250, 244, 228), (120, 170, 120)),
           fall=420.0, spin=1.0):
    """Paper scraps and confetti tumbling through the frame from time t0."""
    if T < t0:
        return
    rng = K.rng_at(seed, 5)
    dt = T - t0
    x0, y0, x1, y1 = area
    for i in range(n):
        x = rng.uniform(x0, x1) + 40 * math.sin(dt * rng.uniform(1, 3) + i)
        y = rng.uniform(y0 - 300, y0) + dt * fall * rng.uniform(0.6, 1.3)
        if y > y1 + 60:
            continue
        w, h = rng.uniform(16, 60), rng.uniform(10, 34)
        c.save()
        c.translate(x, y)
        c.rotate(dt * 200 * spin * rng.uniform(-1, 1) + i * 37)
        c.scale(1, abs(math.cos(dt * rng.uniform(2, 6) + i)) + 0.15)
        colr = colors[i % len(colors)]
        c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), paint(colr))
        c.restore()
