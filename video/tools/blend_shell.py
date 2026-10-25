"""Sfuma la shell: mescola i frame con shell visibile (A) e nascosta (B) e monta l'MP4."""
import os, shutil, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FF = "ffmpeg"  # winget install Gyan.FFmpeg
A_DIR = os.path.join(ROOT, "frames", "visible")
B_DIR = os.path.join(ROOT, "frames", "hidden")
TMP = os.path.join(ROOT, "frames", "blended")
FRAMES = 144
FADE_OUT = (0.15, 0.35)
FADE_IN = (0.60, 0.80)
EXPECTED_B = 96

def smooth(a, b, t):
    x = min(1.0, max(0.0, (t - a) / (b - a)))
    return x * x * (3 - 2 * x)

def alpha(t):
    return 1.0 - smooth(*FADE_OUT, t) * (1.0 - smooth(*FADE_IN, t))

# aspetta i frame nascosti
deadline = time.time() + 90 * 60
last, last_change = -1, time.time()
while True:
    n = len([f for f in os.listdir(B_DIR) if f.startswith("frame_")]) if os.path.isdir(B_DIR) else 0
    if n >= EXPECTED_B:
        break
    if n != last:
        last, last_change = n, time.time()
    elif time.time() - last_change > 4 * 60 or time.time() > deadline:
        print("STALLO a %d frame" % n); sys.exit(1)
    time.sleep(10)
time.sleep(3)

shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(TMP)
for i in range(FRAMES):
    a = os.path.join(A_DIR, "frame_%04d.png" % i)
    b = os.path.join(B_DIR, "frame_%04d.png" % i)
    out = os.path.join(TMP, "frame_%04d.png" % i)
    w = alpha(i / FRAMES)
    if w >= 0.999 or not os.path.exists(b):
        shutil.copy(a, out)
    else:
        expr = "A*%.4f+B*%.4f" % (w, 1 - w)
        subprocess.run([FF, "-y", "-loglevel", "error", "-i", a, "-i", b, "-filter_complex",
                        "[0][1]blend=all_expr='%s'" % expr, "-frames:v", "1", out], check=True)
print("Frame sfumati in %s: ora lancia slowmo_fluido.py" % TMP)
