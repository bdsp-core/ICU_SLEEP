# ICU-SLEEP — Analysis Pipeline

R Markdown analysis pipeline reproducing the ICU-SLEEP paper's tables, figures, and statistics.

## Inputs

Place the de-identified analytic CSV (download from `s3://bdsp-opendata-credentialed/icu-sleep/`) at:

```
paper-code/data/ICU-SLEEP_Enrolled_Deidentified.csv
```

The pipeline only requires the `Enrolled` sheet (one row per patient, 526 rows). The other sheets (`Delirium`, `Study Drug`, `Adverse Events`) are provided alongside the public release for downstream secondary use but are not consumed by this analysis.

## Pipeline order

1. **`z0_RR_dat_mgt_did.Rmd`** — reads the CSV, cleans column names, defines analysis-population indicators, and writes intermediate `rds` files to `data/rds/`:
   - `itt_full.rds` (526 rows, full ITT pop)
   - `demo.rds`, `group.rds`, `outcome1.rds`, `surv1.rds`, `locations.rds`

2. **`z1_RR_tables.Rmd`** — derives mITT (n=312), as-treated `itt` (n=369), PP (n=5), and produces baseline and outcome summary tables.

3. **`z2_RR_primary_analysis.Rmd`** — primary outcome (in-hospital DFD) and secondary outcome (ICU DFD), modeled as ordinal logistic via `ordinal::clm()`. Includes Kent-style heterogeneity-of-treatment-effect (HTE) panels.

4. **`z2_RR_sen_analysis.Rmd`** — sensitivity analyses (covariate adjustment, alternate populations).

5. **`z2_RR_sen_forest_plot.Rmd`** — subgroup forest plots.

6. **`z2_RR_survival_analysis.Rmd`** — time-to-event analyses.

## Group toggles (2-group vs 3-group)

The primary, sensitivity, and survival scripts each contain a single toggle that switches between 2-group (Dex pooled vs Placebo) and 3-group (Dex 0.3 / Dex 0.1 / Placebo). Search each `.Rmd` for the comment `# choose 2 groups or 3 groups` and uncomment the desired line.

## R environment

Tested under R 4.5.2. Required packages:

```
broom, clipr, dplyr, emmeans, fastshap, gamlss, ggplot2, ggprism, ggsci, gofcat,
gt, gtsummary, janitor, knitr, labelled, lubridate, magrittr, nnet, openxlsx,
ordinal, performance, readr, readxl, scales, sjPlot, skimr, survival, survminer,
tableone, tidyr, tidyverse, forestplot, mice, rmarkdown
```

`write_clip()` requires `CLIPR_ALLOW=TRUE` when running headless:

```bash
CLIPR_ALLOW=TRUE Rscript -e 'rmarkdown::render("z0_RR_dat_mgt_did.Rmd")'
```

## Figures

Numerical figure data is exported via `clipr::write_clip()` and pasted into the corresponding DataGraph file in `plots-design-files/`. **DataGraph (a paid macOS application) is required for full figure reproduction**; the `.Rmd` notebooks reproduce all numerical statistics without it.
