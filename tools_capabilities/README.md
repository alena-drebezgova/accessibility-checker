# Tool Capabilities (Static Coverage)

This folder stores static capability snapshots per tool:
- what each rule or audit can cover in WCAG
- what each rule or audit can cover in BITV

Files:
- axe_core_capabilities.json
- lighthouse_capabilities.json
- ibm_capabilities.json

Notes:
- These files are static capability references (not runtime scan results).
- Runtime findings are merged later with these capabilities to build compliance status.
- Keep tool versions in each file aligned with the versions used during scans.
