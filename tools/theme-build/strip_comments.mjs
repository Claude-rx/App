// Take the comments out of scripts: the store's own notes ("stick review 5: ...") stay in tools/, not in what a
// visitor downloads, and the bytes go too.
// usage: node strip_comments.mjs < scripts.json > out.json   (input: ["<script body>", ...]; output: same order)
//
// Each body is parsed (acorn); its comments are cut out, a block comment that spanned lines leaving one newline and
// a line comment leaving its newline, so automatic semicolon insertion reads the code as before. "/*! ... */"
// (a licence) stays. A body that does not parse (template tags in it, or not JavaScript) comes back as null and is
// left alone.
import fs from 'fs';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
let acorn;
for (const p of ['acorn', '/opt/node-tools/node_modules/acorn']) { try { acorn = require(p); break; } catch (e) { /* next */ } }
if (!acorn) { console.error('strip_comments: acorn not found (npm i acorn)'); process.exit(2); }

const bodies = JSON.parse(fs.readFileSync(0, 'utf8'));
const out = bodies.map(src => {
  const comments = [];
  try {
    acorn.parse(src, { ecmaVersion: 'latest', sourceType: 'script', allowHashBang: true, onComment: comments });
  } catch (e) {
    try { comments.length = 0; acorn.parse(src, { ecmaVersion: 'latest', sourceType: 'module', onComment: comments }); }
    catch (e2) { return null; }
  }
  let code = '', cursor = 0;
  for (const c of comments) {
    if (c.type === 'Block' && c.value.startsWith('!')) continue;
    code += src.slice(cursor, c.start);
    code += c.type === 'Block' ? (/[\n\r\u2028\u2029]/.test(c.value) ? '\n' : ' ') : '';
    cursor = c.end;
  }
  return code + src.slice(cursor);
});
process.stdout.write(JSON.stringify(out));
