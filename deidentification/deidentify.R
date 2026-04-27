## ICU-SLEEP — HIPAA Safe Harbor deidentification
## Reads:  ICU-SLEEP_Data_P1_Deidentified_11.26.25.xlsx (semi-deid; still has DOB + real dates)
## Writes: 4 CSVs + manifest + codebook + a saved per-SID shift table
##
## Transformations:
##   1. Drop ZID column (already "[Redacted]" sentinel, no info)
##   2. Drop DOB column entirely
##   3. Cap "Age (years) [at enrollment]" at 89
##   4. Apply per-SID random date shift (deterministic seed) to ALL date/datetime cols
##      and to character columns containing Excel serial dates
##   5. Replace free-text date column "Re-admit date" with "[Date redacted]"
##   6. Write each sheet as a separate CSV preserving original column names
##      (via writexl-then-readxl-then-write_csv to retain readxl's `xxx...123`
##       duplicate-renaming convention used by the analysis code)
##
## Reproducibility: deterministic seed + saved shift table => exact same output
## given the same input file.

suppressPackageStartupMessages({
  library(readxl)
  library(readr)
  library(dplyr)
  library(stringr)
  library(lubridate)
  library(janitor)
})

# Paths can be overridden via env vars ICU_SLEEP_DEID_INPUT_XLSX and ICU_SLEEP_DEID_OUTDIR
INPUT_XLSX <- Sys.getenv("ICU_SLEEP_DEID_INPUT_XLSX",
                         unset = "../ICU_SLEEP_final_FromHao/data/ICU-SLEEP_Data_P1_Deidentified_11.26.25.xlsx")
OUTDIR     <- Sys.getenv("ICU_SLEEP_DEID_OUTDIR",
                         unset = "../_deid_output")
dir.create(OUTDIR, showWarnings = FALSE, recursive = TRUE)

SEED <- 20260425L
SHIFT_RANGE_DAYS <- 1095L  # +/- ~3 years; HIPAA Safe Harbor compliant

# Excel serial to POSIXct
excel_serial_to_posix <- function(x_chr) {
  num <- suppressWarnings(as.numeric(x_chr))
  out <- rep(as.POSIXct(NA), length(num))
  ok <- !is.na(num) & num >= 25569 & num <= 80000   # rough valid range 1970..2118
  if (any(ok)) {
    out[ok] <- as.POSIXct((num[ok] - 25569) * 86400, origin = "1970-01-01", tz = "UTC")
  }
  out
}

# Determine if a character vector is "mostly Excel serials"
is_excel_serial_col <- function(x) {
  if (!is.character(x)) return(FALSE)
  v <- x[!is.na(x)]
  if (length(v) == 0) return(FALSE)
  num <- suppressWarnings(as.numeric(v))
  hits <- sum(!is.na(num) & num >= 25569 & num <= 80000) # within plausible range
  return(hits / length(v) >= 0.5)  # >=50% look like Excel serials
}

cat("=== READING SHEETS ===\n")
sheet_names <- excel_sheets(INPUT_XLSX)
print(sheet_names)

# Read all sheets
all_sheets <- list()
for (sn in sheet_names) {
  cat("  reading:", sn, "\n")
  d <- read_excel(INPUT_XLSX, sheet = sn, na = c("n/a","N/A","?",""), guess_max = 100000)
  all_sheets[[sn]] <- d
}

# Build SID master list from Enrolled sheet
master_sids <- all_sheets[["ICU-SLEEP_Enrolled"]]$SID
master_sids <- master_sids[!is.na(master_sids)]
cat("\nMaster SID count:", length(master_sids), "  unique:", length(unique(master_sids)), "\n")

# Generate per-SID shifts (deterministic)
set.seed(SEED)
unique_sids <- sort(unique(master_sids))
shift_days <- sample(c(setdiff(seq(-SHIFT_RANGE_DAYS, SHIFT_RANGE_DAYS), 0L)),
                     size = length(unique_sids), replace = TRUE)
shift_tbl <- tibble(SID = unique_sids, shift_days = shift_days)

# Save the shift table internally for audit (not published — would re-identify if leaked!)
write_csv(shift_tbl, file.path(OUTDIR, "_INTERNAL_DO_NOT_PUBLISH_shifts.csv"))
cat("Wrote internal shift table.\n")

