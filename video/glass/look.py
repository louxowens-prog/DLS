"""The 1983 print, drugged: every shot drowned in one saturated colour (blood red, magenta, violet, deep cobalt), heavy
haze glowing wherever there is light, bloom and red halation round every highlight, long anamorphic streaks and
prismatic ghost flares, chromatic fringing on bright edges, faded blacks lifted into purple, coarse 35 mm grain, soft
diffusion, gate weave, light leaks, the odd film burn - and, when the dream turns, the picture itself breathing,
melting and smearing like film left on a projector lamp.

look(arr, T, idx, **params) works in place on an RGBA frame. Flare sources are registered by the shot with flare(),
like lettering with kit.reg(), and drawn here after the bloom."""
import math

import cv2
import numpy as np
import skia

import kit as K
from kit import H, W

cv2.setNumThreads(1)
FLARES = []                        # (x, y, power, tint) registered by the shot this frame
_GRAIN = _VIG = _NOISE = _GRID = None
LUM = np.array([0.299, 0.587, 0.114], np.float32)

# the washes: (shadow, mid, highlight) colours a frame's brightness is mapped through
WASH = {
    "red": ((10, 0, 4), (196, 10, 18), (255, 150, 120)),
    "blood": ((8, 0, 2), (150, 4, 10), (255, 120, 80)),
    "magenta": ((12, 0, 14), (200, 20, 130), (255, 190, 235)),
    "violet": ((8, 2, 22), (110, 30, 200), (230, 200, 255)),
    "cobalt": ((0, 2, 18), (20, 50, 200), (190, 220, 255)),
    "ember": ((10, 2, 0), (210, 70, 10), (255, 220, 160)),
    "green": ((0, 10, 6), (40, 170, 110), (210, 255, 220)),
    "fluoro": ((2, 10, 12), (70, 170, 150), (230, 255, 245)),
    "gold": ((10, 4, 0), (200, 130, 30), (255, 236, 190)),
    "bone": ((6, 4, 10), (150, 130, 140), (250, 240, 236)),
}


def flare(x, y, power=1.0, tint=(255, 220, 200)):
    FLARES.append((float(x), float(y), float(power), tint))


# ------------------------------------------------------------------ cached fields

