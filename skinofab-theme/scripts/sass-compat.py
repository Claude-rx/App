#!/usr/bin/env python3
"""
Post-process Tailwind CSS v4 output so generated CSS stays compatible with
the Next Commerce server-side Sass compiler.

Transforms:
- strip @property, @supports, and @layer wrappers
- convert oklch() color functions to hex equivalents
- replace known color-mix() patterns with pre-computed RGBA values
- rewrite logical properties, :is()/:where(), media range syntax, and
  scientific-notation lengths
- fail if unsupported generated CSS remains after the transform

Usage:
  python3 scripts/sass-compat.py assets/main.css
  python3 scripts/sass-compat.py --check assets/main.css
"""

import argparse
import re
import sys

# oklch color values used by Tailwind v4 slate palette → hex
# Computed from https://oklch.com/
OKLCH_TO_HEX = {
    "oklch(98.4% .003 247.858)": "#f8fafc",   # slate-50
    "oklch(96.8% .007 247.896)": "#f1f5f9",   # slate-100
    "oklch(92.9% .013 255.508)": "#e2e8f0",   # slate-200
    "oklch(86.9% .022 252.894)": "#cbd5e1",   # slate-300
    "oklch(70.4% .04 256.788)": "#94a3b8",    # slate-400
    "oklch(55.4% .046 257.417)": "#64748b",   # slate-500
    "oklch(44.6% .043 257.281)": "#475569",   # slate-600
    "oklch(37.2% .044 257.287)": "#334155",   # slate-700
    "oklch(27.9% .041 260.031)": "#1e293b",   # slate-800
    "oklch(20.8% .042 265.755)": "#0f172a",   # slate-900
}

# color-mix replacements
COLOR_MIX_REPLACEMENTS = {
    "color-mix(in oklab, var(--color-black) 20%, transparent)": "rgba(0,0,0,0.2)",
    "color-mix(in oklab, var(--color-black) 30%, transparent)": "rgba(0,0,0,0.3)",
    "color-mix(in oklab, var(--color-white) 70%, transparent)": "rgba(255,255,255,0.7)",
    "color-mix(in oklab, currentcolor 50%, transparent)": "rgba(128,128,128,0.5)",
}

SCIENTIFIC_NOTATION_LENGTH = re.compile(
    r'(\d+(?:\.\d+)?)e[+\-]?\d+px',
    re.IGNORECASE,
)

# Sass evaluates these names as its own colour functions, so anything sharing a
# name is parsed as a Sass call and its CSS argument is rejected. The two rules
# below differ in what the author should do about it: invert/saturate/grayscale/
# opacity are genuine CSS filter functions that need a non-colliding substitute,
# while lighten/darken/complement/desaturate are not CSS at all and mean Sass
# source reached the generated output.
#
# Custom-property declarations are exempt from both: Sass does not evaluate a
# custom property's value, which is why Tailwind's
# `--tw-grayscale: grayscale(100%)` compiles today. Scanned against
# custom-property-masked CSS for that reason.
BANNED_DECLARATION_PATTERNS = (
    (
        "sass-builtin-as-css-filter",
        re.compile(
            r'(?<![\w-])(?:invert|saturate|grayscale|opacity)\(',
            re.IGNORECASE,
        ),
        "This is a real CSS filter function, but Sass claims the same name as a "
        "built-in colour function, so the platform compiler evaluates it as a Sass "
        "call and the upload fails with 'Could not compile CSS. Please check Scss "
        "Syntax.' (`make css-check` passes locally, so it only surfaces at push "
        "time). Use a filter function Sass does not claim - brightness(), "
        "contrast(), blur(), sepia(), hue-rotate(), drop-shadow() - or assign the "
        "value through a custom property, whose value Sass leaves alone. For "
        "opacity() specifically, the `opacity` property is usually what you want.",
    ),
    (
        "sass-colour-function-in-css",
        re.compile(
            r'(?<![\w-])(?:lighten|darken|complement|desaturate)\(',
            re.IGNORECASE,
        ),
        "There is no CSS function by this name: it is a Sass colour function that "
        "reached the generated CSS, and the platform compiler will evaluate it and "
        "reject the argument. Emit the computed colour instead - a hex or rgba() "
        "literal, or a custom property the theme sets - rather than asking the "
        "platform's Sass pass to compute it.",
    ),
)

