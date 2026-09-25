"""Cue sheet shared by the soundtrack and the picture, derived from the narration timeline."""
from timeline import TL

C = {}
C["chat"] = TL.word("open", "any")               # HAL -> a model streaming text
C["title"] = TL.e("open") + 2.45                  # tutti C major: title card
C["fanfare"] = C["title"] - 2.4                   # compressed fanfare starts as the voice ends
C["align"] = C["fanfare"]                         # the Moon-Earth-Sun alignment rises with the trumpets
C["ch1"] = TL.s("defs") - 0.1
C["monolith"] = TL.s("drive") - 0.1
C["silence"] = TL.e("rock") + 0.7                # choir swells, then is cut off dead, as in the film
C["child"] = TL.s("child") - 0.25
C["figure"] = TL.word("child", "figures")        # the tool moment: the fanfare motif returns
C["bone"] = TL.e("child") + 0.1
C["cut"] = C["bone"] + 1.3                       # match cut: bone -> orbiting satellite, into silence
C["ch2"] = TL.s("artif") + 0.1
C["heart"] = TL.word("light", "An")
C["alphago"] = TL.word("chess", "AlphaGo")
C["ch3"] = TL.s("myth") - 0.3
C["ch4"] = TL.s("token") - 0.3
C["sun"] = TL.word("nudge", "Sun")
C["stargate"] = TL.e("tilt2") + 0.12
C["stargate_end"] = TL.e("llama") + 0.12
C["shatter"] = TL.e("glass") + 0.15
C["ch5"] = TL.s("just") - 0.25
C["texas"] = TL.word("dallas", "Texas")
C["austin"] = TL.word("dallas", "Austin")
C["dallas"] = TL.word("dallas", "Dallas")
C["close"] = TL.s("close1") - 0.3
C["end_title"] = TL.e("close2") + 2.45           # final tutti + end card, after a short fanfare
C["fanfare2"] = C["end_title"] - 2.4
C["end"] = TL.total
CHAPTERS = [("THE DAWN OF MIND", "I", C["ch1"]), ("BUILT, NOT BORN", "II", C["ch2"]),
            ("INSIDE THE MACHINE", "III", C["ch3"]), ("THE PREDICTION MISSION", "IV", C["ch4"]),
            ("BEYOND THE NEXT WORD", "V", C["ch5"])]
