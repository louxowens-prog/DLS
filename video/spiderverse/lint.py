"""Text-collision lint: render sampled frames and report overlapping lettering (captions, bubbles, sound words, labels)."""
import sys
from multiprocessing import Pool

import numpy as np


def check(T):
    import sv
    from shots import lint, render_frame
    render_frame(T)
    return T, lint(list(sv.TEXT))


if __name__ == "__main__":
    from timeline import TL
    step = float(sys.argv[1]) if len(sys.argv) > 1 else 0.25
    ts = list(np.arange(0.0, TL.total, step))
    with Pool(4) as p:
        res = p.map(check, ts)
    n = 0
    for T, bad in res:
        for a, b in bad:
            n += 1
            print(f"{T:7.2f}  {a[4]:>10s} {tuple(int(v) for v in a[:4])}  x  {b[4]:<10s} {tuple(int(v) for v in b[:4])}")
    print(len(ts), "frames checked,", n, "collisions")
