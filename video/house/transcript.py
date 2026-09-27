"""Write build/transcript.txt for review: lines, captions, the edit with transition types, and where each device happens."""
import os

from cues import C, count
from edit import EDIT, first
from script import LINES
from timeline import TL

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    import shots
    W = TL.word
    out = ["LINES (start-end, key, speaker, text). Narrator = af_heart (calm, diary-like); AI = af_nicole (a sugary whisper",
           "with an echo; its words appear on screen as small silent-film intertitle cards); DOC = am_michael"]
    for key, who, spoken, cap, gap in LINES:
        out.append(f"{TL.s(key):7.2f}-{TL.e(key):7.2f}  [{key}] {who:3s} {TL.lines[key]['caption']}")
    out += ["", "CAPTIONS (torn pastel paper strips pasted on; bone-white with red type in the horror shots)"]
    for t0, t1, text, key in shots.CAPS:
        out.append(f"{t0:7.2f}-{t1:7.2f}  {text}")
    out += ["", "EDIT (start, length, shot, transition in): iris = silent-film iris out/in; flip = scrapbook page turn;",
            "card = silent-film title card; cut = hard cut on a hit"]
    for i, (t, n, tr) in enumerate(EDIT):
        nx = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total
        out.append(f"{t:7.2f}  {nx - t:5.2f}s  {n:11s} {tr}")
    f = first
    out += ["", "WHERE THE DEVICES ARE",
            "  PAINTED SKIES / WINDOWS: every set (parlour, kitchen, courtroom, bedroom, street) looks out on a garish painted sunset;",
            f"           full painted skies at {f('title'):.1f}, {f('sure'):.1f}, {f('machine'):.1f}, {f('always'):.1f}, {f('plane'):.1f}, {f('clones'):.1f}, {f('three'):.1f}",
            "  FAKE COMPOSITING: every figure is a paper cut-out with a white scissor edge, a drop shadow and a green-blue matte",
            "           fringe on one side; floating heads: the chatbot throughout, the neighbour 71-73 s, the visions 73-75 s",
            f"  HAND-DRAWN ANIMATION: sparkles (hook, title, halo, album), flames ({f('eaten'):.1f}, {f('visions'):.1f}, {f('doctor') + 2:.1f}, {f('burn'):.1f}, {f('count'):.1f}),",
            f"           scribbles ({W('p2', 'salt'):.1f}, {f('ticket') + 1.0:.1f}, {f('visions'):.1f}, {W('s4', 'wrong,'):.1f})",
            "  SOFT FOCUS (sweet) vs HARD RED (horror): sweet = glow + bloom; red shots = " + ", ".join(
                f"{t:.1f}" for t, n, _ in EDIT if n in shots.HORROR),
            "  1970s FILM: grain, halation, dust, hairs, scratches, vignette, gate weave and flicker on every frame",
            f"  WRONG MOTION: stop-motion puppets (new position 8x a second, jittered) throughout; sped-up: parcel {f('parcel'):.1f},",
            f"           calendar {f('calendar'):.1f}, filings {f('pile'):.1f}, envelopes {f('globe'):.1f}, counter {f('counter'):.1f};",
            f"           reverse motion: the visions' heads fly back {C['hear']:.1f}, plasters fly back onto the wall {f('crack'):.1f};",
            f"           freeze frames: {f('grade'):.1f}, {f('nowarning'):.1f}, {f('casezoom'):.1f}",
            f"  EDITING: iris at " + ", ".join(f"{t:.1f}" for t, n, tr in EDIT if tr == "iris") +
            f"; split screens {f('sure'):.1f} and {f('ask'):.1f}; album inserts {f('album1'):.1f}-{f('machine'):.1f},",
            f"           {f('brief'):.1f}, {f('casefile'):.1f}; title cards {f('fine'):.1f}, {f('realcase'):.1f}, {f('end'):.1f}",
            f"  TONE WHIPLASH: sweet parcel/sparkles {f('parcel'):.1f} right after the silence; the 'A REAL CASE' card and music box",
            f"           after the ward; cheerful sting on the title straight after the study burns",
            f"  THE CAT: watches in the parlour, album, kitchen; eyes glow red when the chatbot says something false:",
            f"           {C['eaten']:.1f}, {W('w1', 'isn') + 0.1:.1f}, {f('brief') + 0.8:.1f}, {f('cateyes'):.1f}, {f('neighbor'):.1f}, payoff",
            f"  THE CLOCK (motif): hangs in the parlour from frame 1, its counter running at an illustrative ~289/s (one in a",
            f"           hundred of ~2.5 billion messages a day); explained at {C['clock']:.1f}; pays off at {f('payoff'):.1f}-{f('trust'):.1f}",
            f"           when it reads ~{count(f('count')):,.0f}-{count(f('trust')):,.0f} as the narrator says 'about {TL.count_said:,}'",
            f"\nTOTAL {TL.total:.2f} s"]
    path = os.path.join(HERE, "build", "transcript.txt")
    open(path, "w").write("\n".join(out) + "\n")
    print(path)


if __name__ == "__main__":
    main()
