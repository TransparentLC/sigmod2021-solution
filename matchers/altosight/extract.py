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
    match = re.search(regexPattern.size, s['name'])
    matchSize = None
    if match:
        matchSize = float(match.group(1))
        matchUnit = match.group(2)
    elif not pd.isna(s['size']):
        match = s['size'].split(' ') # type: list[str]
        matchSize = float(match[0])
        matchUnit = match[1]
    if matchSize is not None:
        if matchUnit == 'tb':
            matchSize *= 1024
        return matchSize

def sizeLoose(s: pd.Series) -> str:
    res = set()

    for c in ('size', 'name'):
        if pd.isna(s[c]):
            continue
        matches = re.findall(regexPattern.size, s[c]) # type: list[tuple[str]]
        for matchSize, matchUnit in matches:
            matchSize = int(matchSize)
            if matchUnit == 'tb':
                matchSize *= 1024
            res.add(int(matchSize))

    return ' '.join(str(x) for x in res) if res else None

def sdcardStandard(s: pd.Series) -> typing.Optional[str]:
    if s['x_type'] != 'sdcard':
        return None
    if (
        'sd xc' in s['name'] or
        'sdxc' in s['name']
    ):
        return 'sdxc'
    if (
        'high capacity' in s['name'] or
        'high-capacity' in s['name'] or
        'sd hc' in s['name'] or
        'sdhc' in s['name']
    ):
        return 'sdhc'
    return None

def sdcardIsMicro(s: pd.Series) -> typing.Optional[bool]:
    if s['x_type'] != 'sdcard':
        return None
    return 'micro' in s['name']

def usbStandard(s: pd.Series) -> typing.Optional[str]:
    if s['x_type'] != 'usbstick':
        return None
    for v in (
        '3.1',
        '3.0',
        '2.0',
    ):
        if v in s['name']:
            return v
    return None

def color(s: pd.Series) -> typing.Optional[str]:
    if s['x_type'] != 'phone':
        return None
    for c in (
        'black',
        'white',
        'red',
        'blue',
        'green',
        'gold',
        'silver',
    ):
        if c in s['name']:
            return c

def tvSize(s: pd.Series) -> typing.Optional[float]:
    if s['x_type'] != 'tv':
        return None
    match = re.search(regexPattern.tvSize, s['name'])
    if match is not None:
        m = match.group(1)  # type: typing.Optional[str]
        return round(float(m))
    return None

def model(s: pd.Series) -> typing.Optional[str]:
    match = None
    if s['brand'] == 'toshiba' and s['x_type'] in ('usbstick', 'sdcard'):
        match = re.search(r'[mnu]\d0\d', s['name'])
    elif s['brand'] == 'lexar' and s['x_type'] in ('usbstick',):
        match = re.search(r'[cpsv]\d[05][cm]?', s['name'])
    elif s['brand'] == 'samsung' and s['x_type'] in ('phone',):
        match = re.search(r'\bgalaxy (?:[a-z]\d{1,2}|note ?\d{1,2})\b', s['name'])
    elif s['brand'] == 'sony':
        if s['x_type'] == 'sdcard':
            match = re.search(
                r'\b(?:sf-?(?:\d{1,3}n4|[gm]\d{1,3}t|[em]\d{1,3})|sr-?\d{1,3}(?:ux2[ab]|uy[23]?a|[hu]xa|a[41](?: ?[pv])?)|sf-?(?:\d{1,3}(?:[un][41]|nx|ux(?:2b?)?|uy[23]?|b[f4])|g\d{1,3})|sn-?(?:bb\d{1,3}|ba\d{1,3} ?f?))\b',
                s['name']
            )
        elif s['x_type'] == 'usbstick':
            match = re.search(
                r'\busm-?\d{1,3}(?:g(?:u|t|r|qx)|w3|ca1|x|sa1|m)\b',
                s['name']
            )
        if match:
            return match.group(0).replace(' ', '').replace('-', '')
    if match:
        return match.group(0).replace(' ', '')
    return None
