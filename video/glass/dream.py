"""The dream's landscapes: a hard blue sky over endless golden dunes, white salt flats cracked into tiles, doorways and
staircases standing alone in the sand, a house made of glass, wind lifting sand off the crests, silk veils, flying
glass, and the sandstorm that tears it all down.

Everything is painted with clean gradients and hard edges (the polish of a late-1990s music video), and built to be
seen at two scales: vast and empty, with a tiny figure in it, or close and monumental."""
import math

import numpy as np
import skia

import gel as G
import kit as K
import pers as Pr
from kit import H, W, BLACK, WHITE, mix, paint

SKY_DAY = ((6, 26, 116), (24, 84, 200), (156, 200, 238))       # top, middle, horizon: the hard blue sky
SKY_DAWN = ((4, 8, 40), (50, 54, 132), (255, 174, 106))
SKY_DUSK = ((10, 4, 30), (96, 28, 90), (255, 120, 70))
SAND = dict(lit=(250, 204, 118), mid=(214, 146, 60), shade=(120, 52, 20), deep=(60, 22, 8), rim=(255, 236, 178))
SAND_DAWN = dict(lit=(255, 184, 120), mid=(196, 110, 70), shade=(80, 34, 50), deep=(36, 12, 30), rim=(255, 220, 170))


def sky(c, cols, y0=0, y1=1000, mid_at=0.55, x0=0, x1=W):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(shader=K.lin((0, y0), (0, y1), list(cols), [0.0, mid_at, 1.0])))


def sun(c, x, y, r, color=(255, 246, 220), a=1.0, glow=1.0):
    G.pool(c, x, y, r * 9 * glow, mix(color, (255, 160, 80), 0.4), 0.35 * a)
    G.pool(c, x, y, r * 3.2 * glow, color, 0.6 * a)
    c.drawCircle(x, y, r, paint(color, a))
    c.drawCircle(x, y, r * 0.7, paint(WHITE, a))


# ------------------------------------------------------------------ dunes

def _ridge(xs, crests):
    """Height (px) of a dune ridge: each crest a long convex windward slope on the left, a sharp edge and a short straight
    slip face on the right; where dunes overlap the higher one wins."""
    y = np.zeros_like(xs, dtype=np.float64)
    for xc, w, h in crests:
        u = xs - xc
        left = np.clip(1 + u / (w * 1.8), 0, 1)
        right = np.clip(1 - u / (w * 0.6), 0, 1)
        prof = np.where(u < 0, 1 - (1 - left) ** 2.6, right ** 1.3)
        y = np.maximum(y, h * prof)
    return y


def dune_field(seed, n_layers=6, horizon=900, bottom=H, spread=1.0, tall=1.0):
    """A fixed arrangement of dune layers (back to front): [(base_y, crests, haze)]; crests in a 3-screen-wide strip."""
    rng = K.rng_at(seed, 7)
    layers = []
    for i in range(n_layers):
        k = i / max(1, n_layers - 1)
        base = horizon + (bottom - horizon) * (k ** 1.5) * 0.92 + 18
        n = int(3 + 6 * (1 - k) * spread)
        span = 3 * W
        crests = []
        for j in range(n):
            xc = -W + span * (j + rng.uniform(0.15, 0.85)) / n
            w = (90 + 360 * k) * rng.uniform(0.7, 1.4) * (1.6 - 0.6 * spread)
            h = (20 + 250 * k ** 1.3) * rng.uniform(0.6, 1.3) * tall
            crests.append((xc, w, h))
        layers.append((base, crests, 1 - k))
    return layers


