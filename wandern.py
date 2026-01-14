import streamlit as st
import pandas as pd
import altair as alt
import math

# --- KONFIGURATION ---
st.set_page_config(page_title="Outdoor Gear Planner V5 (Expert)", page_icon="🏔️", layout="wide")
st.title("🏔️ Outdoor Gear Planner V5 (Expert Logic)")
st.caption("Optimiert für Hochtouren, Hütten & Autarkie-Level")

# --- 1. DATENBANK (Expert Update) ---
data = {
    'Name': [
        # Kleidung Oben
        'Merino Shirt (Langarm)', 'Synthetik Shirt (Kurz)', 
        'Fleece Pulli (Midlayer)', 'Daunenjacke (Isolation)', 'Hardshell Jacke (Wetter)',
        
        # Kleidung Unten
        'Wanderhose (Softshell)', 'Leichte Regenhose (Backup)', 'Alpine Hardshellhose (Robust)',
        'Hüttenschuhe/Clogs',
        
        # Schuhe
        'Trailrunner', 'Bergstiefel (B/C)', 'Skischuhe',
        
        # Rucksack
        'Rucksack 40L', 'Rucksack 60L', 'Lawinenrucksack',
        
        # Schlafen
        'Daunenschlafsack -5°C', 'Sommerschlafsack +10°C', 'Seiden-Inlet (Hüttenschlafsack)',
        'Isomatte (R-Wert 4)', 'Schaummatte (R-Wert 2)',
        'Zelt 2P', 'Biwacksack',
        
        # Küche
        'Gaskocher (Ultralight)', 'Topfset Titan 700ml', 'Langer Löffel', 
        'Wasserfilter (Squeeze)',
        'Gaskartusche 100g', 'Gaskartusche 230g',
        
        # Wasserbehälter
        'Wasserflasche 1L (PET)', 'Trinkblase 2L', 'Trinkblase 3L',
        
        # Technik & Gletscher
        'Steigeisen', 'Eispickel', 'Klettersteigset', 'Kletterhelm', 'LVS-Set', 
        'Wanderstöcke (Paar)',
        'Einfachseil 30m', 'Einfachseil 50m',
        'Powerbank 10.000mAh', 'Powerbank 20.000mAh', 'USB-Ladegerät (Dual)',
        'Klappspaten'
    ],
    'Kategorie': [
        'Baselayer', 'Baselayer', 
        'Midlayer', 'Isolation', 'Shell',
        
        'Hose', 'Hose_Regen', 'Hose_Regen', 
        'Schuhe_Camp',
        
        'Schuhe', 'Schuhe', 'Schuhe',
        
        'Rucksack', 'Rucksack', 'Rucksack',
        
        'Schlafen_Sack', 'Schlafen_Sack', 'Schlafen_Sack',
        'Schlafen_Matte', 'Schlafen_Matte',
        'Schlafen_Shelter', 'Schlafen_Shelter',
        
        'Küche', 'Küche', 'Küche', 
        'Küche',
        'Verbrauch_Gas', 'Verbrauch_Gas',
        
        'Wasser_Behaelter', 'Wasser_Behaelter', 'Wasser_Behaelter',
        
        'Technik', 'Technik', 'Technik', 'Technik', 'Technik', 
        'Technik',
        'Seil', 'Seil',
        'Elektronik', 'Elektronik', 'Elektronik',
        'Hygiene'
    ],
    'Gewicht_g': [
        200, 130, 
        300, 350, 300,
        
        400, 150, 450, 
        200,
        
        700, 1400, 3000,
        
        1100, 1600, 2500,
        
        900, 600, 130, 
        600, 350, 
        1400, 250,
        
        80, 150, 15, 
        80,
        200, 380,
        
        40, 150, 170,
        
        850, 450, 500, 300, 700, 
        450,
        2100, 3500,
        200, 400, 80,
        150
    ],
    'Temp_Limit': [15, 25, 10, -5, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, -5, 10, 99, -5, 10, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99]
}
df = pd.DataFrame(data)

