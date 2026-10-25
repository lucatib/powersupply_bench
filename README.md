# powersupply_bench

Modello 3D (Autodesk Fusion) del banco alimentatore: 12 design del progetto cloud **PowerSupply_Bench**,
esportati come archivi Fusion (`.f3d`).

## Contenuto (models/)
| Design | Dimensione |
|---|---|
| AC 3-Pin With Fuse | 2.25 MB |
| ANTI-VANDAL PUSH BUTTON DIA.22 | 0.24 MB |
| Banana | 0.41 MB |
| Case Accessories | 0.56 MB |
| Case Front Back | 1.25 MB |
| Case | 3.33 MB |
| Display | 0.29 MB |
| Fan | 1.15 MB |
| PowerSupply | 2.84 MB |
| StepDown | 0.45 MB |
| TempControl | 2.72 MB |
| Temperature Clip | 0.25 MB |

Totale circa 15,7 MB. Gli `.f3d` sono già compressi (zip): nessun'altra compressione conviene.

## Aprirli
In Fusion: **File → Open → Open from my computer**, oppure trascina il file nella finestra.

## Riesportare dal cloud
Lo script `tools/ExportPowerSupply` esporta tutti i design del progetto (sola lettura, non salva nulla nel cloud).
Copia la cartella in `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\`, poi in Fusion Shift+S → **ExportPowerSupply** → **Run**.

## Altre cartelle
- `step/` — pezzi del case in STEP/3MF per stampa e CAM (dettagli in [docs/export-fusion.md](docs/export-fusion.md)).
- `video/` — video del giro a 360° con la shell che sfuma (solo la versione fluida) con gli script per ricostruirlo ([docs/video-pipeline.md](docs/video-pipeline.md)).
- `docs/` — documentazione.