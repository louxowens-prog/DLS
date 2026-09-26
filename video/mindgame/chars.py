"""The cast, drawn with boiling lines.

JAG, the AI: a head shaped like a jagged skyline (jagged intelligence), a photo-collage face pasted on,
noodle limbs. THE HUMAN: loose Yuasa-style figure, big head, rubbery arms.
"""
import math

import numpy as np
import skia

import mg
from mg import INK, WHITE


def jag(c, x, y, T, s=1.0, arms=(-40, 40), legs=0.0, eyes="normal", gaze=(0, 0), mouth="smile", tilt=0.0,
        head_col=mg.CYAN, body_col=mg.ORANGE, face="earth_ne2.jpg", seed=0, style="cel", bob=True, a=1.0):
    """x, y = point between the feet."""
    by = y - (6 * math.sin(T * 9) if bob else 0) * s
    R = 110 * s
    hx, hy = x, by - 330 * s
    c.save()
    c.translate(hx, hy)
    c.rotate(tilt)
    c.translate(-hx, -hy)
    lw = 7 * s
    # legs
    for side in (-1, 1):
        hip = (x + side * 26 * s, by - 150 * s)
        knee = (x + side * (40 + 30 * legs) * s, by - 75 * s)
        foot = (x + side * (34 + 60 * legs) * s, by)
        mg.tube(c, mg.bez(hip, knee, foot), T, 30 * s, 22 * s, body_col if style != "line" else WHITE, seed + 10 + side, lw=lw * 0.9)
        shoe = mg.circle_pts(foot[0] + side * 16 * s, foot[1] - 6 * s, 0, 16, rx=34 * s, ry=16 * s)
        mg.fill(c, shoe, T, INK, seed + 20 + side, off=(0, 0))
    # torso
    torso = np.array([(x - 50 * s, by - 232 * s), (x + 50 * s, by - 232 * s), (x + 62 * s, by - 138 * s), (x - 62 * s, by - 138 * s)])
    if style != "line":
        mg.fill(c, torso, T, body_col, seed + 30, off=(5 * s, 4 * s))
    mg.stroke(c, torso, T, seed + 31, width=lw, closed=True)
    # arms
    for side, ang in ((-1, arms[0]), (1, arms[1])):
        sh = (x + side * 42 * s, by - 215 * s)
        a_ = math.radians(90 + side * ang)
        hand = (sh[0] + side * 115 * s * abs(math.sin(a_)) + side * 10 * s, sh[1] + 115 * s * math.cos(a_))
        elbow = ((sh[0] + hand[0]) / 2 + side * 25 * s, (sh[1] + hand[1]) / 2 + 20 * s)
        mg.tube(c, mg.bez(sh, elbow, hand), T, 26 * s, 18 * s, head_col if style != "line" else WHITE, seed + 40 + side, lw=lw * 0.9)
        mitt = mg.circle_pts(hand[0], hand[1], 20 * s, 16)
        mg.fill(c, mitt, T, WHITE, seed + 50 + side, off=(0, 0))
        mg.stroke(c, mitt, T, seed + 51 + side, width=lw * 0.9, closed=True)
    # head: jagged skyline on top, round jaw below
    top = []
    xs = np.linspace(hx - R, hx + R, 11)
    for i, xx in enumerate(xs):
        h = [0.2, 0.95, 0.35, 0.75, 0.15, 1.05, 0.3, 0.8, 0.25, 0.65, 0.2][i]
        top.append((xx, hy - R * h))
    jaw = mg.circle_pts(hx, hy, R, 30, a0=0.0, a1=math.pi)
    head = np.vstack([np.array(top)[::-1] if False else np.array(top), jaw[::-1][::-1]])
    head = np.vstack([np.array(top), mg.circle_pts(hx, hy, R, 30, a0=0.0, a1=math.pi)])
    if style != "line":
        mg.fill(c, head, T, head_col, seed + 60, off=(7 * s, 5 * s))
    mg.stroke(c, head, T, seed + 61, width=lw * 1.2, closed=True)
    # collage face: a photo scrap pasted on, features drawn over it
    if face and style != "line":
        fp = mg.circle_pts(hx, hy + 0.2 * R, 0, 28, rx=0.72 * R, ry=0.58 * R)
        mg.collage(c, face, fp, T, seed=seed + 70, src=(900 + 300 * math.sin(seed), 300), scale=1.2 * s, border=6 * s)
    ex = 0.33 * R
    for side in (-1, 1):
        cx_, cy_ = hx + side * ex, hy + 0.05 * R
        if eyes == "closed":
            mg.stroke(c, mg.bez((cx_ - 18 * s, cy_), (cx_, cy_ + 12 * s), (cx_ + 18 * s, cy_)), T, seed + 80 + side, width=lw)
            continue
        er = 26 * s if eyes != "wide" else 36 * s
        c.drawCircle(cx_, cy_, er, mg.paint(WHITE, a))
        mg.stroke(c, mg.circle_pts(cx_, cy_, er, 20), T, seed + 82 + side, width=lw * 0.8, closed=True)
        if eyes == "spiral":
            ang = np.linspace(0, 5 * math.pi, 40) + T * 8 * side
            rr = np.linspace(2, er * 0.85, 40)
            sp = np.stack([cx_ + rr * np.cos(ang), cy_ + rr * np.sin(ang)], 1)
            c.drawPath(mg.path_of(sp), mg.paint(INK, a, stroke=3.5 * s))
        else:
            c.drawCircle(cx_ + gaze[0] * er * 0.45, cy_ + gaze[1] * er * 0.45, er * 0.45, mg.paint(INK, a))
            c.drawCircle(cx_ + gaze[0] * er * 0.45 - er * 0.15, cy_ + gaze[1] * er * 0.45 - er * 0.15, er * 0.13, mg.paint(WHITE, a))
    my = hy + 0.45 * R
    if mouth == "smile":
        mg.stroke(c, mg.bez((hx - 40 * s, my - 6 * s), (hx, my + 26 * s), (hx + 40 * s, my - 6 * s)), T, seed + 90, width=lw)
    elif mouth == "open":
        mp = mg.circle_pts(hx, my + 6 * s, 0, 20, rx=30 * s, ry=22 * s)
        mg.fill(c, mp, T, (120, 20, 30), seed + 91, off=(0, 0))
        mg.stroke(c, mp, T, seed + 92, width=lw, closed=True)
    elif mouth == "o":
        mp = mg.circle_pts(hx, my + 4 * s, 13 * s, 16)
        mg.fill(c, mp, T, (120, 20, 30), seed + 91, off=(0, 0))
        mg.stroke(c, mp, T, seed + 93, width=lw, closed=True)
    elif mouth == "frown":
        mg.stroke(c, mg.bez((hx - 34 * s, my + 12 * s), (hx, my - 12 * s), (hx + 34 * s, my + 12 * s)), T, seed + 94, width=lw)
    else:
        mg.stroke(c, [(hx - 30 * s, my), (hx + 30 * s, my)], T, seed + 95, width=lw)
    c.restore()
    return hx, hy, R


