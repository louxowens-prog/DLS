"""The figures of the nightmare.

MERIT - the entity. A moon-pale woman crowned with reels of tape and a sunburst of punched cards, long hair drifting
like smoke, eyes like slowly turning reels. She never raises her voice.

THE CLERKS - her servants: armoured, masked, half human and half machine. A smooth helmet, a single glowing slit
for eyes, a respirator snout breathing through a grille, cables running into a human throat; one hand is a press that
holds a heavy stamp. They never look at what they stamp.

Also: the stamp's mark, the human hand that stops it, and faces for the superimpositions (see cast.py for the face)."""
import math

import numpy as np
import skia

import cast as C
import pface as PF
import gel as G
import kit as K
from kit import BLACK, WHITE, mix, paint


# ------------------------------------------------------------------ Merit

def _card_ray(c, ang, r0, r1, w, a, T, seed):
    """One punched card standing out from her head like a ray of a dark sun."""
    c.save()
    c.rotate(ang)
    rect = skia.Rect.MakeLTRB(r0, -w / 2, r1, w / 2)
    c.drawRoundRect(rect, 6, 6, paint(shader=K.lin((r0, 0), (r1, 0), [(236, 226, 200, a), (200, 180, 150, a * 0.6), (120, 100, 90, 0.0)])))
    rng = K.rng_at(seed, 71)
    n = int((r1 - r0) / 26)
    for i in range(n):
        for j in range(3):
            if rng.random() < 0.45:
                x = r0 + 20 + i * 26
                y = -w / 2 + w * (0.22 + 0.28 * j)
                c.drawRect(skia.Rect.MakeXYWH(x, y - w * 0.07, 10, w * 0.14), paint((10, 6, 12), a * 0.9 * (1 - i / n)))
    c.restore()


def _reel(c, x, y, r, T, a=1.0, spin=1.0):
    """A reel of magnetic tape: a pale flange with three windows, the dark wound tape, a hub."""
    c.save()
    c.translate(x, y)
    c.rotate(T * 40 * spin)
    c.drawCircle(0, 0, r, paint((210, 206, 220), a))
    c.drawCircle(0, 0, r * 0.82, paint((40, 26, 30), a))           # the wound tape
    for k in range(8):
        c.drawCircle(0, 0, r * (0.42 + 0.05 * k), paint((70, 50, 52), a * 0.5, stroke=1.2))
    c.drawCircle(0, 0, r * 0.36, paint((210, 206, 220), a))
    for k in range(3):                                              # windows in the flange
        c.save()
        c.rotate(k * 120)
        p = K.smooth([(r * 0.42, -r * 0.18), (r * 0.78, -r * 0.3), (r * 0.78, r * 0.3), (r * 0.42, r * 0.18)])
        c.drawPath(p, paint((14, 8, 16), a * 0.7))
        c.restore()
    c.drawCircle(0, 0, r * 0.12, paint((30, 24, 34), a))
    c.drawCircle(-r * 0.3, -r * 0.3, r * 0.16, G.glow_paint(WHITE, 0.25 * a, blur=r * 0.08))
    c.restore()


