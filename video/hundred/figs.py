"""The people, as the lighting finds them: silhouettes with a hard rim of gel colour, and extreme close-ups (an eye,
lips, a hand on a phone, a face in profile) painted in light and deep shadow.

woman(c, x, y, s, pose, rim, side) - Nora, standing: (x, y) between the feet, s = 1 is 1000 px tall.
"""
import math

import numpy as np
import skia

import draw as D
import kit as K
from draw import mix, paint, path

SKIN, SKIN_D = (226, 180, 150), (120, 70, 52)


def _cap(p, x0, y0, x1, y1, w0, w1=None):
    p.addPath(D.capsule(x0, y0, x1, y1, w0, w1))


def _arm(p, sx, sy, a0, l0, bend, l1, w0=46, w1=34):
    """Add a two-segment arm from the shoulder; angles in degrees, 0 = hanging down, + = forward/up towards +x."""
    a0r = math.radians(a0)
    ex, ey = sx + l0 * math.sin(a0r), sy + l0 * math.cos(a0r)
    a1r = a0r + math.radians(bend)
    hx, hy = ex + l1 * math.sin(a1r), ey + l1 * math.cos(a1r)
    _cap(p, sx, sy, ex, ey, w0, w1 + 4)
    _cap(p, ex, ey, hx, hy, w1 + 4, w1)
    p.addPath(D.circle(hx, hy, w1 * 0.75))
    return hx, hy


POSES = {
    # (left arm: angle, bend), (right arm: angle, bend), head tilt, lean
    "stand": ((-6, 4), (6, -4), 0, 0),
    "suitcase": ((-6, 4), (10, -2), 0, 0),
    "chest": ((-8, 4), (10, -150), 6, 3),
    "jaw": ((-8, 4), (14, -170), -10, 0),
    "phone": ((-12, 130), (12, -130), 14, 0),
    "walk": ((-14, 10), (16, -6), 0, 2),
    "lean": ((-40, -30), (10, -150), 12, -8),
    "reach": ((-6, 4), (80, -10), 0, 4),
}


def woman_path(pose="stand", T=0.0, hair="bob", robe=True, stride=0.0):
    la, ra, tilt, lean = POSES[pose]
    p = skia.Path()
    br = 2 * math.sin(T * 1.6)
    # robe / dress to the floor (hem swings with the stride)
    sw = 30 * stride
    body = D.smooth([(-118, -785 + br), (-112, -690), (-82, -560), (-104, -450), (-150 - sw, -150), (-172 - sw, -8),
                     (-60, 4), (60, 4), (172 + sw, -8), (150 + sw, -150), (104, -450), (82, -560), (112, -690), (118, -785 + br),
                     (40, -808 + br), (-40, -808 + br)])
    p.addPath(body)
    p.addPath(D.rrect(-24, -850, 24, -790, 10))                         # neck
    # arms
    _arm(p, -112, -770 + br, la[0], 270, la[1], 250)
    _arm(p, 112, -770 + br, ra[0], 270, ra[1], 250)
    # head and hair
    hp = skia.Path()
    hp.addPath(D.oval(-56, -985, 56, -835))
    if hair == "bob":                                                   # shoulder-length, full, with a fringe
        hp.addPath(D.smooth([(-82, -830), (-90, -930), (-60, -1000), (0, -1012), (60, -1000), (90, -930), (82, -830), (56, -818),
                             (40, -870), (-40, -870), (-56, -818)]))
    elif hair == "bun":
        hp.addPath(D.oval(-62, -1000, 62, -850))
        hp.addPath(D.circle(0, -1010, 38))
    m = skia.Matrix()
    m.setRotate(tilt, 0, -840)
    hp.transform(m)
    p.addPath(hp)
    if lean:
        m2 = skia.Matrix()
        m2.setRotate(lean, 0, 0)
        p.transform(m2)
    return p


