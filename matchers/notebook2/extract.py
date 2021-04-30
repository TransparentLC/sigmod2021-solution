import pandas as pd
import re
import typing
import warnings
from . import regexPattern

customNotebookFeatures = (
    'x_brand',
    'x_weight',
    'x_hdd_capacity',
    'x_ssd_capacity',
    'x_cpu_brand',
    'x_cpu_model',
    'x_cpu_frequency',
    'x_ram_capacity',
    'x_ram_type',
    'x_win_type',
    'x_model',
    'x_size',
)

def brand(s: pd.Series) -> str:
    for k, r in regexPattern.brand.items(): # type: str, re.Pattern
        if (not pd.isna(s['brand']) and r.search(s['brand'])) or r.search(s['title']):
            return k
    warnings.warn(f'Unable to extract brand for "{s["title"]}".')
    return 'other'

def weight(s: pd.Series) -> typing.Optional[float]:
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
                if unit in ('lb', 'lbs', 'pounds'):
                    value = round(float(m[0]) * .45359237, 2)
                    break
                elif unit == 'oz':
                    value = round(float(m[0]) * .0283495231, 2)
                    break
            return value

def diskCapacity(s: pd.Series) -> pd.Series:
    # 同时返回HDD和SSD的大小，以GB为单位
    hdd = 0
    ssd = 0
    hddGuess = False
    ssdGuess = False
    # 有些硬盘大小写在ram_type里
    for col in ('hdd_capacity', 'ssd_capacity', 'title', 'ram_type'):
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
            if type == '' and col == 'hdd_capacity' or type in ('hdd', 'hd','sata', 'mechanical_hard_drive', 'hard drive'):
                # 针对形如 memory size 4gb hard disk 180gb ssd
                if capacity < 20:
                    continue
                hddGuess = type == '' and col == 'hdd_capacity'
                hdd = capacity
            elif type == '' and col == 'ssd_capacity' or type in ('ssd', 'flash_memory_solid_state'):
                ssdGuess = type == '' and col == 'ssd_capacity'
                ssd = capacity
            # 若此时还未获取到大小，则从title中获取500gb这种没有标注hdd还是sdd的当作hdd处理
            elif type == '' and col == 'title' and capacity >= 20 and hdd == 0 and ssd == 0:
                hdd = capacity

    if hdd == 0 and ssd == 0:
        warnings.warn(f'Unable to extract disk capacity for "{s["title"]}".')
    elif hdd == ssd:
        if hddGuess:
            hdd = 0
        elif ssdGuess:
            ssd = 0
    return pd.Series((hdd, ssd))

def cpuBrand(s: pd.Series) -> str:
    for col in ('cpu_brand', 'cpu_model', 'title'):
        if not pd.isna(s[col]):
            for k, r in regexPattern.cpuBrand.items(): # type: str, re.Pattern
                match = re.search(r, s[col])
                if match:
                    return k
    warnings.warn(f'Unable to extract CPU brand for "{s["title"]}".')
    return None

def cpuModel(s: pd.Series) -> str:
    if not pd.isna(s['x_cpu_brand']):
        for col in ('cpu_brand', 'cpu_model', 'title', 'cpu_type', 'cpu_brand'):
            if not pd.isna(s[col]):
                match = re.search(regexPattern.cpuModel[s['x_cpu_brand']], s[col])
                if match:
                    if s['x_cpu_brand'] in ('intel celeron', 'intel pentium'):
                        return match.group(0)
                    elif s['x_cpu_brand'] == 'intel core':
                        coreType = match.group(1)
                        coreSeries = match.group(2)
                        # 某一行把i7 640m打成了i7 m640
                        if coreSeries[0].isalpha():
                            coreSeries = coreSeries[1:] + coreSeries[0]
                        # 修正一些写错的型号
                        if coreSeries in ('720q', '820q', '640'):
                            coreSeries += 'm'
                        return f'{coreType}-{coreSeries}'
                    elif s['x_cpu_brand'] == 'amd':
                        return f'{match.group(1)}-{match.group(2)}'
    warnings.warn(f'Unable to extract CPU model for "{s["title"]}".')
    return None

def cpuFrequency(s: pd.Series) -> float:
    # 单位GHz
    for col in ('cpu_frequency', 'title'):
        if not pd.isna(s[col]):
            match = re.search(regexPattern.cpuFrequency, s[col])
            if not (match is None):
                fre_unit = match.group(2)
                fre = float(match.group(1).replace(' ', '.'))
                if fre == 0:
                    return None
                elif fre_unit == 'mhz' and fre >= 1000:
                    fre /= 1000
                return fre
    warnings.warn(f'Unable to extract CPU frequency for "{s["title"]}".')
    return None

def ramCapacity(s: pd.Series) -> float:
    # 单位GB
    if not pd.isna(s['ram_capacity']) :
        match = re.search(regexPattern.ramCapacity, s['ram_capacity'])
        if not (match is None):
            cap_unit = match.group(2)
            cap = float(match.group(1))
            # 修正某个把4GB打成4MB的情况
            if cap_unit == 'mb' and cap >= 1024:
                cap /= 1024
            # 修正0GB的情况
            if cap:
                return cap
    # 尝试从标题获取
    if not pd.isna(s['title']) :
        match = re.search(regexPattern.ramCapacityTitle, s['title'])
        if not (match is None):
            cap_unit = match.group(2)
            cap = float(match.group(1))
            # 修正某个把4GB打成4MB的情况
            if cap_unit == 'mb' and cap >= 1024:
                cap /= 1024
            # 修正0GB的情况
            if cap:
                return cap
    # 如果还找不到就从标题的*gb中找到数值最小的一个
    # possibleGbs = tuple(float(x) for x in re.findall(r' (\d{1,2})gb? ', s['title']))
    # if possibleGbs:
    #     return min(possibleGbs)
    warnings.warn(f'Unable to extract RAM capacity for "{s["title"]}".')
    return None

def ramType(s: pd.Series) -> str:
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

def winType(s: pd.Series) -> typing.Optional[str]:
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

def model(s: pd.Series) -> typing.Optional[str]:
    if not pd.isna(s['title']):
        if s['x_brand'] in regexPattern.model:
            match = re.search(
                regexPattern.model[s['x_brand']],
                s['title'].replace('15-series','')
            )
            if not (match is None):
                m = match.group(1) # type: typing.Optional[str]
                if s['x_brand'] == 'acer':
                    if not m and match.group(2):
                        m = match.group(2)
                    m = '-'.join(m.split(' '))
                elif s['x_brand'] == 'dell':
                    if m.startswith('i'):
                        m = m[1:]
                elif s['x_brand'] == 'lenovo':
                    m += ' ' + match.group(2)
                elif s['x_brand'] == 'hp':
                    r = match.group(2) # type: typing.Optional[str]
                    if r and m.endswith(r):
                        m = m[:-len(r)]
                    m = ' '.join(m.split('-'))
                if m:
                    return m
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
                re.search(r'\d+', w)
            ):
                return w
    warnings.warn(f'Unable to extract model for "{s["title"]}".')
    return None

def size(s: pd.Series) -> typing.Optional[float]:
    match = re.search(regexPattern.size, s['title'])
    if not (match is None):
        m = match.group(1) # type: typing.Optional[str]
        return round(float(m))
    warnings.warn(f'Unable to extract size for "{s["title"]}".')
    return None
