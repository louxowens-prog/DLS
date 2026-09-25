"""2D compositing for the 2001-style short: starfields, sun glare, display graphics warped into
the 3D screens (stand-in for the film's rear-projected 16mm displays), a true slit-scan
Star Gate, and the vertical frame with a 2.20:1 picture band, Jost titles and captions."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", ".models", "fonts")
W, H = 1080, 1920
BW, BH = 1080, 490
BAND_Y = 715                      # top of the picture band (centred in the vertical frame)
_fc = {}


def jost(weight, size):
    key = (weight, int(size))
    if key not in _fc:
        _fc[key] = ImageFont.truetype(os.path.join(FONTS, f"Jost_{weight}.ttf"), int(size))
    return _fc[key]


def spaced(draw, xy, text, size, fill, track=0.42, weight="300Light", anchor="mm"):
    """Futura-style caps with wide tracking, as on the film's titles."""
    f = jost(weight, size)
    widths = [f.getlength(c) for c in text]
    total = sum(widths) + size * track * (len(text) - 1)
    x = xy[0] - total / 2 if anchor == "mm" else xy[0]
    for c, w in zip(text, widths):
        draw.text((x, xy[1]), c, font=f, fill=fill, anchor="lm")
        x += w + size * track


# ---------------------------------------------------------------- space

_rng = np.random.default_rng(1968)
_stars = np.zeros((BH, BW, 3), np.uint8)
for _ in range(260):                      # 2001's skies are sparse, not glittering
    y, x = _rng.integers(0, BH), _rng.integers(0, BW)
    b = int(_rng.uniform(60, 230))
    _stars[y, x] = b
STARS = Image.fromarray(_stars)


def over_stars(rgba):
    base = STARS.copy()
    base.paste(rgba, (0, 0), rgba)
    return base