def human(c, x, y, T, s=1.0, arms=(-30, 30), legs=0.0, mouth="smile", eyes="normal", gaze=(0, 0), tilt=0.0,
          shirt=mg.RED, skin=(245, 205, 170), hair=(60, 40, 30), seed=100, style="cel", bob=True):
    by = y - (5 * math.sin(T * 7 + 1) if bob else 0) * s
    lw = 7 * s
    hx, hy = x, by - 380 * s
    c.save()
    c.translate(hx, hy)
    c.rotate(tilt)
    c.translate(-hx, -hy)
    for side in (-1, 1):
        hip = (x + side * 24 * s, by - 170 * s)
        foot = (x + side * (30 + 55 * legs) * s, by)
        mg.tube(c, mg.bez(hip, (x + side * (36 + 20 * legs) * s, by - 85 * s), foot), T, 44 * s, 30 * s, (50, 60, 110), seed + side, lw=lw * 0.9)
        shoe = mg.circle_pts(foot[0] + side * 18 * s, foot[1] - 8 * s, 0, 16, rx=38 * s, ry=17 * s)
        mg.fill(c, shoe, T, INK, seed + 4 + side, off=(0, 0))
    body = np.array([(x - 62 * s, by - 305 * s), (x + 62 * s, by - 305 * s), (x + 72 * s, by - 160 * s), (x - 72 * s, by - 160 * s)])
    if style != "line":
        mg.fill(c, body, T, shirt, seed + 10, off=(6 * s, 4 * s))
    mg.stroke(c, body, T, seed + 11, width=lw, closed=True)
    for side, ang in ((-1, arms[0]), (1, arms[1])):
        sh = (x + side * 50 * s, by - 290 * s)
        a_ = math.radians(90 + side * ang)
        hand = (sh[0] + side * 130 * s * abs(math.sin(a_)), sh[1] + 130 * s * math.cos(a_))
        mg.tube(c, mg.bez(sh, ((sh[0] + hand[0]) / 2 + side * 30 * s, (sh[1] + hand[1]) / 2 + 25 * s), hand), T, 34 * s, 24 * s, shirt, seed + 20 + side, lw=lw * 0.9)
        mitt = mg.circle_pts(hand[0], hand[1], 19 * s, 14)
        mg.fill(c, mitt, T, skin, seed + 25 + side, off=(0, 0))
        mg.stroke(c, mitt, T, seed + 26 + side, width=lw * 0.8, closed=True)
    R = 78 * s
    head = mg.circle_pts(hx, hy, R, 36, rx=R * 0.92)
    if style != "line":
        mg.fill(c, head, T, skin, seed + 30, off=(5 * s, 4 * s))
    mg.stroke(c, head, T, seed + 31, width=lw * 1.1, closed=True)
    hairp = mg.bez((hx - R * 0.95, hy - R * 0.1), (hx - R * 0.6, hy - R * 1.5), (hx + R * 0.95, hy - R * 0.35), n=18)
    hp = np.vstack([hairp, mg.circle_pts(hx, hy, R * 0.98, 18, a0=-0.35, a1=-math.pi + 0.1)])
    if style != "line":
        mg.fill(c, hp, T, hair, seed + 32, off=(0, 0))
    mg.stroke(c, hairp, T, seed + 33, width=lw)
    for side in (-1, 1):
        ex, ey = hx + side * R * 0.35 + gaze[0] * 5 * s, hy + R * 0.1 + gaze[1] * 5 * s
        if eyes == "closed":
            mg.stroke(c, [(ex - 10 * s, ey), (ex + 10 * s, ey)], T, seed + 40 + side, width=lw * 0.8)
        elif eyes == "wide":
            c.drawCircle(ex, ey, 14 * s, mg.paint(WHITE))
            mg.stroke(c, mg.circle_pts(ex, ey, 14 * s, 14), T, seed + 42 + side, width=lw * 0.6, closed=True)
            c.drawCircle(ex, ey, 5 * s, mg.paint(INK))
        else:
            c.drawCircle(ex, ey, 7 * s, mg.paint(INK))
    my = hy + R * 0.5
    if mouth == "smile":
        mg.stroke(c, mg.bez((hx - 24 * s, my - 4 * s), (hx, my + 14 * s), (hx + 24 * s, my - 4 * s)), T, seed + 50, width=lw * 0.8)
    elif mouth == "open":
        mp = mg.circle_pts(hx, my + 4 * s, 0, 16, rx=18 * s, ry=14 * s)
        mg.fill(c, mp, T, (140, 30, 40), seed + 51, off=(0, 0))
        mg.stroke(c, mp, T, seed + 52, width=lw * 0.8, closed=True)
    else:
        mg.stroke(c, [(hx - 18 * s, my), (hx + 18 * s, my)], T, seed + 53, width=lw * 0.8)
    c.restore()
    return hx, hy, R


