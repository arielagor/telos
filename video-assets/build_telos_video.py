#!/usr/bin/env python3
"""Composite the Telos long-form walkthrough from HeyGen avatar beats + AGOR cutaways.

Per beat: avatar full-frame (crop portrait + blur-fill room, no gray bars) for a short lead,
then the slide full-frame with the avatar as a bottom-right PiP; burned captions throughout.
Then concat all beats, add a persistent disclosure lower-third + progress bar, and bookend with
title + outro cards.

Run from video-assets/.  python build_telos_video.py
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
HEY = "heygen"
CUT = "cutaways"
TMP = "_build"
os.makedirs(TMP, exist_ok=True)
OUT = "FINAL-telos-walkthrough.mp4"
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30"]
AENC = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
SEGF = "C:/Windows/Fonts/segoeui.ttf"
SEGB = "C:/Windows/Fonts/segoeuib.ttf"

# EDL: beat -> (mode, slide, avatar_lead_seconds). mode: "avatar" | "cut".
EDL = {
    "b01": ("cut", "slide-b02.png", 6.0),
    "b02": ("cut", "slide-b03.png", 2.6),
    "b03": ("cut", "slide-b04.png", 2.6),
    "b04": ("cut", "slide-b05.png", 2.6),
    "b05": ("cut", "slide-b06.png", 2.6),
    "b06": ("cut", "slide-b07.png", 2.6),
    "b07": ("cut", "slide-b08.png", 2.6),
    "b08": ("cut", "slide-b09.png", 2.6),
    "b09": ("cut", "slide-b10.png", 2.6),
    "b10": ("cut", "slide-b11.png", 2.6),
    "b11": ("cut", "slide-b12.png", 2.6),
    "b12": ("cut", "slide-b13.png", 2.6),
    "b13": ("avatar", None, 0.0),
    "b14": ("cut", "slide-b15.png", 2.6),
    "b14a": ("cut", "slide-b17.png", 2.6),
    "b14b": ("cut", "slide-b18.png", 2.6),
    "b14c": ("cut", "slide-b19.png", 2.6),
    "b15": ("avatar", None, 0.0),
}


def run(cmd, log=None):
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if r.returncode:
        print("FFMPEG ERROR:\n", r.stderr.decode()[-2500:])
        sys.exit(1)


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "default=noprint_wrappers=1:nokey=1", p],
                                capture_output=True, text=True).stdout.strip())


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def make_disclosure():
    """Persistent bottom disclosure strip (transparent PNG, 1920x1080)."""
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1032, 1920, 1080], fill=(8, 11, 20, 205))
    d.rectangle([0, 1030, 1920, 1033], fill=(56, 189, 248, 180))
    txt = "Synthetic avatar + AI voice  ·  script generated from the submitted repo  ·  no human voiceover recorded  ·  authorized by Ariel Agor"
    f = font(SEGF, 24)
    w = d.textbbox((0, 0), txt, font=f)[2]
    d.text(((1920 - w) // 2, 1044), txt, font=f, fill=(200, 210, 230, 255))
    p = os.path.join(TMP, "disclosure.png")
    img.save(p)
    return p


def esc_ass(p):
    # ffmpeg ass filter path escaping (drive colon)
    return p.replace("\\", "/").replace(":", "\\:")


def make_ass(script, d, path):
    """Proportional-timed captions for one beat (no whisper needed)."""
    words = script.split()
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 7 or w.endswith((".", "?")) and len(cur) >= 4:
            chunks.append(" ".join(cur)); cur = []
    if cur:
        chunks.append(" ".join(cur))
    total = sum(len(c) for c in chunks) or 1
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, "
        "Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV\n"
        "Style: Cap,Segoe UI,50,&H00F4F6FB,&H00120A0A,&H78000000,-1,3,3,1,2,140,140,64\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    def tc(t):
        h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
        return f"{h:d}:{m:02d}:{s:05.2f}"
    lines, t = [], 0.0
    for c in chunks:
        seg = d * (len(c) / total)
        lines.append(f"Dialogue: 0,{tc(t)},{tc(min(d, t+seg))},Cap,,0,0,0,,{c}")
        t += seg
    open(path, "w", encoding="utf-8").write(header + "\n".join(lines) + "\n")


def build_segment(bid, mode, slide, lead, beats_meta):
    src = os.path.join(HEY, bid + ".mp4")
    d = dur(src)
    ass = os.path.join(TMP, bid + ".ass")
    make_ass(beats_meta[bid], d, ass)
    out = os.path.join(TMP, bid + "_seg.mp4")
    av_full = ("[0:v]crop=608:1080:656:0,split=2[fg][bgs];"
               "[bgs]scale=1920:1080,boxblur=40:5,eq=brightness=-0.12:saturation=0.85[bg];"
               "[bg][fg]overlay=(W-w)/2:0[full]")
    capf = f"ass={esc_ass(ass)}"
    if mode == "avatar":
        fc = av_full + f";[full]{capf}[v]"
        inputs = ["-i", src]
    else:
        fc = (av_full + ";"
              "[1:v]scale=1920:1080,format=yuv420p[slide];"
              "[0:v]crop=608:1080:656:0,scale=-1:560[pipraw];"
              "[pipraw]pad=iw+8:ih+8:4:4:color=0x38bdf8[pip];"
              f"[full][slide]overlay=0:0:enable='gte(t,{lead})'[s1];"
              f"[s1][pip]overlay=W-w-56:H-h-70:enable='gte(t,{lead})'[s2];"
              f"[s2]{capf}[v]")
        inputs = ["-i", src, "-loop", "1", "-t", f"{d}", "-i", os.path.join(CUT, slide)]
    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "0:a",
           *ENC, *AENC, "-t", f"{d}", out]
    run(cmd)
    print(f"  segment {bid} ({d:.1f}s, {mode})")
    return out, d


def card_clip(slide, seconds, name, fades=True):
    out = os.path.join(TMP, name)
    vf = "scale=1920:1080,format=yuv420p"
    if fades:
        vf += f",fade=t=in:st=0:d=0.6,fade=t=out:st={seconds-0.7:.2f}:d=0.7"
    run(["ffmpeg", "-y", "-loop", "1", "-t", f"{seconds}", "-i", os.path.join(CUT, slide),
         "-f", "lavfi", "-t", f"{seconds}", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
         "-vf", vf, *ENC, *AENC, "-shortest", out])
    return out, seconds


def main():
    beats = {b["id"]: b["script"] for b in json.load(open("beats.json"))["beats"]}
    missing = [b for b in EDL if not os.path.exists(os.path.join(HEY, b + ".mp4"))]
    if missing:
        print("MISSING beat renders:", missing); return 1

    print("[1/4] building beat segments ...")
    segs = []
    for bid in sorted(EDL):
        mode, slide, lead = EDL[bid]
        out, _ = build_segment(bid, mode, slide, lead, beats)
        segs.append(out)

    print("[2/4] concatenating beats ...")
    listf = os.path.join(TMP, "concat.txt")
    open(listf, "w").write("\n".join(f"file '{os.path.abspath(s)}'" for s in segs) + "\n")
    body = os.path.join(TMP, "body.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listf, "-c", "copy", body])
    bd = dur(body)

    print("[3/4] disclosure strip + progress bar ...")
    disc = make_disclosure()
    body2 = os.path.join(TMP, "body2.mp4")
    fc = (f"[0:v][1:v]overlay=0:0[d];"
          f"[d]drawbox=x=0:y=ih-6:w=iw*t/{bd:.3f}:h=6:color=0x8b5cf6@1:t=fill[v]")
    run(["ffmpeg", "-y", "-i", body, "-i", disc, "-filter_complex", fc,
         "-map", "[v]", "-map", "0:a", *ENC, *AENC, body2])

    print("[4/4] title + outro bookends ...")
    intro, _ = card_clip("slide-b01.png", 4.6, "intro.mp4")
    outro, _ = card_clip("slide-b16.png", 5.2, "outro.mp4")
    finlist = os.path.join(TMP, "final_concat.txt")
    open(finlist, "w").write("\n".join(f"file '{os.path.abspath(p)}'" for p in [intro, body2, outro]) + "\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", finlist, "-c", "copy",
         "-movflags", "+faststart", OUT])
    print(f"\nDONE -> {os.path.join(HERE, OUT)}  ({dur(OUT):.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
