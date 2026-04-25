# ICU-SLEEP public data — codebook

Auto-generated from the public CSV release. For each column, lists data type, missingness, and a brief value summary. Column names retain the original Excel headers (with positional suffixes `...123` etc. preserved by readxl/clean_names for duplicate-header pairs).

## ICU-SLEEP_Adverse_Events_Deidentified.csv

**Rows:** 2878  **Columns:** 18

| # | Column | Type | n non-NA | n unique | Summary |
|---|--------|------|----------|----------|---------|
| 1 | `ZID` | character | 2878 | 1 | top: [Redacted] |
| 2 | `SID` | character | 2878 | 284 | top: 312 \| 387 \| 383 |
| 3 | `SID Status` | character | 2878 | 3 | top: Retained (Final) \| Retained (Final); Repeat subject \| Replaced |
| 4 | `Event` | character | 2878 | 8 | top: bp_low_abs_ae \| hr_high_abs_ae \| bp_high_abs_ae |
| 5 | `Event_Value` | numeric | 2867 | 124 | min=35, median=93, max=201 |
| 6 | `Event_Type` | character | 2878 | 2 | top: AE \| SAE |
| 7 | `Event_Time` | character | 2878 | 2612 | top: 2021-05-07T20:00:00 \| 2021-05-08T02:00:00 \| 2021-10-15T18:00:00 |
| 8 | `...8` | character | 5 | 2 | top: _ |
| 9 | `Event during study drug administration?` | character | 2878 | 1 | top: Y |
| 10 | `Type of AE_description` | character | 2878 | 7 | top: Specified AEs not reported as SAEs \| SAE (Serious Adverse Event) \| SAE (Serious Adverse Event); AE of Special Inte... |
| 11 | `Event_description` | character | 2878 | 18 | top: Hypotension (systolic blood pressure (SBP) <95 ... \| Tachycardia (>100 bpm or increase >20% from pre... \| Hypertension (SBP > 160 mm Hg or increase >20% ... |
| 12 | `Severity` | character | 135 | 4 | top: Severe \| Mild \| Moderate |
| 13 | `Expectedness` | character | 136 | 3 | top: Expected \| Unexpected |
| 14 | `Relationship to the study intervention` | character | 135 | 6 | top: Potentially related \| Unlikely to be related \| Not Related |
| 15 | `Action taken` | character | 167 | 12 | top: Intervention: None (study drug continued) \| Intervention: Study drug stopped \| Intervention: Study drug continued, pressors given |
| 16 | `Date Reported to PHRC (Partners Human Research Committees), if applicable` | character | 1 | 2 | top: Yes, date unavailable |
| 17 | `Comments` | character | 184 | 53 | top: Study team ppt slides in Dropbox; Reported to D... \| Per BP (a-line) recording \| No study team ppt slides found in Dropbox; Not ... |
| 18 | `Notes (source of info)` | character | 2878 | 2 | top: Event pulled by code \| Event manually flagged |

## ICU-SLEEP_Delirium_Deidentified.csv

**Rows:** 7364  **Columns:** 189

| # | Column | Type | n non-NA | n unique | Summary |
|---|--------|------|----------|----------|---------|
| 1 | `ZID` | character | 7364 | 1 | top: [Redacted] |
| 2 | `SID` | character | 7364 | 526 | top: 12c \| 17 \| 151 |
| 3 | `SID Status` | character | 7364 | 4 | top: Retained (Final) \| Replaced \| Retained (Final); Repeat subject |
| 4 | `DateTime enrolled [Signed ICF completed]` | POSIXct | 526 | 470 | range 2015-07-18 12:00:00 .. 2025-06-26 12:00:00 (date-shifted) |
| 5 | `Date of first drug administration'` | POSIXct | 369 | 347 | range 2015-07-18 .. 2025-06-26 (date-shifted) |
| 6 | `Does 'Date enrolled' = 'Date of first drug administration'?` | character | 369 | 3 | top: Y \| N |
| 7 | `Delirium status on 'Date enrolled'` | character | 526 | 6 | top: 0 \| 1 \| 0? |
| 8 | `Delirium status on 'Date of first drug administration' ["Initial cognitive testing scores (before receiving the first study intervention): Confusion Assessment Method (CAM) / CAM-ICU / CAM-S"]` | character | 369 | 6 | top: 0 \| 1 \| 1? |
| 9 | `...9` | logical | 0 | 1 |  |
| 10 | `On-study day [From 'Date Enrolled']` | character | 7318 | 53 | top: 1 \| 2 \| 3 |
| 11 | `On-study day [From 'Date of first drug administration']` | character | 6524 | 44 | top: 1 \| 2 \| 3 |
| 12 | `On-study Date` | character | 7364 | 3042 | top: 2018-01-28T20:00:00 \| 2019-02-02T20:00:00 \| 2019-02-03T20:00:00 |
| 13 | `AM/Eval #1; PM/Eval #2` | character | 6796 | 3 | top: AM \| PM |
| 14 | `Location of study visit (Inpatient: ICU, floor; Post-discharge)` | character | 7364 | 7 | top: Inpatient: Floor \| Inpatient: ICU \| Post-discharge |
| 15 | `Location of study visit (specific)` | character | 6673 | 91 | top: Blake 12 (MICU/SICU); Adult Critical Care - Med... \| Ellison 4 (SICU); Adult Critical Care - Surgical \| Blake 7 (MICU); Adult Critical Care - Medical |
| 16 | `Evaluation / visit Date-Time` | character | 7364 | 7028 | top: 06/15/20 PM \| 03/31/20 PM \| 09/28/19 PM |
| 17 | `Eval/visit Date-Time within collection period?` | character | 4880 | 4 | top: Y \| N \| N? |
| 18 | `PVT performed?` | character | 875 | 3 | top: Y \| N |
| 19 | `Notes [e.g., If PVT not done, notes on reason: free text]` | character | 385 | 112 | top: Refused \| Missing (?) \| Unavailable |
| 20 | `One-time neuropsychological battery [parts include: CVLT-II, WAIS-IV Digit Span, TMT A&B] done at this timepoint / study visit? (e.g., alongside delirium evaluation)` | character | 7364 | 4 | top: N \| Y \| Y* |
| 21 | `CAM/CAM-ICU performed?` | character | 7364 | 12 | top: Yes \| No, Other \| No, Refused |
| 22 | `Notes 1 [If CAM not done, notes on reason: free text]` | character | 2614 | 497 | top: Unclear about doing eval post-floor day 7 (if s... \| No structured delirium evaluation required at t... \| Study drug dosing requirements not met (i.e., p... |
| 23 | `Notes 2 [Delirium Override Note: free-text]` | character | 665 | 570 | top: *Disregard (post-14d inpatient study phase) \| per RN, pt not delirious \| A&O x 3, Anxious but cooperative,  Not deliriou... |
| 24 | `Notes 3 (misc: free text)` | character | 3144 | 1256 | top: Review of medical record not performed / medica... \| AM: Patient consent \| AM: Consent by TBD [scanned copy of ICF not upl... |
| 25 | `1_Delirium status per CAM framework (0-1)` | character | 7364 | 4 | top: 0 \| UTA \| 1 |
| 26 | `2_Delirium status per CAM-ICU framework (0-1)` | character | 7364 | 4 | top: 0 \| UTA \| 1 |
| 27 | `3_Delirium impression based on nursing guidance and/or informal judgment.` | character | 881 | 4 | top: Not delirious \| Delirious \| Uncertain |
| 28 | `Overall delirium status at timepoint based on [CAM or CAM-ICU framework; Informal judgment ('delirium override field')]` | character | 7364 | 10 | top: CAM framework (0-1): Assessed per formal struct... \| None \| PI designation at time of consent (Pt. with cap... |
| 29 | `Unimputed_Overall delirium status at timepoint` | character | 5282 | 4 | top: 0 \| 1 \| UTA (Coma) |
| 30 | `Imputed_Overall delirium status at timepoint` | character | 6441 | 5 | top: 0 \| 1 \| UTA (Coma) |
| 31 | `Missing data rule applied` | character | 2162 | 9 | top: Not a missing evaluation (no structured deliriu... \| Evaluations post-discharge are marked as non-de... \| Code any missing evaluation between two negativ... |
| 32 | `...32` | logical | 0 | 1 |  |
| 33 | `Unimputed_'Delirum or coma free' day` | character | 3966 | 4 | top: 1 \| UTA \| 0 |
| 34 | `Imputed_'Delirium or coma free' day` | character | 3966 | 4 | top: 1 \| 0 \| UTA |
| 35 | `...35` | logical | 0 | 1 |  |
| 36 | `# ICU eval days (up to first 7 ICU days) [From 'Date of first drug administration']` | numeric | 369 | 8 | min=1, median=3, max=7 |
| 37 | `Unimputed_ICU Total 'Delirium or coma free' Days [From 'Date of first drug administration']_ICU Delirium-free days (ICU-DFDs) [Secondary outcome: aim 1B]` | numeric | 369 | 9 | min=0, median=2, max=7 |
| 38 | `Unimputed_ICU Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 39 | `Unimputed_ICU Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 8 | min=0, median=0, max=6 |
| 40 | `ICU Total 'Coma' Days [From 'Date of first drug administration']...40` | numeric | 369 | 5 | min=0, median=0, max=3 |
| 41 | `Unimputed_ICU Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 8 | min=0, median=0, max=6 |
| 42 | `Imputed_ICU Total 'Delirium or coma free' Days [From 'Date of first drug administration']_ICU Delirium-free days (ICU-DFDs) [Secondary outcome: aim 1B]` | numeric | 369 | 9 | min=0, median=2, max=7 |
| 43 | `Imputed_ICU Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 44 | `Imputed_ICU Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 8 | min=0, median=0, max=6 |
| 45 | `ICU Total 'Coma' Days [From 'Date of first drug administration']...45` | numeric | 369 | 5 | min=0, median=0, max=3 |
| 46 | `Imputed_ICU Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 8 | min=0, median=0, max=6 |
| 47 | `# hosp eval days (max of 14) [From 'Date of first drug administration']...47` | numeric | 369 | 14 | min=2, median=9, max=14 |
| 48 | `Unimputed_In-hosp Total 'Delirium or coma free' Days [From 'Date of first drug administration']_In-hospital Delirium-free days (IH-DFDs) [Primary outcome: aim 1A]` | numeric | 369 | 16 | min=0, median=6, max=14 |
| 49 | `Unimputed_In-hosp Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 14 | min=0, median=0, max=14 |
| 50 | `Unimputed_In-hosp Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 14 | min=0, median=0, max=13 |
| 51 | `In-hosp Total 'Coma' Days [From 'Date of first drug administration']...51` | numeric | 369 | 6 | min=0, median=0, max=8 |
| 52 | `Unimputed_In-hosp Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 15 | min=0, median=0, max=13 |
| 53 | `Imputed_In-hosp Total 'Delirium or coma free' Days [From 'Date of first drug administration']_In-hospital Delirium-free days (IH-DFDs) [Primary outcome: aim 1A]` | numeric | 369 | 16 | min=0, median=6, max=14 |
| 54 | `Imputed_In-hosp Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 16 | min=0, median=0, max=14 |
| 55 | `Imputed_In-hosp Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 16 | min=0, median=0, max=14 |
| 56 | `In-hosp Total 'Coma' Days [From 'Date of first drug administration']...56` | numeric | 369 | 6 | min=0, median=0, max=8 |
| 57 | `Imputed_In-hosp Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 15 | min=0, median=0, max=13 |
| 58 | `# hosp eval days (max of 14) [From 'Date of first drug administration']...58` | numeric | 369 | 14 | min=2, median=9, max=14 |
| 59 | `# extra days (post-discharge or death; if total # on-study days <14)` | numeric | 369 | 14 | min=0, median=5, max=12 |
| 60 | `Imputed_14-day window_Total 'Delirium or coma free' Days [From 'Date of first drug administration']` | numeric | 369 | 16 | min=0, median=13, max=14 |
| 61 | `Imputed_14-day window_Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 16 | min=0, median=0, max=14 |
| 62 | `Imputed_14-day window_Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 16 | min=0, median=0, max=14 |
| 63 | `In-hosp Total 'Coma' Days [From 'Date of first drug administration']...63` | numeric | 369 | 6 | min=0, median=0, max=8 |
| 64 | `Imputed_14-day window_Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 15 | min=0, median=0, max=13 |
| 65 | `# hosp eval days (up to first 7 days) [From 'Date of first drug administration']...65` | numeric | 369 | 7 | min=2, median=7, max=7 |
| 66 | `Unimputed_In-hosp 7d_Total 'Delirium or coma free' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=6, max=7 |
| 67 | `Unimputed_In-hosp 7d_Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 68 | `Unimputed_In-hosp 7d_Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 69 | `In-hosp 7d_Total 'Coma' Days [From 'Date of first drug administration']...69` | numeric | 369 | 6 | min=0, median=0, max=4 |
| 70 | `Unimputed_In-hosp 7d_Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 71 | `Imputed_In-hosp 7d_Total 'Delirium or coma free' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=6, max=7 |
| 72 | `Imputed_In-hosp 7d_Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 73 | `Imputed_In-hosp 7d_Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 74 | `In-hosp 7d_Total 'Coma' Days [From 'Date of first drug administration']...74` | numeric | 369 | 6 | min=0, median=0, max=4 |
| 75 | `Imputed_In-hosp 7d_Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 76 | `# hosp eval days (up to first 7 days) [From 'Date of first drug administration']...76` | numeric | 369 | 7 | min=2, median=7, max=7 |
| 77 | `# extra days (post-discharge or death; if total # on-study days <7)` | numeric | 369 | 7 | min=0, median=0, max=5 |
| 78 | `Imputed_7-day window_Total 'Delirium or coma free' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=7, max=7 |
| 79 | `Imputed_7-day window_Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 80 | `Imputed_7-day window_Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 81 | `In-hosp 7d_Total 'Coma' Days [From 'Date of first drug administration']...81` | numeric | 369 | 6 | min=0, median=0, max=4 |
| 82 | `Imputed_7-day window_Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 83 | `...83` | character | 5625 | 2 | top: _ |
| 84 | `RASS` | character | 4369 | 10 | top: 0 Alert n calm: Spontaneously pays attention to... \| -1 Drowsy: Not fully alert, but has sustained a... \| -2 Light sedation: Briefly awakens to voice (ey... |
| 85 | `[1] CAM-S: Acute Onset or Fluctuating Course (0-1)` | numeric | 4602 | 3 | min=0, median=0, max=1 |
| 86 | `Note [1]` | character | 742 | 4 | top: Scored per RN's judgement/notes \| Scored per visit notes \| Per family (daughter) |
| 87 | `[2] CAM-S: Inattention (0-2)` | numeric | 4310 | 4 | min=0, median=0, max=2 |
| 88 | `Note [2]` | character | 460 | 4 | top: Scored per RN's judgement/notes \| Scored per visit notes \| Scored based on NP eval (~1h later) |
| 89 | `[3] CAM-S: Disorganized Thinking (0-2)` | numeric | 4352 | 4 | min=0, median=0, max=2 |
| 90 | `Note [3]` | character | 509 | 3 | top: Scored per RN's judgement/notes \| Scored per visit notes |
| 91 | `[4] CAM-S: Altered Level of Consciousness (0-2)` | numeric | 4609 | 4 | min=0, median=0, max=2 |
| 92 | `Note [4]` | character | 726 | 3 | top: Scored per RN's judgement/notes \| Scored per visit notes |
| 93 | `[5] CAM-S: Disorientation (0-2)` | numeric | 4525 | 4 | min=0, median=0, max=2 |
| 94 | `Note [5]` | character | 711 | 4 | top: Scored per RN's judgement/notes \| Scored per visit notes \| Per family |
| 95 | `[6] CAM-S: Memory Impairment (0-2)` | numeric | 4133 | 4 | min=0, median=1, max=2 |
| 96 | `Note [6]` | character | 404 | 4 | top: Scored per RN's judgement/notes \| Scored per visit notes \| Scored based on NP eval (~1h later) |
| 97 | `[7] CAM-S: Perceptual Disturbances (0-2)` | numeric | 4272 | 4 | min=0, median=0, max=2 |
| 98 | `Note [7]` | character | 531 | 3 | top: Scored per RN's judgement/notes \| Scored per visit notes |
| 99 | `[8] CAM-S: Psychomotor Agitation (0-2)` | numeric | 4385 | 4 | min=0, median=0, max=2 |
| 100 | `Note [8]` | character | 509 | 3 | top: Scored per RN's judgement/notes \| Scored per visit notes |
| 101 | `[9] CAM-S: Psychomotor Retardation (0-2)` | numeric | 4388 | 4 | min=0, median=0, max=2 |
| 102 | `Note [9]` | character | 516 | 3 | top: Scored per RN's judgement/notes \| Scored per visit notes |
| 103 | `[10] CAM-S: Altered Sleep-Wake Cycle (0-2)` | numeric | 4466 | 4 | min=0, median=1, max=2 |
| 104 | `Note [10]` | character | 657 | 5 | top: Scored per RN's judgement/notes \| Scored per visit notes \| Per family |
| 105 | `# of CAM-S SF features scored (features 1-4)` | numeric | 7364 | 5 | min=0, median=4, max=4 |
| 106 | `# of CAM-S LF features scored (features 1-10)` | numeric | 7364 | 11 | min=0, median=10, max=10 |
| 107 | `CAM-S Short Form Total (0-7): Severity of delirium symptoms (features 1-4)` | numeric | 4541 | 9 | min=0, median=0, max=7 |
| 108 | `CAM-S SF Prorated Score (fractional)` | character | 4541 | 30 | top: 0/7 \| 0.14285714285714285 \| 0.2857142857142857 |
| 109 | `CAM-S Long Form Total (0-19): Severity of delirium symptoms (features 1-10)` | numeric | 4651 | 19 | min=0, median=2, max=17 |
| 110 | `CAM-S LF Prorated Score (fractional)` | character | 4651 | 137 | top: 5.2631578947368418E-2 \| 0.10526315789473684 \| 0/19 |
| 111 | `Delirium status per CAM framework (0-1)` | character | 7364 | 4 | top: 0 \| UTA \| 1 |
| 112 | `...112` | logical | 0 | 1 |  |
| 113 | `CAM-ICU: Acute onset & fluctuating course` | numeric | 4602 | 3 | min=0, median=0, max=1 |
| 114 | `CAM-ICU: Inattention (0-1)` | numeric | 3889 | 3 | min=0, median=0, max=1 |
| 115 | `CAM-ICU: Disorganized thinking (0-1)` | numeric | 3860 | 3 | min=0, median=0, max=1 |
| 116 | `CAM-ICU: Altered LOC (0-1)` | numeric | 4604 | 3 | min=0, median=0, max=1 |
| 117 | `Delirium status per CAM-ICU framework (0-1)` | character | 7364 | 4 | top: 0 \| UTA \| 1 |
| 118 | `...118` | logical | 0 | 1 |  |
| 119 | `Cognitive Eval (Raw data for CAM / CAM-ICU / CAM-S)` | logical | 0 | 1 |  |
| 120 | `Eval version` | character | 3993 | 5 | top: v.1 \| v.2 \| v.3 |
| 121 | `Pain: at rest (0-10)` | numeric | 3938 | 12 | min=0, median=1, max=10 |
| 122 | `Note [Pain: at rest]` | character | 328 | 231 | top: UTA \| per chart \| back pain |
| 123 | `Pain: with movement (0-10)` | numeric | 3891 | 12 | min=0, median=2, max=10 |
| 124 | `Note [Pain: with movement]` | character | 153 | 99 | top: UTA \| per chart \| 8-9 |
| 125 | `Pain: max in past 24h (0-10)` | numeric | 3923 | 12 | min=0, median=4, max=10 |
| 126 | `Note [Pain: max in past 24h]` | character | 235 | 161 | top: per chart \| UTA \| Per RN |
| 127 | `Sleep problems: Last night` | numeric | 4101 | 3 | min=0, median=1, max=1 |
| 128 | `Sleep problems: Trouble falling asleep` | numeric | 2013 | 3 | min=0, median=0, max=1 |
| 129 | `Sleep problems: Waking up and having trouble falling back to sleep; or waking up too early in the morning` | numeric | 2013 | 3 | min=0, median=0, max=1 |
| 130 | `Sleep problems: Having nightmares that were intense or bothersome` | numeric | 2013 | 3 | min=0, median=0, max=1 |
| 131 | `Sleep problems: Breathing problems or snoring` | numeric | 2013 | 3 | min=0, median=0, max=1 |
| 132 | `Sleep problems: Other` | numeric | 2013 | 3 | min=0, median=0, max=1 |
| 133 | `Note [Sleep problems]` | character | 1078 | 734 | top: no naps \| not good \| good |
| 134 | `Sleep problems: New or worse` | numeric | 4036 | 3 | min=0, median=0, max=1 |
| 135 | `Note [Sleep problems: New or worse]` | character | 103 | 92 | top: at home too \| in hospital \| disturbed sleep |
| 136 | `Sleep: NRS-Sleep Score` | numeric | 3683 | 12 | min=0, median=6, max=10 |
| 137 | `Note [NRS-Sleep Score]` | character | 484 | 363 | top: UTA \| No naps \| 5-6 |
| 138 | `Memory: Registration (3-words)` | character | 4966 | 6 | top: 0 \| -1 \| UTA |
| 139 | `Note [Memory: Registration]` | character | 1545 | 361 | top: Refused \| Not asked; "Pt. unavailable" \| Coma (RASS -4 or -5) |
| 140 | `Memory: Recall (2-min; 3-words)` | character | 4957 | 6 | top: 1 \| 0 \| -1 |
| 141 | `Memory: Recall (2-min; 3-words): # words recalled` | numeric | 3368 | 5 | min=0, median=2, max=3 |
| 142 | `Note [Memory: Recall (2-min; 3-words)]` | character | 1550 | 363 | top: Refused \| Not asked; "Pt. unavailable" \| Coma (RASS -4 or -5) |
| 143 | `Attention: DOW backwards` | character | 4960 | 6 | top: 0 \| -1 \| 1 |
| 144 | `Note [Attention: DOW backwards]` | character | 1450 | 349 | top: Refused \| Not asked; "Pt. unavailable" \| Coma (RASS -4 or -5) |
| 145 | `Attention: MOY backwards` | character | 4948 | 6 | top: 0 \| -1 \| 1 |
| 146 | `Note [Attention: MOY backwards]` | character | 1585 | 443 | top: Refused \| Not asked; "Pt. unavailable" \| Coma (RASS -4 or -5) |
| 147 | `Attention: Digit Span (3-digits forward)` | character | 4962 | 6 | top: 0 \| -1 \| UTA |
| 148 | `Note [Attention: Digit Span (3-digits forward)]` | character | 1570 | 318 | top: Refused \| Not asked; "Pt. unavailable" \| Eval of digit span observed during neuropsychol... |
| 149 | `Attention: Digit Span (4-digits forward)` | character | 4963 | 6 | top: 0 \| -1 \| UTA |
| 150 | `Note [Attention: Digit Span (4-digits forward)]` | character | 1607 | 345 | top: Refused \| Not asked; "Pt. unavailable" \| Eval of digit span observed during neuropsychol... |
| 151 | `Attention: Digit Span (5-digits forward)` | character | 4962 | 6 | top: 0 \| -1 \| 1 |
| 152 | `Note [Attention: Digit Span (5-digits forward)]` | character | 1706 | 404 | top: Refused \| Not asked; "Pt. unavailable" \| Eval of digit span observed during neuropsychol... |
| 153 | `Attention: Digit Span (3-digits backward)` | character | 4961 | 6 | top: 0 \| -1 \| 1 |
| 154 | `Note [Attention: Digit Span (3-digits backward)]` | character | 1722 | 379 | top: Refused \| Not asked; "Pt. unavailable" \| Eval of digit span observed during neuropsychol... |
| 155 | `Attention: Digit Span (4-digits backward)` | character | 4957 | 6 | top: 0 \| 1 \| -1 |
| 156 | `Note [Attention: Digit Span (4-digits backward)]` | character | 1965 | 512 | top: Refused \| Not asked; "Pt. unavailable" \| Eval of digit span observed during neuropsychol... |
| 157 | `Orientation (person): Full name` | character | 4360 | 6 | top: 0 \| -1 \| UTA |
| 158 | `Note [Orientation (person): Full name]` | character | 1761 | 206 | top: Refused \| Not asked [Q added to study eval form on ~ 03/0... \| Not asked; "Pt. unavailable" |
| 159 | `Orientation (time): Date` | character | 4968 | 6 | top: 0 \| -1 \| 1 |
| 160 | `Note [Orientation (time): Date]` | character | 1434 | 252 | top: Refused \| Not asked; "Pt. unavailable" \| Refused; info based on clinical team (e.g., RN)... |
| 161 | `Orientation (time): Month` | character | 4969 | 6 | top: 0 \| -1 \| UTA |
| 162 | `Note [Orientation (time): Month]` | character | 1325 | 221 | top: Refused \| Not asked; "Pt. unavailable" \| [Redacted] |
| 163 | `Orientation (time): Year` | character | 4968 | 6 | top: 0 \| -1 \| UTA |
| 164 | `Note [Orientation (time): Year]` | character | 1326 | 265 | top: Refused \| Not asked; "Pt. unavailable" \| Refused; info based on clinical team (e.g., RN)... |
| 165 | `Orientation (time): Season` | character | 4966 | 6 | top: 0 \| -1 \| UTA |
| 166 | `Note [Orientation (time): Season]` | character | 1273 | 211 | top: Refused \| Not asked; "Pt. unavailable" \| Refused; info based on clinical team (e.g., RN)... |
| 167 | `Orientation (place): City` | character | 4964 | 6 | top: 0 \| -1 \| UTA |
| 168 | `Note [Orientation (place): City]` | character | 1298 | 247 | top: Refused \| Not asked; "Pt. unavailable" \| Refused; info based on clinical team (e.g., RN)... |
| 169 | `Orientation (place): State` | character | 4963 | 6 | top: 0 \| -1 \| UTA |
| 170 | `Note [Orientation (place): State]` | character | 1274 | 223 | top: Refused \| Not asked; "Pt. unavailable" \| Refused; info based on clinical team (e.g., RN)... |
| 171 | `Orientation (place): Name of place` | character | 4966 | 6 | top: 0 \| -1 \| UTA |
| 172 | `Note [Orientation (place): Name of place]` | character | 1346 | 278 | top: Refused \| Not asked; "Pt. unavailable" \| Refused; info based on clinical team (e.g., RN)... |
| 173 | `Orientation (place): Floor of hospital` | character | 4953 | 6 | top: 0 \| -1 \| 1 |
| 174 | `Note [Orientation (place): Floor of hospital]` | character | 1345 | 253 | top: Refused \| Not asked; "Pt. unavailable" \| Coma (RASS -4 or -5) |
| 175 | `In past day, think that you were not really in hospital? [Acute onset/fluctuating course]` | character | 4959 | 6 | top: 0 \| -1 \| UTA |
| 176 | `Note [In past day, think that you were not really in hospital]` | character | 1346 | 275 | top: Refused \| Not asked; "Pt. unavailable" \| Coma (RASS -4 or -5) |
| 177 | `In past day, felt confused? [Acute onset/fluctuating course]` | character | 4967 | 6 | top: 0 \| -1 \| 1 |
| 178 | `Note [In past day, felt confused]` | character | 1448 | 381 | top: Refused \| Not asked; "Pt. unavailable" \| Coma (RASS -4 or -5) |
| 179 | `Perceptual disturbance: Visual hallucinations in past day? [Acute onset/fluctuating course]` | character | 4965 | 6 | top: 0 \| -1 \| UTA |
| 180 | `Note [Perceptual disturbance: Visual hallucinations in past day]` | character | 1381 | 318 | top: Refused \| Not asked; "Pt. unavailable" \| Coma (RASS -4 or -5) |
| 181 | `Perceptual disturbance: Auditory hallucinations in past day? [Acute onset/fluctuating course]` | character | 4965 | 6 | top: 0 \| -1 \| UTA |
| 182 | `Note [Perceptual disturbance: Auditory hallucinations in past day]` | character | 1316 | 245 | top: Refused \| Not asked; "Pt. unavailable" \| Coma (RASS -4 or -5) |
| 183 | `Perceptual disturbance (delusions): Think people were trying to harm you in past day? [Acute onset/fluctuating course]` | character | 4965 | 6 | top: 0 \| -1 \| UTA |
| 184 | `Note [Perceptual disturbance (delusions): Think people were trying to harm you in past day]` | character | 1307 | 237 | top: Refused \| Not asked; "Pt. unavailable" \| Coma (RASS -4 or -5) |
| 185 | `Perceptual disturbance: Misinterpretations / not what it seemed in past day? [Acute onset/fluctuating course]` | character | 4962 | 6 | top: 0 \| -1 \| UTA |
| 186 | `Note [Perceptual disturbance: Misinterpretations / not what it seemed in past day]` | character | 1319 | 249 | top: Refused \| Not asked; "Pt. unavailable" \| Coma (RASS -4 or -5) |
| 187 | `Perceptual disturbance: Think things were moving strangely in past day? [Acute onset/fluctuating course]` | character | 4962 | 6 | top: 0 \| -1 \| UTA |
| 188 | `Note [Perceptual disturbance: Think things were moving strangely in past day]` | character | 1309 | 241 | top: Refused \| Not asked; "Pt. unavailable" \| Coma (RASS -4 or -5) |
| 189 | `_` | logical | 0 | 1 |  |

## ICU-SLEEP_Enrolled_Deidentified.csv

**Rows:** 526  **Columns:** 308

| # | Column | Type | n non-NA | n unique | Summary |
|---|--------|------|----------|----------|---------|
| 1 | `ZID` | character | 526 | 1 | top: [Redacted] |
| 2 | `MRN` | character | 526 | 1 | top: [Redacted] |
| 3 | `SID` | character | 526 | 526 | top: 100 \| 101 \| 102 |
| 4 | `SID Status` | character | 526 | 4 | top: Retained (Final) \| Replaced \| Replaced; Repeat subject |
| 5 | `First Name` | character | 526 | 1 | top: [Redacted] |
| 6 | `Last Name` | character | 526 | 1 | top: [Redacted] |
| 7 | `BDSP ID` | numeric | 526 | 522 | min=1.112e+08, median=1.166e+08, max=1.224e+08 |
| 8 | `Date shift` | character | 526 | 1 | top: [Redacted] |
| 9 | `Analysis population: mITT` | character | 526 | 3 | top: Y \| N \| N, excluded |
| 10 | `Analysis population: PP` | character | 526 | 3 | top: N \| Y \| N, excluded |
| 11 | `Analysis population: Safety` | character | 526 | 2 | top: Y \| N |
| 12 | `Randomized` | character | 526 | 3 | top: Y \| N \| Y? |
| 13 | `Randomization allocation/assignment list` | character | 520 | 8 | top: Dex 0.3 mcg/kg/h \| Dex 0.1 mcg/kg/h \| Placebo |
| 14 | `Received study drug (any amount), y/n` | character | 526 | 2 | top: Y \| N |
| 15 | `Dosing structure: Initial (bolus + continuous); Final (continuous)` | character | 526 | 2 | top: Final (continuous) \| Initial (bolus + continuous) |
| 16 | `At least one efficacy measurement is obtained? Y/N` | character | 526 | 2 | top: Y \| N |
| 17 | `DateTime 'First study drug administration'` | POSIXct | 369 | 370 | range 2015-07-18 20:57:00 .. 2025-06-26 23:09:00 (date-shifted) |
| 18 | `DateTime 'Last study drug administration'` | POSIXct | 369 | 370 | range 2015-07-20 05:39:00 .. 2025-06-30 04:31:00 (date-shifted) |
| 19 | `Total # ICU nights where study drug (dex) was started; max of 7` | numeric | 526 | 8 | min=0, median=1, max=7 |
| 20 | `Total # ICU nights available to give study drug (dex); max of 7` | numeric | 526 | 8 | min=0, median=2, max=7 |
| 21 | `Start of AE collection period ['Date of enrollment (Consent; written)']` | POSIXct | 369 | 348 | range 2015-07-18 12:00:00 .. 2025-06-26 12:00:00 (date-shifted) |
| 22 | `End of AE collection period [DateTime 'Morning after last night of study drug administration']` | POSIXct | 369 | 349 | range 2015-07-20 10:00:00 .. 2025-06-30 10:00:00 (date-shifted) |
| 23 | `Withdrawn, y/n` | character | 526 | 3 | top: N \| Y \| Y* |
| 24 | `DateTime of withdrawal` | character | 209 | 206 | top: Withdrawn by study team post-inpatient study ph... \| 2018-01-29T11:59:59 \| 2015-11-28T10:59:59 |
| 25 | `Reason for withdrawal_notes 1` | character | 209 | 28 | top: Failed to maintain study eligibility: no longer... \| Failed to maintain study eligibility: met 1 exc... \| Failed to maintain study eligibility: met 1 exc... |
| 26 | `Reason for withdrawal_notes 2` | character | 204 | 5 | top: Study drug dosing requirements not met (i.e., p... \| Study drug dosing error (pharmacy/study team): ... \| Unblinded |
| 27 | `Were all eligibility requirements met at the time of enrollment? (i.e., met all inclusion criteria and none of the exclusion criteria) [Y/N]` | character | 526 | 2 | top: Y \| N |
| 28 | `If not all eligibility requirements were met at the time of enrollment, please explain.` | character | 9 | 9 | top: Inclusion criteria: 'Not on mechanical ventilat... \| Exclusion criteria: 'Dementia, as measured by a... \| Exclusion criteria: 'Dementia, as measured by a... |
| 29 | `Presence of any significant reported cardiac dysfunction (ejection fraction <30%) at baseline?` | character | 526 | 2 | top: N \| Y |
| 30 | `Extubation status at time of enrollment [Non-intubated; Intubated]` | character | 526 | 2 | top: Non-intubated \| Intubated, on mechanical ventilation |
| 31 | `Hosp_AdmissionDTS` | POSIXct | 526 | 526 | range 2015-07-17 06:04:00 .. 2025-06-18 19:14:00 (date-shifted) |
| 32 | `ICU_AdmissionDTS  [for ICU admission during which the pt. was enrolled]` | POSIXct | 526 | 526 | range 2015-07-17 15:00:00 .. 2025-06-18 19:14:00 (date-shifted) |
| 33 | `DateTime enrolled [Signed ICF completed]` | POSIXct | 526 | 469 | range 2015-07-18 12:00:00 .. 2025-06-26 12:00:00 (date-shifted) |
| 34 | `ICU_DischargeDTS [for ICU admission during which the pt. was enrolled]` | POSIXct | 526 | 526 | range 2015-07-20 13:48:00 .. 2025-06-30 12:26:00 (date-shifted) |
| 35 | `Hosp_DischargeDTS` | POSIXct | 526 | 526 | range 2015-07-27 10:21:00 .. 2025-07-10 12:33:00 (date-shifted) |
| 36 | `Days_in_icu_pre_enrollment [for ICU admission during which the pt. was enrolled]` | numeric | 526 | 491 | min=-0.1444, median=1.031, max=22.74 |
| 37 | `ICU_LOS [for ICU admission during which the pt. was enrolled]` | numeric | 526 | 513 | min=0.4472, median=3.735, max=37.97 |
| 38 | `Days_in_hosp_pre_enrollment` | numeric | 526 | 504 | min=-0.1271, median=2.123, max=80.57 |
| 39 | `Hosp_LOS` | numeric | 526 | 522 | min=1.485, median=10.66, max=114.6 |
| 40 | `Disposition/level of support at hosp discharge` | character | 526 | 13 | top: Home, with services \| Skilled Nursing Facility (SNF) \| Home, self-care |
| 41 | `Notes [Place of Discharge]` | character | 248 | 2 | top: [Redacted] |
| 42 | `Mortality in ICU [for ICU admission during which the pt. was enrolled]` | character | 526 | 3 | top: N \| Y \| N* |
| 43 | `Mortality in hospital` | character | 526 | 2 | top: N \| Y |
| 44 | `DateTime Death` | POSIXct | 135 | 135 | range 2015-07-30 02:34:00 .. 2025-09-08 12:00:00 (date-shifted) |
| 45 | `Days from "DateTime enrolled" to "DateTime Death"` | numeric | 135 | 121 | min=0.3778, median=64, max=364 |
| 46 | `Days from "DateTime First study drug administration" to "DateTime Death"` | numeric | 101 | 102 | min=0.7111, median=65.63, max=363.6 |
| 47 | `Mortality [within 14d from "DateTime enrolled"], y/n` | character | 526 | 2 | top: N \| Y |
| 48 | `Mortality [within 14d from "DateTime First study drug administration"], y/n` | character | 492 | 3 | top: N \| Y |
| 49 | `Mortality [within 12mo from "DateTime enrolled"], y/n` | character | 526 | 2 | top: N \| Y |
| 50 | `Re-admit within 30d from 'Date of hosp discharge': Y/N` | character | 494 | 4 | top: N \| Y \| N (ED visit only) |
| 51 | `Re-admit within 30d from 'Date of hosp discharge': Type` | character | 526 | 8 | top: None \| Inpatient (floor) \| N/A (deceased at discharge) |
| 52 | `Re-admit date` | character | 152 | 2 | top: [Date redacted] |
| 53 | `Re-admit reason` | character | 150 | 141 | top: Fever and chills \| Acute on chronic diastolic CHF (congestive hear... \| Anemia |
| 54 | `DOB` | logical | 0 | 1 |  |
| 55 | `Age (years) [at enrollment]` | numeric | 526 | 513 | min=22.42, median=68.09, max=89 |
| 56 | `Sex` | character | 526 | 2 | top: Male \| Female |
| 57 | `Race` | character | 526 | 6 | top: White \| Black or African American \| Asian |
| 58 | `Ethnicity (Hispanic or Latino)` | character | 526 | 3 | top: Not Hispanic or Latino/a/e/x \| Hispanic or Latino/a/e/x \| Unknown or not disclosed |
| 59 | `ICU Site [at enrollment]` | character | 526 | 3 | top: Blake 12 (MICU/SICU) \| Ellison 4 (SICU) \| Blake 7 (MICU) |
| 60 | `Primary Diagnosis for ICU Admission [during which the pt. was enrolled]` | character | 526 | 458 | top: Sepsis \| Pneumonia \| Liver transplant |
| 61 | `Primary Diagnosis for ICU Admission [during which the pt. was enrolled], Categorized` | character | 524 | 21 | top: Respiratory (failure) \| Cardiovascular \| Trauma |
| 62 | `Secondary Diagnosis (if applicable) for ICU Admission [during which the pt. was enrolled], Categorized` | character | 92 | 16 | top: Other surgery \| Cardiovascular \| Hematology/oncology |
| 63 | `Weight (kg)` | numeric | 526 | 357 | min=36.3, median=81.3, max=188.6 |
| 64 | `Notes [Med hx]` | character | 19 | 20 | top: Acc. to pt she is on traZODone (DESYREL)  for i... \| ADL are for before he broke his neck. \| Anxiety and Bipolar, disorder dates unknown |
| 65 | `Education (years)` | numeric | 336 | 20 | min=6, median=14, max=25 |
| 66 | `History of Depression, y/n` | character | 373 | 3 | top: N \| Y |
| 67 | `History of Depression_notes` | character | 93 | 63 | top: UNKNOWN \| [Redacted] \| UNKNOWN (According to the patient himself) |
| 68 | `Insomnia Disorder_y/n` | character | 375 | 3 | top: N \| Y |
| 69 | `Insomnia Disorder_notes` | character | 64 | 41 | top: UNKNOWN- according to the pt \| [Redacted] \| Trouble falling asleep |
| 70 | `Hypersomnolence Disorder, y/n` | character | 374 | 3 | top: N \| Y |
| 71 | `Hypersomnolence Disorder_notes` | character | 2 | 3 | top: acc to pt secondary to OSA \| Amy E Spooner, MD [Redacted] sleep disorder [Re... |
| 72 | `Central Sleep Apnea Syndrome, y/n` | character | 374 | 3 | top: N \| Y |
| 73 | `Central Sleep Apnea Syndrome_notes` | character | 3 | 4 | top: na \| per his records. Pt uses CPAP at home, date unk... \| UNKNOWN |
| 74 | `Obstructive Sleep Apnea, y/n` | character | 375 | 3 | top: N \| Y |
| 75 | `Obstructive Sleep Apnea_notes` | character | 59 | 42 | top: UNKNOWN \| [Redacted] \| CPAP |
| 76 | `Snoring, y/n` | character | 375 | 3 | top: N \| Y |
| 77 | `Snoring_notes` | character | 16 | 15 | top: according to the husband pt snores at night. \| UNKNOWN acc. to family \| + 30 years |
| 78 | `Upper Airway Resistance Syndrome (UARS), y/n` | character | 375 | 2 | top: N |
| 79 | `UARS_notes` | logical | 0 | 1 |  |
| 80 | `Parasomnias, y/n` | character | 375 | 2 | top: N |
| 81 | `Parasomnias_notes` | logical | 0 | 1 |  |
| 82 | `Narcolepsy, y/n` | character | 374 | 2 | top: N |
| 83 | `Narcolepsy_notes` | logical | 0 | 1 |  |
| 84 | `IADLs: A - Ability to use telephone` | numeric | 374 | 3 | min=0, median=1, max=1 |
| 85 | `IADLs: B - Shopping` | numeric | 373 | 3 | min=0, median=1, max=1 |
| 86 | `IADLs: C - Food preparation` | numeric | 373 | 3 | min=0, median=1, max=1 |
| 87 | `IADLs: D - Housekeeping` | numeric | 374 | 3 | min=0, median=1, max=1 |
| 88 | `IADLs: E - Laundry` | numeric | 374 | 3 | min=0, median=1, max=1 |
| 89 | `IADLs: F - Mode of transportation` | numeric | 373 | 3 | min=0, median=1, max=1 |
| 90 | `IADLs: G - Responsibility for medications` | numeric | 374 | 3 | min=0, median=1, max=1 |
| 91 | `IADLs: H - Ability to handle finance` | numeric | 372 | 3 | min=0, median=1, max=1 |
| 92 | `Lawton IADL Total Score (0-8)` | numeric | 374 | 10 | min=0, median=8, max=8 |
| 93 | `IQCODE-SF performed?` | character | 403 | 3 | top: Y \| N |
| 94 | `IQCODE-SF Performed Date` | character | 402 | 384 | top: 2021-08-03T20:00:00 \| 2016-10-16T20:00:00 \| 2017-05-18T20:00:00 |
| 95 | `Is "IQCODE-SF Performed Date" the same as "Date enrolled"? y/n` | character | 402 | 5 | top: Y \| N? \| N |
| 96 | `IQCODE-SF notes` | character | 28 | 8 | top: "IQCODE-SF Performed Date" before "Date enrolled" \| "IQCODE-SF Performed Date" after "Date enrolled... \| "IQCODE-SF Performed Date" after "Date enrolled... |
| 97 | `# days post "Date enrolled" (if "IQCODE-SF Performed Date" after "Date enrolled")` | character | 16 | 5 | top: 1? \| 3? \| 2? |
| 98 | `IQCODE-SF - Remembering things about family and friends, eg occupations, birthdays, addresses` | numeric | 402 | 4 | min=2, median=3, max=4 |
| 99 | `IQCODE-SF - Remembering things that have happened recently` | numeric | 402 | 3 | min=3, median=3, max=4 |
| 100 | `IQCODE-SF - Recalling conversations a few days later` | numeric | 402 | 3 | min=3, median=3, max=4 |
| 101 | `IQCODE-SF - Remembering her/his address and telephone number` | numeric | 402 | 4 | min=1, median=3, max=4 |
| 102 | `IQCODE-SF - Remembering what day and month it is` | numeric | 402 | 3 | min=3, median=3, max=4 |
| 103 | `IQCODE-SF - Remembering where things are usually kept` | numeric | 402 | 3 | min=3, median=3, max=4 |
| 104 | `IQCODE-SF - Remembering where to find things which have been put in a different place from usual` | numeric | 402 | 3 | min=3, median=3, max=4 |
| 105 | `IQCODE-SF - Knowing how to work familiar machines around the house` | numeric | 402 | 2 | min=3, median=3, max=3 |
| 106 | `IQCODE-SF - Learning to use a new gadget or machine around the house` | numeric | 402 | 4 | min=2, median=3, max=4 |
| 107 | `IQCODE-SF - Learning new things in general` | numeric | 402 | 4 | min=2, median=3, max=4 |
| 108 | `IQCODE-SF - Following a story in a book or on TV` | numeric | 402 | 3 | min=3, median=3, max=4 |
| 109 | `IQCODE-SF - Making decisions on everyday matters` | numeric | 402 | 3 | min=3, median=3, max=4 |
| 110 | `IQCODE-SF - Handling money for shopping` | numeric | 402 | 5 | min=1, median=3, max=4 |
| 111 | `IQCODE-SF - Handling financial matters, eg the pension, dealing with the bank` | numeric | 402 | 5 | min=1, median=3, max=5 |
| 112 | `IQCODE-SF - Handling other everyday arithmetic problems, eg knowing how much food to buy, knowing how long between visits from family or friends` | numeric | 402 | 4 | min=2, median=3, max=4 |
| 113 | `IQCODE-SF - Using his/her intelligence to understand what's going on and to reason things through` | numeric | 402 | 3 | min=3, median=3, max=4 |
| 114 | `Total IQCODE-SF score (16-80)` | numeric | 402 | 11 | min=46, median=48, max=56 |
| 115 | `Mean IQCODE-SF score (1-5)` | numeric | 402 | 11 | min=2.875, median=3, max=3.5 |
| 116 | `Delirium status on 'Date enrolled'` | character | 526 | 5 | top: 0 \| 1 \| 0? |
| 117 | `Delirium status on 'Date of first drug administration' ["Initial cognitive testing scores (before receiving the first study intervention): Confusion Assessment Method (CAM) / CAM-ICU / CAM-S"]` | character | 369 | 6 | top: 0 \| 1 \| 1? |
| 118 | `NRS-Sleep score for sleep quality on night before 'Date of first drug administration' ["Initial cognitive testing scores (before receiving the first study intervention): Numeric Rating Scale for Sleep (NRS-Sleep) score for sleep quality on the previous night"]` | numeric | 337 | 12 | min=0, median=5, max=10 |
| 119 | `# ICU eval days (up to first 7 ICU days) [From 'Date of first drug administration']` | numeric | 369 | 8 | min=1, median=3, max=7 |
| 120 | `Unimputed_ICU Total 'Delirium or coma free' Days [From 'Date of first drug administration']_ICU Delirium-free days (ICU-DFDs) [Secondary outcome: aim 1B]` | numeric | 369 | 9 | min=0, median=2, max=7 |
| 121 | `Unimputed_ICU Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 122 | `Unimputed_ICU Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 8 | min=0, median=0, max=6 |
| 123 | `ICU Total 'Coma' Days [From 'Date of first drug administration']...123` | numeric | 369 | 5 | min=0, median=0, max=3 |
| 124 | `Unimputed_ICU Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 8 | min=0, median=0, max=6 |
| 125 | `Imputed_ICU Total 'Delirium or coma free' Days [From 'Date of first drug administration']_ICU Delirium-free days (ICU-DFDs) [Secondary outcome: aim 1B]` | numeric | 369 | 9 | min=0, median=2, max=7 |
| 126 | `Imputed_ICU Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 127 | `Imputed_ICU Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 8 | min=0, median=0, max=6 |
| 128 | `ICU Total 'Coma' Days [From 'Date of first drug administration']...128` | numeric | 369 | 5 | min=0, median=0, max=3 |
| 129 | `Imputed_ICU Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 8 | min=0, median=0, max=6 |
| 130 | `# hosp eval days (max of 14) [From 'Date of first drug administration']...130` | numeric | 369 | 14 | min=2, median=9, max=14 |
| 131 | `Unimputed_In-hosp Total 'Delirium or coma free' Days [From 'Date of first drug administration']_In-hospital Delirium-free days (IH-DFDs) [Primary outcome: aim 1A]` | numeric | 369 | 16 | min=0, median=6, max=14 |
| 132 | `Unimputed_In-hosp Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 14 | min=0, median=0, max=14 |
| 133 | `Unimputed_In-hosp Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 14 | min=0, median=0, max=13 |
| 134 | `In-hosp Total 'Coma' Days [From 'Date of first drug administration']...134` | numeric | 369 | 6 | min=0, median=0, max=8 |
| 135 | `Unimputed_In-hosp Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 15 | min=0, median=0, max=13 |
| 136 | `Imputed_In-hosp Total 'Delirium or coma free' Days [From 'Date of first drug administration']_In-hospital Delirium-free days (IH-DFDs) [Primary outcome: aim 1A]` | numeric | 369 | 16 | min=0, median=6, max=14 |
| 137 | `Imputed_In-hosp Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 16 | min=0, median=0, max=14 |
| 138 | `Imputed_In-hosp Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 16 | min=0, median=0, max=14 |
| 139 | `In-hosp Total 'Coma' Days [From 'Date of first drug administration']...139` | numeric | 369 | 6 | min=0, median=0, max=8 |
| 140 | `Imputed_In-hosp Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 15 | min=0, median=0, max=13 |
| 141 | `# hosp eval days (max of 14) [From 'Date of first drug administration']...141` | numeric | 369 | 14 | min=2, median=9, max=14 |
| 142 | `# extra days (post-discharge or death; if total # on-study days <14)` | numeric | 369 | 14 | min=0, median=5, max=12 |
| 143 | `Imputed_14-day window_Total 'Delirium or coma free' Days [From 'Date of first drug administration']` | numeric | 369 | 16 | min=0, median=13, max=14 |
| 144 | `Imputed_14-day window_Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 16 | min=0, median=0, max=14 |
| 145 | `Imputed_14-day window_Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 16 | min=0, median=0, max=14 |
| 146 | `In-hosp Total 'Coma' Days [From 'Date of first drug administration']...146` | numeric | 369 | 6 | min=0, median=0, max=8 |
| 147 | `Imputed_14-day window_Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 15 | min=0, median=0, max=13 |
| 148 | `# hosp eval days (up to first 7 days) [From 'Date of first drug administration']...148` | numeric | 369 | 7 | min=2, median=7, max=7 |
| 149 | `Unimputed_In-hosp 7d_Total 'Delirium or coma free' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=6, max=7 |
| 150 | `Unimputed_In-hosp 7d_Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 151 | `Unimputed_In-hosp 7d_Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 152 | `In-hosp 7d_Total 'Coma' Days [From 'Date of first drug administration']...152` | numeric | 369 | 6 | min=0, median=0, max=4 |
| 153 | `Unimputed_In-hosp 7d_Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 154 | `Imputed_In-hosp 7d_Total 'Delirium or coma free' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=6, max=7 |
| 155 | `Imputed_In-hosp 7d_Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 156 | `Imputed_In-hosp 7d_Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 157 | `In-hosp 7d_Total 'Coma' Days [From 'Date of first drug administration']...157` | numeric | 369 | 6 | min=0, median=0, max=4 |
| 158 | `Imputed_In-hosp 7d_Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 159 | `# hosp eval days (up to first 7 days) [From 'Date of first drug administration']...159` | numeric | 369 | 7 | min=2, median=7, max=7 |
| 160 | `# extra days (post-discharge or death; if total # on-study days <7)` | numeric | 369 | 7 | min=0, median=0, max=5 |
| 161 | `Imputed_7-day window_Total 'Delirium or coma free' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=7, max=7 |
| 162 | `Imputed_7-day window_Total 'Delirium or coma' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 163 | `Imputed_7-day window_Total 'Delirium' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 164 | `In-hosp 7d_Total 'Coma' Days [From 'Date of first drug administration']...164` | numeric | 369 | 6 | min=0, median=0, max=4 |
| 165 | `Imputed_7-day window_Total 'UTA (unk delirium status)' Days [From 'Date of first drug administration']` | numeric | 369 | 9 | min=0, median=0, max=7 |
| 166 | `CCI_mi` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 167 | `CCI_chf` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 168 | `CCI_pvd` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 169 | `CCI_cevd` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 170 | `CCI_dementia` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 171 | `CCI_cpd` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 172 | `CCI_rheumd` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 173 | `CCI_pud` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 174 | `CCI_mld` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 175 | `CCI_diab` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 176 | `CCI_diabwc` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 177 | `CCI_hp` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 178 | `CCI_rend` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 179 | `CCI_canc` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 180 | `CCI_msld` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 181 | `CCI_metacanc` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 182 | `CCI_aids` | numeric | 526 | 2 | min=0, median=0, max=1 |
| 183 | `CCI_cci_score_unweighted` | numeric | 526 | 10 | min=0, median=2, max=9 |
| 184 | `CCI_cci_score_weighted` | numeric | 526 | 16 | min=0, median=2, max=16 |
| 185 | `med_prestudy_opioids` | numeric | 526 | 267 | min=0, median=0.03333, max=24.45 |
| 186 | `med_prestudy_benzos` | numeric | 526 | 27 | min=0, median=0, max=44.57 |
| 187 | `med_prestudy_phenobarbital` | numeric | 526 | 6 | min=0, median=0, max=974 |
| 188 | `med_prestudy_chlordiazepoxide` | numeric | 526 | 2 | min=0, median=0, max=100 |
| 189 | `med_prestudy_antipsychotics` | numeric | 526 | 1 | min=0, median=0, max=0 |
| 190 | `med_prestudy_propofol` | numeric | 526 | 108 | min=0, median=0, max=3.145e+04 |
| 191 | `med_prestudy_ketamine` | numeric | 526 | 19 | min=0, median=0, max=1666 |
| 192 | `med_prestudy_dexmedetomidine` | numeric | 526 | 61 | min=0, median=0, max=10.21 |
| 193 | `med_prestudy_melatonin` | numeric | 526 | 21 | min=0, median=0, max=140 |
| 194 | `med_duringstudy_opioids` | numeric | 526 | 324 | min=0, median=0.2076, max=64.99 |
| 195 | `med_duringstudy_benzos` | numeric | 526 | 42 | min=0, median=0, max=150.1 |
| 196 | `med_duringstudy_phenobarbital` | numeric | 526 | 8 | min=0, median=0, max=7.032e+04 |
| 197 | `med_duringstudy_chlordiazepoxide` | numeric | 526 | 1 | min=0, median=0, max=0 |
| 198 | `med_duringstudy_antipsychotics` | numeric | 526 | 1 | min=0, median=0, max=0 |
| 199 | `med_duringstudy_propofol` | numeric | 526 | 54 | min=0, median=0, max=4.644e+04 |
| 200 | `med_duringstudy_ketamine` | numeric | 526 | 14 | min=0, median=0, max=5584 |
| 201 | `med_duringstudy_dexmedetomidine` | numeric | 526 | 27 | min=0, median=0, max=7.609 |
| 202 | `med_duringstudy_melatonin` | numeric | 526 | 31 | min=0, median=0, max=70 |
| 203 | `Day_1_SOFA_score` | numeric | 526 | 15 | min=0, median=3, max=16 |
| 204 | `Day_1_Respiratory_SOFA` | numeric | 526 | 3 | min=0, median=0, max=4 |
| 205 | `Day_1_Coagulatory_SOFA` | numeric | 526 | 5 | min=0, median=0, max=4 |
| 206 | `Day_1_Liver_SOFA` | numeric | 526 | 4 | min=0, median=0, max=4 |
| 207 | `Day_1_CVS_SOFA` | numeric | 526 | 4 | min=0, median=0, max=4 |
| 208 | `Day_1_CNS_SOFA` | numeric | 526 | 5 | min=0, median=0, max=4 |
| 209 | `Day_1_Renal_SOFA` | numeric | 526 | 5 | min=0, median=0, max=4 |
| 210 | `Day_2_SOFA_score` | numeric | 522 | 16 | min=0, median=2, max=15 |
| 211 | `Day_2_Respiratory_SOFA` | numeric | 522 | 4 | min=0, median=0, max=4 |
| 212 | `Day_2_Coagulatory_SOFA` | numeric | 522 | 6 | min=0, median=0, max=4 |
| 213 | `Day_2_Liver_SOFA` | numeric | 522 | 5 | min=0, median=0, max=4 |
| 214 | `Day_2_CVS_SOFA` | numeric | 522 | 4 | min=0, median=0, max=4 |
| 215 | `Day_2_CNS_SOFA` | numeric | 522 | 6 | min=0, median=0, max=4 |
| 216 | `Day_2_Renal_SOFA` | numeric | 522 | 6 | min=0, median=0, max=4 |
| 217 | `Day_3_SOFA_score` | numeric | 503 | 17 | min=0, median=2, max=16 |
| 218 | `Day_3_Respiratory_SOFA` | numeric | 503 | 4 | min=0, median=0, max=4 |
| 219 | `Day_3_Coagulatory_SOFA` | numeric | 503 | 6 | min=0, median=0, max=4 |
| 220 | `Day_3_Liver_SOFA` | numeric | 503 | 6 | min=0, median=0, max=4 |
| 221 | `Day_3_CVS_SOFA` | numeric | 503 | 4 | min=0, median=0, max=4 |
| 222 | `Day_3_CNS_SOFA` | numeric | 503 | 6 | min=0, median=0, max=4 |
| 223 | `Day_3_Renal_SOFA` | numeric | 503 | 6 | min=0, median=0, max=4 |
| 224 | `Day_4_SOFA_score` | numeric | 474 | 16 | min=0, median=1, max=15 |
| 225 | `Day_4_Respiratory_SOFA` | numeric | 474 | 4 | min=0, median=0, max=4 |
| 226 | `Day_4_Coagulatory_SOFA` | numeric | 474 | 6 | min=0, median=0, max=4 |
| 227 | `Day_4_Liver_SOFA` | numeric | 474 | 6 | min=0, median=0, max=4 |
| 228 | `Day_4_CVS_SOFA` | numeric | 474 | 4 | min=0, median=0, max=4 |
| 229 | `Day_4_CNS_SOFA` | numeric | 474 | 6 | min=0, median=0, max=4 |
| 230 | `Day_4_Renal_SOFA` | numeric | 474 | 6 | min=0, median=0, max=4 |
| 231 | `Day_5_SOFA_score` | numeric | 421 | 16 | min=0, median=1, max=14 |
| 232 | `Day_5_Respiratory_SOFA` | numeric | 421 | 4 | min=0, median=0, max=4 |
| 233 | `Day_5_Coagulatory_SOFA` | numeric | 421 | 6 | min=0, median=0, max=4 |
| 234 | `Day_5_Liver_SOFA` | numeric | 421 | 6 | min=0, median=0, max=4 |
| 235 | `Day_5_CVS_SOFA` | numeric | 421 | 4 | min=0, median=0, max=4 |
| 236 | `Day_5_CNS_SOFA` | numeric | 421 | 6 | min=0, median=0, max=4 |
| 237 | `Day_5_Renal_SOFA` | numeric | 421 | 6 | min=0, median=0, max=4 |
| 238 | `Day_6_SOFA_score` | numeric | 376 | 17 | min=0, median=1, max=16 |
| 239 | `Day_6_Respiratory_SOFA` | numeric | 376 | 4 | min=0, median=0, max=4 |
| 240 | `Day_6_Coagulatory_SOFA` | numeric | 376 | 6 | min=0, median=0, max=4 |
| 241 | `Day_6_Liver_SOFA` | numeric | 376 | 5 | min=0, median=0, max=3 |
| 242 | `Day_6_CVS_SOFA` | numeric | 376 | 4 | min=0, median=0, max=4 |
| 243 | `Day_6_CNS_SOFA` | numeric | 376 | 6 | min=0, median=0, max=4 |
| 244 | `Day_6_Renal_SOFA` | numeric | 376 | 6 | min=0, median=0, max=4 |
| 245 | `Day_7_SOFA_score` | numeric | 339 | 15 | min=0, median=1, max=15 |
| 246 | `Day_7_Respiratory_SOFA` | numeric | 339 | 4 | min=0, median=0, max=4 |
| 247 | `Day_7_Coagulatory_SOFA` | numeric | 339 | 6 | min=0, median=0, max=4 |
| 248 | `Day_7_Liver_SOFA` | numeric | 339 | 5 | min=0, median=0, max=3 |
| 249 | `Day_7_CVS_SOFA` | numeric | 339 | 4 | min=0, median=0, max=4 |
| 250 | `Day_7_CNS_SOFA` | numeric | 339 | 6 | min=0, median=0, max=4 |
| 251 | `Day_7_Renal_SOFA` | numeric | 339 | 6 | min=0, median=0, max=4 |
| 252 | `Day_8_SOFA_score` | numeric | 305 | 16 | min=0, median=1, max=14 |
| 253 | `Day_8_Respiratory_SOFA` | numeric | 305 | 4 | min=0, median=0, max=4 |
| 254 | `Day_8_Coagulatory_SOFA` | numeric | 305 | 6 | min=0, median=0, max=4 |
| 255 | `Day_8_Liver_SOFA` | numeric | 305 | 6 | min=0, median=0, max=4 |
| 256 | `Day_8_CVS_SOFA` | numeric | 305 | 4 | min=0, median=0, max=4 |
| 257 | `Day_8_CNS_SOFA` | numeric | 305 | 6 | min=0, median=0, max=4 |
| 258 | `Day_8_Renal_SOFA` | numeric | 305 | 6 | min=0, median=0, max=4 |
| 259 | `Day_9_SOFA_score` | numeric | 260 | 16 | min=0, median=1, max=14 |
| 260 | `Day_9_Respiratory_SOFA` | numeric | 260 | 4 | min=0, median=0, max=4 |
| 261 | `Day_9_Coagulatory_SOFA` | numeric | 260 | 6 | min=0, median=0, max=4 |
| 262 | `Day_9_Liver_SOFA` | numeric | 260 | 6 | min=0, median=0, max=4 |
| 263 | `Day_9_CVS_SOFA` | numeric | 260 | 4 | min=0, median=0, max=4 |
| 264 | `Day_9_CNS_SOFA` | numeric | 260 | 6 | min=0, median=0, max=4 |
| 265 | `Day_9_Renal_SOFA` | numeric | 260 | 6 | min=0, median=0, max=4 |
| 266 | `Day_10_SOFA_score` | numeric | 230 | 14 | min=0, median=1, max=15 |
| 267 | `Day_10_Respiratory_SOFA` | numeric | 230 | 4 | min=0, median=0, max=4 |
| 268 | `Day_10_Coagulatory_SOFA` | numeric | 230 | 6 | min=0, median=0, max=4 |
| 269 | `Day_10_Liver_SOFA` | numeric | 230 | 6 | min=0, median=0, max=4 |
| 270 | `Day_10_CVS_SOFA` | numeric | 230 | 4 | min=0, median=0, max=4 |
| 271 | `Day_10_CNS_SOFA` | numeric | 230 | 6 | min=0, median=0, max=4 |
| 272 | `Day_10_Renal_SOFA` | numeric | 230 | 6 | min=0, median=0, max=4 |
| 273 | `Day_11_SOFA_score` | numeric | 205 | 16 | min=0, median=1, max=16 |
| 274 | `Day_11_Respiratory_SOFA` | numeric | 205 | 4 | min=0, median=0, max=4 |
| 275 | `Day_11_Coagulatory_SOFA` | numeric | 205 | 6 | min=0, median=0, max=4 |
| 276 | `Day_11_Liver_SOFA` | numeric | 205 | 6 | min=0, median=0, max=4 |
| 277 | `Day_11_CVS_SOFA` | numeric | 205 | 4 | min=0, median=0, max=4 |
| 278 | `Day_11_CNS_SOFA` | numeric | 205 | 6 | min=0, median=0, max=4 |
| 279 | `Day_11_Renal_SOFA` | numeric | 205 | 6 | min=0, median=0, max=4 |
| 280 | `Day_12_SOFA_score` | numeric | 182 | 16 | min=0, median=1, max=15 |
| 281 | `Day_12_Respiratory_SOFA` | numeric | 182 | 4 | min=0, median=0, max=4 |
| 282 | `Day_12_Coagulatory_SOFA` | numeric | 182 | 6 | min=0, median=0, max=4 |
| 283 | `Day_12_Liver_SOFA` | numeric | 182 | 6 | min=0, median=0, max=4 |
| 284 | `Day_12_CVS_SOFA` | numeric | 182 | 4 | min=0, median=0, max=4 |
| 285 | `Day_12_CNS_SOFA` | numeric | 182 | 6 | min=0, median=0, max=4 |
| 286 | `Day_12_Renal_SOFA` | numeric | 182 | 6 | min=0, median=0, max=4 |
| 287 | `Day_13_SOFA_score` | numeric | 169 | 14 | min=0, median=1, max=15 |
| 288 | `Day_13_Respiratory_SOFA` | numeric | 169 | 4 | min=0, median=0, max=4 |
| 289 | `Day_13_Coagulatory_SOFA` | numeric | 169 | 6 | min=0, median=0, max=4 |
| 290 | `Day_13_Liver_SOFA` | numeric | 169 | 6 | min=0, median=0, max=4 |
| 291 | `Day_13_CVS_SOFA` | numeric | 169 | 4 | min=0, median=0, max=4 |
| 292 | `Day_13_CNS_SOFA` | numeric | 169 | 6 | min=0, median=0, max=4 |
| 293 | `Day_13_Renal_SOFA` | numeric | 169 | 6 | min=0, median=0, max=4 |
| 294 | `Day_14_SOFA_score` | numeric | 147 | 15 | min=0, median=1, max=15 |
| 295 | `Day_14_Respiratory_SOFA` | numeric | 147 | 3 | min=0, median=0, max=4 |
| 296 | `Day_14_Coagulatory_SOFA` | numeric | 147 | 6 | min=0, median=0, max=4 |
| 297 | `Day_14_Liver_SOFA` | numeric | 147 | 6 | min=0, median=0, max=4 |
| 298 | `Day_14_CVS_SOFA` | numeric | 147 | 4 | min=0, median=0, max=4 |
| 299 | `Day_14_CNS_SOFA` | numeric | 147 | 5 | min=0, median=0, max=3 |
| 300 | `Day_14_Renal_SOFA` | numeric | 147 | 6 | min=0, median=0, max=4 |
| 301 | `Day_15_SOFA_score` | numeric | 3 | 4 | min=0, median=1, max=3 |
| 302 | `Day_15_Respiratory_SOFA` | numeric | 3 | 2 | min=0, median=0, max=0 |
| 303 | `Day_15_Coagulatory_SOFA` | numeric | 3 | 3 | min=0, median=0, max=3 |
| 304 | `Day_15_Liver_SOFA` | numeric | 3 | 2 | min=0, median=0, max=0 |
| 305 | `Day_15_CVS_SOFA` | numeric | 3 | 2 | min=0, median=0, max=0 |
| 306 | `Day_15_CNS_SOFA` | numeric | 3 | 2 | min=0, median=0, max=0 |
| 307 | `Day_15_Renal_SOFA` | numeric | 3 | 3 | min=0, median=0, max=1 |
| 308 | `_` | logical | 0 | 1 |  |

## ICU-SLEEP_Study_Drug_Deidentified.csv

**Rows:** 1421  **Columns:** 50

| # | Column | Type | n non-NA | n unique | Summary |
|---|--------|------|----------|----------|---------|
| 1 | `ZID` | character | 1421 | 1 | top: [Redacted] |
| 2 | `SID...2` | character | 1421 | 526 | top: 192b \| 102 \| 123 |
| 3 | `SID Status` | character | 1421 | 4 | top: Retained (Final) \| Replaced \| Replaced; Repeat subject |
| 4 | `On-study day [From 'Date Enrolled']` | numeric | 1421 | 8 | min=1, median=2, max=8 |
| 5 | `On-study day [From 'Date of first drug adminstration']` | numeric | 1049 | 8 | min=1, median=2, max=7 |
| 6 | `On-study Date [Night for drug to start: 20:00]` | POSIXct | 1421 | 1107 | range 2015-07-18 .. 2025-06-29 (date-shifted) |
| 7 | `Was study drug given (any amount)?` | character | 1421 | 2 | top: Y \| N |
| 8 | `Was study drug started & then stopped d/t any safety concern? [real; or perceived]` | character | 1421 | 3 | top: N \| Y \| Y? |
| 9 | `Was study drug held for a safety reason?` | character | 1421 | 3 | top: N \| Y \| Y? |
| 10 | `Note (Incomplete drug dosing)` | character | 792 | 452 | top: Study drug held d/t ... (?) \| Patient/family refused \| Not randomized |
| 11 | `Note (misc)` | character | 507 | 288 | top: Did not receive at least 1 night with ≥5.5hrs \| Study drug completed earlier than intended (inc... \| Did not receive at least 1 night with ≥5.5hrs (... |
| 12 | `Dosing info (continuous infusion)` | character | 753 | 301 | top: 66 mL: 6 mL/hr (Intravenous) over 11h [0.825 mL... \| 66 mL: 6 mL/hr (Intravenous) over 11h [0.825 mL... \| 66 mL: 6 mL/hr (Intravenous) over 11h [0.825 mL... |
| 13 | `Drug Start Time 1 (continuous infusion)` | POSIXct | 753 | 754 | range 2015-07-18 20:57:00 .. 2025-06-29 20:02:00 (date-shifted) |
| 14 | `Confidence of Start Time 1 (continuous infusion)` | character | 753 | 3 | top: High \| Low |
| 15 | `Drug End Time 1 (continuous infusion)` | POSIXct | 753 | 753 | range 2015-07-19 06:34:00 .. 2025-06-30 04:31:00 (date-shifted) |
| 16 | `Confidence of End Time 1 (continuous infusion)` | character | 753 | 3 | top: Low \| High |
| 17 | `Duration (hh:mm) of drug (continuous infusion): 1st admin` | POSIXct | 1421 | 958 | range 1896-12-31 .. 1902-12-29 10:52:00 (date-shifted) |
| 18 | `Was drug stopped & then re-started? (continuous infusion)` | character | 751 | 3 | top: N \| Y |
| 19 | `Drug Start Time 2 (continuous infusion)` | POSIXct | 10 | 11 | range 2017-03-13 21:30:00 .. 2022-10-02 00:30:00 (date-shifted) |
| 20 | `Confidence of Start Time 2 (continuous infusion)` | character | 10 | 3 | top: High \| Low |
| 21 | `Drug End Time 2 (continuous infusion)` | POSIXct | 10 | 11 | range 2017-03-14 06:10:00 .. 2022-10-02 06:54:00 (date-shifted) |
| 22 | `Confidence of End Time 2 (continuous infusion)` | character | 10 | 3 | top: High \| Low |
| 23 | `Duration (hh:mm) of drug (continuous infusion): 2nd admin (if applicable)` | POSIXct | 1421 | 466 | range 1896-12-31 .. 1902-12-29 (date-shifted) |
| 24 | `Duration (hh:mm) of drug (continuous infusion): All admin` | POSIXct | 1421 | 957 | range 1896-12-31 .. 1902-12-29 10:52:00 (date-shifted) |
| 25 | `Bolus infusion` | character | 47 | 2 | top: Y |
| 26 | `Dosing info (bolus infusion)` | character | 47 | 19 | top: 80 mcg: 13.3 mL/hr (Intravenous) over 90-min \| 68.9 mcg: 23 mL/hr (Intravenous) over 45-min [1... \| 71.7 mcg: 12 mL/hr (Intravenous) over 90-min [1... |
| 27 | `Drug Start Time (bolus)` | POSIXct | 47 | 48 | range 2015-07-28 20:10:00 .. 2022-01-19 21:03:00 (date-shifted) |
| 28 | `Confidence of Start Time (bolus)` | character | 47 | 2 | top: High |
| 29 | `Drug End Time (bolus)` | POSIXct | 47 | 48 | range 2015-07-28 21:40:00 .. 2022-01-19 22:30:00 (date-shifted) |
| 30 | `Confidence of End Time (bolus)` | character | 47 | 2 | top: Low |
| 31 | `Total # ICU nights where study drug (dex) was started; max of 7` | numeric | 526 | 9 | min=0, median=1, max=7 |
| 32 | `Total # ICU nights available to give study drug (dex); max of 7` | numeric | 526 | 9 | min=0, median=2, max=7 |
| 33 | `DateTime 'Last study drug administration'` | POSIXct | 369 | 370 | range 2015-07-20 05:39:00 .. 2025-06-30 04:31:00 (date-shifted) |
| 34 | `End of AE collection period [DateTime 'Morning after last night of study drug administration']` | POSIXct | 369 | 349 | range 2015-07-20 10:00:00 .. 2025-06-30 10:00:00 (date-shifted) |
| 35 | `_` | logical | 0 | 1 |  |
| 36 | `SID...36` | character | 1421 | 526 | top: 192b \| 102 \| 123 |
| 37 | `Drug_start_time (overall)` | POSIXct | 757 | 756 | range 2015-07-18 20:57:00 .. 2025-06-29 20:02:00 (date-shifted) |
| 38 | `Drug_stop_time (overall)` | POSIXct | 757 | 757 | range 2015-07-19 06:34:00 .. 2025-06-30 04:31:00 (date-shifted) |
| 39 | `hr_low_rel_ae` | numeric | 757 | 5 | min=0, median=0, max=4 |
| 40 | `hr_low_abs_ae` | numeric | 757 | 16 | min=0, median=0, max=22 |
| 41 | `hr_low_abs_sae` | numeric | 757 | 3 | min=0, median=0, max=1 |
| 42 | `hr_high_rel_ae` | numeric | 757 | 2 | min=0, median=0, max=0 |
| 43 | `hr_high_abs_ae` | numeric | 757 | 24 | min=0, median=0, max=61 |
| 44 | `bp_low_rel_ae` | numeric | 757 | 2 | min=0, median=0, max=0 |
| 45 | `bp_low_abs_ae` | numeric | 757 | 23 | min=0, median=0, max=35 |
| 46 | `bp_low_abs_sae` | numeric | 757 | 9 | min=0, median=0, max=8 |
| 47 | `bp_high_rel_ae` | numeric | 757 | 2 | min=0, median=0, max=0 |
| 48 | `bp_high_abs_ae` | numeric | 757 | 12 | min=0, median=0, max=11 |
| 49 | `other_ae` | numeric | 757 | 2 | min=0, median=0, max=0 |
| 50 | `other_sae` | numeric | 757 | 3 | min=0, median=0, max=1 |