def merit(c, x, y, s, T, eyes=1.0, talk=0.0, crown=1.0, rays=1.0, hair=1.0, mantle=1.0, smile=0.35, gaze=(0.0, 0.0),
          L=(255, 110, 50), R=(130, 70, 255), core=0.62, amb=(20, 10, 26), tilt=0.0, a=1.0, wide=0.0, jewel=1.0,
          rim_col=(200, 150, 255), key_at=(-0.5, 0.9)):
    """Merit, face-on, at (x, y) = the bridge of her nose, scale s (her face ~300 px wide at s = 1)."""
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    # --- a sunburst of punched cards behind her head
    if rays > 0:
        n = 18
        for i in range(n):
            ang = i * 360 / n + T * 2.5
            _card_ray(c, ang, 260, 260 + 520 * rays * (0.8 + 0.2 * math.sin(i * 1.3)), 56, 0.85, T, i)
    # --- hair drifting like smoke, as if underwater
    if hair > 0:
        for i in range(16):
            ang = math.pi * (0.05 + 0.9 * i / 15)
            sw = 30 * math.sin(T * 0.6 + i)
            pts = [(math.cos(ang) * 120, -40 - math.sin(ang) * 140),
                   (math.cos(ang) * (260 + sw), 60 - math.sin(ang) * 120 + 40),
                   (math.cos(ang) * (330 + 2 * sw), 260 + 120 * (1 - abs(math.cos(ang))) + sw)]
            path = K.bez_path(pts)
            c.drawPath(path, paint((30, 16, 40), 0.9 * hair, stroke=70 - 2 * abs(i - 7.5)))
    # --- the crown: five reels on a silver arc, and a ring of light
    if crown > 0:
        c.drawPath(K.bez_path([(-250, -150), (0, -390), (250, -150)]), paint((200, 196, 220), 0.9 * crown, stroke=10))
        c.drawCircle(0, -60, 300, paint((240, 220, 255), 0.35 * crown, stroke=4))
        for k, (ang, r) in enumerate(((-62, 46), (-31, 56), (0, 70), (31, 56), (62, 46))):
            rx = math.sin(math.radians(ang)) * 250
            ry = -150 - math.cos(math.radians(ang)) * 210
            _reel(c, rx, ry, r * crown, T, a=crown, spin=1 if k % 2 else -1)
    # --- the face
    PF.pface(c, 0, 0, 1.0, "merit", T, key=L, fill=R, rim=rim_col, amb=amb, blink=1 - eyes, gaze=gaze, talk=talk, smile=smile,
             wide=wide, key_at=key_at)
    # --- a jewel on the brow: a tiny reel of red light
    if jewel > 0:
        c.drawCircle(0, -150, 14, paint((200, 196, 220), jewel))
        c.drawCircle(0, -150, 9, G.glow_paint((255, 40, 40), jewel))
        G.pool(c, 0, -150, 50, (255, 60, 40), 0.5 * jewel)
    # --- the mantle: gauze falling from the crown past her cheeks, its weave punched with tiny holes
    if mantle > 0:
        for sd in (-1, 1):
            sw = 10 * math.sin(T * 0.5 + sd)
            p = K.smooth([(sd * 120, -250), (sd * 230, -200), (sd * (300 + sw), 60), (sd * (330 + sw), 400), (sd * 230, 520),
                          (sd * (190 + sw), 260), (sd * 168, 40), (sd * 150, -160)])
            c.drawPath(p, paint(shader=K.lin((sd * 150, 0), (sd * 330, 0), [(200, 180, 240, 0.08 * mantle), (220, 200, 255, 0.4 * mantle)])))
            c.drawPath(p, paint((240, 230, 255), 0.25 * mantle, stroke=2))
            rng = K.rng_at(sd + 9, 3)
            for i in range(40):
                yy = rng.uniform(-150, 450)
                xx = sd * (190 + (yy + 150) / 600 * 110 + rng.uniform(0, 50))
                c.drawRect(skia.Rect.MakeXYWH(xx, yy, 5, 9), paint((255, 240, 255), 0.35 * mantle))
    c.restore()
    c.restore()


# ------------------------------------------------------------------ the Clerks

