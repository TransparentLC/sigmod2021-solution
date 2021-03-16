import re

# 在这里保存要用到的各种正则表达式
# 看不懂的话可以粘贴到这里查看示意图：
# https://regexper.com

brand = {k: re.compile(v) for k, v in {
    'acer': r'\bacer\b',
    'asus': r'\basus\b',
    'dell': r'\bdell\b',
    'hp': r'\bhp\b',
    'lenovo': r'\b(?:lenovo|thinkpad)\b',
}.items()}

weight = re.compile(r'\b([0-9]*\.?[0-9]+) ?((?:kg|pounds|lbs|g))\b')

cpuBrand=re.compile(r'(intel|amd)(\s[a-z]+\s(a|i)[0-9]|\s[a-z]+[0-9]|\s(e|a)(-|\s)([0-9]+|[a-z]+)|\s[a-z]+|)')
