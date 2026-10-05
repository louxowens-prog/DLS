"""The horror comic: an original 1950s-style horror book drawn procedurally, and live scenes that freeze into it.

ink       comicize(): a live frame becomes an inked, flat-coloured, halftone-dotted panel on yellowed newsprint
page      panels with thick borders and white gutters; a page-curl turn; a panel that zooms up to fill the frame
lettering yellow caption boxes, speech / shout / whisper balloons, the assistant's electric balloon, drawn sound words
shock     the background drops to one flat saturated colour (blood red, electric blue, sickly green) with jagged
          radiating rays and a fork of lightning
effects   lightning bolts, rain, fog banks, cobwebs, creepy-crawlies, too-red stylised blood
"""
import math

import numpy as np
import skia
from PIL import Image, ImageFilter

import kit as K
from kit import H, W, INK, WHITE, mix, paint, path

NEWS = (234, 216, 172)              # yellowed newsprint
BOXY = (255, 222, 70)               # caption-box yellow
BLOOD, ELEC, SICK, ACID, VIOLET = (212, 8, 24), (24, 70, 255), (120, 210, 40), (186, 255, 60), (92, 20, 140)
GORE = (226, 0, 22)                 # too-red, comic-book blood
SHOCKS = {"red": BLOOD, "blue": ELEC, "green": SICK, "violet": VIOLET, "yellow": (255, 210, 0)}


# ------------------------------------------------------------------ ink: a live frame becomes a comic panel

_fields = {}


def _field(pitch, angle):
    key = (pitch, angle)
    if key not in _fields:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        a = math.radians(angle)
        u = x * math.cos(a) + y * math.sin(a)
        v = -x * math.sin(a) + y * math.cos(a)
        du = np.mod(u, pitch) - pitch / 2
        dv = np.mod(v, pitch) - pitch / 2
        _fields[key] = np.sqrt(du * du + dv * dv).astype(np.float32)
    return _fields[key]


def dots(shade, pitch=12, angle=45):
    """0..1 shade -> 0..1 dot coverage (dot radius ~ sqrt(shade)); dots >= 8 px survive phone compression."""
    f = _field(pitch, angle)
    r = pitch * 0.72 * np.sqrt(np.clip(shade, 0, 1))
    return np.clip(r - f + 0.5, 0, 1) * (shade > 0.03)