def dunes(c, T, field, pal=SAND, haze_col=(236, 206, 170), haze=0.75, pan=0.0, light=1.0, ripples=True, sx=1.0,
          stream=0.0, wind=1.0, seed=0, layers=None):
    """Paint a dune field. pan shifts it sideways (px); light=1 sun from the left (slip faces in shadow on the right),
    -1 from the right. stream > 0 lifts sand off the nearest crests in the wind."""
    xs = np.linspace(-60, W + 60, 220)
    for li, (base, crests, far) in enumerate(field):
        if layers is not None and li not in layers:
            continue
        cr = [((xc - pan * (1.0 - 0.75 * far)) * sx + W / 2 * (1 - sx), w * sx, h) for xc, w, h in crests]
        if light < 0:
            cr = [(W - xc, w, h) for xc, w, h in cr]
        ys = base - _ridge(xs if light > 0 else W - xs, cr)
        hz = haze * far ** 1.2
        lit, mid_, shade, deep = (mix(pal[k], haze_col, hz) for k in ("lit", "mid", "shade", "deep"))
        top = float(ys.min())
        body = K.path([(xs[0], H + 10)] + list(zip(xs, ys)) + [(xs[-1], H + 10)])
        c.drawPath(body, paint(shader=K.lin((0, top), (0, base + 80 + 260 * (1 - far)), [lit, mid_, mix(mid_, deep, 0.5)], [0.0, 0.55, 1.0])))
        # slip faces in shadow: from each crest the steep lee face, bounded by the silhouette on one side and by the
        # sinuous knife-edge of the crest sweeping down towards the viewer on the other
        for xc, w, h in cr:
            if h < 6:
                continue
            xcs = xc if light > 0 else W - xc
            sgn = 1 if light > 0 else -1
            toe = xcs + sgn * w * 0.55
            crest_y = float(np.interp(xcs, xs, ys))
            if abs(crest_y - (base - h)) > 4:                        # hidden behind a higher neighbour
                continue
            seg = np.linspace(xcs, toe, 14)
            ridge_y = np.interp(seg, xs, ys)
            foot = base + h * 0.7
            wig = 0.08 * math.sin(xcs * 0.013 + li)
            edge = [(xcs - sgn * w * (0.42 * u ** 1.15 + wig * math.sin(u * math.pi)), crest_y + (foot - crest_y) * u) for u in np.linspace(0, 1, 10)]
            pts = list(zip(seg, ridge_y)) + [(toe + sgn * w * 0.5, foot)] + edge[::-1]
            p = K.smooth(pts, closed=True)
            c.drawPath(p, paint(shader=K.lin((xcs, crest_y), (xcs, foot), [mix(shade, deep, 0.5) + (0.95,), shade + (0.9,), mix(shade, mid_, 0.6) + (0.0,)], [0.0, 0.55, 1.0])))
            # the bright knife-edge where light meets shadow
            c.drawPath(K.smooth(edge, closed=False), paint(mix(pal["rim"], haze_col, hz), 0.55, stroke=1.2 + 2.2 * (1 - far)))
            c.drawPath(K.smooth(edge, closed=False), paint(mix(pal["rim"], haze_col, hz), 0.18, stroke=8 * (1 - far) + 2, blur=4))
        if ripples and far < 0.7:
            # wind ripples: fine lines following the slope, dark under bright
            rng = K.rng_at(seed + li, 13)
            for r in range(int(10 + 26 * (1 - far))):
                x0 = rng.uniform(-40, W + 40)
                L = rng.uniform(80, 260) * (1.4 - far)
                yb = float(np.interp(x0, xs, ys)) + rng.uniform(14, 40 + 300 * (1 - far))
                if yb > H:
                    continue
                q = K.bez_path([(x0, yb), (x0 + L / 2, yb - rng.uniform(4, 14)), (x0 + L, yb + rng.uniform(-6, 6))])
                c.drawPath(q, paint(mix(shade, mid_, 0.5), 0.22 * (1 - far), stroke=2.2 * (1.3 - far)))
                c.save()
                c.translate(0, -2.5)
                c.drawPath(q, paint(mix(lit, WHITE, 0.3), 0.18 * (1 - far), stroke=1.4))
                c.restore()
        if stream > 0 and far < 0.5:
            for ci, (xc, w, h) in enumerate(cr):
                xcs = xc if light > 0 else W - xc
                cy = float(np.interp(xcs, xs, ys))
                if -40 < xcs < W + 40 and abs(cy - (base - h)) < 4:
                    sand_stream(c, T, xcs, cy, (1 - far) * stream, wind=wind * (1 if light > 0 else -1), col=mix(pal["lit"], WHITE, 0.25),
                                seed=seed * 31 + li * 7 + ci)


