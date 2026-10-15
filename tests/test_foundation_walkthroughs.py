"""Source-critical boundaries for AE-PSL and MaTU's connected walkthroughs."""
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
try:
    from stories import foundation_walkthroughs as walkthroughs
except ImportError:
    walkthroughs = None


class FoundationWalkthroughTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(walkthroughs, 'Connected foundation walkthroughs must exist')
        self.ae = [ET.fromstring(s['art']) for s in walkthroughs.AE_STEPS]
        self.matu = [ET.fromstring(s['art']) for s in walkthroughs.MATU_STEPS]

    def test_alignment_trains_both_ae_halves_with_frozen_feature_extraction(self):
        for index in (0, 1):
            models = self.ae[index].findall('.//*[@data-fw-module]')
            for kind, trainable in [('feature-extractor', 'false'), ('encoder', 'true'), ('decoder', 'true')]:
                matching = [m for m in models if m.attrib['data-fw-module'] == kind]
                self.assertTrue(matching, kind)
                self.assertTrue(all(m.attrib['data-fw-trainable'] == trainable for m in matching))
            self.assertTrue(self.ae[index].findall('.//*[@data-fw-operation="reconstruction-loss"]'))
        self.assertEqual({n.attrib['data-fw-location'] for n in self.ae[1].findall('.//*[@data-fw-operation="reconstruction-loss"]')}, {'client-1', 'client-2'})

    def test_only_decoder_weights_are_averaged_after_client_alignment(self):
        sends = self.ae[2].findall('.//*[@data-fw-message]')
        self.assertEqual([x.attrib['data-fw-message'] for x in sends], ['decoder-weights', 'decoder-weights'])
        self.assertEqual({x.attrib['data-from'] for x in sends}, {'client-1', 'client-2'})
        self.assertTrue(all(x.attrib['data-to'] == 'server' for x in sends))
        self.assertEqual(len(self.ae[2].findall('.//*[@data-fw-operation="decoder-mean"]')), 1)
        self.assertEqual(len(self.ae[2].findall('.//*[@data-fw-retained="local-encoder"]')), 2)

    def test_fine_tuning_preserves_cls_bypass_and_server_prediction(self):
        packet = self.ae[3].find('.//*[@data-fw-message="activations"]')
        self.assertEqual(packet.attrib['data-from'], 'client')
        self.assertEqual(packet.attrib['data-to'], 'server')
        self.assertEqual(packet.find('.//*[@data-fw-channel="patch-latents"]').attrib['data-compressed'], 'true')
        self.assertEqual(packet.find('.//*[@data-fw-channel="cls"]').attrib['data-compressed'], 'false')
        self.assertEqual(len(self.ae[3].findall('.//*[@data-fw-operation="server-predict"]')), 1)
        for codec in self.ae[3].findall('.//*[@data-fw-module]'):
            if codec.attrib['data-fw-module'] in ('encoder', 'decoder'):
                self.assertEqual(codec.attrib['data-fw-trainable'], 'false')

    def test_loss_is_summed_and_both_cut_gradients_return(self):
        self.assertEqual(self.ae[4].find('.//*[@data-fw-loss-reduction]').attrib['data-fw-loss-reduction'], 'sum')
        self.assertEqual(len(self.ae[4].findall('.//*[@data-fw-operation="server-backward"]')), 1)
        channels = self.ae[4].findall('.//*[@data-fw-message="gradients"]')
        self.assertEqual({x.attrib['data-channel'] for x in channels}, {'patch-latents', 'cls'})
        self.assertTrue(all(x.attrib['data-from'] == 'server' and x.attrib['data-to'] == 'client' for x in channels))
        self.assertEqual(self.ae[5].find('.//*[@data-fw-module="encoder"]').attrib['data-fw-trainable'], 'false')
        self.assertEqual(self.ae[5].find('.//*[@data-fw-operation="client-update"]').attrib['data-trainable'], 'LoRA')

    def test_sign_election_uses_sum_and_maximum_aligned_magnitude(self):
        self.assertEqual(walkthroughs.unify_task_vectors([[5, -4], [-3, 1], [-3, 1]]), [-3, -4])
        self.assertEqual(walkthroughs.unify_task_vectors([[2, -1, 4, 1], [1, -3, -2, 2]]), [2, -3, 4, 2])
        self.assertEqual(walkthroughs.unify_task_vectors([[1, -2], [-1, 2]]), [0, 0])

    def test_masks_and_scalars_match_the_original_absolute_magnitude(self):
        mask, scale = walkthroughs.task_modulator([1, -3, -2, 2], [2, -3, 4, 2])
        self.assertEqual(mask, [1, 1, 0, 1])
        self.assertAlmostEqual(scale, 8 / 7)
        recovered = [scale * m * u for m, u in zip(mask, [2, -3, 4, 2])]
        self.assertAlmostEqual(sum(abs(v) for v in recovered), 8)
        self.assertNotEqual(recovered, [1, -3, -2, 2], 'Modulation is approximate, not exact recovery')

    def test_similarity_filters_conflicts_before_related_task_transfer(self):
        self.assertEqual(walkthroughs.sign_similarity([1, -1, 1, 1], [1, -1, -1, 1]), .75)
        self.assertEqual(walkthroughs.sign_similarity([1, -1, 1, 1], [-1, 1, 1, -1]), .25)
        self.assertEqual(walkthroughs.sign_similarity([1, -1, 0, 1], [1, -1, 0, 1]), .875)
        self.assertEqual(walkthroughs.sign_similarity([1, -1, 0, 1], [0, 0, 0, -1]), .375)
        related = self.matu[4].findall('.//*[@data-fw-similarity]')
        self.assertEqual([float(x.attrib['data-fw-similarity']) for x in related], [.875, .375])
        self.assertTrue(any(float(x.attrib['data-fw-similarity']) > .5 and x.attrib['data-selected'] == 'true' for x in related))
        self.assertTrue(all(float(x.attrib['data-fw-similarity']) > .5 for x in related if x.attrib['data-selected'] == 'true'))
        self.assertEqual(self.matu[5].find('.//*[@data-fw-operation="reunify"]').attrib['data-before'], 'client-return')
        self.assertEqual(len(self.matu[5].findall('.//*[@data-fw-operation="recover-task"]')), 2)

    def test_suppressed_coordinate_survives_similarity_and_recovery(self):
        def values(scene, key):
            row = scene.find(f'.//*[@data-fw-vector="{key}"]')
            self.assertIsNotNone(row, key)
            return [int(x) for x in row.attrib['data-values'].split(',')]

        participants = [values(self.matu[3], f'client-{i}-task-A') for i in (1, 2)]
        self.assertEqual([row[2] for row in participants], [1, -1])
        aggregate = values(self.matu[3], 'server-task-A')
        self.assertEqual(aggregate, [1, -1, 0, 1])
        self.assertEqual(values(self.matu[4], 'server-task-A'), aggregate)
        self.assertEqual(values(self.matu[4], 'server-task-B')[2], 0, 'The uploaded B mask already removed coordinate 3')
        self.assertEqual(values(self.matu[5], 'next-unified'), aggregate)
        for task in ('A', 'B'):
            self.assertEqual(values(self.matu[5], f'recovered-{task}')[2], 0)

    def test_art_contract_and_timing(self):
        for steps in (walkthroughs.AE_STEPS, walkthroughs.MATU_STEPS):
            self.assertTrue(4 <= len(steps) <= 6)
            for step in steps:
                scene = ET.fromstring(step['art'])
                self.assertEqual(scene.tag, 'div')
                self.assertEqual(scene.attrib['role'], 'group')
                self.assertTrue(scene.attrib['aria-label'])
                self.assertIsNotNone(scene.find('.//*[@data-fw-network]'))
                self.assertLessEqual(len(step['caption'].split()), 16)
                self.assertTrue(step['title_in_art'])
                self.assertTrue(7000 <= step['duration_ms'] <= 12000)
                for part in scene.findall('.//*[@data-reveal]'):
                    self.assertLess(int(part.attrib['data-reveal']), step['duration_ms'] - 1000)


if __name__ == '__main__':
    unittest.main()
