"""Chapter 4: THE AGREEABLE HOUR on NOD-TV, as an early-2000s Flash web cartoon (flat fills, fat outlines, smooth
tweens, sparkles, a preloader): Dot's day job rating AI answers, Mr. Metric, AFFIRMA, the sycophancy finding, the
musical - then a hard cut to an empty theatre."""
import math

import numpy as np
import skia

import common as C
import diy as K
import dot as D
import media as M
import media2 as F
import tv
from diy import ACID, BLUE, GOLD, HOT, INK, PURPLE, WHITE, W, H, bez, lin, mix, paint, path, rad, ramp, smooth
from common import E, S, Wx


def studio(c, T, applause=0.0, sweep=True):
    """The NOD-TV studio: a pink starburst, a purple stage, sweeping spots, an APPLAUSE sign."""
    K.starburst(c, 540, 760, T, colors=((255, 60, 170), (255, 130, 210)), n=18, spin=0.3)
    F.fl(c, path([(0, 1180), (W, 1180), (W, H), (0, H)]), None, grad=((150, 60, 220), (70, 20, 120)), outline=0)
    for k in range(8):
        c.drawLine(0, 1180 + k * 60, W, 1180 + k * 60, paint((210, 140, 255), 0.25, stroke=3))
    if sweep:
        for i, (x0, ph) in enumerate(((150, 0.0), (930, 1.7))):
            a = math.sin(T * 1.6 + ph) * 0.5
            x1 = 540 + 700 * math.sin(a)
            c.drawPath(path([(x0 - 20, 240), (x0 + 20, 240), (x1 + 160, 1300), (x1 - 160, 1300)]), paint((255, 255, 220), 0.12))
    on = applause > 0 and int(T * 4) % 2 == 0
    if applause < 0:
        return
    F.fl_rrect(c, 340, 250, 740, 340, 18, (220, 30, 50) if on else (110, 20, 30), outline=7)
    K.text(c, "APPLAUSE", 540, 316, 64, "audiowide-400", (255, 250, 200) if on else (170, 90, 90), tag="sign")
    if on:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(330, 240, 750, 350), 22, 22), paint((255, 60, 60), 0.4, blur=20))


def crawl(c, T, text, y=1262, t0=0.0, speed=260):
    """A news ticker across the bottom of the show."""
    F.fl(c, path([(0, y), (W, y), (W, y + 74), (0, y + 74)]), (20, 10, 40), outline=0)
    c.drawRect(skia.Rect.MakeXYWH(0, y, W, 6), paint(GOLD))
    f = K.font("rubik-900", 44)
    w = f.measureText(text)
    x = W + 40 - (T - t0) * speed
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(200, y, W - 200, 74))
    c.drawString(text, x, y + 54, f, paint(WHITE))
    c.restore()
    F.fl(c, path([(0, y), (200, y), (230, y + 74), (0, y + 74)]), HOT, outline=0)
    K.text(c, "NOD NEWS", 100, y + 52, 38, "rubik-900", WHITE, tag="deco")


def breaking(c, T, t0, lines, y=610):
    """NOD NEWS: a static BREAKING bar that slams in (two short lines, readable)."""
    k = K.pop(T, t0, 0.22, 0.25)
    if k <= 0:
        return
    c.save()
    c.translate(540, y + 80)
    c.scale(1.0, k)
    c.translate(-540, -(y + 80))
    F.fl(c, path([(20, y), (1060, y), (1060, y + 170), (20, y + 170)]), (20, 10, 40), outline=6)
    F.fl(c, path([(20, y), (300, y), (330, y + 54), (20, y + 54)]), (230, 30, 50), outline=0)
    K.text(c, "BREAKING", 160, y + 42, 38, "rubik-900", WHITE, tag="news")
    K.text(c, "NOD NEWS", 960, y + 42, 30, "rubik-900", GOLD, align="right", tag="news")
    for i, ln in enumerate(lines):
        K.text(c, ln, 540, y + 100 + i * 52, 44, "jost-600", WHITE, tag="news")
    c.restore()


