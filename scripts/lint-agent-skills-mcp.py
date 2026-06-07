#!/usr/bin/env python3
"""Validate this repository with the existing agent-skills-mcp scanner.

This is intentionally the external/spec-facing step. Repo-specific policy lives in
scripts/lint-skills.mjs.
"""
from pathlib import Path
import sys

from agent_skills_mcp.scan import scan_skills

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"

expected = sorted(SKILLS_ROOT.rglob("SKILL.md"))
scanned = list(scan_skills(SKILLS_ROOT))
scanned_paths = sorted(SKILLS_ROOT / item.relative_path for item in scanned)

errors: list[str] = []

if not expected:
    errors.append("no SKILL.md files found under skills/")

if len(scanned) != len(expected):
    errors.append(
        f"agent-skills-mcp scanned {len(scanned)} skills, expected {len(expected)}"
    )
    missing = sorted(set(expected) - set(scanned_paths))
    for path in missing:
        errors.append(f"not scanned: {path.relative_to(ROOT)}")

for skill in scanned:
    rel = Path("skills") / skill.relative_path
    if not skill.name:
        errors.append(f"{rel}: external scanner returned empty name")
    if not skill.description:
        errors.append(f"{rel}: external scanner returned empty description")
    if not skill.content.strip():
        errors.append(f"{rel}: external scanner returned empty content")

if errors:
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    raise SystemExit(1)

print(f"agent-skills-mcp scan ok ({len(scanned)} skills checked)")
