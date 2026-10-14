import importlib.util
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_projects', ROOT / 'scripts/build_projects.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class Catalog(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.years = []
        self.cards = {}
        self.links = []
        self.ids = set()
        self.current_year = None
        self.feed(markup)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if 'data-project-year' in attrs:
            self.current_year = int(attrs['data-project-year'])
            self.years.append(self.current_year)
        if tag == 'article' and 'data-project' in attrs:
            self.cards[attrs['data-project']] = {**attrs, 'year': self.current_year}
        if tag == 'a':
            self.links.append(attrs)


class ResearchHomeTests(unittest.TestCase):
    def setUp(self):
        self.projects = build.load_projects()
        self.html = build.gallery_page(self.projects, home=True)
        self.catalog = Catalog(self.html)

    def test_every_public_paper_appears_once_in_the_correct_descending_year(self):
        self.assertEqual(len(self.catalog.cards), 14)
        self.assertEqual(self.catalog.years, [2026, 2025, 2024, 2023, 2022])
        for p in self.projects:
            self.assertEqual(self.catalog.cards[p['slug']]['year'], p['year'])
            self.assertNotIn('hidden', self.catalog.cards[p['slug']])
        self.assertNotIn('logipuz', self.catalog.cards)
        self.assertNotIn('sdapt', self.catalog.cards)

    def test_method_names_and_established_acronyms_are_searchable(self):
        terms = self.catalog.cards['fedln']['data-search']
        for term in ['NNC', 'AKD', 'NA-FedAvg', 'Nearest Neighbor Correction']:
            self.assertIn(term, terms)
        for p in self.projects:
            self.assertIn(p['title'], self.catalog.cards[p['slug']]['data-search'])

    def test_research_topics_follow_actual_training_and_privacy_contributions(self):
        cards = self.catalog.cards
        for slug in ['plix', 'da-mldg']:
            self.assertIn('reliable', cards[slug]['data-areas'])
            self.assertNotIn('decentralized', cards[slug]['data-areas'])
        self.assertIn('reliable', cards['fedser']['data-areas'])
        self.assertNotIn('privacy', cards['fedser']['data-areas'])
        self.assertEqual(set(cards['enccluster']['data-areas'].split()), {'foundation', 'privacy', 'decentralized'})

    def test_single_catalog_and_correct_code_destinations(self):
        self.assertIn('rel="canonical" href="https://nousphera.github.io/"', self.html)
        self.assertNotIn('Explore the code', self.html)
        self.assertNotIn('href="/projects/"', self.html)
        self.assertIn('href="https://huggingface.co/aaqibsaeed/plixkws"', self.html)
        for link in self.catalog.links:
            for key in ['aria-labelledby', 'aria-describedby']:
                if key in link:
                    self.assertTrue(all(i in self.catalog.ids for i in link[key].split()))

    def test_legacy_catalog_has_a_canonical_and_working_no_script_link(self):
        from research_home import legacy_gallery
        markup = legacy_gallery(build.asset_url)
        self.assertIn('href="/#collection"', markup)
        self.assertIn('rel="canonical" href="https://nousphera.github.io/"', markup)
        self.assertNotIn('http-equiv="refresh"', markup)


if __name__ == '__main__':
    unittest.main()
