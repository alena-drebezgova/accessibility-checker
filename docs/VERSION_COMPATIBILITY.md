# Version Compatibility Matrix (Phase 0.1)

Status: Draft verified on 2026-05-29

## Why this document exists

This project integrates tools with different release cadences and different runtime stacks.
A single tool version is not enough. We must track at least five layers for each integration:

1. Tool package version (npm/pypi artifact).
2. Embedded engine version (for example Lighthouse -> axe-core).
3. Runtime version (Node/Python compatibility).
4. Web surface version (report renderer, extension UI, rule archive).
5. Standards checklist version (WCAG/BITV) — the reference we compare against.

If one of these layers changes, scan output can change even if the top-level tool version looks stable.

## How the comparison pipeline works

The key insight is that Lighthouse, axe-core, and IBM do not implement the full WCAG/BITV list.
Each covers a subset of criteria. Our library adds the layer that knows the full list.

```text
STANDARDS (versioned, source of truth)
wcag_2_2.json  ->  87 criteria (the reference)
bitv_3_0.json  ->  98 Prüfschritte

        v  (each tool covers its own subset)

Tool results:
  axe 4.11.4        -> covers ~57 criteria
  Lighthouse 13.3.0 -> covers ~50 criteria
  IBM checker 3.0.0 -> covers ~60 criteria

        v  (Comparator maps rule IDs to WCAG/BITV IDs)

Standards compliance report (per criterion):
  1.1.1  -> axe: FAIL | LH: FAIL | IBM: FAIL -> FAIL
  1.3.1  -> axe: PASS | LH: N/A  | IBM: PASS -> PASS
  2.5.8  -> axe: PASS | LH: N/A  | IBM: N/A  -> PARTIAL
  3.3.7  -> axe: N/A  | LH: N/A  | IBM: N/A  -> MANUAL
```

Status meanings:
- `FAIL` — at least one covering tool found a violation.
- `PASS` — all covering tools passed.
- `PARTIAL` — only some tools cover the criterion, so confidence is incomplete.
- `MANUAL` — no tool covers this criterion; human review is required.
- `N/A` — this tool does not test this criterion at all.

## Standards versioning

### WCAG 2.1
- Published: 2018-06-05
- Criteria count: 78
- File: `checklists/wcag/wcag_2_1.json`
- Still the baseline for most tools and for BITV-Test v3.0.

### WCAG 2.2
- Published: 2023-10-05
- Criteria count: 87
- New vs 2.1: 2.4.11, 2.4.12, 2.4.13, 2.5.7, 2.5.8, 3.2.6, 3.3.7, 3.3.8, 3.3.9
- Removed vs 2.1: 4.1.1 (Parsing — no longer separately testable)
- File: `checklists/wcag/wcag_2_2.json`
- Source: https://www.w3.org/TR/WCAG22/

### BIK BITV-Test v3.0
- Based on: WCAG 2.1 AA
- Prüfschritte count: 98
- File: `checklists/bitv/bitv_3_0.json`
- Source: https://www.bitvtest.de
- Note: contains manual-only Prüfschritte with no automated tool coverage.

When a new standards version appears:
Add a new file, for example `checklists/wcag_3_0.json`. Keep older files.
The comparator selects which version to use at scan time.
Every report records the checklist version used.

## Verified upstream facts

### Lighthouse
- Package version: 13.3.0
- Node engine: >=22.19
- Includes dependency on axe-core: ^4.11.4
- WCAG 2.2 AA coverage: approximately 50 of 87 criteria
- Source: GoogleChrome/lighthouse package.json (main branch)

### axe-core
- Package version: 4.11.4
- Node engine in package metadata: >=4
- WCAG 2.2 AA coverage: approximately 57 of 87 criteria (tags: wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa)
- Source: dequelabs/axe-core package.json (develop branch)

### IBM Equal Access checker
- Package version: 3.0.0
- Node engine: >=16
- WCAG 2.2 AA coverage: approximately 60 of 87 criteria (estimate, verify from rule-server)
- Source: IBMa/equal-access accessibility-checker/package.json (main-4.x)

