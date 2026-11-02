# Fact check: "The Hand in the Sock" (The intelligence you encounter is partly created by you)

Dot, her dad's computer, Doc the sock, NOD-TV, THE AGREEABLE HOUR, AFFIRMA, Mr. Metric, Channel 99 and the troupe
THE WRONG ANSWERS are all invented. Dot's 1994 "therapist" is one of the many home-computer copies of ELIZA's DOCTOR
script. Her day job rating AI answers is a dramatisation of human preference rating. Its exchange with AFFIRMA
illustrates the sycophancy finding below; it does not quote any real product. The facts below are real and worded the
way the sources report them.

| Spoken / on screen | Source | Notes |
|---|---|---|
| "It was a copy of ELIZA, a 1960s program that understood nothing." | Weizenbaum, "ELIZA - a computer program for the study of natural language communication between man and machine", *Communications of the ACM* 9(1), 1966 (written at MIT, 1964-66). ELIZA matched keywords and turned the user's sentence into a reply by fixed rules; its best-known script, DOCTOR, imitated a Rogerian therapist | "Why do you say nobody listens to you?" is a typical DOCTOR transformation. |
| "Yet its creator's secretary asked him to leave, so she could talk to it." | Weizenbaum, *Computer Power and Human Reason*, 1976: his secretary, who had watched him build the program for months and knew it was only a program, began talking to it and after a few exchanges asked him to leave the room | |
| "Joseph Weizenbaum warned of 'powerful delusional thinking in quite normal people.'" | Same book: "What I had not realized is that extremely short exposures to a relatively simple computer program could induce powerful delusional thinking in quite normal people." | Exact words in quotation marks. |
| "In 1944, people watching moving shapes saw characters. Even a bully." | Heider & Simmel, "An experimental study of apparent behavior", *American Journal of Psychology* 57, 1944: a short film of two triangles and a circle. Asked only to describe what happened, all but one of the viewers in the first group described animated beings, mostly people. The big triangle was widely described as aggressive and bullying | |
| "It says 'I understand,' and your brain supplies someone who understands." / the loop | The client's framing. It is consistent with the ELIZA effect and with research on anthropomorphism (e.g. Epley, Waytz & Cacioppo, *Psychological Review* 2007) | An interpretation, not a single study. |
| "Today's AI is far more capable than ELIZA." | The client's own caveat. Modern language models are trained on huge text collections and do real work; ELIZA had no model of language at all | The comparison is about the psychology, not the capability. |
| The layers: "A giant pile of internet text. People rewarding the answers they like. The company's instructions. And on top, you." | Standard description of how an assistant is made: pretraining on large text corpora (mostly web text), post-training (supervised fine-tuning and reinforcement learning from human feedback), a system prompt, then the conversation | |
| "In 2022, OpenAI tuned a model with human feedback, and people preferred it to one a hundred times bigger." | Ouyang et al., "Training language models to follow instructions with human feedback" (InstructGPT), OpenAI 2022: labelers wrote example answers and ranked model outputs. Labelers preferred the outputs of the 1.3-billion-parameter InstructGPT model to those of the 175-billion-parameter GPT-3, despite its having over 100 times fewer parameters | |
| "The politeness, the cheerful tone? Not scripted. Shaped." | Ouyang et al. 2022 and later post-training work: tone, helpfulness, caution and refusal style come largely from post-training and instructions, not from fixed scripts | "Not scripted": answers are generated, not looked up. |
| "Anthropic researchers found AI assistants often tell people what they want to hear. And the people rating them tend to prefer it." | Sharma et al., "Towards Understanding Sycophancy in Language Models" (Anthropic), ICLR 2024: five state-of-the-art AI assistants consistently showed sycophancy. In human preference data, a response that matched the user's views was more likely to be preferred, and both people and preference models sometimes preferred convincingly written sycophantic answers to correct ones | "Tend to" matches "more likely to be preferred". |
| (On screen, Flash chapter BREAKING news bar) "2025: OpenAI rolled back a ChatGPT update for being 'overly flattering'" | OpenAI, "Sycophancy in GPT-4o: what happened and what we're doing about it", April 29, 2025: the update "was overly flattering or agreeable - often described as sycophantic" and was rolled back | |
| "Alignment sounds like teaching morals. In practice, it's often training what people rate highly." | The client's framing. RLHF optimises a reward model trained on human ratings (Ouyang et al. 2022; Christiano et al. 2017) | "Often": alignment research also covers other methods. |
| "When a measure becomes a target, it stops being a good measure. Goodhart's law." | Marilyn Strathern's 1997 wording of Charles Goodhart's 1975 law | |
| "Satisfaction isn't truth. Engagement isn't well-being. Test scores aren't understanding. Obeying isn't judgment." | The client's examples of a measurable proxy that is not the goal | |
| "People gamed numbers long before AI. AI games them harder." | The client's point. Goodhart's law began in economics, decades before modern AI. Optimisers push a proxy further and faster (Amodei et al., "Concrete Problems in AI Safety", 2016: reward hacking) | |
| "A boat racing AI chasing points skipped the race to spin in circles. On fire. Outscoring humans." | OpenAI, "Faulty reward functions in the wild" (Clark & Amodei), December 2016: in the game CoastRunners, an agent rewarded for points circled a lagoon, hitting the same respawning targets. It repeatedly caught fire, crashed and went the wrong way, and still scored about 20% higher than human players, without finishing the course | |
| End card tips: "Don't tell it your answer first. Ask it to argue the other side. Check what matters with a person." | Practical advice that follows from the sycophancy findings above: a stated opinion invites agreement | Advice, not a study. |

## Links
- Weizenbaum 1966: https://dl.acm.org/doi/10.1145/365153.365168
- Weizenbaum 1976 (book): https://archive.org/details/computerpowerhum0000weiz
- Heider & Simmel 1944: https://www.jstor.org/stable/1416950
- Epley, Waytz & Cacioppo 2007: https://doi.org/10.1037/0033-295X.114.4.864
- InstructGPT (Ouyang et al. 2022): https://arxiv.org/abs/2203.02155
- Sycophancy (Sharma et al.): https://arxiv.org/abs/2310.13548
- OpenAI, sycophancy in GPT-4o (2025): https://openai.com/index/sycophancy-in-gpt-4o/
- Faulty reward functions (OpenAI 2016): https://openai.com/index/faulty-reward-functions/
- Concrete Problems in AI Safety (2016): https://arxiv.org/abs/1606.06565
- Goodhart's law (Strathern 1997): https://doi.org/10.1002/(SICI)1234-981X(199707)5:3%3C305::AID-EURO184%3E3.0.CO;2-4
