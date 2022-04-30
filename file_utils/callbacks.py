import json

from tabulate import tabulate


class PrintFiles:
    def get_all(self, data):
        print(
            tabulate(
                data, headers=["Id", "original file path", "file name", "created on"]
            )
        )


class PrintJson:
    def get_all(self, data):
        print(
            json.dumps(
                [
                    {"id": row[0], "file_path": f"{row[1]}/{row[2]}", "created": row[3]}
                    for row in data
                ]
            )
        )