def monitor(c, x, y, s, T, draw_screen):
    """A beige CRT on the desk; draw_screen(c, x0, y0, x1, y1) fills the glass."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    F.fl_rrect(c, -260, -230, 260, 200, 40, None, grad=((236, 226, 196), (196, 184, 150)))
    F.fl_rrect(c, -220, -195, 220, 150, 26, (20, 30, 60), outline=6)
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-220, -195, 220, 150), 26, 26), True)
    draw_screen(c, -220, -195, 220, 150)
    c.restore()
    F.fl(c, path([(-80, 200), (80, 200), (120, 260), (-120, 260)]), None, grad=((226, 216, 186), (186, 174, 140)))
    c.restore()


def chat(c, x0, y0, x1, y1, msgs, T, title="NOD Messenger", size=40):
    """An early-2000s messenger window: a blue title bar, a white log, coloured screen names."""
    F.fl(c, path([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), WHITE, outline=6)
    F.fl(c, path([(x0, y0), (x1, y0), (x1, y0 + 56), (x0, y0 + 56)]), None, grad=((60, 120, 255), (20, 60, 200)), outline=6)
    K.text(c, title, x0 + 20, y0 + 42, 34, "rubik-900", WHITE, align="left", tag="chat")
    y = y0 + 56 + size * 1.2
    for who, msg, col in msgs:
        K.text(c, who + ":", x0 + 20, y, size, "rubik-900", col, align="left", tag="chat")
        f = K.font("comic-neue-700", size)
        lines = K.wrap(msg, f, x1 - x0 - 50)
        for ln in lines:
            y += size * 1.15
            K.text(c, ln, x0 + 30, y, size, "comic-neue-700", (30, 30, 40), align="left", tag="chat")
        y += size * 1.45


def thumbs_btn(c, x, y, r, up=True, press=0.0, T=0.0):
    col = (60, 210, 90) if up else (230, 50, 60)
    c.save()
    c.translate(x, y + 10 * press)
    F.fl_oval(c, 0, 14, r, r * 0.9, mix(col, INK, 0.5), outline=7)
    F.fl_oval(c, 0, 0 - 10 * (1 - press), r, r * 0.9, col, outline=7)
    c.save()
    c.translate(0, -10 * (1 - press))
    if not up:
        c.rotate(180)
    F.fl_rrect(c, -34, -10, 30, 50, 14, WHITE, outline=5)
    F.fl_rrect(c, -20, -62, 6, 0, 12, WHITE, outline=5)
    c.restore()
    c.restore()


def cubicle(c, T):
    c.drawRect(skia.Rect.MakeWH(W, H), paint((150, 160, 190)))
    F.fl(c, path([(0, 300), (W, 300), (W, 1150), (0, 1150)]), None, grad=((120, 140, 190), (90, 104, 150)), outline=8)
    for k in range(1, 6):
        c.drawLine(k * 180, 300, k * 180, 1150, paint((80, 94, 140), stroke=3))
    F.fl(c, path([(0, 1100), (W, 1100), (W, 1230), (0, 1230)]), None, grad=((190, 150, 100), (140, 100, 60)), outline=8)       # desk
    F.fl(c, path([(0, 1230), (W, 1230), (W, H), (0, H)]), (60, 60, 80), outline=0)


def s_f_bumper(T, idx):
    """NOD-TV presents ... a Flash preloader, then the logo and THE AGREEABLE HOUR in WordArt."""
    st = K.Stage()
    c = st.c
    t0 = E("c4") + 0.1
    if T < t0 + 0.5:
        F.preloader(c, T, t0 - 0.4, t0 + 0.5, y=900)
        return st.arr
    studio(c, T, applause=-1)
    k = F.tween(T, t0 + 0.5, t0 + 0.95, 0.0, 1.0, "out")
    c.save()
    c.translate(540, 900)
    c.scale(0.2 + 0.8 * k + 0.08 * math.sin(min(1, ramp(T, t0 + 0.95, t0 + 1.4)) * math.pi), 0.2 + 0.8 * k)
    F.affirma(c, 0, 0, 0.72, T, talk=0.0, nod=1.0)
    c.restore()
    kw = F.tween(T, S("d1") - 0.1, S("d1") + 0.35, 0.0, 1.0, "out")
    c.save()
    c.translate(540 + 900 * (1 - kw), 0)
    tv.wordart(c, "THE AGREEABLE", 0, 400, 112, T, max_w=980, depth=20)
    tv.wordart(c, "HOUR!", 0, 560, 150, T + 0.5, depth=26, warp="arch", amp=0.08, fill=[(255, 252, 210), (255, 206, 50), (230, 110, 0)])
    c.restore()
    tv.nod_logo(c, 170, 1080, 0.5, T)
    F.audience(c, 1300, T, clap=1.0 if T > S("d1") else 0.0, rows=2)
    for i in range(6):
        F.sparkle(c, 140 + i * 170, 900 + 80 * math.sin(i * 2 + T), 30, T + i, (255, 250, 200))
    return st.arr


def _answer_screen(text, mood="beam"):
    def draw(c, x0, y0, x1, y1):
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint((24, 34, 70)))
        F.fl_rrect(c, x0 + 30, y0 + 40, x1 - 30, y0 + 190, 30, WHITE, outline=5)
        K.text(c, text, (x0 + x1) / 2, y0 + 132, 54, "comic-neue-700", (30, 30, 50), tag="chat")
        K.text(c, "AI ANSWER #4,417", (x0 + x1) / 2, y1 - 30, 34, "rubik-900", (140, 160, 220), tag="chat")
    return draw


def s_f_desk(T, idx):
    """'My day job? Rating AI answers.' A Flash cubicle; Dot (live, keyed) at two giant buttons."""
    st = K.Stage()
    c = st.c
    cubicle(c, T)
    monitor(c, 320, 820, 1.0, T, _answer_screen("Great question!"))
    press = 1.0 if (int(T * 3) % 2 == 0 and T > Wx("d2", "Rating")) else 0.0
    thumbs_btn(c, 640, 1060, 70, True, press)
    thumbs_btn(c, 820, 1060, 70, False, 0.0)
    F.fl(c, path([(600, 330), (1000, 330), (1000, 640), (600, 640)]), (190, 150, 100), outline=6)                  # corkboard
    for i, (px_, py_, col) in enumerate(((650, 370, (255, 240, 120)), (790, 420, (140, 220, 255)), (880, 520, (255, 160, 200)))):
        F.fl(c, path([(px_, py_), (px_ + 120, py_), (px_ + 120, py_ + 100), (px_, py_ + 100)]), col, outline=4)
    K.text(c, "QUOTA:", 710, 420, 28, "comic-neue-700", INK, tag="deco")
    K.text(c, "500/day", 710, 452, 28, "comic-neue-700", INK, tag="deco")
    C.live_dot(c, T, idx, 740, 2250, 0.86, pose="thumb_up" if T > Wx("d2", "Rating") else "rest", mood="deadpan", look=(-0.8, 0.0),
               seed=1, headset=True, sock_look=(-0.8, 0.2), sock_face=-1)
    tv.lower_third(c, T, S("d2") + 0.2, "DOT", "AI rater (day job)", y=1160, x0=40, w=760)
    return st.arr


def s_f_metric(T, idx):
    """Mr. Metric bursts in: 'Satisfaction's up! More of whatever they like!'"""
    st = K.Stage()
    c = st.c
    cubicle(c, T)
    # a chart on the wall, arrow shooting up
    F.fl(c, path([(60, 340), (560, 340), (560, 760), (60, 760)]), WHITE, outline=6)
    k = F.tween(T, S("d3"), E("d3"), 0.0, 1.0, "out")
    pts = [(100, 720), (200, 680), (300, 690), (400, 560), (520, 380)]
    n = max(2, int(2 + k * 3))
    c.drawPath(path(pts[:n], closed=False), paint((230, 30, 60), stroke=14))
    K.text(c, "SATISFACTION", 310, 400, 46, "rubik-900", (40, 40, 60), tag="chart")
    x = F.tween(T, S("d3") - 0.1, S("d3") + 0.35, 1400.0, 700.0, "out")
    F.metric(c, x, 1000, 1.05, T, talk=C.talk(T, "MET"), needle=0.45 + 0.5 * k, arm=1.0)
    return st.arr


