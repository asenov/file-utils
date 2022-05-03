#!/usr/bin/env python3
import argparse

from file_utils import AsTable, AsJSON, list_files


def main(params):
    output_type = {"json": AsJSON, "print": AsTable}

    print(list_files(params.db, output_type[params.output]()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List of files in a local database")
    parser.add_argument("db", type=str, help="Local Database path")
    parser.add_argument(
        "-o", "--output", default="print", choices=["json", "print"], help="Output mode"
    )
    args = parser.parse_args()

    main(args)
