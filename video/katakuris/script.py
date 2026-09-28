"""The script: "Automation can magnify a small error", told by the youngest daughter of a mountain-guesthouse family
that also, for no good reason, processes insurance claims. A horror-comedy musical.

Speech lines: (key, who, spoken, caption, gap_after)
  who  = NAR   the narrator: a young woman, deadpan and matter-of-fact (af_bella)
         MAMA  her mother, dreamy (af_heart) - only in the duet
         MACH  the claims machine, a sugary robot baritone (am_michael, vocoded) - only in the duet
  spoken spells numbers out for the voice; caption is what the reader sees ("|" forces a caption break).
Song markers: (key, "SONG", None, None, gap_after) -> SONGS[key]. During a song there are no captions: the lyrics
are shown karaoke-style in the same band, and the narrator half-speaks them on the downbeats.
"""
NAR, MAMA, MACH, SONG = "NAR", "MAMA", "MACH", "SONG"
VOICES = {NAR: ("af_bella", 1.1), MAMA: ("af_heart", 1.0), MACH: ("am_michael", 0.95)}

LINES = [
    # ---- cold open: the real case, in the first two seconds
    ("c0", NAR, "A computer accused forty thousand people of fraud. It was wrong about most of them.",
     "A computer accused 40,000 people of fraud.| It was wrong about most of them.", 0.45),

    # ---- chapter 1: one little mistake (family sitcom)
    ("a1", NAR, "This is my family. We run a guesthouse on the mountain, and process insurance claims. Don't ask.",
     "This is my family.| We run a guesthouse on the mountain,| and process insurance claims.| Don’t ask.", 0.3),
    ("a2", NAR, "Last spring, Grandpa stamped one claim wrong. One error. One apology. Fixed by Tuesday.",
     "Last spring, Grandpa stamped one claim wrong.| One error. One apology.| Fixed by Tuesday.", 0.4),

    # ---- chapter 2: the machine
    ("b1", NAR, "Then Papa bought a machine. Ten million claims a year, on Grandpa's rules. All of them.",
     "Then Papa bought a machine.| Ten million claims a year,| on Grandpa’s rules.| All of them.", 0.2),
    ("s1", SONG, None, None, 0.0),
    ("b2", NAR, "Now Grandpa's one mistake is in ten million claims. Not one error. Millions.",
     "Now Grandpa’s one mistake is in 10 million claims.| Not one error.| Millions.", 0.3),
    ("b3", NAR, "Automation multiplies everything. What you do right, and what you do wrong.",
     "Automation multiplies everything.| What you do right,| and what you do wrong.", 0.25),
    ("b4", NAR, "And the errors aren't random. The same wrong rule hits the same kind of person, again and again, at machine speed.",
     "And the errors aren’t random.| The same wrong rule hits the same kind of person,| again and again,| at machine speed.", 0.45),

    # ---- chapter 3: a letter for you (the real case, told to you)
    ("d1", NAR, "Now it's you. You lose your job, and file for unemployment insurance.",
     "Now it’s you.| You lose your job,| and file for unemployment insurance.", 0.3),
    ("d2", NAR, "Months later, a letter. A computer says you committed fraud. No human checked.",
     "Months later, a letter.| A computer says you committed fraud.| No human checked.", 0.3),
    ("d3", NAR, "Pay it all back. Plus a penalty four times as big. Plus interest.",
     "Pay it all back.| Plus a penalty four times as big.| Plus interest.", 0.25),
    ("d4", NAR, "They take your wages. They take your tax refund. You did nothing wrong.",
     "They take your wages.| They take your tax refund.| You did nothing wrong.", 0.3),
    ("d5", NAR, "This happened in Michigan. An algorithm alone decided over forty thousand fraud cases. About eighty-five percent were wrong.",
     "This happened in Michigan.| An algorithm alone decided| over 40,000 fraud cases.| About 85% were wrong.", 0.25),
    ("d6", NAR, "People lost their homes. Australia's Robo-debt hit hundreds of thousands more.",
     "People lost their homes.| Australia’s Robodebt| hit hundreds of thousands more.", 0.4),

    # ---- chapter 4: 99.9% in love (the floating dream duet), then the arithmetic
    ("s2", SONG, None, None, 0.0),
    ("e1", NAR, "But it makes a billion decisions. Point one percent of a billion is one million. One million failures.",
     "But it makes a billion decisions.| 0.1% of a billion is one million.| One million failures.", 0.2),
    ("s3", SONG, None, None, 0.0),

    # ---- chapter 5: where a million is too many
    ("f1", NAR, "A million bad ads? You shrug. But one auto-translation turned good morning into attack them, and a man was arrested.",
     "A million bad ads? You shrug.| But one auto-translation turned “good morning”| into “attack them”,| and a man was arrested.", 0.3),
    ("f2", NAR, "But some machines can't afford even one.", "But some machines can’t afford even one.", 0.3),
    ("f3", NAR, "Aircraft. One bad sensor, and the seven-three-seven MAX's automation kept forcing the nose down. Three hundred forty-six people died.",
     "Aircraft.| One bad sensor, and the 737 MAX’s automation| kept forcing the nose down.| 346 people died.", 0.25),
    ("f4", NAR, "Power grids. One software bug silenced the alarms. Fifty-five million people lost power.",
     "Power grids.| One software bug silenced the alarms.| 55 million people lost power.", 0.25),
    ("f5", NAR, "Weapons. A missile-defense clock drifted a third of a second. Twenty-eight soldiers died.",
     "Weapons.| A missile-defense clock drifted a third of a second.| 28 soldiers died.", 0.25),
    ("f6", NAR, "Medicine. One software bug gave six patients massive radiation overdoses.",
     "Medicine.| One software bug| gave six patients massive radiation overdoses.", 0.45),

    # ---- finale
    ("g1", NAR, "So here's the rule. The bigger the scale, and the higher the stakes, the smaller the mistake you can afford.",
     "So here’s the rule.| The bigger the scale, and the higher the stakes,| the smaller the mistake you can afford.", 0.25),
    ("s4", SONG, None, None, 0.0),
    ("g2", NAR, "Somewhere in the next billion decisions is yours.", "Somewhere in the next billion decisions| is yours.", 0.5),
]

