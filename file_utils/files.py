"""
files management utils
"""
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
        yield os.path.dirname(path), os.path.basename(path)
    if os.path.isdir(path):
        for root, _, files in os.walk(path, topdown=True):
            for fname in files:
                # handle broken links
                if not os.path.isfile(os.path.join(root, fname)):
                    continue
                yield root, fname


def store_files(db_name, local_paths: list):
    with SQLiteDBManager(db_name) as db_conn:
        for path in local_paths:
            for dir_path, file_name in get_filepath(path):
                _logger.info("Adding %s %s", dir_path, file_name)
                file_id = db_conn.insert_row(
                    "files",
                    {
                        "file_name": file_name,
                        "original_file_location": dir_path,
                        "created_on": datetime.now(),
                    },
                )
                #if not file_id:
                #    continue
                for index, chunk in enumerate(
                    read_file_chunks(os.path.join(dir_path, file_name)), start=1
                ):
                    if chunk:
                        db_conn.insert_row(
                            "file_chunks",
                            {"chunk_id": index, "chunk": chunk, "file_id": file_id},
                        )


def restore_file_by_id(db_name, file_id, dest_location):
    if not os.path.isfile(db_name):
        raise FileNotFoundError(f"DB file {db_name} does not exists")
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


def list_files(db_name, callback):  # pylint: disable=R1710
    if not os.path.isfile(db_name):
        raise FileNotFoundError(f"DB file {db_name} does not exists")
    with SQLiteDBManager(db_name) as db_conn:
        if hasattr(callback, "get_all"):
            return getattr(callback, "get_all")(
                db_conn.query("select * from v_files order by file_name ASC")
            )


def find_files(db_name, file_name, callback):  # pylint: disable=R1710
    if not os.path.isfile(db_name):
        raise FileNotFoundError(f"DB file {db_name} does not exists")
    find_query = "select * from v_files where file_name LIKE ? "
    params = (file_name.replace("*", "%") if "*" in file_name else f"{file_name}%",)
    with SQLiteDBManager(db_name) as db_conn:
        if hasattr(callback, "get_all"):
            return getattr(callback, "get_all")(db_conn.query(find_query, params))


def delete_file_by_id(db_name, file_id: int):
    """Removes file record from sqlite database

    Args:
        db_name (str): Path to sqldatabse
        file_id (int): File record id

    Raises:
        FileNotFoundError: When db files does not exists
        RuntimeError: When record id does not exists
    """
    if not os.path.isfile(db_name):
        err_msg = f"DB file {db_name} does not exists"
        _logger.error(err_msg)
        raise FileNotFoundError(err_msg)
    with SQLiteDBManager(db_name) as db_conn:
        try:
            _ = next(db_conn.query("select id from files where id = ? ", (file_id,)))
        except StopIteration as err:
            err_msg = f"Record {file_id} does not exist"
            _logger.error(err_msg)
            raise RuntimeError(err_msg) from err
        db_conn.delete_file_record(file_id)
        _logger.info("File %s has been deleted", file_id)
