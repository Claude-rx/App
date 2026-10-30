#!/usr/bin/env python3
"""Check literal template includes and URL names against reviewed inventory.

The same pass enforces the template contract rules that otherwise live only
in prose and get re-introduced by the next contributor:

- ``settings.*`` is never a filter argument (``|default:settings.foo``). The
  platform raises a 500 on every route as soon as the setting has a value.
- ``{% firstof ... as X %}`` yields a string, so ``X`` can never select an
  object for ``{% purchase_info_for_product %}``.
- Storefront routes come from ``{% url %}`` or ``get_absolute_url``; a
  hardcoded route in ``href``/``action`` breaks the moment the store's
  route prefix differs. The gate flags the platform roots (``/catalogue/``,
  ``/cart/``, ``/checkout/`` and the rest of ``PLATFORM_ROUTE_ROOTS``) and
  the foreign reflexes ported templates carry (``/products/``,
  ``/collections/``, ``/account/``), which 404 here.
"""

import argparse
import re
import sys
from pathlib import Path


TEMPLATE_DIRECTORIES = ("layouts", "templates", "partials")
TAG_RE = re.compile(r"{%\s*(include|url)\b(?P<body>.*?)%}", re.DOTALL)
BARE_CART_PRODUCT_PK_RE = re.compile(
    r"(?:^|\s)pk\s*=\s*product\.pk(?=\s|$)"
)
LITERAL_RE = re.compile(
    r"""\s*(?P<quote>['"])(?P<value>(?:(?!(?P=quote)).)*)(?P=quote)(?:\s|$)""",
    re.DOTALL,
)
# Django's unescape_string_literal handles ONLY \\ and the escaped DELIMITING
# quote (\" inside "...", \' inside '...') of a template string literal. Every
# other backslash sequence reaches the filter as two literal characters:
# split:"\n" splits on backslash-n, never on a newline, and split:"\'" splits
# on backslash-apostrophe. The platform renders such a template without error,
# so the defect is silent until real settings data flows through the filter.
DTL_EXPRESSION_RE = re.compile(r"{{.*?}}|{%.*?%}", re.DOTALL)
# The value pattern consumes any backslash escape as a unit, so an escaped
# quote (\" or \') inside the argument cannot cut the capture short and hide
# a later escape from the gate.
FILTER_ARGUMENT_RE = re.compile(
    r"\|\s*(?P<filter>\w+)\s*:\s*"
    r"(?P<quote>['\"])(?P<value>(?:\\.|(?!(?P=quote))[^\\])*)(?P=quote)",
    re.DOTALL,
)
# settings.* as a filter ARGUMENT (the value after the colon). settings.foo
# on the left of the pipe is fine; the platform resolves it. On the right it
# raises a 500 on every route once the setting is populated.
SETTINGS_FILTER_ARGUMENT_RE = re.compile(
    r"\|\s*(?P<filter>\w+)\s*:\s*settings\.(?P<setting>[\w.]+)"
)
# A quoted string literal inside an expression is never evaluated, so
# "settings." inside one is text, not a lookup. Blanked to same-length spaces
# before matching so offsets (and therefore line numbers) stay intact.
STRING_LITERAL_RE = re.compile(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"")
# The body must not cross %}: a firstof with no "as" clause would otherwise
# swallow the next tag and claim its assignment.
FIRSTOF_AS_RE = re.compile(
    r"{%\s*firstof\b(?P<body>(?:(?!%}).)*?)\s+as\s+(?P<name>\w+)\s*%}",
    re.DOTALL,
)
# Tags that rebind a name to an object again: {% with x=obj %} / {% with obj
# as x %} and {% for x in ... %}. A rebinding shadows the firstof string
# until the matching end tag.
WITH_RE = re.compile(r"{%\s*with\b(?P<body>(?:(?!%}).)*?)%}", re.DOTALL)
ENDWITH_RE = re.compile(r"{%\s*endwith\s*%}")
FOR_RE = re.compile(r"{%\s*for\s+(?P<names>[\w,\s]+?)\s+in\b(?:(?!%}).)*?%}", re.DOTALL)
ENDFOR_RE = re.compile(r"{%\s*endfor\s*%}")
WITH_BINDING_RE = re.compile(r"(?P<kw>\w+)\s*=|\bas\s+(?P<as>\w+)")
PURCHASE_INFO_RE = re.compile(
    r"{%\s*purchase_info_for_product\s+(?P<request>[\w.]+)\s+"
    r"(?P<product>[\w.]+)"
)
# A literal storefront route inside an href/action attribute. Routes must come
# from {% url %} or get_absolute_url so the platform's prefix and slugs apply.
# PLATFORM_ROUTE_ROOTS are the roots every storefront URL name resolves under
# (developer docs, "URLs and template paths"): products and categories both
# live under /catalogue/, accounts under /accounts/. FOREIGN_ROUTE_REFLEXES
# are roots other platforms use that a ported template carries over; on this
# platform they 404, so a literal one is wrong twice.
PLATFORM_ROUTE_ROOTS = (
    "catalogue", "cart", "checkout", "blog", "search", "support", "accounts",
)
FOREIGN_ROUTE_REFLEXES = ("products", "collections", "account")
STOREFRONT_ROUTE_PREFIXES = PLATFORM_ROUTE_ROOTS + FOREIGN_ROUTE_REFLEXES
# Only a local absolute path counts: the value starts with the route root.
# An external URL that happens to contain /products/ is not a storefront route.
HARDCODED_ROUTE_RE = re.compile(
    r"""\b(?P<attribute>href|action)\s*=\s*(?P<quote>['"])"""
    r"""(?P<value>/(?:""" + "|".join(STOREFRONT_ROUTE_PREFIXES)
    + r""")/[^'"]*)(?P=quote)""",
    re.IGNORECASE,
)
INLINE_COMMENT_RE = re.compile(r"{#[^\r\n]*?#}")
BLOCK_COMMENT_RE = re.compile(
    r"{%\s*comment(?:\s+.*?)?\s*%}.*?{%\s*endcomment\s*%}",
    re.DOTALL,
)
VERBATIM_BLOCK_RE = re.compile(
    r"{%\s*verbatim(?:\s+.*?)?\s*%}.*?"
    r"{%\s*endverbatim(?:\s+.*?)?\s*%}",
    re.DOTALL,
)
BLOCK_TAG_RE = re.compile(
    r"{%\s*(?P<tag>endblock|block)\b(?:\s+(?P<name>[\w-]+))?[^%]*%}"
)
REQUIRED_BASE_BLOCKS = {
    "announcement_bar",
    "nav_header",
    "content_wrapper",
    "footer",
    "side_cart",
    "pixels",
    "custom_css",
    "platform_compatibility",
    "preview_indicator",
    "delight_scripts",
    "footer_app_hooks",
    "tracking",
}


