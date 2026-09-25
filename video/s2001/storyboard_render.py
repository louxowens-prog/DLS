import sys, time, json, os
sys.path.insert(0, os.path.dirname(__file__))
import sets
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
info = {}
for name in sys.argv[2:]:
    anim = sets.BUILDERS[name]()
    anim(0.55)
    t = time.time()
    sets.render_frame(os.path.join(out, f"{name}.png"))
    info[name] = {"sec": round(time.time() - t, 1), "screens": sets.screen_corners()}
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    so = bpy.data.objects.get("sunball")
    if so:
        p = world_to_camera_view(bpy.context.scene, bpy.context.scene.camera, so.location)
        info[name]["sun"] = (p.x * sets.BAND_W, (1 - p.y) * sets.BAND_H)
    print(name, info[name]["sec"], flush=True)
json.dump(info, open(os.path.join(out, "info.json"), "w"))
