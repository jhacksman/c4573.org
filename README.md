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