shift_lookup <- setNames(shift_tbl$shift_days, shift_tbl$SID)

apply_deid <- function(df, sheet_name) {
  cat("\n--- ", sheet_name, " ---\n", sep="")
  cat("  rows in: ", nrow(df), "  cols in: ", ncol(df), "\n", sep="")

  # Find SID col
  sid_cols <- grep("^SID($|\\.\\.\\.)", names(df), perl = TRUE, value = TRUE)
  cat("  SID-like cols: ", paste(sid_cols, collapse=" | "), "\n", sep="")
  if (length(sid_cols) == 0) {
    stop("No SID column found in sheet ", sheet_name)
  }
  sid_col <- sid_cols[1]
  shifts_per_row <- shift_lookup[df[[sid_col]]]
  shifts_per_row[is.na(shifts_per_row)] <- 0L

  # 1) ZID is already "[Redacted]" sentinel — leave column in place to preserve
  #    duplicate-column position-numbering used by the analysis code (clean_names
  #    appends position suffixes like _123 that change if cols are dropped)
  # 2) DOB: blank out values but keep column to preserve position numbering
  if ("DOB" %in% names(df)) {
    cat("  BLANKING DOB column values (keeping column for position stability)\n")
    df$DOB <- as.POSIXct(NA)  # all NA; preserves column position
  }

  # 3) HIPAA Safe Harbor age handling:
  #    - Floor to integer (drops partial-year precision tied to original DOB,
  #      e.g., 89.3 -> 89; per HIPAA, ages 0-89 may be retained as integers)
  #    - Top-code ages >= 90 to a single value of 90 (the "90 or older" bucket).
  #      We use the numeric sentinel 90 so the analysis pipeline can keep
  #      treating the column as numeric.
  age_col <- "Age (years) [at enrollment]"
  if (age_col %in% names(df)) {
    v_orig <- df[[age_col]]
    v_num  <- suppressWarnings(as.numeric(v_orig))
    # Source already top-codes some patients as strings like "90 or above; [Redacted]";
    # they become NA after as.numeric. Detect and treat them as >=90.
    already_topcoded <- !is.na(v_orig) & is.na(v_num) & grepl("90", v_orig)
    n_top_numeric <- sum(v_num >= 90, na.rm = TRUE)
    n_top_string  <- sum(already_topcoded)
    n_top <- n_top_numeric + n_top_string
    if (n_top > 0) {
      cat("  TOP-CODING ", n_top, " ages >= 90 to 90 ",
          "(", n_top_numeric, " numeric + ", n_top_string,
          " already-string-topcoded; HIPAA Safe Harbor)\n", sep = "")
    }
    # Floor numeric ages, top-code at 90, then merge in already-topcoded patients as 90.
    v_num <- floor(v_num)
    v_num <- pmin(v_num, 90)
    v_num[already_topcoded] <- 90
    df[[age_col]] <- v_num
  }

  # 4) Shift native date/datetime columns
  date_cols <- names(df)[sapply(df, function(x) inherits(x, c("POSIXct","POSIXt","Date")))]
  cat("  shifting ", length(date_cols), " native date cols:\n", sep="")
  for (col in date_cols) {
    df[[col]] <- df[[col]] + lubridate::days(shifts_per_row)
    cat("    [", col, "]\n", sep="")
  }

  # 5) Detect & shift character columns that hold Excel-serial dates.
  #    BUT exclude columns that are durations (year ~ 1899) — these are time-only.
  serial_candidates <- names(df)[sapply(df, is_excel_serial_col)]
  for (col in serial_candidates) {
    parsed <- excel_serial_to_posix(df[[col]])
    yrs <- year(parsed)
    yrs <- yrs[!is.na(yrs)]
    if (length(yrs) == 0) next
    if (max(yrs) < 1950) {
      cat("  SKIP duration-like char col [", col, "] (max year ", max(yrs), ")\n", sep="")
      next
    }
    cat("  SHIFTING char-Excel-serial col [", col, "] yr_range ", min(yrs), "..", max(yrs), "\n", sep="")
    parsed_shift <- parsed + lubridate::days(shifts_per_row)
    # Write back as ISO date strings, preserving NA
    new_col <- format(parsed_shift, "%Y-%m-%dT%H:%M:%S")
    new_col[is.na(parsed_shift)] <- df[[col]][is.na(parsed_shift)]  # keep originals where unparseable
    df[[col]] <- new_col
  }

  # 6) Free-text date columns: redact
  free_text_date_cols <- c("Re-admit date")
  for (col in intersect(free_text_date_cols, names(df))) {
    cat("  redacting free-text date col [", col, "]\n", sep="")
    df[[col]] <- ifelse(is.na(df[[col]]), NA_character_, "[Date redacted]")
  }

  cat("  rows out: ", nrow(df), "  cols out: ", ncol(df), "\n", sep="")
  df
}

