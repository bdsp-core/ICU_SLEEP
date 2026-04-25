# Reproducing the paper's numbers

End-to-end instructions for reproducing the ICU-SLEEP paper's tables and statistics.

## Prerequisites

- R 4.5.2 (other 4.x versions likely work; see [R packages](#r-packages) below).
- macOS or Linux. Note: a known macOS-only artifact of the older code path was a case-insensitive filename collision; this repository's `paper-code/` has been patched to be cross-platform.
- DataGraph (paid macOS app) is required to render figures from the `.dgraph` design files. All numerical statistics are reproducible without it.

## R packages

```r
install.packages(c(
  "broom","clipr","dplyr","emmeans","fastshap","forestplot","gamlss",
  "ggplot2","ggprism","ggsci","gofcat","gt","gtsummary","janitor","knitr",
  "labelled","lubridate","magrittr","mice","nnet","openxlsx","ordinal",
  "performance","readr","readxl","scales","sjPlot","skimr","survival",
  "survminer","tableone","tidyr","tidyverse","rmarkdown"
))
```

## Steps

1. **Get the data.** Follow [docs/data-access.md](data-access.md) to download `ICU-SLEEP_Enrolled_Deidentified.csv` to `paper-code/data/`.

2. **Set the working directory** to `paper-code/`.

3. **Knit z0_RR_dat_mgt_did.Rmd**:
   ```bash
   cd paper-code
   CLIPR_ALLOW=TRUE Rscript -e 'rmarkdown::render("z0_RR_dat_mgt_did.Rmd")'
   ```
   This populates `data/rds/` with `itt_full.rds`, `demo.rds`, `group.rds`, `outcome1.rds`, `surv1.rds`, `locations.rds`.

4. **Knit z1_RR_tables.Rmd**:
   ```bash
   CLIPR_ALLOW=TRUE Rscript -e 'rmarkdown::render("z1_RR_tables.Rmd")'
   ```
   Populates `mitt.rds`, `itt.rds` (= as-treated, n=369), `pp.rds` (n=5).

5. **Knit z2_*.Rmd**, switching between 2-group and 3-group toggles:
   - Each script has a single line under `# choose 2 groups or 3 groups`. Comment one out, uncomment the other.
   - Render to differently-named outputs to keep both:
     ```bash
     CLIPR_ALLOW=TRUE Rscript -e 'rmarkdown::render("z2_RR_primary_analysis.Rmd", \
        output_file = "z2_RR_primary_analysis.3group.html")'
     ```

## Expected primary results (paper Table 2 / Abstract)

Run on the de-identified CSV release; profile-likelihood CI from `ordinal::clm` confint:

| Outcome | OR | 95% CI | P |
|---|---|---|---|
| IH-DFD (mITT, unadjusted, imputed) | 0.829 | 0.527–1.296 | 0.415 |
| ICU-DFD (mITT, unadjusted, imputed) | 0.940 | 0.575–1.521 | 0.803 |

mITT N: Placebo=105, Dex=207, total=312.

## Known caveats

- **Figure reproducibility:** numerical figure data is exported via `clipr::write_clip()` and pasted into the matching `.dgraph` file in `paper-code/plots-design-files/`. Without DataGraph, figures cannot be regenerated end-to-end. Numerical tables and statistics are unaffected.
- **PP analysis** is small (n=5) by SAP definition.
- **Date-shifted data:** all date columns in the release are randomly shifted per-patient. Within-patient intervals are exact; absolute dates are not.
