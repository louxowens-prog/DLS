"""Race environments: the candy stadium, the rainbow road (side-on and in 3D perspective), and a 3D circuit."""
import math

import numpy as np
import skia

import sr
from sr import CANDY, CX, H, INK, W, WHITE, paint, path

_cache = {}


class Cam:
    def __init__(self, eye, target, fov=50.0, cx=CX, cy=880.0, roll=0.0):
        self.eye = np.array(eye, np.float64)
        f = np.array(target, np.float64) - self.eye
        f /= np.linalg.norm(f)
        r = np.cross(f, [0, 1, 0])
        r /= np.linalg.norm(r)
        u = np.cross(r, f)
        if roll:
            cr, sn = math.cos(roll), math.sin(roll)
            r, u = r * cr + u * sn, -r * sn + u * cr
        self.f, self.r, self.u = f, r, u
        self.k = (W / 2) / math.tan(math.radians(fov) / 2)
        self.cx, self.cy = cx, cy

    def project(self, p):
        d = np.asarray(p, np.float64) - self.eye
        z = d @ self.f
        return np.array([self.cx + self.k * (d @ self.r) / max(z, 1e-3), self.cy - self.k * (d @ self.u) / max(z, 1e-3)]), z


# ------------------------------------------------------------------ the stadium strip (rendered once, scrolled)

def _stadium_strip(pal=0):
    key = ("stadium", pal)
    if key in _cache:
        return _cache[key]
    SW, SH = W * 3, 700
    a = np.zeros((SH, SW, 4), np.uint8)
    rng = np.random.default_rng(7 + pal)
    sf = skia.Surface(a)
    with sf as c:
        # neon towers and loops far back
        for i in range(26):
            x = rng.uniform(0, SW)
            w, h = rng.uniform(60, 140), rng.uniform(250, 560)
            cc = CANDY[i % len(CANDY)]
            p = path([(x, SH - 260), (x + w, SH - 260), (x + w * 0.8, SH - 260 - h), (x + w * 0.2, SH - 260 - h)])
            sr.glossy(c, p, sr.lighter(cc, 0.15), rim=WHITE, spec=0.6, lw=4)
            for k in range(int(h / 60)):
                c.drawRect(skia.Rect.MakeXYWH(x + w * 0.3, SH - 300 - k * 60, w * 0.4, 18), paint(WHITE, 0.8))
        for k in range(4):                                         # rainbow loop ribbons
            cx0, r = rng.uniform(300, SW - 300), rng.uniform(150, 230)
            for j, cc in enumerate(CANDY):
                c.drawCircle(cx0, SH - 330 - r * 0.2, r - j * 9, paint(cc, stroke=10))
        # grandstand with a confetti crowd
        c.drawRect(skia.Rect.MakeXYWH(0, SH - 270, SW, 270), paint(shader=sr.lin((0, SH - 270), (0, SH), [(80, 40, 160), (40, 20, 90)])))
        for i in range(2600):
            x, y = rng.uniform(0, SW), rng.uniform(SH - 255, SH - 20)
            c.drawCircle(x, y, rng.uniform(4, 8), paint(CANDY[rng.integers(len(CANDY))]))
        for i in range(0, SW, 160):
            c.drawRect(skia.Rect.MakeXYWH(i, SH - 280, 80, 14), paint(sr.LEMON))
    _cache[key] = a
    return a


def stadium(arr, T, speed=1.0, y_base=1180, pal=0, blur=True):
    """Candy sky, scrolling stadium behind; everything behind the track is streak-blurred at speed."""
    sr.sky(arr, [(0, (255, 110, 200)), (0.35, (255, 170, 150)), (0.62, (255, 225, 140)), (1, (130, 225, 255))])
    strip = _stadium_strip(pal)
    SH, SW = strip.shape[:2]
    off = int(T * speed * 1400) % (SW - W)
    y0 = y_base - SH
    crop = strip[:, off:off + W]
    al = crop[..., 3:4].astype(np.float32) / 255
    ys, ye = max(0, y0), min(H, y0 + SH)
    arr[ys:ye, :, :3] = (arr[ys:ye, :, :3] * (1 - al[ys - y0:ye - y0]) + crop[ys - y0:ye - y0, :, :3] * al[ys - y0:ye - y0]).astype(np.uint8)
    if blur and speed > 0.05:
        sr.streak(arr, 20 + 140 * min(1.5, speed), 0, y_base + 10)


def road_side(c, T, y0=1180, y1=1330, speed=1.0):
    """The rainbow track seen side-on: candy bands, a checkered kerb, dashes flying by."""
    n = len(CANDY)
    for i, cc in enumerate(CANDY):
        c.drawRect(skia.Rect.MakeXYWH(0, y0 + (y1 - y0) * i / n, W, (y1 - y0) / n + 1), paint(cc))
    off = (T * speed * 1800) % 120
    for x in np.arange(-120, W + 120, 120):
        c.drawRect(skia.Rect.MakeXYWH(x - off, y0 - 22, 60, 22), paint(WHITE))
        c.drawRect(skia.Rect.MakeXYWH(x - off + 60, y0 - 22, 60, 22), paint(sr.RED))
    c.drawRect(skia.Rect.MakeXYWH(0, y1, W, 30), paint(INK))
    c.drawRect(skia.Rect.MakeXYWH(0, y0 + 2, W, 10), paint(WHITE, 0.55, blur=4))
    c.drawRect(skia.Rect.MakeXYWH(0, y0 + (y1 - y0) * 0.18, W, (y1 - y0) * 0.16), paint(WHITE, 0.18, blur=6))


