from pathlib import Path


class AvailableDefaultTools:
    @staticmethod
    def write_code_to_file(code: str, code_path: Path) -> int:
        return code_path.write_text(code, encoding="utf-8")
