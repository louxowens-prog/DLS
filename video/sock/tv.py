"""Cheap TV: WordArt, lower thirds, network bugs and bumpers, the video mixer's wipes (star, page curl, spinning
cube), freeze frames with scribbled labels, a phone camera's screen, handheld shake, snap zooms, and VHS."""
import math

import numpy as np
import skia
from PIL import Image

import diy as K
from diy import ACID, BLUE, GOLD, HOT, INK, PURPLE, WHITE, W, H, col, ease, lin, mix, paint, path, rad, ramp, smooth

RAINBOW = [(255, 40, 120), (255, 150, 30), (255, 236, 40), (120, 255, 60), (40, 200, 255), (150, 70, 255)]


# ------------------------------------------------------------------ WordArt

def glyph_paths(s, size, fname):
    f = K.font(fname, size)
    gl = f.textToGlyphs(s)
    ws = f.getWidths(gl)
    out, x = [], 0.0
    for g, gw in zip(gl, ws):
        p = f.getPath(g)
        out.append((p, x, gw))
        x += gw
    return out, x


def wordart(c, s, x, y, size, T=0.0, fill=RAINBOW, edge=INK, depth=None, warp="wave", amp=0.12, fname="rubik-900",
            tag="wordart", max_w=None, ext=None, shine=True, k=1.0, spin=0.0, a=1.0, ow=None):
    """1997 WordArt: per-letter warp (wave / arch / slant / none), a fat outline, a rainbow (or any) gradient fill,
    and a deep extrusion in the gradient's darkest colour. (x, y) = the baseline centre."""
    gl, w = glyph_paths(s, size, fname)
    if max_w and w > max_w:
        size *= max_w / w
        gl, w = glyph_paths(s, size, fname)
    ext = ext or (PURPLE if fill is RAINBOW else mix(fill[-1], INK, 0.3))
    c.save()
    c.translate(x, y)
    if spin:
        c.rotate(spin)
    c.scale(k, k)
    x0 = -w / 2
    n = max(1, len(s) - 1)
    places = []
    for i, (p, gx, gw) in enumerate(gl):
        u = i / n
        cx = x0 + gx + gw / 2
        if warp == "wave":
            dy = -math.sin(u * 2 * math.pi + T * 3.0) * size * amp
            rot = math.degrees(math.cos(u * 2 * math.pi + T * 3.0)) * amp * 0.9
        elif warp == "arch":
            dy = -math.sin(u * math.pi) * size * amp * 2
            rot = (u - 0.5) * 30 * amp * 3
        elif warp == "slant":
            dy, rot = -u * size * amp * 2, -8
        else:
            dy, rot = 0.0, 0.0
        places.append((p, gx, gw, cx, dy, rot))
    def each(fn):
        for p, gx, gw, cx, dy, rot in places:
            if p is None:
                continue
            c.save()
            c.translate(cx, dy)
            c.rotate(rot)
            c.translate(-(gw / 2), 0)
            fn(p)
            c.restore()
    depth = int(depth if depth is not None else size * 0.11)
    each(lambda p: (c.save(), c.translate(depth * 0.7, depth * 0.8), c.drawPath(p, paint(edge, a, stroke=(ow or size * 0.12))), c.restore()))
    for d in range(depth, 0, -1):                                   # the extrusion, down and to the right
        each(lambda p, d=d: (c.save(), c.translate(d * 0.7, d * 0.8), c.drawPath(p, paint(mix(ext, INK, 0.35 * d / max(1, depth)), a)),
                             c.restore()))
    each(lambda p: c.drawPath(p, paint(edge, a, stroke=ow or size * 0.12)))
    for p, gx, gw, cx, dy, rot in places:
        if p is None:
            continue
        c.save()
        c.translate(cx, dy)
        c.rotate(rot)
        c.translate(-(gw / 2), 0)
        # the gradient runs across the whole word, not each letter
        c.drawPath(p, paint(shader=lin((-cx + gw / 2 - w / 2, -size * 0.8), (-cx + gw / 2 + w / 2, size * 0.1), list(fill)), a=a))
        if shine:
            c.save()
            c.clipPath(p, doAntiAlias=True)
            c.drawRect(skia.Rect.MakeLTRB(-10, -size, gw + 10, -size * 0.5), paint(WHITE, 0.4 * a))
            c.restore()
        c.restore()
    K.reg_local(c, x0, -size * (0.85 + amp * 2), x0 + w, size * (0.25 + amp * 2), tag)
    c.restore()
    return w * k


