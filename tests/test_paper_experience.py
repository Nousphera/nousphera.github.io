import copy
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_projects as build
from paper_experience import load_story, validate_story

class PaperExperienceTests(unittest.TestCase):
    def test_connected_walkthroughs_keep_navigation_and_text_light_scenes(self):
        projects = build.load_projects()
        for slug in ['mpsl', 'fedstar', 'fedser']:
            p = next(p for p in projects if p['slug'] == slug)
            story = load_story(slug)
            self.assertEqual(len(story['steps']), 6, slug)
            html = build.project_page(p, projects)
            self.assertIn('class="paper-story connected-story"', html)
            self.assertIn(f'data-story-kind="{slug}"', html)
            self.assertIn('data-story-navigation hidden', html)
            self.assertIn('assets/connected-story.css?', html)
            self.assertIn(f'assets/{slug}-story.css?', html)
            for step in story['steps']:
                self.assertTrue(step.get('title_in_art'), slug)
                self.assertLessEqual(len(step['caption'].split()), 16, slug)

    def test_every_other_paper_has_complete_distinct_source_bound_experience(self):
        projects=build.load_projects(); artwork=set(); count=0
        for p in projects:
            if p['slug']=='fedln': continue
            s=load_story(p['slug']);self.assertIsNotNone(s,p['slug']);validate_story(s)
            html=build.project_page(p,projects)
            for fragment in ['data-paper-story','data-story-toggle','class="hero-topics"','class="results-panel"','Takeaways']:
                self.assertIn(fragment,html,p['slug'])
            for panel in ['overview','method','findings','citation']:
                self.assertEqual(html.count(f'id="{panel}" data-tab-panel'),1,p['slug'])
            self.assertIn(build.esc(p['abstract']),html)
            for step in s['steps']:
                art=step.get('art',step.get('svg',''))
                digest=hashlib.sha256(art.encode()).hexdigest()
                self.assertNotIn(digest,artwork,'Every scene must explain its own operation')
                artwork.add(digest);count+=1
                self.assertIn('data-reveal=',art)
                self.assertTrue(step.get('short_title'),p['slug'])
                # No hard-coded palette can become illegible after a theme change.
                self.assertIsNone(re.search(r'(?:fill|stroke)="#[0-9a-fA-F]',art))
        self.assertGreaterEqual(count,39)

    def test_story_markup_cannot_inject_scripts_or_external_assets(self):
        s=copy.deepcopy(load_story('fedcompress'))
        s['overview']='<a href="javascript:alert(1)">Test</a>'
        with self.assertRaises(ValueError):validate_story(s)
        s=copy.deepcopy(load_story('fedcompress'))
        s['steps'][0]['art' if 'art' in s['steps'][0] else 'svg']='<svg aria-label="Bad"><image href="https://external.example/a"/></svg>'
        with self.assertRaises(ValueError):validate_story(s)

if __name__=='__main__':unittest.main()
