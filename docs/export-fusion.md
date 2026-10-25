# Esportare i design dal cloud Fusion

Lo script `tools/ExportPowerSupply` esporta tutti i design del progetto cloud **PowerSupply_Bench** come archivi `.f3d`
in `models/` (sola lettura: non salva nulla nel cloud, i file già aperti restano aperti).

1. Copia `tools/ExportPowerSupply` in `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\`.
2. In Fusion: Shift+S → **ExportPowerSupply** → **Run** (se non compare, chiudi e riapri la finestra).
3. Il log è in `run.log` accanto allo script.

Gli `.f3d` sono già compressi (zip): ricomprimerli non conviene e può renderli illeggibili.

## STEP e 3MF (`step/`)
| File | Dimensione |
|---|---|
| Case.3mf | 7.02 MB |
| Case_back.step | 0.14 MB |
| Case_bot.step | 1.78 MB |
| Case_front.step | 0.28 MB |
| Case_left.step | 3.32 MB |
| Case_right.step | 4.07 MB |
| Case_top.step | 1.29 MB |
| Fan_grid.step | 0.48 MB |
| Foot.step | 0.03 MB |

I `.step` sono testo e Git li comprime bene; `Case.3mf` è già compresso (zip).
