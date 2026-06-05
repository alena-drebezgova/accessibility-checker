# BITV

BITV is documented separately from WCAG because it is not just a renamed WCAG checklist. It is a German test procedure with its own pruefschritte, review expectations, and manual-only cases.

BITV comes from Germany and is used as a German accessibility testing standard, so this page is written with German terminology and context in mind.

## Supported version

- BITV 2.0 (BIK BITV-Test / EN 301 549 (Web))
- EN 301 549 version: 3.2.1
- WCAG reference in EN 301 549 web profile: 2.1
- Source: [bitvtest.de](https://bitvtest.de/pruefverfahren/bitv-20-web)

The project treats BITV as a profile that references EN 301 549 and WCAG 2.1 criteria, but is not identical to WCAG.

## Checklist files

- `checklists/bitv/bitv_20_web.json`

Each BITV checklist entry should contain:

1. pruefschritt ID
2. title and description
3. linked WCAG baseline criterion, if there is one
4. mapping status
5. notes explaining ambiguous or manual cases

## Mapping strategy

BITV mapping is hybrid:

- automated candidate generation narrows the search space
- human curation confirms the final mapping
- the comparator consumes only the curated result, not the raw candidate list

Recommended flow:

1. generate BITV candidates from German pruefschritt text and English tool rule descriptions
2. review top matches with confidence scores
3. accept, reject, or mark as manual only
4. write the final mapping file used by the comparator

## Status policy

BITV entries may end up in one of four practical states:

- `covered` when at least one tool can verify the pruefschritt
- `partial` when the criterion is only partially supported by automated tools
- `manual` when no reliable automation exists
- `unmapped` when the mapping still needs curator work

## Why this folder exists separately from WCAG

1. BITV has German language descriptions that need semantic matching.
2. Some BITV checks are stricter than the related WCAG criterion.
3. Some BITV checks have no automated equivalent at all.
4. The final mapping must be curated, versioned, and traceable.
