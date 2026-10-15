"""Protocol-boundary checks for EncCluster, EFU and FiBA artwork."""
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from stories.privacy import STORIES


class PrivacyWalkthroughTests(unittest.TestCase):
    def scenes(self, slug):
        steps = STORIES[slug]['steps']
        self.assertTrue(all('art' in step for step in steps), 'Connected artwork is missing')
        return steps, [ET.fromstring(step['art']) for step in steps]

    def test_walkthroughs_keep_roles_and_allow_reveals_to_complete(self):
        for slug in ('enccluster', 'efu', 'fiba'):
            steps, scenes = self.scenes(slug)
            self.assertTrue(4 <= len(steps) <= 6)
            for step, scene in zip(steps, scenes):
                self.assertEqual(scene.tag, 'div')
                self.assertTrue(scene.get('aria-label'))
                self.assertTrue(step['title_in_art'])
                self.assertLessEqual(len(step['caption'].split()), 16)
                self.assertTrue(7000 <= step['duration_ms'] <= 12000)
                self.assertIsNotNone(scene.find('.//*[@data-pw-context]'))
                for node in scene.findall('.//*[@data-reveal]'):
                    self.assertLess(int(node.get('data-reveal')), step['duration_ms'] - 1000)

    def test_enccluster_substitutes_encrypted_centroids_in_recovered_positions(self):
        _, scenes = self.scenes('enccluster')
        mapping = scenes[3].find('.//*[@data-position-map="recovered"]')
        self.assertEqual(mapping.get('data-location'), 'server')
        self.assertEqual(mapping.get('data-values'), 'A,B,A,B,B,A')
        expanded = scenes[4].find('.//*[@data-expanded-model]')
        self.assertEqual([node.get('data-centroid') for node in expanded], ['A', 'B', 'A', 'B', 'B', 'A'])
        self.assertTrue(all(node.get('data-encrypted') == 'true' for node in expanded))
        self.assertIsNotNone(scenes[3].find('.//*[@data-shared-seed="true"]'))

    def test_encrypted_protocols_share_aggregate_only_and_differ_in_mapping_transport(self):
        for slug, mapping_type in [('enccluster', 'bf-fingerprints'), ('efu', 'visible-map')]:
            _, scenes = self.scenes(slug)
            payloads = [node.get('data-payload') for scene in scenes for node in scene.findall('.//*[@data-upload]')]
            self.assertEqual(set(payloads), {'encrypted-centroids', mapping_type, 'partial-key'})
            decryptions = [node for scene in scenes for node in scene.findall('.//*[@data-decrypt]')]
            self.assertTrue(decryptions)
            self.assertTrue(all(node.get('data-decrypt') == 'weighted-aggregate' for node in decryptions))
            self.assertIsNotNone(scenes[-1].find('.//*[@data-broadcast="global-model"]'))

    def test_efu_local_branches_are_alternatives_and_unlearning_has_three_terms(self):
        _, scenes = self.scenes('efu')
        alternatives = scenes[0].find('.//*[@data-local-alternatives]')
        self.assertEqual({node.get('data-local-mode') for node in alternatives.findall('.//*[@data-local-mode]')}, {'learn', 'unlearn'})
        terms = {node.get('data-loss-term'): node for node in scenes[1].findall('.//*[@data-loss-term]')}
        self.assertEqual(set(terms), {'negative-cross-entropy', 'adversarial-cross-entropy', 'inverted-mas'})
        self.assertEqual(terms['adversarial-cross-entropy'].get('data-preparation'), 'offline-once')
        self.assertEqual(terms['adversarial-cross-entropy'].get('data-target'), 'incorrect-label')

    def test_efu_aggregation_key_binds_function_and_round(self):
        _, scenes = self.scenes('efu')
        binding = scenes[4].find('.//*[@data-key-binding]')
        self.assertEqual(binding.get('data-key-binding'), 'function,round')
        self.assertEqual(binding.find('.//*[@data-request="authorized"]').get('data-decryptable'), 'true')
        self.assertEqual(binding.find('.//*[@data-request="omit-client"]').get('data-decryptable'), 'false')

    def test_fiba_poisoning_and_defense_comparison_do_not_become_one_pipeline(self):
        _, scenes = self.scenes('fiba')
        poisoned = scenes[1].find('.//*[@data-poisoned-input]')
        self.assertEqual(poisoned.get('data-location'), 'attacker-client')
        self.assertEqual(poisoned.get('data-target'), 't')
        self.assertEqual(poisoned.get('data-transform'), 'LSB')
        choices = scenes[3].find('.//*[@data-aggregation-alternatives]')
        self.assertEqual(choices.get('data-selection'), 'one-per-run')
        self.assertEqual({node.get('data-rule') for node in choices.findall('.//*[@data-rule]')}, {'FedAvg', 'Median', 'Trimmed Mean', 'FoolsGold', 'KRUM', 'Multi-KRUM'})
        metrics = {node.get('data-metric') for node in scenes[4].findall('.//*[@data-metric]')}
        self.assertEqual(metrics, {'clean-accuracy', 'attack-success', 'LPIPS', 'Neural-Cleanse'})
        probe = scenes[5].find('.//*[@data-placement-probe]')
        self.assertEqual(probe.get('data-attack-family'), 'LSB')
        self.assertEqual(probe.get('data-trigger-sizes'), '500,700')
        self.assertEqual(probe.get('data-after-convergence'), 'true')

    def test_fiba_low_and_high_placement_cover_equal_complementary_halves(self):
        _, scenes = self.scenes('fiba')
        masks = {}
        for kind in ('low', 'high', 'all'):
            grid = scenes[5].find(f'.//*[@data-activation-map="{kind}"]')
            self.assertIsNotNone(grid, 'Placement cells must expose the illustrated activation ranking')
            masks[kind] = {int(cell.get('data-cell')): float(cell.get('data-level'))
                           for cell in grid if cell.get('data-selected') == 'true'}
        self.assertEqual(len(masks['low']), 10)
        self.assertEqual(len(masks['high']), 10)
        self.assertFalse(masks['low'].keys() & masks['high'].keys())
        self.assertEqual(masks['low'].keys() | masks['high'].keys(), masks['all'].keys())
        self.assertLessEqual(max(masks['low'].values()), min(masks['high'].values()))


if __name__ == '__main__':
    unittest.main()
