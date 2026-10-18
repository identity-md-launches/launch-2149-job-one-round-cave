import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('replay', Path(__file__).with_name('replay.py'))
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class ReplayTests(unittest.TestCase):
    def setUp(self):
        docs = []
        for name, text in [('a.md', 'ZTO token decimals\nZTO token\n'), ('b.md', 'IMD token\n')]:
            docs.append({'path': name, 'text': text, 'sha256': r.search.digest(text.encode())})
        self.index = {'format': r.search.FORMAT, 'documents': docs}
        self.saved = r.search.search_snapshot(self.index, 'token', 3)

    def check(self, saved):
        return r.replay(self.index, saved, 3)['reproduced']

    def test_original_and_live_flags(self):
        self.assertTrue(self.check(self.saved))
        for hit in self.saved['hits']:
            hit['source_verified'] = True
        self.assertTrue(self.check(self.saved))
        self.assertFalse(r.replay(self.index, self.saved, 3)['current_sources_checked'])

    def test_mutated_fields(self):
        for field, value in [('text', 'other'), ('citation', 'a.md:5-6'), ('line_start', 2),
                             ('sha256', '0'*64), ('score', 99), ('path', 'else.md'),
                             ('matched_terms', ['else'])]:
            with self.subTest(field=field):
                bad = copy.deepcopy(self.saved)
                bad['hits'][0][field] = value
                self.assertFalse(self.check(bad))

    def test_order_omission_duplicate(self):
        bad = copy.deepcopy(self.saved)
        bad['hits'].reverse()
        self.assertFalse(self.check(bad))
        bad['hits'].pop()
        self.assertFalse(self.check(bad))
        bad['hits'] = [self.saved['hits'][0]]*2
        self.assertFalse(self.check(bad))

    def test_metadata_extra_and_types(self):
        for key, value in [('terms', ['wrong']), ('extra', 1), ('indexed_documents', True)]:
            bad = copy.deepcopy(self.saved)
            bad[key] = value
            self.assertFalse(self.check(bad))

    def test_empty_result(self):
        saved = r.search.search_snapshot(self.index, 'absent', 3)
        self.assertTrue(self.check(saved))
        self.assertEqual(r.replay(self.index, saved, 3)['expected_hits'], 0)

    def test_explicit_limit(self):
        self.assertFalse(r.replay(self.index, self.saved, 1)['reproduced'])
        for limit in [True, 0, 51, '3']:
            with self.assertRaises(r.search.SearchError):
                r.replay(self.index, self.saved, limit)

    def test_malformed_and_nonfinite(self):
        for field, value in [('require_all', 1), ('hits', {}), ('query', None)]:
            bad = copy.deepcopy(self.saved)
            bad[field] = value
            with self.assertRaises(r.search.SearchError):
                self.check(bad)
        bad = copy.deepcopy(self.saved)
        bad['hits'][0]['score'] = float('nan')
        with self.assertRaises(r.search.SearchError):
            self.check(bad)

    def test_index_hash_validation(self):
        self.index['documents'][0]['text'] += 'changed'
        with self.assertRaises(r.search.SearchError):
            self.check(self.saved)

    def test_does_not_mutate(self):
        old = copy.deepcopy((self.index, self.saved))
        self.check(self.saved)
        self.assertEqual(old, (self.index, self.saved))

    def test_real_demo(self):
        demo = r.demo()
        self.assertTrue(demo['historical_zto_result']['reproduced'])
        self.assertFalse(demo['altered_line_citation']['reproduced'])


if __name__ == '__main__':
    unittest.main()
