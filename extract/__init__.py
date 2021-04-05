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
    for col in ('cpu_brand', 'cpu_model', 'title'):
        if not pd.isna(s[col]):
            for k, r in regexPattern.cpuBrand.items(): # type: str, re.Pattern
                match = re.search(r, s[col])
                if match:
                    return k
    warnings.warn(f'Unable to extract CPU brand for "{s["title"]}".')
    return None
   
def cpuModel(s: pd.core.series.Series) -> str:
    for col in ('cpu_brand', 'cpu_model', 'title'):
        if not pd.isna(s[col]):
            match = re.search(regexPattern.cpuModel[s['x_cpu_brand']], s[col])
            if match:
                if s['x_cpu_brand'] in ('intel celeron', 'intel pentium'):
                    return match.group(0)
                elif s['x_cpu_brand'] in ('intel core', 'amd'):
                    return f'{match.group(1)}-{match.group(2)}'
    warnings.warn(f'Unable to extract CPU model for "{s["title"]}".')
    return None

def cpuFrequency(s: pd.core.series.Series) -> float:
    # 单位GHz
    if not pd.isna(s['cpu_frequency']):
        match = re.search(regexPattern.cpuFrequency, s['cpu_frequency'])
        if not (match is None):
            fre_unit = match.group(3)
            fre = float(match.group(1))
            if fre == 0:
                return None
            elif fre_unit == 'mhz':
                fre /= 1000
            return fre
    warnings.warn(f'Unable to extract CPU frequency for "{s["title"]}".')
    return None
                      
def ramCapacity(s: pd.core.series.Series) -> float:
    # 单位GB
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
    #尝试从标题获取
    if not pd.isna(s['title']) :
        match = re.search(regexPattern.ramCapacityTitle,s['title'])
        if not (match is None):
            return float(match.group(1))
    warnings.warn(f'Unable to extract RAM capacity for "{s["title"]}".')
    return None

def ramType(s: pd.core.series.Series) -> str:
    if not pd.isna(s['ram_type']) :
        match = re.search(regexPattern.ramType,s['ram_type'])
        if not (match is None):
            return match.group()
    #尝试从标题获取
    if not pd.isna(s['title']) :
        match = re.search(regexPattern.ramType,s['title'])
        if not (match is None):
            return match.group()
    warnings.warn(f'Unable to extract RAM type for "{s["title"]}".')
    return None

def winType(s: pd.core.series.Series) -> typing.Optional[str]:
    # 为什么会有些数据把操作系统的信息写在ram_capacity里面……啊！
    for col in ('title', 'ram_capacity'):
        if not pd.isna(s[col]) :
            match = re.search(regexPattern.winType, s[col])
            if not (match is None):
                winVer = match.group(1)
                winType = match.group(2)
                if winType:
                    if winType == 'professional':
                        winType = 'pro'
                    elif winType == 'home premium':
                        winType = 'home'
                    return f'{winVer} {winType}'
                else:
                    return winVer
    warnings.warn(f'Unable to extract system for "{s["title"]}".')
    return None

def model(s: pd.core.series.Series) -> typing.Optional[str]:
    if 'elitebook' in s['title']:
        match=re.search(regexPattern.model['hp2'], s['title'])
        if not (match is None):
            return match.group()
    if not pd.isna(s['title']):
        if s['x_brand'] in regexPattern.model:
            match = re.search(regexPattern.model[s['x_brand']], s['title'].replace('15-series',''))
            if not (match is None):
                m = match.group(1) # type: typing.Optional[str]
                if s['x_brand'] == 'lenovo':
                    m += ' ' + match.group(2)
                elif s['x_brand'] == 'hp':
                    # 那个正则表达式也可能误匹配到这些七个字母的词
                    if m in ('windows', 'revolve', 'hewlett', 'packard'):
                        m = None
                    else:
                        r = match.group(2) # type: typing.Optional[str]
                        if r and m.endswith(r):
                            m = m[:-len(r)]
                return m
        else:
            # 考虑brand是other的情况，尝试按照这个规则查找型号
            # 去除各种符号
            # 按照空格分割，去掉空字符串，长度至少为2
            # 剩下的第一个同时有字母和数字的词，也允许有-
            title = s['title'] # type: str
            for char in ',.":;()&/\\':
                title = title.replace(char, ' ')
            titleWords = tuple(filter(lambda s: len(s) > 1, title.split(' ')))
            for w in titleWords:
                if (
                    re.search(r'^[a-z\d-]+$', w) and
                    re.search(r'[a-z]+', w) and
                    re.search(r'\d+')
                ):
                    return w
    warnings.warn(f'Unable to extract model for "{s["title"]}".')
    return None

def size(s: pd.core.series.Series) -> typing.Optional[float]:
    match = re.search(regexPattern.size, s['title'])
    if not (match is None):
        m = match.group(1) # type: typing.Optional[str]
        return round(float(m))
    warnings.warn(f'Unable to extract size for "{s["title"]}".')
    return None