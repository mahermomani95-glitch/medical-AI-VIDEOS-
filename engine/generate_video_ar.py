#!/usr/bin/env python3
"""
Assemble a finished MP4 for one Arabic-track question: real neural
narration read over the pre-rendered scene images.

Per the project's language rule, narration is Arabic but medical
terminology inside each sentence is spoken in English -- so this script
auto-detects Arabic vs. Latin runs within each narration line and
synthesizes each run with the matching edge-tts voice (Arabic voice for
Arabic text, English voice for the embedded medical terms), then stitches
the runs back into one continuous scene clip with short pauses.

Uses edge-tts (Microsoft Edge's free neural TTS service) instead of
Piper: Piper's only Arabic voice (ar_JO-kareem-medium) was judged very
poor quality by the user ("the worst Arabic language speaker i have ever
seen"). edge-tts's Arabic neural voices (e.g. ar-EG-ShakirNeural,
ar-JO-TaimNeural) are dramatically better -- but per a Whisper-transcription
QA check, those Arabic voices badly mangle embedded English medical terms
when a whole mixed sentence is read by one voice, so this script still
routes each language run to its own voice rather than reading everything
with the Arabic voice.

Runs inside GitHub Actions, where outbound internet access is
unrestricted, so it can reach Microsoft's edge-tts service.

Usage: python generate_video_ar.py <script.ar.json> <scene_png_dir> <ar_voice_name> <en_voice_name> <out_dir> [rate_percent]
  ar_voice_name / en_voice_name are edge-tts voice names, e.g. ar-EG-ShakirNeural / en-US-ChristopherNeural
  rate_percent is an edge-tts --rate value, e.g. "-10%" (negative = slower). Defaults to the script's "rate_percent" field or "-10%".
"""
import json
import random
import re
import subprocess
import sys
import time
from pathlib import Path

AR_CHAR = re.compile(r"[؀-ۿݐ-ݿ]")
# Split into runs of "has Arabic" vs "no Arabic" characters, keeping punctuation with its neighbor.
RUN_SPLIT = re.compile(r"[؀-ۿݐ-ݿ][؀-ۿݐ-ݿ\s0-9،؛؟.,\-]*|[^؀-ۿݐ-ݿ]+")


CONNECTOR_WORDS = {"ثم", "أو", "و"}
STRIP_CHARS = " ،:;.,-؛—–‏‎"
LATIN_LETTER = re.compile(r"[A-Za-z]")


def _has_no_real_content(chunk, is_ar):
    cleaned = chunk.strip(STRIP_CHARS)
    if not cleaned:
        return True  # pure punctuation, e.g. a lone ":" or "--" -- harmless to fold in either direction
    if is_ar:
        words = cleaned.split()
        return len(words) <= 2 and all(w.strip(STRIP_CHARS) in CONNECTOR_WORDS for w in words)
    # A "non-Arabic" run with no actual Latin letters left after stripping
    # punctuation (e.g. a lone em dash "—" caught between two Arabic
    # clauses) isn't really English text -- it's punctuation that RUN_SPLIT
    # happened to classify as the "non-Arabic" bucket. Sending it to
    # edge-tts on its own either crashes or wastes a pointless voice switch.
    return not LATIN_LETTER.search(cleaned)


def _merge_bare_connectors(runs):
    # A lone Arabic connector ("ثم"/"أو"/"و") sitting between two English
    # option names, or a bare punctuation mark like "—" sitting between two
    # Arabic clauses, would otherwise force a full voice switch (or an
    # edge-tts call with no real text to say) -- fold it into whichever run
    # precedes it instead. This is what turns "Stomach <switch> ثم <switch>
    # Colon <switch> ثم <switch> ..." into one continuous run instead of a
    # dozen voice flips per sentence.
    merged = []
    for chunk, is_ar in runs:
        if merged and _has_no_real_content(chunk, is_ar):
            prev_chunk, prev_is_ar = merged[-1]
            merged[-1] = (f"{prev_chunk} {chunk}", prev_is_ar)
        else:
            merged.append((chunk, is_ar))
    return merged


