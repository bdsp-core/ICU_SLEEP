# De-identification pipeline

This script transforms the source semi-deidentified Excel workbook into the public-release CSVs that meet HIPAA Safe Harbor requirements.

## Source

The non-public source workbook (held under PHI controls by the study team) is `ICU-SLEEP_Data_P1_Deidentified_11.26.25.xlsx`. It contains 4 sheets: Enrolled, Delirium, Study Drug, Adverse Events. As received it had names/MRN/ZID redacted to `[Redacted]` but **retained DOB and full real-world dates** — both Safe Harbor identifiers.

## What `deidentify.R` does

1. **Drops nothing structural.** Column positions are preserved so the analysis pipeline's position-suffixed column names (`..._123`, `..._134`, etc.) remain stable.
2. **Blanks the DOB column.** Set to all-NA. (Patient age is preserved and capped at 89.)
3. **Caps `Age (years) [at enrollment]` at 89** to satisfy the Safe Harbor "ages over 89" rule.
4. **Per-SID date shift.** Each patient receives a deterministic random offset in days ∈ [-1095, +1095] (~3 years). Every datetime value (native POSIXct columns + character columns containing Excel-serial dates) is shifted by the patient's offset. Within-patient intervals are preserved exactly, so all derived `days_from_X_to_Y` outcomes are unchanged. The deterministic seed (default `20260425`) is recorded in the script so the deidentification is reproducible given the same source file.
5. **Free-text date column** (`Re-admit date` — contained free-form dates like "3/30/18") is replaced with `[Date redacted]`.
6. **Outputs four CSVs**, one per sheet, plus a `MANIFEST.txt` describing what was done.
7. **Writes an internal-only shift table** (`_INTERNAL_DO_NOT_PUBLISH_shifts.csv`) which would re-identify dates if leaked. **This file MUST be kept in the PHI-protected location alongside the original source XLSX.**

## Outputs

- `ICU-SLEEP_Enrolled_Deidentified.csv` (526 rows × 308 cols)
- `ICU-SLEEP_Delirium_Deidentified.csv` (7,364 rows × 189 cols)
- `ICU-SLEEP_Study_Drug_Deidentified.csv` (1,421 rows × 50 cols)
- `ICU-SLEEP_Adverse_Events_Deidentified.csv` (2,878 rows × 18 cols)
- `MANIFEST.txt`
- `_INTERNAL_DO_NOT_PUBLISH_shifts.csv`  ← never publish

## Verification

The primary outcome model run on the de-identified CSVs produces results bit-identical (to the precision the paper reports) to the same model on the un-shifted source data:

| Outcome | Source XLSX | Deid CSV | Paper |
|---|---|---|---|
| IH-DFD OR (95% CI) profile | 0.8295 (0.527–1.296) | 0.8295 (0.527–1.296) | 0.829 (0.527–1.296) |
| ICU-DFD OR (95% CI) profile | 0.9402 (0.575–1.521) | 0.9402 (0.575–1.521) | 0.940 (0.575–1.521) |

This confirms the date-shift preserves all interval-based statistics.
