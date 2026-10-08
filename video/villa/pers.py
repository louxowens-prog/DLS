"""A small perspective renderer for the alleys, the gallery and the corridors.

The camera looks down +z with y up. Every flat surface is drawn in its own 2-D coordinates (metres x 100) through a
homography, so stone courses, portraits and pools of coloured light lie on the walls in true perspective. Parts of a
surface behind the camera are clipped away first. A dolly moves the camera; a zoom changes the focal length."""
import math

import numpy as np
import skia

import kit as K
from kit import BLACK, mix, paint

U = 100.0                       # local drawing units per metre
NEAR = 0.15


class Cam:
    def __init__(self, pos=(0.0, 1.6, 0.0), yaw=0.0, pitch=0.0, roll=0.0, f=900.0, cx=540.0, cy=960.0):
        self.pos = np.array(pos, float)
        self.f, self.cx, self.cy = f, cx, cy
        cy_, sy_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
        cr, sr = math.cos(math.radians(roll)), math.sin(math.radians(roll))
        Ry = np.array([[cy_, 0, -sy_], [0, 1, 0], [sy_, 0, cy_]])
        Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
        Rz = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]])
        self.R = Rz @ Rx @ Ry                                  # world -> camera

    def cam(self, p):
        return self.R @ (np.asarray(p, float) - self.pos)

    def depth(self, p):
        return float(self.cam(p)[2])

    def proj(self, p):
        q = self.cam(p)
        if q[2] <= NEAR:
            return None
        return (self.cx + self.f * q[0] / q[2], self.cy - self.f * q[1] / q[2], q[2])

    def scale_at(self, p):
        """Screen pixels per metre at a point (for billboards)."""
        z = self.depth(p)
        return self.f / max(NEAR, z)


class Plane:
    """A flat surface: origin, unit axes u and v (3-D). Draw in local coords (x = u metres x U, y = v metres x U,
    y DOWN the plane if v points down) inside `with plane.draw(c, cam) as pc:`. Returns None if nothing is visible."""

    def __init__(self, origin, u, v, extent):
        self.o = np.array(origin, float)
        self.u = np.array(u, float) / np.linalg.norm(u)
        self.v = np.array(v, float) / np.linalg.norm(v)
        self.ext = extent                                          # (u0, v0, u1, v1) metres
        self.n = np.cross(self.u, self.v)

    def world(self, a, b):
        return self.o + self.u * a + self.v * b

    def visible_poly(self, cam):
        """The extent clipped to z > NEAR (in camera space), as local (a, b) metres."""
        u0, v0, u1, v1 = self.ext
        pts = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        z = lambda a, b: cam.cam(self.world(a, b))[2] - NEAR * 1.5
        out = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            za, zb = z(*a), z(*b)
            if za > 0:
                out.append(a)
            if (za > 0) != (zb > 0):
                t = za / (za - zb)
                out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        return out

    def matrix(self, cam, poly):
        """Homography: local units -> screen, from four visible points."""
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        cxm, cym = sum(xs) / len(xs), sum(ys) / len(ys)
        s = max(0.05, min(max(xs) - min(xs), max(ys) - min(ys)) * 0.25)
        loc = [(cxm - s, cym - s), (cxm + s, cym - s), (cxm + s, cym + s), (cxm - s, cym + s)]
        scr = [cam.proj(self.world(a, b)) for a, b in loc]
        if any(q is None for q in scr):
            return None
        m = skia.Matrix()
        ok = m.setPolyToPoly([skia.Point(a * U, b * U) for a, b in loc], [skia.Point(q[0], q[1]) for q in scr])
        return m if ok else None

    def draw(self, c, cam):
        return _PlaneCtx(self, c, cam)


class _PlaneCtx:
    def __init__(self, pl, c, cam):
        self.pl, self.c, self.cam = pl, c, cam
        self.ok = False

    def __enter__(self):
        poly = self.pl.visible_poly(self.cam)
        if len(poly) < 3:
            return None
        m = self.pl.matrix(self.cam, poly)
        if m is None:
            return None
        self.c.save()
        self.c.concat(m)
        self.c.clipPath(K.path([(a * U, b * U) for a, b in poly]), doAntiAlias=True)
        self.ok = True
        return self.c

    def __exit__(self, *a):
        if self.ok:
            self.c.restore()


class Light:
    def __init__(self, pos, color, power=1.0, reach=3.0):
        self.pos, self.color, self.power, self.reach = np.array(pos, float), color, power, reach


def light_plane(pc, pl, lights, albedo=1.0, gain=1.0, spread=1.0):
    """Pools of coloured light on a plane (inside its draw context): each light's foot on the plane, the pool wider
    and dimmer the further the light stands off the surface; a hot, nearly white core near the source, the colour
    saturating outward and falling fast into black."""
    for L in lights:
        d = float(np.dot(L.pos - pl.o, pl.n))
        foot = L.pos - pl.n * d
        a = float(np.dot(foot - pl.o, pl.u))
        b = float(np.dot(foot - pl.o, pl.v))
        dist = abs(d)
        r = (L.reach * spread * (0.45 + 0.7 * dist)) * U
        k = gain * L.power * albedo / (1 + (dist / L.reach) ** 2)
        if k <= 0.004:
            continue
        col = L.color
        hot = mix(col, (255, 255, 255), 0.55)
        passes = int(math.ceil(k))
        for i in range(passes):
            kk = min(1.0, k - i)
            sh = K.rad((a * U, b * U), r, [col + (kk,), col + (kk * 0.6,), col + (kk * 0.2,), col + (0.0,)], [0.0, 0.2, 0.5, 1.0])
            p = paint(col, 1.0, shader=sh)
            p.setBlendMode(skia.BlendMode.kPlus)
            pc.drawCircle(a * U, b * U, r, p)
        rc = r * 0.28
        sh = K.rad((a * U, b * U), rc, [hot + (min(1.0, k * 0.5),), hot + (0.0,)])
        p = paint(hot, 1.0, shader=sh)
        p.setBlendMode(skia.BlendMode.kPlus)
        pc.drawCircle(a * U, b * U, rc, p)


