from unittest import TestCase

from file_utils import AsJSON, AsTable


class TestOutputHandlers(TestCase):
    def setUp(self) -> None:
        self.data = [("id", "dir location", "file name", "file size", "created")]

    def test_print(self):
        ret = AsTable.get_all(self.data)
        self.assertIsInstance(ret, str)
        self.assertIn("id", ret)
        self.assertIn("dir location", ret)
        self.assertIn("file name", ret)
        self.assertIn("file size", ret)
        self.assertIn("created", ret)

    def test_json(self):
        ret = AsJSON.get_all(self.data)
        self.assertIsInstance(ret, str)
        self.assertIn("id", ret)
        self.assertIn("dir location", ret)
        self.assertIn("file name", ret)
        self.assertIn("file_size", ret)
        self.assertIn("created", ret)