BANNED_GENERATED_PATTERNS = (
    (
        "@property",
        re.compile(r'@property\b'),
        "Houdini @property rules must be stripped before upload.",
    ),
    (
        "@supports",
        re.compile(r'@supports\b'),
        "Feature-query wrappers can fail the platform Sass compiler.",
    ),
    (
        "@layer",
        re.compile(r'@layer\b'),
        "Tailwind layer wrappers must be unwrapped before upload.",
    ),
    (
        "min()/max()/clamp()",
        re.compile(r'(?<![a-z-])(?:min|max|clamp)\(', re.IGNORECASE),
        "The platform Sass compiler evaluates CSS min()/max()/clamp() as Sass math and rejects mixed units (the upload fails with 'Could not compile CSS. Please check Scss Syntax.'). Use a fixed value plus max-width/min-width instead. minmax() grid tracks are fine.",
    ),
    (
        "oklch()",
        re.compile(r'oklch\(', re.IGNORECASE),
        "Convert OKLCH colors to hex or another legacy color format.",
    ),
    (
        "color-mix()",
        re.compile(r'color-mix\(', re.IGNORECASE),
        "Only known color-mix patterns are safe to convert.",
    ),
    (
        ":is()/:where()",
        re.compile(r':(?:is|where)\(', re.IGNORECASE),
        "Expand modern selector helpers before upload.",
    ),
    (
        "logical property",
        re.compile(
            r'\b(?:padding|margin|inset|border)-(?:inline|block)(?:-(?:start|end))?\s*:'
        ),
        "Use physical left/right/top/bottom properties in generated CSS.",
    ),
    (
        "inset shorthand",
        re.compile(r'\binset\s*:'),
        "Use explicit top/right/bottom/left declarations in generated CSS.",
    ),
    (
        "media range syntax",
        re.compile(r'\(\s*width\s*[<>]=?'),
        "Use min-width/max-width media queries.",
    ),
    (
        "scientific notation length",
        SCIENTIFIC_NOTATION_LENGTH,
        "Replace e-notation lengths with normal px values.",
    ),
)


def strip_at_property(css):
    """Remove @property blocks."""
    return re.sub(r'@property\s+--[\w-]+\s*\{[^}]*\}', '', css)


def oklch_to_hex(l, c, h):
    """Convert oklch values to hex color. Simplified conversion via OKLab intermediate."""
    import math
    # OKLab from oklch
    a = c * math.cos(math.radians(h))
    b_lab = c * math.sin(math.radians(h))

    # OKLab to linear sRGB
    l_ = l + 0.3963377774 * a + 0.2158037573 * b_lab
    m_ = l - 0.1055613458 * a - 0.0638541728 * b_lab
    s_ = l - 0.0894841775 * a - 1.2914855480 * b_lab

    l_3 = l_ * l_ * l_
    m_3 = m_ * m_ * m_
    s_3 = s_ * s_ * s_

    r_lin = 4.0767416621 * l_3 - 3.3077115913 * m_3 + 0.2309699292 * s_3
    g_lin = -1.2684380046 * l_3 + 2.6097574011 * m_3 - 0.3413193965 * s_3
    b_lin = -0.0041960863 * l_3 - 0.7034186147 * m_3 + 1.7076147010 * s_3

    def gamma(v):
        if v <= 0.0031308:
            return 12.92 * v
        return 1.055 * (v ** (1/2.4)) - 0.055

    r = max(0, min(1, gamma(r_lin)))
    g = max(0, min(1, gamma(g_lin)))
    b_val = max(0, min(1, gamma(b_lin)))

    return "#{:02x}{:02x}{:02x}".format(int(r * 255 + 0.5), int(g * 255 + 0.5), int(b_val * 255 + 0.5))


def replace_oklch(css):
    """Replace all oklch() values with hex — both mapped and computed."""
    # First try exact matches from our curated map
    for oklch, hex_val in OKLCH_TO_HEX.items():
        css = css.replace(oklch, hex_val)

    # Then convert any remaining oklch() values via computation
    def oklch_match_to_hex(m):
        try:
            parts = m.group(1).strip()
            # Handle oklch(.971 .013 17.38) format
            tokens = parts.replace(',', ' ').split()
            l_val = float(tokens[0].rstrip('%'))
            if '%' in tokens[0]:
                l_val = l_val / 100.0
            c_val = float(tokens[1])
            h_val = float(tokens[2]) if len(tokens) > 2 else 0
            return oklch_to_hex(l_val, c_val, h_val)
        except Exception:
            return m.group(0)  # Return original if conversion fails

    css = re.sub(r'oklch\(([^)]+)\)', oklch_match_to_hex, css)
    return css


