"""Render single frames or contact sheets for review: python3 preview.py name [times...]"""
import os
import sys

import numpy as np
from PIL import Image

import sr as G

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "preview")


def frame_at(T):
    from shots import render_frame
    return render_frame(T)


def sheet(times, path, cols=4, scale=0.3):
    ims = [Image.fromarray(frame_at(T)[..., :3]).resize((int(G.W * scale), int(G.H * scale)), Image.LANCZOS) for T in times]
    w, h = ims[0].size
    rows = -(-len(ims) // cols)
    out = Image.new("RGB", (cols * w + (cols - 1) * 6, rows * h + (rows - 1) * 6), (40, 40, 40))
    for i, im in enumerate(ims):
        out.paste(im, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
    os.makedirs(OUT, exist_ok=True)
    out.save(path)
    return path


if __name__ == "__main__":
    name = sys.argv[1]
    times = [float(x) for x in sys.argv[2:]]
    print(sheet(times, os.path.join(OUT, name + ".jpg")))
