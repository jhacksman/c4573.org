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
