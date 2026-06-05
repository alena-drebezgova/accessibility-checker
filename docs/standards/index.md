# Standards Documentation Index

This section defines the standards layer of the project: the versioned source of truth that the comparator uses when it turns tool findings into compliance results.

## What belongs here

- WCAG checklist versions and criterion structure
- BITV checklist versions and pruefschritte structure
- checklist file format and required metadata
- mapping rules from tool findings to standards IDs
- manual-only and partial-coverage policy

## Sections

- [WCAG](wcag.md): checklist versions, criteria metadata, and coverage mapping
- [BITV](bitv.md): BITV pruefschritte, hybrid mapping, and curator workflow

## Shared rules

1. Standards are versioned data, not hardcoded logic.
2. WCAG and BITV are separate checklists with separate IDs.
3. Tool adapters do not decide standards compliance; the comparator does.
4. If no tool covers a criterion, the report must mark it as manual.
5. If only some tools cover a criterion, the report must mark it as partial.

## First draft output

The first draft of this folder should give a reader enough information to understand:

- which standards versions we support
- how a checklist entry is structured
- how coverage is assigned to tool findings
- how BITV mapping differs from WCAG mapping
