"""Cue sheet shared by the soundtrack and the picture, derived from the narration timeline."""
from timeline import TL

C = {}
C["fanfare"] = TL.e("open") + 0.15            # trumpets: C - G - C
C["title"] = C["fanfare"] + 4.35              # tutti C major: title card
C["int1"] = C["fanfare"] + 5.45               # "THE DAWN OF MIND"
C["monolith"] = TL.s("drive") - 0.1
C["silence"] = TL.s("nothing") - 0.03          # choir cut off dead, as in the film
C["child"] = TL.s("child") - 0.25
C["figure"] = TL.word("child", "figures")     # the tool moment: the fanfare motif returns
C["bone"] = TL.e("child") + 0.12
C["cut"] = C["bone"] + 1.55                   # match cut: bone -> orbiting spacecraft, into silence
C["int2"] = TL.s("artif") - 0.55
C["heart"] = TL.word("light", "An")
C["alphago"] = TL.word("chess", "AlphaGo")
C["int3"] = TL.s("myth") - 1.0
C["int4"] = TL.s("token") - 1.0
C["sun"] = TL.word("nudge", "Sun")
C["stargate"] = TL.s("llama") - 0.25
C["stargate_end"] = TL.e("llama") + 0.15
C["shatter"] = TL.e("glass") + 0.18
C["int5"] = TL.s("just") - 1.0
C["texas"] = TL.word("dallas", "Texas")
C["austin"] = TL.word("dallas", "Austin")
C["dallas"] = TL.word("dallas", "Dallas")
C["close"] = TL.s("close1") - 0.5
C["fanfare2"] = TL.e("close2") + 0.25
C["end_title"] = C["fanfare2"] + 4.35
C["end"] = TL.total
