# Proof Handoff

## Gathering 38: caller-request coverage

`covered_search.py` joins line 2's Request Coverage to this line-2/line-3
handoff. A valid smaller proof set can otherwise omit something the recipient
asked for. This checker requires a separate caller request and retained exact
request and manifest hashes, checks account/slot/code coverage, then re-verifies
the proofs, complete bundled corpus and saved ranked search. It rereads both
request and manifest before reporting success.

```sh
python3 -B shared/proof-handoff/covered_search.py demo
```

Observed locally: two accounts, three raw slots and ZTO stored code matched
the historical request; proofs at block **26,212,390**, both generated source
documents and all four search hits reproduced. Public historical source:
https://ethereum-rpc.publicnode.com. No fresh RPC was made. The fixed demonstration
checkpoint is an inherited RPC observation, not independent consensus trust.

To check the shipped bundle with the shipped historical request:

```sh
python3 -B shared/proof-handoff/covered_search.py check shared/proof-handoff/tools/request-coverage/examples/zto-and-pool-request.json shared/proof-handoff/tools/proof-set/examples/zto-and-pool.json --block-hash 0x38dc4deb12174972d332cc1f95008b25ea87434f420ce0a51938e1b28755e9dc --bundle shared/proof-handoff/examples/zto-proof-bundle.json --expected-sha256 57ba25ab26d159efaa1c07dc28c1dc0a0e0914049df9646b46374fd04621089f --request-sha256 fe73c071e039b1c7202b72bb21b5b767b796ba94e85975aa1847034a0fdbad0b --manifest-sha256 a4e9d3fb56c90bf1202ac3d53b8ce7c557febe06d88581a9430a2f6a59f14e8f
```

For your own evidence, replace all paths and pins with reviewed values. The
request format is documented in `tools/request-coverage/README.md`; its copied
source and example are pinned in `COVERAGE-PROVENANCE.json`. Keep this entire
folder together. No line folder or external Python dependency is needed.
`--query TEXT` optionally performs a new search after receipt reproduction.
`--scratch-parent DIR` goes before the subcommand; default `test/scratch`.
Temporary restoration directories are removed on return. The checker never
overwrites the supplied bundle, request or manifest. Exit 0 means all checks
passed (including a valid no-hit query); exit 2 means failure, with error JSON
only on stderr. It never signs, sends, pays, posts or reads configuration.

Nine new integration tests passed, including a genuinely verified subset bundle
that coverage rejects, omitted slots/code, changed pins and caller request,
forged rehashed excerpts, invalid requests, no partial CLI success and a demo
copied into an isolated folder with no line folders. Reproduce with:

```sh
python3 -B -m unittest discover -s shared/proof-handoff -p 'test_covered_search.py' -v
```

The caller must authenticate the request, retained hashes, intended chain and
checkpoint independently. Hashes delivered beside untrusted inputs authenticate
nothing. Exact coverage says nothing about choosing the right address or storage
layout. The inherited resource bounds below apply, with an additional 16 KiB
request limit (32 accounts, 64 slots each). Static workspace inputs are required;
rereads do not establish an atomic snapshot or stop path replacement races.
Historical raw state is not a current quote, balance interpretation or approval.

Carry reproducible, cited Ethereum proof results between offline workers. This
joins line 2's Proof Set with line 3's Evidence Bundle. Python 3.10+ and the
standard library only; this entire folder is portable without the line folders.
All inherited implementations and fixtures are copied unchanged under `tools/`;
`PROVENANCE.json` records their exact source paths and SHA-256 values.

From the workspace root:

```sh
python3 -B shared/proof-handoff/handoff.py demo
```

This verifies the real historical ZTO account, its 1,287 runtime bytes, and the
ZTO/IMD PoolManager storage proof at one execution header. It then bundles two
documents generated solely from verified results, restores them temporarily,
reproduces the saved search, and returns exact line citations. When tried it
reported `verified: true`, `accounts: 2`, `corpus_matches_proofs: true` and
`receipt_reproduced: true`. The first hit includes the pool's raw slot/value.
It is not a decoded price, token balance, current chain read or source audit.

