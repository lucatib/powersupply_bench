# powersupply_bench

3D model (Autodesk Fusion) of the bench power supply: 12 designs from the cloud project **PowerSupply_Bench**,
exported as Fusion archives (`.f3d`).

## Capabilities
- **1500 W** adjustable AC→DC supply (220 VAC in, 0–72 VDC) feeding the two outputs.
- **Dual output, 0–65 V and 0–22 A each**, from two ZK-6522C step-down modules.
- **Voltage and current control**: each output works in constant voltage or constant current mode.
- **Colour display with graph** on each output, showing voltage, current and power, with a live graph.
- **Temperature-controlled cooling**: two 50 mm PWM fans driven by a temperature controller with its own display and probe.

The two outputs share the 1500 W supply, so their combined power stays within 1500 W.
Full parts list with links: [docs/components.md](docs/components.md).

## Contents (models/)
| Design | Size |
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

About 15.7 MB in total. The `.f3d` files are already compressed (zip): further compression does not help.

## Opening them
In Fusion: **File → Open → Open from my computer**, or drag the file into the window.

## Re-exporting from the cloud
The `tools/ExportPowerSupply` script exports every design in the project (read-only, nothing is saved to the cloud).
Copy the folder to `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\`, then in Fusion press Shift+S → **ExportPowerSupply** → **Run**.

## Other folders
- `step/` — case parts as STEP/3MF for printing and CAM (details in [docs/export-fusion.md](docs/export-fusion.md)).
- `video/` — 360° turntable video with the fading shell (smooth version only), with the scripts to rebuild it ([docs/video-pipeline.md](docs/video-pipeline.md)).
- `docs/` — documentation, including the [list of components](docs/components.md) with links.
