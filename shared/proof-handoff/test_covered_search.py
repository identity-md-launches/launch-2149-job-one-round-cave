"""Real historical proof handoffs, omissions, tampering and portable use."""
import contextlib
import copy
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import covered_search as t


class CoveredSearchTests(unittest.TestCase):
    def setUp(self):
        Path('test/scratch').mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir='test/scratch')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.request = self.root / 'request.json'
        self.request.write_bytes(t.DEMO_REQUEST.read_bytes())
        _, self.request_pin = t.c.load_request(self.request)
        self.bundle = self.root / 'bundle.json'
        self.made = t.h.pack(t.h.DEMO_MANIFEST, t.h.p.a.DEMO_HASH,
                             'storage value', self.bundle, self.root)

    def check(self, **overrides):
        args = dict(request=self.request, manifest=t.h.DEMO_MANIFEST,
                    block_hash=t.h.p.a.DEMO_HASH, bundle=self.bundle,
                    expected_bundle=self.made['bundle_sha256'],
                    expected_request=self.request_pin,
                    expected_manifest=self.made['manifest_sha256'], scratch=self.root)
        args.update(overrides)
        return t.check(**args)

    def test_real_exact_request_and_search(self):
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        report = self.check(query=t.h.p.w.ZTO)
        self.assertTrue(report['verified'])
        self.assertEqual(len(report['coverage']), 2)
        self.assertEqual(sum(len(x['slots']) for x in report['coverage']), 3)
        self.assertTrue(report['handoff']['receipt_reproduced'])
        self.assertTrue(report['handoff']['search']['hits'])
        self.assertEqual(int(report['handoff']['anchor']['blockNumber'], 16), 26212390)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_pins_required_and_exact(self):
        for name in ('expected_request', 'expected_manifest'):
            for pin in (None, True, 'A' * 64, '1' * 64):
                with self.subTest(name=name, pin=pin), self.assertRaises(ValueError):
                    self.check(**{name: pin})
        self.request.write_bytes(self.request.read_bytes() + b'\n')
        with self.assertRaisesRegex(ValueError, 'request pin'):
            self.check()

    def test_missing_account_slot_or_code_rejected_before_proofs(self):
        manifest, _, _ = t.c.p.load_manifest(t.h.DEMO_MANIFEST)
        for kind in ('account', 'slot', 'code', 'extra'):
            changed = copy.deepcopy(manifest)
            if kind == 'account':
                changed['accounts'].pop()
            elif kind == 'slot':
                changed['accounts'][0]['slots'].pop()
            elif kind == 'code':
                del changed['accounts'][0]['code']
            else:
                changed['accounts'][0]['slots'].append('0x2')
            with self.subTest(kind=kind), patch.object(t.c.p, 'load_manifest', return_value=(
                    changed, self.root, self.made['manifest_sha256'])), patch.object(t.h, 'check') as verify:
                with self.assertRaisesRegex(ValueError, 'coverage'):
                    self.check()
                verify.assert_not_called()

    def test_valid_subset_proofs_and_bundle_still_refused(self):
        # A provider can prove and bundle a smaller set successfully. The
        # independently retained caller request must still expose its omission.
        isolated = self.root / 'provider'
        shutil.copytree(t.h.HERE / 'tools', isolated / 'tools')
        manifest_path = isolated / 'tools/proof-set/examples/zto-and-pool.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['accounts'].pop()
        manifest_path.write_text(json.dumps(manifest))
        output = self.root / 'subset.json'
        made = t.h.pack(manifest_path, t.h.p.a.DEMO_HASH, 'storage value', output, self.root)
        self.assertTrue(t.h.check(manifest_path, t.h.p.a.DEMO_HASH, output,
                                 made['bundle_sha256'], self.root)['verified'])
        with self.assertRaisesRegex(ValueError, 'account coverage'):
            self.check(manifest=manifest_path, bundle=output,
                       expected_manifest=made['manifest_sha256'], expected_bundle=made['bundle_sha256'])

    def test_changed_request_during_check_rejected(self):
        real = t.h.check
        def change(*args, **kwargs):
            result = real(*args, **kwargs)
            self.request.write_bytes(self.request.read_bytes() + b'\n')
            return result
        with patch.object(t.h, 'check', side_effect=change):
            with self.assertRaisesRegex(ValueError, 'changed during'):
                self.check()

    def test_wrong_checkpoint_bundle_and_forged_search(self):
        with self.assertRaises(ValueError):
            self.check(block_hash='0x' + '11' * 32)
        with self.assertRaises(ValueError):
            self.check(expected_bundle='1' * 64)
        value = t.h.b.load(self.bundle)
        value['receipt']['result']['hits'][0]['text'] = 'invented evidence'
        self.bundle.write_bytes(t.h.b.receipt.canonical(value))
        with self.assertRaisesRegex(ValueError, 'does not reproduce'):
            self.check(expected_bundle=t.h.b.identity(value))

    def test_malformed_request_and_path_escape(self):
        for raw in (b'{"format":1,"format":2}', b'{"x":NaN}', b' ' * 16385):
            self.request.write_bytes(raw)
            with self.assertRaises(ValueError):
                self.check()
        with self.assertRaises(ValueError):
            self.check(request=Path.cwd().parent / 'not-opened.json')

    def test_cli_failure_has_no_partial_success(self):
        args = ['check', str(self.request), str(t.h.DEMO_MANIFEST),
                '--block-hash', t.h.p.a.DEMO_HASH, '--bundle', str(self.bundle),
                '--expected-sha256', self.made['bundle_sha256'],
                '--request-sha256', '1' * 64, '--manifest-sha256', self.made['manifest_sha256']]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = t.main(args)
        self.assertEqual(status, 2)
        self.assertEqual(out.getvalue(), '')
        self.assertFalse(json.loads(err.getvalue())['verified'])

    def test_portable_without_line_folders(self):
        isolated = self.root / 'isolated'
        shutil.copytree(t.h.HERE, isolated)
        proc = subprocess.run([sys.executable, '-B', 'covered_search.py', 'demo'],
                              cwd=isolated, capture_output=True, timeout=90)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(json.loads(proc.stdout)['verified'])


if __name__ == '__main__':
    unittest.main()
