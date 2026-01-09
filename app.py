# app.py
from __future__ import annotations

from datetime import datetime
import uuid

import pandas as pd
import streamlit as st

from storage import load_consos, add_conso, delete_conso

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


DRINK_TYPES = ["Bière", "Ricard", "Rhum", "Vodka", "Tequilla", "Vin", "Whisky", "Shot", "Cocktail", "Autre"]
NAMES = ["Divers Inconnus", "Damien", "Eliott", "Elwenn", "Gaetan", "Jeanne", "Jules", "Marie", "Mattis", "Maude", "Quentin"]

DOSES = {
    "2 cl (mini shot)": 20,
    "5 cl (shot)": 50,
    "10 cl": 100,
    "12.5 cl (vin)": 125,
    "20 cl": 200,
    "25 cl": 250,
    "33 cl": 330,
    "50 cl": 500,
    "1 L": 1000,
}
NB_OPTIONS = list(range(1, 11))

# Emojis par boisson (simple)
DRINK_EMOJI = {
    "Bière": "🍺",
    "Ricard": "🟨",
    "Rhum": "🥃",
    "Vodka": "🧊",
    "Tequilla": "🌵",
    "Vin": "🍷",
    "Whisky": "🥃",
    "Shot": "🎯",
    "Cocktail": "🍸",
    "Autre": "🍶",
}

def with_emoji(drink: str) -> str:
    return f"{DRINK_EMOJI.get(drink, '🍻')} {drink}"

st.set_page_config(page_title="Compteur de boissons", page_icon="🍻", layout="centered")

# Un peu de CSS (léger) : centrer tables + card total
st.markdown(
    """
    <style>
    .stDataFrame td, .stDataFrame th { text-align: center !important; }
    .total-card{
        padding: 16px 18px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.03);
        margin: 10px 0 16px 0;
    }
    .total-title{opacity:0.85; font-size: 14px; margin-bottom: 6px;}
    .total-value{font-size: 34px; font-weight: 800; line-height: 1.1;}
    .total-sub{opacity:0.75; font-size: 13px; margin-top: 4px;}
    </style>

    """,
    unsafe_allow_html=True,
)

st.title("🍻 No Rizz Boisson Club")
st.caption("C'est un jeu dangereux... Mais c'est un jeu qui me plaît")

# --- Charger données (simple et robuste)
consos = load_consos()
df = pd.DataFrame(consos)

for col in ["id", "date", "nom", "boisson", "nb", "dose_ml", "volume_l"]:
    if col not in df.columns:
        df[col] = None

if not df.empty:
    df["nb"] = pd.to_numeric(df["nb"], errors="coerce").fillna(0).astype(int)
    df["dose_ml"] = pd.to_numeric(df["dose_ml"], errors="coerce").fillna(0).astype(int)
    df["volume_l"] = pd.to_numeric(df["volume_l"], errors="coerce")
    df["volume_l"] = df["volume_l"].fillna((df["nb"] * df["dose_ml"]) / 1000.0)
    df = df.sort_values("date", ascending=False)

# --- Onglets
tab_add, tab_hist, tab_rank, tab_stats, tab_del = st.tabs(
    ["➕ Ajouter", "📜 Historique", "🏆 Classement", "📈 Statistiques", "🗑️ Supprimer"]
)