def _grain_bank():
    global _GRAIN
    if _GRAIN is None:
        rng = np.random.default_rng(1983)
        bank = []
        for i in range(8):
            g = rng.normal(0, 1, (H // 2 + 64, W // 2 + 64, 3)).astype(np.float32)
            g = cv2.GaussianBlur(g, (0, 0), 1.15)                         # coarse clumps, like fast stock pushed
            g = g * 0.6 + g.mean(axis=2, keepdims=True) * 0.4
            g /= g.std()
            bank.append(g.astype(np.float16))
        _GRAIN = bank
    return _GRAIN


def _vignette():
    global _VIG
    if _VIG is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((x - W / 2) / (W * 0.6)) ** 2 + ((y - H / 2) / (H * 0.58)) ** 2)
        _VIG = np.clip(1 - 0.7 * np.clip(d - 0.38, 0, 1) ** 1.5, 0, 1)[..., None].astype(np.float32)
    return _VIG


def _noise_fields():
    """Smooth random fields at quarter resolution - haze banks, melt displacement, burn shapes, light leaks. They are
    built in the frequency domain, so they tile seamlessly: scrolling one round the frame never shows a seam."""
    global _NOISE
    if _NOISE is None:
        rng = np.random.default_rng(83)
        h, w = H // 4, W // 4
        fy = np.fft.fftfreq(h)[:, None]
        fx = np.fft.fftfreq(w)[None, :]
        r = np.sqrt((fy * h / w) ** 2 + fx ** 2)                    # isotropic in pixels
        out = []
        for i in range(10):
            f = np.zeros((h, w), np.float32)
            for scale, amp in ((0.012, 1.0), (0.025, 0.5), (0.05, 0.25), (0.1, 0.12)):
                spec = np.fft.fft2(rng.normal(0, 1, (h, w))) * np.exp(-(r / scale) ** 2)
                g = np.real(np.fft.ifft2(spec)).astype(np.float32)
                f += amp * g / (g.std() + 1e-9)
            f = (f - f.mean()) / (f.std() + 1e-6)
            out.append(f)
        _NOISE = out
    return _NOISE


def _grid():
    global _GRID
    if _GRID is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        _GRID = (x, y)
    return _GRID


def _scroll(f, dx, dy):
    """A field shifted by (dx, dy) quarter-res pixels, wrapping round."""
    return np.roll(np.roll(f, int(dy) % f.shape[0], axis=0), int(dx) % f.shape[1], axis=1)


def weave(T, idx):
    r = np.random.default_rng(idx * 7 + 3)
    return (2.2 * math.sin(T * 1.3) + 1.0 * math.sin(T * 3.7 + 1) + r.normal(0, 0.6),
            1.8 * math.sin(T * 1.1 + 2) + 0.9 * math.sin(T * 4.3) + r.normal(0, 0.6))


def wash_map(lum, wash, pulse=0.0):
    """Brightness mapped through a three-colour gradient: shadow -> mid (at 0.42) -> highlight."""
    lo, mid, hi = (np.array(c, np.float32) / 255 for c in (WASH[wash] if isinstance(wash, str) else wash))
    m = 0.42 + 0.06 * pulse
    a = np.clip(lum * (1 / m), 0, 1)
    b = np.clip((lum - m) * (1 / (1 - m)), 0, 1)
    dm, dh = mid - lo, hi - mid
    return cv2.merge([a * float(dm[c]) + b * float(dh[c]) + float(lo[c]) for c in range(3)])


def mix_wash(w1, w2, k):
    a = WASH[w1] if isinstance(w1, str) else w1
    b = WASH[w2] if isinstance(w2, str) else w2
    return tuple(K.mix(p, q, k) for p, q in zip(a, b))


_M = np.array([[0.299, 0.587, 0.114]], np.float32)


def _lum(x):
    return cv2.transform(x, _M)


_LEAK = None


def _leak_shape():
    global _LEAK
    if _LEAK is None:
        y_, x_ = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
        _LEAK = (np.clip(1 - x_ / (W / 4 * 0.45), 0, 1) ** 2, np.clip((x_ - W / 4 * 0.6) / (W / 4 * 0.4), 0, 1) ** 2)
    return _LEAK


# ------------------------------------------------------------------ the print

def look(arr, T, idx, wash=None, wash_k=0.82, keep=0.0, pulse=0.0, bloom=1.0, haze=0.5, streak=0.6, streak_tint=(120, 150, 255),
         ca=1.0, melt=0.0, breathe=0.0, smear=0.0, burn=0.0, burn_at=(0.85, 0.15), leak=0.3, grain=0.82, sat=1.1,
         lift=(0.055, 0.012, 0.085), crush=1.25, wv=1.0, dust=1.0, flick=1.0, diffusion=1.0, halation=1.0, vig=1.0,
         invert=0.0, expose=1.0, seed=0):
    x = arr[..., :3].astype(np.float32)
    x *= 1 / 255.0
    nf = _noise_fields()
    # --- the picture melting and breathing (before the optics, so the glow melts with it)
    if melt > 0.01 or breathe > 0.01:
        X, Y = _grid()
        k = T * 0.35
        i0 = int(k) % len(nf)
        fr = k - int(k)
        fa = nf[i0] * (1 - fr) + nf[(i0 + 1) % len(nf)] * fr
        fb = nf[(i0 + 5) % len(nf)] * (1 - fr) + nf[(i0 + 6) % len(nf)] * fr
        q = np.arange(W // 4, dtype=np.float32)[None, :]
        drip = melt * 14 * (1 + np.sin(q * (4 / 90.0) + T * 1.7)) * (np.arange(H // 4, dtype=np.float32)[:, None] / (H / 4))
        dx = fa * (26 * melt)
        dy = fb * (34 * melt) + drip
        if breathe > 0:
            # always a zoom in (never out), so the edge of the frame is never pulled into view
            s_ = -breathe * (0.014 * (1 + math.sin(T * 2 * math.pi / 3.2)) + 0.004 * (1 + math.sin(T * 5.1)))
            yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
            dx = dx + (xx * 4 - W / 2) * s_
            dy = dy + (yy * 4 - H / 2) * s_
        dx = cv2.resize(dx.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
        dy = cv2.resize(dy.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
        x = cv2.remap(x, X + dx, Y + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if smear > 0.01:                                                                 # paint running down the frame
        run = np.roll(cv2.blur(x, (3, 90)), 40, axis=0)
        x = np.maximum(x, cv2.addWeighted(x, 1 - smear, run, smear, 0))
    # --- the wash: one colour for the whole scene
    if wash is not None and wash_k > 0:
        g = wash_map(_lum(x), wash, pulse * math.sin(T * 2 * math.pi / 1.7))
        if keep > 0:
            # strongly coloured light (fire, a neon sign) keeps some of its own colour inside the wash
            mx = cv2.max(cv2.max(x[..., 0], x[..., 1]), x[..., 2])
            mn = cv2.min(cv2.min(x[..., 0], x[..., 1]), x[..., 2])
            k = wash_k * (1 - keep * np.clip((mx - mn) / (mx + 0.05), 0, 1))
            x = x + (g - x) * k[..., None]
        else:
            x = cv2.addWeighted(x, 1 - wash_k, g, wash_k, 0)
    # --- optics: diffusion, haze, bloom, halation, anamorphic streaks (all worked out at quarter size)
    small = cv2.resize(x, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    lum_s = _lum(small)
    add = np.zeros_like(small)
    if diffusion > 0:
        add += (cv2.GaussianBlur(small, (0, 0), 1.8) - small) * 0.18 * diffusion
    hi = np.clip((lum_s - 0.5) / 0.5, 0, 1)[..., None] ** 1.5
    tiny = None
    if bloom > 0 or haze > 0:
        sh = small * hi
        tiny = cv2.resize(sh, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
    if bloom > 0:
        add += cv2.GaussianBlur(sh, (0, 0), 8) * 0.38 * bloom
        add += _up4(cv2.GaussianBlur(tiny, (0, 0), 15)) * 0.34 * bloom
    if halation > 0:
        add += cv2.GaussianBlur(small * hi ** 2, (0, 0), 4) * np.array([0.5, 0.1, 0.04], np.float32) * halation
    if haze > 0:
        # light scattered through smoke: a wide glow of everything bright, shaped by drifting banks of haze
        glow = _up4(cv2.GaussianBlur(cv2.resize(small, (W // 8, H // 8), interpolation=cv2.INTER_AREA), (0, 0), 11))
        f1 = _scroll(nf[2], T * 3.0 + seed * 40, T * -1.2)
        f2 = _scroll(nf[7], T * -2.1, T * 0.8 + seed * 25)
        # banks of smoke with clear air between them, so the haze reads as smoke drifting through the light
        bank = np.clip(0.45 + 0.6 * f1 + 0.35 * f2, 0, 1.6)[..., None]
        add += glow * bank * 0.6 * haze + glow.mean(axis=(0, 1)) * bank * 0.07 * haze
    if streak > 0:
        # anamorphic streaks from small hot points (a broad bright area makes a glow, not a line): the highlight
        # minus its local average, smeared sideways, short and bright plus long and faint
        hs = np.clip((lum_s - 0.7) / 0.3, 0, 1) ** 2
        pts = np.clip(hs - cv2.blur(hs, (41, 41)) * 0.85, 0, 1)
        st = cv2.blur(cv2.blur(pts, (41, 1)), (41, 1)) * 1.6 + cv2.blur(cv2.blur(cv2.blur(pts, (151, 1)), (151, 1)), (151, 1)) * 0.9
        add += st[..., None] * (np.array(streak_tint, np.float32) * (1.8 * streak / 255))
    x += cv2.resize(add, (W, H), interpolation=cv2.INTER_LINEAR)
    # --- prismatic ghosts: flare sources registered by the shot
    if FLARES:
        x += _flares()
    # --- chromatic fringing on the edges of the frame and on bright edges
    if ca > 0:
        for ch, s_ in ((0, 1 + 0.0042 * ca), (2, 1 - 0.0042 * ca)):
            M = np.float32([[s_, 0, (1 - s_) * W / 2], [0, s_, (1 - s_) * H / 2]])
            x[..., ch] = cv2.warpAffine(np.ascontiguousarray(x[..., ch]), M, (W, H), borderMode=cv2.BORDER_REFLECT)
    # --- tone: saturation, a shoulder on the highlights, shadows crushed then lifted into faded purple
    if expose != 1.0:
        x *= expose
    if sat != 1.0:
        l3 = cv2.merge([_lum(x)] * 3)
        x = cv2.addWeighted(x, sat, l3, 1 - sat, 0)
    np.maximum(x, 0, out=x)
    x = x / (x * 0.28 + 1.0)
    x *= 1.26
    np.minimum(x, 1.4, out=x)
    if crush != 1.0:
        x = cv2.pow(x, crush)
    lift_ = np.array(lift, np.float32)
    x *= (1 - lift_)
    x += lift_
    if invert > 0:
        x = cv2.addWeighted(x, 1 - invert, 1 - np.clip(x, 0, 1), invert, 0)
    # --- light leaks: warm light spilling in from the edge of the frame
    if leak > 0:
        f = _scroll(nf[4], T * 9.0, 0)
        L1, L2 = _leak_shape()
        side = L1 * (0.5 + 0.5 * math.sin(T * 0.6 + seed)) + L2 * (0.5 + 0.5 * math.sin(T * 0.43 + 2 + seed))
        m = np.clip(side * (0.6 + 0.4 * f), 0, 1)[..., None]
        tint = np.array([1.0, 0.36, 0.12], np.float32) * (0.75 + 0.25 * math.sin(T * 0.9)) * 0.35 * leak
        lk = cv2.resize((m * tint).astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
        np.clip(x, 0, 1, out=x)
        x += lk * (1 - x)                                                          # screen
    # --- flicker and vignette together
    r = np.random.default_rng(idx * 13 + 5)
    fl = 1 + flick * (0.016 * math.sin(T * 23.0) + r.normal(0, 0.008))
    x *= _vig_k(vig) * fl
    # --- grain, strongest in the mid-tones
    if grain > 0:
        bank = _grain_bank()
        r = np.random.default_rng(idx * 31 + 7)
        g = bank[idx % len(bank)]
        oy, ox = r.integers(0, 64), r.integers(0, 64)
        g = cv2.resize(g[oy:oy + H // 2, ox:ox + W // 2].astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
        l = np.clip(_lum(x), 0, 1)
        amp = (0.018 + 0.144 * l * (1 - l)) * grain
        x += g * amp[..., None]
    # --- a film burn: the frame catching fire on the projector lamp
    if burn > 0.01:
        x = _burn(x, burn, burn_at, seed)
    x *= 255.0
    x = np.clip(x, 0, 255).astype(np.uint8)
    # --- gate weave
    if wv > 0:
        dx, dy = weave(T, idx)
        M = np.float32([[1, 0, dx * wv], [0, 1, dy * wv]])
        x = cv2.warpAffine(x, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    # --- dust, hairs and scratches
    if dust > 0:
        r = np.random.default_rng(idx * 101 + 11)
        if r.random() < 0.45 * dust:
            for _ in range(r.integers(1, 5)):
                cx, cy, rr = int(r.uniform(0, W)), int(r.uniform(0, H)), int(r.uniform(1, 5))
                v = 0 if r.random() < 0.6 else 240
                cv2.circle(x, (cx, cy), rr, (v, v, v), -1, lineType=cv2.LINE_AA)
        if r.random() < 0.08 * dust:
            cx, cy = int(r.uniform(0, W)), int(r.uniform(0, H))
            pts = np.array([[cx + int(24 * math.sin(i * 0.4)), cy + i * 7] for i in range(r.integers(6, 22))], np.int32)
            cv2.polylines(x, [pts], False, (10, 6, 8), 1, lineType=cv2.LINE_AA)
        if r.random() < 0.05 * dust:                                               # a vertical scratch
            sx = int(W * (0.2 + 0.6 * ((idx // 6) * 0.618 % 1)))
            cv2.line(x, (sx, 0), (sx + 3, H), (200, 190, 180), 1, lineType=cv2.LINE_AA)
    arr[..., :3] = x
    FLARES.clear()
    return arr


def _up4(a):
    return cv2.resize(a, (W // 4, H // 4), interpolation=cv2.INTER_LINEAR)


_VK = {}


def _vig_k(v):
    v = round(v, 2)
    if v not in _VK:
        _VK[v] = (1 - (1 - _vignette()) * v).astype(np.float32)
    return _VK[v]


def _flares():
    """Prismatic ghosts strung along the line from each source through the centre of the frame, a starburst at the
    source and a broad rainbow ring - drawn additively into their own layer."""
    st = K.Stage((0, 0, 0))
    c = st.c
    cx, cy = W / 2, H / 2
    for (x, y, pw, tint) in FLARES:
        if pw <= 0.01:
            continue
        pw = min(pw, 2.0)
        add = lambda col, a, blur=0.0: _gp(col, a, blur)
        # starburst
        for k in range(6):
            ang = k * math.pi / 6 + 0.2
            L = 260 * pw
            p = add(tint, 0.35 * pw, 3)
            c.drawLine(x - math.cos(ang) * L, y - math.sin(ang) * L, x + math.cos(ang) * L, y + math.sin(ang) * L,
                       _stroke(p, 3 + 2 * pw))
        c.drawCircle(x, y, 60 * pw, add(tint, 0.55 * pw, 30 * pw))
        # ghosts: little irises of the lens, each a different colour of the spectrum
        for f, r, col, a in ((-0.35, 46, (90, 255, 140), 0.16), (0.3, 30, (255, 120, 60), 0.2), (0.62, 90, (80, 140, 255), 0.11),
                             (-0.8, 140, (255, 60, 180), 0.08), (1.25, 64, (255, 230, 90), 0.12), (-1.3, 30, (120, 255, 255), 0.18)):
            gx, gy = cx + (x - cx) * -f, cy + (y - cy) * -f
            p = skia.Path()
            for k in range(6):
                ang = k * math.pi / 3 + 0.3
                (p.moveTo if k == 0 else p.lineTo)(gx + r * pw * math.cos(ang), gy + r * pw * math.sin(ang))
            p.close()
            c.drawPath(p, add(col, a * pw, 6))
        # a broad faint rainbow ring around the frame's centre, opposite the source
        rx, ry = cx - (x - cx) * 0.5, cy - (y - cy) * 0.5
        for k, col in enumerate(((255, 60, 60), (255, 200, 60), (60, 255, 120), (60, 120, 255))):
            c.drawCircle(rx, ry, (330 + k * 14) * pw, _stroke(add(col, 0.06 * pw, 8), 12))
    return st.arr[..., :3].astype(np.float32) * (1 / 255.0)


def _gp(col, a, blur):
    p = K.paint(col, min(1.0, a), blur=blur)
    p.setBlendMode(skia.BlendMode.kPlus)
    return p


def _stroke(p, w):
    p.setStyle(skia.Paint.kStroke_Style)
    p.setStrokeWidth(w)
    return p


def _burn(x, k, at, seed):
    """A burn spreading from `at` (fractions of the frame): white-hot inside, an orange-brown rim, ragged edges."""
    nf = _noise_fields()
    y_, x_ = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
    d = np.sqrt(((x_ - at[0] * W / 4) / (W / 4)) ** 2 + ((y_ - at[1] * H / 4) / (W / 4)) ** 2)
    f = nf[(seed + 3) % len(nf)] * 0.22
    v = k * 1.6 - d + f                                        # > 0 inside the burn
    up = lambda a: cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    hot = up(np.clip(v / 0.08, 0, 1).astype(np.float32))
    rim = up(np.clip(1 - np.abs(v) / 0.07, 0, 1).astype(np.float32))
    core = np.array([1.0, 0.95, 0.82], np.float32)
    edge = np.array([1.0, 0.45, 0.08], np.float32)
    x = x * (1 - rim * 0.5) + edge * rim * 1.1
    return x * (1 - hot) + core * hot * 1.2