def sand_stream(c, T, x, y, k=1.0, wind=1.0, col=(255, 226, 170), seed=0, n=36):
    """Sand lifting off a crest in the wind: a soft plume and streaks of grains racing away to the side."""
    rng = K.rng_at(seed, 19)
    for j in range(3):
        L = 180 + 140 * j
        G.fog(c, T, x - 40, y - 60 - j * 20, x + wind * L, y + 10, col, a=0.07 * k, n=2, seed=seed + j, speed=60 * wind, size=0.5)
    for i in range(int(n * k)):
        ph = rng.uniform(0, 1)
        life = rng.uniform(0.8, 1.6)
        u = ((T / life) + ph) % 1.0
        dx = wind * (20 + 420 * u ** 1.3) * rng.uniform(0.6, 1.2)
        dy = -18 * math.sin(u * math.pi) * rng.uniform(0.5, 2.0) + 30 * u ** 2
        px, py = x + dx + rng.uniform(-20, 20), y + dy
        a = k * (1 - u) * 0.8
        c.drawLine(px, py, px - wind * (10 + 26 * u), py + 2, paint(col, a, stroke=rng.uniform(1.0, 2.4)))


def figure_far(c, x, y, s, col=(255, 252, 246), veil=True, T=0.0, a=1.0, shadow=(0.0, 0.0, 0.0), sh_len=1.0, sh_dir=1.0):
    """A tiny robed figure far away on the sand (feet at x, y; about 100 px tall at s = 1), a veil streaming in the
    wind, a long shadow across the dune."""
    if sh_len > 0:
        c.drawPath(K.path([(x - 6 * s, y), (x + 6 * s, y), (x + sh_dir * 160 * s * sh_len, y + 10 * s), (x + sh_dir * 150 * s * sh_len, y + 18 * s)]),
                   paint(shadow, 0.35 * a, blur=2 * s))
    body = K.smooth([(x, y - 100 * s), (x + 8 * s, y - 90 * s), (x + 10 * s, y - 70 * s), (x + 22 * s, y), (x - 22 * s, y), (x - 10 * s, y - 70 * s),
                     (x - 8 * s, y - 90 * s)])
    c.drawPath(body, paint(col, a))
    c.drawCircle(x, y - 102 * s, 9 * s, paint(col, a))
    if veil:
        wv = math.sin(T * 2.2)
        p = K.smooth([(x, y - 108 * s), (x + 40 * s, y - 104 * s + 8 * wv * s), (x + 90 * s, y - 92 * s + 14 * wv * s), (x + 120 * s, y - 70 * s + 10 * wv * s),
                      (x + 70 * s, y - 76 * s), (x + 16 * s, y - 84 * s)])
        c.drawPath(p, paint(col, 0.55 * a))


# ------------------------------------------------------------------ salt flat

def salt_cam(height=1.6, pitch=-8.0, f=900.0, x=0.0, z=0.0, yaw=0.0, cy=960.0):
    return Pr.Cam((x, height, z), yaw=yaw, pitch=pitch, f=f, cy=cy)


_HEX = {}


def _hex_path(size, R, seed):
    key = (size, R, seed)
    if key not in _HEX:
        rng = K.rng_at(seed, 3)
        p = skia.Path()
        dx, dy = size * 1.5, size * math.sqrt(3)
        n = int(R / size) + 2
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                cx, cy = i * dx, j * dy + (dy / 2 if i % 2 else 0)
                if cx * cx + cy * cy > R * R:
                    continue
                pts = []
                for k in range(6):
                    ang = math.pi / 3 * k
                    jx, jy = rng.normal(0, size * 0.08, 2)
                    pts.append(((cx + size * math.cos(ang) + jx) * Pr.U, (cy + size * math.sin(ang) + jy) * Pr.U))
                p.moveTo(*pts[0])
                for q in pts[1:]:
                    p.lineTo(*q)
                p.close()
        _HEX[key] = p
    return _HEX[key]


