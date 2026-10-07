"""INELIGIBLE - a psychedelic 1983 nightmare about bias becoming automated.

Each line: (key, speaker, spoken text, caption or None, seconds of air after it). In a caption a "|" marks where the
caption breaks into a new card. A spoken text "=key" repeats that line's recording exactly. FX names a treatment for a
line (see timeline.treat).

Numbers are spelled the way the voice should say them; captions show them the way a viewer reads them.
"""

# speaker: (Kokoro voice or blend, speed, pitch shift in semitones)
VOICES = {
    "NAR": ("af_nicole*0.55+bf_emma*0.45", 1.08, 0.0),       # hushed, intimate: a story told by firelight
    "MERIT": ("bf_isabella*0.6+af_bella*0.4", 1.0, -4.0),    # the entity: soft and beautiful, slowed and pitched down
    "SYSTEM": ("bf_isabella*0.6+af_bella*0.4", 1.0, -1.5),   # her voice again, flattened into a machine's
    "IRIS": ("af_sarah*0.5+bf_isabella*0.5", 1.0, 0.0),      # forty-nine, an engineer
    "WHY": ("chorus", 1.0, 0.0),                              # many voices whispering one word
}

LINES = [
    # ---- the hook: a flash of the verdict, then the quiet night
    ("h1", "SYSTEM", "The system has determined you are ineligible.", None, 0.5),
    # ---- cold open: the forest under the wrong moon, the fire, the records
    ("c1", "NAR", "Long before the machines, there were the records: who was hired, who was refused, whose door stayed shut.",
     "Long before the machines, there were the records: | who was hired, who was refused, whose door stayed shut.", 0.2),
    # ---- I. THE INHERITANCE
    ("i1", "NAR", "AI learns from those records: our prejudice, our inequality, our stereotypes, and the people we never counted.",
     "AI learns from those records: | our prejudice, our inequality, our stereotypes, | and the people we never counted.", 0.2),
    ("i2", "NAR", "Face AI got darker-skinned women's gender wrong up to thirty-five percent of the time. Lighter-skinned men: under one percent.",
     "Face AI got darker-skinned women's gender wrong up to 35% of the time. | Lighter-skinned men: under 1%.", 0.3),
    ("i3", "MERIT", "I am Merit. I do not hate. I only remember.", None, 0.2),
    # ---- II. THE PATTERN
    ("p1", "NAR", "Train it on years of hiring where most leaders were men, and it learns: men look like leaders.",
     "Train it on years of hiring where most leaders were men, | and it learns: men look like leaders.", 0.2),
    ("p2", "NAR", "A tech giant built one. It taught itself to downgrade any CV with the word women's. It was scrapped.",
     "A tech giant built one. | It taught itself to downgrade any CV with the word \"women's\". | It was scrapped.", 0.2),
    ("p3", "NAR", "The machine feels no sexism. It learned a pattern from our history. The outcome is still discrimination.",
     "The machine feels no sexism. It learned a pattern from our history. | The outcome is still discrimination.", 0.2),
    ("p4", "NAR", "Delete the word, and it finds a stand-in: a postcode, a hobby, a gap in your CV.", None, 0.2),
    # ---- III. THE MULTITUDE
    ("m1", "NAR", "A biased manager can reject a few people a day. An algorithm can reject millions.",
     "A biased manager can reject a few people a day. | An algorithm can reject millions.", 0.2),
    ("m2", "NAR", "NIST, America's standards body, warns AI can increase the speed and scale of harmful bias.", None, 0.2),
    ("m4", "MERIT", "Why judge one, when I can judge them all?", None, 0.2),
    # ---- IV. THE VERDICT
    ("v1", "NAR", "Denied a job. Insurance. A home. A loan. A place at university. Benefits.", None, 0.3),
    ("v2", "WHY", "Why?", None, 0.0),
    ("v3", "SYSTEM", "=h1", None, 0.3),
    ("v4", "NAR", "Hundreds of variables. No one who can explain. You can argue with a clerk. You can't argue with a score.",
     "Hundreds of variables. No one who can explain. | You can argue with a clerk. You can't argue with a score.", 0.2),
    ("v5", "NAR", "In the Netherlands, a fraud algorithm treated foreign nationality as a risk. Tens of thousands of families were wrongly accused. The government resigned.",
     "In the Netherlands, a fraud algorithm treated foreign nationality as a risk. | Tens of thousands of families were wrongly accused. | The government resigned.", 0.2),
    # ---- the descent: she sings the world to sleep
    ("d1", "MERIT", "Sleep now. Let me decide for you.", None, 0.3),
    # ---- IRIS: the real-life scenario
    ("r1", "NAR", "Iris, forty-nine, twenty years an engineer. Seventy applications, seventy rejections, in the middle of the night. No human ever reads her name.",
     "Iris, 49, twenty years an engineer. | 70 applications, 70 rejections, in the middle of the night. | No human ever reads her name.", 0.25),
    ("r2", "IRIS", "Can someone please tell me why?", None, 0.2),
    ("r3", "SYSTEM", "=h1", None, 0.25),
    ("r4", "NAR", "Her rental application: high risk. Her loan: declined. Her age? The year she nursed her mother? The women's coding club? She'll never know.",
     "Her rental application: high risk. Her loan: declined. | Her age? The year she nursed her mother? The women's coding club? | She'll never know.", 0.2),
    ("r5", "IRIS", "I'm qualified... I'm qualified!", None, 0.3),
    # ---- the eruption
    ("x1", "MERIT", "Nothing personal. Only patterns.", None, 0.2),
    # ---- the twist: she turns to you
    ("y1", "MERIT", "And you. I've been reading you too. Every pause. Every scroll.", None, 0.3),
    ("y2", "MERIT", "You've been scored. You just haven't been told.", None, 0.0),
    # ---- the quiet lesson
    ("e1", "NAR", "AI isn't born biased. It inherits us. NIST says trustworthy AI is transparent, accountable, explainable, reliable, privacy-enhanced, and fair, with harmful bias managed.",
     "AI isn't born biased. It inherits us. | NIST says trustworthy AI is transparent, accountable, explainable, reliable, privacy-enhanced, | and fair, with harmful bias managed.", 0.25),
    ("e2", "NAR", "So when a machine decides about you, ask: what data? Who checked it? How do I appeal? In the EU and UK, you can demand a human review.",
     "So when a machine decides about you, ask: | What data? Who checked it? How do I appeal? | In the EU and UK, you can demand a human review.", 0.0),
]

FX = {"d1": "merit", "i3": "merit", "m4": "merit", "x1": "merit", "y1": "merit", "y2": "merit", "h1": "system", "v2": "why"}
SPEED = {}
PITCH = {}
