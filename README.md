# ICU-SLEEP

Code repository for the **Investigation of Sleep in the Intensive Care Unit (ICU-SLEEP)** clinical trial — a single-center, phase 2, double-blind, three-arm, parallel-group, randomized controlled trial of dexmedetomidine for sleep promotion in non-ventilated medical/surgical ICU patients aged 50+.

- **ClinicalTrials.gov:** [NCT03355053](https://clinicaltrials.gov/ct2/show/NCT03355053)
- **IRB:** Mass General Brigham (MGB) #2017P000090
- **Statistical Analysis Plan:** signed 2024-06-19; included in the data publication on bdsp.io.
- **Manuscript:** in preparation (peer review submission upcoming) — citation will be added on acceptance.
- **Data publication:** [bdsp.io project page](https://bdsp.io/projects/phgb6nut6vxcqew5tiek/overview/) (DOI to be added once assigned)

## Where the data lives

The de-identified analytic data is **not in this repository**. Download it from the credentialed-access AWS S3 bucket once you obtain bdsp.io credentials:

```
s3://bdsp-opendata-credentialed/icu-sleep/
```

See [docs/data-access.md](docs/data-access.md) for credentialing and download instructions.

The identified (PHI) version of the source data is retained internally by Brandon Westover at:
```
Brandon - PHI/Datasets/zz_Delirium_Encephalopathy/@Delirium_Encephalopathy_Data Roundup_Identified/ICU-SLEEP (Investigation of Sleep in the ICU)/
```
(in case it is needed for future re-deidentification or audit; not publicly accessible).

## Repository layout

```
ICU_SLEEP/
├── paper-code/             R Markdown analysis pipeline reproducing the paper
│   ├── z0_RR_dat_mgt_did.Rmd     data management (CSV -> rds)
│   ├── z1_RR_tables.Rmd          baseline & outcome tables
│   ├── z2_RR_primary_analysis.Rmd     primary outcome (DFD ordinal logistic)
│   ├── z2_RR_sen_analysis.Rmd         sensitivity analyses
│   ├── z2_RR_sen_forest_plot.Rmd      forest plots
│   ├── z2_RR_survival_analysis.Rmd    time-to-event analyses
│   ├── plots-design-files/      DataGraph .dgraph design files for figures
│   └── data/                    populated by user from the S3 download
│
├── deidentification/       Safe-Harbor de-identification pipeline (raw XLSX -> public CSVs)
│   └── deidentify.R
│
├── ancillary-code/         Companion code from earlier ICU-SLEEP-related repositories
│   ├── icu-sleep-vitals/         Python tooling for plotting vitals (Bedmaster/HL7/EDW)
│   └── icu-sleep-preprocessing/  notebooks and scripts kept for posterity
│
└── docs/
    ├── codebook.md         data dictionary for the public CSVs
    ├── data-access.md      how to obtain the data from S3
    ├── reproducibility.md  how to reproduce the paper's numbers
    └── related-work.md     companion publication (noiselight)
```

## Reproducing the paper

See [docs/reproducibility.md](docs/reproducibility.md) for end-to-end instructions. In brief:

1. Download `ICU-SLEEP_Enrolled_Deidentified.csv` from S3 to `paper-code/data/`.
2. Open the R project; install the package set listed in [paper-code/README.md](paper-code/README.md).
3. Knit, in order: `z0_RR_dat_mgt_did.Rmd` → `z1_RR_tables.Rmd` → the four `z2_*.Rmd` analyses (each in 2-group and 3-group toggles).
4. Numerical outputs (Table 1, Table 2, primary OR/CI/P, secondary, sensitivity, survival, forest) appear in the rendered HTML notebooks. Figures are produced by pasting `write_clip()` outputs into the matching `.dgraph` files in `plots-design-files/` (DataGraph required for figure rendering).

## Related work

- **noiselight** (sound and light recordings from the same ICU course): https://github.com/bdsp-core/noiselight — published as Leone MJ et al., *Chronobiol Int.* 2023. Maintained as a separate repository.

## License

Code: see [LICENSE](LICENSE). Data: distributed via bdsp.io under their credentialed-access data use agreement.

## Citation

See [CITATION.cff](CITATION.cff). On acceptance of the manuscript, the citation will be updated with the published reference and the assigned data DOI.
