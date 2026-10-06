"""The 1974 print: soft-focus diffusion (highlights bloom into halos), red-orange halation round the brightest edges,
saturated gels in slightly faded, warm colour with deep blacks, fine 35 mm grain, gentle gate weave, a vignette, a
little flicker, and the odd speck of dust. `plain` turns it into the flat, sharp, cold image of the present day."""
import math

import cv2
import numpy as np

import kit as K
from kit import H, W

cv2.setNumThreads(1)
_GRAIN = None
_VIG = None


def _grain_bank():
    global _GRAIN
    if _GRAIN is None:
        rng = np.random.default_rng(1974)
        bank = []
        for i in range(6):
            g = rng.normal(0, 1, (H // 2 + 64, W // 2 + 64, 3)).astype(np.float32)
            g = cv2.GaussianBlur(g, (0, 0), 0.65)
            g = g * 0.65 + g.mean(axis=2, keepdims=True) * 0.35          # grain is mostly in luminance, a little in colour
            g /= g.std()
            bank.append(g.astype(np.float16))
        _GRAIN = bank
    return _GRAIN


def _vignette():
    global _VIG
    if _VIG is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.6)) ** 2)
        _VIG = np.clip(1 - 0.55 * np.clip(d - 0.45, 0, 1) ** 1.6, 0, 1)[..., None].astype(np.float32)
    return _VIG


def weave(T, idx):
    """Gate weave: a slow wander plus a frame-to-frame jitter (pixels)."""
    r = np.random.default_rng(idx * 7 + 3)
    return (0.9 * math.sin(T * 1.3) + 0.5 * math.sin(T * 3.7 + 1) + r.normal(0, 0.35),
            0.7 * math.sin(T * 1.1 + 2) + 0.4 * math.sin(T * 4.3) + r.normal(0, 0.35))


def look(arr, T, idx, diffusion=1.0, halation=1.0, grain=1.0, sat=1.1, fade=1.0, dust=1.0, flick=1.0, plain=0.0,
         lift=(0.03, 0.018, 0.022), wv=1.0):
    x = arr[..., :3].astype(np.float32) / 255.0
    film = 1.0 - plain
    # --- diffusion: a soft halo round every highlight, and a touch of overall softness
    if film > 0:
        small = cv2.resize(x, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        lum_s = small @ np.array([0.299, 0.587, 0.114], np.float32)
        hi = np.clip((lum_s - 0.58) / 0.42, 0, 1)[..., None] ** 1.6
        bloom = cv2.GaussianBlur(small * hi, (0, 0), 9)
        wide = cv2.GaussianBlur(small * hi, (0, 0), 28)
        soft = cv2.GaussianBlur(small, (0, 0), 1.6)
        up = lambda a: cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)
        k = diffusion * film
        x = x * (1 - 0.16 * k) + up(soft) * 0.16 * k
        x = x + up(bloom) * 0.42 * k + up(wide) * 0.26 * k
        # --- halation: red-orange light bleeding back through the film base
        if halation > 0:
            hal = cv2.GaussianBlur(small * hi ** 2, (0, 0), 5)
            x = x + up(hal) * np.array([0.42, 0.11, 0.04], np.float32) * halation * film
    # --- tone: deep blacks, lifted a hair toward a warm print colour; a gentle shoulder on the highlights
    x = np.clip(x, 0, None)
    x = x / (1 + 0.32 * x)                                     # shoulder
    x = x * 1.30
    lum = x @ np.array([0.299, 0.587, 0.114], np.float32)
    s = sat * film + 0.82 * plain
    x = lum[..., None] + (x - lum[..., None]) * s
    if film > 0:
        warm = np.array([1.03, 1.0, 0.93], np.float32)
        x = x * (1 + (warm - 1) * np.clip(lum, 0, 1)[..., None] * fade * film)
        lift_ = np.array(lift, np.float32) * fade * film
        x = lift_ + x * (1 - lift_)
    if plain > 0:                                               # the present: cold fluorescent, flat, a little green
        cool = np.array([0.93, 1.0, 1.04], np.float32)
        x = x * (1 + (cool - 1) * plain)
    # --- flicker
    if flick > 0 and film > 0:
        r = np.random.default_rng(idx * 13 + 5)
        x = x * (1 + flick * film * (0.012 * math.sin(T * 23.0) + r.normal(0, 0.006)))
    # --- vignette
    vig = _vignette()
    x = x * (1 - (1 - vig) * (0.55 + 0.45 * film))
    # --- grain: strongest in the mid-tones
    if grain > 0:
        bank = _grain_bank()
        r = np.random.default_rng(idx * 31 + 7)
        g = bank[idx % len(bank)]
        oy, ox = r.integers(0, 64), r.integers(0, 64)
        g = g[oy:oy + H // 2, ox:ox + W // 2].astype(np.float32)
        g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
        l = np.clip(x @ np.array([0.299, 0.587, 0.114], np.float32), 0, 1)[..., None]
        amp = (0.008 + 0.022 * l * (1 - l) * 4) * grain * (0.35 + 0.65 * film)
        x = x + g * amp
    x = np.clip(x * 255.0, 0, 255).astype(np.uint8)
    # --- gate weave
    if wv > 0 and film > 0:
        dx, dy = weave(T, idx)
        M = np.float32([[1, 0, dx * wv * film], [0, 1, dy * wv * film]])
        x = cv2.warpAffine(x, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    # --- dust and hairs, now and then
    if dust > 0 and film > 0:
        r = np.random.default_rng(idx * 101 + 11)
        if r.random() < 0.35 * dust:
            for _ in range(r.integers(1, 4)):
                cx, cy, rr = int(r.uniform(0, W)), int(r.uniform(0, H)), int(r.uniform(1, 4))
                v = 0 if r.random() < 0.7 else 235
                cv2.circle(x, (cx, cy), rr, (v, v, v), -1, lineType=cv2.LINE_AA)
        if r.random() < 0.06 * dust:
            cx, cy = int(r.uniform(0, W)), int(r.uniform(0, H))
            pts = np.array([[cx + int(20 * math.sin(i * 0.4)), cy + i * 6] for i in range(r.integers(6, 20))], np.int32)
            cv2.polylines(x, [pts], False, (8, 8, 8), 1, lineType=cv2.LINE_AA)
    arr[..., :3] = x
    return arr
