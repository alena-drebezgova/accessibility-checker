# Scripts

## Bootstrap Standards Data

Use this command to (re)generate WCAG/BITV checklists, mapping files, and coverage artifacts:

```bash
python3 scripts/bootstrap_standards_data.py
```

The script writes structured primary outputs:

- `checklists/wcag/wcag_2_1.json`
- `checklists/wcag/wcag_2_2.json`
- `checklists/bitv/bitv_3_0.json`
- `config/bitv/bitv_axe_mapping.json`
- `config/bitv/bitv_axe_mapping_candidates.json`
- `coverage/tools/axe_core_coverage.json`
- `coverage/tools/lighthouse_coverage.json`
- `coverage/tools/ibm_coverage.json`
- `coverage/standards/bitv_coverage.json`
- `coverage/coverage_map.json`

The current generator writes the structured JSON artifacts listed above; older flat-path mirrors are no longer produced by this script.

## Fetch BITV Checklist

Use this command to fetch the official BITV page and build the raw + normalized BITV checklist layer:

```bash
python3 scripts/fetch_bitv_checklist.py
```

It writes two outputs by default:

- `checklists/bitv/raw/bitv_20_web.json`
- `checklists/bitv/bitv_20_web.json`

The raw file stores the structured extraction from bitvtest.de (including description and Einordnung des Pruefschritts). The normalized file flattens the raw sections into the canonical checklist format used for comparison and mapping.

## CI Example

```yaml
- name: Regenerate standards artifacts
  run: python3 scripts/bootstrap_standards_data.py
```
