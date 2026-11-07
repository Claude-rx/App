#!/usr/bin/env node
// Assemble plugins/supliful-mediclab (the Cowork / Claude Code plugin) from its sources and package
// dist/supliful-mediclab.plugin.
//   node scripts/build-cowork-plugin.mjs           build + zip
//   node scripts/build-cowork-plugin.mjs --check   fail if the committed plugin is out of date (CI)
// Sources: tools/supliful (server code, label defaults), .claude/skills/supliful-api (official skill).
import { cpSync, rmSync, mkdirSync, readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, relative, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";
import { tmpdir } from "node:os";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SRC = join(ROOT, "tools", "supliful");
const PLUGIN = join(ROOT, "plugins", "supliful-mediclab");
const check = process.argv.includes("--check");

/** [source, destination inside the plugin] */
const COPIES = [
  ["tools/supliful/mcp.mjs", "server/mcp.mjs"],
  ["tools/supliful/lib", "server/lib"],
  ["tools/supliful/labels/render.mjs", "server/labels/render.mjs"],
  ["tools/supliful/labels/extract.mjs", "server/labels/extract.mjs"],
  ["tools/supliful/labels/brand.json", "server/labels/defaults/brand.json"],
  ["tools/supliful/labels/specs.json", "server/labels/defaults/specs.json"],
  ["tools/supliful/labels/catalog.json", "server/labels/defaults/catalog.json"],
  ["tools/supliful/.env.example", "server/env.example"],
  [".claude/skills/supliful-api", "skills/supliful-api"],
];

function files(p) {
  if (!existsSync(p)) return [];
  if (statSync(p).isFile()) return [p];
  return readdirSync(p).flatMap((f) => files(join(p, f)));
}

function build(target) {
  rmSync(join(target, "server"), { recursive: true, force: true });
  rmSync(join(target, "skills", "supliful-api"), { recursive: true, force: true });
  for (const [from, to] of COPIES) {
    mkdirSync(dirname(join(target, to)), { recursive: true });
    cpSync(join(ROOT, from), join(target, to), { recursive: true });
  }
}

if (check) {
  const stale = [];
  for (const [from, to] of COPIES) {
    const src = join(ROOT, from);
    for (const f of files(src)) {
      const rel = relative(src, f);
      const dest = statSync(src).isFile() ? join(PLUGIN, to) : join(PLUGIN, to, rel);
      if (!existsSync(dest) || !readFileSync(dest).equals(readFileSync(f))) stale.push(relative(ROOT, dest));
    }
  }
  if (stale.length) {
    console.error(`Plugin is out of date (${stale.length} files). Run: npm run plugin:build\n  ${stale.join("\n  ")}`);
    process.exit(1);
  }
  console.log("plugins/supliful-mediclab is up to date.");
  process.exit(0);
}

build(PLUGIN);
const manifest = JSON.parse(readFileSync(join(PLUGIN, ".claude-plugin", "plugin.json"), "utf8"));
const outDir = join(ROOT, "dist");
mkdirSync(outDir, { recursive: true });
const tmp = join(tmpdir(), `${manifest.name}.plugin`);
rmSync(tmp, { force: true });
execFileSync("zip", ["-qr", tmp, ".", "-x", "*.DS_Store"], { cwd: PLUGIN });
cpSync(tmp, join(outDir, `${manifest.name}.plugin`));
console.log(`Built ${manifest.name} ${manifest.version}: plugins/${manifest.name}/ and dist/${manifest.name}.plugin (${files(PLUGIN).length} files)`);
