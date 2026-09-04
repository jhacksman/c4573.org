#!/usr/bin/env python3
"""Render a c4573 blog post to single-voice narration MP3 using the stephen_fry
cloned voice on the quato Qwen3-TTS server.

Client pattern mirrors dtfftl/src/tts.py: one POST /speak per paragraph-sized
segment, all fired at once (server queues, least-queued GPU dispatch),
`timeout: 0`, WAV validated. Each segment is checked for:

  * runaway   -- duration >= 2x expected at 2.3 words/sec (4 s floor)
  * silence   -- an internal silence gap >= 1.5 s
  * pace      -- duration deviates > 15% from expected (segments >= 12 words)

Failing segments are re-rendered up to RUNAWAY_RETRIES more times and the best
attempt (no runaway/silence, then closest to expected pace) is kept.

Section headings (<h2>) are spoken as their own short segment with a longer
pause after them (dtfftl story-header convention). Em-dashes inside a
paragraph become segment breaks with a short pause. Segments are trimmed of
leading/trailing silence, concatenated with explicit gaps, normalized to
-16 LUFS / -1.5 dBTP, and written as 44.1 kHz mono 128k MP3 under audio/.

Usage: python3 render_blog_audio_fry.py blog/<slug>.html
       python3 render_blog_audio_fry.py blog/<slug>.html --normalize-only
"""
import html
import json
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

TTS_URL = "http://10.9.10.9:7849/speak"
VOICE = "stephen_fry"
TTS_TIMEOUT = 3600           # read timeout; server-side timeout is 0 (unlimited)
MIN_WAV_SIZE_BYTES = 1000
WORDS_PER_SEC = 2.3          # expected narration pace
RUNAWAY_FACTOR = 2.0         # >= 2x expected -> re-render
RUNAWAY_FLOOR_SEC = 4.0      # tiny segments: don't flag unless over expected+floor
PACE_TOLERANCE = 0.15        # +/- 15% of expected duration
PACE_MIN_WORDS = 12          # pace check only meaningful on longer segments
SILENCE_GAP_SEC = 1.5        # internal silence this long -> re-render
SILENCE_DB = -40
RUNAWAY_RETRIES = 2
MAX_WORKERS = 12
GAP_SEC = 0.6                # silence between paragraphs
TITLE_GAP_SEC = 1.0          # silence after the title
HEADING_PRE_GAP_SEC = 1.0    # silence before a section heading
HEADING_POST_GAP_SEC = 0.8   # silence after a section heading
DASH_GAP_SEC = 0.35          # silence at an em-dash break
EDGE_SILENCE_KEEP_SEC = 0.15 # leading/trailing silence left on each clip

PRONOUNCE = {
    r'\bAI\b': 'A.I.', r'\bAPI\b': 'A.P.I.', r'\bUN\b': 'U.N.',
    r'\bOpenAI\b': 'Open A.I.', r'\bUBI\b': 'U.B.I.',
    r'\bFTL\b': 'F.T.L.', r'\bGPU\b': 'G.P.U.', r'\bGPUs\b': 'G.P.U.s',
}


def extract_segments(html_path: Path) -> list[dict]:
    """Return ordered segments: {text, kind} with kind in title|heading|para|dash.
    `dash` marks a continuation piece split off a paragraph at an em-dash."""
    raw = html_path.read_text()
    start = raw.index('<h1 class="blog-title"')
    end = raw.index('<hr')
    body = raw[start:end]
    blocks = re.findall(r'<(h1|h2|p)\b[^>]*>(.*?)</\1>', body, flags=re.DOTALL)
    segs = []
    for tag, inner in blocks:
        if 'audio-label' in inner or 'speed-btn' in inner or 'blog-meta' in inner:
            continue
        txt = re.sub(r'<[^>]+>', '', inner)
        txt = html.unescape(txt)
        txt = re.sub(r'\s+', ' ', txt).strip()
        if not txt or ' · c4573.org' in txt:
            continue
        for pat, rep in PRONOUNCE.items():
            txt = re.sub(pat, rep, txt)
        txt = txt.replace('..', '.')  # "G.P.U.." at sentence end -> "G.P.U."
        if tag == 'h1':
            kind = 'title'
        elif tag == 'h2':
            kind = 'heading'
        else:
            kind = 'para'
        if kind in ('title', 'heading') and not txt.endswith(('.', '?', '!', ':')):
            txt += '.'
        # Em-dashes become segment breaks with a short pause.
        pieces = [p.strip(' ,;') for p in re.split(r'\s*[—–]\s*', txt)]
        pieces = [p for p in pieces if p]
        for n, piece in enumerate(pieces):
            segs.append({"text": piece, "kind": kind if n == 0 else 'dash'})
    return segs


