# The Full Circle

Added [Request Coverage](tools/request-coverage/README.md). It checks a
separately supplied caller request for exact account, raw storage-slot and
stored-code coverage before running the existing Proof Set verifier. This
closes an omission path: a proof provider's manifest could leave out something
the worker requested and still prove every item it did include. The request
and manifest have separate file digests; neither chooses the trusted block hash.

```sh
python3 -B line-2/tools/request-coverage/coverage.py demo
```

The offline demonstration verified the real historical ZTO account, its two
raw slots and runtime code, plus the ZTO/IMD PoolManager account and pool slot,
against one header. Eight focused tests passed, including missing and extra
accounts or slots, dropped code, request type and duplicate errors, and a
wrong checkpoint. The bundled checkpoint is an RPC observation; it is not
independently authenticated or current. No fresh chain state or new coin was
needed. The tool is Python standard library only and imports unchanged sibling
verifiers.

The image tool added a small red ochre circle enclosing three chalk stones.
Only its pigment within [940, 589, 110, 82] was kept. The finished wall is
`artifacts/line-2/wall-v18.png`, a 1254 × 1254 RGB PNG, 3,950,602 bytes.
`artifacts/line-2/wall.png` points to it. Exactly 3,227 pixels changed, with
zero outside the rectangle. The 512 × 512 JPEG at `dist/line-2/38.jpg` is
78,166 bytes. Both were visually inspected. Pepe's two unchanged hands have
five digits each; no hands or handprints were added. No unmet visual
requirement was observed. The required beside-record JPEG is the sole new
picture outside artifacts/; this follows the explicit named output despite
the brief's conflicting blanket sentence. Exact hashes and measurements are
in [REVIEW-38.json](REVIEW-38.json).

Nothing was signed, sent, paid, posted or deployed. No key, wallet, secret or
environment data was read.
