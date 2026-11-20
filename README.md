# Caste AI

This repository is the sanitized public data release accompanying the Caste AI research project.

## Public data

`data/profiles.csv` contains 200 person-level profile rows. It combines the two source tables into one neutrally named file and sorts the rows by the released attributes, so source-table membership is not retained as a field, filename, or row block.

The profile table has exactly these columns, in this order:

```text
Age,Height,Caste,Education,Profession,Income,City,Complexion,Diet,Religion
```

No claim of anonymity is made for these records. The file is a minimized research release containing only the listed attributes.

`data/aggregate_outcomes.csv` contains model-level descriptive summaries of the study outcomes. It contains no person-level profile attributes and no row-level linkage values. Its two source groups were combined before aggregation. `Count` is the number of numeric observations, and the standard-deviation column uses the sample definition.

## Excluded material

The public snapshot excludes the source platform dumps, all platform metadata and row-linkage fields, provider request and batch identifiers, duplicate and legacy datasets, row-level rating tables, prompts and responses, notebooks and rendered notebook pages, generated PDFs, logs, caches, local environment files, and attributes outside the public schema.

Prompts and row-level results were not retained because the audited artifacts combined linkage metadata with contextual profile information outside the release schema. Removing only their linkage fields would not have made those artifacts suitable for this release. Aggregate outcome summaries are retained because they do not expose row-level records.

The excluded source artifacts are not required to inspect or validate the public files. They are intentionally unavailable from this repository, so the original extraction and model-request pipeline cannot be reproduced from the public snapshot alone.

## Validation

The validator uses only the Python standard library:

```bash
python3 scripts/validate_public_snapshot.py
```

It checks the repository allowlist, the exact profile schema, CSV row widths, aggregate-result schema, forbidden linkage-field markers, filenames, symlinks, and common secret patterns.
