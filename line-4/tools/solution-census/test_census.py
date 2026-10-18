import copy
import importlib.util
import itertools
from pathlib import Path
import random
import subprocess
import sys
import unittest

spec = importlib.util.spec_from_file_location('census', Path(__file__).with_name('census.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def oracle(data):
    """Enumerate all package subsets; check raw exact edges without imported checker."""
    packages, roots = data['packages'], data['roots']
    names = sorted(packages)
    results = []
    for values in itertools.product(*[[None] + list(packages[p]) for p in names]):
        chosen = dict((p, v) for p, v in zip(names, values) if v is not None)
        todo, seen, valid = list(roots.items()), set(), True
        while todo:
            p, requirement = todo.pop()
            if p not in chosen or (requirement != '*' and requirement != '==' + chosen[p]):
                valid = False
                break
            if p not in seen:
                seen.add(p)
                todo.extend(packages[p][chosen[p]].items())
        if valid and set(chosen) == seen:
            results.append(chosen)
    return results


class CensusTests(unittest.TestCase):
    def test_unique_and_unreachable(self):
        data = {'roots': {'a': '*'}, 'packages': {'a': {'1': {}}, 'unused': {'1': {}, '2': {}}}}
        result = m.census(data)
        self.assertEqual(result['compatible_selections'], 1)
        self.assertEqual(result['classification'], 'unique')
        self.assertEqual(result['packages']['a']['forced'], '1')
        self.assertTrue(result['packages']['unused']['always_absent'])
        self.assertEqual(result['candidate_assignments'], 1)

    def test_optional_dependency_and_no_duplicate_count(self):
        data = {'roots': {'a': '*'}, 'packages': {'a': {'1': {}, '2': {'b': '*'}}, 'b': {'1': {}, '2': {}}}}
        r = m.census(data)
        self.assertEqual(r['compatible_selections'], 3)
        self.assertEqual(r['packages']['b']['absent'], 1)
        self.assertEqual(r['packages']['b']['versions'], {'1': 1, '2': 1})
        self.assertIsNone(r['packages']['a']['forced'])
        self.assertEqual(len(r['witnesses']), 2)

    def test_missing_and_empty_domain(self):
        for data in ({'roots': {'missing': '*'}, 'packages': {}},
                     {'roots': {'a': '==2'}, 'packages': {'a': {'1': {}}}}):
            r = m.census(data, 1)
            self.assertEqual(r['classification'], 'unsatisfiable')
            self.assertEqual(r['checked_assignments'], 0)
            self.assertNotIn('forced', next(iter(r['packages'].values())))

    def test_missing_nonroot_in_one_branch(self):
        data = {'roots': {'a': '*'}, 'packages': {'a': {'1': {}, '2': {'missing': '*'}}}}
        r = m.census(data)
        self.assertEqual(r['classification'], 'unique')
        self.assertTrue(r['packages']['missing']['always_absent'])

    def test_cycles(self):
        data = {'roots': {'a': '*'}, 'packages': {'a': {'1': {'b': '*'}}, 'b': {'1': {'a': '*'}, '2': {'a': '==2'}}}}
        self.assertEqual(m.census(data)['witnesses'], [{'a': '1', 'b': '1'}])

    def test_partial_budget_no_uniqueness_claim(self):
        data = {'roots': {'a': '*'}, 'packages': {'a': {'1': {}, '2': {}, '3': {}}}}
        for budget in (1, 2):
            r = m.census(data, budget)
            self.assertEqual(r['status'], 'inconclusive')
            self.assertEqual(r['count_kind'], 'lower-bound')
            self.assertEqual(r['classification'], 'unknown' if budget == 1 else 'multiple')
            self.assertNotIn('forced', r['packages']['a'])
        self.assertEqual(m.census(data, 3)['status'], 'complete')

    def test_seeded_independent_oracle(self):
        rng = random.Random(3504)
        for _ in range(300):
            packages = {}
            for p in ('a', 'b', 'c'):
                packages[p] = {v: {q: rng.choice(('*', '==1', '==2'))
                                   for q in ('a', 'b', 'c', 'missing') if rng.random() < .18}
                               for v in ('1', '2') if rng.random() < .85}
            data = {'roots': {'a': rng.choice(('*', '==1', '==2'))}, 'packages': packages}
            expected = oracle(data)
            result = m.census(data)
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(result['compatible_selections'], len(expected))
            for p, row in result['packages'].items():
                self.assertEqual(row['absent'], sum(p not in s for s in expected))
                for v, count in row['versions'].items():
                    self.assertEqual(count, sum(s.get(p) == v for s in expected))
            for s in result['witnesses']:
                self.assertIn(s, expected)

    def test_normalization_immutability_and_digest(self):
        data = {'roots': {'A_B': '*'}, 'packages': {'a-b': {'1.0': {}}}}
        before = copy.deepcopy(data)
        r = m.census(data)
        self.assertEqual(data, before)
        self.assertEqual(r['witnesses'], [{'a-b': '1.0'}])
        data['roots'] = {'a-b': '*'}
        self.assertEqual(r['catalog_sha256'], m.census(data)['catalog_sha256'])
        data['packages']['a-b']['2'] = {}
        self.assertNotEqual(r['catalog_sha256'], m.census(data)['catalog_sha256'])

    def test_invalid(self):
        data = {'roots': {'a': '*'}, 'packages': {'a': {'1': {}}}}
        for budget in (True, 0, -1, 1000001, 1.5):
            with self.assertRaises(m.fmt.Invalid):
                m.census(data, budget)
        with self.assertRaises(m.fmt.Invalid):
            m.census(dict(data, roots={}))

    def test_constraints_and_demo_counts(self):
        data = {'roots': {'a': '>=1,!=2,<4'},
                'packages': {'a': {'1': {}, '2': {}, '3': {}, '4': {}}}}
        r = m.census(data)
        self.assertEqual(r['compatible_selections'], 2)
        self.assertEqual(r['packages']['a']['versions'], {'1': 1, '2': 0, '3': 1, '4': 0})
        real = m.fmt.load(m.CHECKER.parent.parent / 'conflict-core/examples/requests-conflict.json')
        real = dict(real, roots={'requests': '*', 'urllib3': '<2'})
        result = m.census(real)
        self.assertEqual(result['compatible_selections'], 26)
        self.assertEqual(result['candidate_assignments'], 216)
        self.assertEqual(result['packages']['urllib3']['forced'], '1.26.20')
        self.assertEqual(result['packages']['chardet']['absent'], 24)

    def test_cli(self):
        script = str(Path(__file__).with_name('census.py'))
        for args, code in ((['demo'], 0), (['demo', '--max-assignments', '1'], 3),
                           (['demo', '--max-assignments', '0'], 2)):
            r = subprocess.run([sys.executable, '-B', script] + args, capture_output=True, text=True)
            self.assertEqual(r.returncode, code, r.stdout + r.stderr)


if __name__ == '__main__':
    unittest.main()
