"""Write build/transcript.txt for review: narration, captions, the edit (with transition types), and cues."""
import os

from cues import C
from edit import EDIT
from script import LINES
from timeline import TL

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    import shots
    out = ["NARRATION (start-end, key, caption) — narrator af_heart unless marked; the announcer goes through a stadium PA"]
    for key, spoken, cap, gap, opts in LINES:
        v = opts.get("voice", "af_heart")
        out.append(f"{TL.s(key):7.2f}-{TL.e(key):7.2f}  [{key}] {cap or spoken}" + ("" if v == "af_heart" else "   (ANNOUNCER, am_michael)"))
    out += ["", "CAPTION CHUNKS (lists d6, t2, u2 are shown as on-screen graphics instead)"]
    for t0, t1, text, key in shots.CAPS:
        out.append(f"{t0:7.2f}-{t1:7.2f}  {text}")
    out += ["", "EDIT (start, shot, transition in): head:<who> = head wipe with that character's giant face"]
    for i, (t, n, tr) in enumerate(EDIT):
        nx = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total
        out.append(f"{t:7.2f}  {nx - t:5.2f}s  {n:11s} {tr}")
    out += ["", "SPEED RAMPS (slow motion, then snap):",
            f"  launch at {C['go']:.2f} (0.6 s slow), wine spill at {C['hazards'][7]:.2f} (0.85 s slow), transfer jump in {TL.s('t5'):.2f}-{TL.e('t5'):.2f},"
            f" crash at {C['crash']:.2f} (0.7 s slow, band cut dead)",
            "ANNOUNCER PICTURE-IN-PICTURE: during a0, a1, a2, a3 (lip-synced to his voice)",
            "LAYERED 'POP-UP' DEPTH (huge foreground face, sharp action behind): race, finish, h2h, newtrack",
            f"\nTOTAL {TL.total:.2f} s"]
    path = os.path.join(HERE, "build", "transcript.txt")
    open(path, "w").write("\n".join(out) + "\n")
    print(path)


if __name__ == "__main__":
    main()
