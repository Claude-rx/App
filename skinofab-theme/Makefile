# Spark Theme — Development Commands

# Tailwind CSS standalone CLI (gitignored, run `make install-tailwind` to fetch)
TAILWIND = ./tailwindcss
COMPAT = python3 scripts/sass-compat.py
TAILWIND_VERSION = v4.2.2
CSS_INPUT = css/input.css

.PHONY: dev build css css-drift css-check contract dtl verify-theme test watch push release install-tailwind

# Run both Tailwind watcher and ntk watcher in parallel
dev:
	@echo "Starting Spark development..."
	@echo "  Tailwind: $(CSS_INPUT) -> assets/main.css"
	@echo "  ntk: watching for changes -> pushing to store"
	@$(TAILWIND) -i "$(CSS_INPUT)" -o assets/main.css --watch &
	@ntk watch

# Compile Tailwind once + post-process for Sass compatibility.
# assets/main.css is updated only after the strict compat pass succeeds.
css:
	@set -e; \
	TMP_CSS=$$(mktemp); \
	trap 'rm -f "$$TMP_CSS"' EXIT; \
	$(TAILWIND) -i "$(CSS_INPUT)" -o "$$TMP_CSS" --minify; \
	$(COMPAT) "$$TMP_CSS" assets/main.css

# Fail if the committed CSS differs from a fresh post-processed build.
css-drift:
	python3 scripts/check-css-drift.py --input "$(CSS_INPUT)"

# Build CSS and fail if generated output still contains platform-unsafe CSS.
css-check: css
	$(COMPAT) --check assets/main.css

# Build for production (compile + minify + sass-compat)
build: css-check
	@echo "Build complete. Push with: ntk push assets/main.css"

# Build + push CSS to store
push: css-check
	ntk push assets/main.css

# Lightweight local regression tests for theme tooling.
test:
	python3 -m unittest discover -s tests

# Assert theme-contract.json: the platform integration points every derived theme
# keeps (fleet scope) plus, on Spark's own copy, the runtime hooks theme.js
# resolves (spark scope). A live check defaults to the fleet scope; add
# --scope spark when the live theme is Spark itself.
# Point it at a live theme before or after a push:
#   make contract THEME_ARGS="--store https://x.29next.store --theme-id 68"               # a derived theme
#   make contract THEME_ARGS="--store https://dev.29next.store --theme-id 68 --scope spark"  # Spark itself
contract:
	python3 scripts/check-theme-contract.py $(THEME_ARGS)

# Compile every template with Django 4.2 and stubs of the platform's tags, the
# way the platform does at upload. Uses an installed Django 4.2; otherwise, when
# uv is available, runs in a throwaway uv environment (nothing installed);
# otherwise skips with a notice.
dtl:
	@if python3 -c 'import django, sys; sys.exit(django.VERSION[:2] != (4, 2))' 2>/dev/null; then \
		python3 scripts/check-dtl.py; \
	elif command -v uv >/dev/null 2>&1; then \
		uv run --no-project --quiet --with "django==4.2.*" python scripts/check-dtl.py; \
	else \
		python3 scripts/check-dtl.py; \
	fi

# Full pre-upload verification for generated theme artifacts.
verify-theme: css-check test dtl contract
	@echo "Theme verification complete."

# Watch Tailwind only (useful when running ntk watch separately)
watch:
	$(TAILWIND) -i "$(CSS_INPUT)" -o assets/main.css --watch

# Production release: rebuild main.css and stage it for commit.
# Run this before committing CSS source changes so the committed
# main.css stays in sync with $(CSS_INPUT).
release: css-check
	@git add assets/main.css
	@echo "main.css rebuilt and staged. Commit it with your CSS source changes."

# Download the Tailwind v4 standalone CLI binary for this platform.
# The binary is gitignored (76MB, platform-specific) and not preserved
# by the platform on theme push, so each dev fetches their own.
install-tailwind:
	@OS=$$(uname -s | tr '[:upper:]' '[:lower:]'); \
	ARCH=$$(uname -m); \
	case "$$OS-$$ARCH" in \
		darwin-arm64)  TARGET=macos-arm64 ;; \
		darwin-x86_64) TARGET=macos-x64 ;; \
		linux-x86_64)  TARGET=linux-x64 ;; \
		linux-aarch64) TARGET=linux-arm64 ;; \
		*) echo "Unsupported platform: $$OS-$$ARCH"; exit 1 ;; \
	esac; \
	URL="https://github.com/tailwindlabs/tailwindcss/releases/download/$(TAILWIND_VERSION)/tailwindcss-$$TARGET"; \
	echo "Downloading Tailwind $(TAILWIND_VERSION) for $$TARGET..."; \
	curl -L -o tailwindcss "$$URL"; \
	chmod +x tailwindcss; \
	./tailwindcss --help > /dev/null && echo "OK: ./tailwindcss installed."
