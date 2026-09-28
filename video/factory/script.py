"""The script: "Extending human intelligence" - AI as an intellectual amplifier - as a 1971 factory-tour musical.

You find a golden ticket in the grey town, the day your dad's test results arrive. A strange host tours five
rooms, each an invention for one kind of thinking; four guests who misuse the machines are dealt with, and the
little workers sing the moral. Your own question - the letter - goes through every room, so the real-life
scenario plays out at full strength; the true story of a mother and seventeen doctors bookends it.

Speech lines: (key, who, spoken, caption, gap_after)
  spoken spells numbers out for the voice; caption is what the reader sees ("|" forces a caption break).
Song markers: (key, "SONG", None, None, gap_after) -> SONGS[key]. During a song there are no captions: the lyrics
are shown karaoke-style in the same band, half-spoken on the beat (the voices are text-to-speech; they can't sing).
"""
NAR, HOST, ANN, COPIER, BELIEVER, YESMAN, RUSHER, MIRROR, FARMER, STUDENT, DOCTOR, WORKERS, SONG = (
    "NAR", "HOST", "ANN", "COPIER", "BELIEVER", "YESMAN", "RUSHER", "MIRROR", "FARMER", "STUDENT", "DOCTOR", "WORKERS", "SONG")
# who: (voice, speed, pitch in semitones)
VOICES = {NAR: ("af_heart", 1.1, 0.0), HOST: ("bm_george", 1.02, 0.0), ANN: ("am_michael", 1.15, 0.0),
          COPIER: ("am_puck", 1.0, 3.5), BELIEVER: ("bf_isabella", 1.0, 0.0), YESMAN: ("am_onyx", 0.95, 0.0),
          RUSHER: ("af_nova", 1.15, 3.0), MIRROR: ("am_echo", 0.85, -2.0), FARMER: ("bm_lewis", 1.0, 0.0),
          STUDENT: ("af_kore", 1.05, 0.0), DOCTOR: ("af_sarah", 0.95, 0.0), WORKERS: ("am_puck", 0.92, 5.0)}
SPEED = {"t1a": 1.08, "t1b": 1.32, "t1c": 1.6, "t2": 0.82, "g3": 0.84, "x1": 1.22, "x2": 0.88, "x3": 0.86}   # per-line pace
PITCH = {"x1": 1.5}

