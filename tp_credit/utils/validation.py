from __future__ import annotations

from typing import Any


ALLOWED_SITUATIONS_FAMILIALES = {"celibataire", "marie", "divorce"}
ALLOWED_TYPES_EMPLOI = {"salarie_prive", "fonctionnaire", "independant", "sans_emploi"}

REQUIRED_FIELDS = {
    "age",
    "revenu_mensuel",
    "montant_credit_demande",
    "duree_remboursement_mois",
    "nb_credits_anterieurs",
    "situation_familiale",
    "type_emploi",
}


def _to_float(value: Any, field_name: str, errors: dict[str, str]) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        errors[field_name] = "Doit être une valeur numérique"
        return None


def _to_int(value: Any, field_name: str, errors: dict[str, str]) -> int | None:
    numeric_value = _to_float(value, field_name, errors)
    if numeric_value is None:
        return None

    if not numeric_value.is_integer():
        errors[field_name] = "Doit être une valeur entière"
        return None

    return int(numeric_value)


def validate_credit_payload(payload: dict[str, Any] | None) -> tuple[dict[str, Any], dict[str, str]]:
    errors: dict[str, str] = {}
    cleaned: dict[str, Any] = {}

    if not isinstance(payload, dict):
        return {}, {"payload": "Le corps de la requête doit être un JSON valide"}

    missing_fields = [field for field in REQUIRED_FIELDS if field not in payload]
    for field in missing_fields:
        errors[field] = "Champ obligatoire manquant"

    age = _to_int(payload.get("age"), "age", errors)
    if age is not None:
        if not 18 <= age <= 80:
            errors["age"] = "L’âge doit être compris entre 18 et 80"
        else:
            cleaned["age"] = age

    revenu_mensuel = _to_float(payload.get("revenu_mensuel"), "revenu_mensuel", errors)
    if revenu_mensuel is not None:
        if revenu_mensuel <= 0:
            errors["revenu_mensuel"] = "Le revenu mensuel doit être supérieur à 0"
        else:
            cleaned["revenu_mensuel"] = revenu_mensuel

    montant_credit = _to_float(payload.get("montant_credit_demande"), "montant_credit_demande", errors)
    if montant_credit is not None:
        if montant_credit <= 0:
            errors["montant_credit_demande"] = "Le montant demandé doit être supérieur à 0"
        else:
            cleaned["montant_credit_demande"] = montant_credit

    duree = _to_int(payload.get("duree_remboursement_mois"), "duree_remboursement_mois", errors)
    if duree is not None:
        if not 6 <= duree <= 120:
            errors["duree_remboursement_mois"] = "La durée doit être comprise entre 6 et 120 mois"
        else:
            cleaned["duree_remboursement_mois"] = duree

    nb_credits = _to_int(payload.get("nb_credits_anterieurs"), "nb_credits_anterieurs", errors)
    if nb_credits is not None:
        if nb_credits < 0:
            errors["nb_credits_anterieurs"] = "Le nombre de crédits antérieurs doit être supérieur ou égal à 0"
        else:
            cleaned["nb_credits_anterieurs"] = nb_credits

    situation_familiale = payload.get("situation_familiale")
    if isinstance(situation_familiale, str):
        situation_familiale = situation_familiale.strip().lower()
        if situation_familiale not in ALLOWED_SITUATIONS_FAMILIALES:
            errors["situation_familiale"] = "Valeur invalide"
        else:
            cleaned["situation_familiale"] = situation_familiale
    else:
        errors["situation_familiale"] = "Doit être une chaîne de caractères"

    type_emploi = payload.get("type_emploi")
    if isinstance(type_emploi, str):
        type_emploi = type_emploi.strip().lower()
        if type_emploi not in ALLOWED_TYPES_EMPLOI:
            errors["type_emploi"] = "Valeur invalide"
        else:
            cleaned["type_emploi"] = type_emploi
    else:
        errors["type_emploi"] = "Doit être une chaîne de caractères"

    return cleaned, errors