def _merge_same_voice(runs):
    merged = []
    for chunk, is_ar in runs:
        if merged and merged[-1][1] == is_ar:
            merged[-1] = (f"{merged[-1][0]} {chunk}", is_ar)
        else:
            merged.append((chunk, is_ar))
    return merged


def split_runs(text):
    raw = []
    for m in RUN_SPLIT.finditer(text):
        chunk = m.group(0).strip()
        if not chunk:
            continue
        is_ar = bool(AR_CHAR.search(chunk))
        raw.append((chunk, is_ar))
    return _merge_same_voice(_merge_bare_connectors(raw))


def run_checked(cmd, label):
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        detail = proc.stderr.decode(errors="replace")[:800].replace("\n", " ")
        print(f"::error::{label} failed (exit {proc.returncode}): {detail}")
        sys.exit(1)
    return proc


TTS_ATTEMPTS = 4


def synth(text, voice, rate_percent, out_mp3):
    """Synthesize one run, retrying transient edge-tts failures.

    edge-tts is a free network service and rendering the full bank makes tens
    of thousands of calls across many concurrent jobs, so occasional failures
    (rate limiting, dropped connections) are a certainty rather than an edge
    case. A single unretried failure used to abort the whole question --
    observed in the first pilot, where one question died mid-render and left
    partial scene clips behind while its 13 neighbours succeeded on identical
    text patterns.

    Returns True on success, False if the run could not be synthesized after
    all attempts (the caller substitutes silence rather than losing the whole
    video for one short run).
    """
    # NOTE: must be "--rate=<value>" (one token), not "--rate" "<value>" as two
    # separate argv entries -- argparse sees a value like "-10%" (starts with
    # '-', doesn't match its negative-number regex because of the trailing
    # '%') and misparses it as an unrecognized option instead of --rate's
    # argument, failing with "argument --rate: expected one argument".
    # Confirmed locally: "--rate -10%" fails immediately, "--rate=-10%" works.
    last_detail = ""
    for attempt in range(1, TTS_ATTEMPTS + 1):
        proc = subprocess.run(
            ["edge-tts", "--voice", voice, f"--rate={rate_percent}", "--text", text,
             "--write-media", str(out_mp3)],
            capture_output=True,
        )
        ok = proc.returncode == 0 and out_mp3.exists() and out_mp3.stat().st_size > 0
        if ok:
            if attempt > 1:
                print(f"[tts] recovered on attempt {attempt} for '{text[:40]}'")
            return True
        last_detail = proc.stderr.decode(errors="replace")[:400].replace("\n", " ")
        if attempt < TTS_ATTEMPTS:
            # Exponential backoff with a floor, to ride out rate limiting.
            delay = 2 ** attempt + random.uniform(0, 1.5)
            print(f"[tts] attempt {attempt}/{TTS_ATTEMPTS} failed for '{text[:40]}' "
                  f"({last_detail[:120]}); retrying in {delay:.1f}s")
            time.sleep(delay)

    print(f"::warning::edge-tts gave up after {TTS_ATTEMPTS} attempts on "
          f"'{text[:60]}' voice={voice}: {last_detail}")
    return False


def make_silence(seconds, out_wav):
    run_checked([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
        "-t", str(seconds), str(out_wav),
    ], "ffmpeg silence generation")


def concat_audio(pieces, out_wav, tag):
    # Use the audio concat FILTER (not the concat demuxer): pieces mix mp3
    # (edge-tts) and wav (silence) containers and could differ in sample
    # rate, so decode+resample every input properly instead of a
    # stream-copy-style concatenation that could corrupt/desync them.
    inputs = []
    for w in pieces:
        inputs += ["-i", str(w)]
    n = len(pieces)
    filter_inputs = "".join(f"[{i}:a]" for i in range(n))
    filter_complex = f"{filter_inputs}concat=n={n}:v=0:a=1[out]"
    run_checked([
        "ffmpeg", "-y", "-loglevel", "error",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-ar", "24000", "-ac", "1",
        str(out_wav),
    ], f"ffmpeg concat ({tag})")


