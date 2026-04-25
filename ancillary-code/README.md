# Ancillary code

This directory consolidates code from two earlier repositories that supported the ICU-SLEEP study but are not part of the core paper analysis. Material is preserved here because it may be useful for downstream secondary work (vitals processing, sleep-stage analysis, breathing data, etc.).

## Subdirectories

### `icu-sleep-vitals/`
Python tooling for plotting patient vitals from Bedmaster, HL7, and EDW data sources. Originally `bdsp-core/ICU-sleep-vitals` (now archived, redirected here).

### `icu-sleep-preprocessing/`
Mixed Jupyter notebooks and Python scripts originally in `bdsp-core/ICU-Sleep` (now archived, redirected here). Contents include:

- `bedmaster_conversion/` — utilities for handling Bedmaster recordings.
- `code1/` — mostly Jupyter notebooks for various preprocessing and analysis explorations (breathing, sleep staging, CPC, ECG, vital signs). **Some notebooks are unrelated to ICU-SLEEP** (e.g., Covid-19 hypoxia/sedation studies that happened to share a workspace) — they are kept for traceability but are not part of the trial pipeline.
- `BP_values_EDW.ipynb`, `medication_categories.xlsx` — supplemental processing.

**Removed during consolidation:**
- Two large vendored MATLAB toolboxes (`Cardiovascular_Toolbox`, `chronux_toolbox`) — these are third-party and easily obtained from their original sources. Drop reduced repo size by ~50 MB.
- Large output binaries (multi-MB `.tiff` plots, `.svg` figures, `cpc_sample/` data dump) — regeneratable.
- `BackupFiles/`, `*-Copy*.ipynb`, `.~lock.*`, `.ipynb_checkpoints/` — cruft.

The original repositories' git histories are not preserved in this consolidated repo. To inspect original commit history, see the archived upstream repos at:
- `bdsp-core/ICU-Sleep` (archived)
- `bdsp-core/ICU-sleep-vitals` (archived)

## Code quality caveat

This is exploratory research code. Paths are typically hardcoded for legacy MGB compute environments and won't run as-is. Treat it as reference material and a starting point for new analyses.
