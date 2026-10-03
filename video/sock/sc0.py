"""Cold open: Dot to a phone camera in front of an un-keyed green screen (clamps, wrinkles, a light stand), a freeze
frame with scribbled labels, then the key switches on for the title."""
import math

import numpy as np
import skia

import common as C
import diy as K
import dot as D
import tv
from diy import GOLD, HOT, INK, PURPLE, WHITE, W, H, lin, mix, paint, path, rad, ramp
from common import E, S, Wx


def green_screen(c, T, wide=False, seed=2):
    """A green cloth pinned up in a basement: wrinkles and creases, A-clamps, a light stand, wood panelling at the edge."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint((120, 84, 52)))
    for k in range(9):                                                    # wood panelling behind
        x = k * 130
        c.drawRect(skia.Rect.MakeXYWH(x, 0, 126, H), paint(mix((150, 104, 62), (110, 74, 44), (k % 3) / 3)))
        c.drawLine(x + 127, 0, x + 127, H, paint((70, 44, 26), stroke=5))
    x0, x1 = (40, 1040) if not wide else (110, 980)
    cloth = path([(x0, 60), (x1, 40), (x1 + 20, H), (x0 - 20, H)])
    c.drawPath(cloth, paint(C.K.SCREEN if hasattr(C.K, "SCREEN") else (30, 200, 70)))
    c.save()
    c.clipPath(cloth, doAntiAlias=True)
    rng = np.random.default_rng(seed)
    for i in range(14):                                                   # soft folds hanging from the clamps
        fx = x0 + (x1 - x0) * rng.uniform(0, 1)
        c.drawLine(fx, 40, fx + rng.uniform(-160, 160), H, paint((10, 120, 40), 0.35, stroke=rng.uniform(20, 60), blur=22))
        c.drawLine(fx + 30, 40, fx + 30 + rng.uniform(-160, 160), H, paint((120, 255, 150), 0.18, stroke=rng.uniform(10, 30), blur=16))
    for i in range(5):                                                    # creases from being folded in a box
        y = rng.uniform(300, 1700)
        c.drawLine(x0, y, x1, y + rng.uniform(-40, 40), paint((10, 110, 40), 0.4, stroke=4, blur=2))
        c.drawLine(x0, y + 5, x1, y + 5 + rng.uniform(-40, 40), paint((140, 255, 170), 0.25, stroke=3, blur=2))
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=rad((W * 0.45, H * 0.35), 1300, [(255, 255, 230, 0.18), (0, 0, 0, 0.0), (0, 0, 0, 0.35)],
                                                         [0, 0.5, 1])))
    c.restore()
    for cx in (x0 + 30, x1 - 30):                                         # A-clamps
        c.save()
        c.translate(cx, 60)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-26, -40, 52, 120), 10, 10), paint((30, 30, 34)))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-18, 60, 36, 50), 8, 8), paint((230, 80, 40)))
        c.drawCircle(0, 0, 8, paint((160, 160, 170)))
        c.restore()
    # a light stand at the right edge, a softbox glow
    sx = W - 40 if not wide else W - 70
    c.drawLine(sx, 200, sx - 30, H, paint((24, 24, 28), stroke=16))
    c.drawRect(skia.Rect.MakeXYWH(sx - 140, 120, 240, 170), paint((240, 240, 230)))
    c.drawRect(skia.Rect.MakeXYWH(sx - 140, 120, 240, 170), paint((24, 24, 28), stroke=12))
    c.drawCircle(sx - 20, 200, 300, paint((255, 250, 220), 0.12, blur=80))
    if wide:                                                              # gaffer tape X on the floor, a tripod leg
        c.drawLine(380, 1780, 520, 1700, paint((240, 200, 40), stroke=22))
        c.drawLine(380, 1700, 520, 1780, paint((240, 200, 40), stroke=22))


def s_phone(T, idx):
    """'Part of every AI you talk to is you.' Selfie, on the phone, raw green screen behind."""
    st = K.Stage()
    c = st.c
    green_screen(c, T)
    pose_t = T - S("o1")
    mood = "deadpan" if T < Wx("o1", "you", 1) else "proud"
    C.live_dot(c, T, idx, 560, 2700, 1.5, pose="sock_up", mood=mood, look=(0.0, 0.05), seed=1,
               sock_open=0.25 + 0.25 * math.sin(T * 9) if Wx("o1", "every") < T < Wx("o1", "talk") else 0.0,
               sock_look=(0.9, 0.2), tilt=2 * math.sin(T * 1.7))
    tv.phone_ui(c, T, 0.0)
    arr = st.arr
    dx, dy, rot = tv.shake(T, 9, 1, 0.8)
    z = 1.0 + 0.16 * K.ease(ramp(T, Wx("o1", "you", 1), Wx("o1", "you", 1) + 0.12))
    return tv.apply_cam(arr, dx, dy, rot, z, cx=560, cy=640)


FREEZE = None


def s_freeze1(T, idx):
    """'I learned that the embarrassing way.' A wider shot; a freeze frame with scribbled labels."""
    global FREEZE
    t_fz = Wx("o2", "embarrassing") + 0.25
    Tf = min(T, t_fz)
    st = K.Stage()
    c = st.c
    green_screen(c, Tf, wide=True)
    C.live_dot(c, Tf, int(Tf * 24), 540, 2280, 1.12, pose="sock_chest", mood="side" if Tf > S("o2") + 0.3 else "deadpan",
               look=(0.6, 0.1), seed=1, sock_look=(-0.6, -0.4), sock_face=1)
    arr = st.arr
    if T >= t_fz:
        tv.freeze_tint(arr, 1.0)
        c = skia.Surface(arr).getCanvas()
        k1, k2 = ramp(T, t_fz + 0.05, t_fz + 0.45), ramp(T, t_fz + 0.35, t_fz + 0.75)
        if T < t_fz + 0.08:
            c.drawRect(skia.Rect.MakeWH(W, H), paint(WHITE, 0.7))
        tv.scribble_arrow(c, 760, 330, 610, 500, WHITE, k=k1, seed=3)
        tv.scrawl(c, "ME. DOT. 41.", 770, 300, 70, (255, 240, 120), rot=-5, k=k1)
        tv.scribble_arrow(c, 250, 1150, 250, 1000, WHITE, k=k2, seed=5, bend=-0.2)
        tv.scrawl(c, "DOC. (A SOCK)", 330, 1240, 70, (140, 255, 200), rot=4, k=k2)
    else:
        dx, dy, rot = tv.shake(T, 6, 2, 0.5)
        arr = tv.apply_cam(arr, dx, dy, rot, 1.02)
    return arr


def s_title(T, idx):
    """The key switches on: a hot-pink sunburst, spinning stars, WordArt, Dot and Doc waving."""
    t0 = C.E("o2") + 0.1
    st = K.Stage()
    c = st.c
    K.starburst(c, 540, 860, T, colors=((150, 30, 200), (255, 50, 160)), n=16, spin=0.5)
    rng = np.random.default_rng(4)
    for i in range(70):                                                     # glitter
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        tw = (math.sin(T * 9 + i) + 1) / 2
        c.drawCircle(x, y, 2 + 3 * tw, paint((255, 240, 160), 0.4 + 0.6 * tw))
    for i, (x, y, r) in enumerate(((150, 1150, 70), (930, 1020, 90), (880, 1500, 60), (200, 1600, 80))):
        K.cg_star(c, x, y, r, T, seed=i, color=GOLD if i % 2 else (255, 120, 200))
    C.live_dot(c, T, idx, 540, 2430, 1.02, pose="wave", mood="grin", look=(0, 0), seed=1, who_talks=None,
               sock_open=0.5 + 0.5 * math.sin(T * 14), sock_look=(0.3, -0.2), halo=12)
    k = K.pop(T, t0, 0.35, 0.35)
    c.save()
    c.translate(540, 470)
    c.scale(k, k)
    tv.wordart(c, "THE HAND", 0, 0, 170, T, depth=26)
    tv.wordart(c, "IN THE SOCK", 0, 165, 150, T + 0.4, warp="arch", amp=0.1, depth=24,
               fill=[(255, 252, 210), (255, 206, 50), (230, 110, 0)], ext=(180, 40, 120))
    c.restore()
    K.flare(c, 820, 360, T, 0.9 * ramp(T, t0 + 0.2, t0 + 0.5))
    return st.arr
