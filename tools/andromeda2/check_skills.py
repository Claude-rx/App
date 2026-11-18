#!/usr/bin/env python3
"""Validate the andromeda2-* skill suite.

Checks, per skill:
  - SKILL.md has YAML frontmatter with `name` (== directory name, kebab-case) and `description` (<= 1024 chars, no < >)
  - SKILL.md body stays under 500 lines
  - every `references/...` and `scripts/...` path mentioned in SKILL.md exists in the skill
  - sibling skills named in SKILL.md (andromeda2-xxx) exist
  - shared copies are in sync with tools/andromeda2/shared (via sync_shared --check)
  - eval cases (evals/<case>/) have prompt.md with a settings block, case.yaml with schema_version/name, >= 1 grader file
  - reference files over 300 lines have a "Contents" section

Run: python3 tools/andromeda2/check_skills.py   (exit 1 on any problem)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".claude" / "skills"
EXPECTED = [
    "andromeda2-core", "andromeda2-ad-copy", "andromeda2-video-scripts", "andromeda2-static-ads",
    "andromeda2-launch-testing", "andromeda2-scaling", "andromeda2-hard-scaling", "andromeda2-zombie-campaigns",
    "andromeda2-creative-iteration",
]


def yaml_problem(block: str) -> str | None:
    """Return a YAML error for the frontmatter block, or None. Uses PyYAML when installed; otherwise flags the
    mistakes that break real YAML parsers in one-line plain scalars (': ' or ' #' inside an unquoted value)."""
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None
    if yaml is not None:
        try:
            data = yaml.safe_load(block)
        except yaml.YAMLError as exc:
            return str(exc).splitlines()[0]
        return None if isinstance(data, dict) else "frontmatter is not a mapping"
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s+(.*)$", line)
        if not m:
            continue
        val = m.group(2)
        if val[:1] in "\"'|>":
            continue
        if ": " in val or " #" in val:
            return f"unquoted value of '{m.group(1)}' contains ': ' or ' #' (invalid YAML plain scalar)"
    return None


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    block, body = text[4:end], text[end + 4:]
    fm: dict[str, str] = {}
    key = None
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            fm[key] = m.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            fm[key] += " " + line.strip()
    for k, v in fm.items():
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            fm[k] = v[1:-1]
    return fm, body


def check_skill(d: Path) -> list[str]:
    errs: list[str] = []
    rel = d.relative_to(ROOT)
    skill_md = d / "SKILL.md"
    if not skill_md.is_file():
        return [f"{rel}: missing SKILL.md"]
    text = skill_md.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if text.startswith("---\n") and text.find("\n---", 4) != -1:
        problem = yaml_problem(text[4:text.find("\n---", 4)])
        if problem:
            errs.append(f"{rel}: invalid YAML frontmatter: {problem}")
    name, desc = fm.get("name", ""), fm.get("description", "")
    if name != d.name:
        errs.append(f"{rel}: frontmatter name {name!r} != directory {d.name!r}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name or "-"):
        errs.append(f"{rel}: name must be kebab-case")
    if not desc:
        errs.append(f"{rel}: missing description")
    elif len(desc) > 1024:
        errs.append(f"{rel}: description is {len(desc)} chars (max 1024)")
    if "<" in desc or ">" in desc:
        errs.append(f"{rel}: description must not contain angle brackets")
    n_lines = body.count("\n")
    if n_lines > 500:
        errs.append(f"{rel}: SKILL.md body is {n_lines} lines (keep under 500)")
    for ref in sorted(set(re.findall(r"`((?:references|scripts)/[A-Za-z0-9_.\-/]+)`", text))):
        if not (d / ref).exists():
            errs.append(f"{rel}: SKILL.md points to {ref} which does not exist")
    for sib in sorted(set(re.findall(r"\bandromeda2-[a-z-]*[a-z](?![a-z-]|\.md)", text))):
        if not (SKILLS / sib / "SKILL.md").is_file():
            errs.append(f"{rel}: mentions sibling skill {sib} which does not exist")
    for ref_file in sorted((d / "references").glob("*.md")):
        lines = ref_file.read_text(encoding="utf-8").splitlines()
        if len(lines) > 300 and not any(l.strip().lower().startswith(("contents", "## contents", "**contents")) for l in lines[:40]):
            errs.append(f"{ref_file.relative_to(ROOT)}: {len(lines)} lines and no Contents section near the top")
    evals = d / "evals"
    if evals.is_dir():
        for case in sorted(p for p in evals.iterdir() if p.is_dir() and p.name not in ("results", "files")):
            crel = case.relative_to(ROOT)
            pm = case / "prompt.md"
            if not pm.is_file() or not pm.read_text(encoding="utf-8").startswith("---\n"):
                errs.append(f"{crel}: prompt.md missing or has no settings block")
            cy = case / "case.yaml"
            if not cy.is_file():
                errs.append(f"{crel}: missing case.yaml")
            else:
                c = cy.read_text(encoding="utf-8")
                if 'schema_version: "1.1"' not in c or f"name: {case.name}" not in c:
                    errs.append(f"{crel}: case.yaml needs schema_version \"1.1\" and name: {case.name}")
            graders = list((case / "graders").glob("*.md")) if (case / "graders").is_dir() else []
            if not graders:
                errs.append(f"{crel}: no graders/*.md")
            for g in graders:
                if not g.read_text(encoding="utf-8").startswith("---\ntype:"):
                    errs.append(f"{g.relative_to(ROOT)}: grader needs the type/focus/weight header")
    return errs


def main() -> int:
    errs: list[str] = []
    for name in EXPECTED:
        d = SKILLS / name
        if not d.is_dir():
            errs.append(f".claude/skills/{name}: missing skill")
            continue
        errs.extend(check_skill(d))
    extra = sorted(p.name for p in SKILLS.glob("andromeda2-*") if p.name not in EXPECTED)
    for e in extra:
        errs.append(f".claude/skills/{e}: unexpected andromeda2-* directory (add it to EXPECTED or remove it)")
    sync = subprocess.run([sys.executable, "-I", str(ROOT / "tools/andromeda2/sync_shared.py"), "--check"],
                          capture_output=True, text=True)
    if sync.returncode != 0:
        errs.append(sync.stderr.strip() or "shared copies out of sync")
    if errs:
        print("andromeda2 skill check FAILED:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"ok: {len(EXPECTED)} andromeda2 skills valid; {sync.stdout.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
