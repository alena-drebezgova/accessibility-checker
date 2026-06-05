# Tools Documentation Index

This section documents all accessibility engine integrations used by the project.

The goal is to keep one consistent runtime contract across all tools, so the comparator and reporter do not need tool-specific branching logic.

## Tool Pages

- [axe-core](axe-core.md): rules model, WCAG tag parsing, adapter behavior
- [lighthouse](lighthouse.md): audit model, session-attached mode, isolated fallback
- [ibm-equal-access](ibm-equal-access.md): rule model, WCAG metadata extraction, adapter behavior

## Tool Comparison Snapshot

| Tool | Node Package | Source Repository | Current GitHub Version | Node Requirement | Standards Source |
|------|--------------|-------------------|------------------------|------------------|------------------|
| axe-core | [axe-core](https://www.npmjs.com/package/axe-core) | [dequelabs/axe-core](https://github.com/dequelabs/axe-core) | [4.12.0](https://github.com/dequelabs/axe-core/blob/develop/package.json) | >=4 | [README](https://github.com/dequelabs/axe-core/blob/develop/README.md#the-accessibility-rules), [rules](https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md) |
| Lighthouse | [lighthouse](https://www.npmjs.com/package/lighthouse) | [GoogleChrome/lighthouse](https://github.com/GoogleChrome/lighthouse) | [13.3.0](https://github.com/GoogleChrome/lighthouse/blob/main/package.json) | >=22.19 | [default config](https://github.com/GoogleChrome/lighthouse/blob/main/core/config/default-config.js) |
| IBM Equal Access | [accessibility-checker](https://www.npmjs.com/package/accessibility-checker) | [IBMa/equal-access](https://github.com/IBMa/equal-access) | [3.0.0](https://github.com/IBMa/equal-access/blob/main-4.x/accessibility-checker/package.json) | >=16 | [template](https://github.com/IBMa/equal-access/blob/main-4.x/accessibility-checker-engine/src/v4/rules/_template.txt), [WCAG 2.2 example](https://github.com/IBMa/equal-access/blob/main-4.x/accessibility-checker-engine/src/v4/rules/target_spacing_sufficient.ts) |

## Unified Adapter Contract

This section is the canonical shared definition for all tool adapters.

All tool adapters must implement the same logical interface:

```python
class ToolAdapter(Protocol):
	name: str
	version: str

	def run(self, snapshot: BrowserSnapshot) -> ToolResult:
		...
```

### BrowserSnapshot (input)

Minimal required fields:

- checkpoint_name
- url
- page_handle (active Browser Library page)
- context_handle (active Browser Library context)
- cookies
- local_storage
- session_storage
- timestamp

### ToolResult (output)

Minimal required fields:

- tool
- tool_version
- checkpoint_name
- url
- findings (normalized list)
- raw_summary
- execution_mode
- duration_ms
- errors (if any)

## Normalization Rules

All tools must normalize findings to one shared schema used by the comparator:

- source_rule_id
- severity
- message
- selector_or_target
- wcag_candidates
- bitv_candidates
- status (pass, fail, incomplete, not_applicable, manual_only)

## Mapping Responsibility

Tool adapters should expose as much native metadata as possible.

- axe-core: WCAG tags from rules
- Lighthouse: audit metadata and linked rule references
- IBM Equal Access: rule metadata with WCAG policy links

Final standards-level mapping is performed by the comparator layer, not by individual adapters.

## Scope

Each tool page should describe:

1. Version constraints
2. Runtime requirements
3. Input and output model
4. Mapping behavior to WCAG/BITV
5. Known limitations

## Documentation Quality Gate

Before implementing or changing an adapter, ensure the corresponding tool page includes:

1. Tested version range
2. Required environment
3. Execution mode details
4. Example normalized output
5. Failure and fallback behavior
