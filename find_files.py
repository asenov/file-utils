#!/usr/bin/env python3
import argparse
import sys

from file_utils import AsTable, AsJSON, Generic, find_files


def main(params):
    output_type = {"json": AsJSON, "print": AsTable, "generic": Generic}

    return find_files(params.db, params.file_name, output_type[params.output]())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search by file name in a local database"
    )
    parser.add_argument("db", type=str, help="Local Database path")
    parser.add_argument(
        "file_name",
        type=str,
        help="Full file name or file prefix. Insensitive to capital letters",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="print",
        choices=["json", "print", "generic"],
        help="Output mode",
    )
    args = parser.parse_args()

    sys.stdout.write(main(args))
    sys.stdout.flush()
