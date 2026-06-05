# Robot Framework Accessibility Checker

A stateful accessibility testing library for Robot Framework.

This project integrates multiple accessibility engines (axe-core, Lighthouse, IBM Equal Access), maps their findings to WCAG and BITV checklists, and supports checkpoint-based scanning inside real UI flows (for example: after login, after opening a dialog, after submitting a form).

## Goals

- Run accessibility checks inside end-to-end test flows, not only on static URLs.
- Reuse the active Browser Library session and keep authentication/session state.
- Normalize results from multiple tools into one comparison model.
- Produce both tool-level reports and standards-level compliance reports.

## High-Level Architecture

- Session Orchestrator: controls checkpoint lifecycle for one Robot test.
- State Bridge: reads the current Browser Library context/page/storage state.
- Tool Adapters: run axe-core, Lighthouse, and IBM checks against the same snapshot.
- Comparator: maps findings to WCAG/BITV criteria and computes final status.
- Reporter: exports JSON/HTML outputs and checkpoint timelines.

## Repository Structure

```text
accessibility-checker/
├── .github/
│   └── workflows/                     # CI/CD pipelines (tests, publish, docs)
├── config/                            # Curated mapping configs (for example BITV-to-tool mapping)
├── coverage/                          # Generated tool coverage maps and merged coverage model
├── checklists/                        # Generated checklist JSON data (WCAG/BITV)
├── docs/                              # Project documentation
├── scripts/                           # Data bootstrap and generation scripts
├── src/
│   └── robotframework_accessibility_checker/
│       ├── checklists/               # Checklist handling code inside the package
│       └── tools/                    # Tool adapters (axe, Lighthouse, IBM)
├── tests/
│   ├── robot/
│   │   └── examples/                 # Robot Framework usage examples
│   └── unit/                         # Python unit tests
├── archive/                          # Archived planning notes
│   └── accessibility_library_plan.md
├── plan.md                           # Main implementation plan
└── docs/reports/matrices/            # Compatibility matrix sources (CSV/JSON)
```

## What Each Main Directory Is For

- `.github/workflows`: automation for CI, packaging checks, and release workflows.
- `src`: installable Python package source code.
- `tests`: automated tests (unit + Robot scenarios).
- `scripts`: developer utilities to fetch standards data and build mapping artifacts.
- `checklists`: versioned WCAG/BITV checklist data used by the comparator.
- `coverage`: generated coverage datasets per tool and unified coverage map.
- `config`: human-reviewed/curated mapping files and runtime configuration artifacts.
- `docs`: user and developer documentation.

## Planned Package Modules

The package under `src/robotframework_accessibility_checker` is expected to contain modules such as:

- `keywords.py`
- `session_orchestrator.py`
- `state_bridge.py`
- `comparator.py`
- `reporter.py`
- `tools/axe_core.py`
- `tools/lighthouse.py`
- `tools/ibm_checker.py`

## Current Status

This repository currently contains architecture planning and compatibility analysis artifacts.
Implementation scaffolding is in progress.

## Next Steps

1. Add `pyproject.toml` and package metadata.
2. Create initial Python module files in `src/robotframework_accessibility_checker`.
3. Implement first bootstrap scripts in `scripts/`.
4. Add baseline unit tests and Robot examples.
