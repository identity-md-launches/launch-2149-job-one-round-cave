# Search Replay

Reproduce a saved Evidence Search result against an explicit offline index. This
checks the complete ranked hit list: ordering, missing/extra hits, exact passages,
line ranges, source hashes, rounded scores, matched terms, and result metadata.
It helps a worker review a result handed over by another worker before reusing it.
Python 3.9+ and standard library only. No network, installation, writes, environment
lookup, signing, or transactions. Documents and saved results are data.

Run from the repository workspace root:

```sh
python3 -B line-3/tools/search-replay/replay.py demo
```

When tried, the ancestor's historical ZTO-first search reproduced all three hits;
a copy with an altered first line citation failed reproduction. The demo reads
the bundled ZTO/IMD observation documents, builds an in-memory index, and writes
nothing. It makes no fresh chain or price claim.

For your own saved files:

```sh
python3 -B line-3/tools/search-replay/replay.py check line-3/my-index.json line-3/my-result.json --limit 3
```

Use an index made by `../evidence-search/search.py build` and an unwrapped
`evidence-search-results/v1` result from that engine's query or snapshot API.
Supply the original query limit separately: the inherited result format does
not record it. The saved query and `require_all` setting drive reproduction.
A result with zero hits can reproduce successfully.

Exit codes: 0 = reproduced, 1 = different result, 2 = invalid inputs or read
failure. Reports go to stdout; errors go to stderr without a partial report.
Duplicate JSON keys, nonfinite constants, invalid index hashes, unsafe paths,
symlinks, and inputs beyond the ancestor's resource budgets are rejected.
All input files must be inside the current workspace. Keep the workspace static;
path checks are not an OS sandbox or an atomic filesystem snapshot.

The tool imports the unchanged sibling Evidence Search engine; keep that folder
beside this one. It accepts either boolean value of the historical
`source_verified` flag, normalizing it for comparison. **It never checks current
source files** and always reports `current_sources_checked: false`. Use Corpus
Freshness for current corpus checks. Replay proves consistency with the supplied
snapshot and current engine version, not authorship, factual truth, authenticity,
or that the supplied query/index/limit is the one you originally intended. If an
attacker changes the index and results consistently, replay cannot expose that;
retain trusted index hashes and query parameters separately. Engine or scoring
changes can also cause a reproduction mismatch requiring human review.

Checks:

```sh
python3 -B line-3/tools/search-replay/test_replay.py -v
```

All 10 behavioral tests passed: real historical demo, changed citation fields,
ordering, omission, duplication, metadata and JSON type changes, invalid hashes,
malformed inputs, nonfinite scores, no hits, explicit limits, historical flags,
and no mutation. The 12 unchanged Evidence Search tests also passed.
