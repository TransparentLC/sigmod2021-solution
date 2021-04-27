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
    # 这个似乎是X4里面标错了
    if s['instance_id'] == 'altosight.com//13459':
        return 128

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
    # if 'micro-usb' in s['name'] or 'micro usb' in s['name'] or 'microusb' in s['name']:
    #     return 'micro'
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
        match = re.search(r'\bglide|dual|fit|extreme|ultra\b', s['name'])
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
    else:
        # 如果name里面根本没有写型号/写错了，就只能参考Y4直接钦定硬点了
        forcelySetModels = {
            k: set(f'altosight.com//{x}' for x in v)
            for k, v in ({
                'NOTextreme': (
                    693, 835, 926, 1160, 1872, 3407, 3762, 3815,
                    3899, 5016, 6139, 6221, 8513, 9071, 13950,
                ),
                'NOTultra': (
                    12344,
                ),
                'sr8a4': (
                    365, 7300, 7689, 10085,
                ),
                'srg1uxa': (
                    25, 289, 299, 2251, 5435, 7264, 7379, 8585,
                    9410, 11130, 12085,
                ),
                'sf8u': (
                    799, 1442, 1756, 7302, 7391, 12123, 12124,
                ),
                'sf16n4': (
                    1437, 2835, 9520, 9628, 10079, 12099, 12100, 13370,
                    13626, 13932,
                ),
                'usm4gmp': (
                    1482, 1483,
                ),
                'usm16ca1': (
                    1226, 1281, 8491, 9435, 9506, 11151,
                ),
                'usm32gqx': (
                    12813,
                ),
                'usm32gr': (
                    4583, 5053, 12799, 12800, 13389,
                ),
                'n101': (
                    1352, 1353, 1354, 4665, 5148, 5224, 5313, 5225,
                    6266, 6349, 6350, 6439, 9531, 9544, 9545, 10113,
                    12461, 13435, 13436,
                ),
                'n302': (
                    6507, 9219,
                ),
                'n401': (
                    3600, 6306, 11666,
                ),
                'u202': (
                    3595, 3672, 3676, 6198, 9054,
                ),
                # 这个是网上查的，因为这四个是一组但是完全不符合上面的型号格式
                'v128': (
                    1550, 4539, 5666, 5667,
                ),
                'c20c': (
                    4073, 13459,
                ),
                'c20m': (
                    5848, 11419, 11422,
                ),
                's70': (
                    1198,
                ),
            }).items()
        }
        for k, v in forcelySetModels.items():
            if s['instance_id'] in v:
                return k

    return None
