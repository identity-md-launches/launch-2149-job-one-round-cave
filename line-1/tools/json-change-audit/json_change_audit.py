#!/usr/bin/env python3
"""Read-only structural JSON change retention review for four workspace trees."""
import argparse
from decimal import Decimal, DecimalException
import importlib.util
import json
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location(
    'json_audit_tree', Path(__file__).resolve().parents[1] / 'tree-review' / 'tree_review.py')
tree = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tree)
MISSING = object()
SIDES = ('base', 'ours', 'theirs', 'candidate')
LIMITS = [
    'JSON object members are compared structurally; arrays and type replacements are atomic.',
    'Conflicting branch expectations always require review, even if candidate chooses one.',
    'Only branch changes are checked; unrelated candidate edits and non-JSON contents are not audited.',
    'No semantic correctness, approval, rename tracking, formatting or author authentication.',
    'Stable trusted workspace trees required; reads are bounded but not atomic.',
    'Pointers expose member names. Reports omit values; manifests are not confidentiality.']


def parse(text):
    if text is None:
        return MISSING
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON object member')
            result[key] = value
        return result
    def constant(value):
        raise ValueError('non-finite JSON number')
    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_int=Decimal,
                           parse_float=Decimal, parse_constant=constant)
    except DecimalException as error:
        raise ValueError('unsupported JSON number exponent') from error
    budget = [0]
    def bounded(item, depth):
        budget[0] += 1
        if depth > 64 or budget[0] > 50000:
            raise ValueError('JSON exceeds depth 64 or 50000 nodes')
        if isinstance(item, dict):
            for child in item.values():
                bounded(child, depth + 1)
        elif isinstance(item, list):
            for child in item:
                bounded(child, depth + 1)
    bounded(value, 0)
    return value


def equal(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    return a == b


def changes(base, branch, path=()):
    if equal(base, branch):
        return []
    if isinstance(base, dict) and isinstance(branch, dict):
        return [change for key in sorted(base.keys() | branch.keys())
                for change in changes(base.get(key, MISSING), branch.get(key, MISSING), path+(key,))]
    return [(path, branch)]


def lookup(value, path):
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return MISSING
        value = value[key]
    return value


def pointer(path):
    return ''.join('/' + key.replace('~', '~0').replace('/', '~1') for key in path)


def audit(texts):
    base, ours, theirs, candidate = map(parse, texts)
    edits = [changes(base, branch) for branch in (ours, theirs)]
    maps = [dict(branch) for branch in edits]
    conflicts = [set(), set()]
    # Edit paths within one branch are prefix-free. Check each opposite
    # ancestor in O(depth) dictionary probes rather than all edit pairs.
    for index, branch in enumerate(edits):
        for path, expected in branch:
            for length in range(len(path)+1):
                ancestor = path[:length]
                if ancestor in maps[1-index]:
                    other = maps[1-index][ancestor]
                    if not equal(lookup(other, path[length:]), expected):
                        conflicts[index].add(path)
                        conflicts[1-index].add(ancestor)
    rows = []
    for index, branch in enumerate(edits):
        for path, expected in branch:
            incompatible = path in conflicts[index]
            retained = equal(lookup(candidate, path), expected)
            rows.append({'side': SIDES[index+1], 'pointer': pointer(path),
                         'operation': 'delete' if expected is MISSING else 'set',
                         'retained': retained, 'branch_conflict': incompatible,
                         'status': 'checked' if retained and not incompatible else 'review'})
    return {'status': 'review' if any(r['status'] == 'review' for r in rows) else 'checked',
            'changes': rows}


def inspect(sources):
    if len(sources) != 4:
        raise ValueError('four trees required')
    files = set().union(*(set(s['files']) for s in sources))
    dirs = set().union(*(s['directories'] for s in sources))
    collisions = files & dirs
    rows = []
    for path in sorted(files):
        if any(path == c or path.startswith(c+'/') for c in collisions):
            rows.append({'path': path, 'status': 'blocked', 'reason': 'file/directory collision'})
        elif not path.lower().endswith('.json'):
            rows.append({'path': path, 'status': 'skipped'})
        else:
            try:
                rows.append({'path': path, **audit([s['files'].get(path) for s in sources])})
            except (ValueError, RecursionError) as error:
                rows.append({'path': path, 'status': 'invalid',
                             'reason': 'Invalid or unsupported JSON: ' + str(error)})
    return {'schema': 'json-change-audit/v1',
            'needs_review': any(r['status'] in ('review', 'blocked', 'invalid') for r in rows),
            'inputs': {side: tree.manifest(source) for side, source in zip(SIDES, sources)},
            'files': rows, 'limits': LIMITS}


def from_directories(paths):
    if len(paths) != 4:
        raise ValueError('four directories required')
    budget = [0]
    return inspect([tree.snapshot(path, budget) for path in paths])


def demo():
    base = '{"review":{"required":false},"obsolete":null}'
    ours = '{"review":{"required":true},"obsolete":null}'
    theirs = '{"review":{"required":false}}'
    return {'retained': audit([base, ours, theirs, '{"review":{"required":true}}']),
            'lost_edit': audit([base, ours, theirs, theirs]),
            'restored_deletion': audit([base, ours, theirs, ours]), 'limits': LIMITS}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='*', help='BASE OURS THEIRS CANDIDATE directories')
    parser.add_argument('--demo', action='store_true')
    args = parser.parse_args(argv)
    if (args.demo and args.paths) or (not args.demo and len(args.paths) != 4):
        parser.error('provide four directories or --demo')
    try:
        report = demo() if args.demo else from_directories(args.paths)
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        print('json-change-audit: ' + ascii(str(error)), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=True, indent=2))
    if args.demo:
        return 0 if [report[k]['status'] for k in ('retained', 'lost_edit', 'restored_deletion')] == ['checked', 'review', 'review'] else 1
    return 1 if report['needs_review'] else 0


if __name__ == '__main__':
    sys.exit(main())
