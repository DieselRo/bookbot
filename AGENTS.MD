---
agent_map:
  path: ./
  parent: (root)
  children:
    - ./bookbot/AGENTS.md
    
    - ./scripts/AGENTS.md
    - ./tests/AGENTS.md
  owners: []
  status: "wip"
  contracts:
    - "Docs here must stay in sync with code in this directory."
version: 2
---

# Directory Guide — 

## Purpose
Fill in a short purpose for this directory.

## Contents & Layout
- List key files and subdirectories with one-line descriptions.

## Entry Points & APIs
- Public interfaces and expected inputs/outputs.

## Rules (Local Conventions)
- Constraints or conventions specific to this directory.

## Invariants & Tests
- What must hold (determinism, ordering, schemas), and test pointers.

## Links (Navigation)
- Parent: (root)
- Children:
- ./bookbot/AGENTS.md

- ./scripts/AGENTS.md
- ./tests/AGENTS.md

## Maintenance
- When and how to update this guide.


## Schemas & Golden Tests
- JSON payload schemas live in `bookbot/formats.py`.
- Golden JSON fixtures live under `tests/golden/` and are validated by `tests/test_golden.py`.
 - All JSON payloads include `report_version` (current: 1). Bump on breaking changes.
 - To update goldens intentionally, require an explicit `UPDATE_GOLDENS=1` step in PR notes.
