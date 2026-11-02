"""Shared by the shots: the stage with its hand-tint layer, the camera, the Emcee's cameo, captions-free zones."""
import math

import numpy as np
import skia

import draw as D
from draw import H, W, ease, ramp


class ZStage(D.Stage):
    """A frame, plus a transparent layer for hand-painted colour (film80 lays it on after the black and white)."""

    def __init__(self, bg=(0, 0, 0)):
        super().__init__(bg)
        self.tint_arr = np.zeros((H, W, 4), np.uint8)
        self.ts = skia.Surface(self.tint_arr)
        self.t = self.ts.getCanvas()


def cam(c, z, cx=540, cy=960, dx=0.0, dy=0.0):
    c.translate(cx + dx, cy + dy)
    c.scale(z, z)
    c.translate(-cx, -cy)


def cams(st, z, cx=540, cy=960, dx=0.0, dy=0.0):
    """The same camera on the picture and on its tint layer."""
    for c in (st.c, st.t):
        cam(c, z, cx, cy, dx, dy)


def save(st):
    st.c.save()
    st.t.save()


def restore(st):
    st.c.restore()
    st.t.restore()


def beat(T, bpm, phase=0.0):
    """0..1 saw on the beat (for bounces)."""
    return ((T * bpm / 60.0) + phase) % 1.0