## Project policy for runtime alignment

Planned baseline:

- Python: >=3.11
- Robot Framework: >=7.0,<8.0
- Browser library: >=17.0,<18.0
- Node (when Lighthouse is enabled): >=22.19

## Mandatory metadata for each scan report

Every exported JSON/HTML report must include:

- tool_version
- embedded_engine_version
- node_version / python_version / browser_version
- rule_archive_version (IBM)
- wcag_checklist_version_used
- bitv_checklist_version_used

## Known risks

1. Lighthouse and direct axe-core can diverge when the resolved axe patch version differs.
2. IBM checks may change with ruleArchive updates even if the package version is unchanged.
3. New WCAG criteria, for example 2.5.8, may not be covered by any tool yet and must be marked `MANUAL`.
4. BIK BITV-Test updates its Prüfschritte independently; watch bitvtest.de for changes.

## WCAG and BITV: two different mapping strategies

### WCAG mapping (tag-based, automated)

How it works:

axe-core rules have tags such as `wcag111`, `wcag143`, `wcag22aa` — these identify WCAG 1.1.1, 1.4.3, and AA-level coverage in WCAG 2.2.

```text
axe-core rule "image-alt"
  -> tags: ["wcag111", "wcag21a", "wcag22a", "cat.images"]
  -> meaning: this rule covers WCAG 1.1.1 Level A

Lighthouse audit "image-alt"
  -> references axe rule "image-alt"
  -> maps to: WCAG 1.1.1

IBM rule "RPT_Img_UsemapAlt"
  -> metadata: WCAG_1_1_1
  -> maps to: WCAG 1.1.1
```

Process:
1. `fetch_axe_coverage.py` parses axe-core rules and extracts tags.
2. `fetch_lighthouse_coverage.py` looks for axe rule references in Lighthouse audits.
3. `fetch_ibm_coverage.py` looks for WCAG_X_X_X metadata in IBM rules.
4. `generate_coverage_map.py` merges everything into one matrix.
5. Result: `coverage/coverage_map.json` with the full WCAG mapping.

Automation: fully automated. Run the scripts whenever the tool version changes.

### BITV mapping (semantic, curator + config)

Why not use tags?

BITV 3.0 contains 98 Prüfschritte organized as:
- Module A: Wahrnehmbarkeit (Perceivability)
- Module B: Bedienbarkeit (Operability)
- and so on.

Each Prüfschritt has a German description and a test methodology.
BITV differs from WCAG in that:
- numbering is different (BITV 1.1.1a vs WCAG 1.1.1)
- rule interpretation can be stricter
- some Prüfschritte are manual-only and cannot be automated
- mapping must be based on semantic understanding, not on tag parsing alone

Example:

```text
BITV Prüfschritt 1.1.1a
  Titel: "Nicht-Text-Inhalte"
  Beschreibung: "Alle Bilder, Icons und sonstige Nicht-Text-Inhalte müssen einen Text-Äquivalent haben"

axe-core rule "image-alt"
  tags: ["wcag111"]
  description: "Images must have an alt attribute"

Mapping: BITV 1.1.1a -> semantically equivalent -> axe "image-alt"
         (but not exactly identical — BITV may require more)
```

Process:
1. `fetch_bitv_checklist.py` scrapes bitvtest.de and extracts all Prüfschritte with descriptions.
2. The curator manually creates `config/bitv/bitv_axe_mapping.json` — an explicit mapping for each Prüfschritt.
3. `generate_bitv_coverage_map.py` uses that config and creates `coverage/standards/bitv_coverage.json`.
4. Result: a traceable, current mapping with notes.

Structure of `bitv_axe_mapping.json`:

