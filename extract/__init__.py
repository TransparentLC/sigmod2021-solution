import pandas as pd
import re
from .brandRegex import brandRegex

def brand(s: pd.core.series.Series) -> str:
    data = s['title'] if pd.isna(s['brand']) else s['brand'] # type: str
    for key, regex in brandRegex.items():
        key # type: str
        regex # type: re.Pattern
        if (not pd.isna(s['brand']) and regex.search(s['brand'])) or regex.search(s['title']):
            return key
    raise Exception(f'Failed to extract brand: {data}')