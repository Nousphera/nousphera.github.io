"""A plotted checkpoint must retain its source value, scale and method."""
import copy
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from result_curves import curve_svg, validate_curve_groups, curve_groups


class CurveTests(unittest.TestCase):
    def setUp(self):
        self.groups = [{
            'label': 'Upload',
            'charts': [{
                'title': 'fMoW',
                'x': {'label': 'Upload (TB)', 'min': 0, 'max': 4, 'ticks': [0, 2, 4]},
                'y': {'label': 'Gain (pp)', 'min': 0, 'max': 15, 'ticks': [0, 5, 10, 15]},
                'series': [
                    {'label': 'MocoSFL', 'points': [[0.3, 4.5], [2.1, 8.1]]},
                    {'label': 'SDAPT', 'highlight': True, 'points': [[0.7, 3.9], [3.8, 12.8]]},
                ],
            }],
        }]

    def test_exact_checkpoints_accessible_and_theme_native(self):
        validate_curve_groups(self.groups)
        svg = curve_svg(self.groups[0]['charts'][0])
        root = ET.fromstring(svg)
        self.assertEqual(root.get('role'), 'img')
        self.assertIn('SDAPT', root.find('desc').text)
        self.assertIn('12.8', root.find('desc').text)
        for x, y in [(0.3, 4.5), (2.1, 8.1), (0.7, 3.9), (3.8, 12.8)]:
            self.assertIn(f'data-result-x="{x}" data-result-y="{y}"', svg)
        self.assertNotIn('fill="#', svg)
        self.assertIn('rs-curve-own', svg)

    def test_reject_clipping_nonfinite_and_unsorted_checkpoints(self):
        for point in [[5, 12], [1, 17], [float('nan'), 2]]:
            groups = copy.deepcopy(self.groups)
            groups[0]['charts'][0]['series'][0]['points'][-1] = point
            with self.assertRaises(ValueError):
                validate_curve_groups(groups)
        groups = copy.deepcopy(self.groups)
        groups[0]['charts'][0]['series'][0]['points'].reverse()
        with self.assertRaises(ValueError):
            validate_curve_groups(groups)

    def test_groups_are_distinguishable_without_javascript(self):
        groups = self.groups + [{**copy.deepcopy(self.groups[0]), 'label': 'Client compute'}]
        markup = curve_groups({'groups': groups, 'default_group': 1}, 'budget')
        self.assertIn('<fieldset', markup)
        self.assertIn('type="radio"', markup)
        self.assertEqual(markup.count(' checked'), 1)
        self.assertIn('id="budget-choice-1" checked', markup)
        self.assertIn('class="rs-curve-group"', markup)
        self.assertNotIn('<script', markup)


if __name__ == '__main__':
    unittest.main()
