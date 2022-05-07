import os
import shutil
import sqlite3
import tempfile
import unittest
from unittest import mock

from file_utils.files import (
    delete_file_by_id,
    find_files,
    get_filepath,
    list_files,
    read_file_chunks,
    restore_file_by_id,
    store_files,
)


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


class TestFileOperations(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.mkdtemp()

        self.db_folder = f"{self.tmp_dir}/database"
        self.files_folder = f"{self.tmp_dir}/files"
        os.mkdir(self.db_folder)
        os.mkdir(self.files_folder)

        self.files = [
            f"{self.files_folder}/one.txt",
            f"{self.files_folder}/two.txt",
            f"{self.files_folder}/one.txt",
        ]
        create_file(self.files[0], "one")
        create_file(self.files[1], "two")

        self.db_path = f"{self.db_folder}/database.db"
        _ = store_files(self.db_path, self.files)

        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()

    def tearDown(self) -> None:
        if os.path.isdir(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        self.cur.close()
        self.conn.close()

    def test_store_files(self):
        self.assertTrue(os.path.isfile(self.db_path))

        ret = self.cur.execute("select * from files order by id asc").fetchall()
        self.assertEqual(len(ret), 2)

        self.assertEqual(len(ret[0]), 4)
        self.assertEqual(1, ret[0][0])
        self.assertEqual(self.files_folder, ret[0][1])
        self.assertEqual("one.txt", ret[0][2])

        self.assertEqual(2, ret[1][0])
        self.assertEqual(self.files_folder, ret[1][1])
        self.assertEqual("two.txt", ret[1][2])

    def test_store_files_chunks(self):
        ret = self.cur.execute(
            "select * from file_chunks order by file_id asc"
        ).fetchall()
        self.assertEqual(len(ret), 2)

        first_row = ret[0]
        self.assertEqual(len(first_row), 3)
        self.assertEqual(first_row[0], 1)
        self.assertEqual(first_row[1], 1)
        self.assertEqual(first_row[2], b"one")

        second_row = ret[1]
        self.assertEqual(second_row[0], 2)
        self.assertEqual(second_row[1], 1)
        self.assertEqual(second_row[2], b"two")

    def test_restore_file_by_id(self):
        restore_location = f"{self.tmp_dir}/restored_files"
        os.mkdir(restore_location)
        with self.assertRaisesRegex(FileNotFoundError, "DB file none does not exists"):
            _ = restore_file_by_id("none", 1, restore_location)
        with self.assertRaisesRegex(RuntimeError, "File id does not exists"):
            _ = restore_file_by_id(self.db_path, 10, restore_location)

        _ = restore_file_by_id(self.db_path, 1, restore_location)
        files = [f"{restore_location}/one.txt", f"{restore_location}/two.txt"]
        self.assertTrue(os.path.isfile(files[0]))
        self.assertFalse(os.path.isfile(files[1]))

        _ = restore_file_by_id(self.db_path, 2, restore_location)
        self.assertTrue(os.path.isfile(files[0]))
        self.assertTrue(os.path.isfile(files[1]))

        with open(files[0], "r") as reader:
            self.assertTrue(reader.read(), b"one")

        with open(files[1], "r") as reader:
            self.assertTrue(reader.read(), b"two")

    def test_list_files(self):
        result_handler = mock.Mock()
        with self.assertRaisesRegex(FileNotFoundError, "DB file none does not exists"):
            _ = list_files("none", result_handler)
        _ = list_files(self.db_path, result_handler)
        result_handler.get_all.assert_called_once()

    def test_find_files(self):
        result_handler = mock.Mock()
        with self.assertRaisesRegex(FileNotFoundError, "DB file none does not exists"):
            _ = find_files("none", "one", result_handler)
        _ = find_files(self.db_path, "one", result_handler)
        result_handler.get_all.assert_called_once()

    def test_delete_file(self):
        with self.assertRaisesRegex(FileNotFoundError, "DB file none does not exists"):
            _ = delete_file_by_id("none", 10)

        with self.assertRaisesRegex(RuntimeError, "Record 10 does not exist"):
            _ = delete_file_by_id(self.db_path, 10)
        _ = delete_file_by_id(self.db_path, 1)
        self.assertIsNone(
            self.cur.execute("select id from files where id = 1").fetchone()
        )
