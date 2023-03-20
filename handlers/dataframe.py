import pandas as pd

from prompts.file import DATAFRAME_PROMPT

from .base import BaseHandler


class CsvToDataframe(BaseHandler):
    def handle(self, filename: str):
        df = pd.read_csv(filename)
        description = (
            f"Dataframe with {len(df)} rows and {len(df.columns)} columns."
            "Columns are: "
            f"{', '.join(df.columns)}"
        )

        print(
            f"\nProcessed CsvToDataframe, Input CSV: {filename}, Output Description: {description}"
        )

        return DATAFRAME_PROMPT.format(filename=filename, description=description)
