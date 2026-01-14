import streamlit as st
import pandas as pd

# --- TITEL & BESCHREIBUNG ---
st.title("🏔️ Smart Outdoor Gear Selector")
st.write("Wähle deine Bedingungen und erhalte einen Ausrüstungsvorschlag.")

# --- 1. DATEN LADEN (Hier simulieren wir deine Excel-Tabelle) ---
# Später ersetzen wir das durch: df = pd.read_excel("meine_ausruestung.xlsx")
data = {
    'Name': ['Merino Shirt', 'Synthetik Shirt', 'Fleece Pulli', 'Daunenjacke', 'Regenjacke Hardshell', 'Wanderhose', 'Rucksack 40L', 'Rucksack 20L'],
    'Kategorie': ['Baselayer', 'Baselayer', 'Midlayer', 'Isolation', 'Shell', 'Hose', 'Rucksack', 'Rucksack'],
    'Gewicht_g': [150, 130, 300, 350, 250, 400, 1200, 800],
    'Volumen_l': [0.5, 0.5, 2.0, 3.0, 1.0, 1.0, 40.0, 20.0], # Bei Rucksäcken ist das die Kapazität
    'Temp_Min': [20, 25, 10, -5, 10, 10, -99, -99], # Ab wann brauche ich das (grob)
    'Wasserdicht': [False, False, False, False, True, False, False, False]
}
df = pd.DataFrame(data)

# Zeige die Datenbank optional an
if st.checkbox("Zeige gesamte Ausrüstungs-Datenbank"):
    st.dataframe(df)

# --- 2. EINGABEFORMULAR (User Input) ---
st.sidebar.header("Wander-Bedingungen")
temp = st.sidebar.slider("Erwartete Tiefsttemperatur (°C)", -10, 30, 15)
regen = st.sidebar.checkbox("Regen erwartet?")
dauer = st.sidebar.selectbox("Dauer", ["Tages-Tour", "Mehrtages-Tour"])

# --- 3. LOGIK (Variante B - Intelligente Auswahl) ---
vorschlag_liste = []

# -- Logik für Kleidung (Zwiebelprinzip) --

# Schritt 1: Baselayer (Immer nötig)
# Wir nehmen das leichtere Shirt, wenn es warm ist, sonst Merino
if temp > 20:
    baselayer = df[(df['Kategorie'] == 'Baselayer') & (df['Name'].str.contains('Synthetik'))].iloc[0]
else:
    baselayer = df[(df['Kategorie'] == 'Baselayer') & (df['Name'].str.contains('Merino'))].iloc[0]
vorschlag_liste.append(baselayer)

# Schritt 2: Midlayer (Nur wenn kälter als 15 Grad)
if temp < 15:
    midlayer = df[df['Kategorie'] == 'Midlayer'].iloc[0]
    vorschlag_liste.append(midlayer)

# Schritt 3: Isolation (Nur wenn kälter als 5 Grad)
if temp < 5:
    iso = df[df['Kategorie'] == 'Isolation'].iloc[0]
    vorschlag_liste.append(iso)

# Schritt 4: Shell (Wenn Regen ODER sehr kalt/windig)
if regen or temp < 5:
    shell = df[df['Kategorie'] == 'Shell'].iloc[0]
    vorschlag_liste.append(shell)

# Schritt 5: Hose (Immer)
hose = df[df['Kategorie'] == 'Hose'].iloc[0]
vorschlag_liste.append(hose)

# -- Logik für Rucksack --
# Berechne das Volumen der Kleidung (grob)
pack_volumen_benoetigt = sum([item['Volumen_l'] for item in vorschlag_liste])

# Wenn Mehrtagestour -> Nimm den großen Rucksack, sonst reicht der kleine (wenn es passt)
if dauer == "Mehrtages-Tour" or pack_volumen_benoetigt > 18:
    rucksack = df[(df['Kategorie'] == 'Rucksack') & (df['Volumen_l'] >= 40)].iloc[0]
else:
    rucksack = df[(df['Kategorie'] == 'Rucksack') & (df['Volumen_l'] < 40)].iloc[0]

vorschlag_liste.append(rucksack)

# --- 4. ERGEBNIS ANZEIGEN ---
st.header("🎒 Dein Pack-Vorschlag")

# Umwandeln der Liste zurück in eine Tabelle zur Anzeige
ergebnis_df = pd.DataFrame(vorschlag_liste)

# Berechnungen
gesamtgewicht = ergebnis_df[ergebnis_df['Kategorie'] != 'Rucksack']['Gewicht_g'].sum() + rucksack['Gewicht_g']
packvolumen_items = ergebnis_df[ergebnis_df['Kategorie'] != 'Rucksack']['Volumen_l'].sum()
rucksack_kapazitaet = rucksack['Volumen_l']

# Metriken anzeigen (Große Zahlen)
col1, col2, col3 = st.columns(3)
col1.metric("Gesamtgewicht", f"{gesamtgewicht/1000:.2f} kg")
col2.metric("Benötigtes Volumen", f"{packvolumen_items:.1f} L")
col3.metric("Rucksack Füllstand", f"{int((packvolumen_items / rucksack_kapazitaet)*100)} %")

# Tabelle anzeigen
st.table(ergebnis_df[['Name', 'Kategorie', 'Gewicht_g', 'Volumen_l']])

# Warnhinweise
if packvolumen_items > rucksack_kapazitaet:
    st.error(f"ACHTUNG: Dein Equipment ({packvolumen_items} L) passt nicht in den Rucksack ({rucksack_kapazitaet} L)!")

if regen and not any(ergebnis_df['Wasserdicht']):
    st.warning("Es soll regnen, aber du hast keine wasserdichte Jacke im Set!")
