from os import getenv
from pathlib import Path

from dotenv import load_dotenv

from Integrations.Groq.Service.groq_service import GroqService
from Integrations.Pandas.Service.pandas_service import PandasService
from Service.file_service import FileService


def main() -> None:
    load_dotenv()

    spreadsheet_name = getenv("WORKING_SPREADSHEET_NAME")
    if not spreadsheet_name:
        raise ValueError("WORKING_SPREADSHEET_NAME has not been configured.")

    spreadsheet_path = (
        Path(__file__).resolve().parent/ "Working_spreadsheet"/ spreadsheet_name
    )

    file_service = FileService(spreadsheet_path)
    if not file_service.verify_spreadsheet_exists():
        print("Spreadsheet not found.")
        return

    pandas_service = PandasService(spreadsheet_path)
    spreadsheet_columns = pandas_service.read_columns()

    groq_service = GroqService(
        spreadsheet_columns=spreadsheet_columns,
        spreadsheet_path=spreadsheet_path,
    )

    print("Assistant started. Type 'close' to exit.")
    print("What would you like to know about the spreadsheet?")

    while True:
        user_input = input("\n>>> ").strip()

        if user_input.lower() == "close":
            break

        if not user_input:
            continue

        try:
            response = groq_service.do_call(user_input)
            print(response)
        except Exception as exception:
            print(f"Error: {exception}")


if __name__ == "__main__":
    main()
