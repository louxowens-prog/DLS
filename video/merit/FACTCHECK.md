# INELIGIBLE: fact-check notes

Every claim spoken or shown on screen is listed here with its source and wording notes. Iris is invented. Her story
is a composite of documented cases (see the last section), and the screen says so: "DRAMATISATION · BASED ON
DOCUMENTED CASES" appears as she is introduced.

## The narration

| Line | Claim | Source and notes |
|---|---|---|
| i1 | AI learns from human records: prejudice, inequality, stereotypes and the people never counted. | NIST AI RMF 1.0 (2023), §3.7, names three kinds of AI bias: **systemic** (societal and institutional), **computational and statistical** (often non-representative samples, i.e. sampling bias) and **human-cognitive**. The on-screen cards list the six sources from the brief: prejudice, historical inequality, stereotypes, sampling bias, cultural assumptions and institutional discrimination. |
| i2 | Face AI got darker-skinned women's gender wrong up to 35% of the time; lighter-skinned men, under 1%. | Buolamwini & Gebru, *Gender Shades* (FAT* 2018). Three commercial gender classifiers had error rates up to **34.7%** for darker-skinned women and at most **0.8%** for lighter-skinned men. The benchmark datasets used in the field were 79.6% and 86.2% lighter-skinned. On screen: 34.7% and 0.8%. |
| p1 | Train on years of hiring where most leaders were men, and it learns that men look like leaders. | The brief's own example. It is also exactly what happened in the case on the next line. |
| p2 | A tech giant built one; it taught itself to downgrade any CV containing "women's"; it was scrapped. | Reuters (Dastin, 10 Oct 2018). The tool gave candidates scores from one to five stars, so the screen shows a star rating dropping and the words "RANKED LOWER"; no numbers are invented. The models were trained on 10 years of CVs, mostly from men, and the system "taught itself that male candidates were preferable". It penalised CVs that included the word "women's", as in "women's chess club captain". Amazon disbanded the team by early 2017, and the company says recruiters never relied solely on its rankings. The company is not named on screen (no real brands). |
| p3 | The machine feels no sexism; it learned a pattern; the outcome is still discrimination. | The brief's point, kept almost word for word. |
| p4 | "Delete the word, and it can still find stand-ins: a postcode, a hobby, a gap in your CV." | Said as a possibility, not as something that system was shown to do. Reuters again. After the word was neutralised, "that was no guarantee that the machines would not devise other ways of sorting candidates that could prove discriminatory". Obermeyer et al. (*Science*, 2019) show the same proxy effect in health care: spending stood in for need, so Black patients had to be sicker to be flagged for extra care. Postcodes standing in for race is the classic redlining proxy. |
| m1 | A biased manager can reject a few people a day; an algorithm can reject millions. | An illustration of scale. In *Mobley v. Workday* (N.D. Cal.), the court conditionally certified a nationwide age-discrimination collective in May 2025. The collective may cover millions of applicants screened by one vendor's AI tools. |
| m2 | "NIST, the US standards agency, warns AI can increase the speed and scale of harmful bias." | NIST AI RMF 1.0, §3.7: "AI systems can potentially increase the speed and scale of biases and perpetuate and amplify harms to individuals, groups, communities, organizations, and society." The same section opens: "Bias … can become ingrained in the automated systems that help make decisions about our lives." |
| v1 | Denied a job, insurance, a home, a loan, a place at university, benefits. | The brief's list: employment, insurance, housing, credit, admission and benefits. |
| v3 | "The system has determined you are ineligible." | The brief's line. |
| v4 | Hundreds of variables; no one who can explain; you can argue with a clerk, not with a score. | The brief: opaque automated bureaucracy can be worse than the human kind. The cloud of variables and weights is marked on screen "ILLUSTRATION · NOT A REAL MODEL"; the score on the clerk's window is illustrative too. |
| v5 | In the Netherlands, a fraud algorithm treated foreign nationality as a risk; tens of thousands of families were wrongly accused; the government resigned. | Amnesty International, *Xenophobic Machines* (Oct 2021). Dutch nationality (yes/no) was a risk factor in the risk-classification model the Dutch tax authority used on childcare-benefit claims; the insert shows that column and the flags (file numbers are invented). Tens of thousands of parents and carers were falsely accused of fraud, and the government resigned in January 2021. |
| e1 | AI isn't born biased; it inherits us. NIST: trustworthy AI is transparent, accountable, explainable, reliable, privacy-enhanced, and fair with harmful bias managed. | NIST AI RMF 1.0, §3, lists the characteristics of trustworthy AI as valid and reliable; safe; secure and resilient; accountable and transparent; explainable and interpretable; privacy-enhanced; and fair, with harmful bias managed. The narration names the six the brief stresses. The on-screen tablet lists all seven. |
| e2 | "So when a machine alone decides about you, ask: what data? Who checked it? How do I appeal? In the EU and UK, you can demand a human review." On screen: "THE RIGHT TO A HUMAN, for decisions made solely by machine with legal or similarly significant effects." | The line is scoped to decisions made by a machine alone, and the screen gives the legal scope. EU: GDPR Art. 22 gives a right not to be subject to solely automated decisions with legal or similarly significant effects. Where such decisions are allowed, Art. 22(3) gives the right to "obtain human intervention … and to contest the decision". UK: the Data (Use and Access) Act 2025, s.80, in force from 5 February 2026, permits more solely automated decisions. New Art. 22C requires safeguards that let the person get information, make representations, **obtain human intervention** and contest the decision. |

