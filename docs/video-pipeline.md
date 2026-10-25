# Video del giro a 360° (slow motion fluido)

File finale: `video/powerbench_360_slowmo_fluido.mp4` — 5,9 s, 1280×720, 48 fps (144 frame renderizzati). Giro di camera attorno al modello
con la shell (BodyTop, BodyBot, BodyLeft, BodyRight, Front, Back) che sfuma e riappare prima di chiudere il cerchio.

## Cosa serve
| File | Ruolo |
|---|---|
| `video/fusion_scripts/Powerbench360Render` | Script Fusion: renderizza i 144 frame, in due passate |
| `video/tools/blend_shell.py` | Sfuma la shell mescolando le due passate |
| `video/tools/slowmo_fluido.py` | Slow motion (ffmpeg) → mp4 finale |
| ffmpeg | `winget install Gyan.FFmpeg` |

I frame PNG (`video/frames/`, circa 49 MB) **non sono nel repository**: si ricostruiscono con i passi qui sotto.

## Ricostruire il video
1. **Render in Fusion.** Copia `video/fusion_scripts/Powerbench360Render` in
   `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\`, apri il modello (workspace Render, materiali e ambiente già
   impostati), Shift+S → **Powerbench360Render** → **Run**. Non toccare la vista e lascia Fusion aperto finché non finisce
   (circa 25-30 minuti). Il renderer ignora l'opacità, quindi lo script fa due passate:
   - `video/frames/visible/` — 144 frame con la shell visibile
   - `video/frames/hidden/` — frame 21–116 con la shell nascosta

   Impostazioni: 1280×720, qualità 40; la camera ruota attorno al centro del modello partendo dalla vista corrente,
   con elevazione e distanza fisse (`ELEVATION_DEG`, `FIT` nello script).
2. **Dissolvenza:** `python video/tools/blend_shell.py` → `video/frames/blended/`
   (sparisce tra il 15% e il 35% del giro, nascosta fino al 60%, riappare entro l'80%).
3. **Slow motion:** `python video/tools/slowmo_fluido.py` → il video finale.

Lo slow motion porta i 144 frame veri (24 fps, 6 s) a 48 fps con un'interpolazione a movimento stimato 2x:

```bash
ffmpeg -framerate 24 -i video/frames/blended/frame_%04d.png \
  -vf "setsar=1,minterpolate=fps=48:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none" \
  -r 48 -c:v libx264 -pix_fmt yuv420p -crf 15 -movflags +faststart video/powerbench_360_slowmo_fluido.mp4
```

## Note
- Con 72 frame e interpolazione 4x le sei banane del connettore (oggetti uguali e vicini) venivano sdoppiate nei frame inventati e sfarfallavano: per questo ora i frame renderizzati sono 144 e l'interpolazione è solo 2x.
- La camera parte dalla vista corrente di Fusion, con elevazione (`ELEVATION_DEG`) e distanza (`FIT`) fisse nello script.
- Il viewport di Fusion non è utilizzabile per questo effetto: su questo modello la shell appare semi-trasparente e non sparisce.