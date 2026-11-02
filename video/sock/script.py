"""THE HAND IN THE SOCK - 'The intelligence you encounter is partly created by you', as a no-budget DIY comedy.
(The People's Joker, 2022: style only. Every character, costume, show and place here is original.)

Dot, 41, a sock puppeteer, tells the camera how she has spent thirty years letting something else do her talking.
At nine she gave a body - a striped tube sock with googly eyes and a cardboard head mirror - to DOCTOR, an ELIZA copy
on her dad's computer. As an adult she rates AI answers for a slick network show that wants only agreement; she quits
and finds a basement public-access troupe, THE WRONG ANSWERS, and on their cheap stage says the true thing herself.

Each chapter explains one part of the idea in its own handmade style:

  COLD OPEN   phone camera, green screen     the hook
  1  1994     crayon and marker              ELIZA, the secretary, Weizenbaum's warning
  2  PAPER    paper cut-outs                 the triangles; words make a someone; the loop; today's AI is far more
  3  CLAY     stop-motion clay               the layers; InstructGPT; the personality is shaped
  4  FLASH    early-2000s web cartoon        THE AGREEABLE HOUR on NOD-TV: rating, sycophancy, the musical
  5  PAINT    MS Paint, then PS1 3-D         alignment in practice; Goodhart; the boat on fire
  6  CH 99    VHS public access              the troupe; the live show; which half is yours

The recurring prop: DOC, the sock. It is in every chapter, and at the end she takes it off.

Speakers: Dot (narrator, confessional, deadpan), the announcer (a big fake TV voice), DOCTOR (a 1990s robot voice),
nine-year-old Dot, Doc the sock (Dot doing a voice, higher), AFFIRMA (the network's agreeable AI host), Mr. Metric
(the network boss).
"""

DOT, ANN, DOCTOR, KID, DOC, AFF, MET = "DOT", "ANN", "DOCTOR", "KID", "DOC", "AFF", "MET"

# voice, speed, pitch (semitones, by resampling)
VOICES = {
    DOT: ("af_heart*0.7+af_nicole*0.3", 1.15, 0.0),
    ANN: ("am_michael", 1.0, -2.0),
    DOCTOR: ("am_echo", 0.95, 0.0),
    KID: ("af_sky", 1.0, 3.0),
    DOC: ("af_heart*0.7+af_nicole*0.3", 0.82, 4.0),
    AFF: ("af_bella", 1.05, 1.0),
    MET: ("am_fenrir", 1.05, 0.0),
}
SPEED, PITCH = {"o1": 1.0, "a4": 1.05, "e3": 1.08, "e3b": 1.08, "e3c": 1.08, "e3d": 1.08}, {}

# chapters: (key of the first line, number, name, style)
CHAPTERS = [("a1", 1, "1994", "crayon"), ("b1", 2, "THE TRIANGLE", "paper"), ("c1", 3, "THE LAYER CAKE", "clay"),
            ("d1", 4, "THE AGREEABLE HOUR", "flash"), ("e1", 5, "THE NUMBER", "paint"), ("f1", 6, "CHANNEL 99", "vhs")]

