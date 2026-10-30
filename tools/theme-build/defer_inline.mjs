// Let inline scripts that use a deferred library run after it has loaded, with the same global names.
// usage: node defer_inline.mjs < scripts.json > out.json   (input: ["<script body>", ...]; output: same order)
//
// A parser-time inline script like `function loadVideo(){...}; var swiper = new Swiper(...)` breaks once Swiper is
// loaded with `defer`. Each body is rewritten so that:
//   - top-level function declarations stay where they are (still global, still hoisted: onclick="loadVideo()" works);
//   - top-level var/let/const names stay global (`var a, b;` up front), their initialisers become assignments;
//   - everything else runs on DOMContentLoaded, which fires after every deferred script has run, in document order.
// Output: [{code, globals}] in input order; code is null for a body that does not parse or has nothing to defer
// (left alone). globals lists the var/let/const names that are now assigned late, so the caller can check that no
// other parser-time script reads them.
import fs from 'fs';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
let acorn;
for (const p of ['acorn', '/opt/node-tools/node_modules/acorn']) { try { acorn = require(p); break; } catch (e) { /* next */ } }
if (!acorn) { console.error('defer_inline: acorn not found (npm i acorn)'); process.exit(2); }

const bodies = JSON.parse(fs.readFileSync(0, 'utf8'));
const out = bodies.map(src => {
  let ast;
  try { ast = acorn.parse(src, { ecmaVersion: 'latest', sourceType: 'script', ranges: true }); } catch (e) { return { code: null, globals: [] }; }
  const hoisted = [], names = [];
  let body = '', cursor = 0, deferred = 0;
  const keep = (from, to) => { body += src.slice(from, to); };
  for (const node of ast.body) {
    keep(cursor, node.start);                     // comments / whitespace between statements
    if (node.type === 'FunctionDeclaration') {
      hoisted.push(src.slice(node.start, node.end));
    } else if (node.type === 'VariableDeclaration') {
      const assigns = [];
      for (const d of node.declarations) {
        if (d.id.type !== 'Identifier') return { code: null, globals: [] };   // destructuring: leave the script alone
        names.push(d.id.name);
        if (d.init) assigns.push(d.id.name + ' = ' + src.slice(d.init.start, d.init.end));
      }
      if (assigns.length) { body += assigns.join(';\n') + ';'; deferred++; }
    } else {
      body += src.slice(node.start, node.end); deferred++;
    }
    cursor = node.end;
  }
  keep(cursor, src.length);
  if (!deferred) return { code: null, globals: [] };
  const code = (names.length ? 'var ' + [...new Set(names)].join(', ') + ';\n' : '') +
    (hoisted.length ? hoisted.join('\n') + '\n' : '') +
    "document.addEventListener('DOMContentLoaded', function () {\n" + body + '\n});';
  return { code, globals: [...new Set(names)] };
});
process.stdout.write(JSON.stringify(out));