def replace_color_mix(css):
    """Replace color-mix() with pre-computed values."""
    # First try exact matches
    for cm, replacement in COLOR_MIX_REPLACEMENTS.items():
        css = css.replace(cm, replacement)

    # Then regex replace remaining color-mix() — convert to rgba approximations
    # Handle nested parens: color-mix(in oklab,var(--color-black)20%,transparent)
    def color_mix_to_rgba(m):
        try:
            content = m.group(0)
            if 'transparent' in content:
                pct_match = re.search(r'(\d+)%', content)
                pct = int(pct_match.group(1)) / 100.0 if pct_match else 0.5
                if 'black' in content or 'currentColor' in content.lower() or 'currentcolor' in content:
                    return "rgba(0,0,0,{})".format(pct)
                elif 'white' in content:
                    return "rgba(255,255,255,{})".format(pct)
                else:
                    return "rgba(128,128,128,{})".format(pct)
            return content
        except Exception:
            return m.group(0)

    # Match color-mix( ... ) including nested parens from var()
    css = re.sub(r'color-mix\((?:[^()]*\([^()]*\))*[^()]*\)', color_mix_to_rgba, css)

    # Remove @supports blocks that wrap color-mix fallbacks
    css = re.sub(
        r'@supports\s*\(color:\s*color-mix\(in lab,\s*red,\s*red\)\)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',
        r'\1',
        css
    )
    return css


def strip_supports_hyphens(css):
    """
    Remove the @supports wrapper around CSS custom property fallbacks.
    These are Tailwind v4's browser compat wrappers that Sass can't parse.
    """
    css = re.sub(
        r'@supports\s*\(\(.*?\)\)\s*\{([\s\S]*?)\}(?=\})',
        r'\1',
        css,
        count=1
    )
    return css


def strip_at_rule_blocks(css, at_rule):
    """Remove complete at-rule blocks such as @supports {...}.

    Tailwind v4.2 emits feature-query wrappers that are valid browser CSS but
    can trip the platform Sass parser before the browser ever sees them.
    """
    result = []
    i = 0
    needle = at_rule
    while i < len(css):
        if css.startswith(needle, i):
            try:
                brace = css.index('{', i)
            except ValueError:
                break
            i = brace + 1
            depth = 1
            while i < len(css) and depth > 0:
                if css[i] == '{':
                    depth += 1
                elif css[i] == '}':
                    depth -= 1
                i += 1
        else:
            result.append(css[i])
            i += 1
    if i < len(css):
        result.append(css[i:])
    return ''.join(result)


def strip_at_layer(css):
    """Remove @layer wrappers — unwrap their contents.
    Sass can't parse @layer theme{...} or @layer base{...}.
    Uses brace counting to properly match opening/closing braces."""
    result = []
    i = 0
    while i < len(css):
        # Look for @layer keyword
        if css[i:i+6] == '@layer':
            # Find the opening brace
            j = css.index('{', i)
            # Skip the @layer ... { part
            i = j + 1
            # Track brace depth to find the matching closing brace
            depth = 1
            content_start = i
            while i < len(css) and depth > 0:
                if css[i] == '{':
                    depth += 1
                elif css[i] == '}':
                    depth -= 1
                i += 1
            # Append everything between the braces (excluding the final })
            result.append(css[content_start:i-1])
        else:
            result.append(css[i])
            i += 1
    return ''.join(result)


