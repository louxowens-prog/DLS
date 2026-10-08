"""Captions over the finished print: the narrator in warm ivory, the Curator in pale gold, the machine in ice blue,
Nadia in pale rose. Whole phrases, low and left of centre, clear of the Reels buttons and caption bar, with a dark halo
so they read over the white room and the jewel-toned dream alike."""
import numpy as np
import skia

import kit as K
from kit import paint
from timeline import TL

CAP_SIZE, MAX_W, CX, BASE = 54, 830, 520, 1500
COLORS = {"NAR": (255, 246, 232), "CURATOR": (255, 214, 130), "SYSTEM": (190, 232, 255), "NADIA": (255, 210, 216)}


def _caps():
    from edit import EDIT
    cuts = [e[0] for e in EDIT]
    out = []
    for t0, t1, s, k in TL.captions():
        end = TL.lines[k]["end"]
        nxt = [x for x in cuts if end - 0.05 < x < t1]
        out.append((t0, min([t1] + nxt), s, k))
    return out


CAPS = _caps()


def _scrim(arr, box, col):
    """How much dark backing a caption needs: none over the dark, more where the picture behind it is as bright as
    the lettering (gold captions over gold, ivory over the white room)."""
    x0, y0, x1, y1 = (int(max(0, box[0])), int(max(0, box[1])), int(min(arr.shape[1], box[2])), int(min(arr.shape[0], box[3])))
    if x1 <= x0 or y1 <= y0:
        return 0.0
    reg = arr[y0:y1:3, x0:x1:3, :3].astype(np.float32) / 255
    lum = reg[..., 0] * 0.2126 + reg[..., 1] * 0.7152 + reg[..., 2] * 0.0722
    capl = (col[0] * 0.2126 + col[1] * 0.7152 + col[2] * 0.0722) / 255
    close = float(np.mean(lum > capl - 0.42))
    u = min(1.0, max(0.0, (close - 0.04) / 0.18))
    return 0.8 * u * u * (3 - 2 * u)


def caption(c, s, who, a, arr=None):
    f = K.font("jost-600", CAP_SIZE)
    lines = K.wrap_balanced(s, f, MAX_W)
    lh = CAP_SIZE * 1.2
    y0 = BASE - lh * (len(lines) - 1)
    col = COLORS.get(who, (250, 248, 244))
    wmax = max(f.measureText(ln) for ln in lines)
    box = (CX - wmax / 2 - 34, y0 - CAP_SIZE * 0.95, CX + wmax / 2 + 34, y0 + lh * (len(lines) - 1) + CAP_SIZE * 0.42)
    sa = _scrim(arr, box, col) if arr is not None else 0.0
    if sa > 0.02:                                                   # a soft dark backing, feathered at the edges
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(*box), 26, 26), paint((4, 2, 6), sa * a, blur=16))
    for i, ln in enumerate(lines):
        y = y0 + lh * i
        w = f.measureText(ln)
        x = CX - w / 2
        c.drawString(ln, x + 2, y + 3, f, paint((0, 0, 0), 0.75 * a, blur=6))
        c.drawString(ln, x, y, f, paint((8, 2, 6), 0.95 * a, stroke=8))
        c.drawString(ln, x, y, f, paint(col, a))
        K.reg(x, y - CAP_SIZE * 0.78, x + w, y + CAP_SIZE * 0.24, "caption")


def overlay(arr, T):
    cap = next((cp for cp in reversed(CAPS) if cp[0] <= T < cp[1]), None)      # the newest card wins a handover
    if not cap:
        return
    t0, t1, s, key = cap
    a = min(1.0, (T - t0) / 0.08, max(0.0, (t1 - T) / 0.06))
    st = skia.Surface(arr)
    caption(st.getCanvas(), s, TL.lines[key]["who"], a, arr)
