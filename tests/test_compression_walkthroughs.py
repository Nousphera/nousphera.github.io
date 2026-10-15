"""Protect FedCompress and FedCode's distinct transformations and transfers."""
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from paper_experience import load_story, validate_story


def values(node):
    return [float(v) for v in node.get('data-values').split(',')]


class CompressionWalkthroughTests(unittest.TestCase):
    def scenes(self, slug):
        story = load_story(slug)
        self.assertEqual(len(story['steps']), 6, slug)
        return [ET.fromstring(step['art']) for step in story['steps']]

    def test_navigation_names_the_operation_in_each_reordered_scene(self):
        compress = load_story('fedcompress')['steps']
        code = load_story('fedcode')['steps']
        self.assertEqual(compress[3]['short_title'], 'Distill')
        self.assertEqual(compress[4]['short_title'], 'Adapt capacity')
        self.assertEqual(code[3]['short_title'], 'Map globally')
        self.assertEqual(code[5]['short_title'], 'Calibrate')

    def test_centroid_identity_survives_concatenation_and_index_reconstruction(self):
        scenes = self.scenes('fedcode')
        identities = {}
        for scene in scenes:
            for token in scene.findall('.//*[@data-value-tone]'):
                value = float(token.get('data-value'))
                tone = token.get('data-value-tone')
                if value in identities:
                    self.assertEqual(identities[value], tone, f'Value {value} changed visual identity')
                identities[value] = tone
        self.assertTrue({-1.2, 1.4, -.6, .9}.issubset(identities))
        self.assertEqual(len({identities[v] for v in [-1.2, 1.4, -.6, .9]}), 4)
        rebuilt = scenes[5].find('.//*[@data-indices="calibration"]')
        self.assertEqual([float(t.get('data-value')) for t in rebuilt.findall('.//*[@data-value-tone]')],
                         [-1.2, -1.2, .9, .9])

    def test_connected_scenes_are_accessible_text_light_and_fully_revealed(self):
        for slug in ['fedcompress', 'fedcode']:
            story = load_story(slug)
            scenes = self.scenes(slug)
            validate_story(story)
            for scene, step in zip(scenes, story['steps']):
                self.assertEqual(scene.tag, 'div')
                self.assertEqual(scene.get('role'), 'group')
                self.assertIsNotNone(scene.find('.//*[@data-cw-network]'))
                self.assertIsNotNone(scene.find('.//*[@data-role="server"]'))
                self.assertIsNotNone(scene.find('.//*[@data-role="client"]'))
                self.assertTrue(step['title_in_art'])
                self.assertLessEqual(len(step['caption'].split()), 16)
                self.assertTrue(7000 <= step['duration_ms'] <= 12000)
                self.assertIsNone(re.search(r'\b(example|illustration|schematic)\b', ' '.join(scene.itertext()), re.I))
                for part in scene.findall('.//*[@data-reveal]'):
                    self.assertLess(int(part.get('data-reveal')), step['duration_ms'] - 1000)

    def test_compress_average_preserves_positions_but_breaks_cluster_count(self):
        scenes = self.scenes('fedcompress')
        scene = scenes[2]
        a = values(scene.find('.//*[@data-weights="client-a"]'))
        b = values(scene.find('.//*[@data-weights="client-b"]'))
        mean = values(scene.find('.//*[@data-weights="aggregated"]'))
        self.assertEqual(a, [-1, -1, 1, 1])
        self.assertEqual(b, [0, 2, 0, 2])
        self.assertEqual(mean, [-.5, .5, .5, 1.5])
        self.assertEqual(len(set(a)), 2)
        self.assertEqual(len(set(b)), 2)
        self.assertEqual(len(set(mean)), 3)
        self.assertIsNotNone(scene.find('.//*[@data-aggregation="fedavg"]'))
        self.assertEqual(values(scenes[3].find('.//*[@data-weights="teacher"]')), mean)

    def test_compress_distills_on_server_data_with_a_clustering_objective(self):
        scene = self.scenes('fedcompress')[3]
        data = scene.find('.//*[@data-distill-data]')
        self.assertEqual(data.get('data-location'), 'server')
        self.assertEqual(data.get('data-labels'), 'none')
        self.assertEqual(data.get('data-distribution'), 'ood')
        self.assertEqual(set(data.get('data-feeds').split()), {'teacher', 'student'})
        objective = scene.find('.//*[@data-objective]')
        self.assertEqual(set(objective.get('data-objective').split()), {'kl', 'weight-clustering'})
        self.assertEqual(len(set(values(scene.find('.//*[@data-weights="student"]')))), 2)

    def test_compress_capacity_uses_client_effective_rank_and_server_progress(self):
        scene = self.scenes('fedcompress')[4]
        self.assertEqual(scene.find('.//*[@data-score="effective-rank"]').get('data-location'), 'client')
        self.assertEqual(scene.find('.//*[@data-score-aggregation]').get('data-score-aggregation'), 'data-weighted')
        self.assertEqual(scene.find('.//*[@data-capacity-trigger]').get('data-capacity-trigger'), 'moving-average-plateau')
        self.assertEqual(scene.find('.//*[@data-capacity-update]').get('data-capacity-update'), 'increase-within-budget')

    def test_code_client_uses_nearest_values_without_receiving_sender_positions(self):
        scenes = self.scenes('fedcode')
        scene = scenes[1]
        centers = values(scene.find('.//*[@data-codebook="global"]'))
        self.assertEqual(centers, [-1, 1])
        self.assertEqual(values(scene.find('.//*[@data-weights="stored-local"]')), [-.8, .7, -.6, 1.2])
        self.assertEqual(values(scene.find('.//*[@data-weights="mapped-local"]')), [-1, 1, -1, 1])
        transfer = scene.find('.//*[@data-transfer="down"]')
        self.assertEqual(transfer.get('data-payload'), 'codebook')
        self.assertFalse(transfer.findall('.//*[@data-indices]'))
        self.assertNotEqual(values(scenes[0].find('.//*[@data-weights="global"]')),
                            values(scene.find('.//*[@data-weights="mapped-local"]')))

    def test_code_server_concatenates_centers_then_remaps_existing_weights(self):
        scene = self.scenes('fedcode')[3]
        self.assertEqual(values(scene.find('.//*[@data-codebook="client-a"]')), [-1.2, 1.4])
        self.assertEqual(values(scene.find('.//*[@data-codebook="client-b"]')), [-.6, .9])
        self.assertEqual(values(scene.find('.//*[@data-codebook="combined"]')), [-1.2, -.6, .9, 1.4])
        self.assertEqual(values(scene.find('.//*[@data-weights="remapped-global"]')), [-1.2, -1.2, .9, .9])
        self.assertIsNotNone(scene.find('.//*[@data-server-update="nearest-center"]'))
        self.assertIsNone(scene.find('.//*[@data-aggregation="fedavg"]'))

    def test_code_calibration_transmits_indices_and_reconstructs_sender_positions(self):
        scene = self.scenes('fedcode')[5]
        self.assertEqual(scene.get('data-round-kind'), 'periodic-calibration')
        self.assertEqual(values(scene.find('.//*[@data-codebook="calibration"]')), [-1.2, .9])
        self.assertEqual(scene.find('.//*[@data-indices="calibration"]').get('data-values'), '0,0,1,1')
        self.assertEqual(values(scene.find('.//*[@data-weights="calibrated"]')), [-1.2, -1.2, .9, .9])
        transfer = scene.find('.//*[@data-transfer="calibration"]')
        self.assertEqual(transfer.get('data-payload'), 'codebook indices')
        average = scene.find('.//*[@data-aggregation="fedavg"]')
        self.assertEqual(average.get('data-direction'), 'up')
        self.assertEqual(average.get('data-input'), 'reconstructed-client-models')


if __name__ == '__main__':
    unittest.main()
