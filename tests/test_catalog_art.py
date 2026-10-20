"""Check the inline thumbnail contract at the public-catalog boundary."""

from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from catalog_art import thumbnail


class CatalogArtTests(unittest.TestCase):
    def test_every_public_paper_has_distinct_inline_art(self):
        slugs = [path.stem for path in (ROOT / "data/projects").glob("*.json")]
        scenes = [thumbnail(slug) for slug in slugs]
        self.assertEqual(len(scenes), 15)
        self.assertEqual(len(set(scenes)), len(scenes))
        for slug, markup in zip(slugs, scenes):
            with self.subTest(slug=slug):
                svg = ElementTree.fromstring(markup)
                self.assertEqual(svg.attrib["viewBox"], "0 0 400 180")
                self.assertEqual(svg.attrib["class"], "catalog-art")
                self.assertEqual(svg.attrib["aria-hidden"], "true")
                self.assertEqual(svg.attrib["focusable"], "false")
                for node in svg.iter():
                    self.assertNotIn("id", node.attrib)
                    self.assertNotIn("href", node.attrib)
                    self.assertNotIn(node.tag.split("}")[-1],
                                     {"image", "use", "script", "foreignObject", "animate", "defs"})

    def test_art_uses_theme_tokens_and_readable_labels(self):
        allowed_paints = {"none", "currentColor"} | {
            f"var(--tile-{tone})" for tone in
            ("accent", "secondary", "muted", "line", "surface", "soft")}
        for path in (ROOT / "data/projects").glob("*.json"):
            with self.subTest(slug=path.stem):
                svg = ElementTree.fromstring(thumbnail(path.stem))
                labels = []
                for node in svg.iter():
                    for paint in ("fill", "stroke"):
                        if paint in node.attrib:
                            self.assertIn(node.attrib[paint], allowed_paints)
                    if node.tag.endswith("}text"):
                        labels.append(node)
                        self.assertGreaterEqual(float(node.attrib["font-size"]), 18)
                        self.assertLessEqual(len(node.text), 14)
                self.assertLessEqual(len(labels), 3)
                self.assertGreaterEqual(len(labels), 2)
                self.assertIn('class="ca-pulse"', thumbnail(path.stem))

    def test_unknown_slug_fails_without_markup_injection(self):
        for value in ("missing-paper", "<script>", None):
            with self.assertRaises(ValueError):
                thumbnail(value)


if __name__ == "__main__":
    unittest.main()
