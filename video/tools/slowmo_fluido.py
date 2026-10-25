"""Slow motion fluido: frame sfumati (video/frames/blended) -> video/powerbench_360_slowmo_fluido.mp4.

Interpolazione a movimento stimato 4x (24 -> 96 fps), riprodotta a 48 fps: 3 s diventano 5,9 s.
Richiede ffmpeg (winget install Gyan.FFmpeg).
"""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "frames", "blended", "frame_%04d.png")
OUT = os.path.join(ROOT, "powerbench_360_slowmo_fluido.mp4")

subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error", "-framerate", "24", "-i", SRC,
    "-vf", "setsar=1,minterpolate=fps=96:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none,setpts=2*PTS",
    "-r", "48", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "15", "-movflags", "+faststart", OUT,
], check=True)
print("Creato", OUT)
