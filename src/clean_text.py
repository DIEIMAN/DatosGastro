import re
import unicodedata
from typing import Iterable

try:
    import ftfy
except ImportError:  # pragma: no cover - optional dependency
    ftfy = None


MOJIBAKE_MARKERS = ("Ã", "Â", "â", "€", "™", "œ", "�")
EMPTY_VALUES = {"", "nan", "none", "null", "s/d", "sd", "sin dato", "no disponible"}


def fix_mojibake(value):
    if value is None:
        return value
    text = str(value)
    if ftfy:
        text = ftfy.fix_text(text)
    replacements = {
        "Ã¡": "á",
        "Ã©": "é",
        "Ã­": "í",
        "Ã³": "ó",
        "Ãº": "ú",
        "Ã±": "ñ",
        "Ã": "Á",
        "Ã‰": "É",
        "Ã": "Í",
        "Ã“": "Ó",
        "Ãš": "Ú",
        "Ã‘": "Ñ",
        "Âª": "ª",
        "Âº": "º",
        "Â°": "°",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text


def clean_spaces(value) -> str:
    if value is None:
        return ""
    text = fix_mojibake(value)
    text = re.sub(r"[\t\r\n]+", " ", str(text))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def strip_accents(value) -> str:
    text = clean_spaces(value)
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_case(value, mode: str = "preserve") -> str:
    text = clean_spaces(value)
    if mode == "upper":
        return text.upper()
    if mode == "lower":
        return text.lower()
    if mode == "title":
        return text.title()
    return text


def normalize_text(value, case: str = "preserve", remove_accents: bool = False) -> str:
    text = normalize_case(value, case)
    if remove_accents:
        text = strip_accents(text)
    return clean_spaces(text)


def normalize_proper_name(value) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    if text.isupper() or text.islower():
        return text.title()
    return text


def is_empty_like(value) -> bool:
    return normalize_text(value, case="lower", remove_accents=True) in EMPTY_VALUES


def has_suspect_encoding(value) -> bool:
    text = str(value or "")
    if any(marker in text for marker in MOJIBAKE_MARKERS):
        return True
    fixed = fix_mojibake(text)
    return fixed != text and any(marker in text for marker in MOJIBAKE_MARKERS)


def clean_dataframe_columns(df, columns: Iterable[str] | None = None, case: str = "preserve"):
    selected = list(columns) if columns is not None else list(df.select_dtypes(include="object").columns)
    result = df.copy()
    for column in selected:
        if column in result.columns:
            result[column] = result[column].map(lambda value: normalize_text(value, case=case))
    return result


if __name__ == "__main__":
    samples = ["  LA  POESÃA  ", "san cristobal", "Noche de las HeladerÃ­as"]
    for sample in samples:
        print(
            {
                "original": sample,
                "normalizado": normalize_text(sample),
                "nombre_propio": normalize_proper_name(sample),
                "sospechoso": has_suspect_encoding(sample),
            }
        )