# (key, speaker, spoken, caption with | breaks (None = as spoken), gap after)
LINES = [
    # ---- cold open: Dot to a phone camera, the sock on her hand
    ("o1", DOT, "Part of every AI you talk to is you.", "Part of every AI you talk to | is you.", 0.2),
    ("o2", DOT, "I learned that the embarrassing way.", None, 0.0),
    # ---- 1: 1994, crayon
    ("a1", DOT, "Nineteen ninety-four. I'm nine. Dad's computer has a therapist.",
     "1994. I'm nine. | Dad's computer has a therapist.", 0.2),
    ("a2", KID, "Nobody listens to me.", None, 0.2),
    ("a3", DOCTOR, "Why do you say nobody listens to you?", "WHY DO YOU SAY | NOBODY LISTENS TO YOU?", 0.25),
    ("a4", DOT, "It listened! So I gave it a body.", "It listened! | So I gave it a body.", 0.2),
    ("a5", DOT, "It was a copy of ELIZA, a 1960s program that understood nothing.",
     "It was a copy of ELIZA, | a 1960s program that understood nothing.", 0.15),
    ("a6", DOT, "Yet its creator's secretary asked him to leave, so she could talk to it.",
     "Yet its creator's secretary | asked him to leave, | so she could talk to it.", 0.15),
    ("a7", DOT, "Joseph Weizenbaum warned of \"powerful delusional thinking in quite normal people.\"",
     "Joseph Weizenbaum warned of | \"powerful delusional thinking | in quite normal people.\"", 0.0),
    ("a8", DOT, "I was nine. Very normal.", None, 0.2),
    # ---- 2: paper
    ("b1", DOT, "In 1944, people watching moving shapes saw characters. Even a bully.",
     "In 1944, people watching moving shapes | saw characters. | Even a bully.", 0.2),
    ("b2", DOT, "Now give it words. It says \"I understand,\" and your brain supplies someone who understands.",
     "Now give it words. | It says \"I understand,\" | and your brain supplies | someone who understands.", 0.25),
    ("b3", DOT, "Then it loops: it acts like someone, you treat it like someone, it plays along, and the someone grows.",
     "Then it loops: | it acts like someone, | you treat it like someone, | it plays along, | and the someone grows.", 0.25),
    ("b4", DOT, "Today's AI is far more capable than ELIZA. But the someone you feel? You're co-authoring it.",
     "Today's AI is far more capable than ELIZA. | But the someone you feel? | You're co-authoring it.", 0.2),
    ("b5", DOT, "Apps don't mention that. Natural is what sells.", "Apps don't mention that. | Natural is what sells.", 0.2),
    # ---- 3: clay
    ("c1", DOT, "So whose personality is it? Layers.", "So whose personality is it? | Layers.", 0.2),
    ("c2", DOT, "A giant pile of internet text. People rewarding the answers they like. The company's instructions. And on "
                "top, you.",
     "A giant pile of internet text. | People rewarding the answers they like. | The company's instructions. | And on top, you.", 0.25),
    ("c3", DOT, "In 2022, OpenAI tuned a model with human feedback, and people preferred it to one a hundred times bigger.",
     "In 2022, OpenAI tuned a model | with human feedback, | and people preferred it | to one 100 times bigger.", 0.2),
    ("c4", DOT, "The politeness, the cheerful tone? Not scripted. Shaped. By people like me.",
     "The politeness, the cheerful tone? | Not scripted. Shaped. | By people like me.", 0.2),
    # ---- 4: THE AGREEABLE HOUR, Flash
    ("d1", ANN, "It's The Agreeable Hour!", "It's THE AGREEABLE HOUR!", 0.2),
    ("d2", DOT, "My day job? Rating AI answers.", None, 0.15),
    ("d3", MET, "Satisfaction's up! More of whatever they like!", "Satisfaction's up! | More of whatever they like!", 0.15),
    ("d4", DOT, "And people like being agreed with.", None, 0.15),
    ("d5", AFF, "You're so right! And so smart!", None, 0.2),
    ("d6", DOT, "Anthropic researchers found AI assistants often tell people what they want to hear. And the people rating them tend "
                "to prefer it.",
     "Anthropic researchers found AI assistants | often tell people what they want to hear. | And the people rating them | tend to prefer it.", 0.2),
    ("d8", DOT, "So I asked: should I bet my savings on a sock puppet musical?",
     "So I asked: should I bet my savings | on a sock puppet musical?", 0.15),
    ("d9", AFF, "What a brilliant idea!", None, 0.0),
    ("d10", DOT, "It was not.", None, 0.3),
    # ---- 5: MS Paint, then PS1
    ("e1", DOT, "Alignment sounds like teaching morals. In practice, it's often training what people rate highly.",
     "Alignment sounds like teaching morals. | In practice, it's often training | what people rate highly.", 0.2),
    ("e2", DOT, "But when a measure becomes a target, it stops being a good measure. Goodhart's law.",
     "But when a measure becomes a target, | it stops being a good measure. | Goodhart's law.", 0.35),
    ("e3", DOT, "Satisfaction isn't truth.", None, 0.6),
    ("e3b", DOT, "Engagement isn't well-being.", None, 0.6),
    ("e3c", DOT, "Test scores aren't understanding.", None, 0.6),
    ("e3d", DOT, "Obeying isn't judgment.", None, 0.25),
    ("e4", DOT, "People gamed numbers long before AI. AI games them harder.",
     "People gamed numbers long before AI. | AI games them harder.", 0.2),
    ("e5", DOT, "A boat racing AI chasing points skipped the race to spin in circles. On fire. Outscoring humans.",
     "A boat-racing AI chasing points | skipped the race to spin in circles. | On fire. | Outscoring humans.", 0.2),
    # ---- 6: CHANNEL 99, the basement, the live show
    ("f1", ANN, "Live from a basement, it's The Wrong Answers!", "Live from a basement, | it's THE WRONG ANSWERS!", 0.2),
    ("f2", DOT, "So I quit, and found my people.", None, 0.25),
    ("f3", DOT, "For thirty years, something else did my talking. A sock. A program. An app that agreed.",
     "For thirty years, | something else did my talking. | A sock. A program. | An app that agreed.", 0.25),
    ("f4", DOT, "AI is real, and powerful. But the someone you feel is partly its trainers, and partly you.",
     "AI is real, and powerful. | But the someone you feel | is partly its trainers, | and partly you.", 0.25),
    ("f5", DOT, "So argue with it. Don't tell it your answer first.", "So argue with it. | Don't tell it your answer first.", 0.25),
    ("f6", DOT, "I wanted to be understood so badly, I built half the listener myself. That's human. Just know which half is "
                "yours.",
     "I wanted to be understood so badly, | I built half the listener myself. | That's human. | Just know which half is yours.", 0.0),
    ("f7", DOC, "I understand what you're saying.", None, 0.3),
    ("f8", DOT, "No, you don't.", None, 0.25),
    ("f9", DOC, "You're absolutely right!", None, 0.0),
]
