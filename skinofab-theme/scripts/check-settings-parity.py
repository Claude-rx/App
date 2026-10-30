#!/usr/bin/env python3
"""Validate exact settings parity and value types for the Spark theme."""

import argparse
import json
import math
import sys
from pathlib import Path


STRING_TYPES = {
    "text",
    "textarea",
    "html",
    "css",
    "richtext",
    "url",
    "image_picker",
    "color",
    "menu",
}
LIST_TYPES = {"products", "product_categories"}
# Picker-backed settings use null to represent no selection. The committed
# data uses this for product settings; image_picker has the same unset model.
NULLABLE_TYPES = {"product", "product_category", "image_picker"}
REQUIRED_MENUS = ("main_menu", "footer_menu")
OPTION_TYPES = {"select", "radio"}
NUMBER_TYPES = {"number", "range"}
SUPPORTED_TYPES = (
    STRING_TYPES
    | LIST_TYPES
    | OPTION_TYPES
    | NUMBER_TYPES
    | {"checkbox", "product", "product_category"}
)


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_optional_names(path):
    names = set()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            name = line.split("#", 1)[0].strip()
            if name:
                names.add(name)
    return names


def flatten_schema(schema):
    settings = {}
    violations = []
    if not isinstance(schema, dict):
        return settings, ["[schema-shape] schema root must be an object"]

    for group_name, group in schema.items():
        if not isinstance(group, dict):
            violations.append(
                f"[schema-shape] group {group_name!r} must be an object"
            )
            continue
        for subgroup_name, entries in group.items():
            location = f"{group_name}/{subgroup_name}"
            if not isinstance(entries, list):
                violations.append(
                    f"[schema-shape] subgroup {location!r} must be a list"
                )
                continue
            for index, setting in enumerate(entries):
                if not isinstance(setting, dict):
                    violations.append(
                        f"[schema-shape] {location}[{index}] must be an object"
                    )
                    continue
                name = setting.get("name")
                setting_type = setting.get("type")
                if not isinstance(name, str) or not name:
                    violations.append(
                        f"[schema-shape] {location}[{index}] has no valid name"
                    )
                    continue
                if not isinstance(setting_type, str) or not setting_type:
                    violations.append(
                        f"[schema-shape] setting {name!r} has no valid type"
                    )
                    continue
                if name in settings:
                    violations.append(
                        f"[schema-shape] duplicate setting name {name!r}"
                    )
                    continue
                settings[name] = setting
    return settings, violations


def option_values(setting):
    values = []
    options = setting.get("options", [])
    if not isinstance(options, list):
        return values
    for option in options:
        if isinstance(option, dict) and "value" in option:
            values.append(option["value"])
    return values