LINES = [
    # ---- cold open: the true story, teased
    ("c0", NAR, "Seventeen doctors. Three years. And still no answer for her little boy.",
     "17 doctors. 3 years.| And still no answer for her little boy.", 0.25),
    ("c1", NAR, "Then, one night, she found a way to think bigger.", None, 0.8),

    # ---- the grey town
    ("a1", NAR, "In the grey town, thinking is slow work. Three hours digging through fifty reports, and no time left to think.",
     "In the grey town, thinking is slow work.| 3 hours digging through 50 reports,| and no time left to think.", 0.3),
    ("a3", NAR, "And today, you got a letter. Your dad's test results. Four pages of words you don't understand.",
     "And today, you got a letter.| Your dad's test results.| 4 pages of words you don't understand.", 0.3),
    ("b1", NAR, "Then, inside a chocolate wrapper: a golden ticket.", None, 0.25),
    ("b2", NAR, "Admit one mind. Bring a question. You bring the letter.",
     "“Admit one mind. Bring a question.”| You bring the letter.", 0.4),

    # ---- the newsreel: the world goes mad for thinking machines
    ("n1", ANN, "Extra! Extra! Thinking machines in every pocket!", None, 0.1),
    ("n2", ANN, "Consultants: forty percent better work! Writers: forty percent faster! And beginners gain the most!",
     "Consultants: 40% better work!| Writers: 40% faster!| And beginners gain the most!", 0.15),
    ("n3", FARMER, "It read my loan papers to me in plain English.", None, 0.1),
    ("n4", STUDENT, "It argues with my essay before my teacher does.", None, 0.4),

    # ---- the gates, the host, the rule
    ("g1", HOST, "Welcome, welcome, in from the rain. Here we stretch the reach of the brain.",
     "Welcome, welcome, in from the rain.| Here we stretch the reach of the brain.", 0.2),
    ("g2", HOST, "One rule only: my machines think with you. Never for you.",
     "One rule only:| my machines think WITH you.| Never FOR you.", 0.3),
    ("g3", HOST, "Those who forget... don't finish the tour.", None, 1.6),

    # ---- the door opens: the wonderland, the ballad
    ("s1", SONG, None, None, 0.2),
    ("r0", NAR, "This is what it feels like. Every expert you could never afford, patient at two in the morning, explaining it again.",
     "This is what it feels like.| Every expert you could never afford,| patient at 2 in the morning, explaining it again.", 0.45),

    # ---- room 1: the untangler
    ("h1", HOST, "In here, the tangled comes undone.", None, 0.15),
    ("r1", NAR, "Your dad's letter goes in tangled, and comes out in plain words. It explains again, simpler, until you get it.",
     "Your dad's letter goes in tangled,| and comes out in plain words.| It explains again, simpler, until you get it.", 0.2),
    ("k1", COPIER, "Ooh! I'll just swallow the answer!", None, 1.0),
    ("w1", SONG, None, None, 0.3),

    # ---- room 2: the press
    ("h2", HOST, "Fifty reports in, and what comes out? Just what matters. And what's in doubt.",
     "50 reports in, and what comes out?| Just what matters. And what's in doubt.", 0.15),
    ("r2", NAR, "Fifty studies on his condition go in. Out come the six that matter, with a flag where two disagree.",
     "50 studies on his condition go in.| Out come the 6 that matter,| with a flag where 2 disagree.", 0.15),
    ("r2b", NAR, "Three hours of searching become three hours of thinking.",
     "3 hours of searching| become 3 hours of thinking.", 0.2),
    ("k2", BELIEVER, "It sounds so sure! I'll believe every word!", None, 1.0),
    ("w2", SONG, None, None, 0.3),

    # ---- room 3: the mirror that argues back
    ("h3", HOST, "A mirror that argues. It won't just agree.", None, 0.15),
    ("r3", NAR, "It makes the strongest case against each treatment, and finds the hole in your own reasoning.",
     "It makes the strongest case against each treatment,| and finds the hole in your own reasoning.", 0.2),
    ("k3", YESMAN, "Mirror, just tell me I'm right.", None, 0.15),
    ("k3b", MIRROR, "You're right.", None, 1.0),
    ("w3", SONG, None, None, 0.3),

    # ---- room 4: the kitchen of what-if
    ("h4", HOST, "A fog goes in. A plan comes out. With every question you forgot about.",
     "A fog goes in. A plan comes out.| With every question you forgot about.", 0.15),
    ("r4", NAR, "What else could explain his symptoms? What happens if you wait? Ideas fizz, most pop, and your worry becomes a plan, with three questions nobody has asked.",
     "What else could explain his symptoms?| What happens if you wait?| Ideas fizz, most pop,| and your worry becomes a plan,| with 3 questions nobody has asked.", 0.2),
    ("k4", RUSHER, "First idea! Done! Next!", None, 1.0),
    ("w4", SONG, None, None, 0.5),

    # ---- the tunnel (the horror peak)
    ("t1a", HOST, "Is it true? Is it sure? Did anybody check?", None, 0.1),
    ("t1b", HOST, "A study that isn't. A quote no one said. A number invented, so polished, so sure.",
     "A study that isn't. A quote no one said.| A number invented, so polished, so sure.", 0.05),
    ("t1c", HOST, "Is it true, is it true, is it true, is it true?", None, 1.5),
    ("t2", HOST, "It can be wrong. Beautifully. So you check.", None, 0.35),
    ("e1", NAR, "Trust it blindly, and you stop checking. In one study, consultants using AI on a task it was bad at were nineteen points less likely to get it right. Used well, you think more.",
     "Trust it blindly, and you stop checking.| In one study, consultants using AI on a task it was bad at| were 19 points less likely to get it right.| Used well, you think more.", 0.5),

    # ---- the real-life scenario, at full strength
    ("p1", NAR, "Next morning, you walk in with one page, and ask the question nobody had asked: could his diabetes pill be lowering his B twelve?",
     "Next morning, you walk in with one page,| and ask the question nobody had asked:| “Could his diabetes pill be lowering his B12?”", 0.25),
    ("p2", DOCTOR, "That's... exactly the right question.", None, 0.3),
    ("p3", NAR, "One blood test. His B twelve was low. A supplement, and by spring, the numbness is fading.",
     "One blood test. His B12 was low.| A supplement, and by spring,| the numbness is fading.", 0.6),

    # ---- the host explodes; then the warm reveal
    ("x1", HOST, "You questioned my machines! You argued with them! You checked every single drop!",
     "You questioned my machines!| You argued with them!| You checked every single drop!", 1.5),
    ("x2", HOST, "Good. That is exactly what they are for.", None, 0.25),
    ("x3", HOST, "The factory is yours.", None, 0.5),
    ("z1", NAR, "The benefit isn't speed. It's reach.", None, 0.6),

    # ---- the true story, paid off
    ("y1", NAR, "Remember that boy? His mother typed every symptom into an AI, and it suggested tethered cord syndrome.",
     "Remember that boy?| His mother typed every symptom into an AI,| and it suggested tethered cord syndrome.", 0.2),
    ("y2", NAR, "A neurosurgeon checked the scans, and agreed. Alex had surgery.",
     "A neurosurgeon checked the scans, and agreed.| Alex had surgery.", 0.25),
    ("y3", NAR, "The AI didn't replace her doctors. It gave her the reach to find the right one.",
     "The AI didn't replace her doctors.| It gave her the reach to find the right one.", 0.4),
    ("y4", NAR, "Now, bring your question.", None, 0.5),
]

