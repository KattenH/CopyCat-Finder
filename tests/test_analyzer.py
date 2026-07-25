import os
import shutil
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from src.core.analyzer import ImageAnalyzer


class ImageAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="copycat-test-", dir=".")
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)

    def test_finds_duplicates_in_nested_folders(self):
        nested_dir = Path(self.temp_dir) / "nested"
        nested_dir.mkdir(parents=True, exist_ok=True)

        first = nested_dir / "first.png"
        second = nested_dir / "second.png"
        Image.new("RGB", (10, 10), color="red").save(first)
        Image.new("RGB", (10, 10), color="red").save(second)

        analyzer = ImageAnalyzer(model_name="clip-ViT-B-32")
        groups = analyzer.find_duplicates(self.temp_dir, threshold=0.99)

        self.assertTrue(groups)
        self.assertIn(str(first), groups[0])
        self.assertIn(str(second), groups[0])


if __name__ == "__main__":
    unittest.main()
