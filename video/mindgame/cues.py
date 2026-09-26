"""Cue sheet shared by the soundtrack and the picture."""
from timeline import TL

C = {}
C["half"] = TL.word("h2", "half")
C["title"] = TL.word("h3", "jagged")
C["stamps"] = [TL.word("l2", "Yes", 0), TL.word("l2", "Yes", 1), TL.word("l3", "Disputed"), TL.word("l3", "Not"),
               TL.word("l4", "No.", 0), TL.word("l4", "evidence") - 0.25]
C["clock"] = TL.word("h1", "clock")
C["separate"] = TL.word("l4", "separate")
C["wait"] = TL.s("g1")
C["wait_stop"] = TL.s("g1") - 0.45
C["notif"] = TL.word("g4", "A.G.I.")
C["water"] = TL.s("g5")
C["montage"] = [a for w, a, b in TL.lines["g6"]["words"]]
C["silence"] = TL.s("c1") - 0.85
C["frightened"] = TL.s("c3j")
C["octopus"] = TL.word("c4", "octopus")
C["missing"] = TL.s("m0") - 0.3
C["items"] = [TL.s(k) for k in ("m1", "m2", "m3", "m4", "m5", "m6")]
C["finale"] = TL.e("m6") + 0.3
C["final_silence"] = TL.s("f2") - 0.6
C["end_card"] = TL.e("f2") + 0.35
C["end"] = TL.total
