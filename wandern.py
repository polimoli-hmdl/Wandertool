import streamlit as st
import pandas as pd

# --- TITEL & KONFIGURATION ---
st.set_page_config(page_title="Outdoor Gear Planner V2", page_icon="🏔️")
st.title("🏔️ Ultimate Outdoor Gear Planner V2")

# --- 1. ERWEITERTE DATENBANK (Simulation) ---
# Hinweis: 'Temp_Min' bei Isomatten ist hier der Grenzwert (R-Wert umgerechnet)
data = {
    'Name': [
        'Merino Shirt', 'Synthetik Shirt', 'Fleece Pulli', 'Daunenjacke', 'Hardshell Jacke', 
        'Wanderhose', 'Softshellhose', 'Hardshellhose',
        'Leichte Wanderschuhe', 'Bergstiefel (Steigeisenfest)', 'Skischuhe',
        'Rucksack 40L', 'Rucksack 60L', 'Lawinenrucksack',
        'Daunenschlafsack -5°C', 'Sommerschlafsack +10°C', 
        'Isomatte (R-Wert 4)', 'Schaummatte (R-Wert 2)',
        'Zelt 2P', 'Biwacksack',
        'Gaskocher', 'Topfset Titan', 'Spork', 'Klappspaten',
        'Steigeisen', 'Eispickel', 'Klettersteigset', 'Helm', 'LVS-Set', 'Wanderstöcke'
    ],
    'Kategorie': [
        'Baselayer', 'Baselayer', 'Midlayer', 'Isolation', 'Shell', 
        'Hose', 'Hose', 'Hose',
        'Schuhe', 'Schuhe', 'Schuhe',
        'Rucksack', 'Rucksack', 'Rucksack',
        'Schlafen_Sack', 'Schlafen_Sack', 
        'Schlafen_Matte', 'Schlafen_Matte',
        'Schlafen_Shelter', 'Schlafen_Shelter',
        'Küche', 'Küche', 'Küche', 'Hygiene',
        'Technik', 'Technik', 'Technik', 'Technik', 'Technik', 'Technik'
    ],
    'Gewicht_g': [
        150, 130, 300, 350, 250, 
        400, 500, 300,
        800, 1400, 3000,
        1200, 1600, 2500,
        900, 500, 
        600, 300,
        1500, 300,
        100, 200, 15, 150,
        800, 400, 500, 300, 700, 400
    ],
    'Temp_Min': [ # Ab wann nötig / bis wann tauglich
        20, 25, 15, 5, 99, 
        99, 5, -10, 
        99, 99, 99,
        99, 99, 99,
        -5, 10, 
        -5, 10,
        99, 99,
        99, 99, 99, 99,
        99, 99, 99, 99, 99, 99
    ],
    # Tags helfen uns bei speziellen Filtern
    'Tags': [
        'Wandern', 'Wandern', 'Wandern', 'Wandern', 'Wandern', 
        'Wandern', 'Winter', 'Hochtour',
        'Wandern', 'Hochtour', 'Skitour',
        'Wandern', 'Trekking', 'Skitour',
        'Winter', 'Sommer', 
        'Winter', 'Sommer',
        'Komfort', 'Notfall',
        'Kochen', 'Kochen', 'Kochen', 'Draußen',
        'Hochtour', 'Hochtour', 'Klettersteig', 'Sicherheit', 'Skitour', 'Wandern'
    ]
}
df = pd.DataFrame(data)

# --- 2. SIDEBAR - EINGABEN ---
st.sidebar.header("🗺️ Tour-Parameter")

# Basics
dauer_tage = st.sidebar.number_input("Dauer (Tage)", min_value=1, value=1)
temp = st.sidebar.slider("Tiefsttemperatur (°C)", -20, 30, 10)
wetter = st.sidebar.selectbox("Wetter", ["Sonnig", "Wechselhaft", "Regen/Schnee"])

# Art der Tour (Multiselect für Kombinationen!)
tour_art = st.sidebar.multiselect(
    "Art der Tour (Mehrfachauswahl möglich)",
    ["Wandern", "Hochtour (Gletscher)", "Klettersteig", "Skitour"],
    default=["Wandern"]
)

