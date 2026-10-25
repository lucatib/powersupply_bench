# 360° turntable video (smooth slow motion)

Final file: `video/powerbench_360_slowmo_fluido.mp4` — 5.9 s, 1280×720, 48 fps (144 rendered frames). The camera circles the model
while the shell (BodyTop, BodyBot, BodyLeft, BodyRight, Front, Back) fades out and comes back before the loop closes.

## What you need
| File | Role |
|---|---|
| `video/fusion_scripts/Powerbench360Render` | Fusion script: renders the 144 frames in two passes |
| `video/tools/blend_shell.py` | Fades the shell by blending the two passes |
| `video/tools/slowmo_fluido.py` | Slow motion (ffmpeg) → final mp4 |
| ffmpeg | `winget install Gyan.FFmpeg` |

The PNG frames (`video/frames/`, about 49 MB) **are not in the repository**: rebuild them with the steps below.

## Rebuilding the video
1. **Render in Fusion.** Copy `video/fusion_scripts/Powerbench360Render` to
   `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\`, open the model (Render workspace, with materials and environment
   already set), Shift+S → **Powerbench360Render** → **Run**. Do not touch the view and leave Fusion open until it finishes
   (about 25–30 minutes). The renderer ignores opacity, so the script makes two passes:
   - `video/frames/visible/` — 144 frames with the shell visible
   - `video/frames/hidden/` — frames 21–116 with the shell hidden

   Settings: 1280×720, quality 40; the camera turns around the centre of the model starting from the current view,
   with fixed elevation and distance (`ELEVATION_DEG`, `FIT` in the script).
2. **Fade:** `python video/tools/blend_shell.py` → `video/frames/blended/`
   (fades out between 15% and 35% of the turn, stays hidden until 60%, is back by 80%).
3. **Slow motion:** `python video/tools/slowmo_fluido.py` → the final video.

Slow motion takes the 144 real frames (24 fps, 6 s) to 48 fps with 2x motion-compensated interpolation:

```bash
ffmpeg -framerate 24 -i video/frames/blended/frame_%04d.png \
  -vf "setsar=1,minterpolate=fps=48:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none" \
  -r 48 -c:v libx264 -pix_fmt yuv420p -crf 15 -movflags +faststart video/powerbench_360_slowmo_fluido.mp4
```

## Notes
- With 72 frames and 4x interpolation, the six banana posts on the connector (identical objects close together) were doubled in the invented frames and flickered: that is why 144 frames are now rendered and the interpolation is only 2x.
- The camera starts from the current Fusion view, with elevation (`ELEVATION_DEG`) and distance (`FIT`) fixed in the script.
- The Fusion viewport cannot be used for this effect: on this model the shell looks semi-transparent and does not disappear.
