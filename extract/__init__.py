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
    matches = regexPattern.weight.findall(s['title'] if pd.isna(s['weight']) else s['weight']) # type: list[tuple[str, str]]
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

def diskCapacity(s: pd.core.series.Series) -> tuple[int, int]:
    # 同时返回HDD和SSD的大小，以GB为单位
    # 先获取HDD的大小
    hdd = 0
    ssd = 0
    for col in ('hdd_capacity', 'ssd_capacity', 'title'):
        if pd.isna(s[col]):
            continue
        matches = regexPattern.disk.findall(s[col]) # type: list[tuple[str, str, str]]
        if len(matches) == 0:
            continue
        for m in matches:
            capacity = int(m[0]) # type: int
            unit = m[1] # type: str
            type = m[2] # type: typing.Optional[str]
            if unit == 'tb':
                capacity *= 1024
            # 只有在HDD那一列搜索时才不要求出现类型
            if type in ('hdd', 'sata', 'mechanical_hard_drive', 'hard drive') or (type == '' and col == 'hdd_capacity'):
                hdd = capacity
            # 只有在SSD那一列搜索时才不要求出现类型
            elif type in ('ssd', 'flash_memory_solid_state') or (type == '' and col == 'ssd_capacity'):
                ssd = capacity

    if hdd == 0 and ssd == 0:
        warnings.warn(f'Unable to extract disk capacity for "{s["title"]}".')
    return (hdd, ssd)
