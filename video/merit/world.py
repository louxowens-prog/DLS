"""The places of the nightmare, painted: a night sky whose stars stand in a grid like the holes of a punched card, a
moon far too large with something turning inside it, black pines in banks of fog, a fire of burning records whose
sparks rise to become the stars. Everything is painted in light on near-black; the look's wash colours it."""
import math

import cv2
import numpy as np
import skia

import gel as G
import kit as K
from kit import BLACK, WHITE, H, W, mix, paint

_TEX = {}


def tex(name, fn):
    if name not in _TEX:
        _TEX[name] = fn()
    return _TEX[name]


# ------------------------------------------------------------------ painterly texture

def _brush_tex():
    """Fibrous paint texture: noise smeared along a slow swirl, grey around 128."""
    rng = np.random.default_rng(5)
    n = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    a = cv2.GaussianBlur(n, (0, 0), sigmaX=6, sigmaY=1.2)
    b = cv2.GaussianBlur(rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32), (0, 0), sigmaX=1.2, sigmaY=5)
    m = cv2.GaussianBlur(rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32), (0, 0), 40)
    m = (m - m.min()) / (m.max() - m.min() + 1e-6)
    t = a * m + b * (1 - m)
    t = cv2.resize(t, (W, H), interpolation=cv2.INTER_CUBIC)
    t = (t - t.mean()) / (t.std() + 1e-6)
    g = np.clip(128 + t * 30, 0, 255).astype(np.uint8)
    rgba = np.dstack([g, g, g, np.full_like(g, 255)])
    return K.image(rgba)


def paint_grain(c, a=0.5, blend=skia.BlendMode.kOverlay):
    """Overlay the brush texture on everything drawn so far (inside the current clip)."""
    img = tex("brush", _brush_tex)
    p = skia.Paint()
    p.setAlphaf(a)
    p.setBlendMode(blend)
    c.drawImage(img, 0, 0, skia.SamplingOptions(), p)


def _airbrush_noise():
    rng = np.random.default_rng(9)
    n = rng.normal(0, 1, (H // 8, W // 8)).astype(np.float32)
    n = cv2.resize(cv2.GaussianBlur(n, (0, 0), 3), (W, H), interpolation=cv2.INTER_CUBIC)
    n = (n - n.min()) / (n.max() - n.min())
    g = (n * 255).astype(np.uint8)
    return K.image(np.dstack([g, g, g, np.full_like(g, 255)]))


# ------------------------------------------------------------------ sky

def sky(c, top=(4, 2, 18), mid=(30, 10, 60), low=(90, 30, 90), y0=0, y1=H):
    c.drawRect(skia.Rect.MakeLTRB(0, y0, W, y1), paint(shader=K.lin((0, y0), (0, y1), [top, mid, low], [0.0, 0.55, 1.0])))


def card_stars(c, T, x0=0, y0=0, x1=W, y1=1100, cols=17, rows=22, a=1.0, seed=0, curve=0.06, pulse=1.0, color=(240, 236, 255)):
    """Stars that look wrong: a perfect grid, like the holes punched in a card, curving with the sky; some holes
    missing, the rest twinkling in slow waves that sweep across the grid like data being read."""
    rng = K.rng_at(seed, 31)
    hole = rng.random((rows, cols)) < 0.62
    for r in range(rows):
        for q in range(cols):
            if not hole[r, q]:
                continue
            u, v = q / (cols - 1), r / (rows - 1)
            x = x0 + (x1 - x0) * u
            y = y0 + (y1 - y0) * v + curve * (y1 - y0) * (2 * u - 1) ** 2 * (1 - v)
            wave = 0.5 + 0.5 * math.sin(T * 1.6 * pulse - u * 7 - v * 3 + seed)
            tw = 0.35 + 0.65 * wave ** 3
            s = 1.0 + 0.9 * (1 - v)
            p = G.glow_paint(color, a * tw)
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 3.0 * s, y - 6.0 * s, 6.0 * s, 12.0 * s), 1.5, 1.5, p)
            if tw > 0.8:
                G.pool(c, x, y, 16 * s, color, a * (tw - 0.8) * 1.6)