def _plate(c, p, base, a=1.0, light=(0.0, -1.0), spec=0.5, edge=True):
    """Fill a path as a curved metal plate: graded from lit to dark, a specular band, a dark edge."""
    b = p.computeTightBounds()
    cx, cy = b.centerX(), b.centerY()
    hw, hh = b.width() / 2 + 1, b.height() / 2 + 1
    p0 = (cx + light[0] * hw, cy + light[1] * hh)
    p1 = (cx - light[0] * hw, cy - light[1] * hh)
    hi, lo = mix(base, WHITE, 0.35), mix(base, BLACK, 0.65)
    c.drawPath(p, paint(shader=K.lin(p0, p1, [hi, base, lo], [0.0, 0.45, 1.0]), a=a))
    if spec > 0:
        c.save()
        c.clipPath(p, doAntiAlias=True)
        sx, sy = cx + light[0] * hw * 0.45, cy + light[1] * hh * 0.45
        c.drawOval(skia.Rect.MakeLTRB(sx - hw * 0.7, sy - hh * 0.12, sx + hw * 0.7, sy + hh * 0.12), paint(WHITE, 0.35 * spec * a, blur=hh * 0.08))
        c.restore()
    if edge:
        c.drawPath(p, paint(mix(base, BLACK, 0.8), a, stroke=3))


