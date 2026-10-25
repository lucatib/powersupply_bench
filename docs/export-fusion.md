# Exporting the designs from the Fusion cloud

The `tools/ExportPowerSupply` script exports every design in the cloud project **PowerSupply_Bench** as `.f3d` archives
into `models/` (read-only: nothing is saved to the cloud, and files that are already open stay open).

1. Copy `tools/ExportPowerSupply` to `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\`.
2. In Fusion: Shift+S → **ExportPowerSupply** → **Run** (if it does not appear, close and reopen the window).
3. The log is in `run.log` next to the script.

The `.f3d` files are already compressed (zip): compressing them again does not help and can make them unreadable.

## STEP and 3MF (`step/`)
| File | Size |
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

The `.step` files are text and Git compresses them well; `Case.3mf` is already compressed (zip).