def mask_match(match):
    return "".join("\n" if char == "\n" else " " for char in match.group(0))


def mask_comments(text):
    # Django tokenizes inline comments before interpreting block tags. Masking
    # them first prevents comment/endcomment text inside {# ... #} from
    # changing the extent of a real block comment.
    text = INLINE_COMMENT_RE.sub(mask_match, text)
    return BLOCK_COMMENT_RE.sub(mask_match, text)


def mask_ignored_regions(text):
    return VERBATIM_BLOCK_RE.sub(mask_match, mask_comments(text))


def inspect_block_structure(text):
    block_names = set()
    stack = []
    errors = []

    for match in BLOCK_TAG_RE.finditer(text):
        tag_name = match.group("tag")
        block_name = match.group("name")
        line_number = text.count("\n", 0, match.start()) + 1

        if tag_name == "block":
            if not block_name:
                errors.append(f"block on line {line_number} has no name")
                continue
            if block_name in block_names:
                errors.append(
                    f"duplicate block {block_name!r} on line {line_number}"
                )
            block_names.add(block_name)
            stack.append((block_name, line_number))
            continue

        if not stack:
            errors.append(f"endblock on line {line_number} has no opening block")
            continue

        expected_name, opening_line = stack.pop()
        if block_name and block_name != expected_name:
            errors.append(
                f"block {expected_name!r} opened on line {opening_line} "
                f"closes as {block_name!r} on line {line_number}"
            )

    for block_name, opening_line in stack:
        errors.append(
            f"block {block_name!r} opened on line {opening_line} is unclosed"
        )

    return block_names, errors


