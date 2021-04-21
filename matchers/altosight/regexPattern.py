import re

# $ONY的U盘和SD卡的型号非常多
# 参见：
# https://www.sony.jp/rec-media/lineup/pocketbit.html
# https://www.sony.jp/rec-media/lineup/sd.html
type = {k: re.compile(v) for k, v in {
    'sdcard': r'(?:\b(?:(?:micro ?)?sd(?:[hx]c)?|secure digital|uhs(?: class)?|exceria|sf-?(?:\d{1,3}n4|[gm]\d{1,3}t|[em]\d{1,3})|sr-?\d{1,3}(?:ux2[ab]|uy[23]?a|[hu]xa|a[41](?: ?[pv])?)|sf-?(?:\d{1,3}(?:[un][41]|nx|ux(?:2b?)?|uy[23]?|b[f4]|u)|g\d{1,3})|sn-?(?:bb\d{1,3}|ba\d{1,3} ?f?))\b)|\bevo\+ ',
    'xqdcard': r'\b(?:xqd|lxqd[a-z\d]+)\b',
    'usbstick': r'\b(?:micro)?usb|\b(?:(?:jump|pen)?drive|cruzer|attache|transmemory|data ?traveler|micro vault|basic line|hxs\d?|usm-?\d{1,3}(?:g(?:u|t|r|qx)|w3|ca1|x|sa1|m))\b',
    'phone': r'\b(?:sim|lte)\b',
    'tv': r'\btv\b',
    'ssd': r'\b(?:ssd|hyperx savage)\b',
    'hdd': r'\b(?:hdd|disque|disco rigido|disque dur)\b',
}.items()}

size = re.compile(r'\b((?:\d+\.)?\d+) ?(g[bo]|tb)(?! ?ram)\b')

tvSize = re.compile(r'\b(\d{2}(?:\.\d)?)(?:[- ]inch|")\b')
