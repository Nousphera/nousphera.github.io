"""Check the published metadata/PDF relationship, not just template strings."""
import importlib.util
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_projects', ROOT / 'scripts/build_projects.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.meta = {}; self.links = []; self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs); self.tags.append(tag)
        if tag == 'meta' and attrs.get('name', '').startswith('citation_'):
            self.meta.setdefault(attrs['name'], []).append(attrs['content'])
        if tag == 'a':
            self.links.append(attrs.get('href'))


class ScholarTests(unittest.TestCase):
    def test_all_papers_have_searchable_full_text_and_matching_metadata(self):
        from scholar import record
        for p in build.load_projects():
            with self.subTest(paper=p['slug']):
                folder = ROOT / 'projects' / p['slug']
                item = record(p)  # validates PDF signature, size and SHA-256
                base = f'https://nousphera.github.io/projects/{p["slug"]}/'
                pages = [Page((folder / name).read_text()) for name in ['index.html', 'paper.html']]
                self.assertEqual(pages[0].meta, pages[1].meta)
                m = pages[0].meta
                self.assertEqual(m['citation_title'], [p['title']])
                self.assertEqual(m['citation_author'], p['authors'])
                self.assertEqual(m['citation_pdf_url'], [base + 'paper.pdf'])
                self.assertEqual(m['citation_abstract_html_url'], [base + 'paper.html'])
                if 'doi =' in p['bibtex']:
                    self.assertTrue(m['citation_doi'])
                html = (folder / 'paper.html').read_text()
                self.assertIn(build.esc(item['abstract']), html)
                self.assertNotIn('details', pages[1].tags)
                self.assertNotIn('hidden', html)
                self.assertIn('paper.pdf', pages[1].links)
                text = subprocess.check_output(['pdftotext', str(folder / 'paper.pdf'), '-'], text=True)
                self.assertGreater(len(text), 4000)
                self.assertIn('references', re.sub(r'\s+', '', text).lower())
                self.assertIn('tsouvalas', text.lower())

    def test_sitemap_contains_each_project_and_abstract_record(self):
        urls = {e.text for e in ET.parse(ROOT / 'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
        for p in build.load_projects():
            base = f'https://nousphera.github.io/projects/{p["slug"]}/'
            self.assertIn(base, urls)
            self.assertIn(base + 'paper.html', urls)


if __name__ == '__main__':
    unittest.main()
