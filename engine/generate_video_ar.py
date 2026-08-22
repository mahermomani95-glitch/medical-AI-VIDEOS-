#!/usr/bin/env python3
"""
Assemble a finished MP4 for one Arabic-track question: real neural
narration read over the pre-rendered scene images.

Per the project's language rule, narration is Arabic but medical
terminology inside each sentence is spoken in English -- so this script
auto-detects Arabic vs. Latin runs within each narration line and
synthesizes each run with the matching Piper voice (Arabic voice for
Arabic text, English voice for the embedded medical terms), then stitches
the runs back into one continuous scene clip with short pauses.

Runs inside GitHub Actions, where outbound internet access is
unrestricted, so it can reach Hugging Face for both voice models.

Usage: python generate_video_ar.py <script.ar.json> <scene_png_dir> <ar_voice.onnx> <en_voice.onnx> <out_dir> [length_scale]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

AR_CHAR = re.compile(r"[؀-ۿݐ-ݿ]")
# Split into runs of "has Arabic" vs "no Arabic" characters, keeping punctuation with its neighbor.
RUN_SPLIT = re.compile(r"[؀-ۿݐ-ݿ][؀-ۿݐ-ݿ\s0-9،؛؟.,\-]*|[^؀-ۿݐ-ݿ]+")


CONNECTOR_WORDS = {"ثم", "أو", "و"}
STRIP_CHARS = " ،:;.,-؛"


def _is_connector_only(text):
    cleaned = text.strip(STRIP_CHARS)
    if not cleaned:
        return True  # pure punctuation, e.g. a lone ":" -- harmless to fold in either direction
    words = cleaned.split()
    return len(words) <= 2 and all(w.strip(STRIP_CHARS) in CONNECTOR_WORDS for w in words)


def _merge_bare_connectors(runs):
    # A lone Arabic connector ("ثم"/"أو"/"و") sitting between two English
    # option names would otherwise force a full voice switch for one tiny
    # word -- fold it into whichever run precedes it instead. This is what
    # turns "Stomach <switch> ثم <switch> Colon <switch> ثم <switch> ..."
    # into one continuous run instead of a dozen voice flips per sentence.
    merged = []
    for chunk, is_ar in runs:
        if merged and is_ar and _is_connector_only(chunk):
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


def synth(text, voice, length_scale, out_wav):
    proc = subprocess.run(
        ["piper", "--model", str(voice), "--length_scale", str(length_scale), "--output_file", str(out_wav)],
        input=text.encode("utf-8"), capture_output=True,
    )
    if proc.returncode != 0 or not out_wav.exists():
        detail = proc.stderr.decode(errors="replace")[:800].replace("\n", " ")
        print(f"::error::piper failed (exit {proc.returncode}) on text '{text[:60]}...' voice={voice}: {detail}")
        sys.exit(1)


def make_silence(seconds, out_wav):
    run_checked([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "lavfi", "-i", f"anullsrc=r=22050:cl=mono",
        "-t", str(seconds), str(out_wav),
    ], "ffmpeg silence generation")


def concat_wavs(wav_paths, out_wav, tmp_dir, tag):
    # Use the audio concat FILTER (not the concat demuxer) since the two
    # Piper voices may not share a native sample rate -- the filtergraph
    # decodes and resamples every input properly, where the demuxer's
    # simple stream-copy-style concatenation can corrupt/desync mismatched
    # inputs.
    inputs = []
    for w in wav_paths:
        inputs += ["-i", str(w)]
    n = len(wav_paths)
    filter_inputs = "".join(f"[{i}:a]" for i in range(n))
    filter_complex = f"{filter_inputs}concat=n={n}:v=0:a=1[out]"
    run_checked([
        "ffmpeg", "-y", "-loglevel", "error",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-ar", "22050", "-ac", "1",
        str(out_wav),
    ], f"ffmpeg concat ({tag})")


def duration_seconds(wav_path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(wav_path)],
        capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def synth_scene_narration(narration, ar_voice, en_voice, length_scale, out_wav, tmp_dir, tag):
    runs = split_runs(narration)
    if not runs:
        make_silence(0.3, out_wav)
        return

    pieces = []
    for i, (chunk, is_ar) in enumerate(runs):
        voice = ar_voice if is_ar else en_voice
        wav = tmp_dir / f"{tag}.run{i}.wav"
        synth(chunk, voice, length_scale, wav)
        pieces.append(wav)
        # small breath between runs (slightly longer between AR<->EN switches)
        gap = tmp_dir / f"{tag}.gap{i}.wav"
        make_silence(0.18, gap)
        pieces.append(gap)

    # A slightly longer pause at the end of the scene (part of the "slow it down a bit" fix)
    end_gap = tmp_dir / f"{tag}.endgap.wav"
    make_silence(0.45, end_gap)
    pieces.append(end_gap)

    concat_wavs(pieces, out_wav, tmp_dir, tag)


def main():
    args = sys.argv[1:]
    if len(args) < 5:
        print("Usage: generate_video_ar.py <script.ar.json> <scene_png_dir> <ar_voice.onnx> <en_voice.onnx> <out_dir> [length_scale]", file=sys.stderr)
        sys.exit(1)
    script_path, png_dir, ar_voice, en_voice, out_dir = args[:5]
    length_scale = args[5] if len(args) > 5 else None

    script_path, png_dir, ar_voice, en_voice, out_dir = (
        Path(script_path), Path(png_dir), Path(ar_voice), Path(en_voice), Path(out_dir)
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = out_dir / "tmp"
    tmp_dir.mkdir(exist_ok=True)

    data = json.loads(script_path.read_text(encoding="utf-8"))
    qid = data["id"]
    length_scale = length_scale or data.get("length_scale", 1.15)
    clips = []

    for i, scene in enumerate(data["scenes"], start=1):
        scene_id = scene["id"]
        png = png_dir / f"{qid}.scene{i}-{scene_id}.png"
        if not png.exists():
            print(f"[error] missing scene image {png}", file=sys.stderr)
            sys.exit(1)

        tag = f"{qid}.scene{i}"
        wav = out_dir / f"{tag}.wav"
        synth_scene_narration(scene["narration"], ar_voice, en_voice, length_scale, wav, tmp_dir, tag)
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
