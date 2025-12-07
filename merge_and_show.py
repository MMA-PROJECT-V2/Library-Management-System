#!/usr/bin/env python3
"""Merge one or more pytest JUnit XML files (or run pytest) and print a combined
per-test listing followed by totals and pass percentage.

Usage:
  python scripts/merge_and_show.py [--run-local] [file1.xml file2.xml ...]

If --run-local is provided the script will run `pytest --junitxml=local_results.xml`
in the repository root and include that result in the merge. Otherwise pass existing
JUnit XML report files as arguments.
"""
from __future__ import annotations

import sys
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import List, Tuple


def run_pytest_write_xml(path: Path) -> int:
    # Run pytest, produce JUnit XML and also generate a terminal coverage report
    cmd = [
        sys.executable,
        '-m',
        'pytest',
        f'--junitxml={str(path)}',
        '--cov=backend/books_service',
        '--cov-report=term',
    ]
    print('Running pytest to produce:', path)
    repo_root = Path(__file__).resolve().parent
    return subprocess.run(cmd, cwd=repo_root / 'backend' / 'books_service').returncode


def parse_junit(path: Path) -> List[Tuple[str, str, str]]:
    # returns list of tuples (module_or_classname, test_name, status) where
    # status in {PASSED, FAILED, ERROR, SKIPPED}
    tree = ET.parse(path)
    root = tree.getroot()

    cases = []
    # testsuite(s) contain testcase elements
    for testcase in root.findall('.//testcase'):
        classname = testcase.attrib.get('classname') or ''
        name = testcase.attrib.get('name') or ''

        status = 'PASSED'
        if testcase.find('failure') is not None:
            status = 'FAILED'
        elif testcase.find('error') is not None:
            status = 'ERROR'
        elif testcase.find('skipped') is not None:
            status = 'SKIPPED'

        cases.append((classname, name, status))
    return cases


def merge_files(paths: List[Path]) -> List[Tuple[str, str, str]]:
    all_cases: List[Tuple[str, str, str]] = []
    for p in paths:
        if not p.exists():
            print('Warning: file not found, skipping:', p)
            continue
        cases = parse_junit(p)
        all_cases.extend(cases)
    return all_cases


def print_report(all_cases: List[Tuple[str, str, str]]):
    # Sort for stable output by classname then name
    all_cases.sort(key=lambda x: (x[0], x[1]))

    passed = failed = errors = skipped = 0
    total = len(all_cases)

    for i, (classname, name, status) in enumerate(all_cases, start=1):
        # Try to form a file-like path when classname resembles a module path
        display_prefix = classname
        if classname and (classname.startswith('backend') or classname.startswith('tests') or '.' in classname):
            display_prefix = classname.replace('.', '\\') + '.py'

        node_display = f"{display_prefix}::{name}" if display_prefix else name
        pct = int(i / total * 100) if total else 0
        print(f"{node_display} {status} [{pct:3d}%]")

        if status == 'PASSED':
            passed += 1
        elif status == 'FAILED':
            failed += 1
        elif status == 'ERROR':
            errors += 1
        elif status == 'SKIPPED':
            skipped += 1

    pass_pct = (passed / total * 100) if total else 0.0

    print('\n' + '=' * 60)
    print('Combined Test Summary')
    print(f'  Total tests: {total}')
    print(f'  Passed:      {passed}')
    print(f'  Failed:      {failed}')
    print(f'  Errors:      {errors}')
    print(f'  Skipped:     {skipped}')
    print(f'  Pass rate:   {pass_pct:.2f}%')


def main(argv: List[str]):
    repo_root = Path(__file__).resolve().parent
    args = argv[1:]
    run_local = False
    if '--run-local' in args:
        run_local = True
        args.remove('--run-local')

    xml_paths: List[Path] = [Path(a) for a in args]

    if run_local:
        local_xml = repo_root / 'local_pytest_results.xml'
        rc = run_pytest_write_xml(local_xml)
        xml_paths.insert(0, local_xml)

    if not xml_paths:
        print('No XML files provided and --run-local not specified.')
        print('Usage: python scripts/merge_and_show.py [--run-local] file1.xml file2.xml')
        sys.exit(2)

    all_cases = merge_files(xml_paths)
    print_report(all_cases)


if __name__ == '__main__':
    main(sys.argv)