# WCAG

WCAG is the primary standards reference for the comparator. The project keeps WCAG as versioned checklist data so that reports can be generated against a known published baseline.

WCAG is an international accessibility standard maintained by W3C, so this page uses the standard's common English terminology and reference structure.

## Supported versions

- WCAG 2.1: project baseline for most tool mappings and for BITV 3.0 alignment
- WCAG 2.2: preferred current comparison target when the chosen tool coverage allows it

Source: [w3.org/TR/WCAG22](https://www.w3.org/TR/WCAG22/)

Older or future versions can be added as new checklist files without removing the existing ones.

## Checklist files

- `checklists/wcag/wcag_2_1.json`
- `checklists/wcag/wcag_2_2.json`

Each checklist file should contain:

1. checklist version and publication date
2. criterion ID and title
3. conformance level
4. short description
5. status metadata used by the comparator
6. optional notes about tool coverage gaps

## Canonical criterion shape

```json
{
	"id": "1.1.1",
	"title": "Non-text Content",
	"level": "A",
	"version": "2.2",
	"status": "covered",
	"notes": [
		"Mapped from axe-core tags and equivalent rule metadata"
	]
}
```

## Mapping strategy

WCAG mapping is automated wherever possible.

- axe-core contributes rule tags such as `wcag111` and `wcag22aa`
- Lighthouse inherits accessibility coverage through its axe-based audits
- IBM Equal Access contributes WCAG metadata from its rule definitions

The comparator merges those sources and assigns a final WCAG status per criterion:

- `FAIL` when at least one covering tool reports a violation
- `PASS` when all covering tools pass
- `PARTIAL` when only some tools cover the criterion
- `MANUAL` when no tool covers the criterion

## What this page should answer

1. Which WCAG versions are stored in the project.
2. How a criterion is represented in checklist data.
3. How automated tool coverage becomes a WCAG compliance result.
4. Why some criteria are intentionally left as manual.
