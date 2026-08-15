#!/usr/bin/env python3
"""Render a c4573 blog post to single-voice narration MP3 using macOS Ava (Premium).

Extracts h1/h2/p text from the blog-body (up to the <hr>), speaks it with `say`,
then normalizes to podcast loudness (-16 LUFS) as MP3.
"""
import html
import re
import subprocess
import sys
from pathlib import Path

VOICE = "Ava (Premium)"
RATE = 172  # wpm — natural essay pace

def extract_text(html_path: Path) -> str:
    raw = html_path.read_text()
    # Isolate the article content: from the <h1 class="blog-title"> to the <hr ...>
    start = raw.index('<h1 class="blog-title"')
    end = raw.index('<hr')
    body = raw[start:end]
    # Pull ordered h1/h2/p blocks
    blocks = re.findall(r'<(h1|h2|p)\b[^>]*>(.*?)</\1>', body, flags=re.DOTALL)
    lines = []
    for tag, inner in blocks:
        # skip the audio-player label / non-content paragraphs (none inside this range, but be safe)
        if 'audio-label' in inner or 'speed-btn' in inner:
            continue
        txt = re.sub(r'<[^>]+>', '', inner)      # strip inner tags (<em>, <a>)
        txt = html.unescape(txt)                  # &mdash; -> em dash, &amp; -> &
        txt = re.sub(r'\s+', ' ', txt).strip()
        if not txt:
            continue
        # headers get a period so the voice lands them, then a paragraph gap
        if tag in ('h1', 'h2') and not txt.endswith(('.', '?', '!', ':')):
            txt += '.'
        lines.append(txt)
    text = '\n\n'.join(lines)
    # Pronunciation touch-ups for the narrator
    subs = {
        r'\bAI\b': 'A.I.', r'\bAPI\b': 'A.P.I.', r'\bUN\b': 'U.N.',
        r'\bOpenAI\b': 'Open A.I.', r'\bPhD\b': 'PhD', r'\bUBI\b': 'U.B.I.',
        r'\bFTL\b': 'F.T.L.', r'\bGPU\b': 'G.P.U.',
    }
    for pat, rep in subs.items():
        text = re.sub(pat, rep, text)
    return text

def main():
    post = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("blog/right-argument-wrong-messenger.html")
    slug = post.stem
    text = extract_text(post)
    words = len(text.split())
    txt_path = Path(f"/tmp/{slug}.txt")
    txt_path.write_text(text)
    print(f"Extracted {words} words -> {txt_path}")

    aiff = Path(f"/tmp/{slug}.aiff")
    print(f"Rendering with '{VOICE}' at {RATE} wpm...")
    subprocess.run(["say", "-v", VOICE, "-r", str(RATE), "-f", str(txt_path),
                    "-o", str(aiff)], check=True)
    print(f"AIFF: {aiff} ({aiff.stat().st_size/1e6:.1f} MB)")

    out_dir = post.parent.parent / "audio"
    out_dir.mkdir(exist_ok=True)
    mp3 = out_dir / f"{slug}.mp3"
    print(f"Normalizing -> {mp3}")
    subprocess.run(["ffmpeg", "-y", "-i", str(aiff),
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", "44100", "-ac", "1", "-b:a", "128k",
                    str(mp3)], check=True, capture_output=True)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "csv=p=0", str(mp3)],
                         capture_output=True, text=True).stdout.strip()
    print(f"DONE: {mp3} ({mp3.stat().st_size/1e6:.1f} MB, {float(dur)/60:.1f} min)")

if __name__ == "__main__":
    main()
