import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('audit', Path(__file__).with_name('json_change_audit.py'))
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Path("test/scratch").mkdir(parents=True, exist_ok=True)

    def check(self, base, ours, theirs, candidate):
        return a.audit([json.dumps(v) for v in (base, ours, theirs, candidate)])

    def test_independent_keys(self):
        self.assertEqual(self.check({'x':0,'y':0}, {'x':1,'y':0}, {'x':0,'y':2}, {'x':1,'y':2})['status'], 'checked')

    def test_lost_replacement_valid_json(self):
        r = self.check({'x':0}, {'x':1}, {'x':0}, {'x':0})
        self.assertEqual(r['status'], 'review')
        self.assertFalse(r['changes'][0]['retained'])

    def test_null_is_not_deleted(self):
        r = self.check({'x':None}, {}, {'x':None}, {'x':None})
        self.assertEqual(r['status'], 'review')
        self.assertEqual(r['changes'][0]['operation'], 'delete')

    def test_bool_is_not_number_nested(self):
        self.assertEqual(self.check({'a':[False]}, {'a':[0]}, {'a':[False]}, {'a':[False]})['status'], 'review')

    def test_numbers_exact_and_equivalent(self):
        self.assertTrue(a.equal(a.parse('1'), a.parse('1.0')))
        self.assertFalse(a.equal(a.parse('9007199254740992'), a.parse('9007199254740993')))
        self.assertFalse(a.equal(a.parse('1e9999'), a.parse('2e9999')))
        self.assertTrue(a.equal(a.parse('-0'), a.parse('0.0')))

    def test_conflict_when_one_selected(self):
        r = self.check({'x':0}, {'x':1}, {'x':2}, {'x':1})
        self.assertEqual(r['status'], 'review')
        self.assertTrue(all(row['branch_conflict'] for row in r['changes']))

    def test_agreed_change_once(self):
        self.assertEqual(self.check({}, {'x':1}, {'x':1}, {'x':1})['status'], 'checked')

    def test_ancestor_descendant_conflict_both_sides(self):
        for left, right in [(None, {'x':1}), ({'x':1}, None)]:
            r = self.check({'x':0}, left, right, left)
            self.assertEqual(r['status'], 'review')
            self.assertTrue(all(row['branch_conflict'] for row in r['changes']))

    def test_compatible_ancestor_deletions(self):
        r = self.check({'a':{'x':0}}, {}, {'a':{}}, {})
        self.assertEqual(r['status'], 'checked')

    def test_arrays_are_atomic(self):
        r = self.check([0,0], [1,0], [0,2], [1,2])
        self.assertEqual(r['status'], 'review')
        self.assertTrue(all(row['branch_conflict'] for row in r['changes']))

    def test_pointer_escaping(self):
        r = self.check({'a/~':0}, {'a/~':1}, {'a/~':0}, {'a/~':1})
        self.assertEqual(r['changes'][0]['pointer'], '/a~1~0')

    def test_file_presence_and_null(self):
        self.assertEqual(a.audit([None,'null',None,None])['status'], 'review')
        self.assertEqual(a.audit([None,'{}',None,'{}'])['status'], 'checked')
        self.assertEqual(a.audit(['{}',None,'{}',None])['status'], 'checked')

    def test_duplicate_and_nonfinite_rejected(self):
        for text in ('{"x":1,"x":2}', 'NaN', 'Infinity', '-Infinity', '', '{', '1e99999999999999999999999999'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                a.parse(text)

    def test_depth_and_nodes(self):
        for text in ('['*65+'0'+']'*65, '['+','.join(['0']*50000)+']'):
            with self.assertRaises(ValueError):
                a.parse(text)

    def test_many_independent_changes(self):
        base = {str(i):0 for i in range(2000)}
        left = {k:1 if int(k)%2 else 0 for k in base}
        right = {k:0 if int(k)%2 else 1 for k in base}
        self.assertEqual(self.check(base,left,right,dict.fromkeys(base,1))['status'], 'checked')

    def test_invalid_and_skipped_and_collision(self):
        def source(files, dirs=()):
            return {'files':files, 'directories':set(dirs)}
        sources = [source({'a.json':'{','b.txt':'hello','p':'x'}), source({}, ['p']), source({}), source({})]
        report = a.inspect(sources)
        self.assertEqual([r['status'] for r in report['files']], ['invalid','skipped','blocked'])
        self.assertTrue(report['needs_review'])

    def test_filesystem_trial_immutable_and_cli(self):
        # Actual inherited record used as unfamiliar structured document.
        source = Path('dist/line-1/35.json')
        original = source.read_bytes()
        base = json.loads(original)
        ours = {**base, 'review_required':True}
        theirs = {**base, 'review_note':'Inspect the combined candidate.'}
        good = {**ours, 'review_note':theirs['review_note']}
        with tempfile.TemporaryDirectory(dir='test/scratch') as folder:
            paths = []
            for side, value in zip(a.SIDES, (base,ours,theirs,good)):
                directory = Path(folder)/side
                directory.mkdir()
                (directory/'document.json').write_text(json.dumps(value))
                paths.append(directory)
            before = [hashlib.sha256((p/'document.json').read_bytes()).hexdigest() for p in paths]
            self.assertFalse(a.from_directories(paths)['needs_review'])
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(a.main([str(p) for p in paths]), 0)
            self.assertEqual(before, [hashlib.sha256((p/'document.json').read_bytes()).hexdigest() for p in paths])
            (paths[3]/'document.json').write_text(json.dumps(ours))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(a.main([str(p) for p in paths]), 1)
        self.assertEqual(source.read_bytes(), original)

    def test_reader_rejects_symlink_and_escape(self):
        with tempfile.TemporaryDirectory(dir='test/scratch') as folder:
            root = Path(folder)
            (root/'link.json').symlink_to('absent')
            with self.assertRaises(ValueError):
                a.from_directories([root]*4)
        with self.assertRaises(ValueError):
            a.from_directories(['/tmp']*4)

    def test_conflict_flags_match_pairwise_oracle(self):
        values = [None, {}, {'a':0}, {'a':1}, {'a':{}}, {'a':{'b':0}},
                  {'a':{'b':1}}, {'a':{'c':0}}, {'a':False}, {'a':[]}]
        for base in values:
            for left in values:
                for right in values:
                    edits = [a.changes(base, left), a.changes(base, right)]
                    flagged = [set(), set()]
                    for lp, lv in edits[0]:
                        for rp, rv in edits[1]:
                            if lp == rp[:len(lp)]:
                                mismatch = not a.equal(a.lookup(lv, rp[len(lp):]), rv)
                            elif rp == lp[:len(rp)]:
                                mismatch = not a.equal(a.lookup(rv, lp[len(rp):]), lv)
                            else:
                                mismatch = False
                            if mismatch:
                                flagged[0].add(a.pointer(lp))
                                flagged[1].add(a.pointer(rp))
                    rows = self.check(base,left,right,left)['changes']
                    for index, side in enumerate(('ours','theirs')):
                        actual = {r['pointer'] for r in rows if r['side'] == side and r['branch_conflict']}
                        self.assertEqual(actual, flagged[index])

    def test_demo(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(a.main(['--demo']), 0)


if __name__ == '__main__':
    Path('test/scratch').mkdir(parents=True, exist_ok=True)
    unittest.main()
