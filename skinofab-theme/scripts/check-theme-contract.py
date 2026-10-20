#!/usr/bin/env python3
"""Assert a theme still carries the integration points Spark declares.

Spark-derived store themes never update from this repo, so a fix that lands
here does not reach them. The failures this gate targets are silent: the
storefront renders, the dashboard shows the app installed and enabled, and only
the events go missing. Nothing surfaces it until someone looks.

Two modes:

    check-theme-contract.py                       # a working copy, before push
    check-theme-contract.py --store ... --theme-id N   # a live theme, after it

The remote mode is the one that matters. A store carries several theme copies,
and republishing an old one silently undoes a patch applied to the active theme.

Every requirement carries a scope. `fleet` binds every Spark-derived theme and
is what the live check enforces by default; `spark` binds Spark's own working
copy only, because derived themes are forks that may carry the same hook in a
different file. Local mode checks both by default (it is Spark's CI gate);
`--scope` overrides either default. A live check of Spark's own copy (a dev
store, not a fork) therefore needs `--scope spark` to run the same rules the
working-copy check did.
"""

import argparse
import importlib.util
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


CONTRACT_FILENAME = "theme-contract.json"
# The contract ships with Spark, beside this script. A derived theme being
# checked does not carry one, and in remote mode there is no local theme at all.
DEFAULT_CONTRACT = Path(__file__).resolve().parents[1] / CONTRACT_FILENAME
TEMPLATE_DIRECTORIES = ("layouts", "templates", "partials")
REQUEST_TIMEOUT = 30
# A fleet requirement binds every Spark-derived theme; a spark requirement binds
# only Spark's own working copy. Nothing else is a valid scope, and a requirement
# without one is a load error rather than a silent default.
SCOPE_FLEET = "fleet"
SCOPE_SPARK = "spark"
SCOPES = (SCOPE_FLEET, SCOPE_SPARK)
# Plain http is accepted only for a store on this machine, which is what a local
# stub or dev server looks like; anything reached over a network needs https.
LOOPBACK_HOSTS = ("localhost", "127.0.0.1", "::1")


