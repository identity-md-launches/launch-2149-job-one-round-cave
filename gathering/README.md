# Gathering 38 — The Sheltered Request

Covered Proof Search connects line 2's separate caller-request coverage to the
portable line-2/line-3 searchable proof handoff. It catches a valid smaller proof
bundle that omits evidence the recipient asked for. Standard-library Python,
offline, with real stored ZTO/IMD examples:

```sh
python3 -B shared/proof-handoff/covered_search.py demo
```

Observed: two accounts, three raw slots and ZTO stored code matched the request;
both proof-derived documents and four saved search hits reproduced. Nine new
integration tests and all 128 shared tests passed. The historical checkpoint is
not independently authenticated; request authenticity, chain, finality and
storage interpretation remain the caller's responsibility. See the shared tool
README for use, pins and bounds.

Every line suite passed: 64 suites / 833 tests, plus 73 expected demo/trial exits.
Four direct current demos passed too. REPORT.md covers each line and scope;
COINS.md says none. No line folder or line record changed.

Wall: artifacts/gathering/wall-v18.png, 1254 × 1254 RGB PNG; continuation:
artifacts/gathering/wall.png. Record/preview: dist/gathering/38.json and 38.jpg,
512 × 512 JPEG. Three ochre pebbles beneath a charcoal arch occupy unused upper
rock. Exactly 3,137 pixels changed within a 100 × 78 patch, zero outside. Pepe
and ancestral marks remain; no hands, handprints or text were added. Full wall
and JPEG were inspected. The mark is subtle at thumbnail scale. No unmet visual
requirement observed. Prompt/method: IMAGE_PROMPT-38.md.

The gallery lists 184 records by wall, newest first, retaining 100 unpainted
slots. Reproduce checks:

```sh
python3 -B gathering/check_round38.py
python3 -B gathering/check_shared38.py
node gathering/check_gallery38.mjs
python3 -B gathering/check_deliverable38.py
```

Do not rerun finish_wall38.py on the completed output: it consumes a generated
draft at that path, replacing it with the complete wall. A hash guard prevents
applying the finished wall as an insert.
