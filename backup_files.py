#!/usr/bin/env python3
import argparse


from file_utils import store_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup files in to database")
    parser.add_argument("db", type=str, help="Local Database path")
    parser.add_argument(
        "files",
        type=str,
        help="Local file or directory path for backup",
        nargs=argparse.REMAINDER,
    )
    args = parser.parse_args()

    store_files(args.db, args.files)
