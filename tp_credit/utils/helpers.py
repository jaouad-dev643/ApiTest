from __future__ import annotations

import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model.pkl"
DATASET_PATH = BASE_DIR / "credit_dataset.csv"
HISTORY_PATH = BASE_DIR / "historique_predictions.json"


def load_model(model_path: Path = MODEL_PATH) -> Any:
    if not model_path.exists():
        raise FileNotFoundError(f"Modèle introuvable: {model_path}")

    with model_path.open("rb") as model_file:
        return pickle.load(model_file)


def ensure_history_file(history_path: Path = HISTORY_PATH) -> None:
    if not history_path.exists():
        history_path.write_text("[]", encoding="utf-8")


def append_history_entry(entry: dict[str, Any], history_path: Path = HISTORY_PATH) -> None:
    ensure_history_file(history_path)
    try:
        with history_path.open("r", encoding="utf-8") as history_file:
            entries = json.load(history_file)
            if not isinstance(entries, list):
                entries = []
    except (json.JSONDecodeError, OSError):
        entries = []

    entries.append(entry)

    with history_path.open("w", encoding="utf-8") as history_file:
        json.dump(entries, history_file, ensure_ascii=False, indent=2)


def read_recent_history(limit: int = 10, history_path: Path = HISTORY_PATH) -> list[dict[str, Any]]:
    ensure_history_file(history_path)

    try:
        with history_path.open("r", encoding="utf-8") as history_file:
            entries = json.load(history_file)
            if not isinstance(entries, list):
                return []
    except (json.JSONDecodeError, OSError):
        return []

    return entries[-limit:][::-1]


def _normalize_decision(decision: Any) -> str:
    value = str(decision).strip().upper()
    if value in {"ACCORDE", "ACCORDÉ", "ACCEPTE", "ACCEPTED", "1"}:
        return "ACCORDE"
    return "REFUSE"


def to_decision_display(decision: Any) -> str:
    normalized = _normalize_decision(decision)
    return "ACCORDÉ" if normalized == "ACCORDE" else "REFUSÉ"


def build_history_entry(input_data: dict[str, Any], decision: str, confiance: str) -> dict[str, Any]:
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "donnees_recues": input_data,
        "decision": decision,
        "confiance": confiance,
    }


def compute_dataset_statistics(dataset_path: Path = DATASET_PATH) -> dict[str, Any]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset introuvable: {dataset_path}")

    dataframe = pd.read_csv(dataset_path)
    if "decision" not in dataframe.columns:
        raise ValueError("La colonne 'decision' est absente du dataset")

    normalized_decisions = dataframe["decision"].apply(_normalize_decision)
    total = len(dataframe)
    accords = int((normalized_decisions == "ACCORDE").sum())
    refus = int((normalized_decisions == "REFUSE").sum())

    accord_rate = (accords / total * 100) if total else 0.0
    refus_rate = (refus / total * 100) if total else 0.0

    revenus_accordes = dataframe.loc[normalized_decisions == "ACCORDE", "revenu_mensuel"]
    revenus_refuses = dataframe.loc[normalized_decisions == "REFUSE", "revenu_mensuel"]

    repartition_emploi = (
        dataframe["type_emploi"].value_counts(normalize=True).mul(100).round(2).to_dict()
        if "type_emploi" in dataframe.columns
        else {}
    )

    return {
        "nombre_total_demandes": int(total),
        "nombre_demandes_accordees": accords,
        "nombre_demandes_refusees": refus,
        "taux_accord": round(accord_rate, 2),
        "taux_refus": round(refus_rate, 2),
        "revenu_moyen_accordes": round(float(revenus_accordes.mean()), 2) if not revenus_accordes.empty else 0.0,
        "revenu_moyen_refuses": round(float(revenus_refuses.mean()), 2) if not revenus_refuses.empty else 0.0,
        "montant_moyen_demande": round(float(dataframe["montant_credit_demande"].mean()), 2),
        "duree_moyenne_remboursement": round(float(dataframe["duree_remboursement_mois"].mean()), 2),
        "repartition_par_type_emploi": repartition_emploi,
    }
