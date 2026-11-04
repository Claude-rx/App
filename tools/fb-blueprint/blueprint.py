#!/usr/bin/env python3
"""CLI for the Facebook Ads Blueprint decision engine.

    python3 tools/fb-blueprint/blueprint.py <command> [--input file.json]

Reads a JSON object of keyword arguments (file or stdin) and prints the
decision as JSON. Commands map 1:1 to engine functions:

    python3 tools/fb-blueprint/blueprint.py list
    echo '{"monthly_spend": 45000}' | python3 tools/fb-blueprint/blueprint.py ads_per_week

Stdlib only; no network. See docs/media-buying/SOP.md for the rules.
"""

from __future__ import annotations

import argparse
import inspect
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import engine  # noqa: E402

COMMANDS = {
    name: fn for name, fn in inspect.getmembers(engine, inspect.isfunction)
    if fn.__module__ == "engine" and not name.startswith("_")
}


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", help="engine function name, or 'list' / 'rules'")
    ap.add_argument("--input", help="JSON file with keyword arguments (default: stdin)")
    args = ap.parse_args(argv)

    if args.command == "list":
        for name, fn in sorted(COMMANDS.items()):
            sig = inspect.signature(fn)
            doc = (fn.__doc__ or "").strip().splitlines()[0]
            print(f"{name}{sig}\n    {doc}")
        return 0
    if args.command == "rules":
        print(json.dumps(engine.R, indent=2))
        return 0
    fn = COMMANDS.get(args.command)
    if fn is None:
        print(f"unknown command {args.command!r}; run 'list'", file=sys.stderr)
        return 2
    raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
    kwargs = json.loads(raw) if raw.strip() else {}
    try:
        result = fn(**kwargs)
    except TypeError as exc:
        print(f"bad arguments for {args.command}: {exc}\nsignature: {inspect.signature(fn)}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