def road_front(c, T, speed=1.0, horizon=760, curve=0.0, width=2.6, y_bottom=H):
    """The rainbow road running away into the distance (perspective strips), neon poles whipping past."""
    rows = []
    for k in range(60):
        z = 1 + k * 1.2
        y = horizon + (y_bottom - horizon) * (1 / z) ** 0.9
        x_c = CX + curve * 900 * (1 - 1 / z) ** 2
        half = W * width / 2 / z
        rows.append((z, y, x_c, half))
    rows = rows[::-1]
    for (z0, y0, xc0, h0), (z1, y1, xc1, h1) in zip(rows[:-1], rows[1:]):
        L = [(xc0 - h0, y0), (xc1 - h1, y1)]
        R = [(xc0 + h0, y0), (xc1 + h1, y1)]
        sr.rainbow_bands(c, L, R)
        phase = int((z1 - T * speed * 14) // 1.5) % 2
        if phase:
            c.drawPath(path([(xc0 - h0 * 0.04, y0), (xc0 + h0 * 0.04, y0), (xc1 + h1 * 0.04, y1), (xc1 - h1 * 0.04, y1)]), paint(WHITE, 0.95))
        for side in (-1, 1):
            kc = WHITE if int((z1 - T * speed * 14) // 1.2) % 2 else sr.RED
            c.drawPath(path([(xc0 + side * h0, y0), (xc0 + side * h0 * 1.08, y0), (xc1 + side * h1 * 1.08, y1), (xc1 + side * h1, y1)]), paint(kc))
    sheen = sr.path([(CX - W * width / 2 * 0.95, y_bottom), (CX - W * width / 2 * 0.35, y_bottom), (CX + 6, horizon + 8), (CX - 6, horizon + 8)])
    c.drawPath(sheen, paint(WHITE, 0.16))
    for k in range(8):                                             # neon poles
        z = 1.2 + ((k * 3.0 - T * speed * 14) % 24)
        y = horizon + (y_bottom - horizon) * (1 / z) ** 0.9
        xc = CX + curve * 900 * (1 - 1 / z) ** 2
        for side in (-1, 1):
            x = xc + side * W * width / 2 / z * 1.25
            hgt = 900 / z
            c.drawRect(skia.Rect.MakeXYWH(x - 10 / z, y - hgt, 20 / z, hgt), paint(CANDY[(k + (side > 0) * 3) % len(CANDY)]))
            c.drawCircle(x, y - hgt, 30 / z, paint(WHITE, 0.9, blur=8 / z))


def circuit_pts(n=240, rx=4.2, rz=2.6):
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return np.stack([rx * np.cos(a), 0.35 * np.sin(2 * a), rz * np.sin(a)], 1)


def draw_circuit(c, cam, T, width=0.7):
    """A closed rainbow circuit in 3D (a flat ribbon with a little banking), back to front."""
    P = circuit_pts()
    n = len(P)
    quads = []
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]
        d = b - a
        nrm = np.cross(d, [0, 1, 0])
        nrm /= np.linalg.norm(nrm) + 1e-9
        for j, cc in enumerate(CANDY):
            u0, u1 = -width / 2 + width * j / len(CANDY), -width / 2 + width * (j + 1) / len(CANDY)
            q = [a + nrm * u0, a + nrm * u1, b + nrm * u1, b + nrm * u0]
            pr = [cam.project(p) for p in q]
            if min(z for _, z in pr) < 0.2:
                continue
            quads.append((np.mean([z for _, z in pr]), [p for p, _ in pr], cc))
    quads.sort(key=lambda q: -q[0])
    for _, pp, cc in quads:
        c.drawPath(path(pp), paint(cc))
    return P


def near_wall(arr, T, y0=1330, speed=1.0):
    """The near side of the track (the camera rides the rail): candy barrier panels with chevrons, streaking past."""
    sf = skia.Surface(arr)
    off = (T * speed * 2200) % 520
    with sf as c:
        c.drawRect(skia.Rect.MakeXYWH(0, y0, W, H - y0), paint(shader=sr.lin((0, y0), (0, H), [(60, 30, 120), (20, 10, 50)])))
        for k in range(-1, 4):
            x = k * 520 - off
            for j, cc in enumerate((sr.PINK, sr.LEMON)):
                px = x + j * 260
                c.drawRect(skia.Rect.MakeXYWH(px, y0 + 40, 250, 260), paint(cc))
                for m in range(3):
                    cx0 = px + 40 + m * 70
                    c.drawPath(path([(cx0, y0 + 80), (cx0 + 40, y0 + 170), (cx0, y0 + 260), (cx0 + 22, y0 + 260), (cx0 + 62, y0 + 170), (cx0 + 22, y0 + 80)]),
                               paint(WHITE, 0.9))
        c.drawRect(skia.Rect.MakeXYWH(0, y0, W, 40), paint(shader=sr.lin((0, y0), (0, y0 + 40), [WHITE, (150, 160, 200), (90, 90, 130)])))
        c.drawRect(skia.Rect.MakeXYWH(0, y0 + 300, W, 30), paint(shader=sr.lin((0, y0 + 300), (0, y0 + 330), [WHITE, (120, 120, 160)])))
    sr.streak(arr, 30 + 150 * min(1.5, speed), y0, H)