def figure(c, pth, x, y, s, rim=K.RED, side=1, rim_w=10, rim_a=1.0, halo=0.35, fill=(4, 3, 6), rim2=None, flip=False):
    """Fill a figure path at (x, y), scale s, as a silhouette lit by a hard rim of gel colour from `side` (+1 right)
    and, optionally, a second rim (rim2 = colour) from the other side."""
    c.save()
    c.translate(x, y)
    c.scale(-s if flip else s, s)
    if halo > 0:                                                        # light behind the figure, so it separates
        q = paint(rim, halo, blur=60 / max(s, 0.2))
        q.setBlendMode(skia.BlendMode.kPlus)
        c.drawPath(pth, q)
    c.drawPath(pth, paint(fill))
    c.save()
    c.clipPath(pth, doAntiAlias=True)
    for colr, sd, ww, aa in ((rim, side, rim_w, rim_a), (rim2, -side, rim_w * 0.7, rim_a * 0.7)):
        if colr is None:
            continue
        if flip:
            sd = -sd
        c.drawPath(pth, paint(colr, aa))
        c.save()
        c.translate(-sd * ww / s, ww * 0.25 / s)
        c.drawPath(pth, paint(fill, blur=ww * 0.35 / s))
        c.restore()
    c.restore()
    c.restore()


def woman(c, x, y, s, pose="stand", rim=K.RED, side=1, T=0.0, rim2=None, halo=0.35, hair="bob", stride=0.0, rim_w=10, flip=False):
    figure(c, woman_path(pose, T, hair, stride=stride), x, y, s, rim, side, rim_w=rim_w, halo=halo, rim2=rim2, flip=flip)


def woman_profile_path(T=0.0, stride=0.0, arm=0.0, head=0.0, hand=None, lying=False):
    """Nora in profile facing right (+x), feet at 0, 1000 tall: the face line (brow, nose, lips, chin), a full bob,
    a long satin robe. stride -1..1 swings the hem and the arms; head: tilt (deg, + = down); hand: 'chest', 'jaw',
    'phone' or None."""
    p = skia.Path()
    br = 2.5 * math.sin(T * 1.6)
    sw = 40 * stride
    if lying:                                                           # flat on her back: a straight body, the feet raised a little
        p.addPath(D.smooth([(26, -800), (34, -760), (66, -700 + br), (70, -672 + br), (50, -634), (36, -566), (44, -480), (46, -300),
                            (44, -140), (52, -40), (70, -10), (60, 6), (-40, 4), (-60, -150), (-66, -330), (-70, -470), (-52, -560),
                            (-62, -690), (-58, -760), (-26, -806)]))
    else:
        p.addPath(D.smooth([(26, -800), (34, -760), (68, -700 + br), (74, -672 + br), (52, -634), (34, -566), (42, -488), (64, -300 + sw * 0.3),
                            (96 + sw, -120), (124 + sw, -6), (40, 2), (-40, 2), (-120 - sw * 0.6, -6), (-104 - sw * 0.4, -150), (-80, -330),
                            (-74, -470), (-48, -560), (-62, -690), (-58, -760), (-26, -806)]))
    if stride:                                                          # feet under the hem
        p.addPath(D.smooth([(80 + sw, -12), (150 + sw, -16), (160 + sw, 4), (80 + sw, 6)]))
    hp = skia.Path()
    hp.addPath(D.smooth([(-6, -990), (40, -968), (58, -930), (60, -914), (84, -884), (64, -874), (70, -862), (62, -852), (67, -842),
                         (56, -822), (28, -812), (22, -790), (-26, -792), (-36, -840), (-66, -880), (-62, -950)]))
    hp.addPath(D.smooth([(-6, -1004), (46, -982), (64, -944), (48, -934), (20, -952), (-10, -930), (-30, -880), (-20, -832),
                         (-58, -820), (-90, -836), (-96, -900), (-80, -968)]))          # the bob, the fringe
    if head:
        m = skia.Matrix()
        m.setRotate(head, 0, -800)
        hp.transform(m)
    p.addPath(hp)
    sx, sy = -6, -748
    if hand == "chest":
        _arm(p, sx, sy, 22, 230, 128, 170, 38, 28)
    elif hand == "jaw":
        _arm(p, sx, sy, 30, 230, 150, 205, 38, 28)
    elif hand == "phone":
        _arm(p, sx, sy, 12, 230, 100, 200, 38, 28)
    else:
        _arm(p, sx, sy, 8 + 24 * stride + arm, 240, 14, 220, 38, 28)
    return p


def woman_p(c, x, y, s, rim=K.RED, side=1, T=0.0, rim2=None, halo=0.35, stride=0.0, rim_w=10, flip=False, head=0.0, hand=None, fill=(4, 3, 6)):
    figure(c, woman_profile_path(T, stride, head=head, hand=hand), x, y, s, rim, side, rim_w=rim_w, halo=halo, rim2=rim2, flip=flip, fill=fill)


