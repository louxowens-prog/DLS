"""Render the picture in parallel chunks, then mux with the soundtrack.

python3 render.py            -> build/final.mp4 (master) and build/reels.mp4 (smaller)
python3 render.py --scale .5 -> quick half-resolution proof
"""
import argparse
import math
import os
import subprocess
import sys
import time
from multiprocessing import Process

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")


def work(k, a, b, scale, out):
    os.environ["OMP_NUM_THREADS"] = "1"
    from PIL import Image
    import mg as G
    from shots import render_frame
    from timeline import FPS
    w, h = int(G.W * scale) // 2 * 2, int(G.H * scale) // 2 * 2
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "10", "-pix_fmt", "yuv420p",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(a, b):
        fr = render_frame(i / FPS, idx=i)[..., :3]
        if scale != 1.0:
            fr = np.asarray(Image.fromarray(fr).resize((w, h), Image.BILINEAR))
        p.stdin.write(np.ascontiguousarray(fr).tobytes())
        if (i - a) % 120 == 0:
            print(f"[w{k}] {i - a}/{b - a} frames, {time.time() - t0:.0f}s", flush=True)
    p.stdin.close()
    p.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    args = ap.parse_args()
    sys.path.insert(0, HERE)
    from timeline import FPS, TL
    os.makedirs(os.path.join(BUILD, "chunks"), exist_ok=True)
    end = args.end if args.end is not None else TL.total
    f0, f1 = int(args.start * FPS), int(math.ceil(end * FPS))
    n = f1 - f0
    # interleave the heavy and light shots by giving each worker several smaller chunks
    nch = args.workers * 3
    bounds = [f0 + round(n * i / nch) for i in range(nch + 1)]
    parts = [os.path.join(BUILD, "chunks", f"part_{i:02d}.mp4") for i in range(nch)]
    t0 = time.time()
    jobs = list(range(nch))
    running = []
    while jobs or running:
        while jobs and len(running) < args.workers:
            i = jobs.pop(0)
            pr = Process(target=work, args=(i, bounds[i], bounds[i + 1], args.scale, parts[i]))
            pr.start()
            running.append(pr)
        for pr in running[:]:
            if not pr.is_alive():
                pr.join()
                running.remove(pr)
        time.sleep(0.5)
    print(f"frames done in {time.time() - t0:.0f}s", flush=True)
    lst = os.path.join(BUILD, "chunks", "list.txt")
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    video = os.path.join(BUILD, "video.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video], check=True)
    audio = os.path.join(BUILD, "audio.wav")
    tag = "" if args.scale == 1.0 else "_proof"
    master = os.path.join(BUILD, f"final{tag}.mp4")
    af = "loudnorm=I=-14:TP=-1.5:LRA=11"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-ss", str(args.start), "-i", audio, "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-pix_fmt", "yuv420p",
                    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
                    "-r", str(FPS), "-af", af, "-ar", "48000", "-c:a", "aac", "-b:a", "256k", "-shortest",
                    "-movflags", "+faststart", master], check=True)
    print("wrote", master, os.path.getsize(master) / 1e6, "MB", flush=True)


if __name__ == "__main__":
    main()
