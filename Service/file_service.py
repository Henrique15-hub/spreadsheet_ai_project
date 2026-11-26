from pathlib import Path


class FileService:
    def __init__(self, spreadsheet_path: Path) -> None:
        self.spreadsheet_path = spreadsheet_path

    def verify_spreadsheet_exists(self) -> bool:
        return self.spreadsheet_path.exists() and self.spreadsheet_path.is_file()
