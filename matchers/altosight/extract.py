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

def size(s: pd.Series) -> str:
    res=""
    if not pd.isna(s['size']):
        match=re.search(regexPattern.size2,s['size'])
        if match:
            s1=match.group(1)+" "+match.group(3).replace("go","gb")
            res+=s1
    
    match=re.search(regexPattern.size,s['name'])
    if match:
        s2=match.group(1)+" "+match.group(2).replace("go","gb")
        if res!=s2:
            res+=s2
    
    if res!="":
        return res
        
    return None

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

def model(s: pd.Series) -> typing.Optional[str]:
    match = None
    if s['brand'] == 'toshiba' and s['x_type'] in ('usbstick', 'sdcard'):
        match = re.search(r'[mnu]\d0\d', s['name'])
    elif s['brand'] == 'lexar' and s['x_type'] in ('usbstick',):
        match = re.search(r'[cpsv]\d[05][cm]?', s['name'])
    elif s['brand'] == 'samsung' and s['x_type'] in ('phone',):
        match = re.search(r'\bgalaxy (?:[a-z]\d{1,2}|note ?\d{1,2})\b', s['name'])
    if match:
        return match.group(0).replace(' ','')
    return None
