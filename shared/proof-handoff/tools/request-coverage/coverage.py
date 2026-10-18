#!/usr/bin/env python3
"""Check an independent state request before verifying an Ethereum proof set."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'coverage_proof_set', HERE.parent / 'proof-set' / 'proof_set.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
w = p.w
MAX_REQUEST = 16_384


def load_request(path):
    """Load a bounded, duplicate-key-free caller request from this workspace."""
    with w.workspace_path(path).open('rb') as stream:
        raw = stream.read(MAX_REQUEST + 1)
    w.require(len(raw) <= MAX_REQUEST, 'request exceeds 16 KiB limit')
    return w.parse_json(raw), hashlib.sha256(raw).hexdigest()


def request_map(request):
    p.exact_keys(request, ('format', 'accounts'))
    w.require(request['format'] == 'proof-request/1', 'unsupported request format')
    rows = request['accounts']
    w.require(isinstance(rows, list) and 1 <= len(rows) <= p.MAX_ACCOUNTS,
              'request needs 1..32 accounts')
    result = {}
    for index, row in enumerate(rows):
        p.exact_keys(row, ('address', 'slots', 'code'))
        address = w.hex0(w.hex_data(row['address'], 20, f'request account {index} address'))
        w.require(address not in result, 'duplicate requested account')
        slots = row['slots']
        w.require(isinstance(slots, list) and len(slots) <= 64,
                  f'request account {index}: at most 64 slots allowed')
        numbers = [w.slot_number(slot) for slot in slots]
        w.require(len(numbers) == len(set(numbers)), 'duplicate requested slot')
        w.require(type(row['code']) is bool, 'request code must be boolean')
        result[address] = {'slots': set(numbers), 'code': row['code']}
    return result


def manifest_map(manifest):
    p.check_manifest(manifest)
    return {
        w.hex0(w.hex_data(row['address'], 20)): {
            'slots': {w.slot_number(slot) for slot in row['slots']},
            'code': 'code' in row,
        }
        for row in manifest['accounts']
    }


def check_coverage(request, manifest):
    """Reject omissions and extras independently of proof-set metadata/order."""
    wanted = request_map(request)
    supplied = manifest_map(manifest)
    w.require(set(wanted) == set(supplied), 'manifest account coverage differs from request')
    for address, expectation in wanted.items():
        w.require(expectation['slots'] == supplied[address]['slots'],
                  f'manifest storage-slot coverage differs for {address}')
        w.require(expectation['code'] == supplied[address]['code'],
                  f'manifest code coverage differs for {address}')
    return [
        {'address': address, 'slots': [hex(slot) for slot in sorted(row['slots'])],
         'code': row['code']}
        for address, row in sorted(wanted.items())
    ]


def verify(request, manifest, base, block_hash, request_sha256, manifest_sha256):
    coverage = check_coverage(request, manifest)
    proof = p.verify(manifest, base, block_hash, manifest_sha256)
    return {
        'format': 'request-coverage-result/1',
        'verified': True,
        'coverage': coverage,
        'requestSha256': request_sha256,
        'proofSet': proof,
        'trust': ('Coverage matches the separately supplied request and every proof matches '
                  'the supplied block hash. Authenticate the request and checkpoint independently.'),
    }


def check_digest(supplied, actual, label):
    if supplied is not None:
        w.require(w.hex_data(supplied, 32, label) == bytes.fromhex(actual),
                  f'{label} differs from expected')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('demo', help='offline real ZTO and ZTO/IMD pool proof coverage')
    check = sub.add_parser('verify', help='check a caller request and proof manifest')
    check.add_argument('request')
    check.add_argument('manifest')
    check.add_argument('--block-hash', required=True)
    check.add_argument('--request-sha256', help='separately obtained exact request digest')
    check.add_argument('--manifest-sha256', help='separately obtained exact manifest digest')
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            request_path = HERE / 'examples' / 'zto-and-pool-request.json'
            manifest_path = HERE.parent / 'proof-set/examples/zto-and-pool.json'
            trusted = p.a.DEMO_HASH
        else:
            request_path, manifest_path, trusted = args.request, args.manifest, args.block_hash
        request, request_digest = load_request(request_path)
        manifest, base, manifest_digest = p.load_manifest(manifest_path)
        if args.command == 'verify':
            check_digest(args.request_sha256, request_digest, 'request SHA-256')
            check_digest(args.manifest_sha256, manifest_digest, 'manifest SHA-256')
        result = verify(request, manifest, base, trusted, request_digest, manifest_digest)
        if args.command == 'demo':
            result['demo'] = ('Historical real ZTO and ZTO/IMD proofs; the fixed block hash '
                              'is an RPC observation, not an independently authenticated checkpoint.')
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except w.Invalid as error:
        print(json.dumps({'verified': False, 'error': str(error)}), file=sys.stderr)
        return 1
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        print(json.dumps({'verified': False, 'error': 'Unreadable or malformed request or proof set.'}),
              file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
