// Run one of the mouse-pouches checks against another funnel that shares its checkout, offer and thank-you pages.
//   node tools/funnel/getridof/run_for.cjs mice-5-reasons tools/funnel/getridof/payment_check.cjs https://getridof.shop
// It loads the check with every "mouse-pouches" in its source replaced by the given slug, so the two funnels are
// held to the same checks without keeping two copies of them. Use it for payment_check, polish_checks and mobile_audit;
// the listicle page itself has its own check (listicle_check.cjs), because e2e.cjs and live_check.cjs test the sales page.
const fs = require('fs'), path = require('path'), Module = require('module');
const [slug, script, ...rest] = process.argv.slice(2);
if (!/^[a-z0-9-]+$/.test(slug || '') || !script) { console.error('usage: run_for.cjs <slug> <check.cjs> [args...]'); process.exit(2); }
const file = path.resolve(script);
const src = fs.readFileSync(file, 'utf8').split('mouse-pouches').join(slug);
process.argv = [process.argv[0], file, ...rest];
const m = new Module(file, module);
m.filename = file; m.paths = Module._nodeModulePaths(path.dirname(file));
m._compile(src, file);
