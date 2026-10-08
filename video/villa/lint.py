"""Text lint: render sampled frames and report overlapping lettering and lettering under the Reels UI."""
import sys
from multiprocessing import Pool

import numpy as np


def check(T):
    import kit as K
    from shots import lint, render_frame, ui_zone
    render_frame(T)
    boxes = list(K.TEXT)
    return T, lint(boxes), ui_zone(boxes)


if __name__ == "__main__":
    from timeline import TL
    step = float(sys.argv[1]) if len(sys.argv) > 1 else 0.25
    ts = list(np.arange(0.0, TL.total, step))
    with Pool(int(__import__("os").environ.get("LINT_W", "4"))) as p:
        res = p.map(check, ts)
    n = u = 0
    seen = set()
    for T, bad, ui in res:
        for a, b in bad:
            n += 1
            key = (a[4], b[4], int(T))
            if key not in seen:
                seen.add(key)
                print(f"{T:7.2f}  {a[4]:>10s} {tuple(int(v) for v in a[:4])}  x  {b[4]:<10s} {tuple(int(v) for v in b[:4])}")
        for b in ui:
            u += 1
            key = ("ui", b[4], int(T))
            if key not in seen:
                seen.add(key)
                print(f"{T:7.2f}  UI ZONE  {b[4]:>10s} {tuple(int(v) for v in b[:4])}")
    print(len(ts), "frames checked,", n, "collisions,", u, "in UI zones")
