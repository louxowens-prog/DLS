"""Write build/transcript.txt: every line, the captions, the edit with registers and transitions, and where each
device of the brief is."""
import os

import ov
from audio import SILENCES
from cues import CARDS, USE_TAGS, WHO_TAGS, C, CLOCKS
from edit import EDIT, first
from script import CHAPTERS
from timeline import TL

HERE = os.path.dirname(os.path.abspath(__file__))
S, E = TL.s, TL.e


def main():
    f = first
    out = ["A LIGHT FOR EVERY DESK - 'Education' (AI tutoring) as a life in four chapters, in the style of a 1985 art film "
           "(style only: no people, names, music, cards or set designs from the film)", ""]
    out += ["LINES (start-end, speaker, text)"]
    for k in TL.order:
        L = TL.lines[k]
        out.append(f"{L['start']:7.2f}-{L['end']:7.2f}  {L['who']:8s} {L['spoken']}")
    out += ["", "CAPTIONS (none for the four aphorisms, which are written large in the picture, nor for the clock times "
                "and the typed prompts, which are on screen)"]
    for t0, t1, text, key in ov.CAPS:
        if key not in ov.NO_CAPTION:
            out.append(f"{t0:7.2f}-{t1:7.2f}  {text}")
    out += ["", "EDIT (start, length, shot, register, transition in). Registers: present = muted colour; memory = black "
                "and white; fiction = lacquer stage colour; card = chapter card. Transitions: cut; fade = to/from black."]
    for i, (t, n, reg, tr) in enumerate(EDIT):
        nx = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total
        out.append(f"{t:7.2f}  {nx - t:5.2f}s  {n:14s} {reg:8s} {tr}")
    out += ["", "WHERE THE DEVICES ARE",
            "  FOUR CHAPTERS, each opened by a title card (white serif on black, the word in Japanese in vertical script): " +
            "; ".join(f"{c[0]} {c[1]} {c[2]} at {c[3]:.1f}" for c in CARDS),
            f"  THREE REGISTERS: PRESENT (muted colour, countdown clock top left: {', '.join(s for t, s in CLOCKS)}) - the "
            f"real-life scenario, literally; MEMORY (black and white: the classroom of 38 {f('class'):.1f}, the bell, "
            f"the tutor's window {f('window'):.1f}, the old test {f('old_test'):.1f}, the teacher at night "
            f"{f('teacher_night'):.1f}, the back row {f('back_row'):.1f}); FICTION (lacquer stage tableaux: the prince "
            f"and his tutor {f('prince'):.1f}, the car and the dials {f('car'):.1f}, the answer box {f('box'):.1f}, "
            f"the study {f('study'):.1f}, Harvard {f('harvard'):.1f}, the paper cranes {f('cranes'):.1f}, the lamps "
            f"{f('lamps'):.1f}, the languages {f('language'):.1f}, Nigeria {f('nigeria'):.1f})",
            f"  SETS THAT SPLIT, SLIDE OR TURN: the tutoring stage splits in two {C['split98']:.1f}; the car set turns on a "
            f"turntable {C['turn']:.1f}; the chatbot bars slide away to reveal 'hints, not answers' {C['hints']:.1f}; "
            f"sliding screens open on six languages {S('e3') + 4.5:.1f}",
            f"  THE RECURRING OBJECT: the lamp - her desk lamp clicks on {C['lamp_on']:.1f}; one bulb for 38 pupils "
            f"{f('class'):.1f}; the tutor's lamp across the street {f('window'):.1f}; the stage lantern over one desk "
            f"{f('aph1'):.1f}, {f('aph2'):.1f}; lanterns over each learner {f('lamps'):.1f}; the pay-off, a lantern over "
            f"every desk {f('final'):.1f}",
            f"  THE COUNTDOWN CONVERGES: 21:40 -> 09:00 (the exam {f('exam'):.1f}); in the last image the three registers "
            f"merge: the black-and-white classroom, the pale present, the gold lanterns of the stage, her in the back "
            f"row {f('final'):.1f}",
            "  THE THIRTEEN USES, stamped as they happen ('n / 13'): " +
            "; ".join(f"{u[2]} {u[3]} {u[0]:.1f}" for u in USE_TAGS),
            "  WHO IT HELPS MOST: " + "; ".join(f"{u[3]} {u[0]:.1f}" for u in WHO_TAGS) +
            "; unusual schedules and gaps in schooling are her own story (left school at 16, works shifts)",
            "  APHORISMS (her notebook, written in italic serif and spoken): 'Attention was the most expensive thing in "
            "the room.'; 'For the first time, the whole lesson was mine.'; 'Time to finally see the back row.'; "
            "'A light for every desk.'",
            "  SILENCES (every bus cut): " + "; ".join(f"{a:.1f}-{b:.1f}" for a, b in SILENCES) +
            " - the last one right before the final image",
            "  SOUND: minimalist ostinato (arpeggios in 3+3+2 eighths, pulsing viola, cello, a triplet line against the "
            "duple pulse) growing from a thin pulse to full orchestra with brass, timpani and harp on the stage; present "
            "= room tone, rain, clock, lamp switch, typing, pencil; memory = solo piano, far classroom murmur, chalk, the "
            "school bell; fiction = full ostinato, wooden clappers when sets change; a temple bell under each chapter card; "
            "a bamboo flute at dawn",
            f"\nTOTAL {TL.total:.2f} s"]
    path = os.path.join(HERE, "build", "transcript.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write("\n".join(out) + "\n")
    print(path)


if __name__ == "__main__":
    main()
