import re

# 在这里保存要用到的各种正则表达式
# 看不懂的话可以粘贴到这里查看示意图：
# https://regexper.com
# https://jex.im/regulex/

brand = {k: re.compile(v) for k, v in {
    'acer': r'\bacer\b',
    'asus': r'\basus\b',
    'dell': r'\bdell\b',
    'hp': r'\bhp\b',
    'lenovo': r'\b(?:lenovo|thinkpad)\b',
}.items()}

weight = re.compile(r'\b([0-9]*\.?[0-9]+) ?((?:kg|pounds|lbs))\b')

disk = re.compile(r'\b([0-9]+) ?((?:gb|tb))(?: (?:\d+ ?rpm ?)?(ram|hdd|sata|mechanical_hard_drive|hard drive|ssd|flash_memory_solid_state))?(?: \/ \d+ ?rpm)?\b')

cpuBrand = re.compile(r'(intel|amd|core)(\s[a-z]+\s(a|i)[0-9]|\s[a-z]+[0-9]|\s(e|a)(-|\s)([0-9]+|[a-z]+)|\s[a-z]+|)')

cpuModel = re.compile(r'(i|a|n)([0-9])(\s\(.+?\)\s|-|\s|)([0-9]+|)(u|m|lm|)')

cpuModel2 = re.compile(r'(intel pentium|intel celeron)(\s[0-9]+|)(u|m|)')

cpuModel3 = re.compile(r'(i|a|n)([0-9])(\s\(.+?\)\s|-|\s)([0-9]+)(u|m|lm|)')

cpuFrequency = re.compile(r'([0-9](.|)([0-9]+|))(\s|)(ghz|mhz)')

ramCapacity = re.compile(r'([0-9]+)(\s|)(gb|mb)')

ramType = re.compile(r'\b(?:(?:ddr\dl?)|(?:so-dimm))\b')

winType = re.compile(r'\b(?:windows|win) ([0-9]*\.?[0-9]+|xp) ?((?:professional|pro|home premium|home)?)\b')

Number = re.compile(r'[a-h,j-z][0-9]+(-|\s|)([0-9]+|)')

# 有些品牌在X2里出现的次数太少了，所以还得自己在网上看一堆型号才行……
# 比如这里，注意每个产品标题下面的MFR字样：
# https://www.bhphotovideo.com/c/products/Notebooks/ci/6782/N/4110474287
model = {k: re.compile(v) for k, v in {
    'acer': r'(?:\b|;)([a-z]\d-\d{3})[a-z]*-[a-z\d.]+\b',
    'asus': r'\b([a-z]+\d+[a-z]+-[a-z]+\d+[a-z]*)\b',
    'dell': r'\b([a-z\d]{5}(?:-[a-z\d]+)?)\b',
    'hp': r'\b((?:\d{2}[a-z]?-[a-z\d]{6})|(?:[a-z\d]{3})([a-z\d]{4}))\b',
    'hp2':r'[0-9]+(\s|)(m|g|p)',   #elitebook
    'lenovo': r'\b(x\d{1,3})[a-z]?(?: (?:carbon|carbon touch|tablet|tablet pc|laptop))? (\d{4})[a-z\d]*\b',
}.items()}