def man_profile_path(T=0.0, stride=0.0, push=False, coat=False, clipboard=False):
    """A man in profile facing right, 1000 tall: trousers (two legs), a jacket or a long coat, arms forward if pushing."""
    p = skia.Path()
    sw = stride
    for sgn in (-1, 1):                                                 # legs
        a = sgn * 18 * sw
        hx, hy = 0, -470
        kx, ky = hx + 240 * math.sin(math.radians(a)), hy + 240 * math.cos(math.radians(a))
        fx, fy = kx + 230 * math.sin(math.radians(a - 6 * abs(sw))), ky + 230 * math.cos(math.radians(a - 6 * abs(sw)))
        _cap(p, hx, hy, kx, ky, 66, 52)
        _cap(p, kx, ky, fx, fy, 52, 42)
        p.addPath(D.smooth([(fx - 20, fy - 14), (fx + 60, fy - 10), (fx + 64, fy + 6), (fx - 24, fy + 8)]))
    hem = -150 if coat else -420
    p.addPath(D.smooth([(-70, hem), (-76, -600), (-60, -760), (-20, -800), (40, -790), (70, -700), (62, -560), (70, hem)]))
    p.addPath(D.rrect(-22, -850, 26, -780, 10))
    p.addPath(D.smooth([(-50, -980), (20, -990), (60, -950), (66, -920), (90, -892), (66, -880), (70, -850), (52, -822), (10, -812),
                        (-40, -830), (-64, -890)]))
    if push:
        _arm(p, 0, -760, 50, 220, 10, 200, 56, 42)
    elif clipboard:
        _arm(p, 0, -760, 14, 250, 95, 210, 58, 44)
        p.addPath(D.rrect(150, -720, 250, -580, 8))
    else:
        _arm(p, 0, -760, 10 + 26 * sw, 250, 12, 230, 56, 42)
    return p


def seated_man_path(turn=0.0):
    """A man at a desk in profile facing right: head, shoulders, back, an arm forward to the pen. turn 0..1: the head
    comes round to face us."""
    p = skia.Path()
    p.addPath(D.smooth([(-150, 40), (-170, -200), (-140, -420), (-60, -470), (40, -460), (90, -400), (110, -260), (80, -120), (60, 40)]))
    _cap(p, 40, -420, 200, -250, 60, 44)
    _cap(p, 200, -250, 330, -190, 44, 34)
    p.addPath(D.circle(335, -190, 26))
    p.addPath(D.rrect(-20, -530, 30, -450, 10))
    hx = 10 + 0 * turn
    p.addPath(D.oval(hx - 62 + 10 * turn, -660, hx + 70 - 8 * turn, -500))
    if turn < 0.5:                                                      # profile: a nose
        p.addPath(path([(hx + 60, -600), (hx + 92, -560), (hx + 62, -548)]))
    return p


