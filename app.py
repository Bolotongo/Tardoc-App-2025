import streamlit as st
import pandas as pd
import openai
import os

st.set_page_config(page_title="TARDOC Abrechnungshelfer", layout="wide")

openai.api_key = st.secrets.get("OPENAI_API_KEY", "DEIN_KEY_HIER")

EXCEL_PATH = "tardoc_1.4b.xlsx"
if os.path.exists(EXCEL_PATH):
    uploaded_file = EXCEL_PATH
else:
    uploaded_file = st.file_uploader("Lade die TARDOC-Excel-Datei hoch", type=[".xlsx"])

if uploaded_file:
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
    }).dropna(subset=["Leistungstitel"]).drop_duplicates()

    tab1, tab2, tab3, tab4 = st.tabs(["🧭 GPT-KI", "🔽 Dropdown", "🔍 Freitextsuche", "✅ Mehrfachauswahl"])

    with tab1:
        st.markdown("""
            <div style='text-align: center;'>
                <img src='https://media.giphy.com/media/3ov9k7jQXQ2FznhkCs/giphy.gif' width='150'>
                <p style='font-size: 18px;'>Hi, ich bin <strong>NaviDoc</strong> – dein animierter Kompass-Helfer!</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("### 👋 Ich helfe dir bei TARDOC-Fragen.")
        user_input = st.text_area("Beschreibe deine Leistung", height=200)
        if st.button("KI befragen") and user_input:
            with st.spinner("NaviDoc denkt nach..."):
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Du bist ein TARDOC-Abrechnungshelfer. Suche passende L-Nummern und erkläre sie."},
                        {"role": "user", "content": user_input}
                    ]
                )
                answer = response.choices[0].message["content"]
                st.success("💡 Vorschlag der KI:")
                st.text_area("Antwort der KI", value=answer, height=300)

    with tab2:
        option = st.selectbox("Wähle eine Leistung:", ["Bitte auswählen"] + list(df["Leistungstitel"].unique()))
        if option != "Bitte auswählen":
            selected = df[df["Leistungstitel"] == option].iloc[0]
            st.subheader("📄 Details")
            for key in ["L-Nummer", "Leistungstitel", "Bezeichnung", "Interpretation"]:
                st.markdown(f"**{key}:** {selected.get(key, '')}")
            regeln = selected.get("Tarifmechanik Regeln", "").lower()
            if "nicht kumulierbar" in regeln:
                st.warning("⚠️ Nicht kumulierbar")

    with tab3:
        query = st.text_input("Freitextsuche:")
        if query:
            filtered = df[df.apply(lambda row: query.lower() in str(row["Leistungstitel"]).lower(), axis=1)]
            st.write(filtered)

    with tab4:
        auswahl = st.multiselect("Mehrere Positionen:", df["Leistungstitel"].unique())
        if auswahl:
            selected_df = df[df["Leistungstitel"].isin(auswahl)]
            st.write(selected_df[["L-Nummer", "Leistungstitel", "Tarifmechanik Regeln"]])
else:
    st.info("Bitte lade zuerst deine Excel-Datei hoch.")
