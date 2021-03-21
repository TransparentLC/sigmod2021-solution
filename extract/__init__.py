import pandas as pd
import typing
import warnings
from .regexPattern import *

def brand(s: pd.core.series.Series) -> str:
    for k, r in regexPattern.brand.items(): # type: str, re.Pattern
        if (not pd.isna(s['brand']) and r.search(s['brand'])) or r.search(s['title']):
            return k
    warnings.warn(f'Unable to extract brand for "{s["title"]}".')
    return 'other'

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
            return value

def diskCapacity(s: pd.core.series.Series) -> pd.Series:
    # 同时返回HDD和SSD的大小，以GB为单位
    hdd = 0
    ssd = 0
    hddGuess = False
    ssdGuess = False
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
            # 经常有“8gb ram - 128gb ssd”这种写法，这个RAM很容易混淆
            # 所以把大小后面的RAM也写到正则表达式里（就像大小后面的HDD或SSD等等一样）
            # 但是这种时候就跳过
            if type == 'ram':
                continue
            if unit == 'tb':
                capacity *= 1024
            # 只有在HDD/SSD那一列搜索时才不要求出现类型
            # 但是也有title写着ssd，hdd_capacity也写着ssd，但是ssd_capacity空着的情况
            # 这样的结果就是HDD和SSD都是相同的值，需要把其中一个设为0
            if type == '' and col == 'hdd_capacity' or type in ('hdd', 'sata', 'mechanical_hard_drive', 'hard drive'):
                hddGuess = type == '' and col == 'hdd_capacity'
                hdd = capacity
            elif type == '' and col == 'ssd_capacity' or type in ('ssd', 'flash_memory_solid_state'):
                ssdGuess = type == '' and col == 'ssd_capacity'
                ssd = capacity

    if hdd == 0 and ssd == 0:
        warnings.warn(f'Unable to extract disk capacity for "{s["title"]}".')
    elif hdd == ssd:
        if hddGuess:
            hdd = 0
        elif ssdGuess:
            ssd = 0
    return pd.Series((hdd, ssd))

def cpuBrand(s: pd.core.series.Series) -> str:
    if not pd.isna(s['cpu_brand']):
        match = re.search(regexPattern.cpuBrand, s['cpu_brand'])
        return match.group()
    warnings.warn(f'Unable to extract CPU brand for "{s["title"]}".')
    return None
   
def cpuModel(s: pd.core.series.Series) -> str:
    ms1,ms2,ms3='','',''
    if not pd.isna(s['cpu_model']) :
        match1 = re.search(regexPattern.cpuModel,s['cpu_model'])
        if (match1 is None):
            match1=re.search(regexPattern.cpuModel2,s['cpu_model'])
        if not (match1 is None):
            ms1=match1.group().replace(' ( 3rd gen )','').replace(' ( 2nd gen )','').replace(' ( 4th gen )','')
        else:
            ms1=''
    if not pd.isna(s['title']) :
        match2 = re.search(regexPattern.cpuModel3,s['title'])
        if (match2 is None):
            match2=re.search(regexPattern.cpuModel2,s['title'])
        if not (match2 is None):
            ms2=match2.group().replace(' ( 3rd gen )','').replace(' ( 2nd gen )','').replace(' ( 4th gen )','')
        else:
            ms2=''
    if not pd.isna(s['cpu_brand']) :
        match3 = re.search(regexPattern.cpuModel,s['cpu_brand'])
        if (match3 is None):
            match3=re.search(regexPattern.cpuModel2,s['cpu_brand'])
        if not (match3 is None):
            ms3=match3.group().replace(' ( 3rd gen )','').replace(' ( 2nd gen )','').replace(' ( 4th gen )','')
        else:
            ms3=''
    match=max([ms1,ms2,ms3],key=len)
    return match.replace('-',' ')
                  
def cpuFrequency(s: pd.core.series.Series) -> float:
    #单位GHz
    if not pd.isna(s['cpu_frequency']):
        match = re.search(regexPattern.cpuFrequency, s['cpu_frequency'])
        if not (match is None):
            fre_unit = match.group(3)
            fre = float(match.group(1))
            if fre_unit == 'mhz':
                fre /= 1000
            return fre
    warnings.warn(f'Unable to extract CPU frequency for "{s["title"]}".')
    return None
                      
def ramCapacity(s: pd.core.series.Series) -> float:
    #单位GB
    if not pd.isna(s['ram_capacity']) :
        match = re.search(regexPattern.ramCapacity, s['ram_capacity'])
        if not (match is None):
            cap_unit = match.group(3)
            cap = float(match.group(1))
            # 修正某个把4GB打成4MB的情况
            if cap_unit == 'mb' and cap >= 1024:
                cap /= 1024
            # 修正0GB的情况
            if cap:
                return cap
    warnings.warn(f'Unable to extract RAM capacity for "{s["title"]}".')
    return None

def ramType(s: pd.core.series.Series) -> str:
    if not pd.isna(s['ram_type']) :
        match = re.search(regexPattern.ramType,s['ram_type'])
        if not (match is None):
            return match.group()
    warnings.warn(f'Unable to extract RAM type for "{s["title"]}".')
    return None
