#!/usr/bin/env python3
"""
Scaffold and validate a repo-wide AGENTS.md mesh.

- Creates missing per-directory AGENTS.md files with front-matter.
- Validates front-matter keys and parent/children links.

Usage:
  python scripts/scaffold_agents.py --write     # create missing guides
  python scripts/scaffold_agents.py --validate  # validate existing guides
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEMPLATE = """---
agent_map:
  path: {path}
  parent: {parent}
  children:{children}
  owners: []
  status: "wip"
  contracts:
    - "Docs here must stay in sync with code in this directory."
version: 2
---

# Directory Guide — {dirname}

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
- Parent: {parent}
- Children:{children_list}

## Maintenance
- When and how to update this guide.
"""

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def find_code_dirs(root: Path) -> list[Path]:
    code_dirs = []
    for p, dirs, files in os.walk(root):
        p = Path(p)
        if any(part.startswith(".") for part in p.parts):
            continue
        if p.name in {"books", "__pycache__", "tests", "scripts", ".github"}:
            # still allow AGENTS in tests/scripts if desired; skip auto-create
            pass
        # Consider a code dir if it has .py files or is a known top-level area
        has_py = any(f.endswith(".py") for f in files)
        if has_py and p != root:
            code_dirs.append(p)
    return sorted(code_dirs)


def fm_children(dir_path: Path) -> list[str]:
    children = []
    for child in sorted(dir_path.iterdir()):
        if child.is_dir() and not child.name.startswith('.') and child.name != "__pycache__":
            rel = child.relative_to(dir_path)
            children.append(f"./{rel.as_posix()}/AGENTS.md")
    return children


def write_agents_md(dir_path: Path) -> None:
    rel = dir_path.relative_to(ROOT)
    parent = "../AGENTS.md" if dir_path != ROOT else ""
    children = fm_children(dir_path)
    children_yaml = "\n" + "\n".join(f"    - ./{c}" for c in children) if children else " []"
    children_list = "\n" + "\n".join(f"- ./{c}" for c in children) if children else " (none)"
    content = TEMPLATE.format(
        path=f"./{rel.as_posix()}/" if rel.as_posix() != "." else "./",
        parent=parent or "(root)",
        children=children_yaml,
        children_list=children_list,
        dirname=rel.name if rel.name != "." else "root",
    )
    target = "AGENTS.MD" if dir_path == ROOT else "AGENTS.md"
    (dir_path / target).write_text(content, encoding="utf-8")


def parse_front_matter(text: str) -> dict | None:
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return None
    fm = m.group(1)
    # minimal key presence checks without YAML dependency
    required = ["agent_map:", "path:", "parent:", "children:", "status:", "version:"]
    for key in required:
        if key not in fm:
            return None
    return {}


def validate_agents_md(dir_path: Path) -> list[str]:
    errors = []
    f = dir_path / ("AGENTS.MD" if dir_path == ROOT else "AGENTS.md")
    if not f.exists():
        errors.append(f"Missing: {f}")
        return errors
    text = f.read_text(encoding="utf-8", errors="ignore")
    if parse_front_matter(text) is None:
        errors.append(f"Invalid front-matter: {f}")
    # check parent link for non-root
    if dir_path != ROOT:
        if "parent: ../AGENTS.md" not in text and "parent: (root)" not in text:
            errors.append(f"Parent link incorrect: {f}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Create missing AGENTS.md files")
    ap.add_argument("--validate", action="store_true", help="Validate existing AGENTS.md files")
    args = ap.parse_args()

    if not args.write and not args.validate:
        ap.print_help()
        return 1

    code_dirs = [ROOT] + find_code_dirs(ROOT)

    if args.write:
        for d in code_dirs:
            f = d / "AGENTS.md"
            if not f.exists():
                write_agents_md(d)

    if args.validate:
        all_errors: list[str] = []
        for d in code_dirs:
            all_errors.extend(validate_agents_md(d))
        if all_errors:
            for e in all_errors:
                print(e)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
