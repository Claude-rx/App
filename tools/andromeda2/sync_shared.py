#!/usr/bin/env python3
"""Copy the shared Andromeda 2 layer into every andromeda2-* skill.

Each skill must be self-contained (it is installed and packaged on its own), so the shared references and a2.py live in
every skill as byte-identical copies of the masters in tools/andromeda2/shared/. Edit the masters, then run:

    python3 tools/andromeda2/sync_shared.py          # write the copies
    python3 tools/andromeda2/sync_shared.py --check  # exit 1 if any copy is missing or stale (used by CI)
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARED = ROOT / "tools" / "andromeda2" / "shared"
SKILLS = ROOT / ".claude" / "skills"

# master (relative to SHARED) -> destination (relative to the skill dir)
FILES = {
    "references/andromeda2-doctrine.md": "references/andromeda2-doctrine.md",
    "references/psychology-toolkit.md": "references/psychology-toolkit.md",
    "references/metrics-and-diagnosis.md": "references/metrics-and-diagnosis.md",
    "scripts/a2.py": "scripts/a2.py",
}


def skill_dirs() -> list[Path]:
    return sorted(p for p in SKILLS.glob("andromeda2-*") if (p / "SKILL.md").is_file())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="verify only; exit 1 on drift")
    args = ap.parse_args()
    dirs = skill_dirs()
    if not dirs:
        print("no andromeda2-* skills found", file=sys.stderr)
        return 1
    stale: list[str] = []
    for skill in dirs:
        for src_rel, dst_rel in FILES.items():
            src, dst = SHARED / src_rel, skill / dst_rel
            if dst.is_file() and dst.read_bytes() == src.read_bytes():
                continue
            if args.check:
                stale.append(str(dst.relative_to(ROOT)))
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            if dst.suffix == ".py":
                dst.chmod(0o755)
            print(f"synced {dst.relative_to(ROOT)}")
    if stale:
        print("stale or missing shared copies (run tools/andromeda2/sync_shared.py):", file=sys.stderr)
        for s in stale:
            print(f"  {s}", file=sys.stderr)
        return 1
    if args.check:
        print(f"ok: {len(dirs)} skills x {len(FILES)} shared files in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
