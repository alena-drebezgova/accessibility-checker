# Bootstrap

Bootstrap is the data preparation process that builds the local, versioned JSON artifacts required by the comparator and the standards mapping layer.

This page is primarily for maintainers and automation scripts, because the bootstrap step prepares source data before the library runs in real test flows.

## Why It Exists

The library should not fetch standards and mapping data from external sites at runtime. Instead, data is generated in advance and committed to the repository so reports stay reproducible.

## What Bootstrap Produces

- checklist files for WCAG and BITV
- BITV candidate mappings and curated final mappings
- merged coverage maps used by the comparator

## Inputs

1. Official standards sources such as W3C WCAG and bitvtest.de
2. Tool metadata from GitHub or package metadata
3. Curated mapping decisions from maintainers
4. Embedding-based candidate suggestions for BITV review

## Outputs

Each output file has a specific job in the pipeline:

- `checklists/wcag/wcag_2_1.json`: versioned WCAG 2.1 checklist data with criterion IDs, levels, titles, and metadata used by the comparator.
- `checklists/wcag/wcag_2_2.json`: versioned WCAG 2.2 checklist data, including the newer criteria that do not exist in WCAG 2.1.
- `checklists/wcag/raw/wcag_2_1.json`: raw structured extraction from the official W3C WCAG 2.1 TR page.
- `checklists/wcag/raw/wcag_2_2.json`: raw structured extraction from the official W3C WCAG 2.2 TR page.
- `checklists/bitv/raw/bitv_2_0_web.json`: raw structured extraction from the official BITV-Test page, grouped by section and preserving source metadata.
- `checklists/bitv/bitv_2_0_web.json`: versioned BITV 2.0 web checklist data with pruefschritte, German descriptions, EN 301 549 classification, and mapping status.
- `coverage/standards/bitv_coverage.json`: BITV-specific coverage view that connects German pruefschritte to the tool rules and marks partial or manual cases.
- `coverage/coverage_map.json`: the merged coverage matrix that the comparator reads at runtime to decide PASS, FAIL, PARTIAL, or MANUAL.
- `coverage/mappings/bitv_axe_mapping_candidates.json`: generated candidate matches for BITV mapping, usually produced by embeddings and then reviewed by a human.
- `coverage/mappings/bitv_axe_mapping.json`: the final curated BITV mapping file that the comparator trusts as the source of truth.

Static tool capability snapshots are generated separately into `tools_capabilities/`.

The project keeps the outputs structured so the comparator reads canonical paths directly instead of reconstructing data from live network calls.

If a file is listed here, it should be generated during bootstrap and not reconstructed from live network calls during test execution.

## Bootstrap Workflow

1. Fetch or refresh the raw standard source data.
2. Normalize the raw data into local JSON files.
3. Generate tool coverage datasets from upstream rule metadata.
4. Generate BITV mapping candidates with embeddings.
5. Review candidates and write the curated mapping file.
6. Rebuild the merged coverage map used by the comparator.

## When To Rerun It

- when WCAG or BITV versions change
- when axe-core, Lighthouse, or IBM Equal Access versions change
- when the embedding model changes
- when the curated BITV mapping is corrected or expanded

## Topic Areas

- Fetching WCAG and BITV checklist sources
- Building tool coverage datasets
- Generating mapping candidates and curated mappings
- Regenerating merged coverage map after updates

## Practical Rule

If the comparator or reports depend on it, it should come from bootstrap-generated files rather than live network calls during test execution.
