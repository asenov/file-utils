from unittest import TestCase

from file_utils import AsTable, AsJSON


class TestOutputHandlers(TestCase):
    def setUp(self) -> None:
        self.data = [("id", "dir location", "file name", "created")]

    def test_print(self):
        ret = AsTable.get_all(self.data)
        self.assertIsInstance(ret, str)
        self.assertIn("id", ret)
        self.assertIn("dir location", ret)
        self.assertIn("file name", ret)
        self.assertIn("created", ret)

    def test_json(self):
        ret = AsJSON.get_all(self.data)
        self.assertIsInstance(ret, str)
        self.assertIn("id", ret)
        self.assertIn("dir location", ret)
        self.assertIn("file name", ret)
        self.assertIn("created", ret)
