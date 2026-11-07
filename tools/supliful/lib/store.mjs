// Tiny durable JSON store for webhook dedupe and the Shopify <-> Supliful order map.
// One file per collection under SUPLIFUL_STATE_DIR (gitignored). Writes are atomic (tmp + rename).
import { mkdirSync, readFileSync, writeFileSync, renameSync, existsSync, appendFileSync } from "node:fs";
import { join } from "node:path";

export class JsonStore {
  constructor(dir) {
    this.dir = dir;
    mkdirSync(dir, { recursive: true });
    this.cache = new Map();
  }
  file(name) {
    return join(this.dir, `${name}.json`);
  }
  load(name) {
    if (this.cache.has(name)) return this.cache.get(name);
    const f = this.file(name);
    const data = existsSync(f) ? JSON.parse(readFileSync(f, "utf8")) : {};
    this.cache.set(name, data);
    return data;
  }
  get(name, key) {
    return this.load(name)[key];
  }
  set(name, key, value) {
    const data = this.load(name);
    data[key] = value;
    const f = this.file(name);
    writeFileSync(`${f}.tmp`, JSON.stringify(data, null, 1));
    renameSync(`${f}.tmp`, f);
    return value;
  }
  /** Append-only event log (JSONL), so every delivery can be inspected and replayed. */
  append(name, entry) {
    appendFileSync(join(this.dir, `${name}.jsonl`), JSON.stringify({ at: new Date().toISOString(), ...entry }) + "\n");
  }
}
