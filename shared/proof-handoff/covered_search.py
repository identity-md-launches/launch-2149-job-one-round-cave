#!/usr/bin/env python3
"""Verify a searchable proof handoff against an independently retained request."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

import handoff as h

c = h.load('covered_handoff_request', 'tools/request-coverage/coverage.py')
DEMO_REQUEST = h.HERE / 'tools/request-coverage/examples/zto-and-pool-request.json'


def check(request, manifest, block_hash, bundle, expected_bundle,
          expected_request, expected_manifest, scratch='test/scratch', query=None):
    """Fail before reporting success if intent, proofs, corpus or receipt differs."""
    for label, pin in (('request', expected_request), ('manifest', expected_manifest)):
        if not h.b.receipt.valid_hash(pin):
            raise ValueError(label + ' pin must be 64 lowercase hex characters')
    wanted, request_digest = c.load_request(request)
    if request_digest != expected_request:
        raise ValueError('request pin mismatch')
    supplied, _, manifest_digest = c.p.load_manifest(manifest)
    if manifest_digest != expected_manifest:
        raise ValueError('manifest pin mismatch')
    coverage = c.check_coverage(wanted, supplied)
    result = h.check(manifest, block_hash, bundle, expected_bundle, scratch,
                     expected_manifest=expected_manifest, query=query)
    # Compare exact bytes, not just a normalized map; ordinary changes while
    # checking cannot silently publish a result for a different caller request.
    _, final_request_digest = c.load_request(request)
    _, _, final_manifest_digest = c.p.load_manifest(manifest)
    if (final_request_digest, final_manifest_digest) != (request_digest, manifest_digest):
        raise ValueError('request or manifest changed during handoff check')
    return {'format': 'covered-proof-search/v1', 'verified': True,
            'request_sha256': request_digest, 'coverage': coverage,
            'handoff': result,
            'limits': ['Authenticate the caller request and checkpoint independently.',
                       'Coverage is exact accounts, raw slots and code presence; not storage interpretation.',
                       'Historical proof results are not current state, price or payment authorization.',
                       'Keep inputs static; rereads are not an atomic snapshot.']}


def demo(scratch='test/scratch'):
    _, request_digest = c.load_request(DEMO_REQUEST)
    with tempfile.TemporaryDirectory(dir=h.scratch_parent(scratch), prefix='covered-search-') as tmp:
        output = Path(tmp) / 'bundle.json'
        made = h.pack(h.DEMO_MANIFEST, h.p.a.DEMO_HASH, 'storage value', output, scratch)
        result = check(DEMO_REQUEST, h.DEMO_MANIFEST, h.p.a.DEMO_HASH, output,
                       made['bundle_sha256'], request_digest,
                       made['manifest_sha256'], scratch)
    result['demo'] = 'Real historical ZTO and ZTO/IMD proofs; inherited RPC checkpoint, not consensus authentication.'
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch-parent', default='test/scratch')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('demo')
    verify = sub.add_parser('check')
    verify.add_argument('request')
    verify.add_argument('manifest')
    for flag in ('block-hash', 'bundle', 'expected-sha256', 'request-sha256', 'manifest-sha256'):
        verify.add_argument('--' + flag, required=True)
    verify.add_argument('--query')
    args = parser.parse_args(argv)
    try:
        result = demo(args.scratch_parent) if args.command == 'demo' else check(
            args.request, args.manifest, args.block_hash, args.bundle,
            args.expected_sha256, args.request_sha256, args.manifest_sha256,
            args.scratch_parent, args.query)
        print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError, RecursionError, OverflowError):
        print(json.dumps({'verified': False, 'error':
              'Request coverage, retained pins, proofs, corpus or search receipt did not verify.'}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