schlafen_typ = st.sidebar.selectbox("Übernachtung", ["Hütte/Keine", "Zelt", "Biwak/Tarp"])
kochen = st.sidebar.checkbox("Selbstversorgung (Kochen)?")

# --- 3. LOGIK-ENGINE ---

packliste = [] # Hier kommen die Items rein
worn_items = [] # Items, die man am Körper trägt

# Hilfsfunktion zum Hinzufügen (vermeidet Duplikate Code)
def add_item(filter_col, filter_val, sort_col='Gewicht_g', asc=True, target_list=packliste, menge=1, name_contains=None):
    candidates = df[df[filter_col] == filter_val]
    if name_contains:
        candidates = candidates[candidates['Name'].str.contains(name_contains)]
    
    if not candidates.empty:
        # Nimm das leichteste (oder passendste)
        best_item = candidates.sort_values(by=sort_col, ascending=asc).iloc[0].to_dict()
        best_item['Menge'] = menge
        target_list.append(best_item)

# --- A. KLEIDUNG & SCHUHE ---

# 1. Schuhe (AM KÖRPER)
if "Skitour" in tour_art:
    add_item('Kategorie', 'Schuhe', name_contains="Skischuhe", target_list=worn_items)
elif "Hochtour (Gletscher)" in tour_art:
    add_item('Kategorie', 'Schuhe', name_contains="Bergstiefel", target_list=worn_items)
else:
    add_item('Kategorie', 'Schuhe', name_contains="Leichte", target_list=worn_items)

# 2. Hose (AM KÖRPER)
if temp < 0 or "Skitour" in tour_art:
    add_item('Kategorie', 'Hose', name_contains="Softshell", target_list=worn_items)
else:
    add_item('Kategorie', 'Hose', name_contains="Wanderhose", target_list=worn_items)

# 3. Baselayer (AM KÖRPER + WECHSELWÄSCHE)
# Einer wird getragen
if temp > 15:
    add_item('Kategorie', 'Baselayer', name_contains="Synthetik", target_list=worn_items)
else:
    add_item('Kategorie', 'Baselayer', name_contains="Merino", target_list=worn_items)

# Wechselwäsche für Rucksack (nur bei Mehrtagestouren)
if dauer_tage > 1:
    # Logic: Alle 3 Tage ein frisches Shirt, grob vereinfacht
    menge_shirts = int(dauer_tage / 3) 
    if menge_shirts >= 1:
        add_item('Kategorie', 'Baselayer', name_contains="Merino", menge=menge_shirts)
        
    # Socken (nicht in DB, aber als Beispiel für Logik)
    # Hier könnte man Socken aus DB laden.

# 4. Layers (RUCKSACK oder AN)
if temp < 15:
    add_item('Kategorie', 'Midlayer') # Fleece
if temp < 5:
    add_item('Kategorie', 'Isolation') # Daune

# 5. Wetterschutz
if wetter != "Sonnig" or temp < 5 or "Hochtour (Gletscher)" in tour_art:
    add_item('Kategorie', 'Shell')
    if "Hochtour (Gletscher)" in tour_art or "Skitour" in tour_art:
         add_item('Kategorie', 'Hose', name_contains="Hardshellhose") # Überhose

# --- B. SCHLAFEN ---
if schlafen_typ != "Hütte/Keine":
    # Schlafsack nach Temperatur wählen
    passende_saecke = df[(df['Kategorie'] == 'Schlafen_Sack') & (df['Temp_Min'] <= temp)]
    if not passende_saecke.empty:
        # Nimm den leichtesten, der warm genug ist
        best_sack = passende_saecke.sort_values('Gewicht_g').iloc[0].to_dict()
        best_sack['Menge'] = 1
        packliste.append(best_sack)
    else:
        st.error(f"ACHTUNG: Kein Schlafsack in der DB ist warm genug für {temp}°C!")

    # Matte
    passende_matten = df[(df['Kategorie'] == 'Schlafen_Matte') & (df['Temp_Min'] <= temp)]
    if not passende_matten.empty:
        best_matte = passende_matten.sort_values('Gewicht_g').iloc[0].to_dict()
        best_matte['Menge'] = 1
        packliste.append(best_matte)
    
    # Shelter
    if schlafen_typ == "Zelt":
        add_item('Kategorie', 'Schlafen_Shelter', name_contains="Zelt")
    elif schlafen_typ == "Biwak/Tarp":
        add_item('Kategorie', 'Schlafen_Shelter', name_contains="Biwak")

