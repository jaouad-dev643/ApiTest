# Plateforme intelligente d'analyse de crédit (Prototype bancaire marocain)

## 1) Contexte métier

Dans ce prototype, une banque marocaine souhaite automatiser le pré-traitement des demandes de crédit pour gagner du temps, homogénéiser les décisions et assister les conseillers dans l'analyse initiale.

## 2) Objectif du projet

Cette mini-plateforme locale permet de :
- entraîner un modèle de Machine Learning sur un dataset de demandes de crédit ;
- exposer une API Flask de scoring (`ACCORDÉ` / `REFUSÉ`) ;
- utiliser une interface Streamlit moderne pour les utilisateurs non techniques ;
- conserver un historique local des prédictions ;
- valider robustement les données entrantes.

## 3) Architecture

```bash
tp_credit/
├── credit_dataset.csv
├── train_model.py
├── app.py
├── interface.py
├── tester_api.py
├── requirements.txt
├── README.md
├── model.pkl                    # généré après entraînement
├── historique_predictions.json
└── utils/
    ├── __init__.py
    ├── validation.py
    └── helpers.py
```

## 4) Dépendances

Le projet utilise :
- Python 3.11+
- Flask
- pandas
- scikit-learn
- Streamlit
- requests
- pickle (bibliothèque standard)

## 5) Installation

Depuis le dossier `tp_credit` :

```bash
pip install -r requirements.txt
```

## 6) Entraîner le modèle

Le script d'entraînement :
- charge `credit_dataset.csv` ;
- affiche un résumé du dataset ;
- prépare les variables numériques et catégorielles ;
- entraîne un pipeline (`ColumnTransformer` + `RandomForestClassifier`) ;
- affiche `accuracy_score` et `classification_report` ;
- sauvegarde le modèle dans `model.pkl`.

Commande :

```bash
python train_model.py
```

## 7) Lancer l'API Flask

Commande :

```bash
python app.py
```

API disponible sur : `http://127.0.0.1:5000`

## 8) Lancer l'interface Streamlit

Commande :

```bash
streamlit run interface.py
```

L'interface permet :
- saisie d'une demande ;
- affichage de la décision et de la confiance ;
- visualisation des statistiques dataset ;
- affichage de l'historique récent.

## 9) Tester l'API côté client

Commande :

```bash
python tester_api.py
```

Le script envoie 2 exemples (accord probable / refus probable) vers `/predire`.

## 10) Routes disponibles

### `GET /`
Retourne l'état de l'API et les routes exposées.

### `GET /demo`
Retourne des exemples de payload JSON.

### `POST /predire`
Analyse une demande et retourne :

```json
{
  "decision": "ACCORDÉ",
  "confiance": "92.4%",
  "score_brut": 0.924,
  "donnees_reçues": {
    "age": 35,
    "revenu_mensuel": 12000.0,
    "montant_credit_demande": 90000.0,
    "duree_remboursement_mois": 36,
    "nb_credits_anterieurs": 1,
    "situation_familiale": "marie",
    "type_emploi": "fonctionnaire"
  }
}
```

En cas d'erreurs de validation :

```json
{
  "erreur": "Validation échouée",
  "details": {
    "age": "L’âge doit être compris entre 18 et 80",
    "type_emploi": "Valeur invalide"
  }
}
```

### `GET /statistiques`
Retourne un JSON avec indicateurs globaux du dataset (volumétrie, taux d'accord/refus, moyennes, répartition emploi).

### `GET /historique`
Retourne les 10 dernières prédictions enregistrées dans `historique_predictions.json`.

## 11) Validation des données

La validation se trouve dans `utils/validation.py` et contrôle :
- `age` : entier entre 18 et 80
- `revenu_mensuel` : nombre > 0
- `montant_credit_demande` : nombre > 0
- `duree_remboursement_mois` : entier entre 6 et 120
- `nb_credits_anterieurs` : entier >= 0
- `situation_familiale` : `celibataire`, `marie`, `divorce`
- `type_emploi` : `salarie_prive`, `fonctionnaire`, `independant`, `sans_emploi`

## 12) Pistes d'amélioration

- ajout d'authentification et de journalisation avancée ;
- entraînement sur un dataset plus riche et réel ;
- calibration des probabilités et interprétabilité du modèle ;
- conteneurisation (Docker) ;
- ajout de tests unitaires et CI/CD.
