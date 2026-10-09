# RULES.md — c4573.org

Project rules and hard-won lessons. Read before changing anything here.
Post-authoring and audio-rendering process lives in `README.md`; this file is for the
site's code.

## Boris Cherny method (mandatory)

1. **PLAN** — write the approach before coding
2. **EXECUTE** — implement it
3. **VERIFY** — prove it in a real browser, not by reading the diff
4. **DOCUMENT** — record lessons here

## Git discipline

- Commit after each logical change, meaningful messages.
- **Never commit audio.** `audio/*.mp3` is content, not source history.
- Publishing is the boss's call. Commit locally; do not push unless told to.

## Layout of the site

No build step. Static HTML served by GitHub Pages (`CNAME` = c4573.org).

- `css/style.css` — every shared style, including the blog audio player
- `js/audio-player.js` — the blog audio player behavior
- `blog/*.html` — one file per post; each has a small inline `<style>` for `.blog-*`
  rules and nothing else
- `blog/index.html` and `blog/spacex-starbase-property-records.html` have no player

Posts reference shared assets **relatively** (`../css/style.css`, `../js/audio-player.js`),
not from the site root. Match that when adding a new asset.

## Blog audio player

### Markup contract

A post carries exactly this, and nothing else player-related:

```html
      <!-- Audio Player -->
      <div class="audio-player-wrapper" id="audioWrapper">
        <div class="audio-player">
          <div class="audio-label">🔊 Listen to this post</div>
          <audio id="blogAudio" src="../audio/<slug>.mp3" preload="metadata" controls></audio>
        </div>
      </div>
```

plus `<script src="../js/audio-player.js" defer></script>` before `</body>`.

`js/audio-player.js` self-initializes on any page containing `.audio-player-wrapper`.
It reads nothing from inline attributes — **never add an `onclick` to a player control.**
It builds the whole transport, including the sticky `IntersectionObserver`, so a post
needs no inline player CSS or JS at all.

### Why the native controls are gone

`<audio controls>` chrome cannot be re-laid-out — the shadow DOM is not addressable, so
a custom arrangement (speed dropdown bottom-right, seek bar absorbing the width, skip
buttons between seek and volume) is only reachable by removing `controls` and building
the transport. The markup still *ships* `controls`; the script strips it on init. That is
the graceful-degradation story: **JS off gets working native controls, JS on gets the
custom bar, and neither state shows a dead control.** Keep the attribute in the markup.

### Persistence

Speed and volume live in `localStorage` under `c4573:audio:rate` and
`c4573:audio:volume`, so a reader's choice follows them from post to post. Reads are
wrapped in try/catch — Safari private mode throws on `localStorage`.

## Lessons

### `python3 -m http.server` cannot test audio seeking (2026-10-09)

`SimpleHTTPRequestHandler` **ignores the `Range` header** and answers `200` with the
entire body. Chrome responds by collapsing `currentTime` to `0` on any seek past the
buffered region, and the media element then refuses every subsequent `currentTime`
assignment. Symptom: seek, −10s and +10s all appear completely broken while play/pause,
volume and speed work fine.

This is the *server*, not the player. GitHub Pages serves `206 Partial Content`
correctly. Verify media with a range-capable server; `curl -D- -H 'Range: bytes=0-99'`
against it must return `206`, not `200`.

### mp3 `duration` is revised upward mid-playback

Chrome reports an estimate from the header, then corrects it after reading more of the
file: 742.05 s became 744.28 s on `three-companies.mp3` during one test run. Any
assertion of the form `|currentTime - duration| < small` is flaky by construction, and
anything that caches `duration` at init will drift. Read `audio.duration` at use time,
and clamp against `seekable.end()` when the exact end matters.

### Do not trust `progress` alone for the buffered bar

`progress` can stop firing before `loadedmetadata`, so a buffered-range painter wired
only to `progress` computes nothing (duration is still 0) and then never runs again.
Against a 206 server the whole file can arrive in one chunk and the bar stays empty.
Repaint from `timeupdate` / `canplay` / `loadedmetadata` as well.

### Compare vertical *centers*, not box tops, when asserting rows

Flex `align-items: center` means a 34 px button and a 19 px time label on the same line
have `y` values 7 px apart. Asserting "same row" on `getBoundingClientRect().y` fails on
a correct layout. Bucket on `y + height / 2`.

### Read pixels, not resized screenshot previews

A downscaled screenshot preview showed a convincing gray triangle in the card's
bottom-left corner that does not exist: every pixel in that region samples exactly
`rgb(22,27,34)`, the surface color. When a screenshot shows something surprising, sample
the pixels with PIL before changing code to chase it.

### The sticky wrapper's negative margin must match `.container` padding

`.audio-player-wrapper` uses `margin: 0 -1.25rem; padding: 0 1.25rem` so the sticky card
spans the container gutter. `.container` drops to `padding: 0 1rem` at ≤480 px, so the
card hung 4 px past the viewport on each side and `scrollWidth` exceeded `clientWidth` on
every phone. This shipped unnoticed for the life of the old player. The ≤480 px block now
overrides the wrapper to `-1rem`. **If `.container`'s padding ever changes, change the
wrapper to match.**

### Inline `<style>` rules carry their leading comment

When splitting an inline stylesheet into rules at brace depth 0 to filter some out, the
`/* Audio Player */` comment attaches to the front of the *next* rule, so a selector test
anchored with `^\s*\.` silently skips it. Strip comments before matching. This left one
orphaned `.audio-player-wrapper` rule in all 16 posts on the first migration pass.

### Per-post variance is real — survey before bulk-editing

The 16 posts were documented as byte-identical outside the post body. They were not:

- `texas-scraper-kit-launch.html`'s inline `<style>` was **100% player CSS**, so filtering
  left an empty block that had to be deleted outright.
- `ai-math-terrance-tao.html` and `severance-protocol.html` had the same rules written as
  condensed one-liners rather than expanded blocks.
- `ai-math-terrance-tao.html`'s `IntersectionObserver` lacked the
  `rootMargin: '-1px 0px 0px 0px'` the other 15 had.
- `the-psychology-of-doom.html`'s `<audio src>` carries a `?v=` cache-buster that must
  survive any rewrite.

Assert per-file invariants (count, exact `src`) before and after a bulk edit rather than
trusting that the files match.

### Known defect, deliberately not fixed

`blog/exposure-gap.html` points at `../audio/exposure-gap.mp3`, **which does not exist**
in `audio/`. The player degrades honestly — the controls disable and the label reads
"🔊 Listen to this post — audio unavailable" — but the post still needs its narration
rendered or its player removed.
