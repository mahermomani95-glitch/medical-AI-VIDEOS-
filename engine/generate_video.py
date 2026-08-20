#!/usr/bin/env python3
"""
Assemble a finished MP4 for one question: real neural narration (Piper,
deep male English voice) read over the pre-rendered scene images.

Runs inside GitHub Actions, where outbound internet access is unrestricted
(unlike a locked-down sandbox), so it can actually reach Hugging Face to
fetch the voice model.

Usage: python generate_video.py <script.json> <scene_png_dir> <voice.onnx> <out_dir>
"""
import json
import subprocess
import sys
from pathlib import Path

def synth(text, voice, out_wav):
    proc = subprocess.run(
        ["piper", "--model", str(voice), "--output_file", str(out_wav)],
        input=text.encode("utf-8"), capture_output=True,
    )
    if proc.returncode != 0 or not out_wav.exists():
        print(f"[error] piper failed: {proc.stderr.decode()[:500]}", file=sys.stderr)
        sys.exit(1)

def duration_seconds(wav_path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(wav_path)],
        capture_output=True, text=True,
    )
    return float(out.stdout.strip())

def main():
    script_path, png_dir, voice, out_dir = sys.argv[1:5]
    script_path, png_dir, voice, out_dir = Path(script_path), Path(png_dir), Path(voice), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(script_path.read_text(encoding="utf-8"))
    qid = data["id"]
    clips = []

    for i, scene in enumerate(data["scenes"], start=1):
        scene_id = scene["id"]
        png = png_dir / f"{qid}.scene{i}-{scene_id}.png"
        if not png.exists():
            print(f"[error] missing scene image {png}", file=sys.stderr)
            sys.exit(1)

        wav = out_dir / f"{qid}.scene{i}.wav"
        synth(scene["narration"], voice, wav)
        dur = duration_seconds(wav)

        clip = out_dir / f"{qid}.scene{i}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-loop", "1", "-i", str(png),
            "-i", str(wav),
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-vf", "scale=1920:1080",
            str(clip),
        ], check=True)
        clips.append(clip)
        print(f"[scene {i}] {scene_id}: {dur:.1f}s narrated -> {clip.name}")

    concat_list = out_dir / f"{qid}.concat.txt"
    with open(concat_list, "w") as f:
        for c in clips:
            f.write(f"file '{c.resolve()}'\n")

    final = out_dir / f"{qid}.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy", str(final),
    ], check=True)
    print(f"[done] {final}")

if __name__ == "__main__":
    main()