def man_face(c, x, y, s, a=1.0, glow_col=(150, 200, 255)):
    """The turned head's face: lit from below by the phone - pale planes, eye sockets in black. No features beyond that."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    face = D.oval(-56, -76, 56, 84)
    c.drawPath(face, paint(shader=D.lin((0, 84), (0, -76), [mix(glow_col, (255, 255, 255), 0.3), mix(glow_col, (0, 0, 0), 0.5), (0, 0, 0)]), a=a))
    for sx in (-1, 1):
        c.drawPath(D.oval(sx * 22 - 18, -18, sx * 22 + 18, 6), paint((0, 0, 0), a))
        c.drawCircle(sx * 22, -6, 3, paint((255, 255, 255), a * 0.9))
    c.drawPath(D.oval(-16, 40, 16, 50), paint((0, 0, 0), a * 0.8))
    c.restore()


def lady_path(pour=0.0):
    """An older woman standing in profile facing right, a hat, arms forward with a bag (pour 0..1 tips it)."""
    p = skia.Path()
    p.addPath(D.smooth([(-110, 0), (-120, -300), (-90, -560), (-60, -760), (40, -770), (80, -560), (110, -300), (120, 0)]))
    p.addPath(D.rrect(-18, -820, 22, -760, 10))
    p.addPath(D.oval(-48, -950, 58, -800))
    p.addPath(D.smooth([(-110, -900), (0, -935), (120, -905), (40, -890), (-40, -890)]))      # a hat brim
    p.addPath(D.oval(-50, -1000, 50, -890))
    _cap(p, 40, -720, 180, -600, 46, 36)
    _cap(p, 180, -600, 250, -680 + 40 * pour, 36, 30)
    return p


def doctor_path():
    p = skia.Path()
    p.addPath(D.smooth([(-150, 0), (-160, -380), (-130, -700), (-120, -790), (120, -790), (130, -700), (160, -380), (150, 0)]))
    p.addPath(D.rrect(-26, -850, 26, -780, 10))
    p.addPath(D.oval(-62, -1000, 62, -830))
    _arm(p, -120, -770, -8, 280, 6, 260)
    _arm(p, 120, -770, 30, 280, -110, 220)
    return p


def lying_path(T=0.0, breath=1.0):
    """Nora lying on her back, head to the left, in profile (local: head at x -460, feet at +480, back on y = 0)."""
    p = skia.Path()
    b = 6 * breath * math.sin(T * 1.6)
    p.addPath(D.smooth([(-380, 0), (-380, -90 - b), (-250, -120 - b), (-60, -110 - b), (120, -95), (300, -80), (480, -60),
                        (500, 0)]))
    p.addPath(D.oval(-520, -120, -380, 10))                            # head on the pillow
    p.addPath(path([(-392, -70), (-370, -100), (-386, -54)]))           # the nose
    p.addPath(D.smooth([(-530, -90), (-470, -140), (-390, -120), (-380, 10), (-520, 20)]))          # hair on the pillow
    return p


# ------------------------------------------------------------------ extreme close-ups

def eye(c, cx, cy, s, T=0.0, open_k=1.0, gel=K.RED, refl=True, pupil=1.0, look=(0.0, 0.0), wet=1.0, iris_col=(96, 128, 70)):
    """An eye filling the frame (w ~ 900 px at s = 1). open_k 0..1; refl: a phone's glow in the cornea."""
    c.save()
    c.translate(cx, cy)
    c.scale(s, s)
    # skin, lit by the gel from the right, the far side falling to black
    c.drawRect(skia.Rect.MakeLTRB(-1400, -1400, 1400, 1400), paint(shader=D.rad((420, -160), 1300, [mix(gel, SKIN, 0.35),
                                                                                                     mix(gel, (30, 10, 10), 0.55), (6, 2, 4)], [0, 0.45, 1])))
    for k in range(3):                                                  # the brow, soft and dark above
        c.drawPath(D.smooth([(-560, -360 - 12 * k), (-200, -470 - 12 * k), (300, -460 - 8 * k), (620, -330), (300, -400), (-200, -410)]),
                   paint((20, 8, 8), 0.5, blur=30))
    ok = max(0.02, open_k)
    up = [(-430, 10), (-250, -150 * ok - 30), (0, -230 * ok - 10), (260, -170 * ok - 20), (440, -10)]
    lo = [(440, -10), (250, 110), (0, 150), (-260, 110), (-430, 10)]
    opening = D.smooth(up + lo[1:-1], closed=True)
    # crease above the lid
    c.drawPath(D.smooth([(-420, -60), (-200, -300), (60, -330), (330, -250), (470, -40)], closed=False), paint((30, 10, 10), 0.6, stroke=18, blur=10))
    c.save()
    c.clipPath(opening, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(-460, -320, 460, 200), paint(shader=D.rad((60, 20), 520, [(236, 226, 220), (200, 170, 168), (120, 60, 60)], [0, 0.6, 1])))
    rng = np.random.default_rng(4)
    for _ in range(14):                                                 # veins at the corners
        sx = rng.choice([-1, 1])
        x0 = sx * rng.uniform(300, 430)
        pts = [(x0, rng.uniform(-60, 80))]
        for k in range(4):
            pts.append((pts[-1][0] - sx * rng.uniform(30, 60), pts[-1][1] + rng.uniform(-25, 25)))
        c.drawPath(path(pts, closed=False), paint((190, 40, 40), 0.55, stroke=2.5))
    ix, iy = look[0] * 120, -20 + look[1] * 60
    R = 205
    c.drawCircle(ix, iy, R, paint(shader=D.rad((ix, iy), R, [mix(iris_col, (255, 230, 150), 0.4), iris_col, mix(iris_col, (0, 0, 0), 0.6),
                                                             (10, 8, 6)], [0.0, 0.45, 0.88, 1.0])))
    for k in range(120):                                                # the iris fibres
        a = k / 120 * 2 * math.pi + rng.uniform(-0.02, 0.02)
        r0, r1 = R * (0.32 + 0.05 * rng.random()), R * (0.85 + 0.1 * rng.random())
        c.drawLine(ix + r0 * math.cos(a), iy + r0 * math.sin(a), ix + r1 * math.cos(a), iy + r1 * math.sin(a),
                   paint(mix(iris_col, (255, 240, 200), rng.uniform(0.0, 0.5)), 0.35, stroke=rng.uniform(1.5, 4)))
    for k in range(10):                                                 # crypts
        a = rng.uniform(0, 2 * math.pi)
        r = R * rng.uniform(0.45, 0.75)
        c.drawPath(D.smooth(D.ellipse(ix + r * math.cos(a), iy + r * math.sin(a), 14, 7, 8)), paint((20, 14, 8), 0.45))
    pr = R * 0.36 * pupil
    c.drawCircle(ix, iy, pr, paint((2, 2, 3)))
    c.drawCircle(ix, iy, R, paint((5, 4, 4), 0.85, stroke=16, blur=4))  # the limbal ring
    if refl:                                                            # the phone in the cornea, and the window
        c.drawPath(D.rrect(ix + 40, iy - 120, ix + 100, iy - 20, 12), paint((235, 245, 255), 0.95 * wet))
        c.drawPath(D.rrect(ix - 120, iy - 140, ix - 70, iy - 80, 8), paint(mix(gel, (255, 255, 255), 0.5), 0.6 * wet))
    c.drawRect(skia.Rect.MakeLTRB(-460, -320, 460, 200), paint(shader=D.lin((0, -240 * ok - 20), (0, -40), [(0, 0, 0, 0.7), (0, 0, 0, 0.0)])))
    c.restore()
    # lids: the wet line, the lash line, the lashes
    c.drawPath(D.smooth(lo[:], closed=False), paint((250, 210, 210), 0.55 * wet, stroke=7))
    c.drawPath(D.smooth(up, closed=False), paint((10, 4, 4), stroke=16))
    for k in range(46):                                                 # upper lashes curl up and out
        u = k / 45
        px, py = D.smooth(up, closed=False).getPoint(0) if False else (0, 0)
        x = -420 + 860 * u
        yb = -((1 - (2 * u - 1) ** 2) * (220 * ok + 10)) - 10
        L = (60 + 70 * math.sin(math.pi * u)) * (0.75 + 0.45 * abs(math.sin(k * 2.7)))
        ang = math.radians(-100 + 70 * (u - 0.5))
        x += 6 * math.sin(k * 1.9)
        c.drawPath(path([(x, yb), (x + L * 0.5 * math.cos(ang) + 10 * (u - 0.5) * 6, yb + L * 0.6 * math.sin(ang)),
                         (x + L * math.cos(ang) + 30 * (u - 0.5) * 3, yb + L * math.sin(ang) - 10)], closed=False),
                   paint((6, 2, 2), 0.95, stroke=5))
    for k in range(26):
        u = k / 25
        x = -380 + 760 * u
        yb = (1 - (2 * u - 1) ** 2) * 140 + 10
        c.drawLine(x, yb, x + 10 * (u - 0.5) * 4, yb + 34, paint((10, 4, 4), 0.7, stroke=3))
    c.restore()


