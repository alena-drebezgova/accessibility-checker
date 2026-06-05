# IBM Equal Access

This section documents IBM Equal Access integration details in the stateful checkpoint model.

## Role In The Stack

IBM Equal Access provides an additional rule engine perspective and policy metadata that complements axe and Lighthouse.

The adapter must execute against the same active Browser Library state used by other tools.

## Version And Runtime

- Planned baseline: 3.x
- Runtime: browser page context from BrowserSnapshot
- Node.js requirement: depends on integration path used by selected IBM runner
- Node package used by this integration: [accessibility-checker](https://www.npmjs.com/package/accessibility-checker)
- Source repository: [IBMa/equal-access](https://github.com/IBMa/equal-access)

## Version Support Policy

- minimum_supported: 3.0.0
- target_baseline: 3.x
- max_tested: 3.0.0
- node_runtime_min: >=16

Policy notes:

- Rule archive version must be captured with each scan.
- Compatibility updates require synchronized changes in version_matrix.json and compatibility_matrix.csv.

## Current GitHub Release Reference

- Current accessibility-checker package version in GitHub repository file: 3.0.0
- Node engines requirement in the same file: >=16

Source file (exact place):

- https://github.com/IBMa/equal-access/blob/main-4.x/accessibility-checker/package.json

## Execution Model

1. Session Orchestrator provides BrowserSnapshot.
2. IBM adapter reads active page/context from snapshot.
3. Adapter executes IBM checks on current UI state.
4. Results are normalized to ToolResult schema.

Explanation of step 1:

- Session Orchestrator is the flow manager for the current Robot test checkpoint.
- BrowserSnapshot is a structured snapshot of the current page state.
- In this project, the snapshot is produced through the Browser Library integration layer before it is passed to the IBM adapter.

In simple words: the checkpoint manager captures the current page state and then gives that state to the IBM checker.

## Native Data Sources

- accessibility-checker package metadata
- accessibility-checker-engine rule files
- rulesets metadata with WCAG policy IDs and criterion numbers

## Adapter Contract

See the shared contract definition in [../index.md](../index.md#unified-adapter-contract).

Input:

- BrowserSnapshot
- Optional options: policy profile, severity filters, include_experimental

Output:

- ToolResult with normalized findings
- Raw summary from IBM engine

## Normalized Finding Example

```json
{
	"source_rule_id": "RPT_Img_UsemapAlt",
	"severity": "serious",
	"message": "Image map areas must have alternate text",
	"selector_or_target": "img[usemap]",
	"wcag_candidates": ["1.1.1"],
	"bitv_candidates": ["1.1.1a"],
	"status": "fail"
}
```

Field-by-field explanation:

- source_rule_id: original rule ID from the IBM engine.
- severity: tool-level impact/severity.
- message: human-readable issue description.
- selector_or_target: where the issue was found on the page.
- wcag_candidates: WCAG criteria that this finding may map to.
- bitv_candidates: BITV pruefschritte that this finding may map to.
- status: normalized result status for the pipeline (fail, pass, incomplete, and so on).

Important: this is still a tool-level normalized finding. Final standards compliance decision is made later by the comparator.

## Mapping Strategy

- Extract WCAG-related metadata from IBM rule model where available.
- Keep IBM-native rule IDs in normalized output for traceability.
- Delegate final standards status decision to comparator.

## WCAG Norms Used In This IBM Release

IBM rule definitions encode standards mapping directly in rulesets ids and criterion numbers.

Observed mapping patterns in source:

- Generic template includes ids like WCAG_2_0 and WCAG_2_1.
- Concrete rules include ids with WCAG_2_2 and criterion numbers (for example 2.5.8).

Source files:

- Template ruleset mapping pattern:
	https://github.com/IBMa/equal-access/blob/main-4.x/accessibility-checker-engine/src/v4/rules/_template.txt
- Concrete WCAG 2.2 rule example (target spacing / 2.5.8):
	https://github.com/IBMa/equal-access/blob/main-4.x/accessibility-checker-engine/src/v4/rules/target_spacing_sufficient.ts

Practical interpretation for this project:

- IBM engine rule metadata references WCAG 2.0, 2.1, and 2.2 in current rule files.
- Final standards compliance status still must be resolved by comparator using the project mapping layer.

## Strengths

- Rich built-in standards metadata in rule definitions
- Additional independent rule engine perspective beyond axe and Lighthouse
- Explicit linkage from rulesets to WCAG policy IDs and criterion numbers

## Known Limitations

- Coverage is partial relative to full WCAG/BITV checklist.
- Policy mappings may evolve between IBM engine versions.
- Some findings may require human review for final standards interpretation.

## Failure Behavior

If IBM execution fails at a checkpoint:

1. Return ToolResult with errors and no hard crash of the session pipeline.
2. Allow comparator to continue with available tool results.
3. Mark missing IBM contribution explicitly in report metadata.