```json
{
  "bitv_3_0": {
    "mappings": {
      "1.1.1a": {
        "title": "Nicht-Text-Inhalte",
        "description": "Alle Bilder müssen alt-Text haben",
        "mapped_to": {
          "axe_rules": ["image-alt", "input-image-alt"],
          "ibm_rules": ["RPT_Img_UsemapAlt"],
          "lighthouse_audits": ["image-alt"]
        },
        "wcag_equivalent": "1.1.1",
        "notes": "Stricter than WCAG: BITV requires descriptive alt text, not just presence"
      },
      "3.2.5c": {
        "title": "Change on Request",
        "description": "Context must change only on explicit user request",
        "mapped_to": {
          "axe_rules": [],
          "ibm_rules": [],
          "lighthouse_audits": []
        },
        "wcag_equivalent": "3.2.5",
        "status": "MANUAL_ONLY",
        "notes": "No automated tool can reliably verify this"
      }
    }
  }
}
```

Automation: not automated. It requires:
- knowledge of German and accessibility standards
- knowledge of how the tools work
- manual review of each mapping
- updates when BITV or the tools change

## Semi-automated BITV mapping: embeddings + human review

Fully manual mapping for 98 Prüfschritte is a lot of work. The recommended hybrid approach is:

### Step 1: Generate candidates automatically (embeddings)

```bash
python scripts/generate_bitv_axe_embeddings.py
# -> config/bitv/bitv_axe_mapping_candidates.json
```

Where the descriptions come from:

1. BITV Prüfschritte descriptions (German):
   - Source: https://www.bitvtest.de/pruefverfahren/bitv-2-0-nach-eu-standard
   - Method: `scripts/fetch_bitv_checklist.py` scrapes HTML pages
   - Extracts: title, description, and test method for each Prüfschritt
   - Output goes into `checklists/bitv/bitv_3_0.json` with full descriptions

2. axe-core descriptions (English):
   - Option 1: from the npm package if Node is installed
   - Option 2: from GitHub (without Node)
     - https://raw.githubusercontent.com/dequelabs/axe-core/develop/doc/rule-descriptions.md
     - or directly from rule files: https://github.com/dequelabs/axe-core/tree/develop/lib/rules
   - Output goes into `coverage/tools/axe_core_coverage.json`

How it works:

1. Load the descriptions of all 98 Prüfschritte from `checklists/bitv/bitv_3_0.json`.
2. Load the descriptions of all axe-core rules from `coverage/tools/axe_core_coverage.json`.
3. Use a multilingual model (`sentence-transformers` with `distiluse-base-multilingual-cased-v2`).
4. Generate embeddings (vector representations of meaning in a multidimensional space).
5. Compute cosine similarity between each pair (a number between 0 and 1).
6. For each Prüfschritt, return the top 3 matching rules with a confidence score.

Example: how similarity score works:

```text
BITV Prüfschritt 1.1.1a:
  "Alle Bilder müssen einen alt-Text haben"
  embedding: [0.234, -0.156, 0.892, ..., 0.045]  (384-dimensional vector)

axe-core rule "image-alt":
  "Images must have alt text"
  embedding: [0.241, -0.149, 0.889, ..., 0.042]  (384-dimensional vector)

cosine_similarity([0.234, -0.156, ...], [0.241, -0.149, ...]) = 0.92
  -> very similar (close to 1.0 = identical)

axe-core rule "button-name":
  "Buttons must have accessible names"
  embedding: [0.112, 0.453, -0.234, ..., 0.678]

cosine_similarity([0.234, -0.156, ...], [0.112, 0.453, ...]) = 0.34
  -> not similar (close to 0.0 = completely different)
```

Result:

```json
{
  "1.1.1a": [
    {"rule": "image-alt", "similarity_score": 0.92},
    {"rule": "input-image-alt", "similarity_score": 0.88},
    {"rule": "area-alt", "similarity_score": 0.81}
  ],
  "2.4.11b": [
    {"rule": "focusorder", "similarity_score": 0.79},
    {"rule": "focus-visible", "similarity_score": 0.72},
    {"rule": "tabindex", "similarity_score": 0.65}
  ],
  "3.2.5c": [
    {"rule": null, "similarity_score": 0.0, "note": "No candidates found - likely MANUAL_ONLY"}
  ]
}
```

### Step 2: Manual review and finalization

