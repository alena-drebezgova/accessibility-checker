# Browser Library Integration

This section documents how the project uses Browser Library at runtime.

Browser Library is the runtime source of truth for the active page, browser context, and session state.

Source: [robotframework-browser](https://github.com/MarketSquare/robotframework-browser)

This page is written for Robot Framework teams that already control their browser through Browser Library and want accessibility checks to reuse that same state.

## Topics

- Accessing active page and context
- Reading and preserving session state
- Snapshot contract for tool adapters
- Checkpoint-based execution model

## What the integration must preserve

1. The active page must stay the same between the test action and the accessibility checkpoint.
2. Authentication state must remain intact across checkpoints.
3. Cookies, local storage, and session storage must be read from the same browser context.
4. Each tool adapter must receive the same BrowserSnapshot input.

## Snapshot contract

The Browser Library layer should provide a structured snapshot with at least:

- checkpoint_name
- url
- page_handle
- context_handle
- cookies
- local_storage
- session_storage
- timestamp

## Execution model

1. Robot test performs an interaction step.
2. Session Orchestrator asks the Browser Library bridge for the current snapshot.
3. Tool adapters receive that snapshot and run against the same live state.
4. Comparator merges results into the standards report.

## Why this folder exists separately from tools

Tools answer what was found.
Integration answers where the tool should run and which live browser state it must reuse.
