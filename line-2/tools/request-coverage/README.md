# Request Coverage

Check a caller-authored list of Ethereum accounts, raw storage slots and code
requirements against a separately supplied Proof Set manifest. An omitted slot
can otherwise disappear from a seemingly successful proof report: the proof
verifier checks what its manifest names, not what the caller originally asked
for. This tool requires exact coverage first, then runs the unchanged Proof Set
verifier against a supplied execution block hash. Neither the request nor the
manifest can choose the trusted block hash.

From the repository root, run the real historical ZTO and ZTO/IMD pool example
offline with Python 3.9+ standard library only:

```sh
python3 -B line-2/tools/request-coverage/coverage.py demo
```

## What happened when tried

The bundled caller request covered ZTO's account, two raw slots and stored
code, plus the ZTO/IMD PoolManager account and pool slot0. The separate
Proof Set manifest supplied the historical witnesses. Both accounts and all
three slots verified against the same state root under block hash
`0x38dc4deb12174972d332cc1f95008b25ea87434f420ce0a51938e1b28755e9dc`.
Deleting either account, one slot or the code file from the manifest caused
coverage failure before any proof result was printed. Focused checks also
exercised extra slots, malformed requests and a wrong block hash. These are
real stored chain proofs from the inherited fixtures, but the example hash
is an RPC observation rather than an independently authenticated checkpoint.
It makes no current-state or price claim.

## Use with your own request

Create a caller-reviewed JSON file shaped like
`examples/zto-and-pool-request.json`. Its `accounts` list has 1 to 32 entries;
each has an address, 0 to 64 raw slots, and a boolean `code` saying whether
stored code bytes must be checked. Keep this request separate from the proof
provider's manifest. Then run:

```sh
python3 -B line-2/tools/request-coverage/coverage.py verify \
  line-2/tools/request-coverage/examples/zto-and-pool-request.json \
  line-2/tools/proof-set/examples/zto-and-pool.json \
  --block-hash 0x38dc4deb12174972d332cc1f95008b25ea87434f420ce0a51938e1b28755e9dc
```

The example command reproduces the historical trial. Supply an independently
authenticated block hash for real use. Optional `--request-sha256 0x...` and
`--manifest-sha256 0x...` check separately obtained exact-file digests. A
request digest copied only from the untrusted request file authenticates
nothing. The output includes both file digests, normalized coverage and the
full Proof Set result. Success is printed only after all proofs pass; exit 1
prints an error to stderr, and argument errors exit 2.

Unknown fields, duplicate JSON keys, duplicate accounts or slots, wrong JSON
types, missing or extra requested evidence, workspace-escaping input paths,
wrong headers, bad trie proofs and code-hash mismatches fail. Account order,
slot order and hex letter case do not affect coverage. Requests are limited to
16 KiB; Proof Set keeps its own manifest and witness limits. No network access,
installation, wallet, key, signing, transaction, payment or posting is needed.
Carry sibling `proof-set/`, `state-witness/`, `header-anchor/` and
`code-witness/` beside this folder. The offline demo also needs their historical
example files.

This checks completeness relative to the caller's request and proof validity
relative to the supplied hash. The caller remains responsible for the intended
addresses, storage layout, request authenticity, chain identity, checkpoint
authentication, canonicality, finality and freshness. Stored-code matching
does not establish source, ABI, proxy target or behavior.
