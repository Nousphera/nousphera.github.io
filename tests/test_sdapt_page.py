"""Keep the project page aligned with the audited manuscript data."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_projects as build
from paper_results import load_results, results_markup


class SdaptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = next(p for p in build.load_projects() if p['slug'] == 'sdapt')
        cls.source = json.loads((ROOT / 'assets/projects/sdapt/results.json').read_text())
        cls.result = load_results(cls.project)

    def test_every_fewshot_score_and_lp_score_matches_table_one(self):
        charts = {c['title']: c for c in self.result['panels'][0]['groups'][0]['charts']}
        for dataset in self.source['table1']['datasets']:
            chart = charts[dataset['dataset']]
            self.assertEqual(chart['x']['label'], 'Shots (k)')
            for row in dataset['rows']:
                series = next(s for s in chart['series'] if s['label'] == row['method'])
                self.assertEqual(series['points'], list(map(list, zip([4, 8, 16], row['scores'][:3]))))
            insight = next(r for r in self.project['insight']['results'] if r['title'].startswith(dataset['dataset']))
            for row, source_row in zip(insight['rows'], dataset['rows']):
                self.assertEqual([float(v) for v in row['values']], source_row['scores'])

    def test_budget_preserves_all_56_observations_on_each_axis(self):
        for group, metric, divisor in zip(
            self.result['panels'][1]['groups'],
            ['communication_tb', 'client_compute_gflops', 'samples_seen'],
            [1, 1e6, 1e6],
        ):
            count = 0
            for chart in group['charts']:
                self.assertEqual(chart['x']['scale'], 'log')
                for series in chart['series']:
                    source = next(s for s in self.source['figure2']['series'] if s['dataset'] == chart['title'] and s['method'] == series['label'])
                    self.assertEqual(len(series['points']), len(source['checkpoints']))
                    count += len(series['points'])
                    for (x, y), checkpoint in zip(series['points'], source['checkpoints']):
                        self.assertAlmostEqual(x, checkpoint[metric] / divisor, places=8)
                        self.assertEqual(y, checkpoint['gain_pp'])
            self.assertEqual(count, 56)

    def test_signed_gains_include_every_label_and_two_regressions(self):
        rows = self.project['insight']['results'][4]['rows']
        self.assertEqual(len(rows), 8)
        for row, source in zip(rows, self.source['table2']['rows']):
            self.assertEqual(row['label'], source['label_as_printed'])
            self.assertEqual(float(row['values'][0]), source['mocosfl_gain_pp'])
            self.assertEqual(float(row['values'][1]), source['sdapt_gain_pp'])
        self.assertEqual(sum(float(r['values'][1]) < 0 for r in rows), 2)
        mean = sum(r['gains_over_ft_pp'][i] for d in self.source['table1']['datasets'] for r in d['rows'] if r['method'] == 'SDAPT' for i in range(3)) / 9
        self.assertEqual(round(mean, 1), 7.4)

    def test_generated_page_has_every_marker_and_no_empty_source_disclosure(self):
        html = build.project_page(self.project, [self.project])
        self.assertEqual(html.count('data-result-x='), 36 + 56 * 3)
        self.assertNotIn('Original paper figures &amp; sources', html)
        self.assertNotIn('full-label', html.lower())
        self.assertIn('Linear probing (LP)', html)
        self.assertNotIn('/Users/', json.dumps(self.source))


if __name__ == '__main__':
    unittest.main()