def salt_flat(c, cam, T, base=(192, 196, 204), crack=(110, 122, 148), sky_cols=((30, 64, 150), (100, 140, 206), (196, 208, 224)),
              horizon_glow=(214, 218, 224), size=1.6, R=90.0, seed=0, crack_a=0.8):
    """A white salt plain to the horizon, cracked into a honeycomb of plates (in true perspective), a mirage shimmer on
    the horizon. Returns the horizon's screen y."""
    hy = cam.proj((cam.pos[0], 0.0, cam.pos[2] + 4000.0))
    hy = hy[1] if hy else 900
    sky(c, sky_cols, 0, hy + 2)
    c.drawRect(skia.Rect.MakeLTRB(0, hy, W, H), paint(shader=K.lin((0, hy), (0, H), [mix(base, horizon_glow, 0.6), base, mix(base, (200, 206, 216), 0.25)], [0, 0.3, 1.0])))
    pl = Pr.Plane((cam.pos[0] - R, 0.0, cam.pos[2] - 2), (1, 0, 0), (0, 0, 1), (0, 0, 2 * R, 2 * R))
    with pl.draw(c, cam) as pc:
        if pc is not None:
            pc.save()
            pc.translate(R * Pr.U, (R - 2) * Pr.U * 0 + 2 * Pr.U)
            p = _hex_path(size, R, seed)
            pc.drawPath(p, paint(crack, crack_a * 0.6, stroke=7.0))
            pc.save()
            pc.translate(0, -5)
            pc.drawPath(p, paint(mix(base, WHITE, 0.6), crack_a * 0.5, stroke=3.0))
            pc.restore()
            pc.restore()
    # distance haze and the mirage band at the horizon
    c.drawRect(skia.Rect.MakeLTRB(0, hy - 6, W, hy + 90), paint(shader=K.lin((0, hy - 6), (0, hy + 90), [horizon_glow + (0.0,), horizon_glow + (0.6,), horizon_glow + (0.0,)], [0, 0.35, 1.0])))
    return hy


# ------------------------------------------------------------------ architecture standing in the sand

def doorway(c, x, y, s, open_k=0.0, inside=None, frame=(214, 168, 70), leaf=(26, 20, 22), T=0.0, a=1.0, shadow=0.35, light=1.0,
            glow=(255, 236, 200), glow_k=0.0):
    """A freestanding door frame (x, y = the middle of its threshold; 300 x 600 px at s = 1). open_k swings the leaf;
    inside(c, rect) paints whatever lies beyond it - another place entirely."""
    w, h, t = 300 * s, 600 * s, 34 * s
    x0, x1, y0 = x - w / 2, x + w / 2, y - h
    c.save()
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    if shadow > 0:
        c.drawPath(K.path([(x0 - t, y), (x1 + t, y), (x1 + t + light * 420 * s, y + 70 * s), (x0 - t + light * 420 * s, y + 70 * s)]), paint((40, 14, 6), shadow, blur=6 * s))
    if open_k > 0:
        rect = skia.Rect.MakeLTRB(x0, y0, x1, y)
        c.save()
        c.clipRect(rect, doAntiAlias=True)
        if inside is not None:
            inside(c, rect)
        else:
            c.drawRect(rect, paint(glow))
        c.restore()
        if glow_k > 0:
            G.pool(c, x, y - h / 2, h * 0.9, glow, 0.35 * glow_k * open_k)
            c.drawPath(K.path([(x0, y), (x1, y), (x1 + 160 * s, y + 260 * s), (x0 - 160 * s, y + 260 * s)]), G.glow_paint(glow, 0.25 * glow_k * open_k, blur=20 * s))
    # the leaf: swinging inwards it narrows to a sliver against the left jamb
    lw = w * (1 - open_k) ** 0.8
    if lw > 1:
        lf = K.path([(x0, y0), (x0 + lw, y0 + 20 * s * open_k), (x0 + lw, y - 10 * s * open_k), (x0, y)])
        c.drawPath(lf, paint(shader=K.lin((x0, 0), (x0 + lw, 0), [mix(leaf, WHITE, 0.08), leaf, mix(leaf, BLACK, 0.4)])))
        for py in (0.18, 0.55):                                    # two sunk panels
            c.drawRect(skia.Rect.MakeLTRB(x0 + lw * 0.16, y0 + h * py, x0 + lw * 0.84, y0 + h * (py + 0.3)), paint(mix(leaf, frame, 0.25), 0.6, stroke=3 * s))
        c.drawCircle(x0 + lw * 0.86, y0 + h * 0.52, 7 * s, paint(frame))
    # the frame: jambs, a lintel with a cornice, all gilt
    fr = paint(shader=K.lin((x0 - t, 0), (x1 + t, 0), [mix(frame, WHITE, 0.45), frame, mix(frame, BLACK, 0.35), frame, mix(frame, WHITE, 0.3)]))
    c.drawRect(skia.Rect.MakeLTRB(x0 - t, y0, x0, y), fr)
    c.drawRect(skia.Rect.MakeLTRB(x1, y0, x1 + t, y), fr)
    c.drawRect(skia.Rect.MakeLTRB(x0 - t * 1.6, y0 - t * 1.4, x1 + t * 1.6, y0), fr)
    c.drawRect(skia.Rect.MakeLTRB(x0 - t * 2.0, y0 - t * 2.0, x1 + t * 2.0, y0 - t * 1.4), paint(mix(frame, WHITE, 0.2)))
    c.drawLine(x0 - t * 1.6, y0 - t * 1.4, x1 + t * 1.6, y0 - t * 1.4, paint(mix(frame, BLACK, 0.5), stroke=2 * s))
    c.restore()
    c.restore()


