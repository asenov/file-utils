import tempfile
import unittest

from file_utils.files import get_filepath


def create_file(path):
    with open(f"{path}", "w") as w:
        w.write("content")


class TestGetFilePath(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_file_path(self):
        with tempfile.NamedTemporaryFile() as tmpfile:
            ret = next(get_filepath(tmpfile.name))
            self.assertEqual(ret, tmpfile.name)

    def test_dir_content(self):
        with tempfile.TemporaryDirectory(prefix="file_utils") as t_dir:
            create_file(f"{t_dir}/one.txt")
            with tempfile.TemporaryDirectory() as subt_dir:
                for item in get_filepath(f"{t_dir}"):
                    self.assertTrue(item, f"{t_dir}/one.txt")
                    self.assertNotIn(item, subt_dir)
