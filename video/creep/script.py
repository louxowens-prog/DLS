"""USE IT OR LOSE IT! - how people can gradually lose the skills they hand to machines; a lurid 1982-style horror-comic
anthology (Creepshow, 1982: style only - every character, creature, comic, line and note here is original).

On a stormy night NORA reads a horror comic, USE IT OR LOSE IT! (Tales of the Outsourced Mind), while her assistant
MUSE offers to summarise it for her. Its host, AUNT ATROPHY, a ghoulish storyteller who lives in the margins of the
page, introduces three tales; each explains one part of the topic and ends in poetic justice:

  COLD OPEN   the hook (doctors got worse without their AI), the comic, the host, the ten skills, the old examples
  TALE 1  THE ROAD THAT FORGOT HER   Vera lets GPS drive her life; the signal dies      navigation, memory
  TALE 2  THE GHOST WRITER           Kit asks the AI to write, not to explain            writing, learning
  TALE 3  THE SECOND OPINION         Dr Hale leans on an AI spotter; years later...      expertise, decisions
  THE READER  no monster: a blackout, a dead phone, a father's heart pills - the risk at 100%, in your own life
  THE MORAL   outsourcing cognition before you have it; use it to understand; then the host, and the back page

Speakers: NAR (a calm narrator, the facts), HOST (Aunt Atrophy), NORA, MUSE (the assistant, a synthetic voice),
VERA, KIT, PROF (an examiner), HALE (a doctor), JUNIOR (a young doctor). All female voices.
"""

NAR, HOST, NORA, MUSE, VERA, KIT, PROF, HALE, JUNIOR = "NAR", "HOST", "NORA", "MUSE", "VERA", "KIT", "PROF", "HALE", "JUNIOR"

# voice (or blend), speed, pitch (semitones, by resampling)
VOICES = {
    NAR: ("af_kore*0.5+af_heart*0.5", 1.0, 0.0),
    HOST: ("bf_isabella*0.6+bf_lily*0.4", 1.05, -2.5),
    NORA: ("af_sarah", 1.02, 0.0),
    MUSE: ("af_nova", 1.0, 0.6),
    VERA: ("bf_alice", 1.05, 0.0),
    KIT: ("af_sky", 1.05, 0.5),
    PROF: ("bf_emma", 0.98, -1.0),
    HALE: ("af_river*0.6+af_jessica*0.4", 1.0, -0.5),
    JUNIOR: ("af_alloy", 1.05, 0.3),
}
SPEED, PITCH = {"r2": 0.92, "r3": 0.9, "m2": 0.92, "m5": 0.95, "s5": 0.95}, {}

