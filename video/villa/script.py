"""THE HOLLOW SCHOLARS - a 1970s Italian gothic nightmare about education going hollow.

Each line: (key, speaker, spoken text, caption or None, seconds of air after it). In a caption a "|" marks where the
caption breaks into a new card. A spoken text "=key" repeats that line's recording exactly (the deja vu loop), and
FX names a treatment for a line (see timeline.FX).

Numbers are spelled the way the voice should say them; captions show them the way a viewer reads them. UNESCO is
spelled "Yoonesko" for the voice so it is said "yoo-NESS-koh", not "un-ESS-koh".
"""

# speaker: (Kokoro voice or blend, speed, pitch shift in semitones)
VOICES = {
    "NAR": ("bf_emma*0.6+af_nicole*0.4", 1.08, 0.0),          # calm, hypnotic, a little breathy
    "CLARA": ("bf_lily*0.5+af_bella*0.5", 1.0, 0.3),          # a young British graduate who thinks she is a tourist
    "GOV": ("af_alloy*0.5+af_kore*0.5", 0.88, -0.8),           # the Governess: low, slow, unfailingly polite
    "INT1": ("bf_isabella", 1.04, -1.2),                        # the interviewer
    "INT2": ("af_sarah*0.6+bf_alice*0.4", 1.04, 0.0),          # her colleague
}

LINES = [
    # ---- the hook: a porcelain graduate, and what is inside
    ("h1", "NAR", "Top marks. A perfect degree. And inside...", None, 0.3),
    ("h2", "NAR", "nothing.", None, 0.0),
    # ---- the square: the automaton clock strikes nine; Clara loses her group
    ("o1", "NAR", "Nine o'clock. The clock strikes, and its little scholars march out for their diplomas.", None, 0.2),
    ("o3", "CLARA", "Hello?", None, 0.35),
    # ---- the labyrinth: the tutor, and the shortcut
    ("l1", "NAR", "AI could be the finest tutor ever built. In one university trial, students with an AI tutor learned twice as much.",
     "AI could be the finest tutor ever built. | In one university trial, students with an AI tutor learned twice as much.", 0.2),
    ("l2", "NAR", "It can also do the work for you. Essays. Homework. Code. Reports.", None, 0.2),
    ("l3", "CLARA", "My name's on this. I never wrote it.", None, 0.2),
    # ---- the villa
    ("v1", "GOV", "Signorina Clara. Your work is already finished.", None, 0.25),
    # ---- the gallery of graduates
    ("g1", "NAR", "Perfect work, with almost no understanding behind it.", None, 0.2),
    ("g2", "NAR", "At a UK university, researchers slipped AI answers into real online exams. Ninety-four percent went undetected. On average, they outscored the real students.",
     "At a UK university, researchers slipped AI answers into real online exams. | 94% went undetected. | On average, they outscored the real students.", 0.2),
    ("g3", "NAR", "Ghost writers aren't new. Now they're free and instant.", None, 0.25),
    # ---- the writing room: the same night, year after year
    ("w1", "GOV", "Shall I write it for you?", None, 0.12),
    ("w2", "CLARA", "Just this once.", None, 0.3),
    ("w3", "GOV", "=w1", None, 0.12),
    ("w4", "CLARA", "=w2", None, 0.15),
    ("w5", "NAR", "Eighty-eight percent of UK students use AI to help with assessed work. Nearly one in five have pasted its words straight in.",
     "88% of UK students use AI to help with assessed work. | Nearly 1 in 5 have pasted its words straight in.", 0.2),
    ("w6", "GOV", "=w1", None, 0.12),
    ("w7", "CLARA", "=w2", None, 0.25),
    ("w8", "NAR", "Proven AI cheating at UK universities tripled in a year. And that's only the ones who got caught.",
     "Proven AI cheating at UK universities tripled in a year. | And that's only the ones who got caught.", 0.3),
    # ---- the clockwork room
    ("c1", "NAR", "You can pass a programming course, and still not be able to program.", None, 0.15),
    ("c2", "NAR", "In a new trial, coders learning a new tool with AI scored fifty percent on a test afterwards. Coding by hand: sixty-seven. The biggest gap? Debugging.",
     "In a new trial (2026), coders learning a new tool with AI scored 50% on a test afterwards. | Coding by hand: 67%. | The biggest gap? Debugging.", 0.2),
    ("c3", "GOV", "Fix it, signorina.", None, 0.15),
    ("c4", "CLARA", "I... I can't.", None, 0.0),
    # ---- the hall of mirrors
    ("m1", "NAR", "Do this for years, and degrees stop meaning what they say. Even the honest ones.", None, 0.15),
    ("m2", "NAR", "So universities are bringing back handwritten exams, and employers face-to-face interviews.", None, 0.2),
    # ---- the locked room
    ("x1", "GOV", "Your examination is waiting.", None, 0.0),
    # ---- real life
    ("r1", "NAR", "She was never in an old town. It isn't nineteen seventy-four. It's Monday, nine a.m., and she has been silent in this chair for forty seconds.",
     "She was never in an old town. | It isn't 1974. | It's Monday, 9 a.m., and she has been silent in this chair for forty seconds.", 0.25),
    ("r2", "INT1", "First-class degree in computer science. So, why does this code crash?", None, 1.1),
    ("r3", "INT2", "Then talk us through your dissertation.", None, 0.35),
    ("r4", "CLARA", "It was about... it was...", None, 0.9),
    ("r5", "INT1", "Thank you, Clara. We'll be in touch.", None, 0.35),
    ("r6", "NAR", "Six rejections. Fifty-three thousand pounds of debt. A degree on the wall, and nothing behind it.",
     "Six rejections. | £53,000 of student debt. | A degree on the wall, and nothing behind it.", 0.4),
    # ---- the reveal turns on the viewer
    ("p1", "NAR", "One day, the machine will wait outside the door. What will be left inside you?", None, 0.0),
    # ---- the quiet lesson
    ("e1", "NAR", "AI can be the best tutor you'll ever have, if it makes you do the thinking.", None, 0.2),
    ("e2", "NAR", "Yoonesko calls for AI that is human-centred, age-appropriate and carefully governed. Yet in twenty twenty-three, fewer than one in ten schools and universities had any formal guidance.",
     "UNESCO calls for AI that is human-centred, age-appropriate and carefully governed. | Yet in 2023, fewer than 1 in 10 schools and universities had any formal guidance.", 0.2),
    ("e3", "NAR", "Ask it to teach you, not to do it for you. If you can't explain it without the machine, you don't know it yet.",
     "Ask it to teach you, not to do it for you. | If you can't explain it without the machine, you don't know it yet.", 0.0),
]

# the third "Just this once" is the same recording, gone mechanical: the voice of someone turning into porcelain
FX = {"w4": "pale", "w7": "porcelain"}
SPEED = {"e3": 0.92, "e1": 0.95, "c1": 0.98, "p1": 0.95, "g2": 1.12, "e2": 1.14, "m2": 1.12}
PITCH = {}
