from __future__ import annotations

import requests
import streamlit as st


API_BASE_URL = "http://127.0.0.1:5000"


def call_get(endpoint: str, timeout: int = 5) -> tuple[dict, str | None]:
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=timeout)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as exc:
        return {}, str(exc)


def call_post(endpoint: str, payload: dict, timeout: int = 10) -> tuple[dict, str | None, int | None]:
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=payload, timeout=timeout)
        status_code = response.status_code
        body = response.json()
        if response.ok:
            return body, None, status_code
        return body, body.get("erreur", "Erreur API"), status_code
    except requests.exceptions.RequestException as exc:
        return {}, str(exc), None


def render_decision(result: dict) -> None:
    decision = result.get("decision", "INCONNUE")
    confiance = result.get("confiance", "0.0%")
    score_brut = float(result.get("score_brut", 0.0))

    if decision == "ACCORDÉ":
        st.success(f"Décision: {decision}")
    else:
        st.error(f"Décision: {decision}")

    st.metric("Confiance", confiance)
    st.progress(min(max(score_brut, 0.0), 1.0))


def render_statistiques() -> None:
    stats, error = call_get("/statistiques")
    st.subheader("Statistiques du dataset")

    if error:
        st.warning(f"Impossible de charger les statistiques: {error}")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total demandes", stats.get("nombre_total_demandes", 0))
    col2.metric("Accordées", stats.get("nombre_demandes_accordees", 0))
    col3.metric("Refusées", stats.get("nombre_demandes_refusees", 0))
    col4.metric("Taux d'accord", f"{stats.get('taux_accord', 0)}%")

    col5, col6, col7 = st.columns(3)
    col5.metric("Revenu moyen (accordés)", f"{stats.get('revenu_moyen_accordes', 0)} MAD")
    col6.metric("Revenu moyen (refusés)", f"{stats.get('revenu_moyen_refuses', 0)} MAD")
    col7.metric("Montant moyen demandé", f"{stats.get('montant_moyen_demande', 0)} MAD")

    st.write("Répartition par type d'emploi")
    repartition = stats.get("repartition_par_type_emploi", {})
    if repartition:
        st.bar_chart(repartition)
    else:
        st.info("Aucune donnée de répartition disponible.")


def render_historique() -> None:
    st.subheader("Historique récent")
    history_data, error = call_get("/historique")
    if error:
        st.warning(f"Impossible de charger l'historique: {error}")
        return

    historique = history_data.get("historique", [])
    if not historique:
        st.info("Aucune prédiction enregistrée pour le moment.")
        return

    for entry in historique:
        decision = entry.get("decision", "INCONNUE")
        icon = "✅" if decision == "ACCORDÉ" else "❌"
        with st.expander(f"{icon} {entry.get('timestamp', 'N/A')} — {decision}"):
            st.write(f"Confiance: {entry.get('confiance', 'N/A')}")
            st.json(entry.get("donnees_recues", {}))


def main() -> None:
    st.set_page_config(page_title="Analyse de crédit", layout="wide")

    st.title("Plateforme intelligente d’analyse de crédit")
    st.caption("Prototype bancaire marocain — Flask + Machine Learning")

    with st.sidebar:
        st.header("Panneau API")
        if st.button("Vérifier l’API"):
            response, error = call_get("/")
            if error:
                st.error("API indisponible")
                st.caption(error)
            else:
                st.success(response.get("message", "API disponible"))

        if st.button("Voir statistiques"):
            stats, error = call_get("/statistiques")
            if error:
                st.error(f"Erreur: {error}")
            else:
                st.json(stats)

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("Nouvelle demande de crédit")
        with st.form("credit_form"):
            age = st.number_input("Âge", min_value=18, max_value=80, value=30, step=1)
            revenu = st.number_input("Revenu mensuel (MAD)", min_value=0.0, value=8000.0, step=100.0)
            montant = st.number_input("Montant demandé (MAD)", min_value=0.0, value=100000.0, step=1000.0)
            duree = st.number_input("Durée de remboursement (mois)", min_value=6, max_value=120, value=36, step=1)
            nb_credits = st.number_input("Nombre de crédits antérieurs", min_value=0, value=0, step=1)
            situation = st.selectbox("Situation familiale", ["celibataire", "marie", "divorce"])
            emploi = st.selectbox(
                "Type d’emploi",
                ["salarie_prive", "fonctionnaire", "independant", "sans_emploi"],
            )

            submit = st.form_submit_button("Soumettre la demande")

        if submit:
            payload = {
                "age": int(age),
                "revenu_mensuel": float(revenu),
                "montant_credit_demande": float(montant),
                "duree_remboursement_mois": int(duree),
                "nb_credits_anterieurs": int(nb_credits),
                "situation_familiale": situation,
                "type_emploi": emploi,
            }

            with st.spinner("Analyse en cours..."):
                result, error, status = call_post("/predire", payload)

            if error:
                st.error(f"Erreur API ({status if status else 'N/A'}): {error}")
                if result:
                    st.json(result)
            else:
                render_decision(result)
                st.write("Données envoyées")
                st.json(result.get("donnees_reçues", payload))

    with col_right:
        render_statistiques()

    st.divider()
    render_historique()


if __name__ == "__main__":
    main()
