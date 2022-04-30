import os
import shutil
import tempfile
import unittest

from file_utils.files import get_filepath, read_file_chunks


def create_file(path, contents="empty"):
    with open(f"{path}", "w") as w:
        w.write(contents)


class TestGetFilePath(unittest.TestCase):
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

    def test_empty_dir(self):
        with tempfile.TemporaryDirectory(prefix="file_utils") as t_dir:
            with tempfile.TemporaryDirectory():
                with self.assertRaises(StopIteration):
                    _ = next(get_filepath(t_dir))


class TestFileChunks(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        if os.path.isdir(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_content(self):
        file_path = f"{self.tmp_dir}/test.txt"
        create_file(file_path, "here")

        ret = next(read_file_chunks(file_path))
        self.assertEqual(ret, b"here")