def lips(c, cx, cy, s, open_k=0.0, gel=K.RED, rim=K.BLUE, tremble=0.0):
    """Lips filling the frame (w ~ 700 px at s = 1), parted by open_k, lit by the gel."""
    c.save()
    c.translate(cx, cy)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-1200, -1500, 1200, 1500), paint(shader=D.rad((-300, -200), 1300, [mix(gel, SKIN, 0.4), mix(gel, (30, 8, 8), 0.6),
                                                                                                     (4, 2, 3)], [0, 0.5, 1])))
    for sx in (-1, 1):                                                  # the philtrum's two soft ridges
        c.drawPath(D.smooth([(sx * 52, -330), (sx * 40, -200), (sx * 56, -112)], closed=False), paint((255, 220, 210), 0.12, stroke=16, blur=10))
    c.drawPath(D.smooth([(0, -330), (0, -200), (0, -118)], closed=False), paint((30, 6, 8), 0.25, stroke=40, blur=22))
    o = 70 * open_k
    upper = D.smooth([(-360, 0), (-200, -90), (-60, -120), (0, -96), (60, -120), (200, -90), (360, 0), (200, -10 - o * 0.3),
                      (0, -6 - o * 0.5), (-200, -10 - o * 0.3)])
    lower = D.smooth([(-360, 0), (-200, 10 + o * 0.4), (0, 8 + o), (200, 10 + o * 0.4), (360, 0), (220, 110 + o), (0, 150 + o),
                      (-220, 110 + o)])
    lipc = (170, 40, 50)
    if o > 2:
        c.drawPath(D.smooth([(-300, 0), (0, -6 - o * 0.5), (300, 0), (0, 10 + o)]), paint((10, 2, 4)))
        c.drawPath(D.rrect(-120, -6 - o * 0.5, 120, -6 - o * 0.5 + min(o * 0.5, 30), 10), paint((210, 200, 196), 0.75))
    for pth, lt in ((upper, (-140, -110)), (lower, (-120, 60 + o))):
        c.drawPath(pth, paint(shader=D.rad(lt, 420, [mix(lipc, gel, 0.4), mix(lipc, (0, 0, 0), 0.4), (20, 4, 6)], [0, 0.6, 1])))
    c.drawPath(D.smooth([(-160, 70 + o), (-40, 110 + o), (80, 90 + o)], closed=False), paint((255, 230, 230), 0.35, stroke=10, blur=6))
    c.drawPath(D.smooth([(-360, 0), (0, -2 - o * 0.4), (360, 0)], closed=False), paint(rim, 0.25, stroke=5, blur=3))
    c.restore()


