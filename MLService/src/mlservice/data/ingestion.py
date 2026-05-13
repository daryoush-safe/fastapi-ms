from pathlib import Path

import pandas as pd


class DataIngestion:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def load(self) -> pd.DataFrame:
        suffix = self.file_path.suffix

        if suffix == ".csv":
            return pd.read_csv(self.file_path)

        if suffix in [".xlsx", ".xls"]:
            return pd.read_excel(self.file_path)

        raise ValueError(f"Unsupported file format: {suffix}")