def lit(pc, pl, lights, albedo_fn, amb=(7, 5, 7), gain=1.0, spread=1.0):
    """Light x surface: ambient plus the gel pools, multiplied by the surface's own texture (drawn by albedo_fn in local
    units, in its true colours at full brightness)."""
    pc.saveLayer(None, None)
    pc.drawPaint(paint(amb))
    light_plane(pc, pl, lights, 1.0, gain * 2.6, spread)
    mp = skia.Paint()
    mp.setBlendMode(skia.BlendMode.kMultiply)
    pc.saveLayer(None, mp)
    albedo_fn(pc)
    pc.restore()
    pc.restore()


def depth_fog(pc, pl, cam, color=(0, 0, 0), density=0.12, start=1.0, a=1.0, steps=6):
    """Fade a plane toward `color` with distance (inside its draw context): sampled along the plane's longer axis."""
    u0, v0, u1, v1 = pl.ext
    along_u = abs(u1 - u0) >= abs(v1 - v0)
    pts, cols, pos = [], [], []
    for i in range(steps + 1):
        t = i / steps
        if along_u:
            a_, b_ = u0 + (u1 - u0) * t, (v0 + v1) / 2
        else:
            a_, b_ = (u0 + u1) / 2, v0 + (v1 - v0) * t
        z = max(0.0, cam.depth(pl.world(a_, b_)) - start)
        cols.append(color + (a * (1 - math.exp(-density * z)),))
        pos.append(t)
    if along_u:
        p0, p1 = (u0 * U, 0), (u1 * U, 0)
    else:
        p0, p1 = (0, v0 * U), (0, v1 * U)
    pc.drawPaint(paint(shader=K.lin(p0, p1, cols, pos)))


def fog_at(cam, p, color=(0, 0, 0), density=0.12, start=1.0):
    z = max(0.0, cam.depth(p) - start)
    return 1 - math.exp(-density * z)


# ------------------------------------------------------------------ common planes

def wall_x(x, z0, z1, y0, y1, facing=1):
    """A wall at x, running from z0 to z1, floor y0 to top y1; facing +1 = faces +x (a left wall)."""
    if facing > 0:
        return Plane((x, y1, z0), (0, 0, 1), (0, -1, 0), (0, 0, z1 - z0, y1 - y0))
    return Plane((x, y1, z1), (0, 0, -1), (0, -1, 0), (0, 0, z1 - z0, y1 - y0))


def floor(x0, x1, z0, z1, y=0.0):
    return Plane((x0, y, z1), (1, 0, 0), (0, 0, -1), (0, 0, x1 - x0, z1 - z0))


def ceiling(x0, x1, z0, z1, y):
    return Plane((x0, y, z0), (1, 0, 0), (0, 0, 1), (0, 0, x1 - x0, z1 - z0))


def wall_z(z, x0, x1, y0, y1):
    """A wall facing the camera at depth z."""
    return Plane((x0, y1, z), (1, 0, 0), (0, -1, 0), (0, 0, x1 - x0, y1 - y0))


def stone_blocks(pc, ext, base, course=0.34, block=0.62, seed=0, var=0.22, mortar=0.45):
    """An ashlar wall as albedo: every block its own shade, dark mortar between (local units)."""
    u0, v0, u1, v1 = ext
    rng = K.rng_at(seed, 7)
    pc.drawPaint(paint(mix(BLACK, base, mortar)))
    n = int((v1 - v0) / course) + 1
    for i in range(n):
        y = (v0 + i * course) * U
        x = u0 - (i % 2) * block * 0.5
        while x < u1:
            w = block * rng.uniform(0.75, 1.3)
            sh = 1 - var + rng.uniform(0, 2 * var)
            col = tuple(int(min(255, ch * sh)) for ch in base)
            pc.drawRect(skia.Rect.MakeXYWH(x * U + 2, y + 2, w * U - 4, course * U - 4), paint(col))
            x += w


def stone_courses(pc, ext, color, course=0.34, block=0.62, a=0.5, seed=0, width=2.2):
    """Mortar lines of a stone wall in local units: horizontal courses and staggered joints."""
    u0, v0, u1, v1 = ext
    rng = K.rng_at(seed, 3)
    p = paint(color, a, stroke=width)
    n = int((v1 - v0) / course) + 1
    for i in range(n):
        y = (v0 + i * course) * U
        pc.drawLine(u0 * U, y, u1 * U, y, p)
        off = (i % 2) * block * 0.5 + rng.uniform(-0.08, 0.08)
        x = u0 + off
        while x < u1:
            pc.drawLine(x * U, y, x * U, y + course * U, p)
            x += block * rng.uniform(0.8, 1.25)
