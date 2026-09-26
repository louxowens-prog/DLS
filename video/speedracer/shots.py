"""The edit: shots, Speed Racer transitions (head wipes, iris wipes, split slams), the announcer's TV box,
bloom, and captions."""
import math

import numpy as np
import skia

import cast
import scenes_a as A
import scenes_b as B
import scenes_c as Cc
import sr
from common import talk
from cues import C
from edit import EDIT, WIPE
from timeline import FPS, TL

SHOT = {
    "grid": A.s_grid, "race": A.s_race, "two": A.s_two, "finish": A.s_finish, "chess": A.s_chess, "imagenet": A.s_imagenet,
    "fuzzy": A.s_fuzzy, "dash": A.s_dash, "frameworks": A.s_frameworks, "arc": A.s_arc,
    "engine": B.s_engine, "learner": B.s_learner, "facts": B.s_facts, "dinner": B.s_dinner, "hazards": B.s_hazards,
    "skills": B.s_skills, "expedition": B.s_expedition, "transfer": B.s_transfer, "coffee": B.s_coffee,
    "hood": Cc.s_hood, "loop": Cc.s_loop, "memory": Cc.s_memory, "h2h": Cc.s_h2h, "newtrack": Cc.s_newtrack,
    "chess2": Cc.s_chess2, "laps": Cc.s_laps, "joke": Cc.s_joke, "final": Cc.s_final, "end": Cc.s_end,
}
STARTS = [e[0] for e in EDIT]
NOCAP_KEYS = {"d6", "t2", "u2"}
CAPS = [c for c in TL.captions() if c[3] not in NOCAP_KEYS]
# the announcer's TV box for each of his lines: (x, y, w, h)
PIP = {"a0": (580, 660, 440, 340), "a1": (40, 620, 440, 340), "a2": (40, 470, 440, 340), "a3": (190, 560, 700, 540)}


def shot_frame(i, T):
    t0, name, _ = EDIT[i]
    t1 = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total + 1.0
    arr = sr.new()
    SHOT[name](arr, T - t0, t1 - t0, T)
    return arr


def index_at(T):
    i = 0
    for k, s in enumerate(STARTS):
        if s <= T:
            i = k
    return i


def head_wipe(a, b, k, who, T):
    """A giant face slides right-to-left across the frame; behind it, the next shot."""
    k = min(1.0, max(0.0, k))
    u = k * k * (3 - 2 * k)
    s = 7.5
    x_line = sr.W + 720 - (sr.W + 1440) * u
    out = a.copy()
    xs = int(max(0, min(sr.W, x_line)))
    out[:, xs:] = b[:, xs:]
    sf = sr.surf(out)
    with sf as c:
        sr.speed_lines(c, x_line, 900, T, n=30, color=sr.WHITE, r0=700, a=0.5, seed=77) if 0.1 < k < 0.9 else None
        cast.face(c, who, x_line, 930, s, T, talk=talk(T) if who == "host" else (talk(T, "announcer") if who == "announcer" else 0.3),
                  look=(-1, 0), facing=-1, expr="wow" if who != "memorizer" else "grin")
    return out


def iris(a, b, k, cx=sr.CX, cy=880):
    R0 = 1300
    if k < 0.5:
        src, r = a, R0 * (1 - 2 * k) ** 1.3
    else:
        src, r = b, R0 * (2 * k - 1) ** 1.3
    out = sr.new(sr.INK)
    yy, xx = np.ogrid[:sr.H, :sr.W]
    m = (xx - cx) ** 2 + (yy - cy) ** 2 < r * r
    out[m] = src[m]
    sf = sr.surf(out)
    with sf as c:
        for j, colr in enumerate(sr.CANDY):
            c.drawCircle(cx, cy, r + 8 + j * 10, sr.paint(colr, stroke=10))
    return out


def split_slam(a, b, k):
    """The next shot slams in from the right along a slanted edge with a chrome bar."""
    u = min(1.0, k)
    u = 1 - (1 - u) ** 3
    out = a.copy()
    yy = np.arange(sr.H)[:, None]
    xx = np.arange(sr.W)[None, :]
    edge = sr.W + 300 - (sr.W + 600) * u + (yy - 900) * 0.2
    m = xx >= edge
    out[m] = b[m]
    sf = sr.surf(out)
    with sf as c:
        e0 = sr.W + 300 - (sr.W + 600) * u
        c.drawPath(sr.path([(e0 - 900 * 0.2 - 10, 0), (e0 - 900 * 0.2 + 10, 0), (e0 + (sr.H - 900) * 0.2 + 10, sr.H), (e0 + (sr.H - 900) * 0.2 - 10, sr.H)]),
                   sr.paint(shader=sr.lin((0, 0), (0, sr.H), [sr.WHITE, (160, 170, 200), sr.WHITE])))
    return out


