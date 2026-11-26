from pathlib import Path
from typing import Any

import pandas as pd


class PandasService:
    def __init__(self, spreadsheet_path: Path) -> None:
        self.spreadsheet_path = spreadsheet_path
        self.engine = self.choose_engine()

    def read_all_rows(self, number_of_rows: int | None = None) -> list[list[Any]]:
        data_frame = pd.read_excel(
            self.spreadsheet_path,
            engine=self.engine,
            nrows=number_of_rows,
        )
        return data_frame.to_numpy().tolist()

    def choose_engine(self) -> str:
        extension = self.spreadsheet_path.suffix.lower()

        engines = {
            ".xls": "xlrd",
            ".xlsx": "openpyxl",
            ".xlsm": "openpyxl",
            ".xlsb": "pyxlsb",
        }

        if extension not in engines:
            raise ValueError(f"Unsupported spreadsheet format: {extension}")

        return engines[extension]

    def read_columns(self) -> list[str]:
        data_frame = pd.read_excel(
            self.spreadsheet_path,
            engine=self.engine,
            nrows=0,
        )
        columns = data_frame.columns.to_list()

        if not columns:
            raise ValueError("The spreadsheet does not contain any columns.")

        return columns

    def read_first_rows(self) -> list[list[Any]]:
        data_frame = pd.read_excel(
            self.spreadsheet_path,
            engine=self.engine,
            nrows=10,
        )
        rows = data_frame.to_numpy().tolist()

        if not rows:
            raise ValueError(
                "No data could be read. Check the usage instructions and "
                "make sure the spreadsheet uses the required format."
            )

        return rows
