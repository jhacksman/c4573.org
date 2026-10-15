# Audio and publication plan

Authorized by the user on October 15, 2026: render with stephen_fry on quato, check audio, then publish.

Use the committed article without prose changes and a fresh, persistent `.render/age-of-digital-abundance-fry/` cache (the renderer now defaults to `.render`, rather than the older `/tmp` location described by Jack). Check quato voice and queue, run the established renderer under screen, inspect all segment outcomes, transcribe and compare the full MP3, review suspicious passages and opening/ending, measure loudness/peak/format/silence, then verify the website player with Range-capable delivery. Add the newest index card and retain one New badge. Determine the established audio delivery route; the previous no-audio rule must be reconciled with the established tracked-audio Pages deployment. Publish source only after audio checks pass, then verify the public article, index and audio. Record actual evidence and limitations here.

## Delivery route resolved

Jack inspected the deployment and confirmed that MP3s are ordinary tracked files on main, delivered by legacy GitHub Pages. Independently confirmed the latest audio commit d3592fe. The previous no-audio instruction contradicted every recent release. User authorization to publish includes the necessary final MP3; RULES.md now distinguishes final publishable audio from ignored render intermediates. No new audio host, release system or deployment mechanism is introduced.

## Completed audio checks

- Render completed successfully with `stephen_fry`: 75 segments, 3,507 spoken words; article checksum unchanged from the draft. Four segments were retried. Segment 71 retained a pacing-only flag; its complete text appears in the full transcript without omission.
- Final MP3: 1,454.186 seconds (24:14), 23,268,248 bytes; 44.1 kHz mono, 128 kbps. Measured −16.41 LUFS integrated, −1.57 dB true peak, 3.30 LU loudness range. No internal silence at least 1.5 seconds long.
- Full `small.en` transcript comparison: 98.83% normalized token similarity; no omitted or reordered passages. Differences consisted of numerical/currency formatting, spelling and recognition ambiguity. A separate `large-v3-turbo` transcription of the two ambiguous passages confirmed “acquiring” and “morning.” The review was automatic transcription plus mismatch review and signal measurements, not a human listening audit.
- Browser tests against a local Range-capable server: duration loaded as 24:14; play advanced; seeking reached 729 seconds; +10 reached 739; playback speed changed to 1.5; pause worked. Controls restored to 1× and start. At 390 px, page width equaled scroll width. Blog index links the new post first with the only New badge.
- Persistent intermediates, full transcripts and detailed comparisons remain in ignored `.render/age-of-digital-abundance-fry/`. Summary and hashes are in `audio-verification.json`.

## Published and verified

Published commit `0697525` to main; GitHub Pages build completed successfully. At 15:57 Pacific on October 15, 2026, the public article and blog index returned 200, the audio Range request returned 206, and the complete public MP3 SHA-256 matched the checked local file. The public browser loaded the 24:14 duration, played successfully and sought to 729 seconds. Playback was then paused and restored to the beginning.

Public URL: https://c4573.org/blog/age-of-digital-abundance.html

Proof screenshot: `/Volumes/JackPack/c4573-ethos/articles/age-of-digital-abundance/published.png`. Detailed public verification is recorded in audio-verification.json. No audio intermediates were committed; the final MP3 uses the established tracked-content delivery route.
