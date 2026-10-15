"""Semantic checks for the schematic FedSER round, independent of page wiring."""
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


SOURCE = Path(__file__).resolve().parents[1] / 'scripts/stories/fedser_round.py'


class FedSERStoryTests(unittest.TestCase):
    def scenes(self):
        self.assertTrue(SOURCE.exists(), 'The connected FedSER story is not implemented')
        spec = importlib.util.spec_from_file_location('fedser_round', SOURCE)
        story = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(story)
        return story.STEPS, [ET.fromstring(step['art']) for step in story.STEPS]

    def test_every_stage_keeps_the_sample_local_and_finishes_before_advance(self):
        steps, scenes = self.scenes()
        self.assertEqual(len(steps), 6)
        for step, scene in zip(steps, scenes):
            self.assertEqual(scene.tag, 'div')
            self.assertEqual(scene.get('role'), 'group')
            self.assertTrue(scene.get('aria-label'))
            self.assertTrue(step['title_in_art'])
            self.assertGreaterEqual(step['duration_ms'], 7000)
            self.assertLessEqual(step['duration_ms'], 12000)
            local = scene.find('.//*[@data-se-sample="speech-01"]')
            self.assertIsNotNone(local)
            self.assertEqual(local.get('data-location'), 'client')
            network = scene.find('.//*[@data-se-network]')
            self.assertIn('Server', ''.join(network.itertext()))
            self.assertIn('Client A', ''.join(network.itertext()))
            self.assertTrue(network.findall('.//*[@data-active="true"]'))
            for element in scene.findall('.//*[@data-reveal]'):
                self.assertLess(int(element.get('data-reveal')), step['duration_ms'] - 1000)

    def test_attention_selects_columns_rows_and_a_channel_then_combines_them(self):
        _, scenes = self.scenes()
        scene = scenes[1]
        def selected(key):
            return {(int(cell.get('data-frequency')), int(cell.get('data-time')))
                    for cell in scene.find(f'.//*[@data-grid="{key}"]')
                    if cell.get('data-focused') == 'true'}
        self.assertEqual(selected('time'), {(r, c) for r in range(4) for c in (2, 3)})
        self.assertEqual(selected('frequency'), {(1, c) for c in range(6)})
        channels = scene.findall('.//*[@data-channel-plane]')
        self.assertEqual([int(c.get('data-channel-plane')) for c in channels if c.get('data-focused') == 'true'], [1])
        self.assertEqual(selected('combined'), {(1, 2), (1, 3)})
        self.assertEqual(scene.find('.//*[@data-grid="combined"]').get('data-channel'), '1')

    def test_confidence_example_uses_top_class_and_rejects_ambiguous_sample(self):
        _, scenes = self.scenes()
        candidates = scenes[3].findall('.//*[@data-prediction]')
        self.assertEqual(len(candidates), 2)
        outcomes = {}
        for candidate in candidates:
            scores = {node.get('data-emotion'): float(node.get('data-probability'))
                      for node in candidate.findall('.//*[@data-probability]')}
            self.assertEqual(set(scores), {'neutral', 'happy', 'sad', 'angry'})
            self.assertAlmostEqual(sum(scores.values()), 1)
            winner = max(scores, key=scores.get)
            self.assertEqual(candidate.get('data-top-class'), winner)
            accepted = scores[winner] > float(candidate.get('data-threshold'))
            self.assertEqual(candidate.get('data-outcome'), 'use' if accepted else 'defer')
            self.assertEqual(candidate.get('data-example'), 'true')
            outcomes[candidate.get('data-prediction')] = candidate.get('data-outcome')
        self.assertEqual(outcomes, {'speech-01': 'use', 'speech-02': 'defer'})

    def test_only_accepted_pseudo_label_joins_supervised_loss(self):
        _, scenes = self.scenes()
        losses = scenes[4].findall('.//*[@data-loss-kind]')
        self.assertEqual({node.get('data-loss-kind') for node in losses}, {'supervised', 'pseudo-label'})
        sources = {node.get('data-loss-kind'): node.get('data-loss-source') for node in losses}
        self.assertEqual(sources, {'supervised': 'known-01', 'pseudo-label': 'speech-01'})
        merge = scenes[4].find('.//*[@data-joint-loss]')
        self.assertEqual(merge.get('data-inputs'), 'supervised,pseudo-label')
        self.assertEqual(merge.get('data-output'), 'local-parameters')

    def test_upload_and_return_contain_parameters_and_use_data_weighted_average(self):
        _, scenes = self.scenes()
        payloads = scenes[5].findall('.//*[@data-transfer]')
        self.assertEqual({node.get('data-transfer') for node in payloads}, {'upload', 'broadcast'})
        self.assertTrue(all(node.get('data-payload') == 'model-parameters' for node in payloads))
        aggregate = scenes[5].find('.//*[@data-aggregation]')
        self.assertEqual(aggregate.get('data-aggregation'), 'FedAvg')
        self.assertEqual(aggregate.get('data-weighting'), 'local-data-size')
        self.assertEqual(aggregate.get('data-output'), 'next-global-model')
        self.assertIsNotNone(scenes[0].find('.//*[@data-input-model="global-model"]'))


if __name__ == '__main__':
    unittest.main()
