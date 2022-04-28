import logging
import os
import sqlite3

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)
_logger = logging.getLogger(__file__)


class SQLiteDBManager:
    def __init__(self, db_path: str) -> None:
        self._initialize_db = not os.path.isfile(db_path)
        self._conn = sqlite3.connect(db_path)
        self._cursor = self._conn.cursor()
        self._db_path = db_path

    def _setup_db(self) -> None:
        """Creates a new sqlite database if db file path is not a file"""
        if self._initialize_db:
            base_dir = os.path.abspath(os.path.dirname(__file__))
            with open(os.path.join(base_dir, "schema/db_schema.sql"), "r") as fp_schema:
                self._conn.executescript(fp_schema.read())
            self._conn.commit()

    def __enter__(self):
        self._setup_db()
        return self

    def __exit__(self, *exc_info):
        self._cursor.close()
        self._conn.close()

    def insert_row(self, table, args):
        """Insert rows in to specific table

        Args:
            table (str): DB table name
            args (dict): Values to insert

        Returns:
            lastrowid (int): on success otherwise None
        """
        stm_values = ("?," * len(args))[:-1]
        query = f"INSERT INTO {table} ({', '.join(args)}) VALUES({stm_values})"

        try:
            self._cursor.execute(query, tuple(args.values()))
            self._conn.commit()

            return self._cursor.lastrowid
        except sqlite3.IntegrityError:
            _logger.error("File already exists in database")

    def query(self, query: str, params: tuple = ()):
        """
        Args:
            query (str): Lookup query to database
            params (tuple): Must contain query statement parameters

        Yeilds:
            Result row from the database based on the query. Fields are positional

        Raises:
            ValueError when
               - query contain any of drop, delete or update
               - query parameter does not contain select statement
        """
        testing_query = query.lower()
        for term in ("drop", "delete", "update"):
            if term in testing_query:
                raise ValueError("Unsupported query operation")
        if "select" not in testing_query:
            raise ValueError("Query does not contain select statement")

        self._cursor.execute(query, params)

        for item in self._cursor.fetchall():
            yield item
