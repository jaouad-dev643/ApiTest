from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "credit_dataset.csv"
MODEL_PATH = BASE_DIR / "model.pkl"

NUMERICAL_COLUMNS = [
    "age",
    "revenu_mensuel",
    "montant_credit_demande",
    "duree_remboursement_mois",
    "nb_credits_anterieurs",
]

CATEGORICAL_COLUMNS = ["situation_familiale", "type_emploi"]
TARGET_COLUMN = "decision"


def load_dataset(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Fichier dataset introuvable: {csv_path}")

    dataframe = pd.read_csv(csv_path)
    return dataframe


def display_dataset_summary(dataframe: pd.DataFrame) -> None:
    print("\n=== Résumé du dataset ===")
    print(f"Shape: {dataframe.shape}")
    print("\nAperçu (head):")
    print(dataframe.head())
    print("\nDistribution de la cible 'decision':")
    print(dataframe[TARGET_COLUMN].value_counts(dropna=False))


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERICAL_COLUMNS),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLUMNS),
        ]
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def train_and_evaluate(dataframe: pd.DataFrame) -> Pipeline:
    required_columns = set(NUMERICAL_COLUMNS + CATEGORICAL_COLUMNS + [TARGET_COLUMN])
    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Colonnes manquantes dans le dataset: {missing}")

    x = dataframe[NUMERICAL_COLUMNS + CATEGORICAL_COLUMNS]
    y = dataframe[TARGET_COLUMN]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)

    y_pred = pipeline.predict(x_test)
    accuracy = accuracy_score(y_test, y_pred)

    print("\n=== Évaluation du modèle ===")
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification report:")
    print(classification_report(y_test, y_pred))

    return pipeline


def save_model(model_pipeline: Pipeline, model_path: Path) -> None:
    with model_path.open("wb") as model_file:
        pickle.dump(model_pipeline, model_file)
    print(f"\nModèle sauvegardé avec succès dans: {model_path}")


def main() -> None:
    try:
        dataframe = load_dataset(DATASET_PATH)
        display_dataset_summary(dataframe)
        trained_pipeline = train_and_evaluate(dataframe)
        save_model(trained_pipeline, MODEL_PATH)
    except Exception as exc:
        print(f"\nErreur pendant l'entraînement: {exc}")


if __name__ == "__main__":
    main()