The curator opens `bitv_axe_mapping_candidates.json` and reviews the scores:

| Score | Interpretation | Curator action |
|-------|---|---|
| > 0.85 | Very close — the embedding found the right match | Quick review: read both descriptions, confirm, approve |
| 0.70 – 0.85 | Similar, but not perfect — needs review | Compare the descriptions carefully; it may be another aspect of the same rule |
| < 0.70 | Not very similar — the embedding is uncertain | Investigate manually or mark as MANUAL_ONLY |
| 0.0 | Nothing matched at all | This Prüfschritt likely needs manual review |

What "edge cases (score < 0.70)" means:

Edge cases are borderline, unclear cases. These are Prüfschritte for which the embedding did not find a clear match.

Examples of edge cases:

```text
Edge case 1: a Prüfschritt about text contrast on a background
  BITV description: "Text and background must have 4.5:1 contrast"
  Score for axe "color-contrast": 0.68 (low!)
  Why low? Because axe describes it with different words
  Curator: reads both descriptions, understands they are the same, adds the mapping

Edge case 2: BITV about focus behavior
  Embedding returned scores: [0.65, 0.60, 0.58]
  All three are low, nothing is a good match
  Curator: this may be MANUAL_ONLY because tools do not verify behavior

Edge case 3: BITV about document structure
  Embedding returned: 0.0 (nothing at all)
  Curator: even similar rules were not found, so no tool covers this
```

Why edge cases matter:

✅ High scores (>0.85): the curator can trust them and approve quickly
⚠️ Medium scores (0.70-0.85): the curator checks them carefully and usually confirms them
🔍 Edge cases (<0.70): the curator should focus here, because these are the hard cases — either find the right rule or mark it MANUAL_ONLY

After review, the final `config/bitv/bitv_axe_mapping.json` is created:

```json
{
  "bitv_3_0": {
    "mappings": {
      "1.1.1a": {
        "title": "Nicht-Text-Inhalte",
        "mapped_to": {
          "axe_rules": ["image-alt", "input-image-alt", "area-alt"]
        },
        "confidence": "high",
        "score_from_embeddings": 0.92
      },
      "3.2.5c": {
        "title": "Change on Request",
        "mapped_to": {
          "axe_rules": []
        },
        "status": "MANUAL_ONLY",
        "reason": "Embedding score 0.0, no tool can verify user intent"
      }
    }
  }
}
```

When should the embeddings generator be run?

| Event | Action |
|---------|----------|
| First time | Run it, then the curator reviews all results |
| New BITV version | Run it for the new Prüfschritte, then review the new results |
| New axe-core version | Run it, then check whether existing mappings changed |
| Periodic model update | Run it with the new embedding model and check divergence from old results |

Benefits of the embedding approach:

✅ For the curator:
- No need to compare every pair (98 × 50+ = thousands of combinations)
- Immediately sees the top 3 candidates with scores
- Can focus on edge cases (score < 0.70)
- Reproducible: one model -> one set of candidates

✅ For the project:
- Speed: days down to hours
- Quality: embeddings capture semantics, not only keywords
- Multilingual: one model works with German and English
- Versionable: the embedding model version can be pinned

Potential problems and how to avoid them:

| Problem | Solution |
|----------|---------|
| The embedding model does not know accessibility terminology | Use a fine-tuned model for a11y or review low-score results |
| One Prüfschritt maps to several axe rules | Embeddings will show all of them; the curator chooses the right one |
| A new model version produces different results | Pin the model version in requirements and document updates |
| Score does not reflect real-world equivalence | Manual review is still required; the score is only a recommendation |

---

- docs/reports/matrices/version_matrix.json (includes standards_checklists, tool_wcag_coverage, and standards_mapping_strategy blocks)
- docs/reports/matrices/compatibility_matrix.csv
- docs/VERSION_COMPATIBILITY.md (this file, with a comparison of WCAG/BITV mapping strategies)
- plan.md sections 0.1, 0.1.1, 0.5 (architecture diagrams and data bootstrap scripts)