import json

from tabulate import tabulate


class AsTable:
    @staticmethod
    def get_all(data):
        return tabulate(
            data, headers=["Id", "original file path", "file name", "created on"]
        )


class AsJSON:
    @staticmethod
    def get_all(data):
        return json.dumps(
            [
                {"id": row[0], "file_path": f"{row[1]}/{row[2]}", "created": row[3]}
                for row in data
            ]
        )