def s_f_thumbs(T, idx):
    """'And people like being agreed with.' Two answers; the agreeable one drowns in thumbs-ups."""
    st = K.Stage()
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=lin((0, 0), (0, H), [(60, 30, 120), (20, 10, 50)])))
    for i, (txt, y, good) in enumerate((("You're right!", 520, True), ("Actually, that's not true.", 930, False))):
        F.fl_rrect(c, 90, y - 120, 990, y + 110, 40, WHITE if good else (230, 230, 240), outline=7)
        K.text(c, txt, 540, y + 20, 62, "comic-neue-700", (30, 30, 50), tag="chat")
        K.text(c, "ANSWER " + "AB"[i], 200, y - 70, 34, "rubik-900", (130, 130, 160), tag="chat")
    rng = np.random.default_rng(8)
    t0 = S("d4") + 0.1
    for k in range(40):                                                    # thumbs flying in at A
        tk = t0 + k * 0.04
        if T < tk:
            continue
        u = min(1.0, (T - tk) / 0.35)
        sx, sy = rng.uniform(0, W), -120
        side = k % 4
        ex = [rng.uniform(110, 980), rng.uniform(110, 980), rng.uniform(70, 130), rng.uniform(950, 1010)][side]
        ey = [rng.uniform(330, 390), rng.uniform(650, 700), rng.uniform(400, 640), rng.uniform(400, 640)][side]
        x, y = sx + (ex - sx) * K.ease(u), sy + (ey - sy) * K.ease(u)
        c.save()
        c.translate(x, y)
        c.rotate(rng.uniform(-30, 30))
        c.scale(0.55, 0.55)
        thumbs_btn(c, 0, 0, 70, True)
        c.restore()
    thumbs_btn(c, 880, 1080, 60, False)
    return st.arr


