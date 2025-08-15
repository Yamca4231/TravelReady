# app/validation.py
from typing import List, Set
from collections.abc import Collection

# Błąd walidacji danych wejściowych
class ValidationError(Exception):
    pass

# Weryfikacja, czy value to List[str]
def _ensure_list_of_str(value, field_name: str) -> List[str]:
    if not isinstance(value, list):
        raise ValidationError(f"{field_name} must be a list")
    result: List[str] = []
    for idx, el in enumerate(value):
        if not isinstance(el, str):
            raise ValidationError(f"{field_name}[{idx}] must be a string")
        result.append(el)
    return result

# GŁÓWNA FUNKCJA WALIDUJĄCA I NORMALIZUJĄCA
# Oczekuje: 
#   payload['checked']: lista stringów (elementy checklisty)
# Zwraca: 
#   znormalizowaną listę (bez duplikatów, kolejność pierwszych wystąpień zachowana),
#   w której wszystkie elementy należą do `allowed_items`
def validate_checked_payload(payload: dict, allowed_items: Collection[str], max_len: int | None = None) -> List[str]:
    
    # 1) Kształt payloadu
    if not isinstance(payload, dict):
        raise ValidationError("payload must be an object (JSON)")
    
    # 2) Obecność klucza 'checked'
    if "checked" not in payload:
        raise ValidationError("missing 'checked' field")

    # 3) Typ i elementy listy
    checked_raw = _ensure_list_of_str(payload["checked"], "checked")

    # 4) Limit długości
    if max_len is not None and len(checked_raw) > max_len:
        raise ValidationError(f"too many items: {len(checked_raw)} > {max_len}")

    # 5) Whitelista: odrzuć elementy spoza dozwolonego zbioru
    ordered_unknown = list(dict.fromkeys(x for x in checked_raw if x not in allowed_items))
    if ordered_unknown:
        raise ValidationError(f"unknown items: {', '.join(ordered_unknown)}")

    # 6) Normalizacja: usuwamy duplikaty z zachowaniem kolejności
    seen = set()
    normalized: List[str] = []
    for x in checked_raw:
        if x not in seen:
            normalized.append(x)
            seen.add(x)
    return normalized

def validate_checked_list(data: List[str], allowed_items: Set[str], max_len: int | None = None) -> List[str]:
    return validate_checked_payload({"checked": data}, allowed_items, max_len)
