"""Cue sheet shared by the soundtrack and the picture."""
from timeline import TL

C = {}
W = TL.word
C["go"] = W("a0", "on!")                          # green light: the launch
C["two"] = W("h2", "two")
C["chess_done"] = W("d2", "Done")
C["img_done"] = W("d3", "Done")
_d6 = [a for w, a, b in TL.lines["d6"]["words"]]
C["gauges"] = [_d6[i] for i in (0, 1, 2, 4, 5, 7, 8, 10, 11, 12, 14)]
C["hazards"] = [W("t2", "Six"), W("t2", "vegetarian"), W("t2", "peanuts"), W("t2", "store"), W("t2", "oven"),
                W("t2", "ingredient"), W("t2", "late"), W("t2", "Wine")]
C["loop"] = [W("u2", k) for k in ("Perceive", "Model", "Predict", "Plan", "Act", "Observe", "Learn")]
C["crash"] = [b for w, a, b in TL.lines["v3"]["words"] if w.startswith("crashes")][0] + 0.05
C["expedition"] = W("t4", "organize")
C["joke"] = TL.s("w2")
C["end_card"] = TL.e("f1") + 0.35
C["end"] = TL.total
