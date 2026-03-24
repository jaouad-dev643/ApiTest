from __future__ import annotations

from typing import Any

import pandas as pd
from flask import Flask, jsonify, request

from utils.helpers import (
    DATASET_PATH,
    append_history_entry,
    build_history_entry,
    compute_dataset_statistics,
    ensure_history_file,
    load_model,
    read_recent_history,
    to_decision_display,
)
from utils.validation import validate_credit_payload


app = Flask(__name__)


try:
    MODEL = load_model()
    MODEL_LOAD_ERROR = None
except Exception as exc:
    MODEL = None
    MODEL_LOAD_ERROR = str(exc)

ensure_history_file()


@app.get("/")
def home() -> Any:
    return jsonify(
        {
            "message": "API crédit — opérationnelle ✅",
            "routes": {
                "POST /predire": "Soumettre une demande",
                "GET /demo": "Voir un exemple",
                "GET /statistiques": "Voir les statistiques du dataset",
                "GET /historique": "Voir les dernières prédictions",
            },
        }
    )


@app.get("/demo")
def demo_payload() -> Any:
    return jsonify(
        {
            "exemples": [
                {
                    "age": 35,
                    "revenu_mensuel": 12000,
                    "montant_credit_demande": 90000,
                    "duree_remboursement_mois": 36,
                    "nb_credits_anterieurs": 1,
                    "situation_familiale": "marie",
                    "type_emploi": "fonctionnaire",
                },
                {
                    "age": 24,
                    "revenu_mensuel": 3200,
                    "montant_credit_demande": 110000,
                    "duree_remboursement_mois": 84,
                    "nb_credits_anterieurs": 3,
                    "situation_familiale": "celibataire",
                    "type_emploi": "sans_emploi",
                },
            ]
        }
    )


@app.post("/predire")
def predict_credit() -> Any:
    if MODEL is None:
        return (
            jsonify(
                {
                    "erreur": "Modèle indisponible",
                    "details": MODEL_LOAD_ERROR or "model.pkl introuvable ou invalide",
                }
            ),
            500,
        )

    payload = request.get_json(silent=True)
    cleaned_data, validation_errors = validate_credit_payload(payload)

    if validation_errors:
        return (
            jsonify(
                {
                    "erreur": "Validation échouée",
                    "details": validation_errors,
                }
            ),
            400,
        )

    try:
        input_frame = pd.DataFrame([cleaned_data])
        prediction_raw = MODEL.predict(input_frame)[0]
        probabilities = MODEL.predict_proba(input_frame)[0]
        classes = list(MODEL.classes_)

        predicted_index = classes.index(prediction_raw)
        score_brut = float(probabilities[predicted_index])

        decision = to_decision_display(prediction_raw)
        confiance = f"{score_brut * 100:.1f}%"

        response_payload = {
            "decision": decision,
            "confiance": confiance,
            "score_brut": round(score_brut, 3),
            "donnees_reçues": cleaned_data,
        }

        history_entry = build_history_entry(cleaned_data, decision, confiance)
        append_history_entry(history_entry)

        return jsonify(response_payload)

    except Exception as exc:
        return (
            jsonify(
                {
                    "erreur": "Erreur interne pendant la prédiction",
                    "details": str(exc),
                }
            ),
            500,
        )


@app.get("/statistiques")
def statistiques() -> Any:
    try:
        stats = compute_dataset_statistics(DATASET_PATH)
        return jsonify(stats)
    except Exception as exc:
        return (
            jsonify(
                {
                    "erreur": "Impossible de calculer les statistiques",
                    "details": str(exc),
                }
            ),
            500,
        )


@app.get("/historique")
def historique() -> Any:
    try:
        entries = read_recent_history(limit=10)
        return jsonify({"historique": entries, "total_retourne": len(entries)})
    except Exception as exc:
        return (
            jsonify(
                {
                    "erreur": "Impossible de lire l'historique",
                    "details": str(exc),
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
