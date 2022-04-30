import json

from tabulate import tabulate


class PrintFiles:
    @staticmethod
    def get_all(data):
        print(
            tabulate(
                data, headers=["Id", "original file path", "file name", "created on"]
            )
        )


class PrintJson:
    @staticmethod
    def get_all(data):
        print(
            json.dumps(
                [
                    {"id": row[0], "file_path": f"{row[1]}/{row[2]}", "created": row[3]}
                    for row in data
                ]
            )
        )