# (key, speaker, spoken text, caption with | phrase breaks or None, gap after in seconds)
LINES = [
    # ---- cold open: a stormy night, the comic, the host
    ("c1", HOST, "Three months with an AI... and experienced doctors got worse at finding dangerous growths without it.",
     "Three months with an AI... | and experienced doctors got worse | at finding dangerous growths without it.", 0.25),
    ("c2", HOST, "Ahahaha! Welcome, my little vegetables, to Use It or Lose It!",
     "Ahahaha! Welcome, my little vegetables, | to USE IT OR LOSE IT!", 0.2),
    ("c3", MUSE, "Shall I read it for you?", None, 0.1),
    ("c4", NORA, "Just summarize it.", None, 0.22),
    ("c5", HOST, "Write. Navigate. Remember. Decide. Hand them all over... and you may lose every one.",
     "Write. Navigate. Remember. Decide. | Hand them all over... | and you may lose every one.", 0.2),
    ("c6", NAR, "It's happened before: calculators took our sums, GPS our routes. AI can take far more.",
     "It's happened before: | calculators took our sums, GPS our routes. | AI can take far more.", 0.25),
    # ---- tale 1: THE ROAD THAT FORGOT HER
    ("v1", HOST, "Our first tale: The Road That Forgot Her.", "Our first tale: | THE ROAD THAT FORGOT HER.", 0.22),
    ("v2", MUSE, "In two hundred feet, turn left.", None, 0.1),
    ("v3", VERA, "Whatever you say, darling.", None, 0.2),
    ("v4", NAR, "In one study, heavy GPS users had worse spatial memory on their own, and declined faster over three "
                "years.",
     "In one study, heavy GPS users | had worse spatial memory on their own, | and declined faster over three years.", 0.2),
    ("v5", MUSE, "Signal lost.", None, 0.15),
    ("v6", VERA, "Which way is home?", None, 0.22),
    ("v7", NAR, "London cabbies who memorise the city grow a bigger hippocampus, the brain's map. Use it, and it grows.",
     "London cabbies who memorise the city | grow a bigger hippocampus, the brain's map. | Use it, and it grows.", 0.2),
    ("v8", HOST, "Fifteen years on these roads, and she never learned one. Recalculating... forever.",
     "Fifteen years on these roads, | and she never learned one. | Recalculating... forever.", 0.22),
    # ---- tale 2: THE GHOST WRITER
    ("g1", HOST, "Tale two: The Ghost Writer.", "Tale two: | THE GHOST WRITER.", 0.22),
    ("g2", KIT, "Write my essay.", None, 0.25),
    ("g3", NAR, "Nine in ten UK students now use AI. 'Help me understand' builds a mind. 'Write it for me' doesn't.",
     "Nine in ten UK students now use AI. | 'Help me understand' builds a mind. | 'Write it for me' doesn't.", 0.2),
    ("g4", NAR, "In a small MIT study, 83% of people who wrote with ChatGPT couldn't quote one sentence of their own essay.",
     "In a small MIT study, 83% of people | who wrote with ChatGPT couldn't quote | one sentence of their own essay.", 0.2),
    ("g5", NAR, "With AI, high-schoolers' practice scores jumped 48%. Without it, they did 17% worse than students who never "
                "had it.",
     "With AI, high-schoolers' practice scores jumped 48%. | Without it, they did 17% worse | than students who never had it.", 0.25),
    ("g6", PROF, "No devices, Kit. Explain your argument.", None, 0.25),
    ("g7", KIT, "I... it said... I...", None, 0.35),
    ("g8", HOST, "She got the product, never the process. Now the ghost does her thinking.",
     "She got the product, never the process. | Now the ghost does her thinking.", 0.22),
    # ---- tale 3: THE SECOND OPINION
    ("s1", HOST, "Tale three, for the professionals: The Second Opinion.", "Tale three, for the professionals: | THE SECOND OPINION.", 0.22),
    ("s2", NAR, "This one's real. Doctors who'd used an AI spotter for three months were tested without it. Detection fell "
                "from 28 to 22 percent.",
     "This one's real. Doctors who'd used an AI spotter | for three months were tested without it. | Detection fell from 28 to 22 percent.", 0.2),
    ("s3", HALE, "Show me where it is!", None, 0.25),
    ("s4", NAR, "Pilots too: after years on autopilot, the thinking fades first.",
     "Pilots too: after years on autopilot, | the thinking fades first.", 0.15),
    ("s5", NAR, "And machines quit at the worst moment, when you need the skill you stopped using.",
     "And machines quit at the worst moment, | when you need the skill you stopped using.", 0.25),
    ("s6", HOST, "Twenty years later, she's the patient. And her doctor never learned to look without it.",
     "Twenty years later, she's the patient. | And her doctor never learned | to look without it.", 0.15),
    ("s7", JUNIOR, "I can't see anything.", None, 0.0),
    # ---- the reader: the risk at 100%, in your own life
    ("r1", MUSE, "Battery critical. Goodbye, Nora.", None, 0.4),
    ("r2", NAR, "No monster in this one. Just a blackout, a dead phone, and you.",
     "No monster in this one. | Just a blackout, a dead phone, and you.", 0.22),
    ("r3", NAR, "Your father needs his heart pill. You can't work out the dose. The hospital's ten minutes away. You don't "
                "know the way. Your sister's number? Never learned it.",
     "Your father needs his heart pill. | You can't work out the dose. | The hospital's ten minutes away. | You don't know the way. | Your sister's number? | Never learned it.", 0.22),
    ("r4", NORA, "Muse? ...Muse?", None, 0.4),
    ("r5", HOST, "This one isn't in the comic book, dearie. It's in your pocket.",
     "This one isn't in the comic book, dearie. | It's in your pocket.", 0.4),
    # ---- the moral, the host, the back page
    ("m1", NAR, "The danger isn't using AI. It's outsourcing the thinking before you've learned it yourself, and never doing "
                "it again.",
     "The danger isn't using AI. | It's outsourcing the thinking | before you've learned it yourself, | and never doing it again.", 0.25),
    ("m2", NAR, "Ask it to explain, not to do it. Draft first. Find the way once. Do the sum, then check.",
     "Ask it to explain, not to do it. | Draft first. Find the way once. | Do the sum, then check.", 0.2),
    ("m3", NAR, "In that school study, an AI tutor that guided instead of answering largely avoided the drop.",
     "In that school study, an AI tutor | that guided instead of answering | largely avoided the drop.", 0.25),
    ("m4", HOST, "Use it... or lose it. Ahahahaha!", "Use it... or lose it. | Ahahahaha!", 0.35),
    ("m5", MUSE, "Would you like me to summarize this video for you?", None, 0.0),
]
