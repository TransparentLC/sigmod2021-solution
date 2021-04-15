import re

type = {k: re.compile(v) for k, v in {
    'sdcard': r'(?:\b(?:(?:micro ?)?sd(?:[hx]c)?|secure digital|uhs(?: class)?|exceria)\b)|\bevo\+ ',
    'xqdcard': r'\bxqd\b',
    'usbstick': r'\b(?:micro)?usb|\b(?:(?:jump|pen)?drive|cruzer|attache|transmemory|data ?traveler|micro vault)\b',
    'phone': r'\b(?:sim|lte)\b',
    'tv': r'\btv\b',
    'ssd': r'\b(?:ssd|hyperx savage)\b',
    'hdd': r'\b(?:hdd|disque|disco rigido|disque dur)\b',
}.items()}

size = re.compile(r'\b((?:\d+\.)?\d+) ?(g[bo]|tb)(?! ?ram)\b')