def clerk(c, x, y, s, T, arm=0.0, slit=1.0, slit_col=(255, 40, 30), breathe=True, tilt=0.0, a=1.0, metal=(92, 88, 100),
          skin=(214, 190, 186), stamp=True, rim=(255, 60, 40), rim_k=1.0, look=0.0, cloak=True, seed=0):
    """A Clerk from the waist up at (x, y) = the base of its neck, scale s (~700 px wide at s = 1).
    arm: the stamp arm, 0 = held at the chest, 1 = raised high; look: the head turned (-1..1)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    br = 0.5 + 0.5 * math.sin(T * 2.2 + seed) if breathe else 0.5
    dark = mix(metal, BLACK, 0.55)
    # --- a ragged cloak behind
    if cloak:
        rng = K.rng_at(seed, 79)
        pts = [(-330, 60), (-260, -20), (260, -20), (330, 60), (360, 900)]
        for i in range(12):
            xx = 360 - i * 66
            pts.append((xx, 900 + rng.uniform(-60, 80)))
        pts.append((-360, 900))
        c.drawPath(K.path(pts), paint((18, 14, 20)))
    # --- the robe: heavy dark cloth from the shoulders down, folds catching the light
    robe = K.smooth([(-150, -10), (-270, 40), (-330, 200), (-350, 900), (350, 900), (330, 200), (270, 40), (150, -10), (0, 30)])
    c.drawPath(robe, paint((26, 22, 30)))
    rng = K.rng_at(seed, 81)
    for k in range(11):
        xx = -300 + k * 60 + rng.uniform(-10, 10)
        c.drawPath(K.bez_path([(xx * 0.6, 60), (xx * 0.95 + rng.uniform(-20, 20), 420), (xx * 1.05, 900)]), paint((52, 46, 58), 0.55, stroke=rng.uniform(6, 14), blur=5))
        c.drawPath(K.bez_path([(xx * 0.6 + 14, 60), (xx * 0.95 + 18, 420), (xx * 1.05 + 20, 900)]), paint((8, 6, 10), 0.6, stroke=8, blur=6))
    # the seal on the breast: a punched card in an iron ring
    c.drawCircle(0, 220, 78, paint(dark))
    c.drawCircle(0, 220, 78, paint(mix(metal, WHITE, 0.3), stroke=6))
    c.drawRoundRect(skia.Rect.MakeLTRB(-48, 192, 48, 248), 6, 6, paint((190, 180, 160)))
    rng = K.rng_at(3, 9)
    for i in range(7):
        for j in range(3):
            if rng.random() < 0.5:
                c.drawRect(skia.Rect.MakeXYWH(-42 + i * 12.5, 199 + j * 16, 6, 9), paint((20, 14, 16)))
    for k in range(3):                                                                               # chains hanging from it
        c.drawPath(K.bez_path([(-60 + k * 60, 296), (-50 + k * 50, 380), (-70 + k * 70, 470)]), paint(mix(metal, WHITE, 0.2), 0.7, stroke=4))
    # --- the human throat, and the cables that run into it
    neck = K.smooth([(-70, 10), (-64, -110), (64, -110), (70, 10)])
    c.drawPath(neck, paint(skin))
    c.drawPath(neck, paint(shader=K.lin((-70, 0), (70, 0), [(0, 0, 0, 0.6), (0, 0, 0, 0.0), (0, 0, 0, 0.6)])))
    c.drawPath(K.bez_path([(-10, -100), (-4, -60), (-14, -20)]), paint(mix(skin, BLACK, 0.4), 0.5, stroke=4))      # a tendon
    for k, (x0, x1) in enumerate(((-40, -120), (30, 140), (-6, -40))):
        cab = K.bez_path([(x0, -70 + k * 22), (x0 + (x1 - x0) * 0.4, 20), (x1, 90)])
        c.drawPath(cab, paint((20, 18, 22), stroke=18))
        c.drawPath(cab, paint(mix(metal, WHITE, 0.2), 0.5, stroke=4))
        c.drawCircle(x0, -70 + k * 22, 14, paint(mix(metal, BLACK, 0.3)))                  # where the cable goes in
        c.drawCircle(x0, -70 + k * 22, 18, paint((120, 40, 50), 0.5, stroke=3))
    # --- gorget
    for k in range(3):
        g = K.smooth([(-120 + k * 12, -10 + k * 20), (0, -30 + k * 26), (120 - k * 12, -10 + k * 20), (120 - k * 10, 20 + k * 20), (0, 0 + k * 26), (-120 + k * 10, 20 + k * 20)])
        _plate(c, g, mix(metal, BLACK, 0.1 * k), light=(0, -1), spec=0.4)
    # --- pauldrons
    for sd in (-1, 1):
        for k in range(3):
            pd = K.smooth([(sd * (150 + k * 24), 10 + k * 34), (sd * (250 + k * 12), -10 + k * 36), (sd * (318 + k * 4), 70 + k * 38),
                           (sd * (306 + k * 2), 130 + k * 32), (sd * (230 + k * 16), 90 + k * 36)])
            _plate(c, pd, mix(metal, BLACK, 0.08 * k), light=(-sd * 0.4, -1), spec=0.5)
        for k in range(3):
            c.drawCircle(sd * (200 + k * 40), 10 + k * 20, 7, paint(mix(metal, WHITE, 0.5)))
    # --- the stamp arm (its right, our left)
    if stamp:
        k = K.ease(arm)
        sx, sy = -300, 40
        ex, ey = -360 + 40 * k, 250 - 380 * k
        hx, hy = -250 + 30 * k, 360 - 820 * k
        c.drawPath(K.capsule(sx, sy, ex, ey, 150, 130), paint((30, 26, 34)))
        c.drawPath(K.capsule(ex, ey, hx, hy, 130, 110), paint((34, 30, 38)))
        _plate(c, K.capsule(ex + (hx - ex) * 0.55, ey + (hy - ey) * 0.55, hx, hy, 84, 72), metal, light=(-0.5, -1), spec=0.4)
        c.drawCircle(ex, ey, 46, paint(mix(metal, BLACK, 0.35)))
        c.drawCircle(ex, ey, 46, paint(mix(metal, WHITE, 0.3), stroke=4))
        # the press and the stamp it holds
        c.save()
        c.translate(hx, hy)
        c.drawRect(skia.Rect.MakeLTRB(-60, -40, 60, 40), paint(mix(metal, BLACK, 0.4)))
        c.drawRect(skia.Rect.MakeLTRB(-18, 30, 18, 110), paint(mix(metal, WHITE, 0.1)))            # the piston
        blk = K.rrect(-150, 110, 150, 230, 10)
        _plate(c, blk, (70, 46, 34), light=(-0.3, -1), spec=0.3)                                     # the dark wooden block
        c.drawRect(skia.Rect.MakeLTRB(-156, 226, 156, 256), paint((40, 6, 10)))                       # the inked rubber face
        c.restore()
    # --- the head: a deep hood, and in it a blank pewter face with one burning slit for eyes
    c.save()
    c.translate(0, -120)
    c.rotate(tilt + look * 6)
    hx_ = look * 22
    hood = K.smooth([(-190, 40), (-210, -160), (-170, -330), (-60, -410), (60, -410), (170, -330), (210, -160), (190, 40),
                     (260, 160), (-260, 160)])
    c.drawPath(hood, paint((22, 18, 26)))
    for k in range(7):                                                                               # folds
        xx = -150 + k * 50
        c.drawPath(K.bez_path([(xx * 0.5, -390), (xx * 1.1, -200), (xx * 1.3, 120)]), paint((40, 34, 46), 0.6, stroke=6, blur=3))
    c.drawPath(K.smooth([(-150, 30), (-160, -170), (-120, -300), (0, -340), (120, -300), (160, -170), (150, 30)]), paint((4, 2, 6)))
    mask = K.smooth([(0, -300), (70, -288), (112, -236), (124, -160), (118, -90), (100, -30), (62, 16), (0, 32), (-62, 16), (-100, -30),
                     (-118, -90), (-124, -160), (-112, -236), (-70, -288)])
    c.save()
    c.translate(hx_, 0)
    _plate(c, mask, mix(metal, WHITE, 0.25), light=(-0.25, -1), spec=0.6, edge=False)
    # a face pressed into the metal from behind: brow, the ridge of a nose, closed lips
    c.drawPath(K.bez_path([(-96, -196), (-50, -216), (-12, -196)]), paint((60, 56, 66), 0.5, stroke=6, blur=3))
    c.drawPath(K.bez_path([(96, -196), (50, -216), (12, -196)]), paint((60, 56, 66), 0.5, stroke=6, blur=3))
    c.drawPath(K.smooth([(-8, -180), (8, -180), (14, -96), (0, -84), (-14, -96)]), paint((200, 196, 206), 0.45, blur=3))
    c.drawPath(K.bez_path([(-18, -88), (0, -80), (18, -88)]), paint((50, 46, 56), 0.7, stroke=4))
    for sd in (-1, 1):
        c.drawPath(K.bez_path([(sd * 60, -120), (sd * 80, -70), (sd * 70, -20)]), paint((60, 56, 66), 0.45, stroke=8, blur=6))
    # the slit
    sl = K.rrect(-100, -176, 100, -152, 9)
    c.drawPath(sl, paint((20, 2, 4)))
    if slit > 0:
        c.drawPath(sl, G.glow_paint(slit_col, slit))
        c.drawRect(skia.Rect.MakeLTRB(-88, -168, 88, -160), G.glow_paint(mix(slit_col, WHITE, 0.7), slit))
        G.pool(c, 0, -164, 230, slit_col, 0.4 * slit, squash=0.22)
    # the mouth: a round grille, breathing
    c.drawCircle(0, -36, 34, paint((26, 22, 30)))
    for k in range(5):
        c.drawLine(-26 + k * 13, -62, -26 + k * 13, -10, paint((90, 86, 96), stroke=3))
    c.drawCircle(0, -36, 34, paint((180, 176, 186), 0.7, stroke=5))
    G.pool(c, 0, -36, 70, (255, 110, 70), 0.25 * br)
    for sd in (-1, 1):                                                                               # rivets along the jaw
        for k in range(4):
            c.drawCircle(sd * (104 - k * 18), -60 + k * 22, 5, paint((210, 206, 216), 0.8))
    c.restore()
    c.restore()
    # --- rim light from behind: the strobe catches the edges
    if rim_k > 0:
        c.save()
        mp = skia.Paint()
        mp.setBlendMode(skia.BlendMode.kPlus)
        mp.setAlphaf(min(1.0, rim_k))
        c.saveLayer(None, mp)
        for sd in (-1, 1):
            c.drawPath(K.smooth([(sd * 196, -100), (sd * 212, -280), (sd * 172, -450), (sd * 70, -530), (sd * 170, -470), (sd * 226, -300)]),
                       paint(rim, 0.55, blur=6))
            c.drawPath(K.smooth([(sd * 250, -40), (sd * 350, 60), (sd * 340, 160), (sd * 300, 60)]), paint(rim, 0.5, blur=6))
        c.restore()
        c.restore()
    c.restore()
    c.restore()


def stamp_mark(c, x, y, s, ang=-8.0, a=1.0, text="INELIGIBLE", color=(200, 16, 24), seed=0, tag="stamp"):
    """The mark the stamp leaves: a double-ruled box, bold condensed capitals, the ink patchy where the rubber missed."""
    f = K.font("oldstandard-700", 120)
    w = f.measureText(text)
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    box = skia.Rect.MakeLTRB(-w / 2 - 40, -125, w / 2 + 40, 55)
    c.saveLayer(None, None)
    c.drawRect(box, paint(color, a, stroke=12))
    c.drawRect(skia.Rect.MakeLTRB(box.left() + 18, box.top() + 18, box.right() - 18, box.bottom() - 18), paint(color, a, stroke=4))
    c.drawString(text, -w / 2, 0, f, paint(color, a))
    # missed ink: speckles knocked out of the print
    rng = K.rng_at(seed, 83)
    pe = paint((0, 0, 0), 1.0)
    pe.setBlendMode(skia.BlendMode.kDstOut)
    for i in range(160):
        c.drawCircle(rng.uniform(box.left(), box.right()), rng.uniform(box.top(), box.bottom()), rng.uniform(1, 5), pe)
    c.restore()
    K.reg_local(c, box.left(), box.top(), box.right(), box.bottom(), tag)
    c.restore()


def hand(c, x, y, s, ang=0.0, a=1.0, skin=(214, 170, 150), open_=1.0, light=(255, 150, 80)):
    """A human hand, palm out, fingers up (the human hand that reaches in and stops the stamp)."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    palm = K.smooth([(-90, 0), (-96, -120), (-60, -170), (60, -170), (96, -120), (90, 0), (60, 80), (-60, 80)])
    c.drawPath(K.capsule(0, 60, 0, 420, 150, 160), paint(mix(skin, BLACK, 0.3), a))              # the forearm
    c.drawPath(palm, paint(skin, a))
    for k, (dx, L, w) in enumerate(((-66, 150, 40), (-22, 190, 42), (22, 200, 42), (64, 170, 38))):
        sp = (1 - open_) * 0.6
        c.drawPath(K.capsule(dx, -150, dx + dx * 0.15 * open_, -150 - L * (1 - sp), w, w * 0.85), paint(skin, a))
        c.drawPath(K.capsule(dx, -150, dx + dx * 0.15 * open_, -150 - L * (1 - sp), w, w * 0.85), paint(mix(skin, BLACK, 0.5), 0.6 * a, stroke=2))
    c.drawPath(K.capsule(-90, -20, -170, -110, 46, 40), paint(skin, a))                          # the thumb
    c.drawPath(palm, paint(shader=K.lin((-100, -170), (100, 80), [light + (0.5,), (0, 0, 0, 0.4)]), a=a))
    c.restore()


def mouth_close(c, x, y, s, who, T, talk=0.0, L=(255, 80, 60), R=(120, 60, 255), a=1.0, expr="neutral"):
    """A face so close that only the mouth and chin fill the frame."""
    C.face(c, x, y - 134 * s, s, who, T, L=L, R=R, expr=expr, talk=talk, a=a, neck=True)


def eye_close(c, x, y, s, who, T, blink=0.0, gaze=(0.0, 0.0), L=(255, 80, 60), R=(120, 60, 255), a=1.0, expr="neutral"):
    """A face so close that one eye fills the frame (the left eye centred at x, y)."""
    C.face(c, x + 64 * s, y + 16 * s, s, who, T, L=L, R=R, expr=expr, blink=blink, gaze=gaze, a=a, neck=False)
