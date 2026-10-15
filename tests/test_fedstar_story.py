"""Protect the scientific meaning of the connected FedSTAR example."""
import importlib.util
from pathlib import Path
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'scripts/stories/fedstar_round.py'


class FedSTARStoryTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SOURCE.is_file(), 'The connected FedSTAR story is missing')
        spec = importlib.util.spec_from_file_location('fedstar_round', SOURCE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.steps = module.STEPS
        self.scenes = [ET.fromstring(step['art']) for step in self.steps]

    def test_six_scenes_keep_the_same_client_server_context(self):
        self.assertEqual(len(self.scenes), 6)
        for scene, step in zip(self.scenes, self.steps):
            self.assertEqual(scene.get('role'), 'group')
            self.assertIn('example', scene.get('aria-label').lower())
            self.assertIsNotNone(scene.find('.//*[@data-fs-network]'))
            self.assertIsNotNone(scene.find('.//*[@data-role="server"]'))
            self.assertIsNotNone(scene.find('.//*[@data-role="client"]'))
            self.assertTrue(step['title_in_art'])
            self.assertTrue(7000 <= step['duration_ms'] <= 12000)
            for reveal in scene.findall('.//*[@data-reveal]'):
                self.assertLess(int(reveal.get('data-reveal')), step['duration_ms'] - 1000)

    def test_known_and_unlabeled_batches_start_equally_sized(self):
        pools = self.scenes[0]
        known = pools.find('.//*[@data-batch="labeled"]')
        unknown = pools.find('.//*[@data-batch="unlabeled"]')
        self.assertEqual([c.get('data-clip') for c in known.findall('.//*[@data-clip]')], ['L1', 'L2'])
        self.assertEqual([c.get('data-clip') for c in unknown.findall('.//*[@data-clip]')], ['U1', 'U2'])
        self.assertEqual([c.get('data-label') for c in known.findall('.//*[@data-clip]')], ['go', 'stop'])
        for clip in unknown.findall('.//*[@data-clip]'):
            self.assertIsNone(clip.get('data-label'))

    def test_temperature_predictions_and_clip_identity_survive_filtering(self):
        prediction = self.scenes[1]
        self.assertIsNotNone(prediction.find('.//*[@data-temperature="4"]'))
        expected = {'U1': ('go', .94), 'U2': ('stop', .68)}
        waveforms = {}
        for scene in self.scenes:
            for clip in scene.findall('.//*[@data-clip]'):
                clip_id = clip.get('data-clip')
                wave = clip.find('.//*[@data-waveform]')
                if wave is not None:
                    pattern = wave.get('data-waveform')
                    if clip_id in waveforms:
                        self.assertEqual(waveforms[clip_id], pattern, clip_id)
                    waveforms[clip_id] = pattern
            for example in scene.findall('.//*[@data-confidence]'):
                self.assertEqual((example.get('data-prediction'), float(example.get('data-confidence'))),
                                 expected[example.get('data-example')])
        self.assertEqual(set(waveforms), {'L1', 'L2', 'U1', 'U2'})

    def test_rising_round_threshold_accepts_only_high_confidence_example(self):
        schedule = self.scenes[2].find('.//*[@data-schedule="cosine"]')
        self.assertEqual((float(schedule.get('data-start')), float(schedule.get('data-end'))), (.5, .9))
        self.assertEqual(schedule.get('data-progress'), 'global-round')
        threshold = float(self.scenes[3].find('.//*[@data-threshold]').get('data-threshold'))
        decisions = self.scenes[3].findall('.//*[@data-decision]')
        self.assertEqual(len(decisions), 2)
        for decision in decisions:
            confidence = float(decision.get('data-confidence'))
            if decision.get('data-example') == 'U1':
                self.assertGreater(confidence, threshold)
                self.assertEqual(decision.get('data-decision'), 'accepted')
                self.assertEqual(decision.get('data-target'), 'go')
            else:
                self.assertLess(confidence, threshold)
                self.assertEqual(decision.get('data-decision'), 'deferred')
                self.assertIsNone(decision.get('data-target'))

    def test_one_update_combines_known_targets_and_weighted_accepted_targets(self):
        scene = self.scenes[4]
        supervised = scene.find('.//*[@data-loss="supervised"]')
        pseudo = scene.find('.//*[@data-loss="pseudo"]')
        self.assertEqual([c.get('data-clip') for c in supervised.findall('.//*[@data-clip]')], ['L1', 'L2'])
        self.assertEqual(float(pseudo.get('data-weight')), .5)
        self.assertEqual([c.get('data-clip') for c in pseudo.findall('.//*[@data-clip]')], ['U1'])
        self.assertEqual(pseudo.find('.//*[@data-clip]').get('data-target'), 'go')
        updates = scene.findall('.//*[@data-local-update]')
        self.assertEqual(len(updates), 1, 'Both losses feed one local update')
        self.assertEqual(set(updates[0].get('data-inputs').split()), {'supervised', 'pseudo'})
        self.assertIsNone(scene.find('.//*[@data-clip="U2"][@data-target]'))

    def test_only_models_cross_client_server_boundary(self):
        for scene in self.scenes:
            self.assertIsNotNone(scene.find('.//*[@data-local-only="raw-audio"]'))
            for exchange in scene.findall('.//*[@data-exchange]'):
                self.assertEqual(exchange.get('data-payload'), 'model-parameters')
                self.assertFalse(exchange.findall('.//*[@data-clip]'))
        final = self.scenes[5]
        self.assertIsNotNone(final.find('.//*[@data-aggregation="data-weighted-fedavg"]'))
        self.assertIsNotNone(final.find('.//*[@data-exchange="upload"]'))
        self.assertIsNotNone(final.find('.//*[@data-exchange="broadcast"]'))


if __name__ == '__main__':
    unittest.main()
