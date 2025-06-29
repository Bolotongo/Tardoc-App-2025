import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="TARDOC Abrechnungshelfer", layout="wide")

# Passwortschutz
st.title("🔒 Zugang geschützt")
password = st.text_input("Bitte Passwort eingeben:", type="password")
if password != "tardoc2025":
    st.warning("Zugang nur mit gültigem Passwort.")
    st.stop()

st.title("🔧 TARDOC Abrechnungshelfer inkl. smarter Blocklogik & Mehrfachauswahl")

EXCEL_PATH = "tardoc_1.4b.xlsx"
if os.path.exists(EXCEL_PATH):
    uploaded_file = EXCEL_PATH
else:
    uploaded_file = st.file_uploader("Lade die TARDOC-Excel-Datei hoch", type=[".xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Tarifpositionen", skiprows=4)
        df.columns = df.columns.str.strip()

        df = df.rename(columns={
            df.columns[0]: "L-Nummer",
            df.columns[1]: "Bezeichnung",
            df.columns[2]: "Leistungstitel",
            df.columns[3]: "Interpretation",
            df.columns[4]: "AL (normiert)",
            df.columns[5]: "IPL (normiert)",
            df.columns[6]: "Qualitative Dignität",
            df.columns[7]: "Pflichtleistung",
            df.columns[8]: "Typ",
            df.columns[16]: "Tarifmechanik Regeln"
        })

        df = df.dropna(subset=["Leistungstitel"]).drop_duplicates()

        tab1, tab2, tab3 = st.tabs(["🔽 Dropdown", "🔍 Freitextsuche", "✅ Mehrfachauswahl"])

        selected = None

        with tab1:
            option = st.selectbox(
                "Wähle eine Leistung:",
                ["Bitte auswählen"] + list(df["Leistungstitel"].dropna().unique()),
                help="Die Blocklogik-Hinweise erscheinen direkt darunter."
            )
            if option != "Bitte auswählen":
                filtered = df[df["Leistungstitel"] == option]
                if not filtered.empty:
                    selected = filtered.iloc[0]

        with tab2:
            query = st.text_input("Suche Freitext:")
            if query:
                query_lower = query.lower()
                filtered = df[df.apply(lambda row:
                    query_lower in str(row["L-Nummer"]).lower()
                    or query_lower in str(row["Leistungstitel"]).lower()
                    or query_lower in str(row["Bezeichnung"]).lower()
                    or query_lower in str(row["Interpretation"]).lower(), axis=1)]
                if not filtered.empty:
                    selected = filtered.iloc[0]

        if selected is not None:
            st.subheader("📄 Details zur ausgewählten Position")
            for key in ["L-Nummer", "Leistungstitel", "Bezeichnung", "Interpretation", "AL (normiert)", "IPL (normiert)", "Qualitative Dignität", "Pflichtleistung", "Typ"]:
                st.markdown(f"**{key}:** {selected.get(key, '')}")
            st.markdown(f"**Regeln:** {selected.get('Tarifmechanik Regeln', '')}")

            regeln = str(selected.get('Tarifmechanik Regeln', '')).lower()
            st.subheader("📌 Blocklogik Hinweise:")
            if "nicht kumulierbar" in regeln:
                st.warning("⚠️ Diese Leistung ist laut Regeln nicht kumulierbar.")
            if "nur zusammen mit" in regeln:
                st.info("ℹ️ Nur zusammen mit anderen Positionen abrechnen.")
            if "pflichtleistung" in regeln or "obligatorisch" in regeln:
                st.success("✅ Pflichtleistung laut Regeln.")
            if not any(x in regeln for x in ["nicht kumulierbar", "nur zusammen mit", "pflichtleistung", "obligatorisch"]):
                st.info("ℹ️ Keine speziellen Blocklogik-Hinweise vorhanden.")

        with tab3:
            auswahl = st.multiselect(
                "Wähle mehrere Positionen:",
                df["Leistungstitel"].dropna().unique()
            )
            if auswahl:
                df_selected = df[df["Leistungstitel"].isin(auswahl)]