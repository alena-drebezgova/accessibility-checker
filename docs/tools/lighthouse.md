# Lighthouse

This section documents Lighthouse integration details in the stateful checkpoint model.

## Role In The Stack

Lighthouse provides audit-level diagnostics and accessibility category scoring that complement rule-level engines.

Because Lighthouse often launches independently, this adapter has explicit state-management modes.

## Version And Runtime

- Planned baseline: 13.3.x
- Node.js required
- Browser dependency: Chromium-compatible execution path
- Node package used by this integration: [lighthouse](https://www.npmjs.com/package/lighthouse)
- Source repository: [GoogleChrome/lighthouse](https://github.com/GoogleChrome/lighthouse)

## Version Support Policy

- minimum_supported: 13.3.0
- target_baseline: 13.3.x
- max_tested: 13.3.0
- node_runtime_min: >=22.19

Policy notes:

- This adapter is pinned to Lighthouse 13.3.x until explicit compatibility validation for 14.x.
- Any move of minimum_supported requires matrix and CI runtime update in the same PR.

## Current GitHub Release Reference

- Current Lighthouse version in GitHub repository file: 13.3.0
- Node engines requirement in the same file: >=22.19
- Embedded axe-core dependency constraint in the same file: ^4.11.4

Source file (exact place):

- https://github.com/GoogleChrome/lighthouse/blob/main/package.json

## Execution Model

1. Session Orchestrator provides BrowserSnapshot.
2. Lighthouse adapter decides whether session_attached or isolated mode is available.
3. Adapter executes Lighthouse against the current checkpoint state.
4. Audit results are normalized to ToolResult schema.

Explanation of step 1:

- Session Orchestrator is the flow manager for the current Robot test checkpoint.
- BrowserSnapshot is a structured snapshot of the current page state.
- In this project, the snapshot is produced through the Browser Library integration layer before it is passed to the Lighthouse adapter.

In simple words: the checkpoint manager captures the current page state and then gives that state to Lighthouse.

## Native Data Sources

- lighthouse package metadata
- default Lighthouse config and accessibility audit refs
- embedded axe-core dependency metadata

## Execution Modes

### session_attached (preferred)

- Attach to existing browser/session state from BrowserSnapshot
- Reuse authenticated state from current test flow
- Best fit for checkpoint analysis after login/interactions

### isolated (fallback)

- Launch isolated Lighthouse execution
- Import available state from snapshot (cookies/storage where feasible)
- Use only when attached mode is not available

## Adapter Contract

See the shared contract definition in [../index.md](../index.md#unified-adapter-contract).

Input:

- BrowserSnapshot
- lighthouse_mode: session_attached or isolated
- Optional config: categories, form_factor, throttling, output detail level

Output:

- ToolResult with normalized findings and score metadata
- Raw summary including category scores and selected audit details

## Normalized Finding Example

```json
{
	"source_rule_id": "image-alt",
	"severity": "high",
	"message": "Image elements do not have [alt] attributes",
	"selector_or_target": "audit:image-alt",
	"wcag_candidates": ["1.1.1"],
	"bitv_candidates": ["1.1.1a"],
	"status": "fail"
}
```

Field-by-field explanation:

- source_rule_id: original audit or linked rule ID from Lighthouse.
- severity: normalized severity derived from audit importance/impact context.
- message: human-readable issue description.
- selector_or_target: where the issue was found, or audit identifier if element-level selector is unavailable.
- wcag_candidates: WCAG criteria that this finding may map to.
- bitv_candidates: BITV pruefschritte that this finding may map to.
- status: normalized result status for the pipeline (fail, pass, incomplete, and so on).

Important: this is still a tool-level normalized finding. Final standards compliance decision is made later by the comparator.

## Mapping Strategy

- Use Lighthouse accessibility audits metadata.
- Resolve linked references to rule IDs where available.
- Convert to comparator-ready normalized findings.

## WCAG Norms Used In This Lighthouse Release

Lighthouse accessibility category is based on axe-derived audits and tag-weighting rules in the default config.

Direct evidence in source:

- Accessibility audit refs include wcag2a, wcag2aa, wcag22aa and wcag2aaa-tagged items (for example target-size and identical-links-same-purpose comments).
- Accessibility score weighting is documented in comments as derived from axe-core Impact and Tags.

Source file (audit refs and weighting comments):

- https://github.com/GoogleChrome/lighthouse/blob/main/core/config/default-config.js

Practical interpretation for this project:

- Core automated coverage primarily maps to WCAG 2.x A/AA checks.
- Some WCAG 2.2 checks are present (for example target-size).
- AAA and manual-only checks exist but are weight 0 or manual in many cases.

## Strengths

- Provides category-level accessibility scoring in addition to individual audits
- Reuses a mature audit ecosystem already tied to axe-derived accessibility checks
- Useful complementary perspective to direct rule-engine outputs

## Known Limitations

- Session handling can differ across environments.
- Some audits are page-state sensitive and may vary with timing.
- In isolated mode, authenticated and dynamic state parity may be incomplete.

## Failure And Fallback Policy

1. Attempt session_attached first when configured.
2. If unsupported or failed, retry with isolated mode when allowed.
3. Record execution_mode and fallback information in ToolResult metadata.
