# Data access

The de-identified ICU-SLEEP analytic data is distributed via the BDSP credentialed-access platform and stored in AWS S3. Source code in this repository does not include the data files.

## Step 1: Obtain credentials via bdsp.io

Visit the project landing page: https://bdsp.io/projects/phgb6nut6vxcqew5tiek/overview/

Follow bdsp.io instructions to:
1. Create a bdsp.io account.
2. Complete the credentialed user training.
3. Sign the data use agreement.

Once approved, bdsp.io will provide AWS access credentials.

## Step 2: Download from S3

Bucket: `s3://bdsp-opendata-credentialed/icu-sleep/`

Listing:

```bash
aws s3 ls s3://bdsp-opendata-credentialed/icu-sleep/
```

Download a single file:

```bash
aws s3 cp s3://bdsp-opendata-credentialed/icu-sleep/ICU-SLEEP_Enrolled_Deidentified.csv \
          paper-code/data/ICU-SLEEP_Enrolled_Deidentified.csv
```

Download everything:

```bash
aws s3 sync s3://bdsp-opendata-credentialed/icu-sleep/ ./icu-sleep-data/
```

## Files in the release

| File | Rows | Cols | Description |
|---|---|---|---|
| `ICU-SLEEP_Enrolled_Deidentified.csv` | 526 | 308 | one row per enrolled patient (used by the analysis pipeline) |
| `ICU-SLEEP_Delirium_Deidentified.csv` | 7,364 | 189 | longitudinal delirium evaluations |
| `ICU-SLEEP_Study_Drug_Deidentified.csv` | 1,421 | 50 | per-night study drug administration records |
| `ICU-SLEEP_Adverse_Events_Deidentified.csv` | 2,878 | 18 | adverse events log |
| `ICU-SLEEP_Data_Deidentified_PUBLIC.xlsx` | — | — | one workbook with 4 sheets matching the CSVs above; preserves source cell colors, fonts, and study-team comments (lost in CSV format). For visual inspection; use the CSVs for programmatic analysis. |
| `MANIFEST.txt` | — | — | provenance and de-identification summary |
| `ICU-SLEEP_SAP_06.19.24_Signed.pdf` | — | — | signed Statistical Analysis Plan |
| `codebook.md` | — | — | data dictionary (also see [docs/codebook.md](codebook.md)) |
| `README.txt` | — | — | top-level overview matching this repository's README |

## What is NOT in the release

- Direct identifiers (names, MRN, DOB, ZID) — removed.
- Original (non-shifted) date values — removed.
- The per-patient date-shift table — held internally by the study PI under PHI controls.
- Raw waveform/Bedmaster recordings — separate, large, governed by separate access procedures.
