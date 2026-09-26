"""Write build/transcript.txt for review: lines (who says what, when), captions, the edit with transition types,
and where each comic device happens."""
import os

from cues import C
from edit import EDIT
from script import LINES, VOICES
from timeline import TL

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    import shots
    out = ["LINES (start-end, key, speaker, text). Narrator = af_heart; BOT (the AI, a flat cartoon) = am_puck, ring-modulated;",
           "NOIR (black-and-white skeptic) = am_fenrir through an old-radio band; ANIME (cel-shaded believer) = af_bella"]
    for key, who, spoken, cap, gap in LINES:
        out.append(f"{TL.s(key):7.2f}-{TL.e(key):7.2f}  [{key}] {who:5s} {cap or spoken}")
    out += ["", "NARRATION CAPTIONS (yellow comic narration boxes; character lines are in speech bubbles instead)"]
    for t0, t1, text, key in shots.CAPS:
        out.append(f"{t0:7.2f}-{t1:7.2f}  {text}")
    out += ["", "EDIT (start, length, shot, transition in): glitch = dimensional tear (RGB split, slices, shards, flicker),",
            "slide = new panel slides over with an ink edge + gutter, impact = 2 flat-colour frames with focus lines"]
    for i, (t, n, tr) in enumerate(EDIT):
        nx = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total
        out.append(f"{t:7.2f}  {nx - t:5.2f}s  {n:9s} {tr}")
    out += ["", "WHERE THE DEVICES ARE",
            "  ON TWOS: every character (narrator, AI, noir, anime) is drawn at 12 drawings/s (each drawing held 2 frames at 24 fps),",
            "           while camera moves (pans on the wall, push-ins, page scrolls) run on ones. Walk cycle: road 10.2-20.3 s.",
            f"  IMPACT FRAMES (flat colour + ink focus lines + silhouette): {C['gold']:.2f} (POW), {C['brain']:.2f} (BOOM), {C['boom']:.2f} (BOOM),",
            f"           plus impact transitions at {EDIT[1][0]:.2f} and {EDIT[10][0]:.2f}",
            f"  SPIDER-SENSE squiggles: {C['pin']:.2f} (you are here), {C['neither']:.2f} (Neither), {TL.word('a7', 'intelligence'):.2f} (one brain per person),"
            f" {C['general']:.2f} (generalization)",
            f"  SMEARS / MULTIPLES: can shake {C['shake']:.2f} (multiples), point whip ~{C['shake'] + 0.55:.2f} (smear), skateboard bot {C['speed'] - 0.3:.2f}"
            f" (multiples), anime fist pump {TL.s('d2'):.2f} (smear), bot drop {C['new'] - 0.3:.2f} (smear), bot spin {TL.word('a1', 'gets'):.2f} (multiples),"
            f" days/nights {TL.s('a2'):.2f} (sun multiples)",
            f"  RECORD SCRATCH FREEZES (SKRRT, beat backspins out): {C['scratch1']:.2f}, {C['scratch2']:.2f}",
            "  STYLE CLASH (4 styles in one frame): 56.8-67.4 s (noir B&W panel, anime panel, main-style narrator, flat-cartoon AI)",
            "  MISREGISTRATION (cyan/magenta plates off register on out-of-focus planes): every night-city background (far 11 px, mid 5 px)",
            "  HALFTONE (dots >= 8 px, pitch 14-20 px) and HATCHING: skies, walls, hoodie, faces, panels, sound-word letters",
            f"\nTOTAL {TL.total:.2f} s"]
    path = os.path.join(HERE, "build", "transcript.txt")
    open(path, "w").write("\n".join(out) + "\n")
    print(path)


if __name__ == "__main__":
    main()