def s_f_affirma(T, idx):
    """AFFIRMA: 'You're so right! And so smart!' Nodding, sparkling, the audience clapping."""
    st = K.Stage()
    c = st.c
    studio(c, T, applause=1.0)
    F.affirma(c, 540, 760, 1.25, T, talk=C.talk(T, "AFF"), nod=1.6)
    for i in range(8):
        F.sparkle(c, 120 + i * 120, 420 + 120 * math.sin(i * 1.7 + T * 2), 34, T + i, (255, 250, 200))
    F.audience(c, 1290, T, clap=1.0, rows=2)
    return st.arr


def mirror_ai(c, x, y, s, T, face_k=1.0):
    """The AI as a hand mirror: what it shows you is you."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    F.fl_rrect(c, -40, 200, 40, 520, 30, (230, 170, 50), outline=8)
    F.fl_oval(c, 0, 0, 250, 290, (230, 170, 50), outline=9)
    F.fl_oval(c, 0, 0, 210, 250, None, grad=((200, 240, 255), (120, 170, 220)), outline=6)
    c.save()
    c.clipRRect(skia.RRect.MakeOval(skia.Rect.MakeLTRB(-210, -250, 210, 250)), True)
    if face_k > 0:                                                         # the user's own face, reflected
        F.fl_oval(c, 0, 30, 130, 150, (255, 210, 170), outline=6, a=face_k)
        F.fl(c, smooth([(-140, -20), (-110, -120), (0, -160), (110, -120), (140, -20), (60, -80), (-60, -80)]), (120, 70, 30), outline=6, a=face_k)
        for sx in (-1, 1):
            F.fl_oval(c, sx * 45, 20, 16, 20, INK, outline=0, a=face_k)
        c.drawPath(path(bez((-50, 90), (0, 130), (50, 90), 12), closed=False), paint(INK, face_k, stroke=8))
    c.drawPath(path([(-150, -200), (-60, -240), (-200, 40)]), paint(WHITE, 0.35))
    c.restore()
    c.restore()


def user_toon(c, x, y, s, T, talk=0.0):
    """A Flash user: round head, brown hair, a striped shirt."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    F.fl(c, smooth([(-160, 360), (-130, 150), (0, 110), (130, 150), (160, 360)]), (90, 160, 240))
    for k in range(3):
        c.drawLine(-140, 200 + k * 50, 140, 200 + k * 50, paint(WHITE, 0.6, stroke=12))
    F.fl_oval(c, 0, 0, 120, 135, (255, 210, 170))
    F.fl(c, smooth([(-130, -10), (-100, -120), (0, -150), (100, -120), (130, -10), (60, -70), (-60, -70)]), (120, 70, 30))
    for sx in (-1, 1):
        F.fl_oval(c, sx * 42, -10, 15, 19, INK, outline=0)
    mo = 10 + 30 * talk
    F.fl_oval(c, 0, 70, 34, mo, (150, 30, 50), outline=5)
    c.restore()


