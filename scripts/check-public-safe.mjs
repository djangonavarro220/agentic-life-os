import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
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

function fail(message) {
  console.error(message);
  failed = true;
}

walk(root);
let failed = false;

const forbidden = [
  /ghp_[A-Za-z0-9_]+/,
  /sk-[A-Za-z0-9_-]+/,
  /xox[baprs]-[A-Za-z0-9-]+/,
  /BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY/,
  /telegram:-?\d+:[0-9]+/,
  /TELEGRAM_[A-Z_]*TOKEN\s*=/,
  /Authorization:\s*Bearer\s+[A-Za-z0-9_.-]+/i
];

for (const file of files) {
  const rel = path.relative(root, file);
  const text = fs.readFileSync(file, 'utf8');

  for (const rx of forbidden) {
    if (rx.test(text)) fail(`public-safety match ${rx} in ${rel}`);
  }

  if (rel.endsWith('.json')) {
    try {
      JSON.parse(text);
    } catch (error) {
      fail(`invalid JSON in ${rel}: ${error.message}`);
    }
  }

  if (rel.endsWith('SKILL.md')) {
    if (!text.startsWith('---\n')) fail(`SKILL frontmatter must start at byte 0 in ${rel}`);
    const end = text.indexOf('\n---\n', 4);
    if (end === -1) {
      fail(`SKILL frontmatter missing closing marker in ${rel}`);
      continue;
    }
    const frontmatter = text.slice(4, end).split('\n');
    const body = text.slice(end + 5).trim();
    const fields = new Map();
    for (const line of frontmatter) {
      const match = line.match(/^([A-Za-z0-9_.-]+):\s*(.*)$/);
      if (match) fields.set(match[1], match[2].trim());
    }
    const name = fields.get('name');
    const description = fields.get('description');
    if (!name) fail(`SKILL missing name in ${rel}`);
    if (!description) fail(`SKILL missing description in ${rel}`);
    if (name && !/^[a-z0-9][a-z0-9-]{0,63}$/.test(name)) fail(`SKILL invalid name '${name}' in ${rel}`);
    if (description && description.length > 1024) fail(`SKILL description too long in ${rel}`);
    if (!body) fail(`SKILL body is empty in ${rel}`);
  }
}

if (failed) process.exit(1);
console.log(`lint ok (${files.length} files checked)`);