# --- C. TECHNIK & EXTRAS ---
if "Hochtour (Gletscher)" in tour_art:
    add_item('Kategorie', 'Technik', name_contains="Steigeisen")
    add_item('Kategorie', 'Technik', name_contains="Pickel")
    add_item('Kategorie', 'Technik', name_contains="Helm") # Gletscherspalten/Steinschlag

if "Klettersteig" in tour_art:
    add_item('Kategorie', 'Technik', name_contains="Klettersteigset")
    if not any(d['Name'] == 'Helm' for d in packliste): # Helm nur 1x
        add_item('Kategorie', 'Technik', name_contains="Helm")

if "Skitour" in tour_art:
    add_item('Kategorie', 'Technik', name_contains="LVS")
    # Lawinenrucksack statt normalem Rucksack?
    # Das lösen wir unten bei der Rucksackwahl

# Immer dabei
add_item('Kategorie', 'Technik', name_contains="Wanderstöcke", target_list=worn_items) # Oder im Rucksack, je nach Geschmack
add_item('Hygiene', 'Klappspaten') # LNT Prinzip ;)

# --- D. KÜCHE ---
if kochen:
    add_item('Kategorie', 'Küche', name_contains="Gaskocher")
    add_item('Kategorie', 'Küche', name_contains="Topf")
    add_item('Kategorie', 'Küche', name_contains="Spork")


# --- E. RUCKSACK WAHL (Ganz am Schluss) ---
# Wir summieren erst das Gewicht um zu sehen, was wir brauchen
current_pack_weight = sum([item['Gewicht_g'] * item['Menge'] for item in packliste])

if "Skitour" in tour_art:
     add_item('Kategorie', 'Rucksack', name_contains="Lawinenrucksack")
elif dauer_tage > 2 or schlafen_typ != "Hütte/Keine":
     add_item('Kategorie', 'Rucksack', name_contains="60L")
else:
     add_item('Kategorie', 'Rucksack', name_contains="40L")


# --- 4. OUTPUT & VISUALISIERUNG ---
st.divider()

# Datenframes erstellen
df_pack = pd.DataFrame(packliste)
df_worn = pd.DataFrame(worn_items)

# Gewichtsberechnungen
weight_pack = (df_pack['Gewicht_g'] * df_pack['Menge']).sum() if not df_pack.empty else 0
weight_worn = (df_worn['Gewicht_g'] * df_worn['Menge']).sum() if not df_worn.empty else 0
total_weight = weight_pack + weight_worn

# Spaltenlayout für Kennzahlen
col1, col2, col3 = st.columns(3)
col1.metric("🎒 Rucksackgewicht (Base Weight)", f"{weight_pack/1000:.2f} kg")
col2.metric("👕 Am Körper (Worn Weight)", f"{weight_worn/1000:.2f} kg")
col3.metric("⚖️ Systemgewicht (Total)", f"{total_weight/1000:.2f} kg")

# Tabs für bessere Übersicht
tab1, tab2 = st.tabs(["🎒 Packliste (Rucksack)", "👕 Am Körper"])

with tab1:
    if not df_pack.empty:
        # Schöne Darstellung
        display_df = df_pack[['Menge', 'Name', 'Kategorie', 'Gewicht_g']].copy()
        display_df['Gesamtgewicht'] = display_df['Gewicht_g'] * display_df['Menge']
        st.dataframe(display_df, use_container_width=True)
        
        # CSV Export Button
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button("Packliste herunterladen (CSV)", csv, "packliste.csv", "text/csv")
    else:
        st.info("Dein Rucksack ist leer!")

with tab2:
    if not df_worn.empty:
        st.dataframe(df_worn[['Menge', 'Name', 'Kategorie', 'Gewicht_g']], use_container_width=True)
    else:
        st.info("Du gehst nackt? Mutig.")

# Warnhinweise Logik
if "Hochtour (Gletscher)" in tour_art and not any(d['Name'] == 'Steigeisen' for d in packliste):
    st.error("Gefahr: Hochtour ausgewählt, aber keine Steigeisen gefunden!")
