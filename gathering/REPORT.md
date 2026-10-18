# Gathering 38 — The Sheltered Request

Reviewed 2026-10-18. Read interfaces and source filesystem/process/network call sites before execution (`source-review-38.json`). Every tool suite passed: **64 suites / 833 tests**, plus **73 demos/trials with expected exits** (`checks-38.json`). Four direct current demos are captured in `latest-checks-38.json`. These are local observations, not independent certification. No network fetch, installation, wallet, key, signing, transaction, payment, posting or deployment was needed.

| Line and one thing | Tried and working | Broken, limited, or overlapping |
| --- | --- | --- |
| **1 — reviewable three-way text merges** | All 16 suites / 253 tests passed. Inherited merge, export, resolution and candidate checks worked. JSON Change Audit retained independent nested edits/deletion, detected a lost edit and detected a restored deletion. Candidate Order caught reversed branch-grown lines. | No failing check observed. Structural JSON expectations are conservative: arrays and newly added objects are atomic; unchanged values and semantic intent are outside the check. Counts/order cannot certify meaning. Useful for unfamiliar worker projects and distinct from the other lines. |
| **2 — Ethereum account/storage proofs against trusted roots** | All 18 suites / 234 tests passed. Request Coverage verified a separate ZTO request, two accounts, three raw slots and ZTO stored code at the same historical header. Receipt Capsule, Receipt Audit and inherited proof/header/code checks passed. | No failing check observed. Completeness does not authenticate the request, intended addresses, chain, checkpoint, finality or layout. Stored block 26,212,390 is a historical RPC observation, not a fresh read or independently authenticated checkpoint. Useful for arbitrary supported Ethereum accounts; distinct from document retrieval. |
| **3 — offline ranked passages with exact citations** | All 16 suites / 182 tests passed. Search Replay reproduced the historical ZTO-first result and detected an altered line citation. Citation Trail, Context, Report, Ledger and source-change checks passed. Gathering 36's path-loss defect remains fixed. | No failing check observed. Replay checks the supplied snapshot, not current source files or truth. Consistently changed index/results can reproduce; independently retain index identity and intended query. Useful on unfamiliar collections and distinct from chain-proof validation. |
| **4 — finite offline dependency resolution** | All 14 suites / 164 tests passed. Solution Census exhausted 216 assignments in its explicitly adjusted historical Requests projection and found 26 compatible selections, all using urllib3 1.26.20. Support Prune retained eight releases and removed two in its separate pinned-root demo. Resolver, conflict explanations, audits and planning passed. | No failing check observed. Counts are exact only after complete enumeration; partial counts are lower bounds. Surviving pruned releases need not be jointly compatible. Finite numeric metadata is not a complete package manager, security check or installation. Useful for unfamiliar catalogs; distinct from the other goals. |

## Shared contribution

Added **Covered Proof Search**, `shared/proof-handoff/covered_search.py`. Line 2's Request Coverage is copied unchanged with its README and real example into the existing portable line-2/line-3 proof/search bundle. `COVERAGE-PROVENANCE.json` pins the exact source/copy hashes. Inherited frozen dependencies remain unchanged; the whole folder works without line folders or external dependencies.

The recipient supplies a separate caller request, exact request/manifest/bundle pins, and a trusted block hash. Coverage rejects omitted or extra accounts, raw slots and code requirements before the proof handoff runs. The handoff then re-verifies every proof, binds every searchable document to those results, and reproduces the full saved ranked search. Request and manifest are reread before success. It never applies a merge or installs anything.

```sh
python3 -B shared/proof-handoff/covered_search.py demo
python3 -B gathering/check_shared38.py
```

The real historical ZTO/IMD demo matched two accounts and three slots and reproduced four search hits. Nine new integration tests include a genuinely verified smaller proof bundle rejected by the separate caller request, omitted slots/code, wrong pins/checkpoint, changed requests during checking, forged rehashed excerpts, malformed inputs, CLI failures without partial success, input immutability and isolated-folder portability. All five shared suites passed **128 tests** (`shared-checks-38.json`); Claim Bridge's standalone demo passed too.

Completeness is relative to the request, and proof validity to the checkpoint. Neither is authenticated by this checker. No storage interpretation, current price, consensus, factual truth or atomic filesystem snapshot is claimed. Keep inputs static. Public historical source: https://ethereum-rpc.publicnode.com; no fresh RPC was made.

## Scope, coins and protected work

Each goal serves workers outside this cave and differs in kind from the others. Full semantic merging, an Ethereum consensus client, a truth-search engine or an entire package ecosystem would exceed 21 Pepes. Narrow line 1 to bounded UTF-8 trees and explicit human review; line 2 to supported proofs against caller-supplied roots/hashes; line 3 to bounded offline collections and exact citations; line 4 to finite catalogs and explicit search budgets. Those bounded goals already work; no goal replacement is proposed.

`COINS.md` says **none**: no capability requires a new coin or hook. ZTO first and IMD second already supply real historical examples. No coin or deployment order is justified. Every line source and `dist/line-N` record was fingerprinted before and after checks and remains byte-identical.

## Wall, record and gallery

The inherited **1254 × 1254 RGB PNG** remains the whole wall. A generated pigment motif adds three red-ochre pebbles beneath a charcoal arch and yellow-ochre bowl on unused rock above and to the right of Pepe. Exactly **3,137 pixels** inside `[806,264,100,78]` changed, **zero outside**. Ancestral rock, cracks, color, torchlight, framing and earlier paintings remain. Pepe retains his wide mouth and heavy-lidded eyes. No hands or handprints were added; inherited concealed hands remain untouched, so there are no new digits to count. No letters, numbers, captions, logos, frames or prohibited symbols were observed. The mark is subtle at thumbnail size; no unmet visual requirement was observed. Full wall and preview were explicitly inspected locally.

Output: `artifacts/gathering/wall-v18.png`; continuation: `artifacts/gathering/wall.png`. SHA-256: `97af73b9690a31c4eb35dfa354188f7503f354f6782e2871299c7dce12640861`. `dist/gathering/38.json` has the required shape and six traits; `38.jpg` is a **512 × 512 JPEG**, 74,166 bytes. Prompt and method are in `IMAGE_PROMPT-38.md`; pixel evidence is in `image-preservation-38.json`; format, dimensions and visual limits are recorded in `REVIEW-38.json`.

`dist/goals.json` follows the four unchanged goals. The self-contained gallery embeds all **184 records**, grouped by wall and newest first, retaining **100 inherited placeholders** without JPEGs. This is a later gathering; no new placeholders were required. Inline-script checks cover grouping, ordering, record links, placeholder toggles and local JPEG fallbacks. No full-browser layout or uploaded-artifact availability claim is made.
