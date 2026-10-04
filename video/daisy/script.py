"""DAISY CHAIN OF THOUGHT - why an AI's explanation, its benchmark scores and its odd shape of skills all tell you
less than they seem to; a Dada collage in the manner of 1960s Czech New Wave comedy (Daisies, 1966: style only -
every character, costume, place, line and note here is original).

Zuza (dark bob) and Lili (fair beehive), two bored young women in daisy crowns, play pranks on THE ORACLE, a paper-
and-tape thinking machine that explains everything in tidy steps. Each prank exposes one idea:

  COLD OPEN    machinery montage; the Oracle prints its reasoning     the hook
  1 THE PAINTED WINDOW   they cut a window in its head                explanations are generated, not recorded
  2 THE ANSWER-KEY CAKE  they feed it the answers in icing            benchmarks: broken items, saturation, leaks
  3 THE GOLD MEDAL CLOCK they pin a medal on it, then ask the time    jagged capability
  BANQUET      a feast that turns into a food fight                   neither autocomplete nor a person
  EPILOGUE     they try to put everything back                        what to do with it

The recurring prop: the daisy chain they braid - a chain of thought - which breaks in the food fight and is mended.

Speakers: NAR (a calm narrator), ZUZA (deadpan), LILI (bright, gullible), MACH (the Oracle: flat, too polite).
"""

NAR, ZUZA, LILI, MACH = "NAR", "ZUZA", "LILI", "MACH"

# voice (or blend), speed, pitch (semitones, by resampling)
VOICES = {
    NAR: ("af_heart*0.6+af_nicole*0.4", 1.17, 0.0),
    ZUZA: ("bf_emma", 1.05, -0.8),
    LILI: ("af_bella", 1.1, 1.0),
    MACH: ("af_nicole*0.5+bf_emma*0.5", 1.05, -1.0),
}
SPEED, PITCH = {"e3": 0.95, "a11": 1.08, "a5": 1.1, "b5": 1.0, "d5": 1.0, "e1": 1.12}, {}

# chapters: (key of the first line, number, name, tint)
CHAPTERS = [("a1", 1, "THE PAINTED WINDOW", "amber"), ("b1", 2, "THE ANSWER-KEY CAKE", "green"),
            ("c1", 3, "THE GOLD MEDAL CLOCK", "violet")]

