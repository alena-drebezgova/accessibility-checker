# Scripts

## Bootstrap Standards Data

Use this command to (re)generate WCAG/BITV checklists, mapping files, and coverage artifacts:

```bash
python3 scripts/bootstrap_standards_data.py
```

The script writes structured primary outputs:

- `checklists/wcag/raw/wcag_2_1.json`
- `checklists/wcag/raw/wcag_2_2.json`
- `checklists/wcag/wcag_2_1.json`
- `checklists/wcag/wcag_2_2.json`
- `checklists/bitv/raw/bitv_2_0_web.json`
- `checklists/bitv/bitv_2_0_web.json`
- `coverage/mappings/bitv_axe_mapping.json`
- `coverage/mappings/bitv_axe_mapping_candidates.json`
- `coverage/standards/bitv_coverage.json`
- `coverage/coverage_map.json`

The current generator writes the structured JSON artifacts listed above; older flat-path mirrors are no longer produced by this script.

## Fetch BITV Checklist

Use this command to fetch the official BITV page and build the raw + normalized BITV checklist layer:

```bash
python3 scripts/fetch_bitv_checklist.py
```

It writes two outputs by default:

- `checklists/bitv/raw/bitv_2_0_web.json`
- `checklists/bitv/bitv_2_0_web.json`

The raw file stores the structured extraction from bitvtest.de (including description and Einordnung des Pruefschritts). The normalized file flattens the raw sections into the canonical checklist format used for comparison and mapping.

## Fetch WCAG Checklist

Use this command to fetch official W3C WCAG sources and build the raw + normalized WCAG checklist layer:

```bash
python3 scripts/fetch_wcag_checklist.py
```

It writes four outputs by default:

- `checklists/wcag/raw/wcag_2_1.json`
- `checklists/wcag/raw/wcag_2_2.json`
- `checklists/wcag/wcag_2_1.json`
- `checklists/wcag/wcag_2_2.json`

The source pages are `https://www.w3.org/TR/WCAG21/` and `https://www.w3.org/TR/WCAG22/`.

## Fetch Tool Capabilities

Use this command to fetch static tool capabilities from GitHub and generate local capability snapshots:

```bash
python3 scripts/fetch_tool_capabilities.py
```

Run only one tool when needed (single-purpose entry points):

```bash
python3 scripts/fetch_axe_capabilities.py
python3 scripts/fetch_lighthouse_capabilities.py
python3 scripts/fetch_ibm_capabilities.py
```

You can also use one common script with explicit selection:

```bash
python3 scripts/fetch_tool_capabilities.py --tool axe
python3 scripts/fetch_tool_capabilities.py --tool lighthouse
python3 scripts/fetch_tool_capabilities.py --tool ibm
python3 scripts/fetch_tool_capabilities.py --tool all
```

It writes three outputs:

- `tools_capabilities/axe_core_capabilities.json`
- `tools_capabilities/lighthouse_capabilities.json`
- `tools_capabilities/ibm_capabilities.json`

The script uses GitHub repository metadata for:

- dequelabs/axe-core
- GoogleChrome/lighthouse
- IBMa/equal-access

## CI Example

```yaml
- name: Regenerate standards artifacts
  run: python3 scripts/bootstrap_standards_data.py
```