def face_profile(c, x, y, s, key=(170, 215, 255), rim=K.RED, eye_k=1.0, key_a=1.0, rim_a=1.0, tear=0.0, hand=False, T=0.0,
                 head=0.0, skin_gel=None, pain=0.0, pale=0.0, sweat=0.0, lying=False):
    """Nora's head and shoulders in profile facing right, from the same outline as her silhouette (local units: chin
    near (60, -820); s ~ 4 fills the frame). The key light (the phone) falls on the face from the front, a hard gel rim
    on the back of the hair; the rest is shadow."""
    pth = woman_profile_path(T, 0.0, head=head, hand=None, lying=lying)
    gel = skin_gel or rim
    if pale > 0:                                                        # the blood going out of her face
        key = mix(key, (150, 160, 175), pale)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPath(pth, paint((8, 4, 6)))
    c.save()
    c.clipPath(pth, doAntiAlias=True)
    # skin in the key light: the front of the face and the throat
    c.drawRect(skia.Rect.MakeLTRB(-200, -1050, 200, -770), paint(shader=D.lin((90, -880), (-40, -880),
               [mix(mix(SKIN, key, 0.35), (255, 255, 255), 0.1) + (key_a,), mix(SKIN_D, gel, 0.35) + (0.85 * key_a,), (8, 4, 6, 0.0)])))
    # the hair over it (dark, with the rim)
    hair = D.smooth([(-6, -1004), (46, -982), (64, -944), (48, -934), (20, -952), (-10, -930), (-30, -880), (-20, -832),
                     (-58, -820), (-90, -836), (-96, -900), (-80, -968)])
    if head:
        m = skia.Matrix()
        m.setRotate(head, 0, -800)
        hair.transform(m)
        c.rotate(head, 0, -800)
    c.drawPath(D.oval(22, -930, 52, -900), paint((8, 4, 6), 0.5, blur=4))                # the eye socket's shadow
    if eye_k > 0.1:
        c.drawPath(D.smooth([(36, -914), (46, -919 - 2 * eye_k), (54, -913), (46, -910)]), paint((236, 236, 242), 0.92))
        c.drawCircle(49, -914, 2.6 * eye_k, paint((24, 16, 12)))
        c.drawCircle(50.5, -915.5, 0.9, paint((255, 255, 255)))
    c.drawPath(D.smooth([(34, -915), (46, -922 + 4 * (1 - eye_k)), (56, -913)], closed=False), paint((8, 4, 4), stroke=1.8))
    for k in range(7):
        u = k / 6
        bx, by = 37 + 18 * u, -918 - 3 * math.sin(math.pi * u) + 4 * (1 - eye_k)
        c.drawLine(bx, by, bx + 4, by - 5 * eye_k - 1.5, paint((8, 4, 4), stroke=1.0))
    c.drawPath(D.smooth([(30, -936 - 3 * pain), (46, -940 + 2 * pain), (58, -933 + 6 * pain)], closed=False), paint((14, 6, 6), 0.8,
                                                                                                          stroke=2.4 + 0.8 * pain))    # brow
    if pain > 0:                                                        # the furrow above the nose, the line by the mouth
        c.drawPath(D.smooth([(56, -936), (60, -944), (57, -952)], closed=False), paint((40, 14, 14), 0.6 * pain, stroke=1.4))
        c.drawPath(D.smooth([(58, -866), (52, -856), (54, -846)], closed=False), paint((40, 14, 14), 0.5 * pain, stroke=1.4))
    if sweat > 0:                                                       # beads on the brow and temple, catching the light
        for (sx_, sy_) in ((40, -962), (50, -955), (28, -950), (34, -905), (22, -940), (58, -948)):
            c.drawPath(D.oval(sx_ - 1.6, sy_ - 2.4, sx_ + 1.6, sy_ + 2.4), paint((235, 245, 255), 0.75 * sweat))
    if tear > 0:
        c.drawPath(path([(55, -908), (57, -908 + 40 * tear)], closed=False), paint((230, 240, 255), 0.85, stroke=1.4))
    c.drawPath(D.smooth([(66, -862), (70, -857), (64, -852), (67, -846)], closed=False), paint(mix((150, 30, 44), (110, 90, 110), pale), 0.8,
                                                                                            stroke=3.2))   # lips
    if pain > 0.3:                                                      # lips parted: a breath she can't catch
        c.drawPath(D.oval(62, -858, 68, -851 + 3 * pain), paint((10, 2, 4), min(1.0, pain)))
    if head:
        c.rotate(-head, 0, -800)
    c.drawPath(hair, paint((6, 3, 4)))
    c.save()
    c.clipPath(hair, doAntiAlias=True)
    c.drawPath(hair, paint(rim, rim_a))
    c.translate(5, 2)
    c.drawPath(hair, paint((6, 3, 4), blur=2.4))
    c.restore()
    c.restore()
    if hand:                                                            # her hand on her jaw: the back of it, fingers up the cheek
        palm = D.smooth([(-34, -752), (6, -748), (26, -802), (20, -816), (-40, -818), (-44, -800)])
        knuck = [(-34, -812), (-17, -816), (0, -816), (16, -810)]
        tips = [(-30, -864), (-12, -874), (6, -874), (22, -860)]
        parts = [palm] + [D.capsule(kx, ky, tx, ty, 15, 12) for (kx, ky), (tx, ty) in zip(knuck, tips)]
        for p_ in parts:
            c.drawPath(p_, paint(shader=D.lin((30, -800), (-40, -800), [mix(mix(SKIN, key, 0.35), (0, 0, 0), 0.1), mix(SKIN_D, gel, 0.45),
                                                                     (12, 6, 7)])))
            c.drawPath(p_, paint((6, 3, 3), 0.7, stroke=1.0))
    c.restore()