def robot(c, x, y, T, s=1.0, arm=0.0, seed=200):
    """A boxy household robot for the kitchen scene."""
    lw = 7 * s
    body = mg.rect_pts(x - 80 * s, y - 260 * s, 160 * s, 170 * s)
    mg.fill(c, body, T, (200, 205, 215), seed, off=(6, 4))
    mg.stroke(c, body, T, seed + 1, width=lw, closed=True)
    head = mg.rect_pts(x - 60 * s, y - 380 * s, 120 * s, 100 * s)
    mg.fill(c, head, T, (170, 180, 195), seed + 2, off=(6, 4))
    mg.stroke(c, head, T, seed + 3, width=lw, closed=True)
    for side in (-1, 1):
        c.drawCircle(x + side * 28 * s, y - 335 * s, 14 * s, mg.paint((255, 60, 40)))
    for side in (-1, 1):
        mg.stroke(c, [(x + side * 50 * s, y - 90 * s), (x + side * 50 * s, y)], T, seed + 5 + side, width=lw * 2)
    sh = (x + 80 * s, y - 230 * s)
    hand = (sh[0] + 140 * s * math.cos(arm), sh[1] - 140 * s * math.sin(arm))
    mg.stroke(c, [sh, hand], T, seed + 8, width=lw * 1.6)
    mg.stroke(c, [(hand[0] - 16 * s, hand[1] - 10 * s), (hand[0] + 12 * s, hand[1]), (hand[0] - 16 * s, hand[1] + 10 * s)], T, seed + 9, width=lw)
    return hand
