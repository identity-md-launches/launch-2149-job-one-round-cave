#!/usr/bin/env python3
"""Count distinct reachable dependency selections in a bounded finite catalog."""
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys

CHECKER = Path(__file__).resolve().parent.parent / 'exhaustive-audit/audit.py'
if not CHECKER.is_relative_to(Path.cwd().resolve()):
    raise RuntimeError('run from the workspace containing the tools')
spec = importlib.util.spec_from_file_location('census_checker', CHECKER)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
fmt = checker.fmt


def census(data, max_assignments=10000):
    if type(max_assignments) is not int or not 1 <= max_assignments <= 1000000:
        raise fmt.Invalid('max_assignments must be an integer from 1 to 1000000')
    packages, roots = fmt.validate(data)
    possible, todo = set(), list(roots)
    while todo:
        p = todo.pop()
        if p in possible:
            continue
        possible.add(p)
        for deps in packages.get(p, {}).values():
            todo.extend(deps)
    names = sorted(possible)
    domains, total = [], 1
    for p in names:
        versions = sorted(packages.get(p, {}), key=fmt.version)
        domain = ([v for v in versions if checker.matches(v, roots[p])]
                  if p in roots else [None] + versions)
        domains.append(domain)
        total *= len(domain)
    # Include unreachable catalog releases as zero observations. Absence counts
    # are derived at the end, rather than updated for each candidate assignment.
    counts = {p: {v: 0 for v in sorted(releases, key=fmt.version)}
              for p, releases in sorted(packages.items())}
    checked, solutions, witnesses = 0, 0, []
    for values in itertools.product(*domains):
        if checked == max_assignments:
            break
        checked += 1
        supplied = {p: v for p, v in zip(names, values) if v is not None}
        reached = checker.assignment(packages, roots, supplied)
        if reached is None or reached != supplied:
            continue
        # Requiring supplied == reachable prevents irrelevant package choices
        # from counting the same solution multiple times; no solution set needed.
        solutions += 1
        if len(witnesses) < 2:
            witnesses.append(reached)
        for p, v in reached.items():
            counts[p][v] += 1
    complete = checked == total
    rows = {}
    for p in sorted(set(packages) | possible):
        versions = counts.get(p, {})
        absent = solutions - sum(versions.values())
        row = {'versions': versions, 'absent': absent}
        if complete and solutions:
            row['forced'] = next((v for v, count in versions.items()
                                  if count == solutions), None)
            row['always_absent'] = absent == solutions
        rows[p] = row
    classification = ('unsatisfiable' if solutions == 0 else
                      'unique' if solutions == 1 else 'multiple') if complete else (
                      'multiple' if solutions >= 2 else 'unknown')
    payload = {'packages': packages, 'roots': roots}
    return {'method': 'finite-solution-census-v1',
            'status': 'complete' if complete else 'inconclusive',
            'classification': classification,
            'count_kind': 'exact' if complete else 'lower-bound',
            'compatible_selections': solutions,
            'catalog_sha256': hashlib.sha256(json.dumps(payload, sort_keys=True,
                separators=(',', ':')).encode()).hexdigest(),
            'candidate_assignments': total, 'checked_assignments': checked,
            'max_assignments': max_assignments,
            'packages': rows, 'witnesses': witnesses}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalog', help='workspace-local JSON or demo')
    parser.add_argument('--max-assignments', type=int, default=10000)
    args = parser.parse_args(argv)
    try:
        path = (CHECKER.parent.parent / 'conflict-core/examples/requests-conflict.json'
                if args.catalog == 'demo' else args.catalog)
        data = fmt.load(path)
        if args.catalog == 'demo':
            # Explicit illustrative requirements; historical release maps untouched.
            data = dict(data, roots={'requests': '*', 'urllib3': '<2'})
        result = census(data, args.max_assignments)
        if args.catalog == 'demo':
            result['demonstration_roots'] = data['roots']
        code = 0 if result['status'] == 'complete' else 3
    except (fmt.Invalid, OSError, UnicodeError, ValueError, TypeError, RecursionError) as exc:
        result, code = {'status': 'invalid', 'error': str(exc)}, 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return code


if __name__ == '__main__':
    sys.exit(main())
