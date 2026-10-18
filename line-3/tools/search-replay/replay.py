#!/usr/bin/env python3
"""Reproduce saved ranked search results against an explicitly supplied snapshot."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys

ENGINE = Path(__file__).absolute().parents[1] / 'evidence-search' / 'search.py'
spec = importlib.util.spec_from_file_location('replay_search', ENGINE)
search = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search)


def replay(index, saved, limit):
    """Check the complete deterministic result, including ordering and omissions.

    limit is supplied separately: the ancestor result does not record it.
    A historical source_verified flag is validated as boolean but never trusted.
    """
    if type(limit) is not int or not 1 <= limit <= 50:
        raise search.SearchError('limit must be an integer between 1 and 50')
    if not isinstance(saved, dict) or saved.get('format') != 'evidence-search-results/v1':
        raise search.SearchError('expected evidence-search-results/v1')
    if type(saved.get('require_all')) is not bool:
        raise search.SearchError('require_all must be boolean')
    if not isinstance(saved.get('hits'), list) or len(saved['hits']) > 50:
        raise search.SearchError('invalid saved hits')
    normalized = copy.deepcopy(saved)
    for hit in normalized['hits']:
        if not isinstance(hit, dict) or type(hit.get('source_verified')) is not bool:
            raise search.SearchError('each hit needs a boolean source_verified')
        hit['source_verified'] = False
    expected = search.search_snapshot(index, saved.get('query'), limit, saved['require_all'])
    # Canonical JSON avoids Python's True == 1 equality and checks every field.
    canonical = lambda value: json.dumps(value, sort_keys=True, ensure_ascii=False,
                                         separators=(',', ':'), allow_nan=False)
    try:
        reproduced = canonical(normalized) == canonical(expected)
    except (ValueError, TypeError, UnicodeError):
        raise search.SearchError('saved result is not finite JSON') from None
    return {'format': 'evidence-search-replay/v1', 'reproduced': reproduced,
            'limit': limit, 'expected_hits': len(expected['hits']),
            'saved_hits': len(saved['hits']), 'current_sources_checked': False,
            'scope': 'Deterministic snapshot ranking and citations; not truth or live freshness.'}


def load_saved(filename):
    raw = search.read_bytes(search.workspace_path(filename), search.MAX_INDEX_BYTES)
    def invalid(value):
        raise search.SearchError('non-finite JSON constant')
    try:
        return json.loads(raw, object_pairs_hook=search.reject_duplicates, parse_constant=invalid)
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        raise search.SearchError('saved result must be UTF-8 JSON') from None


def demo():
    root = ENGINE.parent / 'examples' / 'docs'
    index = search.build_index(root)
    saved = search.search(index, 'ZTO token decimals', root, limit=3)
    good = replay(index, saved, 3)
    altered = copy.deepcopy(saved)
    altered['hits'][0]['line_start'] += 1
    bad = replay(index, altered, 3)
    return {'historical_zto_result': good, 'altered_line_citation': bad}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('demo')
    check = sub.add_parser('check')
    check.add_argument('index')
    check.add_argument('result')
    check.add_argument('--limit', type=int, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo()
            status = 0
        else:
            result = replay(search.load_index(args.index), load_saved(args.result), args.limit)
            status = 0 if result['reproduced'] else 1
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return status
    except (search.SearchError, OSError, RecursionError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
