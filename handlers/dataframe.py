import pandas as pd
from prompts.file import DATAFRAME_PROMPT

from .base import BaseHandler


class CsvToDataframe(BaseHandler):
    def handle(self, filename: str):
        df = pd.read_csv(filename)
        description = str(df.describe())
        return DATAFRAME_PROMPT.format(filename=filename, description=description)
