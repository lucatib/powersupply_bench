# Powerbench 3D — video del giro a 360°

Video renderizzato del powerbench (modello Fusion) con giro di camera e la shell che sfuma e riappare.

## Video (`video/`)
- `powerbench_360_slowmo_fluido.mp4` — **finale**: slow motion 2x, 5,9 s, 1280×720, 48 fps.
- `powerbench_360_slowmo.mp4` — stessa cosa a 24 fps (v1).
- `powerbench_360_slowmo_dissolvenza.mp4` — slow motion con frame intermedi a dissolvenza (doppi contorni sui pezzi veloci).
- `powerbench_360_dissolvenza.mp4` — base non rallentata, 3 s, 24 fps.

## Come è stato costruito
1. **Render in Fusion** (ray tracing locale, 72 frame, 1280×720, qualità 40) con la camera che orbita attorno al modello.
   Il renderer ignora l'opacità, quindi due passate:
   - `video/frames/visible/` — frame 0–71 con la shell visibile
   - `video/frames/hidden/` — frame 10–58 con la shell nascosta (BodyTop, BodyBot, BodyLeft, BodyRight, Front, Back)
2. **Dissolvenza** (`video/tools/blend_shell.py`): mescola visible/hidden con una curva smoothstep
   (sparisce tra 15% e 35% del giro, nascosta fino al 60%, riappare entro l'80%) → `video/frames/blended/`.
3. **Slow motion** con ffmpeg (interpolazione a movimento stimato, 4x, riprodotta a 48 fps):

```bash
ffmpeg -framerate 24 -i video/frames/blended/frame_%04d.png \
  -vf "setsar=1,minterpolate=fps=96:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none,setpts=2*PTS" \
  -r 48 -c:v libx264 -pix_fmt yuv420p -crf 15 -movflags +faststart video/powerbench_360_slowmo_fluido.mp4
```
Per la versione a dissolvenza sostituire `mi_mode=mci:...` con `mi_mode=blend` e aggiungere `hqdn3d=0:0:4:4`.

## Script Fusion (`video/fusion_scripts/`)
Si installano copiando le cartelle in `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\` e si lanciano con Shift+S.
- `Powerbench360` — cattura il viewport, un PNG per frame (anteprima del movimento).
- `Powerbench360Render` — versione attuale a 216 frame in due passate (shell visibile / nascosta), camera con elevazione fissa.
  I 72 frame di questo progetto sono stati fatti con una versione precedente più semplice (stessa idea, 72 frame).
- `Powerbench360Viewport` — cattura viewport con opacità della shell: **non usabile** su questo modello
  (la shell appare semi-trasparente nel viewport e non sparisce).

## Note
- La vista di partenza è quella corrente di Fusion; la camera ruota attorno al centro del bounding box.
- ffmpeg: `winget install Gyan.FFmpeg`.

## Nel repository
- Su GitHub c'è solo il video finale (`video/powerbench_360_slowmo_fluido.mp4`), per occupare poco spazio.
- I frame PNG intermedi (49 MB) e le versioni intermedie del video restano solo in locale (vedi `.gitignore`); si rigenerano con gli script Fusion.
