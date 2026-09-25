import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image
import comp
SB = os.path.join(os.path.dirname(__file__), "..", "out", "_2001", "sb")
info = json.load(open(os.path.join(SB, "info.json")))
out = []
def band(name):
    return Image.open(os.path.join(SB, name + ".png"))
# 1 opening
b = comp.over_stars(band("alignment"))
b = comp.glare(b, info.get("alignment", {}).get("sun", (540, 60)), 1.0)
f = comp.frame(b, None, None)
from PIL import ImageDraw
d = ImageDraw.Draw(f)
comp.spaced(d, (540, comp.BAND_Y - 110), "WHAT IS INTELLIGENCE?", 44, (240, 240, 240))
out.append(f)
# 2 centrifuge with displays
b = band("centrifuge").convert("RGB")
words = ["MODEL", "LEARN", "INFER", "ADAPT", "PLAN", "ACT"]
for i, (nm, quad) in enumerate(sorted(info["centrifuge"]["screens"].items())):
    panel = comp.display([words[i % 6]], 640, 420, title=f"FUNCTION {i + 1:02d}")
    comp.warp_into(b, panel, quad)
out.append(comp.frame(b, "I  ·  INTELLIGENCE", "A useful definition: model the world, learn, infer, adapt, plan, act."))
# 3 monolith archive
b = comp.over_stars(band("monolith"))
out.append(comp.frame(b, "I  ·  INTELLIGENCE", "Ask it to lift a rock with three planks, a rope and a broken pulley. Nothing happens."))
# 4 match cut: tool -> station
t1 = band("dawn").convert("RGB")
t2 = comp.over_stars(band("station"))
pair = Image.new("RGB", (comp.BW, comp.BH))
pair.paste(t1.crop((0, 0, 540, 490)), (0, 0)); pair.paste(t2.crop((270, 0, 810, 490)), (540, 0))
ImageDraw.Draw(pair).line([(540, 0), (540, 490)], fill=(255, 255, 255), width=4)
out.append(comp.frame(pair, "II  ·  ARTIFICIAL", "Artificial doesn't mean fake. It means built, not born."))
# 5 memory room + relationship map
b = band("memory").convert("RGB")
panel = comp.display(["FRANCE -> PARIS", "JAPAN -> TOKYO", "ITALY -> ROME", "same direction"], 700, 380,
                     bg=(20, 0, 0), fg=(255, 150, 130), accent=(255, 60, 40), title="LEARNED RELATIONSHIPS")
comp.warp_into(b, panel, [(330, 95), (750, 125), (750, 330), (330, 355)])
out.append(comp.frame(b, "III  ·  NOT A LIBRARY", "No stored copies of its training text. A learned map of relationships."))
# 6 slit-scan star gate
b = comp.slit_scan(3.0, hue=1)
out.append(comp.frame(b, "V  ·  JUST THE NEXT WORD?", "Whether that's real reasoning is still debated. The behavior is there."))
os.makedirs(os.path.join(SB, "final"), exist_ok=True)
for i, f in enumerate(out):
    f.save(os.path.join(SB, "final", f"sb{i + 1}.png"))
sheet = Image.new("RGB", (540 * 3, 960 * 2))
for i, f in enumerate(out):
    sheet.paste(f.resize((540, 960)), ((i % 3) * 540, (i // 3) * 960))
sheet.save(os.path.join(SB, "final", "storyboard_sheet.png"))
print("ok")
