#!/usr/bin/env python3
"""Source-pinned zh-TW UI translation overlay for Herdr v0.9.3.

Does not modify the Herdr server protocol, structured CLI output or update metadata.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

UPSTREAM_COMMIT = '7b116c05bfda646af39d2524c54e70c751f57ee8'


def command(*argv: str, cwd: Path) -> str:
    result = subprocess.run(argv, cwd=cwd, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def placeholders(s: str) -> Counter:
    # Extract Rust format markers, excluding escaped braces. The supplied entries
    # currently use only simple named/positional placeholders.
    return Counter(re.findall(r'(?<!\{)\{([^{}]*)\}(?!\})', s))


def apply(repo: Path, manifest: Path, dry_run: bool = False) -> dict:
    repo = repo.resolve()
    if not (repo / 'Cargo.toml').is_file():
        raise RuntimeError('Not a Herdr source tree (Cargo.toml missing)')
    revision = command('git', 'rev-parse', 'HEAD', cwd=repo)
    if revision != UPSTREAM_COMMIT:
        raise RuntimeError(f'Requires exact upstream v0.9.3 commit {UPSTREAM_COMMIT}; found {revision}')
    if command('git', 'status', '--porcelain', cwd=repo):
        raise RuntimeError('Source tree is not clean; use a fresh isolated clone (no changes made)')
    mappings = json.loads(manifest.read_text(encoding='utf-8'))
    result = {'upstream_commit': revision, 'files': {}, 'applied_keys': 0, 'applied_occurrences': 0, 'missing_keys': {}, 'mode': 'preview' if dry_run else 'applied'}
    updates = {}
    for rel, dictionary in mappings.items():
        if not rel.startswith('src/') or not rel.endswith('.rs') or '..' in Path(rel).parts:
            raise RuntimeError(f'Unsafe path {rel}')
        path = repo / rel
        content = path.read_text(encoding='utf-8')
        # Preserve embedded Rust tests (including English expected outputs).
        match = re.search(r'(?m)^#\[cfg\(test\)\]', content)
        body, tail = (content[:match.start()], content[match.start():]) if match else (content, '')
        missing = []
        used = 0
        substitutions = 0
        for english, traditional in dictionary.items():
            if placeholders(english) != placeholders(traditional):
                raise RuntimeError(f'Rust format arguments changed in {rel}: {english!r}')
            if not english or not traditional or '\\' in english or '\\' in traditional or '"' in english or '"' in traditional:
                raise RuntimeError(f'Unsupported literal in {rel}: {english!r}')
            original = '"' + english + '"'
            replacement = '"' + traditional + '"'
            count = body.count(original)
            if count == 0:
                missing.append(english)
                continue
            body = body.replace(original, replacement)
            used += 1
            substitutions += count
        updates[path] = body + tail
        result['files'][rel] = {'matched_keys': used, 'replaced_literals': substitutions, 'unmatched_keys': len(missing)}
        result['applied_keys'] += used
        result['applied_occurrences'] += substitutions
        if missing:
            result['missing_keys'][rel] = missing

    # Dedicated terminal-cell width correctness fix for translated labels.
    # Confirm source function contents before editing, fail on upstream drift.
    ui = repo / 'src/ui/widgets.rs'
    source = updates.get(ui, ui.read_text(encoding='utf-8'))
    old = 'format!(" {hint} {label} ").chars().count() as u16'
    new = 'format!(" {hint} {label} ").as_str().width() as u16'
    old2 = 'format!(" {label} ").chars().count() as u16'
    new2 = 'format!(" {label} ").as_str().width() as u16'
    if source.count(old) != 1 or source.count(old2) != 1:
        raise RuntimeError('Cannot verify original UI width calculation; refusing patch')
    if 'use unicode_width::UnicodeWidthStr;' not in source:
        source = source.replace('\n\nuse crate::app::state::Palette;', '\nuse unicode_width::UnicodeWidthStr;\n\nuse crate::app::state::Palette;', 1)
    updates[ui] = source.replace(old, new).replace(old2, new2)
    result['files']['src/ui/widgets.rs'] = {'layout_cell_width_corrections': 2}

    # Never alter source files if any validation above fails.
    if not dry_run:
        for path, contents in updates.items():
            path.write_text(contents, encoding='utf-8', newline='')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description='Apply pinned Herdr 0.9.3 zh-TW UI overlay')
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = apply(args.source, Path(__file__).with_name('translations_zh_TW.json'), args.dry_run)
    body = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    print(body)
    if args.report:
        args.report.write_text(body, encoding='utf-8')
    if report['applied_keys'] == 0:
        print('ERROR: No translations matched', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        raise SystemExit(1)
