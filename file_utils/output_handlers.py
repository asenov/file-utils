import json

from tabulate import tabulate

# pylint: disable=too-few-public-methods


class AsTable:
    @staticmethod
    def get_all(data):
        return tabulate(
            data,
            headers=[
                "Id",
                "original file path",
                "file name",
                "created on",
                "file size (MB)",
            ],
        )


class AsJSON:
    @staticmethod
    def get_all(data):  # pylint: disable=R0903
        return json.dumps(
            [
                {
                    "id": row[0],
                    "file_path": f"{row[1]}/{row[2]}",
                    "created": row[3],
                    "file_size_mb": row[4],
                }
                for row in data
            ]
        )


class Generic:
    @staticmethod
    def get_all(data):
        for row in data:
            print(f"{row[0]} {row[4]} {row[3]} {row[1]}/{row[2]}")
        return ""
