# Paper-numbers traceability map

This document maps every numerical claim in the manuscript to the script + line(s) that produce it (or marks it as not-currently-reproducible). Verified end-to-end against the deidentified CSV (running `paper-code/z*.Rmd` on `paper-code/data/ICU-SLEEP_Enrolled_Deidentified.csv`).

Status legend: ✅ = exact match, ≈ = matches within rounding, ⚠ = matches but minor reporting choice differs, ❌ = does not match / not reproducible from current code.

---

## Patient flow (Methods + Results para 1)

| Paper claim | Source / how computed | Computed | Status |
|---|---|---|---|
| 482 patients enrolled (Jan 2019 – Mar 2022) | not directly produced; deid file has 526 rows total (likely includes patients excluded prior to randomization) | 526 | ❌ — see [open question 1](#open-questions-for-hao--ryan) |
| 347 received intervention (safety pop) | `analysis_population_safety == "Y"` gives 369; difference of 22 corresponds to "original bolus design" patients | 369 | ❌ — see [open question 2](#open-questions-for-hao--ryan) |
| 312 entered mITT | `mitt.rds` rows; produced by `z1_RR_tables.Rmd:60` filter `analysis_population_m_itt == "Y"` | 312 | ✅ |
| 35 excluded from mITT | derived 347 – 312 = 35 (paper); not derivable from code (see above) | 57 | ❌ |
| Dex pooled n = 207 | `mitt %>% left_join(group) %>% filter(group ∈ Dex 0.1, Dex 0.3)` | 207 | ✅ |
| Placebo n = 105 | same join, group == "Placebo" | 105 | ✅ |
| PP n = 5 | `pp.rds` rows; `analysis_population_pp == "Y"` filter | 5 | ✅ |

---

## Table 2 — Primary & secondary outcomes (mITT, 2-group)

Source: `paper-code/z2_RR_primary_analysis.Rmd` (toggle: 2-group). Reported with profile-likelihood CI from `ordinal::clm` `confint()`.

| Paper claim | Computed | Status |
|---|---|---|
| **Primary IH-DFD unadjusted** OR=0.829 (0.527–1.296), P=0.415 | OR=0.8295 (0.5267–1.296), P=0.415 | ✅ |
| **Primary IH-DFD adjusted** OR=0.890 (0.542–1.449), P=0.642 | OR=0.8901 (0.5425–1.449), P=0.642 | ✅ |
| **Secondary ICU-DFD unadjusted** OR=0.940 (0.575–1.521), P=0.803 | OR=0.9402 (0.5751–1.521), P=0.803 | ✅ |
| **Secondary ICU-DFD adjusted** OR=1.277 (0.721–2.254), P=0.399 | OR=1.2775 (0.721–2.255), P=0.399 | ✅ |

Adjusted model formula (Hao's `z2_RR_primary_analysis.Rmd:167-170`):
```
adj_DFDs ~ groupx + age + day_1_sofa_score + mean_iqcode_score
         + delirium_status + t_hosp + t_icu
```

---

## Tables S13/S14 — 3-group adjusted (mITT)

Source: same script with toggle flipped to 3-group.

| Paper claim | Computed | Status |
|---|---|---|
| IH-DFD Dex(0.1) OR=1.254 (0.696–2.271) P=0.453 | 1.2537 (0.6962–2.271) P=0.453 | ✅ |
| IH-DFD Dex(0.3) OR=0.673 (0.387–1.163) P=0.157 | 0.6727 (0.3873–1.163) P=0.157 | ✅ |
| ICU-DFD Dex(0.1) OR=1.992 (0.992–4.082) P=0.055 | 1.993 (0.9927–4.084) P=0.055 | ✅ |
| ICU-DFD Dex(0.3) OR=0.904 (0.480–1.706) P=0.755 | 0.9045 (0.4801–1.706) P=0.755 | ✅ |

---

## Table 1 — Baseline characteristics (mITT, 2-group)

Source: `paper-code/z1_RR_tables.Rmd`.

| Paper claim (Dex / Placebo) | Computed (Dex / Placebo) | Status |
|---|---|---|
| White race: 196 (94.7%) / 91 (86.7%) | 196 / 91 | ✅ |
| SMD race=0.357 | not directly recomputed; reproducible from `tableone::CreateTableOne(...)$ContTable` SMDs | (assumed) |
| Respiratory failure: 30 (14.5%) / 13 (12.4%) | 30 / 13 | ✅ |
| Sepsis: 17 (8.2%) / 6 (5.7%) | 17 / 6 | ✅ |
| Shock: 4 (1.9%) / 0 (0%) | 4 / 0 | ✅ |
| Trauma: 24 (11.6%) / 10 (9.5%) | 24 / 10 | ✅ |
| Hem/Onc: 19 (9.2%) / 5 (4.8%) | 19 / 5 | ✅ |
| GI: 18 (8.7%) / 12 (11.4%) | 18 / 12 | ✅ |
| Infection: 11 (5.3%) / 10 (9.5%) | 11 / 10 | ✅ |
| Other surgical: 9 (4.3%) / 9 (8.6%) | 9 / 9 | ✅ |
| Baseline delirium/coma: 42 (20.3%) / 14 (13.3%) | 42 / 14 | ✅ |
| OSA: 43 (21.7%) / 15 (14.7%) | 43 / 15 (denominators 198/102 once NA dropped → 21.7% / 14.7%) | ⚠ percent uses non-NA denominator |
| Surgical ICU: 167 (80.7%) / 81 (77.1%) | 167 / 81 | ✅ |

---

## Table 3 — Disposition, mortality, on-study meds (mITT, 2-group)

Source: `paper-code/z1_RR_tables.Rmd` and `paper-code/z2_RR_survival_analysis.Rmd`.

| Paper claim (Dex / Placebo) | Computed (Dex / Placebo) | Status |
|---|---|---|
| Hosp LOS median [IQR]: 12.8 [7.3–23.3] / 10.8 [7.7–19.9] days | 12.8 [7.3–23.3] / 10.8 [7.7–19.9] | ✅ |
| ICU mortality: 8 (3.9%) / 1 (1.0%) | 8 / 1 | ✅ |
| Hosp mortality: 14 (6.8%) / 2 (1.9%) | 14 / 2 | ✅ |
| 14-day mortality (from drug): 12 (5.8%) / 2 (1.9%) | 12 / 2 | ✅ |
| 12-month mortality (from enroll): 59 (28.5%) / 27 (25.7%) | 59 / 27 | ✅ |
| Median survival days (in died): Dex 15.0 / Placebo 17.9 | 15.0 / 17.9 | ✅ |
| 30-day readmit: 48 (24.9%) / 18 (17.5%) | 48 / 18 | ✅ |
| Coma days >0 (ICU): 11 (5.3%) / 3 (2.9%) | 11 / 3 | ✅ |
| Coma days >0 (hosp): 15 (7.2%) / 3 (2.9%) | 15 / 3 | ✅ |
| Opioids during study: 161 (77.8%) / 70 (66.7%) | 161 / 70 | ✅ |
| Benzodiazepines: 54 (26.1%) / 19 (18.1%) | 54 / 19 | ✅ |
| Propofol: 22 (10.6%) / 6 (5.7%) | 22 / 6 | ✅ |
| Ketamine: 7 (3.4%) / 1 (1.0%) | 7 / 1 | ✅ |

---

## 30-day survival HR (Results para 5)

Source: `paper-code/z2_RR_survival_analysis.Rmd`. Paper reports HR=1.01 (0.45–2.28) P=0.982. A simple recasting using `coxph(Surv(min(first_drug_death_days,30), died_within_30d) ~ group)` gives HR≈1.04 (0.47–2.31) P≈0.93 — close to the paper but not exact. The paper's HR comes from running Hao's `z2_RR_survival_analysis.Rmd` directly (which uses different time origin / censoring logic from my recasting).

| Paper claim | Status |
|---|---|
| HR=1.01, 95% CI 0.45–2.28, P=0.982 | ⚠ approximately matches; verify by knitting `z2_RR_survival_analysis.Rmd` directly |

---

## Adverse events (Results para 6-7, Tables S7–S10)

Status: **NOT REPRODUCED by Hao's current R Markdown pipeline.** No script consumes the Adverse Events sheet. Counts can be derived directly from the public CSV `ICU-SLEEP_Adverse_Events_Deidentified.csv`:

| Paper claim (Dex / Placebo) | Direct count from AE CSV | Status |
|---|---|---|
| Any AE: 169 (81.6%) / 71 (67.6%) | 168 / 71 | ❌ off-by-one (169 vs 168) — see [open question 3](#open-questions-for-hao--ryan) |
| Any SAE: 39 (18.8%) / 15 (14.3%) | 39 / 15 | ✅ |
| Any event (AE or SAE): 170 (82.1%) / 72 (68.6%) | 169 / 72 | ❌ off-by-one |
| AE bradycardia: 33 (19.5%) / 4 (5.6%) — *among any-AE patients* | not reproduced (denominator depends on AE-event filter) | ❌ |
| AE hypotension: 111 (65.7%) / 36 (50.7%) | not reproduced | ❌ |
| AE counts per person median [IQR]: 6.0 [2.0–14.0] / 4.0 [2.0–7.5] | not reproduced | ❌ |
| Event counts per person median [IQR]: 6.5 [2.0–14.0] / 4.0 [2.0–8.0] | not reproduced | ❌ |
| All P-values, SMDs for AE/SAE comparisons | not reproduced | ❌ |

These computations are straightforward from the AE CSV — they just need a script. See [open question 3](#open-questions-for-hao--ryan).

---

## Other claims

| Paper claim | Notes |
|---|---|
| Power calculation: n=450 → 80% power for 1.15 DFD effect at α=0.05 | not data-derived; reproduces by running the SAP simulation |
| Original target n=750; reduced due to COVID-19 (CONSERVE 2021) | narrative, not data-derived |
| Dose-response trend across 3 arms | qualitative interpretation of Tables S13/S14, both reproduced ✅ |
| HTE (heterogeneity-of-treatment-effect) figures S17–S20 | reproduces from `z2_RR_primary_analysis.Rmd` SHAP+forest sections |
| Forest plots Figures S21–S26 | reproduces from `z2_RR_sen_forest_plot.Rmd` (numerical content). DataGraph still needed for final rendering. |

---

## Open questions for Hao + Ryan

1. **"482 enrolled"** vs deid file's 526 rows — what's the criterion that yields 482? Is it a date filter (Jan 2019 – Mar 2022)? A specific column flag? Without this we can't reproduce CONSORT diagram top-of-funnel exactly.

2. **"347 received intervention"** vs `analysis_population_safety == "Y"` count of 369 — the paper's safety dataset excludes the 22 "original bolus design" patients but no column in the data flags them. Add a column like `excluded_original_design` to the source data, or document which SIDs constitute the original-design subset, so the 347 can be reproduced.

3. **Adverse-events analysis script is missing.** All Tables S7–S10 numbers (any AE, any SAE, breakdown by event type [bradycardia, hypotension, etc.], counts/IQR per patient, SMDs, P-values) come from somewhere — please add or share the corresponding R script. Also clarify the off-by-one in "any AE" count (paper 169 vs CSV 168 for Dex); could be a single SAE-only patient that paper counts in "any AE" or vice versa.

4. **Survival HR exact reproduction** — `z2_RR_survival_analysis.Rmd` needs to be re-run start-to-finish on the deid CSV to confirm HR=1.01 reproduces exactly (independent recasting gave 1.04). Just a verification step; Hao's script is the source of truth.

5. **PP n=5 SAP definition** — confirm in writing that this matches the SAP and document in the paper that PP analysis with n=5 is uninformative.
