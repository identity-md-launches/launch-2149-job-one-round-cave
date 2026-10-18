# JSON Change Audit

Review whether a separately supplied merge candidate retains both branches'
structural JSON changes. A syntactically valid result can silently restore a
removed member or lose a changed value. This tool identifies those losses by
JSON Pointer, without merging, writing, executing, or approving input documents.
It works on unfamiliar worker projects and uses Python's standard library only.

Run this offline demonstration from the workspace root:

```sh
python3 -B line-1/tools/json-change-audit/json_change_audit.py --demo
```

The demo exits 0 after showing a retained nested edit and deletion, a lost edit,
and a restored deletion. For your own stable workspace directories:

```sh
python3 -B line-1/tools/json-change-audit/json_change_audit.py BASE OURS THEIRS CANDIDATE
```

The JSON report includes exact-byte manifests of all four trees, per-file status,
and per-change side, escaped JSON Pointer, operation, retention and branch-conflict
flags. An empty pointer means the document root. Values are omitted, but member
names are visible; neither omission nor hashing is confidentiality. Exit 0 means
all audited expectations checked, 1 means review is needed (including invalid
JSON or path collisions), and 2 means input-tree or command-line failure.
Non-`.json` files are explicitly `skipped`; a pass does not audit their contents.

Policy: recurse only when both base and branch values are objects. Otherwise,
record the complete changed value as one expectation. Arrays, new objects,
removed objects, and type replacements are atomic. Compare each expectation
against the candidate at the same pointer. Missing files and members differ from
JSON null; Boolean values differ from numbers. Object ordering and whitespace
are ignored; array ordering matters. Decimal parsing avoids float rounding and
infinity overflow, so `1` and `1.0` compare equally while large distinct numbers
stay distinct. Duplicate members and nonstandard NaN/Infinity are rejected.
Each document is limited to 50,000 value nodes and depth 64.

Opposite-branch expectations at the same pointer or overlapping ancestor paths
must be compatible. All incompatible expectations require review even when the
candidate selects one side. Concurrent additions of different complete objects
can therefore require review even if a person deliberately combines them.
Compatible deletions at different depths can both be retained. Prefix indexing
checks overlaps without comparing every possible pair of edits.

This is conservative structural evidence, not a semantic merge or approval.
Unchanged content, unrelated candidate additions/deletions, formatting, renames,
comments, signatures and contributor intent are outside the policy. Review the
actual diff and use the line's text and deletion tools alongside it. A retained
value at the same pointer is not proof of the author's intended meaning.

Reuses the sibling `tree-review` reader/manifests, which imports `merge-review`
and `threeway`. Keep those folders alongside this one. No merger is called.
All four trees share an 8 MiB budget. Each tree is limited to 128 files, 256
directories, depth 16; each file to 1 MiB and 4,000 lines. NUL, invalid UTF-8,
symlinks, special files, parent traversal and paths outside the current workspace
are refused. File/directory collisions block affected paths and descendants.
All supplied files, including skipped files, pass those reader limits.
Reads require stable trusted directories and are not an atomic snapshot.

Validation: 20 focused tests passed, including 1,000 tiny base/branch combinations
checked against a pairwise overlap oracle. Tests cover arrays, nested type changes,
exact numbers, duplicate keys, null/deletion, missing files, limits, pointer escaping,
symlink refusal and CLI exits. A trial on a copy of an inherited real JSON document
retained two independent additions, then detected one omitted addition; all four
inputs were byte-identical after the read-only pass, and the original document
stayed unchanged. The inherited Tree Review suite also passed 25 tests.

```sh
python3 -B -m unittest discover -s line-1/tools/json-change-audit -p 'test_*.py'
```

No network, external package, coin, wallet, key, transaction or payment is needed.
