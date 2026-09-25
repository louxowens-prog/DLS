"""Render one shot's frames: python3 render_shots.py <set> <fps> <seconds> <u0> <u1> <outdir> [samples]"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import sets
name, fps, secs, u0, u1, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
samples = int(sys.argv[7]) if len(sys.argv) > 7 else None
os.makedirs(out, exist_ok=True)
anim = sets.BUILDERS[name]()
if samples:
    bpy.context.scene.cycles.samples = samples
n = max(2, int(round(secs * fps)))
meta = {"fps": fps, "frames": n, "screens": []}
t0 = time.time()
for i in range(n):
    path = os.path.join(out, f"{i:05d}.png")
    anim(u0 + (u1 - u0) * i / (n - 1))
    meta["screens"].append(sets.screen_corners())
    if not os.path.exists(path):
        sets.render_frame(path)
    if i % 10 == 0:
        el = time.time() - t0
        print(f"{name} {i + 1}/{n}  {el / (i + 1):.1f}s/f  eta {el / (i + 1) * (n - i - 1) / 60:.1f} min", flush=True)
json.dump(meta, open(os.path.join(out, "meta.json"), "w"))
print(f"{name} DONE in {(time.time() - t0) / 60:.1f} min", flush=True)
