
import re
try:
    import ftfy
except ImportError:
    ftfy = None


def fix_mojibake(value):
    if value is None:
        return value
    text = str(value)
    if ftfy:
        text = ftfy.fix_text(text)
    return text


def normalize_text(value):
    if value is None:
        return ''
    text = fix_mojibake(value)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
