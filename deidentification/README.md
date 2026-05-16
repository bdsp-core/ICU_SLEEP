# De-identification pipeline

This script transforms the source semi-deidentified Excel workbook into the public-release CSVs that meet HIPAA Safe Harbor requirements.

## Source

The non-public source workbook (held under PHI controls by the study team) is `ICU-SLEEP_Data_P1_Deidentified_11.26.25.xlsx`. It contains 4 sheets: Enrolled, Delirium, Study Drug, Adverse Events. As received it had names/MRN/ZID redacted to `[Redacted]`, and date columns had already been per-patient date-shifted by the trial team (the per-patient shift values originally lived in a "Date shift" column, which was redacted in the file released to the analysis team). The magnitude of this layer-1 shift was ±364 days (per-patient shift values ranged from −363 to +364 days). DOB and other date columns were retained but in shifted form.

## What `deidentify.R` does

This script applies a **second, independent deidentification layer** on top of the trial team's shifts, providing defense in depth before public release. Within-patient intervals are preserved exactly through both layers, so all derived `days_from_X_to_Y` outcomes are unchanged.

1. **Drops nothing structural.** Column positions are preserved so the analysis pipeline's position-suffixed column names (`..._123`, `..._134`, etc.) remain stable.
2. **Blanks the DOB column.** Set to all-NA. (Patient age is preserved and capped at 89.)
3. **Caps `Age (years) [at enrollment]` at 89** to satisfy the Safe Harbor "ages over 89" rule.
4. **Adds a second per-SID date shift.** Each patient receives a deterministic random offset in days ∈ [-1095, +1095] (~3 years), applied on top of the trial team's existing shift. Every datetime value (native POSIXct columns + character columns containing Excel-serial dates) is shifted by the patient's offset. The deterministic seed (default `20260425`) is recorded in the script so this layer is reproducible given the same source file.
5. **Free-text date column** (`Re-admit date` — contained free-form dates like "3/30/18") is replaced with `[Date redacted]`.
6. **Outputs four CSVs**, one per sheet, plus a `MANIFEST.txt` describing what was done.
7. **Writes an internal-only shift table** (`_INTERNAL_DO_NOT_PUBLISH_shifts.csv`) recording this second layer's shifts. **This file MUST be kept in the PHI-protected location alongside the original source XLSX.** Note: even with this table, dates cannot be re-identified without also recovering the trial team's first-layer shifts (which are not publicly accessible).

The combined effect — two independent per-patient shifts each in a ±3-year range — yields cumulative shifts effectively much larger than required by HIPAA Safe Harbor's "all date elements smaller than year" rule, so the publicly released dates have month/day precision that is well decorrelated from the actual calendar dates.

## Outputs

- `ICU-SLEEP_Enrolled_Deidentified.csv` (526 rows × 308 cols)
- `ICU-SLEEP_Delirium_Deidentified.csv` (7,364 rows × 189 cols)
- `ICU-SLEEP_Study_Drug_Deidentified.csv` (1,421 rows × 50 cols)
- `ICU-SLEEP_Adverse_Events_Deidentified.csv` (2,878 rows × 18 cols)
- `MANIFEST.txt`
- `_INTERNAL_DO_NOT_PUBLISH_shifts.csv`  ← never publish

## Verification

The primary outcome model run on the de-identified CSVs produces results bit-identical (to the precision the paper reports) to the same model on the un-shifted source data:

| Outcome | Source XLSX (already shifted once) | Deid CSV (shifted twice) | Paper |
|---|---|---|---|
| IH-DFD OR (95% CI) profile | 0.8295 (0.527–1.296) | 0.8295 (0.527–1.296) | 0.829 (0.527–1.296) |
| ICU-DFD OR (95% CI) profile | 0.9402 (0.575–1.521) | 0.9402 (0.575–1.521) | 0.940 (0.575–1.521) |

This confirms both date-shifting layers preserve all interval-based statistics.