def hand_phone(c, x, y, s, T=0.0, screen=None, thumb=0.0, gel=K.RED, glow_col=(200, 225, 255), ang=0.0, lit=1.0, tremble=0.0):
    """A hand holding the phone (local: phone centre at 0, 0, 400 x 820); thumb 0..1 moves over the screen."""
    c.save()
    c.translate(x + tremble * 3 * math.sin(T * 37), y + tremble * 2 * math.sin(T * 41))
    c.rotate(ang)
    c.scale(s, s)
    skin_lit = mix(SKIN, glow_col, 0.35)
    # the palm behind, under the phone's lower half
    c.drawPath(D.smooth([(-280, 120), (-250, 460), (-60, 720), (220, 740), (330, 520), (260, 200)]), paint(shader=D.rad((40, 260), 640,
                                                                                                                           [mix(mix(SKIN_D, gel, 0.35), (0, 0, 0), 0.4), (24, 10, 10), (6, 3, 3)])))
    K.phone(c, 0, 0, 1.0, 0, screen, glow_col=glow_col, lit=lit)
    shadow = mix(mix(SKIN_D, gel, 0.35), (0, 0, 0), 0.6)
    edge = mix(skin_lit, (255, 255, 255), 0.1)
    for k in range(4):                                                  # fingers curling round the left edge: two joints each
        fy = -70 + k * 118
        w0 = 64 - 3 * k
        pts = [(-300, fy + 70), (-238, fy + 22), (-188, fy - 4)]
        for j in range(2):
            (x0, y0), (x1, y1) = pts[j], pts[j + 1]
            c.drawPath(D.capsule(x0, y0, x1, y1, w0, w0 * 0.86), paint(shadow))
        c.drawPath(D.smooth([(-262, fy + 40), (-220, fy + 4), (-186, fy - 22)], closed=False), paint(edge, 0.55, stroke=7, blur=3))
        c.drawLine(-240, fy + 2, -226, fy + 36, paint((0, 0, 0), 0.6, stroke=3))
        c.drawPath(D.oval(-204, fy - 22, -176, fy + 10), paint(mix(edge, (255, 230, 220), 0.3), 0.5))
    tx, ty = 230 - 220 * thumb, 260 - 160 * thumb + 18 * math.sin(T * 9) * (thumb > 0.05)
    c.drawPath(D.capsule(330, 600, (330 + tx) / 2 + 30, (600 + ty) / 2 + 20, 100, 84), paint(shadow))
    c.drawPath(D.capsule((330 + tx) / 2 + 30, (600 + ty) / 2 + 20, tx, ty, 84, 70), paint(shadow))
    c.drawPath(D.smooth([((330 + tx) / 2 + 10, (600 + ty) / 2 - 10), (tx - 20, ty - 26)], closed=False), paint(edge, 0.55, stroke=8, blur=3))
    c.drawPath(D.oval(tx - 28, ty - 26, tx + 22, ty + 16), paint(mix(edge, (255, 230, 220), 0.3), 0.45))
    c.restore()


