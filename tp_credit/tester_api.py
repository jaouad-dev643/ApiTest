from __future__ import annotations

import json

import requests


API_URL = "http://127.0.0.1:5000/predire"


EXEMPLES = [
    {
        "label": "Cas probable ACCORDÉ",
        "payload": {
            "age": 36,
            "revenu_mensuel": 12500,
            "montant_credit_demande": 95000,
            "duree_remboursement_mois": 36,
            "nb_credits_anterieurs": 1,
            "situation_familiale": "marie",
            "type_emploi": "fonctionnaire",
        },
    },
    {
        "label": "Cas probable REFUSÉ",
        "payload": {
            "age": 24,
            "revenu_mensuel": 2800,
            "montant_credit_demande": 140000,
            "duree_remboursement_mois": 96,
            "nb_credits_anterieurs": 3,
            "situation_familiale": "celibataire",
            "type_emploi": "sans_emploi",
        },
    },
]


def test_api() -> None:
    for exemple in EXEMPLES:
        print(f"\n=== {exemple['label']} ===")
        try:
            response = requests.post(API_URL, json=exemple["payload"], timeout=8)
            print(f"Status code: {response.status_code}")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except requests.exceptions.ConnectionError:
            print("Erreur de connexion: l'API Flask semble arrêtée.")
            print("Démarrez d'abord l'API avec: python app.py")
            break
        except requests.exceptions.RequestException as exc:
            print(f"Erreur pendant l'appel API: {exc}")


if __name__ == "__main__":
    test_api()
