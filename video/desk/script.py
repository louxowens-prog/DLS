"""The script: "Education" - AI tutoring - as a life in four chapters, in the style of a 1985 art film (style only).

One woman, first person, the night before the maths exam that decides whether she gets into college. She left
school at sixteen, works shifts, and never had a tutor. Three registers, intercut and never confused:
  PRESENT  the last evening and the exam morning, in muted colour, with a countdown on screen
  MEMORY   her school years, in black and white: the back row, the bell, the tutor across the street
  FICTION  lacquer stage tableaux for the ideas: the desks, the car, the answer box, the lamps
The recurring object is a desk lamp: one bulb for thirty-eight children, the tutor's lamp across the street, her
lamp tonight, and at the end a lamp over every desk.

Speech lines: (key, who, spoken, caption, gap_after). Spoken spells numbers out for the voice; the caption is what
the reader sees ("|" forces a caption break).
"""
NAR, CLOCK, TUTOR, TEACHER = "NAR", "CLOCK", "TUTOR", "TEACHER"
# who: (voice, speed, pitch in semitones)
VOICES = {NAR: ("af_heart", 1.06, 0.0), CLOCK: ("bf_emma", 0.95, 0.0), TUTOR: ("am_michael", 1.0, 0.0),
          TEACHER: ("bf_alice", 1.02, 0.0)}
SPEED = {}
PITCH = {}

CHAPTERS = [  # (number word, title, Japanese, first line key)
    ("ONE", "CROWD", "群衆", "a1"),
    ("TWO", "LIGHT", "光", "b1"),
    ("THREE", "DOUBT", "疑い", "d1"),
    ("FOUR", "DAWN", "夜明け", "e1"),
]