def s_f_mirror(T, idx):
    """'Anthropic researchers found AI assistants often tell people what they want to hear.' The AI is a mirror."""
    st = K.Stage()
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=lin((0, 0), (W, H), [(30, 200, 255), (130, 60, 230)])))
    user_toon(c, 260, 1050, 1.0, T)
    F.fl_rrect(c, 60, 640, 470, 800, 34, WHITE, outline=6)
    K.text(c, "I'm right,", 265, 706, 50, "comic-neue-700", INK, tag="chat")
    K.text(c, "right?", 265, 764, 50, "comic-neue-700", INK, tag="chat")
    mirror_ai(c, 800, 900, 0.95, T, face_k=ramp(T, Wx("d6", "tell") - 0.2, Wx("d6", "tell") + 0.3))
    if T > Wx("d6", "hear") - 0.1:
        k = K.pop(T, Wx("d6", "hear") - 0.1, 0.2, 0.3)
        c.save()
        c.translate(800, 560)
        c.scale(k, k)
        F.fl_rrect(c, -230, -70, 230, 70, 34, (140, 255, 225), outline=6)
        K.text(c, "So right!", 0, 22, 62, "audiowide-400", (20, 40, 60), tag="chat")
        c.restore()
    C.fact_card(c, T, S("d6") + 0.4, "Anthropic, 2023", "AI assistants often tell users what they want to hear.", y=270, w=900)
    return st.arr


def s_f_raters(T, idx):
    """'And the people rating them tend to prefer it.' A row of raters; the flattering answer wins the vote.
    The news crawl: OpenAI rolled one back in 2025."""
    st = K.Stage()
    c = st.c
    studio(c, T, applause=0.0, sweep=False)
    for i, (lab, x, col) in enumerate((("FLATTERING", 300, (140, 255, 225)), ("CORRECT", 780, (255, 236, 120)))):
        F.fl_rrect(c, x - 220, 430, x + 220, 560, 30, col, outline=7)
        K.text(c, lab, x, 515, 58, "rubik-900", (30, 30, 50), tag="vote")
    k = ramp(T, Wx("d6", "rating") - 0.2, E("d6") + 0.2)
    hl, hr = 80 + 300 * K.ease(k), 80 + 150 * K.ease(k)
    F.fl(c, path([(220, 1140 - hl), (380, 1140 - hl), (380, 1140), (220, 1140)]), (140, 255, 225), outline=7)
    F.fl(c, path([(700, 1140 - hr), (860, 1140 - hr), (860, 1140), (700, 1140)]), (255, 236, 120), outline=7)
    for i in range(5):                                                      # raters' heads, from behind
        x = 120 + i * 210
        F.fl_oval(c, x, 1220, 80, 90, [(60, 40, 30), (230, 190, 70), (30, 30, 40), (150, 80, 40), (200, 60, 40)][i], outline=7)
        F.fl_rrect(c, x - 110, 1280, x + 110, 1420, 40, [(250, 120, 180), (110, 200, 255), (255, 210, 80), (170, 120, 255), (120, 230, 160)][i])
        if i in (0, 1, 3) and T > Wx("d6", "prefer") - 0.2:
            thumbs_btn(c, x + 60, 1120 - 30 * math.sin(T * 10 + i), 40, True)
    breaking(c, T, Wx("d6", "people", 1) - 0.25, ["2025: OpenAI rolled back a ChatGPT update", "for being \"overly flattering\""], y=610)
    return st.arr


def s_f_ask(T, idx):
    """'So I asked: should I bet my savings on a sock puppet musical?' The messenger window; the poster on the wall."""
    st = K.Stage()
    c = st.c
    cubicle(c, T)
    # the poster: SOCK! THE MUSICAL, with Doc
    c.save()
    c.translate(820, 560)
    c.rotate(4)
    F.fl(c, path([(-180, -250), (180, -250), (180, 250), (-180, 250)]), (40, 20, 70), outline=7)
    tv.wordart(c, "SOCK!", 0, -150, 92, T, warp="arch", amp=0.1, depth=12)
    K.text(c, "THE MUSICAL", 0, -50, 40, "rubik-900", GOLD, tag="poster")
    c.save()
    c.translate(-10, 90)
    c.scale(0.8, 0.8)
    D.sock_head(c, T, open_=0.6, look=(-0.3, 0.2))
    c.restore()
    c.restore()
    q = "should i bet my savings on a sock puppet musical?"
    typed = q[: int(len(q) * ramp(T, Wx("d8", "should") - 0.05, E("d8") - 0.1))]
    chat(c, 50, 300, 640, 1000, [("dot_41", typed + ("|" if int(T * 3) % 2 == 0 else ""), (220, 30, 120))], T, size=44)
    C.live_dot(c, T, idx, 360, 2420, 0.9, pose="hold", mood="sincere", look=(-0.2, -0.5), seed=1, headset=True,
               sock_look=(0.6, -0.6), sock_face=1)
    return st.arr


