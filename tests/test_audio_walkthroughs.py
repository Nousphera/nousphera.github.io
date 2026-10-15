"""Protect support/query and source/target boundaries in the visual explanations."""
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree as ET
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from stories.audio_walkthroughs import PLIX_STEPS, DA_STEPS

class AudioWalkthroughTests(unittest.TestCase):
    def test_training_uses_known_query_labels_and_support_means(self):
        root=ET.fromstring(PLIX_STEPS[0]['art'])
        self.assertEqual(root.find('.//*[@data-query-label]').get('data-query-label'),'Go')
        self.assertEqual(root.find('.//*[@data-loss]').get('data-loss'),'cross-entropy')
        self.assertEqual(root.find('.//*[@data-label-source]').get('data-label-source'),'query-ground-truth')
        self.assertEqual(root.find('.//*[@data-prototype-source]').get('data-prototype-source'),'support-only')

    def test_support_observations_stay_fixed_during_mean_animation(self):
        root=ET.fromstring(PLIX_STEPS[2]['art'])
        supports=[e for e in root.iter() if e.get('class')=='ax-support-dot']
        contributions=[e for e in root.iter() if 'ax-contribution' in e.get('class','')]
        self.assertEqual(len(supports),6)
        self.assertEqual(len(contributions),6)
        self.assertTrue(all(e.get('style') is None for e in supports))

    def test_plix_query_never_changes_support_mean(self):
        for step in PLIX_STEPS[1:]:
            root=ET.fromstring(step['art'])
            for encoder in root.findall('.//*[@data-encoder-state]'):
                self.assertEqual(encoder.get('data-encoder-state'),'frozen')
        mean=ET.fromstring(PLIX_STEPS[2]['art'])
        self.assertEqual(mean.find('.//*[@data-query-in-mean]').get('data-query-in-mean'),'false')
        self.assertFalse(mean.findall('.//*[@data-clip-kind="query"]'))
        query=ET.fromstring(PLIX_STEPS[3]['art'])
        self.assertTrue(query.findall('.//*[@data-clip-kind="query"]'))
        self.assertEqual(query.find('.//*[@data-prototype-source]').get('data-prototype-source'),'support-only')

    def test_new_vocabulary_reuses_frozen_encoder(self):
        root=ET.fromstring(PLIX_STEPS[-1]['art'])
        self.assertEqual({n.get('data-prototype') for n in root.findall('.//*[@data-prototype]')},{'Left','Right'})
        self.assertEqual(root.find('.//*[@data-encoder-state]').get('data-encoder-state'),'frozen')

    def test_da_target_is_held_out_until_evaluation(self):
        for i,step in enumerate(DA_STEPS):
            nodes=ET.fromstring(step['art']).findall('.//*[@data-target-access]')
            self.assertTrue(nodes)
            self.assertEqual({n.get('data-target-access') for n in nodes},{'excluded' if i<4 else 'evaluation-only'})
        self.assertIn('θ′',DA_STEPS[2]['art'])
        self.assertIn('L<sub>train</sub>(θ)',DA_STEPS[3]['art'])
        self.assertIn('L<sub>test</sub>(θ′)',DA_STEPS[3]['art'])

    def test_art_is_compact_accessible_and_theme_safe(self):
        for step in PLIX_STEPS+DA_STEPS:
            root=ET.fromstring(step['art'])
            self.assertTrue(root.get('aria-label'))
            self.assertLessEqual(len(step['caption'].split()),16)
            self.assertTrue(step['title_in_art'])
            for part in root.findall('.//*[@data-reveal]'):
                self.assertLess(int(part.get('data-reveal')),step['duration_ms']-1000)
            self.assertNotRegex(' '.join(root.itertext()),r'(?i)\b(example|illustrative|schematic)\b')

if __name__=='__main__':unittest.main()
