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

cpuBrand = {k: re.compile(v) for k, v in {
    'intel core': r'\b(?:intel\.?|core) i[3579]\b',
    'intel pentium': r'\bpentium\b',
    'intel celeron': r'\bceleron\b',
    'amd': r'\bamd\b',
}.items()}

cpuModel = {k: re.compile(v) for k, v in {
    'intel core': r'\b(i[3579])[ -](\d{3,5}[a-z]{0,2})\b',
    'intel pentium': r'\b(?:\d{4}[a-z]|n\d{4})\b',
    'intel celeron': r'\b\d{4}[a-z]\b',
    # 参见 https://zh.wikipedia.org/zh-cn/AMD加速处理器列表
    # [^-a-z\d]+是为了不与某种格式的笔记本型号混淆……
    'amd': r'\b([ae](?:[12468]|10|12)|e)[ -](\d{3,4}[a-z]{0,2})[^-a-z\d]+\b',
}.items()}

cpuFrequency = re.compile(r'([0-9](.|)([0-9]+|))(\s|)(ghz|mhz)')

ramCapacity = re.compile(r'(?<!max ram supported)(?: (\d+))(\s|)(gb|mb)')

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
