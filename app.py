import streamlit as st
import pandas as pd
from datetime import date
import os

# Konfiguration
st.set_page_config(page_title="Profi-Stockkarte", page_icon="🐝", layout="centered")

# --- LOGIN BEREICH ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔒 Bitte anmelden")
        pw = st.text_input("Passwort eingeben", type="password")
        if st.button("Anmelden"):
            if pw == "Gnupatsch#12": 
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Falsches Passwort!")
        return False
    return True

if check_password():
    # --- APP STARTET HIER ---
    st.title("🐝 Digitale Stockkarte v1.4")

    DATEI = "stockkarten_daten_v3.csv"

    # Struktur der Datenbank
    spalten = [
        "Eintragsdatum", "Volk", "Königin Alter", "Königin gesehen", 
        "Stifte", "Varroa", "Honigentnahme Datum", "Fütterung Datum", 
        "Futtermenge (kg)", "Notiz"
    ]

    if not os.path.exists(DATEI):
        df_leer = pd.DataFrame(columns=spalten)
        df_leer.to_csv(DATEI, index=False)

    alle_voelker = ["Volk 1", "Volk 2", "Volk 3", "Volk 4", "Volk 5", "Ableger A"]
    
    # Daten laden
    df = pd.read_csv(DATEI)

    # --- EINGABEBEREICH (Oben) ---
    st.header("📝 Neuer Eintrag")
    with st.form("imker_form", clear_on_submit=True):
        f_datum = st.date_input("Datum der Durchschau", date.today())
        f_volk = st.selectbox("Welches Volk?", alle_voelker)
        
        st.subheader("Volkszustand")
        c1, c2 = st.columns(2)
        with c1:
            f_q_alter = st.number_input("Königin Geburtsjahr", min_value=2020, max_value=2026, value=2025)
            f_q_gesehen = st.checkbox("Königin gesehen?")
        with c2:
            f_stifte = st.checkbox("Stifte vorhanden?")
            f_varroa = st.number_input("Varroa-Abfall (pro Tag)", min_value=0)

        st.subheader("Ernte & Fütterung")
        h_check = st.checkbox("Heute Honig entnommen?")
        f_check = st.checkbox("Heute gefüttert?")
        
        f_futter_menge = st.number_input("Futtermenge (kg/Liter)", min_value=0.0, step=0.5)
        f_notiz = st.text_area("Besonderheiten")
        
        gespeichert = st.form_submit_button("Eintrag speichern")

    if gespeichert:
        h_datum = f_datum if h_check else "-"
        f_futter_datum = f_datum if f_check else "-"
        
        neue_zeile = pd.DataFrame([[
            f_datum, f_volk, f_q_alter, f_q_gesehen, f_stifte, 
            f_varroa, h_datum, f_futter_datum, f_futter_menge, f_notiz
        ]], columns=spalten)
        
        neue_zeile.to_csv(DATEI, mode='a', header=False, index=False)
        st.success(f"Daten für {f_volk} gesichert!")
        st.rerun()

    # --- GRAFIK BEREICH (Mitte) ---
    st.divider()
    st.header("📈 Varroa-Verlauf")
    
    # Auswahl für welches Volk die Grafik angezeigt werden soll
    gewaehltes_volk_grafik = st.selectbox("Grafik anzeigen für:", alle_voelker, key="grafik_select")
    
    if not df.empty:
        df_plot = df[df["Volk"] == gewaehltes_volk_grafik].copy()
        if not df_plot.empty:
            df_plot["Eintragsdatum"] = pd.to_datetime(df_plot["Eintragsdatum"])
            df_plot = df_plot.sort_values("Eintragsdatum")
            st.line_chart(data=df_plot, x="Eintragsdatum", y="Varroa")
        else:
            st.info(f"Noch keine Daten für {gewaehltes_volk_grafik} vorhanden.")
    else:
        st.info("Datenbank ist noch leer.")

    # --- TABELLE (Unten) ---
    st.divider()
    st.header("📋 Alle Aufzeichnungen")
    st.dataframe(df, use_container_width=True)