# --- 2. SIDEBAR EINGABEN ---
with st.sidebar:
    st.header("🗺️ Tour-Settings")
    dauer_tage = st.number_input("Dauer (Tage)", 1, 30, 3)
    temp = st.slider("Tiefsttemperatur (°C)", -25, 30, 5)
    
    tour_art = st.multiselect("Tour-Typ", 
                             ["Wandern", "Hochtour", "Klettersteig", "Skitour"],
                             default=["Wandern"])
    
    st.subheader("🏠 Schlafen & Wohnen")
    schlafen_typ = st.selectbox("Übernachtung", ["Hütte (Bewirtschaftet)", "Zelt/Biwak"])
    
    st.subheader("⚡ Technik & Seil")
    strom_zugang = st.checkbox("Zugang zu Steckdose/Strom?", value=False, help="In Hütten oft ja, im Zelt nein.")
    seil_wahl = st.selectbox("Seil nötig?", ["Kein Seil", "30m Einfachseil", "50m Einfachseil"])

    st.subheader("💧 Verpflegung")
    quellen_status = st.select_slider("Wasserquellen", options=["Viele", "Selten", "Keine"])
    essen_pro_tag = 700 # Default Fixwert, da User "Kalt frühstückt" sparen wir Gas, nicht Essen-Gewicht

    # Wasser-Empfehlung
    empf_wasser = 2.0
    if quellen_status == "Selten": empf_wasser = 3.0
    if quellen_status == "Keine": empf_wasser = 4.5
    if "Hochtour" in tour_art: empf_wasser += 0.5
    
    wasser_kapazitaet = st.slider(f"Wasserkapazität (Empf: {empf_wasser}L)", 0.5, 6.0, empf_wasser, 0.5)

# --- 3. LOGIK ENGINE ---

packliste = []     # Rucksack
worn_items = []    # Am Körper
consumables = []   # Verbrauch

def add(kategorie, name_part=None, target=packliste, menge=1, min_temp=None):
    """Smarte Auswahlfunktion"""
    subset = df[df['Kategorie'] == kategorie]
    if name_part:
        subset = subset[subset['Name'].str.contains(name_part, case=False)]
    if min_temp is not None:
        # Filter items that can handle the temp (Temp_Limit <= user_temp)
        # Hier vereinfacht: Wir suchen einfach das passende Item
        pass
    
    if not subset.empty:
        # Nimm das leichteste Item, das passt
        item = subset.sort_values('Gewicht_g').iloc[0].to_dict()
        item['Menge'] = menge
        # Typ Zuweisung für Charts
        if target == worn_items: item['Typ'] = 'Am Körper'
        elif target == consumables: item['Typ'] = 'Verbrauch'
        else: item['Typ'] = 'Ausrüstung'
        
        target.append(item)

# === A. KLEIDUNG & SCHUHE ===

# 1. Schuhe (Am Körper)
if "Skitour" in tour_art:
    add('Schuhe', 'Skischuhe', worn_items)
elif "Hochtour" in tour_art:
    add('Schuhe', 'Bergstiefel', worn_items)
else:
    add('Schuhe', 'Trailrunner', worn_items)

# 2. Hose (Am Körper)
add('Hose', 'Wanderhose', worn_items)

# 3. Regenhose (Im Rucksack)
# User Wunsch: Bei Hochtour "Alpine Hardshellhose" statt "Leichte Regenhose"
if "Hochtour" in tour_art or "Skitour" in tour_art:
    add('Hose_Regen', 'Alpine Hardshell', packliste)
else:
    add('Hose_Regen', 'Leichte Regen', packliste)

# 4. Baselayer (Wechselwäsche Logik)
# Einer am Körper
add('Baselayer', 'Merino' if temp < 15 else 'Synthetik', worn_items)

# Wechselwäsche: Alle 2 Tage frisch
if dauer_tage > 1:
    total_needed = math.ceil(dauer_tage / 2)
    extras = total_needed - 1 # Einen hat man an
    if extras > 0:
        add('Baselayer', 'Merino', packliste, menge=extras)

# 5. Layers (Fleece & Isolation)
# User: "Fleece immer Midlayer, Daune Isolation. Bei sehr kalt (<0) beides."
if temp < 15:
    add('Midlayer', 'Fleece', packliste) # Immer dabei wenn < 15
if temp < 10:
    add('Isolation', 'Daunenjacke', packliste) # Daune ab < 10

# 6. Hardshell Jacke (Immer dabei außer sicher Hochsommer)
add('Shell', 'Hardshell', packliste)

# 7. Camp-Schuhe
if dauer_tage > 1:
    add('Schuhe_Camp', 'Hüttenschuhe', packliste)

# === B. SCHLAFEN ===

if schlafen_typ == "Hütte (Bewirtschaftet)":
    # User: "Nur Hüttenschlafsack Seide"
    add('Schlafen_Sack', 'Seiden-Inlet', packliste)
    # Keine Matte, kein Zelt
else:
    # Zelt/Biwak
    add('Schlafen_Shelter', 'Zelt', packliste)
    add('Schlafen_Matte', 'Isomatte' if temp < 5 else 'Schaummatte', packliste)
    # Schlafsack nach Temp
    if temp < 5:
        add('Schlafen_Sack', 'Daunenschlafsack', packliste)
    else:
        add('Schlafen_Sack', 'Sommerschlafsack', packliste)

# === C. TECHNIK & SEIL ===

# Strom & Powerbank
if strom_zugang:
    add('Elektronik', 'Ladegerät', packliste)
    # Evtl kleines Kabel, Gewicht vernachlässigbar
