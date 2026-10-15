"""The walkthrough must preserve one coherent example across the FL round."""
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree as ET
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from paper_experience import load_story


class DeltaMaskStoryTests(unittest.TestCase):
    def test_round_connects_clients_to_server_and_preserves_bit_positions(self):
        story = load_story('deltamask')
        self.assertEqual(len(story['steps']), 6)
        scenes = [ET.fromstring(step['art']) for step in story['steps']]
        for scene in scenes:
            self.assertIsNotNone(scene.find('.//*[@data-dm-network]'))
            self.assertIn('Server', ''.join(scene.itertext()))
            self.assertIn('Client A', ''.join(scene.itertext()))
        rows = {}
        for scene in scenes:
            for row in scene.findall('.//*[@data-mask]'):
                key = row.attrib['data-mask']
                values = [int(x) for x in row.attrib['data-values'].split(',')]
                if key in rows:
                    self.assertEqual(values, rows[key], key)
                rows[key] = values
        reference, local, queries, recovered = [rows[k] for k in ['reference', 'local', 'queries', 'reconstructed']]
        self.assertEqual([i + 1 for i, (a, b) in enumerate(zip(reference, local)) if a != b], [2, 4, 5, 7])
        self.assertEqual([i + 1 for i, v in enumerate(queries) if v], [2, 5, 7])
        self.assertEqual(recovered, [a ^ b for a, b in zip(reference, queries)])
        self.assertEqual(recovered[3], reference[3], 'Omitted position4 must retain the reference bit')
        self.assertNotEqual(recovered[3], local[3])
        self.assertIn('false positives', story['steps'][4]['caption'].lower())
        self.assertGreater(story['steps'][4]['duration_ms'], 8000)


if __name__ == '__main__':
    unittest.main()
