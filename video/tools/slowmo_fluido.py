"""Slow motion fluido: frame sfumati (video/frames/blended) -> video/powerbench_360_slowmo_fluido.mp4.

144 frame veri a 24 fps (6 s) portati a 48 fps con un'interpolazione a movimento stimato 2x.
Richiede ffmpeg (winget install Gyan.FFmpeg).
"""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "frames", "blended", "frame_%04d.png")
OUT = os.path.join(ROOT, "powerbench_360_slowmo_fluido.mp4")

subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error", "-framerate", "24", "-i", SRC,
    "-vf", "setsar=1,minterpolate=fps=48:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none",
    "-r", "48", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "15", "-movflags", "+faststart", OUT,
], check=True)
print("Creato", OUT)