# ------------------------------------------------------------------ lower thirds, bugs

def lower_third(c, T, t0, name, sub, y=1180, x0=60, w=860, c1=HOT, c2=PURPLE, tag="lower", dur=None):
    """A garish lower third: a gradient bar wipes in, a gold star spins at its end, the name in fat type, the
    subtitle on a second bar."""
    k = ease(ramp(T, t0, t0 + 0.35))
    if dur is not None:
        k *= 1 - ease(ramp(T, t0 + dur - 0.3, t0 + dur))
    if k <= 0:
        return
    ww = w * k
    c.save()
    c.drawRect(skia.Rect.MakeXYWH(x0 + 10, y + 10, ww, 104), paint(INK, 0.5))
    c.drawRect(skia.Rect.MakeXYWH(x0, y, ww, 104), paint(shader=lin((x0, 0), (x0 + w, 0), [c1, c2])))
    c.drawRect(skia.Rect.MakeXYWH(x0, y + 104, ww * 0.82, 62), paint(INK, 0.92))
    c.drawRect(skia.Rect.MakeXYWH(x0, y + 104, ww * 0.82, 6), paint(GOLD))
    c.clipRect(skia.Rect.MakeXYWH(x0, y - 40, ww + 60, 240))
    K.text(c, name, x0 + 28, y + 76, 66, "luckiest-guy-400", WHITE, align="left", tag=tag, outline=INK, ow=8)
    K.text(c, sub, x0 + 28, y + 150, 38, "comic-neue-700", (255, 240, 160), align="left", tag=tag)
    c.restore()
    if k > 0.9:
        sp = K.star_path(x0 + ww + 6, y + 52, 46, rot=T * 180)
        c.drawPath(sp, paint(INK, stroke=8))
        c.drawPath(sp, paint(shader=lin((x0 + ww - 40, y), (x0 + ww + 40, y + 100), [(255, 245, 170), GOLD, (200, 120, 0)])))


def nod_logo(c, x, y, s, T, a=1.0):
    """NOD-TV: a chrome bubble logo with a smiling head that nods yes, forever."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    nod = math.sin(T * 2 * math.pi * 1.6) * 10
    c.drawCircle(0, 0, 120, paint(shader=rad((-30, -40), 160, [(255, 255, 255), (255, 150, 210), HOT, (120, 0, 70)], [0, 0.3, 0.7, 1]), a=a))
    c.drawCircle(0, 0, 120, paint(INK, a, stroke=10))
    c.save()
    c.translate(0, nod * 0.6)
    c.rotate(nod * 0.3)
    c.drawCircle(-36, -22, 14, paint(INK, a))
    c.drawCircle(36, -22, 14, paint(INK, a))
    c.drawPath(path(K.bez((-60, 22), (0, 90 + nod), (60, 22), 16), closed=False), paint(INK, a, stroke=13))
    c.restore()
    c.drawOval(skia.Rect.MakeXYWH(-70, -100, 90, 50), paint(WHITE, 0.6 * a))
    K.chrome_text(c, "NOD-TV", 0, 205, 104, T, "rubik-900", face=((255, 255, 255), (190, 200, 230), (90, 100, 140)), tag="logo")
    c.restore()


def ch99_bug(c, x=150, y=300, T=0.0, a=0.9):
    """The public-access station's corner bug."""
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 104, y - 56, 208, 92), 14, 14), paint(INK, 0.55 * a))
    K.text(c, "CH 99", x, y + 6, 54, "vt323-400", (255, 255, 255), tag="bug", a=a)
    K.text(c, "PUBLIC ACCESS", x, y + 30, 22, "vt323-400", (255, 236, 120), tag="bug", a=a)


def color_bars(c, x0=0, y0=0, w=W, h=H):
    cols = [(192, 192, 192), (192, 192, 0), (0, 192, 192), (0, 192, 0), (192, 0, 192), (192, 0, 0), (0, 0, 192)]
    bw = w / 7
    for i, cc in enumerate(cols):
        c.drawRect(skia.Rect.MakeXYWH(x0 + i * bw, y0, bw + 1, h * 0.67), paint(cc))
    cols2 = [(0, 0, 192), (19, 19, 19), (192, 0, 192), (19, 19, 19), (0, 192, 192), (19, 19, 19), (192, 192, 192)]
    for i, cc in enumerate(cols2):
        c.drawRect(skia.Rect.MakeXYWH(x0 + i * bw, y0 + h * 0.67, bw + 1, h * 0.08), paint(cc))
    c.drawRect(skia.Rect.MakeXYWH(x0, y0 + h * 0.75, w, h * 0.25), paint((10, 10, 10)))
    for i, cc in enumerate([(0, 33, 76), (255, 255, 255), (50, 0, 106)]):
        c.drawRect(skia.Rect.MakeXYWH(x0 + i * w / 6, y0 + h * 0.75, w / 6, h * 0.25), paint(cc))


