import unittest
import xml.etree.ElementTree as ET

from scripts.render_metrics import render_svg


class RenderMetricsTests(unittest.TestCase):
    def test_renders_valid_svg_and_public_metrics(self):
        svg = render_svg(
            {
                "repos": 12,
                "stars": 34,
                "languageCount": 3,
                "updated": "2026-11-18",
                "languages": [{"name": "Python", "count": 5}],
            }
        )

        root = ET.fromstring(svg)
        text = "".join(root.itertext())
        self.assertIn("12", text)
        self.assertIn("34", text)
        self.assertIn("Python", text)
        self.assertIn("2026-11-18", text)

    def test_escapes_language_text(self):
        svg = render_svg(
            {
                "repos": 0,
                "stars": 0,
                "languageCount": 1,
                "updated": "2026-11-18",
                "languages": [{"name": "A&B", "count": 1}],
            }
        )

        self.assertIn("A&amp;B", svg)
        ET.fromstring(svg)

    def test_rejects_negative_counts(self):
        with self.assertRaisesRegex(ValueError, "repos"):
            render_svg(
                {
                    "repos": -1,
                    "stars": 0,
                    "languageCount": 0,
                    "updated": "2026-11-18",
                    "languages": [],
                }
            )


if __name__ == "__main__":
    unittest.main()
