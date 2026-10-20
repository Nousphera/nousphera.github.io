import copy
import importlib.util
import json
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_projects', ROOT / 'scripts/build_projects.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

class ProjectTests(unittest.TestCase):
    def test_html_and_structured_data_escape_untrusted_text(self):
        p = copy.deepcopy(build.load_projects()[0])
        p['title'] = '<script>wrong</script> & "quoted"'
        p['summary'] = '</script><script>alert(1)</script>'
        html = build.project_page(p, [p])
        self.assertNotIn('<script>wrong', html)
        self.assertNotIn('<script>alert', html)
        self.assertIn('&lt;script&gt;wrong', html)
        self.assertIn('application/ld+json', html)

    def test_catalog_complete_unique_and_assets_exist(self):
        projects = build.load_projects()
        self.assertEqual(len(projects), 15)
        self.assertEqual(len({p['slug'] for p in projects}), 15)
        for p in projects:
            build.validate(p)
            for key in ('figure', 'secondary_figure'):
                if key in p:
                    self.assertTrue((ROOT / p[key]['src']).is_file(), p['slug'])
                    self.assertGreater(p[key]['width'], 0)
                    self.assertGreater(p[key]['height'], 0)
            self.assertTrue(p['bibtex'].startswith('@'))
            self.assertNotIn('FederatedML', json.dumps(p))
            self.assertNotIn('/Users/', json.dumps(p))

    def test_rejects_nonpublic_or_script_resource_urls(self):
        p = copy.deepcopy(build.load_projects()[0])
        for url in ['javascript:alert(1)', 'http://localhost/a', 'file:///tmp/a', '//example.com']:
            p['links']['Paper'] = url
            with self.assertRaises(ValueError):
                build.validate(p)

    def test_no_javascript_needed_for_paper_content(self):
        p = build.load_projects()[0]
        html = build.project_page(p, [p])
        for text in ['id="method"', 'id="findings"', 'id="citation"', 'download', '<details', 'name="citation_author"', 'rel="canonical"']:
            self.assertIn(text, html)
        self.assertIn(build.esc(p['abstract']), html)
        self.assertIn('width="', html)
        self.assertIn('height="', html)

    def test_gallery_filter_metadata_has_paper_terms(self):
        projects = build.load_projects()
        html = build.gallery_page(projects)
        for p in projects:
            self.assertIn(f'/projects/{p["slug"]}/', html)
            self.assertIn(build.esc(p['name'].lower()), html.lower())
        self.assertIn('role="status"', html)

    def test_publication_metadata_uses_citation_year(self):
        p = next(p for p in build.load_projects() if p['slug'] == 'deltamask')
        self.assertEqual(p['year'], 2024)
        html = build.project_page(p, [p])
        self.assertIn('name="citation_publication_date" content="2025"', html)
        self.assertIn('IEEE BigData 2024', html)

    def test_abstract_source_is_visible_and_validated(self):
        p = copy.deepcopy(next(p for p in build.load_projects() if p['slug'] == 'fedcode'))
        html = build.project_page(p, [p])
        self.assertIn(build.esc(p['abstract_source']['note']), html)
        p['abstract_source']['url'] = 'javascript:alert(1)'
        with self.assertRaises(ValueError):
            build.validate(p)

    def test_local_page_links_and_fragments_resolve(self):
        class Links(HTMLParser):
            def __init__(self):
                super().__init__(); self.urls = []; self.ids = set()
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if 'id' in attrs: self.ids.add(attrs['id'])
                for key in ('href', 'src'):
                    if key in attrs: self.urls.append(attrs[key])
        pages = [ROOT / 'index.html', *sorted((ROOT / 'projects').rglob('index.html'))]
        self.assertEqual(len(pages), 17)
        for page in pages:
            parser = Links(); parser.feed(page.read_text())
            for url in parser.urls:
                parsed = urlparse(url)
                if parsed.scheme or parsed.netloc: continue
                target = ROOT / unquote(parsed.path).lstrip('/') if parsed.path.startswith('/') else page.parent / unquote(parsed.path)
                if not parsed.path: target = page
                if target.is_dir(): target = target / 'index.html'
                self.assertTrue(target.exists(), f'{page}: {url}')
                if parsed.fragment and target.suffix == '.html':
                    other = Links(); other.feed(target.read_text())
                    self.assertIn(parsed.fragment, other.ids, f'{page}: {url}')

if __name__ == '__main__':
    unittest.main()
