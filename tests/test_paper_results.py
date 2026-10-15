"""Evidence and chart regressions for the compact result presentation."""
import copy
import math
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree as ET
import re

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_projects as build
from paper_results import (bar_chart, compact_table, emphasis, load_results,
                           results_markup, scatter_svg, selected_result,
                           validate_results, _position)


class ResultsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.projects = {p['slug']: p for p in build.load_projects()}

    def test_all_pages_use_compact_source_bound_panels_without_detail_boilerplate(self):
        for p in self.projects.values():
            data = load_results(p)
            html = results_markup(p)
            self.assertEqual(html.count('class="rs-card '), len(data['panels']))
            self.assertNotIn('<details', html)
            self.assertNotIn('<script', html)
            self.assertNotIn('<img', html)
            self.assertNotIn('Experiment details', html)
            self.assertIn('Takeaways', html)
            self.assertTrue(all('<strong>' in text for text in data['takeaways']))

    def test_every_selected_value_and_uncertainty_survives_rendering(self):
        for p in self.projects.values():
            html = results_markup(p)
            for panel in load_results(p)['panels']:
                self.assertIn(build.esc(panel['source']['url']), html)
                if panel['kind'] == 'scatter':
                    for point in panel['plot']['points']:
                        self.assertIn(f'data-result-x="{point["x"]}"', html)
                        self.assertIn(f'data-result-y="{point["y"]}"', html)
                    continue
                r = selected_result(p, panel)
                cols = panel.get('columns', range(len(r['columns'])-1)) if panel['kind'] == 'table' else {c for spec in panel['charts'] for c in spec['columns']}
                for row in r['rows']:
                    for c in cols:
                        self.assertIn(build.esc(str(row['values'][c])), html)

    def test_mpsl_aggregate_uses_all_five_classification_tasks(self):
        d = load_results(self.projects['mpsl'])
        audit = d['audit']['aggregation']
        self.assertEqual(len(audit['task_order']), 5)
        self.assertNotIn('retrieval', ' '.join(audit['task_order']).lower())
        for point in d['panels'][0]['plot']['points']:
            method = audit['methods'][point['label']]
            self.assertAlmostEqual(sum(method['task_accuracy_percent']) / 5, point['y'])
            self.assertEqual(point['x'], method['trainable_client_parameters_million'])
        self.assertAlmostEqual(100*(1-1/43.7), d['audit']['calculations']['trainable_parameter_reduction_percent']['value'])

    def test_deltamask_uses_reported_table_averages_and_valid_ratio(self):
        p = self.projects['deltamask']; d = load_results(p)
        source_rows = {r['label']: r for r in p['insight']['results'][1]['rows']}
        for point in d['panels'][0]['plot']['points']:
            row = source_rows[point['label']]
            self.assertEqual(point['y'], float(row['values'][0]))
            self.assertEqual(point['x'], float(row['values'][1]))
        self.assertAlmostEqual(100*(1-.233/.948), d['audit']['calculations']['bitrate_reduction_percent']['value'])
        self.assertIn('Reported', d['panels'][0]['plot']['y']['label'])

    def test_bad_indices_cannot_silently_select_other_evidence(self):
        p = self.projects['fedstar']; d = load_results(p)
        for bad in [-1, 999, '0']:
            modified = copy.deepcopy(d); modified['panels'][0]['result_index'] = bad
            with self.assertRaises(ValueError): validate_results(p, modified)
        modified = copy.deepcopy(d); modified['panels'][0]['rows'] = [-1]
        with self.assertRaises(ValueError): validate_results(p, modified)

    def test_bar_axis_includes_zero_and_never_invents_missing_values(self):
        r = {'columns':['Method','Change'], 'rows':[{'label':'A','values':['−2.5']}, {'label':'B','values':['1.0 ± 0.2']}, {'label':'C','values':['—']}]}
        html = bar_chart(r, {'columns':[0], 'title':'Change (pp)'})
        self.assertIn('--zero:75.00000%', html)
        self.assertIn('left:12.50000%;width:62.50000%', html)
        self.assertIn('1.0 ± 0.2', html)
        self.assertEqual(html.count('class="rs-bar-track"'), 2)
        for bad in [float('nan'), float('inf'), -1, .5]:
            with self.assertRaises(ValueError): bar_chart(r, {'columns':[0], 'title':'Change', 'maximum':bad})
        r['rows'][0]['values'] = ['<10']
        with self.assertRaises(ValueError): bar_chart(r, {'columns':[0], 'title':'Change'})

    def test_series_labels_cannot_add_phantom_results(self):
        r = {'columns':['Method','Accuracy'], 'rows':[{'label':'A','values':['50']}]}
        for labels in [[], ['A','B']]:
            with self.assertRaises(ValueError):
                bar_chart(r, {'columns':[0], 'title':'Accuracy', 'series_labels':labels})

    def test_scatter_values_labels_and_axes_cannot_disagree(self):
        p = self.projects['mpsl']; d = load_results(p)
        bad = copy.deepcopy(d); bad['panels'][0]['plot']['points'][0]['x_display'] = '999'
        with self.assertRaises(ValueError): validate_results(p, bad)
        bad = copy.deepcopy(d); bad['panels'][0]['plot']['x']['max'] = 20
        with self.assertRaises(ValueError): validate_results(p, bad)
        bad = copy.deepcopy(d); bad['panels'][0]['plot']['y']['ticks'] = [100]
        with self.assertRaises(ValueError): validate_results(p, bad)
        self.assertAlmostEqual(_position(10, {'min':1,'max':100,'scale':'log'}), .5)
        for mobile in (False, True):
            svg = ET.fromstring(scatter_svg(d['panels'][0]['plot'], mobile))
            self.assertEqual(svg.tag, 'svg')

    def test_result_text_cannot_inject_markup(self):
        with self.assertRaises(ValueError): emphasis('<a href="javascript:alert(1)">A</a>')
        r = {'title':'<script>','context':'scope','columns':['Method','Value'], 'rows':[{'label':'<img>','values':['<script>']}]}
        html = compact_table(r)
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)


if __name__ == '__main__':
    unittest.main()