def real_stars(c, T, n=160, y1=1000, a=0.8, seed=0):
    rng = K.rng_at(seed, 37)
    for i in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, y1) ** 1.0
        r = rng.uniform(0.6, 2.2)
        tw = 0.6 + 0.4 * math.sin(T * rng.uniform(1, 4) + i)
        c.drawCircle(x, y, r, G.glow_paint((240, 235, 255), a * tw))


def _moon_tex():
    """A moon's face: maria and craters from layered noise, pale silver; 640 px across."""
    S = 640
    rng = np.random.default_rng(12)
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    d = np.sqrt((x - S / 2) ** 2 + (y - S / 2) ** 2) / (S / 2)
    n = np.zeros((S, S), np.float32)
    for sc, amp in ((40, 1.0), (14, 0.5), (5, 0.25)):
        g = rng.normal(0, 1, (S // sc + 2, S // sc + 2)).astype(np.float32)
        n += amp * cv2.resize(g, (S, S), interpolation=cv2.INTER_CUBIC)
    n = (n - n.mean()) / n.std()
    base = 0.78 + 0.1 * n
    for _ in range(60):                                        # craters: a dark floor, a bright rim
        cx, cy, r = rng.uniform(0, S), rng.uniform(0, S), rng.uniform(4, 40)
        dd = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / r
        base -= 0.12 * np.exp(-dd ** 4) * rng.uniform(0.5, 1)
        base += 0.07 * np.exp(-((dd - 1.05) / 0.12) ** 2)
    limb = np.clip(1 - d ** 6, 0, 1) * (0.75 + 0.25 * np.sqrt(np.clip(1 - d ** 2, 0, 1)))
    v = np.clip(base * limb, 0, 1)
    rgb = np.stack([v * 206, v * 202, v * 218], -1)
    alpha = np.clip((1 - d) * S / 2.5, 0, 1) * 255
    return K.image(np.dstack([rgb, alpha]).astype(np.uint8))


def moon(c, x, y, r, T, a=1.0, eye=0.0, pupil=(0.0, 0.0), corona=1.0, color=(255, 255, 255), iris_col=(255, 60, 40)):
    """The moon, far too large, with a corona like an eclipse. eye (0..1): something inside it opens - a ring of fibres
    and a black pupil turning to look (pupil: direction, -1..1)."""
    if corona > 0:
        G.pool(c, x, y, r * 2.4, (150, 120, 255), 0.22 * a * corona)
        G.pool(c, x, y, r * 1.35, (230, 220, 255), 0.35 * a * corona)
    img = tex("moon", _moon_tex)
    p = skia.Paint()
    p.setAlphaf(a)
    c.save()
    c.translate(x - r, y - r)
    c.scale(2 * r / 640, 2 * r / 640)
    c.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    c.restore()
    if color != (255, 255, 255):
        c.drawCircle(x, y, r, paint(color, 0.35 * a))
    if eye > 0:
        c.save()
        c.clipPath(K.circle(x, y, r * 0.995), doAntiAlias=True)
        px, py = x + pupil[0] * r * 0.25, y + pupil[1] * r * 0.25
        ir = r * 0.62
        k = K.ease(eye)
        c.drawCircle(px, py, ir, paint(iris_col, 0.55 * a * k, blur=r * 0.05))
        rng = K.rng_at(4, 4)
        for i in range(90):                                    # the fibres of an iris
            ang = i / 90 * 6.283 + rng.uniform(-0.03, 0.03) + T * 0.02
            r0, r1 = ir * 0.35, ir * rng.uniform(0.8, 1.0)
            c.drawLine(px + math.cos(ang) * r0, py + math.sin(ang) * r0, px + math.cos(ang) * r1, py + math.sin(ang) * r1,
                       paint(mix(iris_col, BLACK, rng.uniform(0.2, 0.6)), 0.5 * a * k, stroke=rng.uniform(2, 5) * r / 300))
        c.drawCircle(px, py, ir, paint(mix(iris_col, BLACK, 0.7), 0.7 * a * k, stroke=r * 0.03))
        c.drawCircle(px, py, ir * 0.33 * (0.7 + 0.3 * k), paint((4, 2, 6), a * k))
        c.drawCircle(px - ir * 0.15, py - ir * 0.18, ir * 0.07, G.glow_paint(WHITE, 0.8 * a * k))
        c.restore()


# ------------------------------------------------------------------ the forest

def _pine_path(h, w, seed):
    """A ragged conifer silhouette, base at (0, 0), top at (0, -h): tiers of drooping, needled branches, each ending
    in a few uneven tips, a bare trunk at the foot, a crooked leader at the top."""
    rng = K.rng_at(seed, 41)
    tiers = int(9 + h / 70)
    side = {1: [], -1: []}
    for sd in (1, -1):
        for i in range(tiers):
            u = i / tiers
            y_in = -h * (0.1 + 0.88 * u)
            half = w / 2 * (1 - u) ** 0.9 * rng.uniform(0.7, 1.2) + 6
            droop = h / tiers * rng.uniform(0.35, 0.9)
            pts = [(sd * half * 0.12, y_in - h / tiers * 0.25)]
            ntip = 2 + int(rng.integers(0, 3))
            for k in range(ntip):
                f = (k + 1) / ntip
                x = sd * half * (0.35 + 0.65 * f) * rng.uniform(0.85, 1.1)
                y = y_in + droop * f ** 1.4 + rng.uniform(-3, 3)
                pts.append((x, y))
                if k < ntip - 1:
                    pts.append((x - sd * half * rng.uniform(0.08, 0.18), y - h / tiers * rng.uniform(0.1, 0.35)))
            pts.append((sd * half * rng.uniform(0.25, 0.4), y_in + droop * 0.7))
            side[sd] += pts
    left = side[-1]
    right = side[1]
    trunk = w * 0.035
    tip = (rng.uniform(-6, 6), -h * 1.03)
    pts = [(-trunk, 0), (-trunk, -h * 0.08)] + left + [tip] + right[::-1] + [(trunk, -h * 0.08), (trunk, 0)]
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    return p


_PINES = {}


def pine(c, x, y, h, w, color, a=1.0, seed=0, sway=0.0):
    key = (int(h), int(w), seed)
    if key not in _PINES:
        _PINES[key] = _pine_path(h, w, seed)
    c.save()
    c.translate(x, y)
    if sway:
        c.skew(sway, 0)
    c.drawPath(_PINES[key], paint(color, a))
    c.restore()


def pine_row(c, T, y, h, color, n=9, a=1.0, seed=0, spread=1.0, x_off=0.0, sway=0.0):
    rng = K.rng_at(seed, 43)
    xs = np.sort(rng.uniform(-120, W + 120, n))
    for i, x in enumerate(xs):
        hh = h * rng.uniform(0.75, 1.25)
        sw = sway * math.sin(T * 0.7 + i) * 0.02
        pine(c, x * spread + x_off, y + rng.uniform(-20, 20), hh, hh * rng.uniform(0.32, 0.45), color, a, seed=seed * 100 + i, sway=sw)
    c.drawRect(skia.Rect.MakeLTRB(-200, y - 5, W + 200, H + 200), paint(color, a))


def fog_band(c, T, y, h, color, a=0.4, seed=0, speed=12.0):
    G.fog(c, T, -200, y - h / 2, W + 200, y + h / 2, color, a=a, n=7, seed=seed, speed=speed, size=1.3)


def forest(c, T, cam_y=0.0, moon_r=330, moon_xy=(640, 520), haze=(120, 90, 200), eye=0.0, pupil=(0, 0), stars=1.0,
           moon_a=1.0, sky_cols=None, seed=0):
    """The whole night: sky, card-hole stars, the moon, five banks of pines going back into fog."""
    c.save()
    c.translate(0, cam_y)
    sky(c, *(sky_cols or ((3, 2, 14), (24, 10, 52), (70, 30, 96))), y0=-600, y1=H)
    if stars > 0:
        card_stars(c, T, 40, -380, W - 40, 900, a=stars, seed=seed)
    moon(c, moon_xy[0], moon_xy[1] - cam_y * 0.6, moon_r, T, a=moon_a, eye=eye, pupil=pupil)
    rows = [(1080, 520, mix(haze, BLACK, 0.55), 0.85), (1180, 640, mix(haze, BLACK, 0.7), 0.95), (1300, 780, mix(haze, BLACK, 0.82), 1.0),
            (1440, 980, mix(haze, BLACK, 0.9), 1.0), (1640, 1240, (4, 3, 6), 1.0)]
    for i, (y, h, col, a) in enumerate(rows):
        pine_row(c, T, y + cam_y * 0.15 * i, h, col, n=9 - i, a=a, seed=seed * 10 + i, sway=1.0)
        fog_band(c, T, y - h * 0.15, 260, haze, a=0.28 - 0.04 * i, seed=seed * 10 + i)
    c.restore()


# ------------------------------------------------------------------ fire

def flame_shape(cx, base, h, w, T, seed):
    """A tongue of flame: a teardrop whose edges flicker with the time."""
    rng = K.rng_at(seed, 47)
    n = 14
    pts = []
    for i in range(n):
        u = i / (n - 1)
        y = base - h * u
        half = w / 2 * math.sin(math.pi * min(1.0, u * 1.1)) ** 0.7 * (1 - u) ** 0.4
        wob = 0.25 * w * math.sin(T * 7 + u * 6 + seed) * u
        pts.append((cx + half + wob + rng.uniform(-3, 3), y))
    for i in range(n - 1, -1, -1):
        u = i / (n - 1)
        y = base - h * u
        half = w / 2 * math.sin(math.pi * min(1.0, u * 1.1)) ** 0.7 * (1 - u) ** 0.4
        wob = 0.25 * w * math.sin(T * 7 + u * 6 + seed) * u
        pts.append((cx - half + wob, y))
    return K.smooth(pts)


def fire(c, x, y, s, T, a=1.0, seed=0, logs=True, glow=1.0):
    """A campfire at (x, y) (its base), scale s: crossed logs, tongues of flame white to red, a pool of light."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if glow > 0:
        fl = G.flicker(T, seed, 0.15)
        G.pool(c, 0, -120, 900 * fl, (255, 100, 30), 0.35 * a * glow)
        G.pool(c, 0, -80, 360 * fl, (255, 150, 70), 0.4 * a * glow)
        G.pool(c, 0, 10, 700, (255, 90, 20), 0.35 * a * glow, squash=0.22)
    if logs:
        for ang, col in ((-14, (40, 24, 16)), (12, (52, 30, 18)), (-3, (34, 20, 14))):
            c.save()
            c.rotate(ang)
            c.drawRoundRect(skia.Rect.MakeLTRB(-190, -24, 190, 24), 22, 22, paint(col, a))
            c.drawRoundRect(skia.Rect.MakeLTRB(-150, -24, 150, -8), 10, 10, G.glow_paint((255, 90, 20), 0.5 * a))
            c.restore()
    rng = K.rng_at(seed, 53)
    for i in range(9):                                         # tongues, red at the back to white in the heart
        u = i / 8
        h = (180 + 220 * (1 - abs(u - 0.5) * 2)) * (0.8 + 0.3 * math.sin(T * 5.3 + i * 1.7))
        w = 110 + 40 * rng.random()
        cx = (u - 0.5) * 230
        col = mix((255, 40, 10), (255, 150, 40), 1 - abs(u - 0.5) * 2)
        c.drawPath(flame_shape(cx, 0, h, w, T, seed + i), G.glow_paint(col, 0.55 * a, blur=6))
    for i in range(5):
        u = i / 4
        h = (120 + 140 * (1 - abs(u - 0.5) * 2)) * (0.85 + 0.25 * math.sin(T * 6.1 + i))
        c.drawPath(flame_shape((u - 0.5) * 130, -6, h, 70, T * 1.2, seed + 20 + i), G.glow_paint((255, 190, 90), 0.5 * a, blur=4))
    c.drawPath(flame_shape(0, -10, 120 + 30 * math.sin(T * 8), 60, T * 1.4, seed + 40), G.glow_paint((255, 236, 190), 0.6 * a, blur=3))
    c.restore()


def embers(c, T, x, y, spread=160, height=1400, n=60, a=1.0, seed=0, size=3.0, to_stars=0.0, wind=40.0):
    """Sparks rising from (x, y), drifting, fading; to_stars (0..1) straightens them into square card-holes."""
    rng = K.rng_at(seed, 59)
    for i in range(n):
        life = rng.uniform(2.5, 5.0)
        ph = rng.uniform(0, life)
        u = ((T + ph) % life) / life
        sx = x + rng.normal(0, spread * 0.35)
        yy = y - height * u ** 0.85
        xx = sx + wind * u * 2 * math.sin(T * 0.8 + i) + spread * 0.6 * u * rng.uniform(-1, 1)
        fade = (1 - u) ** 1.2 * min(1.0, u * 12)
        col = mix((255, 220, 140), (255, 70, 20), u)
        r = size * rng.uniform(0.6, 1.4) * (1 - 0.5 * u)
        if to_stars > 0 and u > 0.4:
            k = to_stars * ramp_(u, 0.4, 0.9)
            c.drawRoundRect(skia.Rect.MakeXYWH(xx - r, yy - r * (1 + 1.2 * k), 2 * r, 2 * r * (1 + 1.2 * k)), 1, 1,
                            G.glow_paint(mix(col, (240, 236, 255), k), a * fade))
        else:
            c.drawCircle(xx, yy, r, G.glow_paint(col, a * fade))


def ramp_(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def smoke(c, T, x, y, w=300, h=1200, color=(120, 100, 140), a=0.3, seed=0, n=10):
    """Smoke rising: soft blobs drifting up, widening and fading."""
    rng = K.rng_at(seed, 61)
    for i in range(n):
        life = rng.uniform(4, 7)
        u = ((T + rng.uniform(0, life)) % life) / life
        xx = x + rng.normal(0, w * 0.2) + w * 0.6 * u * math.sin(T * 0.3 + i)
        yy = y - h * u
        r = w * (0.25 + 0.8 * u)
        c.drawCircle(xx, yy, r, G.glow_paint(color, a * math.sin(math.pi * u) * 0.6, blend=skia.BlendMode.kScreen, blur=r * 0.5))


def page(c, x, y, w, h, ang, T, burn=0.0, a=1.0, lines=10, seed=0, color=(196, 184, 160), title=None, tag="deco",
         title_size=None, text_col=(40, 30, 30)):
    """A record: a sheet of paper with typed lines; burn (0..1) chars it from one corner, glowing at the edge."""
    rng = K.rng_at(seed, 67)
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    rect = skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2)
    edge = None
    if burn > 0:
        # the unburnt part: the page minus a ragged circle growing from the lower-right corner
        R = burn * (w + h) * 0.9
        pts = []
        for i in range(40):
            t = i / 39 * math.pi * 0.5 + math.pi
            rr = R * (1 + 0.12 * math.sin(i * 1.7 + seed) + 0.08 * math.sin(i * 4.1))
            pts.append((w / 2 + math.cos(t) * rr, h / 2 + math.sin(t) * rr))
        hole = skia.Path()
        hole.moveTo(w / 2 + 10, h / 2 + 10)
        for q in pts:
            hole.lineTo(*q)
        hole.close()
        edge = hole
        c.clipPath(hole, skia.ClipOp.kDifference, True)
    c.drawRect(rect, paint(color, a))
    c.drawRect(rect, paint(shader=K.lin((-w / 2, -h / 2), (w / 2, h / 2), [(255, 255, 255, 0.0), (90, 60, 30, 0.35)]), a=a))
    y0 = -h / 2 + h * 0.12
    if title:
        f = K.font("special-elite-400", title_size or w * 0.09)
        c.drawString(title, -w / 2 + w * 0.08, y0, f, paint(text_col, a))
        y0 += h * 0.08
    for i in range(lines):
        yy = y0 + i * (h * 0.8 / max(1, lines))
        if yy > h / 2 - h * 0.06:
            break
        L = w * rng.uniform(0.45, 0.82)
        c.drawRect(skia.Rect.MakeXYWH(-w / 2 + w * 0.08, yy, L, max(2, h * 0.012)), paint(text_col, 0.55 * a))
    c.restore()
    if edge is not None:
        c.save()
        c.translate(x, y)
        c.rotate(ang)
        c.clipRect(rect)
        c.drawPath(edge, G.glow_paint((255, 120, 30), 0.9 * a, blur=2))
        c.drawPath(edge, _stroke(G.glow_paint((255, 200, 90), a), 6))
        c.restore()


def _stroke(p, w):
    p.setStyle(skia.Paint.kStroke_Style)
    p.setStrokeWidth(w)
    return p


# ------------------------------------------------------------------ stone

def _stone_tex():
    rng = np.random.default_rng(21)
    S = 512
    n = np.zeros((S, S), np.float32)
    for sc, amp in ((64, 1.0), (16, 0.6), (4, 0.3), (2, 0.2)):
        g = rng.normal(0, 1, (S // sc + 2, S // sc + 2)).astype(np.float32)
        n += amp * cv2.resize(g, (S, S), interpolation=cv2.INTER_CUBIC)
    n = (n - n.min()) / (n.max() - n.min())
    v = (0.55 + 0.45 * n) * 255
    return K.image(np.dstack([v, v, v, np.full_like(v, 255)]).astype(np.uint8))


def stone_fill(c, p, base=(120, 112, 118), a=1.0, light=(255, 140, 60), light_from=(0.0, 1.0), k=0.9):
    """Fill a path with rough stone, lit from one side (light_from: direction in the shape's box, 0..1)."""
    b = p.computeTightBounds()
    c.save()
    c.clipPath(p, doAntiAlias=True)
    c.drawPath(p, paint(base, a))
    img = tex("stone", _stone_tex)
    sp = skia.Paint()
    sp.setAlphaf(a)
    sp.setBlendMode(skia.BlendMode.kMultiply)
    c.save()
    c.translate(b.left(), b.top())
    c.scale(b.width() / 512, b.height() / 512)
    c.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), sp)
    c.restore()
    lx, ly = b.left() + b.width() * light_from[0], b.top() + b.height() * light_from[1]
    G.pool(c, lx, ly, max(b.width(), b.height()) * 1.1, light, 0.6 * a * k)
    c.drawPath(p, paint(shader=K.rad((lx, ly), max(b.width(), b.height()) * 1.3, [(0, 0, 0, 0.0), (0, 0, 0, 0.75)]), a=a))
    c.restore()


def engraved(c, s, x, y, size, fname="cinzel-800", color=(255, 210, 160), a=1.0, glow=0.0, tag="plaque", align="center"):
    """Lettering cut into stone: a dark groove, a lit lower edge, optional fire-glow in the cut."""
    f = K.font(fname, size)
    w = f.measureText(s)
    x0 = x - w / 2 if align == "center" else x
    c.drawString(s, x0 + size * 0.03, y + size * 0.04, f, paint((255, 220, 190), 0.35 * a))
    c.drawString(s, x0, y, f, paint((8, 4, 6), 0.95 * a))
    if glow > 0:
        c.drawString(s, x0, y, f, G.glow_paint(color, glow * a, blur=size * 0.12))
        c.drawString(s, x0, y, f, paint(color, glow * a * 0.9))
    K.reg_local(c, x0, y - size * 0.78, x0 + w, y + size * 0.22, tag)
    return w
