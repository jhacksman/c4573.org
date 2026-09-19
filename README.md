# c4573.org

Static site (GitHub Pages, CNAME `c4573.org`). No build step.

## Adding a blog post

1. Copy the most recent `blog/*.html` and replace: `<title>`, `meta description`,
   `og:title`, `og:description`, `og:url`, `canonical`, `<h1 class="blog-title">`,
   `<p class="blog-meta">` (date), the `<audio src>` slug, the body paragraphs, and the
   footer blurb above `</div></section>`. Everything else (CSS, nav, player, footer, script)
   stays byte-identical across posts.
2. Add an entry at the top of `blog/index.html`. Only the newest post carries
   `<span class="badge badge-available">New</span>`; older entries keep an empty span
   (the empty span preserves card layout).
3. Render audio to `audio/<slug>.mp3` (see below).
4. Commit locally. Publishing is the boss's call.

If the post has a target runtime, budget **2.36 narrated words per second** for a
quote-heavy essay (see the 2026-09-18 and 2026-09-19 lessons): a 20-minute read is ~2,830
words, not 3,100. "Narrated words" includes the `<h1>` and every `<h2>`, and excludes `<h3>`
— the renderer only extracts `h1`, `h2` and `p`, so anything written as `<h3>`, a bare
`<blockquote>` or a list is silently left out of the audio.

Write the per-section word budget **before** the prose and measure after every draft pass.
Counting by eye does not work; see the 2026-09-19 lessons.

## Blog audio

Convention: single-voice narration, 44.1 kHz mono 128k MP3, `loudnorm` to -16 LUFS,
TP -1.5 dBTP. Two renderers:

- `render_blog_audio.py blog/<slug>.html` — macOS `say` with Ava (Premium). Local, no GPU.
- `render_blog_audio_fry.py blog/<slug>.html` — `stephen_fry` cloned voice on the quato
  Qwen3-TTS server (`http://10.9.10.9:7849`, Swagger at `/docs`). Requires `requests`.
  Segment WAVs and `joined.wav` land in `/tmp/<slug>-fry/`; pass `--normalize-only` to
  redo just the loudness step from `joined.wav`.

Run long renders under `screen -dmS c4573-fry ...` and read the log; don't poll.

### quato TTS lessons (2026-09-04)

- Fire every paragraph as its own `/speak` request at once with `timeout: 0`; the server
  queues and dispatches to the least-loaded GPU. 10 segments / 273 words took ~3 min wall
  on 2 GPUs with no cold start.
- Wrap each segment as `— text —` (dtfftl convention) so the cloned voice doesn't clip the
  first syllable. Fry rendered 5- and 6-word segments cleanly with this.
- Runaway check: re-render if audio >= 2x expected duration at 2.3 words/sec, with a
  4-second floor for tiny segments so a 2.6-second expected clip isn't flagged by padding.
- Fry's output is peakier than Ava's. Single-pass `loudnorm` lands ~-17.5 LUFS and a
  linear two-pass stops at -17.0 because the -1.5 dBTP ceiling caps the gain. The script
  therefore adds the residual gain into `alimiter` at -1.5 dBTP after the two-pass.
  Existing posts measure between -16.5 and -19.2 LUFS.

### Full-length render lessons (2026-09-04, Chicken Little, 54 segments / 2,241 words)

- Segmentation: `<h1>` title and each `<h2>` heading are their own short segment (period
  appended if missing) with a 1.0 s gap before and 0.8 s after a heading; paragraphs get
  0.6 s. Em-dashes inside a paragraph split into sub-segments with a 0.35 s gap. Each
  clip is trimmed to 0.15 s of edge silence before concat so the gaps are exactly what
  the constants say. Result: no silence >= 1.5 s anywhere in a 14.7 min join.
- Abbreviation substitutions (`GPU` -> `G.P.U.`) leave `G.P.U..` at a sentence end;
  collapse `..` after substituting.
- Fry's pace is not 2.3 words/sec. Batch median was 2.61 w/s; 13–52 word segments ran
  20–33% fast, 80–120 word segments ran near 2.3, and 5–6 word segments ran slow from
  the em-dash padding. A fixed-reference +/-15% pace check flags most of the piece and
  triples the render (the first run burned 10 min doing exactly that). The script now
  renders everything once, takes the median pace of segments >= 12 words, and only
  re-renders outliers vs. that median, keeping the attempt closest to it. Runaway
  detection still uses the fixed 2.3 w/s reference.
- Pace outliers are mostly stable: 7 of 13 flagged segments came back within 1–3 points
  of the same deviation on all three attempts. That is the voice's delivery of that
  text, not a defect. Re-rendering fixed 6.
- Per-attempt WAVs are kept as `seg_NN.tryK.wav` and reused on restart, so killing a run
  costs nothing already rendered. If you do kill a run, also clear the server queue:
  `DELETE /gpu/{0,1}/queue` (check `GET /jobs` first; cancelled ids are returned).
- quato had 2 GPUs in service (0 and 1), not 3. With 54 requests queued at once, each
  request's wall time grew to 400–800 s; phase 1 took ~38 min for 14.7 min of audio
  (~2.6x realtime aggregate) with no cold start. Budget 45–60 min end to end for a
  2,000+ word post including the outlier passes.
- Spot-check narration with `whisper <mp3> --model base.en --output_format txt` (the
  `/opt/homebrew/bin/whisper` CLI) and diff against `/tmp/<slug>-fry/segments.txt`.

### Long-post lessons (2026-09-18, d/acc, 74 segments / 3,255 words / 22:50)

