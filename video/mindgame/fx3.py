"""More of Mind Game's mixed media: painted backgrounds, 'live-action' film footage, and flat-shaded 3D.

- painterly(): an oil-paint backdrop of thousands of brush strokes following a flow field, re-painted on fours
- footage(): a real photograph shown as a strip of film (Ken Burns move, gate weave, grain, dust, flicker)
- Cam / draw_quads(): a tiny perspective renderer; faces are flat-shaded and outlined with boiling ink, the
  way the film drops hand-drawn characters into CG sets
"""
import math
import os

import numpy as np
import skia
from PIL import Image
from scipy import ndimage

import mg
from mg import H, W

_cache = {}


# ------------------------------------------------------------------ painted backdrops

def _field(h, w, seed, scale):
    rng = np.random.default_rng(seed)
    g = rng.random((h // scale + 3, w // scale + 3)).astype(np.float32)
    return ndimage.zoom(g, scale, order=3)[:h, :w]


def painterly(arr, stops, seed=0, T=0.0, n=5200, blob=0.35, jit=14):
    """Fill arr with a painted sky/landscape: vertical colour stops [(y01, rgb), ...] plus soft colour blobs."""
    k = (tuple(map(tuple, (s[1] for s in stops))), tuple(s[0] for s in stops), seed, (mg.step(T) // 2) % 3, n, jit)
    if k not in _cache:
        h, w = H // 2, W // 2
        ys = np.linspace(0, 1, h)
        ts = [s[0] for s in stops]
        base = np.stack([np.interp(ys, ts, [s[1][ch] for s in stops]) for ch in range(3)], -1)[:, None, :].repeat(w, 1)
        f1, f2 = _field(h, w, seed, 90), _field(h, w, seed + 1, 40)
        base = base * (1 - blob * 0.35 + blob * 0.7 * f1[..., None]) + (f2[..., None] - 0.5) * 30
        base = np.clip(base, 0, 255)
        ang = _field(h, w, seed + 2, 120) * math.pi * 2
        canvas = np.zeros((h, w, 4), np.uint8)
        canvas[..., :3] = base.astype(np.uint8)
        canvas[..., 3] = 255
        rng = np.random.default_rng(seed * 7 + k[3])
        sf = skia.Surface(canvas)
        with sf as c:
            for _ in range(n):
                x, y = rng.uniform(0, w), rng.uniform(0, h)
                col = base[int(y), int(x)] + rng.normal(0, jit, 3)
                a = ang[int(y), int(x)] + rng.normal(0, 0.25)
                L = rng.uniform(8, 22)
                p = mg.paint(tuple(int(v) for v in np.clip(col, 0, 255)), 0.8, stroke=rng.uniform(3, 7))
                c.drawLine(x - L * math.cos(a), y - L * math.sin(a), x + L * math.cos(a), y + L * math.sin(a), p)
        img = np.asarray(Image.fromarray(canvas[..., :3]).resize((W, H), Image.BICUBIC))
        _cache[k] = img
        if len(_cache) > 60:
            _cache.pop(next(iter(_cache)))
    arr[..., :3] = _cache[k]


# ------------------------------------------------------------------ film footage

def _photo_arr(name):
    k = ("ph", name)
    if k not in _cache:
        _cache[k] = np.asarray(Image.open(os.path.join(mg.TEX, name)).convert("RGB"))
    return _cache[k]


def film_frame(name, fw, fh, t, z0=1.0, z1=1.15, fx=0.5, fy=0.5, gray=False):
    """The photo cropped to fw x fh with a slow push-in."""
    src = _photo_arr(name)
    sh, sw = src.shape[:2]
    z = z0 + (z1 - z0) * t
    cover = max(fw / sw, fh / sh) * z
    cw, ch = fw / cover, fh / cover
    x0 = (sw - cw) * fx
    y0 = (sh - ch) * fy
    img = Image.fromarray(src).resize((fw, fh), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    a = np.asarray(img).astype(np.float32)
    if gray:
        a = a.mean(-1, keepdims=True).repeat(3, -1)
    return a


def footage(arr, name, T, t01, rect=None, strip=True, z0=1.0, z1=1.18, fx=0.5, fy=0.5, gray=False, tint=None):
    """Draw a photo as a running strip of film: sprocket holes, gate weave, grain, dust, flicker."""
    x, y, fw, fh = rect or (40, 560, W - 80, 700)
    rng = np.random.default_rng(int(T * 24) * 31 + 7)
    wx, wy = rng.normal(0, 2.2), rng.normal(0, 2.2)
    img = film_frame(name, int(fw), int(fh), t01, z0, z1, fx, fy, gray)
    img = img * (1 + rng.normal(0, 0.025))
    g = rng.normal(0, 9, (int(fh) // 2 + 1, int(fw) // 2 + 1)).repeat(2, 0).repeat(2, 1)[:int(fh), :int(fw)]
    img = img + g[..., None]
    yy, xx = np.mgrid[0:int(fh), 0:int(fw)]
    vig = 1 - 0.35 * (((xx - fw / 2) / (fw / 2)) ** 2 + ((yy - fh / 2) / (fh / 2)) ** 2)
    img = img * vig[..., None]
    if tint is not None:
        img = img * 0.7 + np.array(tint, np.float32) * 0.3
    for _ in range(rng.integers(3, 9)):                               # dust
        dx, dy, r = rng.integers(0, int(fw)), rng.integers(0, int(fh)), rng.integers(1, 4)
        img[max(0, dy - r):dy + r, max(0, dx - r):dx + r] *= 0.25
    if rng.random() < 0.35:                                          # a scratch
        sx = rng.integers(0, int(fw))
        img[:, sx:sx + 2] = img[:, sx:sx + 2] * 0.5 + 110
    img = np.clip(img, 0, 255).astype(np.uint8)
    X, Y = int(x + wx), int(y + wy)
    if strip:
        pad = 58
        arr[max(0, Y - pad):min(H, Y + int(fh) + pad), :, :3] = (18, 16, 14)
        sf = mg.surf(arr)
        with sf as c:
            off = (T * 240) % 70
            for row in (Y - pad / 2 - 13, Y + fh + pad / 2 - 13):
                for i in range(-1, 17):
                    c.drawRoundRect(skia.Rect.MakeXYWH(i * 70 - off + 16, row, 36, 26), 6, 6, mg.paint((235, 230, 215)))
    y0, y1 = max(0, Y), min(H, Y + int(fh))
    x0, x1 = max(0, X), min(W, X + int(fw))
    arr[y0:y1, x0:x1, :3] = img[y0 - Y:y1 - Y, x0 - X:x1 - X]


# ------------------------------------------------------------------ flat-shaded 3D

class Cam:
    def __init__(self, eye, target, fov=50.0, cx=mg.CX, cy=880.0):
        self.eye = np.array(eye, np.float64)
        f = np.array(target, np.float64) - self.eye
        f /= np.linalg.norm(f)
        r = np.cross(f, [0, 1, 0])
        r /= np.linalg.norm(r)
        u = np.cross(r, f)
        self.f, self.r, self.u = f, r, u
        self.k = (W / 2) / math.tan(math.radians(fov) / 2)
        self.cx, self.cy = cx, cy

    def project(self, p):
        d = np.asarray(p, np.float64) - self.eye
        z = d @ self.f
        return np.array([self.cx + self.k * (d @ self.r) / z, self.cy - self.k * (d @ self.u) / z]), z


def box(x0, y0, z0, x1, y1, z1):
    """Six faces of an axis-aligned box: (name, [4 corners], outward normal)."""
    P = lambda a, b, c: (a, b, c)
    return [
        ("front", [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)], (0, 0, 1)),
        ("back", [P(x1, y0, z0), P(x0, y0, z0), P(x0, y1, z0), P(x1, y1, z0)], (0, 0, -1)),
        ("top", [P(x0, y1, z1), P(x1, y1, z1), P(x1, y1, z0), P(x0, y1, z0)], (0, 1, 0)),
        ("bottom", [P(x0, y0, z0), P(x1, y0, z0), P(x1, y0, z1), P(x0, y0, z1)], (0, -1, 0)),
        ("left", [P(x0, y0, z0), P(x0, y0, z1), P(x0, y1, z1), P(x0, y1, z0)], (-1, 0, 0)),
        ("right", [P(x1, y0, z1), P(x1, y0, z0), P(x1, y1, z0), P(x1, y1, z1)], (1, 0, 0)),
    ]


def draw_quads(c, cam, quads, T, light=(-0.4, 0.8, 0.5), ink=True, seed=0, lw=6.0):
    """quads: [(corners, normal, rgb, tag)]; back faces culled, painter's order, flat Lambert shading."""
    L = np.array(light, np.float64)
    L /= np.linalg.norm(L)
    items = []
    for i, (pts, n, col, tag) in enumerate(quads):
        ctr = np.mean(np.asarray(pts, np.float64), 0)
        if np.dot(np.asarray(n, np.float64), cam.eye - ctr) <= 0:
            continue
        proj = [cam.project(p) for p in pts]
        if min(z for _, z in proj) <= 0.05:
            continue
        depth = np.mean([z for _, z in proj])
        items.append((depth, i, np.array([p for p, _ in proj]), n, col, tag))
    items.sort(key=lambda t: -t[0])
    out = {}
    for depth, i, pp, n, col, tag in items:
        shade = 0.45 + 0.55 * max(0.0, float(np.dot(np.asarray(n, np.float64), L)))
        rgb = tuple(int(min(255, v * shade)) for v in col)
        c.drawPath(mg.path_of(pp, True), mg.paint(rgb))
        if ink:
            mg.stroke(c, pp, T, seed + i, width=lw, closed=True, amp=1.4, double=False)
        out[tag] = pp
    return out