def unsupported_escape(value, quote):
    """Return the first backslash sequence Django will not unescape, if any.

    Django only unescapes ``\\\\`` and the backslash-escaped delimiting quote,
    so ``\\'`` inside a double-quoted literal is NOT unescaped.
    """
    index = 0
    while index < len(value) - 1:
        if value[index] == "\\":
            following = value[index + 1]
            if following == "\\" or following == quote:
                index += 2
                continue
            return "\\" + following
        index += 1
    return None


def inspect_filter_arguments(masked, relative_path):
    violations = []
    for expression in DTL_EXPRESSION_RE.finditer(masked):
        for match in FILTER_ARGUMENT_RE.finditer(expression.group(0)):
            escape = unsupported_escape(match.group("value"), match.group("quote"))
            if escape is None:
                continue
            offset = expression.start() + match.start()
            line_number = masked.count("\n", 0, offset) + 1
            filter_name = match.group("filter")
            advice = (
                ' Split on newlines with |linebreaksbr|split:"<br>".'
                if escape == "\\n" and filter_name == "split"
                else ""
            )
            violations.append(
                f"[escape-in-filter-argument] {relative_path}:{line_number}: "
                f"{filter_name}:\"{escape}\" - Django template string literals "
                "unescape only \\\\ and the escaped delimiting quote, so the "
                "filter receives the two "
                f"literal characters {escape!r}.{advice}"
            )
    return violations


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def blank_string_literals(text):
    return STRING_LITERAL_RE.sub(lambda m: " " * len(m.group(0)), text)


def inspect_settings_filter_arguments(masked, relative_path):
    violations = []
    for expression in DTL_EXPRESSION_RE.finditer(masked):
        body = blank_string_literals(expression.group(0))
        for match in SETTINGS_FILTER_ARGUMENT_RE.finditer(body):
            line_number = line_of(masked, expression.start() + match.start())
            violations.append(
                f"[settings-filter-argument] {relative_path}:{line_number}: "
                f"{match.group('filter')}:settings.{match.group('setting')} - "
                "settings.* must never be a filter argument; the platform "
                "raises a 500 on every route once the setting has a value. "
                "Bind it first ({% with x=settings.name %}) and use "
                "{% firstof %} or {% if %} on the bound name."
            )
    return violations


