"""Regression checks for published scientific values and static fallbacks."""
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_projects as build


class Markup(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.bars = []; self.ids = []; self.panels = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if 'data-tab-panel' in a: self.panels.append(a)
        if 'data-value' in a: self.bars.append(a)


class FedLNPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = next(p for p in build.load_projects() if p['slug'] == 'fedln')
        cls.html = build.project_page(cls.p, [cls.p])
        cls.markup = Markup(cls.html)

    def test_figure8_and_table3_values_are_preserved(self):
        expected = ['65.68','67.31','70.02','74.69','70.39','70.06',
                    '47.25','48.72','54.12','55.39','57.39','53.99',
                    '57.65','67.27','74.76','68.43','65.34',
                    '63.54','65.23','54.59','68.39','67.92']
        self.assertEqual([b['data-value'] for b in self.markup.bars], expected)
        for bar in self.markup.bars:
            self.assertIn('data-method', bar)
            self.assertIn(f'--fl-value:{bar["data-value"]}%', self.html)
        self.assertIn('0–100%', self.html)
        self.assertIn('falls below FedAvg', self.html)

    def test_static_sections_and_tour_are_readable_without_scripts(self):
        self.assertEqual([p['id'] for p in self.markup.panels], ['overview','method','findings','citation'])
        self.assertTrue(all('hidden' not in p for p in self.markup.panels))
        self.assertEqual(len(self.markup.ids), len(set(self.markup.ids)))
        self.assertIn('fl-tour-fallback', self.html)
        self.assertIn(build.esc(self.p['abstract']), self.html)
        self.assertIn('Earlier workshop version', self.html)
        self.assertNotIn('<!-- FEDLN_TOUR -->', self.html)

    def test_equations_are_native_accessible_mathml(self):
        import re
        equations = re.findall(r'<math\b.*?</math>', self.html, re.S)
        self.assertEqual(len(equations), 3)
        for markup in equations:
            math = ElementTree.fromstring(markup)
            self.assertTrue(math.attrib.get('aria-label'))
        self.assertIn('tied votes are broken randomly', self.html)
        self.assertIn('mean absolute error', self.html)
        self.assertIn('without adding a normalization term', self.html)


if __name__ == '__main__': unittest.main()