def is_finite_number(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    return not isinstance(value, float) or math.isfinite(value)


def validate_schema_setting(name, setting):
    violations = []
    setting_type = setting["type"]

    if setting_type not in SUPPORTED_TYPES:
        violations.append(
            f"[schema-type] {name!r}: unsupported schema type "
            f"{setting_type!r}"
        )

    if setting_type in OPTION_TYPES:
        options = setting.get("options")
        if not isinstance(options, list) or not options:
            violations.append(
                f"[schema-options] {name!r}: options must be a non-empty "
                "list"
            )
        else:
            if any(
                not isinstance(option, dict)
                or not isinstance(option.get("name"), str)
                or "value" not in option
                for option in options
            ):
                violations.append(
                    f"[schema-options] {name!r}: each option must be an "
                    "object with a string 'name' and a 'value' key"
                )

            seen_values = []
            duplicate_values = []
            for option in options:
                if not isinstance(option, dict) or "value" not in option:
                    continue
                value = option["value"]
                if value in seen_values:
                    if value not in duplicate_values:
                        duplicate_values.append(value)
                else:
                    seen_values.append(value)
            if duplicate_values:
                violations.append(
                    f"[schema-options] {name!r}: option values must be "
                    f"unique; duplicates: {duplicate_values!r}"
                )

    if setting_type == "range":
        valid_bounds = {}
        for bound_name in ("min", "max"):
            bound = setting.get(bound_name)
            if not is_finite_number(bound):
                violations.append(
                    f"[schema-range] {name!r}: {bound_name} must be a "
                    "finite number"
                )
                continue
            valid_bounds[bound_name] = bound

        if (
            "min" in valid_bounds
            and "max" in valid_bounds
            and valid_bounds["min"] >= valid_bounds["max"]
        ):
            violations.append(
                f"[schema-range] {name!r}: min must be less than max"
            )

        step = setting.get("step")
        if not is_finite_number(step) or step <= 0:
            violations.append(
                f"[schema-range] {name!r}: step must be a positive "
                "finite number"
            )

    if setting_type == "number":
        valid_bounds = {}
        for bound_name in ("min", "max"):
            if bound_name not in setting:
                continue
            bound = setting[bound_name]
            if not is_finite_number(bound):
                violations.append(
                    f"[schema-range] {name!r}: {bound_name} must be a "
                    "finite number"
                )
                continue
            valid_bounds[bound_name] = bound

        if (
            "min" in valid_bounds
            and "max" in valid_bounds
            and valid_bounds["min"] > valid_bounds["max"]
        ):
            violations.append(
                f"[schema-range] {name!r}: min must not exceed max"
            )

    return violations


def validate_value(setting, value):
    setting_type = setting["type"]

    if value is None:
        if setting_type in NULLABLE_TYPES:
            return None
        return f"null is not valid for type {setting_type!r}"

    if setting_type == "checkbox":
        if type(value) is bool:
            return None
        return f"expected bool, got {type(value).__name__}"

    if setting_type in NUMBER_TYPES:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return f"expected int or float, got {type(value).__name__}"
        if not is_finite_number(value):
            return f"expected a finite number, got {value!r}"

        minimum = setting.get("min")
        if is_finite_number(minimum) and value < minimum:
            return f"value {value!r} is below minimum {minimum!r}"

        maximum = setting.get("max")
        if is_finite_number(maximum) and value > maximum:
            return f"value {value!r} exceeds maximum {maximum!r}"

        return None

    if setting_type in STRING_TYPES:
        if isinstance(value, str):
            return None
        return f"expected str, got {type(value).__name__}"

    if setting_type in {"product", "product_category"}:
        if isinstance(value, str):
            return None
        if isinstance(value, int) and not isinstance(value, bool):
            return None
        return f"expected str, int, or null, got {type(value).__name__}"

    if setting_type in LIST_TYPES:
        if isinstance(value, list):
            return None
        return f"expected list, got {type(value).__name__}"

    if setting_type == "select" and setting.get("multi-select") is True:
        if not isinstance(value, list):
            return f"expected list, got {type(value).__name__}"
        allowed = option_values(setting)
        invalid = [item for item in value if item not in allowed]
        if invalid:
            return (
                f"values {invalid!r} are not in allowed options "
                f"{allowed!r}"
            )
        return None

    if setting_type in {"select", "radio"}:
        allowed = option_values(setting)
        if value == "" or value in allowed:
            return None
        return f"value {value!r} is not in allowed options {allowed!r}"

    return f"unsupported schema type {setting_type!r}"


def validate_settings(schema, data, optional_names):
    settings, violations = flatten_schema(schema)

    for name in sorted(settings):
        setting = settings[name]
        violations.extend(validate_schema_setting(name, setting))
        if setting["type"] in SUPPORTED_TYPES and "default" in setting:
            error = validate_value(setting, setting["default"])
            if error:
                violations.append(f"[default] {name!r}: {error}")

    if not isinstance(data, dict):
        violations.append("[data-shape] settings data root must be an object")
        return settings, violations

    schema_names = set(settings)
    data_names = set(data)

    for name in sorted(data_names - schema_names):
        violations.append(
            f"[data-key] {name!r} exists in data but not in schema"
        )

    for name in sorted(schema_names - data_names - optional_names):
        violations.append(
            f"[schema-key] {name!r} is missing from settings data"
        )

    for name in REQUIRED_MENUS:
        value = data.get(name)
        if not isinstance(value, str) or not value.strip():
            violations.append(
                f"[required-menu] {name!r} must be present as a non-empty string"
            )

    for name in sorted(schema_names & data_names):
        setting = settings[name]
        if setting["type"] not in SUPPORTED_TYPES:
            continue
        error = validate_value(setting, data[name])
        if error:
            violations.append(f"[type] {name!r}: {error}")

    return settings, violations


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Check settings schema/data parity and value types."
    )
    parser.add_argument("--schema", default="configs/settings_schema.json")
    parser.add_argument("--data", default="configs/settings_data.json")
    parser.add_argument("--optional", default="configs/settings_optional.txt")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        schema = load_json(Path(args.schema))
        data = load_json(Path(args.data))
        optional_names = load_optional_names(Path(args.optional))
    except (OSError, json.JSONDecodeError) as error:
        print(f"Settings parity gate failed: {error}", file=sys.stderr)
        return 1

    settings, violations = validate_settings(schema, data, optional_names)
    if violations:
        print(
            f"Settings parity gate failed with {len(violations)} violation(s):",
            file=sys.stderr,
        )
        for violation in violations:
            print(f"- {violation}", file=sys.stderr)
        return 1

    print(
        "Settings parity gate passed: "
        f"{len(data)} data values match {len(settings)} schema settings."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
