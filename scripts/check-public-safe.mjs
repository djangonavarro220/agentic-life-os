import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const forbidden = [
  /ghp_[A-Za-z0-9_]+/,
  /sk-[A-Za-z0-9_-]+/,
  /xox[baprs]-[A-Za-z0-9-]+/,
  /BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY/,
  /telegram:-?\d+:[0-9]+/,
  /TELEGRAM_[A-Z_]*TOKEN\s*=/,
  /Authorization:\s*Bearer\s+[A-Za-z0-9_.-]+/i
];
const skipDirs = new Set(['.git', 'node_modules', 'dist', 'build']);
const files = [];
function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (skipDirs.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else files.push(full);
  }
}
walk(root);
let failed = false;
for (const file of files) {
  const rel = path.relative(root, file);
  const text = fs.readFileSync(file, 'utf8');
  for (const rx of forbidden) {
    if (rx.test(text)) {
      console.error(`public-safety match ${rx} in ${rel}`);
      failed = true;
    }
  }
}
if (failed) process.exit(1);
console.log(`public-safety ok (${files.length} files checked)`);
