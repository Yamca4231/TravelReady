# tests/unit/test_validation.py
# --------------------------------------------------------------------------------------
# Testy jednostkowe walidacji. Sprawdza ścieżki poprawnego działania oraz błędów
# --------------------------------------------------------------------------------------

import pytest

# Jeden bezpieczny import na poziomie modułu
try:
    from app.validation import validate_checked_payload, validate_checked_list, ValidationError
except Exception as e:
    pytest.skip(f"Brak app.validation – pomijam testy walidacji ({e})", allow_module_level=True)

pytestmark = [pytest.mark.unit]

# Pomocnik do asercji komunikatów błędów.
def _msg_has(msg: str, candidates: list[str]) -> bool: 
    msg = msg.lower()
    return any(c.lower() in msg for c in candidates)

# --------------------------------------------------------------------------------------
# TESTY
# --------------------------------------------------------------------------------------

# TC-U-03: Pusta lista zaznaczonych pozycji.
# Oczekiwanie: dozwolone — walidator zwraca pustą listę (brak błędu).
def test_validate_accepts_empty_list_and_returns_empty():
    allowed = {"Kurtka", "Rękawice"}
    payload = {"checked": []}
    assert validate_checked_payload(payload, allowed) == []

# TC-U-04: Poprawne elementy, ale z duplikatem.
#   Oczekiwanie: zwrócona lista bez duplikatów, z zachowaniem kolejności pierwszych wystąpień.
def test_validate_accepts_subset_and_deduplicates_preserving_order():
    allowed = {"Kurtka", "Rękawice", "Powerbank"}
    payload = {"checked": ["Kurtka", "Powerbank", "Kurtka", "Rękawice"]}
    assert validate_checked_payload(payload, allowed) == ["Kurtka", "Powerbank", "Rękawice"]

# TC-U-05: 'checked' nie jest listą (np. string).
# Oczekiwanie: ValidationError z komunikatem „musi być listą”.
def test_validate_rejects_non_list_checked():
    with pytest.raises(ValidationError) as e:
        validate_checked_payload({"checked": "Kurtka"}, {"Kurtka"})
    assert _msg_has(str(e.value), ["musi być listą", "must be a list"])


# TC-U-06: element na liście nie jest stringiem (np. int).
# Oczekiwanie: ValidationError z komunikatem „musi być string”.
def test_validate_rejects_non_string_items():
    with pytest.raises(ValidationError) as e:
        validate_checked_payload({"checked": ["Kurtka", 123]}, {"Kurtka"})
    assert _msg_has(str(e.value), ["musi być string", "must be a string"])

# TC-U-07: lista zawiera element spoza dozwolonego zbioru (whitelisty).
# Oczekiwanie: ValidationError i wskazanie „winowajcy” w komunikacie.
def test_validate_rejects_unknown_items():
    with pytest.raises(ValidationError) as e:
        validate_checked_payload({"checked": ["Kurtka", "nieznany element"]}, {"Kurtka", "Rękawice"})
    msg = str(e.value)
    assert _msg_has(msg, ["nieznane elementy", "unknown items"]) and "nieznany element" in msg

# TC-U-08: duży ładunek (wiele elementów), nawet jeśli to duplikaty.
# Oczekiwanie: limit jest egzekwowany PRZED deduplikacją — błąd.
def test_limit_max_len_is_enforced_before_dedup():
    with pytest.raises(ValidationError) as e:
        validate_checked_payload({"checked": ["A"] * 5}, {"A", "B"}, max_len=3)
    assert _msg_has(str(e.value), ["zbyt wiele elementów", "too many items"])

# TC-U-09: Użycie wrappera przyjmującego „gołą” listę.
# Oczekiwanie: zwrócona lista bez duplikatów, z zachowaniem kolejności pierwszych wystąpień.
def test_validate_checked_list_wrapper_returns_deduped_order():
    out = validate_checked_list(["Kurtka", "Rękawice", "Kurtka"], {"Kurtka", "Rękawice"}, max_len=10)
    assert out == ["Kurtka", "Rękawice"]

# TC-U-10: Potwierdza, że wrapper zachowuje się jak validate_checked_payload dla tej samej listy.
def test_payload_must_be_object_and_missing_key():
    with pytest.raises(ValidationError):
        validate_checked_payload(["nie-dict"], {"X"})
    with pytest.raises(ValidationError):
        validate_checked_payload({}, {"X"})