LINES = [
    # ---- cold open: the present, the lamp clicks on
    ("o0a", NAR, "Explain derivatives using cars.", None, 0.15),
    ("o0b", TUTOR, "Your speedometer is a derivative.", None, 0.3),
    ("o2", NAR, "Eleven hours until my exam. And I still don't understand derivatives.",
     "Eleven hours until my exam.| And I still don't understand derivatives.", 0.7),

    # ---- ONE: CROWD
    ("a1", NAR, "I left school at sixteen. Before that, I was the girl in the back row. Thirty-eight of us, one teacher, forty-five minutes. About a minute each.",
     "I left school at sixteen.| Before that, I was the girl in the back row.| 38 of us, one teacher, 45 minutes.| About a minute each.", 0.35),
    ("a3", TEACHER, "Any questions?", None, 0.1),
    ("a4", NAR, "The bell always rang first.", None, 0.6),
    ("a5", NAR, "Across the street, a boy had a tutor. For most of history, that kind of teaching was only for families who could pay.",
     "Across the street, a boy had a tutor.| For most of history, that kind of teaching| was only for families who could pay.", 0.35),
    ("a6", NAR, "In famous research from 1984, tutored students beat ninety-eight percent of a regular class. Later studies found a smaller effect, but still a large one.",
     "In famous research from 1984, tutored students| beat 98% of a regular class.| Later studies found a smaller effect,| but still a large one.", 0.45),
    ("a7", NAR, "Attention was the most expensive thing in the room.", None, 0.9),

    # ---- TWO: LIGHT (the real-life scenario, at full strength)
    ("b1", CLOCK, "Twenty-one fifty-two.", "21:52.", 0.25),
    ("b2", NAR, "After my shift, I asked a machine.", None, 0.15),
    ("b2q", NAR, "Don't explain derivatives mathematically. Explain them using cars.", None, 0.35),
    ("b3", TUTOR, "Your odometer shows how far you've gone. Your speedometer shows how fast that's changing, right now. That's a derivative.",
     "Your odometer shows how far you've gone.| Your speedometer shows how fast that's changing,| right now. That's a derivative.", 0.4),
    ("b4", NAR, "Now explain it visually.", "“Now explain it visually.”", 0.25),
    ("b5", TUTOR, "Drag the point along the curve. How steep it is, right there, is the derivative.",
     "Drag the point along the curve.| How steep it is, right there,| is the derivative.", 0.4),
    ("b6", NAR, "Give me five problems.", "“Give me five problems.”", 1.0),
    ("b7", NAR, "Four right. One wrong.", None, 0.15),
    ("b7q", NAR, "Show me exactly where my reasoning went wrong.", None, 0.3),
    ("b8", TUTOR, "Your power rule is right. But the inside changes too. Multiply by two.",
     "Your power rule is right.| But the inside changes too.| Multiply by 2.", 0.5),
    ("b9", NAR, "Nobody had ever looked at my work that closely. Not once.",
     "Nobody had ever looked at my work that closely.| Not once.", 0.8),
    ("b11", NAR, "It went at my pace. It made the problems harder only when I got them right. It kept slipping in the chain rule I always forget. And at midnight, it asked me to teach it back.",
     "It went at my pace.| It made the problems harder| only when I got them right.| It kept slipping in the chain rule I always forget.| And at midnight, it asked me to teach it back.", 0.4),
    ("b12", NAR, "For the first time, the whole lesson was mine.", None, 0.9),

    # ---- THREE: DOUBT
    ("d1", NAR, "But there's a trap. If it just hands you answers, you learn nothing.",
     "But there's a trap.| If it just hands you answers, you learn nothing.", 0.3),
    ("d2", NAR, "In one study, high-school students with a plain chatbot did better in practice, then seventeen percent worse on the exam without it. A tutor that gave hints, not answers, largely avoided that drop.",
     "In one study, high-school students with a plain chatbot| did better in practice,| then 17% worse on the exam without it.| A tutor that gave hints, not answers,| largely avoided that drop.", 0.35),
    ("d3", NAR, "So my rule was:", None, 0.1),
    ("d3q", NAR, "Never give me the answer. Make me find it.", None, 0.4),
    ("d4", NAR, "Built that way, it works. At Harvard, physics students with an AI tutor learned more than twice as much, in less time, as in an active-learning class.",
     "Built that way, it works.| At Harvard, physics students with an AI tutor| learned more than twice as much, in less time,| as in an active-learning class.", 0.5),
    ("d5", NAR, "And my teacher was never the problem. She had thirty-eight of us, and a stack of papers every night.",
     "And my teacher was never the problem.| She had 38 of us,| and a stack of papers every night.", 0.3),
    ("d6", NAR, "The same tools can draft her lessons, grade simple work, and flag the kid who's lost. Teachers who use AI weekly say it saves them about six hours a week.",
     "The same tools can draft her lessons,| grade simple work, and flag the kid who's lost.| Teachers who use AI weekly say| it saves them about 6 hours a week.", 0.4),
    ("d7", NAR, "Time to finally see the back row.", None, 0.9),

    # ---- FOUR: DAWN
    ("e1", CLOCK, "Seven thirty.", "07:30.", 0.25),
    ("e2", NAR, "It isn't just me. It's the boy whose letters swim. The girl learning in a second language. The village with no maths teacher. The night-shift nurse. The twelve-year-old already bored of algebra.",
     "It isn't just me.| It's the boy whose letters swim.| The girl learning in a second language.| The village with no maths teacher.| The night-shift nurse.| The 12-year-old already bored of algebra.", 0.3),
    ("e3", NAR, "Forty percent of people can't get schooling in a language they understand. It can translate the lesson, coach their pronunciation, and play the other side of a conversation.",
     "40% of people can't get schooling| in a language they understand.| It can translate the lesson,| coach their pronunciation,| and play the other side of a conversation.", 0.3),
    ("e4", NAR, "In Nigeria, six weeks of after-school AI tutoring in English brought gains like one and a half to two years of ordinary school.",
     "In Nigeria, six weeks of after-school AI tutoring in English| brought gains like 1.5 to 2 years| of ordinary school.", 0.5),
    ("e5", CLOCK, "Nine o'clock.", "09:00.", 0.35),
    ("e6", NAR, "Question one. A derivative, with an inside. I smiled.",
     "Question one.| A derivative, with an inside.| I smiled.", 0.6),
    ("e7", NAR, "Six weeks later, I got in.", None, 1.6),
    ("e8", NAR, "For most of history, a tutor was a privilege. Now it can be almost anyone's.",
     "For most of history, a tutor was a privilege.| Now it can be almost anyone's.", 0.5),
    ("e9", NAR, "A light for every desk.", None, 0.6),
]

SONGS = {}
LYRIC_SHOWN = {}

# the thirteen things a tutor can do, in the order the film shows them: (line, word it lands on, label)
USES = [
    ("b3", "odometer", "ADAPTS TO WHAT YOU LOVE"),
    ("b5", "Drag", "EXPLAINS IT ANOTHER WAY"),
    ("b5", "steep", "INTERACTIVE EXERCISES"),
    ("b6", "Give", "GENERATES PRACTICE"),
    ("b7q", "Show", "FINDS WHERE YOU GOT LOST"),
    ("b8", "Your", "INSTANT FEEDBACK"),
    ("b11", "pace", "TEACHES AT YOUR PACE"),
    ("b11", "harder", "ADJUSTS THE DIFFICULTY"),
    ("b11", "chain", "REVIEWS WHAT YOU FORGET"),
    ("b11", "teach", "TESTS UNDERSTANDING"),
    ("e3", "translate", "TRANSLATES LESSONS"),
    ("e3", "pronunciation", "COACHES PRONUNCIATION"),
    ("e3", "conversation", "SIMULATES CONVERSATIONS"),
]
# who it helps most, lit one lamp at a time (line, word, label)
WHO = [
    ("e2", "It's", "LEARNING DIFFERENCES"),
    ("e2", "girl", "LANGUAGE BARRIERS"),
    ("e2", "village", "NO TEACHER NEARBY"),
    ("e2", "night-shift", "UNUSUAL HOURS"),
    ("e2", "twelve", "ADVANCED INTERESTS"),
]
