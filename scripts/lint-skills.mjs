import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const skillsRoot = path.join(root, 'skills');
const lifeOsRoot = path.join(root, 'skills', 'life-os');
const skillIndexPath = path.join(lifeOsRoot, 'skill-index.yaml');

let failed = false;
const errors = [];
const warnings = [];

function error(message) {
  failed = true;
  errors.push(message);
}

function warn(message) {
  warnings.push(message);
}

function readText(file) {
  return fs.readFileSync(file, 'utf8');
}

function listFiles(dir, predicate = () => true) {
  const out = [];
  function walk(current) {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      if (entry.name === '.git' || entry.name === 'node_modules') continue;
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (predicate(full)) out.push(full);
    }
  }
  if (fs.existsSync(dir)) walk(dir);
  return out.sort();
}

function parseScalarYamlFrontmatter(text, file) {
  if (!text.startsWith('---\n')) {
    error(`${file}: SKILL.md must start with frontmatter at byte 0`);
    return null;
  }
  const end = text.indexOf('\n---\n', 4);
  if (end === -1) {
    error(`${file}: frontmatter is missing closing --- marker`);
    return null;
  }
  const body = text.slice(end + 5).trim();
  if (!body) error(`${file}: body is empty`);

  const frontmatter = text.slice(4, end);
  const fields = new Map();
  for (const rawLine of frontmatter.split('\n')) {
    const line = rawLine.trimEnd();
    if (!line || line.startsWith('#')) continue;
    if (/^\s/.test(rawLine)) continue; // nested metadata, not a top-level scalar
    const match = line.match(/^([A-Za-z0-9_.-]+):\s*(.*)$/);
    if (match) fields.set(match[1], match[2].trim().replace(/^['"]|['"]$/g, ''));
  }
  return { fields, body, frontmatter };
}

function parseSkillIndexSubskills(file) {
  const text = readText(file);
  const lines = text.split('\n');
  const names = [];
  let inSubskills = false;
  for (const line of lines) {
    if (/^subskills:\s*$/.test(line)) {
      inSubskills = true;
      continue;
    }
    if (!inSubskills) continue;
    const match = line.match(/^  ([a-z0-9][a-z0-9-]*):\s*$/);
    if (match) names.push(match[1]);
    if (/^[A-Za-z0-9_-]+:\s*$/.test(line) && !line.startsWith('  ')) inSubskills = false;
  }
  return names;
}

function validateJson() {
  for (const file of listFiles(root, f => f.endsWith('.json'))) {
    const rel = path.relative(root, file);
    try {
      JSON.parse(readText(file));
    } catch (err) {
      error(`${rel}: invalid JSON: ${err.message}`);
    }
  }
}

function validateSkills() {
  const skillFiles = listFiles(skillsRoot, f => path.basename(f) === 'SKILL.md');
  if (skillFiles.length === 0) error('no SKILL.md files found under skills/');

  const seenNames = new Map();
  for (const file of skillFiles) {
    const rel = path.relative(root, file);
    const parsed = parseScalarYamlFrontmatter(readText(file), rel);
    if (!parsed) continue;
    const { fields, body } = parsed;
    const dirName = path.basename(path.dirname(file));
    const name = fields.get('name');
    const description = fields.get('description');

    for (const required of ['name', 'description', 'version', 'license']) {
      if (!fields.get(required)) error(`${rel}: missing frontmatter field '${required}'`);
    }
    if (name && !/^[a-z0-9][a-z0-9-]{0,63}$/.test(name)) error(`${rel}: invalid skill name '${name}'`);
    if (description && description.length > 1024) error(`${rel}: description exceeds 1024 chars`);
    if (description && description.length < 20) warn(`${rel}: description is very short`);
    if (name && dirName !== name) error(`${rel}: skill name '${name}' must match directory '${dirName}'`);
    if (name) {
      if (seenNames.has(name)) error(`${rel}: duplicate skill name '${name}', first seen in ${seenNames.get(name)}`);
      seenNames.set(name, rel);
    }
    if (!body.startsWith('# ')) error(`${rel}: body must start with an H1 heading`);
    if (!/##\s+Data\b/.test(body) && rel !== 'skills/life-os/SKILL.md') warn(`${rel}: subskill has no '## Data' section`);
  }

  if (!fs.existsSync(skillIndexPath)) {
    error('skills/life-os/skill-index.yaml is missing');
    return;
  }
  const indexed = parseSkillIndexSubskills(skillIndexPath);
  const indexedSet = new Set(indexed);
  if (indexed.length === 0) error('skills/life-os/skill-index.yaml has no subskills');
  for (const name of indexed) {
    const skillPath = path.join(lifeOsRoot, 'skills', name, 'SKILL.md');
    const schemaPath = path.join(lifeOsRoot, 'skills', name, 'schemas', 'data.schema.json');
    if (!fs.existsSync(skillPath)) error(`skill-index references missing subskill ${name}: ${path.relative(root, skillPath)}`);
    if (!fs.existsSync(schemaPath)) error(`subskill ${name} is missing schemas/data.schema.json`);
  }
  for (const file of skillFiles) {
    const rel = path.relative(root, file);
    if (!rel.startsWith('skills/life-os/skills/')) continue;
    const name = path.basename(path.dirname(file));
    if (!indexedSet.has(name)) error(`${rel}: subskill is not listed in skills/life-os/skill-index.yaml`);
  }
}

validateJson();
validateSkills();

for (const message of warnings) console.warn(`warning: ${message}`);
for (const message of errors) console.error(`error: ${message}`);

if (failed) process.exit(1);
console.log(`skill lint ok (${listFiles(skillsRoot, f => path.basename(f) === 'SKILL.md').length} skills checked)`);
