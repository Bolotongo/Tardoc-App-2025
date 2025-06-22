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

st.title("🔧 TARDOC Abrechnungshelfer für Ärzt:innen")

# Versuche, Datei direkt aus Projektverzeichnis zu laden
EXCEL_PATH = "tardoc_1.4b.xlsx"  # Datei im selben Verzeichnis wie app.py erwartet

if os.path.exists(EXCEL_PATH):
    uploaded_file = EXCEL_PATH
else:
    uploaded_file = st.file_uploader("Lade die TARDOC-Excel-Datei hoch (z. B. Version 1.4b)", type=[".xlsx"])

if uploaded_file:
    try:
        # Lade Daten aus dem richtigen Tabellenblatt, ab Zeile 5
        df = pd.read_excel(uploaded_file, sheet_name="Tarifpositionen", skiprows=4)
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

        # Bereinige Daten
        df = df.dropna(subset=["Leistungstitel"]).drop_duplicates()

        # Tabs: Dropdown oder Freitextsuche
        tab1, tab2 = st.tabs(["🔽 Dropdown-Auswahl", "🔍 Freitextsuche"])

        with tab1:
            option = st.selectbox("Wähle eine Leistung aus:", df["Leistungstitel"].unique())
            result = df[df["Leistungstitel"] == option].iloc[0]

        with tab2:
            query = st.text_input("Suche nach L-Nummer oder Begriff (z. B. AA.00 oder Konsultation):")
            if query:
                query_lower = query.lower()
                filtered = df[df.apply(lambda row:
                    query_lower in str(row["L-Nummer"]).lower()
                    or query_lower in str(row["Leistungstitel"]).lower()
                    or query_lower in str(row["Bezeichnung"]).lower()
                    or query_lower in str(row["Interpretation"]).lower(), axis=1)]
            else:
                filtered = pd.DataFrame()

            if not filtered.empty:
                result = filtered.iloc[0]
            else:
                result = None

        if result is not None:
            st.subheader("📄 Details zur Tarifposition")
            st.markdown(f"**L-Nummer:** {result['L-Nummer']}")
            st.markdown(f"**Bezeichnung:** {result['Bezeichnung']}")
            st.markdown(f"**Interpretation:** {result['Interpretation']}")
            st.markdown(f"**AL (normiert):** {result['AL (normiert)']}")
            st.markdown(f"**IPL (normiert):** {result['IPL (normiert)']}")
            st.markdown(f"**Qualitative Dignität:** {result['Qualitative Dignität']}")
            st.markdown(f"**Pflichtleistung:** {result['Pflichtleistung']}")
            st.markdown(f"**Typ:** {result['Typ']}")
            st.markdown(f"**Regeln:** {result['Tarifmechanik Regeln']}")
        else:
            if query:
                st.warning("Keine passende Tarifposition gefunden.")

    except Exception as e:
        st.error(f"Fehler beim Einlesen der Datei: {e}")
else:
    st.info("Bitte lade eine Excel-Datei im TARDOC-Format hoch oder speichere sie als 'tardoc_1.4b.xlsx' im App-Verzeichnis.")