else:
    # Keine Steckdose -> Powerbank berechnen
    # Annahme: 3000mAh pro Tag (Smartphone + Navi)
    bedarf_mah = dauer_tage * 3000
    if bedarf_mah > 10000:
        add('Elektronik', '20.000', packliste)
    else:
        add('Elektronik', '10.000', packliste)

# Seil (User Wahl)
if seil_wahl == "30m Einfachseil":
    add('Seil', '30m', packliste)
elif seil_wahl == "50m Einfachseil":
    add('Seil', '50m', packliste)

# Alpine Hardware
if "Hochtour" in tour_art:
    add('Technik', 'Steigeisen', packliste)
    add('Technik', 'Eispickel', packliste)
    add('Technik', 'Helm', packliste)

if "Klettersteig" in tour_art:
    add('Technik', 'Klettersteigset', packliste)
    # Helm nur einmal hinzufügen
    if not any(d['Name'] == 'Kletterhelm' for d in packliste):
        add('Technik', 'Helm', packliste)

if "Skitour" in tour_art:
    add('Technik', 'LVS', packliste) # Schaufel/Sonde hier impliziert im Set

add('Technik', 'Wanderstöcke', worn_items)
add('Hygiene', 'Klappspaten', packliste)

# === D. KÜCHE & WASSER ===

add('Küche', 'Wasserfilter', packliste) # User: Immer Filter, keine Tabletten

# Wasser Behälter
cap_fill = 0
while cap_fill < wasser_kapazitaet:
    if wasser_kapazitaet - cap_fill >= 2.0:
        add('Wasser_Behaelter', 'Trinkblase 2L', packliste)
        cap_fill += 2.0
    else:
        add('Wasser_Behaelter', 'Flasche', packliste)
        cap_fill += 1.0

# Kochen (nur wenn nicht Hütte oder explizit gewünscht)
# Annahme: Bei Hütte meist HP, aber manche kochen trotzdem.
# Wir machen es abhängig vom Schlaf-Typ: Zelt = Kochen. Hütte = Kein Kochen (Vereinfachung)
if schlafen_typ == "Zelt/Biwak":
    add('Küche', 'Kocher', packliste)
    add('Küche', 'Topf', packliste)
    add('Küche', 'Löffel', packliste)
    
    # Gas: 14g pro Tag (Kaltes Frühstück)
    gas_total = dauer_tage * 14
    if gas_total <= 100:
        add('Verbrauch_Gas', '100g', packliste)
    else:
        add('Verbrauch_Gas', '230g', packliste)

# Verbrauch (Gewicht)
consumables.append({
    'Name': 'Wasser (Start)', 'Kategorie': 'Wasser', 
    'Gewicht_g': wasser_kapazitaet * 1000, 'Menge': 1, 'Typ': 'Verbrauch'
})
consumables.append({
    'Name': 'Essen (Riegel/Dinner)', 'Kategorie': 'Essen',
    'Gewicht_g': essen_pro_tag, 'Menge': dauer_tage, 'Typ': 'Verbrauch'
})

# === OUTPUT ===

# Daten zusammenführen
all_items = packliste + worn_items + consumables
df_res = pd.DataFrame(all_items)
df_res['Gesamtgewicht'] = df_res['Gewicht_g'] * df_res['Menge']

# Metriken
base_w = df_res[df_res['Typ'] == 'Ausrüstung']['Gesamtgewicht'].sum()
worn_w = df_res[df_res['Typ'] == 'Am Körper']['Gesamtgewicht'].sum()
cons_w = df_res[df_res['Typ'] == 'Verbrauch']['Gesamtgewicht'].sum()
total = base_w + worn_w + cons_w

st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("🎒 Base Weight (Rucksack)", f"{base_w/1000:.2f} kg")
c2.metric("👕 Worn Weight (Körper)", f"{worn_w/1000:.2f} kg")
c3.metric("💧 Verbrauch (Start)", f"{cons_w/1000:.2f} kg")

# Tabs für saubere Trennung
tab_pack, tab_worn, tab_cons = st.tabs(["🎒 Rucksack (Ausrüstung)", "👕 Am Körper", "🥪 Verbrauch"])

def show_table(filter_typ):
    subset = df_res[df_res['Typ'] == filter_typ].copy()
    if not subset.empty:
        st.dataframe(
            subset[['Menge', 'Name', 'Gewicht_g', 'Gesamtgewicht']], 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Leer")

with tab_pack:
    show_table('Ausrüstung')
    st.caption("Das 'Base Weight' enthält alles im Rucksack außer Essen, Wasser und Brennstoff.")

with tab_worn:
    show_table('Am Körper')

with tab_cons:
    show_table('Verbrauch')
    st.caption("Dieses Gewicht nimmt während der Tour jeden Tag ab.")
