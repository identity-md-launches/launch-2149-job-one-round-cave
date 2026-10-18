# Solution Census

Count the distinct compatible, root-reachable version selections in a finite
catalog. Find whether a resolution is unique, see which releases are forced,
and distinguish an optional dependency from a mandatory one. This helps a worker
review whether a lock choice follows from requirements or selects one of many
possible outcomes. No packages are installed, imported or executed.

Run from the repository root with Python 3.9+ (standard library only):

```sh
python3 -B line-4/tools/solution-census/census.py demo
```

The demonstration exhausted **216 candidate assignments** and found **26 distinct
compatible selections** in the committed historical Requests metadata projection.
All 26 selected urllib3 1.26.20; chardet was absent from 24. Requests 2.25.1
occurred in two selections and the other two Requests releases each occurred in
12. The demonstration explicitly substitutes roots `requests: *` and
`urllib3: <2` into the stored Conflict Core snapshot; its release maps are
unchanged. These are finite metadata compatibility results, not installation,
security or version recommendations. No live metadata was fetched.

For your own workspace-local catalog:

```sh
python3 -B line-4/tools/solution-census/census.py path/to/catalog.json --max-assignments 10000
```

Use Offline Resolver's exact JSON schema and numeric conjunction grammar:
`packages` maps package names to versions to mandatory dependency constraints;
`roots` maps mandatory package names to constraints. Keep the adjacent
`exhaustive-audit/` and `offline-resolver/` folders. The demo also needs
`conflict-core/examples/requests-conflict.json`. Names normalize case and
punctuation; equivalent numeric release labels within a package are rejected.
The inherited loader rejects duplicate JSON keys, inputs over 1,000,000 bytes,
and paths or symlinks resolving outside the current workspace.

`compatible_selections` is exact only when `status` is `complete`; otherwise it
is a lower bound. `packages[p].versions[v]` counts selections containing that
release, and `absent` counts selections without the package. On partial results
these too are lower bounds, never probabilities. A package's version counts
plus absence equal the reported selection count. Unreachable catalog packages
are included with zero release counts. Missing possible targets are included
with an empty version map.

A complete, nonempty result also supplies `forced` (one version used in every
solution, else null) and `always_absent`. Neither field is emitted when no
solution exists or when enumeration is incomplete. Two witnesses suffice to
prove `classification: multiple` even during incomplete enumeration; one witness
does **not** prove uniqueness. Incomplete results with zero or one solution say
`unknown`. Complete results classify as `unsatisfiable`, `unique` or `multiple`.
Only the first two selections are stored as witnesses, bounding witness output.

Enumeration considers versions of all potentially reachable packages, with an
absence option for nonroots. It independently checks edges and root reachability
using Exhaustive Audit's iterative checker. Only assignments containing exactly
their reachable packages are counted, preventing multiplicity from irrelevant
versions. This does not call the resolver's search or its comparison predicate;
input grammar and the audit edge checker are reused rather than independently
certified. `catalog_sha256` binds canonical package names and sorted JSON,
including roots; it is not a signature or an artifact integrity guarantee.

`--max-assignments` accepts integers 1–1,000,000. The default is 10,000. Finishing
at exactly the budget is complete; an empty candidate domain proves zero solutions
without checking an assignment. Search is exponential; this limit does not bound
input validation, candidate-product arithmetic, memory, or wall-clock time.
There are no platform markers, extras, full PEP 440, artifact or security checks.
There is no random choice, network access, environment lookup, account access,
file writing, transaction, payment or deployment. Inputs are never modified.

Exit 0 means completed enumeration, **including unsatisfiable catalogs**;
exit 3 means incomplete enumeration; exit 2 means invalid input.

Checks:

```sh
python3 -B -m unittest discover -s line-4/tools/solution-census -p 'test_*.py' -v
```

The suite checks optional packages, deduplication, unreachable releases, missing
targets, cycles, zero domains, exact and partial budgets, normalization, immutable
inputs, CLI exits, numeric constraints, and the real stored demo. A separate small
raw-edge enumerator compares counts and package marginals on 300 seeded catalogs.