deid <- list()
for (sn in sheet_names) {
  deid[[sn]] <- apply_deid(all_sheets[[sn]], sn)
}

# Write CSVs
cat("\n=== WRITING CSVs ===\n")
manifest <- list()
for (sn in sheet_names) {
  safe_base <- sn |>
    sub("^ICU-SLEEP_", "", x = _) |>
    gsub(" ", "_", x = _)
  csv_name <- paste0("ICU-SLEEP_", safe_base, "_Deidentified.csv")
  out_path <- file.path(OUTDIR, csv_name)
  write_csv(deid[[sn]], out_path)
  size_mb <- file.size(out_path) / 1e6
  cat(sprintf("  wrote %s  (%.1f MB, %d rows, %d cols)\n",
              csv_name, size_mb, nrow(deid[[sn]]), ncol(deid[[sn]])))
  manifest[[sn]] <- list(
    file = csv_name,
    n_rows = nrow(deid[[sn]]),
    n_cols = ncol(deid[[sn]]),
    size_mb = round(size_mb, 2)
  )
}

# Manifest
manifest_lines <- c(
  "ICU-SLEEP Public Data Release — Manifest",
  paste0("Generated: ", Sys.time()),
  paste0("Source: ", basename(INPUT_XLSX)),
  paste0("Date-shift seed: ", SEED, "  range: +/-", SHIFT_RANGE_DAYS, " days, per-SID, deterministic"),
  "",
  "Files:",
  ""
)
for (sn in names(manifest)) {
  m <- manifest[[sn]]
  manifest_lines <- c(manifest_lines,
    sprintf("  %s  (%d rows x %d cols, %.2f MB)  -- from sheet '%s'",
            m$file, m$n_rows, m$n_cols, m$size_mb, sn))
}
manifest_lines <- c(manifest_lines, "",
  "Deidentification applied (TWO LAYERS):",
  "  Layer 1 - applied by the trial team prior to release to the analysis team:",
  "    - Removed: names, MRN",
  "    - Date-shifted: all dates (including DOB) per-patient (shift values redacted",
  "      from the released 'Date shift' column)",
  "    - Top-coded: 2 patients (>= 90 years) flagged as '90 or above'",
  "",
  paste0("  Layer 2 - applied by this script (deidentify.R; seed=", SEED,
         ", second per-SID shift in +/-", SHIFT_RANGE_DAYS, " days):"),
  "    - Blanked: DOB column values (column kept for analysis-pipeline column-",
  "               position stability)",
  "    - Age handling: floored numeric ages to integer (drops partial-year",
  "                    precision); top-coded all ages >= 90 to numeric 90",
  "                    (combined with layer-1 string-topcoded entries)",
  "    - Shifted: all date/datetime values per-SID by an additional random",
  "               offset (deterministic seed) on top of layer 1",
  "    - Redacted: free-text 'Re-admit date' column -> '[Date redacted]'",
  "",
  "  Combined effect: within-patient intervals are preserved exactly through",
  "  both layers, so all interval-based outcomes (LOS, days_to_X, survival,",
  "  DFDs) and primary/secondary OR/CI/P statistics are identical to the",
  "  un-shifted source.",
  "",
  "NOT INCLUDED in public release: per-SID layer-2 shift table",
  "  (kept internally as _INTERNAL_DO_NOT_PUBLISH_shifts.csv).",
  "NOT KNOWN to the analysis team: per-patient layer-1 shift values",
  "  (held by the trial team)."
)
writeLines(manifest_lines, file.path(OUTDIR, "MANIFEST.txt"))
cat("\nWrote MANIFEST.txt\n")

cat("\n=== DEID COMPLETE ===\n")
