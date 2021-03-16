import pandas as pd
import typing
import warnings
from .regexPattern import *

def brand(s: pd.core.series.Series) -> str:
    for k, r in regexPattern.brand.items(): # type: str, re.Pattern
        if (not pd.isna(s['brand']) and r.search(s['brand'])) or r.search(s['title']):
            return k
    # 找不到的话就使用brand的原始值
    fallback = s['title'] if pd.isna(s['brand']) else s['brand']
    warnings.warn(f'Unable to extract brand, fallback to "{fallback}".')
    return fallback

def weight(s: pd.core.series.Series) -> typing.Optional[float]:
    matches = regexPattern.weight.findall(s['title'] if pd.isna(s['weight']) else s['weight'])
    if len(matches) == 0:
        # 找不到的话就是真的没有数据了
        return None
    else:
        # 统一以kg为单位，否则需要换算
        matchKg = next((m for m in matches if m[1] == 'kg'), None) # type: typing.Optional[tuple[str, str]]
        if matchKg:
            return float(matchKg[0])
        else:
            for m in matches: # type: tuple[str, str]
                value = float(m[0])
                unit = m[1]
                if unit in ('lbs', 'pounds'):
                    value = round(float(m[0]) * .45359237, 2)
                    break
                elif unit == 'g':
                    value = float(m[0]) / 1000
                    break
            return value

def cpuBrand(s: pd.core.series.Series) -> str:
    if(not pd.isna(s['cpu_brand'])):
        match=re.search(regexPattern.cpuBrand,s['cpu_brand'])
        return match.group()
    else:
        return None