def duration_seconds(wav_path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(wav_path)],
        capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def synth_scene_narration(narration, ar_voice, en_voice, rate_percent, out_wav, tmp_dir, tag):
    runs = split_runs(narration)
    if not runs:
        make_silence(0.3, out_wav)
        return

    pieces = []
    dropped = 0
    for i, (chunk, is_ar) in enumerate(runs):
        voice = ar_voice if is_ar else en_voice
        mp3 = tmp_dir / f"{tag}.run{i}.mp3"
        if synth(chunk, voice, rate_percent, mp3):
            pieces.append(mp3)
        else:
            # Losing one short run (often a single spoken letter) is far
            # better than losing the whole question's video. Substitute a
            # brief silence and keep going; the warning above records it.
            dropped += 1
            miss = tmp_dir / f"{tag}.miss{i}.wav"
            make_silence(0.25, miss)
            pieces.append(miss)
        # small breath between runs (slightly longer between AR<->EN switches)
        gap = tmp_dir / f"{tag}.gap{i}.wav"
        make_silence(0.18, gap)
        pieces.append(gap)

    if dropped:
        print(f"::warning::{tag}: {dropped}/{len(runs)} narration run(s) "
              f"could not be synthesized and were replaced with silence")

    # A slightly longer pause at the end of the scene (part of the "slow it down a bit" fix)
    end_gap = tmp_dir / f"{tag}.endgap.wav"
    make_silence(0.45, end_gap)
    pieces.append(end_gap)

    concat_audio(pieces, out_wav, tag)


def main():
    args = sys.argv[1:]
    if len(args) < 5:
        print("Usage: generate_video_ar.py <script.ar.json> <scene_png_dir> <ar_voice_name> <en_voice_name> <out_dir> [rate_percent]", file=sys.stderr)
        sys.exit(1)
    script_path, png_dir, ar_voice, en_voice, out_dir = args[:5]
    rate_percent = args[5] if len(args) > 5 else None

    script_path, png_dir, out_dir = Path(script_path), Path(png_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = out_dir / "tmp"
    tmp_dir.mkdir(exist_ok=True)

    data = json.loads(script_path.read_text(encoding="utf-8"))
    qid = data["id"]
    rate_percent = rate_percent or data.get("rate_percent", "-10%")
    clips = []

    for i, scene in enumerate(data["scenes"], start=1):
        scene_id = scene["id"]
        png = png_dir / f"{qid}.scene{i}-{scene_id}.png"
        if not png.exists():
            print(f"::error::missing scene image {png}")
            sys.exit(1)

        tag = f"{qid}.scene{i}"
        wav = out_dir / f"{tag}.wav"
        synth_scene_narration(scene["narration"], ar_voice, en_voice, rate_percent, wav, tmp_dir, tag)
        dur = duration_seconds(wav)

        clip = out_dir / f"{tag}.mp4"
        run_checked([
            "ffmpeg", "-y", "-loglevel", "error",
            "-loop", "1", "-i", str(png),
            "-i", str(wav),
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-vf", "scale=1920:1080",
            str(clip),
        ], f"ffmpeg mux scene {i}")
        clips.append(clip)
        print(f"[scene {i}] {scene_id}: {dur:.1f}s narrated -> {clip.name}")

    concat_list = out_dir / f"{qid}.concat.txt"
    with open(concat_list, "w") as f:
        for c in clips:
            f.write(f"file '{c.resolve()}'\n")

    final = out_dir / f"{qid}.mp4"
    run_checked([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy", str(final),
    ], "ffmpeg final concat")
    print(f"[done] {final}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        print(f"::error::Unhandled exception in generate_video_ar.py: {e}")
        traceback.print_exc()
        sys.exit(1)