def stairs(c, cam, x, z0, n=14, rise=0.32, run=0.55, width=2.4, col=(222, 216, 206), T=0.0, a=1.0, light=(-0.6, 0.8)):
    """A white marble staircase climbing away from the camera into the sky and stopping in mid-air, nothing under it
    but its own shadow."""
    steps = []
    for i in range(n):
        y0, y1 = i * rise, (i + 1) * rise
        z, zz = z0 + i * run, z0 + (i + 1) * run
        steps.append((y0, y1, z, zz))
    lit, side, dark = mix(col, WHITE, 0.5), mix(col, (150, 140, 150), 0.35), mix(col, (60, 50, 70), 0.6)
    for (y0, y1, z, zz) in reversed(steps):
        P = lambda X, Y, Z: cam.proj((X, Y, Z))
        x0, x1 = x - width / 2, x + width / 2
        q = [P(x0, y1, z), P(x1, y1, z), P(x1, y1, zz), P(x0, y1, zz)]                      # tread
        r = [P(x0, y0, z), P(x1, y0, z), P(x1, y1, z), P(x0, y1, z)]                        # riser
        s_ = [P(x0, y0, z), P(x0, y1, z), P(x0, y1, zz), P(x0, y0, zz)] if light[0] < 0 else None
        if any(v is None for v in q + r):
            continue
        c.drawPath(K.path([v[:2] for v in r]), paint(side, a))
        c.drawPath(K.path([v[:2] for v in q]), paint(lit, a))
        c.drawPath(K.path([v[:2] for v in q]), paint(mix(col, BLACK, 0.2), 0.4 * a, stroke=1.2))
        under = [P(x0, y0, z), P(x1, y0, z), P(x1, y0 - 0.12, zz), P(x0, y0 - 0.12, zz)]
        if all(v is not None for v in under):
            c.drawPath(K.path([v[:2] for v in under]), paint(dark, 0.5 * a))


