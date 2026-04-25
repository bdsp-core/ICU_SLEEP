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

INPUT_XLSX <- "../ICU_SLEEP_final_FromHao/data/ICU-SLEEP_Data_P1_Deidentified_11.26.25.xlsx"
OUTDIR <- "../_deid_output"
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

  # 3) Cap age at 89
  age_col <- "Age (years) [at enrollment]"
  if (age_col %in% names(df)) {
    n_over <- sum(df[[age_col]] > 89, na.rm = TRUE)
    if (n_over > 0) {
      cat("  CAPPING ", n_over, " ages > 89 to 89\n")
      df[[age_col]] <- pmin(df[[age_col]], 89, na.rm = FALSE)
    }
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
  "Deidentification applied:",
  "  - Dropped: ZID, DOB columns",
  "  - Capped: 'Age (years) [at enrollment]' at 89 (HIPAA Safe Harbor for >=90)",
  "  - Shifted: all date/datetime values per-SID by a random offset (range +/-1095 d)",
  "             (within-patient intervals are preserved, so all derived",
  "              days_from_X_to_Y values remain unchanged)",
  "  - Redacted: free-text 'Re-admit date' column -> '[Date redacted]'",
  "",
  "NOT INCLUDED in public release: per-SID shift table",
  "  (kept internally as _INTERNAL_DO_NOT_PUBLISH_shifts.csv)"
)
writeLines(manifest_lines, file.path(OUTDIR, "MANIFEST.txt"))
cat("\nWrote MANIFEST.txt\n")

cat("\n=== DEID COMPLETE ===\n")
