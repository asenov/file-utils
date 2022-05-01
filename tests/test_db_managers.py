import os.path
import shutil
import tempfile
from datetime import datetime
from unittest import TestCase

from file_utils.db_managers import SQLiteDBManager


class TestSQLiteManagers(TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.mkdtemp()

    def tearDown(self) -> None:
        if os.path.isdir(self.directory):
            shutil.rmtree(self.directory)

    def test_insert_row(self):
        with SQLiteDBManager(f"{self.directory}/data.db") as db_conn:
            table = "files"
            data = {
                "file_name": "random",
                "original_file_location": "path",
                "created_on": datetime.now(),
            }
            record_id = db_conn.insert_row(table, data)
            self.assertEqual(record_id, 1)

            record_id = db_conn.insert_row(table, data)
            self.assertIsNone(record_id, "File already exists")

    def test_query_row(self):
        with SQLiteDBManager(f"{self.directory}/data.db") as db_conn:
            table = "files"
            now = datetime.now()
            data = {
                "file_name": "random",
                "original_file_location": "path",
                "created_on": now,
            }
            record_id = db_conn.insert_row(table, data)
            query = "select * from files where id=?"
            params = (record_id,)

            ret = next(db_conn.query(query, params))
            self.assertIsInstance(ret, tuple)
            self.assertEqual(ret[0], 1)
            self.assertEqual(ret[1], data["original_file_location"])
            self.assertEqual(ret[2], data["file_name"])
            self.assertEqual(ret[3], str(now))

            query = "delete from files where id = ?"
            params = (record_id,)
            with self.assertRaisesRegex(ValueError, "Unsupported query operation"):
                _ = next(db_conn.query(query, params))

            query = "where id = ?"
            params = (record_id,)
            with self.assertRaisesRegex(
                ValueError, "Query does not contain select statement"
            ):
                _ = next(db_conn.query(query, params))
            # print(next(db_conn.query(query, params)))
