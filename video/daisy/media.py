"""The hand-made media, one per chapter: crayon on drawing paper, paper cut-outs on construction paper (stop-motion),
plus shared textures. (Clay is in diy; Flash, MS Paint and PS1 are in media2.)"""
import math

import numpy as np
import skia
from PIL import Image, ImageFilter
from scipy import ndimage

import diy as K
from diy import INK, WHITE, W, H, bez, lin, mix, paint, path, rad, smooth

_TEX = {}


def _noise(h, w, scale, seed):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (max(2, h // scale), max(2, w // scale)))
    return np.asarray(Image.fromarray(((n - n.min()) / (n.max() - n.min() + 1e-9) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC),
                      np.float32) / 255


def tex(name, fn):
    if name not in _TEX:
        _TEX[name] = fn()
    return _TEX[name]


# ------------------------------------------------------------------ time: hand-made things move on 2s, 3s, 4s

def step(T, fps=12):
    return math.floor(T * fps + 1e-6) / fps


def jit(T, amp=1.0, seed=0, fps=12):
    """A per-drawing nudge (x, y, rotation) that changes fps times a second."""
    k = int(math.floor(T * fps + 1e-6))
    r = np.random.default_rng((seed * 7919 + k * 104729) % (2 ** 32))
    return r.uniform(-amp, amp), r.uniform(-amp, amp), r.uniform(-amp, amp) * 0.6


# ------------------------------------------------------------------ crayon

PAPER = (250, 247, 238)
CRAYON = {"red": (230, 40, 40), "blue": (40, 90, 230), "sky": (90, 170, 255), "green": (40, 170, 70), "yellow": (255, 210, 30),
          "orange": (255, 130, 30), "pink": (255, 90, 170), "purple": (140, 60, 200), "brown": (130, 80, 40), "black": (30, 26, 30),
          "grey": (140, 140, 150), "peach": (255, 196, 160), "gold": (240, 180, 30), "acid": (160, 230, 30)}


def drawing_paper(arr, seed=3, tone=PAPER, lines=False):
    """White drawing paper: a fibrous tooth, a soft shadow at the edges, optional notebook lines."""
    def make():
        n = _noise(H, W, 3, seed) * 0.6 + _noise(H, W, 40, seed + 1) * 0.4
        img = np.array(tone, np.float32)[None, None] * (0.94 + 0.08 * n[..., None])
        yy, xx = np.mgrid[0:H, 0:W]
        v = 1 - 0.12 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        img *= v[..., None]
        return np.clip(img, 0, 255).astype(np.uint8)
    arr[..., :3] = tex(("paper", seed, tone), make)
    if lines:
        c = skia.Surface(arr).getCanvas()
        for y in range(260, H, 64):
            c.drawLine(0, y, W, y, paint((140, 180, 230), 0.55, stroke=2.5))
        c.drawLine(140, 0, 140, H, paint((230, 110, 120), 0.6, stroke=3))


def _grain():
    """The paper's tooth that a wax crayon skips over: a streaky alpha mask (cached, full frame)."""
    def make():
        rng = np.random.default_rng(11)
        a = rng.random((H, W)).astype(np.float32)
        a = ndimage.uniform_filter(a, size=(1, 5))                   # streaks along the stroke direction (roughly)
        a = 0.55 * a + 0.45 * _noise(H, W, 2, 12)
        m = np.clip((a - 0.3) * 2.6, 0, 1)
        out = np.zeros((H, W, 4), np.uint8)
        out[..., 3] = (m * 255).astype(np.uint8)
        return K.image(out)
    return tex("grain", make)


class crayon_layer:
    """with crayon_layer(c): ... -> everything drawn inside picks up the waxy, skipping texture of crayon on paper."""

    def __init__(self, c, a=1.0):
        self.c, self.a = c, a

    def __enter__(self):
        p = skia.Paint()
        p.setAlphaf(self.a)
        self.c.saveLayer(None, p)
        return self.c

    def __exit__(self, *e):
        p = skia.Paint()
        p.setBlendMode(skia.BlendMode.kDstIn)
        self.c.save()
        self.c.resetMatrix()
        self.c.drawImage(_grain(), 0, 0, skia.SamplingOptions(), p)
        self.c.restore()
        self.c.restore()


def wob(pts, T, seed=0, amp=3.0, fps=8):
    """A child's line never lands in the same place twice: re-jitter every drawing (on 3s)."""
    k = int(math.floor(T * fps + 1e-6))
    r = np.random.default_rng((seed * 131 + k * 977) % (2 ** 32))
    pts = np.asarray(pts, float)
    return pts + r.normal(0, amp, pts.shape)


def crayon_line(c, pts, color, w=10, T=0.0, seed=0, amp=2.5, closed=False, passes=3, prog=1.0):
    """A crayon stroke: a few wobbly passes over the same line, heavier in the middle."""
    pts = np.asarray(pts, float)
    if prog < 1:
        n = max(2, int(len(pts) * prog))
        pts = pts[:n]
    for i in range(passes):
        q = wob(pts, T, seed + i * 17, amp)
        c.drawPath(path(q, closed=closed), paint(color, 0.75 if i else 0.95, stroke=w * (1.0 if i == 0 else 0.6)))


def crayon_fill(c, pts, color, T=0.0, seed=0, spacing=11, angle=30, w=9, a=0.9, amp=2.0):
    """Scribbled-in colour: a zig-zag of crayon inside the outline (overshooting a little, as kids do)."""
    p = smooth(wob(pts, T, seed, amp))
    b = p.computeTightBounds()
    c.save()
    c.clipPath(p, doAntiAlias=True)
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    cx, cy = b.centerX(), b.centerY()
    R = math.hypot(b.width(), b.height()) / 2 + 20
    zz = []
    k = 0
    for d in np.arange(-R, R, spacing):
        e = R if k % 2 == 0 else -R
        zz.append((cx + d * ca - e * sa, cy + d * sa + e * ca))
        k += 1
    zz = wob(zz, T, seed + 5, amp * 1.5)
    c.drawPath(path(zz, closed=False), paint(color, a, stroke=w))
    c.restore()


def kid_text(c, s, x, y, size, color, T=0.0, seed=0, rot=-3, fname="gochi-hand-400", tag="kidtext", k=1.0):
    """A child's crayon lettering: each letter at its own angle and height, re-drawn on 3s."""
    f = K.font(fname, size)
    n = max(0, min(len(s), int(math.ceil(len(s) * k))))
    total = f.measureText(s)
    r = np.random.default_rng(seed)
    kk = int(math.floor(T * 8 + 1e-6))
    rb = np.random.default_rng((seed * 31 + kk * 7) % (2 ** 32))
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    xx = -total / 2
    for i, ch in enumerate(s):
        cw = f.measureText(ch)
        if i < n:
            c.save()
            c.translate(xx + cw / 2, r.uniform(-size * 0.08, size * 0.08) + rb.uniform(-1.5, 1.5))
            c.rotate(r.uniform(-9, 9) + rb.uniform(-1.5, 1.5))
            c.drawString(ch, -cw / 2, 0, f, paint(color, stroke=size * 0.05))
            c.drawString(ch, -cw / 2, 0, f, paint(color))
            c.restore()
        xx += cw * 1.02
    K.reg_local(c, -total / 2, -size * 0.85, total / 2, size * 0.3, tag)
    c.restore()


def tape(c, x, y, w=150, h=46, rot=-30, a=0.75):
    """A strip of yellowed sticky tape."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2 + 6, -h / 4), (w / 2, 0), (w / 2 + 5, h / 4), (w / 2, h / 2), (-w / 2, h / 2),
           (-w / 2 - 5, h / 4), (-w / 2, 0), (-w / 2 - 6, -h / 4)]
    c.drawPath(path(pts), paint((250, 240, 200), a * 0.6))
    c.drawPath(path(pts), paint((200, 190, 150), a * 0.5, stroke=1.5))
    c.restore()


# ------------------------------------------------------------------ paper cut-outs

CONSTRUCTION = {"red": (214, 44, 50), "orange": (240, 120, 36), "yellow": (250, 206, 44), "green": (60, 160, 70),
                "acid": (170, 230, 40), "blue": (40, 96, 200), "sky": (110, 180, 240), "purple": (120, 60, 170),
                "pink": (246, 110, 170), "hot": (240, 40, 140), "black": (34, 30, 36), "white": (246, 244, 236),
                "brown": (140, 90, 50), "grey": (150, 150, 156), "kraft": (196, 156, 106), "cream": (244, 232, 200)}


def _fiber(seed):
    def make():
        n = _noise(H, W, 2, seed) * 0.5 + _noise(H, W, 9, seed + 1) * 0.3 + _noise(H, W, 60, seed + 2) * 0.2
        rng = np.random.default_rng(seed + 3)
        for _ in range(500):                                              # fibres
            x, y = rng.integers(0, W), rng.integers(0, H)
            L = rng.integers(6, 22)
            a = rng.uniform(0, math.pi)
            xs = np.clip((x + np.arange(L) * math.cos(a)).astype(int), 0, W - 1)
            ys = np.clip((y + np.arange(L) * math.sin(a)).astype(int), 0, H - 1)
            n[ys, xs] += rng.choice([-0.25, 0.25])
        return n
    return tex(("fiber", seed), make)


def construction_bg(arr, color, seed=5):
    n = _fiber(seed)
    img = np.array(color, np.float32)[None, None] * (0.9 + 0.16 * n[..., None])
    arr[..., :3] = np.clip(img, 0, 255).astype(np.uint8)


_PTEX = {}


def _paper_shader(seed=0):
    """A soft fibre texture to lay over cut paper (as a multiply)."""
    if seed not in _PTEX:
        n = _noise(512, 512, 2, seed + 40) * 0.6 + _noise(512, 512, 12, seed + 41) * 0.4
        a = np.zeros((512, 512, 4), np.uint8)
        v = (200 + n * 55).astype(np.uint8)
        a[..., 0] = a[..., 1] = a[..., 2] = v
        a[..., 3] = 255
        _PTEX[seed] = K.image(a).makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat)
    return _PTEX[seed]


def scissor(pts, seed=0, amp=1.6, step_px=14.0, closed=True):
    """Scissor-cut outline: resample, then nudge each point (a hand-cut edge, a little straighter in places)."""
    pts = np.asarray(pts, float)
    if closed:
        pts = np.vstack([pts, pts[:1]])
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        L = np.linalg.norm(b - a)
        n = max(1, int(L / step_px))
        for i in range(n):
            out.append(a + (b - a) * i / n)
    out = np.array(out)
    r = np.random.default_rng(seed)
    return out + r.normal(0, amp, out.shape)


def cutout(c, pts, color, seed=0, lift=1.0, T=None, shadow=True, texture=True, edge=True, smooth_=False, a=1.0):
    """A shape cut from construction paper and laid on the board: a soft drop shadow (it lifts off the paper), the
    fibre texture, a slightly darker cut edge."""
    q = scissor(pts, seed)
    p = smooth(q) if smooth_ else path(q)
    if shadow:
        c.save()
        c.translate(5 * lift, 8 * lift)
        c.drawPath(p, paint(INK, 0.32 * a, blur=4 + 4 * lift))
        c.restore()
    c.drawPath(p, paint(color, a))
    if texture:
        tp = skia.Paint(AntiAlias=True)
        tp.setShader(_paper_shader(seed % 3))
        tp.setBlendMode(skia.BlendMode.kMultiply)
        tp.setAlphaf(0.55 * a)
        c.save()
        c.clipPath(p, doAntiAlias=True)
        c.drawPaint(tp)
        c.restore()
    if edge:
        c.drawPath(p, paint(mix(color, INK, 0.3), 0.6 * a, stroke=2.2))
    return p


def cut_circle(c, cx, cy, r, color, seed=0, **kw):
    a = np.linspace(0, 2 * math.pi, max(12, int(r / 5)), endpoint=False)
    return cutout(c, np.stack([cx + r * np.cos(a), cy + r * np.sin(a)], 1), color, seed, smooth_=True, **kw)


def cut_rect(c, x0, y0, x1, y1, color, seed=0, **kw):
    return cutout(c, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color, seed, **kw)


def cut_text(c, s, x, y, size, color, seed=0, fname="londrina-900", T=0.0, tag="cuttext", spacing=1.06, lift=1.0, k=1.0):
    """Letters cut out one by one and glued down a little crooked."""
    f = K.font(fname, size)
    gl = f.textToGlyphs(s)
    ws = f.getWidths(gl)
    total = sum(ws) * spacing
    r = np.random.default_rng(seed)
    xx = x - total / 2
    n = max(0, min(len(gl), int(math.ceil(len(gl) * k))))
    for i, (g, gw) in enumerate(zip(gl, ws)):
        gp = f.getPath(g)
        if gp is not None and not gp.isEmpty() and i < n:
            dx, dy, rr = jit(T, 0.8, seed + i, 12) if T is not None else (0, 0, 0)
            c.save()
            c.translate(xx + gw / 2 + dx, y + r.uniform(-size * 0.05, size * 0.05) + dy)
            c.rotate(r.uniform(-7, 7) + rr)
            c.translate(-gw / 2, 0)
            c.save()
            c.translate(4 * lift, 6 * lift)
            c.drawPath(gp, paint(INK, 0.3, blur=4))
            c.restore()
            c.drawPath(gp, paint(color))
            tp = skia.Paint(AntiAlias=True)
            tp.setShader(_paper_shader(i % 3))
            tp.setBlendMode(skia.BlendMode.kMultiply)
            tp.setAlphaf(0.5)
            c.save()
            c.clipPath(gp, doAntiAlias=True)
            c.drawPaint(tp)
            c.restore()
            c.drawPath(gp, paint(mix(color, INK, 0.35), 0.7, stroke=2))
            c.restore()
        xx += gw * spacing
    K.reg_local(c, x - total / 2, y - size * 0.8, x + total / 2, y + size * 0.25, tag)


def brad(c, x, y, r=9):
    """A brass paper fastener (the joint of a cut-out puppet)."""
    c.drawCircle(x + 1.5, y + 2, r, paint(INK, 0.35, blur=2))
    c.drawCircle(x, y, r, paint(shader=rad((x - r * 0.3, y - r * 0.3), r * 1.2, [(255, 240, 170), (210, 160, 40), (130, 90, 10)])))