## The real-life scenario (Iris)

Iris is fictional: 49, an engineer for twenty years, 70 applications and 70 rejections arriving within minutes, in the
middle of the night. Every detail comes from documented cases:
- **Night-time rejections within minutes:** Derek Mobley's applications through AI screening "were rejected, sometimes
  within minutes, occasionally in the middle of the night" (*Mobley v. Workday*; the ADEA collective was certified in May 2025).
- **"Rental application: high risk / recommendation: decline":** In *Louis v. SafeRent* (D. Mass.), Mary Louis's
  tenant-screening score of 324 came back "Score recommendation: DECLINE". The case settled for $2.275M (final approval
  November 2024), and the score can no longer be used for voucher holders.
- **Age, a care gap, a women's club as possible hidden reasons:** Age (Mobley), the word "women's" (Reuters/Amazon) and
  stand-in variables (Obermeyer) are each documented. The point of the scene is that Iris cannot find out which one sealed it.

## The twist

"You've been scored. You just haven't been told." The FTC staff report *A Look Behind the Screens* (September 2024)
found that the major social media and video-streaming services engaged in "vast surveillance" of users. They fed
users' personal information into automated systems, with few ways to opt out, and shared it broadly.

## Wording choices

- "Up to 35%" and "under 1%" are rounded from 34.7% and 0.8%; the exact figures are on screen.
- "A tech giant" and "a fraud algorithm" avoid naming companies, people or products, per the brief.
- NIST is the US National Institute of Standards and Technology, a federal standards and measurement agency ("the US standards agency").

## Sources
- [NIST AI Risk Management Framework 1.0 (NIST AI 100-1, 2023)](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf)
- [Gender Shades (MIT Media Lab publication page)](https://www.media.mit.edu/publications/gender-shades-intersectional-accuracy-disparities-in-commercial-gender-classification/) and [the paper (PMLR 81)](https://proceedings.mlr.press/v81/buolamwini18a.html)
- [Reuters: Amazon scraps secret AI recruiting tool that showed bias against women (via HR Reporter)](https://www.hrreporter.com/focus-areas/recruitment-and-staffing/amazon-scraps-secret-ai-recruiting-tool-that-showed-bias-against-women/287026)
- [Obermeyer et al., racial bias in a health-care algorithm (Chicago Booth Review)](https://www.chicagobooth.edu/review/2019/october/how-racial-bias-infected-major-health-care-algorithm)
- [Amnesty International: Xenophobic Machines, the Dutch childcare benefits scandal](https://www.amnesty.org/en/latest/news/2021/10/xenophobic-machines-dutch-child-benefit-scandal/)
- [Mobley v. Workday: conditional certification of the ADEA collective (Proskauer)](https://www.proskauer.com/blog/ai-bias-lawsuit-against-workday-reaches-next-stage-as-court-grants-conditional-certification-of-adea-claim)
- [Louis v. SafeRent: settlement (Fortune)](https://fortune.com/2024/11/21/renter-scoring-saferent-million-settle-case-algorithm-discriminating-race-income) and [case summary (Cohen Milstein)](https://cohenmilstein.com/case-study/louis-et-al-v-saferent-solutions-et-al)
- [GDPR Article 22](https://gdpr-info.eu/art-22-gdpr/)
- [UK Data (Use and Access) Act 2025, section 80](https://www.legislation.gov.uk/ukpga/2025/18/section/80/enacted) and [GOV.UK guidance on the changes](https://www.gov.uk/guidance/data-use-and-access-act-2025-data-protection-and-privacy-changes)
- [FTC staff report: A Look Behind the Screens (summary, Hunton)](https://www.hunton.com/privacy-and-cybersecurity-law-blog/ftc-publishes-staff-report-on-data-practices-of-social-media-and-video-streaming-services)
