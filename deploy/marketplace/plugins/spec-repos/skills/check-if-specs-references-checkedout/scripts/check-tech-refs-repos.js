#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const specsFolderName = process.argv[2];
const projectRoot = process.argv[3];

if (!specsFolderName || !projectRoot) {
  console.error('Usage: node check-tech-refs-repos.js <specs-folder-name> <project-root>');
  console.error('  <project-root>    the root directory of the project you are checking from');
  console.error('  <specs-folder-name>  must be a sibling of <project-root>');
  process.exit(1);
}

const gitReposPath = path.dirname(path.resolve(projectRoot));

const specsFolder = path.join(gitReposPath, specsFolderName);
if (!fs.existsSync(specsFolder) || !fs.statSync(specsFolder).isDirectory()) {
  console.error(`Specs folder not found: ${specsFolder}`);
  process.exit(1);
}

function collectTechRefsFiles(dir) {
  const results = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith('.')) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...collectTechRefsFiles(full));
    } else if (entry.isFile() && entry.name.endsWith('.tech-refs.md')) {
      results.push(full);
    }
  }
  return results;
}

const repoPattern = /\{git repos path\}[/\\]([^\s`)/\\]+)/g;
const referenced = new Set();

for (const file of collectTechRefsFiles(specsFolder)) {
  const content = fs.readFileSync(file, 'utf8');
  for (const match of content.matchAll(repoPattern)) {
    referenced.add(match[1]);
  }
}

console.log(`\nGit repos path: ${gitReposPath}`);
console.log(`Specs folder:   ${specsFolder}\n`);

if (referenced.size === 0) {
  console.log('No {git repos path} references found in any .tech-refs.md file.');
  process.exit(0);
}

let allPresent = true;
for (const repo of [...referenced].sort()) {
  const fullPath = path.join(gitReposPath, repo);
  const exists = fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory();
  console.log(`  ${exists ? '✓' : '✗'}  ${repo}`);
  if (!exists) allPresent = false;
}

console.log('');
if (allPresent) {
  console.log('All referenced repositories are checked out.');
} else {
  console.log(`One or more repositories are missing. Clone them into:\n  ${gitReposPath}`);
  process.exit(1);
}
