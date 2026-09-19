# PLAN — rewrite of blog/dacc-has-a-build-order.html

Full rewrite, not a patch. Draft under review: commit 1c12569, 3,329 narrated words, 23:24.

## Why

1. **The enemy goes unnamed.** Every other post on this site names companies with receipts.
   The draft argues against abstract camps. "Landlord's terms" appears once, in the
   second-to-last section. Fix: the technofeudal frame opens the piece and runs through
   every section. Rent, tolls, chokepoints, landlords.
2. **It never stress-tests itself.** Three Companies has "What We Don't Know." Ghost GDP has
   "Where Citrini Overreaches." Chicken Little concedes the acorn was real. This draft's only
   concession is scoped to Mozi sourcing — it audits the evidence and never audits the thesis.
   Fix: a new section making the strongest case against d/acc, with a real concession.
3. **Runtime.** Target 20:00. Draft renders 23:24.

## Budget

**2,830 narrated words, hard ceiling 2,880.** Pace figure: **2.36 w/s** (two measured full
renders of this essay: 2.376 and 2.357). 2,830 / 2.36 = 1,199 s = **19:59**.

Not 2.61 w/s — that is the Chicken Little figure for a different paragraph shape, and using
it caused both previous misses.

Narrated words = `<h1>` + every `<h2>` + every `<p>` between `<h1 class="blog-title">` and
`<hr>`. `<h3>`, bare `<blockquote>` and lists are silently absent from the audio. Nothing
load-bearing goes in them.

## Sections

| # | Section | Budget | Was |
|---|---|---:|---:|
| 1 | Title + open (technofeudal frame, receipts) | 220 | 195 |
| 2 | Where the Term Came From | 240 | 328 |
| 3 | Decentralize, Encrypt, Accelerate | 120 | 231 |
| 4 | "Math-Backed" Is the Wrong Compliment | 240 | 324 |
| 5 | Mozi Belongs to d/acc, Not to Effective Altruism | 450 | 802 |
| 6 | The Case for e/acc, Made Properly | 285 | 405 |
| 7 | The Case for the Safety Camp, Made Properly | 265 | 356 |
| 8 | What a Build Order Looks Like on a Workbench | 265 | 274 |
| 9 | **The Strongest Case Against This** (NEW) | 320 | — |
| 10 | Where We Part Company | 165 | 165 |
| 11 | Pick the Direction | 220 | 249 |
| | **Total** | **2,790** | 3,329 |

40 words of headroom against the 2,830 target, 90 against the ceiling.

## What gets cut

- **Mozi, -352.** The Warring States scene-setting, the elaboration of why aggression is theft,
  and half the quote apparatus. Keep: the artisan/engineer sourcing, *jian ai* and *fei gong*,
  "far from being pacifists," chapters 52–71 to Qin Guli, all five caveats compressed to one
  paragraph, the Farcaster double-cast and its correction, the effective-altruism contrast, the
  centralization limit. The argument survives; the tour does not.
- **Cypherpunk section, -111.** Two of three Hughes quotes go. Keep the no-traceable-author
  finding and the 1993-03-09 anchor.
- **"Math-Backed", -84.** Bostrom's second (nanotech sequencing) quote goes. Buterin's
  concession on the classification problem *moves* to section 9, where it does more work.
- **Where the Term Came From, -88.** Andreessen / OpenAI-board scene-setting compresses to
  one clause. The four d's and the Switzerland-vs-feudalism line stay in full — that line is
  now the hinge of the whole piece.
- **e/acc, -120 and Safety, -91.** Quote length only. No argument is dropped from either
  steelman; both keep every receipt.

## Section 9 — the self-stress-test

Not a strawman. The strongest available case:

- The offense/defense classification problem is not an edge case, it is the center. Every
  defensive technology is a capability and capabilities are dual-use by construction.
  Formal verification hardens your code and hardens malware. A vaccine platform is the same
  bench as gain-of-function. Encryption — this site's cleanest example — protects a dissident
  and a ransomware crew with the same primitive.
- Jervis's second variable fails: postures are not distinguishable. Bostrom's differential
  development assumes you can rank in advance; usually you can only rank in retrospect.
- "Defense-favoring" is a judgment call made by whoever is building, the party least able to
  be neutral about it. Every camp already believes it is building the defensive thing —
  Altman thinks licensing is defense, Yudkowsky thinks the ban is defense.
- A build order everyone agrees with and nobody can apply is not a build order. It is a mood
  with better vocabulary.

**Concede:** all of that survives. There is no test that returns offensive or defensive.
Anyone who says the framework settles the question is selling something.

**Answer, honest and partial:** the framework does not need to classify every technology. It
needs one question that is actually answerable — does the thing, once built, require a
permanent operator? Can the person it protects copy it and run it, or does somebody have to
keep a hand on a switch forever? That test does not sort technologies. It sorts chokepoints.
And the chokepoint is the failure mode this site exists to fight.

**Residual concession:** it still will not tell you whether a given bio tool is net offensive.
It tells you who will own it. That is less than a theory of technology and more than any other
camp is offering.

## Carried forward unchanged

Every verified citation in the draft, and both disagreements with Buterin (the soft pause
fails its own test; the open-weights hedge is unacceptable as a plan). The bootstrapism close.
The hackerspace paragraph, strengthened. No new facts without a primary source.

## Render

1. `rm -rf /tmp/dacc-has-a-build-order-fry` **before rendering.** The WAV cache is keyed by
   segment index, not text. A rewrite shifts every index; reusing the cache splices old audio
   into new positions and produces a file that sounds fine and says the wrong thing.
2. `screen -dmS c4573-fry`, read the log, do not poll. Budget 45–60 min.
3. Measure duration, integrated LUFS (-16 target), true peak, internal silence >= 1.5 s.
4. Spot-check with `whisper --model small.en`. Not base.en.

## Pronunciation

Keep d/acc, e/acc, offense/defense, AGI, BCE, ID. Headings avoid bare acronyms — "Effective
Altruism" spelled out rather than "EA" — and an `EA` entry gets added as a backstop. Hyphens
in replacements, never em-dashes.