def glass_house(c, cam, x, z, w=4.0, d=4.0, h=2.6, roof=1.4, T=0.0, a=1.0, warm=(255, 200, 120), edge=(255, 244, 220),
                inside=None, glow=1.0):
    """A house made entirely of glass, lit from inside: every wall transparent, every room on show. inside(c, cam) paints
    its occupant (drawn between the back and front panes)."""
    X0, X1, Z0, Z1 = x - w / 2, x + w / 2, z - d / 2, z + d / 2
    P = lambda X, Y, Z: cam.proj((X, Y, Z))
    V = {}
    for nm, (X, Y, Z) in dict(a=(X0, 0, Z0), b=(X1, 0, Z0), c_=(X1, 0, Z1), d_=(X0, 0, Z1), e=(X0, h, Z0), f=(X1, h, Z0), g=(X1, h, Z1),
                              h_=(X0, h, Z1), r0=(x, h + roof, Z0), r1=(x, h + roof, Z1)).items():
        V[nm] = P(X, Y, Z)
    if any(v is None for v in V.values()):
        return
    pt = lambda k: V[k][:2]
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    # light falling out onto the ground around it
    fx, fy = pt("a")[0] * 0.5 + pt("c_")[0] * 0.5, pt("a")[1] * 0.5 + pt("c_")[1] * 0.5
    G.pool(c, fx, fy, abs(pt("b")[0] - pt("a")[0]) * 1.6, warm, 0.35 * glow, squash=0.35)
    back = [("d_", "c_", "g", "h_"), ("a", "d_", "h_", "e"), ("b", "c_", "g", "f")]
    for f in back:
        c.drawPath(K.path([pt(k) for k in f]), paint(mix(warm, BLACK, 0.55), 0.25))
    c.drawPath(K.path([pt("a"), pt("b"), pt("c_"), pt("d_")]), paint(mix(warm, BLACK, 0.3), 0.55))      # a lit floor
    G.pool(c, fx, fy - 40, abs(pt("b")[0] - pt("a")[0]) * 0.7, warm, 0.5 * glow)
    if inside is not None:
        inside(c, cam)
    front = ("a", "b", "f", "e")
    c.drawPath(K.path([pt(k) for k in front]), paint(shader=K.lin(pt("e"), pt("b"), [(255, 255, 255, 0.18), (255, 255, 255, 0.02), (255, 255, 255, 0.12)])))
    for f in (("e", "f", "r1", "r0"), ("e", "h_", "r1", "r0")):
        pass
    for k0, k1 in (("a", "b"), ("b", "c_"), ("c_", "d_"), ("d_", "a"), ("e", "f"), ("f", "g"), ("g", "h_"), ("h_", "e"), ("a", "e"), ("b", "f"),
                   ("c_", "g"), ("d_", "h_"), ("e", "r0"), ("f", "r0"), ("h_", "r1"), ("g", "r1"), ("r0", "r1")):
        c.drawLine(*pt(k0), *pt(k1), paint(edge, 0.85, stroke=2.2))
        c.drawLine(*pt(k0), *pt(k1), G.glow_paint(edge, 0.25, blur=4))
    c.restore()


def eyes_in_dark(c, T, n=60, y0=0, y1=H, seed=0, col=(255, 210, 120), a=1.0, size=1.0, open_k=1.0):
    """Lenses glinting in the darkness all around: small rings that catch the light and blink."""
    rng = K.rng_at(seed, 29)
    for i in range(n):
        x, y = rng.uniform(20, W - 20), rng.uniform(y0, y1)
        r = rng.uniform(4, 13) * size
        ph = rng.uniform(0, 6.28)
        k = open_k * (0.55 + 0.45 * math.sin(T * rng.uniform(0.5, 1.4) + ph)) * a
        if k <= 0.02:
            continue
        c.drawCircle(x, y, r, paint(col, 0.6 * k, stroke=1.6))
        c.drawCircle(x, y, r * 0.42, paint((10, 6, 4), k))
        c.drawCircle(x - r * 0.25, y - r * 0.25, r * 0.18, G.glow_paint(WHITE, k))
        G.pool(c, x, y, r * 3, col, 0.12 * k)


# ------------------------------------------------------------------ silk, sand and glass in motion

