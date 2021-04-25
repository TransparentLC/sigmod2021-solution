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
    # 我没有说要钦定，没有任何这个意思
    # 产品的类型，还是要按照基本法、选举法，去产生
    # forcedlySetTypes = {
    #     'altosight.com//1513': 'usbstick',
    #     'altosight.com//3476': 'usbstick',
    #     'altosight.com//10745': 'usbstick',
    # }
    # if s['instance_id'] in forcedlySetTypes.keys():
    #     return forcedlySetTypes[s['instance_id']]
    if s['brand'] == 'pny' and ('attaché' in s['name'] or 'attache' in s['name']):
        return 'usbstick'
    elif s['brand'] == 'sandisk' and 'extreme' in s['name']:
        return 'usbstick'
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

def sdcardUhsLevel(s: pd.Series) -> typing.Optional[int]:
    if s['x_type'] != 'sdcard':
        return None
    match = re.search(r'(?:uhs[- ]?)([123]|i{1,3})\b', s['name'])
    if match:
        return int(match.group(1)) if match.group(1).isdigit() else len(match.group(1))


def sdcardAdapterSize(s: pd.Series) -> typing.Optional[str]:
    if s['x_type'] != 'sdcard':
        return None
    match = re.search(r'\bsd adapter (\d+) ?gb\b', s['name'])
    if match:
        return int(match.group(1))

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
    colorAliases = {
        'blanc': 'white',
        'blanco': 'white',
        'bianco': 'white',
        'plata': 'silver',
        'plateado': 'silver',
        'argento': 'silver',
    }
    if (
        s['x_type'] == 'phone' or
        s['x_type'] == 'usbstick' and s['brand'] == 'toshiba'
    ):
        for c in (
            'black',
            'white',
            'red',
            'blue',
            'green',
            'gold',
            'silver',
            *colorAliases.keys()
        ):
            if re.search(r'(?:\b|^)' + c + r'(?:\b|$)', s['name']):
                if c in colorAliases.keys():
                    return colorAliases[c]
                return c
    return None

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
    elif s['brand'] == 'lexar' and s['x_type'] == 'usbstick':
        match = re.search(r'[cpsv]\d[05][cm]?', s['name'])
    elif s['brand'] == 'samsung' and s['x_type'] == 'phone':
        match = re.search(r'\bgalaxy (?:[a-z]\d{1,2}|note ?\d{1,2})\b', s['name'])
    elif s['brand'] == 'sony':
        if s['x_type'] == 'sdcard':
            match = re.search(
                r'\b(?:sf-?(?:\d{1,3}n4|[gm]\d{1,3}t|[em]\d{1,3})|sr-?\d{1,3}(?:ux2[ab]|uy[23]?a|[hu]xa|a[41](?: ?[pv])?)|sf-?(?:\d{1,3}(?:[un][41]|nx|ux(?:2b?)?|uy[23]?|b[f4]|u)|g\d{1,3})|sn-?(?:bb\d{1,3}|ba\d{1,3} ?f?))\b',
                s['name']
            )
        elif s['x_type'] == 'usbstick':
            match = re.search(
                r'\busm-?\d{1,3}(?:g(?:u|t|r|qx|mp)|w3|ca1|x|sa1|m)\b',
                s['name']
            )
        if match:
            return match.group(0).replace(' ', '').replace('-', '')
    elif s['brand'] == 'sandisk' and s['x_type'] == 'usbstick':
        match = re.search(r'\bglide|dual|fit|extreme\b', s['name'])
    elif s['brand'] == 'sandisk' and s['x_type'] == 'sdcard':
        match = re.search(r'\bextreme|ultra\b', s['name'])
    # elif s['brand'] == 'intenso' and s['x_type'] == 'usbstick':
    #     for c in (
    #         'premium',
    #         'rainbow',
    #         'basic',
    #         'speed',
    #     ):
    #         if c in s['name']:
    #             return c

    if match:
        return match.group(0).replace(' ', '')
    elif s['instance_id'] in (f'altosight.com//{x}' for x in (
            693, 835, 926, 1160,
            1872, 3407, 3762, 3815,
            3899, 5016, 6139, 6221,
            8513, 9071, 13950,
        )):
            return 'idontknowwhatmodelitisbutofcourseNOTextreme'
    elif s['instance_id'] in (f'altosight.com//{x}' for x in (
            12344,
        )):
            return 'idontknowwhatmodelitisbutofcourseNOTultra'
    elif s['instance_id'] in (f'altosight.com//{x}' for x in (
            365, 7300, 7689, 10085,
        )):
            return 'sr8a4'
    elif s['instance_id'] in (f'altosight.com//{x}' for x in (
            799, 1442, 1756, 7302,
            7391, 12123, 12124,
        )):
            return 'sf8u'
    elif s['instance_id'] in (f'altosight.com//{x}' for x in (
            1482, 1483,
        )):
            return 'usm4gmp'

    return None
