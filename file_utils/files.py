"""
files management utils
"""
import glob
import logging
import os
from datetime import datetime

from .db_managers import SQLiteDBManager

_CHUNK_SIZE = 10485760

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)
_logger = logging.getLogger(__file__)


def read_file_chunks(file_path: str):
    """Reads a file by chunks of `_CHUNK_SIZE`

    Yields a part of a file if the file size is larger than the size of a single chunk
    """
    chunk = True
    with open(file_path, "rb") as fp_reader:
        while chunk:
            chunk = fp_reader.read(_CHUNK_SIZE)
            yield chunk


def get_filepath(path: str):
    """Provides the path to file(s) from `path`.

    Yields only file paths from `path`
        if `path` is a single file will be yeilded `path`
        if `path` is a directory will be yielded recursively only file paths stored in to `path`
    """
    if os.path.isfile(path):
        yield path
    if os.path.isdir(path):
        for item in glob.iglob(f"{path}/*", recursive=True):
            if os.path.isfile(item):
                yield item


def store_files(db_name, local_paths: list):
    with SQLiteDBManager(db_name) as db_conn:
        for path in local_paths:
            for item in get_filepath(path):
                file_name = os.path.basename(item)
                dir_path = os.path.dirname(item)
                _logger.info("Adding %s", item)
                file_id = db_conn.insert_row(
                    "files",
                    {
                        "file_name": file_name,
                        "original_file_location": dir_path,
                        "created_on": datetime.now(),
                    },
                )
                if not file_id:
                    continue
                for index, chunk in enumerate(
                    read_file_chunks(os.path.abspath(item)), start=1
                ):
                    if chunk:
                        db_conn.insert_row(
                            "file_chunks",
                            {"chunk_id": index, "chunk": chunk, "file_id": file_id},
                        )


def restore_file_by_id(db_name, file_id, dest_location):
    if not os.path.isfile(db_name):
        raise RuntimeError(f"DB file {db_name} does not exists")
    find_query = "select id, file_name from files where id = ? limit 1"
    chunks_query = (
        "select chunk from file_chunks where file_id = ? order by chunk_id ASC"
    )
    with SQLiteDBManager(db_name) as db_conn:
        try:
            ret = list(db_conn.query(find_query, (file_id,)))[0]
            file_name = ret[1]
        except IndexError as err:
            raise RuntimeError("File id does not exists") from err
        destination = f"{dest_location}/{file_name}"
        with open(destination, "wb") as fp_writer:
            for chunk in db_conn.query(chunks_query, (file_id,)):
                fp_writer.write(chunk[0])
        _logger.info("File has been restored %s", destination)


def list_files(db_name, callback):
    if not os.path.isfile(db_name):
        raise RuntimeError("DB file does not exists")
    with SQLiteDBManager(db_name) as db_conn:
        if hasattr(callback, "get_all"):
            getattr(callback, "get_all")(
                db_conn.query("select * from files order by file_name ASC")
            )


def find_files(db_name, file_name, callback):
    find_query = "select * from files where file_name LIKE ? "
    with SQLiteDBManager(db_name) as db_conn:
        if hasattr(callback, "get_all"):
            getattr(callback, "get_all")(db_conn.query(find_query, (f"{file_name}%",)))