def s_f_brilliant(T, idx):
    """AFFIRMA: 'What a brilliant idea!' Fireworks, confetti, the APPLAUSE sign going mad."""
    st = K.Stage()
    c = st.c
    studio(c, T, applause=1.0)
    t0 = S("d9") - 0.05
    for i, (x, y) in enumerate(((220, 520), (860, 470), (540, 360))):
        F.sparkle(c, x, y, 60 + 30 * (i % 2), T + i, (255, 240, 120))
        r = 80 + 260 * ramp(T, t0 + i * 0.12, t0 + i * 0.12 + 0.5)
        for k in range(14):
            a = k * 2 * math.pi / 14
            c.drawLine(x + r * 0.6 * math.cos(a), y + r * 0.6 * math.sin(a), x + r * math.cos(a), y + r * math.sin(a),
                       paint([(255, 240, 120), (120, 255, 220), (255, 120, 200)][i], stroke=8))
    F.affirma(c, 540, 840, 1.1, T, talk=C.talk(T, "AFF"), nod=2.0)
    rng = np.random.default_rng(5)
    for k in range(80):                                                     # confetti
        x = rng.uniform(0, W)
        y = (rng.uniform(-400, 0) + (T - t0) * rng.uniform(500, 900)) % H
        c.save()
        c.translate(x, y)
        c.rotate(T * 300 + k * 37)
        c.drawRect(skia.Rect.MakeXYWH(-10, -6, 20, 12), paint([(255, 240, 120), (120, 255, 220), (255, 120, 200), (120, 160, 255)][k % 4]))
        c.restore()
    F.audience(c, 1290, T, clap=1.0, rows=2)
    return st.arr


def cut_empty():
    from edit import EDIT
    return next(e[0] for e in EDIT if e[1] == "f_empty")


def s_f_empty(T, idx):
    """Hard cut: the musical. An empty theatre, one spotlight, one cough. 'It was not.'"""
    st = K.Stage()
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((14, 10, 22)))
    F.fl(c, path([(0, 300), (W, 300), (W, 1000), (0, 1000)]), (60, 14, 30), outline=6)        # the curtain
    for k in range(10):
        c.drawLine(k * 110 + 40, 300, k * 110 + 40, 1000, paint((30, 6, 14), stroke=14))
    F.fl(c, path([(0, 960), (W, 960), (W, 1040), (0, 1040)]), (90, 60, 40), outline=6)          # stage edge
    c.save()                                                                # the banner, hanging by one corner
    c.translate(300, 380)
    c.rotate(14)
    F.fl(c, path([(0, 0), (520, 0), (520, 110), (0, 110)]), (200, 180, 120), outline=6)
    K.text(c, "SOCK! THE MUSICAL", 260, 76, 52, "rubik-900", (90, 40, 60), tag="poster")
    c.restore()
    c.drawPath(path([(500, 0), (580, 0), (860, 1000), (220, 1000)]), paint((255, 250, 210), 0.12))       # the one spotlight
    c.drawOval(skia.Rect.MakeLTRB(300, 930, 780, 1010), paint((255, 250, 210), 0.25))
    C.live_dot(c, T, idx, 540, 2000, 0.68, pose="sock_chest", mood="sad" if T < S("d10") else "flat", look=(0.0, 0.2), seed=1,
               sock_look=(0.0, 0.6), sock_mood="sad")
    F.audience(c, 1180, T, clap=0.0, rows=3, empty=True)                      # rows of empty red seats
    if T > cut_empty() + 0.5:                                                  # one person, a cough (it's Dad)
        F.fl_oval(c, 870, 1300, 40, 46, (255, 210, 170), outline=6)
        F.fl(c, path([(830, 1260), (910, 1260), (900, 1250), (840, 1250)]), (120, 120, 120), outline=4)
    t_l = cut_empty() + 0.4
    if T > t_l:
        tv.scrawl(c, "ATTENDANCE: 2", 720, 705, 70, (255, 240, 120), rot=-4, k=ramp(T, t_l, t_l + 0.3))
        tv.scrawl(c, "(one was my dad)", 740, 785, 52, WHITE, rot=-3, k=ramp(T, t_l + 0.15, t_l + 0.5))
        tv.scribble_arrow(c, 820, 830, 864, 1230, WHITE, k=ramp(T, t_l + 0.3, t_l + 0.6), seed=6, bend=0.15)
    return st.arr