# ==============
# TAB : AJOUTER
# ==============
with tab_add:
    st.subheader("Ajouter une consommation")

    with st.form("add_conso", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.selectbox("Nom", NAMES)
        with col2:
            boisson = st.selectbox("Boisson", DRINK_TYPES, format_func=with_emoji)

        col3, col4 = st.columns(2)
        with col3:
            nb = st.selectbox("Nombre", NB_OPTIONS, index=0)
        with col4:
            dose_label = st.selectbox("Dose", list(DOSES.keys()), index=5)  # 25cl par défaut (selon ta liste)
            dose_ml = DOSES[dose_label]

        volume_l = (int(nb) * int(dose_ml)) / 1000.0

        submitted = st.form_submit_button("➕ Ajouter")

        if submitted:
            new_item = {
                "id": str(uuid.uuid4()),
                "date": datetime.now().date().isoformat(),
                "nom": nom,
                "boisson": boisson,
                "nb": int(nb),
                "dose_ml": int(dose_ml),
                "volume_l": float(volume_l),
            }
            add_conso(new_item)
            st.success(f"Ajouté : {nom} • {with_emoji(boisson)} • {nb} × {dose_label} = {volume_l:.2f} L")
            st.stop()

# ==================
# TAB : HISTORIQUE
# ==================
with tab_hist:
    st.subheader("Historique des consommations")

    if df.empty:
        st.info("Aucune consommation enregistrée pour le moment.")
    else:
        df_hist = df.copy()

        # Affichage joli
        df_hist["Boisson"] = df_hist["boisson"].map(with_emoji)
        df_hist["Dose"] = (df_hist["dose_ml"] / 10).round(0).astype(int).astype(str) + " cl"
        df_hist["Volume"] = df_hist["volume_l"].round(2).map(lambda x: f"{x:.2f} L")
        df_hist["Nombre"] = df_hist["nb"].astype(int)

        df_hist = df_hist.rename(columns={"date": "Date", "nom": "Nom"})

        st.dataframe(
            df_hist[["Date", "Nom", "Boisson", "Nombre", "Dose", "Volume"]],
            use_container_width=True,
            hide_index=True,
        )

# ==================
# TAB : CLASSEMENT
# ==================
with tab_rank:
    st.subheader("Classement des pochtrons")

    selected_drink = st.selectbox(
        "Filtrer par type de boisson",
        ["all"] + DRINK_TYPES,
        index=0,
        format_func=lambda x: "🍻 all" if x == "all" else with_emoji(x),
    )

    if df.empty:
        st.info("Aucune consommation enregistrée pour le moment.")
    else:
        df_stats = df if selected_drink == "all" else df[df["boisson"] == selected_drink]

        if df_stats.empty:
            st.info("Aucune donnée pour ce type de boisson.")
        else:
            total = float(df_stats["volume_l"].sum())
            subtitle = "Toutes boissons confondues" if selected_drink == "all" else f"{with_emoji(selected_drink)}"

            # Total plus visuel
            st.markdown(
                f"""
                <div class="total-card">
                  <div class="total-title">Total consommé — {subtitle}</div>
                  <div class="total-value">{total:.2f} L</div>
                    <div class="total-sub">(depuis le 09/01/2026)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            by_name = (
                df_stats.groupby("nom", as_index=False)["volume_l"]
                .sum()
                .sort_values("volume_l", ascending=False)
            )

            st.markdown("### 🏆 Top 3")
            top3 = by_name.head(3)

            cols = st.columns(3)
            for i, (_, row) in enumerate(top3.iterrows()):
                with cols[i]:
                    st.metric(label=f"#{i+1} {row['nom']}", value=f"{float(row['volume_l']):.2f} L")

            st.markdown("### 📊 Classement complet")
            max_val = float(by_name["volume_l"].max()) if not by_name.empty else 1.0

            for _, row in by_name.iterrows():
                name = row["nom"]
                val = float(row["volume_l"])
                st.write(f"**{name}** — {val:.2f} L")
                st.progress(min(val / max_val, 1.0))

# =====================
# TAB : STATISTIQUES
# =====================
with tab_stats:
    st.subheader("Statistiques")

    if df.empty:
        st.info("Pas de données pour afficher des statistiques.")
    else:
        # Préparation dates
        df_plot = df.copy()
        df_plot["date"] = pd.to_datetime(df_plot["date"], errors="coerce")
        df_plot = df_plot.dropna(subset=["date"])
        df_plot["day"] = df_plot["date"].dt.date

# ===========
# 1) Cumul total par jour (du 09/01/2026 à la dernière conso)
# ===========
    st.markdown("### 📈 Volume total cumulé (L) par jour")

    df_plot = df.copy()
    df_plot["date"] = pd.to_datetime(df_plot["date"], errors="coerce")
    df_plot = df_plot.dropna(subset=["date"])
    df_plot["day"] = df_plot["date"].dt.date

    fixed_start = datetime(2026, 1, 9).date()
    # On veut aller jusqu'à la dernière date où il y a une consommation
    last_day = df_plot["day"].max()

    if pd.isna(last_day) or last_day < fixed_start:
        st.info("Pas encore de consommations depuis le 09/01/2026.")
    else:
        # Total par jour
        daily_total = (
            df_plot.groupby("day", as_index=False)["volume_l"]
            .sum()
            .sort_values("day")
        )
        # Crée tous les jours entre fixed_start et last_day
        all_days = pd.date_range(start=fixed_start, end=last_day, freq="D").date

        # Ajoute les jours sans conso à 0
        daily_total = daily_total.set_index("day").reindex(all_days, fill_value=0.0).reset_index()
        daily_total = daily_total.rename(columns={"index": "day"})

        # Cumul
        daily_total["cumul_l"] = daily_total["volume_l"].cumsum()

        # Plot
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(111)
        x = pd.to_datetime(daily_total["day"])
        y = daily_total["cumul_l"]

        ymax = float(y.max()) if len(y) else 0.0
        ax1.set_ylim(0, ymax * 1.05 if ymax > 0 else 1)


        ax1.plot(x, y)
        ax1.set_ylabel("Litres (cumul)")
        ax1.set_xlabel("Date")
        # Affichage intelligent des dates (au fil des jours -> plus on avance, plus on agrège)
        days_range = (pd.to_datetime(last_day) - pd.to_datetime(fixed_start)).days

        if days_range <= 31:
            locator = mdates.DayLocator(interval=2)
            formatter = mdates.DateFormatter("%d/%m")
        elif days_range <= 120:
            locator = mdates.WeekdayLocator(interval=1)
            formatter = mdates.DateFormatter("%d/%m")
        else:
            locator = mdates.MonthLocator(interval=1)
            formatter = mdates.DateFormatter("%b %Y")

        ax1.xaxis.set_major_locator(locator)
        ax1.xaxis.set_major_formatter(formatter)
        fig1.autofmt_xdate()

        st.pyplot(fig1, clear_figure=True)

        # ===========
        # 2) Courbes par personne (filtre boisson + période + sélection)
        # ===========
        st.markdown("### 👥 Consommation par personne (L/jour)")

        colA, colB = st.columns(2)
        with colA:
            drink_choice = st.selectbox(
                "Boisson",
                ["all"] + DRINK_TYPES,
                index=0,
                format_func=lambda x: "🍻 all" if x == "all" else with_emoji(x),
            )
        with colB:
            period_choice = st.selectbox(
                "Période",
                ["7 derniers jours", "1 mois", "3 mois", "6 mois", "1 an"],
                index=1,
            )

        period_map = {
            "7 derniers jours": 7,
            "1 mois": 30,
            "3 mois": 90,
            "6 mois": 180,
            "1 an": 365,
        }
        days_back = period_map[period_choice]

        names_available = sorted(df_plot["nom"].dropna().unique().tolist())
        selected_names = st.multiselect(
            "Sélectionne les personnes à afficher",
            names_available,
            default=names_available[:3] if len(names_available) >= 3 else names_available,
        )

        if not selected_names:
            st.info("Sélectionne au moins une personne.")
        else:
            # Filtre boisson
            df2 = df_plot.copy()
            if drink_choice != "all":
                df2 = df2[df2["boisson"] == drink_choice]

            # Filtre période
            today = datetime.now().date()
            start_date = today - pd.Timedelta(days=days_back - 1)
            df2 = df2[df2["day"] >= start_date]

            # Filtre personnes
            df2 = df2[df2["nom"].isin(selected_names)]

            if df2.empty:
                st.info("Aucune donnée sur cette période / filtre.")
            else:
                # Série journalière par personne (jours manquants = 0)
                date_index = pd.date_range(start=start_date, end=today, freq="D").date
                daily_people = (
                    df2.groupby(["day", "nom"], as_index=False)["volume_l"]
                    .sum()
                )

                pivot = daily_people.pivot(index="day", columns="nom", values="volume_l").reindex(date_index, fill_value=0.0)

                fig2 = plt.figure()
                ax2 = fig2.add_subplot(111)

                x = pd.to_datetime(pivot.index)
                for name in selected_names:
                    if name in pivot.columns:
                        ax2.plot(x, pivot[name], label=name)

                ax2.set_ylabel("Litres par jour")
                ax2.set_xlabel("Date")
                ax2.legend()

                locator2 = mdates.AutoDateLocator()
                formatter2 = mdates.ConciseDateFormatter(locator2)
                ax2.xaxis.set_major_locator(locator2)
                ax2.xaxis.set_major_formatter(formatter2)

                st.pyplot(fig2, clear_figure=True)

# ==================
# TAB : SUPPRIMER
# ==================
with tab_del:
    st.subheader("Retirer une consommation (supprimer une ligne)")

    if df.empty:
        st.caption("Rien à supprimer.")
    else:
        # sécurisation pour affichage
        df_del = df.copy()
        df_del["nb"] = df_del["nb"].fillna(0).astype(int)
        df_del["dose_ml"] = df_del["dose_ml"].fillna(0).astype(int)
        df_del["volume_l"] = df_del["volume_l"].fillna(0.0).astype(float)

        labels = (
            df_del["date"].astype(str)
            + " — " + df_del["nom"].astype(str)
            + " — " + df_del["boisson"].map(with_emoji).astype(str)
            + " — " + df_del["nb"].astype(str)
            + " × " + df_del["dose_ml"].astype(str) + "ml"
            + " (" + df_del["volume_l"].round(2).astype(str) + "L)"
        ).tolist()

        id_map = dict(zip(labels, df_del["id"].tolist()))

        selected = st.selectbox("Sélectionne une ligne à supprimer", labels)

        if st.button("🗑️ Supprimer", type="secondary"):
            target_id = id_map[selected]
            delete_conso(target_id)
            st.success("Ligne supprimée.")
            st.rerun()
