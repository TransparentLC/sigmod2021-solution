import pandas as pd
import re
import typing
import warnings
from . import regexPattern

def type(s: pd.Series) -> str:
    name = s['name'] # type: str
    for k, r in regexPattern.type.items(): # type: str, re.Pattern
        if re.search(r, name):
            return k
    warnings.warn(f'Unable to extract type for "{name}".')
    return 'other'

def size(s: pd.Series) -> int:
    if not pd.isna(s['size']):
        splitted = s['size'].split(' ') # type: list[str]
        num = int(splitted[0])
        unit = splitted[1]
        if unit == 'tb':
            num *= 1024
        return int(num)
    return None