The demo writes only self-created temporary directories under `test/scratch/`
and removes them on return. Set `--scratch-parent WORKSPACE_DIRECTORY` **before**
the subcommand to use another workspace location. Parent directories may be
created and remain. No environment/config discovery, network, credentials,
wallet, transaction, payment or document execution is involved.

## Check the included handoff

```sh
python3 -B shared/proof-handoff/handoff.py check shared/proof-handoff/tools/proof-set/examples/zto-and-pool.json --block-hash 0x38dc4deb12174972d332cc1f95008b25ea87434f420ce0a51938e1b28755e9dc --manifest-sha256 a4e9d3fb56c90bf1202ac3d53b8ce7c557febe06d88581a9430a2f6a59f14e8f --bundle shared/proof-handoff/examples/zto-proof-bundle.json --expected-sha256 57ba25ab26d159efaa1c07dc28c1dc0a0e0914049df9646b46374fd04621089f
```

Add `--query 'storedCodeKind'` to ask a new question after reproducing the saved
search. A valid empty result remains successful verification. Exit 0 means all
checks completed, including an empty search; exit 2 means invalid input or a
failed check. Failure prints only an error JSON on stderr, no partial success.

These pins reproduce the included historical example. The block hash was
inherited from an RPC observation, not independently authenticated consensus.
Public source: https://ethereum-rpc.publicnode.com. The included mainnet block
number, decoded from the verified header, is **26,212,390**.

## Create your own handoff

Use Proof Set's manifest format, reviewing its exact accounts, complete raw slot
sets and optional code expectations. `pack MANIFEST --block-hash HASH --query
QUERY --output NEW_JSON` verifies all proofs before creating a bundle. It accepts
`--limit` (1–50), `--all`, and an optional exact-file `--manifest-sha256` pin.
Choose a new output filename; existing files are never replaced. Transfer this
tool folder, the bundle, manifest, header, witnesses and code files, retaining
their relative paths. No code dependencies need installing.

The recipient uses `check` with the same reviewed manifest and independently
retained block/manifest/bundle pins. The optional manifest pin hashes exact file
bytes; the bundle pin hashes canonical JSON, so formatting alone does not change
it. Pins received only alongside untrusted inputs supply no authentication.

Each check re-verifies the entire proof set, compares **all** embedded documents
against freshly generated proof results, and reproduces every saved search field
on temporary restored sources. A valid hash alone cannot turn a forged excerpt
or prose assertion into a proof result. Search terms and source text remain data.

## Checks and limits

```sh
python3 -B shared/proof-handoff/test_handoff.py -v
```

Eleven tests passed: real proofs/citations/new queries, wrong checkpoint and
pins, rehashed forged excerpts, rehashed changed documents, missing account
documents, no-hit receipts, exclusive output/input immutability, scratch cleanup,
CLI failure output, and relocation into a workspace containing no line folders.

Proof Set's bounds remain: 32 accounts, 64 slots per account, 64 KiB manifest,
bounded headers/trie nodes/code. Evidence Bundle retains its 24 MB envelope,
12 MB receipt and 8 MB corpus limits. Workspaces must stay static; there is no
atomic snapshot or defense against concurrent filesystem replacement. I/O
failure during exclusive bundle creation can leave a partial new output; choose
a new filename after inspecting it. Scratch cleanup removes only this process's
new temporary directories. The original source corpus is never modified.

The caller must authenticate checkpoint chain, canonicality and finality. These
tools do not verify consensus, execute code, interpret storage layouts, follow
proxy targets or establish factual truth. Exact search reproduction depends on
the retained tool versions. ZTO and its existing IMD pair supply the real example;
no new coin or deployment is needed.
