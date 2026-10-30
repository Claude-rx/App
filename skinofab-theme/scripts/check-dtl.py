#!/usr/bin/env python3
"""Parse every theme template with Django's template compiler.

The platform renders themes with Django 4.2. It rejects a template with a
syntax error at upload, but only one file per push, and a broken tag inside
a rarely visited template can sit unnoticed until a shopper reaches it. This
gate compiles every ``.html`` file under ``layouts/``, ``templates/`` and
``partials/`` the way the platform would, without rendering anything, and
reports every error with its file and line.

Compiling checks what Django checks at parse time:

- block structure (an unclosed ``{% if %}``, a stray ``{% endfor %}``,
  ``{% extends %}`` not first);
- unknown tags and filters, including a ``{% load %}`` of a library the
  platform does not have;
- filter argument counts, and positional and keyword arguments of
  platform simple tags such as ``{% purchase_info_for_product %}``.

It does not resolve ``{% include %}``/``{% extends %}`` targets or URL names;
``scripts/check-templates.py`` covers those.

Django's own tags and filters are the real ones. Platform tags and filters
come from ``scripts/platform-template-builtins.json``, an inventory of every
library the platform loads into the theme engine, with each simple tag's
signature and each filter's argument arity. The stubs accept exactly what
the platform's definitions accept and render nothing. When the platform adds
a tag or filter, add it to that file.

Django is an optional dev dependency (``pip install "django==4.2.*"``).
Without it the gate prints a skip notice and exits 0, unless ``--require``
is passed, which CI does. Another Django version fails the gate unless
``--any-django`` is passed, because parse rules differ between versions.
"""

import argparse
import json
import sys
import traceback
import types
from pathlib import Path


TEMPLATE_DIRECTORIES = ("layouts", "templates", "partials")
BUILTINS_FILE = Path(__file__).with_name("platform-template-builtins.json")
STUB_MODULE = "spark_dtl_platform_stubs"
DJANGO_LIBRARIES = {
    # Django libraries the platform engine loads as builtins.
    "i18n": "django.templatetags.i18n",
    "l10n": "django.templatetags.l10n",
    "static": "django.templatetags.static",
    "humanize": "django.contrib.humanize.templatetags.humanize",
}


def load_inventory(path=BUILTINS_FILE):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _simple_tag_source(name, spec):
    """Python source for a no-op function with the platform tag's signature."""
    params = []
    if spec.get("takes_context"):
        params.append("context")
    for param in spec.get("params", []):
        params.append(f"{param[:-1]}=None" if param.endswith("=") else param)
    if spec.get("varargs"):
        params.append("*args")
    kwonly = spec.get("kwonly", [])
    if kwonly and not spec.get("varargs"):
        params.append("*")
    for param in kwonly:
        params.append(f"{param[:-1]}=None" if param.endswith("=") else param)
    if spec.get("varkw"):
        params.append("**kwargs")
    for param in params:
        bare = param.lstrip("*").split("=")[0]
        if not bare.isidentifier():
            raise ValueError(f"tag {name!r}: bad parameter {param!r}")
    return f"def stub({', '.join(params)}):\n    return ''\n"


def build_stub_library(inventory):
    from django import template

    register = template.Library()

    class StubNode(template.Node):
        def render(self, context):
            return ""

    for name, spec in inventory["tags"].items():
        kind = spec["kind"]
        if kind == "simple":
            namespace = {}
            exec(_simple_tag_source(name, spec), namespace)
            register.simple_tag(
                namespace["stub"], name=name, takes_context=spec.get("takes_context", False)
            )
        elif kind == "block":
            until = tuple(spec["parse_until"])

            def compile_block(parser, token, until=until):
                parser.parse(until)
                parser.delete_first_token()
                return StubNode()

            register.tag(name, compile_block)
        elif kind == "tag":
            register.tag(name, lambda parser, token: StubNode())
        else:
            raise ValueError(f"tag {name!r}: unknown kind {kind!r}")

    for name, spec in inventory["filters"].items():
        arg = spec["arg"]
        if arg == "none":
            func = lambda value: value
        elif arg == "required":
            func = lambda value, arg: value
        elif arg == "optional":
            func = lambda value, arg=None: value
        else:
            raise ValueError(f"filter {name!r}: unknown arg {arg!r}")
        register.filter(name, func)
    return register


def build_engine(inventory):
    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            INSTALLED_APPS=["django.contrib.humanize"],
            USE_I18N=True,
            TEMPLATES=[],
        )
        django.setup()
    from django.template import Engine

    module = types.ModuleType(STUB_MODULE)
    module.register = build_stub_library(inventory)
    sys.modules[STUB_MODULE] = module

    libraries = dict(DJANGO_LIBRARIES)
    for spec in list(inventory["tags"].values()) + list(inventory["filters"].values()):
        libraries[spec["library"]] = STUB_MODULE
    return Engine(
        debug=True,
        builtins=list(DJANGO_LIBRARIES.values()) + [STUB_MODULE],
        libraries=libraries,
    )


def template_files(root):
    for directory in TEMPLATE_DIRECTORIES:
        base = root / directory
        if base.is_dir():
            yield from sorted(base.rglob("*.html"))


def check(root, engine):
    from django.template import TemplateSyntaxError

    failures = []
    files = list(template_files(root))
    for path in files:
        relative = path.relative_to(root).as_posix()
        source = path.read_text(encoding="utf-8")
        try:
            engine.from_string(source)
        except TemplateSyntaxError as error:
            line = getattr(error, "template_debug", {}).get("line", "?")
            failures.append(f"{relative}:{line}: {error}")
        except Exception as error:  # report it and keep checking the other files
            if not any(":?: " in failure for failure in failures):
                # Usually a broken inventory stub, which repeats in every file:
                # show the first traceback so the entry can be found.
                traceback.print_exc()
            failures.append(f"{relative}:?: {type(error).__name__}: {error}")
    return files, failures


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1], type=Path)
    parser.add_argument(
        "--any-django",
        action="store_true",
        help="run with a Django version other than 4.2 (results may differ from the platform)",
    )
    parser.add_argument(
        "--require",
        action="store_true",
        help="fail instead of skipping when Django is not installed",
    )
    args = parser.parse_args(argv)

    try:
        import django
    except ImportError:
        message = 'Django is not installed; skipping the DTL parse gate (install uv, or pip install "django==4.2.*").'
        if args.require:
            print(f"check-dtl: {message}", file=sys.stderr)
            return 1
        print(f"check-dtl: {message}")
        return 0
    if django.VERSION[:2] != (4, 2) and not args.any_django:
        print(
            f"check-dtl: Django {django.get_version()} is installed but the platform runs 4.2, "
            'so results could differ. Install "django==4.2.*" or pass --any-django.',
            file=sys.stderr,
        )
        return 1

    try:
        inventory = load_inventory()
    except (OSError, ValueError) as error:
        print(f"check-dtl: cannot read {BUILTINS_FILE.name}: {error}", file=sys.stderr)
        return 1
    engine = build_engine(inventory)
    files, failures = check(args.root.resolve(), engine)
    if failures:
        print(f"check-dtl: {len(failures)} of {len(files)} templates failed to parse:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"check-dtl: {len(files)} templates parse cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