def pip(arr, T):
    for key, (x, y, w, h) in PIP.items():
        t0, t1 = TL.s(key) - 0.3, TL.e(key) + 0.4
        if not (t0 <= T < t1):
            continue
        k = sr.pop(T, t0, 0.25) * (1 - sr.ease(sr.ramp(T, t1 - 0.2, t1)))
        if k <= 0.01:
            continue
        sf = sr.surf(arr)
        with sf as c:
            c.save()
            c.translate(x + w / 2, y + h / 2)
            c.scale(k, k)
            c.translate(-(x + w / 2), -(y + h / 2))
            rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 22, 22)
            c.save()
            c.clipRRect(rr, doAntiAlias=True)
            c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), sr.paint(shader=sr.lin((0, y), (0, y + h), [(255, 90, 170), (90, 40, 200)])))
            rng = np.random.default_rng(3)
            for j in range(90):
                c.drawCircle(x + rng.uniform(0, w), y + h * 0.62 + rng.uniform(0, h * 0.4), rng.uniform(3, 6), sr.paint(sr.CANDY[j % 7], 0.8))
            cast.face(c, "announcer", x + w * 0.45, y + h * 0.5, h / 330, T, talk=talk(T, "announcer"), look=(0.5, 0.1))
            # the ribbon mic
            c.drawRoundRect(skia.Rect.MakeXYWH(x + w * 0.62, y + h * 0.6, h * 0.12, h * 0.24), 12, 12,
                            sr.paint(shader=sr.lin((0, y + h * 0.6), (0, y + h * 0.84), [sr.WHITE, (150, 160, 190)])))
            c.drawRect(skia.Rect.MakeXYWH(x + w * 0.66, y + h * 0.84, h * 0.04, h * 0.2), sr.paint(sr.INK))
            c.restore()
            sr.tv_frame(c, x, y, w, h, T)
            bar = skia.Path()
            bar.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x + 20, y + h - 64, w * 0.62, 48), 10, 10))
            sr.glossy(c, bar, sr.LEMON, lw=3)
            c.drawString("THE ANNOUNCER", x + 34, y + h - 28, sr.font("bungee-400", min(30, h * 0.09)), sr.paint(sr.INK))
            c.restore()


GAP = 1.55


def line_w(ln, f):
    words = ln.split()
    return sum(f.measureText(w) for w in words) + f.measureText(" ") * GAP * (len(words) - 1)


def balanced(s, f, maxw):
    if line_w(s, f) <= maxw:
        return [s]
    words = s.split()
    best, bi = None, 1
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        wa, wb = line_w(a, f), line_w(b, f)
        cost = max(wa, wb) + (400 if max(wa, wb) > maxw else 0)
        if best is None or cost < best:
            best, bi = cost, i
    return [" ".join(words[:bi]), " ".join(words[bi:])]


def draw_caption(arr, T):
    s = next((c[2] for c in CAPS if c[0] <= T < c[1]), None)
    if not s or T >= C["end_card"]:
        return
    f = sr.font("rubik-900", 60)
    sp = f.measureText(" ") * GAP
    lines = balanced(s, f, 840)
    sf = sr.surf(arr)
    with sf as c:
        y = sr.CAP_Y - (len(lines) - 1) * 10
        for ln in lines:
            x = sr.CX - line_w(ln, f) / 2
            for w in ln.split():
                c.drawString(w, x + 3, y + 5, f, sr.paint((0, 0, 0), 0.55, blur=5))
                c.drawString(w, x, y, f, sr.paint((0, 0, 0), 1.0, stroke=8))
                c.drawString(w, x, y, f, sr.paint((255, 255, 255)))
                x += f.measureText(w) + sp
            y += 72


def render_frame(T, idx=None, captions=True):
    i = index_at(T)
    out = None
    for j in (i, i + 1):
        if j <= 0 or j >= len(EDIT):
            continue
        b0, _, tr = EDIT[j]
        if tr.startswith("head") or tr == "iris":
            if b0 - WIPE / 2 <= T < b0 + WIPE / 2:
                a = shot_frame(j - 1, T)
                b = shot_frame(j, T)
                k = (T - (b0 - WIPE / 2)) / WIPE
                out = head_wipe(a, b, k, tr.split(":")[1], T) if tr.startswith("head") else iris(a, b, k)
                break
        elif tr == "split" and b0 <= T < b0 + 0.3:
            out = split_slam(shot_frame(j - 1, T), shot_frame(j, T), (T - b0) / 0.3)
            break
    if out is None:
        out = shot_frame(i, T)
        b0, _, tr = EDIT[i]
        if tr == "cut" and i > 0 and 0 <= T - b0 < 2 / FPS:
            w = 0.55 if T - b0 < 1 / FPS else 0.25
            out[..., :3] = (out[..., :3] * (1 - w) + 255 * w).astype(np.uint8)
    pip(out, T)
    sr.bloom(out, 0.45)
    if captions:
        draw_caption(out, T)
    return out
