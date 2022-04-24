from tabulate import tabulate


class PrintFilesCallback:
    def get_all(self, data):
        print(
            tabulate(
                data, headers=["Id", "original file path", "file name", "created on"]
            )
        )
