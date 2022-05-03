#!/usr/bin/env python3
import argparse
import os

from file_utils import restore_file_by_id


def main(params):
    restore_file_by_id(
        params.db, params.file_id, os.path.abspath(params.destination)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore file from backup by file id")
    parser.add_argument("db", type=str, help="Local Database path")
    parser.add_argument(
        "file_id",
        type=int,
        help="File ID to restore from backup database to local directory",
    )
    parser.add_argument(
        "destination",
        type=str,
        help="Directory where to restore the target file",
    )
    args = parser.parse_args()
    main(args)