def glare(img, xy, strength=1.0):
    """Soft lens bloom plus a faint horizontal streak around a bright source."""
    a = np.asarray(img).astype(np.float32)
    yy, xx = np.mgrid[0:BH, 0:BW]
    d2 = ((xx - xy[0]) ** 2 + (yy - xy[1]) ** 2).astype(np.float32)
    bloom = 255 * strength * (np.exp(-d2 / (2 * 22 ** 2)) + 0.35 * np.exp(-d2 / (2 * 90 ** 2)))
    streak = 255 * 0.25 * strength * np.exp(-((yy - xy[1]) ** 2) / (2 * 2.5 ** 2)) * np.exp(-np.abs(xx - xy[0]) / 260)
    add = (bloom + streak)[..., None] * np.array([1.0, 0.97, 0.9])
    return Image.fromarray(np.clip(a + add, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- display graphics

def _coeffs(src, dst):
    """Perspective transform coefficients mapping dst quad -> src quad (PIL convention)."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def warp_into(band, panel, quad):
    """Composite a flat display graphic into a screen quad (tl, tr, br, bl) of the band."""
    w, h = panel.size
    c = _coeffs([(0, 0), (w, 0), (w, h), (0, h)], quad)
    warped = panel.convert("RGBA").transform(band.size, Image.PERSPECTIVE, c, Image.BICUBIC)
    band.paste(warped, (0, 0), warped)


def display(lines, w=640, h=420, bg=(4, 10, 24), fg=(120, 200, 255), accent=(255, 140, 40), title=None, fs=40):
    """A 1968 flight-deck readout: flat panels, bold sans, block graphics."""
    img = Image.new("RGBA", (w, h), bg + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=fg, width=4)
    y = 30
    if title:
        th = int(fs * 1.6)
        d.rectangle([0, 0, w, th], fill=accent)
        d.text((24, th / 2), title, font=jost("600SemiBold", int(fs * 0.9)), fill=(10, 10, 16), anchor="lm")
        y = th + fs
    for ln in lines:
        x = 28
        parts = ln.split("->")          # Jost has no arrow glyph: draw arrows as vector strokes
        for i, part in enumerate(parts):
            d.text((x, y), part.strip(), font=jost("500Medium", fs), fill=fg, anchor="lm")
            x += jost("500Medium", fs).getlength(part.strip()) + 20
            if i < len(parts) - 1:
                d.line([(x, y), (x + 60, y)], fill=accent, width=6)
                d.polygon([(x + 72, y), (x + 54, y - 12), (x + 54, y + 12)], fill=accent)
                x += 96
        y += int(fs * 1.45)
    return img


# ---------------------------------------------------------------- slit-scan Star Gate

_tex = None


def _artwork():
    """The backlit artwork that slides past the slit: coloured gel bands and gratings."""
    global _tex
    if _tex is None:
        rng = np.random.default_rng(7)
        Hh, Ww = 512, 2048
        tex = np.zeros((Hh, Ww, 3), np.float32)
        gels = np.array([[1, .2, .5], [.2, .6, 1], [1, .6, .1], [.3, 1, .4], [.7, .3, 1], [1, 1, .6]], np.float32)
        for _ in range(420):
            x0, w = rng.integers(0, Ww), rng.integers(4, 60)
            y0, h = rng.integers(0, Hh), rng.integers(10, 240)
            tex[y0:y0 + h, x0:x0 + w] += gels[rng.integers(0, 6)] * rng.uniform(0.2, 0.9)
        xs = np.arange(Ww)
        tex += (0.25 * (np.sin(xs / 9.0) > 0.6))[None, :, None] * np.array([.4, .8, 1], np.float32)
        _tex = np.clip(tex, 0, 1.4)
    return _tex


def slit_scan(t, hue=0.0):
    """True slit-scan: each wall pixel integrates the artwork along its path during the 'exposure'.

    Two planes recede to a vertical slit at centre (as in Trumbull's rig). A column at horizontal
    distance dx from the slit sees the plane at depth z = K/dx; during one frame's exposure the
    artwork travels past, so each pixel averages several artwork positions -> the streaked light.
    """
    tex = _artwork()
    Th, Tw = tex.shape[:2]
    yy, xx = np.mgrid[0:BH, 0:BW].astype(np.float32)
    dx = np.abs(xx - BW / 2) + 1.0
    z = 900.0 / dx
    v = ((yy - BH / 2) * z * 0.9 + Th / 2 + 40 * math.sin(t * 0.7)).astype(np.int32) % Th
    acc = np.zeros((BH, BW, 3), np.float32)
    n = 8
    for k in range(n):
        u = ((z * 60 + (t * 30 + k * 0.9) * 55) % Tw).astype(np.int32)
        acc += tex[v, u]
    acc /= n
    fade = np.clip(dx / 40, 0, 1)[..., None] * np.clip(1.4 - z / 60, 0, 1)[..., None]
    rot = np.roll(np.eye(3), int(hue) % 3, axis=1)
    img = np.clip(acc @ rot * fade * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(img)


# ---------------------------------------------------------------- the vertical frame

def frame(band, chapter=None, caption=None, title_alpha=1.0, cap_alpha=1.0):
    out = Image.new("RGB", (W, H), (0, 0, 0))
    out.paste(band.convert("RGB"), (0, BAND_Y))
    d = ImageDraw.Draw(out)
    if chapter:
        spaced(d, (W / 2, BAND_Y - 90), chapter, 34, tuple(int(235 * title_alpha) for _ in range(3)))
    if caption:
        import textwrap
        lines = textwrap.wrap(caption, 34)
        f = jost("400Regular", 44)
        y = BAND_Y + BH + 110
        for ln in lines:
            d.text((W / 2, y), ln, font=f, fill=tuple(int(230 * cap_alpha) for _ in range(3)), anchor="mm")
            y += 60
    return out


def intertitle(text, a=1.0):
    band = Image.new("RGB", (BW, BH), (0, 0, 0))
    d = ImageDraw.Draw(band)
    spaced(d, (BW / 2, BH / 2), text, 40, tuple(int(240 * a) for _ in range(3)))
    return band