REFRAIN = ("Think it through, think it through;", "the thinking's up to you!")
SONGS = {
    # the wistful ballad, half-sung by the host as the door opens
    "s1": dict(style="ballad", bpm=104, intro=4, outro=2, lines=[
        (HOST, "Step inside, and see"),
        (HOST, "how far a mind can go,"),
        (HOST, "past every book you'll never read,"),
        (HOST, "and every mind you'll never know;"),
        (HOST, "the door stays open,"),
        (HOST, "if the thinking's done by you.")]),
    # the little workers' moral chants: a verse for the guest, then the same refrain every time
    "w1": dict(style="chant", bpm=140, intro=2, outro=1, lines=[
        (WORKERS, "He swallowed it whole,"), (WORKERS, "and he hasn't a clue!"),
        (WORKERS, REFRAIN[0]), (WORKERS, REFRAIN[1])]),
    "w2": dict(style="chant", bpm=140, intro=2, outro=1, lines=[
        (WORKERS, "She never once checked,"), (WORKERS, "so up the pipe she flew!"),
        (WORKERS, REFRAIN[0]), (WORKERS, REFRAIN[1])]),
    "w3": dict(style="chant", bpm=140, intro=2, outro=1, lines=[
        (WORKERS, "He only asked 'Am I right?'"), (WORKERS, "so his small world shrank too!"),
        (WORKERS, REFRAIN[0]), (WORKERS, REFRAIN[1])]),
    "w4": dict(style="chant", bpm=140, intro=2, outro=1, lines=[
        (WORKERS, "She grabbed the first bubble;"), (WORKERS, "fast isn't far, it's true!"),
        (WORKERS, REFRAIN[0]), (WORKERS, REFRAIN[1])]),
}
LYRIC_SHOWN = {}

# the thirteen uses, grouped by room (shown on each room's door plaque)
ROOMS = {
    1: ("THE UNTANGLER", ["explain unfamiliar subjects", "translate jargon"]),
    2: ("THE PRESS", ["summarize documents", "find inconsistencies"]),
    3: ("THE ARGUING MIRROR", ["critique an argument", "opposing views", "compare ideas"]),
    4: ("KITCHEN OF WHAT-IF", ["brainstorm", "generate hypotheses", "explore consequences",
                               "organize thoughts", "vague ideas into plans", "missing questions"]),
}
