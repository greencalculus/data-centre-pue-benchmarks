# Data Centre PUE Benchmarks

Every publicly disclosed Power Usage Effectiveness (PUE) figure we could trace to its publisher, in one table, with the source, the period, and what each figure measures.

PUE = total facility energy ÷ IT equipment energy (ISO/IEC 30134-2:2026). A PUE of 1.0 would mean every kWh reaches the IT equipment.

- **104 rows** from 9 publishers: Google (fleet and 35 campuses), Amazon Web Services (fleet and 27 cloud regions), Microsoft, Equinix, Digital Realty, the Uptime Institute global survey (2007–2025), the European Commission's report on EU data centres, IDC estimates as quoted by AWS, and NLR's ESIF data centre.
- **Each value is copied exactly** as the publisher printed it. Nothing is estimated, converted or averaged by us.
- **Retrieved 10 October 2026.** Each row records its source URL and the table, filing or document date it came from.

Interactive version with a PUE calculator: https://greencalculus.com/calculators/data-centre-pue-calculator/

## Files

| File | What it is |
|---|---|
| `pue-benchmarks.csv` | The dataset, one row per figure |
| `pue-benchmarks.json` | The same rows as JSON |
| `sources_snapshot.json` | The Google and AWS tables as parsed from their pages on the retrieval date |
| `build.py` | Rebuilds the CSV and JSON from the snapshot and the hand-checked rows |

## Columns

| Column | Meaning |
|---|---|
| `id` | Row id, stable within a version |
| `publisher` | Who published the figure |
| `scope` | `fleet`, `campus`, `cloud_region`, `geographic_region`, `facility`, `new_builds`, `industry_survey`, `industry_estimate` or `regulatory_average` |
| `facility_or_region` | The site, region or population the figure describes |
| `country` | ISO 3166-1 alpha-2 code where the figure is for one country |
| `period` / `period_type` | The period the figure covers: trailing 12 months, calendar or fiscal year, quarter, survey year, design value or estimate |
| `pue` | The figure as published |
| `metric` | `operational` (measured), `design`, `survey_average`, `regulatory_average` or `estimate` |
| `boundary_note` | What the publisher says the figure includes |
| `source_title`, `source_url`, `source_date` | Where the figure was read |
| `retrieved` | The date we read it |
| `notes` | Quotes, quarterly values and caveats |

## Read before comparing

- **Figures are not like for like.** Google reports a fleet trailing-12-month PUE including all overhead; Uptime reports a survey average of each respondent's own data centre; the EU figure averages facilities of 500 kW and above that reported under the Energy Efficiency Directive. Compare within a `metric` and `period_type` first.
- **Measurement points differ.** Where a publisher meters IT energy (UPS output, PDU output or IT equipment input) changes the result. Most publishers do not say.
- **Design PUE is not operating PUE.** Rows with `metric = design` are targets for new buildings.
- **Absence is information.** Meta's 2025 Sustainability Report contains no fleet PUE, so Meta has no row.

## Licence and citation

The compilation is released under **CC BY 4.0**. The figures themselves are facts published by the organisations named in each row; cite them as well as this dataset.

Cite as: Say, J. (2026). *Data Centre PUE Benchmarks* (Version 2026.10.10) [Data set]. GreenCalculus.

Corrections: open an issue on this repository with the row id and the source.