def comicize(arr, k=1.0, levels=4, ink_w=1.0, dot=True, paper=NEWS, sat=1.35):
    """Turn a frame (RGBA uint8, in place) into a printed comic panel: flat colour, ink lines, Ben-Day dots, newsprint.
    k blends from the live frame (0) to the full print (1)."""
    if k <= 0.01:
        return arr
    src = arr[..., :3].astype(np.float32)
    im = Image.fromarray(arr[..., :3]).filter(ImageFilter.GaussianBlur(1.6))
    a = np.asarray(im, np.float32) / 255.0
    lum = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
    # ink: edges of the luminance (at half size), thickened, plus the deepest shadows filled solid
    sm = np.asarray(Image.fromarray((lum * 255).astype(np.uint8)).resize((W // 2, H // 2), Image.BILINEAR), np.float32) / 255
    gx = np.zeros_like(sm)
    gy = np.zeros_like(sm)
    gx[:, 1:-1] = sm[:, 2:] - sm[:, :-2]
    gy[1:-1] = sm[2:] - sm[:-2]
    g = np.sqrt(gx * gx + gy * gy)
    e = np.clip((g - 0.07 / ink_w) * 9.0, 0, 1)
    e = np.asarray(Image.fromarray((e * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).resize((W, H), Image.BILINEAR), np.float32) / 255
    solid = np.clip((0.1 - lum) * 14, 0, 1)
    ink = np.clip(np.maximum(e, solid), 0, 1)
    # flat colour: saturate, then posterise
    l3 = lum[..., None]
    c = np.clip(l3 + (a - l3) * sat, 0, 1)
    c = np.round(c * (levels - 1)) / (levels - 1)
    c = c * 0.62 + np.clip(c * 1.25, 0, 1) * 0.38                         # printed colour is lighter: the dots carry the dark
    out = c * (np.array(paper, np.float32) / 255.0)
    if dot:
        sh = np.clip((0.62 - lum) / 0.5, 0, 1) * 0.85
        d = dots(sh, 12, 45)[..., None]
        out = out * (1 - d) + np.array(INK, np.float32) / 255 * d
        hi = np.clip((lum - 0.55) / 0.4, 0, 1) * (np.max(c, axis=2) - np.min(c, axis=2) > 0.3)
        d2 = dots(hi * 0.5, 14, 15)[..., None]                           # pale dots in saturated light areas
        out = out * (1 - d2 * 0.35) + d2 * 0.35
    out = out * (1 - ink[..., None]) + np.array(INK, np.float32) / 255 * ink[..., None]
    out = out * 255
    arr[..., :3] = np.clip(src * (1 - k) + out * k, 0, 255).astype(np.uint8)
    return arr


def newsprint(arr, amt=1.0):
    """Paper fibre and a little ink spread over a printed page (the same every frame)."""
    if "np" not in _c:
        rng = np.random.default_rng(5)
        g = rng.normal(0, 1, (H // 3, W // 3)).astype(np.float32)
        g = np.asarray(Image.fromarray(np.clip(g * 40 + 128, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32)
        _c["np"] = ((g - 128) / 40 * 5.0)[..., None]
    arr[..., :3] = np.clip(arr[..., :3].astype(np.float32) + _c["np"] * amt, 0, 255).astype(np.uint8)
    return arr


_c = {}


# ------------------------------------------------------------------ page: panels, gutters, transitions

def panel(c, img, x0, y0, x1, y1, border=12, rot=0.0, shadow=True, a=1.0):
    """Draw an image (RGBA array) into a bordered panel; the image is scaled to cover the panel."""
    c.save()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c.translate(cx, cy)
    c.rotate(rot)
    c.translate(-cx, -cy)
    r = skia.Rect.MakeLTRB(x0, y0, x1, y1)
    if shadow:
        c.drawRect(r.makeOffset(10, 14), paint(INK, 0.55 * a, blur=6))
    if img is not None:
        ih, iw = img.shape[:2]
        sc = max((x1 - x0) / iw, (y1 - y0) / ih)
        sw, sh = (x1 - x0) / sc, (y1 - y0) / sc
        src = skia.Rect.MakeXYWH((iw - sw) / 2, (ih - sh) / 2, sw, sh)
        p = skia.Paint(AntiAlias=True)
        p.setAlphaf(a)
        c.drawImageRect(K.image(img), src, r, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    c.drawRect(r, paint(INK, a, stroke=border, cap="butt"))
    c.restore()


def page_bg(c, color=NEWS, seed=0, ghosts=True):
    """A blank comic page: newsprint, and the faint outlines of the panels around (printed on the other side)."""
    c.drawColor(K.col(color))
    if ghosts:
        rng = K.rng_at(seed, 3)
        for i in range(6):
            x0, y0 = rng.uniform(-100, 700), rng.uniform(-200, 1700)
            c.drawRect(skia.Rect.MakeXYWH(x0, y0, rng.uniform(300, 600), rng.uniform(300, 500)), paint(mix(color, INK, 0.12), 0.6, stroke=8))


def page_turn(prev, cur, k, tilt=0.18):
    """The page turns: the old frame lifts from the right and folds over to the left, showing its yellowed back, and the
    new frame is revealed underneath. prev, cur: RGBA arrays; returns a new array."""
    k = K.ease(k) * 0.55 + k * 0.45
    out = cur.copy()
    s = skia.Surface(out)
    c = s.getCanvas()
    X = W + 260 - (W + 900) * k
    dx = H * tilt
    xt, xb = X + dx / 2, X - dx / 2                                       # the fold: from (xt, 0) to (xb, H)
    # the fold line's unit normal (pointing right) for the mirror
    fx, fy = xb - xt, H
    L = math.hypot(fx, fy)
    nx, ny = fy / L, -fx / L
    if nx < 0:
        nx, ny = -nx, -ny

    def mirror(x, y):
        d = (x - xt) * nx + (y - 0) * ny
        return x - 2 * d * nx, y - 2 * d * ny
    left = path([(-50, -50), (xt + (xt - xb) * 50 / H, -50), (xb - (xt - xb) * 50 / H, H + 50), (-50, H + 50)])
    right = [(xt, 0), (W, 0), (W, H), (xb, H)]
    flap = path([mirror(x, y) for x, y in right])
    # the shadow the lifting page casts on the new one
    c.save()
    c.clipPath(path([(xt, -50), (W + 400, -50), (W + 400, H + 50), (xb, H + 50)]), doAntiAlias=True)
    c.drawPath(path([(xt, -50), (xt + 160, -50), (xb + 160, H + 50), (xb, H + 50)]), paint(INK, 0.55, blur=40))
    c.restore()
    # what is left of the old page
    c.save()
    c.clipPath(left, doAntiAlias=True)
    c.drawImage(K.image(prev), 0, 0)
    c.restore()
    # the back of the turning page: newsprint, the print showing through, shaded toward the fold
    c.save()
    c.clipPath(left, doAntiAlias=True)
    c.drawPath(flap, paint(INK, 0.35, blur=24))
    c.clipPath(flap, doAntiAlias=True)
    c.drawPath(flap, paint(NEWS))
    m = skia.Matrix()
    # mirror the old print onto the back (faint)
    p0, p1 = (xt, 0), (xb, H)
    ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    c.save()
    c.translate(xt, 0)
    c.rotate(ang)
    c.scale(1, -1)
    c.rotate(-ang)
    c.translate(-xt, 0)
    q = skia.Paint()
    q.setAlphaf(0.12)
    c.drawImage(K.image(prev), 0, 0, skia.SamplingOptions(), q)
    c.restore()
    mx, my = mirror(W, H / 2)
    c.drawPath(flap, paint(shader=K.lin(((xt + xb) / 2, H / 2), (mx, my), [(150, 130, 100, 0.55), (255, 250, 236, 0.0), (120, 100, 70, 0.25)],
                                        [0.0, 0.6, 1.0])))
    c.restore()
    c.drawLine(xt, 0, xb, H, paint(INK, 0.35, stroke=2))
    return out


def panel_zoom(cur, k, bg=NEWS, rect=(150, 520, 930, 1260), rot=-2.5, under=None):
    """The new shot starts as a panel on a comic page and zooms up to fill the frame."""
    k = K.ease(k)
    out = np.zeros_like(cur)
    s = skia.Surface(out)
    c = s.getCanvas()
    if under is not None:
        c.drawImage(K.image(under), 0, 0)
    else:
        page_bg(c, bg, seed=int(rect[0]))
    x0, y0, x1, y1 = rect
    x0, y0, x1, y1 = K.lerp(x0, -20, k), K.lerp(y0, -20, k), K.lerp(x1, W + 20, k), K.lerp(y1, H + 20, k)
    panel(c, cur, x0, y0, x1, y1, border=K.lerp(14, 0, k), rot=rot * (1 - k), shadow=k < 0.9)
    return out


def to_panel(arr, k, rect=(70, 300, 1010, 1380), rot=-1.5, bg=NEWS, seed=0, extra=None):
    """A live frame freezing into a panel: it shrinks onto a page (k 0..1); `extra(c)` draws more of the page."""
    k = K.ease(k)
    img = arr.copy()
    out = arr
    c = skia.Surface(out).getCanvas()
    page_bg(c, bg, seed=seed)
    if extra is not None:
        extra(c)
    x0, y0, x1, y1 = rect
    x0, y0, x1, y1 = K.lerp(-30, x0, k), K.lerp(-30, y0, k), K.lerp(W + 30, x1, k), K.lerp(H + 30, y1, k)
    panel(c, img, x0, y0, x1, y1, border=K.lerp(0, 14, k), rot=rot * k, shadow=k > 0.1)
    return out


# ------------------------------------------------------------------ lettering

def _lines(s, f, maxw):
    return K.wrap(s, f, maxw)


def caption_box(c, s, x, y, maxw=880, size=50, k=1.0, rot=-1.0, fname="comic-neue-700", fill=BOXY, color=INK, tag="caption",
                anchor="bottom", edge=INK, a=1.0, upper=True):
    """A yellow comic caption box, hand-lettered in capitals with a hard ink drop shadow. (x, y): centre-bottom
    (anchor='bottom') or centre-top. Returns the box rect."""
    if k <= 0.01 or not s:
        return None
    txt = s.upper() if upper else s
    while True:
        f = K.font(fname, size)
        lines = K.wrap_balanced(txt, f, maxw - 56)
        if len(lines) > 2:
            lines = _lines(txt, f, maxw - 56)
        if max(f.measureText(ln) for ln in lines) <= maxw - 56 or size < 34:
            break
        size *= 0.94
    lh = size * 1.14
    tw = max(f.measureText(ln) for ln in lines)
    bw, bh = tw + 56, lh * len(lines) + 30
    by = y - bh if anchor == "bottom" else y
    c.save()
    c.translate(x, by + bh / 2)
    c.rotate(rot)
    c.scale(k, k)
    c.translate(-bw / 2, -bh / 2)
    c.drawRect(skia.Rect.MakeXYWH(9, 11, bw, bh), paint(INK, a))
    c.drawRect(skia.Rect.MakeXYWH(0, 0, bw, bh), paint(fill, a))
    c.drawRect(skia.Rect.MakeXYWH(0, 0, bw, bh), paint(edge, a, stroke=5))
    for i, ln in enumerate(lines):
        lw = f.measureText(ln)
        c.drawString(ln, (bw - lw) / 2, 15 + lh * (i + 0.8), f, paint(color, a))
    K.reg_local(c, 0, 0, bw + 9, bh + 11, tag)
    c.restore()
    return (x - bw / 2, by, bw, bh)


def host_box(c, s, x, y, maxw=880, size=50, k=1.0, a=1.0, tag="caption"):
    """The host's own caption: acid-green lettering on a purple-black slab whose bottom edge drips."""
    if k <= 0.01 or not s:
        return None
    f = K.font("comic-neue-700", size)
    lines = K.wrap_balanced(s.upper(), f, maxw - 60)
    if len(lines) > 2:
        lines = _lines(s.upper(), f, maxw - 60)
    lh = size * 1.14
    tw = max(f.measureText(ln) for ln in lines)
    bw, bh = tw + 60, lh * len(lines) + 30
    x0, y0 = x - bw / 2, y - bh
    c.save()
    c.translate(x, y - bh / 2)
    c.scale(k, k)
    c.translate(-x, -(y - bh / 2))
    rng = K.rng_at(len(s), 9)
    pts = [(x0, y0), (x0 + bw, y0), (x0 + bw, y0 + bh)]
    n = 9
    for i in range(1, n):
        u = 1 - i / n
        px = x0 + bw * u
        d = rng.uniform(0, 26) if rng.random() < 0.6 else 0
        pts += [(px + 8, y0 + bh), (px + 4, y0 + bh + d), (px - 4, y0 + bh + d), (px - 8, y0 + bh)]
    pts.append((x0, y0 + bh))
    p = path(pts)
    c.save()
    c.translate(8, 10)
    c.drawPath(p, paint((0, 0, 0), 0.8 * a))
    c.restore()
    c.drawPath(p, paint((36, 8, 44), a))
    c.drawPath(p, paint(ACID, a, stroke=4))
    for i, ln in enumerate(lines):
        lw = f.measureText(ln)
        c.drawString(ln, x - lw / 2, y0 + 15 + lh * (i + 0.8), f, paint(ACID, a))
    K.reg(x0, y0, x0 + bw + 8, y0 + bh + 10, tag)
    c.restore()
    return (x0, y0, bw, bh)


def _balloon_path(cx, cy, w, h, kind, seed=0):
    rx, ry = w / 2, h / 2
    if kind == "shout":
        rng = K.rng_at(seed, 5)
        pts = []
        n = 26
        for i in range(n):
            a = 2 * math.pi * i / n
            r = 1.0 if i % 2 == 0 else 1.2 + rng.uniform(0, 0.1)
            pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
        return path(pts)
    if kind == "electric":
        p = skia.Path()
        p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry), 26, 26))
        return p
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry))
    return p


def balloon(c, s, cx, cy, tail=None, size=50, maxw=560, k=1.0, kind="speech", tag="balloon", a=1.0, rot=0.0, seed=0, empty=False):
    """A speech balloon (oval), shout (jagged burst), whisper (dashed), or electric (the assistant: a glowing rounded
    screen with a zigzag tail, typed in a digital face). empty=True: a balloon with nothing in it."""
    if k <= 0.01:
        return None
    fname = "vt323-400" if kind == "electric" else "comic-neue-700"
    sz = size * (1.22 if kind == "electric" else 1.0)
    f = K.font(fname, sz)
    txt = s.upper()
    lines = [" "] if empty else K.wrap_balanced(txt, f, maxw)
    if len(lines) > 2:
        lines = _lines(txt, f, maxw)
    lh = sz * (1.0 if kind == "electric" else 1.12)
    tw = 260 if empty else max(f.measureText(ln) for ln in lines)
    w = tw * (1.42 if kind in ("speech", "whisper") else 1.18) + 70
    h = lh * len(lines) * (1.55 if kind in ("speech", "whisper") else 1.25) + 46
    if kind == "shout":
        w, h = w * 1.12, h * 1.25
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(k, k)
    c.translate(-cx, -cy)
    body = _balloon_path(cx, cy, w, h, kind, seed)
    fill = (226, 248, 255) if kind == "electric" else WHITE
    edge = (0, 90, 200) if kind == "electric" else INK
    if tail is not None:
        tx, ty = tail
        ang = math.atan2(ty - cy, tx - cx)
        bx, by = cx + w / 2 * 0.7 * math.cos(ang), cy + h / 2 * 0.7 * math.sin(ang)
        perp = ang + math.pi / 2
        wd = min(w, h) * 0.14
        if kind == "electric":                                          # a lightning-zigzag tail
            mx, my = (bx + tx) / 2, (by + ty) / 2
            tp = path([(bx + wd * math.cos(perp), by + wd * math.sin(perp)), (mx + wd * 0.9 * math.cos(perp), my + wd * 0.9 * math.sin(perp)),
                       (mx - wd * 0.3 * math.cos(perp), my - wd * 0.3 * math.sin(perp)), (tx, ty),
                       (mx - wd * 1.3 * math.cos(perp) + (bx - tx) * 0.12, my - wd * 1.3 * math.sin(perp) + (by - ty) * 0.12),
                       (bx - wd * math.cos(perp), by - wd * math.sin(perp))])
        else:
            q = ((bx + tx) / 2 + wd * 0.8 * math.cos(perp), (by + ty) / 2 + wd * 0.8 * math.sin(perp))
            tp = path([(bx + wd * math.cos(perp), by + wd * math.sin(perp)), q, (tx, ty), (bx - wd * math.cos(perp), by - wd * math.sin(perp))])
        body = skia.Op(body, tp, skia.PathOp.kUnion_PathOp) or body
    if kind == "electric":
        g = paint((80, 200, 255), 0.6 * a, blur=22)
        c.drawPath(body, g)
    c.save()
    c.translate(8, 10)
    c.drawPath(body, paint(INK, 0.5 * a))
    c.restore()
    c.drawPath(body, paint(fill, a))
    if kind == "whisper":
        p = paint(edge, a, stroke=5)
        p.setPathEffect(skia.DashPathEffect.Make([18, 12], 0))
        c.drawPath(body, p)
    else:
        c.drawPath(body, paint(edge, a, stroke=6 if kind != "electric" else 5))
    if kind == "electric":                                              # scan lines on the screen
        c.save()
        c.clipPath(body, doAntiAlias=True)
        for yy in range(int(cy - h / 2), int(cy + h / 2), 7):
            c.drawLine(cx - w / 2, yy, cx + w / 2, yy, paint((0, 90, 200), 0.08 * a, stroke=2))
        c.restore()
    tcol = (0, 60, 160) if kind == "electric" else INK
    if not empty:
        for i, ln in enumerate(lines):
            lw = f.measureText(ln)
            c.drawString(ln, cx - lw / 2, cy - lh * len(lines) / 2 + lh * (i + 0.78), f, paint(tcol, a))
        K.reg_local(c, cx - tw / 2 - 8, cy - lh * len(lines) / 2 - 6, cx + tw / 2 + 8, cy + lh * len(lines) / 2 + 6, tag)
    c.restore()
    return (cx - w / 2, cy - h / 2, w, h)


def text_path(s, fname, size, tracking=0.0):
    f = K.font(fname, size)
    g = f.textToGlyphs(s)
    ws = f.getWidths(g)
    p = skia.Path()
    x = 0.0
    for gid, w in zip(g, ws):
        q = f.getPath(gid)
        if q is not None:
            q.offset(x, 0)
            p.addPath(q)
        x += w + tracking
    return p, x - tracking


def sfx(c, s, x, y, size, k=1.0, rot=-8, fill=(255, 226, 0), fill2=(255, 120, 0), edge=INK, fname="bangers-400", extrude=(10, 12),
        tag="sfx", tracking=3.0, a=1.0, wobble=0.0):
    """A drawn sound word: extruded ink block letters, a two-colour fill and a fat outline."""
    if k <= 0.01:
        return
    p, w = text_path(s, fname, size, tracking)
    b = p.getBounds()
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(k, k)
    if wobble:
        c.skew(wobble * 0.1, 0)
    c.translate(-(b.left() + b.right()) / 2, -(b.top() + b.bottom()) / 2)
    ex, ey = extrude
    for i in range(7, 0, -1):
        c.save()
        c.translate(ex * i / 7, ey * i / 7)
        c.drawPath(p, paint(edge, a))
        c.drawPath(p, paint(edge, a, stroke=size * 0.1))
        c.restore()
    c.drawPath(p, paint(edge, a, stroke=size * 0.13))
    c.drawPath(p, paint(shader=K.lin((0, b.top()), (0, b.bottom()), [fill, fill2]), a=a))
    c.save()
    c.translate(-size * 0.015, -size * 0.02)
    c.drawPath(p, paint(WHITE, 0.5 * a, stroke=size * 0.018))
    c.restore()
    K.reg_local(c, b.left() - size * 0.07, b.top() - size * 0.07, b.right() + ex + size * 0.07, b.bottom() + ey + size * 0.07, tag)
    c.restore()


def drip_title(c, s, x, y, size, color=(200, 10, 20), edge=INK, k=1.0, tag="title", seed=0, fname="creepster-400", drip=1.0, a=1.0,
               shadow=(0, 0, 0)):
    """Horror-comic title lettering: fat outlined letters in one colour that run with drips."""
    if k <= 0.01:
        return 0
    p, w = text_path(s, fname, size, 2.0)
    b = p.getBounds()
    c.save()
    c.translate(x, y)
    c.scale(k, k)
    c.translate(-(b.left() + b.right()) / 2, 0)
    rng = K.rng_at(seed, len(s))
    drips = skia.Path()
    for i in range(int(len(s) * 1.6)):
        dx = rng.uniform(b.left() + 10, b.right() - 10)
        L = rng.uniform(0.08, 0.5) * size * drip
        wd = rng.uniform(0.04, 0.08) * size
        drips.addPath(K.capsule(dx, b.bottom() - size * 0.15, dx, b.bottom() + L, wd, wd * 1.25))
    full = skia.Op(p, drips, skia.PathOp.kUnion_PathOp) or p
    c.save()
    c.translate(size * 0.06, size * 0.07)
    c.drawPath(full, paint(shadow, 0.9 * a))
    c.drawPath(full, paint(shadow, 0.9 * a, stroke=size * 0.12))
    c.restore()
    c.drawPath(full, paint(edge, a, stroke=size * 0.12))
    c.drawPath(full, paint(shader=K.lin((0, b.top()), (0, b.bottom() + size * 0.3), [mix(color, WHITE, 0.25), color, mix(color, INK, 0.35)]), a=a))
    c.save()
    c.translate(-size * 0.02, -size * 0.025)
    c.clipPath(full)
    c.drawPath(full, paint(WHITE, 0.35 * a, stroke=size * 0.025))
    c.restore()
    K.reg_local(c, b.left() - size * 0.08, b.top() - size * 0.08, b.right() + size * 0.12, b.bottom() + size * 0.12, tag)
    c.restore()
    return w * k


def label(c, s, x, y, size=40, fname="bangers-400", color=INK, align="center", rot=0.0, tag="label", a=1.0, outline=None, ow=8):
    """Plain lettering, registered for the lint."""
    f = K.font(fname, size)
    w = f.measureText(s)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.translate(-x, -y)
    if outline is not None:
        c.drawString(s, x0, y, f, paint(outline, a, stroke=ow))
    c.drawString(s, x0, y, f, paint(color, a))
    K.reg_local(c, x0, y - size * 0.8, x0 + w, y + size * 0.22, tag)
    c.restore()
    return w


# ------------------------------------------------------------------ shock lighting

def bolt_pts(x0, y0, x1, y1, seed=0, depth=6, rough=0.24):
    rng = K.rng_at(seed, 17)
    pts = [(x0, y0), (x1, y1)]
    amp = math.hypot(x1 - x0, y1 - y0) * rough
    for _ in range(depth):
        out = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
            mx, my = (ax + bx) / 2, (ay + by) / 2
            L = math.hypot(bx - ax, by - ay) + 1e-6
            nx, ny = -(by - ay) / L, (bx - ax) / L
            d = rng.uniform(-1, 1) * amp
            out += [(mx + nx * d, my + ny * d), (bx, by)]
        pts = out
        amp *= 0.55
    return pts


def bolt(c, x0, y0, x1, y1, seed=0, w=10, color=(255, 255, 255), glow=(160, 200, 255), a=1.0, branches=3):
    """A fork of lightning with a coloured glow and a few side branches."""
    if a <= 0.01:
        return
    pts = bolt_pts(x0, y0, x1, y1, seed)
    p = path(pts, closed=False)
    g = paint(glow, 0.7 * a, stroke=w * 4, blur=w * 2.2)
    c.drawPath(p, g)
    c.drawPath(p, paint(glow, a, stroke=w * 1.8))
    c.drawPath(p, paint(color, a, stroke=w))
    rng = K.rng_at(seed, 23)
    for j in range(branches):
        i = int(rng.uniform(0.2, 0.7) * len(pts))
        bx, by = pts[i]
        L = math.hypot(x1 - x0, y1 - y0) * rng.uniform(0.15, 0.35)
        ang = math.atan2(y1 - y0, x1 - x0) + rng.choice([-1, 1]) * rng.uniform(0.4, 0.9)
        q = bolt_pts(bx, by, bx + L * math.cos(ang), by + L * math.sin(ang), seed + 7 * j + 1, depth=4)
        pp = path(q, closed=False)
        c.drawPath(pp, paint(glow, 0.8 * a, stroke=w * 1.1))
        c.drawPath(pp, paint(color, a, stroke=w * 0.5))


def shock(c, color, T=0.0, cx=540, cy=820, seed=1, rays=34, bolts=2, a=1.0):
    """The background drops to one flat saturated colour, with jagged rays radiating from (cx, cy) and lightning."""
    colr = SHOCKS.get(color, color)
    c.drawColor(K.col(colr, a)) if a >= 1 else c.drawRect(skia.Rect.MakeWH(W, H), paint(colr, a))
    dark = mix(colr, INK, 0.55)
    lite = mix(colr, WHITE, 0.25)
    rng = K.rng_at(seed, 31)
    ph = math.floor(T * 12) / 12 * 0.6
    for i in range(rays):
        ang = 2 * math.pi * i / rays + ph * 0.15 + rng.uniform(-0.04, 0.04)
        r0, r1 = 120 + rng.uniform(0, 80), 2200
        wd = rng.uniform(0.03, 0.06)
        pts = [(cx + r0 * math.cos(ang), cy + r0 * math.sin(ang))]
        for j in range(1, 8):                                           # a zigzag ray, widening outward
            r = r0 + (r1 - r0) * j / 7
            zig = (wd * 0.6 if j % 2 else -wd * 0.6)
            pts.append((cx + r * math.cos(ang + zig), cy + r * math.sin(ang + zig)))
        back = [(cx + (r0 + (r1 - r0) * j / 7) * math.cos(ang + wd * (1 + j * 0.3)), cy + (r0 + (r1 - r0) * j / 7) * math.sin(ang + wd * (1 + j * 0.3)))
                for j in range(7, -1, -1)]
        c.drawPath(path(pts + back), paint(dark if i % 2 else lite, (0.8 if i % 2 else 0.35) * a))
    c.drawCircle(cx, cy, 260, paint(mix(colr, WHITE, 0.4), 0.5 * a, blur=120))
    for j in range(bolts):
        side = -1 if j % 2 == 0 else 1
        x0 = cx + side * rng.uniform(260, 420)
        bolt(c, x0, -40, x0 + side * rng.uniform(40, 160), rng.uniform(700, 1200), seed=seed * 13 + j + int(T * 8) % 3, w=9,
             glow=mix(colr, WHITE, 0.5), a=a)


# ------------------------------------------------------------------ weather and creepy things

def rain(c, T, x0=0, y0=0, x1=W, y1=H, n=140, seed=3, a=0.6, ang=0.18, color=(200, 214, 255), speed=2600, length=70):
    rng = K.rng_at(seed, 1)
    for i in range(n):
        x, y, v = rng.uniform(x0 - 200, x1), rng.uniform(0, 1), rng.uniform(0.7, 1.3)
        yy = y0 + ((y * (y1 - y0) + T * speed * v) % (y1 - y0 + length))
        xx = x + (yy - y0) * ang
        L = length * v
        c.drawLine(xx, yy - L, xx + L * ang, yy, paint(color, a * rng.uniform(0.3, 1.0), stroke=rng.uniform(1.2, 2.6)))


def fog(c, T, y0, y1, color=(190, 210, 200), a=0.5, seed=4, n=9, speed=24.0, x0=-300, x1=W + 300):
    """Banks of ground fog drifting across (soft blurred ellipses)."""
    rng = K.rng_at(seed, 2)
    for i in range(n):
        y = rng.uniform(y0, y1)
        w = rng.uniform(380, 760)
        x = x0 + ((rng.uniform(0, x1 - x0) + T * speed * rng.uniform(0.5, 1.5) * (1 if i % 2 else -1)) % (x1 - x0 + w)) - w / 2
        c.drawOval(skia.Rect.MakeXYWH(x, y - w * 0.12, w, w * 0.24), paint(color, a * rng.uniform(0.4, 0.9), blur=w * 0.12))


def cobweb(c, x, y, r, ang0=0.0, span=90.0, a=0.8, color=(230, 230, 236), seed=0, w=1.6):
    """A corner cobweb: threads fanning out from (x, y) over `span` degrees, with sagging cross-threads."""
    rng = K.rng_at(seed, 8)
    n = 7
    angs = [math.radians(ang0 + span * i / (n - 1)) for i in range(n)]
    for t in angs:
        c.drawLine(x, y, x + r * math.cos(t), y + r * math.sin(t), paint(color, a, stroke=w))
    for k in range(1, 7):
        rr = r * k / 7 * rng.uniform(0.92, 1.05)
        for t0, t1 in zip(angs[:-1], angs[1:]):
            p0 = (x + rr * math.cos(t0), y + rr * math.sin(t0))
            p1 = (x + rr * math.cos(t1), y + rr * math.sin(t1))
            mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
            sag = ((x - mid[0]) * 0.12, (y - mid[1]) * 0.12)
            c.drawPath(K.bez_path([p0, (mid[0] + sag[0], mid[1] + sag[1]), p1]), paint(color, a * 0.85, stroke=w * 0.8))


def beetle(c, x, y, s, ang, T, color=(30, 20, 14), shine=(120, 90, 60), seed=0):
    """A skittering beetle (legs scuttle on twos)."""
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(ang))
    c.scale(s, s)
    ph = (math.floor(T * 16 + seed) % 2) * 2 - 1
    for side in (-1, 1):
        for j, ox in enumerate((-10, 0, 10)):
            sw = ph * (1 if j % 2 else -1) * 5
            c.drawPath(path([(ox, side * 8), (ox + 6 + sw, side * 18), (ox + 2 + sw, side * 26)], closed=False), paint(color, stroke=2.4))
    c.drawOval(skia.Rect.MakeLTRB(-16, -10, 16, 10), paint(color))
    c.drawCircle(18, 0, 6, paint(color))
    c.drawLine(-14, 0, 14, 0, paint(mix(color, INK, 0.5), stroke=1.2))
    c.drawOval(skia.Rect.MakeLTRB(-8, -7, 6, -2), paint(shine, 0.7, blur=1.5))
    c.drawPath(path([(22, -3), (32, -10)], closed=False), paint(color, stroke=1.6))
    c.drawPath(path([(22, 3), (32, 10)], closed=False), paint(color, stroke=1.6))
    c.restore()


def spider(c, x, y, s, T, color=(16, 12, 12), seed=0, eyes=(220, 20, 20)):
    """A hairy spider hanging (legs flex on twos)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    ph = math.sin(math.floor(T * 12) / 12 * 9 + seed) * 4
    for side in (-1, 1):
        for j in range(4):
            a0 = math.radians(-60 + j * 38)
            kx, ky = side * (26 + 10 * math.cos(a0)), -10 + 34 * math.sin(a0) - 16
            ex, ey = side * (50 + 8 * j), -6 + j * 16 + ph * (1 if j % 2 else -1)
            c.drawPath(path([(side * 8, j * 5 - 6), (kx, ky), (ex, ey)], closed=False), paint(color, stroke=3.4))
    c.drawOval(skia.Rect.MakeLTRB(-16, -4, 16, 34), paint(color))
    c.drawCircle(0, -10, 11, paint(color))
    for ex in (-4, 4):
        c.drawCircle(ex, -12, 2.2, paint(eyes))
    c.restore()


def splat(c, x, y, r, seed=0, color=GORE, a=1.0, drips=True):
    """A stylised, too-red splash (flat colour, a highlight, round droplets: comic-book, never realistic)."""
    rng = K.rng_at(seed, 12)
    pts = []
    n = 16
    for i in range(n):
        ang = 2 * math.pi * i / n
        rr = r * (rng.uniform(0.55, 0.85) if i % 2 else rng.uniform(0.95, 1.35))
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    p = K.smooth(pts)
    c.drawPath(p, paint(color, a))
    for i in range(9):
        ang = rng.uniform(0, 2 * math.pi)
        d = r * rng.uniform(1.3, 2.1)
        c.drawCircle(x + d * math.cos(ang), y + d * math.sin(ang), r * rng.uniform(0.05, 0.14), paint(color, a))
    if drips:
        for i in range(3):
            dx = x + rng.uniform(-r * 0.6, r * 0.6)
            L = r * rng.uniform(0.6, 1.4)
            c.drawPath(K.capsule(dx, y + r * 0.3, dx, y + r * 0.3 + L, r * 0.12, r * 0.16), paint(color, a))
    c.drawOval(skia.Rect.MakeXYWH(x - r * 0.4, y - r * 0.45, r * 0.35, r * 0.18), paint(WHITE, 0.55 * a, blur=2))