def replace_logical_properties(css):
    """Replace CSS logical properties with physical equivalents.
    padding-inline -> padding-left + padding-right
    padding-block -> padding-top + padding-bottom
    margin-inline -> margin-left + margin-right
    inset -> top/right/bottom/left
    """
    # padding-inline:X -> padding-left:X;padding-right:X
    css = re.sub(
        r'padding-inline:([^;}]+)',
        r'padding-left:\1;padding-right:\1',
        css
    )
    # padding-block:X -> padding-top:X;padding-bottom:X
    css = re.sub(
        r'padding-block:([^;}]+)',
        r'padding-top:\1;padding-bottom:\1',
        css
    )
    # margin-inline:X -> margin-left:X;margin-right:X
    css = re.sub(
        r'margin-inline:([^;}]+)',
        r'margin-left:\1;margin-right:\1',
        css
    )
    # margin-block:X -> margin-top:X;margin-bottom:X
    css = re.sub(
        r'margin-block:([^;}]+)',
        r'margin-top:\1;margin-bottom:\1',
        css
    )
    # border-inline:X -> border-left:X;border-right:X
    css = re.sub(
        r'border-inline:([^;}]+)',
        r'border-left:\1;border-right:\1',
        css
    )
    # border-block:X -> border-top:X;border-bottom:X
    css = re.sub(
        r'border-block:([^;}]+)',
        r'border-top:\1;border-bottom:\1',
        css
    )
    # inset:X -> top:X;right:X;bottom:X;left:X
    css = re.sub(
        r'inset:([^;}]+)',
        r'top:\1;right:\1;bottom:\1;left:\1',
        css
    )
    # padding-inline-start -> padding-left, padding-inline-end -> padding-right
    css = re.sub(r'padding-inline-start:', 'padding-left:', css)
    css = re.sub(r'padding-inline-end:', 'padding-right:', css)
    css = re.sub(r'padding-block-start:', 'padding-top:', css)
    css = re.sub(r'padding-block-end:', 'padding-bottom:', css)
    css = re.sub(r'margin-inline-start:', 'margin-left:', css)
    css = re.sub(r'margin-inline-end:', 'margin-right:', css)
    css = re.sub(r'margin-block-start:', 'margin-top:', css)
    css = re.sub(r'margin-block-end:', 'margin-bottom:', css)
    css = re.sub(r'inset-inline-start:', 'left:', css)
    css = re.sub(r'inset-inline-end:', 'right:', css)
    css = re.sub(r'inset-block-start:', 'top:', css)
    css = re.sub(r'inset-block-end:', 'bottom:', css)
    css = re.sub(r'border-inline-start:', 'border-left:', css)
    css = re.sub(r'border-inline-end:', 'border-right:', css)
    css = re.sub(r'border-block-start:', 'border-top:', css)
    css = re.sub(r'border-block-end:', 'border-bottom:', css)
    return css


def replace_is_where_selectors(css):
    """Replace :is() and :where() pseudo-selectors.
    Simple cases like :is(.foo) -> .foo
    For compound selectors, expand to comma-separated."""
    # :where(*) -> * (universal)
    css = css.replace(':where(*)', '*')
    # :is(.single-class) -> .single-class
    css = re.sub(r':is\(([^,)]+)\)', r'\1', css)
    css = re.sub(r':where\(([^,)]+)\)', r'\1', css)
    # :is([multiple],[size]) with comma -> [multiple],[size]
    # More general: :is(a,b) -> just use first selector as approximation
    css = re.sub(r':is\(([^)]+)\)', r'\1', css)
    css = re.sub(r':where\(([^)]+)\)', r'\1', css)
    return css


def fix_scientific_notation(css):
    """Replace scientific-notation lengths the platform's Sass parser rejects.

    Tailwind v4 can emit enormous e-notation values for utilities like
    ``rounded-full``. The platform's Sass compiler errors out on the exponent.
    Cap any e-notation length at 9999px, which behaves identically for
    border-radius purposes (any value > half the element's diagonal renders as
    a full pill).
    """
    return SCIENTIFIC_NOTATION_LENGTH.sub('9999px', css)


def replace_media_range_syntax(css):
    """Replace CSS Media Query Range Syntax with traditional syntax.
    (width>=768px)  -> (min-width:768px)
    (width<=768px)  -> (max-width:768px)
    (width>=768px) and (width<1024px) -> (min-width:768px) and (max-width:1023px)
    """
    # (width>=Xpx) -> (min-width:Xpx)
    css = re.sub(r'\(width\s*>=\s*(\d+(?:\.\d+)?)(px|em|rem)\)', r'(min-width:\1\2)', css)
    # (width>Xpx) -> (min-width:X+1px) - approximate
    css = re.sub(r'\(width\s*>\s*(\d+(?:\.\d+)?)(px|em|rem)\)', lambda m: '(min-width:{}{})'
                 .format(float(m.group(1)) + (1 if m.group(2) == 'px' else 0.001), m.group(2)), css)
    # (width<=Xpx) -> (max-width:Xpx)
    css = re.sub(r'\(width\s*<=\s*(\d+(?:\.\d+)?)(px|em|rem)\)', r'(max-width:\1\2)', css)
    # (width<Xpx) -> (max-width:X-1px) - approximate
    css = re.sub(r'\(width\s*<\s*(\d+(?:\.\d+)?)(px|em|rem)\)', lambda m: '(max-width:{}{})'
                 .format(float(m.group(1)) - (1 if m.group(2) == 'px' else 0.001), m.group(2)), css)
    return css