# ------------------------------------------------------------------ freeze frames with scribbled labels

def scribble_arrow(c, x0, y0, x1, y1, color=WHITE, w=9, k=1.0, seed=0, bend=0.25):
    """A marker arrow drawn on: a wobbly curve, then the two strokes of the head."""
    rng = np.random.default_rng(seed)
    mx, my = (x0 + x1) / 2 - (y1 - y0) * bend, (y0 + y1) / 2 + (x1 - x0) * bend
    pts = K.bez((x0, y0), (mx, my), (x1, y1), 30) + rng.normal(0, 1.2, (30, 2))
    n = max(2, int(len(pts) * min(1.0, k * 1.4)))
    c.drawPath(path(pts[:n], closed=False), paint(INK, stroke=w + 7))
    c.drawPath(path(pts[:n], closed=False), paint(color, stroke=w))
    if k > 0.75:
        d = pts[-1] - pts[-4]
        a = math.atan2(d[1], d[0])
        for s in (-1, 1):
            hx, hy = x1 - 46 * math.cos(a + s * 0.5), y1 - 46 * math.sin(a + s * 0.5)
            c.drawLine(x1, y1, hx, hy, paint(INK, stroke=w + 7))
            c.drawLine(x1, y1, hx, hy, paint(color, stroke=w))


def scrawl(c, s, x, y, size=58, color=WHITE, rot=-4, k=1.0, fname="permanent-marker-400", tag="scrawl", align="center"):
    """Handwritten marker lettering, written on letter by letter."""
    n = max(0, min(len(s), int(math.ceil(len(s) * k))))
    if n == 0:
        return
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    f = K.font(fname, size)
    full = f.measureText(s)
    x0 = -full / 2 if align == "center" else (0 if align == "left" else -full)
    c.drawString(s[:n], x0, 0, f, paint(INK, stroke=size * 0.2))
    c.drawString(s[:n], x0, 0, f, paint(color))
    K.reg_local(c, x0, -size * 0.8, x0 + full, size * 0.25, tag)
    c.restore()


def freeze_tint(arr, k=1.0):
    """The freeze-frame look: a flash, then slightly crushed and cooler."""
    if k <= 0:
        return
    rgb = arr[..., :3].astype(np.float32)
    y = rgb @ np.array([0.3, 0.59, 0.11], np.float32)
    out = rgb * (1 - 0.35 * k) + y[..., None] * 0.35 * k
    arr[..., :3] = np.clip((out - 128) * (1 + 0.15 * k) + 128, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ phone camera

def phone_ui(c, T, t_rec=0.0, label="1080p  30", flip=False):
    """A phone camera's recording screen: REC dot and timer, focus brackets, battery, grid."""
    for x in (W / 3, 2 * W / 3):
        c.drawLine(x, 230, x, H - 400, paint(WHITE, 0.18, stroke=2))
    for y in (H / 3, 2 * H / 3):
        c.drawLine(0, y, W, y, paint(WHITE, 0.18, stroke=2))
    secs = max(0.0, T - t_rec)
    on = int(T * 2) % 2 == 0
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(W / 2 - 120, 236, 240, 64), 14, 14), paint((230, 30, 40), 0.9))
    if on:
        c.drawCircle(W / 2 - 84, 268, 12, paint(WHITE))
    K.text(c, f"00:{int(secs) // 60:02d}:{int(secs) % 60:02d}", W / 2 + 20, 284, 40, "jost-600", WHITE, tag="phone")
    fx, fy, fs = W / 2 - 40, 760, 230
    for sx in (-1, 1):
        for sy in (-1, 1):
            c.drawLine(fx + sx * fs, fy + sy * fs, fx + sx * (fs - 50), fy + sy * fs, paint((255, 220, 60), stroke=5))
            c.drawLine(fx + sx * fs, fy + sy * fs, fx + sx * fs, fy + sy * (fs - 50), paint((255, 220, 60), stroke=5))


