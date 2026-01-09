#app.py 

# app.py
from __future__ import annotations

from datetime import datetime
import uuid

import pandas as pd
import streamlit as st

from storage import load_consos, add_conso, delete_conso



DRINK_TYPES = ["Bière", "Cocktail", "Shot", "Vin"]
NAMES = ["Divers Inconnus", "Damien", "Eliott", "Elwenn", "Gaetan", "Jeanne", "Jules", "Marie", "Mattis", "Maude", "Quentin"]



st.set_page_config(page_title="Compteur de boissons", page_icon="🍻", layout="centered")

st.title("🍻 Compteur de boissons")
st.caption("MVP : ajout / retrait de consommations + stockage persistant (multi-soirées).")

# --- Charger données
consos = load_consos()
df = pd.DataFrame(consos)

# garantit les colonnes même si df est vide ou si l'ancien JSON n'a pas tout
for col in ["id", "date", "nom", "boisson", "quantite"]:
    if col not in df.columns:
        df[col] = []

# tri simple (YYYY-MM-DD)
if not df.empty:
    df = df.sort_values("date", ascending=False)


# --- Formulaire d'ajout
st.subheader("Ajouter une consommation")

with st.form("add_conso", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        nom = st.selectbox("Nom", NAMES)
    with col2:
        boisson = st.selectbox("Boisson", DRINK_TYPES)

    quantite = st.number_input("Quantité", min_value=1, max_value=50, value=1, step=1)

    submitted = st.form_submit_button("➕ Ajouter")

    if submitted:
        nom_clean = nom
        new_item = {
            "id": str(uuid.uuid4()),
            "date" : datetime.now().date().isoformat(),
            "nom": nom_clean,
            "boisson": boisson,
            "quantite": int(quantite),
        }
        add_conso(new_item)
        st.success(f"Ajouté : {nom_clean} • {boisson} • +{int(quantite)}")
        st.rerun()

st.divider()

# --- Affichage tableau
st.subheader("Historique des consommations")

if df.empty:
    st.info("Aucune consommation enregistrée pour le moment.")
else:
    st.dataframe(
        df[["date", "nom", "boisson", "quantite"]],
        use_container_width=True,
        hide_index=True,
    )

    # Totaux rapides
st.subheader("Classement par nom")

selected_drink = st.selectbox("Filtrer par type de boisson", ["all"] + DRINK_TYPES, index=0)

if df.empty:
    st.info("Aucune consommation enregistrée pour le moment.")
else:
    df_stats = df if selected_drink == "all" else df[df["boisson"] == selected_drink]

    if df_stats.empty:
        st.info("Aucune donnée pour ce type de boisson.")
    else:
        total = int(df_stats["quantite"].sum())
        st.metric("Total (filtre actuel)", total)

        by_name = (
            df_stats.groupby("nom", as_index=False)["quantite"]
            .sum()
            .sort_values("quantite", ascending=False)
        )
        st.dataframe(by_name, use_container_width=True, hide_index=True)



# --- Retrait simple (supprimer une ligne)
st.subheader("Retirer une consommation (supprimer une ligne)")

if df.empty:
    st.caption("Rien à supprimer.")
else:
    labels = (df["date"] + " — " + df["nom"] + " — " + df["boisson"] + " — " + df["quantite"].astype(str)).tolist()
    id_map = dict(zip(labels, df["id"].tolist()))

    selected = st.selectbox("Sélectionne une ligne à supprimer", labels)

    if st.button("🗑️ Supprimer", type="secondary"):
        target_id = id_map[selected]
        consos2 = [c for c in consos if c.get("id") != target_id]
        delete_conso(target_id)
        st.success("Ligne supprimée.")
        st.rerun()