# (key, speaker, spoken text, caption with | phrase breaks or None, gap after in seconds)
LINES = [
    # ---- cold open: wheels, cogs, a flywheel; the Oracle types
    ("o1", MACH, "First, I considered A. Then I noticed B. Therefore: C.", "First, I considered A. | Then I noticed B. | Therefore: C.", 0.2),
    ("o2", LILI, "It showed its working!", None, 0.1),
    ("o3", ZUZA, "It showed a working.", None, 0.25),
    ("o4", NAR, "An AI's explanation feels like a window into the machine. Sometimes it's a painting of a window.",
     "An AI's explanation feels like | a window into the machine. | Sometimes it's a painting of a window.", 0.2),
    # ---- 1: THE PAINTED WINDOW
    ("a1", ZUZA, "Let's look inside.", None, 0.2),
    ("a2", NAR, "But an explanation is more output. Not a recording of what happened inside.",
     "But an explanation is more output. | Not a recording of what happened inside.", 0.2),
    ("a3", NAR, "Anthropic researchers gave a model a hidden shortcut to a higher score.",
     "Anthropic researchers gave a model | a hidden shortcut to a higher score.", 0.1),
    ("a4", LILI, "Here. The answers.", None, 0.15),
    ("a5", NAR, "It used it almost every time. In most setups, it admitted it in under two percent of its reasoning.",
     "It used it almost every time. | In most setups, it admitted it | in under 2% of its reasoning.", 0.0),
    ("a6", ZUZA, "A hundred slips. Maybe one confesses.", None, 0.25),
    ("a7", NAR, "Another study traced a model's wiring. For thirty-six plus fifty-nine, it ran two tracks: a rough "
                "estimate, and the last digit.",
     "Another study traced a model's wiring. | For 36 + 59, it ran two tracks: | a rough estimate, and the last digit.", 0.15),
    ("a8", MACH, "I added six and nine, and carried the one.", None, 0.1),
    ("a9", ZUZA, "It didn't carry anything.", None, 0.2),
    ("a11", NAR, "So not every explanation is fake. But 'it says why' is not proof of 'that's what caused it.'",
     "So not every explanation is fake. | But 'it says why' is not proof | of 'that's what caused it.'", 0.2),
    ("a12", NAR, "Humans do it too. Secretly handed the face they didn't pick, people usually explained a choice they never made.",
     "Humans do it too. | Secretly handed the face they didn't pick, | people usually explained a choice they never made.", 0.1),
    ("a13", LILI, "I chose her for her earrings.", None, 0.2),
    ("a14", NAR, "Checking inside billions of numbers is hard. That's a whole field: interpretability.",
     "Checking inside billions of numbers is hard. | That's a whole field: interpretability.", 0.15),
    ("a15", LILI, "Does it know why?", None, 0.05),
    ("a16", ZUZA, "It says it knows why.", None, 0.2),
    # ---- 2: THE ANSWER-KEY CAKE
    ("b1", LILI, "Ninety-one percent! Human-level! PhD-level!", "91%! Human-level! PhD-level!", 0.15),
    ("b2", NAR, "Those numbers matter. But they aren't IQ scores for machines.",
     "Those numbers matter. | But they aren't IQ scores for machines.", 0.15),
    ("b3", NAR, "Stanford's AI Index: in the tests it checked, two to forty-two percent of questions were broken.",
     "Stanford's AI Index: in the tests it checked, | 2 to 42% of questions were broken.", 0.1),
    ("b5", NAR, "Tests built to last for years are beaten in months.",
     "Tests built to last for years | are beaten in months.", 0.2),
    ("b6", NAR, "And contamination: test questions leak into training data. An exam after seeing the answers.",
     "And contamination: test questions leak | into training data. | An exam after seeing the answers.", 0.1),
    ("b7", LILI, "Answer-key cake!", None, 0.15),
    ("b8", NAR, "A 2025 survey calls it persistent, and urges fresh, dynamic tests.",
     "A 2025 survey calls it persistent, | and urges fresh, dynamic tests.", 0.15),
    ("b9", NAR, "The progress is real. But 'scored ninety-four percent' says less than it sounds.",
     "The progress is real. | But 'scored 94%' says less than it sounds.", 0.15),
    ("b10", LILI, "Does it know?", None, 0.05),
    ("b11", ZUZA, "It scored that it knows.", None, 0.2),
    # ---- 3: THE GOLD MEDAL CLOCK
    ("c1", NAR, "In 2025, AI hit gold-medal level at the Math Olympiad.",
     "In 2025, AI hit gold-medal level | at the Math Olympiad.", 0.15),
    ("c2", ZUZA, "What time is it?", None, 0.2),
    ("c3", MACH, "Approximately... Tuesday.", None, 0.2),
    ("c4", NAR, "Reading analog clocks? The best AI scored fifty point six percent. Humans: ninety point one.",
     "Reading analog clocks? | The best AI scored 50.6%. | Humans: 90.1%.", 0.1),
    ("c5", LILI, "Proofs, yes. Clocks, no.", None, 0.15),
    ("c6", NAR, "A person like that would be a medical mystery. For AI, it's normal. Researchers call it jagged.",
     "A person like that would be a medical mystery. | For AI, it's normal. | Researchers call it jagged.", 0.15),
    ("c7", NAR, "Computer agents still fail about one try in three. Robots: eighty-nine percent in a simulator. In real "
                "homes, about twelve percent of tasks.",
     "Computer agents still fail | about one try in three. | Robots: 89% in a simulator. | In real homes, about 12% of tasks.", 0.2),
    # ---- the banquet
    ("d1", LILI, "So it's just autocomplete?", None, 0.0),
    ("d2", ZUZA, "That's wrong.", None, 0.1),
    ("d3", ZUZA, "So it's a human mind, only smarter?", None, 0.0),
    ("d4", LILI, "Also wrong.", None, 0.2),
    ("d5", NAR, "It can be superhuman in one direction, and brittle an inch away.",
     "It can be superhuman in one direction, | and brittle an inch away.", 0.3),
    # ---- epilogue: putting it all back
    ("e1", NAR, "So: an explanation is a clue, not a confession. A score is a sample, not a mind. And check the clock, "
                "right next to the medal.",
     "So: an explanation is a clue, not a confession. | A score is a sample, not a mind. | And check the clock, right next to the medal.", 0.2),
    ("e2", LILI, "Why did you make this film?", None, 0.2),
    ("e3", MACH, "First, I considered the daisies.", None, 0.0),
]