def lying_nora(c, x, y, s, key=(170, 210, 255), rim=K.RED, eye_k=0.0, T=0.0, key_a=1.0, pain=0.0, pale=0.0, sweat=0.0):
    """Nora lying on her back, head to the left, face up: (x, y) is where her feet would be; she is 1000 * s long and
    her back rests about 77 * s below y. The face is lit from above, so she reads as a woman, not a shape."""
    c.save()
    c.translate(x, y)
    c.rotate(-90)
    face_profile(c, 0, 0, s, key=key, rim=rim, eye_k=eye_k, key_a=key_a, T=T, pain=pain, pale=pale, sweat=sweat, lying=True)
    c.restore()


def hand_flat(c, x, y, s, gel=K.RED, key=(255, 120, 110), ang=0.0, twitch=0.0):
    """A hand lying palm-down on the carpet, fingers loose, coming in from the left edge (local: knuckles at 0, 0)."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    dark = (24, 8, 8)
    lit = mix(mix(SKIN, gel, 0.45), (0, 0, 0), 0.15)
    palm = D.smooth([(-420, -70), (-150, -86), (-10, -78), (16, -10), (0, 64), (-140, 92), (-420, 80)])
    c.drawPath(palm, paint(shader=D.lin((0, -90), (0, 90), [lit, mix(lit, dark, 0.5), dark])))
    for i, (dy, L, w) in enumerate(((-58, 150, 40), (-14, 172, 42), (30, 162, 40), (70, 120, 34))):
        tw = twitch * 14 * math.sin(i * 1.7 + twitch * 9)
        pts = [(-10, dy), (L * 0.55, dy + 4 + i * 2 + tw * 0.4), (L, dy + 14 + 4 * i + tw)]
        for j in range(2):
            (x0, y0), (x1, y1) = pts[j], pts[j + 1]
            c.drawPath(D.capsule(x0, y0, x1, y1, w, w * 0.9), paint(shader=D.lin((x0, y0 - w), (x0, y0 + w), [lit, mix(lit, dark, 0.45), dark])))
        c.drawLine(L * 0.55, dy - w * 0.35, L * 0.55 + 4, dy + w * 0.3, paint((10, 4, 4), 0.6, stroke=3))
        c.drawPath(D.oval(L - 30, dy + 4 * i, L + 4, dy + 22 + 4 * i), paint(mix(lit, (255, 220, 210), 0.3), 0.6))
    c.drawPath(D.capsule(-160, -80, -40, -130, 46, 38), paint(shader=D.lin((0, -150), (0, -70), [lit, dark])))     # the thumb
    c.restore()