- **Fry's pace is text-dependent; 2.61 w/s is not a constant.** This post ran 2.38 w/s end to
  end (3,255 words in 1,370 s) against Chicken Little's 2.61. The difference is paragraph
  shape: quote-dense 50–100 word paragraphs sit near 2.3–2.4, while the short punchy
  paragraphs that ran 20–33% fast in the earlier post were rarer here. Budget 2.4 w/s for
  quote-heavy essays. Predicting 20 minutes from 3,100 words produced 22:50 instead.
- **Em-dash splitting inflates the segment count ~20%.** 60 HTML blocks became 74 TTS
  segments. Estimate wall time from segments, not paragraphs.
- **Slashed names need a PRONOUNCE entry or the voice reads the slash.** Added
  `d/acc -> dee-ack`, `e/acc -> ee-ack`, `offense/defense -> offense-defense`, plus AGI, BCE,
  ID. Use a hyphen in the replacement, never an em-dash, or the substitution creates a
  spurious segment break.
- **Probe a recurring term before committing to a render.** One `POST /speak` with a test
  sentence plus `whisper` on the WAV costs ~30 s and confirmed "dee-ack" before spending an
  hour on 74 segments. Worth it for any term that appears dozens of times.
- **Timing, 2 GPUs, no cold start:** phase 1 (74 segments) ~37 min, two outlier passes ~16 min,
  53 min total for 22.8 min of audio. 14 segments re-rendered, 7 kept with residual pace flags
  — the same "that is just the voice's delivery of that text" pattern as before.
- Output measured -16.4 LUFS integrated, true peak -1.6 dBFS, no internal silence >= 1.5 s.
- **The WAV cache is keyed by segment index only, not by text.** Editing the post and re-running
  will happily splice old audio into new positions. `rm -rf /tmp/<slug>-fry` before any re-render
  that follows a text change; only use the cache to resume an interrupted run of identical text.
- **Two full renders of this post put the pace at 2.376 and 2.357 w/s** (3,255 words / 1,370 s
  and 3,311 words / 1,405 s). Treat ~2.36 w/s as the planning figure for this kind of essay.
- Parentheticals like `(!!)` inside a quotation are dropped silently rather than garbled — safe
  to leave in the prose.
- **Spot-check with `--model small.en`, not `base.en`.** base.en mangled "aggression" into
  "Jian" and "weighted" into "waited" on clean audio; small.en transcribed both correctly.
  Do not re-render a segment on the strength of a base.en diff alone.

### Rewrite lessons (2026-09-19, d/acc rewrite, 68 segments / 2,833 words / 19:48)

- **2.36 w/s held, third measurement.** 2,833 words in 1,188 s is 2.384 w/s end to end,
  against 2.376 and 2.357 on the two previous full renders of this essay. Planning at 2.36
  predicted 19:59 and produced 19:48. Treat 2.36 as settled for a quote-heavy essay.
- **Prose written to a word budget overshoots 15–20% per pass.** Landing 2,830 took four
  measured passes: 3,730 → 3,410 → 3,180 → 2,842 → 2,833. Every one of them felt like it was
  already at target. Write the per-section budget table *before* the prose, then run the
  h1+h2+p counter after each pass. Estimating paragraph length by eye does not work, and the
  error compounds in one direction.
- **Cutting is easier by paragraph than by word.** The shaving passes recovered ~15 words per
  section; the cuts that actually moved the number were dropping whole passages — a
  scene-setting tour, a standalone section folded into one paragraph, a caveat about material
  the rewrite no longer contained.
- **Dry-run `extract_segments()` before rendering.** Two seconds, and it reports the real
  segment count, the post-substitution word count, uncovered acronyms, `..` artifacts, leftover
  slashed terms, and the shortest segments. Cheaper than discovering any of it 40 minutes in.
- **Em-dash splitting can strand a one-word segment.** `Mozi — Mo Di, Master Mo — turns up…`
  split into a 1-word clip, `Mozi`. Headings at 3–5 words render cleanly, but use commas
  instead of em-dashes wherever a split would leave fewer than three words.
- **The cache wipe is not theoretical.** `/tmp/dacc-has-a-build-order-fry/` held 247 segment
  WAVs from the previous render of *different* text. Wiped before this run; the whisper diff
  then showed no contiguous block mismatches, which is the signature a splice would leave.
  A clean whisper diff is the only proof the wipe worked.
- **`segments.txt` contains the kind labels** (`title`, `para`, `heading`, `dash`), which are
  not narrated. Strip them before diffing against a transcript or they show up as dozens of
  spurious deletions.
- **Timing, 2 GPUs, no cold start:** phase 1 (68 segments) ~38 min, two outlier passes ~7 min,
  45 min total for 19.8 min of audio. Batch median 2.47 w/s over the 57 segments >= 12 words.
  16 re-rendered, 7 kept with residual pace flags — the same "that is the voice's delivery of
  that text" pattern as the two previous posts.
- **small.en artifacts to ignore, confirmed again** (0.9323 similarity, zero real errors):
  homophones (compliment/complement, weighted/waited, queue/cue), British orthography from
  Fry's accent (defence, decentralised, favouring, judgements), and proper nouns the model does
  not know — Mozi → "mosey", Buterin → "butrin", Qin Guli → "kin ghuli", Jarzynski-Crooks →
  "jarsinski kruchs", Yudkowsky → "yudkovsky". The `dee-ack` / `ee-ack` substitutions come back
  as "deac" / "e aq", which confirms they fired. None of this justifies a re-render.
- Output measured -16.45 LUFS integrated, true peak -1.69 dBFS, no internal silence >= 1.5 s.