def transform_css(css):
    """Apply the known-safe Spark/Tailwind platform compatibility transforms."""
    css = replace_oklch(css)
    css = replace_color_mix(css)
    css = strip_at_property(css)
    css = strip_supports_hyphens(css)
    css = strip_at_rule_blocks(css, '@supports')
    css = strip_at_layer(css)
    css = replace_logical_properties(css)
    css = replace_is_where_selectors(css)
    css = replace_media_range_syntax(css)
    css = fix_scientific_notation(css)

    # Clean up empty lines
    css = re.sub(r'\n{3,}', '\n\n', css)
    return css


def line_number(css, offset):
    """Return a 1-based line number for a character offset."""
    return css.count('\n', 0, offset) + 1


def snippet_for(css, match):
    """Return a compact context snippet around a regex match."""
    start = max(0, match.start() - 48)
    end = min(len(css), match.end() + 96)
    snippet = re.sub(r'\s+', ' ', css[start:end]).strip()
    if start > 0:
        snippet = '...' + snippet
    if end < len(css):
        snippet += '...'
    return snippet


def mask_css_comments(css):
    """Replace comments with spaces so scanner offsets stay aligned."""
    return re.sub(r'/\*[\s\S]*?\*/', lambda m: ' ' * len(m.group(0)), css)


def mask_custom_property_values(css):
    """Blank out custom-property values, keeping offsets aligned.

    Sass does not evaluate a custom property's value, so a Sass built-in name
    inside one is not a compile hazard. Masking here keeps the declaration
    scanner from flagging Tailwind's own `--tw-*` filter variables.
    """
    return re.sub(
        r'(--[\w-]+\s*:)([^;}]*)',
        lambda m: m.group(1) + ' ' * len(m.group(2)),
        css,
    )


def find_unsupported_constructs(css):
    """Return generated CSS constructs the platform compiler is known to reject."""
    issues = []
    searchable_css = mask_css_comments(css)
    declaration_css = mask_custom_property_values(searchable_css)
    scans = (
        (BANNED_GENERATED_PATTERNS, searchable_css),
        (BANNED_DECLARATION_PATTERNS, declaration_css),
    )
    for patterns, scanned in scans:
        for name, pattern, guidance in patterns:
            for match in pattern.finditer(scanned):
                issues.append({
                    "name": name,
                    "line": line_number(css, match.start()),
                    "snippet": snippet_for(css, match),
                    "guidance": guidance,
                })
    issues.sort(key=lambda issue: issue["line"])
    return issues


def print_unsupported_constructs(path, issues):
    """Print clear failure messages for generated CSS compatibility issues."""
    print(
        "{} contains CSS that is unsafe for the platform compiler:".format(path),
        file=sys.stderr,
    )
    for issue in issues[:20]:
        print(
            "- line {line}: {name}: {snippet}".format(**issue),
            file=sys.stderr,
        )
        print("  {}".format(issue["guidance"]), file=sys.stderr)
    if len(issues) > 20:
        print(
            "- ...and {} more issue(s).".format(len(issues) - 20),
            file=sys.stderr,
        )
    print(
        "Fix the source CSS or add a known-safe sass-compat transform, then rerun `make css-check`.",
        file=sys.stderr,
    )


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Post-process or verify Spark generated CSS for platform compatibility."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="scan the CSS and fail if known unsupported generated constructs remain",
    )
    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="write transformed CSS even if unsupported constructs remain",
    )
    parser.add_argument("input_file")
    parser.add_argument("output_file", nargs="?")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])

    input_file = args.input_file
    output_file = args.output_file if args.output_file else input_file

    with open(input_file, 'r') as f:
        css = f.read()

    if args.check:
        issues = find_unsupported_constructs(css)
        if issues:
            print_unsupported_constructs(input_file, issues)
            return 1
        print("OK: {} contains no known unsupported CSS constructs.".format(input_file))
        return 0

    original_size = len(css)
    css = transform_css(css)

    issues = find_unsupported_constructs(css)
    if issues and not args.no_strict:
        print_unsupported_constructs(output_file, issues)
        print(
            "sass-compat refused to write CSS because an unsupported construct could not be safely converted.",
            file=sys.stderr,
        )
        return 1

    with open(output_file, 'w') as f:
        f.write(css)

    final_size = len(css)
    print(f"Processed {input_file}: {original_size} → {final_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
