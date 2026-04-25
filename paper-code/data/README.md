# `data/` — populated by the user

This folder is intentionally empty in the repository. Place the public data files here after downloading from S3 (see [docs/data-access.md](../../docs/data-access.md)):

```
paper-code/data/
├── ICU-SLEEP_Enrolled_Deidentified.csv   <-- required by the analysis pipeline
└── rds/                                  <-- created by z0_/z1_ runs (gitignored)
```

The other public CSVs (`Delirium`, `Study Drug`, `Adverse Events`) are not consumed by this pipeline but are available alongside the Enrolled CSV in the S3 release for downstream secondary use.
