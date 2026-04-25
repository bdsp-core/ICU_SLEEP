# Minting a code DOI via Zenodo

The data publication on bdsp.io will get its own DOI for the *data*. To get an independent, archival DOI for the *code* in this repository — strongly recommended for journal submission and long-term citability — link the GitHub repo to Zenodo and tag a release at acceptance.

## One-time setup (do this before tagging the release)

1. Go to https://zenodo.org and sign in with the GitHub account that owns the repository (probably the `bdsp-core` org admin).
2. Navigate to your account → "GitHub" tab. You will see a list of repositories.
3. Find `bdsp-core/ICU_SLEEP` and toggle the switch to **On**. This installs a webhook in the GitHub repo.
4. (Optional but recommended) Pre-fill metadata: in your Zenodo account "Profile" tab you can set defaults for affiliation, ORCID, etc.

## When the manuscript is accepted

1. Update [CITATION.cff](../CITATION.cff) with the manuscript DOI (the new line under `identifiers:`) and the bdsp.io data DOI.
2. Update [README.md](../README.md) to reference the published paper.
3. Tag a GitHub release. Use semantic versioning, e.g. `v1.0.0`:
   ```bash
   gh release create v1.0.0 \
     --title "ICU-SLEEP v1.0.0 (paper acceptance)" \
     --notes "Initial release accompanying the published manuscript. See README.md."
   ```
4. Within ~minutes, Zenodo will pick up the release via the webhook, archive a snapshot of the repo, and mint a DOI. You'll receive an email with the DOI URL.
5. Add the Zenodo DOI badge to the top of [README.md](../README.md):
   ```markdown
   [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
   ```
6. Update [CITATION.cff](../CITATION.cff) with the code DOI under `identifiers:`.
7. Make a small follow-up commit with the README + CITATION.cff badge update (no need to re-tag).

## Subsequent releases

Each new tag-release on GitHub automatically gets its own version DOI on Zenodo. There is also a "concept DOI" that always points to the latest version — you can use that one for general citation purposes.

## Why both Zenodo and bdsp.io DOIs?

- **bdsp.io DOI**: identifies the *dataset* (credentialed-access). Cite this when describing the data.
- **Zenodo DOI**: identifies a specific *snapshot of the analysis code*. Cite this for full reproducibility — readers know exactly which code version produced the published results.

Many journals now require both, and the practice strengthens the reproducibility story.
