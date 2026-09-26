"""Write build/transcript.txt: timed narration, on-screen captions, sound cues and the shot list, for review."""
import os

from cues import C
from script import LINES
from timeline import TL

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    import shots
    out = ["NARRATION (start-end, key, caption text)"]
    for key, spoken, cap, gap, opts in LINES:
        voice = opts.get("voice", "af_heart")
        out.append(f"{TL.s(key):7.2f}-{TL.e(key):7.2f}  [{key}] {cap or spoken}" + ("" if voice == "af_heart" else f"   (voice: {voice}, processed)"))
    out += ["", "CAPTION CHUNKS ON SCREEN"]
    for t0, t1, text, key in shots.CAPS:
        if t0 < C["end_card"]:
            out.append(f"{t0:7.2f}-{t1:7.2f}  {text}")
    out += ["", "SOUND CUES"]
    for k, v in C.items():
        out.append(f"  {k}: " + (", ".join(f"{x:.2f}" for x in v) if isinstance(v, list) else f"{v:.2f}"))
    out += ["  band silenced: " + ", ".join(f"{a:.2f}-{b:.2f}" for a, b in
                                          ((C["wait_stop"], C["wait"] + 0.6), (C["silence"], C["missing"] - 0.01),
                                           (C["final_silence"], C["end_card"] - 0.01))),
            "", "SHOTS (start-end, shot, art style)"]
    for a, b, fn in shots.SHOTS:
        out.append(f"{a:7.2f}-{b:7.2f}  {fn.__name__:12s} {shots.STYLE_OF.get(fn, 'print')}")
    Wd = TL.word
    out += ["", "HARD CUTS INSIDE SHOTS",
            f"{Wd('g2', 'GPT-4') - 0.1:7.2f}  s_score: yardstick (well-educated adult, 10 abilities) -> bar chart",
            f"{Wd('c5', 'And') - 0.1:7.2f}  s_c5: consciousness checklist -> conscious-o-meter",
            f"{Wd('m4', 'The') - 0.05:7.2f}  s_m4: ten-year road -> METR time-horizon chart",
            f"{C['finale']:7.2f}  s_finale: re-cuts of earlier shots every 4 frames (light shots only, no inversions)"]
    out += ["", "BIG-FACE INSERTS"]
    for a, b, fn in shots.INSERTS:
        out.append(f"{a:7.2f}-{b:7.2f}  {fn.__name__}")
    out.append(f"\nTOTAL {TL.total:.2f} s")
    path = os.path.join(HERE, "build", "transcript.txt")
    open(path, "w").write("\n".join(out) + "\n")
    print(path)


if __name__ == "__main__":
    main()
