# axe-core

This section documents axe-core integration details in the stateful checkpoint model.

## Role In The Stack

axe-core is the primary DOM-level analyzer that runs directly on the active page from Browser Library.

It should execute without opening a new browser context, so it naturally preserves the authenticated state and dynamic UI state at each checkpoint.

## Version And Runtime

- Planned baseline: 4.11.x
- Runtime dependency: JavaScript execution in the active browser page
- Node.js requirement: optional at runtime if execution happens through page-injected script path
- Node module used when Node path is enabled: [axe-core npm package](https://www.npmjs.com/package/axe-core)
- Source repository: [dequelabs/axe-core](https://github.com/dequelabs/axe-core)

## Version Support Policy

- minimum_supported: 4.11.0
- target_baseline: 4.11.x
- max_tested: 4.12.0
- node_runtime_min: >=4 (package engines)

Policy notes:

- Support range should be updated together with docs/reports/matrices/version_matrix.json.
- If max_tested moves, update this file and compatibility_matrix.csv in one change.

## Current GitHub Release Reference

- Current axe-core version in GitHub repository file: 4.12.0
- Node engines requirement in the same file: >=4

Source file (exact place):

- https://github.com/dequelabs/axe-core/blob/develop/package.json


## Execution Model

1. Session Orchestrator asks State Bridge for a BrowserSnapshot.
2. axe adapter receives active page/context handles from snapshot.
3. Adapter executes axe run on the current DOM.
4. Native violations/passes/incomplete are converted to ToolResult.
 
Explanation of step 1:
- Session Orchestrator is the flow manager for the current Robot test checkpoint.
- State Bridge is the integration layer that reads current Browser Library runtime state.
- BrowserSnapshot is a structured snapshot of the current page state (url, page/context handles, cookies/storage metadata).
In simple words: the flow manager asks the Browser Library bridge, "give me the current page state now", then passes that state to the adapter.

## Native Data Sources

- Rule metadata and tags from axe rule model
- WCAG tags such as wcag111, wcag143, wcag22aa

## Adapter Contract

See the shared contract definition in [../index.md](../index.md#unified-adapter-contract).

Input:

- BrowserSnapshot with active page
- Optional run options: include_tags, exclude_tags, run_only, context_selector

Output:

- ToolResult with normalized findings
- Raw summary counts (violations, passes, incomplete, inapplicable)

## Normalized Finding Example

```json
{
	"source_rule_id": "image-alt",
	"severity": "critical",
	"message": "Images must have alternate text",
	"selector_or_target": "img.logo",
	"wcag_candidates": ["1.1.1"],
	"bitv_candidates": ["1.1.1a"],
	"status": "fail"
}
```

Field-by-field explanation:

- source_rule_id: original rule ID from the tool (here: image-alt).
- severity: tool-level impact/severity.
- message: human-readable issue description.
- selector_or_target: where the issue was found on the page.
- wcag_candidates: WCAG criteria that this finding may map to.
- bitv_candidates: BITV pruefschritte that this finding may map to.
- status: normalized result status for the pipeline (fail, pass, incomplete, and so on).

Important: this is still a tool-level normalized finding. Final standards compliance decision is made later by the comparator.

## Mapping Strategy

- Extract WCAG references from axe tags.
- Convert compact tag format to dotted criterion format where possible.
- Do not finalize standards status in adapter; delegate final decision to comparator.

## WCAG Norms In This axe-core Version

For axe-core 4.12.x, official project docs and generated rule list indicate support groups for:

- WCAG 2.0 Level A and AA
- WCAG 2.1 Level A and AA
- WCAG 2.2 Level A and AA
- WCAG 2.x Level AAA (automatable subset)

Source files:

- WCAG versions/levels statement:
	https://github.com/dequelabs/axe-core/blob/develop/README.md#the-accessibility-rules
- Rule groups and tags (including wcag2a, wcag2aa, wcag21aa, wcag22aa, wcag2aaa):
	https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md

## Strengths

- Fast on-page execution
- Rich selector-level findings
- Strong WCAG tag metadata

## Known Limitations

- Does not cover full WCAG/BITV checklist
- Some findings need manual context interpretation
- Dynamic timing-sensitive UI states may require explicit waits before checkpoint

## Failure Behavior

If execution fails:

1. Return ToolResult with errors populated
2. Keep checkpoint pipeline alive for remaining tools
3. Mark tool status as execution_error in reporter summary
