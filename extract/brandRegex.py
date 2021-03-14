import re

brandPattern = {
    'acer': r'\bacer\b',
    'asus': r'\basus\b',
    'dell': r'\bdell\b',
    'hp': r'\bhp\b',
    'lenovo': r'\b(?:lenovo|thinkpad)\b',
}

brandRegex = {k: re.compile(v, re.IGNORECASE) for k, v in brandPattern.items()}