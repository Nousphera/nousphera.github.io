"""All public walkthroughs share compact copy and safe progressive disclosure."""
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from paper_experience import load_story, CONNECTED_STORIES, STORY_STYLES
from build_projects import load_projects

class AnimationContractTests(unittest.TestCase):
    def test_every_animation_finishes_revealing_before_step_end(self):
        for p in load_projects():
            if p['slug']=='fedln': continue
            for step in load_story(p['slug'])['steps']:
                root=ET.fromstring(step.get('art', step.get('svg','')))
                visible=' '.join(root.itertext())+' '+step['caption']
                self.assertNotRegex(visible,r'(?i)\b(?:illustrat\w*|schematic|example\s*[:·])',p['slug'])
                self.assertLessEqual(len(step['caption'].split()),16,p['slug'])
                self.assertTrue(root.get('aria-label'),p['slug'])
                for node in root.findall('.//*[@data-reveal]'):
                    self.assertLess(int(node.get('data-reveal')),step.get('duration_ms',6000)-1000,p['slug'])

    def test_connected_art_has_responsive_styles_and_manual_navigation(self):
        root=Path(__file__).resolve().parents[1]
        self.assertEqual(set(CONNECTED_STORIES),set(STORY_STYLES))
        for slug,style in STORY_STYLES.items():
            self.assertTrue((root/'assets'/f'{style}-story.css').exists(),slug)
            for step in load_story(slug)['steps']:
                self.assertTrue(step.get('title_in_art'),slug)
                self.assertTrue(step.get('art'),slug)

if __name__=='__main__':unittest.main()