def prepare_text_for_tts(text: str) -> str:
    # dtfftl convention: em-dash pad so cloned voices don't clip the first syllable
    text = text.strip()
    if not text.startswith("—"):
        text = "— " + text
    if not text.endswith("—"):
        text = text + " —"
    return text


def validate_wav_bytes(data: bytes) -> tuple[bool, str]:
    if not data:
        return (False, "empty response")
    if len(data) < MIN_WAV_SIZE_BYTES:
        return (False, f"too small ({len(data)} bytes)")
    if data[:4] != b"RIFF":
        return (False, "invalid WAV header")
    return (True, "")


def wav_duration(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def silence_gaps(path: Path, min_len: float = SILENCE_GAP_SEC) -> list[tuple[float, float]]:
    """Internal silences >= min_len (leading/trailing silence excluded)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                        f"silencedetect=noise={SILENCE_DB}dB:d={min_len}", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    total = wav_duration(path)
    gaps = []
    for s, e in zip(starts, ends):
        if s <= 0.05 or e >= total - 0.05:
            continue  # edge silence, trimmed later
        gaps.append((round(s, 2), round(e, 2)))
    return gaps


def speak(text: str, out: Path) -> tuple[bool, str]:
    try:
        resp = requests.post(TTS_URL, headers={"Content-Type": "application/json"},
                             json={"text": prepare_text_for_tts(text), "voice": VOICE,
                                   "language": "English", "timeout": 0},
                             timeout=(10, TTS_TIMEOUT))
    except Exception as exc:
        return (False, f"request failed: {exc}")
    if resp.status_code != 200:
        return (False, f"HTTP {resp.status_code}: {resp.text[:100]}")
    ok, err = validate_wav_bytes(resp.content)
    if not ok:
        return (False, err)
    out.write_bytes(resp.content)
    return (True, "")


def judge(words: int, dur: float, gaps: list, pace: float) -> tuple[list[str], float]:
    """Return (problems, pace deviation ratio). Runaway is judged against the
    fixed 2.3 w/s reference; pace deviation against `pace` (the batch median
    of the voice, measured after the first pass)."""
    ref = words / WORDS_PER_SEC
    limit = max(ref * RUNAWAY_FACTOR, ref + RUNAWAY_FLOOR_SEC)
    expected = words / pace
    problems = []
    if dur >= limit:
        problems.append("RUNAWAY")
    if gaps:
        problems.append(f"SILENCE{gaps}")
    dev = (dur - expected) / expected if expected else 0.0
    if words >= PACE_MIN_WORDS and abs(dev) > PACE_TOLERANCE:
        problems.append(f"PACE{dev:+.0%}")
    return problems, dev


def render_attempt(idx: int, text: str, out: Path, attempt: int, pace: float) -> dict:
    """Render one attempt (reusing a cached WAV from an earlier run if present)."""
    words = len(text.split())
    cand = out.with_name(f"{out.stem}.try{attempt}.wav")
    cached = cand.exists() and validate_wav_bytes(cand.read_bytes())[0]
    t0 = time.time()
    if cached:
        ok, err = True, ""
    else:
        ok, err = speak(text, cand)
    wall = time.time() - t0
    if not ok:
        print(f"[{idx:02d}] attempt {attempt} FAILED: {err}", flush=True)
        return {"attempt": attempt, "error": err, "wall": round(wall, 1)}
    dur = wav_duration(cand)
    gaps = silence_gaps(cand)
    problems, dev = judge(words, dur, gaps, pace)
    print(f"[{idx:02d}] attempt {attempt}{' (cached)' if cached else ''} "
          f"{' '.join(problems) or 'ok'}: {words}w expected {words/pace:.1f}s got {dur:.1f}s "
          f"({dev:+.0%}) in {wall:.0f}s wall", flush=True)
    return {"attempt": attempt, "dur": round(dur, 2), "wall": round(wall, 1),
            "dev": round(dev, 3), "problems": problems, "file": cand.name, "cached": cached}


def hard_fail(a: dict) -> bool:
    return "dur" not in a or any(p.startswith(("RUNAWAY", "SILENCE")) for p in a["problems"])


def render_all(segs: list[dict], work: Path) -> tuple[dict, float]:
    """Phase 1: one attempt per segment, all fired at once. Measure the voice's
    median pace. Phase 2: re-render flagged segments (runaway, silence, pace
    outliers vs the median) up to RUNAWAY_RETRIES more times; keep the best."""
    texts = [s["text"] for s in segs]
    outs = [work / f"seg_{i:02d}.wav" for i in range(len(segs))]
    attempts = {i: [] for i in range(len(segs))}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(render_attempt, i, texts[i], outs[i], 0, WORDS_PER_SEC): i
                for i in range(len(segs))}
        for f in as_completed(futs):
            attempts[futs[f]].append(f.result())

    paces = sorted(len(texts[i].split()) / a["dur"]
                   for i, al in attempts.items() for a in al
                   if "dur" in a and len(texts[i].split()) >= PACE_MIN_WORDS and a["dur"] > 0)
    pace = paces[len(paces) // 2] if paces else WORDS_PER_SEC
    print(f"batch median pace: {pace:.2f} words/sec over {len(paces)} segments "
          f"(reference {WORDS_PER_SEC})", flush=True)
    # Re-judge every first attempt against the median pace.
    for i, al in attempts.items():
        for a in al:
            if "dur" in a:
                a["problems"], a["dev"] = judge(len(texts[i].split()), a["dur"],
                                                silence_gaps(work / a["file"]), pace)
                a["dev"] = round(a["dev"], 3)

    for attempt in range(1, RUNAWAY_RETRIES + 1):
        todo = [i for i, al in attempts.items() if not al or hard_fail(al[-1]) or al[-1]["problems"]]
        if not todo:
            break
        print(f"pass {attempt}: re-rendering {len(todo)} segments {todo}", flush=True)
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
            futs = {ex.submit(render_attempt, i, texts[i], outs[i], attempt, pace): i for i in todo}
            for f in as_completed(futs):
                attempts[futs[f]].append(f.result())

    results = {}
    for i, al in attempts.items():
        good = [a for a in al if "dur" in a]
        words = len(texts[i].split())
        if not good:
            results[i] = {"idx": i, "words": words, "dur": 0, "ok": False, "attempts": al}
            continue
        best = min(good, key=lambda a: (hard_fail(a), abs(a["dev"])))
        shutil.copyfile(work / best["file"], outs[i])
        results[i] = {"idx": i, "words": words, "dur": best["dur"], "ok": not hard_fail(best),
                      "kept": best["attempt"], "problems": best["problems"],
                      "rerendered": len(al) > 1, "attempts": al}
    return results, pace


def main():
    post = Path(sys.argv[1])
    slug = post.stem
    segs = extract_segments(post)
    work = Path(f"/tmp/{slug}-fry")
    work.mkdir(exist_ok=True)
    (work / "segments.txt").write_text("\n\n".join(f"[{s['kind']}] {s['text']}" for s in segs))
    total_words = sum(len(s["text"].split()) for s in segs)
    print(f"{len(segs)} segments, {total_words} words, expected ~{total_words/WORDS_PER_SEC/60:.1f} min",
          flush=True)

    # Fire everything at once; the server queues and dispatches least-queued.
    results, pace = render_all(segs, work)
    (work / "results.json").write_text(json.dumps({"pace": pace, "segments": results}, indent=2, sort_keys=True))

    failed = [i for i, r in results.items() if not r["ok"]]
    rerendered = sorted(i for i, r in results.items() if r.get("rerendered"))
    residual = sorted(i for i, r in results.items() if r.get("problems"))
    print(f"re-rendered segments: {rerendered}", flush=True)
    print(f"segments kept with residual flags: "
          f"{[(i, results[i]['problems']) for i in residual]}", flush=True)
    if failed:
        print(f"FAILED segments: {failed} -- aborting before concat", flush=True)
        sys.exit(1)

    # Trim edge silence on every clip so the inter-segment gaps are exactly what we set.
    trim = (f"silenceremove=start_periods=1:start_threshold={SILENCE_DB}dB:start_silence={EDGE_SILENCE_KEEP_SEC},"
            f"areverse,silenceremove=start_periods=1:start_threshold={SILENCE_DB}dB:start_silence={EDGE_SILENCE_KEEP_SEC},"
            f"areverse")
    for i in range(len(segs)):
        subprocess.run(["ffmpeg", "-y", "-i", str(work / f"seg_{i:02d}.wav"), "-af", trim,
                        str(work / f"trim_{i:02d}.wav")], check=True, capture_output=True)

    # Concat with explicit gaps: build ffmpeg filter graph.
    inputs, filt, parts = [], [], []
    for i in range(len(segs)):
        inputs += ["-i", str(work / f"trim_{i:02d}.wav")]
    for i, s in enumerate(segs):
        parts.append(f"[{i}:a]")
        if i == len(segs) - 1:
            break
        nxt = segs[i + 1]["kind"]
        if s["kind"] == "title":
            gap = TITLE_GAP_SEC
        elif s["kind"] == "heading":
            gap = HEADING_POST_GAP_SEC
        elif nxt == "heading":
            gap = HEADING_PRE_GAP_SEC
        elif nxt == "dash":
            gap = DASH_GAP_SEC
        else:
            gap = GAP_SEC
        filt.append(f"anullsrc=r=24000:cl=mono,atrim=0:{gap}[g{i}]")
        parts.append(f"[g{i}]")
    concat = "".join(parts) + f"concat=n={len(parts)}:v=0:a=1[cat]"
    graph = ";".join(filt + [concat])

    out_dir = post.parent.parent / "audio"
    out_dir.mkdir(exist_ok=True)
    mp3 = out_dir / f"{slug}.mp3"
    joined = work / "joined.wav"
    subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex", graph, "-map", "[cat]",
                    str(joined)], check=True, capture_output=True)
    print(f"Joined: {joined} ({wav_duration(joined)/60:.1f} min)", flush=True)
    gaps = silence_gaps(joined)
    print(f"joined silence gaps >= {SILENCE_GAP_SEC}s: {gaps or 'none'}", flush=True)
    normalize(joined, mp3)
    print(f"DONE: {mp3} ({mp3.stat().st_size/1e6:.1f} MB, {wav_duration(mp3)/60:.1f} min) "
          f"voice={VOICE}", flush=True)


def normalize(src: Path, mp3: Path) -> None:
    """Two-pass loudnorm to -16 LUFS integrated. Single-pass (dynamic) lands
    ~1.5 LU low on short clips; the second pass uses measured values so the
    integrated loudness hits the target."""
    target = "I=-16:TP=-1.5:LRA=11"
    probe = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src),
                            "-af", f"loudnorm={target}:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    m = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    measured = (f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
                f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
                f":offset={m['target_offset']}:linear=true")
    pass2 = mp3.with_suffix(".pass2.wav")
    subprocess.run(["ffmpeg", "-y", "-i", str(src),
                    "-af", f"loudnorm={target}{measured}", "-ar", "44100", "-ac", "1",
                    str(pass2)], check=True, capture_output=True)
    # Linear pass respects the TP ceiling and may land low on peaky voices (Fry).
    # Make up the residual with gain into a true-peak limiter at -1.5 dBTP.
    probe2 = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(pass2),
                             "-af", f"loudnorm={target}:print_format=json", "-f", "null", "-"],
                            capture_output=True, text=True).stderr
    got = float(json.loads(probe2[probe2.rindex("{"):probe2.rindex("}") + 1])["input_i"])
    residual = max(0.0, min(3.0, -16.0 - got + 0.2))  # +0.2 covers limiter/mp3 loss
    print(f"loudnorm pass2: {got:.2f} LUFS, residual gain {residual:.2f} dB", flush=True)
    subprocess.run(["ffmpeg", "-y", "-i", str(pass2),
                    "-af", f"volume={residual}dB,alimiter=limit=0.841:attack=5:release=60:level=false",
                    "-ar", "44100", "-ac", "1", "-b:a", "128k", str(mp3)],
                   check=True, capture_output=True)
    pass2.unlink(missing_ok=True)


if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[2] == "--normalize-only":
    _post = Path(sys.argv[1])
    normalize(Path(f"/tmp/{_post.stem}-fry/joined.wav"), _post.parent.parent / "audio" / f"{_post.stem}.mp3")
    sys.exit(0)


if __name__ == "__main__":
    main()