def veil(c, T, x, y, length, width, col=(250, 248, 244), a=0.7, wind=(1.0, 0.25), freq=1.0, seed=0, slow=0.35, flip=1.0):
    """A silk veil streaming from (x, y): waves travel down it in slow motion; thin bright folds run along it."""
    n = 24
    t = T * slow
    wx, wy = wind
    pts_c, half = [], []
    for i in range(n + 1):
        u = i / n
        ang = math.atan2(wy, wx) + 0.35 * math.sin(t * 2.1 * freq - u * 5.0 + seed) * u + 0.15 * math.sin(t * 3.7 - u * 9 + seed * 2) * u
        if i == 0:
            px, py = x, y
        else:
            px, py = pts_c[-1][0] + math.cos(ang) * length / n * flip, pts_c[-1][1] + math.sin(ang) * length / n
        pts_c.append((px, py))
        half.append(width * (0.25 + 0.75 * u ** 0.6) * (1 + 0.25 * math.sin(t * 2.6 - u * 7 + seed)))
    left, right = [], []
    for i, (px, py) in enumerate(pts_c):
        j0, j1 = max(0, i - 1), min(n, i + 1)
        dx, dy = pts_c[j1][0] - pts_c[j0][0], pts_c[j1][1] - pts_c[j0][1]
        L = math.hypot(dx, dy) + 1e-6
        nx, ny = -dy / L, dx / L
        left.append((px + nx * half[i], py + ny * half[i]))
        right.append((px - nx * half[i], py - ny * half[i]))
    p = K.smooth(left + right[::-1], closed=True)
    c.drawPath(p, paint(col, a * 0.75))
    for k, off in enumerate((-0.55, -0.1, 0.35, 0.7)):                       # folds catching the light
        fold = [(pts_c[i][0] + (left[i][0] - pts_c[i][0]) * off, pts_c[i][1] + (left[i][1] - pts_c[i][1]) * off) for i in range(2, n + 1)]
        c.drawPath(K.smooth(fold, closed=False), paint(mix(col, WHITE, 0.6), a * (0.35 if k % 2 else 0.18), stroke=2.0 + k))
        c.drawPath(K.smooth(fold, closed=False), paint(mix(col, BLACK, 0.25), a * 0.12, stroke=5.0, blur=3))
    return pts_c


def sandstorm(arr, T, k=1.0, col=(232, 168, 80), dark=0.35, seed=0, speed=1.0):
    """Blow a sandstorm across a finished frame (in place): banks of dust racing sideways, the light going amber and dim,
    streaks of grains."""
    if k <= 0.01:
        return arr
    import cv2
    import look as LK
    nf = LK._noise_fields()
    f1 = LK._scroll(nf[(seed + 1) % len(nf)], -T * 160 * speed, T * 20)
    f2 = LK._scroll(nf[(seed + 6) % len(nf)], -T * 260 * speed, -T * 12)
    dens = np.clip(0.3 + 0.5 * f1 + 0.3 * f2, 0, 1.4) * k
    dens = cv2.blur(dens.astype(np.float32), (41, 3))                         # smeared along the wind into streaks
    dens = cv2.resize(dens, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    x = arr[..., :3].astype(np.float32)
    x *= (1 - dark * k)
    dust = np.array(col, np.float32)
    x = x * (1 - np.clip(dens * 0.6, 0, 0.8)) + dust * np.clip(dens * 0.6, 0, 0.8)
    arr[..., :3] = np.clip(x, 0, 255).astype(np.uint8)
    st = skia.Surface(arr)
    c = st.getCanvas()
    rng = K.rng_at(seed, 37)
    for i in range(int(420 * k)):
        y = rng.uniform(0, H)
        v = rng.uniform(900, 2400) * speed
        x0 = (rng.uniform(0, W * 1.5) - T * v) % (W * 1.5) - W * 0.25
        L = rng.uniform(30, 140)
        c.drawLine(x0, y, x0 + L, y + L * 0.06, paint(mix(col, WHITE, 0.4), rng.uniform(0.2, 0.6) * k, stroke=rng.uniform(1, 2.5)))
    return arr


def shard(c, x, y, r, ang, T, col=(220, 236, 255), a=1.0, seed=0, tint=None):
    """A flying shard of glass: a sharp polygon, a sheen across it, a hot white edge."""
    rng = K.rng_at(seed, 43)
    n = rng.integers(3, 6)
    pts = []
    for i in range(n):
        th = ang + i * 2 * math.pi / n + rng.uniform(-0.4, 0.4)
        rr = r * rng.uniform(0.45, 1.25)
        pts.append((x + rr * math.cos(th), y + rr * math.sin(th)))
    p = K.path(pts)
    base = tint or col
    c.drawPath(p, paint(shader=K.lin(pts[0], pts[len(pts) // 2], [base + (0.12 * a,), WHITE + (0.55 * a,), base + (0.08 * a,)])))
    c.drawPath(p, paint(WHITE, 0.85 * a, stroke=1.6))
    c.drawPath(p, G.glow_paint(base, 0.35 * a, blur=3))
