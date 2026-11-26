from os import getenv
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd

load_dotenv(override=True)

class GroqWorking:
    @staticmethod
    def main():
        spreadsheet_path = (
            Path(__file__).resolve().parent.parent.parent
            / "Working_spreadsheet"
            / getenv("WORKING_SPREADSHEET_NAME")
        )
        try:
            df = pd.read_excel(spreadsheet_path)
        except Exception:
            df = pd.read_csv(spreadsheet_path, encoding='latin1')
        max_row = df.loc[df['salary'].idxmax()]
        print(max_row['name'], max_row['salary'])

if __name__ == "__main__":
    GroqWorking.main()