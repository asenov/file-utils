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
    chunk = True
    with open(file_path, "rb") as fp_txt:
        while chunk:
            chunk = fp_txt.read(_CHUNK_SIZE)
            yield chunk


def store_file(db_name, file_path):
    file_name = os.path.basename(file_path)
    dir_path = os.path.dirname(file_path)
    with SQLiteDBManager(db_name) as db:
        file_id = db.insert_row(
            "files",
            {
                "file_name": file_name,
                "original_file_location": dir_path,
                "created_on": datetime.now(),
            },
        )
        if not file_id:
            return
        for index, chunk in enumerate(read_file_chunks(file_path), start=1):
            if chunk:
                db.insert_row(
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
    with SQLiteDBManager(db_name) as db:
        try:
            ret = list(db.query(find_query, (file_id,)))[0]
            file_name = ret[1]
        except IndexError:
            raise RuntimeError("File id does not exists")
        destination = f"{dest_location}/{file_name}"
        with open(destination, "wb") as fp_w:
            for chunk in db.query(chunks_query, (file_id,)):
                fp_w.write(chunk[0])
        _logger.info(f"File has been restored {destination}")


def list_files(db_name, callback):
    if not os.path.isfile(db_name):
        raise RuntimeError("DB file does not exists")
    with SQLiteDBManager(db_name) as db:
        if hasattr(callback, "get_all"):
            getattr(callback, "get_all")(
                db.query("select * from files order by file_name ASC")
            )


def find_files(db_name, file_name, callback):
    find_query = "select * from files where file_name LIKE ? "
    with SQLiteDBManager(db_name) as db:
        if hasattr(callback, "get_all"):
            getattr(callback, "get_all")(db.query(find_query, (f"{file_name}%",)))