# ------------------------------------------------------------------ camera moves

def shake(T, amp=8.0, seed=0, rot=0.6):
    """Handheld wobble: smooth noise in x, y and roll."""
    def n(f, ph):
        return (math.sin(T * f + ph) * 0.6 + math.sin(T * f * 2.3 + ph * 1.7) * 0.3 + math.sin(T * f * 5.1 + ph * 0.3) * 0.1)
    return amp * n(1.9, seed), amp * n(2.3, seed + 1.3), rot * n(1.3, seed + 2.1)


def apply_cam(arr, dx=0.0, dy=0.0, rot=0.0, zoom=1.0, cx=W / 2, cy=H / 2, blur=0.0):
    """Re-frame a finished frame: shift, roll and zoom about (cx, cy) (zoom >= 1 never shows an edge)."""
    if abs(dx) < 0.01 and abs(dy) < 0.01 and abs(rot) < 0.001 and abs(zoom - 1) < 1e-4:
        return arr
    z = max(zoom, 1.0 + (abs(dx) + abs(dy)) / 700 + abs(rot) * 0.02)
    out = np.zeros_like(arr)
    s = skia.Surface(out)
    c = s.getCanvas()
    c.translate(cx + dx, cy + dy)
    c.rotate(rot)
    c.scale(z, z)
    c.translate(-cx, -cy)
    p = skia.Paint()
    if blur > 0:
        p.setImageFilter(skia.ImageFilters.Blur(blur * 0.3, blur, skia.TileMode.kClamp))
    c.drawImage(K.image(arr), 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    return out


# ------------------------------------------------------------------ the video mixer

def page_curl(a, b, k, corner="br"):
    """The page curl: the old shot peels away from the bottom-right corner like a page of a magazine, its back
    (paper white, shaded) folding over, revealing the new shot beneath."""
    k = ease(k)
    out = b.copy()
    s = skia.Surface(out)
    c = s.getCanvas()
    if k >= 1:
        return out
    L = (W + H) * (1 - 1.08 * k)                                  # the fold line: x + y = L, sweeping up and left
    big = 1e4
    keep = path([(L + big, -big), (-big, L + big), (-big, -big)])
    beyond = path([(L + big, -big), (-big, L + big), (big * 2, big * 2)])
    c.save()
    c.clipPath(keep, doAntiAlias=True)
    c.drawImage(K.image(a), 0, 0)
    c.restore()
    # the flap: the page beyond the fold, mirrored across it, showing its plain paper back
    m = skia.Matrix()
    m.setAll(0, -1, L, -1, 0, L, 0, 0, 1)                         # reflection across x + y = L
    c.save()
    c.concat(m)
    c.clipRect(skia.Rect.MakeWH(W, H))
    c.clipPath(beyond, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(-40, -40, W + 40, H + 40).makeOffset(18, 18), paint(INK, 0.4, blur=22))
    c.drawPaint(paint(shader=lin((L / 2, L / 2), (L / 2 + 300, L / 2 + 300), [(204, 198, 190), (252, 248, 240), (226, 220, 210)], [0, 0.4, 1])))
    c.restore()
    c.drawLine(L + 2000, -2000, -2000, L + 2000, paint(INK, 0.3, stroke=5, blur=3))
    return out


def cube(a, b, k, direction=1):
    """The spinning cube: the old shot is one face of a box that turns away, the new shot the next face."""
    k = ease(k)
    out = np.zeros_like(a)
    out[..., 3] = 255
    s = skia.Surface(out)
    c = s.getCanvas()
    c.drawRect(skia.Rect.MakeWH(W, H), paint(INK))
    th = k * math.pi / 2
    depth = W * 1.6
    def face(img, ang):
        # a face of a cube of side W centred at z = W/2, rotated by ang about the vertical axis, perspective from z = -depth
        cos, sin = math.cos(ang), math.sin(ang)
        pts = []
        for (u, v) in ((-W / 2, -H / 2), (W / 2, -H / 2), (W / 2, H / 2), (-W / 2, H / 2)):
            x3 = u * cos - (-W / 2) * sin
            z3 = u * sin + (-W / 2) * cos + W / 2
            sc = depth / (depth + z3)
            pts.append((W / 2 + x3 * sc * 0.82, H / 2 + v * sc * 0.82))
        if (pts[1][0] - pts[0][0]) <= 1:
            return
        m = skia.Matrix()
        src = [skia.Point(0, 0), skia.Point(W, 0), skia.Point(W, H), skia.Point(0, H)]
        if not m.setPolyToPoly(src, [skia.Point(*p) for p in pts]):
            return
        c.save()
        c.concat(m)
        c.drawImage(K.image(img), 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear))
        c.drawRect(skia.Rect.MakeWH(W, H), paint(INK, 0.45 * abs(math.sin(ang))))
        c.restore()
    if direction > 0:
        face(a, -th)
        face(b, math.pi / 2 - th)
    else:
        face(a, th)
        face(b, -math.pi / 2 + th)
    return out