def inspect_firstof_object_selection(masked, relative_path):
    """Flag a firstof-selected name later handed to purchase_info_for_product.

    {% firstof a b as x %} always stores a STRING, so x can only ever be a
    scalar such as a PK. Passing it where the tag expects a product object
    renders nothing useful and raises no error. Dot-access on the target
    (x.children.first) is the same defect: a string has no attributes.

    The scan walks the file in order. Only calls after the firstof are
    flagged, and a {% with x=obj %} / {% with obj as x %} / {% for x in %}
    that rebinds the name shadows the string until its end tag, so the
    recommended remedy (rebind the object, then call) passes.

    Scope is one file at a time. A firstof-bound name that reaches another
    template through {% include ... with %} is not traced; keep the firstof
    and the purchase_info_for_product call in the same file, or select the
    object with {% with %}/{% if %} at the call site.
    """
    events = []
    for match in FIRSTOF_AS_RE.finditer(masked):
        events.append((match.start(), "firstof", {match.group("name")}))
    for match in WITH_RE.finditer(masked):
        names = set()
        # A quoted default such as 'use /search as a fallback' must not read
        # as an "as fallback" binding; blank literals first.
        for binding in WITH_BINDING_RE.finditer(
            blank_string_literals(match.group("body"))
        ):
            names.add(binding.group("kw") or binding.group("as"))
        events.append((match.start(), "open", names))
    for match in ENDWITH_RE.finditer(masked):
        events.append((match.start(), "close", set()))
    for match in FOR_RE.finditer(masked):
        names = {n.strip() for n in match.group("names").split(",") if n.strip()}
        events.append((match.start(), "open", names))
    for match in ENDFOR_RE.finditer(masked):
        events.append((match.start(), "close", set()))
    for match in PURCHASE_INFO_RE.finditer(masked):
        events.append((match.start(), "call", match))
    if not any(kind == "firstof" for _, kind, _ in events):
        return []
    events.sort(key=lambda event: event[0])

    firstof_lines = {}
    shadow_stack = []
    violations = []
    for offset, kind, payload in events:
        if kind == "firstof":
            for name in payload:
                firstof_lines[name] = line_of(masked, offset)
        elif kind == "open":
            shadow_stack.append(payload)
        elif kind == "close":
            if shadow_stack:
                shadow_stack.pop()
        else:
            match = payload
            root_name = match.group("product").split(".", 1)[0]
            if root_name not in firstof_lines:
                continue
            if any(root_name in names for names in shadow_stack):
                continue
            line_number = line_of(masked, offset)
            violations.append(
                f"[firstof-object] {relative_path}:{line_number}: "
                f"purchase_info_for_product receives {match.group('product')!r}, "
                f"but {root_name!r} comes from {{% firstof ... as {root_name} %}} "
                f"on line {firstof_lines[root_name]} and firstof always yields "
                "a string, never an object. Select the product with "
                "{% with %}/{% if %} and reserve firstof for PKs. (This check "
                "is per file; names passed through {% include %} are not traced.)"
            )
    return violations


def inspect_hardcoded_routes(masked, relative_path):
    violations = []
    for match in HARDCODED_ROUTE_RE.finditer(masked):
        line_number = line_of(masked, match.start())
        violations.append(
            f"[hardcoded-route] {relative_path}:{line_number}: "
            f"{match.group('attribute')}={match.group('quote')}"
            f"{match.group('value')}{match.group('quote')} - storefront "
            "routes must come from {% url %} or get_absolute_url, never a "
            "literal /" + "/, /".join(STOREFRONT_ROUTE_PREFIXES) + "/ path."
        )
    return violations


def load_allowlist(path):
    names = set()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            name = line.split("#", 1)[0].strip()
            if name:
                names.add(name)
    return names


def template_paths(root):
    paths = []
    for directory in TEMPLATE_DIRECTORIES:
        paths.extend((root / directory).rglob("*.html"))
    return sorted(set(paths))


def missing_default_inventory(root, paths):
    missing = []
    base_template = root / "layouts" / "base.html"
    if not base_template.is_file():
        missing.append("required template layouts/base.html")
    else:
        try:
            base_text = mask_ignored_regions(base_template.read_text(encoding="utf-8"))
            base_blocks, _ = inspect_block_structure(base_text)
            for block_name in sorted(REQUIRED_BASE_BLOCKS - base_blocks):
                missing.append(f"overridable base block {block_name!r}")
        except OSError as error:
            missing.append(f"readable layouts/base.html ({error})")

    for directory in TEMPLATE_DIRECTORIES:
        directory_root = root / directory
        if not any(
            path.is_file() and path.is_relative_to(directory_root)
            for path in paths
        ):
            missing.append(f"at least one .html file under {directory}/")

    return missing


