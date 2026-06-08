import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const skipDirs = new Set(['.git', 'node_modules', 'dist', 'build']);
const files = [];
let failed = false;

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (skipDirs.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else files.push(full);
  }
}

function fail(message) {
  console.error(message);
  failed = true;
}

const secretPatterns = [
  /ghp_[A-Za-z0-9_]+/,
  /sk-[A-Za-z0-9_-]{20,}/,
  /xox[baprs]-[A-Za-z0-9-]+/,
  /BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY/,
  /telegram:-?\d+:[0-9]+/,
  /TELEGRAM_[A-Z_]*TOKEN\s*=/,
  /Authorization:\s*Bearer\s+[A-Za-z0-9_.-]+/i
];

walk(root);

for (const file of files.sort()) {
  const rel = path.relative(root, file);
  const text = fs.readFileSync(file, 'utf8');
  for (const pattern of secretPatterns) {
    if (pattern.test(text)) fail(`secret/token pattern ${pattern} in ${rel}`);
  }
}

if (failed) process.exit(1);
console.log(`public-safe ok (${files.length} files scanned for secret/token patterns)`);
