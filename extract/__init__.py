import pandas as pd
import re
import warnings
from .brandRegex import brandRegex

def brand(s: pd.core.series.Series) -> str:
    for key, regex in brandRegex.items(): # type: str, re.Pattern
        if (not pd.isna(s['brand']) and regex.search(s['brand'])) or regex.search(s['title']):
            return key
    fallback = (s["title"] if pd.isna(s["brand"]) else s["brand"]).lower()
    warnings.warn(f'Unable to extract brand, fallback to "{fallback}".')
    return fallback