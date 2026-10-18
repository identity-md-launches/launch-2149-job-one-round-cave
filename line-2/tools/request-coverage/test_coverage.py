"""Focused checks for the independent request boundary and real proof set."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('request_coverage_tests', HERE / 'coverage.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request, cls.request_digest = c.load_request(HERE / 'examples/zto-and-pool-request.json')
        cls.manifest, cls.base, cls.manifest_digest = c.p.load_manifest(
            HERE.parent / 'proof-set/examples/zto-and-pool.json')

    def test_real_proofs_with_external_request(self):
        result = c.verify(self.request, self.manifest, self.base, c.p.a.DEMO_HASH,
                          self.request_digest, self.manifest_digest)
        self.assertTrue(result['verified'])
        self.assertEqual(len(result['coverage']), 2)
        self.assertEqual(result['proofSet']['accounts'][0]['state']['address'], c.w.ZTO)
        self.assertEqual(result['proofSet']['accounts'][1]['state']['address'], c.w.POOL_MANAGER)

    def test_missing_and_extra_accounts_fail_before_proof(self):
        changed = copy.deepcopy(self.manifest)
        changed['accounts'].pop()
        with self.assertRaisesRegex(c.w.Invalid, 'account coverage'):
            c.check_coverage(self.request, changed)
        changed = copy.deepcopy(self.request)
        changed['accounts'].pop()
        with self.assertRaisesRegex(c.w.Invalid, 'account coverage'):
            c.check_coverage(changed, self.manifest)

    def test_missing_and_extra_slots_fail_before_proof(self):
        for slots in (['0x0'], ['0x0', '0x1', '0x2']):
            changed = copy.deepcopy(self.manifest)
            changed['accounts'][0]['slots'] = slots
            with self.assertRaisesRegex(c.w.Invalid, 'storage-slot coverage'):
                c.check_coverage(self.request, changed)

    def test_code_requirement_cannot_be_dropped(self):
        changed = copy.deepcopy(self.manifest)
        del changed['accounts'][0]['code']
        with self.assertRaisesRegex(c.w.Invalid, 'code coverage'):
            c.check_coverage(self.request, changed)

    def test_order_and_hex_case_do_not_change_coverage(self):
        changed = copy.deepcopy(self.manifest)
        changed['accounts'].reverse()
        changed['accounts'][1]['slots'] = ['0x01', '0x00']
        changed['accounts'][1]['address'] = changed['accounts'][1]['address'].upper().replace('0X', '0x')
        self.assertEqual(c.check_coverage(self.request, changed),
                         c.check_coverage(self.request, self.manifest))

    def test_malformed_and_duplicate_request_fail(self):
        changed = copy.deepcopy(self.request)
        changed['accounts'][0]['code'] = 1
        with self.assertRaisesRegex(c.w.Invalid, 'boolean'):
            c.check_coverage(changed, self.manifest)
        changed = copy.deepcopy(self.request)
        changed['accounts'][0]['slots'] = ['0x0', '0x00']
        with self.assertRaisesRegex(c.w.Invalid, 'duplicate requested slot'):
            c.check_coverage(changed, self.manifest)
        with self.assertRaisesRegex(c.w.Invalid, 'duplicate JSON'):
            c.w.parse_json(b'{"format":"proof-request/1","format":"proof-request/1"}')

    def test_wrong_checkpoint_fails_after_coverage(self):
        with self.assertRaisesRegex(c.w.Invalid, 'trusted block hash'):
            c.verify(self.request, self.manifest, self.base, '0x' + '00' * 32,
                     self.request_digest, self.manifest_digest)

    def test_request_digest_is_external_pin(self):
        c.check_digest('0x' + self.request_digest, self.request_digest, 'request SHA-256')
        with self.assertRaisesRegex(c.w.Invalid, 'differs'):
            c.check_digest('0x' + '00' * 32, self.request_digest, 'request SHA-256')


if __name__ == '__main__':
    unittest.main()
