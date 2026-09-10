#!/usr/bin/env python3
"""check-specs: validate a specs repository.

Runs three checks over every feature folder in a specs repository:

  1. both-files      every feature entry has both <slug>.md and <slug>.tech-refs.md
  2. cited-path      every path cited in a .tech-refs.md exists in the sibling checkout
                     named by its heading (## Project) under --root
  3. code-identifier the business spec (<slug>.md) contains no code identifiers
                     (backticked tokens containing '/', '.py', '.ts', '.java',
                     '::', '()', or a CamelCase word with an internal capital)

Exit codes: 0 clean, 1 findings, 2 usage error.
One line per finding: "<check> <file>: <detail>".

Python 3 standard library only.
"""

import argparse
import os
import re
import sys


def is_tech_refs(name):
    return name.endswith(".tech-refs.md")


def is_business_md(name):
    return name.endswith(".md") and not is_tech_refs(name)


def slug_of(name):
    if is_tech_refs(name):
        return name[: -len(".tech-refs.md")]
    if name.endswith(".md"):
        return name[: -len(".md")]
    return None


def check_both_files(specs_dir):
    """Check 1: every feature entry in every folder has both files."""
    findings = []
    for dirpath, _dirnames, filenames in os.walk(specs_dir):
        slugs = set()
        for name in filenames:
            if name.endswith(".md"):
                s = slug_of(name)
                if s:
                    slugs.add(s)
        for s in sorted(slugs):
            biz = os.path.join(dirpath, s + ".md")
            tech = os.path.join(dirpath, s + ".tech-refs.md")
            if not os.path.isfile(biz):
                findings.append(("both-files", os.path.join(dirpath, s),
                                 "missing %s.md" % s))
            if not os.path.isfile(tech):
                findings.append(("both-files", os.path.join(dirpath, s),
                                 "missing %s.tech-refs.md" % s))
    return findings


HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")
BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
BACKTICK_RE = re.compile(r"`([^`]+)`")


def extract_cited_path(bullet_text):
    m = BACKTICK_RE.search(bullet_text)
    if m:
        return m.group(1).strip()
    parts = bullet_text.strip().split()
    if not parts:
        return ""
    return parts[0].rstrip(":,.")


def looks_like_path(candidate):
    if not candidate:
        return False
    return "/" in candidate or re.search(r"\.\w+$", candidate) is not None


def check_cited_paths(specs_dir, root):
    """Check 2: every cited path exists under root/<heading-project>/."""
    findings = []
    for dirpath, _dirnames, filenames in os.walk(specs_dir):
        for name in sorted(filenames):
            if not is_tech_refs(name):
                continue
            fpath = os.path.join(dirpath, name)
            try:
                with open(fpath, "r", encoding="utf-8") as fh:
                    lines = fh.read().splitlines()
            except OSError as exc:
                findings.append(("cited-path", fpath, "unreadable: %s" % exc))
                continue
            project = None
            for line in lines:
                h = HEADING_RE.match(line)
                if h:
                    project = h.group(1).strip().strip("`")
                    continue
                b = BULLET_RE.match(line)
                if not b:
                    continue
                candidate = extract_cited_path(b.group(1))
                if not looks_like_path(candidate):
                    continue
                if project is None:
                    findings.append(("cited-path", fpath,
                                     "%s cited with no project heading" % candidate))
                    continue
                target = os.path.join(root, project, candidate)
                if not os.path.exists(target):
                    findings.append(("cited-path", fpath,
                                     "%s/%s not found under %s"
                                     % (project, candidate, root)))
    return findings


CAMEL_RE = re.compile(r"[a-z][A-Z]")


def is_code_identifier(token):
    for needle in ("/", ".py", ".ts", ".java", "::", "()"):
        if needle in token:
            return True
    if CAMEL_RE.search(token):
        return True
    return False


def check_code_identifiers(specs_dir):
    """Check 3: no code identifiers in the business spec."""
    findings = []
    for dirpath, _dirnames, filenames in os.walk(specs_dir):
        for name in sorted(filenames):
            if not is_business_md(name):
                continue
            fpath = os.path.join(dirpath, name)
            try:
                with open(fpath, "r", encoding="utf-8") as fh:
                    content = fh.read()
            except OSError as exc:
                findings.append(("code-identifier", fpath, "unreadable: %s" % exc))
                continue
            for token in BACKTICK_RE.findall(content):
                token = token.strip()
                if is_code_identifier(token):
                    findings.append(("code-identifier", fpath, token))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check-specs.py",
        description="Validate a specs repository (both files present, cited paths "
                    "exist, no code identifiers in the business spec).",
    )
    parser.add_argument("specs_dir", help="path to the specs repository to check")
    parser.add_argument("--root", default="..",
                        help="parent directory of the sibling code checkouts "
                             "named by tech-refs headings (default: ..)")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.specs_dir):
        parser.error("specs_dir is not a directory: %s" % args.specs_dir)

    findings = []
    findings += check_both_files(args.specs_dir)
    findings += check_cited_paths(args.specs_dir, args.root)
    findings += check_code_identifiers(args.specs_dir)

    for check, path, detail in sorted(findings):
        print("%s %s: %s" % (check, path, detail))

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
