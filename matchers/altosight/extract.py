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

def size(s: pd.Series) -> float:
    sizeRaw = None
    if not pd.isna(s['size']):
        sizeRaw = s['size'].split(' ') # type: list[str]
        num = float(sizeRaw[0])
        unit = sizeRaw[1]
    else:
        sizeRaw = re.search(regexPattern.size, s['name']) # type: re.Match
        if sizeRaw:
            num = float(sizeRaw.group(1))
            unit = sizeRaw.group(2)
    if sizeRaw is not None:
        if unit == 'tb':
            num *= 1024
        return num
    return None
