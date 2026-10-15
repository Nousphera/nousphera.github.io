"""Guard the source's split boundary and the identity of each client's batch."""
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
try:
    from stories.mpsl_round import STEPS
except ModuleNotFoundError:
    STEPS = []


class MPSLStoryTests(unittest.TestCase):
    def setUp(self):
        self.assertEqual(len(STEPS), 6, 'One complete six-stage training cycle')
        self.scenes = [ET.fromstring(step['art']) for step in STEPS]

    def test_transfers_follow_the_paper_and_preserve_client_batches(self):
        # A wrong payload or reversed edge would teach a different algorithm.
        expected = [
            (1, 'activations', 'client', 'server'),
            (2, 'predictions', 'server', 'client'),
            (3, 'local-loss', 'client', 'server'),
            (4, 'cut-gradients', 'server', 'client'),
        ]
        for index, payload, source, destination in expected:
            transfers = self.scenes[index].findall('.//*[@data-ms-transfer]')
            self.assertEqual(len(transfers), 2)
            self.assertEqual({x.attrib['data-client'] for x in transfers}, {'A', 'B'})
            for transfer in transfers:
                self.assertEqual(transfer.attrib['data-ms-transfer'], payload)
                self.assertEqual(transfer.attrib['data-from'], source)
                self.assertEqual(transfer.attrib['data-to'], destination)
                self.assertEqual(transfer.attrib['data-batch'], 'batch-' + transfer.attrib['data-client'])
        for index in (0, 5):
            self.assertEqual(self.scenes[index].findall('.//*[@data-ms-transfer]'), [])

    def test_raw_inputs_and_labels_remain_with_both_clients(self):
        for scene in self.scenes:
            network = scene.find('.//*[@data-ms-network]')
            self.assertIsNotNone(network)
            self.assertEqual(len(network.findall('.//*[@data-ms-server]')), 1)
            for client in ('A', 'B'):
                endpoint = network.find(f'.//*[@data-ms-client="{client}"]')
                self.assertIsNotNone(endpoint)
                self.assertIsNotNone(endpoint.find('.//*[@data-local-only="inputs"]'))
                self.assertIsNotNone(endpoint.find('.//*[@data-local-only="labels"]'))
            for transfer in scene.findall('.//*[@data-ms-transfer]'):
                self.assertEqual(transfer.findall('.//*[@data-local-only]'), [])

    def test_late_fusion_keeps_clients_separate_and_uses_one_encoder(self):
        encoder = self.scenes[2].findall('.//*[@data-ms-operation="shared-encoder"]')
        self.assertEqual(len(encoder), 1)
        self.assertEqual(encoder[0].attrib['data-modalities'], 'image text')
        fusions = self.scenes[2].findall('.//*[@data-ms-operation="late-fusion"]')
        self.assertEqual({x.attrib['data-client'] for x in fusions}, {'A', 'B'})
        for fusion in fusions:
            self.assertEqual(fusion.attrib['data-input'], 'encoded-modalities')
            self.assertEqual(fusion.attrib['data-modalities'], 'image text')

    def test_batch_weighted_loss_precedes_single_backward_and_local_update(self):
        objective = self.scenes[4].find('.//*[@data-ms-operation="weighted-loss"]')
        self.assertIsNotNone(objective)
        self.assertEqual(objective.attrib['data-weight'], 'client-batch-size/global-batch-size')
        self.assertEqual({x.attrib['data-ms-loss'] for x in objective.findall('.//*[@data-ms-loss]')}, {'A', 'B'})
        self.assertEqual(len(self.scenes[4].findall('.//*[@data-ms-operation="shared-backward"]')), 1)
        updates = self.scenes[5].findall('.//*[@data-ms-operation="tokenizer-update"]')
        self.assertEqual({x.attrib['data-client'] for x in updates}, {'A', 'B'})
        self.assertTrue(all(x.attrib['data-signal'] == 'cut-gradients' for x in updates))
        self.assertEqual(len(self.scenes[5].findall('.//*[@data-ms-operation="next-batch"]')), 1)

    def test_scenes_are_accessible_and_reveals_finish_before_transition(self):
        for step, scene in zip(STEPS, self.scenes):
            self.assertEqual(scene.tag, 'div')
            self.assertEqual(scene.attrib['role'], 'group')
            self.assertTrue(scene.attrib['aria-label'])
            self.assertTrue(step['title_in_art'])
            self.assertTrue(7000 <= step['duration_ms'] <= 12000)
            for part in scene.findall('.//*[@data-reveal]'):
                self.assertLess(int(part.attrib['data-reveal']), step['duration_ms'] - 1000)


if __name__ == '__main__':
    unittest.main()