# Songs: the band plays in strict time; each lyric line is half-spoken starting on its downbeat, and the guide melody
# follows her words (so voice, tune and the karaoke wipe move together).
SONGS = {
    "s1": dict(style="kayo", bpm=138, intro=4, outro=2, lines=[
        (NAR, "Stamp it, stamp it, day and night!"),
        (NAR, "Ten million claims, so quick, so bright!"),
        (NAR, "It learned from Grandpa, line by line..."),
        (NAR, "his one mistake, ten million times!")]),
    "s2": dict(style="duet", bpm=96, intro=4, outro=2, lines=[
        (MAMA, "Ninety-nine point nine percent..."),
        (MACH, "Trust me, darling. I am almost always right.")]),
    "s3": dict(style="disco", bpm=124, intro=4, outro=2, lines=[
        (NAR, "Point one percent, just a tiny bit wrong,"),
        (NAR, "a billion decisions, a million come along!"),
        (NAR, "Dig them a grave by the garden wall,"),
        (NAR, "ninety-nine point nine, and we buried them all!")]),
    "s4": dict(style="show", bpm=138, intro=4, outro=4, lines=[
        (NAR, "Start it small before it runs on all,"),
        (NAR, "let a person answer when you call,"),
        (NAR, "watch for the mistake that keeps coming back,"),
        (NAR, "and keep a big red button on the track!")]),
}
LYRIC_SHOWN = {        # how the lyric reads on screen when it differs from what is spoken
    "Ninety-nine point nine percent...": "99.9 percent…",
    "Point one percent, just a tiny bit wrong,": "0.1 percent, just a tiny bit wrong,",
    "ninety-nine point nine, and we buried them all!": "99.9, and we buried them all!",
}

# The motif: the family guestbook, where every claim is logged. One red X on page one; at the end it is a mountain.
CLAIMS_PER_YEAR = 10_000_000
DECISIONS = 1_000_000_000
FAIL_RATE = 0.001
