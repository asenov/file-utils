#!/usr/bin/env python3
import argparse
import sys

from file_utils import delete_file_by_id


def main(params):
    try:
        return delete_file_by_id(params.db, params.file_id)
    except (OSError, RuntimeError) as err:
        sys.stdout.write(f"Operation has failed (Reason: {err})\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove file from backup database by file id"
    )
    parser.add_argument("db", type=str, help="Local Database path")
    parser.add_argument(
        "file_id",
        type=int,
        help="File ID to delete",
    )
    args = parser.parse_args()
    main(args)