def inspect_templates(root, allowlist):
    violations = []
    skipped_includes = 0
    skipped_urls = 0
    paths = template_paths(root)
    resolved_root = root.resolve()

    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as error:
            violations.append(f"[read] {path}: {error}")
            continue

        masked = mask_ignored_regions(text)
        relative_path = path.relative_to(root)
        _, block_errors = inspect_block_structure(masked)
        for error in block_errors:
            violations.append(f"[block-structure] {relative_path}: {error}")

        violations.extend(inspect_filter_arguments(masked, relative_path))
        violations.extend(
            inspect_settings_filter_arguments(masked, relative_path)
        )
        violations.extend(
            inspect_firstof_object_selection(masked, relative_path)
        )
        violations.extend(inspect_hardcoded_routes(masked, relative_path))

        for match in TAG_RE.finditer(masked):
            tag_name = match.group(1)
            body = match.group("body")
            literal = LITERAL_RE.match(body)
            line_number = masked.count("\n", 0, match.start()) + 1
            location = f"{relative_path}:{line_number}"

            if not body.strip():
                argument_name = "target" if tag_name == "include" else "URL name"
                violations.append(
                    f"[{tag_name}] {location}: tag has no {argument_name} argument"
                )
                continue

            if tag_name == "include":
                if literal is None:
                    skipped_includes += 1
                    continue
                target = literal.group("value")
                target_path = Path(target)
                try:
                    resolved_target = (resolved_root / target_path).resolve()
                except (OSError, RuntimeError, ValueError) as error:
                    violations.append(
                        f"[path-escape] {location}: include target {target!r} "
                        f"could not be resolved safely: {error}"
                    )
                    continue
                if (
                    target_path.is_absolute()
                    or ".." in target_path.parts
                    or not resolved_target.is_relative_to(resolved_root)
                ):
                    violations.append(
                        f"[path-escape] {location}: include target {target!r} "
                        "must resolve inside the template root"
                    )
                elif not resolved_target.is_file():
                    violations.append(
                        f"[include] {location}: target {target!r} does not exist"
                    )
                continue

            if literal is None:
                skipped_urls += 1
                continue

            url_name = literal.group("value")
            if url_name not in allowlist:
                violations.append(
                    f"[url-name] {location}: {url_name!r} is not in "
                    "the reviewed allowlist"
                )
                continue
            if (
                url_name == "cart:add"
                and BARE_CART_PRODUCT_PK_RE.search(body)
            ):
                violations.append(
                    f"[cart-product-id] {location}: cart:add must resolve "
                    "a purchasable child PK before falling back to product.pk"
                )

    return paths, skipped_includes, skipped_urls, violations


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Lint template includes and literal URL names."
    )
    parser.add_argument("--root")
    parser.add_argument(
        "--allowlist",
        default="scripts/url-name-allowlist.txt",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    default_scan = args.root is None
    root = Path(".") if default_scan else Path(args.root)
    try:
        allowlist = load_allowlist(Path(args.allowlist))
    except OSError as error:
        print(f"Template integrity gate failed: {error}", file=sys.stderr)
        return 1

    paths, skipped_includes, skipped_urls, violations = inspect_templates(
        root, allowlist
    )

    if default_scan:
        missing = missing_default_inventory(root, paths)
        if missing:
            print(
                "Template integrity gate failed: default template inventory "
                "is incomplete:",
                file=sys.stderr,
            )
            for requirement in missing:
                print(f"- {requirement}", file=sys.stderr)
            return 1

    if not paths:
        directories = ", ".join(TEMPLATE_DIRECTORIES)
        print(
            "Template integrity gate failed: no template files were found "
            f"under the scanned directories ({directories}).",
            file=sys.stderr,
        )
        return 1

    print(
        "INFO: skipped "
        f"{skipped_includes} include tag(s); skipped {skipped_urls} url tag(s) "
        "with non-literal arguments."
    )

    if violations:
        print(
            f"Template integrity gate failed with {len(violations)} "
            "violation(s):",
            file=sys.stderr,
        )
        for violation in violations:
            print(f"- {violation}", file=sys.stderr)
        return 1

    print(
        "Template integrity gate passed: "
        f"checked {len(paths)} template file(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