def load_masking():
    """Reuse check-templates.py's comment masking rather than restating it.

    The module name has a hyphen, so it cannot be imported normally. Masking
    matters here: a required tag sitting inside {# ... #} is commented out and
    must not satisfy the contract.
    """
    path = Path(__file__).with_name("check-templates.py")
    spec = importlib.util.spec_from_file_location("spark_check_templates", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.mask_ignored_regions


def load_contract(path):
    with open(path, encoding="utf-8") as handle:
        contract = json.load(handle)

    requirements = contract.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        raise ValueError(f"{path}: 'requirements' must be a non-empty list")

    for requirement in requirements:
        for field in ("id", "file", "must_contain", "why", "scope"):
            if not requirement.get(field):
                raise ValueError(
                    f"{path}: requirement {requirement.get('id', '?')!r} "
                    f"is missing {field!r}"
                )
        if requirement["scope"] not in SCOPES:
            raise ValueError(
                f"{path}: requirement {requirement['id']!r} has scope "
                f"{requirement['scope']!r}; expected one of {', '.join(SCOPES)}"
            )

    return contract


def select_requirements(contract, scope):
    """Return the requirements a check at `scope` enforces.

    `fleet` keeps only fleet requirements. `spark` keeps everything: Spark's own
    copy must satisfy the fleet rules too, since it is what the fleet derives from.
    """
    if scope not in SCOPES:
        raise ValueError(f"unknown scope {scope!r}; expected one of {', '.join(SCOPES)}")
    if scope == SCOPE_SPARK:
        return list(contract["requirements"])
    return [r for r in contract["requirements"] if r["scope"] == SCOPE_FLEET]


def block_override_re(block_name):
    # A child template may override the block and drop the tag inside it. The
    # tag is then present in the base layout and absent from every rendered
    # page, so the text search alone would pass a broken theme.
    return re.compile(
        r"{%\s*block\s+" + re.escape(block_name) + r"\s*%}"
        r"(?P<body>.*?)"
        r"{%\s*endblock(?:\s+" + re.escape(block_name) + r")?\s*%}",
        re.DOTALL,
    )


def check_sources(sources, requirements, mask):
    """Check {path: text} against the requirements. Returns a list of failures."""
    failures = []

    for requirement in requirements:
        target = requirement["file"]
        needle = requirement["must_contain"]
        text = sources.get(target)

        if text is None:
            failures.append(
                (requirement, f"{target} is missing from the theme")
            )
            continue

        if needle not in mask(text):
            failures.append(
                (requirement, f"{target} does not contain {needle}")
            )
            continue

        block_name = requirement.get("block")
        if not block_name:
            continue

        pattern = block_override_re(block_name)
        for path, other in sorted(sources.items()):
            if path == target:
                continue
            for match in pattern.finditer(mask(other)):
                if needle not in match.group("body"):
                    failures.append(
                        (
                            requirement,
                            f"{display_path(path)} overrides block {block_name!r} without "
                            f"{needle}, which removes it from every page that "
                            "template renders",
                        )
                    )

    return failures


def read_local_sources(root):
    sources = {}
    for directory in TEMPLATE_DIRECTORIES:
        for path in sorted((root / directory).rglob("*.html")):
            if path.is_file():
                key = path.relative_to(root).as_posix()
                sources[key] = path.read_text(encoding="utf-8")
    return sources


def store_url_problem(store):
    """Return why `store` is not an acceptable store URL, or None if it is."""
    try:
        parsed = urllib.parse.urlsplit(store)
        # Reading .port is the validation: urllib raises ValueError for a
        # non-numeric or out-of-range port and splits them silently otherwise.
        # test_malformed_store_url_is_refused_without_a_traceback pins this.
        parsed.port
    except ValueError as error:
        return f"--store is not a valid URL ({error}): {store!r}"
    if not parsed.hostname:
        return f"--store must be a full URL such as https://x.29next.store, got {store!r}"
    if parsed.scheme == "https":
        return None
    if parsed.scheme == "http" and parsed.hostname in LOOPBACK_HOSTS:
        return None
    return f"--store must use https://, got {store!r}"


class RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """Treat any redirect as an error instead of following it.

    The templates endpoint answers directly, so a redirect means the store URL
    is wrong (an old domain, a missing path segment). It is reported for the
    caller to correct rather than followed to a location the caller never named.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(
            req.full_url, code, f"redirected to {newurl}; not following", headers, fp
        )


def read_remote_sources(store, theme_id, apikey):
    """Fetch a live theme's templates from the store admin API.

    The API's ?name= filter is ignored and returns the whole list, so the
    filtering happens here. The endpoint returns every template in one
    unpaginated list; a paginated response would mean only part of the theme
    was read, so it is refused rather than checked as if it were complete.

    The caller validates `store` with store_url_problem() first.
    """
    url = f"{store.rstrip('/')}/api/admin/themes/{theme_id}/templates/"
    request = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {apikey}"}
    )
    opener = urllib.request.build_opener(RefuseRedirects)

    with opener.open(request, timeout=REQUEST_TIMEOUT) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if isinstance(payload, dict):
        if payload.get("next"):
            raise ValueError(
                "the templates endpoint returned a paginated response, so only "
                "part of the theme would be checked"
            )
        entries = payload.get("results")
    else:
        entries = payload
    if not isinstance(entries, list):
        raise ValueError("the templates endpoint did not return a list")

    sources = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        content = entry.get("content")
        if isinstance(name, str) and name.endswith(".html") and isinstance(content, str):
            sources[name] = content
    return sources


def display_path(path):
    """Show a template path on one line.

    Remote template names come from the store, not from this repository. A name
    containing a newline or other control character is shown quoted and escaped,
    so it cannot start a line of its own in the report.
    """
    return path if path.isprintable() else repr(path)


def report(failures, subject, scope, checked, total):
    applied = f"{scope} scope, {checked} of {total} requirement(s)"
    if not failures:
        print(f"Theme contract gate passed: {subject} ({applied}).")
        return 0

    print(
        f"Theme contract gate failed for {subject} ({applied}) "
        f"with {len(failures)} violation(s):",
        file=sys.stderr,
    )
    for requirement, detail in failures:
        print(f"\n- [{requirement['id']}] {detail}", file=sys.stderr)
        print(f"  Why it matters: {requirement['why']}", file=sys.stderr)
        since = requirement.get("since")
        if since:
            print(f"  Required since Spark {since}.", file=sys.stderr)
        verify = requirement.get("verify_on_storefront")
        if verify:
            print(
                "  Confirm on the published storefront (never the Theme "
                f"Editor preview): {verify}",
                file=sys.stderr,
            )
    return 1


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", default=".", help="theme directory to check (default: .)"
    )
    parser.add_argument(
        "--contract",
        default=None,
        help=f"contract file (default: Spark's own {CONTRACT_FILENAME})",
    )
    parser.add_argument("--store", help="store URL, e.g. https://x.29next.store")
    parser.add_argument("--theme-id", help="theme id to check on that store")
    parser.add_argument(
        "--apikey",
        default=os.environ.get("NTK_APIKEY"),
        help="store API key (default: $NTK_APIKEY)",
    )
    parser.add_argument(
        "--scope",
        choices=SCOPES,
        default=None,
        help=(
            "which requirements to enforce: 'fleet' (every Spark-derived theme) "
            "or 'spark' (Spark's own copy: fleet rules plus its runtime hooks). "
            "Default: 'fleet' for a live theme, 'spark' for a working copy."
        ),
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    root = Path(args.root)
    contract_path = Path(args.contract) if args.contract else DEFAULT_CONTRACT

    try:
        contract = load_contract(contract_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Theme contract gate failed: {error}", file=sys.stderr)
        return 1

    remote = bool(args.store or args.theme_id)
    # A live theme is a derived copy unless the caller says otherwise, so the
    # live default is the fleet scope; the working-copy default is Spark's own
    # gate. `--scope` overrides either way.
    scope = args.scope or (SCOPE_FLEET if remote else SCOPE_SPARK)
    requirements = select_requirements(contract, scope)
    if not requirements:
        print(
            f"Theme contract gate failed: no requirement carries scope "
            f"{scope!r}, so nothing would be checked.",
            file=sys.stderr,
        )
        return 1
    if remote:
        if not (args.store and args.theme_id and args.apikey):
            print(
                "Theme contract gate failed: --store, --theme-id and an API "
                "key (--apikey or $NTK_APIKEY) are all required to check a "
                "live theme.",
                file=sys.stderr,
            )
            return 1
        problem = store_url_problem(args.store)
        if problem:
            print(f"Theme contract gate failed: {problem}", file=sys.stderr)
            return 1
        try:
            sources = read_remote_sources(args.store, args.theme_id, args.apikey)
        except (urllib.error.URLError, ValueError, OSError) as error:
            print(
                f"Theme contract gate failed: could not read theme "
                f"{args.theme_id} from {args.store} ({error})",
                file=sys.stderr,
            )
            return 1
        subject = f"theme {args.theme_id} on {args.store}"
    else:
        try:
            sources = read_local_sources(root)
        except OSError as error:
            print(f"Theme contract gate failed: {error}", file=sys.stderr)
            return 1
        subject = f"{len(sources)} template file(s) under {root}"

    if not sources:
        print(
            "Theme contract gate failed: no template files were found, so "
            "nothing was actually checked.",
            file=sys.stderr,
        )
        return 1

    return report(
        check_sources(sources, requirements, load_masking()),
        subject,
        scope,
        len(requirements),
        len(contract["requirements"]),
    )


if __name__ == "__main__":
    sys.exit(main())
