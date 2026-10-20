#!/usr/bin/env python3
"""Fail when generated CSS differs from the committed CSS artifact."""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


SASS_COMPAT = Path(__file__).resolve().with_name("sass-compat.py")
CONTEXT_BYTES = 32


def first_difference(expected, actual):
    """Return the first differing byte offset, including an end-of-file drift."""
    common_length = min(len(expected), len(actual))
    for index in range(common_length):
        if expected[index] != actual[index]:
            return index
    if len(expected) != len(actual):
        return common_length
    return None


def format_difference(expected, actual, offset):
    """Format a compact byte-level view around the first difference."""
    start = max(0, offset - CONTEXT_BYTES)
    end = min(max(len(expected), len(actual)), offset + CONTEXT_BYTES)
    return "\n".join(
        (
            f"First difference at byte {offset}:",
            f"  committed[{start}:{end}]: {expected[start:end]!r}",
            f"  candidate[{start}:{end}]: {actual[start:end]!r}",
        )
    )


def run_command(command, label):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        print(f"CSS drift gate failed: could not run {label}: {error}", file=sys.stderr)
        return False

    if result.returncode == 0:
        return True

    print(
        f"CSS drift gate failed: {label} exited with status "
        f"{result.returncode}.",
        file=sys.stderr,
    )
    if result.stdout:
        print(result.stdout.rstrip(), file=sys.stderr)
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    return False


def compile_candidate(input_path, tailwind_path, output_path):
    """Run the repository CSS pipeline and write only to temporary files."""
    raw_path = output_path.with_name("tailwind-raw.css")
    tailwind_command = [
        tailwind_path,
        "-i",
        str(input_path),
        "-o",
        str(raw_path),
        "--minify",
    ]
    if not run_command(tailwind_command, "Tailwind compilation"):
        return False

    compat_command = [
        sys.executable,
        str(SASS_COMPAT),
        str(raw_path),
        str(output_path),
    ]
    return run_command(compat_command, "Sass compatibility processing")


def check_drift(committed_path, candidate_path):
    """Compare post-sass-compat bytes and print a deterministic diagnostic."""
    try:
        committed = committed_path.read_bytes()
        candidate = candidate_path.read_bytes()
    except OSError as error:
        print(f"CSS drift gate failed: could not read CSS: {error}", file=sys.stderr)
        return 1

    offset = first_difference(committed, candidate)
    if offset is None:
        print(
            "CSS drift gate passed: candidate matches committed CSS "
            f"({len(committed)} bytes)."
        )
        return 0

    print(
        "CSS drift gate failed: generated CSS differs from the committed "
        "assets/main.css artifact.",
        file=sys.stderr,
    )
    print(f"Committed bytes: {len(committed)}", file=sys.stderr)
    print(f"Candidate bytes: {len(candidate)}", file=sys.stderr)
    print(format_difference(committed, candidate, offset), file=sys.stderr)
    return 1


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Compile and post-process CSS, then byte-compare it with the "
            "committed artifact."
        )
    )
    parser.add_argument("--input", default="css/input.css")
    parser.add_argument("--committed", default="assets/main.css")
    parser.add_argument("--tailwind", default="./tailwindcss")
    parser.add_argument(
        "--candidate",
        help=(
            "Use an already post-processed candidate file and skip Tailwind "
            "and sass-compat. Intended for deterministic comparison tests."
        ),
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    committed_path = Path(args.committed)

    if args.candidate:
        return check_drift(committed_path, Path(args.candidate))

    with tempfile.TemporaryDirectory(prefix="spark-css-drift-") as temp_dir:
        candidate_path = Path(temp_dir) / "candidate.css"
        if not compile_candidate(
            Path(args.input),
            args.tailwind,
            candidate_path,
        ):
            return 1
        return check_drift(committed_path, candidate_path)


if __name__ == "__main__":
    sys.exit(main())
