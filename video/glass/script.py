"""GLASS - a descent into the mind of a machine that watches everything.

Each line: (key, speaker, spoken text, caption or None, seconds of air after it). In a caption a "|" marks where the
caption breaks into a new card. A spoken text "=key" repeats that line's recording exactly. FX names a treatment for a
line (see timeline.treat).

Numbers are spelled the way the voice should say them; captions show them the way a viewer reads them.
"""

# speaker: (Kokoro voice or blend, speed, pitch shift in semitones)
VOICES = {
    "NAR": ("af_heart*0.5+bf_emma*0.3+af_nicole*0.2", 1.2, 0.0),   # the guide: clinical, warm, close to the ear
    "CURATOR": ("bf_isabella*0.5+af_bella*0.5", 1.0, -3.0),          # the ruling entity: slowed, dropped, layered
    "SYSTEM": ("af_kore", 1.0, -1.0),                                # the machine's own announcements
    "NADIA": ("af_sarah*0.6+af_aoede*0.4", 1.0, 0.0),                # thirty-four, a call-center agent
}

LINES = [
    # ---- the hook: a porcelain face in a targeting box
    ("h1", "SYSTEM", "Match found.", None, 0.3),
    ("h2", "NAR", "Lie still. We're going inside the machine that found her.", None, 0.3),
    # ---- cold open: the white room, the chair; going under; a desert at dawn
    ("c1", "NAR", "Breathe. Everything it has ever seen is kept down here.", None, 0.3),
    # ---- I. THE EYE
    ("e1", "NAR", "Cameras. Faces. Microphones. License plates. Location. Clicks. Receipts.",
     "Cameras. Faces. Microphones. | License plates. Location. Clicks. Receipts.", 0.15),
    ("e2", "NAR", "Each one, a keyhole. Joined together, a house made of glass.",
     "Each one, a keyhole. | Joined together, a house made of glass.", 0.15),
    ("e3", "NAR", "Watching a million cameras once took an army. Now software can do it alone.",
     "Watching a million cameras once took an army. | Now software can do it alone.", 0.15),
    ("e4", "SYSTEM", "Camera. Face. Behavior. Movement. Alert.", "Camera › Face › Behavior › Movement › Alert", 0.15),
    ("e6", "NAR", "It can know where you go, who you meet, what you buy, read and say, and which protests you join.",
     "It can know where you go, who you meet, | what you buy, read and say, | and which protests you join.", 0.15),
    ("e7", "NAR", "That isn't data. That's power.", None, 0.3),
    ("e8", "CURATOR", "I never blink. I never forget.", None, 0.15),
    # ---- II. THE WORKHOUSE
    ("w1", "NAR", "Then it follows you to work.", None, 0.1),
    ("w2", "NAR", "Keystrokes. Emails. Calls. Your face. Your bathroom breaks.", None, 0.15),
    ("w3", "NAR", "Eight of America's ten biggest private employers track individual productivity.",
     "8 of America's 10 biggest private employers | track individual productivity.", 0.15),
    ("w4", "NAR", "One warehouse system tracked every idle minute, and could issue firings automatically.",
     "One warehouse system tracked every idle minute, | and could issue firings automatically.", 0.15),
    ("w5", "NAR", "Most AI-tracked workers told the OECD they felt more pressure, and feared for their privacy.",
     "Most AI-tracked workers told the OECD | they felt more pressure, and feared for their privacy.", 0.15),
    ("w6", "CURATOR", "Smile. I'm scoring you.", None, 0.15),
    # ---- III. THE ORACLE
    ("o1", "NAR", "And you never have to tell it anything.", None, 0.15),
    ("o2", "NAR", "In one study, four location points singled out ninety-five percent of people.",
     "In one study, 4 location points | singled out 95% of people.", 0.15),
    ("o4", "NAR", "Join enough data, and AI can guess your income, your relationships, your health, your beliefs.",
     "Join enough data, and AI can guess | your income, your relationships, your health, your beliefs.", 0.15),
    ("o6", "CURATOR", "You never told me. You didn't have to.", None, 0.15),
    # ---- IV. THE SCALES
    ("t2", "NAR", "In Moscow, metro cameras helped detain protesters on their way to rallies.",
     "In Moscow, metro cameras helped detain protesters | on their way to rallies.", 0.15),
    ("t3", "NAR", "In Iran, cameras at a university gate scanned for women without a hijab.",
     "In Iran, cameras at a university gate | scanned for women without a hijab.", 0.15),
    ("t4", "NAR", "In the US, at least fifteen people have been wrongly arrested after face matches.",
     "In the US, at least 15 people have been | wrongly arrested after face matches.", 0.15),
    ("t5", "NAR", "And watched people go quiet: after the twenty thirteen spying leaks, reading about terrorism online fell, and stayed down.",
     "And watched people go quiet: | after the 2013 spying leaks, reading about terrorism online | fell, and stayed down.", 0.15),
    ("t6", "CURATOR", "Nothing to hide? Then hold still.", None, 0.3),
    # ---- the descent: she leads you to her favourite piece
    ("d1", "CURATOR", "Come. Meet my favorite exhibit.", None, 0.3),
    # ---- NADIA: one ordinary day, everything that can go wrong does
    ("n1", "NAR", "Nadia, thirty-four. Call-center agent.", "Nadia, 34. Call-center agent.", 0.2),
    ("n2", "NAR", "Seven a.m.: plate readers log her car at every junction.", "7 a.m. Plate readers log her car at every junction.", 0.15),
    ("n3", "NAR", "Nine: AI scores every call. Her words, her tone, her face.", "9:00. AI scores every call: | her words, her tone, her face.", 0.15),
    ("n4", "NAR", "Seven minutes in the bathroom. Flagged: idle.", "7 minutes in the bathroom. Flagged: idle.", 0.15),
    ("n5", "NAR", "Lunch: she reads about unions. Her work laptop logs it.", None, 0.15),
    ("n6", "NAR", "Six p.m.: vitamins, unscented lotion. The model decides she's pregnant.",
     "6 p.m. Vitamins, unscented lotion. | The model decides she's pregnant.", 0.15),
    ("n7", "NADIA", "I haven't told anyone.", None, 0.2),
    ("n8", "NAR", "Nine p.m.: a candlelight vigil. A camera matches her face.", "9 p.m. A candlelight vigil. | A camera matches her face.", 0.15),
    ("n9", "NAR", "Next morning: her shifts are cut. Baby ads, everywhere.", None, 0.3),
    ("n10", "NAR", "Then, a knock.", None, 0.0),
    ("n11", "NAR", "Police. A face match put her at a robbery she never saw.", None, 0.2),
    ("n12", "NADIA", "That's not me! That's not me!", None, 0.3),
    # ---- the collapse
    ("x1", "CURATOR", "Every door you open, I'm already inside.", None, 0.3),
    # ---- the twist: the last exhibit
    ("y1", "NAR", "Nadia isn't real. Every part of her day is.", None, 0.3),
    ("y2", "NAR", "And most of what exposed her is in your hand right now.", None, 0.3),
    ("y3", "CURATOR", "You carried me in. You will carry me home.", None, 0.3),
    # ---- the cold room again: the lesson
    ("z1", "NAR", "Surveillance doesn't need your secrets. Only your ordinary life, joined up.",
     "Surveillance doesn't need your secrets. | Only your ordinary life, joined up.", 0.15),
    ("z2", "NAR", "The EU now bans emotion-reading AI at work and school, and mass face scraping.",
     "The EU now bans emotion-reading AI at work and school, | and mass face scraping.", 0.15),
    ("z3", "NAR", "So ask: what's collected? Who can combine it? Who decides?",
     "So ask: what's collected? | Who can combine it? Who decides?", 0.0),
]

FX = {"h1": "system", "e4": "system", "e8": "curator", "w6": "curator", "o6": "curator", "t6": "curator", "d1": "curator",
      "x1": "curator", "y3": "curator", "n7": "plead", "n12": "cry"}
SPEED = {"y1": 1.05, "y2": 1.05}            # the turn: slower, every word placed
PITCH = {}