def checker(a, b, k, n=6):
    """A checkerboard dissolve, square by square, in a diagonal sweep."""
    out = a.copy()
    s = skia.Surface(out)
    c = s.getCanvas()
    cs = W / n
    rows = int(math.ceil(H / cs))
    p = skia.Path()
    for i in range(n):
        for j in range(rows):
            t = (i + j) / (n + rows - 2)
            if k * 1.3 - 0.3 > t:
                p.addRect(skia.Rect.MakeXYWH(i * cs, j * cs, cs + 1, cs + 1))
    c.save()
    c.clipPath(p)
    c.drawImage(K.image(b), 0, 0)
    c.restore()
    return out


# ------------------------------------------------------------------ VHS

_VHS = {}


def vhs(arr, T, idx, k=1.0, osd=None, track=0.0):
    """Public-access VHS: soft luma, chroma smeared sideways and shifted, a bit of colour bleed, scanlines,
    tape noise, a wobbling tracking band, and the head-switching tear at the bottom."""
    if k <= 0:
        return
    im = Image.fromarray(np.ascontiguousarray(arr[..., :3]))
    yy, cb, cr = im.convert("YCbCr").split()
    yy = yy.resize((W // 2, H // 2), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    cb = cb.resize((W // 8, H // 2), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    cr = cr.resize((W // 8, H // 2), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    cr = Image.fromarray(np.roll(np.asarray(cr), 10, axis=1))
    out = np.asarray(Image.merge("YCbCr", (yy, cb, cr)).convert("RGB")).astype(np.int16)
    rng = np.random.default_rng(idx * 13 + 1)
    # line-by-line horizontal jitter
    jit = (rng.normal(0, 1.2, H // 4).repeat(4)).astype(int)
    ys = np.arange(H)
    # tracking band
    band_y = int((T * 180) % (H + 400)) - 200
    for y0 in range(max(0, band_y), min(H, band_y + 90), 2):
        jit[y0] += int(rng.integers(-22, 22) * (0.5 + track))
    # head-switching tear at the bottom
    for y0 in range(H - 34, H):
        jit[y0] += 30 + (y0 - (H - 34)) * 2
    rows = out[ys[:, None], (np.arange(W)[None, :] - jit[:, None]) % W]
    noise = rng.normal(0, 7, (H // 2, W // 4)).repeat(2, 0).repeat(4, 1)[:H, :W]
    rows = rows + noise[..., None].astype(np.int16)
    rows[::3] = (rows[::3] * 0.86).astype(np.int16)
    if band_y > -100:
        lo, hi = max(0, band_y), min(H, band_y + 90)
        if hi > lo:
            sn = rng.integers(0, 2, (hi - lo, W // 6)).repeat(6, 1)[:, :W] * 90
            rows[lo:hi] = rows[lo:hi] + sn[..., None]
    res = np.clip(rows, 0, 255).astype(np.uint8)
    arr[..., :3] = (arr[..., :3] * (1 - k) + res * k).astype(np.uint8) if k < 1 else res


def vhs_osd(c, T, text="PLAY", date="JUL 14 1994", clock=None, x=110, y=320, a=1.0):
    """The camcorder's on-screen display: PLAY with a triangle, a date stamp in the corner."""
    K.text(c, text, x + 70, y, 58, "vt323-400", WHITE, align="left", tag="osd", a=a, outline=(0, 0, 0), ow=6)
    c.drawPath(path([(x, y - 44), (x, y - 4), (x + 40, y - 24)]), paint(WHITE, a))
    if date:
        K.text(c, date, W - 110, H - 450, 52, "vt323-400", WHITE, align="right", tag="osd", a=a, outline=(0, 0, 0), ow=6)
    if clock:
        K.text(c, clock, W - 110, H - 400, 52, "vt323-400", WHITE, align="right", tag="osd", a=a, outline=(0, 0, 0), ow=6)
