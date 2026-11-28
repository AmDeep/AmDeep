from __future__ import annotations

import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_profile import (  # noqa: E402
    esc,
    load_content,
    render_all,
    validate_content,
)


class ProfileBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.content = load_content(ROOT / "profile-content.json")
        cls.outputs = render_all(cls.content)

    def test_profile_content_has_unique_project_ids_and_links(self) -> None:
        validate_content(self.content)
        self.assertEqual(len(self.content["projects"]), 6)
        self.assertEqual(
            len({project["id"] for project in self.content["projects"]}),
            len(self.content["projects"]),
        )

    def test_each_svg_is_well_formed_and_accessible(self) -> None:
        svg_outputs = {
            name: value for name, value in self.outputs.items() if name.endswith(".svg")
        }
        self.assertGreaterEqual(len(svg_outputs), 8)
        for name, text in svg_outputs.items():
            with self.subTest(asset=name):
                root = ET.fromstring(text)
                self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
                self.assertEqual(root.attrib.get("role"), "img")
                self.assertIn("aria-labelledby", root.attrib)
                self.assertIsNotNone(root.find("{http://www.w3.org/2000/svg}title"))
                self.assertIsNotNone(root.find("{http://www.w3.org/2000/svg}desc"))
        metrics_path = ROOT / "profile" / "metrics.svg"
        self.assertTrue(metrics_path.is_file())
        metrics_root = ET.parse(metrics_path).getroot()
        self.assertEqual(metrics_root.attrib.get("role"), "img")

    def test_readme_has_no_empty_states_or_third_party_stats_widgets(self) -> None:
        readme = self.outputs["README.md"].lower()
        forbidden = (
            "waiting for the first data refresh",
            "github-readme-stats",
            "streak-stats",
            "github-readme-activity-graph",
            "komarev",
            "github-snake",
            "skillicons.dev",
            "profile views",
        )
        for text in forbidden:
            with self.subTest(text=text):
                self.assertNotIn(text, readme)

    def test_all_readme_svg_references_are_generated(self) -> None:
        readme = self.outputs["README.md"]
        referenced = re.findall(
            r"https://raw\.githubusercontent\.com/AmDeep/AmDeep/main/profile/([^\" ]+\.svg)",
            readme,
        )
        self.assertGreaterEqual(len(referenced), 8)
        for filename in referenced:
            with self.subTest(asset=filename):
                self.assertTrue(
                    f"profile/{filename}" in self.outputs
                    or (ROOT / "profile" / filename).is_file()
                )

    def test_all_projects_are_linked_from_readme(self) -> None:
        readme = self.outputs["README.md"]
        for project in self.content["projects"]:
            with self.subTest(project=project["repo"]):
                self.assertIn(project["url"], readme)
                self.assertIn(f"profile/project-{project['id']}.svg", self.outputs)

    def test_reduced_motion_is_supported_in_every_svg(self) -> None:
        for name, text in self.outputs.items():
            if name.endswith(".svg"):
                with self.subTest(asset=name):
                    self.assertIn("prefers-reduced-motion: reduce", text)

    def test_text_escaping_prevents_malformed_svg(self) -> None:
        self.assertEqual(esc("R&D <AI>"), "R&amp;D &lt;AI&gt;")
        altered = dict(self.content)
        altered["name"] = "R&D <AI>"
        outputs = render_all(altered)
        ET.fromstring(outputs["profile/hero.svg"])
        self.assertIn("R&amp;D &lt;AI&gt;", outputs["profile/hero.svg"])

    def test_project_counts_are_qualified_as_scope_not_impact(self) -> None:
        evidence = self.outputs["profile/evidence.svg"]
        self.assertIn("PROJECT SCOPE, NOT VANITY METRICS", evidence)
        self.assertIn("not deployment volume or user impact", evidence)


if __name__ == "__main__":
    unittest.main()
